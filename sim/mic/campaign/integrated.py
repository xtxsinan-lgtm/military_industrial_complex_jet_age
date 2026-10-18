"""Full 1945-1960 Integrated Campaign Simulator (`IntegratedCampaignSim`).

Connects real physics/performance (`mic.perf`), technology research (`mic.tech`),
company economy (`mic.econ`), military procurement (`mic.procurement`), and
wind-tunnel/flight-test/hidden-flaw mechanics (`mic.testing`) across all 16
historical RFPs from 1945 to 1960.

Supports Locked Decision D6 (`force_flyoff: bool = True` by default, so all 16
programs run two-stage Proposal Downselect -> Prototype Build & Flight Test ->
Hardware Fly-Off Evaluation; also supports `force_flyoff=False` for historical
acquisition style comparison).
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
import json
import math
from typing import Any, Dict, List, Optional, Tuple

from mic.campaign.bots import CampaignBotArchetype, get_bot_by_id
from mic.campaign.macro import load_core_tuning
from mic.econ.company import CompanyState, step_company_month
from mic.econ.contracts import create_contract
from mic.econ.inflation import aero_cost_index_1950
from mic.econ.production import ProductionLine
from mic.econ.workforce import EngineeringProjectTask
from mic.perf.performance import PerformanceReport, evaluate as evaluate_performance
from mic.procurement.ai_competitor import generate_historical_program_bids
from mic.procurement.catalog import load_all_programs
from mic.procurement.dates import date_to_day, day_to_fractional_year
from mic.procurement.evaluation import (
    audit_milestone_promises,
    evaluate_flyoff,
    evaluate_proposals,
)
from mic.procurement.models import (
    BidderContext,
    EquipmentProfile,
    Estimate,
    NoveltyProfile,
    ProgramSpec,
    ProposalBid,
)
from mic.procurement.rng import RandomSource
from mic.procurement.scoring import criterion_sign
from mic.tech.catalog import TechCatalog, load_catalog
from mic.tech.research import (
    CompanyTechState,
    apply_learning_by_doing,
    compute_daily_active_progress,
    day_to_year,
    step_company_tech_day,
)
from mic.testing.flaws import get_flaw_catalog_map
from mic.testing.flight_test import run_flight_test_programme
from mic.testing.novelty import ExperienceLedger
from mic.testing.service import simulate_service_years
from mic.testing.sources import run_prototype_rollout, run_tunnel_or_ground_campaign
from mic.testing.truth import (
    LineageTestState,
    apply_flaw_fix_to_state,
    apply_flaw_placard_to_state,
    compute_estimate_report,
    compute_true_performance_report,
    initialize_lineage_state,
)

# Module-level physics evaluation cache for fast Monte-Carlo execution
_PERF_CACHE: Dict[str, PerformanceReport] = {}


def _evaluate_perf_cached(design: Dict[str, Any], tech_ctx: Any) -> PerformanceReport:
    """Evaluate `mic.perf.evaluate(design, tech_context=tech_ctx)` with deterministic caching."""
    design_For_key = {k: v for k, v in design.items() if k not in ("id", "name")}
    ctx_vals = getattr(tech_ctx, "values", {})
    key_str = json.dumps({"d": design_For_key, "t": ctx_vals}, sort_keys=True)
    if key_str not in _PERF_CACHE:
        _PERF_CACHE[key_str] = evaluate_performance(design, tech_context=tech_ctx)
    return _PERF_CACHE[key_str]


@dataclass
class ProgramCampaignOutcome:
    """Record of a single RFP's lifecycle outcome in `IntegratedCampaignSim`."""

    program_id: str
    program_name: str
    customer: str
    role: str
    issue_year: float
    acquisition_style: str
    player_submitted_bid: bool
    player_downselected: bool
    player_built_prototype: bool
    player_won_contract: bool
    proposal_outcome: str
    flyoff_outcome: str
    quantity_awarded: int
    unit_price_bid_usd: float
    crashes_in_test: int = 0
    pilots_lost_in_test: int = 0
    flaws_detected_count: int = 0
    flaws_fixed_count: int = 0
    unfixed_flaw_severity_at_flyoff: int = 0
    service_grounding_days: int = 0
    service_manifested_flaws: int = 0
    service_accidents: int = 0
    service_retrofit_cost_usd: float = 0.0
    reputation_delta_total: float = 0.0


@dataclass
class IntegratedCampaignResult:
    """Complete metrics and telemetry from a 1945-1960 `IntegratedCampaignSim` run."""

    seed: int
    bot_id: str
    bot_name: str
    force_flyoff: bool
    programs_total: int
    bids_submitted: int
    downselects_won: int
    contracts_won: int
    rfp_win_rate_of_bids: float
    rfp_win_rate_of_total: float
    aircraft_delivered: int
    ending_cash_usd: float
    ending_debt_usd: float
    ending_net_worth_nominal_usd: float
    ending_net_worth_1950_usd: float
    chapter_xi_triggered: bool
    is_bankrupt: bool
    prototype_crashes: int
    pilots_lost: int
    flaws_detected: int
    flaws_fixed: int
    service_grounding_events: int
    service_grounding_days: int
    service_squadron_accidents: int
    service_retrofit_cost_usd: float
    ending_reputation_usaf: float
    ending_reputation_usn: float
    ending_reputation_avg: float
    ending_track_record: float
    techs_unlocked_total: int
    techs_unlocked_beyond_start: int
    active_techs_unlocked: int
    final_score: float
    grade_letter: str
    grade_tier: str
    decisions_by_category: Dict[str, int] = field(default_factory=dict)
    decisions_by_year: Dict[int, int] = field(default_factory=dict)
    avg_decisions_per_year: float = 0.0
    program_outcomes: List[ProgramCampaignOutcome] = field(default_factory=list)


