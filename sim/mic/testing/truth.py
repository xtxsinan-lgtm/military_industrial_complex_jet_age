"""TrueAircraft vs. EstimateReport dual representation, prior calculation, and variant inheritance."""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from .data_loader import load_drivers_data, load_testing_tuning
from .features import (
    StubTechContext,
    build_feature_vector,
    compute_5d_coords,
    compute_categorical_signature,
)
from .flaws import ActiveFlawState, build_risk_watchlist, compute_fix_cost_and_days, get_flaw_catalog_map, realize_true_flaws
from .hashing import driver_z_draw
from .novelty import (
    ExperienceLedger,
    compute_active_novelty_features,
    compute_driver_novelty_scores,
    compute_engineering_quality_multipliers,
    compute_regime_multipliers,
    compute_tech_maturity_multiplier,
)

SOURCE_RANK = {"sim": 0, "tunnel": 1, "flight": 2, "service": 3}


@dataclass
class DriverBelief:
    driver_id: str
    mu_belief: float
    var_belief: float
    best_source: str = "sim"
    tunnel_floor_var: float = 0.0


@dataclass
class TrueAircraft:
    design_id: str
    company_id: str
    categorical_sig: str
    coords_5d: Tuple[float, float, float, float, float]
    feature_vector: Dict[str, float]
    driver_priors: Dict[str, Dict[str, float]]  # {d: {mu0, sigma_prior, z_draw, N_d, R_d, Q_d}}
    driver_theta_base: Dict[str, float]         # base log-deviation without flaws
    active_flaws: Dict[str, ActiveFlawState]
    applied_fixes: Set[str] = field(default_factory=set)
    fix_driver_deltas: Dict[str, float] = field(default_factory=dict)
    fix_metric_multipliers: Dict[str, float] = field(default_factory=dict)
    placard_metric_multipliers: Dict[str, float] = field(default_factory=dict)

    def get_true_driver_theta(self, driver_id: str) -> float:
        """Total true driver log-deviation including active flaws and applied fixes (§5.3.5)."""
        theta = float(self.driver_theta_base.get(driver_id, 0.0))
        theta += float(self.fix_driver_deltas.get(driver_id, 0.0))
        flaw_map = get_flaw_catalog_map()
        for fid, fstate in self.active_flaws.items():
            f_entry = flaw_map[fid]
            delta = float(f_entry["truth_effects"].get("driver_log_deltas", {}).get(driver_id, 0.0))
            theta += fstate.residual_factor * delta
        return theta


@dataclass
class LineageTestState:
    lineage_id: str
    design: Dict[str, Any]
    nominal_perf: Dict[str, Any]
    true_aircraft: TrueAircraft
    beliefs: Dict[str, DriverBelief]
    date_day: int = 0
    campaign_seq: int = 0
    prototypes_built: int = 0
    prototypes_surviving: int = 0
    prototype_rolled_out: bool = False
    known_flaws_company: Set[str] = field(default_factory=set)
    event_log: List[str] = field(default_factory=list)
    total_testing_cost_usd: float = 0.0
    total_testing_days: int = 0


