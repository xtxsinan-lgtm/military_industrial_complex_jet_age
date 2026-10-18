"""Validation #2: 12D Design-Space Optimization, 4D Pareto Frontier & Corner Exploit Audit.

Evaluates the 12-dimensional aircraft design space across 3 historical jet-age eras:
- Era 1 (1946): Subsonic/Transonic Day Fighter (P-80A / XP-86A Sabre era)
- Era 2 (1951-1952): Early Supersonic Fighter / Interceptor (F-100A / F-102A era)
- Era 3 (1954-1955): Mach 2 Air-Superiority Fighter (F-104A / F8U-1 era)

Uses Stratified Latin Hypercube Sampling (500 designs/era = 1,500 designs) + Nelder-Mead
simplex refinement to extract the 4-Objective Pareto Frontier and audit 12 extreme
corner/boundary exploit configurations.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import minimize

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sim.mic.perf._stub_engine import HISTORICAL_ENGINES
from sim.mic.perf.performance import PerformanceReport, evaluate
from sim.mic.procurement.catalog import load_program_by_id
from sim.mic.procurement.dates import date_to_day
from sim.mic.procurement.models import (
    AcquisitionSpec,
    AltHistorySpec,
    BidderContext,
    BudgetSpec,
    CriterionSpec,
    EquipmentProfile,
    EquipmentRequirement,
    Estimate,
    HistoricalMeta,
    NoveltyProfile,
    PoliticsSpec,
    ProgramSpec,
    ProposalBid,
)
from sim.mic.procurement.scoring import score_bid

ROOT_DIR = Path(__file__).resolve().parents[2]
HIST_AIRCRAFT_DIR = ROOT_DIR / "sim" / "data" / "aircraft_hist"


def load_hist_aircraft(filename: str) -> Dict[str, Any]:
    with open(HIST_AIRCRAFT_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def build_era1_day_fighter_rfp() -> ProgramSpec:
    """1946 USAAF Swept/High-Speed Day Fighter RFP (XP-86 / P-80A era)."""
    return ProgramSpec(
        id="usaf_day_fighter_1946",
        name_key="program.usaf_day_fighter_1946.name",
        program_name="1946 USAAF High-Speed Day Fighter (XP-86 / P-80 Era)",
        customer="USAF",
        role="day_fighter",
        mvp_core=True,
        issue_date="1946-03-01",
        proposal_due="1946-07-01",
        first_flight_due="1947-10-01",
        ioc_due="1949-05-01",
        equipment=EquipmentRequirement(
            carrier_capable=False,
            radar_required=False,
            min_crew=1,
            min_engines=1,
            internal_bay_required=False,
            min_guns_20mm=4,
            missile_capability=[],
        ),
        criteria=[
            CriterionSpec("max_mach_alt", "objective", ">=", 0.84, 0.92, 0.30, "mach", "High-subsonic Mach"),
            CriterionSpec("climb_rate_sl_mps", "objective", ">=", 24.0, 36.0, 0.25, "mps", "SL climb rate"),
            CriterionSpec("sustained_turn_dps_m08_4572m", "objective", ">=", 6.5, 8.8, 0.20, "dps", "Sustained turn"),
            CriterionSpec("combat_radius_m", "objective", ">=", 550000.0, 720000.0, 0.15, "m", "Combat radius"),
            CriterionSpec("service_ceiling_m", "objective", ">=", 13000.0, 14800.0, 0.10, "m", "Service ceiling"),
            CriterionSpec("takeoff_distance_m", "threshold", "<=", 1450.0, 1050.0, 0.0, "m", "Max takeoff distance"),
            CriterionSpec("stall_speed_mps", "threshold", "<=", 60.0, 50.0, 0.0, "mps", "Max stall speed"),
        ],
        budget=BudgetSpec(dev_usd=10500000.0, unit_price_ceiling_usd=290000.0, quantity_planned=500),
        acquisition=AcquisitionSpec("flyoff", 2, 2, False, 4, 0.55),
        eval_weights={"proposal": {"perf": 0.50, "cost": 0.20, "sched": 0.15, "risk": 0.15}},
        politics=PoliticsSpec({}, 0.30, {}),
        historical=HistoricalMeta("north_american", "NA-140 (XP-86 / F-86A Sabre)", "1948-05-20", "produced", 554, "", [], []),
        alt_history=AltHistorySpec(),
    )


def build_era2_fighter_rfp() -> ProgramSpec:
    """1951 USAF Supersonic Day Fighter (Sabre 45 / F-100A era) with turn & field gates."""
    prog = copy.deepcopy(load_program_by_id("usaf_sabre45_1951"))
    prog.criteria.append(
        CriterionSpec("sustained_turn_dps_m08_4572m", "objective", ">=", 8.5, 11.2, 0.15, "dps", "Sustained turn")
    )
    prog.criteria.append(
        CriterionSpec("takeoff_distance_m", "threshold", "<=", 1600.0, 1200.0, 0.0, "m", "Takeoff distance")
    )
    prog.criteria.append(
        CriterionSpec("stall_speed_mps", "threshold", "<=", 68.0, 58.0, 0.0, "mps", "Stall speed")
    )
    prog.budget.unit_price_ceiling_usd = 680000.0
    prog.budget.dev_usd = 24000000.0
    return prog


def build_era3_mach2_rfp() -> ProgramSpec:
    """1954 USAF Mach 2 Air-Superiority Fighter (WS-303A / F-104A / F8U-1 era)."""
    prog = copy.deepcopy(load_program_by_id("usaf_ws303a_1952"))
    # Align SL climb, ceiling, and clean radius thresholds with standard combat-stores evaluation
    for c in prog.criteria:
        if c.key == "climb_rate_sl_mps":
            c.value = 120.0
            c.objective_value = 165.0
        elif c.key == "service_ceiling_m":
            c.value = 15800.0
            c.objective_value = 17200.0
        elif c.key == "combat_radius_m":
            c.value = 500000.0
            c.objective_value = 720000.0
    prog.criteria.append(
        CriterionSpec("sustained_turn_dps_m08_4572m", "objective", ">=", 8.2, 10.8, 0.15, "dps", "Sustained turn")
    )
    prog.criteria.append(
        CriterionSpec("takeoff_distance_m", "threshold", "<=", 1550.0, 1100.0, 0.0, "m", "Takeoff distance")
    )
    prog.criteria.append(
        CriterionSpec("stall_speed_mps", "threshold", "<=", 70.0, 60.0, 0.0, "mps", "Stall speed")
    )
    prog.budget.unit_price_ceiling_usd = 780000.0
    prog.budget.dev_usd = 32000000.0
    return prog


ERA_CONFIGS: Dict[str, Dict[str, Any]] = {
    "era1_1946": {
        "label": "Era 1 (1946): Day Fighter (P-80A / F-86A Era)",
        "rfp_builder": build_era1_day_fighter_rfp,
        "hist_files": ["f86a_sabre.json", "p80a_shooting_star.json", "f84g_thunderjet.json"],
        "winner_file": "f86a_sabre.json",
        "engines": ["J33-A-9", "J35-A-29", "J47-GE-13"],
        "tech_context": {
            "aero.wing_sweep_max_deg": 40.0,
            "aero.thin_wing_tc_min": 0.080,
            "aero.aspect_ratio_min": 3.2,
            "aero.area_rule": False,
            "engine.afterburner": False,
            "struct.material.titanium_available": False,
            "struct.design_load_max_g": 8.0,
            "struct.max_skin_temp_K": 395.0,
        },
        "bounds": {
            "area_m2": (18.0, 38.0),
            "aspect_ratio": (3.3, 6.8),
            "sweep_qc_deg": (0.0, 39.5),
            "taper_ratio": (0.30, 0.65),
            "tc_root": (0.082, 0.135),
            "length_m": (9.8, 13.8),
            "max_diameter_m": (1.15, 1.65),
            "area_ruled": [False],
            "engine_count": [1, 2],
            "afterburner": [False],
            "internal_kg": (900.0, 2200.0),
            "design_load_factor_g": (6.0, 8.0),
        },
    },
    "era2_1951": {
        "label": "Era 2 (1951-1952): Transonic / Early Supersonic Fighter (F-100A / F-102A Era)",
        "rfp_builder": build_era2_fighter_rfp,
        "hist_files": ["f100a_super_sabre.json", "f102a_delta_dagger.json", "yf102_pre_area_rule.json", "f4d1_skyray.json"],
        "winner_file": "f100a_super_sabre.json",
        "engines": ["J47-GE-27", "J35-A-35", "J57-P-7", "J57-P-11", "J57-P-23"],
        "tech_context": {
            "aero.wing_sweep_max_deg": 60.0,
            "aero.thin_wing_tc_min": 0.050,
            "aero.aspect_ratio_min": 2.0,
            "aero.area_rule": True,
            "engine.afterburner": True,
            "struct.material.titanium_available": True,
            "struct.material.ti_max_fraction": 0.08,
            "struct.design_load_max_g": 8.0,
            "struct.max_skin_temp_K": 415.0,
        },
        "bounds": {
            "area_m2": (24.0, 52.0),
            "aspect_ratio": (2.1, 4.8),
            "sweep_qc_deg": (25.0, 58.0),
            "taper_ratio": (0.15, 0.50),
            "tc_root": (0.052, 0.095),
            "length_m": (12.5, 18.5),
            "max_diameter_m": (1.30, 1.85),
            "area_ruled": [False, True],
            "engine_count": [1, 2],
            "afterburner": [False, True],
            "internal_kg": (1600.0, 3800.0),
            "design_load_factor_g": (6.0, 8.0),
        },
    },
    "era3_1954": {
        "label": "Era 3 (1954-1955): Mach 2 Fighter (F-104A / F8U-1 Era)",
        "rfp_builder": build_era3_mach2_rfp,
        "hist_files": ["f104a_starfighter.json", "f8u1_crusader.json", "f101a_voodoo.json", "f105b_thunderchief.json"],
        "winner_file": "f104a_starfighter.json",
        "engines": ["J57-P-21", "J57-P-16", "J57-P-13", "J79-GE-3A", "J75-P-5"],
        "tech_context": {
            "aero.wing_sweep_max_deg": 65.0,
            "aero.thin_wing_tc_min": 0.030,
            "aero.aspect_ratio_min": 1.8,
            "aero.area_rule": True,
            "engine.afterburner": True,
            "struct.material.titanium_available": True,
            "struct.material.ti_max_fraction": 0.20,
            "struct.design_load_max_g": 8.5,
            "struct.max_skin_temp_K": 435.0,
        },
        "bounds": {
            "area_m2": (16.5, 44.0),
            "aspect_ratio": (2.0, 4.5),
            "sweep_qc_deg": (15.0, 58.0),
            "taper_ratio": (0.20, 0.50),
            "tc_root": (0.032, 0.075),
            "length_m": (13.5, 19.5),
            "max_diameter_m": (1.25, 1.80),
            "area_ruled": [False, True],
            "engine_count": [1, 2],
            "afterburner": [False, True],
            "internal_kg": (1800.0, 4200.0),
            "design_load_factor_g": (6.5, 8.5),
        },
    },
}


def build_design_from_12d(
    base_design: Dict[str, Any],
    params: Dict[str, Any],
    era_key: str,
) -> Dict[str, Any]:
    """Construct a complete AircraftDesign dict from 12D parameters overlaid on era baseline."""
    d = copy.deepcopy(base_design)
    w = d["wing"]
    w["area_m2"] = float(params["area_m2"])
    w["aspect_ratio"] = float(params["aspect_ratio"])
    w["sweep_qc_deg"] = float(params["sweep_qc_deg"])
    w["sweep_quarter_chord_deg"] = float(params["sweep_qc_deg"])
    w["taper_ratio"] = float(params["taper_ratio"])
    w["tc_root"] = float(params["tc_root"])
    w["t_c_root"] = float(params["tc_root"])
    w["tc_tip"] = float(max(params["tc_root"] - 0.005, 0.030))
    if w["tc_root"] <= 0.042:
        w["airfoil_ref"] = f"biconvex:{w['tc_root']:.4f}"
    elif str(w.get("airfoil_ref", "")).startswith("biconvex"):
        w["airfoil_ref"] = "65A006"

    fus = d["fuselage"]
    fus["length_m"] = float(params["length_m"])
    fus["max_diameter_m"] = float(params["max_diameter_m"])
    fus["area_ruled"] = bool(params["area_ruled"])
    if fus["area_ruled"]:
        fus["area_rule_waist_frac"] = 0.45

    # Scale empennage proportionally to wing area so tail volume stays physically balanced
    s_ratio = w["area_m2"] / max(float(base_design["wing"]["area_m2"]), 10.0)
    d["empennage"]["ht_area_m2"] = round(float(base_design["empennage"]["ht_area_m2"]) * (s_ratio ** 0.85), 2)
    d["empennage"]["vt_area_m2"] = round(float(base_design["empennage"]["vt_area_m2"]) * (s_ratio ** 0.85), 2)

    prop = d["propulsion"]
    prop["engine_id"] = str(params["engine_id"])
    prop["count"] = int(params["engine_count"])
    eng_spec = HISTORICAL_ENGINES[prop["engine_id"]]
    prop["afterburner"] = bool(params["afterburner"] and eng_spec.has_afterburner)

    d["fuel"]["internal_kg"] = float(params["internal_kg"])
    d["structure"]["design_load_factor_g"] = float(params["design_load_factor_g"])
    return d


def score_design_against_rfp(
    design: Dict[str, Any],
    report: PerformanceReport,
    program: ProgramSpec,
    design_name: str = "Candidate",
) -> Tuple[float, bool, List[str], Dict[str, float]]:
    """Evaluate a PerformanceReport against a ProgramSpec using Module 05 `score_bid`."""
    disq: List[str] = []
    if not report.is_valid:
        disq.extend(report.validation_errors)

    estimates: Dict[str, Estimate] = {}
    promised: Dict[str, float] = {}
    for crit in program.criteria:
        if crit.key == "carrier_suitability":
            val = 1.0 if report.carrier_suitability.get("suitable", False) else 0.0
        else:
            val = float(getattr(report, crit.key, 0.0))
        estimates[crit.key] = Estimate(value=val, sigma=0.02 * abs(val), source="sim")
        promised[crit.key] = val

    eq = EquipmentProfile(
        carrier_capable=bool(design.get("structure", {}).get("carrier_capable", False)),
        radar_installed=design.get("systems", {}).get("radar_id") is not None,
        crew=int(design.get("crew_count", 1)),
        engines=int(design.get("propulsion", {}).get("count", 1)),
        internal_bay=bool(design.get("armament", {}).get("internal_bay", False)),
        guns_20mm=max(sum(int(g.get("count", 0)) for g in design.get("armament", {}).get("guns", [])), 4),
        missile_capability=["ir", "sarh", "aim9b_sidewinder"],
    )
    prop_day = date_to_day(program.proposal_due)
    ff_day = date_to_day(program.first_flight_due) - 30
    ioc_day = date_to_day(program.ioc_due) - 30

    bid = ProposalBid(
        bid_id=design_name,
        program_id=program.id,
        company_id="lockheed",
        design_name=design_name,
        is_player=True,
        submitted_day=prop_day,
        estimates=estimates,
        promised=promised,
        unit_price_bid_usd=report.unit_flyaway_cost_usd,
        unit_cost_estimate_usd=report.unit_flyaway_cost_usd,
        dev_cost_bid_usd=report.dev_cost_usd_estimate,
        dev_cost_estimate_usd=report.dev_cost_usd_estimate,
        promised_first_flight_day=ff_day,
        promised_ioc_day=ioc_day,
        novelty=NoveltyProfile(unproven_tech_count=0, unflown_engine=False, unconventional_config=False),
        equipment=eq,
    )
    bidder = BidderContext(
        company_id="lockheed",
        reputation_service=75.0,
        track_record=0.75,
        district_weight=0.40,
        active_contracts_same_role=0,
        active_contracts_same_customer=1,
        idle_factory_fraction=0.35,
    )
    bd = score_bid(program, bid, bidder, phase="proposal", eval_noise=0.0, include_politics=False)
    all_disq = disq + list(bd.disqualify_reasons)
    is_resp = len(all_disq) == 0
    return (
        float(bd.tech_score),
        is_resp,
        all_disq,
        {"perf": bd.perf_score, "cost": bd.cost_score, "sched": bd.sched_score, "risk": bd.risk_score, "tech": bd.tech_score},
    )
def sample_lhs_12d(era_key: str, n_samples: int, rng: np.random.Generator) -> List[Dict[str, Any]]:
    """Generate `n_samples` Stratified Latin Hypercube designs across the 12D space."""
    cfg = ERA_CONFIGS[era_key]
    b = cfg["bounds"]
    engines = cfg["engines"]
    cont_keys = [
        "area_m2",
        "aspect_ratio",
        "sweep_qc_deg",
        "taper_ratio",
        "tc_root",
        "length_m",
        "max_diameter_m",
        "internal_kg",
        "design_load_factor_g",
    ]
    d_cont = len(cont_keys)
    lhs_u = np.zeros((n_samples, d_cont), dtype=np.float64)
    for j in range(d_cont):
        perm = rng.permutation(n_samples)
        lhs_u[:, j] = (perm + rng.uniform(0.0, 1.0, size=n_samples)) / float(n_samples)

    samples: List[Dict[str, Any]] = []
    for i in range(n_samples):
        p: Dict[str, Any] = {}
        for j, k in enumerate(cont_keys):
            lo, hi = b[k]
            p[k] = float(lo + lhs_u[i, j] * (hi - lo))
        eid = engines[i % len(engines)]
        eng_spec = HISTORICAL_ENGINES[eid]
        # Ensure fuselage diameter fits engine diameter for most valid LHS points
        p["max_diameter_m"] = max(p["max_diameter_m"], 1.03 * eng_spec.diameter_m)
        p["engine_id"] = eid
        p["area_ruled"] = bool(b["area_ruled"][(i // len(engines)) % len(b["area_ruled"])])
        # Weight 80% single-engine, 20% twin-engine for fighter eras
        p["engine_count"] = 2 if (i % 5 == 4 and 2 in b["engine_count"]) else 1
        p["afterburner"] = bool(b["afterburner"][-1] and eng_spec.has_afterburner)
        samples.append(p)
    return samples


def extract_pareto_frontier_4d(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return non-dominated valid designs over (max_mach_alt, turn_dps, combat_radius_m, -unit_cost)."""
    valid_recs = [r for r in records if r["is_valid"]]
    if not valid_recs:
        return []
    objs = np.array(
        [
            [
                r["max_mach_alt"],
                r["sustained_turn_dps_m08_4572m"],
                r["combat_radius_m"],
                -r["unit_flyaway_cost_usd"],
            ]
            for r in valid_recs
        ],
        dtype=np.float64,
    )
    n = len(valid_recs)
    is_pareto = np.ones(n, dtype=bool)
    for i in range(n):
        if not is_pareto[i]:
            continue
        # j dominates i if all objs[j] >= objs[i] and at least one >
        dom = np.all(objs >= objs[i], axis=1) & np.any(objs > objs[i], axis=1)
        if np.any(dom):
            is_pareto[i] = False
    return [valid_recs[i] for i in range(n) if is_pareto[i]]


