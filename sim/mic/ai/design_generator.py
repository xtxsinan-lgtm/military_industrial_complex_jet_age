"""AI Parametric Aircraft Design Synthesis & Local-Search Optimizer (`sim/mic/ai/design_generator.py`).

Implements Module 07 (`generate_ai_design_for_rfp`):
- Synthesizes a valid `AircraftDesign` dictionary (conforming to `00_conventions.md` §4.2 and
  `sim/mic/aero/geometry.py`) tailored to a military `Requirement` (`ProgramSpec` or dict) and
  the AI airframer's historical signature (`company_signatures` + `ai_doctrine`).
- Enforces all `TechContext` caps (`validate_design` with zero `TECH_CAP:*` or `PACKAGING:*` errors).
- Runs a fast deterministic coordinate local search over wing area, sweep, thickness-to-chord,
  internal fuel, and available engines using Module 01 (`mic.perf.evaluate`).
"""
from __future__ import annotations

import copy
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union

from ..aero.geometry import derive_aircraft_geometry, get_tech_value, validate_design
from ..perf._stub_engine import HISTORICAL_ENGINES, StubEngineDeck, resolve_engine
from ..perf.performance import PerformanceReport, evaluate
from ..procurement.models import CriterionSpec, ProgramSpec
from ..procurement.scoring import clamp, criterion_sign, effective_objective_and_span
from .. procurement.tuning import load_tuning as load_proc_tuning
from ..tech.catalog import load_catalog
from ..tech.context import TechContext, build_tech_context, required_techs
from ..tech.research import CompanyTechState
from .company_ai import AICompanyState, load_ai_airframers
from .engine_vendor_ai import (
    CustomEngineQuote,
    get_available_catalog_engines,
    parse_date_to_day_and_year,
)
from .tuning import get_company_signature, load_ai_tuning


def _resolve_company_and_context(
    company: Any,
    unlocked_techs: Any,
    date_day: int,
    tuning: Dict[str, Any],
) -> Tuple[str, Dict[str, Any], str, TechContext]:
    """Extract `(company_id, traits, designation, TechContext)` from flexible inputs."""
    cat = load_catalog()
    if isinstance(company, AICompanyState):
        cid = company.id
        traits = dict(company.traits)
        desig = company.next_model_designation()
        default_ctx = company.tech_context(catalog=cat)
    elif isinstance(company, Mapping):
        cid = str(company.get("id", company.get("company_id", "north_american")))
        sig = get_company_signature(cid, tuning=tuning)
        doc = dict(company.get("ai_doctrine", {}))
        traits = {**sig, **doc, **dict(company.get("traits", {}))}
        prefix = str(traits.get("model_prefix", cid[:2].upper()))
        desig = str(company.get("designation", f"{prefix}-100"))
        default_ctx = None
    elif isinstance(company, str):
        cid = company
        all_ai = load_ai_airframers(exclude_player_company_id=None, date_day=date_day, catalog=cat, tuning=tuning)
        if cid in all_ai:
            ac = all_ai[cid]
            traits = dict(ac.traits)
            desig = ac.next_model_designation()
            default_ctx = ac.tech_context(catalog=cat)
        else:
            traits = get_company_signature(cid, tuning=tuning)
            desig = f"{traits.get('model_prefix', 'AI')}-100"
            default_ctx = None
    else:
        cid = str(getattr(company, "id", "north_american"))
        traits = get_company_signature(cid, tuning=tuning)
        desig = f"{traits.get('model_prefix', 'AI')}-100"
        default_ctx = None

    if isinstance(unlocked_techs, TechContext):
        ctx = unlocked_techs
    elif isinstance(unlocked_techs, CompanyTechState):
        ctx = unlocked_techs.context(catalog=cat)
    elif unlocked_techs is not None and isinstance(unlocked_techs, (Mapping, Iterable)):
        valid_ids = (
            {str(k): float(v) for k, v in unlocked_techs.items() if str(k) in cat.nodes}
            if isinstance(unlocked_techs, Mapping)
            else [str(tid) for tid in unlocked_techs if str(tid) in cat.nodes]
        )
        ctx = build_tech_context(cid, date_day, valid_ids, catalog=cat)
    elif default_ctx is not None:
        ctx = default_ctx
    else:
        # Unlock historical nodes up to current year for standalone calls
        cur_year = 1945.0 + date_day / 365.25
        auto_unlocked = {
            tid: 0.85
            for tid, node in cat.nodes.items()
            if float(node.historical_year) <= cur_year + 0.25
        }
        ctx = build_tech_context(cid, date_day, auto_unlocked, catalog=cat)

    return cid, traits, desig, ctx


