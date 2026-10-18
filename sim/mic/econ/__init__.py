"""Module 04: Company Economy, Cost Model, Workforce, Production, Contracts, and Finance (`mic.econ`)."""

from .company import CompanyState, step_company_day, step_company_month
from .contracts import (
    DefenseContract,
    compute_overhead_and_irad_recovery,
    compute_renegotiation_act_clawback,
    create_contract,
    step_contract_month,
)
from .cost import (
    CostEstimate,
    estimate_costs,
    wright_cumulative_average_factor,
    wright_lot_average_factor,
)
from .finance import (
    DebtInstrument,
    apply_chapter_xi_reorganization,
    compute_borrowing_limits_and_rates,
    compute_commercial_buffer_month,
    evaluate_credit_rating,
)
from .inflation import (
    aero_cost_index_1950,
    benchmark_engineer_salary_usd_yr,
    benchmark_mfg_wage_usd_hr,
    convert_usd_between_years,
    corporate_aaa_bond_rate,
    cpi_index_1950,
    labor_market_tightness,
    load_inflation_table,
    prime_interest_rate,
    to_constant_1950_usd,
    to_then_year_usd,
)
from .monte_carlo import (
    evaluate_historical_calibration,
    run_monte_carlo_suite,
    simulate_campaign_1945_1960,
)
from .politics import (
    can_afford_political_action,
    spend_political_capital,
    step_political_capital_month,
)
from .production import (
    ProductionLine,
    compute_monthly_spares_and_mods,
    compute_rate_tooling_capex_usd,
    step_production_line_month,
)
from .tuning import load_econ_tuning
from .workforce import (
    DISCIPLINES,
    EngineeringProjectTask,
    brooks_law_efficiency,
    compute_project_monthly_hours,
    discipline_mix_efficiency,
    step_workforce_month,
)

__all__ = [
    "CompanyState",
    "step_company_day",
    "step_company_month",
    "DefenseContract",
    "compute_overhead_and_irad_recovery",
    "compute_renegotiation_act_clawback",
    "create_contract",
    "step_contract_month",
    "CostEstimate",
    "estimate_costs",
    "wright_cumulative_average_factor",
    "wright_lot_average_factor",
    "DebtInstrument",
    "apply_chapter_xi_reorganization",
    "compute_borrowing_limits_and_rates",
    "compute_commercial_buffer_month",
    "evaluate_credit_rating",
    "aero_cost_index_1950",
    "benchmark_engineer_salary_usd_yr",
    "benchmark_mfg_wage_usd_hr",
    "convert_usd_between_years",
    "corporate_aaa_bond_rate",
    "cpi_index_1950",
    "labor_market_tightness",
    "load_inflation_table",
    "prime_interest_rate",
    "to_constant_1950_usd",
    "to_then_year_usd",
    "evaluate_historical_calibration",
    "run_monte_carlo_suite",
    "simulate_campaign_1945_1960",
    "can_afford_political_action",
    "spend_political_capital",
    "step_political_capital_month",
    "ProductionLine",
    "compute_monthly_spares_and_mods",
    "compute_rate_tooling_capex_usd",
    "step_production_line_month",
    "load_econ_tuning",
    "DISCIPLINES",
    "EngineeringProjectTask",
    "brooks_law_efficiency",
    "compute_project_monthly_hours",
    "discipline_mix_efficiency",
    "step_workforce_month",
]