def _build_player_proposal_bid(
    program: ProgramSpec,
    company: CompanyState,
    design: Dict[str, Any],
    perf: PerformanceReport,
    est_report: Dict[str, Any],
    lineage_state: LineageTestState,
    bid_params: Dict[str, float],
    submitted_day: int,
) -> ProposalBid:
    """Construct a `ProposalBid` for the player/bot from `est_report` and `bid_params`."""
    estimates: Dict[str, Estimate] = {}
    promised: Dict[str, float] = {}
    p_z = float(bid_params.get("promise_z", 0.20))

    for crit in program.criteria:
        key = crit.key
        if crit.unit == "bool" or key == "carrier_suitability":
            cs = est_report.get("carrier_suitability", {"suitable": True})
            b_val = 1.0 if (isinstance(cs, dict) and cs.get("suitable", True)) else 0.0
            estimates[key] = Estimate(value=b_val, sigma=0.0, source="tunnel", unit="bool")
            promised[key] = b_val
            continue

        raw_est = est_report.get(key)
        if isinstance(raw_est, dict):
            mu = float(raw_est["value"])
            sig = float(raw_est["sigma"])
            src = str(raw_est.get("source", "sim"))
        else:
            mu = float(getattr(perf, key, crit.value))
            sig = 0.08 * abs(mu)
            src = "sim"

        estimates[key] = Estimate(value=mu, sigma=sig, source=src, unit=crit.unit)
        s_i = criterion_sign(crit.op)
        nom_val = float(getattr(perf, key, mu))
        raw_p = (0.55 * nom_val + 0.45 * mu) + s_i * p_z * sig
        # Ensure promised value meets threshold when nominal performance is within 8% of threshold
        if s_i * (raw_p - crit.value) < 0.0 and (
            abs(nom_val - crit.value) / max(abs(crit.value), 1.0) <= 0.08
        ):
            p_val = float(crit.value)
        else:
            p_val = raw_p
        promised[key] = p_val

    margin = float(bid_params.get("price_margin", 0.10))
    ceil_u = float(program.budget.unit_price_ceiling_usd)
    flyaway_est = float(perf.unit_flyaway_cost_usd)
    # Blend cost estimate with program ceiling scale and apply bot's target margin
    base_cost_ref = min(ceil_u * 0.75, max(ceil_u * 0.56, flyaway_est))
    unit_bid = round(base_cost_ref * (1.0 + margin), 2)
    dev_est = float(program.budget.dev_usd) * 0.84
    dev_bid = round(dev_est * (1.0 + 0.6 * margin), 2)

    ff_due = date_to_day(program.first_flight_due)
    ioc_due = date_to_day(program.ioc_due)
    sched_off = int(bid_params.get("schedule_offset_days", 0.0))
    promised_ff = max(submitted_day + 180, ff_due + sched_off)

    eq_req = program.equipment
    arm = design.get("armament", {})
    guns_list = arm.get("guns", [])
    guns_20 = sum(int(g.get("count", 0)) for g in guns_list if int(g.get("caliber_mm", 20)) >= 20)
    equip = EquipmentProfile(
        carrier_capable=bool(design.get("structure", {}).get("carrier_capable", eq_req.carrier_capable)),
        radar_installed=bool(design.get("systems", {}).get("radar_id") is not None or eq_req.radar_required),
        crew=int(design.get("crew_count", eq_req.min_crew)),
        engines=int(design.get("propulsion", {}).get("count", eq_req.min_engines)),
        internal_bay=bool(arm.get("internal_bay", eq_req.internal_bay_required)),
        guns_20mm=guns_20,
        missile_capability=list(arm.get("missile_ids", eq_req.missile_capability)),
    )
    nov = NoveltyProfile(
        unproven_tech_count=max(0, len(design.get("techs_used", [])) - 2),
        unflown_engine=False,
        unconventional_config=False,
    )

    return ProposalBid(
        bid_id=f"{program.id}__{company.id}",
        program_id=program.id,
        company_id=company.id,
        design_name=str(design.get("name", f"{company.id.upper()}-X")),
        is_player=True,
        submitted_day=submitted_day,
        estimates=estimates,
        promised=promised,
        unit_price_bid_usd=unit_bid,
        unit_cost_estimate_usd=base_cost_ref,
        dev_cost_bid_usd=dev_bid,
        dev_cost_estimate_usd=dev_est,
        promised_first_flight_day=promised_ff,
        promised_ioc_day=ioc_due + sched_off,
        novelty=nov,
        equipment=equip,
    )


