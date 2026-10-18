"""Authoritative `CompanyState` (§4.6) and daily/monthly settlement engine for Module 04."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from .contracts import (
    DefenseContract,
    compute_overhead_and_irad_recovery,
    compute_renegotiation_act_clawback,
    step_contract_month,
)
from .finance import (
    apply_chapter_xi_reorganization,
    compute_borrowing_limits_and_rates,
    compute_commercial_buffer_month,
    evaluate_credit_rating,
)
from .inflation import aero_cost_index_1950, benchmark_mfg_wage_usd_hr
from .politics import spend_political_capital, step_political_capital_month
from .production import (
    ProductionLine,
    compute_monthly_spares_and_mods,
    step_production_line_month,
)
from .tuning import load_econ_tuning
from .workforce import (
    DISCIPLINES,
    EngineeringProjectTask,
    compute_project_monthly_hours,
    step_workforce_month,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_PROFILES_PATH = _REPO_ROOT / "sim" / "data" / "economy" / "company_start_profiles.json"


@dataclass
class CompanyState:
    """Canonical company state conforming to `docs/spec/00_conventions.md` §4.6."""

    id: str
    name: str
    is_player: bool = True
    cash_usd: float = 16000000.0
    debt_usd: float = 0.0
    reputation: Dict[str, float] = field(
        default_factory=lambda: {"USAF": 60.0, "USN": 60.0, "export": 45.0}
    )
    political_capital: float = 35.0
    engineers: Dict[str, float] = field(
        default_factory=lambda: {"aero": 115.0, "structures": 145.0, "propulsion": 45.0, "systems": 75.0}
    )
    facilities: Dict[str, Any] = field(
        default_factory=lambda: {
            "wind_tunnel_level": 2,
            "factory_floor_m2": 65000.0,
            "goco_floor_m2": 0.0,
            "test_site": True,
            "nc_machining_installed": False,
        }
    )
    projects: List[EngineeringProjectTask] = field(default_factory=list)
    aircraft_in_production: List[ProductionLine] = field(default_factory=list)
    tech_unlocked: List[str] = field(default_factory=list)

    # Extended Module 04 operational & financial state
    contracts: List[DefenseContract] = field(default_factory=list)
    credit_rating: str = "A"
    commercial_buffer_level: str = "subcontracting"  # none | subcontracting | civil_diversified
    salary_multiplier: float = 1.0
    morale: float = 1.0
    recent_hire_fraction: float = 0.0
    lobbying_monthly_spend_usd: float = 0.0
    irad_monthly_spend_usd: float = 0.0
    active_delivered_fleet: int = 450
    avg_fleet_airframe_value_1950_usd: float = 150000.0
    consecutive_insolvent_months: int = 0
    chapter_xi_used: bool = False
    is_bankrupt_or_acquired: bool = False
    ytd_defense_revenue_usd: float = 0.0
    ytd_defense_cost_usd: float = 0.0
    ytd_operating_profit_usd: float = 0.0
    tax_loss_carryforward_usd: float = 0.0
    cost_efficiency_factor: float = 1.0

    @classmethod
    def from_profile(
        cls,
        profile_id: str = "medium_prime",
        company_id: str = "player_co",
        name: str = "Player Aviation Corp.",
        is_player: bool = True,
        path: Optional[Path] = None,
    ) -> "CompanyState":
        """Create a `CompanyState` from `sim/data/economy/company_start_profiles.json`."""
        p_file = path if path is not None else _PROFILES_PATH
        with open(p_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)["profiles"]
        prof = data[profile_id]
        return cls(
            id=company_id,
            name=name,
            is_player=is_player,
            cash_usd=float(prof["cash_usd"]),
            debt_usd=float(prof["debt_usd"]),
            credit_rating=str(prof["credit_rating"]),
            reputation=dict(prof["reputation"]),
            political_capital=float(prof["political_capital"]),
            engineers=dict(prof["engineers"]),
            facilities=dict(prof["facilities"]),
            commercial_buffer_level=str(prof["commercial_buffer_level"]),
            active_delivered_fleet=int(prof["active_delivered_fleet"]),
        )

    @property
    def total_engineers_fte(self) -> float:
        return float(sum(max(0.0, float(v)) for v in self.engineers.values()))

    @property
    def total_factory_floor_m2(self) -> float:
        return float(self.facilities.get("factory_floor_m2", 0.0)) + float(self.facilities.get("goco_floor_m2", 0.0))

    @property
    def plant_property_value_usd(self) -> float:
        cfg = load_econ_tuning()["production"]
        owned_m2 = float(self.facilities.get("factory_floor_m2", 0.0))
        wt_lvl = int(self.facilities.get("wind_tunnel_level", 0))
        wt_val_map = {0: 0.0, 1: 650000.0, 2: 1850000.0, 3: 4200000.0, 4: 7800000.0}
        return float(owned_m2 * float(cfg["factory_expansion_cost_1950_usd_per_m2"]) * 0.70 + wt_val_map.get(wt_lvl, 0.0))

    @property
    def total_backlog_usd(self) -> float:
        return float(sum(c.remaining_backlog_usd for c in self.contracts if not c.completed))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def step_company_day(
    company: CompanyState,
    date_day: int = 0,
    days_in_month: int = 30,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    """Advance daily engineering project progress (per `00_conventions.md` §3: projects progress daily)."""
    total_daily_hours = 0.0
    for proj in company.projects:
        if proj.completed:
            continue
        res = compute_project_monthly_hours(
            proj.allocated_engineers,
            project_kind=proj.kind,
            required_shares=proj.required_shares,
            morale=company.morale,
            newly_hired_fraction=company.recent_hire_fraction,
            tuning=tuning,
        )
        daily_hrs = res["effective_hours"] / max(1.0, float(days_in_month))
        proj.hours_completed = min(proj.total_hours_required, proj.hours_completed + daily_hrs)
        if proj.hours_completed >= proj.total_hours_required:
            proj.completed = True
        total_daily_hours += daily_hrs
    return {"daily_effective_engineering_hours": float(total_daily_hours)}


def step_company_month(
    company: CompanyState,
    year: int,
    month: int,
    target_engineers: Optional[Mapping[str, float]] = None,
    advance_projects_in_month: bool = True,
    auto_borrow_revolver: bool = True,
    allow_chapter_xi: bool = True,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute monthly economic settlement on the 1st of the month (per `00_conventions.md` §3).

    Settles:
    1. Engineering workforce payroll, hiring/layoffs, attrition, morale, and project progress.
    2. Production lines (Wright learning curve, Anderlohr break loss, factory floor allocation).
    3. Facility upkeep, GOCO lease, fixed G&A overhead, and ASPR Section XV overhead/IR&D recovery.
    4. Defense contract billings (CPFF, FPIF, FFP, Letter), progress payments, and liquidations.
    5. Spares, modifications, and baseline commercial/subcontracting revenue buffer.
    6. Debt interest, credit rating update, automatic revolving credit draw/repay, and liquidity check.
    7. Year-end (month == 12) Renegotiation Act of 1951 review and corporate income tax settlement.
    """
    cfg = tuning if tuning is not None else load_econ_tuning()
    idx_aero = aero_cost_index_1950(year)

    # 1. Engineering workforce step
    wf_res = step_workforce_month(
        company.engineers,
        target_engineers=target_engineers,
        year=year,
        salary_multiplier=company.salary_multiplier,
        morale=company.morale,
        recent_hire_fraction=company.recent_hire_fraction,
        tuning=cfg,
    )
    company.morale = wf_res["morale"]
    company.recent_hire_fraction = wf_res["recent_hire_fraction"]

    # Map engineering costs to contracts vs IR&D vs idle pool
    contract_map: Dict[str, DefenseContract] = {c.contract_id: c for c in company.contracts}
    contract_direct_cost_this_month: Dict[str, float] = {c.contract_id: 0.0 for c in company.contracts}
    contract_units_this_month: Dict[str, int] = {c.contract_id: 0 for c in company.contracts}
    contract_late_months: Dict[str, int] = {c.contract_id: 0 for c in company.contracts}
    contract_final_done: Dict[str, bool] = {c.contract_id: False for c in company.contracts}

    allocated_fte_total = 0.0
    irad_project_payroll_usd = 0.0
    sal_per_fte = wf_res["monthly_salary_per_fte_usd"]

    for proj in company.projects:
        was_completed = proj.completed
        proj_fte = sum(max(0.0, float(proj.allocated_engineers.get(d, 0.0))) for d in DISCIPLINES)
        if was_completed or proj_fte <= 1e-6:
            continue
        allocated_fte_total += proj_fte
        if advance_projects_in_month:
            p_res = compute_project_monthly_hours(
                proj.allocated_engineers,
                project_kind=proj.kind,
                required_shares=proj.required_shares,
                morale=company.morale,
                newly_hired_fraction=company.recent_hire_fraction,
                tuning=cfg,
            )
            proj.hours_completed = min(proj.total_hours_required, proj.hours_completed + p_res["effective_hours"])
            if proj.hours_completed >= proj.total_hours_required:
                proj.completed = True

        proj_direct_usd = proj_fte * sal_per_fte
        if proj.contract_id and proj.contract_id in contract_direct_cost_this_month:
            contract_direct_cost_this_month[proj.contract_id] += proj_direct_usd
            if proj.completed:
                contract_final_done[proj.contract_id] = True
        else:
            irad_project_payroll_usd += proj_direct_usd

    idle_fte = max(0.0, company.total_engineers_fte - allocated_fte_total)
    idle_eng_payroll_usd = idle_fte * sal_per_fte

    # 2. Commercial buffer & available factory floor
    comm_res = compute_commercial_buffer_month(company.commercial_buffer_level, year, tuning=cfg)
    avail_floor_m2 = max(0.0, company.total_factory_floor_m2 - comm_res["commercial_floor_committed_m2"])

    # 3. Production lines step
    total_mfg_cost_usd = 0.0
    total_idle_line_cost_usd = 0.0
    new_units_delivered = 0

    for line in company.aircraft_in_production:
        if line.completed:
            continue
        l_res = step_production_line_month(line, avail_floor_m2, year, tuning=cfg)
        avail_floor_m2 = max(0.0, avail_floor_m2 - l_res["floor_used_m2"])
        units = l_res["units_built"]
        mfg_cost = l_res["airframe_mfg_cost_usd"]
        # Add GFE cost only if contract does NOT provide GFE free of charge
        if line.contract_id and line.contract_id in contract_map:
            c_obj = contract_map[line.contract_id]
            if not c_obj.gfe_provided:
                mfg_cost += units * line.gfe_unit_cost_usd
            contract_direct_cost_this_month[line.contract_id] += mfg_cost
            contract_units_this_month[line.contract_id] += units
            contract_late_months[line.contract_id] = max(contract_late_months[line.contract_id], l_res["months_late"])
            if line.completed:
                contract_final_done[line.contract_id] = True
        total_mfg_cost_usd += mfg_cost
        total_idle_line_cost_usd += l_res["idle_retention_cost_usd"]
        new_units_delivered += units

    company.active_delivered_fleet += new_units_delivered

    # 4. Facility upkeep, GOCO lease, and Indirect Overhead & IR&D/B&P Recovery
    prod_cfg = cfg["production"]
    con_cfg = cfg["contracts"]
    owned_floor_m2 = float(company.facilities.get("factory_floor_m2", 0.0))
    goco_floor_m2 = float(company.facilities.get("goco_floor_m2", 0.0))
    wt_level = int(company.facilities.get("wind_tunnel_level", 0))
    wt_upkeep_map = {0: 0.0, 1: 4500.0, 2: 12000.0, 3: 26000.0, 4: 48000.0}

    facility_upkeep_usd = idx_aero * (
        owned_floor_m2 * float(prod_cfg["factory_upkeep_1950_usd_per_m2_month"])
        + goco_floor_m2 * float(prod_cfg["goco_lease_1950_usd_per_m2_month"])
        + wt_upkeep_map.get(wt_level, 0.0)
    )
    fixed_ga_usd = max(
        0.0,
        idx_aero * float(con_cfg["overhead_base_fixed_1950_usd_month"]) - comm_res["commercial_overhead_absorbed_usd"],
    )

    direct_govt_base_usd = sum(contract_direct_cost_this_month.values())
    total_irad_bp_usd = irad_project_payroll_usd + company.irad_monthly_spend_usd

    oh_res = compute_overhead_and_irad_recovery(
        direct_govt_contract_cost_usd=direct_govt_base_usd,
        indirect_facility_and_ga_usd=facility_upkeep_usd + fixed_ga_usd + total_idle_line_cost_usd,
        idle_engineering_payroll_usd=idle_eng_payroll_usd,
        irad_and_bp_spend_usd=total_irad_bp_usd,
        tuning=cfg,
    )
    eff_oh_rate = oh_res["effective_overhead_rate"]

    # 5. Settle active defense contracts
    total_contract_cash_in_usd = 0.0
    for c_obj in company.contracts:
        if c_obj.completed:
            continue
        d_cost = contract_direct_cost_this_month.get(c_obj.contract_id, 0.0)
        # Allocate allowable indirect overhead proportionally to direct contract base
        alloc_cost = d_cost * (1.0 + eff_oh_rate) if c_obj.phase == "rdte" else d_cost
        u_deliv = contract_units_this_month.get(c_obj.contract_id, 0)
        m_late = contract_late_months.get(c_obj.contract_id, 0)
        is_done = contract_final_done.get(c_obj.contract_id, False)

        c_step = step_contract_month(
            c_obj,
            allowable_cost_incurred_this_month_usd=alloc_cost,
            units_delivered_this_month=u_deliv,
            months_late=m_late,
            is_final_completion=is_done,
            tuning=cfg,
        )
        total_contract_cash_in_usd += c_step["cash_received_usd"]
        if c_step["reputation_delta"] != 0.0 and c_obj.customer in company.reputation:
            company.reputation[c_obj.customer] = min(
                100.0, max(0.0, company.reputation[c_obj.customer] + c_step["reputation_delta"])
            )

    # 6. Spares & Modification sustainment revenue
    spares_res = compute_monthly_spares_and_mods(
        active_delivered_fleet=company.active_delivered_fleet,
        avg_airframe_unit_value_1950_usd=company.avg_fleet_airframe_value_1950_usd,
        year=year,
        new_units_delivered_this_month=new_units_delivered,
        tuning=cfg,
    )

    # 7. Debt interest & credit rating
    mfg_workers_fte = (total_mfg_cost_usd * 0.55) / max(1.0, benchmark_mfg_wage_usd_hr(year) * 160.0)
    total_employees_fte = company.total_engineers_fte + mfg_workers_fte

    pc_res = step_political_capital_month(
        current_pc=company.political_capital,
        total_employees_fte=total_employees_fte,
        lobbying_spend_then_year_usd=company.lobbying_monthly_spend_usd,
        year=year,
        tuning=cfg,
    )
    company.political_capital = pc_res["new_political_capital"]

    credit_info = compute_borrowing_limits_and_rates(
        year=year,
        credit_rating=company.credit_rating,
        plant_property_value_usd=company.plant_property_value_usd,
        backlog_usd=company.total_backlog_usd,
        current_debt_usd=company.debt_usd,
        tuning=cfg,
    )
    monthly_interest_usd = max(0.0, company.debt_usd) * (credit_info["revolver_annual_rate"] / 12.0)

    # Total cash inflow and outflow
    total_cash_in_usd = (
        total_contract_cash_in_usd
        + spares_res["spares_revenue_usd"]
        + spares_res["modification_revenue_usd"]
        + comm_res["commercial_revenue_usd"]
    )
    total_cash_out_usd = (
        wf_res["direct_payroll_usd"]
        + wf_res["recruiting_cost_usd"]
        + wf_res["severance_cost_usd"]
        + total_mfg_cost_usd
        + total_idle_line_cost_usd
        + facility_upkeep_usd
        + fixed_ga_usd
        + company.irad_monthly_spend_usd
        + company.lobbying_monthly_spend_usd
        + spares_res["spares_cost_usd"]
        + spares_res["modification_cost_usd"]
        + comm_res["commercial_cost_usd"]
        + monthly_interest_usd
    )

    net_operating_cash_flow_usd = total_cash_in_usd - total_cash_out_usd
    company.cash_usd += net_operating_cash_flow_usd

    # Track YTD defense revenue/cost and operating profit
    defense_rev_month = total_contract_cash_in_usd + spares_res["spares_revenue_usd"] + spares_res["modification_revenue_usd"]
    defense_cost_month = (
        wf_res["direct_payroll_usd"]
        + total_mfg_cost_usd
        + facility_upkeep_usd
        + fixed_ga_usd
        + spares_res["spares_cost_usd"]
        + spares_res["modification_cost_usd"]
    )
    company.ytd_defense_revenue_usd += defense_rev_month
    company.ytd_defense_cost_usd += defense_cost_month
    company.ytd_operating_profit_usd += net_operating_cash_flow_usd

    # Year-end Renegotiation Act of 1951 & corporate tax settlement (Month == 12)
    renegotiation_clawback_usd = 0.0
    corporate_tax_paid_usd = 0.0
    if int(month) == 12:
        renegotiation_clawback_usd = compute_renegotiation_act_clawback(
            annual_defense_revenue_usd=company.ytd_defense_revenue_usd,
            annual_defense_cost_usd=company.ytd_defense_cost_usd,
            year=year,
            tuning=cfg,
        )
        company.cash_usd -= renegotiation_clawback_usd
        pre_tax_income = company.ytd_operating_profit_usd - renegotiation_clawback_usd
        if pre_tax_income < 0.0:
            company.tax_loss_carryforward_usd += -pre_tax_income
        else:
            offset = min(pre_tax_income, company.tax_loss_carryforward_usd)
            company.tax_loss_carryforward_usd -= offset
            taxable = max(0.0, pre_tax_income - offset)
            corporate_tax_paid_usd = taxable * float(cfg["finance"]["corporate_tax_rate"])
            company.cash_usd -= corporate_tax_paid_usd

        company.ytd_defense_revenue_usd = 0.0
        company.ytd_defense_cost_usd = 0.0
        company.ytd_operating_profit_usd = 0.0

    # Automatic credit line draw / paydown & solvency evaluation
    borrowed_this_month_usd = 0.0
    repaid_this_month_usd = 0.0
    if company.cash_usd < 0.0 and auto_borrow_revolver:
        needed = -company.cash_usd
        draw = min(needed, credit_info["available_credit_usd"])
        company.cash_usd += draw
        company.debt_usd += draw
        borrowed_this_month_usd = draw
    elif company.cash_usd > 0.0 and company.debt_usd > 0.0 and auto_borrow_revolver:
        # Keep 2 months operating buffer before auto-repaying revolver
        buffer_target = max(1500000.0 * idx_aero, total_cash_out_usd * 2.0)
        surplus = max(0.0, company.cash_usd - buffer_target)
        repay = min(company.debt_usd, surplus * 0.5)
        company.cash_usd -= repay
        company.debt_usd -= repay
        repaid_this_month_usd = repay

    chapter_xi_triggered = False
    if company.cash_usd < -1e-2:
        company.consecutive_insolvent_months += 1
        grace = int(cfg["finance"]["insolvency_grace_months"])
        if company.consecutive_insolvent_months >= grace:
            if allow_chapter_xi and not company.chapter_xi_used:
                c_xi = apply_chapter_xi_reorganization(
                    cash_usd=company.cash_usd,
                    debt_usd=company.debt_usd,
                    reputation=company.reputation,
                    engineers=company.engineers,
                    year=year,
                    tuning=cfg,
                )
                company.cash_usd = c_xi["new_cash_usd"]
                company.debt_usd = c_xi["new_debt_usd"]
                company.chapter_xi_used = True
                company.consecutive_insolvent_months = 0
                chapter_xi_triggered = True
            else:
                company.is_bankrupt_or_acquired = True
    else:
        company.consecutive_insolvent_months = 0

    company.credit_rating = evaluate_credit_rating(
        cash_usd=company.cash_usd,
        debt_usd=company.debt_usd,
        plant_property_value_usd=company.plant_property_value_usd,
        backlog_usd=company.total_backlog_usd,
        monthly_burn_usd=max(100000.0, total_cash_out_usd),
        consecutive_insolvent_months=company.consecutive_insolvent_months,
        tuning=cfg,
    )

    return {
        "year": int(year),
        "month": int(month),
        "cash_in_usd": float(total_cash_in_usd),
        "cash_out_usd": float(total_cash_out_usd),
        "net_operating_cash_flow_usd": float(net_operating_cash_flow_usd),
        "contract_cash_in_usd": float(total_contract_cash_in_usd),
        "spares_revenue_usd": float(spares_res["spares_revenue_usd"]),
        "commercial_revenue_usd": float(comm_res["commercial_revenue_usd"]),
        "engineering_payroll_usd": float(wf_res["direct_payroll_usd"]),
        "mfg_cost_usd": float(total_mfg_cost_usd),
        "facility_and_ga_usd": float(facility_upkeep_usd + fixed_ga_usd),
        "interest_paid_usd": float(monthly_interest_usd),
        "renegotiation_clawback_usd": float(renegotiation_clawback_usd),
        "corporate_tax_paid_usd": float(corporate_tax_paid_usd),
        "borrowed_usd": float(borrowed_this_month_usd),
        "repaid_usd": float(repaid_this_month_usd),
        "ending_cash_usd": float(company.cash_usd),
        "ending_debt_usd": float(company.debt_usd),
        "credit_rating": str(company.credit_rating),
        "new_units_delivered": int(new_units_delivered),
        "chapter_xi_triggered": bool(chapter_xi_triggered),
        "is_bankrupt_or_acquired": bool(company.is_bankrupt_or_acquired),
    }
