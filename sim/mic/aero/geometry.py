"""AircraftDesign schema parsing, TechContext validation, and 3D/longitudinal geometry derivation.

Implements:
- Standardized parsing of `AircraftDesign` dictionaries (per `00_conventions.md` §4.2).
- `validate_design(design, tech_context)` enforcing hard tech caps (`03_tech_effect_keys.md` §1.2)
  with `TECH_CAP:<key>` error codes and physical packaging checks.
- Derived wing planform parameters (b, c_r, c_t, MAC, y_MAC, x_MAC_LE, sweep conversion between
  LE / c/4 / c/2 / TE, exposed area S_exp, wetted area S_wet).
- Longitudinal 64-station cross-sectional area distribution A(x) for fuselage, wing, tail,
  canopy, intake capture subtraction, and Whitcomb transonic/supersonic area-rule waisting.
- Internal fuel volume budget (Torenbeek wing box + fuselage usable volume).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from .airfoil import AirfoilSectionResult, parse_and_analyze_airfoil
from .tuning import load_aero_tuning


def get_tech_value(tech_context: Any, key: str, default: Any) -> Any:
    """Safely read an effect key from a TechContext object, dict, or None."""
    if tech_context is None:
        return default
    if hasattr(tech_context, "values") and isinstance(tech_context.values, dict):
        if key in tech_context.values:
            return tech_context.values[key]
    if hasattr(tech_context, "get") and callable(tech_context.get):
        try:
            val = tech_context.get(key)
            if val is not None:
                return val
        except KeyError:
            return default
    if isinstance(tech_context, dict):
        return tech_context.get(key, default)
    return default


def convert_sweep_rad(
    sweep_from_rad: float,
    aspect_ratio: float,
    taper_ratio: float,
    x_from: float,
    x_to: float,
) -> float:
    """Convert wing sweep angle from chord fraction `x_from` to `x_to` (0=LE, 0.25=c/4, 0.5=c/2, 1=TE)."""
    tan_to = math.tan(sweep_from_rad) - (4.0 / max(aspect_ratio, 0.5)) * (x_to - x_from) * (
        (1.0 - taper_ratio) / (1.0 + taper_ratio)
    )
    return math.atan(tan_to)


@dataclass(frozen=True)
class DerivedWingGeometry:
    """Derived geometric properties of the main wing."""

    area_m2: float
    aspect_ratio: float
    taper_ratio: float
    span_m: float
    root_chord_m: float
    tip_chord_m: float
    mac_m: float
    y_mac_m: float
    x_le_root_m: float
    x_mac_le_m: float
    x_ac_subsonic_m: float
    sweep_qc_deg: float
    sweep_qc_rad: float
    sweep_le_deg: float
    sweep_le_rad: float
    sweep_hc_rad: float
    sweep_te_rad: float
    tc_root: float
    tc_tip: float
    tc_mean: float
    dihedral_deg: float
    incidence_deg: float
    twist_deg: float
    position: str
    planform_type: str
    conical_camber: bool
    exposed_area_m2: float
    wetted_area_m2: float
    flapped_area_ratio: float
    has_plain_flaps: bool
    has_slotted_flaps: bool
    has_fowler_flaps: bool
    has_blown_flaps: bool
    has_le_slats: bool
    has_le_flaps: bool
    airfoil: AirfoilSectionResult


@dataclass(frozen=True)
class DerivedEmpennageGeometry:
    """Derived geometric properties of the horizontal and vertical tail."""

    tailless: bool
    t_tail: bool
    all_moving_tail: bool
    ht_area_m2: float
    ht_aspect_ratio: float
    ht_taper_ratio: float
    ht_span_m: float
    ht_mac_m: float
    ht_sweep_qc_rad: float
    ht_sweep_le_rad: float
    ht_tc_ratio: float
    ht_arm_m: float
    ht_z_m: float
    ht_volume_coeff: float
    ht_wetted_area_m2: float
    vt_area_m2: float
    vt_aspect_ratio: float
    vt_taper_ratio: float
    vt_span_m: float
    vt_mac_m: float
    vt_sweep_qc_rad: float
    vt_sweep_le_rad: float
    vt_tc_ratio: float
    vt_arm_m: float
    vt_volume_coeff: float
    vt_wetted_area_m2: float


@dataclass(frozen=True)
class DerivedFuselageGeometry:
    """Derived fuselage geometry and longitudinal cross-sectional area distribution."""

    length_m: float
    max_diameter_m: float
    fineness_ratio: float
    nose_length_m: float
    tail_length_m: float
    max_cross_section_m2: float
    wetted_area_m2: float
    canopy_type: str
    canopy_frontal_area_m2: float
    area_ruled: bool
    effective_waist_fraction: float
    x_stations_m: np.ndarray = field(repr=False)
    area_fuselage_m2: np.ndarray = field(repr=False)
    area_wing_m2: np.ndarray = field(repr=False)
    area_tail_m2: np.ndarray = field(repr=False)
    area_total_m2: np.ndarray = field(repr=False)
    area_total_unruled_m2: np.ndarray = field(repr=False)
    max_total_area_m2: float = 0.0
    max_total_area_unruled_m2: float = 0.0
    internal_volume_m3: float = 0.0


@dataclass(frozen=True)
class DerivedAircraftGeometry:
    """Complete parsed and derived geometry for an AircraftDesign."""

    design_id: str
    name: str
    company_id: str
    role_tags: Tuple[str, ...]
    crew_count: int
    wing: DerivedWingGeometry
    fuselage: DerivedFuselageGeometry
    empennage: DerivedEmpennageGeometry
    intake_type: str
    intake_compression: str
    intake_variable: bool
    intake_spike: bool
    intake_capture_area_m2: float
    intake_duct_length_m: float
    engine_id: str
    engine_count: int
    afterburner: bool
    engine_x_cg_m: float
    design_load_factor_g: float
    ultimate_load_factor_g: float
    material_al_frac: float
    material_steel_frac: float
    material_ti_frac: float
    carrier_capable: bool
    internal_fuel_kg: float
    drop_tanks_count: int
    drop_tank_fuel_kg_each: float
    combat_uses_drop_tanks: bool
    max_fuel_capacity_kg: float
    wing_fuel_capacity_kg: float
    fuselage_fuel_capacity_kg: float
    radar_id: Optional[str]
    fire_control_id: Optional[str]
    avionics_level: int
    powered_controls: bool
    stability_augmentation: bool
    ejection_seat: bool
    inflight_refuel: bool
    pressurized_cockpit: bool
    guns: Tuple[Dict[str, Any], ...]
    hardpoints: int
    internal_bay: bool
    missile_ids: Tuple[str, ...]
    combat_external_stores_kg: float
    raw_design: Dict[str, Any] = field(repr=False)


def _extract_device_flags(devices: List[Any]) -> Tuple[float, bool, bool, bool, bool, bool, bool]:
    has_plain = False
    has_slotted = False
    has_fowler = False
    has_blown = False
    has_slats = False
    has_le_flaps = False
    flapped_span_frac = 0.0

    for dev in devices:
        if isinstance(dev, str):
            d_type = dev.strip().lower()
            span_f = 0.58
        elif isinstance(dev, dict):
            d_type = str(dev.get("type", "")).strip().lower()
            span_f = float(dev.get("span_frac", 0.58))
        else:
            continue

        if d_type in ("plain", "plain_flap", "plain_flaps", "split", "split_flap", "split_flaps"):
            has_plain = True
            flapped_span_frac = max(flapped_span_frac, span_f)
        elif d_type in ("slotted", "slotted_flap", "slotted_flaps", "single_slotted"):
            has_slotted = True
            flapped_span_frac = max(flapped_span_frac, span_f)
        elif d_type in ("fowler", "fowler_flap", "fowler_flaps", "double_slotted"):
            has_fowler = True
            flapped_span_frac = max(flapped_span_frac, span_f)
        elif d_type in ("blown", "blown_flap", "blown_flaps", "blc"):
            has_blown = True
            flapped_span_frac = max(flapped_span_frac, span_f)
        elif d_type in ("slat", "slats", "le_slat", "le_slats", "auto_slats"):
            has_slats = True
        elif d_type in ("le_flap", "le_flaps", "droop_nose", "krueger"):
            has_le_flaps = True

    if flapped_span_frac == 0.0 and (has_plain or has_slotted or has_fowler or has_blown):
        flapped_span_frac = 0.58
    return (
        float(np.clip(flapped_span_frac, 0.0, 0.78)),
        has_plain,
        has_slotted,
        has_fowler,
        has_blown,
        has_slats,
        has_le_flaps,
    )


def derive_aircraft_geometry(
    design: Dict[str, Any],
    tech_context: Any = None,
    engine_mass_flow_kgps: float = 42.0,
) -> DerivedAircraftGeometry:
    """Parse an `AircraftDesign` dict and compute all 3D and longitudinal geometric quantities."""
    tuning = load_aero_tuning()
    drag_tuning = tuning["drag"]
    mass_tuning = tuning["mass"]

    design_id = str(design.get("id", "custom_design"))
    name = str(design.get("name", design_id))
    company_id = str(design.get("company_id", "player_co"))
    role_tags = tuple(str(t) for t in design.get("role_tags", ["day_fighter"]))
    crew_count = int(np.clip(int(design.get("crew_count", 1)), 1, 3))

    # --- 1. Fuselage basic parameters ---
    fus_in = design.get("fuselage", {})
    fus_len = float(np.clip(float(fus_in.get("length_m", fus_in.get("length", 11.5))), 5.0, 35.0))
    if "max_diameter_m" in fus_in or "max_diameter" in fus_in:
        fus_diam = float(fus_in.get("max_diameter_m", fus_in.get("max_diameter", 1.45)))
    elif "width_m" in fus_in and "height_m" in fus_in:
        fus_diam = math.sqrt(float(fus_in["width_m"]) * float(fus_in["height_m"]))
    else:
        fus_diam = 1.45
    fus_diam = float(np.clip(fus_diam, 0.70, 4.00))
    fineness = fus_len / fus_diam

    nose_fineness = float(np.clip(float(fus_in.get("nose_fineness", 2.4)), 1.0, 6.0))
    tail_fineness = float(np.clip(float(fus_in.get("tail_fineness", 2.8)), 1.0, 6.5))
    nose_len = min(nose_fineness * fus_diam, 0.42 * fus_len)
    tail_len = min(tail_fineness * fus_diam, 0.42 * fus_len)
    canopy_type = str(fus_in.get("canopy_type", "bubble")).lower()
    area_ruled = bool(fus_in.get("area_ruled", False))
    waist_req = float(fus_in.get("area_rule_waist_frac", drag_tuning.get("area_rule_waisting_gain", 0.65)))
    if area_ruled:
        tech_eff = float(get_tech_value(tech_context, "aero.wave_drag_area_rule_eff", waist_req))
        if tech_eff <= 0.0:
            tech_eff = waist_req
        effective_waist = float(np.clip(min(waist_req, tech_eff), 0.15, 0.85))
    else:
        effective_waist = 0.0

    # --- 2. Wing geometry ---
    w_in = design.get("wing", {})
    s_ref = float(np.clip(float(w_in.get("area_m2", w_in.get("area", 26.0))), 6.0, 150.0))
    ar = float(np.clip(float(w_in.get("aspect_ratio", w_in.get("aspect", 4.8))), 1.3, 14.0))
    taper = float(np.clip(float(w_in.get("taper_ratio", w_in.get("taper", 0.50))), 0.02, 1.0))
    sweep_qc_deg = float(np.clip(float(w_in.get("sweep_qc_deg", w_in.get("sweep_deg", 35.0))), -25.0, 72.0))
    sweep_qc_rad = math.radians(sweep_qc_deg)

    tc_default = float(w_in.get("tc_ratio", 0.095))
    tc_root = float(np.clip(float(w_in.get("tc_root", tc_default)), 0.025, 0.22))
    tc_tip = float(np.clip(float(w_in.get("tc_tip", tc_root)), 0.025, 0.22))
    tc_mean = 0.65 * tc_root + 0.35 * tc_tip

    airfoil_spec = w_in.get("airfoil_ref", f"00{tc_mean*100:04.1f}")
    airfoil_res = parse_and_analyze_airfoil(airfoil_spec, override_tc_ratio=tc_mean)

    span = math.sqrt(s_ref * ar)
    c_root = 2.0 * s_ref / (span * (1.0 + taper))
    c_tip = taper * c_root
    mac = (2.0 / 3.0) * c_root * ((1.0 + taper + taper ** 2) / (1.0 + taper))
    y_mac = (span / 6.0) * ((1.0 + 2.0 * taper) / (1.0 + taper))

    sweep_le_rad = convert_sweep_rad(sweep_qc_rad, ar, taper, 0.25, 0.0)
    sweep_hc_rad = convert_sweep_rad(sweep_qc_rad, ar, taper, 0.25, 0.50)
    sweep_te_rad = convert_sweep_rad(sweep_qc_rad, ar, taper, 0.25, 1.00)
    sweep_le_deg = math.degrees(sweep_le_rad)

    x_le_root_frac = float(np.clip(float(w_in.get("x_le_root_frac", 0.34)), 0.12, 0.68))
    x_le_root_m = x_le_root_frac * fus_len
    x_mac_le_m = x_le_root_m + y_mac * math.tan(sweep_le_rad)
    x_ac_subsonic_m = x_mac_le_m + 0.25 * mac

    planform_type = str(w_in.get("planform_type", "delta" if taper <= 0.14 else "conventional")).lower()
    position = str(w_in.get("position", "low")).lower()
    dihedral_deg = float(w_in.get("dihedral_deg", w_in.get("dihedral", 3.0)))
    incidence_deg = float(w_in.get("incidence_deg", 1.0))
    twist_deg = float(w_in.get("twist_deg", -1.5))
    conical_camber = bool(w_in.get("conical_camber", False))

    # Exposed wing area subtracting fuselage overlap
    r_fus = 0.5 * fus_diam
    if r_fus < 0.45 * span:
        c_at_fus = c_root - (c_root - c_tip) * (r_fus / (0.5 * span))
        s_covered = (c_root + c_at_fus) * r_fus
        s_exp = max(s_ref - s_covered, 0.55 * s_ref)
    else:
        s_exp = 0.55 * s_ref
    s_wet_wing = 2.0 * s_exp * (1.0 + 0.25 * tc_root * ((1.0 + (tc_tip / max(tc_root, 1e-3)) * taper) / (1.0 + taper)))

    devices_raw = w_in.get("devices", ["fowler_flaps"])
    (
        flapped_area_ratio,
        has_plain,
        has_slotted,
        has_fowler,
        has_blown,
        has_slats,
        has_le_flaps,
    ) = _extract_device_flags(devices_raw)

    wing_geom = DerivedWingGeometry(
        area_m2=s_ref,
        aspect_ratio=ar,
        taper_ratio=taper,
        span_m=span,
        root_chord_m=c_root,
        tip_chord_m=c_tip,
        mac_m=mac,
        y_mac_m=y_mac,
        x_le_root_m=x_le_root_m,
        x_mac_le_m=x_mac_le_m,
        x_ac_subsonic_m=x_ac_subsonic_m,
        sweep_qc_deg=sweep_qc_deg,
        sweep_qc_rad=sweep_qc_rad,
        sweep_le_deg=sweep_le_deg,
        sweep_le_rad=sweep_le_rad,
        sweep_hc_rad=sweep_hc_rad,
        sweep_te_rad=sweep_te_rad,
        tc_root=tc_root,
        tc_tip=tc_tip,
        tc_mean=tc_mean,
        dihedral_deg=dihedral_deg,
        incidence_deg=incidence_deg,
        twist_deg=twist_deg,
        position=position,
        planform_type=planform_type,
        conical_camber=conical_camber,
        exposed_area_m2=s_exp,
        wetted_area_m2=s_wet_wing,
        flapped_area_ratio=flapped_area_ratio,
        has_plain_flaps=has_plain,
        has_slotted_flaps=has_slotted,
        has_fowler_flaps=has_fowler,
        has_blown_flaps=has_blown,
        has_le_slats=has_slats,
        has_le_flaps=has_le_flaps,
        airfoil=airfoil_res,
    )

    # --- 3. Empennage geometry ---
    emp_in = design.get("empennage", {})
    tailless = bool(emp_in.get("tailless", False))
    t_tail = bool(emp_in.get("t_tail", False))
    all_moving_tail = bool(emp_in.get("all_moving_tail", False))

    ht_arm_frac = float(emp_in.get("ht_arm_frac", 0.44))
    ht_arm_m = max(ht_arm_frac * fus_len, 0.22 * fus_len)
    if tailless:
        ht_area = 0.0
        ht_ar = 3.0
        ht_taper = 0.45
        ht_span = 0.0
        ht_mac = 0.0
        ht_sweep_qc_rad = sweep_qc_rad
        ht_sweep_le_rad = sweep_le_rad
        ht_tc = 0.07
        ht_vol_coeff = 0.0
        ht_wet = 0.0
    else:
        if "ht_area_m2" in emp_in:
            ht_area = max(float(emp_in["ht_area_m2"]), 0.0)
            ht_vol_coeff = (ht_area * ht_arm_m) / max(s_ref * mac, 1e-3)
        else:
            ht_vol_coeff = float(emp_in.get("ht_volume_coeff", 0.40))
            ht_area = ht_vol_coeff * s_ref * mac / max(ht_arm_m, 1.0)
        ht_ar = float(np.clip(float(emp_in.get("ht_aspect_ratio", 3.6)), 1.5, 7.0))
        ht_taper = float(np.clip(float(emp_in.get("ht_taper_ratio", 0.45)), 0.1, 1.0))
        ht_span = math.sqrt(ht_area * ht_ar)
        ht_c_root = 2.0 * ht_area / max(ht_span * (1.0 + ht_taper), 1e-4)
        ht_mac = (2.0 / 3.0) * ht_c_root * ((1.0 + ht_taper + ht_taper ** 2) / (1.0 + ht_taper))
        ht_sweep_qc_deg = float(emp_in.get("ht_sweep_qc_deg", sweep_qc_deg + 3.0))
        ht_sweep_qc_rad = math.radians(ht_sweep_qc_deg)
        ht_sweep_le_rad = convert_sweep_rad(ht_sweep_qc_rad, ht_ar, ht_taper, 0.25, 0.0)
        ht_tc = float(np.clip(float(emp_in.get("ht_tc_ratio", min(tc_mean, 0.085))), 0.03, 0.14))
        ht_wet = 2.0 * ht_area * (1.0 + 0.25 * ht_tc)

    vt_arm_frac = float(emp_in.get("vt_arm_frac", 0.42))
    vt_arm_m = max(vt_arm_frac * fus_len, 0.22 * fus_len)
    if "vt_area_m2" in emp_in:
        vt_area = max(float(emp_in["vt_area_m2"]), 0.5)
        vt_vol_coeff = (vt_area * vt_arm_m) / max(s_ref * span, 1e-3)
    else:
        vt_vol_coeff = float(emp_in.get("vt_volume_coeff", 0.068))
        vt_area = vt_vol_coeff * s_ref * span / max(vt_arm_m, 1.0)
    vt_ar = float(np.clip(float(emp_in.get("vt_aspect_ratio", 1.55)), 0.8, 3.5))
    vt_taper = float(np.clip(float(emp_in.get("vt_taper_ratio", 0.40)), 0.1, 1.0))
    vt_span = math.sqrt(vt_area * vt_ar)
    vt_c_root = 2.0 * vt_area / max(vt_span * (1.0 + vt_taper), 1e-4)
    vt_mac = (2.0 / 3.0) * vt_c_root * ((1.0 + vt_taper + vt_taper ** 2) / (1.0 + vt_taper))
    vt_sweep_qc_deg = float(emp_in.get("vt_sweep_qc_deg", max(sweep_qc_deg + 5.0, 35.0)))
    vt_sweep_qc_rad = math.radians(vt_sweep_qc_deg)
    vt_sweep_le_rad = convert_sweep_rad(vt_sweep_qc_rad, vt_ar, vt_taper, 0.25, 0.0)
    vt_tc = float(np.clip(float(emp_in.get("vt_tc_ratio", min(tc_mean, 0.085))), 0.03, 0.14))
    vt_wet = 2.0 * vt_area * (1.0 + 0.25 * vt_tc)

    ht_z_frac = float(emp_in.get("ht_z_frac", 0.95 if t_tail else 0.15))
    ht_z_m = ht_z_frac * vt_span

    empennage_geom = DerivedEmpennageGeometry(
        tailless=tailless,
        t_tail=t_tail,
        all_moving_tail=all_moving_tail,
        ht_area_m2=ht_area,
        ht_aspect_ratio=ht_ar,
        ht_taper_ratio=ht_taper,
        ht_span_m=ht_span,
        ht_mac_m=ht_mac,
        ht_sweep_qc_rad=ht_sweep_qc_rad,
        ht_sweep_le_rad=ht_sweep_le_rad,
        ht_tc_ratio=ht_tc,
        ht_arm_m=ht_arm_m,
        ht_z_m=ht_z_m,
        ht_volume_coeff=ht_vol_coeff,
        ht_wetted_area_m2=ht_wet,
        vt_area_m2=vt_area,
        vt_aspect_ratio=vt_ar,
        vt_taper_ratio=vt_taper,
        vt_span_m=vt_span,
        vt_mac_m=vt_mac,
        vt_sweep_qc_rad=vt_sweep_qc_rad,
        vt_sweep_le_rad=vt_sweep_le_rad,
        vt_tc_ratio=vt_tc,
        vt_arm_m=vt_arm_m,
        vt_volume_coeff=vt_vol_coeff,
        vt_wetted_area_m2=vt_wet,
    )

    # --- 4. Propulsion & Intake parameters ---
    prop_in = design.get("propulsion", {})
    engine_id = str(prop_in.get("engine_id", "J47-GE-27"))
    engine_count = int(np.clip(int(prop_in.get("count", 1)), 1, 4))
    afterburner = bool(prop_in.get("afterburner", False))
    engine_x_cg_m = float(prop_in.get("x_cg_frac", 0.62)) * fus_len

    in_spec = design.get("intake", {})
    intake_type = str(in_spec.get("type", "nose")).lower()
    intake_var = bool(in_spec.get("variable", False))
    intake_spike = bool(in_spec.get("spike", False))
    if "compression" in in_spec:
        intake_comp = str(in_spec["compression"]).lower()
    elif intake_var:
        intake_comp = "variable_ramp"
    elif intake_spike:
        intake_comp = "fixed_spike"
    else:
        intake_comp = "pitot"

    # Estimate capture area from total engine mass flow (~185 kg/(s*m^2) at SL static design point)
    default_capture = 0.0054 * engine_mass_flow_kgps * engine_count
    intake_capture_m2 = float(in_spec.get("capture_area_m2", max(default_capture, 0.16 * engine_count)))
    if intake_type == "nose":
        duct_len = max(engine_x_cg_m - 0.05 * fus_len, 2.5)
    elif intake_type == "chin":
        duct_len = max(engine_x_cg_m - 0.14 * fus_len, 2.0)
    else:
        duct_len = max(engine_x_cg_m - 0.25 * fus_len, 1.5)

    # --- 5. Longitudinal 64-station cross-sectional area distribution A(x) ---
    n_sta = 64
    x_sta = np.linspace(0.0, fus_len, n_sta)
    a_max_fus = math.pi * (0.5 * fus_diam) ** 2

    # Unruled fuselage radius profile: Haack/parabolic nose, cylindrical midbody, boat-tail aft
    a_fus_unruled = np.zeros(n_sta, dtype=np.float64)
    x_mid_end = fus_len - tail_len
    for i, xv in enumerate(x_sta):
        if xv <= nose_len:
            u = xv / max(nose_len, 0.1)
            # Nose intake has finite lip area at x=0; pointed radome starts at 0
            a_lip = min(1.15 * intake_capture_m2, 0.45 * a_max_fus) if intake_type == "nose" else 0.0
            a_fus_unruled[i] = a_lip + (a_max_fus - a_lip) * (1.0 - (1.0 - u) ** 2.2)
        elif xv <= x_mid_end:
            a_fus_unruled[i] = a_max_fus
        else:
            u = (xv - x_mid_end) / max(tail_len, 0.1)
            a_nozzle = min(0.32 * a_max_fus * engine_count, 0.55 * a_max_fus)
            a_fus_unruled[i] = a_max_fus - (a_max_fus - a_nozzle) * (u ** 1.8)

    # Canopy cross-sectional bump
    canopy_frontal = 0.26 * (1.0 + 0.18 * (crew_count - 1)) if canopy_type == "bubble" else 0.18 * (1.0 + 0.15 * (crew_count - 1))
    x_can_start = 0.14 * fus_len
    x_can_end = x_can_start + (2.6 + 0.9 * (crew_count - 1))
    a_canopy = np.where(
        (x_sta >= x_can_start) & (x_sta <= x_can_end),
        canopy_frontal * np.sin(math.pi * (x_sta - x_can_start) / max(x_can_end - x_can_start, 0.5)) ** 2,
        0.0,
    )
    a_fus_unruled = a_fus_unruled + a_canopy

    # Wing cross-sectional area distribution A_wing(x) by integrating thickness across exposed half-span
    y_span = np.linspace(r_fus, 0.5 * span, 40)
    dy_span = float(y_span[1] - y_span[0]) if len(y_span) > 1 else 0.0
    eta_span = y_span / (0.5 * span)
    c_y = c_root * (1.0 - (1.0 - taper) * eta_span)
    tc_y = tc_root * (1.0 - eta_span) + tc_tip * eta_span
    x_le_y = x_le_root_m + y_span * math.tan(sweep_le_rad)

    # Blended wing-body tailless deltas share centerbody volume between fuselage and thick wing root
    wing_vol_blend = 0.72 if (tailless and planform_type == "delta") else 1.00
    a_wing = np.zeros(n_sta, dtype=np.float64)
    for i, xv in enumerate(x_sta):
        xi = (xv - x_le_y) / np.maximum(c_y, 1e-3)
        in_chord = (xi > 0.0) & (xi < 1.0)
        if np.any(in_chord):
            xi_c = xi[in_chord]
            # Exact normalized airfoil thickness profile: peak = 1.0 * tc * c at xi = 1/3, chordwise area = 0.693 * tc * c^2
            t_local = 2.60 * tc_y[in_chord] * c_y[in_chord] * np.sqrt(xi_c) * (1.0 - xi_c)
            a_wing[i] = 2.0 * float(np.sum(t_local)) * dy_span * wing_vol_blend

    # Empennage cross-sectional area distribution A_tail(x)
    a_tail = np.zeros(n_sta, dtype=np.float64)
    x_tail_center = min(x_ac_subsonic_m + vt_arm_m, 0.92 * fus_len)
    tail_len_span = max(vt_mac * 1.35, 1.4)
    tail_vol = 0.68 * (ht_area * ht_tc * max(ht_mac, 0.5) + vt_area * vt_tc * max(vt_mac, 0.5))
    for i, xv in enumerate(x_sta):
        u = (xv - (x_tail_center - 0.5 * tail_len_span)) / tail_len_span
        if 0.0 < u < 1.0:
            a_tail[i] = (tail_vol / tail_len_span) * 6.0 * u * (1.0 - u)

    # Subtract capture streamtube area smoothly (Raymer §12.5.2) without step discontinuity
    x_inlet_ramp = max(0.18 * fus_len if intake_type == "nose" else 0.28 * fus_len, 1.0)
    a_streamtube = intake_capture_m2 * np.clip(x_sta / x_inlet_ramp, 0.0, 1.0)

    a_total_unruled = np.maximum(a_fus_unruled + a_wing + a_tail - a_streamtube, 0.05)

    # Apply Whitcomb area-rule waisting to fuselage where wing + tail cross-section peaks
    if area_ruled and effective_waist > 0.0:
        min_core_area = max(0.54 * a_max_fus, 1.30 * intake_capture_m2)
        waist_cut = effective_waist * (a_wing + 0.5 * a_tail)
        # Also allow subtle fuselage anti-shock bulges fore/aft of wing root (F-102A Kuchemann/Whitcomb fairings)
        a_fus_ruled = np.maximum(a_fus_unruled - waist_cut, min_core_area)
    else:
        a_fus_ruled = a_fus_unruled.copy()

    a_total_ruled = np.maximum(a_fus_ruled + a_wing + a_tail - a_streamtube, 0.05)

    # Fuselage wetted area from perimeter integration and internal volume
    r_eq = np.sqrt(np.maximum(a_fus_ruled - a_canopy, 0.01) / math.pi)
    s_wet_fus = float(np.trapezoid(2.0 * math.pi * r_eq, x_sta))
    vol_fus = float(np.trapezoid(np.maximum(a_fus_ruled - a_canopy, 0.01), x_sta))

    fuselage_geom = DerivedFuselageGeometry(
        length_m=fus_len,
        max_diameter_m=fus_diam,
        fineness_ratio=fineness,
        nose_length_m=nose_len,
        tail_length_m=tail_len,
        max_cross_section_m2=float(np.max(a_fus_ruled)),
        wetted_area_m2=s_wet_fus,
        canopy_type=canopy_type,
        canopy_frontal_area_m2=canopy_frontal,
        area_ruled=area_ruled,
        effective_waist_fraction=effective_waist,
        x_stations_m=x_sta,
        area_fuselage_m2=a_fus_ruled,
        area_wing_m2=a_wing,
        area_tail_m2=a_tail,
        area_total_m2=a_total_ruled,
        area_total_unruled_m2=a_total_unruled,
        max_total_area_m2=float(np.max(a_total_ruled)),
        max_total_area_unruled_m2=float(np.max(a_total_unruled)),
        internal_volume_m3=vol_fus,
    )

    # --- 6. Structure, Systems, Armament, and Fuel Volume Budget ---
    st_in = design.get("structure", {})
    load_g = float(np.clip(float(st_in.get("design_load_factor_g", 7.33)), 3.5, 10.0))
    ult_g = 1.5 * load_g
    mat_mix = st_in.get("material_mix", {"al": 0.88, "steel": 0.12, "ti": 0.0})
    al_f = max(float(mat_mix.get("al", 0.88)), 0.0)
    st_f = max(float(mat_mix.get("steel", 0.12)), 0.0)
    ti_f = max(float(mat_mix.get("ti", 0.0)), 0.0)
    mat_sum = max(al_f + st_f + ti_f, 1e-6)
    al_f, st_f, ti_f = al_f / mat_sum, st_f / mat_sum, ti_f / mat_sum
    carrier_capable = bool(st_in.get("carrier_capable", "carrier" in role_tags))

    sys_in = design.get("systems", {})
    radar_id = sys_in.get("radar_id", None)
    fcs_id = sys_in.get("fire_control_id", None)
    avionics_level = int(np.clip(int(sys_in.get("avionics_level", 1)), 0, 5))
    powered_controls = bool(sys_in.get("powered_controls", True))
    stab_aug = bool(sys_in.get("stability_augmentation", False))
    ejection_seat = bool(sys_in.get("ejection_seat", True))
    inflight_refuel = bool(sys_in.get("inflight_refuel", False))
    pressurized_cockpit = bool(sys_in.get("pressurized_cockpit", True))

    arm_in = design.get("armament", {})
    guns_list = tuple(dict(g) for g in arm_in.get("guns", []))
    hardpoints = int(np.clip(int(arm_in.get("hardpoints", 2)), 0, 12))
    internal_bay = bool(arm_in.get("internal_bay", False))
    missile_ids = tuple(str(m) for m in arm_in.get("missile_ids", []))
    combat_ext_stores_kg = max(float(arm_in.get("combat_external_stores_kg", 0.0)), 0.0)

    fuel_in = design.get("fuel", {})
    internal_fuel_kg = max(float(fuel_in.get("internal_kg", 1600.0)), 100.0)
    drop_tanks_count = int(np.clip(int(fuel_in.get("drop_tanks_count", 2)), 0, 4))
    drop_tank_fuel_kg_each = max(float(fuel_in.get("drop_tank_fuel_kg_each", 0.0)), 0.0)
    combat_uses_drop_tanks = bool(fuel_in.get("combat_uses_drop_tanks", False))

    # Torenbeek wing fuel box volume + fuselage packaging budget
    rho_fuel = float(mass_tuning.get("fuel_density_kg_per_m3", 780.0))
    eta_wing_fuel = float(mass_tuning.get("wing_fuel_volume_efficiency", 0.52))
    eta_fus_fuel = float(mass_tuning.get("fuselage_fuel_volume_efficiency", 0.54))

    vol_wing_box = (
        eta_wing_fuel
        * (s_exp ** 1.5)
        / math.sqrt(ar)
        * tc_root
        * ((1.0 + taper * math.sqrt(tc_tip / max(tc_root, 1e-3)) + (taper ** 2) * (tc_tip / max(tc_root, 1e-3))) / ((1.0 + taper) ** 2))
    )
    vol_cockpit = 1.45 * crew_count
    vol_avionics = 0.25 + 0.22 * avionics_level + (0.45 if radar_id else 0.0)
    vol_engine_and_duct = engine_count * (1.85 + 0.55 * duct_len * (intake_capture_m2 / max(engine_count, 1)))
    vol_gear_and_guns = 0.85 + 0.18 * len(guns_list) + (1.35 if internal_bay else 0.0)
    vol_fus_available = max(vol_fus - (vol_cockpit + vol_avionics + vol_engine_and_duct + vol_gear_and_guns), 0.35)
    vol_fus_fuel = eta_fus_fuel * vol_fus_available

    wing_fuel_cap_kg = vol_wing_box * rho_fuel
    fus_fuel_cap_kg = vol_fus_fuel * rho_fuel
    max_fuel_cap_kg = wing_fuel_cap_kg + fus_fuel_cap_kg

    return DerivedAircraftGeometry(
        design_id=design_id,
        name=name,
        company_id=company_id,
        role_tags=role_tags,
        crew_count=crew_count,
        wing=wing_geom,
        fuselage=fuselage_geom,
        empennage=empennage_geom,
        intake_type=intake_type,
        intake_compression=intake_comp,
        intake_variable=intake_var,
        intake_spike=intake_spike,
        intake_capture_area_m2=intake_capture_m2,
        intake_duct_length_m=duct_len,
        engine_id=engine_id,
        engine_count=engine_count,
        afterburner=afterburner,
        engine_x_cg_m=engine_x_cg_m,
        design_load_factor_g=load_g,
        ultimate_load_factor_g=ult_g,
        material_al_frac=al_f,
        material_steel_frac=st_f,
        material_ti_frac=ti_f,
        carrier_capable=carrier_capable,
        internal_fuel_kg=internal_fuel_kg,
        drop_tanks_count=drop_tanks_count,
        drop_tank_fuel_kg_each=drop_tank_fuel_kg_each,
        combat_uses_drop_tanks=combat_uses_drop_tanks,
        max_fuel_capacity_kg=max_fuel_cap_kg,
        wing_fuel_capacity_kg=wing_fuel_cap_kg,
        fuselage_fuel_capacity_kg=fus_fuel_cap_kg,
        radar_id=radar_id,
        fire_control_id=fcs_id,
        avionics_level=avionics_level,
        powered_controls=powered_controls,
        stability_augmentation=stab_aug,
        ejection_seat=ejection_seat,
        inflight_refuel=inflight_refuel,
        pressurized_cockpit=pressurized_cockpit,
        guns=guns_list,
        hardpoints=hardpoints,
        internal_bay=internal_bay,
        missile_ids=missile_ids,
        combat_external_stores_kg=combat_ext_stores_kg,
        raw_design=design,
    )


def validate_design(
    design: Dict[str, Any],
    tech_context: Any = None,
    engine_diameter_m: float = 0.0,
) -> Tuple[bool, List[str], List[str]]:
    """Validate an `AircraftDesign` against `TechContext` caps (`03_tech_effect_keys.md`) and physical rules.

    Returns:
        (is_valid, errors, warnings)
        Where `errors` uses `TECH_CAP:<key>` whenever a hard technology cap is violated.
    """
    geom = derive_aircraft_geometry(design, tech_context=tech_context)
    errors: List[str] = []
    warnings: List[str] = []

    if tech_context is not None:
        # 1. Aerodynamic caps
        max_sweep = float(get_tech_value(tech_context, "aero.wing_sweep_max_deg", 70.0))
        if abs(geom.wing.sweep_qc_deg) > max_sweep + 1e-6:
            errors.append("TECH_CAP:aero.wing_sweep_max_deg")

        min_tc = float(get_tech_value(tech_context, "aero.thin_wing_tc_min", 0.02))
        if geom.wing.tc_mean < min_tc - 1e-6:
            errors.append("TECH_CAP:aero.thin_wing_tc_min")

        min_ar = float(get_tech_value(tech_context, "aero.aspect_ratio_min", 1.5))
        if geom.wing.aspect_ratio < min_ar - 1e-6:
            errors.append("TECH_CAP:aero.aspect_ratio_min")

        if geom.wing.planform_type == "delta" and not bool(get_tech_value(tech_context, "aero.delta_wing", True)):
            errors.append("TECH_CAP:aero.delta_wing")

        if geom.wing.planform_type == "variable_sweep" and not bool(
            get_tech_value(tech_context, "aero.variable_sweep", True)
        ):
            errors.append("TECH_CAP:aero.variable_sweep")

        if geom.fuselage.area_ruled and not bool(get_tech_value(tech_context, "aero.area_rule", True)):
            errors.append("TECH_CAP:aero.area_rule")

        if geom.wing.conical_camber and not bool(get_tech_value(tech_context, "aero.conical_camber", True)):
            errors.append("TECH_CAP:aero.conical_camber")

        if geom.wing.has_le_slats and not bool(get_tech_value(tech_context, "aero.le_slats", True)):
            errors.append("TECH_CAP:aero.le_slats")

        if geom.wing.has_le_flaps and not bool(get_tech_value(tech_context, "aero.le_flaps", True)):
            errors.append("TECH_CAP:aero.le_flaps")

        if geom.wing.has_blown_flaps and not bool(get_tech_value(tech_context, "aero.blown_flaps", True)):
            errors.append("TECH_CAP:aero.blown_flaps")

        if geom.wing.has_fowler_flaps and not bool(get_tech_value(tech_context, "aero.fowler_flaps", True)):
            errors.append("TECH_CAP:aero.fowler_flaps")

        if geom.empennage.all_moving_tail and not bool(get_tech_value(tech_context, "aero.all_moving_tail", True)):
            errors.append("TECH_CAP:aero.all_moving_tail")

        if geom.empennage.t_tail and not bool(get_tech_value(tech_context, "aero.t_tail", True)):
            errors.append("TECH_CAP:aero.t_tail")

        if (geom.intake_spike or geom.intake_compression == "fixed_spike") and not bool(
            get_tech_value(tech_context, "aero.inlet_spike", True)
        ):
            errors.append("TECH_CAP:aero.inlet_spike")

        if (geom.intake_variable or geom.intake_compression == "variable_ramp") and not bool(
            get_tech_value(tech_context, "aero.inlet_variable", True)
        ):
            errors.append("TECH_CAP:aero.inlet_variable")

        # 2. Structures & materials caps
        if geom.material_ti_frac > 1e-6:
            if not bool(get_tech_value(tech_context, "struct.material.titanium_available", True)):
                errors.append("TECH_CAP:struct.material.titanium_available")
            max_ti = float(get_tech_value(tech_context, "struct.material.ti_max_fraction", 1.0))
            if geom.material_ti_frac > max_ti + 1e-6:
                errors.append("TECH_CAP:struct.material.ti_max_fraction")

        max_steel = float(get_tech_value(tech_context, "struct.material.steel_max_fraction", 1.0))
        if geom.material_steel_frac > max_steel + 1e-6:
            errors.append("TECH_CAP:struct.material.steel_max_fraction")

        max_g = float(get_tech_value(tech_context, "struct.design_load_max_g", 10.0))
        if geom.design_load_factor_g > max_g + 1e-6:
            errors.append("TECH_CAP:struct.design_load_max_g")

        # 3. Propulsion & Systems caps
        if geom.afterburner and not bool(get_tech_value(tech_context, "engine.afterburner", True)):
            errors.append("TECH_CAP:engine.afterburner")

        max_av_lvl = int(get_tech_value(tech_context, "avionics.level_max", 5))
        if geom.avionics_level > max_av_lvl:
            errors.append("TECH_CAP:avionics.level_max")

        if geom.radar_id is not None:
            if not bool(get_tech_value(tech_context, "avionics.radar_search", True)):
                errors.append("TECH_CAP:avionics.radar_search")
            r_key = f"unlock.radar.{geom.radar_id}"
            if not bool(get_tech_value(tech_context, r_key, True)):
                errors.append(f"TECH_CAP:{r_key}")

        if geom.powered_controls and not bool(get_tech_value(tech_context, "systems.powered_controls", True)):
            errors.append("TECH_CAP:systems.powered_controls")

        if geom.stability_augmentation and not bool(
            get_tech_value(tech_context, "systems.stability_augmentation", True)
        ):
            errors.append("TECH_CAP:systems.stability_augmentation")

        if geom.inflight_refuel and not bool(get_tech_value(tech_context, "systems.inflight_refuel", True)):
            errors.append("TECH_CAP:systems.inflight_refuel")

        # 4. Armament caps
        if geom.internal_bay and not bool(get_tech_value(tech_context, "armament.internal_bay", True)):
            errors.append("TECH_CAP:armament.internal_bay")

        max_hp = int(get_tech_value(tech_context, "armament.hardpoints_max", 12))
        if geom.hardpoints > max_hp:
            errors.append("TECH_CAP:armament.hardpoints_max")

        for g_item in geom.guns:
            gid = g_item.get("gun_id")
            if gid:
                g_key = f"unlock.gun.{gid}"
                if not bool(get_tech_value(tech_context, g_key, True)):
                    errors.append(f"TECH_CAP:{g_key}")

        for mid in geom.missile_ids:
            m_key = f"unlock.missile.{mid}"
            r_key = f"unlock.rocket.{mid}"
            if not bool(get_tech_value(tech_context, m_key, True)) and not bool(
                get_tech_value(tech_context, r_key, True)
            ):
                errors.append(f"TECH_CAP:{m_key}")

    # Physical packaging rules (engine diameter vs fuselage diameter, fuel volume)
    raw_d = float(design.get("fuselage", {}).get("max_diameter_m", geom.fuselage.max_diameter_m))
    if engine_diameter_m > 0.0 and raw_d < 1.01 * engine_diameter_m:
        errors.append("PACKAGING:fuselage_diameter_too_small_for_engine")

    if geom.internal_fuel_kg > 1.35 * geom.max_fuel_capacity_kg:
        errors.append("PACKAGING:internal_fuel_exceeds_volume")
    elif geom.internal_fuel_kg > 1.05 * geom.max_fuel_capacity_kg:
        warnings.append(
            f"PACKAGING:internal_fuel_exceeds_volume ({geom.internal_fuel_kg:.0f} kg > {geom.max_fuel_capacity_kg:.0f} kg)"
        )

    return len(errors) == 0, errors, warnings
