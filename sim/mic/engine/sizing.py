"""Engine mass, dimensions, unit cost, MTBF, Duane reliability growth, and maintenance mh/fh."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .cycle import EngineDesignInput
from .tuning import load_engine_tuning


@dataclass(frozen=True)
class EnginePhysicalMetrics:
    mass_kg: float
    diameter_m: float
    length_m: float
    unit_cost_usd: float
    mtbf_initial_h: float
    mtbf_h: float
    maint_mh_per_fh: float


def duane_mtbf(
    mtbf_initial_h: float,
    cumulative_hours: float,
    alpha: float = 0.42,
    ref_hours: float = 1000.0,
    max_multiplier: float = 6.0,
) -> float:
    """Compute instantaneous MTBF under the Duane (1964) / MIL-HDBK-189 reliability growth model.

    Formula:
        MTBF_C(T) = MTBF_initial * (max(T, T_ref) / T_ref)^alpha
        MTBF_inst(T) = MTBF_C(T) / (1 - alpha), normalized so T = T_ref yields MTBF_initial * growth.
    Here we anchor MTBF(T=0) = mtbf_initial_h and grow as:
        multiplier = min(max_multiplier, (1 + T / T_ref)^alpha)
    """
    a = max(0.05, min(0.55, float(alpha)))
    t_h = max(0.0, float(cumulative_hours))
    t_ref = max(100.0, float(ref_hours))
    mult = min(float(max_multiplier), (1.0 + t_h / t_ref) ** a)
    return float(mtbf_initial_h) * mult


def estimate_physical_metrics(
    design: EngineDesignInput,
    tuning: Optional[Dict[str, Any]] = None,
) -> EnginePhysicalMetrics:
    """Estimate mass, diameter, length, unit cost, MTBF, and maintenance mh/fh from cycle design."""
    t = tuning or load_engine_tuning()
    sz = t["sizing"]
    rc = t["reliability_and_cost"]

    mdot = max(5.0, float(design.mass_flow_kgps))
    opr = max(2.0, float(design.opr))
    sqrt_mdot = math.sqrt(mdot)

    # 1. Diameter [m]
    if design.compressor_type == "centrifugal":
        diam = sz["diam_centrifugal_base_m"] + sz["diam_centrifugal_sqrt_mdot_coeff"] * sqrt_mdot
    else:
        diam = sz["diam_axial_base_m"] + sz["diam_axial_sqrt_mdot_coeff"] * sqrt_mdot
    diam *= float(design.diameter_factor)

    # 2. Length [m]
    if design.compressor_type == "centrifugal":
        length = sz["len_centrifugal_base_m"] + sz["len_centrifugal_sqrt_mdot_coeff"] * sqrt_mdot
        if design.has_afterburner:
            length += sz["len_centrifugal_ab_add_m"]
    else:
        core_len = (
            sz["len_axial_base_m"]
            + sz["len_axial_sqrt_mdot_coeff"] * sqrt_mdot
            + sz["len_axial_ln_opr_coeff"] * math.log(opr)
        )
        if design.variable_stators:
            core_len *= sz["len_axial_vsv_factor"]
        length = core_len
        if design.has_afterburner:
            length += sz["len_axial_ab_base_m"] + sz["len_axial_ab_sqrt_mdot_coeff"] * sqrt_mdot
    length *= float(design.length_factor)

    # 3. Dry Mass [kg]
    mdot_ref = 42.0
    mdot_scaled = mdot_ref * ((mdot / mdot_ref) ** sz["mass_mdot_scale_exp"])
    if design.compressor_type == "centrifugal":
        base_mass = (
            sz["mass_centrifugal_per_kgps"]
            * mdot_scaled
            * ((opr / 4.4) ** sz["mass_centrifugal_opr_exp"])
        )
    else:
        base_mass = (
            sz["mass_axial_per_kgps"]
            * mdot_scaled
            * ((opr / 5.0) ** sz["mass_axial_opr_exp"])
        )
        if design.spools == 2:
            base_mass *= sz["mass_twin_spool_factor"]
        if design.variable_stators:
            base_mass *= sz["mass_vsv_factor"]

    if design.has_afterburner:
        base_mass *= sz["mass_ab_multiplier"]

    if design.bypass_ratio > 0.0:
        base_mass *= 1.0 + 0.18 * design.bypass_ratio

    mass_kg = base_mass * float(design.specific_weight_factor)

    # 4. Reliability (MTBF [h]) and Duane maturity growth
    if design.compressor_type == "centrifugal":
        mtbf_base = rc["mtbf_base_centrifugal_h"]
    else:
        mtbf_base = rc["mtbf_base_axial_h"]

    opr_pen = max(0.35, 1.0 - rc["mtbf_opr_penalty_per_unit_above_5"] * max(0.0, opr - 5.0))
    tit_pen = max(
        0.35,
        1.0 - rc["mtbf_tit_penalty_per_100K_above_1100"] * max(0.0, (design.tit_K - 1100.0) / 100.0),
    )
    mtbf_init = mtbf_base * opr_pen * tit_pen * float(design.mtbf_factor)
    if design.has_afterburner:
        mtbf_init *= rc["mtbf_ab_penalty_factor"]
    if design.spools == 2:
        mtbf_init *= rc["mtbf_twin_spool_penalty_factor"]

    mtbf_current = duane_mtbf(
        mtbf_initial_h=mtbf_init,
        cumulative_hours=design.cumulative_test_hours,
        alpha=rc["duane_alpha_default"],
        ref_hours=rc["duane_ref_hours"],
        max_multiplier=rc["duane_max_multiplier"],
    )

    # 5. Maintenance Man-Hours per Flight Hour (MMH/FH)
    if design.compressor_type == "centrifugal":
        maint = rc["maint_base_mh_per_fh_centrifugal"]
    else:
        maint = rc["maint_base_mh_per_fh_axial"] + rc["maint_opr_coeff"] * max(0.0, opr - 5.0)
    if design.has_afterburner:
        maint += rc["maint_ab_add_mh_per_fh"]
    if design.spools == 2:
        maint += rc["maint_twin_spool_add_mh_per_fh"]
    maint = maint / max(0.5, float(design.mtbf_factor) ** 0.5)

    # 6. Unit Flyaway Cost (then-year USD)
    cost = (rc["unit_cost_base_usd_1950"] + rc["unit_cost_per_kgps_usd"] * mdot) * (
        (opr / 5.0) ** rc["unit_cost_opr_exp"]
    )
    if design.compressor_type == "centrifugal":
        cost *= rc["unit_cost_centrifugal_multiplier"]
    if design.has_afterburner:
        cost *= rc["unit_cost_ab_multiplier"]
    if design.spools == 2:
        cost *= rc["unit_cost_twin_spool_multiplier"]
    if design.variable_stators:
        cost *= rc["unit_cost_vsv_multiplier"]

    return EnginePhysicalMetrics(
        mass_kg=mass_kg,
        diameter_m=diam,
        length_m=length,
        unit_cost_usd=cost,
        mtbf_initial_h=mtbf_init,
        mtbf_h=mtbf_current,
        maint_mh_per_fh=maint,
    )
