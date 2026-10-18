#!/usr/bin/env python3
"""Interactive & Chat-Turn Paper Prototype CLI (Validation #4).

Allows the user to play the full 'Intelligence -> Design -> Wind Tunnel ->
Proposal Downselect -> Prototype Flight Test & Flaw Fixes -> Hardware Fly-Off ->
Source Selection Debrief' loop either:
  1. Turn-by-turn in chat via `--state <path> --step <action_json>`
  2. Interactively in terminal via `--interactive`
  3. Demo walkthrough via `--demo`
"""

import argparse
import copy
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.mic.perf.performance import evaluate as evaluate_perf
from sim.mic.rng import RngStreamRegistry

# Units conversion constants (SI -> US Display per 00_conventions.md §3)
MPS_TO_KT = 1.0 / 0.514444
M_TO_FT = 1.0 / 0.3048
M_TO_NMI = 1.0 / 1852.0
KG_TO_LB = 1.0 / 0.45359237


SCENARIOS = {
    "1952_interceptor": {
        "id": "1952_interceptor",
        "title": "1952 USAF WS-201A Supersonic Interceptor Fly-Off (F-102 / F-100 Era)",
        "date_str": "1952-03-01",
        "year": 1952,
        "customer": "USAF",
        "budget_dev_usd": 28_000_000.0,
        "unit_price_ceiling_usd": 1_150_000.0,
        "quantity_planned": 650,
        "flyoff_days_budget": 540,
        "thresholds": {
            "max_mach_alt": 1.25,
            "service_ceiling_m": 15240.0,      # 50,000 ft
            "climb_rate_sl_mps": 65.0,         # ~12,800 ft/min
            "combat_radius_m": 600_000.0,      # ~324 nmi
            "sustained_turn_dps_m08_4572m": 8.5,
        },
        "objectives": {
            "max_mach_alt": 1.45,
            "service_ceiling_m": 16764.0,      # 55,000 ft
            "climb_rate_sl_mps": 90.0,         # ~17,700 ft/min
            "combat_radius_m": 850_000.0,      # ~459 nmi
            "sustained_turn_dps_m08_4572m": 11.0,
        },
        "weights": {"perf": 0.45, "cost": 0.20, "sched": 0.15, "risk": 0.20},
        "templates": {
            "1": ("YF-102 Pre-Area-Rule Delta (Convair Baseline)", "yf102_pre_area_rule.json"),
            "2": ("YF-100A Swept-Wing Super Sabre (North American Baseline)", "f100a_super_sabre.json"),
            "3": ("F-102A Area-Ruled Wasp-Waist Delta (Whitcomb Breakthrough)", "f102a_delta_dagger.json"),
        },
        "rivals": [
            {
                "company": "North American Aviation",
                "designation": "NA-192 Super Sabre",
                "config_rumor": "45-deg Swept Wing, Single J57 w/ Afterburner",
                "file": "f100a_super_sabre.json",
                "bid_price_usd": 980_000.0,
                "sched_days": 490,
                "tunnel_level": 2,
                "fix_threshold": 3,
                "pol_score": 78.0,
            },
            {
                "company": "Lockheed Aircraft Corp.",
                "designation": "CL-246 Zippered Dart",
                "config_rumor": "Ultra-Thin Trapezoidal Wing, High-Speed Interceptor",
                "file": "f104a_starfighter.json",
                "bid_price_usd": 1_050_000.0,
                "sched_days": 530,
                "tunnel_level": 2,
                "fix_threshold": 4,
                "pol_score": 72.0,
            },
            {
                "company": "Republic Aviation",
                "designation": "AP-63 Heavy Fighter",
                "config_rumor": "Twin-Engine Swept Heavy Interceptor",
                "file": "f101a_voodoo.json",
                "bid_price_usd": 1_240_000.0,
                "sched_days": 560,
                "tunnel_level": 1,
                "fix_threshold": 3,
                "pol_score": 68.0,
            },
        ],
    }
}

