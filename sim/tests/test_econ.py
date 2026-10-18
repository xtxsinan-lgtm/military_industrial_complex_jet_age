"""Comprehensive pytest suite for Module 04 (`mic.econ`)."""

from __future__ import annotations

import json
import math
from pathlib import Path
import numpy as np
import pytest

from sim.mic.econ import (
    CompanyState,
    EngineeringProjectTask,
    ProductionLine,
    aero_cost_index_1950,
    apply_chapter_xi_reorganization,
    brooks_law_efficiency,
    can_afford_political_action,
    compute_borrowing_limits_and_rates,
    compute_commercial_buffer_month,
    compute_monthly_spares_and_mods,
    compute_overhead_and_irad_recovery,
    compute_project_monthly_hours,
    compute_rate_tooling_capex_usd,
    compute_renegotiation_act_clawback,
    convert_usd_between_years,
    cpi_index_1950,
    create_contract,
    discipline_mix_efficiency,
    estimate_costs,
    evaluate_credit_rating,
    evaluate_historical_calibration,
    run_monte_carlo_suite,
    simulate_campaign_1945_1960,
    spend_political_capital,
    step_company_day,
    step_company_month,
    step_contract_month,
    step_political_capital_month,
    step_production_line_month,
    step_workforce_month,
    to_constant_1950_usd,
    to_then_year_usd,
    wright_cumulative_average_factor,
    wright_lot_average_factor,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DIR = REPO_ROOT / "sim" / "golden"


def test_inflation_and_currency_conversions():
    assert math.isclose(cpi_index_1950(1950), 1.0, rel_tol=1e-6)
    assert math.isclose(aero_cost_index_1950(1950), 1.0, rel_tol=1e-6)
    assert cpi_index_1950(1945) < 1.0 < cpi_index_1950(1960)
    assert aero_cost_index_1950(1960) > cpi_index_1950(1960)

    # Round-trip conversions
    amt_1950 = 250000.0
    then_1957 = to_then_year_usd(amt_1950, 1957)
    back_1950 = to_constant_1950_usd(then_1957, 1957)
    assert math.isclose(amt_1950, back_1950, rel_tol=1e-9)

    # Fractional year interpolation
    idx_1952_5 = aero_cost_index_1950(1952.5)
    assert aero_cost_index_1950(1952) < idx_1952_5 < aero_cost_index_1950(1953)
    assert convert_usd_between_years(100000.0, 1948, 1958) > 100000.0


def test_wright_learning_curve_and_anderlohr_setback():
    assert wright_cumulative_average_factor(1, 0.80) == 1.0
    f100 = wright_cumulative_average_factor(100, 0.80)
    f200 = wright_cumulative_average_factor(200, 0.80)
    # Doubling quantity at 80% learning curve multiplies average labor hours by ~0.80
    assert math.isclose(f200 / f100, 0.80, rel_tol=0.015)

    lot_normal = wright_lot_average_factor(101, 150, 0.80, break_setback_units=0.0)
    lot_broken = wright_lot_average_factor(101, 150, 0.80, break_setback_units=50.0)
    assert lot_broken > lot_normal


def test_historical_aircraft_calibration_within_targets():
    cal = evaluate_historical_calibration()
    assert cal["aircraft_count"] == 12
    assert cal["mape_flyaway_pct"] <= 10.0
    assert cal["max_abs_err_flyaway_pct"] <= 20.0
    assert cal["mape_dev_pct"] <= 12.0
    assert cal["max_abs_err_dev_pct"] <= 25.0


def test_golden_cost_historical_vectors():
    golden_path = GOLDEN_DIR / "econ_cost_historical.json"
    with open(golden_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    tol = float(data["relative_tolerance"])

    for vec in data["vectors"]:
        inp = vec["input"]
        exp = vec["expected"]
        est = estimate_costs(
            design=inp["design"],
            mass_breakdown={"empty_mass_kg": inp["empty_mass_kg"]},
            engine={"mass_kg": inp["engine_mass_kg"], "unit_cost": inp["engine_unit_cost_usd"]},
            quantity=inp["quantity"],
            year=inp["year"],
            tech_context=inp.get("tech_context"),
            max_mach=inp["max_mach"],
            prototypes=inp["prototypes"],
        )
        # Verify both attribute and dict-style access
        assert math.isclose(est.unit_flyaway_cost_usd, exp["unit_flyaway_cost_usd"], rel_tol=tol)
        assert math.isclose(est["dev_cost_usd_estimate"], exp["dev_cost_usd_estimate"], rel_tol=tol)
        assert math.isclose(est.maint_mh_per_fh, exp["maint_mh_per_fh"], rel_tol=tol)


def test_golden_contracts_and_settlement_vectors():
    golden_path = GOLDEN_DIR / "econ_contracts_and_settlement.json"
    with open(golden_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    tol = float(data["relative_tolerance"])

    wf = data["wright_factors"]
    assert math.isclose(wright_cumulative_average_factor(100, 0.80), wf["cum_avg_q100_s080"], rel_tol=tol)
    assert math.isclose(wright_lot_average_factor(101, 150, 0.80, 30.0), wf["lot_101_to_150_s080_with_30_setback"], rel_tol=tol)

    comp = CompanyState.from_profile("medium_prime", company_id="golden_co", name="Golden Aero")
    rd_c = create_contract("c_rd_1952", "p_1952", "USAF", "CPFF", "rdte", 15000000.0, quantity=2)
    pr_c = create_contract("c_pr_1952", "p_1952", "USAF", "FPIF", "production", 45000000.0, quantity=180)
    comp.contracts.extend([rd_c, pr_c])
    comp.projects.append(
        EngineeringProjectTask(
            project_id="proj_1952",
            name="F-100 Class R&D",
            kind="airframe_supersonic",
            total_hours_required=600000.0,
            allocated_engineers=dict(comp.engineers),
            contract_id="c_rd_1952",
        )
    )
    comp.aircraft_in_production.append(
        ProductionLine(
            line_id="line_1952",
            design_id="des_1952",
            contract_id="c_pr_1952",
            airframe_mass_lb=14000.0,
            t1_airframe_cost_usd=520000.0,
            gfe_unit_cost_usd=140000.0,
            learning_curve_rate=0.80,
            target_rate_per_month=12.0,
            current_rate_per_month=6.0,
            tooling_rate_cap_per_month=15.0,
            total_quantity_ordered=180,
            scheduled_months=18,
        )
    )
    for m_idx, expected_row in enumerate(data["company_1952_monthly_ledger"], start=1):
        actual_row = step_company_month(comp, year=1952, month=m_idx)
        assert math.isclose(actual_row["ending_cash_usd"], expected_row["ending_cash_usd"], rel_tol=tol)
        assert math.isclose(actual_row["cash_in_usd"], expected_row["cash_in_usd"], rel_tol=tol)
        assert actual_row["new_units_delivered"] == expected_row["new_units_delivered"]


def test_contract_types_cpff_fpif_ffp_letter():
    # 1. CPFF overrun: fee does not grow, cost capped at 125% ceiling, reputation drops
    cpff = create_contract("c1", "p1", "USAF", "CPFF", "rdte", 10000000.0, quantity=1)
    r1 = step_contract_month(cpff, allowable_cost_incurred_this_month_usd=13000000.0, is_final_completion=True)
    # Reimbursed capped at 12.5M + 0.7M fixed fee = 13.2M
    assert math.isclose(r1["cash_received_usd"], 13200000.0, rel_tol=1e-6)
    assert r1["reputation_delta"] < 0.0

    # 2. FPIF underrun vs overrun
    fpif_under = create_contract("c2", "p2", "USAF", "FPIF", "production", 10000000.0, quantity=50)
    step_contract_month(fpif_under, allowable_cost_incurred_this_month_usd=8000000.0, units_delivered_this_month=50, is_final_completion=True)
    # Target profit = 900k; 2M underrun * 20% share = +400k bonus -> total paid = 8.0M + 1.3M = 9.3M
    paid_under = fpif_under.reimbursed_or_progress_paid_usd + fpif_under.delivery_payments_received_usd
    assert math.isclose(paid_under, 9300000.0, rel_tol=1e-6)

    # 3. FFP late delivery penalty
    ffp = create_contract("c3", "p3", "USN", "FFP", "production", 10000000.0, quantity=20)
    step_contract_month(ffp, allowable_cost_incurred_this_month_usd=9500000.0, units_delivered_this_month=20, months_late=4, is_final_completion=True)
    paid_ffp = ffp.reimbursed_or_progress_paid_usd + ffp.delivery_payments_received_usd
    assert paid_ffp < ffp.unit_price_usd * 20

    # 4. Letter contract definitization after 6 months
    let_c = create_contract("c4", "p4", "USAF", "LETTER", "rdte", 8000000.0, quantity=2)
    for _ in range(6):
        step_contract_month(let_c, allowable_cost_incurred_this_month_usd=400000.0)
    assert let_c.contract_type == "CPFF"


def test_workforce_brooks_law_and_discipline_mismatch():
    assert brooks_law_efficiency(200.0, newly_hired_fraction=0.0) == 1.0
    assert brooks_law_efficiency(600.0, newly_hired_fraction=0.3) < 0.85

    matched = {"aero": 30.0, "structures": 38.0, "propulsion": 12.0, "systems": 20.0}
    skewed = {"aero": 95.0, "structures": 5.0, "propulsion": 0.0, "systems": 0.0}
    req = {"aero": 0.30, "structures": 0.38, "propulsion": 0.12, "systems": 0.20}
    assert math.isclose(discipline_mix_efficiency(matched, req), 1.0, rel_tol=1e-6)
    assert discipline_mix_efficiency(skewed, req) < 0.65

    # Daily project progression
    comp = CompanyState.from_profile("small_innovator")
    comp.projects.append(
        EngineeringProjectTask(
            project_id="p_day",
            name="Daily Test",
            total_hours_required=10000.0,
            allocated_engineers=dict(comp.engineers),
        )
    )
    d_res = step_company_day(comp, date_day=10, days_in_month=30)
    assert d_res["daily_effective_engineering_hours"] > 0.0
    assert comp.projects[0].hours_completed > 0.0


def test_production_line_pause_and_spares():
    line = ProductionLine(
        line_id="l1",
        design_id="d1",
        contract_id=None,
        t1_airframe_cost_usd=500000.0,
        target_rate_per_month=10.0,
        current_rate_per_month=8.0,
        tooling_rate_cap_per_month=12.0,
        total_quantity_ordered=100,
    )
    r_active = step_production_line_month(line, available_floor_m2=50000.0, year=1953)
    assert r_active["units_built"] > 0

    # Pause without retaining workforce -> Anderlohr break setback accumulates
    line.target_rate_per_month = 0.0
    line.retain_workforce = False
    step_production_line_month(line, available_floor_m2=50000.0, year=1953)
    assert line.break_setback_units > 0.0

    capex = compute_rate_tooling_capex_usd(2000000.0, old_rate_cap=10.0, new_rate_cap=20.0)
    assert capex > 0.0

    sp = compute_monthly_spares_and_mods(500, 150000.0, 1955, new_units_delivered_this_month=8, mod_kits_delivered_this_month=15)
    assert sp["spares_profit_usd"] > 0.0
    assert sp["modification_profit_usd"] > 0.0


def test_finance_insolvency_and_political_capital():
    comp = CompanyState.from_profile("small_innovator")
    assert can_afford_political_action(comp.political_capital, "request_gfe_bailment")
    comp.political_capital = spend_political_capital(comp.political_capital, "request_gfe_bailment")
    with pytest.raises(ValueError):
        spend_political_capital(2.0, "protest_contract_award")

    pc_step = step_political_capital_month(30.0, total_employees_fte=4000.0, lobbying_spend_then_year_usd=25000.0, year=1954)
    assert pc_step["new_political_capital"] > 30.0

    # Simulate 3 months of severe negative cash without credit line to trigger Chapter XI
    comp.cash_usd = -5000000.0
    comp.debt_usd = 12000000.0
    for m in range(1, 4):
        res = step_company_month(comp, year=1948, month=m, auto_borrow_revolver=False, allow_chapter_xi=True)
    assert comp.chapter_xi_used is True
    assert res["chapter_xi_triggered"] is True


def test_monte_carlo_campaign_reproducibility():
    rng1 = np.random.default_rng(42)
    rng2 = np.random.default_rng(42)
    run1 = simulate_campaign_1945_1960(rng1, strategy="balanced_prime", win_rate=0.33)
    run2 = simulate_campaign_1945_1960(rng2, strategy="balanced_prime", win_rate=0.33)
    assert run1 == run2
    suite = run_monte_carlo_suite(n_runs_per_cell=5, seed=99)
    assert len(suite["cells"]) == 20
