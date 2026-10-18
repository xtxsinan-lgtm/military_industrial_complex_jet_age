"""Comprehensive unit, golden-vector, edge-case, and historical replay test suite for Module 05."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from sim.mic.procurement import (
    BidderContext,
    EquipmentProfile,
    Estimate,
    NoveltyProfile,
    ProposalBid,
    RandomSource,
    adapt_program_to_world,
    audit_milestone_promises,
    compute_cost_score,
    compute_credibility,
    compute_credible_value,
    compute_criterion_utility,
    compute_dynamic_incumbent_bias,
    compute_fpif_unit_price,
    compute_novelty_index,
    compute_politics_bonus,
    compute_risk_score,
    compute_schedule_score,
    create_capability_gap,
    create_contract_from_award,
    date_to_day,
    day_to_date,
    day_to_fiscal_year,
    day_to_iso,
    evaluate_flyoff,
    evaluate_monthly_rfp_trigger,
    evaluate_proposals,
    evaluate_unsolicited_proposal,
    generate_dynamic_ai_bids,
    generate_historical_entrant_bid,
    generate_historical_program_bids,
    generate_procedural_requirement,
    load_all_programs,
    load_budget_index_table,
    load_program_by_id,
    load_threat_milestones,
    load_tuning,
    preview_bid_evaluation,
    redirect_follow_on_program,
    review_annual_lot,
    score_bid,
    should_suppress_stopgap,
)
from sim.mic.procurement.golden_gen import (
    build_dynamic_golden_vectors,
    build_lifecycle_golden_vectors,
    build_scoring_golden_vectors,
)
from sim.mic.procurement.replay import replay_single_program, run_full_replay_suite

GOLDEN_DIR = Path(__file__).resolve().parents[2] / "sim" / "golden"


def _assert_nested_approx(actual: Any, expected: Any, rel: float = 1e-6) -> None:
    if isinstance(expected, float):
        assert actual == pytest.approx(expected, rel=rel, abs=1e-9)
    elif isinstance(expected, dict):
        assert isinstance(actual, dict)
        assert set(actual.keys()) == set(expected.keys())
        for k in expected:
            _assert_nested_approx(actual[k], expected[k], rel=rel)
    elif isinstance(expected, list):
        assert isinstance(actual, list)
        assert len(actual) == len(expected)
        for a, e in zip(actual, expected):
            _assert_nested_approx(a, e, rel=rel)
    else:
        assert actual == expected


def test_dates_roundtrip_and_fiscal_year() -> None:
    d0 = date_to_day("1945-01-01")
    assert d0 == 0
    assert day_to_iso(0) == "1945-01-01"

    d_korea = date_to_day("1950-06-25")
    dt = day_to_date(d_korea)
    assert (dt.year, dt.month, dt.day) == (1950, 6, 25)
    assert day_to_fiscal_year(date_to_day("1950-06-30")) == 1950
    assert day_to_fiscal_year(date_to_day("1950-07-01")) == 1951


def test_rng_box_muller_and_stream_determinism() -> None:
    rng_a = RandomSource([0.15, 0.75, 0.35, 0.85])
    rng_b = RandomSource([0.15, 0.75, 0.35, 0.85])
    assert rng_a.normal(0.0, 1.0) == pytest.approx(rng_b.normal(0.0, 1.0), abs=1e-12)
    assert rng_a.normal(5.0, 2.0) == pytest.approx(rng_b.normal(5.0, 2.0), abs=1e-12)

    rng_det = RandomSource(deterministic=True)
    assert rng_det.normal(0.0, 4.0) == 0.0
    assert rng_det.uniform() == 0.5


def test_catalog_16_programs_and_8_mvp_core() -> None:
    programs = load_all_programs()
    assert len(programs) == 16
    mvp_programs = [p for p in programs if p.mvp_core]
    non_mvp_programs = [p for p in programs if not p.mvp_core]
    assert len(mvp_programs) == 8
    assert len(non_mvp_programs) == 8

    for prog in programs:
        assert len(prog.criteria) >= 4
        assert len(prog.historical.competitors) >= 2
        winner_ids = {c.company_id for c in prog.historical.competitors}
        assert prog.historical.winner_company_id in winner_ids

    threats = load_threat_milestones()
    assert len(threats) == 7
    budgets = load_budget_index_table()
    assert set(budgets.keys()) == set(range(1945, 1962))


def test_golden_scoring_vectors_match() -> None:
    golden_file = GOLDEN_DIR / "procurement_scoring_vectors.json"
    assert golden_file.exists()
    expected = json.loads(golden_file.read_text(encoding="utf-8"))
    actual = build_scoring_golden_vectors()
    _assert_nested_approx(actual["vectors"], expected["vectors"], rel=expected["tolerance_rel"])

    # Verify key domain properties inside scoring vectors
    v = actual["vectors"]
    assert v["honest_incumbent"]["responsive"] is True
    assert v["overclaim_newcomer"]["responsive"] is True
    # Overclaiming newcomer has higher risk penalty (lower risk_score) and lower total score than honest incumbent
    assert v["overclaim_newcomer"]["risk_score"] < v["honest_incumbent"]["risk_score"]
    assert v["overclaim_newcomer"]["total_score"] < v["honest_incumbent"]["total_score"]
    assert v["overclaim_confidence"]["max_mach_alt"] < 0.05

    # Lowball bid has cost score clamped below 100 by buy-in floor and schedule score clamped at 110
    assert v["lowball_and_rush"]["cost_score"] < 95.0
    assert v["lowball_and_rush"]["sched_score"] == pytest.approx(110.0)

    # Non-responsive bid is flagged and lists all disqualifying gates
    assert v["non_responsive"]["responsive"] is False
    assert len(v["non_responsive"]["disqualify_reasons"]) >= 3


def test_golden_lifecycle_vectors_match() -> None:
    golden_file = GOLDEN_DIR / "procurement_lifecycle_vectors.json"
    assert golden_file.exists()
    expected = json.loads(golden_file.read_text(encoding="utf-8"))
    actual = build_lifecycle_golden_vectors()
    _assert_nested_approx(actual["vectors"], expected["vectors"], rel=expected["tolerance_rel"])

    v = actual["vectors"]
    # USN 1955 FAD: both McDonnell and Vought advance to fly-off, McDonnell XF4H-1 wins Stage 2
    assert set(v["fad_proposal_report"]["finalist_bid_ids"]) == {
        "usn_fad_1955__mcdonnell",
        "usn_fad_1955__vought",
    }
    assert v["fad_flyoff_report"]["winner_company_ids"] == ["mcdonnell"]

    # YF-102 pre-area-rule Mach 0.98 shortfall triggers show_cause + liquidated damages
    assert v["yf102_promise_audit"]["show_cause_triggered"] is True
    assert v["yf102_promise_audit"]["liquidated_damage_frac"] == pytest.approx(0.15)

    # F-108 Rapier FY1960 annual review cancels due to ICBM obsolescence + cost growth
    assert v["f108_annual_review"]["cancelled"] is True
    assert v["f108_annual_review"]["cancellation_reason"] == "doctrinal_obsolescence"


def test_golden_dynamic_vectors_match() -> None:
    golden_file = GOLDEN_DIR / "procurement_dynamic_vectors.json"
    assert golden_file.exists()
    expected = json.loads(golden_file.read_text(encoding="utf-8"))
    actual = build_dynamic_golden_vectors()
    _assert_nested_approx(actual["vectors"], expected["vectors"], rel=expected["tolerance_rel"])

    v = actual["vectors"]
    assert v["f11f_stopgap_suppressed"] is True
    assert v["redirected_gor101_incumbent_bias"]["lockheed"] == pytest.approx(0.55)
    assert v["monthly_trigger"]["should_issue"] is True
    assert v["unsolicited_pitch_result"]["accepted"] is True
    assert v["unsolicited_pitch_result"]["outcome"] == "sole_source_award"


def test_historical_replay_16_of_16_and_sensitivity() -> None:
    summary = run_full_replay_suite(write_markdown=False)
    assert summary["total_programs"] == 16
    assert summary["matches_with_politics"] == 16
    assert summary["matches_without_politics"] == 16
    assert summary["mvp_programs"] == 8
    assert summary["mvp_matches"] == 8
    # Average pure performance edge required for newcomer to beat incumbent is ~5% to 12%
    assert 4.0 <= summary["avg_perf_edge_required_pct"] <= 14.0
    assert summary["avg_combined_edge_required_pct"] < summary["avg_perf_edge_required_pct"]


def test_bid_sorting_invariance_under_stochastic_noise() -> None:
    prog = load_program_by_id("usaf_ws201a_1950")
    bids, bidders = generate_historical_program_bids(
        prog, rng=RandomSource(deterministic=True)
    )
    bids_reversed = list(reversed(bids))

    draws = [0.22, 0.68, 0.41, 0.53, 0.19, 0.77, 0.31, 0.84, 0.49, 0.61, 0.25, 0.73]
    rep_fwd = evaluate_proposals(prog, bids, bidders, rng=RandomSource(draws))
    rep_rev = evaluate_proposals(prog, bids_reversed, bidders, rng=RandomSource(draws))

    assert rep_fwd.winner_bid_ids == rep_rev.winner_bid_ids
    for r1, r2 in zip(rep_fwd.rankings, rep_rev.rankings):
        assert r1.bid_id == r2.bid_id
        assert r1.total_score == pytest.approx(r2.total_score, abs=1e-9)


def test_dynamic_ai_competitor_generation_and_evaluation() -> None:
    tuning = load_tuning()
    proc_prog = generate_procedural_requirement(
        customer="USN",
        role="carrier_interceptor",
        issue_day=date_to_day("1954-03-01"),
        demand_score=0.80,
        budget_index=1.15,
        sequence_num=3,
        tuning=tuning,
    )
    ai_roster = [
        {"company_id": "mcdonnell", "skill": 1.08, "reputation": 78.0, "track_record": 0.75},
        {"company_id": "grumman", "skill": 1.02, "reputation": 82.0, "track_record": 0.80},
        {"company_id": "vought", "skill": 0.98, "reputation": 70.0, "track_record": 0.65},
    ]
    bids, bidders = generate_dynamic_ai_bids(
        proc_prog, ai_roster, rng=RandomSource(deterministic=True), tuning=tuning
    )
    assert len(bids) == 3
    rep = evaluate_proposals(
        proc_prog, bids, bidders, rng=RandomSource(deterministic=True), tuning=tuning
    )
    assert rep.outcome in ("awarded", "downselected")
    assert len(rep.rankings) == 3
    assert all(r.responsive for r in rep.rankings)


def test_sole_responsive_beats_non_responsive_and_all_non_responsive_no_award() -> None:
    tuning = load_tuning()
    prog = load_program_by_id("usaf_ws201a_1950")
    bids, bidders = generate_historical_program_bids(
        prog, rng=RandomSource(deterministic=True), tuning=tuning
    )

    # Disqualify all bids except Republic (which normally loses on score to Convair)
    modified_bids = copy.deepcopy(bids)
    for b in modified_bids:
        if b.company_id != "republic":
            b.promised["max_mach_alt"] = 0.95  # below 1.20 threshold

    rep_sole = evaluate_proposals(
        prog, modified_bids, bidders, rng=RandomSource(deterministic=True), tuning=tuning
    )
    assert rep_sole.outcome == "awarded"
    assert rep_sole.winner_company_ids == ["republic"]

    # Disqualify all bids -> outcome is no_responsive_bid
    all_bad = copy.deepcopy(bids)
    for b in all_bad:
        b.promised["max_mach_alt"] = 0.90
    rep_none = evaluate_proposals(
        prog, all_bad, bidders, rng=RandomSource(deterministic=True), tuning=tuning
    )
    assert rep_none.outcome == "no_responsive_bid"
    assert rep_none.winner_bid_ids == []


def test_dynamic_incumbent_bias_and_fpif_ceiling() -> None:
    tuning = load_tuning()
    ctx = BidderContext(
        company_id="mcdonnell",
        reputation_service=85.0,
        track_record=0.80,
        district_weight=0.60,
        active_contracts_same_role=2,
        active_contracts_same_customer=3,
        idle_factory_fraction=0.45,
    )
    inc_bias = compute_dynamic_incumbent_bias(ctx, tuning)
    assert 0.40 <= inc_bias <= 1.00

    prog = load_program_by_id("usaf_ws201a_1950")
    bids, _ = generate_historical_program_bids(
        prog, rng=RandomSource(deterministic=True), tuning=tuning
    )
    contract = create_contract_from_award(
        program=prog,
        bid=bids[0],
        award_day=date_to_day("1951-09-11"),
        contract_kind="production_fpif",
        tuning=tuning,
    )
    lot0 = contract.lots[0]
    # Massive cost overrun should be capped at lot0.unit_ceiling_price_usd
    price_overrun = compute_fpif_unit_price(
        lot=lot0,
        unit_target_cost_usd=1000000.0,
        unit_actual_cost_usd=2500000.0,
    )
    assert price_overrun == pytest.approx(lot0.unit_ceiling_price_usd)
