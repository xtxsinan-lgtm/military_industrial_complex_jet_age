"""Unified feature vector, physics diagnostics fallbacks, and TechContext adapter."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_TECH_EFFECT_VALUES: Dict[str, Any] = {
    "aero.all_moving_tail": False,
    "aero.t_tail": True,
    "aero.area_rule": False,
    "aero.wave_drag_area_rule_eff": 0.0,
    "aero.le_slats": False,
    "aero.le_flaps": False,
    "aero.blown_flaps": False,
    "aero.fowler_flaps": True,
    "aero.inlet_spike": False,
    "aero.inlet_variable": False,
    "struct.material.titanium_available": False,
    "struct.honeycomb": False,
    "avionics.reliability_factor": 1.0,
    "systems.powered_controls": False,
    "systems.stability_augmentation": False,
    "systems.ejection_seat": False,
    "systems.pressurized_cockpit": True,
    "testing.transonic_tunnel": False,
    "testing.supersonic_tunnel": True,
    "testing.rocket_model_testing": False,
    "testing.sim_sigma_factor": 1.0,
    "testing.tunnel_sigma_factor": 1.0,
    "testing.flight_sigma_factor": 1.0,
    "testing.sim_time_factor": 1.0,
    "testing.flight_test_time_factor": 1.0,
    "testing.flaw_detect_factor": 1.0,
    "testing.flaw_incidence.flutter": 1.0,
    "testing.flaw_incidence.aileron_reversal": 1.0,
    "testing.flaw_incidence.transonic_control_loss": 1.0,
    "testing.flaw_incidence.pitch_up": 1.0,
    "testing.flaw_incidence.inertia_coupling": 1.0,
    "testing.flaw_incidence.spin": 1.0,
    "testing.flaw_incidence.inlet": 1.0,
    "testing.flaw_incidence.engine_stall": 1.0,
    "testing.flaw_incidence.structural_fatigue": 1.0,
    "testing.flaw_incidence.systems": 1.0,
    "testing.flaw_incidence.manufacturing": 1.0,
    "mfg.quality_defect_factor": 1.0,
}


class StubTechContext:
    """Self-contained TechContext conforming to `03_tech_effect_keys.md` §1."""

    def __init__(
        self,
        date_day: int = 0,
        company_id: str = "player_co",
        overrides: Optional[Dict[str, Any]] = None,
        tech_maturity: Optional[Dict[str, float]] = None,
    ) -> None:
        self.date_day = int(date_day)
        self.company_id = str(company_id)
        self.values: Dict[str, Any] = dict(DEFAULT_TECH_EFFECT_VALUES)
        if overrides:
            self.values.update(overrides)
        self.tech_maturity: Dict[str, float] = dict(tech_maturity or {})

    def get(self, key: str) -> Any:
        if key not in self.values:
            if key.startswith("testing.flaw_incidence."):
                return 1.0
            raise KeyError(f"Unknown tech effect key: {key}")
        return self.values[key]

    def maturity_of(self, key: str) -> float:
        return float(self.tech_maturity.get(key, 1.0))


def build_feature_vector(
    design: Dict[str, Any],
    nominal_perf: Dict[str, Any],
    aero_diagnostics: Optional[Dict[str, Any]] = None,
    engine_diagnostics: Optional[Dict[str, Any]] = None,
    tech_ctx: Optional[Any] = None,
) -> Dict[str, float]:
    """Assemble the flat numeric FeatureVector (§5.2) from design & diagnostics."""
    ctx = tech_ctx if tech_ctx is not None else StubTechContext()
    aero_diag = aero_diagnostics or {}
    eng_diag = engine_diagnostics or {}

    wing = design.get("wing", {})
    fus = design.get("fuselage", {})
    emp = design.get("empennage", {})
    intake = design.get("intake", {})
    prop = design.get("propulsion", {})
    struct = design.get("structure", {})
    fuel = design.get("fuel", {})
    systems = design.get("systems", {})
    arm = design.get("armament", {})

    sweep_deg = float(wing.get("sweep_deg", wing.get("sweep", 0.0)))
    ar = float(wing.get("aspect_ratio", wing.get("aspect", 5.0)))
    taper = float(wing.get("taper_ratio", wing.get("taper", 0.5)))
    tc_ratio = float(wing.get("tc_ratio", wing.get("t_c", 0.10)))
    wing_area_m2 = float(wing.get("area_m2", wing.get("area", 25.0)))
    span_m = math.sqrt(max(1.0, ar * wing_area_m2))
    planform = str(wing.get("planform", "conventional")).lower()
    is_delta = 1.0 if (planform == "delta" or bool(wing.get("is_delta", False))) else 0.0

    devices = [str(d).lower() for d in wing.get("devices", [])]
    has_le_slats = 1.0 if ("slats" in devices or "le_slats" in devices or bool(wing.get("has_le_slats", False))) else 0.0
    has_le_flaps = 1.0 if ("le_flaps" in devices or "droop_le" in devices) else 0.0
    has_wing_fences = 1.0 if ("wing_fences" in devices or "fences" in devices or bool(wing.get("has_wing_fences", False))) else 0.0
    has_sawtooth_le = 1.0 if ("sawtooth" in devices or "dogtooth" in devices or bool(wing.get("has_sawtooth_le", False))) else 0.0
    has_blown_flaps = 1.0 if ("blown_flaps" in devices or bool(wing.get("has_blown_flaps", False))) else 0.0

    fus_len_m = float(fus.get("length_m", fus.get("length", 12.0)))
    fus_diam_m = float(fus.get("max_diameter_m", fus.get("max_diameter", 1.4)))
    is_area_ruled = 1.0 if bool(fus.get("area_ruled", False)) else 0.0
    fuselage_fineness = fus_len_m / max(0.4, fus_diam_m)
    fuselage_to_span_ratio = fus_len_m / max(2.0, span_m)

    is_t_tail = 1.0 if bool(emp.get("t_tail", False)) else 0.0
    has_all_moving_tail = 1.0 if bool(emp.get("all_moving_tail", ctx.get("aero.all_moving_tail"))) else 0.0
    vv = float(emp.get("vertical_tail_volume", emp.get("vv", 0.065)))
    vh = float(emp.get("horizontal_tail_volume", emp.get("vh", 0.45)))

    intake_type = str(intake.get("type", "nose")).lower()
    non_nose_intake = 0.0 if intake_type == "nose" else 1.0
    is_variable_intake = 1.0 if bool(intake.get("variable", False)) else 0.0

    has_afterburner = 1.0 if bool(prop.get("afterburner", False)) else 0.0
    engine_count = float(prop.get("count", 1))

    design_load_factor_g = float(struct.get("design_load_factor_g", 7.33))
    mat_mix = struct.get("material_mix", {})
    ti_fraction = float(mat_mix.get("ti", 0.0))
    carrier_capable = 1.0 if bool(struct.get("carrier_capable", False)) else 0.0
    has_honeycomb = 1.0 if bool(struct.get("honeycomb", ctx.get("struct.honeycomb"))) else 0.0

    has_powered_controls = 1.0 if bool(systems.get("powered_controls", ctx.get("systems.powered_controls"))) else 0.0
    has_dual_hydraulics = 1.0 if int(systems.get("hydraulic_redundancy", 1)) >= 2 else 0.0
    has_sas = 1.0 if bool(systems.get("stability_augmentation", ctx.get("systems.stability_augmentation"))) else 0.0
    has_ejection_seat = 1.0 if bool(systems.get("ejection_seat", ctx.get("systems.ejection_seat"))) else 0.0
    has_radar = 1.0 if bool(systems.get("radar_id")) else 0.0
    avionics_level = float(systems.get("avionics_level", 1))

    guns = arm.get("guns", [])
    has_guns = 1.0 if (len(guns) > 0 or bool(arm.get("has_guns", True))) else 0.0
    gun_caliber_mm = float(arm.get("gun_caliber_mm", 20.0 if any("20mm" in str(g) for g in guns) else 12.7))
    guns_near_intake = 1.0 if bool(arm.get("guns_near_intake", intake_type in ("nose", "chin") and has_guns > 0.5)) else 0.0
    hardpoints = float(arm.get("hardpoints", 2))

    max_mach_alt = float(nominal_perf.get("max_mach_alt", 0.85))
    max_mach_sl = float(nominal_perf.get("max_mach_sl", min(max_mach_alt, 0.82)))
    max_mach_nom = max(max_mach_alt, max_mach_sl)
    service_ceiling_nom_m = float(nominal_perf.get("service_ceiling_m", 12500.0))
    empty_mass_kg = float(nominal_perf.get("empty_mass_kg", 4500.0))
    mtow_kg = float(nominal_perf.get("mtow_kg", empty_mass_kg * 1.45))
    internal_fuel_kg = float(nominal_perf.get("internal_fuel_kg", fuel.get("internal_kg", empty_mass_kg * 0.35)))
    wing_loading_kgm2 = float(nominal_perf.get("wing_loading_combat_kgm2", (empty_mass_kg + 0.5 * internal_fuel_kg) / max(5.0, wing_area_m2)))

    # 1. Shortal-Maggin Pitch-Up Excess (§5.2.1)
    ar_crit = 5.8 * math.exp(-0.0365 * sweep_deg) * (1.0 + 0.35 * (taper - 0.5))
    shortal_maggin_excess = float(aero_diag.get("shortal_maggin_excess", ar - ar_crit))

    # 2. Korn Drag-Divergence Mach & Excess (§5.2.2)
    sweep_rad = math.radians(min(70.0, max(0.0, sweep_deg)))
    cos_sw = max(0.35, math.cos(sweep_rad))
    m_dd_fallback = (0.87 / cos_sw) - (tc_ratio / (cos_sw * cos_sw)) - (0.20 / (10.0 * (cos_sw ** 3)))
    m_dd = float(aero_diag.get("m_dd", m_dd_fallback))
    mach_dd_excess = float(aero_diag.get("mach_dd_excess", max_mach_nom - m_dd))

    # 3. Wave-drag area-rule ratio (§5.2.3)
    ar_eff = max(0.5, float(ctx.get("aero.wave_drag_area_rule_eff"))) if is_area_ruled > 0.5 else 0.0
    wd_fallback = max(
        1.05,
        2.35
        * (1.0 - 0.55 * is_area_ruled * ar_eff)
        * ((max(0.03, tc_ratio) / 0.06) ** 0.35)
        * (((1.0 / max(4.0, fuselage_fineness)) / 0.10) ** 0.25),
    )
    wave_drag_ratio = float(aero_diag.get("wave_drag_ratio", wd_fallback))

    # 4. Transonic aerodynamic center shift (§5.2.4)
    ac_shift_fallback = 0.14 * max(0.0, min(1.0, (max_mach_nom - 0.80) / 0.35)) * (1.0 + 0.30 * is_delta)
    ac_shift_mac = float(aero_diag.get("ac_shift_mac", ac_shift_fallback))

    # 5. Dynamic pressure at dive & aeroelastic torsion flex index (§5.2.6)
    a_sl = 340.294
    rho_sl = 1.225
    v_dive = 1.15 * max_mach_sl * a_sl
    q_dive_kpa = 0.5 * rho_sl * v_dive * v_dive / 1000.0
    torsion_fallback = (q_dive_kpa / 100.0) * (ar ** 1.5) / (((10.0 * max(0.035, tc_ratio)) ** 2) * (cos_sw * cos_sw))
    torsion_flex_index = float(aero_diag.get("torsion_flex_index", torsion_fallback))

    # 6. Phillips Roll-Inertia Coupling Index (§5.2.5)
    ic_fallback = (fuselage_to_span_ratio ** 2) * max(0.7, max_mach_nom) / (10.0 * max(0.03, vv))
    inertia_coupling_index = float(aero_diag.get("inertia_coupling_index", ic_fallback))

    # 7. Engine diagnostics (§5.2.7)
    engine_maturity = float(eng_diag.get("engine_maturity", 0.75))
    engine_immaturity = max(0.0, 1.0 - engine_maturity)
    compressor_stall_margin = float(eng_diag.get("compressor_stall_margin", 0.15))
    stall_margin_deficit = max(0.0, 0.18 - compressor_stall_margin)
    flameout_alt_margin_m = float(eng_diag.get("flameout_alt_margin_m", 14500.0 - service_ceiling_nom_m))
    flameout_ceiling_deficit_m = -flameout_alt_margin_m
    ab_maturity = float(eng_diag.get("ab_maturity", engine_maturity if has_afterburner > 0.5 else 1.0))
    ab_immaturity = max(0.0, 1.0 - ab_maturity)

    # Derived helper excesses for flaw ramps
    vv_deficit = max(-0.03, 0.075 - vv)
    taper_deficit = max(0.0, 0.45 - taper)
    low_ar_excess = max(0.0, 3.6 - ar)
    thin_wing_excess = max(0.0, 0.08 - tc_ratio)
    ti_deficit = max(0.0, 0.12 - ti_fraction) if has_afterburner > 0.5 else 0.0
    fuel_fraction = internal_fuel_kg / max(1000.0, mtow_kg)

    return {
        "sweep_deg": sweep_deg,
        "aspect_ratio": ar,
        "taper_ratio": taper,
        "tc_ratio": tc_ratio,
        "wing_area_m2": wing_area_m2,
        "span_m": span_m,
        "is_delta": is_delta,
        "has_le_slats": has_le_slats,
        "has_le_flaps": has_le_flaps,
        "has_wing_fences": has_wing_fences,
        "has_sawtooth_le": has_sawtooth_le,
        "has_blown_flaps": has_blown_flaps,
        "fuselage_length_m": fus_len_m,
        "fuselage_diameter_m": fus_diam_m,
        "fuselage_fineness": fuselage_fineness,
        "fuselage_to_span_ratio": fuselage_to_span_ratio,
        "is_area_ruled": is_area_ruled,
        "is_t_tail": is_t_tail,
        "has_all_moving_tail": has_all_moving_tail,
        "vv": vv,
        "vh": vh,
        "vv_deficit": vv_deficit,
        "non_nose_intake": non_nose_intake,
        "is_variable_intake": is_variable_intake,
        "has_afterburner": has_afterburner,
        "engine_count": engine_count,
        "design_load_factor_g": design_load_factor_g,
        "ti_fraction": ti_fraction,
        "ti_deficit": ti_deficit,
        "carrier_capable": carrier_capable,
        "has_honeycomb": has_honeycomb,
        "has_powered_controls": has_powered_controls,
        "has_dual_hydraulics": has_dual_hydraulics,
        "has_sas": has_sas,
        "has_ejection_seat": has_ejection_seat,
        "has_radar": has_radar,
        "avionics_level": avionics_level,
        "has_guns": has_guns,
        "gun_caliber_mm": gun_caliber_mm,
        "guns_near_intake": guns_near_intake,
        "hardpoints": hardpoints,
        "max_mach_alt": max_mach_alt,
        "max_mach_sl": max_mach_sl,
        "max_mach_nom": max_mach_nom,
        "service_ceiling_nom_m": service_ceiling_nom_m,
        "empty_mass_kg": empty_mass_kg,
        "mtow_kg": mtow_kg,
        "internal_fuel_kg": internal_fuel_kg,
        "fuel_fraction": fuel_fraction,
        "wing_loading_kgm2": wing_loading_kgm2,
        "shortal_maggin_excess": shortal_maggin_excess,
        "m_dd": m_dd,
        "mach_dd_excess": mach_dd_excess,
        "wave_drag_ratio": wave_drag_ratio,
        "ac_shift_mac": ac_shift_mac,
        "q_dive_kpa": q_dive_kpa,
        "torsion_flex_index": torsion_flex_index,
        "inertia_coupling_index": inertia_coupling_index,
        "engine_maturity": engine_maturity,
        "engine_immaturity": engine_immaturity,
        "compressor_stall_margin": compressor_stall_margin,
        "stall_margin_deficit": stall_margin_deficit,
        "flameout_alt_margin_m": flameout_alt_margin_m,
        "flameout_ceiling_deficit_m": flameout_ceiling_deficit_m,
        "ab_maturity": ab_maturity,
        "ab_immaturity": ab_immaturity,
        "taper_deficit": taper_deficit,
        "low_ar_excess": low_ar_excess,
        "thin_wing_excess": thin_wing_excess,
    }


def compute_categorical_signature(design: Dict[str, Any], feat: Dict[str, float]) -> str:
    """Return coarse categorical signature (§5.1.2)."""
    company_id = str(design.get("company_id", "player_co"))
    if feat["is_delta"] > 0.5:
        planform_class = "delta"
    elif feat["sweep_deg"] >= 20.0:
        planform_class = "swept"
    else:
        planform_class = "straight"
    t_tail = int(feat["is_t_tail"] > 0.5)
    intake_type = str(design.get("intake", {}).get("type", "nose")).lower()
    carrier = int(feat["carrier_capable"] > 0.5)
    engine_id = str(design.get("propulsion", {}).get("engine_id", "generic_jet"))
    return f"{company_id}:{planform_class}:{t_tail}:{intake_type}:{carrier}:{engine_id}"


def compute_5d_coords(feat: Dict[str, float]) -> Tuple[float, float, float, float, float]:
    """Return normalized 5D continuous coordinate tuple for value noise (§5.1.2)."""
    x1 = feat["sweep_deg"] / 15.0
    x2 = feat["tc_ratio"] / 0.03
    x3 = feat["aspect_ratio"] / 1.5
    x4 = math.log(max(500.0, feat["empty_mass_kg"]) / 2000.0) / 0.35
    x5 = feat["max_mach_nom"] / 0.25
    return (x1, x2, x3, x4, x5)
