"""Unit and golden-vector verification tests for Module 07 (`sim.mic.ai`).

Covers:
1. AI company initialization (`load_ai_airframers`), Chief Designer succession, doctrine-weighted
   R&D project selection, and historical/insolvency market exit (`company_ai.py`).
2. Parametric aircraft design synthesis & coordinate local search (`design_generator.py`),
   including `TechContext` compliance (`validate_design`) and company signature differentiation.
3. RFP entry selection, bid formulation, and two-stage `flyoff` progression (`bidding_ai.py`, D6).
4. Pre-bid trade-press competitor rumors & intelligence inquiry levels (`rumors.py`, D10).
5. Named US engine vendor custom commission quotes & specialties (`engine_vendor_ai.py`, D9).
6. Exact reproduction of golden vectors (`ai_competitor_behaviors.json`, `ai_rumors_and_vendors.json`).
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from sim.mic.aero.geometry import validate_design
from sim.mic.ai import (
    CompetitorRumor,
    compare_vendor_quotes,
    generate_ai_design_for_rfp,
    generate_pre_bid_rumors,
    get_available_catalog_engines,
    get_inquiry_cost,
    load_ai_airframers,
    prepare_all_ai_entries_for_rfp,
    quote_custom_engine,
    score_rfp_entry_for_ai,
    score_tech_node_for_ai,
    select_ai_bidders_for_rfp,
    step_ai_company_month,
    step_all_ai_flyoff_finalists,
)
from sim.mic.perf.performance import evaluate
from sim.mic.procurement import evaluate_flyoff, evaluate_proposals, load_program_by_id
from sim.mic.tech.catalog import load_catalog
from sim.mic.tech.context import build_tech_context

_GOLDEN_DIR = Path(__file__).resolve().parents[1] / "golden"


def test_load_ai_airframers_and_doctrine_rnd():
    """Verify loading 12 non-player airframers (or 13 total) and doctrine-weighted R&D."""
    all_13 = load_ai_airframers(exclude_player_company_id=None, date_day=0)
    assert len(all_13) == 13
    non_player_12 = load_ai_airframers(exclude_player_company_id="north_american", date_day=0)
    assert len(non_player_12) == 12
    assert "north_american" not in non_player_12

    cat = load_catalog()
    convair = non_player_12["convair"]
    grumman = non_player_12["grumman"]

    # Grumman (USN primary) should value carrier tech higher than Convair (USAF primary)
    carrier_nodes = [n for n in cat.nodes.values() if "carrier" in n.id]
    if carrier_nodes:
        cn = carrier_nodes[0]
        s_grum = score_tech_node_for_ai(cn, grumman, date_day=365, catalog=cat)
        s_conv = score_tech_node_for_ai(cn, convair, date_day=365, catalog=cat)
        assert s_grum > s_conv

    # Step 1 month and verify R&D allocation and cash update
    rep = step_ai_company_month(convair, year=1945, month=1, days_in_month=30)
    assert rep["company_id"] == "convair"
    assert len(rep["research_allocations"]) >= 1
    assert rep["active_in_fighter_market"] is True


def test_historical_exit_and_alt_history_contract_survival():
    """Verify Curtiss-Wright exits in 1949 without contracts, but stays active if holding a major contract."""
    companies = load_ai_airframers(exclude_player_company_id="north_american", date_day=0)
    cw = companies["curtiss_wright"]
    cw.company_state.contracts.clear()
    cw.won_major_production_contract = False

    rep_exit = step_ai_company_month(cw, year=1949, month=6, days_in_month=30, run_full_econ=False)
    assert rep_exit["active_in_fighter_market"] is False
    assert rep_exit["exit_reason"] == "historical_pivot_to_bombers_or_missiles"

    # Now verify alt-history survival when won_major_production_contract is True
    cw_alive = load_ai_airframers(exclude_player_company_id="north_american", date_day=0)["curtiss_wright"]
    cw_alive.won_major_production_contract = True
    rep_alive = step_ai_company_month(cw_alive, year=1949, month=6, days_in_month=30, run_full_econ=False)
    assert rep_alive["active_in_fighter_market"] is True


def test_design_generator_validity_and_company_signatures():
    """Verify `generate_ai_design_for_rfp` produces valid designs and preserves company style signatures."""
    cat = load_catalog()
    # Unlock all techs up to 1954 for a 1952 supersonic interceptor test
    unlocked_1954 = {
        tid: 0.90 for tid, node in cat.nodes.items() if float(node.historical_year) <= 1954.0
    }
    rfp_supersonic = {
        "id": "test_ws201a_1952",
        "program_name": "1954 Ultimate Interceptor",
        "customer": "USAF",
        "role": "interceptor",
        "issue_date": "1952-06-01",
        "proposal_due": "1952-11-01",
        "first_flight_due": "1954-06-01",
        "ioc_due": "1956-06-01",
        "equipment": {"carrier_capable": False, "radar_required": True, "min_crew": 1, "min_engines": 1},
        "budget": {"dev_usd": 35000000.0, "unit_price_ceiling_usd": 1200000.0, "quantity_planned": 400},
        "criteria": [
            {"key": "max_mach_alt", "kind": "threshold", "op": ">=", "value": 1.25, "objective_value": 1.65, "weight": 0.45, "unit": "mach"},
            {"key": "combat_radius_m", "kind": "objective", "op": ">=", "value": 550000.0, "objective_value": 750000.0, "weight": 0.30, "unit": "m"},
            {"key": "climb_rate_sl_mps", "kind": "objective", "op": ">=", "value": 60.0, "objective_value": 110.0, "weight": 0.25, "unit": "mps"},
        ],
    }

    ctx_convair = build_tech_context("convair", 2700, unlocked_1954, catalog=cat)
    ctx_mcdonnell = build_tech_context("mcdonnell", 2700, unlocked_1954, catalog=cat)

    d_convair = generate_ai_design_for_rfp("convair", rfp_supersonic, unlocked_techs=ctx_convair)
    d_mcdonnell = generate_ai_design_for_rfp("mcdonnell", rfp_supersonic, unlocked_techs=ctx_mcdonnell)

    # Validate zero TECH_CAP or PACKAGING errors
    ok_c, errs_c, _ = validate_design(d_convair, tech_context=ctx_convair)
    ok_m, errs_m, _ = validate_design(d_mcdonnell, tech_context=ctx_mcdonnell)
    assert ok_c is True, f"Convair design validation failed: {errs_c}"
    assert ok_m is True, f"McDonnell design validation failed: {errs_m}"

    # Convair signature -> delta wing; McDonnell signature -> twin engine
    assert d_convair["wing"]["planform_type"] == "delta"
    assert d_mcdonnell["propulsion"]["count"] == 2

    rep_c = evaluate(d_convair, tech_context=ctx_convair)
    assert rep_c.is_valid is True
    assert rep_c.max_mach_alt >= 1.20


def test_bidding_ai_and_two_stage_flyoff_progression():
    """Verify AI RFP entry selection, proposal bidding, and two-stage `flyoff` execution (D6)."""
    companies = load_ai_airframers(exclude_player_company_id="north_american", date_day=0)
    rfp_usn = load_program_by_id("usn_os105_1946")

    # USN specialist Grumman should score higher for a USN carrier RFP than USAF specialist Republic
    s_grumman = score_rfp_entry_for_ai(companies["grumman"], rfp_usn)
    s_republic = score_rfp_entry_for_ai(companies["republic"], rfp_usn)
    assert s_grumman > s_republic

    # Full two-stage flyoff flow on 1946 Penetration Fighter
    rfp_1946 = load_program_by_id("usaf_pen_fighter_1946")
    entries = prepare_all_ai_entries_for_rfp(companies, rfp_1946, campaign_seed=19450101)
    assert 3 <= len(entries) <= 6

    bids = [e.bid for e in entries]
    ctx_map = {e.company_id: e.bidder_context for e in entries}
    prop_eval = evaluate_proposals(rfp_1946, bids, ctx_map)
    assert len(prop_eval.finalist_bid_ids) >= 2

    finalists = step_all_ai_flyoff_finalists(
        entries,
        rfp_1946,
        ai_companies=companies,
        finalist_company_ids=prop_eval.finalist_bid_ids,
        campaign_seed=19450101,
    )
    assert len(finalists) == len(prop_eval.finalist_bid_ids)
    for fin in finalists:
        assert fin.flyoff_completed is True
        assert fin.bid.actual_first_flight_day is not None
        assert len(fin.bid.measured_performance) >= len(rfp_1946.criteria)
        for est in fin.bid.measured_performance.values():
            assert est.source == "flight"

    flyoff_eval = evaluate_flyoff(rfp_1946, [f.bid for f in finalists], ctx_map)
    assert len(flyoff_eval.winner_company_ids) >= 1


def test_pre_bid_rumors_inquiry_levels():
    """Verify `generate_pre_bid_rumors` (D10) produces `CompetitorRumor` dicts with shrinking sigmas."""
    companies = load_ai_airframers(exclude_player_company_id="north_american", date_day=0)
    rfp_1946 = load_program_by_id("usaf_pen_fighter_1946")
    entries = prepare_all_ai_entries_for_rfp(companies, rfp_1946, campaign_seed=19450101)

    r_lvl0 = generate_pre_bid_rumors(rfp_1946, entries, inquiry_level=0)
    r_lvl1 = generate_pre_bid_rumors(rfp_1946, entries, inquiry_level=1)
    r_lvl2 = generate_pre_bid_rumors(rfp_1946, entries, inquiry_level=2)

    assert len(r_lvl2) == len(entries)
    assert get_inquiry_cost(0)["cost_usd"] == 0.0
    assert get_inquiry_cost(1)["cost_usd"] < get_inquiry_cost(2)["cost_usd"]

    by_cid_0 = {r["company_id"]: r for r in r_lvl0}
    by_cid_1 = {r["company_id"]: r for r in r_lvl1}
    by_cid_2 = {r["company_id"]: r for r in r_lvl2}

    common_cid = entries[0].company_id
    r0, r1, r2 = by_cid_0[common_cid], by_cid_1[common_cid], by_cid_2[common_cid]
    assert isinstance(r0, CompetitorRumor) and isinstance(r0, dict)

    for metric in ("max_mach_alt", "combat_radius_m", "unit_flyaway_price_usd"):
        assert r0[metric]["source"] == "rumor"
        assert r1[metric]["source"] == "rumor"
        assert r2[metric]["source"] == "rumor"
        assert r0[metric]["sigma"] > r1[metric]["sigma"] > r2[metric]["sigma"] > 0.0


def test_engine_vendor_quotes_and_specialties():
    """Verify the 5 named US engine vendors (D9) exhibit authentic specialty trade-offs."""
    spec = {
        "target_thrust_dry_N": 44000.0,
        "target_thrust_ab_N": 66000.0,
        "afterburner": True,
        "target_mach": 1.8,
        "customer": "USAF",
        "is_derivative": False,
    }
    quotes = {q.vendor_id: q for q in compare_vendor_quotes(spec, date="1952-06-01")}
    assert set(quotes.keys()) == {"pratt_whitney", "general_electric", "allison", "wright", "westinghouse"}

    pw = quotes["pratt_whitney"]
    ge = quotes["general_electric"]
    al = quotes["allison"]
    we = quotes["westinghouse"]
    wr = quotes["wright"]

    # P&W: lowest dry TSFC and highest MTBF
    assert pw.promised_tsfc_dry_sl < ge.promised_tsfc_dry_sl
    assert pw.promised_mtbf_h > ge.promised_mtbf_h > we.promised_mtbf_h

    # GE: highest supersonic afterburner thrust & throttle ratio
    assert ge.promised_ab_thrust_sl_N > pw.promised_ab_thrust_sl_N
    assert ge.engine_deck.throttle_ratio_tr > pw.engine_deck.throttle_ratio_tr

    # Allison: lowest unit price
    assert al.unit_price_usd < pw.unit_price_usd
    assert al.unit_price_usd < ge.unit_price_usd

    # Westinghouse: lightest dry weight & smallest diameter, but highest development risk
    assert we.promised_mass_kg < pw.promised_mass_kg
    assert we.promised_diameter_m < pw.promised_diameter_m
    assert we.development_risk_index > pw.development_risk_index

    # Curtiss-Wright derivative discount (J65 Sapphire style)
    wr_deriv = quote_custom_engine("wright", {**spec, "is_derivative": True}, date="1952-06-01")
    assert wr_deriv.total_dev_cost_usd < 0.60 * wr.total_dev_cost_usd
    assert wr_deriv.promised_delivery_days < wr.promised_delivery_days

    # Check callable EngineSpec contract on returned deck
    t_sl = ge.engine_deck.thrust_N(0.0, 0.0, 1.0, True)
    sfc_sl = ge.engine_deck.tsfc(0.0, 0.0, 1.0, False)
    assert t_sl == pytest.approx(ge.promised_ab_thrust_sl_N, rel=1e-4)
    assert sfc_sl == pytest.approx(ge.promised_tsfc_dry_sl, rel=1e-4)


def test_golden_vectors_reproduction():
    """Verify exact deterministic reproduction of Module 07 golden vector files within 1e-6."""
    g_beh = json.loads((_GOLDEN_DIR / "ai_competitor_behaviors.json").read_text(encoding="utf-8"))
    g_rum = json.loads((_GOLDEN_DIR / "ai_rumors_and_vendors.json").read_text(encoding="utf-8"))

    companies = load_ai_airframers(exclude_player_company_id="north_american", date_day=0)
    assert len(companies) == g_beh["initial_ai_company_count"]

    for cid in ("lockheed", "convair", "grumman", "curtiss_wright"):
        rep = step_ai_company_month(companies[cid], year=1945, month=1, days_in_month=30)
        exp = g_beh["month_1_step_reports"][cid]
        assert rep["active_designer_id"] == exp["active_designer_id"]
        assert [list(x) for x in rep["research_allocations"]] == exp["research_allocations"]
        assert rep["ending_cash_usd"] == pytest.approx(exp["ending_cash_usd"], rel=1e-6)

    rfp_1946 = load_program_by_id("usaf_pen_fighter_1946")
    entries = prepare_all_ai_entries_for_rfp(companies, rfp_1946, campaign_seed=19450101)
    for got, exp in zip([e.to_dict() for e in entries], g_beh["rfp_1946_entries"]):
        assert got["company_id"] == exp["company_id"]
        assert got["unit_price_bid_usd"] == pytest.approx(exp["unit_price_bid_usd"], rel=1e-6)
        assert got["true_max_mach_alt"] == pytest.approx(exp["true_max_mach_alt"], rel=1e-6)

    for lvl in ("0", "1", "2"):
        got_r = generate_pre_bid_rumors(rfp_1946, entries, inquiry_level=int(lvl))
        exp_r = g_rum["rumors_by_inquiry_level"][lvl]
        assert len(got_r) == len(exp_r)
        for gr, er in zip(got_r, exp_r):
            assert gr["company_id"] == er["company_id"]
            assert gr["max_mach_alt"]["value"] == pytest.approx(er["max_mach_alt"]["value"], rel=1e-6)
            assert gr["unit_flyaway_price_usd"]["sigma"] == pytest.approx(er["unit_flyaway_price_usd"]["sigma"], rel=1e-6)