PILOT_ROSTER = [
    {
        "id": "pilot_vance",
        "name": "Maj. Chuck 'Brick' Vance (Ex-Muroc Test Pilot)",
        "skill": 0.90,
        "caution": 0.55,
        "flaw_find_bonus": 0.20,
        "crash_reduction": 0.25,
        "salary_per_phase_usd": 45_000.0,
        "desc": "High flaw discovery (+20%) & crash avoidance (-25%), aggressive envelope expansion.",
    },
    {
        "id": "pilot_mercer",
        "name": "Capt. Hal 'Slide-Rule' Mercer (NACA Engineering Pilot)",
        "skill": 0.85,
        "caution": 0.85,
        "flaw_find_bonus": 0.30,
        "crash_reduction": 0.40,
        "salary_per_phase_usd": 55_000.0,
        "desc": "Methodical NACA engineer-pilot: +30% flaw detection, -40% crash risk, +15 days/phase.",
    },
    {
        "id": "pilot_callahan",
        "name": "Lt. Walt 'Hotshoe' Callahan (Korean War Ace)",
        "skill": 0.78,
        "caution": 0.30,
        "flaw_find_bonus": 0.05,
        "crash_reduction": 0.0,
        "salary_per_phase_usd": 25_000.0,
        "desc": "Fast & cheap (-10 days/phase), pushes hard in high-G turns but higher accident risk.",
    },
]

ENGINE_OPTIONS = {
    "1": ("J57-P-7 (Pratt & Whitney — Twin-Spool Afterburning, 65.8 kN wet)", "j57_p21", True, "Pratt & Whitney"),
    "2": ("J47-GE-27 (General Electric — Reliable Subsonic/Transonic, 26.6 kN dry)", "j47_ge_27", False, "General Electric"),
    "3": ("J79-GE-3A (General Electric — Ahead-of-Time Variable-Stator Mach 2, 65.8 kN wet)", "j79_ge_3a", True, "General Electric"),
    "4": ("J65-W-16 (Curtiss-Wright — Sapphire Derivative, 34.2 kN dry)", "j65_w_16a", False, "Curtiss-Wright"),
}


def load_hist_aircraft(filename: str) -> dict:
    p = ROOT / "sim" / "data" / "aircraft_hist" / filename
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_design_summary(design: dict, year: int = 1952) -> dict:
    """Evaluates physics performance and extracts key metrics + diagnostics."""
    rep = evaluate_perf(design)
    d = rep.to_dict() if hasattr(rep, "to_dict") else vars(rep)
    diag = d.get("diagnostics", {})
    if hasattr(diag, "__dict__"):
        diag = vars(diag)
    return {
        "max_mach_alt": float(d["max_mach_alt"]),
        "max_mach_sl": float(d["max_mach_sl"]),
        "service_ceiling_m": float(d["service_ceiling_m"]),
        "climb_rate_sl_mps": float(d["climb_rate_sl_mps"]),
        "combat_radius_m": float(d["combat_radius_m"]),
        "sustained_turn_dps_m08_4572m": float(d["sustained_turn_dps_m08_4572m"]),
        "instantaneous_turn_dps_m08_4572m": float(d["instantaneous_turn_dps_m08_4572m"]),
        "takeoff_distance_m": float(d["takeoff_distance_m"]),
        "empty_mass_kg": float(d["empty_mass_kg"]),
        "mtow_kg": float(d["mtow_kg"]),
        "unit_flyaway_cost_usd": float(d["unit_flyaway_cost_usd"]),
        "dev_cost_usd_estimate": float(d["dev_cost_usd_estimate"]),
        "maint_mh_per_fh": float(d["maint_mh_per_fh"]),
        "static_margin": float(diag.get("static_margin_mac", 0.06)) if isinstance(diag, dict) else 0.06,
        "flags": list(diag.get("flags", [])) if isinstance(diag, dict) else [],
    }


