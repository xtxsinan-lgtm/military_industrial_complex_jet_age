"""Modified DAPCA-IV / RAND R-1693 Cost Estimating Relationships (CERs) in then-year USD.

Provides `estimate_costs(design, mass_breakdown, engine, quantity, year, company, tech_context=None)`
as the canonical cost oracle for Module 01 (`PerformanceReport`), Module 04 (production & contracts),
and Module 05 (RFP bid evaluation).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Dict, Iterator, Mapping, Optional

from .inflation import aero_cost_index_1950, cpi_index_1950
from .tuning import load_econ_tuning

LB_TO_KG = 0.45359237


def _get_field(obj: Any, key: str, default: Any = None) -> Any:
    """Read `key` from a dict, mapping, dataclass, or object attribute."""
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _get_tech_val(tech_context: Any, key: str, default: Any) -> Any:
    """Read a tech effect key from `TechContext` or a dict/stub."""
    if tech_context is None:
        return default
    if hasattr(tech_context, "get") and callable(tech_context.get):
        try:
            val = tech_context.get(key)
            return default if val is None else val
        except KeyError:
            return default
    values = _get_field(tech_context, "values", None)
    if isinstance(values, Mapping) and key in values:
        return values[key]
    if isinstance(tech_context, Mapping) and key in tech_context:
        return tech_context[key]
    return default


def _mean_immaturity(design: Any, tech_context: Any) -> float:
    """Compute mean tech immaturity `1 - maturity` across `design.techs_used` (0.0 if mature/none)."""
    if tech_context is None:
        return 0.0
    techs_used = _get_field(design, "techs_used", None) or []
    tech_mat_map = _get_field(tech_context, "tech_maturity", None) or {}
    if techs_used and isinstance(tech_mat_map, Mapping):
        imm = [max(0.0, 1.0 - float(tech_mat_map.get(tid, 1.0))) for tid in techs_used]
        if imm:
            return float(sum(imm) / len(imm))
    mat_map = _get_field(tech_context, "maturity", None)
    if isinstance(mat_map, Mapping) and mat_map:
        imm_vals = [max(0.0, 1.0 - float(v)) for v in mat_map.values() if float(v) < 1.0]
        if imm_vals:
            return float(sum(imm_vals) / len(imm_vals))
    return 0.0


def wright_cumulative_average_factor(quantity: int, learning_rate: float) -> float:
    """Return Wright cumulative-average learning factor `F_avg(Q, S)` for `Q` units.

    Under T. P. Wright's (1936) learning curve (`Journal of the Aeronautical Sciences`, 3(4)),
    doubling cumulative output multiplies cumulative-average unit hours by `S = learning_rate`,
    so `b = log2(S)`. Using the standard continuous midpoint integral approximation for unit `i`
    to remain consistent between lot-by-lot and full-run averages:
        F_avg(Q, b) = ((Q + 0.5)^(1 + b) - 0.5^(1 + b)) / ((1 + b) * Q)
    """
    q = max(1, int(round(quantity)))
    s = min(max(float(learning_rate), 0.55), 1.0)
    if q == 1 or abs(s - 1.0) < 1e-9:
        return 1.0
    b = math.log(s) / math.log(2.0)
    return float(((q + 0.5) ** (1.0 + b) - (0.5 ** (1.0 + b))) / ((1.0 + b) * q))


def wright_lot_average_factor(n_start: int, n_end: int, learning_rate: float, break_setback_units: float = 0.0) -> float:
    """Return average unit factor across a production lot of units `[n_start, n_end]` (1-indexed inclusive).

    Supports Anderlohr (1969) production-break loss of learning via `break_setback_units`
    which shifts the effective cumulative unit index backward.
    """
    n1 = max(1.0, float(n_start) - max(0.0, float(break_setback_units)))
    lot_size = max(1, int(n_end) - int(n_start) + 1)
    n2 = n1 + lot_size - 1.0
    s = min(max(float(learning_rate), 0.55), 1.0)
    if abs(s - 1.0) < 1e-9:
        return 1.0
    b = math.log(s) / math.log(2.0)
    total = ((n2 + 0.5) ** (1.0 + b) - (n1 - 0.5) ** (1.0 + b)) / (1.0 + b)
    return float(total / lot_size)


@dataclass(frozen=True)
class CostEstimate:
    """Detailed output of `estimate_costs(...)` in nominal then-year USD and constant-1950 USD.

    Supports both attribute access (`est.unit_flyaway_cost_usd`) and dict-style access
    (`est["unit_flyaway_cost_usd"]`) for full cross-module compatibility.
    """

    year: int
    quantity: int
    prototypes: int
    airframe_mass_kg: float
    airframe_mass_lb: float
    max_mach: float
    learning_curve_rate: float
    wright_labor_factor: float
    wright_material_factor: float
    complexity_factor: float
    material_mix_factor: float
    immaturity_penalty_dev: float
    immaturity_penalty_mfg: float
    aero_cost_index: float
    cpi_index: float

    # Hours breakdown
    engineering_hours: float
    tooling_hours: float
    t1_mfg_labor_hours: float
    avg_mfg_labor_hours: float
    avg_qc_hours: float

    # Recurring unit flyaway cost breakdown (then-year USD)
    t1_airframe_cost_usd: float
    airframe_unit_cost_usd: float
    engine_unit_cost_usd: float
    avionics_unit_cost_usd: float
    armament_unit_cost_usd: float
    gfe_unit_cost_usd: float
    unit_flyaway_cost_usd: float

    # Non-recurring development (RDT&E) cost breakdown (then-year USD)
    engineering_cost_usd: float
    dev_support_cost_usd: float
    tooling_cost_usd: float
    prototype_unit_cost_usd: float
    prototypes_total_cost_usd: float
    flight_test_cost_usd: float
    dev_cost_usd_estimate: float

    # Constant-1950 USD equivalents (per 00_conventions.md §3)
    constant_1950_unit_flyaway_usd: float
    constant_1950_dev_cost_usd: float

    # Operations & maintenance
    maint_mh_per_fh: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def keys(self) -> Iterator[str]:
        return iter(self.__dataclass_fields__.keys())


def _extract_design_parameters(
    design: Any,
    mass_breakdown: Any,
    engine: Any,
    year: int,
    tuning_cer: Dict[str, Any],
    max_mach_override: Optional[float] = None,
) -> Dict[str, Any]:
    """Extract normalized physical & configuration parameters from flexible inputs."""
    # 1. Empty mass & engine mass -> Airframe (AMPR) mass
    empty_mass_kg = _get_field(mass_breakdown, "empty_mass_kg", None)
    if empty_mass_kg is None:
        empty_mass_kg = _get_field(design, "empty_mass_kg", 6000.0)
    empty_mass_kg = float(empty_mass_kg)

    prop = _get_field(design, "propulsion", None)
    engine_count = _get_field(prop, "count", _get_field(design, "engine_count", 1))
    engine_count = max(1, int(engine_count))
    afterburner = bool(_get_field(prop, "afterburner", _get_field(design, "afterburner", False)))

    engine_mass_kg = _get_field(engine, "mass_kg", _get_field(design, "engine_mass_kg", None))
    if engine_mass_kg is None:
        prop_mass_total = _get_field(mass_breakdown, "propulsion_mass_kg", _get_field(mass_breakdown, "engine_mass_kg", None))
        if prop_mass_total is not None:
            engine_mass_kg = float(prop_mass_total) / engine_count
        else:
            engine_mass_kg = 1200.0
    engine_mass_kg = float(engine_mass_kg)

    airframe_mass_kg = max(400.0, empty_mass_kg - engine_count * engine_mass_kg)

    # 2. Wing geometry
    wing = _get_field(design, "wing", None)
    wing_sweep_deg = float(_get_field(wing, "sweep_deg", _get_field(wing, "sweep", _get_field(design, "wing_sweep_deg", 20.0))))
    wing_tc = float(_get_field(wing, "t_c", _get_field(wing, "tc", _get_field(design, "wing_tc", 0.09))))
    planform = str(_get_field(wing, "planform", "")).lower()
    delta_wing = bool(_get_field(wing, "delta_wing", _get_field(design, "delta_wing", planform == "delta")))
    variable_sweep = bool(_get_field(wing, "variable_sweep", _get_field(design, "variable_sweep", False)))

    # 3. Fuselage & intake
    fuselage = _get_field(design, "fuselage", None)
    area_ruled = bool(_get_field(fuselage, "area_ruled", _get_field(design, "area_ruled", False)))
    intake = _get_field(design, "intake", None)
    inlet_variable = bool(_get_field(intake, "variable", _get_field(design, "inlet_variable", False)))

    # 4. Structure & materials
    structure = _get_field(design, "structure", None)
    carrier_capable = bool(_get_field(structure, "carrier_capable", _get_field(design, "carrier_capable", False)))
    mat_mix = _get_field(structure, "material_mix", _get_field(design, "material_mix", None)) or {}
    al_frac = float(_get_field(mat_mix, "al", 0.90))
    steel_frac = float(_get_field(mat_mix, "steel", 0.10))
    ti_frac = float(_get_field(mat_mix, "ti", 0.0))
    total_mat = max(1e-6, al_frac + steel_frac + ti_frac)
    al_frac, steel_frac, ti_frac = al_frac / total_mat, steel_frac / total_mat, ti_frac / total_mat

    # 5. Systems & Armament
    systems = _get_field(design, "systems", None)
    avionics_level = int(_get_field(systems, "avionics_level", _get_field(design, "avionics_level", 1)))
    avionics_level = min(max(avionics_level, 0), 5)

    armament = _get_field(design, "armament", None)
    internal_bay = bool(_get_field(armament, "internal_bay", _get_field(design, "internal_bay", False)))
    guns = _get_field(armament, "guns", None)
    if isinstance(guns, list):
        gun_count = len(guns)
    else:
        gun_count = int(_get_field(design, "gun_count", 4))
    hardpoints = int(_get_field(armament, "hardpoints", _get_field(design, "hardpoints", 2)))

    # 6. Max Mach (use explicit override, or design/mass_breakdown field, or deterministic physics proxy)
    max_mach = max_mach_override
    if max_mach is None:
        max_mach = _get_field(design, "max_mach", _get_field(mass_breakdown, "max_mach", None))
    if max_mach is None:
        # Deterministic proxy when called before performance solve
        if afterburner:
            max_mach = 1.65 if inlet_variable else (1.30 if wing_sweep_deg >= 30.0 or delta_wing else 1.05)
        else:
            max_mach = 0.90 if wing_sweep_deg >= 25.0 else 0.82
    max_mach = min(max(float(max_mach), 0.45), 3.2)

    # 7. Engine unit cost (then-year USD) and reliability
    eng_unit_cost_usd = _get_field(engine, "unit_cost", _get_field(engine, "unit_cost_usd", _get_field(design, "engine_unit_cost_usd", None)))
    if eng_unit_cost_usd is None:
        # Stub engine CER from thrust in 1950 USD -> scaled to then-year USD
        dry_thrust = float(_get_field(engine, "dry_thrust_N", _get_field(design, "engine_dry_thrust_N", 25000.0)))
        ref_t = float(tuning_cer["stub_engine_ref_thrust_N"])
        base_c = float(tuning_cer["stub_engine_cost_base_1950_usd"])
        t_exp = float(tuning_cer["stub_engine_thrust_exp"])
        ab_mult = float(tuning_cer["stub_engine_ab_mult"]) if afterburner else 1.0
        eng_1950 = base_c * ((max(5000.0, dry_thrust) / ref_t) ** t_exp) * ab_mult
        eng_unit_cost_usd = eng_1950 * aero_cost_index_1950(year)
    eng_unit_cost_usd = float(eng_unit_cost_usd)
    eng_maint_mh = float(_get_field(engine, "maint_mh_per_fh", 3.5 * engine_count))

    return {
        "empty_mass_kg": empty_mass_kg,
        "airframe_mass_kg": airframe_mass_kg,
        "engine_count": engine_count,
        "engine_mass_kg": engine_mass_kg,
        "afterburner": afterburner,
        "wing_sweep_deg": wing_sweep_deg,
        "wing_tc": wing_tc,
        "delta_wing": delta_wing,
        "variable_sweep": variable_sweep,
        "area_ruled": area_ruled,
        "inlet_variable": inlet_variable,
        "carrier_capable": carrier_capable,
        "al_frac": al_frac,
        "steel_frac": steel_frac,
        "ti_frac": ti_frac,
        "avionics_level": avionics_level,
        "internal_bay": internal_bay,
        "gun_count": gun_count,
        "hardpoints": hardpoints,
        "max_mach": max_mach,
        "eng_unit_cost_usd": eng_unit_cost_usd,
        "eng_maint_mh": eng_maint_mh,
    }


def estimate_costs(
    design: Any,
    mass_breakdown: Any,
    engine: Any,
    quantity: int,
    year: int,
    company: Any = None,
    tech_context: Any = None,
    *,
    max_mach: Optional[float] = None,
    prototypes: Optional[int] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> CostEstimate:
    """Compute recurring unit flyaway cost, RDT&E development cost, and maintenance hours.

    Conforms to `docs/spec/00_conventions.md` §3 & §4.4 and `docs/spec/03_tech_effect_keys.md` §2.7.
    All monetary outputs are nominal **then-year US dollars** for `year` (with constant-1950 USD
    fields also provided on the returned `CostEstimate`).
    """
    cfg = (tuning if tuning is not None else load_econ_tuning())["cer"]
    yr = int(round(year))
    qty = max(1, int(round(quantity)))
    n_proto = int(prototypes if prototypes is not None else _get_field(design, "prototypes", cfg["default_prototype_count"]))
    n_proto = max(1, n_proto)

    p = _extract_design_parameters(design, mass_breakdown, engine, yr, cfg, max_mach_override=max_mach)
    w_a_lb = p["airframe_mass_kg"] / LB_TO_KG
    v_kt = p["max_mach"] * float(cfg["tropopause_a_kt"])

    idx_aero = aero_cost_index_1950(yr)
    idx_cpi = cpi_index_1950(yr)

    # Read TechContext manufacturing & reliability modifiers (defaults match 1945-1950 baseline)
    labor_hours_factor = float(_get_tech_val(tech_context, "mfg.labor_hours_factor", 1.0))
    learning_rate_lab = float(_get_tech_val(tech_context, "mfg.learning_curve_rate", cfg["default_learning_curve_labor"]))
    tooling_cost_factor = float(_get_tech_val(tech_context, "mfg.tooling_cost_factor", 1.0))
    material_cost_factor = float(_get_tech_val(tech_context, "mfg.material_cost_factor", 1.0))
    ti_cost_factor = float(_get_tech_val(tech_context, "mfg.titanium_cost_factor", 1.0))
    quality_defect_factor = float(_get_tech_val(tech_context, "mfg.quality_defect_factor", 1.0))
    nc_machining = bool(_get_tech_val(tech_context, "mfg.nc_machining", False))
    honeycomb = bool(_get_tech_val(tech_context, "struct.honeycomb", False))
    eng_mtbf_factor = float(_get_tech_val(tech_context, "engine.mtbf_factor", 1.0))
    av_rel_factor = float(_get_tech_val(tech_context, "avionics.reliability_factor", 1.0))

    # Company overhead efficiency modifier (if company provided with custom overhead ratio)
    company_cost_mult = float(_get_field(company, "cost_efficiency_factor", 1.0))

    # Tech maturity penalty (03_tech_effect_keys.md §1.2)
    mean_imm = _mean_immaturity(design, tech_context)
    imm_dev_mult = 1.0 + float(cfg["immaturity_dev_cost_gain"]) * mean_imm
    imm_mfg_mult = 1.0 + float(cfg["immaturity_mfg_scrap_gain"]) * mean_imm

    # Complexity multipliers (RAND R-1693 / modified DAPCA-IV)
    c_mach = 1.0 + float(cfg["mach_complexity_coeff"]) * (
        max(0.0, p["max_mach"] - float(cfg["mach_complexity_threshold"])) ** float(cfg["mach_complexity_exp"])
    )
    c_tc = (
        1.0
        + float(cfg["tc_complexity_linear_coeff"]) * max(0.0, float(cfg["tc_complexity_threshold"]) - p["wing_tc"])
        + float(cfg["tc_ultra_thin_quad_coeff"]) * (max(0.0, float(cfg["tc_ultra_thin_threshold"]) - p["wing_tc"]) ** 2)
    )
    if nc_machining and p["wing_tc"] < 0.08:
        c_tc *= 1.0 - float(cfg["nc_machining_thin_wing_discount"])

    c_sweep = 1.0 + float(cfg["sweep_complexity_per_deg"]) * max(
        0.0, p["wing_sweep_deg"] - float(cfg["sweep_complexity_threshold_deg"])
    )

    fc = cfg["feature_complexity_add"]
    c_feat = 1.0 + (
        (float(fc["carrier_capable"]) if p["carrier_capable"] else 0.0)
        + (float(fc["area_ruled"]) if p["area_ruled"] else 0.0)
        + (float(fc["internal_bay"]) if p["internal_bay"] else 0.0)
        + (float(fc["inlet_variable"]) if p["inlet_variable"] else 0.0)
        + (float(fc["delta_wing"]) if p["delta_wing"] else 0.0)
        + (float(fc["variable_sweep"]) if p["variable_sweep"] else 0.0)
        + (float(fc["high_avionics_level_4plus"]) if p["avionics_level"] >= 4 else 0.0)
        + (float(fc["multi_engine"]) if p["engine_count"] >= 2 else 0.0)
        + (float(fc["afterburner"]) if p["afterburner"] else 0.0)
    )
    complexity_factor = c_mach * c_tc * c_sweep * c_feat

    # Material mix multiplier
    mm = cfg["material_cost_multipliers"]
    c_mat = (
        p["al_frac"] * float(mm["al"])
        + p["steel_frac"] * float(mm["steel"])
        + p["ti_frac"] * float(mm["ti"]) * ti_cost_factor
    )
    if honeycomb:
        c_mat *= float(cfg["honeycomb_material_mult"])

    # Wright learning curve factors over Q production units
    lc_lab = wright_cumulative_average_factor(qty, learning_rate_lab)
    lc_mat = wright_cumulative_average_factor(qty, float(cfg["default_learning_curve_material"]))

    # Recurring manufacturing labor hours & material (1950 base)
    w_norm = w_a_lb / float(cfg["ref_airframe_weight_lb"])
    v_norm = v_kt / float(cfg["ref_speed_kt"])

    h_mfg_t1 = (
        float(cfg["k_mfg_t1_hours"])
        * (w_norm ** float(cfg["exp_mfg_weight"]))
        * (v_norm ** float(cfg["exp_mfg_speed"]))
        * complexity_factor
        * labor_hours_factor
        * imm_mfg_mult
    )
    h_mfg_avg = h_mfg_t1 * lc_lab
    h_qc_t1 = float(cfg["qc_fraction_of_mfg_hours"]) * quality_defect_factor * h_mfg_t1
    h_qc_avg = float(cfg["qc_fraction_of_mfg_hours"]) * quality_defect_factor * h_mfg_avg

    r_mfg_1950 = float(cfg["r_mfg_wrap_1950_usd_hr"]) * company_cost_mult
    r_qc_1950 = float(cfg["r_qc_wrap_1950_usd_hr"]) * company_cost_mult

    mat_t1_1950 = (
        float(cfg["mat_t1_fraction_of_mfg_labor"])
        * (h_mfg_t1 / max(labor_hours_factor, 1e-6))
        * float(cfg["r_mfg_wrap_1950_usd_hr"])
        * c_mat
        * material_cost_factor
    )
    mat_avg_1950 = mat_t1_1950 * lc_mat

    t1_airframe_1950 = h_mfg_t1 * r_mfg_1950 + h_qc_t1 * r_qc_1950 + mat_t1_1950
    avg_airframe_1950 = h_mfg_avg * r_mfg_1950 + h_qc_avg * r_qc_1950 + mat_avg_1950

    t1_airframe_cost_usd = idx_aero * t1_airframe_1950
    airframe_unit_cost_usd = idx_aero * avg_airframe_1950

    # Avionics, Armament, and Engine (GFE/CFE recurring costs)
    av_1950 = float(cfg["avionics_unit_cost_1950_usd"][str(p["avionics_level"])])
    arm_1950 = (
        p["gun_count"] * float(cfg["armament_gun_unit_1950_usd"])
        + p["hardpoints"] * float(cfg["armament_hardpoint_unit_1950_usd"])
        + (float(cfg["armament_internal_bay_1950_usd"]) if p["internal_bay"] else 0.0)
    )
    avionics_unit_cost_usd = idx_aero * av_1950
    armament_unit_cost_usd = idx_aero * arm_1950
    engine_unit_cost_usd = p["engine_count"] * p["eng_unit_cost_usd"]
    gfe_unit_cost_usd = engine_unit_cost_usd + avionics_unit_cost_usd + armament_unit_cost_usd

    unit_flyaway_cost_usd = airframe_unit_cost_usd + gfe_unit_cost_usd

    # Non-recurring Development (RDT&E) cost (1950 base -> scaled by idx_aero)
    c_av_dev = 1.0 + float(cfg["k_av_dev_coeff"]) * (max(0, p["avionics_level"] - 1) ** float(cfg["exp_av_dev"]))
    h_eng = (
        float(cfg["k_eng_dev_hours"])
        * (w_norm ** float(cfg["exp_dev_weight"]))
        * (v_norm ** float(cfg["exp_dev_speed"]))
        * complexity_factor
        * c_av_dev
        * imm_dev_mult
    )
    r_eng_1950 = float(cfg["r_eng_wrap_1950_usd_hr"]) * company_cost_mult
    c_eng_1950 = h_eng * r_eng_1950
    c_dev_support_1950 = float(cfg["dev_support_fraction_of_eng"]) * c_eng_1950

    h_tool = (
        float(cfg["tooling_hours_fraction_of_eng"])
        * (h_eng / max(c_av_dev, 1e-6))
        * (v_norm ** float(cfg["exp_tooling_speed_offset"]))
        * tooling_cost_factor
    )
    c_tool_1950 = h_tool * float(cfg["r_tool_wrap_1950_usd_hr"]) * company_cost_mult

    proto_unit_1950 = (
        float(cfg["prototype_soft_tooling_mult"]) * (h_mfg_t1 * r_mfg_1950 + mat_t1_1950)
        + (engine_unit_cost_usd / max(idx_aero, 1e-9))
        + av_1950
    )
    c_proto_total_1950 = n_proto * proto_unit_1950
    c_ft_1950 = float(cfg["flight_test_fraction_of_eng"]) * c_eng_1950 * (n_proto ** float(cfg["flight_test_proto_exp"]))

    engineering_cost_usd = idx_aero * c_eng_1950
    dev_support_cost_usd = idx_aero * c_dev_support_1950
    tooling_cost_usd = idx_aero * c_tool_1950
    prototype_unit_cost_usd = idx_aero * proto_unit_1950
    prototypes_total_cost_usd = idx_aero * c_proto_total_1950
    flight_test_cost_usd = idx_aero * c_ft_1950

    dev_cost_usd_estimate = (
        engineering_cost_usd
        + dev_support_cost_usd
        + tooling_cost_usd
        + prototypes_total_cost_usd
        + flight_test_cost_usd
    )

    # Maintenance man-hours per flight hour (MMH/FH)
    airframe_maint = float(cfg["maint_base_mh_per_fh"]) + float(cfg["maint_weight_coeff"]) * w_norm + float(
        cfg["maint_mach_coeff"]
    ) * max(0.0, p["max_mach"] - 0.80)
    av_maint = (float(cfg["maint_avionics_coeff"]) * p["avionics_level"]) / max(0.25, av_rel_factor)
    eng_maint = p["eng_maint_mh"] / max(0.25, eng_mtbf_factor)
    maint_mh_per_fh = float(airframe_maint + av_maint + eng_maint)

    return CostEstimate(
        year=yr,
        quantity=qty,
        prototypes=n_proto,
        airframe_mass_kg=float(p["airframe_mass_kg"]),
        airframe_mass_lb=float(w_a_lb),
        max_mach=float(p["max_mach"]),
        learning_curve_rate=float(learning_rate_lab),
        wright_labor_factor=float(lc_lab),
        wright_material_factor=float(lc_mat),
        complexity_factor=float(complexity_factor),
        material_mix_factor=float(c_mat),
        immaturity_penalty_dev=float(imm_dev_mult),
        immaturity_penalty_mfg=float(imm_mfg_mult),
        aero_cost_index=float(idx_aero),
        cpi_index=float(idx_cpi),
        engineering_hours=float(h_eng),
        tooling_hours=float(h_tool),
        t1_mfg_labor_hours=float(h_mfg_t1),
        avg_mfg_labor_hours=float(h_mfg_avg),
        avg_qc_hours=float(h_qc_avg),
        t1_airframe_cost_usd=float(t1_airframe_cost_usd),
        airframe_unit_cost_usd=float(airframe_unit_cost_usd),
        engine_unit_cost_usd=float(engine_unit_cost_usd),
        avionics_unit_cost_usd=float(avionics_unit_cost_usd),
        armament_unit_cost_usd=float(armament_unit_cost_usd),
        gfe_unit_cost_usd=float(gfe_unit_cost_usd),
        unit_flyaway_cost_usd=float(unit_flyaway_cost_usd),
        engineering_cost_usd=float(engineering_cost_usd),
        dev_support_cost_usd=float(dev_support_cost_usd),
        tooling_cost_usd=float(tooling_cost_usd),
        prototype_unit_cost_usd=float(prototype_unit_cost_usd),
        prototypes_total_cost_usd=float(prototypes_total_cost_usd),
        flight_test_cost_usd=float(flight_test_cost_usd),
        dev_cost_usd_estimate=float(dev_cost_usd_estimate),
        constant_1950_unit_flyaway_usd=float(unit_flyaway_cost_usd / max(idx_cpi, 1e-9)),
        constant_1950_dev_cost_usd=float(dev_cost_usd_estimate / max(idx_cpi, 1e-9)),
        maint_mh_per_fh=float(maint_mh_per_fh),
    )
