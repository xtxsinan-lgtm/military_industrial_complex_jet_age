"""Alt-history adaptation and Procedural / Dynamic RFP Generator.

Implements sections 5.9 and 5.10 of docs/spec/05_procurement.md.
"""
from __future__ import annotations

import copy
import math
from typing import Any, Dict, List, Optional, Tuple

from .dates import (
    DAYS_PER_MONTH,
    DAYS_PER_YEAR,
    date_to_day,
    day_to_fractional_year,
    day_to_iso,
)
from .models import (
    AcquisitionSpec,
    AltHistorySpec,
    BudgetSpec,
    CapabilityGapRecord,
    CriterionSpec,
    EquipmentRequirement,
    HistoricalMeta,
    PoliticsSpec,
    ProgramSpec,
    ThreatMilestone,
)
from .scoring import clamp, criterion_sign
from .tuning import load_tuning

# Technological frontier curves 1945 -> 1960 by role and criterion key (SI units)
FRONTIER_ANCHORS: Dict[str, List[Tuple[float, float]]] = {
    "max_mach_alt": [
        (1945.0, 0.78),
        (1948.0, 0.88),
        (1950.0, 1.15),
        (1952.5, 1.55),
        (1955.0, 2.05),
        (1958.0, 2.35),
        (1960.0, 2.50),
    ],
    "climb_rate_sl_mps": [
        (1945.0, 24.0),
        (1948.0, 42.0),
        (1950.0, 68.0),
        (1953.0, 130.0),
        (1956.0, 195.0),
        (1960.0, 235.0),
    ],
    "service_ceiling_m": [
        (1945.0, 12200.0),
        (1948.0, 13700.0),
        (1951.0, 15240.0),
        (1955.0, 17500.0),
        (1960.0, 19800.0),
    ],
    "combat_radius_m": [
        (1945.0, 500000.0),
        (1950.0, 650000.0),
        (1955.0, 800000.0),
        (1960.0, 950000.0),
    ],
    "sustained_turn_dps_m08_4572m": [
        (1945.0, 10.5),
        (1950.0, 11.5),
        (1955.0, 12.2),
        (1960.0, 12.8),
    ],
    "stall_speed_mps": [
        (1945.0, 46.0),
        (1950.0, 51.0),
        (1955.0, 55.0),
        (1960.0, 58.0),
    ],
    "payload_kg": [
        (1945.0, 900.0),
        (1950.0, 1800.0),
        (1955.0, 3600.0),
        (1960.0, 5400.0),
    ],
}

ROLE_COST_MULTIPLIERS: Dict[str, float] = {
    "day_fighter": 0.85,
    "interceptor": 1.25,
    "fighter_bomber": 1.15,
    "escort_fighter": 1.30,
    "carrier_day_fighter": 0.95,
    "carrier_interceptor": 1.35,
}

ROLE_STANDARD_QUANTITIES: Dict[str, int] = {
    "day_fighter": 600,
    "interceptor": 450,
    "fighter_bomber": 550,
    "escort_fighter": 350,
    "carrier_day_fighter": 400,
    "carrier_interceptor": 350,
}


def interpolate_frontier(key: str, year: float) -> float:
    """Piecewise linear interpolation of technological frontier at calendar year."""
    pts = FRONTIER_ANCHORS.get(key)
    if not pts:
        return 1.0
    if year <= pts[0][0]:
        return pts[0][1]
    if year >= pts[-1][0]:
        return pts[-1][1]
    for i in range(len(pts) - 1):
        y0, v0 = pts[i]
        y1, v1 = pts[i + 1]
        if y0 <= year <= y1:
            frac = (year - y0) / max(y1 - y0, 1e-6)
            return v0 + frac * (v1 - v0)
    return pts[-1][1]


def adapt_program_to_world(
    program: ProgramSpec,
    world_best_by_key: Dict[str, float],
    tuning: Optional[Dict[str, Any]] = None,
) -> ProgramSpec:
    """Escalate historical program thresholds if in-game aircraft have already beaten history (§5.9 rule 1)."""
    t = tuning if tuning is not None else load_tuning()
    adapt_frac = float(t["ADAPT_FRAC"])
    default_span = float(t["DEFAULT_SPAN_FRAC"])

    adapted = copy.deepcopy(program)
    for crit in adapted.criteria:
        if crit.unit == "bool" or crit.op != ">=":
            continue
        if crit.key not in world_best_by_key:
            continue
        v_world = float(world_best_by_key[crit.key])
        candidate_t = adapt_frac * v_world
        if candidate_t > crit.value:
            old_t = max(crit.value, 1e-6)
            ratio = candidate_t / old_t
            crit.value = round(candidate_t, 4)
            if crit.objective_value is not None:
                crit.objective_value = round(crit.objective_value * ratio, 4)
            else:
                crit.objective_value = round(
                    crit.value * (1.0 + default_span), 4
                )
    return adapted