def synthesize_flaws_for_design(design: dict, perf: dict, rng, year: int = 1952, hindsight: bool = False) -> list:
    """Deterministically generates hidden flaws based on transonic/supersonic novelty."""
    wing = design.get("wing", {})
    fus = design.get("fuselage", {})
    sweep = float(wing.get("sweep_quarter_chord_deg", 35.0))
    tc = float(wing.get("t_c_root", 0.08))
    ar = float(wing.get("aspect_ratio", 3.5))
    area_ruled = bool(fus.get("area_ruled", False))
    t_tail = bool(design.get("empennage", {}).get("t_tail", False))
    mach = perf["max_mach_alt"]

    candidate_flaws = []
    if mach >= 0.98 and not area_ruled:
        candidate_flaws.append({
            "id": "flaw_transonic_wave_wall",
            "true_name": "Severe Transonic Area-Distribution Wave Drag Spike",
            "known_from_year": 1953,
            "severity": 4,
            "phase_trigger": 3,
            "detect_tunnel_lvl": {1: 0.25, 2: 0.88},
            "detect_flight_phase": {1: 0.0, 2: 0.20, 3: 0.95, 4: 0.95},
            "fix_cost_usd": 1_850_000.0,
            "fix_days": 45,
            "penalty": {"max_mach_alt": -0.22, "combat_radius_m": -85_000.0},
            "fix_bonus_area_rule": True,
        })
    if sweep >= 42.0 or t_tail:
        candidate_flaws.append({
            "id": "flaw_pitch_up_inertial_coupling",
            "true_name": "High-Alpha Sabre-Dance Pitch-Up & Roll-Yaw Inertial Coupling",
            "known_from_year": 1954,
            "severity": 4,
            "phase_trigger": 4,
            "detect_tunnel_lvl": {1: 0.30, 2: 0.70},
            "detect_flight_phase": {1: 0.05, 2: 0.35, 3: 0.65, 4: 0.92},
            "fix_cost_usd": 1_200_000.0,
            "fix_days": 30,
            "penalty": {"sustained_turn_dps_m08_4572m": -1.8, "max_mach_alt": -0.05},
            "fix_bonus_area_rule": False,
        })
    if tc <= 0.065 and ar >= 3.2:
        candidate_flaws.append({
            "id": "flaw_aileron_reversal_flutter",
            "true_name": "Transonic Aeroelastic Wingtip Flutter & Aileron Reversal",
            "known_from_year": 1951,
            "severity": 3,
            "phase_trigger": 3,
            "detect_tunnel_lvl": {1: 0.20, 2: 0.75},
            "detect_flight_phase": {1: 0.0, 2: 0.40, 3: 0.88, 4: 0.90},
            "fix_cost_usd": 850_000.0,
            "fix_days": 22,
            "penalty": {"max_mach_alt": -0.09, "sustained_turn_dps_m08_4572m": -0.9},
            "fix_bonus_area_rule": False,
        })
    if design.get("propulsion", {}).get("afterburner", False):
        candidate_flaws.append({
            "id": "flaw_ab_screech_stall",
            "true_name": "High-Altitude Afterburner Screech & Inlet Buzz Flameout",
            "known_from_year": 1952,
            "severity": 2,
            "phase_trigger": 2,
            "detect_tunnel_lvl": {1: 0.15, 2: 0.55},
            "detect_flight_phase": {1: 0.20, 2: 0.75, 3: 0.85, 4: 0.85},
            "fix_cost_usd": 480_000.0,
            "fix_days": 14,
            "penalty": {"service_ceiling_m": -1100.0, "combat_radius_m": -45_000.0},
            "fix_bonus_area_rule": False,
        })

    active_flaws = []
    for cf in candidate_flaws:
        # Locked Decision D7: era-unknown flaws display as generic uncharted risk until encountered
        is_uncharted = (year < cf["known_from_year"]) and (not hindsight)
        cf_copy = copy.deepcopy(cf)
        cf_copy["discovered"] = False
        cf_copy["discovered_via"] = None
        cf_copy["fixed"] = False
        cf_copy["uncharted_before_discovery"] = is_uncharted
        active_flaws.append(cf_copy)
    return active_flaws


def compute_apparent_and_true_perf(base_perf: dict, flaws: list, sigma_mult: float, rng) -> tuple:
    """Computes true performance (with unfixed flaw penalties) and player Estimate with sigma."""
    true_perf = copy.deepcopy(base_perf)
    for fl in flaws:
        if not fl["fixed"]:
            for k, delta in fl["penalty"].items():
                if k in true_perf:
                    true_perf[k] = max(0.1, true_perf[k] + delta)

    # Estimate shown to player: before discovery, player sees base_perf + small noise;
    # once a flaw is discovered, Estimate reflects the flaw penalty (until fixed).
    est_perf = {}
    base_sigmas = {
        "max_mach_alt": 0.08,
        "service_ceiling_m": 750.0,
        "climb_rate_sl_mps": 6.5,
        "combat_radius_m": 55_000.0,
        "sustained_turn_dps_m08_4572m": 0.85,
        "unit_flyaway_cost_usd": 65_000.0,
    }
    for k, val in base_perf.items():
        if not isinstance(val, (int, float)):
            continue
        known_penalty = sum(
            fl["penalty"].get(k, 0.0)
            for fl in flaws
            if fl["discovered"] and not fl["fixed"]
        )
        sig = base_sigmas.get(k, abs(val) * 0.05) * sigma_mult
        est_perf[k] = {
            "value": val + known_penalty,
            "sigma": sig,
        }
    return true_perf, est_perf


