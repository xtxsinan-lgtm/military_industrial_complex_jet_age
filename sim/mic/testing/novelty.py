"""Novelty scoring, company/industry experience ledger, and regime/maturity/quality multipliers."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from .data_loader import date_str_to_day, load_drivers_data, load_novelty_features_data, load_testing_tuning


class ExperienceLedger:
    """Tracks company familiarity per novelty feature across campaigns and aircraft."""

    def __init__(self, initial_counts: Optional[Dict[str, float]] = None) -> None:
        self.company_counts: Dict[str, float] = dict(initial_counts or {})

    def get_company_exp(self, feature_id: str) -> float:
        return float(self.company_counts.get(feature_id, 0.0))

    def record_experience(self, active_features: Dict[str, float], base_increment: float) -> None:
        for fid, weight in active_features.items():
            if weight > 0.05:
                self.company_counts[fid] = self.get_company_exp(fid) + float(base_increment) * float(weight)


def evaluate_novelty_activation(feat: Dict[str, float], pred: Dict[str, Any]) -> float:
    """Evaluate novelty predicate activation a_f(design) in [0, 1]."""
    ptype = pred["type"]
    f_key = pred["feature"]
    val = float(feat.get(f_key, 0.0))
    if ptype == "flag":
        return 1.0 if val > 0.5 else 0.0
    if ptype == "ramp":
        x0 = float(pred["x0"])
        x1 = float(pred["x1"])
        if abs(x1 - x0) < 1e-12:
            return 1.0 if val >= x1 else 0.0
        t = (val - x0) / (x1 - x0)
        return max(0.0, min(1.0, t))
    raise ValueError(f"Unknown predicate type: {ptype}")


def compute_active_novelty_features(feat: Dict[str, float]) -> Dict[str, float]:
    """Return mapping {novelty_feature_id: activation in [0, 1]}."""
    nov_data = load_novelty_features_data()["novelty_features"]
    out: Dict[str, float] = {}
    for entry in nov_data:
        out[entry["id"]] = evaluate_novelty_activation(feat, entry["predicate"])
    return out


def compute_industry_exp_count(feature_entry: Dict[str, Any], date_day: int) -> int:
    """Count historical US first flights for this feature on or before date_day."""
    count = 0
    for d_str in feature_entry.get("historical_first_flights", []):
        if date_str_to_day(d_str) <= date_day:
            count += 1
    return count


def compute_feature_unfamiliarity(
    feature_entry: Dict[str, Any],
    date_day: int,
    ledger: Optional[ExperienceLedger] = None,
) -> float:
    """Compute unfamiliarity U(f) in [0.15, 1.0] (§5.3.1)."""
    tuning = load_testing_tuning()
    floor = float(tuning.get("unfamiliarity_floor", 0.15))
    tau_comp = float(tuning.get("company_exp_decay_scale", 1.8))
    tau_ind = float(tuning.get("industry_exp_decay_scale", 3.0))

    n_comp = ledger.get_company_exp(feature_entry["id"]) if ledger is not None else 0.0
    n_ind = float(compute_industry_exp_count(feature_entry, date_day))

    decay = 0.65 * math.exp(-n_comp / tau_comp) + 0.35 * math.exp(-n_ind / tau_ind)
    return floor + (1.0 - floor) * decay


def compute_all_unfamiliarities(
    date_day: int,
    ledger: Optional[ExperienceLedger] = None,
) -> Dict[str, float]:
    """Return {novelty_feature_id: U(f)} at `date_day`."""
    nov_data = load_novelty_features_data()["novelty_features"]
    return {entry["id"]: compute_feature_unfamiliarity(entry, date_day, ledger) for entry in nov_data}


def compute_driver_novelty_scores(
    feat: Dict[str, float],
    date_day: int,
    ledger: Optional[ExperienceLedger] = None,
) -> Dict[str, float]:
    """Compute per-driver novelty score N_d (§5.3.1)."""
    drivers = load_drivers_data()["drivers"]
    nov_data = load_novelty_features_data()["novelty_features"]
    unfam = compute_all_unfamiliarities(date_day, ledger)

    scores: Dict[str, float] = {d: 0.0 for d in drivers}
    for entry in nov_data:
        fid = entry["id"]
        act = evaluate_novelty_activation(feat, entry["predicate"])
        if act <= 0.0:
            continue
        u_f = unfam[fid]
        for d, w_fd in entry.get("driver_weights", {}).items():
            if d in scores:
                scores[d] += act * float(w_fd) * u_f
    return scores


def compute_mach_regime_base(mach: float) -> float:
    """Piecewise linear transonic/supersonic regime difficulty curve r_mach(M) (§5.3.2)."""
    pts = load_testing_tuning()["regime_mach_curve"]
    m = float(mach)
    if m <= pts[0][0]:
        return float(pts[0][1])
    for i in range(len(pts) - 1):
        m0, r0 = float(pts[i][0]), float(pts[i][1])
        m1, r1 = float(pts[i + 1][0]), float(pts[i + 1][1])
        if m <= m1:
            t = (m - m0) / max(1e-9, m1 - m0)
            return r0 + t * (r1 - r0)
    return float(pts[-1][1])


def compute_regime_multipliers(max_mach_nom: float) -> Dict[str, float]:
    """Return {driver_id: R_d(M)} (§5.3.2)."""
    drivers = load_drivers_data()["drivers"]
    r_base = compute_mach_regime_base(max_mach_nom)
    return {
        d: 1.0 + float(info["regime_sensitivity"]) * (r_base - 1.0)
        for d, info in drivers.items()
    }


def compute_tech_maturity_multiplier(
    techs_used: Sequence[str],
    tech_ctx: Any,
) -> float:
    """Compute M_tech from TechContext maturities of techs_used (§5.3.3)."""
    if not techs_used:
        return 1.0
    mat_map = getattr(tech_ctx, "tech_maturity", {}) or {}
    mats = [float(mat_map.get(t, 1.0)) for t in techs_used]
    m_min = min(mats)
    m_mean = sum(mats) / len(mats)
    m_eff = 0.65 * m_min + 0.35 * m_mean
    k_mat = float(load_testing_tuning().get("k_tech_maturity", 0.85))
    return 1.0 + k_mat * max(0.0, 1.0 - m_eff)


def compute_engineering_quality_multipliers(
    engineer_ratings: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """Compute Q_d in [0.70, 1.35] from company engineering discipline ratings (§5.3.4)."""
    ratings = engineer_ratings or {}
    drivers = load_drivers_data()["drivers"]
    out: Dict[str, float] = {}
    for d, info in drivers.items():
        disc = info["discipline"]
        q_disc = float(ratings.get(disc, 50.0))
        q_mult = max(0.70, min(1.35, 1.30 - 0.006 * q_disc))
        out[d] = q_mult
    return out