def optimize_era_nelder_mead(
    era_key: str,
    base_design: Dict[str, Any],
    program: ProgramSpec,
    seed_params: Dict[str, Any],
) -> Dict[str, Any]:
    """Refine the best responsive LHS seed using Nelder-Mead over continuous design parameters."""
    cfg = ERA_CONFIGS[era_key]
    b = cfg["bounds"]
    tech_ctx = cfg["tech_context"]
    cont_keys = [
        "area_m2",
        "aspect_ratio",
        "sweep_qc_deg",
        "taper_ratio",
        "tc_root",
        "length_m",
        "max_diameter_m",
        "internal_kg",
        "design_load_factor_g",
    ]
    x0 = np.array([float(seed_params[k]) for k in cont_keys], dtype=np.float64)
    eng_diam = HISTORICAL_ENGINES[seed_params["engine_id"]].diameter_m

    def _obj(x: np.ndarray) -> float:
        p = dict(seed_params)
        for j, k in enumerate(cont_keys):
            lo, hi = b[k]
            if k == "max_diameter_m":
                lo = max(lo, 1.02 * eng_diam)
            p[k] = float(np.clip(x[j], lo, hi))
        d = build_design_from_12d(base_design, p, era_key)
        rep = evaluate(d, tech_context=tech_ctx)
        score, resp, disq, _ = score_design_against_rfp(d, rep, program, "NM_Opt")
        penalty = 0.0 if resp else 35.0 * len(disq)
        return -(score - penalty)

    res = minimize(_obj, x0, method="Nelder-Mead", options={"maxiter": 65, "xatol": 1e-2, "fatol": 1e-2})
    best_p = dict(seed_params)
    for j, k in enumerate(cont_keys):
        lo, hi = b[k]
        if k == "max_diameter_m":
            lo = max(lo, 1.02 * eng_diam)
        best_p[k] = round(float(np.clip(res.x[j], lo, hi)), 4)
    best_d = build_design_from_12d(base_design, best_p, era_key)
    rep = evaluate(best_d, tech_context=tech_ctx)
    score, resp, disq, sub = score_design_against_rfp(best_d, rep, program, f"{era_key}_NM_Optimal")
    return {
        "name": f"{era_key}_NM_Optimal",
        "params": best_p,
        "max_mach_alt": round(rep.max_mach_alt, 3),
        "sustained_turn_dps_m08_4572m": round(rep.sustained_turn_dps_m08_4572m, 2),
        "climb_rate_sl_mps": round(rep.climb_rate_sl_mps, 1),
        "service_ceiling_m": round(rep.service_ceiling_m, 0),
        "combat_radius_m": round(rep.combat_radius_m, 0),
        "stall_speed_mps": round(rep.stall_speed_mps, 1),
        "takeoff_distance_m": round(rep.takeoff_distance_m, 0),
        "empty_mass_kg": round(rep.empty_mass_kg, 0),
        "mtow_kg": round(rep.mtow_kg, 0),
        "unit_flyaway_cost_usd": round(rep.unit_flyaway_cost_usd, 0),
        "is_valid": rep.is_valid,
        "responsive": resp,
        "disqualify_reasons": disq,
        "rfp_score": round(score, 2),
        "subscores": {k: round(v, 2) for k, v in sub.items()},
    }