def score_contender(perf: dict, bid_price_usd: float, sched_days: int, risk_score: float, pol_score: float, scen: dict) -> dict:
    """Computes S_perf, S_cost, S_sched, S_risk, S_pol, S_total (0..100 scale)."""
    thresh = scen["thresholds"]
    obj = scen["objectives"]
    metric_weights = {
        "max_mach_alt": 0.35,
        "service_ceiling_m": 0.20,
        "climb_rate_sl_mps": 0.15,
        "combat_radius_m": 0.15,
        "sustained_turn_dps_m08_4572m": 0.15,
    }
    s_perf_acc = 0.0
    threshold_misses = []
    for k, w in metric_weights.items():
        v = perf[k]
        t = thresh[k]
        o = obj[k]
        if v < t:
            ratio = max(0.0, (v / max(t, 1e-6)))
            pts = 55.0 * (ratio ** 2.5)
            threshold_misses.append(k)
        elif v >= o:
            pts = min(108.0, 100.0 + 15.0 * ((v - o) / max(o - t, 1e-6)))
        else:
            pts = 60.0 + 40.0 * ((v - t) / max(o - t, 1e-6))
        s_perf_acc += w * pts

    ceil_price = scen["unit_price_ceiling_usd"]
    price_ratio = bid_price_usd / ceil_price
    s_cost = max(15.0, min(100.0, 100.0 - 75.0 * max(0.0, price_ratio - 0.72)))

    sched_ratio = sched_days / float(scen["flyoff_days_budget"])
    s_sched = max(20.0, min(100.0, 100.0 - 65.0 * max(0.0, sched_ratio - 0.80)))

    s_risk = max(10.0, min(100.0, risk_score))
    w_map = scen["weights"]
    base_total = (
        w_map["perf"] * s_perf_acc
        + w_map["cost"] * s_cost
        + w_map["sched"] * s_sched
        + w_map["risk"] * s_risk
    )
    # Political / credibility adjustment (±5 pts max)
    pol_mod = (pol_score - 65.0) * 0.12
    s_total = base_total + pol_mod
    return {
        "S_perf": round(s_perf_acc, 2),
        "S_cost": round(s_cost, 2),
        "S_sched": round(s_sched, 2),
        "S_risk": round(s_risk, 2),
        "S_pol": round(pol_score, 2),
        "S_total": round(s_total, 2),
        "threshold_misses": threshold_misses,
    }


def format_perf_table(est_perf: dict, source_label: str, scen: dict) -> str:
    """Formats the player's current performance Estimate table with ±1σ error bars."""
    th = scen["thresholds"]
    ob = scen["objectives"]
    rows = [
        ("Max Speed (Alt)", "max_mach_alt", 1.0, "Mach", "{:.2f}"),
        ("Service Ceiling", "service_ceiling_m", M_TO_FT, "ft", "{:,.0f}"),
        ("Initial Climb Rate", "climb_rate_sl_mps", M_TO_FT * 60.0, "ft/min", "{:,.0f}"),
        ("Combat Radius", "combat_radius_m", M_TO_NMI, "nmi", "{:,.0f}"),
        ("Sustained Turn (M0.8/15k')", "sustained_turn_dps_m08_4572m", 1.0, "deg/s", "{:.1f}"),
    ]
    lines = []
    lines.append(f"  [Source Badge: {source_label}]")
    lines.append("  +----------------------------+----------------------+---------------+---------------+")
    lines.append("  | Metric                     | Player Estimate (±1σ)| RFP Threshold | RFP Objective |")
    lines.append("  +----------------------------+----------------------+---------------+---------------+")
    for label, key, scale, unit, fmt in rows:
        e = est_perf[key]
        val_s = fmt.format(e["value"] * scale)
        sig_s = fmt.format(e["sigma"] * scale)
        t_s = fmt.format(th[key] * scale)
        o_s = fmt.format(ob[key] * scale)
        status = "OK" if e["value"] >= th[key] else "LOW!"
        cell = f"{val_s} ± {sig_s} {unit} [{status}]"
        lines.append(f"  | {label:<26} | {cell:<20} | {t_s:>8} {unit:<4} | {o_s:>8} {unit:<4} |")
    lines.append("  +----------------------------+----------------------+---------------+---------------+")
    return "\n".join(lines)


