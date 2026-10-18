"""Wind-tunnel campaigns, ground test rigs, Bayesian updating, and prototype rollout."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from .data_loader import (
    date_str_to_day,
    day_to_year,
    get_inflation_factor,
    load_report_templates,
    load_sources_data,
    load_testing_tuning,
)
from .features import StubTechContext
from .flaws import get_flaw_catalog_map, get_flaw_display_label
from .hashing import keyed_normal, keyed_u01
from .novelty import ExperienceLedger, compute_active_novelty_features
from .truth import SOURCE_RANK, DriverBelief, LineageTestState, apply_flaw_fix_to_state


def bayesian_normal_update(
    belief: DriverBelief,
    y_meas: float,
    sigma_meas: float,
    source_tag: str,
    sigma_floor: float = 0.0,
) -> None:
    """Conjugate Gaussian precision update with optional tunnel systematic floor (§5.5)."""
    var_meas = max(1e-8, float(sigma_meas) ** 2)
    prec_old = 1.0 / max(1e-8, belief.var_belief)
    prec_meas = 1.0 / var_meas
    var_new = 1.0 / (prec_old + prec_meas)
    mu_new = var_new * (belief.mu_belief * prec_old + float(y_meas) * prec_meas)

    if source_tag == "tunnel" and SOURCE_RANK.get(belief.best_source, 0) <= SOURCE_RANK["tunnel"]:
        floor_var = float(sigma_floor) ** 2
        var_new = max(var_new, floor_var)
        belief.tunnel_floor_var = max(belief.tunnel_floor_var, floor_var)

    belief.mu_belief = mu_new
    belief.var_belief = var_new
    if SOURCE_RANK.get(source_tag, 0) > SOURCE_RANK.get(belief.best_source, 0):
        belief.best_source = source_tag


def run_tunnel_or_ground_campaign(
    campaign_seed: int,
    state: LineageTestState,
    campaign_id: str,
    provider_id: str = "naca",
    depth: str = "standard",
    active_military_contract: bool = True,
    own_wind_tunnel_level: int = 1,
    auto_fix_detected_flaws: bool = False,
    tech_ctx: Optional[Any] = None,
    ledger: Optional[ExperienceLedger] = None,
) -> Dict[str, Any]:
    """Execute one wind-tunnel or ground test campaign on `state` (§5.5.1–§5.5.3)."""
    ctx = tech_ctx if tech_ctx is not None else StubTechContext(date_day=state.date_day)
    sources_spec = load_sources_data()
    tuning = load_testing_tuning()
    templates = load_report_templates()
    flaw_map = get_flaw_catalog_map()

    if campaign_id not in sources_spec["campaigns"]:
        raise KeyError(f"Unknown campaign_id: {campaign_id}")
    camp = sources_spec["campaigns"][campaign_id]

    if provider_id not in camp["allowed_providers"]:
        raise ValueError(f"Provider '{provider_id}' not allowed for campaign '{campaign_id}'")

    prov = sources_spec["providers"][provider_id]
    if provider_id == "aedc":
        avail_day = date_str_to_day(prov["available_from_date"])
        if state.date_day < avail_day:
            raise ValueError("AEDC Tullahoma is not available before 1956-01-01")

    if provider_id == "own" and own_wind_tunnel_level < int(camp["min_own_tunnel_level"]):
        raise ValueError(
            f"Company wind_tunnel_level {own_wind_tunnel_level} < required {camp['min_own_tunnel_level']} for {campaign_id}"
        )

    req_tech = camp.get("required_tech")
    if req_tech and not bool(ctx.get(req_tech)):
        raise ValueError(f"Campaign '{campaign_id}' requires unlocked tech '{req_tech}'")

    depth_info = sources_spec["depth_presets"][depth]
    m_depth = float(depth_info["hours_mult"])
    hours = float(camp["ref_hours"]) * m_depth

    state.campaign_seq += 1
    seq = state.campaign_seq
    year = day_to_year(state.date_day)
    infl = get_inflation_factor(year)
    mass_scale = (max(1000.0, state.true_aircraft.feature_vector["empty_mass_kg"]) / 5000.0) ** 0.50

    # Queue + fabrication + tunnel run days & cost
    u_q = keyed_u01(campaign_seed, "tunnel_queue", state.lineage_id, campaign_id, seq)
    q_base = float(prov.get("queue_base_days", 0))
    q_jit = float(prov.get("queue_jitter_days", 0))
    q_mult = float(prov.get("military_priority_queue_mult", 1.0)) if active_military_contract else 1.0
    queue_days = int(round((q_base + q_jit * u_q) * q_mult))
    fab_days = int(camp["model_fab_days"])
    run_days = int(math.ceil(hours / float(prov["hours_per_day"])))
    # Model fabrication occurs in parallel with queue wait if queue_days > 0
    total_days = max(queue_days, fab_days) + run_days

    hourly_rate_1950 = float(prov["hourly_cost_1950_usd"].get(campaign_id, 250.0))
    model_cost_usd = float(camp["model_cost_1950_usd"]) * mass_scale * infl
    tunnel_fee_usd = hours * hourly_rate_1950 * infl
    total_cost_usd = model_cost_usd + tunnel_fee_usd

    state.date_day += total_days
    state.total_testing_days += total_days
    state.total_testing_cost_usd += total_cost_usd

    # Check Transonic Choking Rule (§3.1, §5.5.2, `03_tech_effect_keys.md` §2.6)
    max_mach_nom = state.true_aircraft.feature_vector["max_mach_nom"]
    has_transonic_tunnel = bool(ctx.get("testing.transonic_tunnel"))
    choked = False
    if bool(camp.get("chokes_in_transonic", False)) and max_mach_nom >= 0.85 and not has_transonic_tunnel:
        choked = True

    q_prov = float(prov["quality_mult"])
    tunnel_sigma_factor = float(ctx.get("testing.tunnel_sigma_factor"))
    drivers_updated: List[str] = []

    for d, prec in camp["driver_precision"].items():
        if d == "cdw" and choked:
            # Choked tunnel cannot measure transonic wave drag
            continue
        sigma_ref = float(prec["sigma_ref"])
        sigma_floor = float(prec["sigma_floor"])
        sigma_meas = tunnel_sigma_factor * q_prov * math.sqrt(
            (sigma_floor ** 2) + (sigma_ref ** 2) / max(0.1, m_depth)
        )
        z_meas = keyed_normal(campaign_seed, "tunnel_meas", state.lineage_id, campaign_id, seq, d)
        theta_true = state.true_aircraft.get_true_driver_theta(d)
        y_meas = theta_true + sigma_meas * z_meas
        bayesian_normal_update(
            state.beliefs[d],
            y_meas=y_meas,
            sigma_meas=sigma_meas,
            source_tag="tunnel",
            sigma_floor=sigma_floor * tunnel_sigma_factor * q_prov,
        )
        drivers_updated.append(d)

    # Flaw detection rolls (§5.6.4)
    flaw_detect_factor = float(ctx.get("testing.flaw_detect_factor"))
    unknown_mult = float(tuning["unknown_era_detect_mult"])
    detected_flaws: List[str] = []
    fixes_applied: List[Dict[str, Any]] = []

    for fid, fstate in state.true_aircraft.active_flaws.items():
        if fstate.detected:
            continue
        f_entry = flaw_map[fid]
        p0 = float(f_entry["detect_prob_by_source"].get(campaign_id, 0.0))
        if p0 <= 0.0:
            continue
        # If tunnel is choked in transonic band, transonic-specific flaws cannot be seen in low_speed_tunnel
        if choked and f_entry["family"] in ("transonic_control_loss", "inlet", "aileron_reversal"):
            continue

        is_known = (year >= int(f_entry["known_from_year"])) or (fid in state.known_flaws_company)
        era_mult = 1.0 if is_known else unknown_mult
        p_eff = min(0.99, max(0.0, p0 * flaw_detect_factor * era_mult))
        p_camp = 1.0 - ((1.0 - p_eff) ** m_depth)

        u_det = keyed_u01(campaign_seed, "tunnel_flaw_det", state.lineage_id, campaign_id, seq, fid)
        if u_det < p_camp:
            fstate.detected = True
            fstate.detected_day = state.date_day
            fstate.detected_source = campaign_id
            fstate.status = "detected"
            state.known_flaws_company.add(fid)
            detected_flaws.append(fid)

            flaw_label = get_flaw_display_label(f_entry, state.date_day, state.known_flaws_company)
            rec_fix = f_entry["fixes"][0]["name"] if f_entry["fixes"] else f_entry["placard"]["name"]
            state.event_log.append(
                templates["tunnel_flaw_detected"].format(
                    campaign_name=camp["name"],
                    flaw_label=flaw_label,
                    severity=fstate.severity,
                    recommended_fix=rec_fix,
                )
            )
            if auto_fix_detected_flaws and f_entry["fixes"]:
                fix_res = apply_flaw_fix_to_state(state, fid, phase="design")
                fixes_applied.append(fix_res)

    if choked:
        state.event_log.append(templates["tunnel_choked"].format(campaign_name=camp["name"]))

    state.event_log.append(
        templates["tunnel_complete"].format(
            campaign_name=camp["name"],
            provider_name=prov["name"],
            hours=hours,
            cost_usd=total_cost_usd,
            drivers_updated=", ".join(drivers_updated) if drivers_updated else "none (choked)",
        )
    )

    if ledger is not None:
        active_nov = compute_active_novelty_features(state.true_aircraft.feature_vector)
        ledger.record_experience(active_nov, float(tuning["experience_gain_tunnel"]))

    return {
        "campaign_id": campaign_id,
        "provider_id": provider_id,
        "depth": depth,
        "hours": hours,
        "queue_days": queue_days,
        "total_days": total_days,
        "total_cost_usd": total_cost_usd,
        "choked": choked,
        "drivers_updated": drivers_updated,
        "detected_flaws": detected_flaws,
        "fixes_applied": fixes_applied,
    }


def run_prototype_rollout(
    campaign_seed: int,
    state: LineageTestState,
    n_prototypes: int = 2,
    engineer_ratings: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Build 1..3 prototypes and perform rollout scale weighing Bayesian update (§5.5.4)."""
    if n_prototypes < 1 or n_prototypes > 3:
        raise ValueError("n_prototypes must be between 1 and 3")

    tuning = load_testing_tuning()
    sources_spec = load_sources_data()
    templates = load_report_templates()

    true_ac = state.true_aircraft
    feat = true_ac.feature_vector

    # True unit flyaway cost
    nom_flyaway = float(state.nominal_perf.get("unit_flyaway_cost_usd", 450000.0))
    theta_mass = true_ac.get_true_driver_theta("mass")
    theta_cunit = true_ac.get_true_driver_theta("cost_unit")
    true_flyaway = nom_flyaway * math.exp(0.45 * theta_mass + 1.00 * theta_cunit)

    c1 = float(tuning["prototype_first_cost_mult"])
    c_add = float(tuning["prototype_additional_cost_mult"])
    proto_cost_usd = true_flyaway * (c1 + c_add * (n_prototypes - 1))

    # Build days
    base_days = float(tuning["prototype_base_build_days"])
    m_coeff = float(tuning["prototype_mass_days_coeff"])
    n_coeff = float(tuning["prototype_novelty_days_coeff"])
    mean_nov = sum(p["N_d"] for p in true_ac.driver_priors.values()) / len(true_ac.driver_priors)
    q_struct = true_ac.driver_priors["mass"]["Q_d"]
    theta_cdev = true_ac.get_true_driver_theta("cost_dev")

    raw_days = (
        base_days
        + m_coeff * math.log(max(800.0, feat["empty_mass_kg"]) / 3000.0)
        + n_coeff * mean_nov
    ) * q_struct * math.exp(0.35 * theta_cdev)
    build_days = max(90, int(round(raw_days)))

    state.date_day += build_days
    state.total_testing_days += build_days
    state.total_testing_cost_usd += proto_cost_usd
    state.prototypes_built += n_prototypes
    state.prototypes_surviving += n_prototypes
    state.prototype_rolled_out = True
    state.campaign_seq += 1
    seq = state.campaign_seq

    # Rollout weighing & shop audit observations
    for d, sigma_meas in sources_spec["prototype_rollout_precision"].items():
        z_meas = keyed_normal(campaign_seed, "proto_rollout", state.lineage_id, seq, d)
        theta_true = true_ac.get_true_driver_theta(d)
        y_meas = theta_true + float(sigma_meas) * z_meas
        bayesian_normal_update(
            state.beliefs[d],
            y_meas=y_meas,
            sigma_meas=float(sigma_meas),
            source_tag="flight",
        )

    true_empty_mass = feat["empty_mass_kg"] * math.exp(true_ac.get_true_driver_theta("mass"))
    state.event_log.append(
        templates["prototype_rollout"].format(
            n_prototypes=n_prototypes,
            build_days=build_days,
            cost_usd=proto_cost_usd,
            empty_mass_kg=true_empty_mass,
        )
    )
    return {
        "n_prototypes": n_prototypes,
        "build_days": build_days,
        "proto_cost_usd": proto_cost_usd,
        "true_empty_mass_kg": true_empty_mass,
    }
