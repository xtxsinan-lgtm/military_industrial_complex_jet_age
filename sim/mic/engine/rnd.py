"""Engine R&D project mechanics, ambition vs TechContext frontier, and outcome distributions.

Aligns strictly with `docs/spec/03_tech_effect_keys.md` §2.3 (`engine.*` keys):
- `engine.centrifugal_compressor`
- `engine.axial_compressor`
- `engine.twin_spool`
- `engine.variable_stators`
- `engine.afterburner`
- `engine.afterburner_temp_max_K`
- `engine.low_bypass_turbofan`
- `engine.bypass_ratio_max`
- `engine.tit_max_K`
- `engine.cooled_turbine_blades`
- `engine.opr_max`
- `engine.opr_max_single_spool_fixed`
- `engine.eta_compressor_poly`
- `engine.eta_turbine_poly`
- `engine.mass_flow_max_kgps`
- `engine.specific_weight_factor`
- `engine.mtbf_factor`
- `engine.dev_cost_factor`
- `engine.dev_risk_factor`
"""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .cycle import EngineDesignInput
from .deck import EngineSpec, design_engine
from .tuning import load_engine_tuning

DEFAULT_START_1945_ENGINE_TECH: Dict[str, Any] = {
    "engine.centrifugal_compressor": True,
    "engine.axial_compressor": True,
    "engine.twin_spool": False,
    "engine.variable_stators": False,
    "engine.afterburner": False,
    "engine.afterburner_temp_max_K": 0.0,
    "engine.low_bypass_turbofan": False,
    "engine.bypass_ratio_max": 0.0,
    "engine.tit_max_K": 1090.0,
    "engine.cooled_turbine_blades": False,
    "engine.opr_max": 5.0,
    "engine.opr_max_single_spool_fixed": 5.0,
    "engine.eta_compressor_poly": 0.83,
    "engine.eta_turbine_poly": 0.86,
    "engine.mass_flow_max_kgps": 40.0,
    "engine.specific_weight_factor": 1.0,
    "engine.mtbf_factor": 1.0,
    "engine.dev_cost_factor": 1.0,
    "engine.dev_risk_factor": 1.0,
}


def _ctx_get(tech_ctx: Any, key: str) -> Any:
    """Read key from a TechContext object or a plain dict."""
    if isinstance(tech_ctx, dict):
        if "values" in tech_ctx and isinstance(tech_ctx["values"], dict):
            return tech_ctx["values"][key]
        return tech_ctx[key]
    if hasattr(tech_ctx, "get") and callable(tech_ctx.get):
        return tech_ctx.get(key)
    raise KeyError(f"Cannot read key '{key}' from tech_ctx of type {type(tech_ctx)}")


def _ctx_maturity(tech_ctx: Any, key: str) -> float:
    """Read maturity in [0, 1] for key from TechContext or dict (defaults to 1.0)."""
    if hasattr(tech_ctx, "maturity_of") and callable(tech_ctx.maturity_of):
        return float(tech_ctx.maturity_of(key))
    if isinstance(tech_ctx, dict) and "maturity" in tech_ctx:
        return float(tech_ctx["maturity"].get(key, 1.0))
    return 1.0