def generate_rumors_table(scen: dict, inquiry_level: int = 0) -> str:
    """Generates Pre-Bid Trade-Press Rumors table (Locked Decision D10)."""
    sigma_mach = 0.14 if inquiry_level == 0 else 0.07
    sigma_price = 180_000.0 if inquiry_level == 0 else 90_000.0
    lines = []
    src = "AVIATION WEEK TRADE RUMORS (Free)" if inquiry_level == 0 else "WASHINGTON LIAISON INTEL BRIEF (Tightened ±σ)"
    lines.append(f"  === PRE-BID COMPETITOR INTELLIGENCE: {src} ===")
    lines.append("  +--------------------------+--------------------+-----------------------+------------------------+")
    lines.append("  | Rival Company & Project  | Rumored Max Speed  | Rumored Unit Price    | Configuration Rumor    |")
    lines.append("  +--------------------------+--------------------+-----------------------+------------------------+")
    for rv in scen["rivals"]:
        d = load_hist_aircraft(rv["file"])
        p = evaluate_design_summary(d)
        m_str = f"M {p['max_mach_alt']:.2f} ± {sigma_mach:.2f}"
        c_str = f"${rv['bid_price_usd']/1e3:,.0f}k ± ${sigma_price/1e3:,.0f}k"
        name_col = f"{rv['company'][:14]} ({rv['designation'][:7]})"
        lines.append(f"  | {name_col:<24} | {m_str:<18} | {c_str:<21} | {rv['config_rumor'][:22]:<22} |")
    lines.append("  +--------------------------+--------------------+-----------------------+------------------------+")
    return "\n".join(lines)