def _populate_player_flyoff_measurements(
    program: ProgramSpec,
    bid: ProposalBid,
    lineage_state: LineageTestState,
    ledger: ExperienceLedger,
    tech_ctx: Any,
    ff_due_day: int,
    schedule_offset_days: int,
    crashes_in_test: int = 0,
) -> None:
    """Populate `bid.measured_performance`, `actual_first_flight_day`, and `unfixed_flaw_severity_sum` after flight test."""
    post_est = compute_estimate_report(lineage_state, ledger=ledger, tech_ctx=tech_ctx)
    true_rep = compute_true_performance_report(lineage_state)

    measured: Dict[str, Estimate] = {}
    for crit in program.criteria:
        key = crit.key
        if crit.unit == "bool" or key == "carrier_suitability":
            cs = true_rep.get("carrier_suitability", {"suitable": True})
            b_val = 1.0 if (isinstance(cs, dict) and cs.get("suitable", True)) else 0.0
            measured[key] = Estimate(value=b_val, sigma=0.0, source="flight", unit="bool")
            continue

        e_info = post_est.get(key)
        t_val = float(true_rep.get(key, bid.estimates[key].value))
        if isinstance(e_info, dict):
            sig = float(e_info["sigma"])
            src = str(e_info.get("source", "flight"))
        else:
            sig = 0.025 * abs(t_val)
            src = "flight"
        measured[key] = Estimate(value=t_val, sigma=sig, source=src, unit=crit.unit)

    bid.measured_performance = measured
    crash_delay = int(crashes_in_test) * 45
    rush_slip = max(0, -int(schedule_offset_days) - 25)
    bid.actual_first_flight_day = int(bid.promised_first_flight_day) - 5 + rush_slip + crash_delay

    unfixed_sev = 0
    for fstate in lineage_state.true_aircraft.active_flaws.values():
        if fstate.residual_factor > 0.35:
            unfixed_sev += int(fstate.severity)
    bid.unfixed_flaw_severity_sum = unfixed_sev


def _ensure_ai_finalists_have_flyoff_data(
    program: ProgramSpec,
    finalist_bids: List[ProposalBid],
    rng: RandomSource,
) -> None:
    """Ensure downselected AI finalists have prototype flight measurements when `force_flyoff=True` (Locked Decision D6)."""
    ff_due = date_to_day(program.first_flight_due)
    for b in finalist_bids:
        if b.is_player:
            continue
        if b.actual_first_flight_day is None:
            b.actual_first_flight_day = ff_due + int(round(rng.normal(-10.0, 25.0)))
        if not b.measured_performance:
            meas: Dict[str, Estimate] = {}
            for crit in program.criteria:
                est = b.estimates.get(crit.key)
                if est is None:
                    continue
                if crit.unit == "bool":
                    meas[crit.key] = Estimate(value=est.value, sigma=0.0, source="flight", unit="bool")
                else:
                    v_f = est.value * (1.0 + rng.normal(0.0, 0.025))
                    meas[crit.key] = Estimate(
                        value=v_f,
                        sigma=0.015 * max(abs(v_f), 1e-3),
                        source="flight",
                        unit=crit.unit,
                    )
            b.measured_performance = meas


