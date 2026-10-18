"""Operational squadron service entry, monthly fleet hazard, groundings, and retrofits (§5.8)."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .data_loader import load_report_templates, load_testing_tuning
from .flaws import get_flaw_catalog_map
from .hashing import keyed_normal, keyed_u01
from .novelty import ExperienceLedger, compute_active_novelty_features
from .sources import bayesian_normal_update
from .truth import LineageTestState, apply_flaw_fix_to_state


@dataclass
class ServiceMonthReport:
    month_index: int
    fleet_size: int
    fleet_fh: float
    newly_manifested_flaws: List[str] = field(default_factory=list)
    grounding_days: int = 0
    squadron_accidents: int = 0
    retrofit_cost_usd: float = 0.0
    reputation_delta: float = 0.0


def simulate_service_month(
    campaign_seed: int,
    state: LineageTestState,
    month_index: int,
    fleet_size: int = 120,
    fh_per_aircraft: Optional[float] = None,
    auto_retrofit_on_manifest: bool = True,
) -> ServiceMonthReport:
    """Simulate one month of squadron service for a fielded aircraft design (§5.8)."""
    tuning = load_testing_tuning()
    templates = load_report_templates()
    flaw_map = get_flaw_catalog_map()

    fh_ac = float(fh_per_aircraft if fh_per_aircraft is not None else tuning["service_monthly_fh_per_aircraft"])
    fleet_fh = float(fleet_size) * fh_ac
    fh_k = fleet_fh / 1000.0

    state.date_day += 30
    state.campaign_seq += 1
    seq = state.campaign_seq

    # 1. Continuous service Bayesian convergence (§5.8.1)
    sigma_srv = float(tuning["service_sigma_per_1000fh"]) / math.sqrt(max(0.1, fh_k))
    for d in state.beliefs:
        z_meas = keyed_normal(campaign_seed, "service_meas", state.lineage_id, month_index, seq, d)
        theta_true = state.true_aircraft.get_true_driver_theta(d)
        y_meas = theta_true + sigma_srv * z_meas
        bayesian_normal_update(
            state.beliefs[d],
            y_meas=y_meas,
            sigma_meas=sigma_srv,
            source_tag="service",
        )

    newly_manifested: List[str] = []
    grounding_days = 0
    squadron_accidents = 0
    retrofit_cost_usd = 0.0
    reputation_delta = 0.0

    # 2. Manifestation of unresolved flaws (§5.8.2)
    for fid, fstate in state.true_aircraft.active_flaws.items():
        f_entry = flaw_map[fid]
        shaz = f_entry["service_hazard"]
        rho = fstate.residual_factor
        if fstate.status == "accepted":
            rho *= float(tuning["accepted_flaw_service_hazard_mult"])

        if not fstate.manifested_in_service and rho > 0.20:
            lam_man = float(shaz["manifest_rate_per_1000fh"]) * rho * fh_k
            p_man = 1.0 - math.exp(-lam_man)
            u_man = keyed_u01(campaign_seed, "service_manifest", state.lineage_id, month_index, fid)
            if u_man < p_man:
                fstate.detected = True
                fstate.manifested_in_service = True
                state.known_flaws_company.add(fid)
                newly_manifested.append(fid)

                g_days = int(shaz["grounding_days"]) if (fstate.severity >= 4 and rho > 0.35) else 0
                grounding_days = max(grounding_days, g_days)

                rep_hit = -float(shaz["rep_penalty"]) * rho * (1.0 + 0.25 * (fstate.severity - 3))
                reputation_delta += rep_hit

                ret_cost = 0.0
                if auto_retrofit_on_manifest and f_entry["fixes"]:
                    # Pay service-phase fix + fleet retrofit kit bill
                    cost_before = state.total_testing_cost_usd
                    days_before = state.total_testing_days
                    day_before = state.date_day
                    fix_res = apply_flaw_fix_to_state(state, fid, phase="service", fleet_size=fleet_size)
                    # Do not double-advance testing days for service retrofits
                    state.total_testing_cost_usd = cost_before
                    state.total_testing_days = days_before
                    state.date_day = day_before
                    ret_cost = float(fix_res["total_cost_usd"])
                    retrofit_cost_usd += ret_cost

                g_clause = f"Fleet grounded for {g_days} days. " if g_days > 0 else ""
                state.event_log.append(
                    templates["service_manifest"].format(
                        month=month_index,
                        flaw_label=f_entry["name"],
                        severity=fstate.severity,
                        fleet_fh=fleet_fh * month_index,
                        grounding_clause=g_clause,
                        retrofit_cost_usd=ret_cost,
                        rep_delta=rep_hit,
                    )
                )

        # 3. Ongoing non-combat squadron attrition (§5.8.3)
        lam_acc = float(shaz["accident_rate_per_1000fh"]) * fstate.residual_factor * fh_k
        # Deterministic inverse-CDF Poisson sample from keyed uniform
        u_acc = keyed_u01(campaign_seed, "service_acc", state.lineage_id, month_index, fid)
        acc_count = _poisson_icdf(lam_acc, u_acc)
        squadron_accidents += acc_count

    return ServiceMonthReport(
        month_index=month_index,
        fleet_size=fleet_size,
        fleet_fh=fleet_fh,
        newly_manifested_flaws=newly_manifested,
        grounding_days=grounding_days,
        squadron_accidents=squadron_accidents,
        retrofit_cost_usd=retrofit_cost_usd,
        reputation_delta=reputation_delta,
    )


def simulate_service_years(
    campaign_seed: int,
    state: LineageTestState,
    years: int = 4,
    max_fleet_size: int = 240,
    ledger: Optional[ExperienceLedger] = None,
) -> Dict[str, Any]:
    """Simulate multi-year squadron service ramp-up and aggregate operational outcomes."""
    tuning = load_testing_tuning()
    if ledger is not None:
        active_nov = compute_active_novelty_features(state.true_aircraft.feature_vector)
        ledger.record_experience(active_nov, float(tuning["experience_gain_service_entry"]))

    n_months = int(years) * 12
    total_accidents = 0
    total_grounding_days = 0
    total_retrofit_usd = 0.0
    total_rep_delta = 0.0
    manifested_all: List[str] = []

    for m in range(1, n_months + 1):
        # Fleet ramps up over first 24 months
        ramp = min(1.0, m / 24.0)
        fleet_n = max(12, int(round(max_fleet_size * ramp)))
        rep = simulate_service_month(
            campaign_seed=campaign_seed,
            state=state,
            month_index=m,
            fleet_size=fleet_n,
            auto_retrofit_on_manifest=True,
        )
        total_accidents += rep.squadron_accidents
        total_grounding_days += rep.grounding_days
        total_retrofit_usd += rep.retrofit_cost_usd
        total_rep_delta += rep.reputation_delta
        manifested_all.extend(rep.newly_manifested_flaws)

    return {
        "months_simulated": n_months,
        "manifested_flaws": manifested_all,
        "total_grounding_days": total_grounding_days,
        "total_squadron_accidents": total_accidents,
        "total_retrofit_cost_usd": total_retrofit_usd,
        "total_reputation_delta": total_rep_delta,
    }


def _poisson_icdf(lam: float, u: float) -> int:
    if lam <= 1e-9:
        return 0
    p = math.exp(-lam)
    cdf = p
    k = 0
    while u > cdf and k < 25:
        k += 1
        p *= lam / k
        cdf += p
    return k