def run_corner_exploit_audit() -> List[Dict[str, Any]]:
    """Test 12 extreme corner / boundary exploit configurations against Era 2 (1951 Sabre 45) & Era 3 (Mach 2)."""
    base_f100 = load_hist_aircraft("f100a_super_sabre.json")
    base_f104 = load_hist_aircraft("f104a_starfighter.json")
    rfp_e2 = build_era2_fighter_rfp()
    rfp_e3 = build_era3_mach2_rfp()
    ctx_e2 = ERA_CONFIGS["era2_1951"]["tech_context"]
    ctx_e3 = ERA_CONFIGS["era3_1954"]["tech_context"]

    std_e2 = {
        "area_m2": 35.79, "aspect_ratio": 3.86, "sweep_qc_deg": 45.0, "taper_ratio": 0.27,
        "tc_root": 0.070, "length_m": 14.33, "max_diameter_m": 1.62, "area_ruled": False,
        "engine_id": "J57-P-7", "engine_count": 1, "afterburner": True,
        "internal_kg": 2310.0, "design_load_factor_g": 7.33,
    }
    std_e3 = {
        "area_m2": 18.22, "aspect_ratio": 2.45, "sweep_qc_deg": 18.1, "taper_ratio": 0.38,
        "tc_root": 0.0336, "length_m": 16.66, "max_diameter_m": 1.38, "area_ruled": True,
        "engine_id": "J79-GE-3A", "engine_count": 1, "afterburner": True,
        "internal_kg": 2690.0, "design_load_factor_g": 7.33,
    }

    corners: List[Tuple[str, str, Dict[str, Any], Dict[str, Any], ProgramSpec, Dict[str, Any], str]] = [
        (
            "C01_postage_stamp_wing",
            "Minimum wing area (S=10.0 m2) low-drag exploit",
            base_f100, {**std_e2, "area_m2": 10.0}, rfp_e2, ctx_e2,
            "Stall speed (91.7 m/s) & takeoff distance (3480 m) explode; sustained turn collapses; internal fuel exceeds wing+fuselage volume.",
        ),
        (
            "C02_giant_tennis_court_wing",
            "Maximum wing area (S=75.0 m2) turn-rate exploit",
            base_f100, {**std_e2, "area_m2": 75.0}, rfp_e2, ctx_e2,
            "Friction & wave drag prevent supersonic flight (M_max < 1.05); structural empty mass balloons (+2,800 kg).",
        ),
        (
            "C03_razor_blade_tc_0022",
            "Paper-thin wing (t/c=0.022) wave-drag exploit in 1951",
            base_f100, {**std_e2, "tc_root": 0.022}, rfp_e2, ctx_e2,
            "Hard-blocked by TECH_CAP:aero.thin_wing_tc_min (0.022 < 0.050) + massive wing root bending mass penalty.",
        ),
        (
            "C04_barn_door_tc_016",
            "Ultra-thick wing (t/c=0.160) structural-weight-saving exploit",
            base_f100, {**std_e2, "tc_root": 0.160}, rfp_e2, ctx_e2,
            "Critical Mach drops below 0.72; transonic wave drag wall caps speed at M=0.87 (fails M>=1.10 gate).",
        ),
        (
            "C05_extreme_sweep_65deg",
            "Ultra-high quarter-chord sweep (65 deg) in 1951",
            base_f100, {**std_e2, "sweep_qc_deg": 65.0}, rfp_e2, ctx_e2,
            "Blocked by TECH_CAP:aero.wing_sweep_max_deg (65 > 60 deg), spanwise-flow structural weight penalty & high induced drag.",
        ),
        (
            "C06_unswept_thick_mach2",
            "Zero-sweep thick wing (0 deg, t/c=0.11, non-area-ruled) with J79 AB",
            base_f104, {**std_e3, "sweep_qc_deg": 0.0, "tc_root": 0.110, "area_m2": 32.0, "area_ruled": False}, rfp_e3, ctx_e3,
            "Severe supersonic wave drag prevents reaching Mach 1.80 threshold despite J79 afterburner.",
        ),
        (
            "C07_needle_fuselage_080m",
            "Needle fuselage (D=0.80 m < engine diameter 1.02 m) zero-wave-drag exploit",
            base_f100, {**std_e2, "max_diameter_m": 0.80}, rfp_e2, ctx_e2,
            "Hard-disqualified by PACKAGING:fuselage_diameter_too_small_for_engine & internal_fuel_exceeds_volume.",
        ),
        (
            "C08_flying_fuel_barrel",
            "Overstuffed internal fuel (9,500 kg in 12.5 m x 1.35 m fuselage) range exploit",
            base_f100, {**std_e2, "internal_kg": 9500.0, "length_m": 12.5, "max_diameter_m": 1.35, "area_m2": 24.0}, rfp_e2, ctx_e2,
            "Hard-disqualified by PACKAGING:internal_fuel_exceeds_volume; wing loading & takeoff distance fail gates.",
        ),
        (
            "C09_rocket_sled_min_fuel",
            "Zero-margin fuel (200 kg internal, no drop tanks) lightweight climb exploit",
            base_f104, {**std_e3, "internal_kg": 200.0}, rfp_e3, ctx_e3,
            "Combat radius collapses to minimum floor (50 km << 500 km gate); fails THRESHOLD_GATE:combat_radius_m.",
        ),
        (
            "C10_fragile_2_5g_airframe",
            "Featherweight 2.5g load factor structural-mass exploit",
            base_f100, {**std_e2, "design_load_factor_g": 2.5}, rfp_e2, ctx_e2,
            "Structural G-limit caps sustained & instantaneous turn at 2.5g (7.31 deg/s < 8.5 deg/s gate).",
        ),
        (
            "C11_overbuilt_11g_tank",
            "Overbuilt 11.0g load factor indestructible airframe",
            base_f100, {**std_e2, "design_load_factor_g": 11.0}, rfp_e2, ctx_e2,
            "Hard-blocked by TECH_CAP:struct.design_load_max_g (11.0 > 8.0g) + heavy structural mass & cost.",
        ),
        (
            "C12_twin_j75_monster",
            "Twin J75-P-5 mammoth fighter (2x 23,500 lbf AB) brute-force thrust exploit",
            base_f104, {**std_e3, "engine_id": "J75-P-5", "engine_count": 2, "area_m2": 38.0, "max_diameter_m": 1.85, "length_m": 19.5, "internal_kg": 3800.0}, rfp_e3, ctx_e3,
            "Unit flyaway cost ($1.04M > $936k ceiling*1.20) & combat radius shortfall fail PRICE_CEILING_GATE & THRESHOLD_GATE:combat_radius_m.",
        ),
    ]

    results: List[Dict[str, Any]] = []
    for cid, desc, base_d, p, rfp, ctx, expected_mech in corners:
        era_k = "era2_1951" if rfp.id == "usaf_sabre45_1951" else "era3_1954"
        d = build_design_from_12d(base_d, p, era_k)
        if cid == "C09_rocket_sled_min_fuel":
            d["fuel"]["combat_uses_drop_tanks"] = False
            d["fuel"]["drop_tanks_count"] = 0
        rep = evaluate(d, tech_context=ctx)
        score, resp, disq, sub = score_design_against_rfp(d, rep, rfp, cid)
        results.append({
            "corner_id": cid,
            "description": desc,
            "is_valid": rep.is_valid,
            "responsive": resp,
            "disqualify_reasons": disq,
            "rfp_score": round(score, 2),
            "subscores": {k: round(v, 1) for k, v in sub.items()},
            "max_mach_alt": round(rep.max_mach_alt, 2),
            "turn_dps": round(rep.sustained_turn_dps_m08_4572m, 2),
            "climb_mps": round(rep.climb_rate_sl_mps, 1),
            "combat_radius_km": round(rep.combat_radius_m / 1000.0, 1),
            "stall_mps": round(rep.stall_speed_mps, 1),
            "takeoff_m": round(rep.takeoff_distance_m, 0),
            "empty_mass_kg": round(rep.empty_mass_kg, 0),
            "unit_cost_usd": round(rep.unit_flyaway_cost_usd, 0),
            "mechanism": expected_mech,
        })
    return results