def _extract_rfp_info(rfp: Union[ProgramSpec, Mapping[str, Any]]) -> Dict[str, Any]:
    """Normalize a `ProgramSpec` or RFP dictionary into structured design targets."""
    if isinstance(rfp, ProgramSpec):
        d = rfp.to_dict()
        criteria_objs = list(rfp.criteria)
    else:
        d = dict(rfp)
        criteria_objs = [
            c if isinstance(c, CriterionSpec) else CriterionSpec.from_dict(c)
            for c in d.get("criteria", [])
        ]

    issue_date = str(d.get("issue_date", "1950-01-01"))
    prop_due = str(d.get("proposal_due", issue_date))
    issue_day, issue_year, issue_iso = parse_date_to_day_and_year(issue_date)
    _, _, prop_due_iso = parse_date_to_day_and_year(prop_due)
    role = str(d.get("role", "day_fighter"))
    customer = str(d.get("customer", "USAF")).upper()
    eq = dict(d.get("equipment", {}))
    budget = dict(d.get("budget", {}))

    target_mach = 0.88 if issue_year < 1949.0 else (1.35 if issue_year < 1953.0 else 1.85)
    target_radius_m = 650000.0
    target_turn_dps = 11.5
    target_climb_mps = 45.0
    needs_carrier = bool(eq.get("carrier_capable", customer == "USN"))

    for c in criteria_objs:
        val_ref = float(c.objective_value if c.objective_value is not None else c.value)
        if c.key in ("max_mach_alt", "max_mach_sl"):
            target_mach = max(target_mach, val_ref)
        elif c.key == "combat_radius_m":
            target_radius_m = max(target_radius_m, val_ref)
        elif c.key == "ferry_range_m":
            target_radius_m = max(target_radius_m, val_ref * 0.34)
        elif c.key in ("sustained_turn_dps_m08_4572m", "instantaneous_turn_dps_m08_4572m"):
            target_turn_dps = max(target_turn_dps, val_ref)
        elif c.key == "climb_rate_sl_mps":
            target_climb_mps = max(target_climb_mps, val_ref)
        elif c.key == "carrier_suitability":
            needs_carrier = True

    return {
        "id": str(d.get("id", "rfp_custom")),
        "role": role,
        "customer": customer,
        "issue_day": issue_day,
        "issue_year": issue_year,
        "issue_iso": prop_due_iso,
        "equipment": eq,
        "criteria": criteria_objs,
        "unit_price_ceiling_usd": float(budget.get("unit_price_ceiling_usd", 850000.0)),
        "target_mach": target_mach,
        "target_radius_m": target_radius_m,
        "target_turn_dps": target_turn_dps,
        "target_climb_mps": target_climb_mps,
        "needs_carrier": needs_carrier,
    }


def _resolve_candidate_engines(
    available_engines: Any,
    issue_iso: str,
    ctx: TechContext,
    target_mach: float,
    tuning: Dict[str, Any],
) -> List[StubEngineDeck]:
    """Resolve and rank candidate engines compatible with `ctx`."""
    ab_unlocked = bool(get_tech_value(ctx, "engine.afterburner", False))
    decks: List[StubEngineDeck] = []

    if available_engines is None:
        cal = get_available_catalog_engines(issue_iso, tuning=tuning)
        decks = [entry["deck"] for entry in cal]
    else:
        for item in available_engines:
            if isinstance(item, StubEngineDeck):
                decks.append(item)
            elif isinstance(item, CustomEngineQuote):
                decks.append(item.engine_deck)
            elif isinstance(item, Mapping):
                if "deck" in item and isinstance(item["deck"], StubEngineDeck):
                    decks.append(item["deck"])
                else:
                    eid = str(item.get("engine_id", item.get("id", "J47-GE-27")))
                    decks.append(resolve_engine(eid, default_id=eid))
            elif isinstance(item, str):
                decks.append(resolve_engine(item, default_id=item))

    if not decks:
        decks = [HISTORICAL_ENGINES["J47-GE-27"]]

    # Filter out afterburning engines if company has not unlocked engine.afterburner
    compatible = [d for d in decks if (not d.has_afterburner) or ab_unlocked]
    if not compatible:
        compatible = decks

    want_ab = ab_unlocked and target_mach >= 1.02
    compatible.sort(
        key=lambda d: (
            1 if (d.has_afterburner == want_ab) else 0,
            d.ab_thrust_sl_N if want_ab else d.dry_thrust_sl_N,
        ),
        reverse=True,
    )
    return compatible[:3]


