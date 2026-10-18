"""Production lines, tooling rate limits, Wright learning curve, Anderlohr break loss, and spares."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Dict, Optional

from .cost import wright_lot_average_factor
from .inflation import aero_cost_index_1950
from .tuning import load_econ_tuning


@dataclass
class ProductionLine:
    """State of an active or paused aircraft production line inside `CompanyState.aircraft_in_production`."""

    line_id: str
    design_id: str
    contract_id: Optional[str]
    airframe_mass_lb: float = 10000.0
    t1_airframe_cost_usd: float = 600000.0
    gfe_unit_cost_usd: float = 150000.0
    learning_curve_rate: float = 0.80
    target_rate_per_month: float = 10.0
    current_rate_per_month: float = 2.0
    tooling_rate_cap_per_month: float = 15.0
    total_quantity_ordered: int = 200
    cumulative_units_built: int = 0
    fractional_unit_wip: float = 0.0
    idle_months: int = 0
    break_setback_units: float = 0.0
    retain_workforce: bool = False
    months_elapsed: int = 0
    scheduled_months: int = 24
    months_late: int = 0
    completed: bool = False

    def required_floor_area_m2(self, tuning: Optional[Dict[str, Any]] = None) -> float:
        """Compute factory floor space (`m^2`) required at `target_rate_per_month`."""
        cfg = (tuning if tuning is not None else load_econ_tuning())["production"]
        base_m2 = float(cfg["factory_m2_per_monthly_rate_10klb"])
        w_ratio = max(0.35, float(self.airframe_mass_lb) / 10000.0)
        return float(max(0.0, self.target_rate_per_month) * base_m2 * (w_ratio ** 0.75))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def compute_rate_tooling_capex_usd(
    base_tooling_cost_usd: float,
    old_rate_cap: float,
    new_rate_cap: float,
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute incremental tooling cost (then-year USD) to raise monthly rate capacity from `old_rate_cap` to `new_rate_cap`."""
    if new_rate_cap <= old_rate_cap:
        return 0.0
    cfg = (tuning if tuning is not None else load_econ_tuning())["production"]
    ref_rate = float(cfg["tooling_ref_rate_per_month"])
    exp_r = float(cfg["tooling_rate_exponent"])
    f_new = (max(1.0, float(new_rate_cap)) / ref_rate) ** exp_r
    f_old = (max(1.0, float(old_rate_cap)) / ref_rate) ** exp_r if old_rate_cap > 0 else 0.0
    return float(max(0.0, base_tooling_cost_usd * (f_new - f_old)))


