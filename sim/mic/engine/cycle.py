"""Parametric on-design and off-design gas-turbine cycle model (Mattingly style).

Supports:
- Centrifugal single-spool turbojets (e.g. J33, VK-1)
- Axial single-spool fixed-stator turbojets (e.g. J35, J47, J65, J71, J73, RD-9B)
- Axial single-spool variable-stator (VSV) turbojets (e.g. J79)
- Axial twin-spool turbojets (e.g. J57, J75)
- Low-bypass mixed-flow turbofans (bypass_ratio > 0)
- Afterburning + variable nozzle (convergent or convergent-divergent)
- Cooled HP turbine blades and airframe blown-flap bleed

References:
- Mattingly, Heiser, Pratt (2002), *Aircraft Engine Design*, 2nd ed., AIAA, Ch. 2, 4, 5, 8.
- MIL-E-5007D inlet pressure recovery schedule.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from ._atmosphere_stub import P0_STD, T0_STD, get_atmosphere
from .tuning import load_engine_tuning


@dataclass
class EngineDesignInput:
    """Parametric design point input for an engine at Sea-Level Static (M=0, h=0)."""

    engine_id: str
    name: str
    compressor_type: str = "axial"  # "centrifugal" | "axial"
    spools: int = 1  # 1 | 2
    variable_stators: bool = False
    has_afterburner: bool = False
    nozzle_type: str = "convergent"  # "convergent" | "convergent_divergent"
    mass_flow_kgps: float = 42.0
    opr: float = 5.35
    tit_K: float = 1117.0
    ab_temp_K: float = 0.0
    bypass_ratio: float = 0.0
    cooled_turbine: bool = False
    eta_c_poly: float = 0.84
    eta_t_poly: float = 0.86
    eta_burner: Optional[float] = None
    pi_burner: Optional[float] = None
    eta_ab: Optional[float] = None
    pi_ab_dry: Optional[float] = None
    pi_ab_wet: Optional[float] = None
    nozzle_cv: Optional[float] = None
    bleed_fraction: float = 0.0
    specific_weight_factor: float = 1.0
    mtbf_factor: float = 1.0
    length_factor: float = 1.0
    diameter_factor: float = 1.0
    cumulative_test_hours: float = 1000.0
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CyclePointResult:
    """Thermodynamic state and performance at a single operating point."""

    mach: float
    alt_m: float
    throttle: float
    ab: bool
    thrust_N: float
    tsfc_kg_per_Ns: float
    fuel_flow_kgps: float
    mass_flow_kgps: float
    opr_actual: float
    tt2_K: float
    pt2_Pa: float
    tt3_K: float
    pt3_Pa: float
    tt4_K: float
    tt5_K: float
    tt7_K: float
    npr: float
    v9_eff_mps: float
    f_core: float
    f_ab: float
    pi_d: float


@dataclass
class OnDesignReference:
    """Reference on-design parameters solved at SLS (M=0, h=0, dry max)."""

    design: EngineDesignInput
    tau_c_R: float
    tau_cL_R: float
    tau_cH_R: float
    pi_c_R: float
    pi_cL_R: float
    pi_cH_R: float
    tau_t_R: float
    tau_tH_R: float
    tau_tL_R: float
    pi_t_R: float
    tt4_eff_R: float
    f_R: float
    eps_cool: float
    eps_bleed: float
    pi_d_R: float
    sls_dry: CyclePointResult
    sls_ab: Optional[CyclePointResult]


def compute_inlet_recovery(
    mach: float,
    compressor_type: str = "axial",
    inlet_type: str = "mil_spec",
    inlet_location: str = "nose",
    variable_inlet: bool = False,
    spike_inlet: bool = False,
    recovery_bonus: float = 0.0,
    uninstalled_bellmouth: bool = False,
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute total pressure ratio pi_d = Pt2 / Pt0."""
    t = tuning or load_engine_tuning()
    thermo = t["thermo"]
    inlet_cfg = t["inlet"]

    plenum_factor = (
        thermo["pi_centrifugal_plenum"]
        if compressor_type == "centrifugal"
        else 1.0
    )

    if uninstalled_bellmouth:
        return 1.0 * plenum_factor

    if inlet_type == "mil_spec":
        pi_d_sub = 0.985
    else:
        loc_map = {
            "nose": inlet_cfg["pi_d_subsonic_nose"],
            "cheek": inlet_cfg["pi_d_subsonic_cheek"],
            "chin": inlet_cfg["pi_d_subsonic_chin"],
            "wing_root": inlet_cfg["pi_d_subsonic_wing_root"],
        }
        pi_d_sub = loc_map.get(inlet_location, inlet_cfg["pi_d_subsonic_nose"])

    pi_d_sub = min(inlet_cfg["pi_d_max_clamp"], pi_d_sub + recovery_bonus)

    m = max(0.0, float(mach))
    if m <= 1.0:
        eta_r = 1.0
    else:
        gamma = thermo["gamma_c"]
        if inlet_type == "mil_spec" or variable_inlet or inlet_type == "variable":
            # MIL-E-5007D supersonic recovery
            eta_r = max(0.20, 1.0 - 0.075 * ((m - 1.0) ** 1.35))
        elif spike_inlet or inlet_type == "spike":
            # Fixed conical/oblique + weaker normal shock
            slope = inlet_cfg["spike_mach_eff_slope"]
            m_eff = 1.0 + slope * (m - 1.0)
            term1 = ((gamma + 1.0) * m_eff * m_eff / ((gamma - 1.0) * m_eff * m_eff + 2.0)) ** (
                gamma / (gamma - 1.0)
            )
            term2 = ((gamma + 1.0) / (2.0 * gamma * m_eff * m_eff - (gamma - 1.0))) ** (
                1.0 / (gamma - 1.0)
            )
            eta_r = 0.99 * term1 * term2
        else:
            # Pitot / normal shock intake
            term1 = ((gamma + 1.0) * m * m / ((gamma - 1.0) * m * m + 2.0)) ** (
                gamma / (gamma - 1.0)
            )
            term2 = ((gamma + 1.0) / (2.0 * gamma * m * m - (gamma - 1.0))) ** (
                1.0 / (gamma - 1.0)
            )
            eta_r = term1 * term2

    return max(0.15, pi_d_sub * eta_r * plenum_factor)


