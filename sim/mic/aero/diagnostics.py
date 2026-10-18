"""Aerodynamic, stability, aeroelastic, and handling-qualities diagnostics for Module 01 & Module 06.

Computes the rich `aero_diagnostics` dictionary consumed by Module 06 (Testing, Wind Tunnel,
Flight Test, and Hidden Flaw generation) and Module 08 (Design Editor warnings/readouts).

References:
- Shortal & Maggin, "Effect of Sweepback and Aspect Ratio on Longitudinal Stability Characteristics
  of Wings at High Subsonic Speeds", NACA TN 2388 (1951).
- Phillips, "Effect of Steady Rolling on Longitudinal and Directional Stability", NACA TN 1627 (1948).
- Raymer, "Aircraft Design: A Conceptual Approach", 5th Ed., Ch. 4 & Ch. 16.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from ..atmosphere import dynamic_pressure_Pa, recovery_temperature_K
from .drag import HighLiftConfigProperties, WaveDragSummary, compute_mdd_and_mcrit
from .geometry import DerivedAircraftGeometry, get_tech_value
from .mass import MassBreakdown
from .tuning import load_aero_tuning
from .vlm import VLMResult, compute_cl_alpha_mach


def compute_aero_diagnostics(
    geom: DerivedAircraftGeometry,
    vlm: VLMResult,
    wave_summary: WaveDragSummary,
    high_lift: HighLiftConfigProperties,
    mass: MassBreakdown,
    max_mach_sl: float,
    max_mach_alt: float,
    alt_of_max_mach_m: float,
    tech_context: Any = None,
) -> Dict[str, Any]:
    """Compute comprehensive stability, aeroelastic, and handling diagnostics."""
    tuning = load_aero_tuning()
    pt = tuning["propulsion_install"]

    # 1. Longitudinal Static Margin & Mach Tuck
    cla_w_sub = float(compute_cl_alpha_mach(geom, vlm, 0.50))
    cla_w_sup = float(compute_cl_alpha_mach(geom, vlm, 1.40))

    # Destabilizing fuselage pitching-moment shift (Munk / Multhopp approximation)
    vol_fus = geom.fuselage.internal_volume_m3
    dx_ac_fus_mac = -1.65 * vol_fus / max(geom.wing.area_m2 * geom.wing.mac_m * cla_w_sub, 0.5)
    dx_ac_fus_mac = float(max(min(dx_ac_fus_mac, -0.02), -0.18))

    # Horizontal tail lift-curve slope and contribution
    if not geom.empennage.tailless and geom.empennage.ht_area_m2 > 0.05:
        ar_ht = geom.empennage.ht_aspect_ratio
        cla_ht_sub = (2.0 * math.pi * ar_ht) / (2.0 + math.sqrt(4.0 + ar_ht ** 2 * 0.85))
        cla_ht_sup = 3.6 / math.sqrt(1.40 ** 2 - 1.0)
        eta_h = 0.96 if geom.empennage.t_tail else 0.90
        vh = geom.empennage.ht_volume_coeff
        deps_sub = vlm.downwash_gradient_subsonic
        deps_sup = 0.35 * deps_sub
        dx_ac_ht_sub = eta_h * vh * (cla_ht_sub / max(cla_w_sub, 1.0)) * (1.0 - deps_sub)
        dx_ac_ht_sup = eta_h * vh * (cla_ht_sup / max(cla_w_sup, 1.0)) * (1.0 - deps_sup)
    else:
        dx_ac_ht_sub = 0.0
        dx_ac_ht_sup = 0.0

    # Wing AC shifts from ~x_ac_mac_frac (~0.25) subsonic to ~0.46 MAC supersonic
    x_ac_w_sub = vlm.x_ac_mac_frac
    x_ac_w_sup = x_ac_w_sub + 0.20

    np_sub_mac = x_ac_w_sub + dx_ac_fus_mac + dx_ac_ht_sub
    np_sup_mac = x_ac_w_sup + 0.65 * dx_ac_fus_mac + dx_ac_ht_sup

    # Align nominal wing placement CG reference so a balanced conventional fighter has SM_sub ~ +0.05 to +0.10 MAC
    sm_sub_mac = np_sub_mac - mass.x_cg_combat_mac_frac
    sm_sup_mac = np_sup_mac - mass.x_cg_combat_mac_frac
    ac_shift_mach_tuck = np_sup_mac - np_sub_mac

    # 2. Pitch-up Tendency (Shortal-Maggin Boundary + Tail Wake Immersion + Tip Stall)
    sweep_deg = abs(geom.wing.sweep_qc_deg)
    taper = geom.wing.taper_ratio
    # Shortal-Maggin critical aspect ratio (NACA TN 2388): wings with AR > AR_crit pitch up at stall
    ar_crit_sm = 8.4 * math.exp(-0.0225 * sweep_deg) * (0.84 + 0.26 * taper)
    if geom.wing.has_le_slats:
        ar_crit_sm += 1.15
    elif geom.wing.has_le_flaps:
        ar_crit_sm += 0.65
    sm_ratio = geom.wing.aspect_ratio / max(ar_crit_sm, 1.0)

    # Tail wake immersion AoA: angle of attack where wing wake sheet hits the horizontal tail plane
    if geom.empennage.tailless:
        tail_wake_alpha_deg = 90.0
    else:
        dz_over_l = geom.empennage.ht_z_m / max(geom.empennage.ht_arm_m, 1.0)
        one_minus_deps = max(1.0 - vlm.downwash_gradient_subsonic, 0.35)
        alpha_wake_rad = math.atan(dz_over_l) / one_minus_deps
        tail_wake_alpha_deg = float(min(max(math.degrees(alpha_wake_rad), 4.0), 42.0))

    # T-tail wake immersion in 12 - 20 deg stall window (e.g. F-101 Voodoo / F-104) strongly amplifies pitch-up
    wake_in_stall_window = 1.0 if (11.0 <= tail_wake_alpha_deg <= 22.0 and not geom.empennage.tailless) else 0.0
    pitch_up_risk = max(0.0, (sm_ratio - 0.88) * 1.35 + 0.45 * wake_in_stall_window + 0.25 * max(vlm.tip_stall_index - 1.25, 0.0))
    deep_stall_risk = (
        max(0.0, 0.75 * wake_in_stall_window + 0.55 * (1.0 if geom.empennage.t_tail else 0.0) + 0.30 * max(sm_ratio - 0.95, 0.0))
        if geom.empennage.t_tail
        else 0.05
    )

    # 3. Roll/Yaw Inertia Ratio & Directional Stability (Phillips Inertia Coupling)
    iyy_ixx = mass.iyy_combat_kgm2 / max(mass.ixx_combat_kgm2, 100.0)
    izz_ixx = mass.izz_combat_kgm2 / max(mass.ixx_combat_kgm2, 100.0)
    inertia_diff_param = (mass.izz_combat_kgm2 - mass.ixx_combat_kgm2) / max(mass.iyy_combat_kgm2, 100.0)

    ar_vt = geom.empennage.vt_aspect_ratio
    cla_vt_sub = (2.0 * math.pi * ar_vt) / (2.0 + math.sqrt(4.0 + ar_vt ** 2 * 0.90))
    m_eval_sup = max(max_mach_alt, 1.35)
    cla_vt_sup = 3.4 / math.sqrt(max(m_eval_sup ** 2 - 1.0, 0.45))

    vv = geom.empennage.vt_volume_coeff
    cn_beta_fus = -1.3 * (geom.fuselage.internal_volume_m3 / max(geom.wing.area_m2 * geom.wing.span_m, 1.0)) * (
        geom.fuselage.max_diameter_m / max(geom.fuselage.length_m, 1.0)
    )
    cn_beta_sub = vv * cla_vt_sub * 0.92 + cn_beta_fus
    cn_beta_sup = vv * cla_vt_sup * 0.82 + cn_beta_fus

    # Phillips roll-coupling risk increases with high Iyy/Ixx, low supersonic Cn_beta, and high speed
    sas_relief = 0.55 if geom.stability_augmentation else 1.00
    roll_coupling_index = (
        sas_relief
        * (iyy_ixx / 4.2)
        * inertia_diff_param
        * (0.095 / max(cn_beta_sup, 0.018))
    )

    # 4. Wing Torsional Stiffness Proxy, Aileron Reversal, and Flutter
    # Material elastic modulus ratio relative to Al 7075
    e_mod_ratio = (
        1.00 * geom.material_al_frac
        + 2.80 * geom.material_steel_frac
        + 1.55 * geom.material_ti_frac
    )
    cos_qc = max(math.cos(geom.wing.sweep_qc_rad), 0.40)
    stiffness_proxy = (
        e_mod_ratio
        * ((geom.wing.tc_mean / 0.09) ** 2.6)
        * ((4.5 / max(geom.wing.aspect_ratio, 1.5)) ** 1.35)
        * (cos_qc ** 1.6)
    )
    # Calibrated so a thin swept wing (e.g. 9% t/c, 35 deg sweep, AR=4.8) has q_rev ~ 95 kPa (~M0.95 SL)
    q_reversal_pa = 86000.0 * stiffness_proxy * (1.25 if geom.powered_controls else 0.85)
    q_max_op_pa = float(dynamic_pressure_Pa(max_mach_sl, 0.0))
    q_margin_reversal = q_reversal_pa / max(q_max_op_pa, 1000.0)

    # Transonic flutter dip factor around M=0.92 - 1.05
    transonic_exposure = 1.25 if max_mach_sl >= 0.88 else 1.0
    flutter_margin_index = (math.sqrt(stiffness_proxy) * 1.35) / max(
        (max_mach_sl / 0.88) * transonic_exposure, 0.4
    )

    # 5. Transonic Control Loss (Mach tuck without all-moving tail or hydraulic controls)
    if max_mach_alt >= 0.88:
        tail_pen = 0.0 if (geom.empennage.all_moving_tail or geom.empennage.tailless) else 0.85
        hyd_pen = 0.0 if geom.powered_controls else 0.75
        transonic_control_loss_risk = (tail_pen + hyd_pen) * ((max_mach_alt - 0.84) / 0.16)
    else:
        transonic_control_loss_risk = 0.05

    # 6. Drag Divergence Margin & Inlet / Thermal Margins
    mdd_cruise, mcrit_cruise = compute_mdd_and_mcrit(geom, 0.25)
    mdd_margin_m085 = float(mdd_cruise) - 0.85

    if geom.intake_compression == "variable_ramp" or geom.intake_variable:
        inlet_eff_max_mach = 2.50
    elif geom.intake_compression == "fixed_spike" or geom.intake_spike:
        inlet_eff_max_mach = 1.95
    else:
        inlet_eff_max_mach = 1.40
    inlet_mach_margin = inlet_eff_max_mach - max_mach_alt

    base_skin_limit_K = float(get_tech_value(tech_context, "struct.max_skin_temp_K", 410.0))
    max_allowed_skin_temp_K = (
        base_skin_limit_K
        + geom.material_ti_frac * float(pt.get("ti_skin_temp_bonus_K_per_fraction", 260.0))
        + geom.material_steel_frac * float(pt.get("steel_skin_temp_bonus_K_per_fraction", 340.0))
    )
    r_fac = float(pt.get("recovery_factor_turbulent", 0.89))
    skin_temp_at_max_K = float(recovery_temperature_K(max_mach_alt, alt_of_max_mach_m, recovery_factor=r_fac))
    # Solve for thermal limit Mach at 11,000 m tropopause (T = 216.65 K)
    t_tropo = 216.65
    thermal_limit_mach = math.sqrt(
        max((max_allowed_skin_temp_K / t_tropo - 1.0) / (0.2 * r_fac), 1.0)
    )

    # 7. Spin & Dutch Roll Indices
    unshielded_rudder = 0.80 if geom.empennage.t_tail else 0.52
    spin_departure_index = (
        0.55 * vlm.tip_stall_index
        + 0.45 * inertia_diff_param
        - 0.35 * (unshielded_rudder * (vv / 0.068))
    )
    # Swept wings have strong dihedral effect -Cl_beta proportional to CL * sin(2*Lambda)
    cl_beta_eff = 0.25 * math.sin(2.0 * abs(geom.wing.sweep_qc_rad)) - 0.018 * geom.wing.dihedral_deg
    dutch_roll_index = sas_relief * max(cl_beta_eff, 0.02) / max(cn_beta_sub, 0.025)

    fuel_vol_margin = (geom.max_fuel_capacity_kg - geom.internal_fuel_kg) / max(geom.max_fuel_capacity_kg, 1.0)

    return {
        "neutral_point_subsonic_mac": float(np_sub_mac),
        "neutral_point_supersonic_mac": float(np_sup_mac),
        "static_margin_subsonic_mac": float(sm_sub_mac),
        "static_margin_supersonic_mac": float(sm_sup_mac),
        "ac_shift_mach_tuck_mac": float(ac_shift_mach_tuck),
        "shortal_maggin_ar_crit": float(ar_crit_sm),
        "shortal_maggin_ratio": float(sm_ratio),
        "tail_wake_immersion_alpha_deg": float(tail_wake_alpha_deg),
        "vlm_tip_stall_index": float(vlm.tip_stall_index),
        "pitch_up_risk_score": float(pitch_up_risk),
        "deep_stall_risk_score": float(deep_stall_risk),
        "inertia_ratio_iyy_ixx": float(iyy_ixx),
        "inertia_ratio_izz_ixx": float(izz_ixx),
        "cn_beta_subsonic_per_rad": float(cn_beta_sub),
        "cn_beta_supersonic_per_rad": float(cn_beta_sup),
        "roll_coupling_phillips_index": float(roll_coupling_index),
        "horizontal_tail_volume_coeff": float(geom.empennage.ht_volume_coeff),
        "vertical_tail_volume_coeff": float(geom.empennage.vt_volume_coeff),
        "wing_torsional_stiffness_proxy": float(stiffness_proxy),
        "q_reversal_pa": float(q_reversal_pa),
        "q_max_operating_pa": float(q_max_op_pa),
        "q_margin_to_aileron_reversal": float(q_margin_reversal),
        "flutter_margin_index": float(flutter_margin_index),
        "transonic_control_loss_risk": float(transonic_control_loss_risk),
        "mdd_at_cruise_cl": float(mdd_cruise),
        "mcrit_at_cruise_cl": float(mcrit_cruise),
        "mdd_margin_at_m085": float(mdd_margin_m085),
        "ewd_wave_drag_efficiency": float(wave_summary.ewd_factor),
        "area_rule_drag_reduction_ratio": float(wave_summary.area_rule_drag_reduction_ratio),
        "inlet_mach_margin": float(inlet_mach_margin),
        "thermal_limit_mach": float(thermal_limit_mach),
        "skin_temp_at_max_mach_K": float(skin_temp_at_max_K),
        "max_allowed_skin_temp_K": float(max_allowed_skin_temp_K),
        "spin_departure_index": float(spin_departure_index),
        "dutch_roll_index": float(dutch_roll_index),
        "fuel_volume_margin_ratio": float(fuel_vol_margin),
        # Cross-module canonical aliases consumed by Module 06 (`sim/mic/testing/features.py`)
        "shortal_maggin_excess": float(geom.wing.aspect_ratio - ar_crit_sm),
        "m_dd": float(mdd_cruise),
        "mach_dd_excess": float(max(0.0, max_mach_alt - float(mdd_cruise))),
        "wave_drag_ewd": float(wave_summary.ewd_factor),
        "wave_drag_ratio": float(wave_summary.cd_wave_m12 / 0.015),
        "cd_wave_peak": float(wave_summary.cd_wave_m12),
        "ac_shift_mac": float(ac_shift_mach_tuck),
        "inertia_coupling_index": float(roll_coupling_index),
        "torsion_flex_index": float(1.0 / max(stiffness_proxy, 0.05)),
    }