def step_production_line_month(
    line: ProductionLine,
    available_floor_m2: float,
    year: float,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Advance `line` by one month, computing units delivered, lot cost via Wright learning curve, and break loss."""
    cfg = (tuning if tuning is not None else load_econ_tuning())["production"]
    if line.completed or line.cumulative_units_built >= line.total_quantity_ordered:
        line.completed = True
        return {
            "units_built": 0,
            "airframe_mfg_cost_usd": 0.0,
            "idle_retention_cost_usd": 0.0,
            "lot_learning_factor": 1.0,
            "floor_used_m2": 0.0,
            "months_late": line.months_late,
        }

    line.months_elapsed += 1
    remaining_units = line.total_quantity_ordered - line.cumulative_units_built

    # Handle paused / zero-target line (Anderlohr 1969 production break learning loss)
    if line.target_rate_per_month <= 1e-6 or available_floor_m2 <= 100.0:
        line.idle_months += 1
        line.current_rate_per_month = 0.0
        idle_cost = 0.0
        if line.retain_workforce:
            # Paying idle shop floor crews preserves learning curve position
            est_unit_cost = line.t1_airframe_cost_usd * wright_lot_average_factor(
                max(1, line.cumulative_units_built),
                max(1, line.cumulative_units_built),
                line.learning_curve_rate,
                break_setback_units=line.break_setback_units,
            )
            idle_cost = float(cfg["retain_workforce_idle_wage_frac"]) * est_unit_cost * max(1.0, line.tooling_rate_cap_per_month * 0.25)
        else:
            loss_frac = min(
                float(cfg["anderlohr_max_ setback_frac"]),
                float(cfg["anderlohr_break_loss_per_month"]) * line.idle_months,
            )
            line.break_setback_units = float(line.cumulative_units_built) * loss_frac
        if line.months_elapsed > line.scheduled_months:
            line.months_late = line.months_elapsed - line.scheduled_months
        return {
            "units_built": 0,
            "airframe_mfg_cost_usd": 0.0,
            "idle_retention_cost_usd": float(idle_cost),
            "lot_learning_factor": 1.0,
            "floor_used_m2": 0.0,
            "months_late": line.months_late,
        }

    line.idle_months = 0
    base_m2_per_rate = float(cfg["factory_m2_per_monthly_rate_10klb"]) * (max(0.35, line.airframe_mass_lb / 10000.0) ** 0.75)
    floor_rate_cap = max(0.0, float(available_floor_m2) / max(1.0, base_m2_per_rate))
    effective_target_rate = min(line.target_rate_per_month, line.tooling_rate_cap_per_month, floor_rate_cap)

    # First-order exponential ramp toward effective_target_rate
    tau = max(1.0, float(cfg["line_ramp_up_tau_months"]))
    alpha = 1.0 - math.exp(-1.0 / tau)
    line.current_rate_per_month = float(line.current_rate_per_month + alpha * (effective_target_rate - line.current_rate_per_month))

    total_output_float = line.fractional_unit_wip + line.current_rate_per_month
    units_built = min(remaining_units, int(math.floor(total_output_float + 1e-9)))
    line.fractional_unit_wip = max(0.0, total_output_float - units_built)

    airframe_cost_usd = 0.0
    lc_factor = 1.0
    if units_built > 0:
        n_start = line.cumulative_units_built + 1
        n_end = line.cumulative_units_built + units_built
        lc_factor = wright_lot_average_factor(
            n_start,
            n_end,
            line.learning_curve_rate,
            break_setback_units=line.break_setback_units,
        )
        airframe_cost_usd = units_built * line.t1_airframe_cost_usd * lc_factor
        line.cumulative_units_built = n_end

    if line.cumulative_units_built >= line.total_quantity_ordered:
        line.completed = True
        line.fractional_unit_wip = 0.0
    elif line.months_elapsed > line.scheduled_months:
        line.months_late = line.months_elapsed - line.scheduled_months

    floor_used = min(float(available_floor_m2), line.current_rate_per_month * base_m2_per_rate)
    return {
        "units_built": int(units_built),
        "airframe_mfg_cost_usd": float(airframe_cost_usd),
        "idle_retention_cost_usd": 0.0,
        "lot_learning_factor": float(lc_factor),
        "floor_used_m2": float(floor_used),
        "months_late": int(line.months_late),
    }


def compute_monthly_spares_and_mods(
    active_delivered_fleet: int,
    avg_airframe_unit_value_1950_usd: float,
    year: float,
    new_units_delivered_this_month: int = 0,
    mod_kits_delivered_this_month: int = 0,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    """Compute monthly initial-provisioning spares, fleet sustainment spares, and modification kit cash flows."""
    cfg = (tuning if tuning is not None else load_econ_tuning())["production"]
    idx = aero_cost_index_1950(year)
    unit_val_then_yr = float(avg_airframe_unit_value_1950_usd) * idx

    init_spares_rev = float(new_units_delivered_this_month) * unit_val_then_yr * float(cfg["spares_initial_provisioning_frac"])
    sust_spares_rev = (float(max(0, active_delivered_fleet)) * unit_val_then_yr * float(cfg["spares_annual_active_fleet_frac"])) / 12.0
    total_spares_rev = init_spares_rev + sust_spares_rev
    spares_cost = total_spares_rev * (1.0 - float(cfg["spares_gross_margin"]))

    mod_rev = float(mod_kits_delivered_this_month) * unit_val_then_yr * float(cfg["modification_kit_airframe_frac"])
    mod_cost = mod_rev * (1.0 - float(cfg["modification_gross_margin"]))

    return {
        "spares_revenue_usd": float(total_spares_rev),
        "spares_cost_usd": float(spares_cost),
        "spares_profit_usd": float(total_spares_rev - spares_cost),
        "modification_revenue_usd": float(mod_rev),
        "modification_cost_usd": float(mod_cost),
        "modification_profit_usd": float(mod_rev - mod_cost),
    }