def _build_seed_design(
    company_id: str,
    designation: str,
    traits: Mapping[str, Any],
    rfp_info: Mapping[str, Any],
    engine_deck: StubEngineDeck,
    ctx: TechContext,
    tuning: Dict[str, Any],
) -> Dict[str, Any]:
    """Construct an initial TechContext-compliant `AircraftDesign` seed."""
    dg = tuning["design_generator"]
    target_mach = float(rfp_info["target_mach"])
    needs_carrier = bool(rfp_info["needs_carrier"])
    eq = rfp_info["equipment"]

    max_sweep = float(get_tech_value(ctx, "aero.wing_sweep_max_deg", 35.0))
    min_tc = float(get_tech_value(ctx, "aero.thin_wing_tc_min", 0.09))
    min_ar = float(get_tech_value(ctx, "aero.aspect_ratio_min", 3.5))
    delta_ok = bool(get_tech_value(ctx, "aero.delta_wing", False))

    delta_bias = float(traits.get("delta_bias", 0.10))
    use_delta = delta_ok and (delta_bias >= 0.65 or str(traits.get("preferred_planform", "")) == "delta") and target_mach >= 1.15 and not (needs_carrier and target_mach < 1.30)

    if use_delta and max_sweep >= 45.0:
        planform = "delta"
        base_sweep = min(max_sweep - 0.5, max(45.0, 46.0 + 0.5 * float(traits.get("sweep_bias_deg", 0.0))))
        base_ar = max(min_ar + 0.05, min(3.2, 2.25 + 0.35 * float(traits.get("aspect_ratio_bias", 0.0))))
        taper = 0.08
    elif target_mach < 0.84 and float(traits.get("sweep_bias_deg", 0.0)) <= -5.0:
        planform = "straight"
        base_sweep = max(0.0, min(12.0, max_sweep - 0.5))
        base_ar = max(min_ar + 0.1, min(6.2, 5.2 + float(traits.get("aspect_ratio_bias", 0.0))))
        taper = 0.48
    else:
        planform = "swept"
        desired_sweep = (28.0 if target_mach < 0.98 else (38.0 if target_mach < 1.45 else 45.0)) + float(traits.get("sweep_bias_deg", 0.0))
        base_sweep = max(0.0, min(max_sweep - 0.5, desired_sweep))
        desired_ar = (4.5 if target_mach < 1.10 else (3.6 if target_mach < 1.65 else 3.0)) + float(traits.get("aspect_ratio_bias", 0.0))
        base_ar = max(min_ar + 0.05, min(float(dg["max_aspect_ratio"]), desired_ar))
        taper = 0.32 if target_mach >= 1.2 else 0.42

    desired_tc = (0.092 if target_mach < 0.92 else (0.068 if target_mach < 1.35 else 0.048)) + float(traits.get("tc_bias", 0.0))
    tc_root = max(min_tc + 0.002, min(float(dg["max_tc_ratio"]), desired_tc))
    tc_tip = max(min_tc + 0.001, tc_root - 0.006)
    tc_mean = 0.5 * (tc_root + tc_tip)

    # Engine count & afterburner
    min_eng = int(eq.get("min_engines", 1))
    twin_bias = float(traits.get("twin_engine_bias", 0.20))
    need_twin_for_range_or_thrust = (
        (engine_deck.dry_thrust_sl_N < 26000.0 and float(rfp_info["target_radius_m"]) >= 850000.0)
        or (engine_deck.ab_thrust_sl_N < 28000.0 and target_mach >= 1.10)
    )
    eng_count = 2 if (min_eng >= 2 or twin_bias >= 0.72 or need_twin_for_range_or_thrust) else 1
    use_ab = bool(engine_deck.has_afterburner and get_tech_value(ctx, "engine.afterburner", False) and (target_mach >= 0.98 or float(rfp_info["target_climb_mps"]) >= 65.0))

    # Wing area & fuel sizing
    total_thrust = eng_count * (engine_deck.ab_thrust_sl_N if use_ab else engine_deck.dry_thrust_sl_N)
    base_area = max(float(dg["min_wing_area_m2"]), min(float(dg["max_wing_area_m2"]), total_thrust / (850.0 if needs_carrier else (820.0 if planform == "delta" else 920.0))))
    if planform == "delta":
        base_area = max(base_area, 36.0)
    elif needs_carrier:
        base_area = max(base_area, 31.0)

    devices: List[str] = []
    if bool(get_tech_value(ctx, "aero.fowler_flaps", False)):
        devices.append("fowler_flaps")
    else:
        devices.append("slotted_flaps")
    if bool(get_tech_value(ctx, "aero.le_slats", False)) and (needs_carrier or planform != "delta"):
        devices.append("le_slats")
    if needs_carrier and bool(get_tech_value(ctx, "aero.blown_flaps", False)):
        devices.append("blown_flaps")

    # Fuselage & intake
    fus_diam = max(1.12 * engine_deck.diameter_m * (1.36 if eng_count == 2 else 1.0), 1.32)
    if bool(eq.get("internal_bay_required", False)):
        fus_diam = max(fus_diam, 1.58)
    fus_len = max(10.5, min(21.0, fus_diam * (8.4 if target_mach < 1.2 else 10.2)))
    area_ruled = bool(get_tech_value(ctx, "aero.area_rule", False)) and target_mach >= 0.94 and float(traits.get("area_rule_adoption_bias", 0.75)) >= 0.45

    pref_intake = str(traits.get("preferred_intake", "nose"))
    if bool(eq.get("radar_required", False)) and pref_intake == "nose":
        pref_intake = "cheek"
    use_var_inlet = bool(get_tech_value(ctx, "aero.inlet_variable", False)) and target_mach >= 1.75
    use_spike_inlet = (not use_var_inlet) and bool(get_tech_value(ctx, "aero.inlet_spike", False)) and target_mach >= 1.35

    # Structure, systems, armament
    max_g_cap = float(get_tech_value(ctx, "struct.design_load_max_g", 7.33))
    load_g = min(max_g_cap, max(6.5, 7.33 + 0.5 * float(traits.get("ruggedness_g_bias", 0.0))))
    ti_avail = bool(get_tech_value(ctx, "struct.material.titanium_available", False))
    max_ti = float(get_tech_value(ctx, "struct.material.ti_max_fraction", 0.0)) if ti_avail else 0.0
    ti_frac = min(max_ti, 0.12 if target_mach >= 1.5 else 0.04) if ti_avail else 0.0
    steel_frac = min(float(get_tech_value(ctx, "struct.material.steel_max_fraction", 0.15)), 0.10)
    al_frac = max(0.0, 1.0 - ti_frac - steel_frac)

    radar_id: Optional[str] = None
    if bool(eq.get("radar_required", False)) and bool(get_tech_value(ctx, "avionics.radar_search", False)):
        for cand_r in ("an_apg_40", "an_apg_37", "an_apg_30", "an_aps_6"):
            if bool(get_tech_value(ctx, f"unlock.radar.{cand_r}", False)):
                radar_id = cand_r
                break

    gun_id = "m3_12_7mm"
    for cand_g in ("m39_20mm", "m24_20mm", "an_m3_20mm", "m3_12_7mm"):
        if bool(get_tech_value(ctx, f"unlock.gun.{cand_g}", cand_g == "m3_12_7mm")):
            gun_id = cand_g
            break
    gun_count = max(int(eq.get("min_guns_20mm", 0)), 4 if "20mm" in gun_id else 6)
    if bool(eq.get("internal_bay_required", False)) and int(eq.get("min_guns_20mm", 0)) == 0:
        gun_count = 0

    req_missiles = [str(m) for m in eq.get("missile_capability", [])]
    missile_ids = [
        m for m in req_missiles
        if bool(get_tech_value(ctx, f"unlock.missile.{m}", False)) or bool(get_tech_value(ctx, f"unlock.rocket.{m}", False))
    ]

    role_tags = [str(rfp_info["role"])]
    if needs_carrier and "carrier" not in role_tags:
        role_tags.append("carrier")

    base_fuel = max(1100.0, min(4200.0, (float(rfp_info["target_radius_m"]) / 420.0) * float(traits.get("internal_fuel_bias", 1.0))))
    design: Dict[str, Any] = {
        "id": f"{company_id}_{designation.lower().replace('-', '_')}_{rfp_info['id']}",
        "name": f"{company_id.replace('_', ' ').title()} {designation}",
        "company_id": company_id,
        "created_date": str(rfp_info["issue_iso"]),
        "role_tags": role_tags,
        "crew_count": max(1, int(eq.get("min_crew", 1))),
        "wing": {
            "planform_type": planform,
            "area_m2": round(base_area, 2),
            "aspect_ratio": round(base_ar, 3),
            "taper_ratio": round(taper, 3),
            "sweep_qc_deg": round(base_sweep, 2),
            "tc_root": round(tc_root, 4),
            "tc_tip": round(tc_tip, 4),
            "t_over_c": round(tc_mean, 4),
            "conical_camber": bool(planform == "delta" and get_tech_value(ctx, "aero.conical_camber", False)),
            "devices": devices,
        },
        "fuselage": {
            "length_m": round(fus_len, 2),
            "max_diameter_m": round(fus_diam, 3),
            "area_ruled": area_ruled,
            "canopy_type": "bubble",
        },
        "empennage": {
            "tailless": planform == "delta",
            "all_moving_tail": bool(planform != "delta" and get_tech_value(ctx, "aero.all_moving_tail", False) and target_mach >= 0.90),
            "t_tail": False,
        },
        "intake": {
            "type": pref_intake,
            "spike": use_spike_inlet,
            "variable": use_var_inlet,
        },
        "propulsion": {
            "engine_id": engine_deck.engine_id,
            "count": eng_count,
            "afterburner": use_ab,
        },
        "structure": {
            "design_load_factor_g": round(load_g, 2),
            "material_mix": {"al": round(al_frac, 3), "steel": round(steel_frac, 3), "ti": round(ti_frac, 3)},
            "carrier_capable": needs_carrier,
        },
        "fuel": {
            "internal_kg": round(base_fuel, 1),
            "drop_tanks_count": 2,
            "drop_tank_fuel_kg_each": 450.0,
            "combat_uses_drop_tanks": float(rfp_info["target_radius_m"]) >= 750000.0,
        },
        "systems": {
            "radar_id": radar_id,
            "fire_control_id": None,
            "avionics_level": min(int(get_tech_value(ctx, "avionics.level_max", 1)), 2 if radar_id else 1),
            "powered_controls": bool(get_tech_value(ctx, "systems.powered_controls", True)),
            "stability_augmentation": bool(get_tech_value(ctx, "systems.stability_augmentation", False) and target_mach >= 1.15),
            "ejection_seat": bool(get_tech_value(ctx, "systems.ejection_seat", True)),
            "inflight_refuel": False,
            "pressurized_cockpit": True,
        },
        "armament": {
            "guns": [{"gun_id": gun_id, "id": gun_id, "count": gun_count, "rounds_each": 200}] if gun_count > 0 else [],
            "hardpoints": min(int(get_tech_value(ctx, "armament.hardpoints_max", 2)), max(2, len(missile_ids))),
            "internal_bay": bool(eq.get("internal_bay_required", False) and get_tech_value(ctx, "armament.internal_bay", False)),
            "missile_ids": missile_ids,
        },
        "techs_used": [],
    }
    _clamp_fuel_to_volume(design, ctx, engine_deck)
    return design