def validate_engine_against_tech(
    target: EngineDesignInput,
    tech_ctx: Any,
) -> List[str]:
    """Validate target engine parameters against TechContext hard caps.

    Returns a list of error codes `TECH_CAP:<key>` (empty list if valid).
    """
    errors: List[str] = []

    if target.compressor_type == "centrifugal":
        if not bool(_ctx_get(tech_ctx, "engine.centrifugal_compressor")):
            errors.append("TECH_CAP:engine.centrifugal_compressor")
    elif target.compressor_type == "axial":
        if not bool(_ctx_get(tech_ctx, "engine.axial_compressor")):
            errors.append("TECH_CAP:engine.axial_compressor")
    else:
        errors.append(f"INVALID_COMPRESSOR_TYPE:{target.compressor_type}")

    if target.spools == 2 and not bool(_ctx_get(tech_ctx, "engine.twin_spool")):
        errors.append("TECH_CAP:engine.twin_spool")

    if target.variable_stators and not bool(_ctx_get(tech_ctx, "engine.variable_stators")):
        errors.append("TECH_CAP:engine.variable_stators")

    if target.has_afterburner:
        if not bool(_ctx_get(tech_ctx, "engine.afterburner")):
            errors.append("TECH_CAP:engine.afterburner")
        ab_max = float(_ctx_get(tech_ctx, "engine.afterburner_temp_max_K"))
        if target.ab_temp_K > ab_max + 1e-6:
            errors.append("TECH_CAP:engine.afterburner_temp_max_K")

    if target.bypass_ratio > 0.0:
        if not bool(_ctx_get(tech_ctx, "engine.low_bypass_turbofan")):
            errors.append("TECH_CAP:engine.low_bypass_turbofan")
        bpr_max = float(_ctx_get(tech_ctx, "engine.bypass_ratio_max"))
        if target.bypass_ratio > bpr_max + 1e-6:
            errors.append("TECH_CAP:engine.bypass_ratio_max")

    if target.cooled_turbine and not bool(_ctx_get(tech_ctx, "engine.cooled_turbine_blades")):
        errors.append("TECH_CAP:engine.cooled_turbine_blades")

    tit_max = float(_ctx_get(tech_ctx, "engine.tit_max_K"))
    if target.tit_K > tit_max + 1e-6:
        errors.append("TECH_CAP:engine.tit_max_K")

    opr_max = float(_ctx_get(tech_ctx, "engine.opr_max"))
    if target.opr > opr_max + 1e-6:
        errors.append("TECH_CAP:engine.opr_max")

    if target.compressor_type == "axial" and target.spools == 1 and not target.variable_stators:
        opr_ss_max = float(_ctx_get(tech_ctx, "engine.opr_max_single_spool_fixed"))
        if target.opr > opr_ss_max + 1e-6:
            errors.append("TECH_CAP:engine.opr_max_single_spool_fixed")

    if target.compressor_type == "centrifugal" and target.opr > 5.0 + 1e-6:
        errors.append("ARCH_CAP:centrifugal_opr_max_5.0")

    mdot_max = float(_ctx_get(tech_ctx, "engine.mass_flow_max_kgps"))
    if target.mass_flow_kgps > mdot_max + 1e-6:
        errors.append("TECH_CAP:engine.mass_flow_max_kgps")

    eta_c_max = float(_ctx_get(tech_ctx, "engine.eta_compressor_poly"))
    if target.eta_c_poly > eta_c_max + 1e-6:
        errors.append("TECH_CAP:engine.eta_compressor_poly")

    eta_t_max = float(_ctx_get(tech_ctx, "engine.eta_turbine_poly"))
    if target.eta_t_poly > eta_t_max + 1e-6:
        errors.append("TECH_CAP:engine.eta_turbine_poly")

    return errors


def compute_ambition(
    target: EngineDesignInput,
    tech_ctx: Any,
    parent_engine: Optional[EngineDesignInput] = None,
) -> float:
    """Compute dimensionless R&D ambition metric A in [0.0, 1.5].

    Measures how aggressively `target` pushes the company's current `engine.*`
    technology frontier (OPR, TIT, mass flow, AB temperature) and accounts for
    the maturity of unlocked architecture features.
    """
    tit_max = float(_ctx_get(tech_ctx, "engine.tit_max_K"))
    opr_max = float(_ctx_get(tech_ctx, "engine.opr_max"))
    if target.compressor_type == "axial" and target.spools == 1 and not target.variable_stators:
        opr_max = min(opr_max, float(_ctx_get(tech_ctx, "engine.opr_max_single_spool_fixed")))
    elif target.compressor_type == "centrifugal":
        opr_max = min(opr_max, 5.0)
    mdot_max = float(_ctx_get(tech_ctx, "engine.mass_flow_max_kgps"))

    # Normalized frontier fractions in [0, 1+]
    u_tit = max(0.0, (target.tit_K - 980.0) / max(50.0, tit_max - 980.0))
    u_opr = max(0.0, (target.opr - 3.5) / max(1.0, opr_max - 3.5))
    u_mdot = max(0.0, (target.mass_flow_kgps - 20.0) / max(10.0, mdot_max - 20.0))

    weights = [0.35, 0.35, 0.30]
    u_vals = [u_tit, u_opr, u_mdot]

    if target.has_afterburner:
        ab_max = max(1800.0, float(_ctx_get(tech_ctx, "engine.afterburner_temp_max_K")))
        u_ab = max(0.0, (target.ab_temp_K - 1650.0) / max(100.0, ab_max - 1650.0))
        weights = [0.28, 0.28, 0.24, 0.20]
        u_vals.append(u_ab)

    # RMS weighted frontier utilization, emphasizing whichever parameter pushes the cap hardest
    mean_u = sum(w * (u ** 2) for w, u in zip(weights, u_vals)) ** 0.5

    # Immaturity penalty from key architecture techs used
    immaturity_add = 0.0
    if target.spools == 2:
        immaturity_add += 0.15 * (1.0 - _ctx_maturity(tech_ctx, "engine.twin_spool"))
    if target.variable_stators:
        immaturity_add += 0.15 * (1.0 - _ctx_maturity(tech_ctx, "engine.variable_stators"))
    if target.has_afterburner:
        immaturity_add += 0.12 * (1.0 - _ctx_maturity(tech_ctx, "engine.afterburner"))
    if target.compressor_type == "axial":
        immaturity_add += 0.10 * (1.0 - _ctx_maturity(tech_ctx, "engine.axial_compressor"))

    ambition = mean_u + immaturity_add

    if parent_engine is not None:
        # Derivative project ambition scales with delta from parent
        d_mdot = abs(target.mass_flow_kgps - parent_engine.mass_flow_kgps) / max(
            10.0, parent_engine.mass_flow_kgps
        )
        d_opr = abs(target.opr - parent_engine.opr) / max(2.0, parent_engine.opr)
        d_tit = abs(target.tit_K - parent_engine.tit_K) / 100.0
        ab_added = 0.25 if (target.has_afterburner and not parent_engine.has_afterburner) else 0.0
        deriv_amb = 0.20 + 0.80 * (d_mdot + d_opr + 0.5 * d_tit) + ab_added
        ambition = min(ambition, deriv_amb)

    return max(0.05, min(1.50, ambition))


