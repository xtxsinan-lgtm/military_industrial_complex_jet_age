"""2D Airfoil parametrization (NACA 4/5/6-series, biconvex, CST, free-draw) and Hess-Smith panel solver.

Implements:
1. Parametric coordinate generators:
   - NACA 4-digit (`naca4`)
   - NACA 5-digit (`naca5`)
   - NACA 6-series (`naca6`, e.g. 63/64/65/66 series)
   - Supersonic biconvex / circular-arc (`biconvex`)
   - Kulfan Class-Shape Transformation (`cst`)
   - Free-draw control points fitted to CST (`free_draw`)
2. Vectorized 2D Hess-Smith source + vortex panel solver (default 120 cosine-spaced panels)
   computing cl_alpha, alpha_zero_lift_rad, cm0, surface Cp(x), and Karman-Tsien critical Mach.
3. USAF DATCOM §4.1.1.4 leading-edge sharpness parameter Delta_y (% chord) and 2D cl_max(Re).
4. Korn drag-divergence factor kappa_A.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import numpy as np
from scipy.special import comb

from .tuning import load_aero_tuning


@dataclass(frozen=True)
class AirfoilSectionResult:
    """Complete geometric and 2D aerodynamic analysis of an airfoil section."""

    spec_id: str
    kind: str  # "naca4" | "naca5" | "naca6" | "biconvex" | "cst" | "free_draw"
    tc_ratio: float
    x_tmax: float
    max_camber: float
    x_camber_max: float
    r_le_ratio: float
    delta_y_pct: float  # USAF DATCOM LE sharpness parameter (% chord between 0.0015c and 0.06c)
    cl_alpha_rad: float
    alpha_zero_lift_rad: float
    cm_0: float
    cl_design: float
    cp_min_at_cl0: float
    korn_kappa_a: float
    m_dd_0: float
    m_crit_0: float
    cl_max_low_speed: float  # at Re = 6e6, M = 0.2
    cst_weights_upper: Tuple[float, ...]
    cst_weights_lower: Tuple[float, ...]
    x_grid: np.ndarray = field(repr=False)
    y_upper: np.ndarray = field(repr=False)
    y_lower: np.ndarray = field(repr=False)


def _cosine_x(n_half: int) -> np.ndarray:
    """Cosine-spaced chordwise coordinates from 0 to 1 (length n_half + 1)."""
    beta = np.linspace(0.0, math.pi, n_half + 1)
    return 0.5 * (1.0 - np.cos(beta))


def _naca4_thickness(x: np.ndarray, tc: float) -> np.ndarray:
    """Standard NACA 4/5-digit half-thickness distribution with closed trailing edge."""
    return 5.0 * tc * (
        0.2969 * np.sqrt(np.maximum(x, 0.0))
        - 0.1260 * x
        - 0.3516 * (x ** 2)
        + 0.2843 * (x ** 3)
        - 0.1036 * (x ** 4)
    )


def _naca6_thickness(x: np.ndarray, tc: float, x_pmin: float) -> np.ndarray:
    """Analytical NACA 6-series thickness approximation calibrated to Abbott & von Doenhoff ordinates.

    Uses a modified 4-digit/6-series representation where the maximum thickness location
    shifts aft with the design pressure-minimum station x_pmin in [0.3, 0.6], and the
    leading-edge radius is smaller than a 4-digit section (r_LE/c ~ 0.68 * (t/c)^2).
    """
    m = float(np.clip(0.35 + 0.12 * (x_pmin - 0.30), 0.34, 0.42))
    # Blend between standard NACA 4-digit (max at 0.30) and aft-shifted laminar profile
    yt_4 = _naca4_thickness(x, tc)
    # Aft-shifted component with reduced LE radius and cusp-like aft boat-tail
    s = np.sqrt(np.maximum(x, 0.0))
    yt_6_shape = tc * (
        1.185 * s
        + 0.420 * x
        - 2.450 * (x ** 2)
        + 1.625 * (x ** 3)
        - 0.780 * (x ** 4)
    )
    # Normalize yt_6_shape so its max equals 0.5 * tc
    peak = float(np.max(yt_6_shape)) if np.max(yt_6_shape) > 1e-9 else 0.5 * tc
    yt_6_norm = yt_6_shape * (0.5 * tc / peak)
    w = float(np.clip((m - 0.30) / 0.10, 0.4, 1.0))
    return (1.0 - w) * yt_4 + w * yt_6_norm


def _naca4_camber(x: np.ndarray, m: float, p: float) -> Tuple[np.ndarray, np.ndarray]:
    """NACA 4-digit mean camber line yc(x) and slope dyc/dx."""
    if m <= 1e-6 or p <= 0.01 or p >= 0.99:
        return np.zeros_like(x), np.zeros_like(x)
    yc = np.where(
        x < p,
        (m / (p ** 2)) * (2.0 * p * x - x ** 2),
        (m / ((1.0 - p) ** 2)) * ((1.0 - 2.0 * p) + 2.0 * p * x - x ** 2),
    )
    dyc = np.where(
        x < p,
        (2.0 * m / (p ** 2)) * (p - x),
        (2.0 * m / ((1.0 - p) ** 2)) * (p - x),
    )
    return yc, dyc


def _naca5_camber(x: np.ndarray, cl_design: float, p_code: int, reflex: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    """NACA 5-digit mean camber line (NACA Report 537)."""
    if abs(cl_design) <= 1e-6:
        return np.zeros_like(x), np.zeros_like(x)
    # Table for standard (non-reflex) 5-digit camber lines at cl_i = 0.3
    table = {
        1: (0.0580, 361.40),
        2: (0.1260, 51.640),
        3: (0.2025, 15.957),
        4: (0.2900, 6.6430),
        5: (0.3910, 3.2300),
    }
    m, k1 = table.get(p_code, (0.2025, 15.957))
    scale = cl_design / 0.30
    k1_s = k1 * scale
    yc = np.where(
        x < m,
        (k1_s / 6.0) * (x ** 3 - 3.0 * m * (x ** 2) + (m ** 2) * (3.0 - m) * x),
        (k1_s * (m ** 3) / 6.0) * (1.0 - x),
    )
    dyc = np.where(
        x < m,
        (k1_s / 6.0) * (3.0 * (x ** 2) - 6.0 * m * x + (m ** 2) * (3.0 - m)),
        np.full_like(x, -k1_s * (m ** 3) / 6.0),
    )
    if reflex:
        yc *= 0.85
        dyc *= 0.85
    return yc, dyc


def _naca6_camber(x: np.ndarray, cl_design: float) -> Tuple[np.ndarray, np.ndarray]:
    """NACA 6-series uniform-load (a=1.0) mean line with closed endpoints."""
    if abs(cl_design) <= 1e-6:
        return np.zeros_like(x), np.zeros_like(x)
    eps = 1e-7
    xc = np.clip(x, eps, 1.0 - eps)
    yc = -(cl_design / (4.0 * math.pi)) * ((1.0 - xc) * np.log(1.0 - xc) + xc * np.log(xc))
    yc = np.where((x <= eps) | (x >= 1.0 - eps), 0.0, yc)
    dyc = -(cl_design / (4.0 * math.pi)) * (np.log(xc) - np.log(1.0 - xc))
    dyc = np.clip(dyc, -0.5, 0.5)
    return yc, dyc


def _combine_camber_thickness(
    x: np.ndarray, yc: np.ndarray, dyc: np.ndarray, yt: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Combine mean camber line and thickness onto identical chordwise stations x."""
    cos_theta = 1.0 / np.sqrt(1.0 + dyc ** 2)
    yu = yc + yt * cos_theta
    yl = yc - yt * cos_theta
    yu[0], yl[0] = 0.0, 0.0
    yu[-1], yl[-1] = 0.0, 0.0
    return yu, yl