def _clamp_fuel_to_volume(design: Dict[str, Any], ctx: TechContext, engine_deck: StubEngineDeck) -> None:
    """Ensure `fuel.internal_kg` fits within `1.02 * max_fuel_capacity_kg` to avoid packaging errors."""
    geom = derive_aircraft_geometry(
        design,
        tech_context=ctx,
        engine_mass_flow_kgps=float(getattr(engine_deck, "mass_flow_kgps", 42.0)),
    )
    max_safe = max(250.0, 0.98 * geom.max_fuel_capacity_kg)
    if float(design["fuel"]["internal_kg"]) > max_safe:
        design["fuel"]["internal_kg"] = round(max_safe, 1)


def score_design_against_rfp(
    design: Dict[str, Any],
    report: PerformanceReport,
    rfp_info: Mapping[str, Any],
    traits: Mapping[str, Any],
    tuning: Dict[str, Any],
) -> float:
    """Compute scalar objective score for a candidate design evaluated by Module 01."""
    dg = tuning["design_generator"]
    proc_t = load_proc_tuning()

    score = 0.0
    if not report.is_valid:
        score -= float(dg["penalty_invalid_design"]) * max(1, len(report.validation_errors))

    criteria: List[CriterionSpec] = list(rfp_info["criteria"])
    total_w = sum(max(0.05, c.weight) for c in criteria) or 1.0
    for c in criteria:
        w = max(0.05, c.weight) / total_w
        if c.key == "carrier_suitability":
            passed = bool(report.carrier_suitability.get("suitable", False))
            score += (float(dg["weight_objective_progress"]) * w) if passed else -120.0
            continue
        val = float(report.get(c.key, c.value))
        s_i = criterion_sign(c.op)
        _, span = effective_objective_and_span(c, proc_t)
        delta_thresh = s_i * (val - float(c.value))
        if delta_thresh < 0.0:
            miss_pct = abs(delta_thresh) / max(abs(float(c.value)), 1.0) * 100.0
            score -= float(dg["penalty_missed_threshold_per_pct"]) * miss_pct * (1.8 if c.kind == "threshold" else 1.0)
        prog = clamp(delta_thresh / max(span, 1e-3), -0.5, 1.35)
        score += float(dg["weight_objective_progress"]) * w * prog

    if bool(rfp_info["needs_carrier"]) and not bool(report.carrier_suitability.get("suitable", False)):
        score -= 90.0

    ceil_usd = max(100000.0, float(rfp_info["unit_price_ceiling_usd"]))
    cost_ratio = report.unit_flyaway_cost_usd / ceil_usd
    score += float(dg["weight_cost_efficiency"]) * clamp(1.15 - cost_ratio, -1.5, 0.5)

    # Signature fidelity bonus (keeps Convair delta, Lockheed low-t/c, McDonnell twin, etc.)
    pref_pf = str(traits.get("preferred_planform", "swept"))
    if pref_pf == "delta" and design["wing"]["planform_type"] == "delta":
        score += float(dg["weight_signature_fidelity"])
    return float(score)


