"""AI RFP Entry Selection, Bid Formulation, and Two-Stage Fly-Off Progression (`sim/mic/ai/bidding_ai.py`).

Implements Module 07 (`bidding_ai.py`) and Locked Decision D6:
- Evaluates which active AI airframers enter an RFP (`score_rfp_entry_for_ai`, `select_ai_bidders_for_rfp`).
- Synthesizes an `AircraftDesign` per AI entrant, initializes Module 06 `LineageTestState`, runs
  pre-bid wind-tunnel campaigns, and formulates a Module 05 `ProposalBid` & `BidderContext`
  (`prepare_ai_rfp_entry`, `prepare_all_ai_entries_for_rfp`).
- Advances downselected AI finalists through prototype rollout, wind-tunnel refinement, and
  flight-test syllabus execution during the two-stage `flyoff` phase (`run_ai_flyoff_progression`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from ..perf._stub_engine import resolve_engine
from ..perf.performance import PerformanceReport, evaluate
from ..procurement.dates import date_to_day
from ..procurement.models import (
    BidderContext,
    EquipmentProfile,
    Estimate,
    NoveltyProfile,
    ProgramSpec,
    ProposalBid,
)
from ..procurement.scoring import clamp, criterion_sign
from ..testing.flight_test import FlightProgrammeResult, run_flight_test_programme
from ..testing.sources import run_prototype_rollout, run_tunnel_or_ground_campaign
from ..testing.truth import (
    LineageTestState,
    compute_estimate_report,
    compute_true_performance_report,
    initialize_lineage_state,
)
from .company_ai import AICompanyState
from .design_generator import generate_ai_design_for_rfp
from .tuning import load_ai_tuning


@dataclass
class AICompetitorEntry:
    """Complete pre-bid and fly-off state for an AI competitor on a specific RFP."""

    program_id: str
    company_id: str
    company_name: str
    design_name: str
    design: Dict[str, Any]
    nominal_report: PerformanceReport
    true_performance: Dict[str, Any]
    estimate_report: Dict[str, Any]
    lineage_state: LineageTestState
    bid: ProposalBid
    bidder_context: BidderContext
    entry_score: float = 0.0
    pre_bid_tunnel_Sorting_run: bool = False
    flyoff_completed: bool = False
    flyoff_flight_result: Optional[FlightProgrammeResult] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "program_id": self.program_id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "design_name": self.design_name,
            "entry_score": round(self.entry_score, 4),
            "unit_price_bid_usd": round(self.bid.unit_price_bid_usd, 2),
            "dev_cost_bid_usd": round(self.bid.dev_cost_bid_usd, 2),
            "true_max_mach_alt": round(float(self.true_performance.get("max_mach_alt", self.nominal_report.max_mach_alt)), 4),
            "true_combat_radius_m": round(float(self.true_performance.get("combat_radius_m", self.nominal_report.combat_radius_m)), 1),
            "promised": {k: round(float(v), 4) for k, v in sorted(self.bid.promised.items())},
            "flyoff_completed": self.flyoff_completed,
            "unfixed_flaw_severity_sum": int(self.bid.unfixed_flaw_severity_sum),
            "actual_first_flight_day": self.bid.actual_first_flight_day,
        }


def _ensure_program_spec(rfp: Union[ProgramSpec, Mapping[str, Any]]) -> ProgramSpec:
    if isinstance(rfp, ProgramSpec):
        return rfp
    return ProgramSpec.from_dict(dict(rfp))


def score_rfp_entry_for_ai(
    ai_company: AICompanyState,
    rfp: Union[ProgramSpec, Mapping[str, Any]],
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute deterministic entry propensity score for `ai_company` on `rfp`."""
    t = (tuning if tuning is not None else load_ai_tuning())["bidding_ai"]
    prog = _ensure_program_spec(rfp)

    if not ai_company.active_in_fighter_market or ai_company.company_state.is_bankrupt_or_acquired:
        return -1.0
    if len(ai_company.active_rfp_bids) >= int(t["max_concurrent_rfp_bids"]):
        return -1.0

    score = float(t["entry_base_score"])
    cust = prog.customer.upper()
    pref_custs = [str(c).upper() for c in ai_company.ai_doctrine.get("preferred_customers", ["USAF"])]
    if cust in pref_custs:
        mult = 1.0 if pref_custs[0] == cust else 0.55
        score += float(t["entry_preferred_customer_bonus"]) * mult

    # Carrier capability gate check for USN RFPs
    has_carrier_tech = any("carrier" in tid for tid in ai_company.tech_state.unlocked_maturity)
    if prog.equipment.carrier_capable and "USN" not in pref_custs and not has_carrier_tech:
        score -= 0.35

    rep = float(ai_company.reputation.get(cust, 50.0)) / 100.0
    score += float(t["entry_reputation_weight"]) * rep

    active_prod = sum(1 for c in ai_company.company_state.contracts if not c.completed and c.phase == "production")
    cap_avail = clamp(1.0 - 0.30 * active_prod, 0.20, 1.0)
    score += float(t["entry_capacity_weight"]) * cap_avail

    # Role fit (heavy twin-engine bias fits interceptor/all-weather; high speed fits interceptor/day_fighter)
    role_fit = 0.55
    if prog.role in ("interceptor", "all_weather_fighter") and float(ai_company.traits.get("twin_engine_bias", 0.2)) >= 0.5:
        role_fit += 0.30
    elif prog.role == "carrier_fighter" and "USN" in pref_custs:
        role_fit += 0.35
    elif prog.role in ("day_fighter", "fighter_bomber"):
        role_fit += 0.25
    score += float(t["entry_role_fit_weight"]) * min(1.0, role_fit)

    hist_ids = {c.company_id for c in prog.historical.competitors}
    if prog.historical.winner_company_id:
        hist_ids.add(prog.historical.winner_company_id)
    if ai_company.id in hist_ids:
        score += float(t["entry_historical_competitor_bonus"])

    return float(score)