def solve_on_design(
    design: EngineDesignInput,
    uninstalled_bellmouth: bool = True,
    tuning: Optional[Dict[str, Any]] = None,
) -> OnDesignReference:
    """Solve on-design cycle at Sea-Level Static (M=0, h=0)."""
    t = tuning or load_engine_tuning()
    th = t["thermo"]

    gamma_c = th["gamma_c"]
    cp_c = th["cp_c_J_per_kgK"]
    gamma_t = th["gamma_t"]
    cp_t = th["cp_t_J_per_kgK"]
    h_pr = th["fuel_lhv_J_per_kg"]
    eta_b = design.eta_burner if design.eta_burner is not None else th["eta_burner_default"]
    pi_b = design.pi_burner if design.pi_burner is not None else th["pi_burner_default"]
    eta_m = th["eta_mech_default"]

    # Cooling and airframe bleed fractions
    if design.cooled_turbine:
        eps_cool = th["cooling_bleed_base"] + th["cooling_bleed_per_K_above_1150"] * max(
            0.0, design.tit_K - 1150.0
        )
    else:
        eps_cool = 0.0
    eps_bleed = max(0.0, min(0.15, design.bleed_fraction))
    beta_core = max(0.5, 1.0 - eps_cool - eps_bleed)

    # Inlet at SLS
    pi_d_R = compute_inlet_recovery(
        0.0,
        compressor_type=design.compressor_type,
        uninstalled_bellmouth=uninstalled_bellmouth,
        tuning=t,
    )
    tt2_R = T0_STD
    pt2_R = P0_STD * pi_d_R

    # Compressor on-design
    pi_c_R = max(1.2, float(design.opr))
    e_c = max(0.65, min(0.95, float(design.eta_c_poly)))
    e_t = max(0.65, min(0.95, float(design.eta_t_poly)))

    if design.spools == 2:
        s_lp = th["twin_spool_lp_opr_exponent"]
        pi_cL_R = pi_c_R ** s_lp
        pi_cH_R = pi_c_R ** (1.0 - s_lp)
    else:
        pi_cL_R = pi_c_R
        pi_cH_R = 1.0

    tau_cL_R = pi_cL_R ** ((gamma_c - 1.0) / (gamma_c * e_c))
    tau_cH_R = pi_cH_R ** ((gamma_c - 1.0) / (gamma_c * e_c))
    tau_c_R = tau_cL_R * tau_cH_R

    tt3_R = tt2_R * tau_c_R
    pt3_R = pt2_R * pi_c_R

    # Burner on-design (enthalpy relative to T0_STD, mean cp_b = 0.5*(cp_c + cp_t))
    cp_b = 0.5 * (cp_c + cp_t)
    tt4_R = float(design.tit_K)
    f_core_R = max(
        0.001,
        cp_b * (tt4_R - tt3_R) / (eta_b * h_pr - cp_t * (tt4_R - T0_STD)),
    )
    f_R = beta_core * f_core_R

    # Mix turbine cooling bleed back in for effective turbine inlet temperature
    m_turb_ratio_R = 1.0 - eps_bleed + f_R
    tt4_eff_R = (
        beta_core * (1.0 + f_core_R) * tt4_R + eps_cool * (cp_c / cp_t) * tt3_R
    ) / m_turb_ratio_R

    # Turbine work balance
    bpr = max(0.0, float(design.bypass_ratio))
    # Fan uses LP compressor ratio if bpr > 0
    tau_f_R = tau_cL_R if bpr > 0.0 else 1.0

    if design.spools == 2:
        # HP turbine drives HP compressor (from Tt25 = Tt2 * tau_cL_R)
        work_hp = cp_c * tt2_R * tau_cL_R * (tau_cH_R - 1.0)
        work_lp = cp_c * tt2_R * ((tau_cL_R - 1.0) + bpr * (tau_f_R - 1.0))
        denom = eta_m * m_turb_ratio_R * cp_t * tt4_eff_R
        tau_tH_R = max(0.45, 1.0 - work_hp / denom)
        tt45_R = tt4_eff_R * tau_tH_R
        tau_tL_R = max(0.45, 1.0 - work_lp / (eta_m * m_turb_ratio_R * cp_t * tt45_R))
        tau_t_R = tau_tH_R * tau_tL_R
    else:
        work_total = cp_c * tt2_R * ((tau_c_R - 1.0) + bpr * (tau_f_R - 1.0))
        denom = eta_m * m_turb_ratio_R * cp_t * tt4_eff_R
        tau_t_R = max(0.40, 1.0 - work_total / denom)
        tau_tH_R = tau_t_R
        tau_tL_R = 1.0

    pi_t_R = tau_t_R ** (gamma_t / ((gamma_t - 1.0) * e_t))

    ref = OnDesignReference(
        design=design,
        tau_c_R=tau_c_R,
        tau_cL_R=tau_cL_R,
        tau_cH_R=tau_cH_R,
        pi_c_R=pi_c_R,
        pi_cL_R=pi_cL_R,
        pi_cH_R=pi_cH_R,
        tau_t_R=tau_t_R,
        tau_tH_R=tau_tH_R,
        tau_tL_R=tau_tL_R,
        pi_t_R=pi_t_R,
        tt4_eff_R=tt4_eff_R,
        f_R=f_R,
        eps_cool=eps_cool,
        eps_bleed=eps_bleed,
        pi_d_R=pi_d_R,
        sls_dry=None,  # type: ignore
        sls_ab=None,
    )

    sls_dry = evaluate_cycle_at_tt4(
        ref,
        mach=0.0,
        alt_m=0.0,
        tt4_K=design.tit_K,
        ab=False,
        tt7_K=0.0,
        uninstalled_bellmouth=uninstalled_bellmouth,
        tuning=t,
    )
    sls_ab: Optional[CyclePointResult] = None
    if design.has_afterburner and design.ab_temp_K > design.tit_K:
        sls_ab = evaluate_cycle_at_tt4(
            ref,
            mach=0.0,
            alt_m=0.0,
            tt4_K=design.tit_K,
            ab=True,
            tt7_K=design.ab_temp_K,
            uninstalled_bellmouth=uninstalled_bellmouth,
            tuning=t,
        )

    ref.sls_dry = sls_dry
    ref.sls_ab = sls_ab
    return ref


