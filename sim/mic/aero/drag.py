"""Full component drag buildup, Sears-Haack/Eminton area-rule wave drag, Korn drag divergence,
induced drag K(M), and high-lift / maneuver CL_max(M) envelope for Module 01.

References:
- Raymer, "Aircraft Design: A Conceptual Approach", 5th Ed., Ch. 12.
- USAF Stability and Control DATCOM, Section 4.1.
- Mason, "Analytic Models for Technology Integration in Aircraft Design" (Korn equation with sweep).
- Eminton / Lord Fourier slender-body wave drag integral.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Optional, Tuple, Union
import numpy as np

from ..atmosphere import isa_properties, reynolds_per_meter
from .geometry import DerivedAircraftGeometry, get_tech_value
from .tuning import load_aero_tuning
from .vlm import VLMResult, compute_cl_alpha_mach

NumberOrArray = Union[float, np.ndarray]


@dataclass(frozen=True)
class WaveDragSummary:
    """Precomputed geometric wave-drag parameters for an aircraft configuration."""

    s_ref_m2: float
    l_eff_m: float
    a_max_ruled_m2: float
    a_max_unruled_m2: float
    d_over_q_sears_haack_m2: float
    d_over_q_sears_haack_unruled_m2: float
    ewd_factor: float
    ewd_factor_unruled: float
    d_over_q_wave_m12_m2: float
    d_over_q_wave_m12_unruled_m2: float
    cd_wave_m12: float
    area_rule_drag_reduction_ratio: float


@dataclass(frozen=True)
class HighLiftConfigProperties:
    """Aerodynamic properties in clean, takeoff, and landing configurations at sea level."""

    cl_max_clean_low_speed: float
    cl_max_takeoff: float
    cl_max_landing: float
    delta_cd0_takeoff: float
    delta_cd0_landing: float
    k_takeoff: float
    k_landing: float


def compute_wave_drag_summary(geom: DerivedAircraftGeometry) -> WaveDragSummary:
    """Compute Sears-Haack wave drag and Eminton/Fourier smoothness factor E_WD from A(x)."""
    tuning = load_aero_tuning()["drag"]
    wave_scale = float(tuning.get("wave_drag_global_scale", 0.68))
    ewd_base = float(tuning.get("ewd_baseline_non_area_ruled", 1.72))
    ewd_min = float(tuning.get("ewd_min_clamp", 1.15))
    ewd_max = float(tuning.get("ewd_max_clamp", 2.50))

    l_eff = 0.95 * geom.fuselage.length_m
    x_sta = geom.fuselage.x_stations_m
    a_fus_core = max(geom.fuselage.max_cross_section_m2 - geom.intake_capture_area_m2, 0.25)

    def _eval_area_dist(a_dist: np.ndarray, is_ruled: bool) -> Tuple[float, float, float]:
        a_max = float(np.max(a_dist))
        dq_sh = (9.0 * math.pi / 2.0) * ((a_max / max(l_eff, 2.0)) ** 2)

        # Smooth A(x) with a 9-point Gaussian Mach-plane oblique cutting kernel
        u = x_sta / max(geom.fuselage.length_m, 1.0)
        a_norm = a_dist / max(a_max, 0.05)
        k_g = np.exp(-0.5 * (np.linspace(-2.0, 2.0, 9) ** 2))
        k_g /= np.sum(k_g)
        a_sm = np.convolve(np.pad(a_norm, 4, mode="reflect"), k_g, mode="valid")
        da_du = np.gradient(a_sm, u)
        d2a_du2 = np.gradient(da_du, u)
        r_int = float(np.trapezoid(d2a_du2[6:-6] ** 2, u[6:-6]))

        # Wing-body cross-sectional bump ratio at peak station
        bump_ratio = max(a_max - a_fus_core, 0.0) / a_fus_core
        # Non-area-ruled delta + short/blunt fuselage interference penalty (YF-102 case)
        nose_fn = geom.fuselage.nose_length_m / max(geom.fuselage.max_diameter_m, 0.5)
        tail_fn = geom.fuselage.tail_length_m / max(geom.fuselage.max_diameter_m, 0.5)
        blunt_pen = max(2.6 - nose_fn, 0.0) * 0.42 + max(2.6 - tail_fn, 0.0) * 0.42
        if not is_ruled and geom.wing.planform_type == "delta" and geom.fuselage.fineness_ratio < 9.5 and not geom.carrier_capable:
            blunt_pen += 0.72

        rough_excess = max(r_int - 240.0, 0.0) / 600.0 + 0.55 * bump_ratio + blunt_pen
        ewd = ewd_base * (0.76 + 0.34 * min(rough_excess, 2.0))
        if is_ruled and geom.fuselage.effective_waist_fraction > 0.0:
            # Area ruling smooths the wing-body Mach-plane area distribution directly
            ewd *= 1.0 - 0.42 * geom.fuselage.effective_waist_fraction
        ewd = float(np.clip(ewd, ewd_min, ewd_max))
        return a_max, dq_sh, ewd

    a_max_r, dq_sh_r, ewd_r = _eval_area_dist(geom.fuselage.area_total_m2, geom.fuselage.area_ruled)
    a_max_u, dq_sh_u, ewd_u = _eval_area_dist(geom.fuselage.area_total_unruled_m2, False)

    dq_wave_m12_r = wave_scale * ewd_r * dq_sh_r
    dq_wave_m12_u = wave_scale * ewd_u * dq_sh_u
    cd_wave_m12 = dq_wave_m12_r / geom.wing.area_m2
    reduction_ratio = 1.0 - (dq_wave_m12_r / max(dq_wave_m12_u, 1e-6))

    return WaveDragSummary(
        s_ref_m2=geom.wing.area_m2,
        l_eff_m=l_eff,
        a_max_ruled_m2=a_max_r,
        a_max_unruled_m2=a_max_u,
        d_over_q_sears_haack_m2=dq_sh_r,
        d_over_q_sears_haack_unruled_m2=dq_sh_u,
        ewd_factor=ewd_r,
        ewd_factor_unruled=ewd_u,
        d_over_q_wave_m12_m2=dq_wave_m12_r,
        d_over_q_wave_m12_unruled_m2=dq_wave_m12_u,
        cd_wave_m12=cd_wave_m12,
        area_rule_drag_reduction_ratio=float(np.clip(reduction_ratio, 0.0, 0.65)),
    )


def compute_mdd_and_mcrit(
    geom: DerivedAircraftGeometry,
    cl: NumberOrArray = 0.0,
) -> Tuple[NumberOrArray, NumberOrArray]:
    """Compute 3D swept-wing drag-divergence Mach M_dd(CL) and critical Mach M_crit(CL).

    Uses the Korn-Mason swept-wing relation with finite-wing effective sweep Lambda_eff = 0.75 * Lambda_c/4:
        M_dd = kappa_A / cos(Lambda_eff) - (t/c) / cos^2(Lambda_eff) - 0.10 * |CL| / cos^3(Lambda_eff)
    """
    tuning = load_aero_tuning()["airfoil"]
    offset = float(tuning.get("mcrit_offset_from_mdd", 0.108))

    # Effective finite-wing sweep (root/tip isobar unsweeping leaves ~78% of geometric sweep effective)
    eff_sweep_rad = 0.78 * abs(geom.wing.sweep_qc_rad)
    cos_s = max(math.cos(eff_sweep_rad), 0.45)

    kappa_a = geom.wing.airfoil.korn_kappa_a
    tc = geom.wing.tc_mean
    mdd_zero = (kappa_a / cos_s) - (tc / (cos_s ** 2))
    # Cap zero-lift M_dd at 0.97 (since sonic fuselage/nacelle interferences still occur near M=1)
    mdd_zero = min(mdd_zero, 0.97)

    is_scalar = np.ndim(cl) == 0
    cl_arr = np.abs(np.asarray(cl, dtype=np.float64))
    # Scale CL sensitivity smoothly so high sweep doesn't explode 1/cos^3 at high AoA
    cl_term = 0.085 * cl_arr / max(cos_s ** 1.8, 0.40)
    mdd = np.clip(mdd_zero - cl_term, 0.60, 0.97)
    mcrit = mdd - offset
    if is_scalar:
        return float(mdd), float(mcrit)
    return mdd, mcrit


def _skin_friction_cf(
    re_per_m: np.ndarray,
    mach: np.ndarray,
    char_len_m: float,
    k_rough_m: float,
    lam_frac: float,
) -> np.ndarray:
    """Compute mixed laminar/turbulent skin-friction coefficient Cf(Re, M) with roughness cutoff."""
    re_actual = np.maximum(re_per_m * max(char_len_m, 0.2), 1e5)
    l_over_k = max(char_len_m / max(k_rough_m, 1e-7), 100.0)
    re_cut_sub = 38.21 * (l_over_k ** 1.053)
    re_cut_sup = 44.62 * (l_over_k ** 1.053) * (np.maximum(mach, 0.9) ** 1.16)
    re_cutoff = np.where(mach <= 0.9, re_cut_sub, re_cut_sup)
    re_eff = np.minimum(re_actual, re_cutoff)

    cf_turb = 0.455 / (((np.log10(re_eff)) ** 2.58) * ((1.0 + 0.144 * (mach ** 2)) ** 0.65))
    cf_lam = 1.328 / np.sqrt(re_eff)
    # Decay laminar flow above M=0.75 due to compressibility / shock disturbances
    lam_eff = lam_frac * np.clip(1.0 - (mach - 0.75) / 0.20, 0.0, 1.0)
    return lam_eff * cf_lam + (1.0 - lam_eff) * cf_turb


def compute_cd0_subsonic(
    geom: DerivedAircraftGeometry,
    mach: NumberOrArray,
    alt_m: NumberOrArray,
    tech_context: Any = None,
    include_drop_tanks: bool = False,
    include_combat_stores: bool = False,
) -> NumberOrArray:
    """Compute component-buildup subsonic zero-lift drag coefficient CD0_sub(M, h)."""
    tuning = load_aero_tuning()
    dt = tuning["drag"]
    cat = tuning["catalog_defaults"]

    is_scalar = np.ndim(mach) == 0 and np.ndim(alt_m) == 0
    m = np.asarray(mach, dtype=np.float64)
    h = np.asarray(alt_m, dtype=np.float64)
    m_b, h_b = np.broadcast_arrays(m, h)
    m_safe = np.maximum(m_b, 0.10)

    re_m = np.asarray(reynolds_per_meter(m_safe, h_b), dtype=np.float64)

    surf_finish_mul = float(get_tech_value(tech_context, "mfg.surface_finish_factor", 1.0))
    skin_drag_mul = float(get_tech_value(tech_context, "aero.drag_skin_factor", 1.0))
    k_rough = float(dt.get("skin_roughness_m", 6.35e-6)) * surf_finish_mul

    lam_wing = (
        float(dt.get("laminar_fraction_naca6", 0.18))
        if geom.wing.airfoil.kind == "naca6"
        else float(dt.get("laminar_fraction_conventional", 0.05))
    )
    lam_fus = 0.04

    # 1. Wing friction & form factor
    cf_w = _skin_friction_cf(re_m, m_safe, geom.wing.mac_m, k_rough, lam_wing)
    m_ff = np.minimum(m_safe, 0.92)
    x_tmax = max(geom.wing.airfoil.x_tmax, 0.25)
    tc_w = geom.wing.tc_mean
    ff_w_sub = (1.0 + (0.6 / x_tmax) * tc_w + 100.0 * (tc_w ** 4)) * (
        1.34 * (m_ff ** 0.18) * (max(math.cos(geom.wing.sweep_qc_rad), 0.35) ** 0.28)
    )
    # Above M=1.05, thickness pressure drag is captured in wave drag so FF -> 1.02
    sup_blend = np.clip((m_safe - 0.95) / 0.25, 0.0, 1.0)
    ff_w = (1.0 - sup_blend) * ff_w_sub + sup_blend * 1.02
    q_w = (
        float(dt.get("interference_wing_high", 1.01))
        if geom.wing.position == "high"
        else float(dt.get("interference_wing_low_mid", 1.02))
    )
    dq_wing = cf_w * ff_w * q_w * geom.wing.wetted_area_m2

    # 2. Fuselage friction & form factor
    cf_f = _skin_friction_cf(re_m, m_safe, geom.fuselage.length_m, k_rough, lam_fus)
    f_rat = max(geom.fuselage.fineness_ratio, 3.5)
    ff_f_sub = 1.0 + (60.0 / (f_rat ** 3)) + (f_rat / 400.0)
    ff_f = (1.0 - sup_blend) * ff_f_sub + sup_blend * 1.02
    dq_fus = cf_f * ff_f * 1.00 * geom.fuselage.wetted_area_m2

    # 3. Horizontal & Vertical Tail
    q_tail = (
        float(dt.get("interference_tail_ttail", 1.03))
        if geom.empennage.t_tail
        else float(dt.get("interference_tail_conventional", 1.04))
    )
    if geom.empennage.ht_area_m2 > 0.01:
        cf_ht = _skin_friction_cf(re_m, m_safe, geom.empennage.ht_mac_m, k_rough, 0.05)
        tc_ht = geom.empennage.ht_tc_ratio
        ff_ht_sub = (1.0 + 2.0 * tc_ht + 100.0 * (tc_ht ** 4)) * (
            1.34 * (m_ff ** 0.18) * (max(math.cos(geom.empennage.ht_sweep_qc_rad), 0.35) ** 0.28)
        )
        ff_ht = (1.0 - sup_blend) * ff_ht_sub + sup_blend * 1.02
        dq_ht = cf_ht * ff_ht * q_tail * geom.empennage.ht_wetted_area_m2
    else:
        dq_ht = 0.0

    cf_vt = _skin_friction_cf(re_m, m_safe, geom.empennage.vt_mac_m, k_rough, 0.05)
    tc_vt = geom.empennage.vt_tc_ratio
    ff_vt_sub = (1.0 + 2.0 * tc_vt + 100.0 * (tc_vt ** 4)) * (
        1.34 * (m_ff ** 0.18) * (max(math.cos(geom.empennage.vt_sweep_qc_rad), 0.35) ** 0.28)
    )
    ff_vt = (1.0 - sup_blend) * ff_vt_sub + sup_blend * 1.02
    dq_vt = cf_vt * ff_vt * q_tail * geom.empennage.vt_wetted_area_m2

    # 4. Canopy, boundary-layer diverter, and aft base drag
    cd_can = (
        float(dt.get("canopy_cd_frontal_bubble", 0.085))
        if geom.fuselage.canopy_type == "bubble"
        else float(dt.get("canopy_cd_frontal_faired", 0.045))
    )
    dq_canopy = cd_can * geom.fuselage.canopy_frontal_area_m2
    dq_diverter = (
        float(dt.get("bl_diverter_dq_m2", 0.014))
        if geom.intake_type in ("cheek", "wing_root", "chin")
        else 0.0
    )
    dq_base = 0.008 * geom.fuselage.max_cross_section_m2

    # 5. External stores (drop tanks & external missiles/pylons when carried)
    dq_stores = 0.0
    if include_drop_tanks and geom.drop_tanks_count > 0 and geom.drop_tank_fuel_kg_each > 0.0:
        dq_stores += geom.drop_tanks_count * float(dt.get("drop_tank_dq_m2_per_tank", 0.032))
    if include_combat_stores and not geom.internal_bay:
        for mid in geom.missile_ids:
            m_info = cat["missiles"].get(mid, {"dq_m2": 0.006})
            dq_stores += float(m_info.get("dq_m2", 0.006))

    excres_factor = float(dt.get("excrescence_leakage_factor", 1.075)) * skin_drag_mul
    cd0_scale = float(dt.get("cd0_global_scale", 0.96))

    dq_skin_total = (dq_wing + dq_fus + dq_ht + dq_vt) * excres_factor
    dq_total = cd0_scale * (dq_skin_total + dq_canopy + dq_diverter + dq_base + dq_stores)
    cd0 = dq_total / geom.wing.area_m2
    return float(cd0) if is_scalar else cd0


def compute_wave_drag_cdw(
    geom: DerivedAircraftGeometry,
    wave_summary: WaveDragSummary,
    mach: NumberOrArray,
    cl: NumberOrArray = 0.0,
) -> NumberOrArray:
    """Compute transonic and supersonic wave drag coefficient CD_w(M, CL)."""
    dt = load_aero_tuning()["drag"]
    lock_k = float(dt.get("lock_wave_drag_coeff", 20.0))
    m_peak = float(dt.get("transonic_wave_peak_mach", 1.08))
    peak_mul = float(dt.get("transonic_wave_peak_multiplier", 1.15))

    is_scalar = np.ndim(mach) == 0 and np.ndim(cl) == 0
    m = np.asarray(mach, dtype=np.float64)
    cl_a = np.asarray(cl, dtype=np.float64)
    m_b, cl_b = np.broadcast_arrays(m, cl_a)

    mdd, mcrit = compute_mdd_and_mcrit(geom, cl_b)
    mdd = np.asarray(mdd, dtype=np.float64)
    mcrit = np.asarray(mcrit, dtype=np.float64)

    # Supersonic wave drag formula (Raymer Eq. 12.46 + supersonic wing thickness & pitot shock wave drag)
    sweep_le_deg = max(abs(geom.wing.sweep_le_deg), 2.0)
    sweep_term = 1.0 - (math.pi * (sweep_le_deg ** 0.77)) / 100.0
    m_sup_delta = np.maximum(m_b - 1.20, 0.0)
    mach_corr = np.clip(1.0 - 0.24 * (m_sup_delta ** 0.57) * sweep_term, 0.65, 1.35)
    # Supersonic wing-section leading-edge shock-expansion additive term (wing volume already in A(x))
    cos_le = max(math.cos(geom.wing.sweep_le_rad), 0.35)
    cdw_wing_thick = 0.55 * ((geom.wing.tc_mean ** 2) * (cos_le ** 1.8)) / np.sqrt(np.maximum(m_b ** 2 - 1.0, 0.35))
    pitot_spill = (
        0.0085 * (np.maximum(m_b - 1.25, 0.0) ** 1.35)
        if geom.intake_compression == "pitot"
        else 0.0
    )
    cdw_sup = wave_summary.cd_wave_m12 * mach_corr + cdw_wing_thick + pitot_spill

    cdw_m12 = float(
        wave_summary.cd_wave_m12
        + 0.55 * ((geom.wing.tc_mean ** 2) * (cos_le ** 1.8)) / math.sqrt(1.20 ** 2 - 1.0)
    )
    cdw_mdd = lock_k * ((mdd - mcrit) ** 4)
    cdw_peak = max(peak_mul * cdw_m12, float(np.max(cdw_mdd)) + 0.005)

    res = np.zeros_like(m_b, dtype=np.float64)

    # Region 1: M <= M_crit -> 0
    # Region 2: M_crit < M <= M_dd -> Lock 4th power
    r2 = (m_b > mcrit) & (m_b <= mdd)
    if np.any(r2):
        res[r2] = lock_k * ((m_b[r2] - mcrit[r2]) ** 4)

    # Region 3: M_dd < M <= m_peak -> Smooth Hermite rise to transonic peak
    r3 = (m_b > mdd) & (m_b <= m_peak)
    if np.any(r3):
        u = np.clip((m_b[r3] - mdd[r3]) / np.maximum(m_peak - mdd[r3], 0.04), 0.0, 1.0)
        # Smooth S-curve 3u^2 - 2u^3
        s = (u ** 2) * (3.0 - 2.0 * u)
        res[r3] = cdw_mdd[r3] + (cdw_peak - cdw_mdd[r3]) * s

    # Region 4: m_peak < M < 1.20 -> Smooth cosine transition from peak to M=1.20 value
    r4 = (m_b > m_peak) & (m_b < 1.20)
    if np.any(r4):
        u = np.clip((m_b[r4] - m_peak) / (1.20 - m_peak), 0.0, 1.0)
        s = 0.5 * (1.0 - np.cos(math.pi * u))
        res[r4] = cdw_peak + (cdw_m12 - cdw_peak) * s

    # Region 5: M >= 1.20 -> Raymer Eq. 12.46 + thickness/spillage wave drag
    r5 = m_b >= 1.20
    if np.any(r5):
        res[r5] = cdw_sup[r5]

    return float(res) if is_scalar else res


def compute_induced_drag_k(
    geom: DerivedAircraftGeometry,
    vlm: VLMResult,
    mach: NumberOrArray,
    tech_context: Any = None,
) -> NumberOrArray:
    """Compute drag-due-to-lift factor K(M) across subsonic, transonic, and supersonic speeds."""
    dt = load_aero_tuning()["drag"]
    e_scale = float(dt.get("oswald_e_scale", 1.02))
    sup_k_scale = float(dt.get("supersonic_k_scale", 0.95))
    camber_red = float(dt.get("conical_camber_k_reduction", 0.08))

    is_scalar = np.ndim(mach) == 0
    m = np.asarray(mach, dtype=np.float64)

    ar = geom.wing.aspect_ratio
    sweep_le = abs(geom.wing.sweep_le_rad)

    # Raymer empirical Oswald efficiency (Eq. 12.48/12.49) blended with VLM span efficiency
    if sweep_le <= math.radians(30.0):
        e_raymer = 1.78 * (1.0 - 0.045 * (ar ** 0.68)) - 0.64
    else:
        e_raymer = 4.61 * (1.0 - 0.045 * (ar ** 0.68)) * ((math.cos(sweep_le)) ** 0.15) - 3.1
    e_raymer = float(np.clip(e_raymer, 0.58, 0.88))
    e_sub = float(np.clip(e_scale * (0.45 * vlm.span_efficiency_vlm + 0.55 * e_raymer), 0.60, 0.90))
    k_100 = 1.0 / (math.pi * ar * e_sub)

    # Leading-edge suction factor s_suction in [0.25, 0.93]: thin/sharp biconvex airfoils lose suction
    r_le_norm = geom.wing.airfoil.r_le_ratio / max(0.010, geom.wing.tc_mean ** 2)
    s_base = float(np.clip(0.38 + 0.52 * min(r_le_norm, 1.05), 0.35, 0.92))
    if geom.wing.has_le_slats or geom.wing.has_le_flaps:
        s_base = min(s_base + 0.08, 0.94)
    if geom.wing.conical_camber and bool(get_tech_value(tech_context, "aero.conical_camber", True)):
        s_base = min(s_base + camber_red, 0.95)

    cla_m = np.asarray(compute_cl_alpha_mach(geom, vlm, m), dtype=np.float64)
    k_zero_suction = 1.0 / np.maximum(cla_m, 1.2)

    # Subsonic K(M): suction degrades gradually as M approaches 0.85
    suction_m = s_base * np.clip(1.0 - 0.35 * np.maximum(m - 0.60, 0.0) / 0.25, 0.55, 1.0)
    k_sub = suction_m * k_100 + (1.0 - suction_m) * k_zero_suction

    # Supersonic K(M) for M >= 1.20 (Raymer Eq. 12.49 bounded against 1/CL_alpha)
    def _sup_k(m_val: np.ndarray) -> np.ndarray:
        b = np.sqrt(np.maximum(m_val ** 2 - 1.0, 0.44))
        denom = np.maximum(4.0 * ar * b - 2.0, 1.5)
        k_ray = sup_k_scale * (ar * (b ** 2) * math.cos(sweep_le)) / denom
        cla_s = np.asarray(compute_cl_alpha_mach(geom, vlm, m_val), dtype=np.float64)
        k_inv_cla = 0.92 / np.maximum(cla_s, 1.0)
        k_out = 0.55 * k_ray + 0.45 * k_inv_cla
        if geom.wing.conical_camber:
            k_out *= 1.0 - 0.5 * camber_red
        return k_out

    k_085 = float(
        (s_base * 0.65) * k_100
        + (1.0 - s_base * 0.65) * (1.0 / float(compute_cl_alpha_mach(geom, vlm, 0.85)))
    )
    k_120 = float(_sup_k(np.array([1.20]))[0])

    res = np.zeros_like(m, dtype=np.float64)
    sub_mask = m <= 0.85
    sup_mask = m >= 1.20
    tr_mask = (~sub_mask) & (~sup_mask)

    if np.any(sub_mask):
        res[sub_mask] = k_sub[sub_mask]
    if np.any(sup_mask):
        res[sup_mask] = _sup_k(m[sup_mask])
    if np.any(tr_mask):
        u = (m[tr_mask] - 0.85) / 0.35
        s = (u ** 2) * (3.0 - 2.0 * u)
        res[tr_mask] = k_085 + (k_120 - k_085) * s

    return float(res) if is_scalar else res


def compute_high_lift_properties(
    geom: DerivedAircraftGeometry,
    vlm: VLMResult,
) -> HighLiftConfigProperties:
    """Compute low-speed clean, takeoff, and landing CL_max and flap/gear drag increments."""
    hl = load_aero_tuning()["high_lift"]
    dt = load_aero_tuning()["drag"]

    cos_qc = max(math.cos(geom.wing.sweep_qc_rad), 0.40)
    cos_le = max(math.cos(geom.wing.sweep_le_rad), 0.35)

    # 1. Clean 3D low-speed CL_max: sweep-corrected 2D section stall + swept LE separation vortex lift
    tip_penalty = float(np.clip(1.05 - 0.10 * max(vlm.tip_stall_index - 1.0, 0.0), 0.82, 1.0))
    cl_max_potential = 0.88 * geom.wing.airfoil.cl_max_low_speed * cos_qc * tip_penalty

    alpha_man_rad = math.radians(float(hl.get("maneuver_aoa_limit_deg", 20.0)))
    alpha_gnd_rad = math.radians(float(hl.get("ground_aoa_limit_deg", 12.2)))
    cla_0 = float(compute_cl_alpha_mach(geom, vlm, 0.20))

    if geom.wing.aspect_ratio <= 3.0 or geom.wing.planform_type == "delta":
        kv = math.pi * float(hl.get("delta_vortex_lift_kp_scale", 0.80))
        cl_vortex_man = (
            cla_0 * math.sin(alpha_man_rad) * (math.cos(alpha_man_rad) ** 2)
            + kv * (math.sin(alpha_man_rad) ** 2) * math.cos(alpha_man_rad)
        )
        # Tailless deltas flare to ~14.4 deg on landing (short aft overhang behind main gear)
        alpha_gnd_delta = math.radians(14.4)
        cl_vortex_gnd = (
            cla_0 * math.sin(alpha_gnd_delta) * (math.cos(alpha_gnd_delta) ** 2)
            + kv * (math.sin(alpha_gnd_delta) ** 2) * math.cos(alpha_gnd_delta)
        )
        cl_max_clean = max(cl_max_potential, cl_vortex_man)
        trim_loss = 0.06 if geom.empennage.tailless else 0.0
        cl_max_gnd_base = max(cl_vortex_gnd - trim_loss, 0.78)
    else:
        # Thin swept wings (tc <= 0.085, sweep >= 30 deg) develop LE separation-bubble vortex lift
        vortex_assist = (
            0.54
            * math.sin(abs(geom.wing.sweep_le_rad))
            * float(np.clip((0.095 - geom.wing.tc_mean) / 0.032, 0.0, 1.0))
        )
        cl_max_clean = cl_max_potential + vortex_assist
        # Ground landing attitude (12.2 deg) limits untrimmed clean lift on high-AR thick straight wings
        cl_at_gnd_aoa = 0.82 * cla_0 * alpha_gnd_rad + 0.08
        cl_max_gnd_base = min(0.92 * cl_max_clean, cl_at_gnd_aoa)

    # 2. Trailing-edge and leading-edge high-lift increments (Raymer Table 12.2)
    # On tailless deltas, TE surfaces are elevons required for pitch trim and cannot be drooped as landing flaps
    f_area = 0.0 if geom.empennage.tailless else geom.wing.flapped_area_ratio
    dcl_te = 0.0
    if geom.wing.has_fowler_flaps:
        dcl_te = float(hl.get("delta_clmax_fowler_flap", 0.76)) * f_area * cos_qc
    elif geom.wing.has_slotted_flaps:
        dcl_te = float(hl.get("delta_clmax_slotted_flap", 0.50)) * f_area * cos_qc
    elif geom.wing.has_plain_flaps:
        dcl_te = float(hl.get("delta_clmax_plain_flap", 0.38)) * f_area * cos_qc

    if geom.wing.has_blown_flaps and not geom.empennage.tailless:
        dcl_te += float(hl.get("delta_clmax_blown_flap_bonus", 0.68)) * max(f_area, 0.55) * cos_qc

    dcl_le = 0.0
    if geom.wing.has_le_slats:
        dcl_le = float(hl.get("delta_clmax_le_slat", 0.22)) * cos_le
    elif geom.wing.has_le_flaps:
        # Full-span LE droop / variable-incidence high-lift assist (e.g., F8U-1, F-105B)
        dcl_le = float(hl.get("delta_clmax_le_flap", 0.20)) * 1.65 * cos_le
    if geom.wing.conical_camber and not geom.empennage.tailless:
        dcl_le += 0.14 * cos_le

    if geom.wing.has_le_slats:
        cl_max_clean += 0.85 * dcl_le

    to_ratio = float(hl.get("takeoff_flap_ratio", 0.60))
    cl_max_takeoff = cl_max_gnd_base + to_ratio * dcl_te + 0.85 * dcl_le
    cl_max_landing = cl_max_gnd_base + dcl_te + dcl_le

    cd0_gear = float(dt.get("landing_gear_cd0_delta", 0.022))
    delta_cd0_to = cd0_gear + 0.015 * f_area * to_ratio
    delta_cd0_ldg = cd0_gear + 0.042 * f_area

    k_clean = float(compute_induced_drag_k(geom, vlm, 0.20))
    return HighLiftConfigProperties(
        cl_max_clean_low_speed=cl_max_clean,
        cl_max_takeoff=cl_max_takeoff,
        cl_max_landing=cl_max_landing,
        delta_cd0_takeoff=delta_cd0_to,
        delta_cd0_landing=delta_cd0_ldg,
        k_takeoff=0.92 * k_clean,
        k_landing=0.88 * k_clean,
    )


def compute_cl_max_mach(
    geom: DerivedAircraftGeometry,
    vlm: VLMResult,
    high_lift: HighLiftConfigProperties,
    mach: NumberOrArray,
) -> NumberOrArray:
    """Compute usable maneuver / buffet-onset maximum lift coefficient CL_max(M) across Mach."""
    hl = load_aero_tuning()["high_lift"]
    m_dip = float(hl.get("transonic_clmax_dip_mach_center", 0.92))
    dip_depth = float(hl.get("transonic_clmax_dip_depth", 0.22))

    is_scalar = np.ndim(mach) == 0
    m = np.asarray(mach, dtype=np.float64)

    cl0 = high_lift.cl_max_clean_low_speed
    # Swept wings and thin wings have a milder transonic shock-buffet dip; slats further mitigate buffet
    sweep_relief = 0.55 * math.sin(abs(geom.wing.sweep_qc_rad))
    slat_relief = 0.25 if geom.wing.has_le_slats else 0.0
    eff_dip = dip_depth * max(1.0 - sweep_relief - slat_relief, 0.35)

    dip_gauss = eff_dip * np.exp(-(((m - m_dip) / 0.14) ** 2))
    # Supersonic AoA-limited + normal-force structural limit decay
    cla_m = np.asarray(compute_cl_alpha_mach(geom, vlm, m), dtype=np.float64)
    alpha_sup_rad = math.radians(16.0)
    cl_sup_cap = cla_m * alpha_sup_rad

    cl_sub_trans = cl0 * (1.0 - dip_gauss)
    sup_blend = np.clip((m - 0.95) / 0.35, 0.0, 1.0)
    cl_max = np.minimum((1.0 - sup_blend) * cl_sub_trans + sup_blend * cl_sup_cap, cl0 * 1.05)
    cl_max = np.clip(cl_max, 0.35, 2.20)
    return float(cl_max) if is_scalar else cl_max


def compute_total_drag_cd(
    geom: DerivedAircraftGeometry,
    vlm: VLMResult,
    wave_summary: WaveDragSummary,
    mach: NumberOrArray,
    alt_m: NumberOrArray,
    cl: NumberOrArray,
    tech_context: Any = None,
    include_drop_tanks: bool = False,
    include_combat_stores: bool = False,
) -> NumberOrArray:
    """Compute total drag coefficient CD(M, h, CL) = CD0_sub(M, h) + CD_wave(M, CL) + K(M) * CL^2."""
    is_scalar = np.ndim(mach) == 0 and np.ndim(alt_m) == 0 and np.ndim(cl) == 0
    cd0 = compute_cd0_subsonic(
        geom,
        mach,
        alt_m,
        tech_context=tech_context,
        include_drop_tanks=include_drop_tanks,
        include_combat_stores=include_combat_stores,
    )
    cdw = compute_wave_drag_cdw(geom, wave_summary, mach, cl=cl)
    k = compute_induced_drag_k(geom, vlm, mach, tech_context=tech_context)
    cl_arr = np.asarray(cl, dtype=np.float64)
    cd_total = cd0 + cdw + k * (cl_arr ** 2)
    return float(cd_total) if is_scalar else cd_total
