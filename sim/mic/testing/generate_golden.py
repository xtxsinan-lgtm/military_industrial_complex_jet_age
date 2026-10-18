"""Generate golden test vectors `sim/golden/testing_*.json` for Module 06."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict

from .archetypes import ARCHETYPES, build_archetype_inputs
from .data_loader import REPO_ROOT
from .features import StubTechContext
from .flaws import evaluate_all_flaw_probabilities
from .flight_test import run_flight_test_programme
from .hashing import (
    driver_z_draw,
    flaw_u01_draw,
    fnv1a_64,
    hash_keys,
    keyed_normal,
    keyed_u01,
    mix64,
    value_noise_5d,
)
from .service import simulate_service_years
from .sources import run_prototype_rollout, run_tunnel_or_ground_campaign
from .truth import (
    compute_estimate_report,
    compute_true_performance_report,
    initialize_lineage_state,
)

GOLDEN_DIR = REPO_ROOT / "sim" / "golden"


def generate_all_golden_vectors() -> Dict[str, Path]:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    paths: Dict[str, Path] = {}

    # 1. Hashing & 5D Value Noise Continuity Vectors
    seed = 19531024
    c0 = (2.3333333333333335, 3.1666666666666665, 3.1933333333333334, 2.58351893845611, 3.72)
    c_pert = (c0[0] + 0.01, c0[1] - 0.008, c0[2] + 0.005, c0[3], c0[4])
    z0 = driver_z_draw(seed, "north_american_co:swept:0:nose:0:j47_ge_27", "north_american_co", "cdw", c0, 0.50)
    z_pert = driver_z_draw(seed, "north_american_co:swept:0:nose:0:j47_ge_27", "north_american_co", "cdw", c_pert, 0.50)

    hashing_golden = {
        "campaign_seed": seed,
        "tolerance_rel": 1e-6,
        "fnv1a_64": {
            "empty": fnv1a_64(""),
            "cdw": fnv1a_64("cdw"),
            "swept_wing_pitch_up": fnv1a_64("swept_wing_pitch_up"),
            "YF-102": fnv1a_64("YF-102"),
        },
        "mix64": {
            "0": mix64(0),
            "1": mix64(1),
            "19531024": mix64(19531024),
        },
        "keyed_draws": {
            "u01_example": keyed_u01(seed, "test_key", "cdw", 1),
            "normal_example": keyed_normal(seed, "test_key", "cdw", 1),
            "flaw_u01_pitch_up": flaw_u01_draw(seed, "north_american_co:swept:0:nose:0:j47_ge_27", "swept_wing_pitch_up"),
        },
        "value_noise_5d": {
            "coords_base": list(c0),
            "coords_perturbed": list(c_pert),
            "vn_base": value_noise_5d(seed, "north_american_co", "cdw", c0),
            "vn_perturbed": value_noise_5d(seed, "north_american_co", "cdw", c_pert),
            "driver_z_base": z0,
            "driver_z_perturbed": z_pert,
            "abs_diff": abs(z_pert - z0),
        },
    }
    p1 = GOLDEN_DIR / "testing_hashing_vectors.json"
    with open(p1, "w", encoding="utf-8") as f:
        json.dump(hashing_golden, f, indent=2)
    paths["hashing"] = p1

    # 2. Truth & Flaw Probabilities Across 4 Historical Archetypes
    arch_golden: Dict[str, Any] = {"campaign_seed": seed, "tolerance_rel": 1e-6, "archetypes": {}}
    for arch_id in ARCHETYPES:
        design, nom_perf, eng_diag, ctx, date_day = build_archetype_inputs(arch_id)
        state = initialize_lineage_state(
            campaign_seed=seed,
            design=design,
            nominal_perf=nom_perf,
            date_day=date_day,
            engine_diagnostics=eng_diag,
            tech_ctx=ctx,
        )
        true_perf = compute_true_performance_report(state)
        est_sim = compute_estimate_report(state, tech_ctx=ctx)
        flaw_probs = evaluate_all_flaw_probabilities(
            state.true_aircraft.feature_vector,
            date_day=date_day,
            tech_ctx=ctx,
        )
        arch_golden["archetypes"][arch_id] = {
            "date_day": date_day,
            "categorical_sig": state.true_aircraft.categorical_sig,
            "coords_5d": list(state.true_aircraft.coords_5d),
            "driver_priors": state.true_aircraft.driver_priors,
            "driver_theta_true": {
                d: state.true_aircraft.get_true_driver_theta(d)
                for d in state.true_aircraft.driver_theta_base
            },
            "flaw_trigger_probabilities": flaw_probs,
            "realized_flaws": {
                fid: {"severity": fs.severity, "trigger_prob": fs.trigger_prob, "u_draw": fs.u_draw}
                for fid, fs in state.true_aircraft.active_flaws.items()
            },
            "true_perf_selected": {
                k: true_perf[k]
                for k in (
                    "max_mach_alt",
                    "max_mach_sl",
                    "service_ceiling_m",
                    "climb_rate_sl_mps",
                    "sustained_turn_dps_m08_4572m",
                    "instantaneous_turn_dps_m08_4572m",
                    "combat_radius_m",
                    "empty_mass_kg",
                    "unit_flyaway_cost_usd",
                )
            },
            "sim_estimate_selected": {
                k: est_sim[k]
                for k in ("max_mach_alt", "sustained_turn_dps_m08_4572m", "combat_radius_m", "empty_mass_kg")
            },
        }
    p2 = GOLDEN_DIR / "testing_truth_and_flaws.json"
    with open(p2, "w", encoding="utf-8") as f:
        json.dump(arch_golden, f, indent=2)
    paths["truth_and_flaws"] = p2

    # 3. Bayesian Variance Reduction Progression & Transonic Choking Check
    design, nom_perf, eng_diag, ctx, date_day = build_archetype_inputs("early_supersonic_delta_1953")
    state = initialize_lineage_state(
        campaign_seed=seed,
        design=design,
        nominal_perf=nom_perf,
        date_day=date_day,
        engine_diagnostics=eng_diag,
        tech_ctx=ctx,
    )
    stages: Dict[str, Any] = {}
    est0 = compute_estimate_report(state, tech_ctx=ctx)
    stages["0_sim"] = {
        "cdw_sigma": math.sqrt(state.beliefs["cdw"].var_belief),
        "mass_sigma": math.sqrt(state.beliefs["mass"].var_belief),
        "max_mach_alt": est0["max_mach_alt"],
        "empty_mass_kg": est0["empty_mass_kg"],
    }

    # Test transonic choking when transonic_tunnel is False
    ctx_no_trans = StubTechContext(
        date_day=date_day,
        company_id=design["company_id"],
        overrides={**ctx.values, "testing.transonic_tunnel": False},
        tech_maturity=ctx.tech_maturity,
    )
    res_choked = run_tunnel_or_ground_campaign(
        seed, state, "low_speed_tunnel", provider_id="naca", depth="standard", tech_ctx=ctx_no_trans
    )
    est1 = compute_estimate_report(state, tech_ctx=ctx)
    stages["1_low_speed_tunnel_choked"] = {
        "choked": res_choked["choked"],
        "cdw_sigma": math.sqrt(state.beliefs["cdw"].var_belief),
        "clmax_sigma": math.sqrt(state.beliefs["clmax"].var_belief),
        "max_mach_alt": est1["max_mach_alt"],
    }

    # Slotted transonic tunnel
    run_tunnel_or_ground_campaign(
        seed, state, "transonic_slotted", provider_id="naca", depth="standard", tech_ctx=ctx
    )
    est2 = compute_estimate_report(state, tech_ctx=ctx)
    stages["2_transonic_slotted"] = {
        "cdw_sigma": math.sqrt(state.beliefs["cdw"].var_belief),
        "max_mach_alt": est2["max_mach_alt"],
    }

    # Prototype rollout
    run_prototype_rollout(seed, state, n_prototypes=2)
    est3 = compute_estimate_report(state, tech_ctx=ctx)
    stages["3_prototype_rollout"] = {
        "mass_sigma": math.sqrt(state.beliefs["mass"].var_belief),
        "empty_mass_kg": est3["empty_mass_kg"],
    }

    # Flight test speed envelope
    run_flight_test_programme(
        seed, state, syllabus_plan={"speed_envelope": "standard"}, tech_ctx=ctx
    )
    est4 = compute_estimate_report(state, tech_ctx=ctx)
    stages["4_flight_speed_envelope"] = {
        "cdw_sigma": math.sqrt(state.beliefs["cdw"].var_belief),
        "max_mach_alt": est4["max_mach_alt"],
    }

    # Service 1 year
    simulate_service_years(seed, state, years=1, max_fleet_size=120)
    est5 = compute_estimate_report(state, tech_ctx=ctx)
    stages["5_service_1yr"] = {
        "cdw_sigma": math.sqrt(state.beliefs["cdw"].var_belief),
        "max_mach_alt": est5["max_mach_alt"],
    }

    p3 = GOLDEN_DIR / "testing_bayesian_progression.json"
    with open(p3, "w", encoding="utf-8") as f:
        json.dump({"campaign_seed": seed, "tolerance_rel": 1e-6, "stages": stages}, f, indent=2)
    paths["bayesian_progression"] = p3

    # 4. Full Seeded Flight Programme Run
    design4, nom4, eng4, ctx4, day4 = build_archetype_inputs("swept_transonic_1950")
    st4 = initialize_lineage_state(
        campaign_seed=19500625,
        design=design4,
        nominal_perf=nom4,
        date_day=day4,
        engine_diagnostics=eng4,
        tech_ctx=ctx4,
    )
    t_res = run_tunnel_or_ground_campaign(
        19500625, st4, "transonic_slotted", provider_id="naca", depth="standard",
        auto_fix_detected_flaws=True, tech_ctx=ctx4,
    )
    p_res = run_prototype_rollout(19500625, st4, n_prototypes=2)
    f_res = run_flight_test_programme(
        19500625, st4,
        syllabus_plan={
            "low_speed": "standard",
            "speed_envelope": "standard",
            "altitude_envelope": "standard",
            "maneuver": "standard",
            "high_aoa_spin": "standard",
            "weapons_stores": "standard",
        },
        flaw_resolution_policy="fix_severe_else_placard",
        tech_ctx=ctx4,
    )
    s_res = simulate_service_years(19500625, st4, years=3, max_fleet_size=200)

    p4 = GOLDEN_DIR / "testing_flight_programme_run.json"
    with open(p4, "w", encoding="utf-8") as f:
        json.dump(
            {
                "campaign_seed": 19500625,
                "tolerance_rel": 1e-6,
                "tunnel_result": t_res,
                "prototype_rollout": p_res,
                "flight_result": {
                    "items_completed": f_res.items_completed,
                    "total_sorties_flown": f_res.total_sorties_flown,
                    "flight_test_days": f_res.flight_test_days,
                    "flight_test_cost_usd": f_res.flight_test_cost_usd,
                    "crashes": f_res.crashes,
                    "pilots_lost": f_res.pilots_lost,
                    "pilots_injured": f_res.pilots_injured,
                    "near_misses": f_res.near_misses,
                    "flaws_detected_in_flight": f_res.flaws_detected_in_flight,
                },
                "service_result": s_res,
                "final_total_testing_cost_usd": st4.total_testing_cost_usd,
                "final_total_testing_days": st4.total_testing_days,
            },
            f,
            indent=2,
        )
    paths["flight_programme_run"] = p4
    return paths


if __name__ == "__main__":
    out = generate_all_golden_vectors()
    for k, v in out.items():
        print(f"Generated {k}: {v}")
