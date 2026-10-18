"""Proposal and fly-off scoring algorithms for Module 05 (Procurement).

Implements sections 5.1 through 5.4 of docs/spec/05_procurement.md.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from .dates import date_to_day
from .models import (
    BidderContext,
    BidScoreBreakdown,
    CriterionEvalDetail,
    CriterionSpec,
    EquipmentProfile,
    EquipmentRequirement,
    Estimate,
    NoveltyProfile,
    ProgramSpec,
    ProposalBid,
)
from .tuning import load_tuning


def clamp(val: float, lo: float, hi: float) -> float:
    """Clamp val to [lo, hi]."""
    return float(min(max(val, lo), hi))


def criterion_sign(op: str) -> float:
    """Return +1.0 for '>=' (more is better), -1.0 for '<=' (less is better)."""
    if op == ">=":
        return 1.0
    if op == "<=":
        return -1.0
    raise ValueError(f"Unsupported criterion operator: {op!r}")


def effective_objective_and_span(
    crit: CriterionSpec, tuning: Optional[Dict[str, Any]] = None
) -> Tuple[float, float]:
    """Return (O_i, Delta_i) per section 5.1 of 05_procurement.md."""
    t = tuning if tuning is not None else load_tuning()
    s_i = criterion_sign(crit.op)
    t_val = float(crit.value)
    default_span_frac = float(t["DEFAULT_SPAN_FRAC"])
    if crit.objective_value is None or abs(float(crit.objective_value) - t_val) < 1e-12:
        obj = t_val * (1.0 + s_i * default_span_frac)
    else:
        obj = float(crit.objective_value)
    delta = max(abs(obj - t_val), 1e-6 * max(abs(t_val), 1.0))
    return obj, delta


def compute_credibility(
    bidder: BidderContext, tuning: Optional[Dict[str, Any]] = None
) -> float:
    """Compute bidder credibility C in [CRED_MIN, CRED_MAX] (§5.2.1)."""
    t = tuning if tuning is not None else load_tuning()
    rep_norm = clamp(bidder.reputation_service, 0.0, 100.0) / 100.0
    track_norm = clamp(bidder.track_record, 0.0, 1.0)
    c_raw = (
        float(t["CRED_BASE"])
        + float(t["CRED_W_REP"]) * rep_norm
        + float(t["CRED_W_TRACK"]) * track_norm
    )
    return clamp(c_raw, float(t["CRED_MIN"]), float(t["CRED_MAX"]))


def compute_novelty_index(
    novelty: NoveltyProfile,
    phase: str = "proposal",
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute technological novelty index N >= 0 (§5.2.2)."""
    t = tuning if tuning is not None else load_tuning()
    n_raw = (
        float(t["NOV_PER_TECH"]) * max(0, int(novelty.unproven_tech_count))
        + float(t["NOV_ENGINE_UNFLOWN"]) * (1.0 if novelty.unflown_engine else 0.0)
        + float(t["NOV_UNCONVENTIONAL"])
        * (1.0 if novelty.unconventional_config else 0.0)
    )
    if phase == "flyoff":
        return float(t["FLYOFF_NOV_FACTOR"]) * n_raw
    return n_raw


def compute_credible_value(
    crit: CriterionSpec,
    mu: float,
    sigma: float,
    promised: float,
    credibility: float,
    novelty_index: float,
    phase: str = "proposal",
    tuning: Optional[Dict[str, Any]] = None,
) -> Tuple[float, float, float]:
    """Compute (E_adj, overclaim_q, credible_value) per §5.2.3."""
    t = tuning if tuning is not None else load_tuning()
    if crit.unit == "bool":
        val = 1.0 if mu >= 0.5 else 0.0
        return val, 0.0, val

    s_i = criterion_sign(crit.op)
    k_skep = (
        float(t["SKEPTIC_K"])
        * (1.0 - credibility)
        * (float(t["SKEPTIC_NOV_BASE"]) + novelty_index)
    )
    e_adj = mu - s_i * k_skep * max(0.0, sigma)

    sigma_eff = max(float(sigma), 0.01 * max(abs(mu), 1.0))
    overclaim_q = max(0.0, (s_i * (promised - mu)) / sigma_eff)

    if phase == "flyoff":
        # In fly-off, promises do not inflate performance credit; measured value is used.
        return e_adj, overclaim_q, e_adj

    # Paper proposal phase
    if s_i * (promised - e_adj) <= 0.0:
        v_hat = promised
    else:
        oc_min = float(t["OC_MIN"])
        oc_max = float(t["OC_MAX"])
        lambda_oc = oc_min + (oc_max - oc_min) * credibility
        v_hat = e_adj + lambda_oc * (promised - e_adj)
    return e_adj, overclaim_q, v_hat