def _bernstein_matrix(x: np.ndarray, order: int) -> np.ndarray:
    """Compute Bernstein basis matrix B[i, k] = comb(n, k) * x^k * (1-x)^(n-k)."""
    n = order
    cols = []
    for k in range(n + 1):
        coeff = float(comb(n, k))
        cols.append(coeff * (x ** k) * ((1.0 - x) ** (n - k)))
    return np.column_stack(cols)


def evaluate_cst(
    x: np.ndarray,
    weights_upper: Sequence[float],
    weights_lower: Sequence[float],
    n1: float = 0.5,
    n2: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Evaluate Kulfan CST upper and lower surface ordinates y_u(x), y_l(x)."""
    order_u = len(weights_upper) - 1
    order_l = len(weights_lower) - 1
    c_func = (np.maximum(x, 0.0) ** n1) * (np.maximum(1.0 - x, 0.0) ** n2)
    bu = _bernstein_matrix(x, order_u)
    bl = _bernstein_matrix(x, order_l)
    yu = c_func * (bu @ np.asarray(weights_upper, dtype=np.float64))
    yl = c_func * (bl @ np.asarray(weights_lower, dtype=np.float64))
    yu[0], yl[0] = 0.0, 0.0
    yu[-1], yl[-1] = 0.0, 0.0
    return yu, yl


def fit_cst_to_coordinates(
    x: np.ndarray,
    yu: np.ndarray,
    yl: np.ndarray,
    order: int = 6,
    n1: float = 0.5,
    n2: float = 1.0,
) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    """Least-squares fit of CST Bernstein weights to arbitrary airfoil coordinates (x, yu, yl)."""
    mask = (x > 1e-4) & (x < 1.0 - 1e-4)
    xm = x[mask]
    c_func = (xm ** n1) * ((1.0 - xm) ** n2)
    b_mat = _bernstein_matrix(xm, order)
    design_mat = c_func[:, None] * b_mat
    wu, _, _, _ = np.linalg.lstsq(design_mat, yu[mask], rcond=None)
    wl, _, _, _ = np.linalg.lstsq(design_mat, yl[mask], rcond=None)
    return tuple(float(v) for v in wu), tuple(float(v) for v in wl)


def _solve_hess_smith_2d(x_grid: np.ndarray, yu: np.ndarray, yl: np.ndarray) -> Tuple[float, float, float, float]:
    """Vectorized 2D Hess-Smith constant-source + constant-vortex panel solver.

    Returns:
        (cl_alpha_inviscid_rad, alpha_zero_lift_rad, cm_0_quarter_chord, cp_min_at_cl0)
    """
    # Construct clockwise contour from TE lower -> LE -> TE upper
    x_lo = x_grid[:0:-1]
    y_lo = yl[:0:-1]
    X = np.concatenate([x_lo, x_grid])
    Y = np.concatenate([y_lo, yu])

    n_panels = len(X) - 1
    x1, y1 = X[:-1], Y[:-1]
    x2, y2 = X[1:], Y[1:]
    xc = 0.5 * (x1 + x2)
    yc = 0.5 * (y1 + y2)
    dx = x2 - x1
    dy = y2 - y1
    panel_len = np.hypot(dx, dy)
    theta = np.arctan2(dy, dx)
    sin_t = dy / panel_len
    cos_t = dx / panel_len

    # Transform collocation points i into local coordinates of panel j
    dx_ij = xc[:, None] - x1[None, :]
    dy_ij = yc[:, None] - y1[None, :]
    x_loc = dx_ij * cos_t[None, :] + dy_ij * sin_t[None, :]
    y_loc = -dx_ij * sin_t[None, :] + dy_ij * cos_t[None, :]

    r1_sq = x_loc ** 2 + y_loc ** 2
    r2_sq = (x_loc - panel_len[None, :]) ** 2 + y_loc ** 2
    ln_r2_r1 = 0.5 * np.log(np.maximum(r2_sq, 1e-18) / np.maximum(r1_sq, 1e-18))
    beta_ij = np.arctan2(y_loc, x_loc - panel_len[None, :]) - np.arctan2(y_loc, x_loc)
    # Wrap beta_ij into (-pi, pi]
    beta_ij = (beta_ij + math.pi) % (2.0 * math.pi) - math.pi

    # Self-influence on diagonal
    np.fill_diagonal(ln_r2_r1, 0.0)
    np.fill_diagonal(beta_ij, math.pi)

    theta_diff = theta[:, None] - theta[None, :]
    sin_td = np.sin(theta_diff)
    cos_td = np.cos(theta_diff)

    two_pi = 2.0 * math.pi
    A_n = (sin_td * ln_r2_r1 + cos_td * beta_ij) / two_pi
    A_t = (-cos_td * ln_r2_r1 + sin_td * beta_ij) / two_pi

    # Build (N+1) x (N+1) linear system for [sigma_1..sigma_N, gamma]
    # For clockwise vortex gamma: B_n = -sum(A_t), B_t = +sum(A_n)
    sys_mat = np.zeros((n_panels + 1, n_panels + 1), dtype=np.float64)
    sys_mat[:n_panels, :n_panels] = A_n
    sys_mat[:n_panels, n_panels] = -np.sum(A_t, axis=1)
    # Kutta condition: V_t(0) + V_t(N-1) = 0
    sys_mat[n_panels, :n_panels] = A_t[0, :] + A_t[-1, :]
    sys_mat[n_panels, n_panels] = float(np.sum(A_n[0, :] + A_n[-1, :]))

    # Solve simultaneously for two angles of attack: alpha_1 = 0 deg, alpha_2 = 4 deg
    alphas = np.array([0.0, math.radians(4.0)], dtype=np.float64)
    rhs = np.zeros((n_panels + 1, 2), dtype=np.float64)
    for k, a in enumerate(alphas):
        rhs[:n_panels, k] = np.sin(theta - a)
        rhs[n_panels, k] = -(math.cos(theta[0] - a) + math.cos(theta[-1] - a))

    try:
        sol = np.linalg.solve(sys_mat, rhs)
    except np.linalg.LinAlgError:
        sol, _, _, _ = np.linalg.lstsq(sys_mat, rhs, rcond=None)

    cl_vals = np.zeros(2, dtype=np.float64)
    cm_vals = np.zeros(2, dtype=np.float64)
    cp_cols = np.zeros((n_panels, 2), dtype=np.float64)

    for k, a in enumerate(alphas):
        sigma = sol[:n_panels, k]
        gamma = sol[n_panels, k]
        vt = np.cos(theta - a) + A_t @ sigma + gamma * np.sum(A_n, axis=1)
        cp = 1.0 - vt ** 2
        cp_cols[:, k] = cp
        # Circulation gives lift coefficient directly: cl = 2 * gamma * perimeter
        cl_k = 2.0 * gamma * float(np.sum(panel_len))
        # Quarter-chord pitching moment from pressure integration (nose-up positive)
        fx = cp * dy
        fy = -cp * dx
        cm_k = -float(np.sum((xc - 0.25) * fy - yc * fx))
        cl_vals[k] = cl_k
        cm_vals[k] = cm_k

    cl_alpha_inv = float((cl_vals[1] - cl_vals[0]) / (alphas[1] - alphas[0]))
    cl_alpha_inv = float(np.clip(cl_alpha_inv, 5.5, 7.2))
    alpha_0 = float(-cl_vals[0] / cl_alpha_inv)
    # Interpolate Cm and Cp to zero lift (cl = 0)
    w0 = -cl_vals[0] / (cl_vals[1] - cl_vals[0]) if abs(cl_vals[1] - cl_vals[0]) > 1e-9 else 0.0
    cm_0 = float(cm_vals[0] + w0 * (cm_vals[1] - cm_vals[0]))
    cp_cl0 = cp_cols[:, 0] + w0 * (cp_cols[:, 1] - cp_cols[:, 0])
    # Exclude extreme LE/TE singular panel spikes when reading minimum Cp
    mid_mask = (xc > 0.02) & (xc < 0.96)
    cp_min_0 = float(np.min(cp_cl0[mid_mask])) if np.any(mid_mask) else float(np.min(cp_cl0))
    return cl_alpha_inv, alpha_0, cm_0, cp_min_0


def _karman_tsien_mcrit(cp_min: float) -> float:
    """Solve Karman-Tsien compressibility relation for critical Mach number where Cp = Cp_crit(M)."""
    cp0 = float(np.clip(cp_min, -3.5, -0.05))
    lo, hi = 0.30, 0.96
    gamma = 1.4
    for _ in range(28):
        mid = 0.5 * (lo + hi)
        beta = math.sqrt(1.0 - mid * mid)
        cp_kt = cp0 / (beta + 0.5 * (mid * mid / (1.0 + beta)) * cp0)
        cp_crit = (2.0 / (gamma * mid * mid)) * (
            ((1.0 + 0.5 * (gamma - 1.0) * mid * mid) / (0.5 * (gamma + 1.0))) ** (gamma / (gamma - 1.0)) - 1.0
        )
        if cp_kt < cp_crit:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def _compute_le_sharpness_and_clmax(
    x_grid: np.ndarray,
    yu: np.ndarray,
    yl: np.ndarray,
    tc_ratio: float,
    max_camber: float,
    kind: str,
) -> Tuple[float, float, float]:
    """Compute LE radius ratio r_LE/c, USAF DATCOM §4.1.1.4 Delta_y (% chord), and 2D cl_max(Re=6e6)."""
    yt = 0.5 * (yu - yl)
    y_0015 = float(np.interp(0.0015, x_grid, yt))
    y_0600 = float(np.interp(0.0600, x_grid, yt))
    delta_y_pct = 100.0 * max(y_0600 - y_0015, 0.001)

    if kind == "biconvex":
        r_le_ratio = 0.0
    elif kind == "naca6":
        r_le_ratio = 0.68 * (tc_ratio ** 2)
    else:
        # Estimate r_LE from y_t near nose: y_t(x) ~ sqrt(2 * r_LE * x) -> r_LE ~ y_t^2 / (2x)
        y_005 = float(np.interp(0.005, x_grid, yt))
        r_le_ratio = float(np.clip((y_005 ** 2) / 0.010, 0.0, 1.35 * (tc_ratio ** 2)))

    # USAF DATCOM Figure 4.1.1.4-22a piecewise curve for untwisted symmetric section cl_max_base(Delta_y)
    # Sharp LE (Delta_y <= 1.4): thin-airfoil stall ~ 0.80 - 0.95
    # Intermediate LE (Delta_y ~ 2.0 - 2.6): leading-edge stall peak ~ 1.40 - 1.55
    # Thick trailing-edge stall (Delta_y >= 3.0): plateaus ~ 1.52 - 1.58
    dy_pts = np.array([0.20, 0.80, 1.40, 1.90, 2.50, 3.20, 4.50])
    cl_pts = np.array([0.76, 0.84, 0.98, 1.28, 1.48, 1.56, 1.54])
    cl_base = float(np.interp(delta_y_pct, dy_pts, cl_pts))
    # Camber increment (Abbott & von Doenhoff: ~3.5 * max_camber for moderate thickness)
    camber_inc = 3.6 * max_camber * float(np.clip(delta_y_pct / 2.2, 0.4, 1.1))
    cl_max_2d = float(np.clip(cl_base + camber_inc, 0.72, 1.90))
    return r_le_ratio, delta_y_pct, cl_max_2d


def parse_and_analyze_airfoil(
    spec: Union[str, Dict[str, Any]],
    override_tc_ratio: Optional[float] = None,
) -> AirfoilSectionResult:
    """Parse an airfoil specification (string code or dict) and compute its 2D aerodynamic properties.

    Supported formats:
      - String shorthand:
        - `"0010"`, `"2412"`, `"0009.5"` -> NACA 4-digit
        - `"23012"`, `"23009"` -> NACA 5-digit
        - `"64-010"`, `"64A010"`, `"65-210"`, `"65A006"` -> NACA 6-series
        - `"biconvex:0.0336"` or `"biconvex"` -> Supersonic biconvex section
      - Dict schema:
        - `{"kind": "naca4"|"naca5"|"naca6"|"biconvex"|"cst"|"free_draw", "code": ..., "tc_ratio": ..., ...}`
    """
    tuning = load_aero_tuning()["airfoil"]
    n_half = max(int(tuning.get("panel_count", 120)) // 2, 30)
    x_grid = _cosine_x(n_half)

    if isinstance(spec, str):
        s = spec.strip()
        s_clean = re.sub(r"^naca\s*[-_]?\s*", "", s, flags=re.IGNORECASE)
        if s_clean.lower().startswith("biconvex"):
            parts = s_clean.split(":")
            tc_val = float(parts[1]) if len(parts) > 1 else 0.04
            spec_dict: Dict[str, Any] = {"kind": "biconvex", "code": s, "tc_ratio": tc_val}
        elif re.match(r"^6[3456]", s_clean):
            spec_dict = {"kind": "naca6", "code": s_clean}
        elif re.match(r"^\d{5}(\.\d+)?$", s_clean):
            spec_dict = {"kind": "naca5", "code": s_clean}
        else:
            spec_dict = {"kind": "naca4", "code": s_clean}
    else:
        spec_dict = dict(spec)

    kind = str(spec_dict.get("kind", "naca4")).lower()
    code = str(spec_dict.get("code", "0010")).strip()
    code_clean = re.sub(r"^naca\s*[-_]?\s*", "", code, flags=re.IGNORECASE)

    cl_design = 0.0
    if kind == "naca4":
        m_match = re.match(r"^(\d)(\d)(\d{2}(?:\.\d+)?)$", code_clean)
        if m_match:
            m_val = float(m_match.group(1)) / 100.0
            p_val = float(m_match.group(2)) / 10.0
            tc_val = float(m_match.group(3)) / 100.0
        else:
            m_val = float(spec_dict.get("max_camber", 0.0))
            p_val = float(spec_dict.get("camber_pos", 0.4))
            tc_val = float(spec_dict.get("tc_ratio", 0.10))
        if override_tc_ratio is not None:
            tc_val = float(override_tc_ratio)
        tc_val = float(np.clip(tc_val, 0.02, 0.25))
        yc, dyc = _naca4_camber(x_grid, m_val, p_val)
        yt = _naca4_thickness(x_grid, tc_val)
        yu, yl = _combine_camber_thickness(x_grid, yc, dyc, yt)
        cl_design = 10.0 * m_val
        spec_id = f"NACA-{code_clean}"

    elif kind == "naca5":
        m_match = re.match(r"^(\d)(\d)(\d)(\d{2}(?:\.\d+)?)$", code_clean)
        if m_match:
            l_digit = int(m_match.group(1))
            p_digit = int(m_match.group(2))
            q_digit = int(m_match.group(3))
            tc_val = float(m_match.group(4)) / 100.0
            cl_design = 0.15 * l_digit
            reflex = q_digit == 1
        else:
            cl_design = float(spec_dict.get("cl_design", 0.3))
            p_digit = 3
            reflex = False
            tc_val = float(spec_dict.get("tc_ratio", 0.12))
        if override_tc_ratio is not None:
            tc_val = float(override_tc_ratio)
        tc_val = float(np.clip(tc_val, 0.02, 0.25))
        yc, dyc = _naca5_camber(x_grid, cl_design, p_digit, reflex=reflex)
        yt = _naca4_thickness(x_grid, tc_val)
        yu, yl = _combine_camber_thickness(x_grid, yc, dyc, yt)
        spec_id = f"NACA-{code_clean}"

    elif kind == "naca6":
        # Examples: "64-010", "64A210", "65-108", "65A006", "64-209.5"
        m_match = re.match(r"^6([3456])[0-9A-Za-z]*[-A]?(\d)(\d{2}(?:\.\d+)?)$", code_clean)
        if m_match:
            x_pmin = int(m_match.group(1)) / 10.0
            cl_design = int(m_match.group(2)) / 10.0
            tc_val = float(m_match.group(3)) / 100.0
        else:
            x_pmin = float(spec_dict.get("x_pmin", 0.4))
            cl_design = float(spec_dict.get("cl_design", 0.0))
            tc_val = float(spec_dict.get("tc_ratio", 0.09))
        if override_tc_ratio is not None:
            tc_val = float(override_tc_ratio)
        tc_val = float(np.clip(tc_val, 0.02, 0.25))
        yc, dyc = _naca6_camber(x_grid, cl_design)
        yt = _naca6_thickness(x_grid, tc_val, x_pmin)
        yu, yl = _combine_camber_thickness(x_grid, yc, dyc, yt)
        spec_id = f"NACA-{code_clean}"

    elif kind == "biconvex":
        tc_val = float(override_tc_ratio if override_tc_ratio is not None else spec_dict.get("tc_ratio", 0.04))
        tc_val = float(np.clip(tc_val, 0.02, 0.20))
        yt = 2.0 * tc_val * x_grid * (1.0 - x_grid)
        yu = yt.copy()
        yl = -yt.copy()
        spec_id = f"Biconvex-{tc_val*100:.2f}pct"

    elif kind == "cst":
        wu = tuple(float(v) for v in spec_dict.get("weights_upper", [0.15, 0.14, 0.13, 0.12, 0.11, 0.10, 0.08]))
        wl = tuple(float(v) for v in spec_dict.get("weights_lower", [-0.15, -0.14, -0.13, -0.12, -0.11, -0.10, -0.08]))
        n1 = float(spec_dict.get("n1", 0.5))
        n2 = float(spec_dict.get("n2", 1.0))
        yu, yl = evaluate_cst(x_grid, wu, wl, n1=n1, n2=n2)
        if override_tc_ratio is not None:
            cur_tc = float(np.max(yu - yl))
            if cur_tc > 1e-4:
                yc_cur = 0.5 * (yu + yl)
                yt_cur = 0.5 * (yu - yl) * (float(override_tc_ratio) / cur_tc)
                yu = yc_cur + yt_cur
                yl = yc_cur - yt_cur
        spec_id = str(spec_dict.get("code", "CST-Custom"))

    elif kind == "free_draw":
        up_pts = np.asarray(spec_dict["upper_points"], dtype=np.float64)
        lo_pts = np.asarray(spec_dict["lower_points"], dtype=np.float64)
        up_pts = up_pts[np.argsort(up_pts[:, 0])]
        lo_pts = lo_pts[np.argsort(lo_pts[:, 0])]
        yu_raw = np.interp(x_grid, up_pts[:, 0], up_pts[:, 1])
        yl_raw = np.interp(x_grid, lo_pts[:, 0], lo_pts[:, 1])
        # Enforce upper > lower by at least 2% chord max thickness
        yt_raw = np.maximum(0.5 * (yu_raw - yl_raw), 0.0)
        yc_raw = 0.5 * (yu_raw + yl_raw)
        if float(np.max(2.0 * yt_raw)) < 0.02:
            yt_raw = _naca4_thickness(x_grid, 0.04)
        wu, wl = fit_cst_to_coordinates(x_grid, yc_raw + yt_raw, yc_raw - yt_raw, order=6)
        yu, yl = evaluate_cst(x_grid, wu, wl)
        if override_tc_ratio is not None:
            cur_tc = float(np.max(yu - yl))
            if cur_tc > 1e-4:
                yc_cur = 0.5 * (yu + yl)
                yt_cur = 0.5 * (yu - yl) * (float(override_tc_ratio) / cur_tc)
                yu = yc_cur + yt_cur
                yl = yc_cur - yt_cur
        spec_id = str(spec_dict.get("code", "FreeDraw-CST"))

    else:
        raise ValueError(f"Unsupported airfoil kind: {kind!r}")

    thickness_dist = yu - yl
    camber_dist = 0.5 * (yu + yl)
    idx_tmax = int(np.argmax(thickness_dist))
    tc_actual = float(thickness_dist[idx_tmax])
    x_tmax = float(x_grid[idx_tmax])
    idx_cmax = int(np.argmax(np.abs(camber_dist)))
    max_camber = float(camber_dist[idx_cmax])
    x_camber_max = float(x_grid[idx_cmax]) if abs(max_camber) > 1e-5 else 0.40

    if kind not in ("cst", "free_draw"):
        n1_fit = 1.0 if kind == "biconvex" else 0.5
        wu, wl = fit_cst_to_coordinates(x_grid, yu, yl, order=6, n1=n1_fit, n2=1.0)

    cl_alpha_inv, alpha_0, cm_0, cp_min_0 = _solve_hess_smith_2d(x_grid, yu, yl)
    visc_factor = float(tuning.get("cl_alpha_2d_viscous_factor", 0.955))
    cl_alpha_rad = cl_alpha_inv * visc_factor

    r_le_ratio, delta_y_pct, cl_max_2d = _compute_le_sharpness_and_clmax(
        x_grid, yu, yl, tc_actual, abs(max_camber), kind
    )

    # Korn technology factor kappa_A: combines family baseline + aft max-thickness bonus
    if kind == "naca4":
        kappa_base = float(tuning.get("korn_kappa_naca4", 0.87))
    elif kind == "naca5":
        kappa_base = float(tuning.get("korn_kappa_naca5", 0.88))
    elif kind == "naca6":
        kappa_base = float(tuning.get("korn_kappa_naca6", 0.90))
    elif kind == "biconvex":
        kappa_base = float(tuning.get("korn_kappa_biconvex", 0.91))
    else:
        # For CST / free_draw, derive smoothly from x_tmax and LE suction peak
        kappa_base = float(tuning.get("korn_kappa_cst_base", 0.885)) + float(
            tuning.get("korn_xtmax_gain", 0.06)
        ) * (x_tmax - 0.33)
    kappa_a = float(np.clip(kappa_base, 0.85, 0.93))

    # Zero-lift drag divergence Mach (2D unswept) and critical Mach (blended Korn + Karman-Tsien)
    m_dd_k = kappa_a - tc_actual
    m_crit_kt = _karman_tsien_mcrit(cp_min_0)
    mcrit_offset = float(tuning.get("mcrit_offset_from_mdd", 0.108))
    m_dd_0 = float(0.75 * m_dd_k + 0.25 * (m_crit_kt + mcrit_offset))
    m_crit_0 = m_dd_0 - mcrit_offset

    return AirfoilSectionResult(
        spec_id=spec_id,
        kind=kind,
        tc_ratio=tc_actual,
        x_tmax=x_tmax,
        max_camber=max_camber,
        x_camber_max=x_camber_max,
        r_le_ratio=r_le_ratio,
        delta_y_pct=delta_y_pct,
        cl_alpha_rad=cl_alpha_rad,
        alpha_zero_lift_rad=alpha_0,
        cm_0=cm_0,
        cl_design=cl_design,
        cp_min_at_cl0=cp_min_0,
        korn_kappa_a=kappa_a,
        m_dd_0=m_dd_0,
        m_crit_0=m_crit_0,
        cl_max_low_speed=cl_max_2d,
        cst_weights_upper=wu,
        cst_weights_lower=wl,
        x_grid=x_grid,
        y_upper=yu,
        y_lower=yl,
    )
