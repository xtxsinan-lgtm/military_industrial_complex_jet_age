"""Corporate finance: credit rating, revolving credit, V-loans, bonds, baseline commercial revenue, and insolvency."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from .inflation import aero_cost_index_1950, corporate_aaa_bond_rate, prime_interest_rate
from .tuning import load_econ_tuning


@dataclass
class DebtInstrument:
    """Loan or bond held by a company."""

    instrument_id: str
    kind: str = "revolver"  # revolver | v_loan | bond
    principal_usd: float = 0.0
    annual_interest_rate: float = 0.035
    remaining_months: int = 12


def evaluate_credit_rating(
    cash_usd: float,
    debt_usd: float,
    plant_property_value_usd: float,
    backlog_usd: float,
    monthly_burn_usd: float,
    consecutive_insolvent_months: int = 0,
    tuning: Optional[Dict[str, Any]] = None,
) -> str:
    """Determine corporate credit rating (`AAA`, `AA`, `A`, `BBB`, `BB`, `B`, `CCC`, `D`)."""
    if consecutive_insolvent_months > 0 and cash_usd < 0.0:
        return "D" if consecutive_insolvent_months >= 3 else "CCC"

    assets = max(1.0, max(0.0, float(cash_usd)) + max(0.0, float(plant_property_value_usd)) + 0.25 * max(0.0, float(backlog_usd)))
    leverage = max(0.0, float(debt_usd)) / assets
    runway_months = max(0.0, float(cash_usd)) / max(1.0, float(monthly_burn_usd))
    backlog_cov = max(0.0, float(backlog_usd)) / max(1.0, float(monthly_burn_usd) * 12.0)

    score = 100.0 - 95.0 * leverage + 1.8 * min(24.0, runway_months) + 8.0 * min(3.0, backlog_cov)
    if score >= 115.0 and leverage <= 0.15:
        return "AAA"
    if score >= 98.0 and leverage <= 0.28:
        return "AA"
    if score >= 82.0 and leverage <= 0.42:
        return "A"
    if score >= 68.0 and leverage <= 0.58:
        return "BBB"
    if score >= 52.0:
        return "BB"
    if score >= 35.0:
        return "B"
    return "CCC"


def compute_borrowing_limits_and_rates(
    year: float,
    credit_rating: str,
    plant_property_value_usd: float,
    backlog_usd: float,
    current_debt_usd: float,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    """Compute maximum borrowing capacity and annualized interest rates for Revolver, V-Loan, and Bonds."""
    cfg = (tuning if tuning is not None else load_econ_tuning())["finance"]
    spreads = cfg["credit_spread_by_rating"]
    spread = float(spreads.get(credit_rating, spreads["BBB"]))

    prime = prime_interest_rate(year)
    aaa = corporate_aaa_bond_rate(year)

    revolver_max = (
        float(cfg["revolver_limit_ppe_frac"]) * max(0.0, float(plant_property_value_usd))
        + float(cfg["revolver_limit_backlog_frac"]) * max(0.0, float(backlog_usd))
    )
    yr_int = int(round(year))
    v_loan_active = int(cfg["v_loan_available_start_year"]) <= yr_int <= int(cfg["v_loan_available_end_year"])
    v_loan_max = float(cfg["v_loan_max_backlog_frac"]) * max(0.0, float(backlog_usd)) if v_loan_active else 0.0

    revolver_rate = prime + spread
    v_loan_rate = prime + float(cfg["v_loan_guarantee_fee_rate"]) + 0.5 * spread
    bond_rate = aaa + spread

    total_cap = revolver_max + v_loan_max
    available_to_draw = max(0.0, total_cap - max(0.0, float(current_debt_usd)))

    return {
        "revolver_limit_usd": float(revolver_max),
        "v_loan_limit_usd": float(v_loan_max),
        "total_credit_limit_usd": float(total_cap),
        "available_credit_usd": float(available_to_draw),
        "revolver_annual_rate": float(revolver_rate),
        "v_loan_annual_rate": float(v_loan_rate),
        "bond_annual_rate": float(bond_rate),
    }


def compute_commercial_buffer_month(
    buffer_level: str,
    year: float,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    """Compute monthly baseline non-fighter subcontracting/commercial revenue, profit, and overhead absorption."""
    cfg = (tuning if tuning is not None else load_econ_tuning())["finance"]
    levels = cfg["commercial_buffer_levels"]
    spec = levels.get(buffer_level, levels["none"])
    idx = aero_cost_index_1950(year)

    rev_usd = float(spec["monthly_revenue_1950_usd"]) * idx
    margin = float(spec["operating_margin"])
    cost_usd = rev_usd * (1.0 - margin)
    oh_abs_usd = float(spec["overhead_absorption_1950_usd"]) * idx
    floor_m2 = float(spec["factory_floor_committed_m2"])

    return {
        "commercial_revenue_usd": float(rev_usd),
        "commercial_cost_usd": float(cost_usd),
        "commercial_operating_profit_usd": float(rev_usd - cost_usd),
        "commercial_overhead_absorbed_usd": float(oh_abs_usd),
        "commercial_floor_committed_m2": float(floor_m2),
    }


def apply_chapter_xi_reorganization(
    cash_usd: float,
    debt_usd: float,
    reputation: Dict[str, float],
    engineers: Dict[str, float],
    emergency_bridge_loan_1950_usd: float = 4000000.0,
    year: float = 1950.0,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute one-time Chapter XI bankruptcy reorganization (debt haircut, bridge liquidity, reputation & staff loss)."""
    cfg = (tuning if tuning is not None else load_econ_tuning())["finance"]
    haircut = float(cfg["chapter_xi_debt_haircut_frac"])
    rep_pen = float(cfg["chapter_xi_reputation_penalty"])
    eng_loss = float(cfg["chapter_xi_engineer_loss_frac"])

    forgiven_debt = max(0.0, float(debt_usd)) * haircut
    new_debt = max(0.0, float(debt_usd) - forgiven_debt)
    bridge_cash = float(emergency_bridge_loan_1950_usd) * aero_cost_index_1950(year)
    new_cash = max(0.0, float(cash_usd)) + bridge_cash
    new_debt += bridge_cash

    for k in list(reputation.keys()):
        reputation[k] = max(5.0, float(reputation[k]) - rep_pen)
    for d in list(engineers.keys()):
        engineers[d] = max(5.0, float(engineers[d]) * (1.0 - eng_loss))

    return {
        "new_cash_usd": float(new_cash),
        "new_debt_usd": float(new_debt),
        "forgiven_debt_usd": float(forgiven_debt),
        "bridge_cash_injected_usd": float(bridge_cash),
    }
