"""Golden test vector generator for Module 05 (Procurement).

Generates deterministic JSON test vectors in sim/golden/:
1. sim/golden/procurement_scoring_vectors.json
2. sim/golden/procurement_lifecycle_vectors.json
3. sim/golden/procurement_dynamic_vectors.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ai_competitor import generate_historical_program_bids
from .catalog import (
    load_budget_index_table,
    load_program_by_id,
    load_threat_milestones,
)
from .dates import date_to_day
from .dynamic_rfp import (
    adapt_program_to_world,
    create_capability_gap,
    evaluate_monthly_rfp_trigger,
    generate_procedural_requirement,
    redirect_follow_on_program,
    should_suppress_stopgap,
)
from .evaluation import (
    audit_milestone_promises,
    compute_fpif_unit_price,
    create_contract_from_award,
    evaluate_flyoff,
    evaluate_proposals,
    review_annual_lot,
)
from .models import (
    BidderContext,
    EquipmentProfile,
    Estimate,
    NoveltyProfile,
    ProposalBid,
)
from .rng import RandomSource
from .scoring import preview_bid_evaluation, score_bid
from .tuning import load_tuning
from .unsolicited import evaluate_unsolicited_proposal

DEFAULT_GOLDEN_DIR = Path(__file__).resolve().parents[2] / "golden"


def build_scoring_golden_vectors() -> Dict[str, Any]:
    """Build golden vectors for §5.1-5.4 scoring formulas."""
    tuning = load_tuning()
    prog = load_program_by_id("usaf_ws201a_1950")
    sub_day = date_to_day("1951-01-15")
    ff_day = date_to_day("1953-10-15")
    ioc_day = date_to_day("1955-11-01")

    base_estimates = {
        "max_mach_alt": Estimate(value=1.28, sigma=0.08, source="sim", unit="mach"),
        "service_ceiling_m": Estimate(
            value=16154.0, sigma=600.0, source="sim", unit="m"
        ),
        "climb_rate_sl_mps": Estimate(
            value=78.0, sigma=5.0, source="sim", unit="mps"
        ),
        "combat_radius_m": Estimate(
            value=648200.0, sigma=35000.0, source="sim", unit="m"
        ),
    }

    # Vector 1a: Honest high-credibility incumbent
    honest_inc_ctx = BidderContext(
        company_id="convair",
        reputation_service=80.0,
        track_record=0.80,
        district_weight=0.55,
    )
    honest_bid = ProposalBid(
        bid_id="vec1_honest_incumbent",
        program_id=prog.id,
        company_id="convair",
        design_name="Model 8-80 Honest",
        is_player=True,
        submitted_day=sub_day,
        estimates=base_estimates,
        promised={k: v.value for k, v in base_estimates.items()},
        unit_price_bid_usd=1180000.0,
        unit_cost_estimate_usd=1180000.0,
        dev_cost_bid_usd=38000000.0,
        dev_cost_estimate_usd=38000000.0,
        promised_first_flight_day=ff_day,
        promised_ioc_day=ioc_day,
        novelty=NoveltyProfile(
            unproven_tech_count=1, unflown_engine=False, unconventional_config=False
        ),
        equipment=EquipmentProfile(
            carrier_capable=False,
            radar_installed=True,
            crew=1,
            engines=1,
            internal_bay=True,
            guns_20mm=0,
            missile_capability=["sarh"],
        ),
        political_capital_spent=10.0,
    )
    bd_honest = score_bid(prog, honest_bid, honest_inc_ctx, phase="proposal", tuning=tuning)

    # Vector 1b: Overclaiming low-credibility newcomer with same true estimates
    newcomer_ctx = BidderContext(
        company_id="newcomer",
        reputation_service=35.0,
        track_record=0.40,
        district_weight=0.35,
    )
    overclaim_bid = ProposalBid(
        bid_id="vec1_overclaim_newcomer",
        program_id=prog.id,
        company_id="newcomer",
        design_name="Newcomer Overclaimed",
        is_player=True,
        submitted_day=sub_day,
        estimates=base_estimates,
        promised={
            "max_mach_alt": 1.48,
            "service_ceiling_m": 17200.0,
            "climb_rate_sl_mps": 88.0,
            "combat_radius_m": 740000.0,
        },
        unit_price_bid_usd=1180000.0,
        unit_cost_estimate_usd=1180000.0,
        dev_cost_bid_usd=38000000.0,
        dev_cost_estimate_usd=38000000.0,
        promised_first_flight_day=ff_day,
        promised_ioc_day=ioc_day,
        novelty=NoveltyProfile(
            unproven_tech_count=3, unflown_engine=True, unconventional_config=True
        ),
        equipment=honest_bid.equipment,
        political_capital_spent=0.0,
    )
    bd_overclaim = score_bid(
        prog, overclaim_bid, newcomer_ctx, phase="proposal", tuning=tuning
    )
    preview_overclaim = preview_bid_evaluation(
        prog, overclaim_bid, newcomer_ctx, tuning=tuning
    )

    # Vector 2: Lowball price & unrealistic 180-day schedule clamp
    lowball_bid = ProposalBid(
        bid_id="vec2_lowball_and_rush",
        program_id=prog.id,
        company_id="convair",
        design_name="Lowball Rush Bid",
        is_player=True,
        submitted_day=sub_day,
        estimates=base_estimates,
        promised={k: v.value for k, v in base_estimates.items()},
        unit_price_bid_usd=500000.0,  # far below $1.18M cost estimate
        unit_cost_estimate_usd=1180000.0,
        dev_cost_bid_usd=15000000.0,
        dev_cost_estimate_usd=38000000.0,
        promised_first_flight_day=sub_day + 180,  # unrealistically early
        promised_ioc_day=ioc_day,
        novelty=honest_bid.novelty,
        equipment=honest_bid.equipment,
    )
    bd_lowball = score_bid(
        prog, lowball_bid, honest_inc_ctx, phase="proposal", tuning=tuning
    )

    # Vector 3: Non-responsive bid (misses Mach threshold, missing internal bay, over price ceiling)
    nonresp_bid = ProposalBid(
        bid_id="vec3_non_responsive",
        program_id=prog.id,
        company_id="newcomer",
        design_name="Non-Responsive Design",
        is_player=True,
        submitted_day=sub_day,
        estimates=base_estimates,
        promised={
            "max_mach_alt": 1.05,  # below 1.20 threshold
            "service_ceiling_m": 16154.0,
            "climb_rate_sl_mps": 78.0,
            "combat_radius_m": 648200.0,
        },
        unit_price_bid_usd=2100000.0,  # exceeds 1.30 * $1.40M ceiling
        unit_cost_estimate_usd=2100000.0,
        dev_cost_bid_usd=38000000.0,
        dev_cost_estimate_usd=38000000.0,
        promised_first_flight_day=ff_day,
        promised_ioc_day=ioc_day,
        novelty=honest_bid.novelty,
        equipment=EquipmentProfile(
            carrier_capable=False,
            radar_installed=True,
            crew=1,
            engines=1,
            internal_bay=False,  # missing required internal bay
            guns_20mm=4,
            missile_capability=[],  # missing required SARH capability
        ),
    )
    bd_nonresp = score_bid(
        prog, nonresp_bid, newcomer_ctx, phase="proposal", tuning=tuning
    )

    return {
        "schema_version": 1,
        "module": "05_procurement",
        "tolerance_rel": 1e-6,
        "vectors": {
            "honest_incumbent": bd_honest.to_dict(),
            "overclaim_newcomer": bd_overclaim.to_dict(),
            "overclaim_confidence": preview_overclaim["criterion_confidence"],
            "lowball_and_rush": bd_lowball.to_dict(),
            "non_responsive": bd_nonresp.to_dict(),
        },
    }


def build_lifecycle_golden_vectors() -> Dict[str, Any]:
    """Build golden vectors for §5.5-5.8 downselect, fly-off, promise audit, and annual lot review."""
    tuning = load_tuning()
    rng_det = RandomSource(deterministic=True)

    # Vector 1: USN 1955-1958 FAD Fly-Off (McDonnell XF4H-1 vs Vought XF8U-3)
    fad_prog = load_program_by_id("usn_fad_1955")
    fad_bids, fad_bidders = generate_historical_program_bids(
        fad_prog, rng=rng_det, tuning=tuning
    )
    fad_prop_rep = evaluate_proposals(
        fad_prog, fad_bids, fad_bidders, rng=rng_det, tuning=tuning
    )
    finalist_ids = set(fad_prop_rep.finalist_bid_ids)
    fad_finalists = [
        b for b in fad_bids if b.bid_id in finalist_ids and b.actual_first_flight_day is not None
    ]
    fad_flyoff_rep = evaluate_flyoff(
        fad_prog, fad_finalists, fad_bidders, rng=rng_det, tuning=tuning
    )

    # Vector 2: YF-102 pre-area-rule promise audit (promised M1.38, delivered M0.98 -> show_cause + LD)
    ws201_prog = load_program_by_id("usaf_ws201a_1950")
    ws201_bids, _ = generate_historical_program_bids(
        ws201_prog, rng=rng_det, tuning=tuning
    )
    convair_bid = [b for b in ws201_bids if b.company_id == "convair"][0]
    contract = create_contract_from_award(
        program=ws201_prog,
        bid=convair_bid,
        award_day=date_to_day("1951-09-11"),
        contract_kind="production_fpif",
        tuning=tuning,
    )
    audit_report = audit_milestone_promises(
        program=ws201_prog,
        contract=contract,
        actual_performance={
            "max_mach_alt": 0.98,  # transonic drag crisis!
            "service_ceiling_m": 14800.0,
            "climb_rate_sl_mps": 62.0,
            "combat_radius_m": 580000.0,
        },
        actual_milestone_day=date_to_day("1953-12-20"),
        current_track_record=0.70,
        milestone="first_flight",
        tuning=tuning,
    )
    fpif_price_after_ld = compute_fpif_unit_price(
        lot=contract.lots[0],
        unit_target_cost_usd=1050000.0,
        unit_actual_cost_usd=1200000.0,
    )

    # Vector 3: Annual July 1 lot review on F-108 Rapier after Sputnik ICBM obsolescence shock
    f108_prog = load_program_by_id("usaf_ws202a_1955")
    f108_bids, _ = generate_historical_program_bids(
        f108_prog, rng=rng_det, tuning=tuning
    )
    naa_bid = [b for b in f108_bids if b.company_id == "north_american"][0]
    f108_contract = create_contract_from_award(
        program=f108_prog,
        bid=naa_bid,
        award_day=date_to_day("1957-06-06"),
        contract_kind="production_fpif",
        tuning=tuning,
    )
    rng_cancel = RandomSource([0.25])  # uniform draw 0.25 < p_cancel
    f108_review = review_annual_lot(
        program=f108_prog,
        contract=f108_contract,
        fiscal_year=1960,
        cost_incurred_ratio=1.35,
        schedule_slip_years=0.8,
        weighted_shortfall_frac=0.0,
        perf_score=88.0,
        budget_index=0.82,
        obsolescence_index=1.35,
        district_weight=0.55,
        political_capital_spent=0.0,
        rng=rng_cancel,
        tuning=tuning,
    )

    return {
        "schema_version": 1,
        "module": "05_procurement",
        "tolerance_rel": 1e-6,
        "vectors": {
            "fad_proposal_report": fad_prop_rep.to_dict(),
            "fad_flyoff_report": fad_flyoff_rep.to_dict(),
            "yf102_promise_audit": audit_report.to_dict(),
            "yf102_fpif_unit_price_after_ld": fpif_price_after_ld,
            "f108_annual_review": f108_review.to_dict(),
        },
    }


def build_dynamic_golden_vectors() -> Dict[str, Any]:
    """Build golden vectors for §5.9-5.11 alt-history adaptation, procedural RFPs, and unsolicited pitches."""
    tuning = load_tuning()
    threats = load_threat_milestones()
    budgets = load_budget_index_table()

    # Vector 1: Alt-history adaptation when player has flown Mach 1.60 before OS-130 (1952)
    os130 = load_program_by_id("usn_os130_1952")
    adapted_os130 = adapt_program_to_world(
        os130,
        world_best_by_key={"max_mach_alt": 1.60, "climb_rate_sl_mps": 135.0},
        tuning=tuning,
    )

    # Stopgap suppression check on usn_f11f_1953
    f11f = load_program_by_id("usn_f11f_1953")
    suppressed = should_suppress_stopgap(
        program=f11f,
        recent_role_awards=[
            {
                "customer": "USN",
                "role": "carrier_day_fighter",
                "award_day": date_to_day("1952-06-01"),
                "delivered_performance": {
                    "max_mach_alt": 1.35,
                    "climb_rate_sl_mps": 115.0,
                    "stall_speed_mps": 48.0,
                    "combat_radius_m": 650000.0,
                },
            }
        ],
        current_day=date_to_day("1953-03-01"),
        tuning=tuning,
    )

    # Follow-on redirection on GOR 101 if Lockheed won the 1946 Penetration Fighter
    gor101 = load_program_by_id("usaf_gor101_1951")
    redirected_gor101 = redirect_follow_on_program(
        gor101,
        prior_program_winners={"usaf_pen_fighter_1946": "lockheed"},
    )

    # Vector 2: Monthly procedural RFP trigger after MiG-15 shock in Korea (Dec 1950)
    check_day = date_to_day("1950-12-01")
    should_issue, d_total, d_parts = evaluate_monthly_rfp_trigger(
        customer="USAF",
        role="day_fighter",
        current_day=check_day,
        fleet_service_entry_day=date_to_day("1946-01-01"),
        fleet_best_mach=0.84,
        active_threats=threats,
        has_unmet_gap=True,
        last_rfp_day_in_role=date_to_day("1948-01-01"),
        open_programs_for_customer=1,
        scheduled_historical_days_in_role=[],
        budget_index=budgets[1951],
        tuning=tuning,
    )
    proc_req = generate_procedural_requirement(
        customer="USAF",
        role="day_fighter",
        issue_day=check_day,
        demand_score=d_total,
        budget_index=budgets[1951],
        sequence_num=1,
        tuning=tuning,
    )

    # Vector 3: Unsolicited proposal evaluation (CL-246 style high-performance pitch)
    pitch_day = date_to_day("1952-11-01")
    virt_req = generate_procedural_requirement(
        customer="USAF",
        role="day_fighter",
        issue_day=pitch_day,
        demand_score=0.75,
        budget_index=1.40,
        sequence_num=99,
        tuning=tuning,
    )
    pitch_ests = {
        c.key: Estimate(
            value=(c.objective_value or c.value) * (1.08 if c.op == ">=" else 0.92),
            sigma=0.03 * abs(c.value),
            source="tunnel",
            unit=c.unit,
        )
        for c in virt_req.criteria
    }
    pitch_bid = ProposalBid(
        bid_id="unsol_cl246_pitch",
        program_id=virt_req.id,
        company_id="lockheed",
        design_name="Model CL-246",
        is_player=True,
        submitted_day=pitch_day,
        estimates=pitch_ests,
        promised={k: v.value for k, v in pitch_ests.items()},
        unit_price_bid_usd=0.82 * virt_req.budget.unit_price_ceiling_usd,
        unit_cost_estimate_usd=0.82 * virt_req.budget.unit_price_ceiling_usd,
        dev_cost_bid_usd=0.85 * virt_req.budget.dev_usd,
        dev_cost_estimate_usd=0.85 * virt_req.budget.dev_usd,
        promised_first_flight_day=pitch_day + 500,
        promised_ioc_day=pitch_day + 1200,
        novelty=NoveltyProfile(
            unproven_tech_count=1, unflown_engine=False, unconventional_config=False
        ),
        equipment=EquipmentProfile(
            carrier_capable=False,
            radar_installed=True,
            crew=1,
            engines=1,
            internal_bay=False,
            guns_20mm=2,
            missile_capability=["ir"],
        ),
    )
    pitch_ctx = BidderContext(
        company_id="lockheed",
        reputation_service=82.0,
        track_record=0.78,
        district_weight=0.55,
    )
    rng_pitch = RandomSource([0.20, 0.80])  # accept=True, sole_source=False -> open GOR
    pitch_res = evaluate_unsolicited_proposal(
        bid=pitch_bid,
        bidder=pitch_ctx,
        customer="USAF",
        role="day_fighter",
        pitch_day=pitch_day,
        role_demand_score=0.75,
        budget_index=1.40,
        has_open_program_in_role=False,
        prototype_already_flown=True,
        rng=rng_pitch,
        tuning=tuning,
    )

    gap_rec = create_capability_gap(os130, cancelled_day=date_to_day("1953-06-01"), tuning=tuning)

    return {
        "schema_version": 1,
        "module": "05_procurement",
        "tolerance_rel": 1e-6,
        "vectors": {
            "adapted_os130_criteria": [c.to_dict() for c in adapted_os130.criteria],
            "f11f_stopgap_suppressed": suppressed,
            "redirected_gor101_incumbent_bias": redirected_gor101.politics.incumbent_bias,
            "monthly_trigger": {
                "should_issue": should_issue,
                "d_total": d_total,
                "d_parts": d_parts,
            },
            "procedural_requirement": proc_req.to_dict(),
            "unsolicited_pitch_result": pitch_res.to_dict(),
            "capability_gap_record": gap_rec.to_dict(),
        },
    }


def write_all_golden_vectors(output_dir: Optional[Path] = None) -> List[Path]:
    """Write all 3 procurement golden vector JSON files to sim/golden/."""
    target = output_dir if output_dir is not None else DEFAULT_GOLDEN_DIR
    target.mkdir(parents=True, exist_ok=True)

    files = {
        "procurement_scoring_vectors.json": build_scoring_golden_vectors(),
        "procurement_lifecycle_vectors.json": build_lifecycle_golden_vectors(),
        "procurement_dynamic_vectors.json": build_dynamic_golden_vectors(),
    }
    written: List[Path] = []
    for fname, payload in files.items():
        p = target / fname
        with open(p, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        written.append(p)
    return written


if __name__ == "__main__":
    paths = write_all_golden_vectors()
    print(f"Wrote {len(paths)} golden vector files to {DEFAULT_GOLDEN_DIR}")
