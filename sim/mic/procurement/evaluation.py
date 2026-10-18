"""Lifecycle evaluation, fly-off resolution, contract creation, promise audit, and annual lot review.

Implements sections 5.5 through 5.8 of docs/spec/05_procurement.md.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .dates import date_to_day, day_to_fiscal_year, day_to_iso
from .models import (
    AnnualReviewReport,
    BidderContext,
    BidScoreBreakdown,
    ContractState,
    Estimate,
    EvaluationReport,
    ProductionLot,
    ProgramSpec,
    PromiseAuditReport,
    ProposalBid,
)
from .rng import RandomSource
from .scoring import clamp, criterion_sign, score_bid
from .tuning import load_tuning


def _rank_breakdowns(breakdowns: List[BidScoreBreakdown]) -> List[BidScoreBreakdown]:
    """Sort breakdowns: responsive first, then descending total_score, perf_score, ascending bid_id."""
    return sorted(
        breakdowns,
        key=lambda b: (
            1 if b.responsive else 0,
            round(b.total_score, 9),
            round(b.perf_score, 9),
            # invert bid_id sort via manual tiebreak not needed if tuple uses string last
        ),
        reverse=True,
    )


def _sort_breakdowns_deterministic(
    breakdowns: List[BidScoreBreakdown],
) -> List[BidScoreBreakdown]:
    """Deterministic ranking with ascending bid_id tie-breaker."""
    return sorted(
        breakdowns,
        key=lambda b: (
            0 if b.responsive else 1,
            -round(b.total_score, 9),
            -round(b.perf_score, 9),
            b.bid_id,
        ),
    )


def generate_debrief_report(
    program: ProgramSpec,
    phase: str,
    outcome: str,
    rankings: List[BidScoreBreakdown],
    winner_bid_ids: List[str],
    waiver_granted: bool = False,
) -> str:
    """Generate human-readable Source Selection Board debrief text (§3.1 step 6)."""
    lines: List[str] = [
        f"=== SOURCE SELECTION DEBRIEF: {program.program_name} ({program.customer}) ===",
        f"Phase: {phase.upper()} | Outcome: {outcome.upper()}",
    ]
    if waiver_granted:
        lines.append(
            "NOTE: All finalists fell short of at least one threshold gate; board granted a threshold waiver to the highest-scoring entrant."
        )
    lines.append(
        "Rank | Company / Design | Resp | Perf | Cost | Sched | Risk | Pol | Pen | Total"
    )
    lines.append("-" * 86)
    for idx, b in enumerate(rankings, start=1):
        pen = b.promise_penalty + b.flaw_penalty
        tag = "*" if b.bid_id in winner_bid_ids else " "
        resp_str = "YES" if b.responsive else "NO "
        lines.append(
            f"{idx:2d}{tag} | {b.company_id}:{b.design_name[:22]:<22} | {resp_str} | "
            f"{b.perf_score:5.1f} | {b.cost_score:5.1f} | {b.sched_score:5.1f} | "
            f"{b.risk_score:5.1f} | {b.politics_bonus:+5.1f} | {pen:4.1f} | {b.total_score:6.2f}"
        )
        if not b.responsive and b.disqualify_reasons:
            lines.append(f"     -> Disqualified: {', '.join(b.disqualify_reasons)}")
    return "\n".join(lines)


def evaluate_proposals(
    program: ProgramSpec,
    bids: List[ProposalBid],
    bidders: Dict[str, BidderContext],
    rng: Optional[RandomSource] = None,
    use_static_incumbent: bool = True,
    include_politics: bool = True,
    tuning: Optional[Dict[str, Any]] = None,
) -> EvaluationReport:
    """Evaluate paper proposals on proposal_due day (§5.5)."""
    t = tuning if tuning is not None else load_tuning()
    rng_src = rng if rng is not None else RandomSource(deterministic=True)
    eval_day = date_to_day(program.proposal_due)
    noise_sd = float(t["EVAL_NOISE_SD"])
    min_score = float(t["MIN_AWARD_SCORE"])
    priv_margin = float(t["PRIVATE_ENTRY_MARGIN"])

    # Sort bids by bid_id ascending before consuming RNG draws
    ordered_bids = sorted(bids, key=lambda b: b.bid_id)
    breakdowns: List[BidScoreBreakdown] = []

    for bid in ordered_bids:
        ctx = bidders.get(bid.company_id, BidderContext(company_id=bid.company_id))
        eps = rng_src.normal(0.0, noise_sd)
        bd = score_bid(
            program=program,
            bid=bid,
            bidder=ctx,
            phase="proposal",
            eval_noise=eps,
            use_static_incumbent=use_static_incumbent,
            include_politics=include_politics,
            tuning=t,
        )
        breakdowns.append(bd)

    rankings = _sort_breakdowns_deterministic(breakdowns)
    responsive_qualified = [
        b for b in rankings if b.responsive and b.total_score >= min_score
    ]

    winner_bid_ids: List[str] = []
    winner_company_ids: List[str] = []
    finalist_bid_ids: List[str] = []
    private_eligible_ids: List[str] = []
    quantity_splits: Dict[str, int] = {}

    if not responsive_qualified:
        outcome = "no_responsive_bid"
    elif program.acquisition.style in ("paper_award", "sole_source"):
        top = responsive_qualified[0]
        outcome = "awarded"
        winner_bid_ids = [top.bid_id]
        winner_company_ids = [top.company_id]
        finalist_bid_ids = [top.bid_id]
        quantity_splits = {top.bid_id: int(program.budget.quantity_planned)}
    else:
        # "flyoff" style: downselect top K for CPFF prototype contracts
        k = max(1, int(program.acquisition.downselect_count))
        selected = responsive_qualified[:k]
        outcome = "downselected"
        finalist_bid_ids = [b.bid_id for b in selected]
        cutoff_score = selected[-1].total_score
        for b in responsive_qualified[k:]:
            if cutoff_score - b.total_score <= priv_margin:
                b.eligible_for_private_prototype = True
                private_eligible_ids.append(b.bid_id)

    debrief = generate_debrief_report(
        program=program,
        phase="proposal",
        outcome=outcome,
        rankings=rankings,
        winner_bid_ids=winner_bid_ids or finalist_bid_ids,
        waiver_granted=False,
    )

    return EvaluationReport(
        program_id=program.id,
        program_name=program.program_name,
        customer=program.customer,
        phase="proposal",
        evaluation_day=eval_day,
        outcome=outcome,
        winner_bid_ids=winner_bid_ids,
        winner_company_ids=winner_company_ids,
        finalist_bid_ids=finalist_bid_ids,
        private_prototype_eligible_bid_ids=private_eligible_ids,
        quantity_splits=quantity_splits,
        waiver_granted=False,
        rankings=rankings,
        debrief_text=debrief,
    )


def evaluate_flyoff(
    program: ProgramSpec,
    finalist_bids: List[ProposalBid],
    bidders: Dict[str, BidderContext],
    rng: Optional[RandomSource] = None,
    use_static_incumbent: bool = True,
    include_politics: bool = True,
    tuning: Optional[Dict[str, Any]] = None,
) -> EvaluationReport:
    """Evaluate prototypes in the fly-off phase (§5.6)."""
    t = tuning if tuning is not None else load_tuning()
    rng_src = rng if rng is not None else RandomSource(deterministic=True)
    eval_day = date_to_day(program.first_flight_due)
    noise_sd = float(t["EVAL_NOISE_SD"])
    min_score = float(t["MIN_AWARD_SCORE"])
    dual_margin = float(t["DUAL_MARGIN"])
    dual_split_win = float(t["DUAL_SPLIT_WINNER"])

    ordered_bids = sorted(finalist_bids, key=lambda b: b.bid_id)
    breakdowns: List[BidScoreBreakdown] = []

    for bid in ordered_bids:
        ctx = bidders.get(bid.company_id, BidderContext(company_id=bid.company_id))
        eps = rng_src.normal(0.0, noise_sd)
        bd = score_bid(
            program=program,
            bid=bid,
            bidder=ctx,
            phase="flyoff",
            eval_noise=eps,
            use_static_incumbent=use_static_incumbent,
            include_politics=include_politics,
            tuning=t,
        )
        breakdowns.append(bd)

    rankings = _sort_breakdowns_deterministic(breakdowns)
    responsive_qualified = [
        b for b in rankings if b.responsive and b.total_score >= min_score
    ]

    winner_bid_ids: List[str] = []
    winner_company_ids: List[str] = []
    quantity_splits: Dict[str, int] = {}
    waiver_granted = False

    # Check if historical cancellation shock kills production after naming technical winner
    # (e.g., August 1950 Penetration Fighter fly-off: XF-88 won fly-off, then program cancelled)
    cancel_shock = float(program.alt_history.historical_cancellation_shock)

    if responsive_qualified:
        top = responsive_qualified[0]
        winner_bid_ids = [top.bid_id]
        winner_company_ids = [top.company_id]
        if cancel_shock >= 0.80:
            outcome = "cancelled_after_flyoff"
            quantity_splits = {top.bid_id: 0}
        elif (
            program.acquisition.allow_dual_award
            and len(responsive_qualified) >= 2
            and (top.total_score - responsive_qualified[1].total_score) <= dual_margin
        ):
            runner_up = responsive_qualified[1]
            outcome = "dual_award"
            winner_bid_ids = [top.bid_id, runner_up.bid_id]
            winner_company_ids = [top.company_id, runner_up.company_id]
            q_total = int(program.budget.quantity_planned)
            q_win = int(round(q_total * dual_split_win))
            quantity_splits = {
                top.bid_id: q_win,
                runner_up.bid_id: max(1, q_total - q_win),
            }
        else:
            outcome = "awarded"
            quantity_splits = {top.bid_id: int(program.budget.quantity_planned)}
    else:
        # All finalists failed at least one fly-off gate -> Waiver roll (§5.6 Case B)
        # Rank all flown finalists by total_score regardless of threshold failure
        flown_candidates = sorted(
            [
                b
                for b in breakdowns
                if "FLYOFF_GATE:prototype_not_flown" not in b.disqualify_reasons
            ],
            key=lambda b: (-round(b.total_score, 9), b.bid_id),
        )
        if not flown_candidates:
            outcome = "cancelled_after_flyoff"
        elif cancel_shock >= 0.80:
            top = flown_candidates[0]
            winner_bid_ids = [top.bid_id]
            winner_company_ids = [top.company_id]
            outcome = "cancelled_after_flyoff"
            quantity_splits = {top.bid_id: 0}
        else:
            p_waiver = clamp(
                float(t["WAIVER_P_BASE"])
                + float(t["WAIVER_P_URGENCY"]) * float(program.acquisition.urgency)
                - cancel_shock,
                0.0,
                0.95,
            )
            u_draw = rng_src.uniform()
            if u_draw < p_waiver and flown_candidates[0].total_score >= min_score:
                top = flown_candidates[0]
                waiver_granted = True
                outcome = "waiver_award"
                winner_bid_ids = [top.bid_id]
                winner_company_ids = [top.company_id]
                quantity_splits = {top.bid_id: int(program.budget.quantity_planned)}
                rankings = flown_candidates + [
                    b for b in breakdowns if b not in flown_candidates
                ]
            else:
                outcome = "cancelled_after_flyoff"

    debrief = generate_debrief_report(
        program=program,
        phase="flyoff",
        outcome=outcome,
        rankings=rankings,
        winner_bid_ids=winner_bid_ids,
        waiver_granted=waiver_granted,
    )

    return EvaluationReport(
        program_id=program.id,
        program_name=program.program_name,
        customer=program.customer,
        phase="flyoff",
        evaluation_day=eval_day,
        outcome=outcome,
        winner_bid_ids=winner_bid_ids,
        winner_company_ids=winner_company_ids,
        finalist_bid_ids=[b.bid_id for b in finalist_bids],
        private_prototype_eligible_bid_ids=[],
        quantity_splits=quantity_splits,
        waiver_granted=waiver_granted,
        rankings=rankings,
        debrief_text=debrief,
    )


def create_contract_from_award(
    program: ProgramSpec,
    bid: ProposalBid,
    award_day: int,
    contract_kind: str = "production_fpif",
    quantity_override: Optional[int] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> ContractState:
    """Create a CPFF prototype or FPIF production ContractState (§5.8.1)."""
    t = tuning if tuning is not None else load_tuning()
    fee_frac = float(t["DEV_FEE_FRAC"])
    fpif_ceil = float(t["FPIF_CEILING"])
    gov_share = float(t["FPIF_GOV_SHARE"])

    dev_target = float(bid.dev_cost_bid_usd)
    dev_fee = fee_frac * dev_target

    lots: List[ProductionLot] = []
    if contract_kind == "production_fpif":
        total_qty = (
            int(quantity_override)
            if quantity_override is not None
            else int(program.budget.quantity_planned)
        )
        n_lots = max(1, int(program.acquisition.production_lots))
        base_lot_qty = total_qty // n_lots
        remainder = total_qty % n_lots
        start_fy = day_to_fiscal_year(award_day)

        for idx in range(n_lots):
            lot_qty = base_lot_qty + (1 if idx < remainder else 0)
            if lot_qty <= 0:
                continue
            lots.append(
                ProductionLot(
                    lot_number=idx + 1,
                    fiscal_year=start_fy + idx,
                    quantity_planned=lot_qty,
                    quantity_awarded=lot_qty if idx == 0 else 0,
                    unit_target_price_usd=float(bid.unit_price_bid_usd),
                    unit_ceiling_price_usd=fpif_ceil * float(bid.unit_price_bid_usd),
                    gov_share=gov_share,
                    liquidated_damage_frac=0.0,
                    status="active" if idx == 0 else "planned",
                )
            )

    return ContractState(
        contract_id=f"contract__{program.id}__{bid.company_id}__{contract_kind}",
        program_id=program.id,
        customer=program.customer,
        role=program.role,
        company_id=bid.company_id,
        design_name=bid.design_name,
        contract_kind=contract_kind,
        award_day=int(award_day),
        dev_target_cost_usd=dev_target,
        dev_fixed_fee_usd=dev_fee,
        dev_cost_incurred_usd=0.0,
        promised_performance=dict(bid.promised),
        promised_first_flight_day=int(bid.promised_first_flight_day),
        promised_ioc_day=int(bid.promised_ioc_day),
        lots=lots,
        status="active",
        cancellation_reason=None,
    )


def compute_fpif_unit_price(
    lot: ProductionLot,
    unit_target_cost_usd: float,
    unit_actual_cost_usd: float,
) -> float:
    """Compute final FPIF unit price paid by government given actual unit cost (§5.8.1)."""
    effective_target_price = lot.unit_target_price_usd * (
        1.0 - lot.liquidated_damage_frac
    )
    overrun = float(unit_actual_cost_usd) - float(unit_target_cost_usd)
    shared_price = effective_target_price + (1.0 - lot.gov_share) * overrun
    return min(lot.unit_ceiling_price_usd, max(0.0, shared_price))


def audit_milestone_promises(
    program: ProgramSpec,
    contract: ContractState,
    actual_performance: Dict[str, float],
    actual_milestone_day: int,
    current_track_record: float,
    milestone: str = "ioc",
    tuning: Optional[Dict[str, Any]] = None,
) -> PromiseAuditReport:
    """Audit delivered performance & schedule against contract promises at FF or IOC (§5.7)."""
    t = tuning if tuning is not None else load_tuning()
    prom_tol = float(t["PROMISE_TOL"])
    gate_w = float(t["GATE_RISK_WEIGHT"])
    show_cause_tol = float(t["SHOW_CAUSE_GATE_TOL"])

    w_sum = 0.0
    shortfall_acc = 0.0
    all_exceeded = True
    failed_thresholds: List[str] = []

    for crit in program.criteria:
        if crit.unit == "bool":
            continue
        s_i = criterion_sign(crit.op)
        p_i = float(contract.promised_performance.get(crit.key, crit.value))
        act_i = float(actual_performance.get(crit.key, p_i))

        raw_rel_shortfall = (s_i * (p_i - act_i)) / max(abs(p_i), 1.0)
        net_shortfall = max(0.0, raw_rel_shortfall - prom_tol)
        if raw_rel_shortfall > -prom_tol:
            all_exceeded = False

        w_tilde = max(float(crit.weight), gate_w)
        w_sum += w_tilde
        shortfall_acc += w_tilde * net_shortfall

        if crit.kind in ("threshold", "objective"):
            thresh_miss = (s_i * (crit.value - act_i)) / max(abs(crit.value), 1.0)
            if thresh_miss > show_cause_tol:
                failed_thresholds.append(crit.key)

    delta_short = shortfall_acc / w_sum if w_sum > 0.0 else 0.0
    f_ld = clamp(float(t["LD_RATE"]) * delta_short, 0.0, float(t["LD_CAP"]))

    # Apply liquidated damages to active/planned lots
    for lot in contract.lots:
        if lot.status in ("active", "planned"):
            lot.liquidated_damage_frac = max(lot.liquidated_damage_frac, f_ld)

    # Reputation delta (performance)
    if delta_short > 0.0:
        rep_perf = max(
            float(t["REP_SHORTFALL_FLOOR"]),
            -float(t["REP_PER_PCT"]) * (100.0 * delta_short),
        )
    elif all_exceeded:
        rep_perf = float(t["REP_BONUS_EXCEED"])
    else:
        rep_perf = 0.0

    # Reputation delta (schedule)
    promised_day = (
        contract.promised_first_flight_day
        if milestone == "first_flight"
        else contract.promised_ioc_day
    )
    months_late = (float(actual_milestone_day) - float(promised_day)) / float(
        t["DAYS_PER_MONTH"]
    )
    months_over_grace = max(0.0, months_late - float(t["REP_LATE_GRACE_MONTHS"]))
    rep_sched = max(
        float(t["REP_LATE_FLOOR"]),
        -float(t["REP_PER_LATE_MONTH"]) * months_over_grace,
    )
    rep_total = rep_perf + rep_sched

    # Track record EMA update
    r_deliv = clamp(1.0 - float(t["TRACK_K"]) * delta_short, 0.0, 1.0)
    alpha = float(t["TRACK_ALPHA"])
    new_track = clamp(
        (1.0 - alpha) * float(current_track_record) + alpha * r_deliv, 0.0, 1.0
    )

    show_cause = len(failed_thresholds) > 0
    if show_cause:
        contract.status = "show_cause"

    return PromiseAuditReport(
        contract_id=contract.contract_id,
        milestone=milestone,
        weighted_shortfall_frac=delta_short,
        liquidated_damage_frac=f_ld,
        reputation_delta_perf=rep_perf,
        reputation_delta_sched=rep_sched,
        reputation_delta_total=rep_total,
        old_track_record=float(current_track_record),
        new_track_record=new_track,
        show_cause_triggered=show_cause,
        failed_threshold_keys=failed_thresholds,
    )


def review_annual_lot(
    program: ProgramSpec,
    contract: ContractState,
    fiscal_year: int,
    cost_incurred_ratio: float,
    schedule_slip_years: float,
    weighted_shortfall_frac: float,
    perf_score: float,
    budget_index: float = 1.0,
    obsolescence_index: float = 0.0,
    district_weight: float = 0.35,
    political_capital_spent: float = 0.0,
    rng: Optional[RandomSource] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> AnnualReviewReport:
    """Execute annual July 1 fiscal lot continuation, cancellation, and quantity scaling (§5.8.2)."""
    t = tuning if tuning is not None else load_tuning()
    rng_src = rng if rng is not None else RandomSource(deterministic=True)

    r_overrun = max(
        0.0, float(cost_incurred_ratio) - 1.0 - float(t["CANCEL_OVERRUN_TOL"])
    )
    y_slip = max(0.0, float(schedule_slip_years))
    d_short = max(0.0, float(weighted_shortfall_frac))
    b_deficit = max(0.0, 1.0 - float(budget_index))
    obs = max(0.0, float(obsolescence_index))
    d_cong = float(program.politics.congressional_interest) * float(district_weight)
    l_norm = min(1.0, max(0.0, float(political_capital_spent)) / 20.0)

    p_cancel = clamp(
        float(t["CANCEL_BASE"])
        + float(t["CANCEL_OVERRUN_K"]) * r_overrun
        + float(t["CANCEL_SLIP_K"]) * y_slip
        + float(t["CANCEL_SHORTFALL_K"]) * d_short
        + float(t["CANCEL_BUDGET_K"]) * b_deficit
        + float(t["CANCEL_OBSOLETE_K"]) * obs
        - float(t["CANCEL_CONGRESS_K"]) * d_cong
        - float(t["CANCEL_LOBBY_K"]) * l_norm,
        0.0,
        float(t["CANCEL_MAX"]),
    )

    u_draw = rng_src.uniform()
    next_lot: Optional[ProductionLot] = None
    for lot in contract.lots:
        if lot.status == "planned":
            next_lot = lot
            break

    if u_draw < p_cancel:
        contract.status = "cancelled"
        if obs >= 0.8:
            reason = "doctrinal_obsolescence"
        elif r_overrun >= 0.3:
            reason = "severe_cost_overrun"
        elif d_short >= 0.1:
            reason = "performance_shortfall"
        else:
            reason = "budget_and_program_review"
        contract.cancellation_reason = reason
        for lot in contract.lots:
            if lot.status == "planned":
                lot.status = "cancelled"
        return AnnualReviewReport(
            contract_id=contract.contract_id,
            fiscal_year=fiscal_year,
            p_cancel=p_cancel,
            cancelled=True,
            cancellation_reason=reason,
            lot_number_reviewed=next_lot.lot_number if next_lot else None,
            qty_multiplier=0.0,
            quantity_awarded=0,
        )

    m_qty = clamp(
        1.0
        + float(t["QTY_PERF_K"])
        * ((float(perf_score) / 100.0) - float(t["QTY_PERF_REF"]))
        - float(t["QTY_OVERRUN_K"]) * r_overrun
        + float(t["QTY_BUDGET_K"]) * (float(budget_index) - 1.0),
        float(t["QTY_MULT_MIN"]),
        float(t["QTY_MULT_MAX"]),
    )

    if next_lot is None:
        contract.status = "completed"
        return AnnualReviewReport(
            contract_id=contract.contract_id,
            fiscal_year=fiscal_year,
            p_cancel=p_cancel,
            cancelled=False,
            cancellation_reason=None,
            lot_number_reviewed=None,
            qty_multiplier=m_qty,
            quantity_awarded=0,
        )

    qty_awarded = max(1, int(round(next_lot.quantity_planned * m_qty)))
    next_lot.quantity_awarded = qty_awarded
    next_lot.status = "active"

    return AnnualReviewReport(
        contract_id=contract.contract_id,
        fiscal_year=fiscal_year,
        p_cancel=p_cancel,
        cancelled=False,
        cancellation_reason=None,
        lot_number_reviewed=next_lot.lot_number,
        qty_multiplier=m_qty,
        quantity_awarded=qty_awarded,
    )