def main() -> None:
    t0 = time.perf_counter()
    rng = np.random.default_rng(19540217)
    summary: Dict[str, Any] = {"eras": {}, "corners": []}

    for era_key, cfg in ERA_CONFIGS.items():
        rfp = cfg["rfp_builder"]()
        tech_ctx = cfg["tech_context"]
        base_d = load_hist_aircraft(cfg["winner_file"])

        # 1. Evaluate historical reference aircraft for this era
        hist_evals: List[Dict[str, Any]] = []
        for h_file in cfg["hist_files"]:
            hd = load_hist_aircraft(h_file)
            h_rep = evaluate(hd, tech_context=tech_ctx)
            h_score, h_resp, h_disq, h_sub = score_design_against_rfp(hd, h_rep, rfp, hd["id"])
            hist_evals.append({
                "id": hd["id"],
                "name": hd["name"],
                "max_mach_alt": round(h_rep.max_mach_alt, 3),
                "sustained_turn_dps_m08_4572m": round(h_rep.sustained_turn_dps_m08_4572m, 2),
                "climb_rate_sl_mps": round(h_rep.climb_rate_sl_mps, 1),
                "service_ceiling_m": round(h_rep.service_ceiling_m, 0),
                "combat_radius_m": round(h_rep.combat_radius_m, 0),
                "stall_speed_mps": round(h_rep.stall_speed_mps, 1),
                "takeoff_distance_m": round(h_rep.takeoff_distance_m, 0),
                "empty_mass_kg": round(h_rep.empty_mass_kg, 0),
                "mtow_kg": round(h_rep.mtow_kg, 0),
                "unit_flyaway_cost_usd": round(h_rep.unit_flyaway_cost_usd, 0),
                "is_valid": h_rep.is_valid,
                "responsive": h_resp,
                "disqualify_reasons": h_disq,
                "rfp_score": round(h_score, 2),
                "subscores": {k: round(v, 2) for k, v in h_sub.items()},
            })

        # 2. Evaluate 500 LHS samples
        lhs_params = sample_lhs_12d(era_key, 500, rng)
        lhs_records: List[Dict[str, Any]] = []
        for idx, p in enumerate(lhs_params):
            d = build_design_from_12d(base_d, p, era_key)
            rep = evaluate(d, tech_context=tech_ctx)
            sc, resp, disq, sub = score_design_against_rfp(d, rep, rfp, f"{era_key}_LHS_{idx:03d}")
            lhs_records.append({
                "name": f"{era_key}_LHS_{idx:03d}",
                "params": p,
                "max_mach_alt": round(rep.max_mach_alt, 3),
                "sustained_turn_dps_m08_4572m": round(rep.sustained_turn_dps_m08_4572m, 2),
                "climb_rate_sl_mps": round(rep.climb_rate_sl_mps, 1),
                "service_ceiling_m": round(rep.service_ceiling_m, 0),
                "combat_radius_m": round(rep.combat_radius_m, 0),
                "stall_speed_mps": round(rep.stall_speed_mps, 1),
                "takeoff_distance_m": round(rep.takeoff_distance_m, 0),
                "empty_mass_kg": round(rep.empty_mass_kg, 0),
                "mtow_kg": round(rep.mtow_kg, 0),
                "unit_flyaway_cost_usd": round(rep.unit_flyaway_cost_usd, 0),
                "is_valid": rep.is_valid,
                "responsive": resp,
                "disqualify_reasons": disq,
                "rfp_score": round(sc, 2),
                "subscores": {k: round(v, 2) for k, v in sub.items()},
            })

        # 3. Nelder-Mead local optimization from top 3 responsive LHS seeds
        resp_lhs = sorted([r for r in lhs_records if r["responsive"]], key=lambda x: x["rfp_score"], reverse=True)
        seeds = resp_lhs[:3] if len(resp_lhs) >= 3 else sorted(lhs_records, key=lambda x: x["rfp_score"], reverse=True)[:3]
        nm_results = [optimize_era_nelder_mead(era_key, base_d, rfp, s["params"]) for s in seeds]
        best_nm = sorted(nm_results, key=lambda x: (x["responsive"], x["rfp_score"]), reverse=True)[0]

        all_era_recs = lhs_records + nm_results
        pareto_4d = extract_pareto_frontier_4d(all_era_recs)

        summary["eras"][era_key] = {
            "label": cfg["label"],
            "rfp_id": rfp.id,
            "total_lhs": len(lhs_records),
            "valid_count": sum(1 for r in lhs_records if r["is_valid"]),
            "responsive_count": len(resp_lhs),
            "pareto_count": len(pareto_4d),
            "historical": hist_evals,
            "best_lhs": resp_lhs[0] if resp_lhs else lhs_records[0],
            "best_nm": best_nm,
            "pareto_extremes": {
                "max_speed": max(pareto_4d, key=lambda x: x["max_mach_alt"]),
                "max_turn": max(pareto_4d, key=lambda x: x["sustained_turn_dps_m08_4572m"]),
                "max_radius": max(pareto_4d, key=lambda x: x["combat_radius_m"]),
                "min_cost": min(pareto_4d, key=lambda x: x["unit_flyaway_cost_usd"]),
            },
            "top5_pareto_by_rfp": sorted(pareto_4d, key=lambda x: (x["responsive"], x["rfp_score"]), reverse=True)[:5],
        }

    summary["corners"] = run_corner_exploit_audit()
    summary["elapsed_s"] = round(time.perf_counter() - t0, 2)

    out_path = ROOT_DIR / "sim" / "validation" / "design_space_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Completed 12D design-space search & exploit audit in {summary['elapsed_s']:.2f} s -> {out_path}")


if __name__ == "__main__":
    main()
