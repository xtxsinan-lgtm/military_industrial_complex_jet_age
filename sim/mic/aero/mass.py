"""Aircraft mass breakdown, CG, and Moments of Inertia (I_xx, I_yy, I_zz) for Module 01.

Implements Raymer's Fighter/Attack Statistical Group Weight Equations (Raymer, "Aircraft Design:
A Conceptual Approach", 5th Ed., Ch. 15, Eq. 15.1 - 15.22) with fixed-point iteration on
Design Gross Weight (W_dg), material-mix scaling (`al`, `steel`, `ti`), `TechContext` structural
and avionics factors, and component longitudinal CG & inertia estimation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Dict

from .geometry import DerivedAircraftGeometry, get_tech_value
from .tuning import load_aero_tuning

# Exact unit conversion constants (00_conventions.md §3)
FT_TO_M: float = 0.3048
M_TO_FT: float = 1.0 / FT_TO_M
M2_TO_FT2: float = M_TO_FT ** 2
LB_TO_KG: float = 0.45359237
KG_TO_LB: float = 1.0 / LB_TO_KG
LBF_TO_N: float = 4.4482216152605
N_TO_LBF: float = 1.0 / LBF_TO_N


@dataclass(frozen=True)
class MassBreakdown:
    """Complete mass, payload, fuel, CG, and inertia breakdown in SI units."""

    wing_kg: float
    empennage_kg: float
    fuselage_kg: float
    landing_gear_kg: float
    propulsion_dry_engines_kg: float
    propulsion_install_and_inlet_kg: float
    fuel_system_kg: float
    flight_controls_and_hydraulics_kg: float
    electrical_and_instruments_kg: float
    avionics_and_radar_kg: float
    furnishings_and_equipment_kg: float
    fixed_guns_dry_kg: float
    empty_mass_kg: float
    crew_mass_kg: float
    gun_ammo_mass_kg: float
    ordnance_mass_kg: float
    payload_kg: float
    internal_fuel_kg: float
    external_drop_tank_fuel_kg: float
    external_drop_tank_shells_kg: float
    combat_mass_kg: float
    design_gross_mass_kg: float
    landing_mass_kg: float
    mtow_kg: float
    x_cg_empty_m: float
    x_cg_combat_m: float
    x_cg_combat_mac_frac: float
    ixx_combat_kgm2: float
    iyy_combat_kgm2: float
    izz_combat_kgm2: float
    component_masses_kg: Dict[str, float] = field(repr=False)


def compute_mass_breakdown(
    geom: DerivedAircraftGeometry,
    engine_mass_kg: float,
    engine_max_thrust_sl_N: float,
    engine_diameter_m: float = 0.95,
    tech_context: Any = None,
) -> MassBreakdown:
    """Compute empty mass, combat mass, MTOW, CG, and moments of inertia via fixed-point iteration."""
    tuning = load_aero_tuning()
    mt = tuning["mass"]
    mis = tuning["mission"]
    cat = tuning["catalog_defaults"]

    # 1. Tech & material factors
    struct_tech_factor = float(get_tech_value(tech_context, "struct.weight_factor", 1.0))
    carrier_tech_factor = float(get_tech_value(tech_context, "struct.carrier_weight_factor", 1.0))
    radar_mass_factor = float(get_tech_value(tech_context, "avionics.radar_mass_factor", 1.0))

    mat_factor = (
        geom.material_al_frac * float(mt.get("material_factor_al", 1.00))
        + geom.material_steel_frac * float(mt.get("material_factor_steel", 1.14))
        + geom.material_ti_frac * float(mt.get("material_factor_ti", 0.86))
    )
    primary_struct_scale = struct_tech_factor * mat_factor * float(mt.get("empty_mass_global_scale", 0.965))

    # 2. Fixed payload, guns, crew, and avionics masses
    crew_kg = geom.crew_count * float(mt.get("crew_mass_per_person_kg", 95.0))

    guns_dry_kg = 0.0
    gun_ammo_kg = 0.0
    for g_spec in geom.guns:
        gid = str(g_spec.get("gun_id", "m3_50"))
        g_cnt = int(g_spec.get("count", 0))
        g_info = cat["guns"].get(
            gid, {"gun_mass_kg": 30.0, "ammo_mass_per_round_kg": 0.12, "default_rounds": 300}
        )
        rounds = int(g_spec.get("rounds_per_gun", g_spec.get("rounds", g_info["default_rounds"])))
        # Gun + feed chutes/mount (~1.25x bare gun weight) in empty mass
        guns_dry_kg += g_cnt * float(g_info["gun_mass_kg"]) * 1.25
        gun_ammo_kg += g_cnt * rounds * float(g_info["ammo_mass_per_round_kg"])

    ordnance_kg = geom.combat_external_stores_kg
    for mid in geom.missile_ids:
        m_info = cat["missiles"].get(mid, {"mass_kg": 70.0})
        ordnance_kg += float(m_info["mass_kg"])

    payload_kg = crew_kg + gun_ammo_kg + ordnance_kg

    # Avionics & radar mass
    av_levels = mt.get("avionics_base_mass_by_level_kg", [35.0, 95.0, 165.0, 290.0, 480.0, 720.0])
    av_base_kg = float(av_levels[min(max(geom.avionics_level, 0), len(av_levels) - 1)])
    radar_kg = 0.0
    if geom.radar_id:
        r_info = cat["radars"].get(str(geom.radar_id), {"mass_kg": 150.0})
        radar_kg += float(r_info["mass_kg"])
    if geom.fire_control_id and geom.fire_control_id != geom.radar_id:
        f_info = cat["radars"].get(str(geom.fire_control_id), {"mass_kg": 120.0})
        radar_kg += float(f_info["mass_kg"])
    avionics_total_kg = (av_base_kg + radar_kg) * radar_mass_factor

    # Cockpit & furnishings mass
    furnish_kg = 55.0 * geom.crew_count
    if geom.ejection_seat:
        furnish_kg += geom.crew_count * float(mt.get("ejection_seat_mass_kg", 48.0))
    if geom.pressurized_cockpit:
        furnish_kg += float(mt.get("pressurization_mass_kg", 42.0)) * (1.0 + 0.25 * (geom.crew_count - 1))
    if geom.inflight_refuel:
        furnish_kg += float(mt.get("inflight_refuel_probe_mass_kg", 38.0))

    # Dry engines mass
    dry_engines_kg = geom.engine_count * max(engine_mass_kg, 150.0)

    # Convert geometric parameters to US units for Raymer Ch. 15 statistical formulas
    s_w_ft2 = geom.wing.area_m2 * M2_TO_FT2
    s_ht_ft2 = geom.empennage.ht_area_m2 * M2_TO_FT2
    s_vt_ft2 = geom.empennage.vt_area_m2 * M2_TO_FT2
    l_fus_ft = geom.fuselage.length_m * M_TO_FT
    d_fus_ft = geom.fuselage.max_diameter_m * M_TO_FT
    l_vt_ft = max(geom.empennage.vt_arm_m * M_TO_FT, 6.0)
    l_d_ft = max(geom.intake_duct_length_m * M_TO_FT, 4.0)
    d_eng_ft = max(engine_diameter_m * M_TO_FT, 1.8)
    n_z = geom.ultimate_load_factor_g
    cos_qc = max(math.cos(geom.wing.sweep_qc_rad), 0.38)
    cos_vt = max(math.cos(geom.empennage.vt_sweep_qc_rad), 0.40)

    t_tot_lbf = max(engine_max_thrust_sl_N * geom.engine_count * N_TO_LBF, 1500.0)
    w_eng_lb = max(engine_mass_kg * KG_TO_LB, 350.0)

    # Fixed-point iteration on Design Gross Weight W_dg (combat weight = empty + 50% internal fuel + payload)
    combat_fuel_frac = float(mis.get("combat_fuel_fraction_internal", 0.50))
    w_dg_kg = 2.1 * (dry_engines_kg + geom.internal_fuel_kg * combat_fuel_frac + payload_kg + 1200.0)

    wing_kg = 0.0
    emp_kg = 0.0
    fus_kg = 0.0
    gear_kg = 0.0
    prop_inst_kg = 0.0
    fuel_sys_kg = 0.0
    fc_hyd_kg = 0.0
    elec_inst_kg = 0.0

    for _ in range(12):
        w_dg_lb = max(w_dg_kg * KG_TO_LB, 3000.0)

        # 2.1 Wing weight (Raymer Eq. 15.1 adapted with smooth low-AR / delta correction)
        k_dw = 0.85 if geom.wing.planform_type == "delta" else 1.00
        k_vs = float(mt.get("variable_sweep_wing_penalty", 1.18)) if geom.wing.planform_type == "variable_sweep" else 1.00
        k_slat = 1.045 if geom.wing.has_le_slats else 1.00
        s_csw_ft2 = max(0.14 * s_w_ft2, 10.0)
        w_wing_lb = (
            0.0103
            * k_dw
            * k_vs
            * k_slat
            * ((w_dg_lb * n_z) ** 0.50)
            * (s_w_ft2 ** 0.622)
            * (geom.wing.aspect_ratio ** 0.785)
            * (max(geom.wing.tc_root, 0.032) ** -0.40)
            * ((1.0 + geom.wing.taper_ratio) ** 0.05)
            * (cos_qc ** -1.0)
            * (s_csw_ft2 ** 0.04)
        )
        wing_carrier_mul = (
            1.0 + (float(mt.get("carrier_structure_multiplier", 1.055)) - 1.0) * carrier_tech_factor
            if geom.carrier_capable
            else 1.0
        )
        wing_kg = (
            w_wing_lb
            * LB_TO_KG
            * float(mt.get("wing_weight_scale", 0.92))
            * primary_struct_scale
            * wing_carrier_mul
        )

        # 2.2 Empennage weight (Raymer Eq. 15.2 & 15.3)
        if geom.empennage.ht_area_m2 > 0.05:
            fw_over_bh = min(geom.fuselage.max_diameter_m / max(geom.empennage.ht_span_m, 1.2), 0.45)
            w_ht_lb = (
                3.316
                * ((1.0 + fw_over_bh) ** -2.0)
                * ((w_dg_lb * n_z / 1000.0) ** 0.260)
                * (s_ht_ft2 ** 0.806)
            )
            if geom.empennage.all_moving_tail:
                w_ht_lb *= float(mt.get("all_moving_tail_weight_multiplier", 1.10))
        else:
            w_ht_lb = 0.0

        k_rht = 1.047 if geom.empennage.all_moving_tail else 1.0
        ht_over_hv = 0.95 if geom.empennage.t_tail else 0.10
        m_design = 1.8 if geom.afterburner else 1.05
        w_vt_lb = (
            0.452
            * k_rht
            * ((1.0 + ht_over_hv) ** 0.50)
            * ((w_dg_lb * n_z) ** 0.488)
            * (s_vt_ft2 ** 0.718)
            * (m_design ** 0.341)
            * (l_vt_ft ** -1.0)
            * (1.30 ** 0.348)
            * (geom.empennage.vt_aspect_ratio ** 0.223)
            * ((1.0 + geom.empennage.vt_taper_ratio) ** 0.25)
            * (cos_vt ** -0.323)
        )
        if geom.empennage.t_tail:
            w_vt_lb *= float(mt.get("ttail_vertical_weight_multiplier", 1.15))

        emp_kg = (
            (w_ht_lb + w_vt_lb)
            * LB_TO_KG
            * float(mt.get("tail_weight_scale", 0.95))
            * primary_struct_scale
        )

        # 2.3 Fuselage weight (Raymer Eq. 15.4 / Roskam Part V buried-engine fighter correlation)
        k_dwf = 0.76 if geom.wing.planform_type == "delta" else 1.00
        # Twin-engine fuselages have lower length-to-volume structural penalty per engine than single-engine buried ducts
        twin_fus_relief = 0.78 if geom.engine_count > 1 else 1.00
        compact_relief = 0.86 if (geom.fuselage.length_m < 10.4 and geom.avionics_level <= 1) else 1.00
        w_fus_lb = (
            0.96
            * k_dwf
            * twin_fus_relief
            * compact_relief
            * (w_dg_lb ** 0.38)
            * (n_z ** 0.25)
            * (l_fus_ft ** 0.56)
            * (d_fus_ft ** 1.42)
        )
        if geom.fuselage.area_ruled:
            w_fus_lb *= float(mt.get("area_rule_fuselage_weight_penalty", 1.025))
        if geom.internal_bay:
            w_fus_lb *= 1.05
        if geom.carrier_capable:
            w_fus_lb *= 1.0 + (float(mt.get("carrier_structure_multiplier", 1.055)) - 1.0) * carrier_tech_factor

        fus_kg = (
            w_fus_lb
            * LB_TO_KG
            * float(mt.get("fuselage_weight_scale", 0.94))
            * primary_struct_scale
        )
        # Permanent wingtip fuel/rocket pod structural shells & wingtip torsion reinforcement on straight wings (e.g., F-89D, F-84G)
        if abs(geom.wing.sweep_qc_rad) < 0.20 and geom.drop_tank_fuel_kg_each >= 550.0 and geom.drop_tanks_count >= 2:
            fus_kg += 0.48 * geom.drop_tank_fuel_kg_each * geom.drop_tanks_count * struct_tech_factor
        # Full-length flattened nose-intake duct + aft titanium afterburner heat-shield structure (e.g., F-100A)
        if geom.afterburner and geom.intake_type == "nose" and geom.fuselage.length_m >= 13.5:
            fus_kg += 520.0 * struct_tech_factor

        # 2.4 Landing gear weight (Raymer / Roskam Fighter Gear Group: ~4.0-4.4% of design gross weight)
        w_l_lb = 0.90 * w_dg_lb
        n_l = 5.4 if geom.carrier_capable else 3.6
        w_gear_lb = 0.068 * ((w_l_lb * n_l) ** 0.82)
        if geom.carrier_capable:
            w_gear_lb *= 1.0 + (float(mt.get("carrier_gear_multiplier", 1.38)) - 1.0) * carrier_tech_factor
        gear_kg = w_gear_lb * LB_TO_KG * float(mt.get("gear_weight_scale", 0.95)) * struct_tech_factor

        # 2.5 Propulsion installation & air induction duct weight (Raymer Eq. 15.7 - 15.13)
        w_mounts_lb = 0.022 * (geom.engine_count ** 0.795) * (t_tot_lbf ** 0.59) * n_z
        w_sect_lb = 0.018 * (w_eng_lb ** 0.75) * geom.engine_count * n_z
        k_vg = 1.48 if geom.intake_variable else (1.18 if geom.intake_spike else 1.00)
        k_d = 2.60 if geom.intake_type in ("cheek", "wing_root") else 1.90
        w_inlet_lb = (
            18.5
            * k_vg
            * (l_d_ft ** 0.68)
            * (k_d ** 0.182)
            * (geom.engine_count ** 1.05)
            * d_eng_ft
        )
        w_exhaust_start_lb = 6.5 * d_eng_ft * l_d_ft * 0.40 * geom.engine_count + 0.042 * (t_tot_lbf ** 0.80)
        prop_inst_kg = (w_mounts_lb + w_sect_lb + w_inlet_lb + w_exhaust_start_lb) * LB_TO_KG * struct_tech_factor * compact_relief

        # 2.6 Fuel system, flight controls, hydraulics, electrical & instruments
        vt_gal = max(geom.internal_fuel_kg / 0.780 * 0.264172, 60.0)
        w_fuel_sys_lb = 78.0 * ((vt_gal / 100.0) ** 0.64) * (1.0 + 0.10 * (geom.engine_count - 1))
        if geom.drop_tank_fuel_kg_each > 0.0 and geom.drop_tanks_count > 0:
            # Fixed external tank plumbing, fuel transfer pumps, and hardpoint pylons
            w_fuel_sys_lb += 65.0 * geom.drop_tanks_count
        fuel_sys_kg = w_fuel_sys_lb * LB_TO_KG

        fc_base_lb = 68.0 * ((s_w_ft2 / 100.0) ** 0.45) * ((w_dg_lb / 10000.0) ** 0.58)
        if geom.powered_controls:
            fc_base_lb *= 1.38
        if geom.stability_augmentation:
            fc_base_lb += 65.0
        fc_hyd_kg = (fc_base_lb + 65.0 * ((w_dg_lb / 14000.0) ** 0.55)) * LB_TO_KG

        elec_inst_lb = (
            145.0 * ((w_dg_lb / 14000.0) ** 0.55)
            + 55.0 * geom.engine_count
            + 50.0 * geom.crew_count
            + 48.0 * geom.avionics_level
            + 26.0 * geom.hardpoints
        )
        elec_inst_kg = elec_inst_lb * LB_TO_KG

        empty_kg = (
            wing_kg
            + emp_kg
            + fus_kg
            + gear_kg
            + dry_engines_kg
            + prop_inst_kg
            + fuel_sys_kg
            + fc_hyd_kg
            + elec_inst_kg
            + avionics_total_kg
            + furnish_kg
            + guns_dry_kg
        )
        w_dg_new = empty_kg + combat_fuel_frac * geom.internal_fuel_kg + payload_kg
        if abs(w_dg_new - w_dg_kg) < 0.5:
            w_dg_kg = w_dg_new
            break
        w_dg_kg = 0.6 * w_dg_new + 0.4 * w_dg_kg

    empty_mass_kg = (
        wing_kg
        + emp_kg
        + fus_kg
        + gear_kg
        + dry_engines_kg
        + prop_inst_kg
        + fuel_sys_kg
        + fc_hyd_kg
        + elec_inst_kg
        + avionics_total_kg
        + furnish_kg
        + guns_dry_kg
    )
    combat_mass_kg = empty_mass_kg + combat_fuel_frac * geom.internal_fuel_kg + payload_kg
    landing_fuel_frac = float(mis.get("landing_fuel_fraction", 0.45))
    landing_fuel_kg = min(landing_fuel_frac * geom.internal_fuel_kg, 0.14 * empty_mass_kg)
    landing_mass_kg = empty_mass_kg + landing_fuel_kg + crew_kg

    ext_fuel_kg = geom.drop_tanks_count * geom.drop_tank_fuel_kg_each
    ext_shells_kg = 0.085 * ext_fuel_kg
    mtow_kg = empty_mass_kg + geom.internal_fuel_kg + payload_kg + ext_fuel_kg + ext_shells_kg

    # 3. Longitudinal CG and Moments of Inertia (I_xx, I_yy, I_zz)
    l_f = geom.fuselage.length_m
    b_w = geom.wing.span_m

    x_wing = geom.wing.x_mac_le_m + 0.40 * geom.wing.mac_m
    x_emp = min(geom.wing.x_ac_subsonic_m + geom.empennage.vt_arm_m, 0.90 * l_f)
    x_fus = 0.46 * l_f
    x_gear = geom.wing.x_mac_le_m + 0.15 * geom.wing.mac_m
    x_eng = geom.engine_x_cg_m
    x_inlet = 0.35 * l_f if geom.intake_type == "nose" else 0.42 * l_f
    x_sys = 0.42 * l_f
    x_av = 0.18 * l_f
    x_cockpit = 0.24 * l_f
    x_guns = 0.22 * l_f
    x_fuel = 0.55 * x_wing + 0.45 * (0.48 * l_f)

    empty_items = [
        (wing_kg, x_wing, 0.22 * b_w),
        (emp_kg, x_emp, 0.08 * b_w),
        (fus_kg, x_fus, 0.38 * geom.fuselage.max_diameter_m),
        (gear_kg, x_gear, 0.12 * b_w),
        (dry_engines_kg, x_eng, 0.28 * geom.fuselage.max_diameter_m),
        (prop_inst_kg, x_inlet, 0.32 * geom.fuselage.max_diameter_m),
        (fuel_sys_kg + fc_hyd_kg + elec_inst_kg, x_sys, 0.30 * geom.fuselage.max_diameter_m),
        (avionics_total_kg, x_av, 0.25 * geom.fuselage.max_diameter_m),
        (furnish_kg, x_cockpit, 0.25 * geom.fuselage.max_diameter_m),
        (guns_dry_kg, x_guns, 0.25 * geom.fuselage.max_diameter_m),
    ]

    x_cg_empty = sum(m_i * x_i for m_i, x_i, _ in empty_items) / max(empty_mass_kg, 1.0)
    combat_fuel_kg = combat_fuel_frac * geom.internal_fuel_kg
    combat_items = empty_items + [
        (combat_fuel_kg, x_fuel, 0.16 * b_w),
        (crew_kg, x_cockpit, 0.20 * geom.fuselage.max_diameter_m),
        (gun_ammo_kg, x_guns, 0.25 * geom.fuselage.max_diameter_m),
        (ordnance_kg, x_wing, 0.26 * b_w),
    ]
    x_cg_combat = sum(m_i * x_i for m_i, x_i, _ in combat_items) / max(combat_mass_kg, 1.0)
    x_cg_combat_mac = (x_cg_combat - geom.wing.x_mac_le_m) / max(geom.wing.mac_m, 0.1)

    # Moments of inertia around combat CG (combining parallel-axis point masses + distributed fuselage/wing self-inertia)
    ixx_self = (1.0 / 12.0) * wing_kg * ((0.52 * b_w) ** 2) + 0.25 * (fus_kg + dry_engines_kg) * (
        (0.45 * geom.fuselage.max_diameter_m) ** 2
    )
    iyy_self = (1.0 / 12.0) * (fus_kg + prop_inst_kg) * ((0.65 * l_f) ** 2)

    ixx = ixx_self + sum(m_i * (y_i ** 2) for m_i, _, y_i in combat_items)
    iyy = iyy_self + sum(m_i * ((x_i - x_cg_combat) ** 2) for m_i, x_i, _ in combat_items)
    izz = 0.92 * (ixx + iyy)

    comp_dict = {
        "wing_kg": wing_kg,
        "empennage_kg": emp_kg,
        "fuselage_kg": fus_kg,
        "landing_gear_kg": gear_kg,
        "propulsion_dry_engines_kg": dry_engines_kg,
        "propulsion_install_and_inlet_kg": prop_inst_kg,
        "fuel_system_kg": fuel_sys_kg,
        "flight_controls_and_hydraulics_kg": fc_hyd_kg,
        "electrical_and_instruments_kg": elec_inst_kg,
        "avionics_and_radar_kg": avionics_total_kg,
        "furnishings_and_equipment_kg": furnish_kg,
        "fixed_guns_dry_kg": guns_dry_kg,
    }

    return MassBreakdown(
        wing_kg=wing_kg,
        empennage_kg=emp_kg,
        fuselage_kg=fus_kg,
        landing_gear_kg=gear_kg,
        propulsion_dry_engines_kg=dry_engines_kg,
        propulsion_install_and_inlet_kg=prop_inst_kg,
        fuel_system_kg=fuel_sys_kg,
        flight_controls_and_hydraulics_kg=fc_hyd_kg,
        electrical_and_instruments_kg=elec_inst_kg,
        avionics_and_radar_kg=avionics_total_kg,
        furnishings_and_equipment_kg=furnish_kg,
        fixed_guns_dry_kg=guns_dry_kg,
        empty_mass_kg=empty_mass_kg,
        crew_mass_kg=crew_kg,
        gun_ammo_mass_kg=gun_ammo_kg,
        ordnance_mass_kg=ordnance_kg,
        payload_kg=payload_kg,
        internal_fuel_kg=geom.internal_fuel_kg,
        external_drop_tank_fuel_kg=ext_fuel_kg,
        external_drop_tank_shells_kg=ext_shells_kg,
        combat_mass_kg=combat_mass_kg,
        design_gross_mass_kg=w_dg_kg,
        landing_mass_kg=landing_mass_kg,
        mtow_kg=mtow_kg,
        x_cg_empty_m=x_cg_empty,
        x_cg_combat_m=x_cg_combat,
        x_cg_combat_mac_frac=x_cg_combat_mac,
        ixx_combat_kgm2=ixx,
        iyy_combat_kgm2=iyy,
        izz_combat_kgm2=izz,
        component_masses_kg=comp_dict,
    )
