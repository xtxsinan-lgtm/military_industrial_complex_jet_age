"""Hidden flaw trigger evaluation, monotonic realization, watchlist, and fix/placard resolution."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .data_loader import day_to_year, get_inflation_factor, load_flaws_data, load_testing_tuning
from .features import StubTechContext
from .hashing import flaw_u01_draw
from .novelty import ExperienceLedger, compute_all_unfamiliarities


@dataclass
class ActiveFlawState:
    flaw_id: str
    severity: int
    trigger_prob: float
    u_draw: float
    detected: bool = False
    detected_day: Optional[int] = None
    detected_source: Optional[str] = None
    status: str = "undetected"  # "undetected" | "detected" | "fixed" | "placarded" | "accepted"
    applied_fix_id: Optional[str] = None
    residual_factor: float = 1.0
    manifested_in_service: bool = False


def get_flaw_catalog_map() -> Dict[str, Dict[str, Any]]:
    return {f["id"]: f for f in load_flaws_data()["flaws"]}


def evaluate_flaw_probability(
    flaw_entry: Dict[str, Any],
    feat: Dict[str, float],
    date_day: int = 0,
    ledger: Optional[ExperienceLedger] = None,
    tech_ctx: Optional[Any] = None,
) -> float:
    """Compute exact trigger probability P_trig,f (§5.6.1)."""
    ctx = tech_ctx if tech_ctx is not None else StubTechContext(date_day=date_day)
    trig = flaw_entry["trigger"]

    # 1. Additive core score S_add
    s_add = float(trig.get("base", 0.0))
    for r in trig.get("ramps", []):
        x_val = float(feat.get(r["feature"], 0.0))
        x0 = float(r["x0"])
        x1 = float(r["x1"])
        w = float(r["weight"])
        if abs(x1 - x0) < 1e-12:
            t = 1.0 if x_val >= x1 else 0.0
        else:
            t = max(0.0, min(1.0, (x_val - x0) / (x1 - x0)))
        s_add += w * t

    for fl in trig.get("flags", []):
        if float(feat.get(fl["feature"], 0.0)) > 0.5:
            s_add += float(fl["add"])

    # 2. Gate multiplier G_f
    g_mult = 1.0
    for g in trig.get("gates", []):
        x_val = float(feat.get(g["feature"], 0.0))
        xmin = float(g["min"])
        xfull = float(g["full"])
        if abs(xfull - xmin) < 1e-12:
            gt = 1.0 if x_val >= xfull else 0.0
        else:
            gt = max(0.0, min(1.0, (x_val - xmin) / (xfull - xmin)))
        g_mult *= gt
        if g_mult <= 0.0:
            return 0.0

    # 3. Design & tech feature multipliers M_feat,f
    m_feat = 1.0
    for m in trig.get("multipliers", []):
        if float(feat.get(m["feature"], 0.0)) > 0.5:
            m_feat *= float(m["mul"])

    # 4. Novelty unfamiliarity multiplier M_nov,f
    unfam = compute_all_unfamiliarities(date_day, ledger)
    nov_keys = flaw_entry.get("novelty_features", [])
    if nov_keys:
        u_mean = sum(unfam.get(k, 0.5) for k in nov_keys) / len(nov_keys)
    else:
        u_mean = 0.5
    m_nov = 0.75 + 0.65 * u_mean

    # 5. Tech incidence family multiplier (§2.6 of 03_tech_effect_keys.md)
    family = flaw_entry["family"]
    inc_key = f"testing.flaw_incidence.{family}"
    i_tech = float(ctx.get(inc_key))
    if family == "manufacturing":
        i_tech *= float(ctx.get("mfg.quality_defect_factor"))
    if flaw_entry["id"] == "radar_fcs_immaturity":
        rel_factor = max(0.25, float(ctx.get("avionics.reliability_factor")))
        i_tech /= rel_factor

    scale = float(load_testing_tuning().get("global_flaw_prob_scale", 0.34))
    p_raw = s_add * g_mult * m_feat * m_nov * i_tech * scale
    p_max = float(flaw_entry.get("max_prob", 0.90))
    return max(0.0, min(p_max, p_raw))


def evaluate_all_flaw_probabilities(
    feat: Dict[str, float],
    date_day: int = 0,
    ledger: Optional[ExperienceLedger] = None,
    tech_ctx: Optional[Any] = None,
) -> Dict[str, float]:
    """Return {flaw_id: P_trig,f} for all 34 flaws."""
    flaws = load_flaws_data()["flaws"]
    return {
        f["id"]: evaluate_flaw_probability(f, feat, date_day, ledger, tech_ctx)
        for f in flaws
    }


def realize_true_flaws(
    campaign_seed: int,
    categorical_sig: str,
    feat: Dict[str, float],
    date_day: int = 0,
    ledger: Optional[ExperienceLedger] = None,
    tech_ctx: Optional[Any] = None,
) -> Dict[str, ActiveFlawState]:
    """Deterministically realize active flaws for a design (§5.6.2)."""
    flaws = load_flaws_data()["flaws"]
    active: Dict[str, ActiveFlawState] = {}
    for f in flaws:
        fid = f["id"]
        p_trig = evaluate_flaw_probability(f, feat, date_day, ledger, tech_ctx)
        u_draw = flaw_u01_draw(campaign_seed, categorical_sig, fid)
        if u_draw < p_trig:
            base_sev = int(f["base_severity"])
            sev = min(5, base_sev + (1 if u_draw < 0.25 * p_trig else 0))
            active[fid] = ActiveFlawState(
                flaw_id=fid,
                severity=sev,
                trigger_prob=p_trig,
                u_draw=u_draw,
            )
    return active


def build_risk_watchlist(
    feat: Dict[str, float],
    date_day: int = 0,
    ledger: Optional[ExperienceLedger] = None,
    tech_ctx: Optional[Any] = None,
    known_flaws_company: Optional[set] = None,
) -> List[Dict[str, Any]]:
    """Build player-facing pre-test Risk Watchlist (§3.1, §5.6)."""
    tuning = load_testing_tuning()
    min_prob = float(tuning.get("watchlist_min_prob", 0.12))
    year = day_to_year(date_day)
    company_known = known_flaws_company or set()

    watchlist: List[Dict[str, Any]] = []
    unknown_era_count = 0
    unknown_era_max_prob = 0.0

    for f in load_flaws_data()["flaws"]:
        fid = f["id"]
        p = evaluate_flaw_probability(f, feat, date_day, ledger, tech_ctx)
        if p < min_prob:
            continue
        is_known_era = (year >= int(f["known_from_year"])) or (fid in company_known)
        if not is_known_era:
            unknown_era_count += 1
            unknown_era_max_prob = max(unknown_era_max_prob, p)
            continue

        if p >= 0.70:
            band = "Severe"
        elif p >= 0.45:
            band = "High"
        elif p >= 0.25:
            band = "Moderate"
        else:
            band = "Low"

        watchlist.append({
            "flaw_id": fid,
            "name": f["name"],
            "family": f["family"],
            "category": f["category"],
            "risk_band": band,
            "estimated_prob": round(p, 4),
            "base_severity": f["base_severity"],
        })

    if unknown_era_count > 0:
        watchlist.append({
            "flaw_id": "unknown_uncharted_regime_risk",
            "name": f"Uncharted High-Speed Regime Risks ({unknown_era_count} potential phenomena)",
            "family": "unknown",
            "category": "aerodynamics",
            "risk_band": "High" if unknown_era_max_prob >= 0.45 else "Moderate",
            "estimated_prob": round(unknown_era_max_prob, 4),
            "base_severity": 4,
        })

    watchlist.sort(key=lambda x: x["estimated_prob"], reverse=True)
    return watchlist


def get_flaw_display_label(flaw_entry: Dict[str, Any], date_day: int, company_known: Optional[set] = None) -> str:
    """Return historical symptom label if before known_from_year, else canonical name."""
    year = day_to_year(date_day)
    if year >= int(flaw_entry["known_from_year"]) or (company_known and flaw_entry["id"] in company_known):
        return str(flaw_entry["name"])
    return str(flaw_entry.get("unknown_symptom_label", flaw_entry["name"]))


def compute_fix_cost_and_days(
    fix_entry: Dict[str, Any],
    empty_mass_nom_kg: float,
    date_day: int,
    phase: str = "prototype",  # "design" | "prototype" | "service"
    already_applied_fixes: Optional[set] = None,
    fleet_size: int = 0,
) -> Dict[str, float]:
    """Compute nominal dollar cost and downtime days for applying an engineering fix (§5.6.5)."""
    tuning = load_testing_tuning()
    year = day_to_year(date_day)
    infl = get_inflation_factor(year)
    mass_scale = (max(1000.0, float(empty_mass_nom_kg)) / 5000.0) ** 0.65

    if phase == "design":
        c_mult = float(tuning["design_phase_fix_cost_mult"])
        d_mult = float(tuning["design_phase_fix_days_mult"])
    elif phase == "service":
        c_mult = float(tuning["service_phase_fix_cost_mult"])
        d_mult = 1.0
    else:
        c_mult = float(tuning["prototype_phase_fix_cost_mult"])
        d_mult = float(tuning["prototype_phase_fix_days_mult"])

    shared = already_applied_fixes is not None and (fix_entry["id"] in already_applied_fixes)
    shared_mult = float(tuning["shared_fix_cost_mult"]) if shared else 1.0

    base_cost_usd = float(fix_entry["base_cost_1950_usd"]) * mass_scale * infl * c_mult * shared_mult
    retrofit_usd = 0.0
    if phase == "service" and fleet_size > 0:
        retrofit_usd = float(fix_entry.get("retrofit_kit_1950_usd", 2500.0)) * mass_scale * infl * int(fleet_size) * shared_mult

    fix_days = max(1, int(round(float(fix_entry["fix_days"]) * d_mult * shared_mult)))
    return {
        "engineering_cost_usd": base_cost_usd,
        "retrofit_cost_usd": retrofit_usd,
        "total_cost_usd": base_cost_usd + retrofit_usd,
        "fix_days": float(fix_days),
        "is_shared_fix": float(1.0 if shared else 0.0),
    }
