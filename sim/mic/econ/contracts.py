"""US defense procurement contracts (CPFF, FPIF, FFP, Letter), progress payments, overhead/IR&D recovery, and Renegotiation Act."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from .tuning import load_econ_tuning


@dataclass
class DefenseContract:
    """Active government contract held by a manufacturer."""

    contract_id: str
    program_id: str
    customer: str = "USAF"  # USAF | USN | export
    contract_type: str = "CPFF"  # CPFF | FPIF | FFP | LETTER
    phase: str = "rdte"  # rdte | production
    target_cost_usd: float = 20000000.0
    target_profit_or_fee_usd: float = 1400000.0
    ceiling_price_usd: float = 25000000.0
    govt_share_ratio: float = 0.80
    unit_price_usd: float = 0.0
    quantity: int = 1
    gfe_provided: bool = True
    incurred_cost_usd: float = 0.0
    reimbursed_or_progress_paid_usd: float = 0.0
    delivery_payments_received_usd: float = 0.0
    fee_paid_usd: float = 0.0
    units_delivered: int = 0
    undefinitized_months_elapsed: int = 0
    definitizes_to: str = "CPFF"
    completed: bool = False

    @property
    def target_price_usd(self) -> float:
        return float(self.target_cost_usd + self.target_profit_or_fee_usd)

    @property
    def remaining_backlog_usd(self) -> float:
        total_expected = self.unit_price_usd * self.quantity if self.contract_type == "FFP" and self.unit_price_usd > 0 else self.target_price_usd
        received = self.reimbursed_or_progress_paid_usd + self.delivery_payments_received_usd + self.fee_paid_usd
        return max(0.0, float(total_expected - received))

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["target_price_usd"] = self.target_price_usd
        d["remaining_backlog_usd"] = self.remaining_backlog_usd
        return d


def create_contract(
    contract_id: str,
    program_id: str,
    customer: str,
    contract_type: str,
    phase: str,
    estimated_cost_usd: float,
    quantity: int = 1,
    fee_or_profit_rate: Optional[float] = None,
    govt_share_ratio: Optional[float] = None,
    gfe_provided: bool = True,
    tuning: Optional[Dict[str, Any]] = None,
) -> DefenseContract:
    """Factory that initializes a `DefenseContract` with statutory ASPA 1947 caps and ceiling rules."""
    cfg = (tuning if tuning is not None else load_econ_tuning())["contracts"]
    ctype = contract_type.upper()
    est_cost = max(1.0, float(estimated_cost_usd))
    qty = max(1, int(quantity))

    if ctype == "CPFF":
        max_fee = float(cfg["cpff_statutory_max_fee_rd"]) if phase == "rdte" else float(cfg["cpff_statutory_max_fee_prod"])
        rate = min(max_fee, float(fee_or_profit_rate if fee_or_profit_rate is not None else cfg["cpff_default_fee_rate"]))
        fee = est_cost * rate
        ceiling = est_cost * float(cfg["cpff_overrun_reimburse_cap_mult"])
        return DefenseContract(
            contract_id=contract_id,
            program_id=program_id,
            customer=customer,
            contract_type="CPFF",
            phase=phase,
            target_cost_usd=est_cost,
            target_profit_or_fee_usd=fee,
            ceiling_price_usd=ceiling,
            govt_share_ratio=1.0,
            unit_price_usd=(est_cost + fee) / qty,
            quantity=qty,
            gfe_provided=gfe_provided,
        )

    if ctype == "FPIF":
        rate = float(fee_or_profit_rate if fee_or_profit_rate is not None else cfg["fpif_default_target_profit_rate"])
        share = float(govt_share_ratio if govt_share_ratio is not None else cfg["fpif_default_govt_share_ratio"])
        profit = est_cost * rate
        ceiling = est_cost * float(cfg["fpif_default_ceiling_price_mult"])
        return DefenseContract(
            contract_id=contract_id,
            program_id=program_id,
            customer=customer,
            contract_type="FPIF",
            phase=phase,
            target_cost_usd=est_cost,
            target_profit_or_fee_usd=profit,
            ceiling_price_usd=ceiling,
            govt_share_ratio=share,
            unit_price_usd=(est_cost + profit) / qty,
            quantity=qty,
            gfe_provided=gfe_provided,
        )

    if ctype == "FFP":
        rate = float(fee_or_profit_rate if fee_or_profit_rate is not None else cfg["ffp_default_profit_rate_bid"])
        profit = est_cost * rate
        total_price = est_cost + profit
        return DefenseContract(
            contract_id=contract_id,
            program_id=program_id,
            customer=customer,
            contract_type="FFP",
            phase=phase,
            target_cost_usd=est_cost,
            target_profit_or_fee_usd=profit,
            ceiling_price_usd=total_price,
            govt_share_ratio=0.0,
            unit_price_usd=total_price / qty,
            quantity=qty,
            gfe_provided=gfe_provided,
        )

    if ctype == "LETTER":
        def_to = "CPFF" if phase == "rdte" else "FPIF"
        rate = float(cfg["cpff_default_fee_rate"] if def_to == "CPFF" else cfg["fpif_default_target_profit_rate"])
        profit = est_cost * rate
        ceiling = est_cost * float(cfg["cpff_overrun_reimburse_cap_mult"])
        return DefenseContract(
            contract_id=contract_id,
            program_id=program_id,
            customer=customer,
            contract_type="LETTER",
            phase=phase,
            target_cost_usd=est_cost,
            target_profit_or_fee_usd=profit,
            ceiling_price_usd=ceiling,
            govt_share_ratio=0.80 if def_to == "FPIF" else 1.0,
            unit_price_usd=(est_cost + profit) / qty,
            quantity=qty,
            gfe_provided=gfe_provided,
            definitizes_to=def_to,
        )

    raise ValueError(f"Unknown contract_type: {contract_type}")


def step_contract_month(
    contract: DefenseContract,
    allowable_cost_incurred_this_month_usd: float,
    units_delivered_this_month: int = 0,
    progress_fraction_override: Optional[float] = None,
    months_late: int = 0,
    is_final_completion: bool = False,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    """Settle one month of cash receipts, progress payment liquidations, and reputation deltas on `contract`."""
    cfg = (tuning if tuning is not None else load_econ_tuning())["contracts"]
    prod_cfg = (tuning if tuning is not None else load_econ_tuning())["production"]

    if contract.completed:
        return {
            "cash_received_usd": 0.0,
            "progress_payment_usd": 0.0,
            "delivery_or_settlement_usd": 0.0,
            "fee_received_usd": 0.0,
            "reputation_delta": 0.0,
        }

    cost_inc = max(0.0, float(allowable_cost_incurred_this_month_usd))
    prev_cost = contract.incurred_cost_usd
    contract.incurred_cost_usd += cost_inc
    contract.units_delivered += max(0, int(units_delivered_this_month))

    # Handle LETTER contract undefinitized period and automatic definitization
    if contract.contract_type == "LETTER":
        contract.undefinitized_months_elapsed += 1
        nte_cap = contract.target_cost_usd * float(cfg["letter_contract_nte_frac"])
        prov_target = min(nte_cap, contract.incurred_cost_usd * 0.85)
        cash_in = max(0.0, prov_target - contract.reimbursed_or_progress_paid_usd)
        contract.reimbursed_or_progress_paid_usd += cash_in
        if contract.undefinitized_months_elapsed >= int(cfg["letter_contract_max_months"]) or is_final_completion:
            contract.contract_type = contract.definitizes_to
        if not is_final_completion:
            return {
                "cash_received_usd": float(cash_in),
                "progress_payment_usd": float(cash_in),
                "delivery_or_settlement_usd": 0.0,
                "fee_received_usd": 0.0,
                "reputation_delta": 0.0,
            }

    # 1. CPFF (Cost-Plus-Fixed-Fee)
    if contract.contract_type == "CPFF":
        reimb_cap = contract.ceiling_price_usd
        allowable_cum = min(reimb_cap, contract.incurred_cost_usd)
        reimb_this_month = max(0.0, allowable_cum - contract.reimbursed_or_progress_paid_usd)
        contract.reimbursed_or_progress_paid_usd += reimb_this_month

        if progress_fraction_override is not None:
            prog = min(1.0, max(0.0, float(progress_fraction_override)))
        elif contract.quantity > 1 and contract.phase == "production":
            prog = min(1.0, contract.units_delivered / max(1, contract.quantity))
        else:
            prog = min(1.0, contract.incurred_cost_usd / max(1.0, contract.target_cost_usd))

        withhold = 0.0 if (is_final_completion or contract.units_delivered >= contract.quantity and contract.phase == "production") else float(cfg["cpff_fee_withhold_frac"])
        payable_fee_cum = contract.target_profit_or_fee_usd * prog * (1.0 - withhold)
        if is_final_completion:
            payable_fee_cum = contract.target_profit_or_fee_usd
        fee_this_month = max(0.0, payable_fee_cum - contract.fee_paid_usd)
        contract.fee_paid_usd += fee_this_month

        rep_delta = 0.0
        # Overrun reputation penalty above 100% of target cost
        prev_overrun_ratio = max(0.0, (prev_cost - contract.target_cost_usd) / max(1.0, contract.target_cost_usd))
        curr_overrun_ratio = max(0.0, (contract.incurred_cost_usd - contract.target_cost_usd) / max(1.0, contract.target_cost_usd))
        if curr_overrun_ratio > prev_overrun_ratio:
            rep_delta -= (curr_overrun_ratio - prev_overrun_ratio) * 10.0 * float(cfg["cpff_overrun_reputation_hit_per_10pct"])

        if is_final_completion:
            contract.completed = True

        total_cash = reimb_this_month + fee_this_month
        return {
            "cash_received_usd": float(total_cash),
            "progress_payment_usd": float(reimb_this_month),
            "delivery_or_settlement_usd": 0.0,
            "fee_received_usd": float(fee_this_month),
            "reputation_delta": float(rep_delta),
        }

    # 2. FPIF (Fixed-Price-Incentive-Firm)
    if contract.contract_type == "FPIF":
        pp_rate = float(cfg["progress_payment_rate_fp"])
        pp_cap = contract.target_price_usd * float(cfg["progress_payment_liquidation_cap"])
        desired_pp_cum = min(pp_cap, contract.incurred_cost_usd * pp_rate)
        pp_this_month = max(0.0, desired_pp_cum - contract.reimbursed_or_progress_paid_usd)
        contract.reimbursed_or_progress_paid_usd += pp_this_month

        delivery_cash = 0.0
        rep_delta = 0.0
        done = is_final_completion or (contract.units_delivered >= contract.quantity)

        if units_delivered_this_month > 0 and not done:
            # Interim unit delivery billing net of progress payment liquidation
            frac_deliv = units_delivered_this_month / max(1, contract.quantity)
            gross_bill = frac_deliv * contract.target_price_usd
            late_pen_frac = min(
                float(prod_cfg["late_penalty_max_pct"]),
                max(0, int(months_late)) * float(prod_cfg["late_penalty_ffp_pct_per_month"]) * 0.67,
            )
            gross_bill *= 1.0 - late_pen_frac
            # Liquidate proportional progress payments
            net_deliv = max(0.0, gross_bill * (1.0 - pp_rate))
            delivery_cash += net_deliv
            contract.delivery_payments_received_usd += net_deliv

        if done:
            # Final FPIF incentive price settlement:
            # P_total = min(Ceiling, TargetCost + TargetProfit + (1 - govt_share)*(TargetCost - ActualCost) -> wait:
            # In FPIF, government pays ActualCost + Profit, where Profit = TargetProfit + contractor_share * (TargetCost - ActualCost),
            # so TotalPrice = min(Ceiling, ActualCost + TargetProfit + (1 - govt_share)*(TargetCost - ActualCost))
            contractor_share = 1.0 - contract.govt_share_ratio
            cost_underrun = contract.target_cost_usd - contract.incurred_cost_usd
            adjusted_profit = contract.target_profit_or_fee_usd + contractor_share * cost_underrun
            final_total_price = min(contract.ceiling_price_usd, contract.incurred_cost_usd + adjusted_profit)
            late_pen_frac = min(
                float(prod_cfg["late_penalty_max_pct"]),
                max(0, int(months_late)) * float(prod_cfg["late_penalty_ffp_pct_per_month"]) * 0.67,
            )
            final_total_price *= 1.0 - late_pen_frac
            already_paid = contract.reimbursed_or_progress_paid_usd + contract.delivery_payments_received_usd + contract.fee_paid_usd
            settlement = final_total_price - already_paid
            delivery_cash += settlement
            contract.delivery_payments_received_usd += settlement
            contract.completed = True
            if months_late > 0:
                rep_delta -= min(10.0, months_late * float(prod_cfg["late_reputation_hit_per_month"]))
            elif cost_underrun >= 0.0:
                rep_delta += 2.5

        total_cash = pp_this_month + delivery_cash
        return {
            "cash_received_usd": float(total_cash),
            "progress_payment_usd": float(pp_this_month),
            "delivery_or_settlement_usd": float(delivery_cash),
            "fee_received_usd": 0.0,
            "reputation_delta": float(rep_delta),
        }

    # 3. FFP (Firm-Fixed-Price)
    if contract.contract_type == "FFP":
        total_contract_price = contract.unit_price_usd * contract.quantity
        pp_rate = float(cfg["progress_payment_rate_fp"])
        pp_cap = total_contract_price * float(cfg["progress_payment_liquidation_cap"])
        desired_pp_cum = min(pp_cap, contract.incurred_cost_usd * pp_rate)
        pp_this_month = max(0.0, desired_pp_cum - contract.reimbursed_or_progress_paid_usd)
        contract.reimbursed_or_progress_paid_usd += pp_this_month

        delivery_cash = 0.0
        rep_delta = 0.0
        done = is_final_completion or (contract.units_delivered >= contract.quantity)

        if units_delivered_this_month > 0 or done:
            late_pen_frac = min(
                float(prod_cfg["late_penalty_max_pct"]),
                max(0, int(months_late)) * float(prod_cfg["late_penalty_ffp_pct_per_month"]),
            )
            effective_unit_price = contract.unit_price_usd * (1.0 - late_pen_frac)
            target_cum_revenue = contract.units_delivered * effective_unit_price
            if done:
                target_cum_revenue = contract.quantity * effective_unit_price
                already_paid = contract.reimbursed_or_progress_paid_usd + contract.delivery_payments_received_usd
                delivery_cash = target_cum_revenue - already_paid
                contract.delivery_payments_received_usd += delivery_cash
                contract.completed = True
                if months_late > 0:
                    rep_delta -= min(12.0, months_late * float(prod_cfg["late_reputation_hit_per_month"]))
                else:
                    rep_delta += 2.0
            else:
                gross_deliv = units_delivered_this_month * effective_unit_price
                net_deliv = max(0.0, gross_deliv * (1.0 - pp_rate))
                delivery_cash = net_deliv
                contract.delivery_payments_received_usd += net_deliv

        total_cash = pp_this_month + delivery_cash
        return {
            "cash_received_usd": float(total_cash),
            "progress_payment_usd": float(pp_this_month),
            "delivery_or_settlement_usd": float(delivery_cash),
            "fee_received_usd": 0.0,
            "reputation_delta": float(rep_delta),
        }

    raise ValueError(f"Unsupported contract_type: {contract.contract_type}")


def compute_overhead_and_irad_recovery(
    direct_govt_contract_cost_usd: float,
    indirect_facility_and_ga_usd: float,
    idle_engineering_payroll_usd: float,
    irad_and_bp_spend_usd: float,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    """Compute allowable indirect overhead pool and IR&D/B&P cost recovery under ASPR Section XV.

    In the 1949-1960 Armed Services Procurement Regulation (ASPR Section XV), contractors
    could recover Independent Research & Development (IR&D) and Bid & Proposal (B&P) expenses
    as allowable indirect overhead up to a negotiated ceiling (`irad_bp_allowable_recovery_cap_frac`
    of active government contract direct cost base), while total allowable indirect overhead
    is capped at `allowable_overhead_cap_ratio * direct_govt_contract_cost_usd`.
    """
    cfg = (tuning if tuning is not None else load_econ_tuning())["contracts"]
    direct_base = max(0.0, float(direct_govt_contract_cost_usd))
    irad_cap = direct_base * float(cfg["irad_bp_allowable_recovery_cap_frac"])
    recoverable_irad_usd = min(max(0.0, float(irad_and_bp_spend_usd)), irad_cap)

    raw_indirect_pool = (
        max(0.0, float(indirect_facility_and_ga_usd))
        + max(0.0, float(idle_engineering_payroll_usd))
        + recoverable_irad_usd
    )
    max_allowable_pool = direct_base * float(cfg["allowable_overhead_cap_ratio"])
    allowable_overhead_recovered_usd = min(raw_indirect_pool, max_allowable_pool)
    unallowable_overhead_absorbed_usd = max(0.0, raw_indirect_pool - allowable_overhead_recovered_usd) + max(
        0.0, float(irad_and_bp_spend_usd) - recoverable_irad_usd
    )

    return {
        "direct_govt_base_usd": float(direct_base),
        "recoverable_irad_bp_usd": float(recoverable_irad_usd),
        "allowable_overhead_recovered_usd": float(allowable_overhead_recovered_usd),
        "unallowable_overhead_absorbed_usd": float(unallowable_overhead_absorbed_usd),
        "effective_overhead_rate": float(allowable_overhead_recovered_usd / max(1.0, direct_base)) if direct_base > 0 else 0.0,
    }


def compute_renegotiation_act_clawback(
    annual_defense_revenue_usd: float,
    annual_defense_cost_usd: float,
    year: int,
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute Renegotiation Act of 1951 excess-profit clawback at year-end (`year >= 1951`)."""
    cfg = (tuning if tuning is not None else load_econ_tuning())["contracts"]
    if int(year) < int(cfg["renegotiation_act_active_start_year"]):
        return 0.0
    rev = max(0.0, float(annual_defense_revenue_usd))
    cost = max(0.0, float(annual_defense_cost_usd))
    profit = rev - cost
    exempt_profit = rev * float(cfg["renegotiation_act_exempt_return_on_sales"])
    if profit <= exempt_profit:
        return 0.0
    excess = profit - exempt_profit
    return float(excess * float(cfg["renegotiation_act_clawback_rate"]))