def run_demo_walkthrough():
    """Runs a complete non-interactive showcase comparing Pre-Area-Rule YF-102 (rushed)
    vs Area-Ruled F-102A (wind-tunnel + flight-tested) in the 1952 WS-201A Fly-Off."""
    scen = SCENARIOS["1952_interceptor"]
    rng = RngStreamRegistry(master_seed=19520301).stream("paper_proto")
    print("=" * 88)
    print(f"  MILITARY-INDUSTRIAL COMPLEX: JET AGE — PAPER PROTOTYPE WALKTHROUGH")
    print(f"  Scenario: {scen['title']} ({scen['date_str']})")
    print("=" * 88)
    print("\n[STEP 1] PENTAGON RFP & PRE-BID TRADE-PRESS RUMORS (Decision D10):")
    print(generate_rumors_table(scen, inquiry_level=0))

    # Compare Candidate A (YF-102 pre-area-rule) vs Candidate B (F-102A area-ruled)
    yf102 = load_hist_aircraft("yf102_pre_area_rule.json")
    perf_yf = evaluate_design_summary(yf102)
    flaws_yf = synthesize_flaws_for_design(yf102, perf_yf, rng, year=1952, hindsight=False)
    _, est_yf_sim = compute_apparent_and_true_perf(perf_yf, flaws_yf, sigma_mult=1.0, rng=rng)

    print("\n[STEP 2] INITIAL DESIGN BUREAU ESTIMATE — YF-102 (Un-Ruled Delta, J57-P-21):")
    print(format_perf_table(est_yf_sim, "SIM (Desk Slide-Rule, High ±σ)", scen))
    uncharted_cnt = sum(1 for fl in flaws_yf if fl["uncharted_before_discovery"])
    print(f"  * Fog-of-War Alert (Decision D7): {uncharted_cnt} [Uncharted High-Speed Regime Risks] flagged!")

    # Step 3: Slotted-Throat Wind Tunnel discovers the Transonic Wave Drag Wall!
    for fl in flaws_yf:
        if fl["id"] == "flaw_transonic_wave_wall":
            fl["discovered"] = True
            fl["discovered_via"] = "Slotted-Throat Transonic Wind Tunnel (Level 2)"
    _, est_yf_tunnel = compute_apparent_and_true_perf(perf_yf, flaws_yf, sigma_mult=0.45, rng=rng)
    print("\n[STEP 3] AFTER LEVEL-2 SLOTTED-THROAT TRANSONIC WIND TUNNEL ($450k, 30 days):")
    print("  >>> DISCOVERY! 'Uncharted High-Speed Regime Risk' revealed as:")
    print("      [Severity 4] Severe Transonic Area-Distribution Wave Drag Spike (Max Speed -0.22 Mach!)")
    print(format_perf_table(est_yf_tunnel, "TUNNEL (NACA Slotted-Throat, Tight ±σ)", scen))

    # Step 4: Apply Whitcomb Area Rule Fix -> F-102A + Flight Test with Capt. Hal Mercer
    f102a = load_hist_aircraft("f102a_delta_dagger.json")
    perf_f102a = evaluate_design_summary(f102a)
    flaws_f102a = synthesize_flaws_for_design(f102a, perf_f102a, rng, year=1952, hindsight=False)
    for fl in flaws_f102a:
        fl["discovered"] = True
        fl["fixed"] = True
    true_f102a, est_f102a_flight = compute_apparent_and_true_perf(perf_f102a, flaws_f102a, sigma_mult=0.12, rng=rng)
    print("\n[STEP 4] APPLY WHITCOMB AREA-RULE REDESIGN + 4-PHASE FLIGHT TEST (Pilot: Capt. Hal Mercer):")
    print(format_perf_table(est_f102a_flight, "FLIGHT (Edwards AFB Phase 1-4 Complete)", scen))

    # Step 5: Hardware Fly-Off & Source Selection Debrief (Decisions D6 & D10)
    print("\n[STEP 5] EDWARDS AFB HARDWARE FLY-OFF & SOURCE SELECTION DEBRIEF (Decisions D6 & D10):")
    contenders = [
        ("PLAYER: F-102A (Area-Ruled + Tested)", true_f102a, 1_020_000.0, 510, 91.0, 74.0),
        ("PLAYER (Alt: Rushed Un-Ruled YF-102)", compute_apparent_and_true_perf(perf_yf, flaws_yf, 0.1, rng)[0], 960_000.0, 440, 42.0, 74.0),
    ]
    for rv in scen["rivals"]:
        rd = load_hist_aircraft(rv["file"])
        rp = evaluate_design_summary(rd)
        contenders.append((f"{rv['company']} ({rv['designation']})", rp, rv["bid_price_usd"], rv["sched_days"], 82.0, rv["pol_score"]))

    scored = []
    for label, pdict, price, sdays, rsk, pol in contenders:
        sc = score_contender(pdict, price, sdays, rsk, pol, scen)
        scored.append((sc["S_total"], label, pdict, price, sc))
    scored.sort(key=lambda x: x[0], reverse=True)

    print("  +----------------------------------------+--------+--------+--------+--------+--------+---------+")
    print("  | Contender                              | S_perf | S_cost | S_schd | S_risk | S_pol  | S_TOTAL |")
    print("  +----------------------------------------+--------+--------+--------+--------+--------+---------+")
    for tot, label, pdict, price, sc in scored:
        print(f"  | {label:<38} | {sc['S_perf']:>6.1f} | {sc['S_cost']:>6.1f} | {sc['S_sched']:>6.1f} | {sc['S_risk']:>6.1f} | {sc['S_pol']:>6.1f} | {tot:>7.2f} |")
    print("  +----------------------------------------+--------+--------+--------+--------+--------+---------+")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MIC: Jet Age Paper Prototype CLI")
    parser.add_argument("--demo", action="store_true", help="Run the 1952 WS-201A Fly-Off walkthrough")
    args = parser.parse_args()
    run_demo_walkthrough()