@dataclass
class EngineProjectEstimate:
    """Cost, schedule, and risk estimates for an engine R&D or derivative project."""

    procurement_mode: str  # "catalog" | "custom_commission" | "inhouse" | "derivative"
    ambition: float
    total_dev_cost_usd: float
    player_cost_share_usd: float
    expected_duration_days: int
    thrust_sigma_rel: float
    tsfc_sigma_rel: float
    mass_sigma_rel: float
    schedule_sigma_rel: float
    catastrophic_flaw_prob: float


@dataclass
class EngineProjectOutcome:
    """Realized engine spec and development outcome after stochastic completion."""

    engine_spec: EngineSpec
    realized_design: EngineDesignInput
    actual_duration_days: int
    actual_player_cost_usd: float
    thrust_multiplier: float
    tsfc_multiplier: float
    mass_multiplier: float
    has_severe_flaw: bool
    flaw_description: Optional[str]


@dataclass
class EngineProjectState:
    """Daily-tick stateful Engine R&D project for campaign integration."""

    project_id: str
    target_design: EngineDesignInput
    estimate: EngineProjectEstimate
    priority_weight: float = 1.0
    progress_days_equivalent: float = 0.0
    calendar_days_elapsed: int = 0
    spent_usd: float = 0.0
    completed: bool = False
    outcome: Optional[EngineProjectOutcome] = None
    parent_engine: Optional[EngineDesignInput] = None


