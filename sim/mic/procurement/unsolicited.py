"""Unsolicited Proposal (Private Venture Pitch) evaluation mechanics.

Implements section 5.11 of docs/spec/05_procurement.md.
Modeled on Lockheed CL-246 (F-104), North American Sabre 45 (F-100),
Republic AP-63 (F-105), and Northrop N-156 (T-38/F-5).
"""
from __future__ import annotations

import copy
import math
from typing import Any, Dict, Optional

from .dates import day_to_fractional_year
from .dynamic_rfp import ROLE_STANDARD_QUANTITIES, generate_procedural_requirement
from .evaluation import create_contract_from_award
from .models import (
    BidderContext,
    ProgramSpec,
    ProposalBid,
    UnsolicitedPitchResult,
)
from .rng import RandomSource
from .scoring import clamp, compute_credibility, criterion_sign, score_bid
from .tuning import load_tuning


def _logistic(x: float) -> float:
    if x >= 35.0:
        return 1.0
    if x <= -35.0:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


def evaluate_unsolicited_proposal(
    bid: ProposalBid,
    bidder: BidderContext,
    customer: str,
    role: str,
    pitch_day: int,
    role_demand_score: float = 0.55,
    budget_index: float = 1.0,
    has_open_program_in_role: bool = False,
    prototype_already_flown: bool = False,
    rng: Optional[RandomSource] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> UnsolicitedPitchResult:
    """Evaluate an unsolicited private-venture proposal (§5.11)."""
    t = tuning if tuning is not None else load_tuning()
    rng_src = rng if rng is not None else RandomSource(deterministic=True)

    review_delay = int(t["U_REVIEW_DELAY_DAYS"])
    cooldown_days = int(t["U_COOLDOWN_DAYS"])
    decision_day = int(pitch_day) + review_delay

    # Synthesize virtual benchmark requirement at pitch_day
    virtual_req: ProgramSpec = generate_procedural_requirement(
        customer=customer,
        role=role,
        issue_day=pitch_day,
        demand_score=role_demand_score,
        budget_index=budget_index,
        sequence_num=99,
        tuning=t,
    )

    year = day_to_fractional_year(pitch_day)
    c_ref_dev = (
        float(t["DEV_MULT"])
        * float(t["COST_REF_C0_USD"])
        * math.exp(float(t["COST_REF_GROWTH"]) * (year - 1945.0))
    )
    pitch_cost = float(t["U_PITCH_COST_FRAC"]) * c_ref_dev

    bd = score_bid(
        program=virtual_req,
        bid=bid,
        bidder=bidder,
        phase="proposal",
        eval_noise=0.0,
        use_static_incumbent=False,
        include_politics=True,
        tuning=t,
    )
    eval_score = bd.total_score + (5.0 if prototype_already_flown else 0.0)

    if not bd.responsive:
        return UnsolicitedPitchResult(
            company_id=bid.company_id,
            design_name=bid.design_name,
            customer=customer,
            role=role,
            pitch_day=int(pitch_day),
            decision_day=decision_day,
            pitch_cost_usd=pitch_cost,
            evaluated_score=eval_score,
            p_accept=0.0,
            accepted=False,
            p_sole_source=0.0,
            outcome="rejected",
            generated_program=None,
            awarded_contract=None,
            cooldown_until_day=decision_day + cooldown_days,
        )

    score_factor = _logistic(
        (eval_score - float(t["U_MID"])) / float(t["U_SCALE"])
    )
    need_factor = clamp(float(t["U_NEED_BASE"]) + float(role_demand_score), 0.20, 1.00)
    b_factor = clamp(float(budget_index), 0.50, 1.30)
    f_open = float(t["U_OPEN_PROGRAM_FACTOR"]) if has_open_program_in_role else 1.0

    p_accept = clamp(score_factor * need_factor * b_factor * f_open, 0.0, 0.95)
    u_acc = rng_src.uniform()
    accepted = u_acc < p_accept

    cred = compute_credibility(bidder, t)
    p_sole = clamp(
        float(t["U_SOLE_BASE"])
        + float(t["U_SOLE_K"]) * (cred - 0.50)
        + (0.20 if prototype_already_flown else 0.0),
        0.15,
        0.90,
    )

    if not accepted:
        return UnsolicitedPitchResult(
            company_id=bid.company_id,
            design_name=bid.design_name,
            customer=customer,
            role=role,
            pitch_day=int(pitch_day),
            decision_day=decision_day,
            pitch_cost_usd=pitch_cost,
            evaluated_score=eval_score,
            p_accept=p_accept,
            accepted=False,
            p_sole_source=p_sole,
            outcome="rejected",
            generated_program=None,
            awarded_contract=None,
            cooldown_until_day=decision_day + cooldown_days,
        )

    u_sole = rng_src.uniform()
    if u_sole < p_sole:
        # Sole-source award (F-100 / F-105 style)
        sole_prog = copy.deepcopy(virtual_req)
        sole_prog.id = f"unsol_sole_{customer.lower()}_{role}_{pitch_day}"
        sole_prog.acquisition.style = "sole_source"
        std_qty = ROLE_STANDARD_QUANTITIES.get(role, 400)
        sole_qty = max(50, int(round(float(t["U_QTY_FRAC"]) * std_qty)))
        sole_prog.budget.quantity_planned = sole_qty

        contract = create_contract_from_award(
            program=sole_prog,
            bid=bid,
            award_day=decision_day,
            contract_kind="production_fpif",
            quantity_override=sole_qty,
            tuning=t,
        )
        return UnsolicitedPitchResult(
            company_id=bid.company_id,
            design_name=bid.design_name,
            customer=customer,
            role=role,
            pitch_day=int(pitch_day),
            decision_day=decision_day,
            pitch_cost_usd=pitch_cost,
            evaluated_score=eval_score,
            p_accept=p_accept,
            accepted=True,
            p_sole_source=p_sole,
            outcome="sole_source_award",
            generated_program=sole_prog,
            awarded_contract=contract,
            cooldown_until_day=decision_day + cooldown_days,
        )

    # Open GOR competition tailored around the player's concept (CL-246 -> F-104 WS-303A style)
    open_prog = copy.deepcopy(virtual_req)
    open_prog.id = f"unsol_gor_{customer.lower()}_{role}_{pitch_day}"
    open_prog.acquisition.style = "paper_award"
    open_prog.politics.incumbent_bias[bid.company_id] = float(t["ORIGINATOR_BIAS"])
    copy_frac = float(t["U_COPY_OBJ_FRAC"])

    for crit in open_prog.criteria:
        if crit.unit == "bool" or crit.key not in bid.promised:
            continue
        p_val = float(bid.promised[crit.key])
        s_i = criterion_sign(crit.op)
        if s_i > 0:
            crit.objective_value = round(max(crit.value * 1.05, copy_frac * p_val), 4)
        else:
            crit.objective_value = round(
                min(crit.value * 0.95, p_val / max(copy_frac, 0.5)), 4
            )

    return UnsolicitedPitchResult(
        company_id=bid.company_id,
        design_name=bid.design_name,
        customer=customer,
        role=role,
        pitch_day=int(pitch_day),
        decision_day=decision_day,
        pitch_cost_usd=pitch_cost,
        evaluated_score=eval_score,
        p_accept=p_accept,
        accepted=True,
        p_sole_source=p_sole,
        outcome="open_competition_issued",
        generated_program=open_prog,
        awarded_contract=None,
        cooldown_until_day=decision_day + cooldown_days,
    )
