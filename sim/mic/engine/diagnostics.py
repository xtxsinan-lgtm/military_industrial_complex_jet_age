"""Engine diagnostics dictionary for Module 06 (testing, uncertainty, hidden flaws).

Computes quantitative stability, surge, flameout, afterburner light-off, and intake
compatibility metrics that drive `testing.flaw_incidence.engine_stall` and
`testing.flaw_incidence.inlet` in Module 06.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .deck import EngineSpec
from .tuning import load_engine_tuning


def compute_diagnostics(
    engine: EngineSpec,
    design_max_mach: float = 0.95,
    design_ceiling_m: float = 12000.0,
    inlet_location: str = "nose",
    inlet_spike: bool = False,
    inlet_variable: bool = False,
    tech_maturity_engine: float = 1.0,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Compute `engine_diagnostics` dict consumed by Module 06.

    Returns a dictionary with:
    - compressor_surge_margin: float in [0.02, 0.40] (stall margin ratio Delta_PR / PR_op; <0.12 risky)
    - high_alt_flameout_risk: float in [0.0, 1.0] (probability weight of combustor blowout near ceiling)
    - ab_lightoff_reliability: float in [0.0, 1.0] (probability of clean AB light-off at altitude)
    - intake_compatibility: float in [0.0, 1.0] (distortion & shock-stability compatibility score)
    - thermal_margin_K: float (headroom before accelerated creep/rupture of HP turbine blades)
    - flaw_Verify_multipliers: dict mapping Module 06 flaw families (`engine_stall`, `inlet`) to
      incidence multipliers based on engine-airframe pairing.
    """
    t = tuning or load_engine_tuning()
    diag_cfg = t["diagnostics"]
    d = engine.design_input

    opr = d.opr if d is not None else 5.5
    tit_K = d.tit_K if d is not None else 1120.0
    comp_type = engine.compressor_type
    spools = engine.spools
    vsv = engine.variable_stators

    # 1. Compressor surge margin (stall margin fraction)
    if comp_type == "centrifugal":
        base_sm = diag_cfg["base_surge_margin_centrifugal"]
        sm = base_sm - 0.015 * max(0.0, opr - 4.0)
    elif spools == 2:
        base_sm = diag_cfg["base_surge_margin_twin_spool"]
        sm = base_sm - diag_cfg["surge_opr_slope_vsv_or_twin"] * max(0.0, opr - 8.0)
    elif vsv:
        base_sm = diag_cfg["base_surge_margin_axial_vsv"]
        sm = base_sm - diag_cfg["surge_opr_slope_vsv_or_twin"] * max(0.0, opr - 8.0)
    else:
        base_sm = diag_cfg["base_surge_margin_axial_fixed"]
        sm = base_sm - diag_cfg["surge_opr_slope_fixed"] * max(0.0, opr - 5.0)

    # Inlet distortion penalty on surge margin (wing-root/cheek ducts distort flow at high alpha/Mach)
    loc_distortion = {
        "nose": 0.00,
        "chin": 0.01,
        "cheek": 0.025,
        "wing_root": 0.035,
    }.get(inlet_location, 0.015)

    # Supersonic shock-expulsion / buzz penalty if inlet lacks spike/variable geometry
    shock_mismatch_penalty = 0.0
    if design_max_mach > 1.35 and not (inlet_spike or inlet_variable):
        shock_mismatch_penalty += 0.04 * (design_max_mach - 1.35)
    if design_max_mach > 1.85 and not inlet_variable:
        shock_mismatch_penalty += 0.06 * (design_max_mach - 1.85)

    # Immature tech penalty
    maturity_pen = 0.04 * (1.0 - max(0.0, min(1.0, float(tech_maturity_engine))))
    surge_margin = max(0.02, min(0.40, sm - loc_distortion - shock_mismatch_penalty - maturity_pen))

    # 2. High-altitude flameout risk (combustor loading parameter P3 * T3 / V_ref at ceiling)
    # Centrifugal can combustors & high-OPR twin-spool combustors resist blowout better than early low-OPR axials
    ceil_ref = diag_cfg["flameout_base_ceil_m"] + 250.0 * (opr - 5.0)
    if comp_type == "centrifugal":
        ceil_ref += 1000.0
    alt_excess = max(0.0, design_ceiling_m - ceil_ref)
    flameout_risk = min(0.95, 0.05 + 0.00008 * (alt_excess ** 1.35) + 0.15 * (1.0 - tech_maturity_engine))
    if surge_margin < 0.12:
        flameout_risk = min(0.95, flameout_risk + 1.5 * (0.12 - surge_margin))

    # 3. Afterburner light-off reliability at altitude
    if engine.has_afterburner:
        base_ab = diag_cfg["ab_lightoff_base_prob"]
        alt_pen = 0.03 * max(0.0, (design_ceiling_m - 12000.0) / 1000.0)
        ab_rel = max(0.50, min(0.995, base_ab - alt_pen - 0.10 * (1.0 - tech_maturity_engine)))
    else:
        ab_rel = 1.0

    # 4. Intake compatibility score [0, 1]
    inlet_compat = 1.0 - 2.5 * (loc_distortion + shock_mismatch_penalty)
    if comp_type == "centrifugal" and inlet_location in ("cheek", "wing_root"):
        # Double-sided centrifugal plenum tolerates bifurcated cheek/wing-root ducts well
        inlet_compat += 0.05
    inlet_compat = max(0.10, min(1.0, inlet_compat))

    # 5. Turbine thermal margin [K]
    cooled = d.cooled_turbine if d is not None else False
    safe_tit = 1220.0 if cooled else 1135.0
    thermal_margin_K = safe_tit - tit_K

    # 6. Flaw incidence multipliers for Module 06
    stall_mult = max(0.4, min(3.5, (0.16 / max(0.03, surge_margin)) * (1.0 + 0.5 * flameout_risk)))
    inlet_mult = max(0.4, min(3.5, 1.0 / max(0.25, inlet_compat)))

    return {
        "engine_id": engine.engine_id,
        "compressor_surge_margin": round(surge_margin, 4),
        "high_alt_flameout_risk": round(flameout_risk, 4),
        "ab_lightoff_reliability": round(ab_rel, 4),
        "intake_compatibility": round(inlet_compat, 4),
        "thermal_margin_K": round(thermal_margin_K, 2),
        "flaw_incidence_multipliers": {
            "engine_stall": round(stall_mult, 4),
            "inlet": round(inlet_mult, 4),
        },
    }