def evaluate_rnd_project(
    target: EngineDesignInput,
    tech_ctx: Any,
    procurement_mode: str = "custom_commission",
    parent_engine: Optional[EngineDesignInput] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> EngineProjectEstimate:
    """Estimate development cost, duration, and outcome uncertainty for an engine project.

    Modes:
    - `catalog`: Off-the-shelf historical/existing engine ($0 dev cost, 0 days, catalog markup on unit cost).
    - `custom_commission`: Contract an external engine manufacturer (e.g., P&W, GE, Allison, Wright)
      to develop a custom engine; airframer pays `custom_commission_fee_multiplier` (default 60%) of R&D cost.
    - `inhouse`: Develop inside the airframer's own propulsion division (100% dev cost, lower unit cost,
      eligible for third-party licensing royalties).
    - `derivative`: Uprate/afterburner modification of an existing `parent_engine` (~32% cost, ~42% duration).
    """
    t = tuning or load_engine_tuning()
    rcfg = t["rnd"]

    if procurement_mode == "catalog":
        return EngineProjectEstimate(
            procurement_mode="catalog",
            ambition=0.0,
            total_dev_cost_usd=0.0,
            player_cost_share_usd=0.0,
            expected_duration_days=0,
            thrust_sigma_rel=0.0,
            tsfc_sigma_rel=0.0,
            mass_sigma_rel=0.0,
            schedule_sigma_rel=0.0,
            catastrophic_flaw_prob=0.0,
        )

    amb = compute_ambition(target, tech_ctx, parent_engine=parent_engine)
    dev_cost_factor = float(_ctx_get(tech_ctx, "engine.dev_cost_factor"))
    dev_risk_factor = float(_ctx_get(tech_ctx, "engine.dev_risk_factor"))

    # Base development cost
    mdot_ratio = max(0.3, target.mass_flow_kgps / rcfg["dev_cost_mdot_ref_kgps"])
    cost = (
        rcfg["base_dev_cost_usd_1950"]
        * (mdot_ratio ** rcfg["dev_cost_mdot_exp"])
        * (1.0 + rcfg["dev_cost_ambition_quad_coeff"] * (amb ** 2))
        * dev_cost_factor
    )
    if target.has_afterburner:
        cost *= rcfg["dev_cost_ab_multiplier"]
    if target.spools == 2:
        cost *= rcfg["dev_cost_twin_spool_multiplier"]
    if target.variable_stators:
        cost *= rcfg["dev_cost_vsv_multiplier"]

    # Base development duration (days)
    days = rcfg["base_dev_days"] + rcfg["dev_days_ambition_slope"] * (amb ** 1.35)
    if target.has_afterburner:
        days += rcfg["dev_days_ab_add"]
    if target.spools == 2:
        days += rcfg["dev_days_twin_spool_add"]

    if procurement_mode == "derivative" or parent_engine is not None:
        cost *= rcfg["derivative_cost_fraction"]
        days *= rcfg["derivative_days_fraction"]

    if procurement_mode == "custom_commission":
        player_share = cost * rcfg["custom_commission_fee_multiplier"]
    else:
        player_share = cost

    # Risk sigmas
    thrust_sigma = (
        rcfg["risk_thrust_sigma_base"] + rcfg["risk_thrust_sigma_ambition_slope"] * (amb ** 1.5)
    ) * dev_risk_factor
    tsfc_sigma = (
        rcfg["risk_tsfc_sigma_base"] + rcfg["risk_tsfc_sigma_ambition_slope"] * (amb ** 1.5)
    ) * dev_risk_factor
    mass_sigma = (
        rcfg["risk_mass_sigma_base"] + rcfg["risk_mass_sigma_ambition_slope"] * (amb ** 1.5)
    ) * dev_risk_factor
    sched_sigma = (0.06 + 0.18 * (amb ** 1.5)) * dev_risk_factor

    # Catastrophic flaw probability (e.g. Westinghouse J40 / Curtiss-Wright J67 style crisis)
    thresh = rcfg["catastrophic_flaw_ambition_threshold"]
    if amb <= thresh:
        cat_prob = 0.02 * (amb / thresh) * dev_risk_factor
    else:
        excess = (amb - thresh) / (1.0 - thresh)
        cat_prob = min(
            rcfg["catastrophic_flaw_max_prob"],
            (0.02 + 0.28 * (excess ** 1.6)) * dev_risk_factor,
        )

    return EngineProjectEstimate(
        procurement_mode=procurement_mode,
        ambition=amb,
        total_dev_cost_usd=cost,
        player_cost_share_usd=player_share,
        expected_duration_days=int(round(days)),
        thrust_sigma_rel=thrust_sigma,
        tsfc_sigma_rel=tsfc_sigma,
        mass_sigma_rel=mass_sigma,
        schedule_sigma_rel=sched_sigma,
        catastrophic_flaw_prob=cat_prob,
    )


def resolve_rnd_outcome(
    target: EngineDesignInput,
    estimate: EngineProjectEstimate,
    rng: np.random.Generator,
    build_deck: bool = True,
    tuning: Optional[Dict[str, Any]] = None,
) -> EngineProjectOutcome:
    """Sample stochastic R&D outcome using an explicit numpy Generator (`00_conventions.md` §3)."""
    t = tuning or load_engine_tuning()
    amb = estimate.ambition

    # High ambition introduces slight negative mean bias on thrust and positive bias on TSFC/mass/schedule
    mean_thrust_bias = -0.025 * max(0.0, amb - 0.55)
    mean_tsfc_bias = +0.020 * max(0.0, amb - 0.55)
    mean_mass_bias = +0.030 * max(0.0, amb - 0.55)
    mean_sched_bias = +0.080 * max(0.0, amb - 0.50)

    z_thrust = float(rng.normal(mean_thrust_bias, estimate.thrust_sigma_rel))
    z_tsfc = float(rng.normal(mean_tsfc_bias, estimate.tsfc_sigma_rel))
    z_mass = float(rng.normal(mean_mass_bias, estimate.mass_sigma_rel))
    z_sched = float(rng.normal(mean_sched_bias, estimate.schedule_sigma_rel))

    flaw_roll = float(rng.random())
    has_flaw = flaw_roll < estimate.catastrophic_flaw_prob
    flaw_desc: Optional[str] = None

    if has_flaw:
        # J40 / J67 style severe setback: thrust shortfall, higher SFC, schedule slip, lower MTBF
        z_thrust -= float(rng.uniform(0.06, 0.14))
        z_tsfc += float(rng.uniform(0.04, 0.10))
        z_sched += float(rng.uniform(0.18, 0.40))
        flaw_desc = (
            "Severe compressor surge and hot-section distress discovered during qualification; "
            "engine de-rated pending redesign."
        )

    thrust_mult = max(0.75, min(1.12, 1.0 + z_thrust))
    tsfc_mult = max(0.92, min(1.25, 1.0 + z_tsfc))
    mass_mult = max(0.88, min(1.30, 1.0 + z_mass))
    sched_mult = max(0.80, min(1.85, 1.0 + z_sched))

    realized = copy.deepcopy(target)
    realized.mass_flow_kgps = target.mass_flow_kgps * thrust_mult
    realized.eta_c_poly = max(0.72, min(0.92, target.eta_c_poly / (tsfc_mult ** 0.6)))
    realized.specific_weight_factor = target.specific_weight_factor * (mass_mult / thrust_mult)
    if has_flaw:
        realized.mtbf_factor = target.mtbf_factor * 0.55
    realized.cumulative_test_hours = 250.0  # Newly qualified engine starts at 250 test hours

    spec = design_engine(realized, build_deck=build_deck, tuning=t)
    actual_days = max(90, int(round(estimate.expected_duration_days * sched_mult)))
    actual_cost = estimate.player_cost_share_usd * (0.5 + 0.5 * sched_mult)

    return EngineProjectOutcome(
        engine_spec=spec,
        realized_design=realized,
        actual_duration_days=actual_days,
        actual_player_cost_usd=actual_cost,
        thrust_multiplier=thrust_mult,
        tsfc_multiplier=tsfc_mult,
        mass_multiplier=mass_mult,
        has_severe_flaw=has_flaw,
        flaw_description=flaw_desc,
    )


def allocate_rnd_priorities(
    projects: List[EngineProjectState],
    propulsion_engineers: int,
    engineers_per_full_speed_project: int = 40,
) -> Dict[str, float]:
    """Compute daily progress rate (in effective days per calendar day) for active engine projects."""
    active = [p for p in projects if not p.completed and p.priority_weight > 0.0]
    if not active:
        return {p.project_id: 0.0 for p in projects}

    total_weight = sum(p.priority_weight for p in active)
    rates: Dict[str, float] = {}
    for p in projects:
        if p.completed or p.priority_weight <= 0.0:
            rates[p.project_id] = 0.0
            continue
        share = p.priority_weight / total_weight
        assigned_eng = propulsion_engineers * share
        # Diminishing returns above 1.35x nominal staffing
        staff_ratio = assigned_eng / max(1.0, float(engineers_per_full_speed_project))
        if staff_ratio <= 1.0:
            rate = staff_ratio ** 0.85
        else:
            rate = min(1.35, 1.0 + 0.25 * math.log(staff_ratio))
        rates[p.project_id] = rate
    return rates


def compute_third_party_engine_sale(
    engine: EngineSpec,
    quantity: int,
    is_inhouse_engine: bool,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    """Compute revenue and royalty when selling an in-house engine to another airframer.

    Rule (answering GDD §18.2 open question):
    - Only companies with an in-house engine division (`is_inhouse_engine=True`) own the
      manufacturing rights to sell engines or license them to third-party airframers.
    - Commissioned engines (`custom_commission`) belong to the propulsion vendor (P&W, GE, etc.),
      though the commissioning airframer gets a 18-month exclusivity window before the engine
      enters the general catalog.
    """
    t = tuning or load_engine_tuning()
    rcfg = t["rnd"]
    if not is_inhouse_engine or quantity <= 0:
        return {"gross_revenue_usd": 0.0, "net_profit_usd": 0.0, "royalty_usd": 0.0}

    markup = rcfg["catalog_markup_multiplier"]
    royalty_rate = rcfg["third_party_license_royalty_rate"]
    unit_price = engine.unit_cost * markup
    gross = unit_price * quantity
    net_profit = (unit_price - engine.unit_cost) * quantity
    royalty = engine.unit_cost * royalty_rate * quantity
    return {
        "gross_revenue_usd": gross,
        "net_profit_usd": net_profit,
        "royalty_usd": royalty,
    }
