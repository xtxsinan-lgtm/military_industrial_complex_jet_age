"""Prototype flight-test syllabus execution across the 6 canonical test items (§5.5.5, §5.7)."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from .data_loader import (
    day_to_year,
    get_inflation_factor,
    load_flight_items_data,
    load_report_templates,
    load_testing_tuning,
)
from .features import StubTechContext
from .flaws import get_flaw_catalog_map, get_flaw_display_label
from .hashing import keyed_normal, keyed_u01
from .novelty import ExperienceLedger, compute_active_novelty_features
from .pilots import TestPilot, compute_pilot_multipliers, get_starter_pilots
from .sources import bayesian_normal_update
from .truth import (
    LineageTestState,
    apply_flaw_fix_to_state,
    apply_flaw_placard_to_state,
)


@dataclass
class FlightProgrammeResult:
    items_completed: List[str]
    total_sorties_flown: int
    flight_test_days: int
    flight_test_cost_usd: float
    crashes: int
    pilots_lost: int
    pilots_injured: int
    near_misses: int
    flaws_detected_in_flight: List[str]
    fixes_applied_in_flight: List[Dict[str, Any]]
    placards_applied_in_flight: List[Dict[str, Any]]
    halted_reason: Optional[str] = None


def run_flight_test_programme(
    campaign_seed: int,
    state: LineageTestState,
    syllabus_plan: Optional[Dict[str, str]] = None,
    pilots: Optional[List[TestPilot]] = None,
    flaw_resolution_policy: str = "fix_severe_else_placard",
    auto_replace_crashed_prototype: bool = True,
    tech_ctx: Optional[Any] = None,
    ledger: Optional[ExperienceLedger] = None,
) -> FlightProgrammeResult:
    """Execute the selected 6-item flight-test syllabus sortie-by-sortie (§5.5.5, §5.7).

    Parameters
    ----------
    syllabus_plan:
        Mapping `{item_id: depth}` where `item_id` is in the 6 syllabus items
        (`low_speed`, `speed_envelope`, `altitude_envelope`, `maneuver`,
        `high_aoa_spin`, `weapons_stores`) and `depth` is `"light" | "standard" | "thorough"`.
        Defaults to all 6 items at `"standard"`.
    flaw_resolution_policy:
        - `"fix_all"`: apply best engineering fix to every flaw discovered in flight test
        - `"fix_severe_else_placard"`: fix flaws with severity >= 3, placard severity <= 2
        - `"placard_all"`: placard all discovered flaws
        - `"ignore"`: accept/press on without fixing
    """
    ctx = tech_ctx if tech_ctx is not None else StubTechContext(date_day=state.date_day)
    flight_spec = load_flight_items_data()
    tuning = load_testing_tuning()
    templates = load_report_templates()
    flaw_map = get_flaw_catalog_map()

    if syllabus_plan is None:
        syllabus_plan = {item["id"]: "standard" for item in flight_spec["syllabus_items"]}

    roster = pilots if pilots is not None else get_starter_pilots()
    if state.prototypes_surviving <= 0:
        state.prototypes_Built = max(1, state.prototypes_built)
        state.prototypes_surviving = max(1, state.prototypes_built)

    start_day = state.date_day
    start_cost = state.total_testing_cost_usd

    items_completed: List[str] = []
    total_sorties = 0
    crashes = 0
    pilots_lost = 0
    pilots_injured = 0
    near_misses = 0
    flaws_detected: List[str] = []
    fixes_applied: List[Dict[str, Any]] = []
    placards_applied: List[Dict[str, Any]] = []
    halted_reason: Optional[str] = None

    time_factor = float(ctx.get("testing.flight_test_time_factor"))
    sigma_factor = float(ctx.get("testing.flight_sigma_factor"))
    flaw_detect_factor = float(ctx.get("testing.flaw_detect_factor"))
    unknown_mult = float(tuning["unknown_era_detect_mult"])
    has_ejection_seat = bool(ctx.get("systems.ejection_seat")) or (
        state.true_aircraft.feature_vector["has_ejection_seat"] > 0.5
    )

    active_nov = compute_active_novelty_features(state.true_aircraft.feature_vector)

    for item in sorted(flight_spec["syllabus_items"], key=lambda x: int(x["order"])):
        item_id = item["id"]
        if item_id not in syllabus_plan:
            continue
        depth_key = syllabus_plan[item_id]
        if depth_key not in flight_spec["depth_presets"]:
            raise ValueError(f"Unknown flight test depth '{depth_key}'")

        sortie_mult = float(flight_spec["depth_presets"][depth_key]["sortie_mult"])
        f_std = int(item["standard_sorties"])
        n_sorties = max(1, int(round(f_std * sortie_mult)))
        src_key = f"flight:{item_id}"

        sorties_done_in_item = 0
        for s_idx in range(n_sorties):
            if state.prototypes_surviving <= 0:
                if auto_replace_crashed_prototype:
                    # Build replacement prototype (#7.3)
                    nom_fly = float(state.nominal_perf.get("unit_flyaway_cost_usd", 450000.0))
                    repl_cost = nom_fly * float(tuning["prototype_additional_cost_mult"])
                    repl_days = int(round(float(tuning["prototype_base_build_days"]) * float(tuning["prototype_replacement_days_mult"])))
                    state.date_day += repl_days
                    state.total_testing_days += repl_days
                    state.total_testing_cost_usd += repl_cost
                    state.prototypes_built += 1
                    state.prototypes_surviving = 1
                else:
                    halted_reason = "halted_no_prototypes"
                    break

            # Select available pilot
            avail_pilots = [p for p in roster if p.is_available(state.date_day)]
            if not avail_pilots:
                # Advance clock until earliest injured pilot recovers or emergency hire
                injured = [p for p in roster if p.status == "injured"]
                if injured:
                    wait_d = max(1, min(p.injured_until_day for p in injured) - state.date_day)
                    state.date_day += wait_d
                    state.total_testing_days += wait_d
                    avail_pilots = [p for p in roster if p.is_available(state.date_day)]
                if not avail_pilots:
                    # Emergency hire replacement test pilot
                    emerg = get_starter_pilots()[0]
                    emerg.id = f"pilot_emerg_{total_sorties}"
                    emerg.name = "Maj. Howard 'Tick' Bridger"
                    roster.append(emerg)
                    avail_pilots = [emerg]

            pilot = avail_pilots[total_sorties % len(avail_pilots)]
            pmults = compute_pilot_multipliers(pilot)

            year = day_to_year(state.date_day)
            infl = get_inflation_factor(year)
            era_safety = max(0.75, 1.25 - 0.03 * (year - 1945))
            mass_scale = (max(1000.0, state.true_aircraft.feature_vector["empty_mass_kg"]) / 5000.0) ** 0.60

            # Parallel prototypes reduce calendar days per sortie
            n_parallel = min(state.prototypes_surviving, len(avail_pilots))
            sortie_days_float = (float(item["days_per_sortie"]) * time_factor) / max(1, n_parallel)
            # Accumulate integer days deterministically
            sortie_days = int(math.floor(sortie_days_float))
            if (total_sorties % 2 == 0) and (sortie_days_float - sortie_days >= 0.35):
                sortie_days += 1
            sortie_days = max(1, sortie_days)

            sortie_cost = float(item["cost_per_sortie_1950_usd"]) * mass_scale * infl

            state.date_day += sortie_days
            state.total_testing_days += sortie_days
            state.total_testing_cost_usd += sortie_cost
            total_sorties += 1
            sorties_done_in_item += 1
            pilot.flights_flown += 1
            pilot.experience = min(100.0, pilot.experience + 0.25)
            pilot.skill = min(96.0, pilot.skill + 0.08)

            # 1. Check flaw discovery & encounter on this sortie (§5.6.4, §5.7.2)
            crashed_this_sortie = False
            crash_cause_label = "Operational Envelope Exceedance"
            crash_flaw_id: Optional[str] = None

            for fid, fstate in state.true_aircraft.active_flaws.items():
                if fstate.detected:
                    continue
                f_entry = flaw_map[fid]
                p0 = float(f_entry["detect_prob_by_source"].get(src_key, 0.0))
                if p0 <= 0.0:
                    continue

                is_known = (year >= int(f_entry["known_from_year"])) or (fid in state.known_flaws_company)
                era_mult = 1.0 if is_known else unknown_mult
                pilot_det = pmults["detect_mult"]
                if item_id == "low_speed" and "carrier_qualified" in pilot.traits and state.true_aircraft.feature_vector["carrier_capable"] > 0.5:
                    pilot_det *= 1.25

                p_eff = min(0.99, max(0.0, p0 * flaw_detect_factor * era_mult * pilot_det))
                p_sortie = 1.0 - ((1.0 - p_eff) ** (1.0 / max(1, f_std)))

                u_enc = keyed_u01(campaign_seed, "flight_flaw_enc", state.lineage_id, item_id, s_idx, fid)
                if u_enc < p_sortie:
                    # Flaw encountered on this sortie!
                    p_crash_cond = min(
                        0.85,
                        max(
                            0.0,
                            float(f_entry["flight_incident"]["crash_prob_given_encounter"])
                            * (0.65 + 0.12 * fstate.severity)
                            * pmults["crash_mult"]
                            * era_safety,
                        ),
                    )
                    u_cr = keyed_u01(campaign_seed, "flight_flaw_crash", state.lineage_id, item_id, s_idx, fid)
                    flaw_label = get_flaw_display_label(f_entry, state.date_day, state.known_flaws_company)

                    if u_cr < p_crash_cond:
                        crashed_this_sortie = True
                        crash_cause_label = flaw_label
                        crash_flaw_id = fid
                        break
                    else:
                        # Pilot recovered -> near-miss & immediate flaw detection
                        near_misses += 1
                        fstate.detected = True
                        fstate.detected_day = state.date_day
                        fstate.detected_source = src_key
                        fstate.status = "detected"
                        state.known_flaws_company.add(fid)
                        flaws_detected.append(fid)

                        state.event_log.append(
                            templates["sortie_flaw_near_miss"].format(
                                flight_num=total_sorties,
                                day=state.date_day,
                                item_name=item["name"],
                                pilot_name=pilot.name,
                                flaw_label=flaw_label,
                                severity=fstate.severity,
                            )
                        )
                        _resolve_detected_flaw_in_flight(
                            state,
                            fid,
                            flaw_resolution_policy,
                            fixes_applied,
                            placards_applied,
                            templates,
                        )

            # 2. If no flaw-discovery crash, check baseline operational crash hazard (§5.7.2)
            if not crashed_this_sortie:
                h_base = float(item["base_crash_prob_per_sortie"])
                for fid, fstate in state.true_aircraft.active_flaws.items():
                    f_entry = flaw_map[fid]
                    enc_w = float(f_entry["flight_incident"]["encounter_weight"])
                    # Known unfixed flaws have 0.5x hazard as pilots are briefed
                    aware_mult = float(tuning["accepted_flaw_flight_hazard_mult"]) if fstate.detected else 1.0
                    h_base += 0.0006 * fstate.residual_factor * enc_w * aware_mult

                p_crash_base = min(0.25, h_base * pmults["crash_mult"] * era_safety)
                u_base_cr = keyed_u01(campaign_seed, "flight_base_crash", state.lineage_id, item_id, s_idx)
                if u_base_cr < p_crash_base:
                    crashed_this_sortie = True

            # 3. Resolve crash if one occurred
            if crashed_this_sortie:
                crashes += 1
                state.prototypes_surviving = max(0, state.prototypes_surviving - 1)
                inv_days = int(tuning["crash_investigation_days"])
                state.date_day += inv_days
                state.total_testing_days += inv_days

                # Investigation board identifies causal flaw with probability 0.75
                if crash_flaw_id is not None:
                    u_id = keyed_u01(campaign_seed, "crash_board_id", state.lineage_id, total_sorties)
                    if u_id < float(tuning["crash_cause_identify_prob"]):
                        fstate = state.true_aircraft.active_flaws[crash_flaw_id]
                        fstate.detected = True
                        fstate.detected_day = state.date_day
                        fstate.detected_source = src_key
                        fstate.status = "detected"
                        state.known_flaws_company.add(crash_flaw_id)
                        flaws_detected.append(crash_flaw_id)
                        _resolve_detected_flaw_in_flight(
                            state,
                            crash_flaw_id,
                            flaw_resolution_policy,
                            fixes_applied,
                            placards_applied,
                            templates,
                        )

                # Pilot bailout / ejection survival (§5.7.2)
                if not has_ejection_seat:
                    p_seat = float(tuning["pilot_base_survival_no_seat"])
                elif year < 1954:
                    p_seat = float(tuning["pilot_base_survival_early_seat"])
                else:
                    p_seat = float(tuning["pilot_base_survival_late_seat"])

                item_surv_mult = float(item["bailout_survival_mult"])
                ej_flaw = state.true_aircraft.active_flaws.get("ejection_envelope_deficiency")
                ej_flaw_mult = 0.75 if (ej_flaw is not None and ej_flaw.residual_factor > 0.30) else 1.0
                p_survive = max(0.15, min(0.96, p_seat * item_surv_mult * ej_flaw_mult))

                u_surv = keyed_u01(campaign_seed, "pilot_survive", state.lineage_id, total_sorties)
                if u_surv < p_survive:
                    u_inj = keyed_u01(campaign_seed, "pilot_injury", state.lineage_id, total_sorties)
                    if u_inj < float(tuning["pilot_injury_prob_given_survival"]):
                        pilots_injured += 1
                        rec_days = int(tuning["pilot_injury_recovery_days"])
                        pilot.status = "injured"
                        pilot.injured_until_day = state.date_day + rec_days
                        outcome_str = f"ejected safely but sustained injuries ({rec_days} days recovery)"
                    else:
                        outcome_str = "ejected and recovered uninjured"
                    state.event_log.append(
                        templates["sortie_crash_survived"].format(
                            flight_num=total_sorties,
                            day=state.date_day,
                            item_name=item["name"],
                            proto_idx=state.prototypes_built - state.prototypes_surviving,
                            cause_label=crash_cause_label,
                            pilot_name=pilot.name,
                            survival_outcome=outcome_str,
                            investigation_days=inv_days,
                        )
                    )
                else:
                    pilots_lost += 1
                    pilot.status = "deceased"
                    state.event_log.append(
                        templates["sortie_crash_fatal"].format(
                            flight_num=total_sorties,
                            day=state.date_day,
                            item_name=item["name"],
                            proto_idx=state.prototypes_built - state.prototypes_surviving,
                            cause_label=crash_cause_label,
                            pilot_name=pilot.name,
                            investigation_days=inv_days,
                        )
                    )

        if halted_reason is not None:
            break

        # Item telemetry Bayesian update upon completing item sorties (§5.5.5)
        if sorties_done_in_item > 0:
            comp_ratio = sorties_done_in_item / max(1.0, float(f_std))
            best_pilot = avail_pilots[0] if avail_pilots else roster[0]
            q_data = compute_pilot_multipliers(best_pilot)["data_sigma_mult"]
            state.campaign_seq += 1
            seq = state.campaign_seq

            for d, sigma_ref in item["driver_precision"].items():
                sigma_meas = (
                    float(sigma_ref)
                    * sigma_factor
                    * q_data
                    / math.sqrt(max(0.20, comp_ratio))
                )
                z_meas = keyed_normal(campaign_seed, "flight_meas", state.lineage_id, item_id, seq, d)
                theta_true = state.true_aircraft.get_true_driver_theta(d)
                y_meas = theta_true + sigma_meas * z_meas
                bayesian_normal_update(
                    state.beliefs[d],
                    y_meas=y_meas,
                    sigma_meas=sigma_meas,
                    source_tag="flight",
                )

            items_completed.append(item_id)
            if ledger is not None:
                ledger.record_experience(active_nov, float(tuning["experience_gain_flight_item"]))

    if len(items_completed) >= 5 and ledger is not None:
        ledger.record_experience(active_nov, float(tuning["experience_gain_full_programme"]))

    return FlightProgrammeResult(
        items_completed=items_completed,
        total_sorties_flown=total_sorties,
        flight_test_days=state.date_day - start_day,
        flight_test_cost_usd=state.total_testing_cost_usd - start_cost,
        crashes=crashes,
        pilots_lost=pilots_lost,
        pilots_injured=pilots_injured,
        near_misses=near_misses,
        flaws_detected_in_flight=flaws_detected,
        fixes_applied_in_flight=fixes_applied,
        placards_applied_in_flight=placards_applied,
        halted_reason=halted_reason,
    )


def _resolve_detected_flaw_in_flight(
    state: LineageTestState,
    flaw_id: str,
    policy: str,
    fixes_list: List[Dict[str, Any]],
    placards_list: List[Dict[str, Any]],
    templates: Dict[str, str],
) -> None:
    flaw_map = get_flaw_catalog_map()
    fstate = state.true_aircraft.active_flaws[flaw_id]
    f_entry = flaw_map[flaw_id]
    flaw_label = get_flaw_display_label(f_entry, state.date_day, state.known_flaws_company)

    if policy == "ignore":
        fstate.status = "accepted"
        return

    do_fix = False
    if policy == "fix_all" and f_entry["fixes"]:
        do_fix = True
    elif policy == "fix_severe_else_placard":
        if fstate.severity >= 3 and f_entry["fixes"]:
            do_fix = True

    if do_fix:
        res = apply_flaw_fix_to_state(state, flaw_id, phase="prototype")
        fixes_list.append(res)
        state.event_log.append(
            templates["fix_applied"].format(
                fix_name=res["fix_name"],
                flaw_label=flaw_label,
                cost_usd=res["total_cost_usd"],
                fix_days=int(res["fix_days"]),
                residual_pct=res["residual_factor"] * 100.0,
            )
        )
    else:
        res = apply_flaw_placard_to_state(state, flaw_id)
        placards_list.append(res)
        state.event_log.append(
            templates["placard_applied"].format(
                placard_name=res["placard_name"],
                flaw_label=flaw_label,
                residual_pct=res["residual_factor"] * 100.0,
            )
        )