def _nozzle_effective_velocity(
    pt9_Pa: float,
    tt9_K: float,
    p0_Pa: float,
    gamma_9: float,
    cp_9: float,
    nozzle_type: str,
    cv: float,
    condiv_max_npr: float,
) -> Tuple[float, float]:
    """Compute effective exhaust velocity V9_eff = Cv * [V9 + (P9 - P0)*A9/m9] and NPR."""
    r_9 = cp_9 * (gamma_9 - 1.0) / gamma_9
    npr = max(1.0001, pt9_Pa / p0_Pa)
    pi_crit = ((gamma_9 + 1.0) / 2.0) ** (gamma_9 / (gamma_9 - 1.0))

    if nozzle_type == "convergent_divergent" and npr > pi_crit:
        npr_eff = min(npr, condiv_max_npr)
        v_ideal = math.sqrt(
            max(0.0, 2.0 * cp_9 * tt9_K * (1.0 - (1.0 / npr_eff) ** ((gamma_9 - 1.0) / gamma_9)))
        )
        # Residual under-expansion above condiv_max_npr
        if npr > condiv_max_npr:
            t9 = tt9_K * ((1.0 / condiv_max_npr) ** ((gamma_9 - 1.0) / gamma_9))
            v_ideal += (r_9 * t9 / max(100.0, v_ideal)) * (1.0 - condiv_max_npr / npr)
        return cv * v_ideal, npr

    # Convergent nozzle
    if npr <= pi_crit:
        # Unchoked: P9 = P0
        m9_sq = max(0.0, (2.0 / (gamma_9 - 1.0)) * (npr ** ((gamma_9 - 1.0) / gamma_9) - 1.0))
        t9 = tt9_K / (1.0 + 0.5 * (gamma_9 - 1.0) * m9_sq)
        v9 = math.sqrt(m9_sq * gamma_9 * r_9 * t9)
        return cv * v9, npr
    else:
        # Choked at M9 = 1.0
        t9 = (2.0 / (gamma_9 + 1.0)) * tt9_K
        v9 = math.sqrt(gamma_9 * r_9 * t9)
        # Pressure thrust contribution per unit mass flow: (V9 / gamma_9) * (1 - pi_crit / NPR)
        v9_eff = v9 + (v9 / gamma_9) * (1.0 - pi_crit / npr)
        return cv * v9_eff, npr