def evaluate_custom_player_turn(
    template_id: str = "3",
    wing_area_m2: float = None,
    sweep_deg: float = None,
    t_c_root: float = None,
    area_ruled: bool = None,
    internal_fuel_kg: float = None,
    tunnel_level: int = 2,
    pilot_idx: int = 1,
    fix_flaws: bool = True,
    bid_price_usd: float = 960_000.0,
    inquiry_level: int = 1,
):
    """Evaluates a custom player turn (usable from chat or CLI flags) and prints full debrief."""
    scen = SCENARIOS["1952_interceptor"]
    rng = RngStreamRegistry(master_seed=19520915).stream("custom_turn")
    t_label, t_file = scen["templates"].get(str(template_id), scen["templates"]["3"])
    design = load_hist_aircraft(t_file)

    if wing_area_m2 is not None:
        design["wing"]["area_m2"] = float(wing_area_m2)
    if sweep_deg is not None:
        design["wing"]["sweep_quarter_chord_deg"] = float(sweep_deg)
    if t_c_root is not None:
        design["wing"]["t_c_root"] = float(t_c_root)
    if area_ruled is not None:
        design["fuselage"]["area_ruled"] = bool(area_ruled)
    if internal_fuel_kg is not None:
        design["fuel"]["internal_kg"] = float(internal_fuel_kg)

    perf = evaluate_design_summary(design)
    flaws = synthesize_flaws_for_design(design, perf, rng, year=1952, hindsight=False)
    pilot = PILOT_ROSTER[max(0, min(len(PILOT_ROSTER) - 1, pilot_idx))]

    sched_days = 430 + (20 if tunnel_level == 1 else (35 if tunnel_level >= 2 else 0))
    sigma_mult = 1.0
    for fl in flaws:
        p_tun = fl["detect_tunnel_lvl"].get(tunnel_level, 0.0) if tunnel_level > 0 else 0.0
        p_flt = max(fl["detect_flight_phase"].values()) + pilot["flaw_find_bonus"]
        if max(p_tun, p_flt) >= 0.50:
            fl["discovered"] = True
            if fix_flaws:
                fl["fixed"] = True
                sched_days += int(fl["fix_days"] * 0.7)

    if tunnel_level >= 2:
        sigma_mult = 0.12
    elif tunnel_level == 1:
        sigma_mult = 0.25
    else:
        sigma_mult = 0.35

    true_p, est_p = compute_apparent_and_true_perf(perf, flaws, sigma_mult=sigma_mult, rng=rng)
    unfixed = sum(1 for fl in flaws if not fl["fixed"])
    risk_score = max(25.0, 92.0 - 18.0 * unfixed + (5.0 if tunnel_level >= 2 else -8.0))

    print("=" * 88)
    print(f"  CUSTOM TURN EVALUATION — Base: {t_label}")
    print(f"  Geometry: S={design['wing']['area_m2']:.1f} m2 | Sweep={design['wing']['sweep_quarter_chord_deg']:.1f} deg | t/c={design['wing']['t_c_root']:.3f} | Area-Ruled={design['fuselage'].get('area_ruled', False)}")
    print(f"  Test Plan: Tunnel Lvl {tunnel_level} | Pilot: {pilot['name']} | Fix Flaws: {fix_flaws} | Bid: ${bid_price_usd:,.0f}")
    print("=" * 88)
    print(generate_rumors_table(scen, inquiry_level=inquiry_level))
    print("\n" + format_perf_table(est_p, f"TESTED PROTOTYPE (Tunnel L{tunnel_level} + Flight)", scen))

    contenders = [
        ("PLAYER PROTOTYPE", true_p, bid_price_usd, sched_days, risk_score, 75.0),
    ]
    for rv in scen["rivals"]:
        rd = load_hist_aircraft(rv["file"])
        rp = evaluate_design_summary(rd)
        contenders.append((f"{rv['company']} ({rv['designation']})", rp, rv["bid_price_usd"], rv["sched_days"], 82.0, rv["pol_score"]))

    scored = []
    for label, pdict, price, sdays, rsk, pol in contenders:
        sc = score_contender(pdict, price, sdays, rsk, pol, scen)
        scored.append((sc["S_total"], label, pdict, price, sc))
    scored.sort(key=lambda x: x[0], reverse=True)

    print("\n  === SOURCE SELECTION DEBRIEF ===")
    print("  +----------------------------------------+--------+--------+--------+--------+--------+---------+")
    print("  | Contender                              | S_perf | S_cost | S_schd | S_risk | S_pol  | S_TOTAL |")
    print("  +----------------------------------------+--------+--------+--------+--------+--------+---------+")
    for tot, label, pdict, price, sc in scored:
        print(f"  | {label:<38} | {sc['S_perf']:>6.1f} | {sc['S_cost']:>6.1f} | {sc['S_sched']:>6.1f} | {sc['S_risk']:>6.1f} | {sc['S_pol']:>6.1f} | {tot:>7.2f} |")
    print("  +----------------------------------------+--------+--------+--------+--------+--------+---------+")