def should_suppress_stopgap(
    program: ProgramSpec,
    recent_role_awards: List[Dict[str, Any]],
    current_day: int,
    tuning: Optional[Dict[str, Any]] = None,
) -> bool:
    """Return True if a stopgap program is redundant due to a recent qualifying award (§5.9 rule 2)."""
    if not program.alt_history.suppress_if_role_satisfied:
        return False
    t = tuning if tuning is not None else load_tuning()
    window_days = float(t["SUPPRESS_YEARS"]) * DAYS_PER_YEAR

    for award in recent_role_awards:
        if award.get("customer") != program.customer or award.get("role") != program.role:
            continue
        award_day = int(award.get("award_day", -99999))
        if current_day - award_day > window_days:
            continue
        perf: Dict[str, float] = award.get("delivered_performance", {})
        meets_all = True
        for crit in program.criteria:
            if crit.unit == "bool" or crit.kind not in ("threshold", "objective"):
                continue
            val = float(perf.get(crit.key, 0.0))
            if crit.op == ">=" and val < 0.95 * crit.value:
                meets_all = False
                break
            if crit.op == "<=" and val > 1.05 * crit.value:
                meets_all = False
                break
        if meets_all:
            return True
    return False


def redirect_follow_on_program(
    program: ProgramSpec,
    prior_program_winners: Dict[str, Optional[str]],
) -> ProgramSpec:
    """Redirect follow-on incumbent bias or sole-source recipient to predecessor winner (§5.9 rule 3)."""
    pred_id = program.alt_history.predecessor_program_id
    if not pred_id or pred_id not in prior_program_winners:
        return copy.deepcopy(program)

    updated = copy.deepcopy(program)
    actual_winner = prior_program_winners[pred_id]
    hist_winner = updated.historical.winner_company_id

    if actual_winner is None:
        # Predecessor was cancelled with no winner -> open competition
        if updated.acquisition.style == "sole_source":
            updated.acquisition.style = "paper_award"
            updated.acquisition.downselect_count = 1
        return updated

    if actual_winner != hist_winner:
        old_bias = updated.politics.incumbent_bias.get(hist_winner, 0.45)
        updated.politics.incumbent_bias[actual_winner] = max(
            old_bias, updated.politics.incumbent_bias.get(actual_winner, 0.0)
        )
        if hist_winner in updated.politics.incumbent_bias:
            updated.politics.incumbent_bias[hist_winner] = min(
                0.15, updated.politics.incumbent_bias[hist_winner]
            )
    return updated


def create_capability_gap(
    program: ProgramSpec,
    cancelled_day: int,
    tuning: Optional[Dict[str, Any]] = None,
) -> CapabilityGapRecord:
    """Create a CapabilityGapRecord for re-issuing a cancelled/failed requirement (§5.9 rule 4)."""
    t = tuning if tuning is not None else load_tuning()
    urgent = float(program.acquisition.urgency) >= 0.75
    delay_months = (
        int(t["REISSUE_DELAY_URGENT_MONTHS"])
        if urgent
        else int(t["REISSUE_DELAY_MONTHS"])
    )
    reissue_day = int(cancelled_day + round(delay_months * DAYS_PER_MONTH))
    return CapabilityGapRecord(
        customer=program.customer,
        role=program.role,
        origin_program_id=program.id,
        created_day=int(cancelled_day),
        reissue_due_day=reissue_day,
        urgency=float(program.acquisition.urgency),
        reissued=False,
    )