def max_available_tt4(
    ref: OnDesignReference,
    mach: float,
    alt_m: float,
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Return governor-limited maximum Tt4 [K] at (mach, alt_m).

    Captures both:
    1. Cold-inlet aerodynamic/mechanical spool overspeed limit (theta_0 < theta_break),
       preventing OPR from exceeding off_design_max_opr_overshoot * OPR_R.
    2. Hot-inlet turbine material temperature limit Tt4 <= Tt4_R (theta_0 >= theta_break).
    """
    t = tuning or load_engine_tuning()
    th = t["thermo"]
    atm = get_atmosphere(alt_m)
    gamma_c = th["gamma_c"]
    tau_r = 1.0 + 0.5 * (gamma_c - 1.0) * (mach ** 2)
    tt2 = atm.T_K * tau_r

    # Max OPR cap from mechanical spool speed / aerodynamic stall limit
    e_c = ref.design.eta_c_poly
    max_opr = ref.pi_c_R * th["off_design_max_opr_overshoot"]
    max_tau_c = max_opr ** ((gamma_c - 1.0) / (gamma_c * e_c))

    # From (tau_c - 1) / (tau_c_R - 1) = (Tt4 / Tt2) / (Tt4_R / Tt2_R):
    ratio_max = (max_tau_c - 1.0) / max(1e-6, ref.tau_c_R - 1.0)
    tt4_spool_limit = ref.design.tit_K * (tt2 / T0_STD) * ratio_max

    # Material limit is design.tit_K
    return min(ref.design.tit_K, tt4_spool_limit)


def evaluate_cycle_at_tt4(
    ref: OnDesignReference,
    mach: float,
    alt_m: float,
    tt4_K: float,
    ab: bool = False,
    tt7_K: float = 0.0,
    inlet_type: str = "mil_spec",
    inlet_location: str = "nose",
    variable_inlet: bool = False,
    spike_inlet: bool = False,
    recovery_bonus: float = 0.0,
    uninstalled_bellmouth: bool = False,
    tuning: Optional[Dict[str, Any]] = None,
) -> CyclePointResult:
    """Evaluate off-design cycle at given flight condition and combustor exit temperature Tt4."""
    t = tuning or load_engine_tuning()
    th = t["thermo"]
    design = ref.design

    atm = get_atmosphere(alt_m)
    t0 = atm.T_K
    p0 = atm.P_Pa
    v0 = mach * atm.a_mps

    gamma_c = th["gamma_c"]
    cp_c = th["cp_c_J_per_kgK"]
    gamma_t = th["gamma_t"]
    cp_t = th["cp_t_J_per_kgK"]
    gamma_ab = th["gamma_ab"]
    cp_ab = th["cp_ab_J_per_kgK"]
    cp_b = 0.5 * (cp_c + cp_t)
    h_pr = th["fuel_lhv_J_per_kg"]

    eta_b = design.eta_burner if design.eta_burner is not None else th["eta_burner_default"]
    pi_b = design.pi_burner if design.pi_burner is not None else th["pi_burner_default"]
    eta_ab = design.eta_ab if design.eta_ab is not None else th["eta_ab_default"]

    # Station 0 -> 2
    tau_r = 1.0 + 0.5 * (gamma_c - 1.0) * (mach ** 2)
    pi_r = tau_r ** (gamma_c / (gamma_c - 1.0))
    tt2 = t0 * tau_r
    pi_d = compute_inlet_recovery(
        mach,
        compressor_type=design.compressor_type,
        inlet_type=inlet_type,
        inlet_location=inlet_location,
        variable_inlet=variable_inlet,
        spike_inlet=spike_inlet,
        recovery_bonus=recovery_bonus,
        uninstalled_bellmouth=uninstalled_bellmouth,
        tuning=t,
    )
    pt2 = p0 * pi_r * pi_d

    # Off-design compressor temperature ratio from choked turbine relation
    # Use iterative 2-step update for tt4_eff coupling with tt3
    e_c = design.eta_c_poly
    beta_core = max(0.5, 1.0 - ref.eps_cool - ref.eps_bleed)

    tt4_eff_est = tt4_K * (ref.tt4_eff_R / design.tit_K)
    for _ in range(2):
        tau_c = 1.0 + (ref.tau_c_R - 1.0) * ((tt4_eff_est / tt2) / (ref.tt4_eff_R / T0_STD))
        tau_c = max(1.02, tau_c)
        tt3 = tt2 * tau_c
        f_core = max(
            0.0005,
            cp_b * max(1.0, tt4_K - tt3) / (eta_b * h_pr - cp_t * (tt4_K - T0_STD)),
        )
        f = beta_core * f_core
        m_turb_ratio = 1.0 - ref.eps_bleed + f
        tt4_eff_est = (
            beta_core * (1.0 + f_core) * tt4_K + ref.eps_cool * (cp_c / cp_t) * tt3
        ) / m_turb_ratio

    pi_c = tau_c ** (gamma_c * e_c / (gamma_c - 1.0))
    pt3 = pt2 * pi_c
    pt4 = pt3 * pi_b

    # Choked HP turbine throat scaling for physical mass flow
    delta_0 = (p0 * pi_r) / P0_STD
    mdot_0 = (
        design.mass_flow_kgps
        * delta_0
        * (pi_d / ref.pi_d_R)
        * (pi_c / ref.pi_c_R)
        * math.sqrt(ref.tt4_eff_R / max(300.0, tt4_eff_est))
        * ((1.0 - ref.eps_bleed + ref.f_R) / m_turb_ratio)
    )

    # Station 4 -> 5 (choked turbine => tau_t = tau_t_R, pi_t = pi_t_R)
    tt5 = tt4_eff_est * ref.tau_t_R
    pt5 = pt4 * ref.pi_t_R

    # Tailpipe / Afterburner -> Nozzle
    if design.nozzle_cv is not None:
        cv = design.nozzle_cv
    else:
        cv = (
            th["nozzle_cv_condiv"]
            if design.nozzle_type == "convergent_divergent"
            else th["nozzle_cv_convergent"]
        )

    use_ab = bool(ab and design.has_afterburner and tt7_K > tt5 + 10.0)
    if use_ab:
        pi_ab_w = design.pi_ab_wet if design.pi_ab_wet is not None else th["pi_ab_duct_wet"]
        pt9 = pt5 * pi_ab_w * th["pi_nozzle_dry"]
        tt7 = max(tt5 + 10.0, float(tt7_K))
        f_ab = m_turb_ratio * max(
            0.0,
            cp_ab * (tt7 - tt5) / (eta_ab * h_pr - cp_ab * (tt7 - T0_STD)),
        )
        gamma_9 = gamma_ab
        cp_9 = cp_ab
    else:
        if design.has_afterburner:
            pi_ab_d = design.pi_ab_dry if design.pi_ab_dry is not None else th["pi_ab_duct_dry"]
        else:
            pi_ab_d = 1.0
        pt9 = pt5 * pi_ab_d * th["pi_nozzle_dry"]
        tt7 = tt5
        f_ab = 0.0
        gamma_9 = gamma_t
        cp_9 = cp_t

    v9_eff, npr = _nozzle_effective_velocity(
        pt9_Pa=pt9,
        tt9_K=tt7,
        p0_Pa=p0,
        gamma_9=gamma_9,
        cp_9=cp_9,
        nozzle_type=design.nozzle_type,
        cv=cv,
        condiv_max_npr=th["condiv_max_npr"],
    )

    f_tot = f + f_ab
    m_exit_ratio = 1.0 - ref.eps_bleed + f_tot

    # Bypass stream thrust if low-bypass turbofan
    bpr = max(0.0, float(design.bypass_ratio))
    if bpr > 0.0:
        s_lp = th["twin_spool_lp_opr_exponent"]
        pi_f = pi_c ** s_lp
        tau_f = pi_f ** ((gamma_c - 1.0) / (gamma_c * e_c))
        pt19 = pt2 * pi_f * th["pi_nozzle_dry"]
        tt19 = tt2 * tau_f
        v19_eff, _ = _nozzle_effective_velocity(
            pt9_Pa=pt19,
            tt9_K=tt19,
            p0_Pa=p0,
            gamma_9=gamma_c,
            cp_9=cp_c,
            nozzle_type="convergent",
            cv=th["nozzle_cv_convergent"],
            condiv_max_npr=th["condiv_max_npr"],
        )
    else:
        v19_eff = 0.0

    # Net thrust
    specific_thrust = m_exit_ratio * v9_eff - (1.0 + bpr) * v0 + bpr * v19_eff
    thrust_N = max(0.0, mdot_0 * specific_thrust)
    fuel_flow_kgps = mdot_0 * f_tot
    tsfc = fuel_flow_kgps / max(1.0, thrust_N)

    return CyclePointResult(
        mach=mach,
        alt_m=alt_m,
        throttle=1.0,
        ab=use_ab,
        thrust_N=thrust_N,
        tsfc_kg_per_Ns=tsfc,
        fuel_flow_kgps=fuel_flow_kgps,
        mass_flow_kgps=mdot_0,
        opr_actual=pi_c,
        tt2_K=tt2,
        pt2_Pa=pt2,
        tt3_K=tt3,
        pt3_Pa=pt3,
        tt4_K=tt4_K,
        tt5_K=tt5,
        tt7_K=tt7,
        npr=npr,
        v9_eff_mps=v9_eff,
        f_core=f,
        f_ab=f_ab,
        pi_d=pi_d,
    )


def evaluate_off_design_point(
    ref: OnDesignReference,
    mach: float,
    alt_m: float,
    throttle: float = 1.0,
    ab: bool = False,
    inlet_type: str = "mil_spec",
    inlet_location: str = "nose",
    variable_inlet: bool = False,
    spike_inlet: bool = False,
    recovery_bonus: float = 0.0,
    uninstalled_bellmouth: bool = False,
    tuning: Optional[Dict[str, Any]] = None,
) -> CyclePointResult:
    """Evaluate engine performance at (mach, alt_m, throttle in [0,1], ab).

    - When ab=False: throttle in [0, 1] scales dry thrust linearly:
      F(throttle) = throttle * F_dry_max(mach, alt_m).
      For throttle >= 0.1, Tt4 is solved by fixed-iteration bisection so that
      the cycle produces F(throttle) and authentic part-power TSFC (including
      the classic SFC bucket around 75-85% thrust at subsonic cruise).
    - When ab=True (and engine has_afterburner): throttle in [0, 1] interpolates
      thrust linearly between military thrust (F_dry_max at throttle=0) and
      maximum afterburning thrust (F_ab_max at throttle=1), with Tt7 solved to match.
    """
    t = tuning or load_engine_tuning()
    th = t["thermo"]
    thr = max(0.0, min(1.0, float(throttle)))

    tt4_max = max_available_tt4(ref, mach, alt_m, tuning=t)
    mil_pt = evaluate_cycle_at_tt4(
        ref,
        mach=mach,
        alt_m=alt_m,
        tt4_K=tt4_max,
        ab=False,
        tt7_K=0.0,
        inlet_type=inlet_type,
        inlet_location=inlet_location,
        variable_inlet=variable_inlet,
        spike_inlet=spike_inlet,
        recovery_bonus=recovery_bonus,
        uninstalled_bellmouth=uninstalled_bellmouth,
        tuning=t,
    )

    if ab and ref.design.has_afterburner and ref.design.ab_temp_K > mil_pt.tt5_K + 20.0:
        ab_max_pt = evaluate_cycle_at_tt4(
            ref,
            mach=mach,
            alt_m=alt_m,
            tt4_K=tt4_max,
            ab=True,
            tt7_K=ref.design.ab_temp_K,
            inlet_type=inlet_type,
            inlet_location=inlet_location,
            variable_inlet=variable_inlet,
            spike_inlet=spike_inlet,
            recovery_bonus=recovery_bonus,
            uninstalled_bellmouth=uninstalled_bellmouth,
            tuning=t,
        )
        if thr >= 0.999:
            return ab_max_pt
        if thr <= 0.001:
            return CyclePointResult(
                **{**mil_pt.__dict__, "throttle": thr, "ab": True}
            )
        target_f = mil_pt.thrust_N + thr * (ab_max_pt.thrust_N - mil_pt.thrust_N)
        lo_t7 = mil_pt.tt5_K + 15.0
        hi_t7 = ref.design.ab_temp_K
        mid_pt = ab_max_pt
        for _ in range(32):
            mid_t7 = 0.5 * (lo_t7 + hi_t7)
            mid_pt = evaluate_cycle_at_tt4(
                ref,
                mach=mach,
                alt_m=alt_m,
                tt4_K=tt4_max,
                ab=True,
                tt7_K=mid_t7,
                inlet_type=inlet_type,
                inlet_location=inlet_location,
                variable_inlet=variable_inlet,
                spike_inlet=spike_inlet,
                recovery_bonus=recovery_bonus,
                uninstalled_bellmouth=uninstalled_bellmouth,
                tuning=t,
            )
            if mid_pt.thrust_N < target_f:
                lo_t7 = mid_t7
            else:
                hi_t7 = mid_t7
        tsfc_val = mid_pt.fuel_flow_kgps / max(1.0, target_f)
        return CyclePointResult(
            **{
                **mid_pt.__dict__,
                "throttle": thr,
                "ab": True,
                "thrust_N": target_f,
                "tsfc_kg_per_Ns": tsfc_val,
            }
        )

    # Dry operation (or AB requested on a non-AB engine -> falls back to dry)
    if thr >= 0.999:
        return mil_pt

    f_max = mil_pt.thrust_N
    target_f = thr * f_max

    if f_max <= 1.0:
        return CyclePointResult(
            **{
                **mil_pt.__dict__,
                "throttle": thr,
                "ab": False,
                "thrust_N": 0.0,
            }
        )

    # Solve for part-power Tt4 down to effective throttle floor (0.10)
    eff_thr = max(0.10, thr)
    eff_target_f = eff_thr * f_max
    lo_t4 = max(mil_pt.tt2_K + 80.0, 0.48 * tt4_max)
    hi_t4 = tt4_max
    mid_pt = mil_pt
    for _ in range(36):
        mid_t4 = 0.5 * (lo_t4 + hi_t4)
        mid_pt = evaluate_cycle_at_tt4(
            ref,
            mach=mach,
            alt_m=alt_m,
            tt4_K=mid_t4,
            ab=False,
            tt7_K=0.0,
            inlet_type=inlet_type,
            inlet_location=inlet_location,
            variable_inlet=variable_inlet,
            spike_inlet=spike_inlet,
            recovery_bonus=recovery_bonus,
            uninstalled_bellmouth=uninstalled_bellmouth,
            tuning=t,
        )
        if mid_pt.thrust_N < eff_target_f:
            lo_t4 = mid_t4
        else:
            hi_t4 = mid_t4

    if thr >= 0.10:
        # Add parasitic accessory/mechanical drag loss at low part-power so TSFC shows realistic bucket around 0.75-0.85 throttle and rises near idle
        part_power_penalty = 1.0 + 0.06 * ((1.0 - thr) ** 2) / max(0.15, thr)
        fuel_flow = mid_pt.fuel_flow_kgps * part_power_penalty
        tsfc_val = fuel_flow / max(1.0, target_f)
    else:
        # Below 0.10 throttle, interpolate fuel flow to idle fuel flow
        idle_ff = th["idle_fuel_flow_fraction_of_mil"] * mil_pt.fuel_flow_kgps
        ff_10 = mid_pt.fuel_flow_kgps * (1.0 + 0.06 * (0.9 ** 2) / 0.15)
        fuel_flow = idle_ff + (thr / 0.10) * max(0.0, ff_10 - idle_ff)
        denom_f = max(th["min_effective_throttle_for_tsfc"] * f_max, target_f, 1.0)
        tsfc_val = fuel_flow / denom_f

    return CyclePointResult(
        **{
            **mid_pt.__dict__,
            "throttle": thr,
            "ab": False,
            "thrust_N": target_f,
            "fuel_flow_kgps": fuel_flow,
            "tsfc_kg_per_Ns": tsfc_val,
        }
    )