def generate_true_aircraft(
    campaign_seed: int,
    design: Dict[str, Any],
    nominal_perf: Dict[str, Any],
    date_day: int = 0,
    aero_diagnostics: Optional[Dict[str, Any]] = None,
    engine_diagnostics: Optional[Dict[str, Any]] = None,
    tech_ctx: Optional[Any] = None,
    ledger: Optional[ExperienceLedger] = None,
    engineer_ratings: Optional[Dict[str, float]] = None,
) -> TrueAircraft:
    """Deterministically construct `TrueAircraft` for a design (§5.1–§5.3)."""
    ctx = tech_ctx if tech_ctx is not None else StubTechContext(date_day=date_day)
    tuning = load_testing_tuning()
    drivers_spec = load_drivers_data()["drivers"]

    feat = build_feature_vector(design, nominal_perf, aero_diagnostics, engine_diagnostics, ctx)
    cat_sig = compute_categorical_signature(design, feat)
    coords_5d = compute_5d_coords(feat)
    company_id = str(design.get("company_id", "player_co"))
    design_id = str(design.get("id", "design_001"))

    nov_scores = compute_driver_novelty_scores(feat, date_day, ledger)
    reg_mults = compute_regime_multipliers(feat["max_mach_nom"])
    m_tech = compute_tech_maturity_multiplier(design.get("techs_used", []), ctx)
    q_mults = compute_engineering_quality_multipliers(engineer_ratings)

    alpha_nov = float(tuning["alpha_novelty"])
    rho_cat = float(tuning["categorical_noise_weight"])
    theta_min = float(tuning["driver_theta_min"])
    theta_max = float(tuning["driver_theta_max"])
    sim_sigma_factor = float(ctx.get("testing.sim_sigma_factor"))

    driver_priors: Dict[str, Dict[str, float]] = {}
    driver_theta_base: Dict[str, float] = {}

    for d, d_info in drivers_spec.items():
        s_d = float(d_info["unfavorable_sign"])
        sigma0 = float(d_info["sigma0"])
        bias0 = float(d_info["bias0"])
        n_d = nov_scores[d]
        r_d = reg_mults[d]
        q_d = q_mults[d]

        mu0 = s_d * bias0 * n_d * m_tech * q_d * sim_sigma_factor
        sigma_prior = sigma0 * (1.0 + alpha_nov * n_d) * r_d * m_tech * q_d * sim_sigma_factor
        z_d = driver_z_draw(campaign_seed, cat_sig, company_id, d, coords_5d, rho_cat)
        theta_base = max(theta_min, min(theta_max, mu0 + sigma_prior * z_d))

        driver_priors[d] = {
            "mu0": mu0,
            "sigma_prior": sigma_prior,
            "z_draw": z_d,
            "N_d": n_d,
            "R_d": r_d,
            "M_tech": m_tech,
            "Q_d": q_d,
        }
        driver_theta_base[d] = theta_base

    active_flaws = realize_true_flaws(campaign_seed, cat_sig, feat, date_day, ledger, ctx)

    return TrueAircraft(
        design_id=design_id,
        company_id=company_id,
        categorical_sig=cat_sig,
        coords_5d=coords_5d,
        feature_vector=feat,
        driver_priors=driver_priors,
        driver_theta_base=driver_theta_base,
        active_flaws=active_flaws,
    )


def initialize_lineage_state(
    campaign_seed: int,
    design: Dict[str, Any],
    nominal_perf: Dict[str, Any],
    date_day: int = 0,
    aero_diagnostics: Optional[Dict[str, Any]] = None,
    engine_diagnostics: Optional[Dict[str, Any]] = None,
    tech_ctx: Optional[Any] = None,
    ledger: Optional[ExperienceLedger] = None,
    engineer_ratings: Optional[Dict[str, float]] = None,
) -> LineageTestState:
    """Create initial `LineageTestState` with `sim` source prior beliefs (§5.3.6)."""
    true_ac = generate_true_aircraft(
        campaign_seed=campaign_seed,
        design=design,
        nominal_perf=nominal_perf,
        date_day=date_day,
        aero_diagnostics=aero_diagnostics,
        engine_diagnostics=engine_diagnostics,
        tech_ctx=tech_ctx,
        ledger=ledger,
        engineer_ratings=engineer_ratings,
    )
    beliefs: Dict[str, DriverBelief] = {}
    for d, p_info in true_ac.driver_priors.items():
        var0 = (p_info["sigma_prior"] ** 2) + (p_info["mu0"] ** 2)
        beliefs[d] = DriverBelief(
            driver_id=d,
            mu_belief=0.0,
            var_belief=var0,
            best_source="sim",
        )
    lineage_id = str(design.get("id", "lineage_001"))
    return LineageTestState(
        lineage_id=lineage_id,
        design=copy.deepcopy(design),
        nominal_perf=copy.deepcopy(nominal_perf),
        true_aircraft=true_ac,
        beliefs=beliefs,
        date_day=int(date_day),
    )