def compute_role_demand_score(
    customer: str,
    role: str,
    current_day: int,
    fleet_service_entry_day: int,
    fleet_best_mach: float,
    active_threats: List[ThreatMilestone],
    has_unmet_gap: bool,
    tuning: Optional[Dict[str, Any]] = None,
) -> Tuple[float, Dict[str, float]]:
    """Compute monthly demand pressure D_total and component breakdown (§5.10.1-5.10.2)."""
    t = tuning if tuning is not None else load_tuning()

    age_years = max(0.0, (float(current_day) - float(fleet_service_entry_day)) / DAYS_PER_YEAR)
    d_age = clamp(
        (age_years - float(t["REPLACE_YEARS"])) / float(t["AGE_RAMP_YEARS"]),
        0.0,
        1.0,
    )

    threat_mach_req = 0.75
    shock_sum = 0.0
    for tm in active_threats:
        tm_day = date_to_day(tm.date)
        if tm_day > current_day:
            continue
        if customer not in tm.affected_customers or role not in tm.affected_roles:
            continue
        mult = 1.25 if "interceptor" in role else 1.0
        threat_mach_req = max(threat_mach_req, tm.threat_mach * mult)
        # Recent threat shocks decay over 2.5 years
        years_since = (float(current_day) - float(tm_day)) / DAYS_PER_YEAR
        if years_since <= 2.5:
            shock_sum += tm.demand_shock * (1.0 - years_since / 2.5)

    d_threat = clamp(
        ((threat_mach_req - float(fleet_best_mach)) / float(t["THREAT_GAP_NORM"]))
        + shock_sum,
        0.0,
        1.0,
    )
    d_gap = 1.0 if has_unmet_gap else 0.0

    d_total = (
        float(t["W_AGE"]) * d_age
        + float(t["W_THREAT"]) * d_threat
        + float(t["W_GAP"]) * d_gap
    )
    return d_total, {
        "d_age": d_age,
        "d_threat": d_threat,
        "d_gap": d_gap,
        "d_total": d_total,
    }


def evaluate_monthly_rfp_trigger(
    customer: str,
    role: str,
    current_day: int,
    fleet_service_entry_day: int,
    fleet_best_mach: float,
    active_threats: List[ThreatMilestone],
    has_unmet_gap: bool,
    last_rfp_day_in_role: int,
    open_programs_for_customer: int,
    scheduled_historical_days_in_role: List[int],
    budget_index: float = 1.0,
    tuning: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, float, Dict[str, float]]:
    """Determine whether to issue a procedural RFP on the 1st of the month (§5.10.2)."""
    t = tuning if tuning is not None else load_tuning()
    d_total, parts = compute_role_demand_score(
        customer=customer,
        role=role,
        current_day=current_day,
        fleet_service_entry_day=fleet_service_entry_day,
        fleet_best_mach=fleet_best_mach,
        active_threats=active_threats,
        has_unmet_gap=has_unmet_gap,
        tuning=t,
    )

    if d_total < float(t["ISSUE_THRESHOLD"]):
        return False, d_total, parts

    min_gap_days = float(t["MIN_GAP_MONTHS"]) * DAYS_PER_MONTH
    if current_day - last_rfp_day_in_role < min_gap_days:
        return False, d_total, parts

    lookahead_days = float(t["HIST_LOOKAHEAD_MONTHS"]) * DAYS_PER_MONTH
    for h_day in scheduled_historical_days_in_role:
        if 0 <= (h_day - current_day) <= lookahead_days:
            return False, d_total, parts

    max_open = max(1, int(round(float(t["MAX_OPEN_BASE"]) * float(budget_index))))
    if open_programs_for_customer >= max_open:
        return False, d_total, parts

    return True, d_total, parts