def generate_ai_design_for_rfp(
    company: Any,
    rfp: Union[ProgramSpec, Mapping[str, Any]],
    unlocked_techs: Any = None,
    available_engines: Any = None,
    rng: Any = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Synthesize and locally refine a valid `AircraftDesign` dict for `(company, rfp)`.

    1. Extracts company doctrine & signature biases (`company_signatures`).
    2. Selects compatible engine(s) from `available_engines` (or historical release calendar).
    3. Builds an initial `TechContext`-compliant seed `AircraftDesign`.
    4. Runs a deterministic coordinate search over wing area, sweep, t/c, and internal fuel,
       evaluating each candidate via `mic.perf.evaluate(design, engine, tech_context)`.
    5. Populates `techs_used` and `performance_summary` and returns the winning `AircraftDesign` dict.
    """
    t = tuning if tuning is not None else load_ai_tuning()
    dg = t["design_generator"]
    rfp_info = _extract_rfp_info(rfp)
    cid, traits, desig, ctx = _resolve_company_and_context(
        company, unlocked_techs, int(rfp_info["issue_day"]), t
    )
    cand_engines = _resolve_candidate_engines(
        available_engines, str(rfp_info["issue_iso"]), ctx, float(rfp_info["target_mach"]), t
    )

    best_design: Optional[Dict[str, Any]] = None
    best_report: Optional[PerformanceReport] = None
    best_engine: StubEngineDeck = cand_engines[0]
    best_score = -1e12

    max_sweep = float(get_tech_value(ctx, "aero.wing_sweep_max_deg", 35.0))
    min_tc = float(get_tech_value(ctx, "aero.thin_wing_tc_min", 0.09))

    for eng in cand_engines[:2]:
        seed = _build_seed_design(cid, desig, traits, rfp_info, eng, ctx, t)
        rep = evaluate(seed, engine=eng, tech_context=ctx)
        sc = score_design_against_rfp(seed, rep, rfp_info, traits, t)
        if sc > best_score:
            best_score, best_design, best_report, best_engine = sc, seed, rep, eng

    assert best_design is not None and best_report is not None

    # Coordinate refinement over wing area, sweep, t/c, and fuel
    base_area = float(best_design["wing"]["area_m2"])
    for a_scale in dg["area_scale_candidates"]:
        cand = copy.deepcopy(best_design)
        cand["wing"]["area_m2"] = round(
            clamp(base_area * float(a_scale), float(dg["min_wing_area_m2"]), float(dg["max_wing_area_m2"])), 2
        )
        _clamp_fuel_to_volume(cand, ctx, best_engine)
        rep = evaluate(cand, engine=best_engine, tech_context=ctx)
        sc = score_design_against_rfp(cand, rep, rfp_info, traits, t)
        if sc > best_score:
            best_score, best_design, best_report = sc, cand, rep

    base_sweep = float(best_design["wing"]["sweep_qc_deg"])
    base_tc = float(best_design["wing"]["tc_root"])
    for sw_off in dg["sweep_offset_candidates_deg"]:
        for tc_off in dg["tc_offset_candidates"]:
            if sw_off == 0.0 and tc_off == 0.0:
                continue
            cand = copy.deepcopy(best_design)
            cand["wing"]["sweep_qc_deg"] = round(clamp(base_sweep + float(sw_off), 0.0, max_sweep - 0.5), 2)
            new_tc = clamp(base_tc + float(tc_off), min_tc + 0.002, float(dg["max_tc_ratio"]))
            cand["wing"]["tc_root"] = round(new_tc, 4)
            cand["wing"]["tc_tip"] = round(max(min_tc + 0.001, new_tc - 0.005), 4)
            cand["wing"]["t_over_c"] = round(0.5 * (cand["wing"]["tc_root"] + cand["wing"]["tc_tip"]), 4)
            _clamp_fuel_to_volume(cand, ctx, best_engine)
            rep = evaluate(cand, engine=best_engine, tech_context=ctx)
            sc = score_design_against_rfp(cand, rep, rfp_info, traits, t)
            if sc > best_score:
                best_score, best_design, best_report = sc, cand, rep

    base_fuel = float(best_design["fuel"]["internal_kg"])
    for f_scale in dg["fuel_scale_candidates"]:
        if f_scale == 1.0:
            continue
        cand = copy.deepcopy(best_design)
        cand["fuel"]["internal_kg"] = round(max(300.0, base_fuel * float(f_scale)), 1)
        _clamp_fuel_to_volume(cand, ctx, best_engine)
        rep = evaluate(cand, engine=best_engine, tech_context=ctx)
        sc = score_design_against_rfp(cand, rep, rfp_info, traits, t)
        if sc > best_score:
            best_score, best_design, best_report = sc, cand, rep

    try:
        best_design["techs_used"] = required_techs(best_design, ctx)
    except Exception:
        best_design["techs_used"] = list(ctx.unlocked[:5])

    best_design["performance_summary"] = {
        "max_mach_alt": round(best_report.max_mach_alt, 4),
        "max_mach_sl": round(best_report.max_mach_sl, 4),
        "combat_radius_m": round(best_report.combat_radius_m, 1),
        "sustained_turn_dps_m08_4572m": round(best_report.sustained_turn_dps_m08_4572m, 3),
        "climb_rate_sl_mps": round(best_report.climb_rate_sl_mps, 2),
        "unit_flyaway_cost_usd": round(best_report.unit_flyaway_cost_usd, 2),
        "dev_cost_usd_estimate": round(best_report.dev_cost_usd_estimate, 2),
        "is_valid": best_report.is_valid,
    }
    return best_design