def compute_true_performance_report(state: LineageTestState) -> Dict[str, Any]:
    """Compute hidden `TrueAircraft` performance report (§5.4)."""
    metrics_spec = load_drivers_data()["metrics"]
    true_ac = state.true_aircraft
    flaw_map = get_flaw_catalog_map()
    is_supersonic = true_ac.feature_vector["max_mach_nom"] >= 1.0

    thetas = {d: true_ac.get_true_driver_theta(d) for d in true_ac.driver_theta_base}
    out: Dict[str, Any] = {}

    for m_key, m_info in metrics_spec.items():
        if m_key not in state.nominal_perf:
            continue
        nom_val = float(state.nominal_perf[m_key])
        el_row = m_info["elasticities_supersonic"] if is_supersonic else m_info["elasticities_subsonic"]
        log_shift = sum(float(el) * thetas[d] for d, el in el_row.items())
        val = nom_val * math.exp(log_shift)

        # Active flaw direct metric multipliers
        for fid, fstate in true_ac.active_flaws.items():
            m_mult = float(flaw_map[fid]["truth_effects"].get("metric_multipliers", {}).get(m_key, 1.0))
            if m_mult != 1.0:
                val *= m_mult ** fstate.residual_factor

        # Fix & placard multipliers
        val *= float(true_ac.fix_metric_multipliers.get(m_key, 1.0))
        val *= float(true_ac.placard_metric_multipliers.get(m_key, 1.0))
        out[m_key] = val

    # ps_grid scaling if present
    if "ps_grid" in state.nominal_perf and "ps_mps_m09_4572m_1g" in out:
        nom_ps = max(1.0, float(state.nominal_perf.get("ps_mps_m09_4572m_1g", 50.0)))
        ratio = out["ps_mps_m09_4572m_1g"] / nom_ps
        out["ps_grid"] = [[float(cell) * ratio for cell in row] for row in state.nominal_perf["ps_grid"]]

    # carrier_suitability
    nom_cs = state.nominal_perf.get("carrier_suitability", {"suitable": bool(true_ac.feature_vector["carrier_capable"] > 0.5), "reasons": []})
    suitable = bool(nom_cs.get("suitable", True)) if isinstance(nom_cs, dict) else bool(nom_cs)
    reasons = list(nom_cs.get("reasons", [])) if isinstance(nom_cs, dict) else []
    for fid, fstate in true_ac.active_flaws.items():
        reason = flaw_map[fid]["truth_effects"].get("carrier_unsuitable_reason")
        if reason and fstate.residual_factor > 0.25 and true_ac.feature_vector["carrier_capable"] > 0.5:
            suitable = False
            if reason not in reasons:
                reasons.append(reason)
    out["carrier_suitability"] = {"suitable": suitable, "reasons": reasons}
    return out