def generate_procedural_requirement(
    customer: str,
    role: str,
    issue_day: int,
    demand_score: float = 0.70,
    budget_index: float = 1.0,
    sequence_num: int = 1,
    tuning: Optional[Dict[str, Any]] = None,
) -> ProgramSpec:
    """Synthesize a complete procedural ProgramSpec for (customer, role, issue_day) (§5.10.3)."""
    t = tuning if tuning is not None else load_tuning()
    year = day_to_fractional_year(issue_day)
    year_int = int(math.floor(year))
    amb = min(float(demand_score), float(t["AMB_CAP"]))
    span_frac = float(t["DEFAULT_SPAN_FRAC"])

    urgent = float(demand_score) >= float(t["URGENT_DEMAND"])
    sched_mult = float(t["URGENT_COMPRESS"]) if urgent else 1.0

    prop_due_day = issue_day + int(round(float(t["PROPOSAL_WINDOW_DAYS"]) * sched_mult))
    ff_due_day = issue_day + int(round(float(t["FF_DUE_DAYS"]) * sched_mult))
    ioc_due_day = issue_day + int(round(float(t["IOC_DUE_DAYS"]) * sched_mult))

    mach_f = interpolate_frontier("max_mach_alt", year) * (1.0 + 0.05 * amb)
    climb_f = interpolate_frontier("climb_rate_sl_mps", year) * (1.0 + 0.05 * amb)
    ceil_f = interpolate_frontier("service_ceiling_m", year)
    rad_f = interpolate_frontier("combat_radius_m", year)
    stall_f = interpolate_frontier("stall_speed_mps", year)

    is_carrier = customer == "USN" or role.startswith("carrier_")
    is_interceptor = "interceptor" in role

    criteria: List[CriterionSpec] = [
        CriterionSpec(
            key="max_mach_alt",
            kind="objective",
            op=">=",
            value=round(mach_f, 2),
            objective_value=round(mach_f * (1.0 + span_frac), 2),
            weight=0.35 if is_interceptor else 0.30,
            unit="mach",
            description="Maximum level Mach at altitude",
        ),
        CriterionSpec(
            key="climb_rate_sl_mps",
            kind="objective",
            op=">=",
            value=round(climb_f, 1),
            objective_value=round(climb_f * (1.0 + span_frac), 1),
            weight=0.25,
            unit="mps",
            description="Sea-level rate of climb",
        ),
        CriterionSpec(
            key="service_ceiling_m",
            kind="objective",
            op=">=",
            value=round(ceil_f, 0),
            objective_value=round(ceil_f * 1.12, 0),
            weight=0.20,
            unit="m",
            description="Service ceiling",
        ),
        CriterionSpec(
            key="combat_radius_m",
            kind="objective",
            op=">=",
            value=round(rad_f * (1.25 if role == "escort_fighter" else 0.85), 0),
            objective_value=round(
                rad_f * (1.50 if role == "escort_fighter" else 1.05), 0
            ),
            weight=0.20 if not is_carrier else 0.10,
            unit="m",
            description="Combat radius",
        ),
    ]

    if is_carrier:
        criteria.append(
            CriterionSpec(
                key="stall_speed_mps",
                kind="objective",
                op="<=",
                value=round(stall_f, 1),
                objective_value=round(stall_f * 0.90, 1),
                weight=0.10 if is_interceptor else 0.15,
                unit="mps",
                description="Carrier approach/stall speed",
            )
        )
        criteria.append(
            CriterionSpec(
                key="carrier_suitability",
                kind="threshold",
                op=">=",
                value=1.0,
                weight=0.0,
                unit="bool",
                description="Carrier deck suitability",
            )
        )

    c_ref = float(t["COST_REF_C0_USD"]) * math.exp(
        float(t["COST_REF_GROWTH"]) * (year - 1945.0)
    )
    role_mult = ROLE_COST_MULTIPLIERS.get(role, 1.0)
    unit_ceil = round(float(t["CEILING_MARGIN"]) * c_ref * role_mult, -3)
    dev_budget = round(float(t["DEV_MULT"]) * unit_ceil, -4)
    base_qty = ROLE_STANDARD_QUANTITIES.get(role, 400)
    qty = max(100, int(round(base_qty * clamp(float(budget_index), 0.5, 1.5))))

    eq = EquipmentRequirement(
        carrier_capable=is_carrier,
        radar_required=is_interceptor,
        min_crew=2 if (is_interceptor and year >= 1955.0 and is_carrier) else 1,
        min_engines=1,
        internal_bay_required=False,
        min_guns_20mm=0 if (is_interceptor and year >= 1955.0) else 2,
        missile_capability=["sarh"] if (is_interceptor and year >= 1954.0) else [],
    )

    prog_id = f"proc_{customer.lower()}_{role}_{year_int}_{sequence_num}"
    prog_name = f"{year_int} {customer} {role.replace('_', ' ').title()} Requirement"

    return ProgramSpec(
        id=prog_id,
        name_key=f"program.{prog_id}.name",
        program_name=prog_name,
        customer=customer,
        role=role,
        mvp_core=False,
        issue_date=day_to_iso(issue_day),
        proposal_due=day_to_iso(prop_due_day),
        first_flight_due=day_to_iso(ff_due_day),
        ioc_due=day_to_iso(ioc_due_day),
        equipment=eq,
        criteria=criteria,
        budget=BudgetSpec(
            dev_usd=dev_budget,
            unit_price_ceiling_usd=unit_ceil,
            quantity_planned=qty,
        ),
        acquisition=AcquisitionSpec(
            style="flyoff" if demand_score < 0.85 else "paper_award",
            downselect_count=2 if demand_score < 0.85 else 1,
            prototype_quantity_per_winner=2,
            allow_dual_award=False,
            production_lots=4,
            urgency=clamp(demand_score, 0.3, 0.95),
        ),
        politics=PoliticsSpec(
            incumbent_bias={},
            congressional_interest=0.35,
            industrial_base_need={},
        ),
        historical=HistoricalMeta(
            winner_company_id="",
            winner_design_name="",
            award_date=day_to_iso(prop_due_day),
            outcome="produced",
            production_delivered=0,
            notes="Procedurally generated requirement.",
            citations=[],
            competitors=[],
        ),
        alt_history=AltHistorySpec(),
    )