def select_ai_bidders_for_rfp(
    ai_companies: Union[Mapping[str, AICompanyState], Sequence[AICompanyState]],
    rfp: Union[ProgramSpec, Mapping[str, Any]],
    tuning: Optional[Dict[str, Any]] = None,
) -> List[Tuple[AICompanyState, float]]:
    """Select between `min_bidders_per_rfp` and `max_bidders_per_rfp` active AI companies for `rfp`."""
    t = (tuning if tuning is not None else load_ai_tuning())["bidding_ai"]
    comp_list = list(ai_companies.values()) if isinstance(ai_companies, Mapping) else list(ai_companies)

    scored: List[Tuple[float, str, AICompanyState]] = []
    for comp in comp_list:
        sc = score_rfp_entry_for_ai(comp, rfp, tuning=tuning)
        if sc > 0.0:
            scored.append((sc, comp.id, comp))

    scored.sort(key=lambda item: (-item[0], item[1]))
    min_b = int(t["min_bidders_per_rfp"])
    max_b = int(t["max_bidders_per_rfp"])
    thresh = float(t["entry_threshold_score"])

    qualified = [(comp, sc) for sc, _, comp in scored if sc >= thresh]
    if len(qualified) < min_b:
        qualified = [(comp, sc) for sc, _, comp in scored[:min_b]]
    return qualified[:max_b]


