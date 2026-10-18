"""Monte-Carlo 1945-1960 campaign cash-flow simulator and historical CER calibration evaluator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

from .company import CompanyState, step_company_month
from .contracts import create_contract
from .cost import estimate_costs
from .inflation import aero_cost_index_1950
from .production import ProductionLine
from .tuning import load_econ_tuning
from .workforce import EngineeringProjectTask

_REPO_ROOT = Path(__file__).resolve().parents[3]
_HIST_AC_PATH = _REPO_ROOT / "sim" / "data" / "economy" / "historical_aircraft_costs.json"


def evaluate_historical_calibration(path: Optional[Path] = None) -> Dict[str, Any]:
    """Evaluate `estimate_costs` against all 12 historical 1945-1960 fighters in `historical_aircraft_costs.json`."""
    p_file = path if path is not None else _HIST_AC_PATH
    with open(p_file, "r", encoding="utf-8") as fh:
        ac_list = json.load(fh)["aircraft"]

    rows: List[Dict[str, Any]] = []
    abs_err_fly: List[float] = []
    abs_err_af: List[float] = []
    abs_err_dev: List[float] = []

    for a in ac_list:
        est = estimate_costs(
            design=a,
            mass_breakdown={"empty_mass_kg": a["empty_mass_kg"]},
            engine={"mass_kg": a["engine_mass_kg"], "unit_cost": a["engine_unit_cost_usd"]},
            quantity=a["quantity"],
            year=a["year"],
            max_mach=a["max_mach"],
            prototypes=a["prototypes"],
        )
        haf = float(a["historical_airframe_unit_usd"])
        hfly = float(a["historical_unit_flyaway_usd"])
        hdev = float(a["historical_dev_cost_usd"])

        err_af_pct = (est.airframe_unit_cost_usd - haf) / haf * 100.0
        err_fly_pct = (est.unit_flyaway_cost_usd - hfly) / hfly * 100.0
        err_dev_pct = (est.dev_cost_usd_estimate - hdev) / hdev * 100.0

        abs_err_af.append(abs(err_af_pct))
        abs_err_fly.append(abs(err_fly_pct))
        abs_err_dev.append(abs(err_dev_pct))

        rows.append(
            {
                "id": a["id"],
                "name": a["name"],
                "service": a["service"],
                "year": a["year"],
                "quantity": a["quantity"],
                "empty_mass_kg": a["empty_mass_kg"],
                "max_mach": a["max_mach"],
                "hist_airframe_usd": haf,
                "model_airframe_usd": est.airframe_unit_cost_usd,
                "err_airframe_pct": err_af_pct,
                "hist_flyaway_usd": hfly,
                "model_flyaway_usd": est.unit_flyaway_cost_usd,
                "err_flyaway_pct": err_fly_pct,
                "hist_dev_usd": hdev,
                "model_dev_usd": est.dev_cost_usd_estimate,
                "err_dev_pct": err_dev_pct,
                "maint_mh_per_fh": est.maint_mh_per_fh,
                "engineering_hours": est.engineering_hours,
                "t1_mfg_labor_hours": est.t1_mfg_labor_hours,
            }
        )

    return {
        "aircraft_count": len(rows),
        "mape_airframe_pct": float(np.mean(abs_err_af)),
        "max_abs_err_airframe_pct": float(np.max(abs_err_af)),
        "mape_flyaway_pct": float(np.mean(abs_err_fly)),
        "max_abs_err_flyaway_pct": float(np.max(abs_err_fly)),
        "mape_dev_pct": float(np.mean(abs_err_dev)),
        "max_abs_err_dev_pct": float(np.max(abs_err_dev)),
        "rows": rows,
    }


def simulate_campaign_1945_1960(
    rng: np.random.Generator,
    strategy: str = "balanced_prime",
    win_rate: float = 0.33,
    profile_id: str = "medium_prime",
) -> Dict[str, Any]:
    """Simulate a 16-year (1945-01 to 1960-12, 192 months) manufacturer cash-flow trajectory.

    Strategies:
    - `conservative_lean`: Keeps lean engineering staff (0.85x scale), modest IR&D/lobbying, subcontracting buffer.
    - `balanced_prime`: Matches workforce to active contracts (1.0x scale), standard IR&D/lobbying, subcontracting buffer.
    - `aggressive_expander`: Expands staff (1.35x scale) + high salary premium (1.08x) + heavy IR&D/lobbying & factory expansion.
    - `no_commercial_buffer`: Same as `balanced_prime` but with `commercial_buffer_level = "none"` (pure fighter specialist).
    """
    comp = CompanyState.from_profile(profile_id=profile_id, company_id=f"mc_{strategy}", name=strategy)

    if strategy == "conservative_lean":
        staff_scale = 0.78
        comp.salary_multiplier = 0.98
        irad_base_1950 = 12000.0
        lobby_base_1950 = 6000.0
        comp.commercial_buffer_level = "subcontracting"
        capacity_lot_mult = 0.78
    elif strategy == "balanced_prime":
        staff_scale = 1.00
        comp.salary_multiplier = 1.02
        irad_base_1950 = 28000.0
        lobby_base_1950 = 14000.0
        comp.commercial_buffer_level = "subcontracting"
        capacity_lot_mult = 1.08
    elif strategy == "aggressive_expander":
        staff_scale = 1.35
        comp.salary_multiplier = 1.06
        irad_base_1950 = 60000.0
        lobby_base_1950 = 28000.0
        comp.commercial_buffer_level = "subcontracting"
        comp.facilities["factory_floor_m2"] += 35000.0
        comp.cash_usd -= 35000.0 * 110.0 * aero_cost_index_1950(1945)
        capacity_lot_mult = 1.38
    elif strategy == "no_commercial_buffer":
        staff_scale = 1.00
        comp.salary_multiplier = 1.02
        irad_base_1950 = 28000.0
        lobby_base_1950 = 14000.0
        comp.commercial_buffer_level = "none"
        capacity_lot_mult = 1.05
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    base_eng = dict(comp.engineers)
    min_cash_usd = comp.cash_usd
    max_debt_usd = comp.debt_usd
    contracts_won = 0
    total_units_delivered = 0

    # 8 historical program RFP waves over 1945-1960 (every 24 months: 1945, 1947, 1949, 1951, 1953, 1955, 1957, 1959)
    for year in range(1945, 1961):
        idx = aero_cost_index_1950(year)
        comp.irad_monthly_spend_usd = irad_base_1950 * idx
        comp.lobbying_monthly_spend_usd = lobby_base_1950 * idx

        for month in range(1, 13):
            # Issue RFP wave on month 2 of odd years
            if month == 2 and (year % 2 == 1):
                # Bid & Proposal expense (~$150k in 1950 USD)
                comp.cash_usd -= 150000.0 * idx
                eff_win_prob = min(0.95, max(0.02, float(win_rate)))
                if rng.random() < eff_win_prob:
                    contracts_won += 1
                    prog_id = f"prog_{year}"
                    era_progress = (year - 1945) / 15.0
                    rd_cost_1950 = 7500000.0 * (1.0 + 2.8 * era_progress)
                    rd_cost_usd = rd_cost_1950 * idx
                    cost_overrun_factor = float(rng.normal(1.02, 0.07))
                    rd_contract = create_contract(
                        contract_id=f"c_rd_{year}",
                        program_id=prog_id,
                        customer="USAF" if (year % 4 != 3) else "USN",
                        contract_type="CPFF",
                        phase="rdte",
                        estimated_cost_usd=rd_cost_usd,
                        quantity=2,
                    )
                    comp.contracts.append(rd_contract)
                    eng_hrs_req = (rd_cost_1950 * 0.42 / 6.80) * max(0.8, cost_overrun_factor)
                    proj = EngineeringProjectTask(
                        project_id=f"p_rd_{year}",
                        name=f"{year} Fighter RDT&E",
                        kind="airframe_supersonic" if year >= 1952 else "airframe_subsonic",
                        total_hours_required=eng_hrs_req,
                        contract_id=rd_contract.contract_id,
                    )
                    comp.projects.append(proj)

                    # Production order scaled by company capacity & Korean War surge
                    korea_mult = 1.65 if (1950 <= year <= 1953) else 1.0
                    qty = int(round(rng.uniform(240, 480) * korea_mult * capacity_lot_mult * (1.0 - 0.32 * era_progress)))
                    t1_af_1950 = 280000.0 * (1.0 + 2.2 * era_progress)
                    t1_af_usd = t1_af_1950 * idx
                    lc_factor = 0.37
                    prod_est_cost_usd = qty * t1_af_usd * lc_factor
                    prod_contract = create_contract(
                        contract_id=f"c_prod_{year}",
                        program_id=prog_id,
                        customer=rd_contract.customer,
                        contract_type="FPIF" if year >= 1951 else "CPFF",
                        phase="production",
                        estimated_cost_usd=prod_est_cost_usd,
                        quantity=qty,
                    )
                    comp.contracts.append(prod_contract)
                    target_rate = max(6.0, min(32.0, qty / 21.0))
                    # Lean firms under-invest in rate tooling, risking late delivery penalties on large orders
                    tool_cap_mult = 0.85 if strategy == "conservative_lean" else 1.15
                    line = ProductionLine(
                        line_id=f"line_{year}",
                        design_id=f"des_{year}",
                        contract_id=prod_contract.contract_id,
                        airframe_mass_lb=8500.0 + 7500.0 * era_progress,
                        t1_airframe_cost_usd=t1_af_usd * max(0.85, float(rng.normal(0.97, 0.05))),
                        gfe_unit_cost_usd=65000.0 * (1.0 + 2.0 * era_progress) * idx,
                        learning_curve_rate=0.79 if strategy == "aggressive_expander" else 0.80,
                        target_rate_per_month=target_rate,
                        current_rate_per_month=max(2.0, target_rate * 0.30),
                        tooling_rate_cap_per_month=target_rate * tool_cap_mult,
                        total_quantity_ordered=qty,
                        scheduled_months=24,
                    )
                    comp.aircraft_in_production.append(line)

            # Allocate active engineers across active R&D projects
            active_projs = [p for p in comp.projects if not p.completed]

            # Dynamic target workforce sizing
            demand_mult = staff_scale * (1.12 if active_projs else (0.72 if strategy == "conservative_lean" else 0.85))
            target_eng = {d: base_eng[d] * demand_mult for d in base_eng}

            if active_projs:
                n_p = len(active_projs)
                for p in active_projs:
                    p.allocated_engineers = {d: comp.engineers[d] / n_p for d in comp.engineers}

            m_res = step_company_month(
                comp,
                year=year,
                month=month,
                target_engineers=target_eng,
                advance_projects_in_month=True,
                auto_borrow_revolver=True,
                allow_chapter_xi=True,
            )
            total_units_delivered += m_res["new_units_delivered"]
            min_cash_usd = min(min_cash_usd, comp.cash_usd)
            max_debt_usd = max(max_debt_usd, comp.debt_usd)

            if comp.is_bankrupt_or_acquired:
                break
        if comp.is_bankrupt_or_acquired:
            break

    net_worth_usd = comp.cash_usd + comp.plant_property_value_usd - comp.debt_usd
    return {
        "strategy": strategy,
        "win_rate": float(win_rate),
        "survived": not comp.is_bankrupt_or_acquired,
        "chapter_xi_used": bool(comp.chapter_xi_used),
        "ending_cash_usd": float(comp.cash_usd),
        "ending_debt_usd": float(comp.debt_usd),
        "ending_net_worth_usd": float(net_worth_usd),
        "min_cash_usd": float(min_cash_usd),
        "max_debt_usd": float(max_debt_usd),
        "contracts_won": int(contracts_won),
        "total_units_delivered": int(total_units_delivered),
        "ending_credit_rating": str(comp.credit_rating),
        "ending_reputation_usaf": float(comp.reputation.get("USAF", 0.0)),
        "ending_political_capital": float(comp.political_capital),
    }


def run_monte_carlo_suite(
    n_runs_per_cell: int = 150,
    seed: int = 19450101,
) -> Dict[str, Any]:
    """Run Monte-Carlo cash-flow matrix across strategies and RFP win rates."""
    rng = np.random.default_rng(seed)
    strategies = ["conservative_lean", "balanced_prime", "aggressive_expander", "no_commercial_buffer"]
    win_rates = [0.10, 0.20, 0.33, 0.50, 0.67]

    cells: List[Dict[str, Any]] = []
    for strat in strategies:
        for wr in win_rates:
            runs = [simulate_campaign_1945_1960(rng, strategy=strat, win_rate=wr) for _ in range(n_runs_per_cell)]
            surv_rate = float(np.mean([1.0 if r["survived"] else 0.0 for r in runs]))
            chap11_rate = float(np.mean([1.0 if r["chapter_xi_used"] else 0.0 for r in runs]))
            nw_vals = [r["ending_net_worth_usd"] for r in runs]
            cash_vals = [r["ending_cash_usd"] for r in runs]
            debt_vals = [r["max_debt_usd"] for r in runs]
            wins_vals = [r["contracts_won"] for r in runs]
            deliv_vals = [r["total_units_delivered"] for r in runs]

            cells.append(
                {
                    "strategy": strat,
                    "win_rate": wr,
                    "n_runs": n_runs_per_cell,
                    "survival_rate": surv_rate,
                    "bankruptcy_rate": 1.0 - surv_rate,
                    "chapter_xi_rate": chap11_rate,
                    "median_net_worth_usd": float(np.median(nw_vals)),
                    "p10_net_worth_usd": float(np.percentile(nw_vals, 10)),
                    "p90_net_worth_usd": float(np.percentile(nw_vals, 90)),
                    "median_ending_cash_usd": float(np.median(cash_vals)),
                    "median_max_debt_usd": float(np.median(debt_vals)),
                    "mean_contracts_won": float(np.mean(wins_vals)),
                    "mean_units_delivered": float(np.mean(deliv_vals)),
                }
            )

    return {
        "seed": seed,
        "n_runs_per_cell": n_runs_per_cell,
        "strategies": strategies,
        "win_rates": win_rates,
        "cells": cells,
    }