def compute_estimate_report(
    state: LineageTestState,
    ledger: Optional[ExperienceLedger] = None,
    tech_ctx: Optional[Any] = None,
) -> Dict[str, Any]:
    """Compute player-facing `EstimateReport` (every metric is an `Estimate` dict) (§5.4)."""
    metrics_spec = load_drivers_data()["metrics"]
    true_ac = state.true_aircraft
    flaw_map = get_flaw_catalog_map()
    is_supersonic = true_ac.feature_vector["max_mach_nom"] >= 1.0

    out: Dict[str, Any] = {}
    for m_key, m_info in metrics_spec.items():
        if m_key not in state.nominal_perf:
            continue
        nom_val = float(state.nominal_perf[m_key])
        el_row = m_info["elasticities_supersonic"] if is_supersonic else m_info["elasticities_subsonic"]

        log_shift = 0.0
        var_log = 0.0
        best_src = "sim"
        best_rank = 0

        for d, el in el_row.items():
            b = state.beliefs[d]
            log_shift += float(el) * b.mu_belief
            var_log += (float(el) ** 2) * b.var_belief
            r = SOURCE_RANK.get(b.best_source, 0)
            if r > best_rank:
                best_rank = r
                best_src = b.best_source

        val = nom_val * math.exp(log_shift)

        # Apply ONLY detected flaws' known metric multipliers
        for fid, fstate in true_ac.active_flaws.items():
            if fstate.detected:
                m_mult = float(flaw_map[fid]["truth_effects"].get("metric_multipliers", {}).get(m_key, 1.0))
                if m_mult != 1.0:
                    val *= m_mult ** fstate.residual_factor

        val *= float(true_ac.fix_metric_multipliers.get(m_key, 1.0))
        val *= float(true_ac.placard_metric_multipliers.get(m_key, 1.0))

        sigma = abs(val) * math.sqrt(max(0.0, var_log))
        out[m_key] = {
            "value": val,
            "sigma": sigma,
            "source": best_src,
            "unit": m_info["unit"],
        }

    # Carrier suitability estimate
    nom_cs = state.nominal_perf.get("carrier_suitability", {"suitable": bool(true_ac.feature_vector["carrier_capable"] > 0.5), "reasons": []})
    suitable = bool(nom_cs.get("suitable", True)) if isinstance(nom_cs, dict) else bool(nom_cs)
    reasons = list(nom_cs.get("reasons", [])) if isinstance(nom_cs, dict) else []
    for fid, fstate in true_ac.active_flaws.items():
        if fstate.detected:
            reason = flaw_map[fid]["truth_effects"].get("carrier_unsuitable_reason")
            if reason and fstate.residual_factor > 0.25 and true_ac.feature_vector["carrier_capable"] > 0.5:
                suitable = False
                if reason not in reasons:
                    reasons.append(reason)
    out["carrier_suitability"] = {"suitable": suitable, "reasons": reasons}
    out["watchlist"] = build_risk_watchlist(
        true_ac.feature_vector,
        state.date_day,
        ledger,
        tech_ctx,
        state.known_flaws_company,
    )
    return out


def apply_flaw_fix_to_state(
    state: LineageTestState,
    flaw_id: str,
    fix_id: Optional[str] = None,
    phase: str = "prototype",
    fleet_size: int = 0,
) -> Dict[str, Any]:
    """Apply an engineering fix to a detected flaw on `state` (§5.6.5)."""
    flaw_map = get_flaw_catalog_map()
    if flaw_id not in state.true_aircraft.active_flaws:
        raise KeyError(f"Flaw {flaw_id} is not active on this aircraft")

    fstate = state.true_aircraft.active_flaws[flaw_id]
    f_entry = flaw_map[flaw_id]
    fixes = f_entry["fixes"]
    if fix_id is None:
        chosen_fix = fixes[0]
    else:
        matching = [fx for fx in fixes if fx["id"] == fix_id]
        if not matching:
            raise KeyError(f"Fix {fix_id} not found for flaw {flaw_id}")
        chosen_fix = matching[0]

    cost_info = compute_fix_cost_and_days(
        chosen_fix,
        state.true_aircraft.feature_vector["empty_mass_kg"],
        state.date_day,
        phase=phase,
        already_applied_fixes=state.true_aircraft.applied_fixes,
        fleet_size=fleet_size,
    )

    is_shared = chosen_fix["id"] in state.true_aircraft.applied_fixes
    state.true_aircraft.applied_fixes.add(chosen_fix["id"])

    if not is_shared:
        for d, delta in chosen_fix.get("driver_log_deltas", {}).items():
            state.true_aircraft.fix_driver_deltas[d] = state.true_aircraft.fix_driver_deltas.get(d, 0.0) + float(delta)
            if d in state.beliefs:
                state.beliefs[d].mu_belief += float(delta)
        for m_key, mult in chosen_fix.get("metric_multipliers", {}).items():
            state.true_aircraft.fix_metric_multipliers[m_key] = (
                state.true_aircraft.fix_metric_multipliers.get(m_key, 1.0) * float(mult)
            )

    fstate.status = "fixed"
    fstate.applied_fix_id = chosen_fix["id"]
    fstate.residual_factor = float(chosen_fix["residual_factor"])

    state.total_testing_cost_usd += cost_info["total_cost_usd"]
    state.total_testing_days += int(cost_info["fix_days"])
    state.date_day += int(cost_info["fix_days"])
    return {
        "flaw_id": flaw_id,
        "fix_id": chosen_fix["id"],
        "fix_name": chosen_fix["name"],
        "residual_factor": fstate.residual_factor,
        **cost_info,
    }