def compute_criterion_utility(
    crit: CriterionSpec,
    credible_val: float,
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute piecewise linear criterion utility u_i in [U_MIN, U_MAX] (§5.3.2)."""
    t = tuning if tuning is not None else load_tuning()
    if crit.unit == "bool":
        return 1.0 if credible_val >= 0.5 else float(t["U_MIN"])

    s_i = criterion_sign(crit.op)
    _, delta = effective_objective_and_span(crit, t)
    m_i = (s_i * (credible_val - crit.value)) / delta

    u_at_thresh = float(t["U_AT_THRESHOLD"])
    u_over_slope = float(t["U_OVER_SLOPE"])
    u_max = float(t["U_MAX"])
    u_below_slope = float(t["U_BELOW_SLOPE"])
    u_min = float(t["U_MIN"])

    if m_i >= 1.0:
        return min(u_max, 1.0 + u_over_slope * (m_i - 1.0))
    if m_i >= 0.0:
        return u_at_thresh + (1.0 - u_at_thresh) * m_i
    return max(u_min, u_at_thresh + u_below_slope * m_i)


def check_equipment_gates(
    req_eq: EquipmentRequirement, bid_eq: EquipmentProfile
) -> List[str]:
    """Check mandatory equipment/configuration gates (§5.3.1)."""
    reasons: List[str] = []
    if req_eq.carrier_capable and not bid_eq.carrier_capable:
        reasons.append("EQUIP_GATE:carrier_capable")
    if req_eq.radar_required and not bid_eq.radar_installed:
        reasons.append("EQUIP_GATE:radar_required")
    if bid_eq.crew < req_eq.min_crew:
        reasons.append(f"EQUIP_GATE:min_crew({bid_eq.crew}<{req_eq.min_crew})")
    if bid_eq.engines < req_eq.min_engines:
        reasons.append(f"EQUIP_GATE:min_engines({bid_eq.engines}<{req_eq.min_engines})")
    if req_eq.internal_bay_required and not bid_eq.internal_bay:
        reasons.append("EQUIP_GATE:internal_bay_required")
    if bid_eq.guns_20mm < req_eq.min_guns_20mm:
        reasons.append(
            f"EQUIP_GATE:min_guns_20mm({bid_eq.guns_20mm}<{req_eq.min_guns_20mm})"
        )
    bid_missiles = set(bid_eq.missile_capability)
    for m_req in req_eq.missile_capability:
        if m_req not in bid_missiles:
            reasons.append(f"EQUIP_GATE:missile_capability({m_req})")
    return reasons


def evaluate_criteria_and_performance(
    program: ProgramSpec,
    bid: ProposalBid,
    credibility: float,
    novelty_index: float,
    phase: str = "proposal",
    tuning: Optional[Dict[str, Any]] = None,
) -> Tuple[float, List[CriterionEvalDetail], List[str]]:
    """Evaluate all criteria on a bid, returning (perf_score, details, gate_failures)."""
    t = tuning if tuning is not None else load_tuning()
    details: List[CriterionEvalDetail] = []
    gate_failures: List[str] = []

    flyoff_tol = float(t["FLYOFF_GATE_TOL"])
    weighted_sum = 0.0
    total_weight = 0.0

    for crit in program.criteria:
        s_i = criterion_sign(crit.op)
        promised_val = float(bid.promised.get(crit.key, crit.value))
        if phase == "flyoff" and crit.key in bid.measured_performance:
            est: Estimate = bid.measured_performance[crit.key]
        else:
            est = bid.estimates.get(
                crit.key, Estimate(value=promised_val, sigma=0.0, source="sim")
            )
        mu = float(est.value)
        sigma = float(est.sigma)

        _, overclaim_q, v_hat = compute_credible_value(
            crit=crit,
            mu=mu,
            sigma=sigma,
            promised=promised_val,
            credibility=credibility,
            novelty_index=novelty_index,
            phase=phase,
            tuning=t,
        )

        # Gate check for "threshold" and "objective" kinds
        gate_passed = True
        if crit.kind in ("threshold", "objective"):
            if crit.unit == "bool":
                gate_passed = mu >= 0.5
            elif phase == "flyoff":
                gate_passed = s_i * (mu - crit.value) >= -flyoff_tol * abs(crit.value)
            else:
                gate_passed = s_i * (promised_val - crit.value) >= -1e-9
            if not gate_passed:
                gate_failures.append(f"THRESHOLD_GATE:{crit.key}")

        u_i = compute_criterion_utility(crit, v_hat, t)
        w_i = float(crit.weight) if crit.kind in ("objective", "weighted") else 0.0
        w_u = w_i * u_i
        if w_i > 0.0:
            weighted_sum += w_u
            total_weight += w_i

        details.append(
            CriterionEvalDetail(
                key=crit.key,
                kind=crit.kind,
                promised=promised_val,
                substantiated_mu=mu,
                substantiated_sigma=sigma,
                credible_value=v_hat,
                overclaim_q=overclaim_q,
                gate_passed=gate_passed,
                utility=u_i,
                weight=w_i,
                weighted_utility=w_u,
            )
        )

    u_max = float(t["U_MAX"])
    if total_weight > 0.0:
        perf_score = clamp(100.0 * (weighted_sum / total_weight), 0.0, 100.0 * u_max)
    else:
        perf_score = 100.0 if not gate_failures else 0.0

    return perf_score, details, gate_failures


def compute_cost_score(
    program: ProgramSpec,
    bid: ProposalBid,
    tuning: Optional[Dict[str, Any]] = None,
) -> Tuple[float, List[str]]:
    """Compute cost score S_cost in [0, 100] and check price ceiling gate (§5.4.1)."""
    t = tuning if tuning is not None else load_tuning()
    reasons: List[str] = []

    p_full = float(t["PRICE_FULL_RATIO"])
    p_zero = float(t["PRICE_ZERO_RATIO"])
    tol = float(t["PRICE_REALISM_TOL"])

    ceil_unit = max(float(program.budget.unit_price_ceiling_usd), 1.0)
    if bid.unit_price_bid_usd > p_zero * ceil_unit + 1e-6:
        reasons.append("PRICE_CEILING_GATE:unit_price_bid_exceeds_limit")

    b_unit_hat = max(
        float(bid.unit_price_bid_usd),
        (1.0 - tol) * float(bid.unit_cost_estimate_usd),
    )
    rho_unit = b_unit_hat / ceil_unit
    s_unit = 100.0 * clamp((p_zero - rho_unit) / (p_zero - p_full), 0.0, 1.0)

    ceil_dev = max(float(program.budget.dev_usd), 1.0)
    b_dev_hat = max(
        float(bid.dev_cost_bid_usd),
        (1.0 - tol) * float(bid.dev_cost_estimate_usd),
    )
    rho_dev = b_dev_hat / ceil_dev
    s_dev = 100.0 * clamp((p_zero - rho_dev) / (p_zero - p_full), 0.0, 1.0)

    w_u = float(t["COST_W_UNIT"])
    w_d = float(t["COST_W_DEV"])
    return w_u * s_unit + w_d * s_dev, reasons


def compute_schedule_score(
    program: ProgramSpec,
    bid: ProposalBid,
    credibility: float,
    novelty_index: float,
    phase: str = "proposal",
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute schedule score S_sched in [0, SCHED_MAX] (§5.4.2)."""
    t = tuning if tuning is not None else load_tuning()
    ff_due_day = date_to_day(program.first_flight_due)

    if phase == "flyoff" and bid.actual_first_flight_day is not None:
        t_ff_hat = float(bid.actual_first_flight_day)
    else:
        d_exp = float(t["DEV_DAYS_BASE"]) * (
            float(t["DEV_DAYS_NOV_BASE"]) + float(t["DEV_DAYS_NOV_K"]) * novelty_index
        )
        t_ff_floor = float(bid.submitted_day) + float(t["SCHED_REALISM"]) * d_exp
        d_slip = float(t["SLIP_DAYS_PER_NOV"]) * novelty_index * (1.0 - credibility)
        t_ff_hat = max(float(bid.promised_first_flight_day), t_ff_floor) + d_slip

    months_late = (t_ff_hat - float(ff_due_day)) / float(t["DAYS_PER_MONTH"])
    raw_sched = 100.0 - float(t["SCHED_PTS_PER_MONTH"]) * months_late
    return clamp(raw_sched, 0.0, float(t["SCHED_MAX"]))


def compute_risk_score(
    details: List[CriterionEvalDetail],
    credibility: float,
    novelty_index: float,
    tuning: Optional[Dict[str, Any]] = None,
) -> Tuple[float, float]:
    """Compute (risk_index R_tech in [0, 1], risk_score S_risk in [0, 100]) (§5.4.3)."""
    t = tuning if tuning is not None else load_tuning()
    gate_w = float(t["GATE_RISK_WEIGHT"])
    q_norm = float(t["RISK_Q_NORM"])

    w_sum = 0.0
    q_acc = 0.0
    sig_acc = 0.0

    for d in details:
        if d.kind == "threshold" and d.weight <= 0.0:
            w_tilde = gate_w
        else:
            w_tilde = max(d.weight, gate_w)
        w_sum += w_tilde
        q_acc += w_tilde * (d.overclaim_q / q_norm)
        denom = 0.10 * max(abs(d.substantiated_mu), 1.0)
        sig_rel = min(1.0, max(0.0, d.substantiated_sigma) / denom)
        sig_acc += w_tilde * sig_rel

    q_bar = clamp(q_acc / w_sum, 0.0, 1.0) if w_sum > 0.0 else 0.0
    sig_bar = clamp(sig_acc / w_sum, 0.0, 1.0) if w_sum > 0.0 else 0.0
    r_nov = clamp(novelty_index, 0.0, 1.0)

    r_tech = clamp(
        float(t["RISK_W_NOV"]) * r_nov
        + float(t["RISK_W_OVER"]) * q_bar
        + float(t["RISK_W_SIG"]) * sig_bar
        + float(t["RISK_W_CRED"]) * (1.0 - credibility),
        0.0,
        1.0,
    )
    return r_tech, 100.0 * (1.0 - r_tech)


def compute_dynamic_incumbent_bias(
    bidder: BidderContext,
    is_originator: bool = False,
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute dynamic incumbent bias in [-0.50, 1.00] from live campaign state (§5.4.5)."""
    t = tuning if tuning is not None else load_tuning()
    same_role = (
        float(t["INC_SAME_ROLE"]) if bidder.active_contracts_same_role > 0 else 0.0
    )
    same_cust = (
        float(t["INC_SAME_CUSTOMER"])
        if bidder.active_contracts_same_customer > 0
        else 0.0
    )
    rep_term = float(t["INC_REP_K"]) * ((bidder.reputation_service - 50.0) / 50.0)
    orig_term = float(t["ORIGINATOR_BIAS"]) if is_originator else 0.0
    return clamp(same_role + same_cust + rep_term + orig_term, -0.50, 1.00)


def compute_politics_bonus(
    program: ProgramSpec,
    bid: ProposalBid,
    bidder: BidderContext,
    use_static_incumbent: bool = True,
    include_politics: bool = True,
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute total political adjustment Delta_pol in [-POL_CAP, +POL_CAP] (§5.4.5)."""
    if not include_politics:
        return 0.0
    t = tuning if tuning is not None else load_tuning()

    if use_static_incumbent and bid.company_id in program.politics.incumbent_bias:
        inc_bias = float(program.politics.incumbent_bias[bid.company_id])
        if bid.is_originator:
            inc_bias = clamp(inc_bias + float(t["ORIGINATOR_BIAS"]), -0.50, 1.00)
    else:
        inc_bias = compute_dynamic_incumbent_bias(
            bidder, is_originator=bid.is_originator, tuning=t
        )

    delta_inc = float(t["INC_PTS"]) * inc_bias
    delta_cong = (
        float(t["CONG_PTS"])
        * float(program.politics.congressional_interest)
        * (float(bidder.district_weight) - 0.35)
    )
    pc = max(0.0, float(bid.political_capital_spent))
    delta_lobby = float(t["LOBBY_MAX_PTS"]) * (
        1.0 - math.exp(-pc / float(t["LOBBY_SCALE_PC"]))
    )

    if bid.company_id in program.politics.industrial_base_need:
        b_ib = float(program.politics.industrial_base_need[bid.company_id])
    else:
        b_ib = float(bidder.idle_factory_fraction) - 0.30
    delta_ib = float(t["IB_PTS"]) * b_ib

    delta_rival = (
        -float(t["RIVAL_PTS"]) if bid.cross_service_derivative else 0.0
    )

    pol_cap = float(t["POL_CAP"])
    return clamp(
        delta_inc + delta_cong + delta_lobby + delta_ib + delta_rival,
        -pol_cap,
        pol_cap,
    )


def compute_flyoff_promise_and_flaw_penalties(
    program: ProgramSpec,
    bid: ProposalBid,
    tuning: Optional[Dict[str, Any]] = None,
) -> Tuple[float, float]:
    """Compute (promise_penalty, flaw_penalty) for fly-off phase (§5.6)."""
    t = tuning if tuning is not None else load_tuning()
    gate_w = float(t["GATE_RISK_WEIGHT"])

    w_sum = 0.0
    shortfall_acc = 0.0
    for crit in program.criteria:
        if crit.unit == "bool":
            continue
        s_i = criterion_sign(crit.op)
        p_i = float(bid.promised.get(crit.key, crit.value))
        est = bid.measured_performance.get(
            crit.key, bid.estimates.get(crit.key, Estimate(value=p_i, sigma=0.0))
        )
        mu_flt = float(est.value)
        delta_prom = max(0.0, (s_i * (p_i - mu_flt)) / max(abs(p_i), 1.0))
        w_tilde = max(float(crit.weight), gate_w)
        w_sum += w_tilde
        shortfall_acc += w_tilde * delta_prom

    avg_shortfall = shortfall_acc / w_sum if w_sum > 0.0 else 0.0
    promise_penalty = float(t["PROMISE_PTS_PER_PCT"]) * 100.0 * avg_shortfall
    flaw_penalty = float(t["FLAW_PTS_PER_SEVERITY"]) * max(
        0, int(bid.unfixed_flaw_severity_sum)
    )
    return promise_penalty, flaw_penalty


def score_bid(
    program: ProgramSpec,
    bid: ProposalBid,
    bidder: BidderContext,
    phase: str = "proposal",
    eval_noise: float = 0.0,
    use_static_incumbent: bool = True,
    include_politics: bool = True,
    tuning: Optional[Dict[str, Any]] = None,
) -> BidScoreBreakdown:
    """Compute complete BidScoreBreakdown for one bid in 'proposal' or 'flyoff' phase."""
    t = tuning if tuning is not None else load_tuning()

    credibility = compute_credibility(bidder, t)
    novelty_idx = compute_novelty_index(bid.novelty, phase=phase, tuning=t)

    eq_failures = check_equipment_gates(program.equipment, bid.equipment)
    perf_score, details, crit_failures = evaluate_criteria_and_performance(
        program=program,
        bid=bid,
        credibility=credibility,
        novelty_index=novelty_idx,
        phase=phase,
        tuning=t,
    )
    cost_score, cost_failures = compute_cost_score(program, bid, t)
    sched_score = compute_schedule_score(
        program=program,
        bid=bid,
        credibility=credibility,
        novelty_index=novelty_idx,
        phase=phase,
        tuning=t,
    )
    risk_idx, risk_score = compute_risk_score(
        details=details,
        credibility=credibility,
        novelty_index=novelty_idx,
        tuning=t,
    )

    flyoff_failures: List[str] = []
    if phase == "flyoff" and bid.actual_first_flight_day is None:
        flyoff_failures.append("FLYOFF_GATE:prototype_not_flown")

    disqualify_reasons = eq_failures + crit_failures + cost_failures + flyoff_failures
    responsive = len(disqualify_reasons) == 0

    weights = program.eval_weights.get(
        phase, {"perf": 0.45, "cost": 0.20, "sched": 0.15, "risk": 0.20}
    )
    tech_score = (
        float(weights["perf"]) * perf_score
        + float(weights["cost"]) * cost_score
        + float(weights["sched"]) * sched_score
        + float(weights["risk"]) * risk_score
    )

    pol_bonus = compute_politics_bonus(
        program=program,
        bid=bid,
        bidder=bidder,
        use_static_incumbent=use_static_incumbent,
        include_politics=include_politics,
        tuning=t,
    )

    if phase == "flyoff":
        promise_pen, flaw_pen = compute_flyoff_promise_and_flaw_penalties(
            program, bid, t
        )
    else:
        promise_pen, flaw_pen = 0.0, 0.0

    total_score = tech_score + pol_bonus - promise_pen - flaw_pen + float(eval_noise)

    return BidScoreBreakdown(
        bid_id=bid.bid_id,
        company_id=bid.company_id,
        design_name=bid.design_name,
        phase=phase,
        responsive=responsive,
        disqualify_reasons=disqualify_reasons,
        credibility=credibility,
        novelty_index=novelty_idx,
        perf_score=perf_score,
        cost_score=cost_score,
        sched_score=sched_score,
        risk_index=risk_idx,
        risk_score=risk_score,
        tech_score=tech_score,
        politics_bonus=pol_bonus,
        promise_penalty=promise_pen,
        flaw_penalty=flaw_pen,
        eval_noise=float(eval_noise),
        total_score=total_score,
        criteria_details=details,
    )


def preview_bid_evaluation(
    program: ProgramSpec,
    bid: ProposalBid,
    bidder: BidderContext,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """UI helper (§3.1 step 2): return live deterministic preview + confidence per criterion."""
    t = tuning if tuning is not None else load_tuning()
    breakdown = score_bid(
        program=program,
        bid=bid,
        bidder=bidder,
        phase="proposal",
        eval_noise=0.0,
        tuning=t,
    )
    confidences: Dict[str, float] = {}
    for crit in program.criteria:
        if crit.unit == "bool":
            est = bid.estimates.get(crit.key, Estimate(value=1.0, sigma=0.0))
            confidences[crit.key] = 1.0 if est.value >= 0.5 else 0.0
            continue
        s_i = criterion_sign(crit.op)
        p_i = float(bid.promised.get(crit.key, crit.value))
        est = bid.estimates.get(crit.key, Estimate(value=p_i, sigma=0.0))
        sig_eff = max(float(est.sigma), 0.01 * max(abs(est.value), 1.0))
        z = (s_i * (float(est.value) - p_i)) / sig_eff
        conf = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
        confidences[crit.key] = clamp(conf, 0.0, 1.0)
    return {
        "breakdown": breakdown,
        "criterion_confidence": confidences,
    }