def prepare_ai_rfp_entry(
    ai_company: AICompanyState,
    rfp: Union[ProgramSpec, Mapping[str, Any]],
    campaign_seed: int = 19450101,
    available_engines: Any = None,
    rng: Any = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> AICompetitorEntry:
    """Synthesize design, run pre-bid tunnel tests, and formulate a `ProposalBid` for `ai_company`."""
    t_all = tuning if tuning is not None else load_ai_tuning()
    t = t_all["bidding_ai"]
    prog = _ensure_program_spec(rfp)
    ctx = ai_company.tech_context()

    design = generate_ai_design_for_rfp(
        company=ai_company,
        rfp=prog,
        unlocked_techs=ctx,
        available_engines=available_engines,
        rng=rng,
        tuning=t_all,
    )
    eng_id = str(design["propulsion"]["engine_id"])
    eng_deck = resolve_engine(eng_id, default_id=eng_id)
    nom_rep = evaluate(design, engine=eng_deck, tech_context=ctx)
    nom_dict = nom_rep.to_dict()
    if isinstance(nom_dict.get("ps_grid"), dict) and "ps_mps" in nom_dict["ps_grid"]:
        nom_dict["ps_grid"] = nom_dict["ps_grid"]["ps_mps"]

    issue_day = date_to_day(prog.issue_date)
    prop_due_day = date_to_day(prog.proposal_due)
    ff_due_day = date_to_day(prog.first_flight_due)
    ioc_due_day = date_to_day(prog.ioc_due)

    lineage = initialize_lineage_state(
        campaign_seed=campaign_seed,
        design=design,
        nominal_perf=nom_dict,
        date_day=issue_day,
        tech_ctx=ctx,
    )

    # Pre-bid wind tunnel campaign
    wt_lvl = int(ai_company.facilities.get("wind_tunnel_level", 1))
    prov_id = "own" if wt_lvl >= 1 else "naca"
    run_tunnel_or_ground_campaign(
        campaign_seed=campaign_seed,
        state=lineage,
        campaign_id="low_speed_tunnel",
        provider_id=prov_id,
        depth="standard",
        active_military_contract=True,
        own_wind_tunnel_level=wt_lvl,
        auto_fix_detected_flaws=True,
        tech_ctx=ctx,
    )
    if nom_rep.max_mach_alt >= 0.90 and bool(ctx.get("testing.transonic_tunnel")):
        t_prov = "own" if wt_lvl >= 2 else "naca"
        run_tunnel_or_ground_campaign(
            campaign_seed=campaign_seed,
            state=lineage,
            campaign_id="transonic_tunnel",
            provider_id=t_prov,
            depth="standard",
            active_military_contract=True,
            own_wind_tunnel_level=wt_lvl,
            auto_fix_detected_flaws=True,
            tech_ctx=ctx,
        )

    est_rep = compute_estimate_report(lineage, tech_ctx=ctx)
    true_rep = compute_true_performance_report(lineage)

    risk_tol = float(ai_company.ai_doctrine.get("risk_tolerance", 0.50))
    bid_agg = float(ai_company.ai_doctrine.get("bid_aggression", 0.65))
    k_promise = float(t["promise_sigma_k_base"]) + float(t["promise_sigma_k_risk_slope"]) * risk_tol

    estimates: Dict[str, Estimate] = {}
    promised: Dict[str, float] = {}
    for crit in prog.criteria:
        key = crit.key
        if crit.unit == "bool" or key == "carrier_suitability":
            cs = est_rep.get("carrier_suitability", {"suitable": True})
            b_val = 1.0 if (cs.get("suitable", True) if isinstance(cs, dict) else bool(cs)) else 0.0
            estimates[key] = Estimate(value=b_val, sigma=0.0, source="tunnel", unit="bool")
            promised[key] = 1.0 if prog.equipment.carrier_capable else b_val
            continue

        e_raw = est_rep.get(key)
        if isinstance(e_raw, Mapping):
            mu_e = float(e_raw["value"])
            sig_e = float(e_raw["sigma"])
            src_e = str(e_raw.get("source", "tunnel"))
        else:
            mu_e = float(nom_dict.get(key, crit.value))
            sig_e = 0.04 * abs(mu_e)
            src_e = "tunnel"

        estimates[key] = Estimate(value=mu_e, sigma=sig_e, source=src_e, unit=crit.unit)
        s_i = criterion_sign(crit.op)
        p_val = mu_e + s_i * k_promise * sig_e
        if s_i * (p_val - crit.value) < 0.0 and abs(mu_e - crit.value) / max(abs(crit.value), 1.0) <= 0.14:
            p_val = float(crit.value)
        promised[key] = p_val

    # Price & schedule formulation
    cust = prog.customer.upper()
    inc_bias = float(prog.politics.incumbent_bias.get(ai_company.id, 0.0))
    has_active_work = any(not c.completed for c in ai_company.company_state.contracts)
    markup = (
        float(t["price_markup_base"])
        - float(t["price_aggression_slope"]) * (bid_agg - 0.50)
        + (float(t["price_incumbent_premium"]) if inc_bias >= 0.25 else 0.0)
        - (float(t["price_desperation_discount"]) if not has_active_work else 0.0)
    )
    unit_est = float(est_rep.get("unit_flyaway_cost_usd", {}).get("value", nom_rep.unit_flyaway_cost_usd))
    dev_est = float(est_rep.get("dev_cost_usd_estimate", {}).get("value", nom_rep.dev_cost_usd_estimate))
    ceil_usd = float(prog.budget.unit_price_ceiling_usd)

    unit_bid = clamp(
        unit_est * markup,
        unit_est * float(t["price_floor_ratio_vs_estimate"]),
        ceil_usd * float(t["price_ceiling_safety_ratio"]),
    )
    if unit_bid > ceil_usd * 1.02:
        unit_bid = ceil_usd * clamp(markup, 0.86, 0.99)
    dev_bid = clamp(dev_est * markup, 0.75 * float(prog.budget.dev_usd), 1.12 * float(prog.budget.dev_usd))

    sched_buf = int(round(float(t["schedule_buffer_days_base"]) + float(t["schedule_buffer_risk_slope"]) * risk_tol))
    prom_ff_day = min(ff_due_day, max(prop_due_day + 150, ff_due_day - sched_buf))

    avail_pc = max(0.0, float(ai_company.company_state.political_capital) - float(t["lobby_pc_min_reserve"]))
    pc_spent = round(avail_pc * float(t["lobby_pc_spend_fraction"]), 2)

    guns_20mm = sum(int(g.get("count", 0)) for g in design["armament"]["guns"] if "20mm" in str(g.get("gun_id", "")))
    eq_prof = EquipmentProfile(
        carrier_capable=bool(design["structure"]["carrier_capable"]),
        radar_installed=design["systems"]["radar_id"] is not None,
        crew=int(design["crew_count"]),
        engines=int(design["propulsion"]["count"]),
        internal_bay=bool(design["armament"]["internal_bay"]),
        guns_20mm=guns_20mm,
        missile_capability=list(design["armament"]["missile_ids"]),
    )
    nov_prof = NoveltyProfile(
        unproven_tech_count=sum(1 for tid in design.get("techs_used", []) if ctx.tech_maturity.get(tid, 1.0) < 0.70),
        unflown_engine=False,
        unconventional_config=design["wing"]["planform_type"] == "delta",
    )

    bid = ProposalBid(
        bid_id=f"{prog.id}__{ai_company.id}",
        program_id=prog.id,
        company_id=ai_company.id,
        design_name=str(design["name"]),
        is_player=False,
        submitted_day=max(issue_day + 1, prop_due_day - 5),
        estimates=estimates,
        promised=promised,
        unit_price_bid_usd=unit_bid,
        unit_cost_estimate_usd=unit_est,
        dev_cost_bid_usd=dev_bid,
        dev_cost_estimate_usd=dev_est,
        promised_first_flight_day=prom_ff_day,
        promised_ioc_day=ioc_due_day,
        novelty=nov_prof,
        equipment=eq_prof,
        political_capital_spent=pc_spent,
    )
    bidder_ctx = BidderContext(
        company_id=ai_company.id,
        reputation_service=float(ai_company.reputation.get(cust, 60.0)),
        track_record=float(getattr(ai_company.company_state, "track_record", 0.55)),
        district_weight=0.45 if ai_company.tier in ("major_prime", "legacy_giant") else 0.30,
        active_contracts_same_role=sum(1 for c in ai_company.company_state.contracts if not c.completed),
        active_contracts_same_customer=1 if inc_bias >= 0.25 else 0,
        idle_factory_fraction=0.35,
    )
    sc = score_rfp_entry_for_ai(ai_company, prog, tuning=t_all)
    return AICompetitorEntry(
        program_id=prog.id,
        company_id=ai_company.id,
        company_name=ai_company.name,
        design_name=str(design["name"]),
        design=design,
        nominal_report=nom_rep,
        true_performance=true_rep,
        estimate_report=est_rep,
        lineage_state=lineage,
        bid=bid,
        bidder_context=bidder_ctx,
        entry_score=sc,
        pre_bid_tunnel_Sorting_run=True,
    )


def prepare_all_ai_entries_for_rfp(
    ai_companies: Union[Mapping[str, AICompanyState], Sequence[AICompanyState]],
    rfp: Union[ProgramSpec, Mapping[str, Any]],
    campaign_seed: int = 19450101,
    available_engines: Any = None,
    rng: Any = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> List[AICompetitorEntry]:
    """Select AI bidders for `rfp` and prepare their designs, pre-bid tunnel tests, and `ProposalBid`s."""
    selected = select_ai_bidders_for_rfp(ai_companies, rfp, tuning=tuning)
    entries: List[AICompetitorEntry] = []
    for comp, _ in selected:
        entry = prepare_ai_rfp_entry(
            ai_company=comp,
            rfp=rfp,
            campaign_seed=campaign_seed,
            available_engines=available_engines,
            rng=rng,
            tuning=tuning,
        )
        entries.append(entry)
    return entries


def run_ai_flyoff_progression(
    entry: AICompetitorEntry,
    rfp: Union[ProgramSpec, Mapping[str, Any]],
    ai_company: Optional[AICompanyState] = None,
    campaign_seed: int = 19450101,
    tuning: Optional[Dict[str, Any]] = None,
) -> AICompetitorEntry:
    """Execute Stage 2 (`flyoff`, Locked Decision D6) prototype rollout & flight testing for an AI finalist."""
    t_all = tuning if tuning is not None else load_ai_tuning()
    t = t_all["bidding_ai"]
    prog = _ensure_program_spec(rfp)

    n_proto = max(1, min(3, int(prog.acquisition.prototype_quantity_per_winner)))
    ctx = ai_company.tech_context() if ai_company is not None else None
    state = entry.lineage_state

    # Advance date to proposal downselect if needed
    prop_due_day = date_to_day(prog.proposal_due)
    ff_due_day = date_to_day(prog.first_flight_due)
    if state.date_day < prop_due_day:
        state.date_day = prop_due_day

    # 1. Build prototypes and perform rollout weighing update
    run_prototype_rollout(campaign_seed=campaign_seed, state=state, n_prototypes=n_proto)
    first_flight_day = state.date_day

    # 2. Choose flaw resolution policy based on remaining schedule margin before fly-off evaluation
    days_remaining = ff_due_day + 120 - state.date_day
    if days_remaining < int(t["flyoff_placard_days_remaining_threshold"]):
        policy = "placard_all"
    elif ai_company is not None and float(ai_company.ai_doctrine.get("risk_tolerance", 0.50)) <= 0.35:
        policy = "fix_all"
    else:
        policy = "fix_severe_else_placard"

    # 3. Execute flight-test syllabus
    flt_res = run_flight_test_programme(
        campaign_seed=campaign_seed,
        state=state,
        flaw_resolution_policy=policy,
        auto_replace_crashed_prototype=True,
        tech_ctx=ctx,
    )

    est_after = compute_estimate_report(state, tech_ctx=ctx)
    true_after = compute_true_performance_report(state)
    entry.estimate_report = est_after
    entry.true_performance = true_after

    measured: Dict[str, Estimate] = {}
    for crit in prog.criteria:
        key = crit.key
        if crit.unit == "bool" or key == "carrier_suitability":
            cs = true_after.get("carrier_suitability", {"suitable": True})
            b_val = 1.0 if (cs.get("suitable", True) if isinstance(cs, dict) else bool(cs)) else 0.0
            measured[key] = Estimate(value=b_val, sigma=0.0, source="flight", unit="bool")
            continue
        e_item = est_after.get(key)
        if isinstance(e_item, Mapping):
            measured[key] = Estimate(
                value=float(e_item["value"]),
                sigma=float(e_item["sigma"]),
                source="flight",
                unit=crit.unit,
            )
        else:
            v_t = float(true_after.get(key, entry.nominal_report.get(key, crit.value)))
            measured[key] = Estimate(value=v_t, sigma=0.015 * abs(v_t), source="flight", unit=crit.unit)

    unfixed_sev = sum(
        int(f.severity)
        for f in state.true_aircraft.active_flaws.values()
        if f.residual_factor >= 0.40 and f.status != "fixed"
    )

    entry.bid.measured_performance = measured
    entry.bid.actual_first_flight_day = first_flight_day
    entry.bid.unfixed_flaw_severity_sum = unfixed_sev
    entry.flyoff_completed = True
    entry.flyoff_flight_result = flt_res
    return entry


def step_all_ai_flyoff_finalists(
    entries: Sequence[AICompetitorEntry],
    rfp: Union[ProgramSpec, Mapping[str, Any]],
    ai_companies: Optional[Mapping[str, AICompanyState]] = None,
    finalist_company_ids: Optional[Sequence[str]] = None,
    campaign_seed: int = 19450101,
    tuning: Optional[Dict[str, Any]] = None,
) -> List[AICompetitorEntry]:
    """Run Stage 2 `flyoff` prototype and flight-test progression for all downselected AI finalists."""
    finalist_set = set(finalist_company_ids) if finalist_company_ids is not None else {e.company_id for e in entries}
    comp_map = ai_companies or {}
    updated: List[AICompetitorEntry] = []
    for entry in entries:
        if entry.company_id not in finalist_set and entry.bid.bid_id not in finalist_set:
            continue
        comp = comp_map.get(entry.company_id)
        updated.append(
            run_ai_flyoff_progression(
                entry=entry,
                rfp=rfp,
                ai_company=comp,
                campaign_seed=campaign_seed,
                tuning=tuning,
            )
        )
    return updated