class IntegratedCampaignSim:
    """Fast, deterministic 1945-1960 integrated campaign simulator across all 16 historical RFPs."""

    def __init__(
        self,
        seed: int = 42,
        bot: Optional[CampaignBotArchetype] = None,
        *,
        bot_id: str = "balanced_prime",
        force_flyoff: bool = True,
        company_profile_id: str = "medium_prime",
        company_id: str = "mcdonnell",
        difficulty: str = "normal",
    ) -> None:
        self.seed: int = int(seed)
        self.bot: CampaignBotArchetype = bot if bot is not None else get_bot_by_id(bot_id)
        self.force_flyoff: bool = bool(force_flyoff)
        self.company_id: str = str(company_id)
        self.difficulty: str = str(difficulty)

        self.core_tuning: Dict[str, Any] = load_core_tuning()
        self.tech_catalog: TechCatalog = load_catalog()
        self.programs: List[ProgramSpec] = sorted(
            load_all_programs(), key=lambda p: date_to_day(p.issue_date)
        )

        self.company: CompanyState = CompanyState.from_profile(
            profile_id=company_profile_id,
            company_id=self.company_id,
            name=f"{self.bot.name} Aero Corp.",
            is_player=True,
        )
        self.tech_state: CompanyTechState = CompanyTechState.create_starting_1945(
            company_id=self.company_id,
            date_day=0,
            catalog=self.tech_catalog,
        )
        self.start_tech_count: int = len(self.tech_state.unlocked_maturity)
        self.experience_ledger: ExperienceLedger = ExperienceLedger()
        self.proc_rng: RandomSource = RandomSource(source=self.seed ^ 0x5A17C9, deterministic=False)

        self.current_day: int = 0
        self.last_econ_month_seq: int = 1945 * 12 + 7  # Aug 1945 is month 8
        self.track_record: float = 0.55
        self.chapter_xi_ever_triggered: bool = False
        self.active_techs_unlocked: int = 0
        self.flaw_map: Dict[str, Dict[str, Any]] = get_flaw_catalog_map()

        self.decisions_by_category: Dict[str, int] = {
            "rd_allocation": 0,
            "rfp_design": 0,
            "wind_tunnel_booking": 0,
            "flight_test_phase": 0,
            "flaw_fix_decision": 0,
            "bid_submission": 0,
            "facility_and_finance": 0,
        }
        self.decisions_by_year: Dict[int, int] = {yr: 0 for yr in range(1945, 1961)}

    def _record_decision(self, category: str, day: int, count: int = 1) -> None:
        yr = min(1960, max(1945, int(math.floor(day_to_fractional_year(day)))))
        self.decisions_by_category[category] = self.decisions_by_category.get(category, 0) + count
        self.decisions_by_year[yr] = self.decisions_by_year.get(yr, 0) + count

    def _update_rd_allocations(self, day: int) -> None:
        year = day_to_fractional_year(day)
        alloc = self.bot.decide_rd_allocation(self.tech_state, self.company, year, self.tech_catalog)
        # Clear completed or unallocated projects
        for tid in list(self.tech_state.projects.keys()):
            if tid not in alloc and tid not in self.tech_state.unlocked_maturity:
                self.tech_state.projects[tid].assigned_engineers = 0
        for tid, eng_n in alloc.items():
            if self.tech_state.can_start_research(tid, self.tech_catalog):
                self.tech_state.start_or_update_project(
                    tid, assigned_engineers=eng_n, funding_mode="irad", catalog=self.tech_catalog
                )
        self.company.irad_monthly_spend_usd = (
            self.bot.irad_monthly_budget_1950_usd * aero_cost_index_1950(int(year))
        )
        if alloc:
            self._record_decision("rd_allocation", day, 1)

    def _step_tech_day_fast(self, dt: int = 1) -> List[str]:
        """Step tech research by `dt` days while avoiding redundant 75-node context rebuilds."""
        state = self.tech_state
        cat = self.tech_catalog
        t = cat.tunables
        date_day = state.date_day
        current_yr = day_to_year(date_day)
        ctx = state.context(catalog=cat)
        dt_f = float(dt)

        # 1. Passive maturity growth
        passive_mat_rate = t["passive_maturity_rate_per_day"] * dt_f
        max_mat = t["max_maturity"]
        if passive_mat_rate > 0.0:
            for tid in state.unlocked_maturity:
                old_m = state.unlocked_maturity[tid]
                if old_m < max_mat:
                    state.unlocked_maturity[tid] = min(max_mat, old_m + passive_mat_rate * (1.0 - old_m))

        progress_deltas: Dict[str, float] = {}
        active_progressed: set[str] = set()

        # 2. Active research projects
        for tid, proj in sorted(state.projects.items()):
            if tid in state.unlocked_maturity or proj.assigned_engineers <= 0:
                continue
            node = cat.get_node(tid)
            branch_bonus = state.designer_branch_bonuses.get(node.branch, 0.0)
            act_prog, comp_usd, govt_usd = compute_daily_active_progress(
                node=node,
                project=proj,
                date_day=date_day,
                ctx=ctx,
                designer_branch_bonus=branch_bonus,
                catalog=cat,
            )
            if act_prog > 0.0:
                step_prog = min(max(0.0, float(node.cost_eng_days) - proj.progress_eng_days), act_prog * dt_f)
                proj.progress_eng_days += step_prog
                proj.company_usd_spent += comp_usd * dt_f
                proj.govt_usd_spent += govt_usd * dt_f
                state.partial_progress[tid] = proj.progress_eng_days
                progress_deltas[tid] = progress_deltas.get(tid, 0.0) + step_prog
                active_progressed.add(tid)

        # 3. Passive NACA diffusion drip
        naca_lag = t["naca_diffusion_lag_years"]
        naca_drip_frac = t["naca_passive_drip_frac_per_day"] * dt_f
        if naca_drip_frac > 0.0:
            for tid, node in cat.nodes.items():
                if tid in state.unlocked_maturity or not node.naca_diffusion:
                    continue
                if current_yr < node.historical_year + naca_lag:
                    continue
                if not all(p in state.unlocked_maturity for p in node.prereqs):
                    continue
                cur_prog = state.projects[tid].progress_eng_days if tid in state.projects else state.partial_progress.get(tid, 0.0)
                drip = min(max(0.0, float(node.cost_eng_days) - cur_prog), naca_drip_frac * float(node.cost_eng_days))
                if drip > 0.0:
                    new_prog = cur_prog + drip
                    state.partial_progress[tid] = new_prog
                    if tid in state.projects:
                        state.projects[tid].progress_eng_days = new_prog
                    progress_deltas[tid] = progress_deltas.get(tid, 0.0) + drip

        # 4. Completions
        newly_unlocked: List[str] = []
        for tid in sorted(progress_deltas.keys()):
            node = cat.get_node(tid)
            prog = state.partial_progress.get(tid, 0.0)
            if prog + 1e-9 >= float(node.cost_eng_days):
                init_mat = node.initial_maturity if node.initial_maturity > 0.0 else t["default_unlock_maturity"]
                state.unlocked_maturity[tid] = init_mat
                if tid in active_progressed or (tid in state.projects and state.projects[tid].assigned_engineers > 0):
                    self.active_techs_unlocked += 1
                state.partial_progress.pop(tid, None)
                state.projects.pop(tid, None)
                newly_unlocked.append(tid)

        state.date_day += dt
        if newly_unlocked or (state.date_day % 30 < dt):
            state.invalidate_context()
        return newly_unlocked

    def _advance_to_day(self, target_day: int) -> None:
        """Advance tech research and monthly company economy up to `target_day`."""
        while self.current_day < target_day:
            if self.current_day == 0 or (self.current_day % 120 < 5):
                self._update_rd_allocations(self.current_day)

            dt = min(5, target_day - self.current_day)
            newly_unlocked = self._step_tech_day_fast(dt)
            if newly_unlocked:
                self.company.tech_unlocked = sorted(self.tech_state.unlocked_maturity.keys())
                self._update_rd_allocations(self.current_day)

            self.current_day += dt
            frac_yr = day_to_fractional_year(self.current_day)
            yr_int = int(math.floor(frac_yr))
            mo_int = min(12, max(1, int(math.floor((frac_yr - yr_int) * 12.0)) + 1))
            m_seq = yr_int * 12 + (mo_int - 1)

            while self.last_econ_month_seq < m_seq:
                self.last_econ_month_seq += 1
                ey = self.last_econ_month_seq // 12
                em = (self.last_econ_month_seq % 12) + 1
                m_rep = step_company_month(self.company, year=ey, month=em)
                if m_rep["chapter_xi_triggered"]:
                    self.chapter_xi_ever_triggered = True
                    self._record_decision("facility_and_finance", self.current_day, 1)
        self.tech_state.invalidate_context()


    def _build_bidder_context(self, program: ProgramSpec) -> BidderContext:
        active_same_role = sum(
            1 for c in self.company.contracts if not c.completed and c.phase == "production"
        )
        active_same_cust = sum(
            1 for c in self.company.contracts if not c.completed and c.customer == program.customer
        )
        rep_srv = float(self.company.reputation.get(program.customer, 60.0))
        return BidderContext(
            company_id=self.company_id,
            reputation_service=rep_srv,
            track_record=self.track_record,
            district_weight=0.38,
            active_contracts_same_role=min(2, active_same_role),
            active_contracts_same_customer=min(2, active_same_cust),
            idle_factory_fraction=0.35 if active_same_role == 0 else 0.15,
        )

    def _award_production_contract_and_service(
        self,
        program: ProgramSpec,
        player_bid: ProposalBid,
        lineage_state: LineageTestState,
        perf: PerformanceReport,
        qty_awarded: int,
        award_day: int,
    ) -> Tuple[int, int, int, float, float]:
        """Set up FPIF production contract + line, audit promises, and run service entry."""
        if qty_awarded <= 0:
            return 0, 0, 0, 0.0, 0.0

        est_prod_cost = float(player_bid.unit_cost_estimate_usd) * qty_awarded
        fpif_con = create_contract(
            contract_id=f"fpif__{program.id}",
            program_id=program.id,
            customer=program.customer,
            contract_type="FPIF",
            phase="production",
            estimated_cost_usd=est_prod_cost,
            quantity=qty_awarded,
            fee_or_profit_rate=max(0.06, min(0.15, self.bot.price_margin)),
            gfe_provided=True,
        )
        self.company.contracts.append(fpif_con)

        # Lease GOCO floor if factory capacity is tight
        if len([l for l in self.company.aircraft_in_production if not l.completed]) >= 2:
            self.company.facilities["goco_floor_m2"] = float(self.company.facilities.get("goco_floor_m2", 0.0)) + 25000.0
            self._record_decision("facility_and_finance", award_day, 1)

        target_rate = max(6.0, min(22.0, qty_awarded / 30.0))
        line = ProductionLine(
            line_id=f"line__{program.id}",
            design_id=str(lineage_state.design["id"]),
            contract_id=fpif_con.contract_id,
            airframe_mass_lb=max(6000.0, float(perf.empty_mass_kg) * 2.20462),
            t1_airframe_cost_usd=float(player_bid.unit_cost_estimate_usd) * 1.45,
            gfe_unit_cost_usd=float(player_bid.unit_cost_estimate_usd) * 0.22,
            learning_curve_rate=float(self.tech_state.context(self.tech_catalog).get("mfg.learning_curve_rate")),
            target_rate_per_month=target_rate,
            current_rate_per_month=max(3.0, target_rate * 0.45),
            tooling_rate_cap_per_month=target_rate * 1.25,
            total_quantity_ordered=qty_awarded,
            scheduled_months=32,
        )
        self.company.aircraft_in_production.append(line)
        self._record_decision("facility_and_finance", award_day, 1)

        # Promise audit at IOC
        true_rep = compute_true_performance_report(lineage_state)
        actual_perf = {
            c.key: (1.0 if true_rep.get("carrier_suitability", {}).get("suitable", True) else 0.0)
            if c.unit == "bool"
            else float(true_rep.get(c.key, c.value))
            for c in program.criteria
        }
        from mic.procurement.evaluation import create_contract_from_award

        proc_contract = create_contract_from_award(program, player_bid, award_day, quantity_override=qty_awarded)
        audit = audit_milestone_promises(
            program=program,
            contract=proc_contract,
            actual_performance=actual_perf,
            actual_milestone_day=int(player_bid.actual_first_flight_day or award_day),
            current_track_record=self.track_record,
            milestone="first_flight",
        )
        self.track_record = audit.new_track_record

        # Simulate squadron service entry (3 years)
        srv = simulate_service_years(
            campaign_seed=self.seed,
            state=lineage_state,
            years=3,
            max_fleet_size=min(240, qty_awarded),
            ledger=self.experience_ledger,
        )
        g_days = int(srv["total_grounding_days"])
        for fid in srv["manifested_flaws"]:
            fstate = lineage_state.true_aircraft.active_flaws.get(fid)
            if fstate is not None and fstate.residual_factor > 0.35 and fstate.severity == 3:
                g_days += int(self.flaw_map[fid]["service_hazard"].get("grounding_days", 20))
        man_flaws = len(srv["manifested_flaws"])
        acc = int(srv["total_squadron_accidents"])
        retro_usd = float(srv["total_retrofit_cost_usd"])
        srv_bonus = 6.5 if (g_days == 0 and acc == 0 and man_flaws == 0) else (3.5 if g_days == 0 else -4.0)
        rep_delta = float(audit.reputation_delta_total) + float(srv["total_reputation_delta"]) + srv_bonus

        self.company.cash_usd -= retro_usd
        cur_rep = float(self.company.reputation.get(program.customer, 60.0))
        self.company.reputation[program.customer] = max(5.0, min(100.0, cur_rep + rep_delta))
        apply_learning_by_doing(
            self.tech_state,
            lineage_state.design.get("techs_used", []),
            "production_10_units",
            scale=min(5.0, qty_awarded / 50.0),
            catalog=self.tech_catalog,
        )
        return g_days, man_flaws, acc, retro_usd, rep_delta


    def run(self) -> IntegratedCampaignResult:
        """Execute the full 1945-1960 campaign across all 16 historical RFPs."""
        outcomes: List[ProgramCampaignOutcome] = []
        bids_submitted = 0
        downselects_won = 0
        contracts_won = 0
        total_crashes = 0
        total_pilots_lost = 0
        total_flaws_detected = 0
        total_flaws_fixed = 0
        total_grounding_events = 0
        total_grounding_days = 0
        total_service_accidents = 0
        total_retrofit_usd = 0.0

        for orig_prog in self.programs:
            prog = copy.deepcopy(orig_prog)
            if self.force_flyoff:
                prog.acquisition.style = "flyoff"
                prog.acquisition.downselect_count = max(2, int(prog.acquisition.downselect_count))

            issue_day = max(0, date_to_day(prog.issue_date))
            prop_due_day = max(issue_day + 30, date_to_day(prog.proposal_due))
            ff_due_day = max(prop_due_day + 90, date_to_day(prog.first_flight_due))

            if issue_day > self.current_day:
                self._advance_to_day(issue_day)

            issue_yr = day_to_fractional_year(issue_day)
            if not self.bot.should_bid_on_program(prog, self.tech_state, self.company, issue_yr):
                outcomes.append(
                    ProgramCampaignOutcome(
                        program_id=prog.id,
                        program_name=prog.program_name,
                        customer=prog.customer,
                        role=prog.role,
                        issue_year=issue_yr,
                        acquisition_style=prog.acquisition.style,
                        player_submitted_bid=False,
                        player_downselected=False,
                        player_built_prototype=False,
                        player_won_contract=False,
                        proposal_outcome="skipped_by_player",
                        flyoff_outcome="n/a",
                        quantity_awarded=0,
                        unit_price_bid_usd=0.0,
                    )
                )
                continue

            # 1. Design aircraft & evaluate nominal physics
            design = self.bot.design_aircraft_for_rfp(prog, self.tech_state, self.company, issue_yr)
            self._record_decision("rfp_design", issue_day, 1)
            ctx = self.tech_state.context(self.tech_catalog)
            perf = _evaluate_perf_cached(design, ctx)
            apply_learning_by_doing(
                self.tech_state, design.get("techs_used", []), "sim_run", catalog=self.tech_catalog
            )

            # 2. Initialize lineage state & run wind-tunnel / ground campaigns
            lineage = initialize_lineage_state(
                campaign_seed=self.seed,
                design=design,
                nominal_perf=perf.to_dict(),
                date_day=issue_day,
                aero_diagnostics=perf.aero_diagnostics,
                tech_ctx=ctx,
                ledger=self.experience_ledger,
            )
            wt_camps = self.bot.select_wind_tunnel_campaigns(prog, design, self.tech_state, self.company)
            syllabus_plan, flaw_policy = self.bot.select_flight_test_plan(prog, design, self.tech_state)
            flaws_fixed_this_prog = 0

            for camp_id, prov_id, depth in wt_camps:
                try:
                    wt_res = run_tunnel_or_ground_campaign(
                        campaign_seed=self.seed,
                        state=lineage,
                        campaign_id=camp_id,
                        provider_id=prov_id,
                        depth=depth,
                        active_military_contract=True,
                        own_wind_tunnel_level=int(self.company.facilities.get("wind_tunnel_level", 1)),
                        auto_fix_detected_flaws=False,
                        tech_ctx=ctx,
                        ledger=self.experience_ledger,
                    )
                    self._record_decision("wind_tunnel_booking", issue_day + 10, 1)
                    self.company.cash_usd -= float(wt_res["total_cost_usd"])
                    for fid in wt_res["detected_flaws"]:
                        self._record_decision("flaw_fix_decision", issue_day + 20, 1)
                        fstate = lineage.true_aircraft.active_flaws[fid]
                        if flaw_policy == "fix_all" or (flaw_policy == "fix_severe_else_placard" and fstate.severity >= 3):
                            fx = apply_flaw_fix_to_state(lineage, fid, phase="design")
                            self.company.cash_usd -= float(fx["total_cost_usd"])
                            flaws_fixed_this_prog += 1
                        elif flaw_policy != "ignore":
                            apply_flaw_placard_to_state(lineage, fid)
                except (KeyError, ValueError):
                    continue

            # 3. Advance to proposal due date & evaluate proposals
            if prop_due_day > self.current_day:
                self._advance_to_day(prop_due_day)

            est_rep = compute_estimate_report(lineage, ledger=self.experience_ledger, tech_ctx=ctx)
            bid_params = self.bot.formulate_bid_parameters(prog, lineage, self.company)
            player_bid = _build_player_proposal_bid(
                prog, self.company, design, perf, est_rep, lineage, bid_params, prop_due_day - 5
            )
            self._record_decision("bid_submission", prop_due_day - 5, 1)
            bids_submitted += 1

            ai_bids, ai_bidders = generate_historical_program_bids(
                prog, exclude_company_ids=[self.company_id], rng=self.proc_rng
            )
            all_bids = ai_bids + [player_bid]
            all_bidders = dict(ai_bidders)
            all_bidders[self.company_id] = self._build_bidder_context(prog)

            prop_eval = evaluate_proposals(prog, all_bids, all_bidders, rng=self.proc_rng)
            is_downselected = player_bid.bid_id in prop_eval.finalist_bid_ids
            is_paper_winner = (
                prop_eval.outcome == "awarded" and player_bid.bid_id in prop_eval.winner_bid_ids
            )
            if is_downselected:
                downselects_won += 1

            built_proto = False
            won_contract = False
            qty_awarded = 0
            fly_outcome = "not_finalist"
            crashes_p = 0
            pilots_lost_p = 0
            g_days = 0
            man_flaws = 0
            srv_acc = 0
            retro_usd = 0.0
            rep_delta = 0.0

            if is_downselected or is_paper_winner:
                # Award CPFF RDT&E prototype contract when downselected in flyoff mode
                if prog.acquisition.style == "flyoff":
                    cpff = create_contract(
                        contract_id=f"cpff__{prog.id}",
                        program_id=prog.id,
                        customer=prog.customer,
                        contract_type="CPFF",
                        phase="rdte",
                        estimated_cost_usd=float(player_bid.dev_cost_bid_usd) * 0.45,
                        quantity=2,
                    )
                    self.company.contracts.append(cpff)
                    self.company.projects.append(
                        EngineeringProjectTask(
                            project_id=f"proj__{prog.id}",
                            name=f"{prog.program_name} Prototype",
                            kind="prototype",
                            contract_id=cpff.contract_id,
                            total_hours_required=65000.0,
                            allocated_engineers={"aero": 25.0, "structures": 35.0, "propulsion": 12.0, "systems": 18.0},
                        )
                    )

                # Build prototypes & run flight test syllabus
                built_proto = True
                roll_res = run_prototype_rollout(campaign_seed=self.seed, state=lineage, n_prototypes=2)
                self.company.cash_usd -= float(roll_res["proto_cost_usd"]) * 0.25
                self._record_decision("flight_test_phase", prop_due_day + 60, len(syllabus_plan))

                ft_res = run_flight_test_programme(
                    campaign_seed=self.seed,
                    state=lineage,
                    syllabus_plan=syllabus_plan,
                    pilots=self.bot.get_test_pilots(),
                    flaw_resolution_policy=flaw_policy,
                    auto_replace_crashed_prototype=True,
                    tech_ctx=self.tech_state.context(self.tech_catalog),
                    ledger=self.experience_ledger,
                )
                crashes_p = int(ft_res.crashes)
                pilots_lost_p = int(ft_res.pilots_lost)
                flaws_fixed_this_prog += len(ft_res.fixes_applied_in_flight)
                self._record_decision("flaw_fix_decision", prop_due_day + 120, len(ft_res.flaws_detected_in_flight))
                self.company.cash_usd -= float(ft_res.flight_test_cost_usd) * 0.35
                if crashes_p > 0:
                    self.company.cash_usd -= float(roll_res["proto_cost_usd"]) * 0.45 * crashes_p

                _populate_player_flyoff_measurements(
                    prog,
                    player_bid,
                    lineage,
                    self.experience_ledger,
                    self.tech_state.context(self.tech_catalog),
                    ff_due_day,
                    int(bid_params.get("schedule_offset_days", 0.0)),
                    crashes_in_test=crashes_p,
                )

                if prog.acquisition.style == "flyoff":
                    finalist_bids = [b for b in all_bids if b.bid_id in prop_eval.finalist_bid_ids]
                    _ensure_ai_finalists_have_flyoff_data(prog, finalist_bids, self.proc_rng)
                    fly_eval = evaluate_flyoff(prog, finalist_bids, all_bidders, rng=self.proc_rng)
                    fly_outcome = fly_eval.outcome
                    if player_bid.bid_id in fly_eval.winner_bid_ids and fly_eval.outcome not in ("cancelled_after_flyoff", "no_responsive_bid"):
                        won_contract = True
                        qty_awarded = int(fly_eval.quantity_splits.get(player_bid.bid_id, prog.budget.quantity_planned))
                else:
                    fly_outcome = "paper_award_direct"
                    if is_paper_winner:
                        won_contract = True
                        qty_awarded = int(prop_eval.quantity_splits.get(player_bid.bid_id, prog.budget.quantity_planned))

                if won_contract and qty_awarded > 0:
                    contracts_won += 1
                    g_days, man_flaws, srv_acc, retro_usd, rep_delta = self._award_production_contract_and_service(
                        prog, player_bid, lineage, perf, qty_awarded, ff_due_day
                    )
                    if g_days > 0:
                        total_grounding_events += 1

            total_crashes += crashes_p
            total_pilots_lost += pilots_lost_p
            det_cnt = sum(1 for f in lineage.true_aircraft.active_flaws.values() if f.detected)
            total_flaws_detected += det_cnt
            total_flaws_fixed += flaws_fixed_this_prog
            total_grounding_days += g_days
            total_service_accidents += srv_acc
            total_retrofit_usd += retro_usd

            outcomes.append(
                ProgramCampaignOutcome(
                    program_id=prog.id,
                    program_name=prog.program_name,
                    customer=prog.customer,
                    role=prog.role,
                    issue_year=issue_yr,
                    acquisition_style=prog.acquisition.style,
                    player_submitted_bid=True,
                    player_downselected=is_downselected,
                    player_built_prototype=built_proto,
                    player_won_contract=won_contract,
                    proposal_outcome=prop_eval.outcome,
                    flyoff_outcome=fly_outcome,
                    quantity_awarded=qty_awarded,
                    unit_price_bid_usd=player_bid.unit_price_bid_usd,
                    crashes_in_test=crashes_p,
                    pilots_lost_in_test=pilots_lost_p,
                    flaws_detected_count=det_cnt,
                    flaws_fixed_count=flaws_fixed_this_prog,
                    unfixed_flaw_severity_at_flyoff=player_bid.unfixed_flaw_severity_sum,
                    service_grounding_days=g_days,
                    service_manifested_flaws=man_flaws,
                    service_accidents=srv_acc,
                    service_retrofit_cost_usd=retro_usd,
                    reputation_delta_total=rep_delta,
                )
            )

        # Advance to end of campaign: 1960-12-31 (day 5618)
        self._advance_to_day(5618)
        return self._build_final_result(
            outcomes=outcomes,
            bids_submitted=bids_submitted,
            downselects_won=downselects_won,
            contracts_won=contracts_won,
            total_crashes=total_crashes,
            total_pilots_lost=total_pilots_lost,
            total_flaws_detected=total_flaws_detected,
            total_flaws_fixed=total_flaws_fixed,
            total_grounding_events=total_grounding_events,
            total_grounding_days=total_grounding_days,
            total_service_accidents=total_service_accidents,
            total_retrofit_usd=total_retrofit_usd,
        )


    def _build_final_result(
        self,
        *,
        outcomes: List[ProgramCampaignOutcome],
        bids_submitted: int,
        downselects_won: int,
        contracts_won: int,
        total_crashes: int,
        total_pilots_lost: int,
        total_flaws_detected: int,
        total_flaws_fixed: int,
        total_grounding_events: int,
        total_grounding_days: int,
        total_service_accidents: int,
        total_retrofit_usd: float,
    ) -> IntegratedCampaignResult:
        nw_nom = float(self.company.cash_usd - self.company.debt_usd + self.company.plant_property_value_usd)
        idx_1960 = aero_cost_index_1950(1960)
        nw_1950 = nw_nom / max(1.0, idx_1960)

        delivered = sum(int(l.cumulative_units_built) for l in self.company.aircraft_in_production)
        rep_usaf = float(self.company.reputation.get("USAF", 60.0))
        rep_usn = float(self.company.reputation.get("USN", 60.0))
        rep_exp = float(self.company.reputation.get("export", 45.0))
        rep_avg = (rep_usaf + rep_usn + rep_exp) / 3.0

        techs_total = len(self.tech_state.unlocked_maturity)
        techs_beyond = max(0, techs_total - self.start_tech_count)

        sc_cfg = self.core_tuning["scoring"]
        weights = sc_cfg["weights"]
        thresholds = sc_cfg["grade_thresholds"]

        nw_pts = min(280.0, max(0.0, nw_1950 / 180000.0))
        deliv_pts = min(260.0, delivered * 0.14)
        ct_pts = contracts_won * float(weights["prime_contract_won_points"])
        rep_pts = (rep_avg / 100.0) * float(weights["reputation_avg_points_full"])
        t_pts = self.active_techs_unlocked * 6.5
        safety_pen = total_crashes * 16.0 + total_grounding_days * 1.2
        final_score = max(0.0, nw_pts + deliv_pts + ct_pts + rep_pts + t_pts - safety_pen)
        if self.company.is_bankrupt_or_acquired:
            final_score *= 0.35

        grade_tier = thresholds[-1]["tier"]
        for row in thresholds:
            if final_score >= float(row["min_score"]):
                grade_tier = str(row["tier"])
                break

        if self.company.is_bankrupt_or_acquired or final_score < 250.0:
            grade_letter = "F"
        elif final_score >= 850.0:
            grade_letter = "A+"
        elif final_score >= 650.0:
            grade_letter = "A"
        elif final_score >= 450.0:
            grade_letter = "B"
        elif final_score >= 320.0:
            grade_letter = "C"
        else:
            grade_letter = "D"

        total_decisions = sum(self.decisions_by_category.values())
        # Campaign spans 15.38 years (Aug 1945 to Dec 1960)
        avg_dec_per_yr = total_decisions / 15.38

        return IntegratedCampaignResult(
            seed=self.seed,
            bot_id=self.bot.bot_id,
            bot_name=self.bot.name,
            force_flyoff=self.force_flyoff,
            programs_total=len(self.programs),
            bids_submitted=bids_submitted,
            downselects_won=downselects_won,
            contracts_won=contracts_won,
            rfp_win_rate_of_bids=contracts_won / max(1, bids_submitted),
            rfp_win_rate_of_total=contracts_won / max(1, len(self.programs)),
            aircraft_delivered=delivered,
            ending_cash_usd=float(self.company.cash_usd),
            ending_debt_usd=float(self.company.debt_usd),
            ending_net_worth_nominal_usd=nw_nom,
            ending_net_worth_1950_usd=nw_1950,
            chapter_xi_triggered=self.chapter_xi_ever_triggered,
            is_bankrupt=bool(self.company.is_bankrupt_or_acquired),
            prototype_crashes=total_crashes,
            pilots_lost=total_pilots_lost,
            flaws_detected=total_flaws_detected,
            flaws_fixed=total_flaws_fixed,
            service_grounding_events=total_grounding_events,
            service_grounding_days=total_grounding_days,
            service_squadron_accidents=total_service_accidents,
            service_retrofit_cost_usd=total_retrofit_usd,
            ending_reputation_usaf=rep_usaf,
            ending_reputation_usn=rep_usn,
            ending_reputation_avg=rep_avg,
            ending_track_record=self.track_record,
            techs_unlocked_total=techs_total,
            techs_unlocked_beyond_start=techs_beyond,
            active_techs_unlocked=self.active_techs_unlocked,
            final_score=round(final_score, 2),
            grade_letter=grade_letter,
            grade_tier=grade_tier,
            decisions_by_category=dict(self.decisions_by_category),
            decisions_by_year=dict(self.decisions_by_year),
            avg_decisions_per_year=round(avg_dec_per_yr, 2),
            program_outcomes=outcomes,
        )


def run_integrated_campaign(
    seed: int = 42,
    bot: Optional[CampaignBotArchetype] = None,
    *,
    bot_id: str = "balanced_prime",
    force_flyoff: bool = True,
    company_profile_id: str = "medium_prime",
    company_id: str = "mcdonnell",
) -> IntegratedCampaignResult:
    """Convenience entrypoint to run one deterministic 1945-1960 integrated campaign."""
    sim = IntegratedCampaignSim(
        seed=seed,
        bot=bot,
        bot_id=bot_id,
        force_flyoff=force_flyoff,
        company_profile_id=company_profile_id,
        company_id=company_id,
    )
    return sim.run()
