"""Unit and golden-vector tests for Module 06 (`sim.mic.testing`)."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from mic.testing import (
    DEFAULT_TECH_EFFECT_VALUES,
    ExperienceLedger,
    StubTechContext,
    apply_flaw_fix_to_state,
    apply_flaw_placard_to_state,
    build_feature_vector,
    build_risk_watchlist,
    compute_estimate_report,
    compute_true_performance_report,
    driver_z_draw,
    evaluate_all_flaw_probabilities,
    evaluate_flaw_probability,
    flaw_u01_draw,
    fnv1a_64,
    generate_pilot_pool,
    get_flaw_catalog_map,
    inherit_variant_belief,
    initialize_lineage_state,
    keyed_normal,
    keyed_u01,
    load_flaws_data,
    mix64,
    run_flight_test_programme,
    run_prototype_rollout,
    run_tunnel_or_ground_campaign,
    simulate_service_years,
    value_noise_5d,
)
from mic.testing.archetypes import ARCHETYPES, build_archetype_inputs
from mic.testing.generate_golden import GOLDEN_DIR

CANONICAL_FLAW_FAMILIES = {
    "flutter",
    "aileron_reversal",
    "transonic_control_loss",
    "pitch_up",
    "inertia_coupling",
    "spin",
    "inlet",
    "engine_stall",
    "structural_fatigue",
    "systems",
    "manufacturing",
}


def test_flaw_catalog_completeness_and_family_mapping() -> None:
    """Verify 34 historical flaws exist and map strictly onto `03_tech_effect_keys.md` §2.6 families."""
    flaws = load_flaws_data()["flaws"]
    assert 25 <= len(flaws) <= 40
    assert len(flaws) == 34

    seen_ids = set()
    seen_families = set()
    for f in flaws:
        fid = f["id"]
        assert fid not in seen_ids, f"Duplicate flaw id {fid}"
        seen_ids.add(fid)
        assert f["family"] in CANONICAL_FLAW_FAMILIES, f"Invalid family {f['family']} on {fid}"
        seen_families.add(f["family"])
        assert 1 <= int(f["base_severity"]) <= 5
        assert 1945 <= int(f["known_from_year"]) <= 1960
        assert len(f["detect_prob_by_source"]) >= 2
        assert len(f["fixes"]) >= 1

    # Every canonical family from 03_tech_effect_keys.md §2.6 is covered
    assert seen_families == CANONICAL_FLAW_FAMILIES


def test_golden_hashing_and_value_noise_continuity() -> None:
    with open(GOLDEN_DIR / "testing_hashing_vectors.json", "r", encoding="utf-8") as f:
        golden = json.load(f)

    seed = int(golden["campaign_seed"])
    tol = float(golden["tolerance_rel"])

    for text, expected in golden["fnv1a_64"].items():
        actual_str = "" if text == "empty" else text
        assert fnv1a_64(actual_str) == int(expected)

    for k_str, expected in golden["mix64"].items():
        assert mix64(int(k_str)) == int(expected)

    assert keyed_u01(seed, "test_key", "cdw", 1) == pytest.approx(
        golden["keyed_draws"]["u01_example"], rel=tol
    )
    assert keyed_normal(seed, "test_key", "cdw", 1) == pytest.approx(
        golden["keyed_draws"]["normal_example"], rel=tol
    )

    c0 = golden["value_noise_5d"]["coords_base"]
    c_pert = golden["value_noise_5d"]["coords_perturbed"]
    vn0 = value_noise_5d(seed, "north_american_co", "cdw", c0)
    vn_pert = value_noise_5d(seed, "north_american_co", "cdw", c_pert)
    assert vn0 == pytest.approx(golden["value_noise_5d"]["vn_base"], rel=tol)
    assert vn_pert == pytest.approx(golden["value_noise_5d"]["vn_perturbed"], rel=tol)
    # Small tweak in coordinates produces smooth change (< 0.035 sigma), never a full reroll
    assert abs(vn_pert - vn0) < 0.035


def test_golden_truth_and_flaw_probabilities() -> None:
    with open(GOLDEN_DIR / "testing_truth_and_flaws.json", "r", encoding="utf-8") as f:
        golden = json.load(f)

    seed = int(golden["campaign_seed"])
    tol = float(golden["tolerance_rel"])

    for arch_id, g_arch in golden["archetypes"].items():
        design, nom_perf, eng_diag, ctx, date_day = build_archetype_inputs(arch_id)
        state = initialize_lineage_state(
            campaign_seed=seed,
            design=design,
            nominal_perf=nom_perf,
            date_day=date_day,
            engine_diagnostics=eng_diag,
            tech_ctx=ctx,
        )
        assert state.true_aircraft.categorical_sig == g_arch["categorical_sig"]

        for d, expected_theta in g_arch["driver_theta_true"].items():
            assert state.true_aircraft.get_true_driver_theta(d) == pytest.approx(expected_theta, rel=tol)

        probs = evaluate_all_flaw_probabilities(
            state.true_aircraft.feature_vector, date_day=date_day, tech_ctx=ctx
        )
        for fid, expected_p in g_arch["flaw_trigger_probabilities"].items():
            assert probs[fid] == pytest.approx(expected_p, rel=tol, abs=1e-9)

        true_perf = compute_true_performance_report(state)
        for m_key, expected_val in g_arch["true_perf_selected"].items():
            assert true_perf[m_key] == pytest.approx(expected_val, rel=tol)


def test_golden_bayesian_progression_and_transonic_choking() -> None:
    with open(GOLDEN_DIR / "testing_bayesian_progression.json", "r", encoding="utf-8") as f:
        golden = json.load(f)

    seed = int(golden["campaign_seed"])
    tol = float(golden["tolerance_rel"])
    stages = golden["stages"]

    design, nom_perf, eng_diag, ctx, date_day = build_archetype_inputs("early_supersonic_delta_1953")
    state = initialize_lineage_state(
        campaign_seed=seed,
        design=design,
        nominal_perf=nom_perf,
        date_day=date_day,
        engine_diagnostics=eng_diag,
        tech_ctx=ctx,
    )
    sigma_cdw_0 = math.sqrt(state.beliefs["cdw"].var_belief)
    assert sigma_cdw_0 == pytest.approx(stages["0_sim"]["cdw_sigma"], rel=tol)

    # Without transonic_tunnel unlocked, low_speed_tunnel reports choked and does not shrink cdw
    ctx_no_trans = StubTechContext(
        date_day=date_day,
        company_id=design["company_id"],
        overrides={**ctx.values, "testing.transonic_tunnel": False},
        tech_maturity=ctx.tech_maturity,
    )
    res_choked = run_tunnel_or_ground_campaign(
        seed, state, "low_speed_tunnel", provider_id="naca", depth="standard", tech_ctx=ctx_no_trans
    )
    assert res_choked["choked"] is True
    assert math.sqrt(state.beliefs["cdw"].var_belief) == pytest.approx(sigma_cdw_0, rel=tol)

    # Slotted transonic tunnel shrinks cdw sigma substantially
    run_tunnel_or_ground_campaign(
        seed, state, "transonic_slotted", provider_id="naca", depth="standard", tech_ctx=ctx
    )
    sigma_cdw_2 = math.sqrt(state.beliefs["cdw"].var_belief)
    assert sigma_cdw_2 < 0.25 * sigma_cdw_0
    assert sigma_cdw_2 == pytest.approx(stages["2_transonic_slotted"]["cdw_sigma"], rel=tol)

    # Prototype rollout collapses empty_mass_kg sigma
    sigma_mass_before = math.sqrt(state.beliefs["mass"].var_belief)
    run_prototype_rollout(seed, state, n_prototypes=2)
    sigma_mass_after = math.sqrt(state.beliefs["mass"].var_belief)
    assert sigma_mass_after < 0.15 * sigma_mass_before
    assert sigma_mass_after == pytest.approx(stages["3_prototype_rollout"]["mass_sigma"], rel=tol)


def test_golden_full_flight_programme_run() -> None:
    with open(GOLDEN_DIR / "testing_flight_programme_run.json", "r", encoding="utf-8") as f:
        golden = json.load(f)

    seed = int(golden["campaign_seed"])
    tol = float(golden["tolerance_rel"])

    design, nom, eng, ctx, day = build_archetype_inputs("swept_transonic_1950")
    st = initialize_lineage_state(
        campaign_seed=seed,
        design=design,
        nominal_perf=nom,
        date_day=day,
        engine_diagnostics=eng,
        tech_ctx=ctx,
    )
    run_tunnel_or_ground_campaign(
        seed, st, "transonic_slotted", provider_id="naca", depth="standard",
        auto_fix_detected_flaws=True, tech_ctx=ctx,
    )
    run_prototype_rollout(seed, st, n_prototypes=2)
    f_res = run_flight_test_programme(
        seed, st,
        syllabus_plan={
            "low_speed": "standard",
            "speed_envelope": "standard",
            "altitude_envelope": "standard",
            "maneuver": "standard",
            "high_aoa_spin": "standard",
            "weapons_stores": "standard",
        },
        flaw_resolution_policy="fix_severe_else_placard",
        tech_ctx=ctx,
    )
    s_res = simulate_service_years(seed, st, years=3, max_fleet_size=200)

    assert f_res.total_sorties_flown == golden["flight_result"]["total_sorties_flown"]
    assert f_res.flight_test_days == golden["flight_result"]["flight_test_days"]
    assert f_res.flight_test_cost_usd == pytest.approx(golden["flight_result"]["flight_test_cost_usd"], rel=tol)
    assert st.total_testing_cost_usd == pytest.approx(golden["final_total_testing_cost_usd"], rel=tol)
    assert s_res["total_retrofit_cost_usd"] == pytest.approx(golden["service_result"]["total_retrofit_cost_usd"], rel=tol)


def test_monotonic_flaw_mitigations_and_tech_effect_keys() -> None:
    """Verify slats/fences/area-rule/SAS and `testing.flaw_incidence.*` keys monotonically reduce risk."""
    design, nom, eng, ctx, day = build_archetype_inputs("swept_transonic_1950")
    feat_clean = build_feature_vector(design, nom, engine_diagnostics=eng, tech_ctx=ctx)

    design_slats = copy.deepcopy(design)
    design_slats["wing"]["devices"] = ["fowler_flaps", "le_slats", "wing_fences"]
    feat_slats = build_feature_vector(design_slats, nom, engine_diagnostics=eng, tech_ctx=ctx)

    flaw_map = get_flaw_catalog_map()
    p_pitch_clean = evaluate_flaw_probability(flaw_map["swept_wing_pitch_up"], feat_clean, day, tech_ctx=ctx)
    p_pitch_slats = evaluate_flaw_probability(flaw_map["swept_wing_pitch_up"], feat_slats, day, tech_ctx=ctx)
    assert p_pitch_slats < 0.30 * p_pitch_clean

    # Verify `testing.flaw_incidence.pitch_up` scales probability proportionally
    ctx_reduced = StubTechContext(
        date_day=day,
        overrides={**ctx.values, "testing.flaw_incidence.pitch_up": 0.50},
    )
    p_pitch_tech = evaluate_flaw_probability(flaw_map["swept_wing_pitch_up"], feat_clean, day, tech_ctx=ctx_reduced)
    assert p_pitch_tech == pytest.approx(0.50 * p_pitch_clean, rel=1e-6)


def test_fix_phase_cost_leverage_and_variant_inheritance() -> None:
    """Verify Design Phase Fix < Prototype Fix < Service Fix and variant belief inheritance."""
    design, nom, eng, ctx, day = build_archetype_inputs("early_supersonic_delta_1953")
    st_design = initialize_lineage_state(42, design, nom, day, engine_diagnostics=eng, tech_ctx=ctx)
    st_proto = initialize_lineage_state(42, design, nom, day, engine_diagnostics=eng, tech_ctx=ctx)
    st_srv = initialize_lineage_state(42, design, nom, day, engine_diagnostics=eng, tech_ctx=ctx)

    fid = next(iter(st_design.true_aircraft.active_flaws.keys()))
    res_d = apply_flaw_fix_to_state(st_design, fid, phase="design")
    res_p = apply_flaw_fix_to_state(st_proto, fid, phase="prototype")
    res_s = apply_flaw_fix_to_state(st_srv, fid, phase="service", fleet_size=200)

    assert res_d["total_cost_usd"] < 0.40 * res_p["total_cost_usd"]
    assert res_p["total_cost_usd"] < 0.25 * res_s["total_cost_usd"]

    # Variant inheritance: small tweak preserves most of tunnel variance reduction
    run_tunnel_or_ground_campaign(42, st_proto, "transonic_slotted", provider_id="naca", tech_ctx=ctx)
    var_parent_tested = st_proto.beliefs["cdw"].var_belief

    variant_design = copy.deepcopy(design)
    variant_design["id"] = "arch_yf102_block2"
    variant_design["wing"]["sweep_deg"] = 59.0  # tiny 1 deg change
    st_variant = inherit_variant_belief(st_proto, 42, variant_design, nom, day, engine_diagnostics=eng, tech_ctx=ctx)
    st_fresh = initialize_lineage_state(42, variant_design, nom, day, engine_diagnostics=eng, tech_ctx=ctx)

    assert st_variant.beliefs["cdw"].var_belief < 0.15 * st_fresh.beliefs["cdw"].var_belief
    assert st_variant.beliefs["cdw"].var_belief >= var_parent_tested