def apply_flaw_placard_to_state(state: LineageTestState, flaw_id: str) -> Dict[str, Any]:
    """Apply an operational flight-manual placard to a detected flaw (§5.6.5)."""
    flaw_map = get_flaw_catalog_map()
    fstate = state.true_aircraft.active_flaws[flaw_id]
    f_entry = flaw_map[flaw_id]
    placard = f_entry["placard"]
    rev_days = int(load_testing_tuning()["placard_revision_days"])

    for m_key, mult in placard.get("metric_multipliers", {}).items():
        state.true_aircraft.placard_metric_multipliers[m_key] = (
            state.true_aircraft.placard_metric_multipliers.get(m_key, 1.0) * float(mult)
        )
    fstate.status = "placarded"
    fstate.residual_factor = float(placard["residual_hazard_factor"])
    state.total_testing_days += rev_days
    state.date_day += rev_days
    return {
        "flaw_id": flaw_id,
        "placard_name": placard["name"],
        "residual_factor": fstate.residual_factor,
        "fix_days": rev_days,
        "total_cost_usd": 0.0,
    }


def inherit_variant_belief(
    parent_state: LineageTestState,
    campaign_seed: int,
    new_design: Dict[str, Any],
    new_nominal_perf: Dict[str, Any],
    date_day: int,
    aero_diagnostics: Optional[Dict[str, Any]] = None,
    engine_diagnostics: Optional[Dict[str, Any]] = None,
    tech_ctx: Optional[Any] = None,
    ledger: Optional[ExperienceLedger] = None,
    engineer_ratings: Optional[Dict[str, float]] = None,
) -> LineageTestState:
    """Create a derivative variant state that smoothly inherits parent posterior beliefs (§7.6)."""
    child = initialize_lineage_state(
        campaign_seed=campaign_seed,
        design=new_design,
        nominal_perf=new_nominal_perf,
        date_day=date_day,
        aero_diagnostics=aero_diagnostics,
        engine_diagnostics=engine_diagnostics,
        tech_ctx=tech_ctx,
        ledger=ledger,
        engineer_ratings=engineer_ratings,
    )
    c_parent = parent_state.true_aircraft.coords_5d
    c_child = child.true_aircraft.coords_5d
    dist_sq = sum((c_child[i] - c_parent[i]) ** 2 for i in range(5))
    delta = min(1.0, math.sqrt(dist_sq) / 2.5)

    for d, child_b in child.beliefs.items():
        parent_b = parent_state.beliefs[d]
        var0_new = child_b.var_belief
        child_b.mu_belief = (1.0 - delta) * parent_b.mu_belief
        child_b.var_belief = (1.0 - delta * delta) * parent_b.var_belief + (delta * delta) * var0_new
        child_b.best_source = parent_b.best_source if delta < 0.35 else "sim"

    child.known_flaws_company = set(parent_state.known_flaws_company)
    return child
