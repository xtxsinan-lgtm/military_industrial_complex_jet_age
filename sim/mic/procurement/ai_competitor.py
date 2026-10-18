"""AI Competitor Proposal Generator for Historical and Dynamic Programs.

Implements section 5.12 of docs/spec/05_procurement.md.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .dates import date_to_day
from .models import (
    BidderContext,
    EquipmentProfile,
    Estimate,
    HistoricalEntrant,
    NoveltyProfile,
    ProgramSpec,
    ProposalBid,
)
from .rng import RandomSource
from .scoring import clamp, criterion_sign, effective_objective_and_span
from .tuning import load_tuning


def generate_historical_entrant_bid(
    program: ProgramSpec,
    entrant: HistoricalEntrant,
    ai_quality: float = 1.0,
    rng: Optional[RandomSource] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> Tuple[ProposalBid, BidderContext]:
    """Generate a ProposalBid and BidderContext from a HistoricalEntrant specification (§5.12.1)."""
    t = tuning if tuning is not None else load_tuning()
    rng_src = rng if rng is not None else RandomSource(deterministic=True)

    q_ai = clamp(float(ai_quality), float(t["AI_MIN_QUALITY"]), 1.30)
    skill_span = float(t["AI_SKILL_SPAN"])
    true_sd = float(t["AI_TRUE_SD"])
    est_err_sd = float(t["AI_PAPER_ERR_SD"])
    paper_sig_rel = float(t["AI_PAPER_SIGMA_REL"])
    flight_sig_rel = float(t["FLIGHT_SIGMA_REL"])
    promise_z = float(t["AI_PROMISE_Z_DEFAULT"])

    estimates: Dict[str, Estimate] = {}
    promised: Dict[str, float] = {}
    measured: Dict[str, Estimate] = {}

    for crit in program.criteria:
        key = crit.key
        anchor = float(entrant.anchor_performance.get(key, crit.value))
        if crit.unit == "bool":
            b_val = 1.0 if anchor >= 0.5 else 0.0
            estimates[key] = Estimate(value=b_val, sigma=0.0, source="tunnel", unit="bool")
            promised[key] = b_val
            if entrant.built_prototype:
                measured[key] = Estimate(
                    value=b_val, sigma=0.0, source="flight", unit="bool"
                )
            continue

        s_i = criterion_sign(crit.op)
        eps_true = rng_src.normal(0.0, true_sd)
        v_true = anchor * (1.0 + s_i * skill_span * (q_ai - 1.0) + eps_true)

        eps_est = rng_src.normal(0.0, est_err_sd)
        mu_est = v_true * (1.0 + eps_est)
        sig_est = paper_sig_rel * max(abs(mu_est), 1e-3)

        estimates[key] = Estimate(
            value=mu_est, sigma=sig_est, source="tunnel", unit=crit.unit
        )

        if key in entrant.promised_overrides:
            p_val = float(entrant.promised_overrides[key])
        else:
            raw_p = mu_est + s_i * promise_z * sig_est
            # AI promises at least the threshold if its estimate is within 12% of threshold
            if s_i * (raw_p - crit.value) < 0.0 and (
                abs(mu_est - crit.value) / max(abs(crit.value), 1.0) <= 0.12
            ):
                p_val = float(crit.value)
            else:
                p_val = raw_p
        promised[key] = p_val

        if entrant.built_prototype:
            sig_flt = flight_sig_rel * max(abs(v_true), 1e-3)
            measured[key] = Estimate(
                value=v_true, sigma=sig_flt, source="flight", unit=crit.unit
            )

    sub_day = date_to_day(program.proposal_due) - 5
    ff_due_day = date_to_day(program.first_flight_due)
    ioc_due_day = date_to_day(program.ioc_due)

    if entrant.first_flight_date:
        actual_ff_day = date_to_day(entrant.first_flight_date)
        promised_ff_day = min(actual_ff_day, ff_due_day)
    else:
        actual_ff_day = None
        promised_ff_day = ff_due_day - int(t["AI_FF_LEAD_DAYS"])

    bid = ProposalBid(
        bid_id=f"{program.id}__{entrant.company_id}",
        program_id=program.id,
        company_id=entrant.company_id,
        design_name=entrant.design_name,
        is_player=False,
        submitted_day=sub_day,
        estimates=estimates,
        promised=promised,
        unit_price_bid_usd=float(entrant.unit_price_bid_usd),
        unit_cost_estimate_usd=float(entrant.unit_price_bid_usd),
        dev_cost_bid_usd=float(entrant.dev_cost_bid_usd),
        dev_cost_estimate_usd=float(entrant.dev_cost_bid_usd),
        promised_first_flight_day=promised_ff_day,
        promised_ioc_day=ioc_due_day,
        novelty=entrant.novelty,
        equipment=entrant.equipment,
        political_capital_spent=0.0,
        cross_service_derivative=entrant.cross_service_derivative,
        is_originator=False,
        measured_performance=measured,
        actual_first_flight_day=actual_ff_day if entrant.built_prototype else None,
        unfixed_flaw_severity_sum=entrant.flyoff_flaws_unfixed_severity,
    )

    ctx = BidderContext(
        company_id=entrant.company_id,
        reputation_service=entrant.reputation_at_bid,
        track_record=entrant.track_record_at_bid,
        district_weight=entrant.district_weight,
        active_contracts_same_role=1
        if program.politics.incumbent_bias.get(entrant.company_id, 0.0) >= 0.35
        else 0,
        active_contracts_same_customer=1
        if program.politics.incumbent_bias.get(entrant.company_id, 0.0) >= 0.20
        else 0,
        idle_factory_fraction=0.30,
    )
    return bid, ctx


def generate_historical_program_bids(
    program: ProgramSpec,
    company_qualities: Optional[Dict[str, float]] = None,
    exclude_company_ids: Optional[List[str]] = None,
    rng: Optional[RandomSource] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> Tuple[List[ProposalBid], Dict[str, BidderContext]]:
    """Generate bids and bidder contexts for all active historical entrants of a program."""
    t = tuning if tuning is not None else load_tuning()
    qualities = company_qualities or {}
    excluded = set(exclude_company_ids or [])
    min_q = float(t["AI_MIN_QUALITY"])

    bids: List[ProposalBid] = []
    bidders: Dict[str, BidderContext] = {}

    for entrant in program.historical.competitors:
        if entrant.company_id in excluded:
            continue
        q = float(qualities.get(entrant.company_id, 1.0))
        if q < min_q:
            # Company has exited or is financially unable to bid
            continue
        bid, ctx = generate_historical_entrant_bid(
            program=program,
            entrant=entrant,
            ai_quality=q,
            rng=rng,
            tuning=t,
        )
        bids.append(bid)
        bidders[entrant.company_id] = ctx

    return bids, bidders


def generate_dynamic_ai_bids(
    program: ProgramSpec,
    ai_companies: List[Dict[str, Any]],
    rng: Optional[RandomSource] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> Tuple[List[ProposalBid], Dict[str, BidderContext]]:
    """Generate synthetic AI competitor bids for a procedural/dynamic RFP (§5.12.2)."""
    t = tuning if tuning is not None else load_tuning()
    rng_src = rng if rng is not None else RandomSource(deterministic=True)
    paper_sig_rel = float(t["AI_PAPER_SIGMA_REL"])
    flight_sig_rel = float(t["FLIGHT_SIGMA_REL"])
    dyn_amb = float(t["AI_DYN_AMB"])

    bids: List[ProposalBid] = []
    bidders: Dict[str, BidderContext] = {}

    sub_day = date_to_day(program.proposal_due) - 7
    ff_due_day = date_to_day(program.first_flight_due)
    ioc_due_day = date_to_day(program.ioc_due)

    for comp in sorted(ai_companies, key=lambda c: str(c["company_id"])):
        cid = str(comp["company_id"])
        skill = float(comp.get("skill", 1.0))
        rep = float(comp.get("reputation", 60.0))
        track = float(comp.get("track_record", 0.55))
        dist_w = float(comp.get("district_weight", 0.35))
        aggression = float(comp.get("aggression", 0.5))

        estimates: Dict[str, Estimate] = {}
        promised: Dict[str, float] = {}
        measured: Dict[str, Estimate] = {}

        for crit in program.criteria:
            if crit.unit == "bool":
                estimates[crit.key] = Estimate(
                    value=1.0, sigma=0.0, source="tunnel", unit="bool"
                )
                promised[crit.key] = 1.0
                measured[crit.key] = Estimate(
                    value=1.0, sigma=0.0, source="flight", unit="bool"
                )
                continue

            s_i = criterion_sign(crit.op)
            obj_val, span = effective_objective_and_span(crit, t)
            # Skill 1.0 targets ~65% of the way from threshold to objective
            progress = clamp(
                0.65 + (skill - 1.0) * 1.2 + rng_src.normal(0.0, dyn_amb),
                0.05,
                1.30,
            )
            v_true = float(crit.value) + s_i * progress * span
            sig_est = paper_sig_rel * max(abs(v_true), 1.0)
            p_val = v_true + s_i * aggression * 0.6 * sig_est
            if s_i * (p_val - crit.value) < 0.0:
                p_val = float(crit.value)

            estimates[crit.key] = Estimate(
                value=v_true, sigma=sig_est, source="tunnel", unit=crit.unit
            )
            promised[crit.key] = p_val
            measured[crit.key] = Estimate(
                value=v_true,
                sigma=flight_sig_rel * max(abs(v_true), 1.0),
                source="flight",
                unit=crit.unit,
            )

        price_ratio = clamp(0.92 - 0.10 * (skill - 1.0) + rng_src.normal(0.0, 0.04), 0.72, 1.15)
        unit_bid = price_ratio * float(program.budget.unit_price_ceiling_usd)
        dev_bid = price_ratio * float(program.budget.dev_usd)

        eq = EquipmentProfile(
            carrier_capable=program.equipment.carrier_capable,
            radar_installed=program.equipment.radar_required,
            crew=max(1, program.equipment.min_crew),
            engines=max(1, program.equipment.min_engines),
            internal_bay=program.equipment.internal_bay_required,
            guns_20mm=max(0, program.equipment.min_guns_20mm),
            missile_capability=list(program.equipment.missile_capability),
        )
        nov = NoveltyProfile(
            unproven_tech_count=1 if aggression >= 0.6 else 0,
            unflown_engine=False,
            unconventional_config=False,
        )

        bid = ProposalBid(
            bid_id=f"{program.id}__{cid}",
            program_id=program.id,
            company_id=cid,
            design_name=f"{cid.upper()} {program.role.title().replace('_', ' ')}",
            is_player=False,
            submitted_day=sub_day,
            estimates=estimates,
            promised=promised,
            unit_price_bid_usd=unit_bid,
            unit_cost_estimate_usd=unit_bid,
            dev_cost_bid_usd=dev_bid,
            dev_cost_estimate_usd=dev_bid,
            promised_first_flight_day=ff_due_day - 30,
            promised_ioc_day=ioc_due_day,
            novelty=nov,
            equipment=eq,
            political_capital_spent=0.0,
            cross_service_derivative=False,
            is_originator=False,
            measured_performance=measured,
            actual_first_flight_day=ff_due_day - 15,
            unfixed_flaw_severity_sum=0,
        )
        bids.append(bid)
        bidders[cid] = BidderContext(
            company_id=cid,
            reputation_service=rep,
            track_record=track,
            district_weight=dist_w,
        )

    return bids, bidders
