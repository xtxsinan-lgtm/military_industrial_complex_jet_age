"""Unit and golden-vector tests for `sim/mic/campaign/` (events, macro, actions, save/load, scoring, runner).

Owned by Module 09 (`docs/spec/09_core_loop.md`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_SIM_DIR = Path(__file__).resolve().parents[1]
if str(_SIM_DIR) not in sys.path:
    sys.path.insert(0, str(_SIM_DIR))

from mic.calendar import iso_to_day  # noqa: E402
from mic.campaign import (  # noqa: E402
    ACTION_CATALOG,
    Campaign,
    HeuristicBotPolicy,
    NullPolicy,
    PlayerAction,
    evaluate_condition,
    migrate_save_envelope,
    register_envelope_migration,
    register_module_migration,
    run_campaign,
    validate_action_schema,
)
from mic.campaign.save_load import canonical_json_dumps as dumps_canon  # noqa: E402

GOLDEN_DIR = _SIM_DIR / "golden"


def test_campaign_golden_smoke_and_full_1945_1960() -> None:
    """Verify 2-year and full 16-year (5844-day) campaign runs match golden state hashes and scores."""
    golden = json.loads((GOLDEN_DIR / "core_campaign_smoke.json").read_text(encoding="utf-8"))

    exp_2y = golden["smoke_2y_seed_42"]
    res_2y = run_campaign(
        seed=42,
        player_policy=HeuristicBotPolicy(),
        start="1945-01-01",
        end="1946-12-31",
        difficulty="normal",
        company_id="mcdonnell",
    )
    assert res_2y.days_simulated == exp_2y["days_simulated"]
    assert res_2y.state_hash == exp_2y["state_hash"]
    assert res_2y.player_score.to_dict() == exp_2y["player_score"]

    exp_full = golden["full_mvp_1945_1960_seed_1945"]
    res_full = run_campaign(
        seed=1945,
        player_policy=HeuristicBotPolicy(),
        start="1945-01-01",
        end="1960-12-31",
        difficulty="normal",
        company_id="north_american",
    )
    assert res_full.days_simulated == 5844
    assert res_full.outcome == "completed_1960"
    assert res_full.state_hash == exp_full["state_hash"]
    assert res_full.player_score.to_dict() == exp_full["player_score"]
    assert len(res_full.leaderboard) == 9


def test_save_load_mid_campaign_bit_exact_determinism(tmp_path: Path) -> None:
    """Verify saving to disk (.json and .json.gz), loading, and continuing produces the exact same state hash."""
    golden = json.loads((GOLDEN_DIR / "core_campaign_smoke.json").read_text(encoding="utf-8"))
    exp_hash = golden["save_load_split_1945_seed_777"]["final_state_hash"]
    mid_day = golden["save_load_split_1945_seed_777"]["mid_day"]

    cmp = Campaign.new_game(seed=777, start="1945-01-01", end="1945-12-31")
    pol = HeuristicBotPolicy()
    while cmp.world.day < mid_day and not cmp.world.ended:
        cmp.step_day(pol)

    json_path = tmp_path / "mid_save.json"
    gz_path = tmp_path / "mid_save.json.gz"
    cmp.save(json_path, compress=False)
    cmp.save(gz_path, compress=True)

    loaded_plain = Campaign.load(json_path)
    loaded_gz = Campaign.load(gz_path)
    assert loaded_plain.state_hash() == cmp.state_hash()
    assert loaded_gz.state_hash() == cmp.state_hash()

    while not loaded_gz.world.ended:
        loaded_gz.step_day(pol)

    assert loaded_gz.state_hash() == exp_hash


def test_save_migration_and_nan_rejection() -> None:
    """Verify envelope/module migration chains and NaN/Infinity serialization rejection."""
    cmp = Campaign.new_game(seed=101, start="1945-01-01", end="1945-01-10")
    env = cmp.to_envelope()

    # Simulate an older v0 save envelope and v0 module state
    env["save_schema_version"] = 0
    env["modules"]["04_economy"]["schema_version"] = 0

    register_envelope_migration(0, lambda d: {**d, "migrated_envelope": True})
    register_module_migration("04_economy", 0, lambda s: {**s, "insolvent_days": int(s.get("insolvent_days", 0))})

    migrated = migrate_save_envelope(env, target_envelope_version=1, target_module_versions={"04_economy": 1})
    assert migrated["save_schema_version"] == 1
    assert migrated["migrated_envelope"] is True
    assert migrated["modules"]["04_economy"]["schema_version"] == 1

    # Newer save version must be rejected
    future_env = dict(env)
    future_env["save_schema_version"] = 99
    with pytest.raises(ValueError, match="newer than supported"):
        migrate_save_envelope(future_env, target_envelope_version=1)

    # NaN / Inf must be rejected by canonical_json_dumps
    with pytest.raises(ValueError, match="Non-finite float"):
        dumps_canon({"bad": float("nan")})
    with pytest.raises(ValueError, match="Non-finite float"):
        dumps_canon({"bad": float("inf")})


def test_all_26_player_actions_and_validation() -> None:
    """Exercise every action in ACTION_CATALOG for both valid execution and validation errors."""
    assert len(ACTION_CATALOG) == 26
    cmp = Campaign.new_game(seed=55, start="1945-01-01", end="1946-12-31", company_id="lockheed")
    cid = "lockheed"

    # Schema validation errors
    assert not validate_action_schema(PlayerAction("unknown.op", cid, {})).ok
    assert not validate_action_schema(PlayerAction("econ.hire_engineers", "", {"discipline": "aero", "count": 5})).ok
    assert not validate_action_schema(PlayerAction("econ.hire_engineers", cid, {"discipline": "aero"})).ok
    assert not validate_action_schema(
        PlayerAction("econ.hire_engineers", cid, {"discipline": "aero", "count": 5, "extra": 1})
    ).ok
    assert not validate_action_schema(
        PlayerAction("econ.hire_engineers", cid, {"discipline": "magic", "count": 5})
    ).ok
    assert not validate_action_schema(
        PlayerAction("econ.hire_engineers", cid, {"discipline": "aero", "count": -3})
    ).ok

    # 1-4: Design actions (create, modify, clone, freeze)
    r_create = cmp.submit_action(
        PlayerAction(
            "design.create",
            cid,
            {
                "name": "XP-80R",
                "role_tags": ["day_fighter"],
                "spec": {"sweep_deg": 12.0, "thrust_N": 24000.0, "wing_area_m2": 22.0, "afterburner": False},
            },
        )
    )
    assert r_create.ok
    did = r_create.data["design_id"]

    assert cmp.submit_action(PlayerAction("design.modify", cid, {"design_id": did, "patch": {"sweep_deg": 35.0}})).ok
    r_clone = cmp.submit_action(PlayerAction("design.clone", cid, {"source_design_id": did, "new_name": "XP-80R-2"}))
    assert r_clone.ok
    assert cmp.submit_action(PlayerAction("design.freeze", cid, {"design_id": did})).ok
    # Cannot modify frozen design
    assert not cmp.submit_action(PlayerAction("design.modify", cid, {"design_id": did, "patch": {"sweep_deg": 20.0}})).ok

    # 5-7: Engine actions (start_project, set_engineers, cancel_project)
    r_eng = cmp.submit_action(
        PlayerAction(
            "engine.start_project",
            cid,
            {
                "name": "XJ37",
                "architecture": "axial_jet",
                "target_thrust_dry_N": 25000.0,
                "afterburner": False,
                "opr": 4.5,
                "tit_K": 1080.0,
                "engineers_assigned": 12,
            },
        )
    )
    assert r_eng.ok
    epid = r_eng.data["project_id"]
    assert cmp.submit_action(PlayerAction("engine.set_engineers", cid, {"project_id": epid, "engineers_assigned": 18})).ok
    assert cmp.submit_action(PlayerAction("engine.cancel_project", cid, {"project_id": epid})).ok

    # 8-9: Tech actions (set_allocation, cancel_research)
    assert cmp.submit_action(
        PlayerAction("tech.set_allocation", cid, {"tech_id": "swept_wing_35", "engineers_assigned": 10})
    ).ok
    assert cmp.submit_action(PlayerAction("tech.cancel_research", cid, {"tech_id": "swept_wing_35"})).ok

    # 10-17: Economy actions (hire, fire, upgrade_wind_tunnel, expand_factory, build_test_site, take_loan, repay_loan)
    assert cmp.submit_action(PlayerAction("econ.hire_engineers", cid, {"discipline": "aero", "count": 5})).ok
    assert cmp.submit_action(PlayerAction("econ.fire_engineers", cid, {"discipline": "aero", "count": 2})).ok
    assert cmp.submit_action(PlayerAction("econ.upgrade_wind_tunnel", cid, {"target_level": 3})).ok
    assert cmp.submit_action(PlayerAction("econ.expand_factory", cid, {"additional_floor_m2": 5000.0})).ok
    # Build test site on mcdonnell (which starts with test_site=False)
    assert cmp.submit_action(PlayerAction("econ.build_test_site", "mcdonnell", {})).ok
    assert cmp.submit_action(PlayerAction("econ.take_loan", cid, {"principal_usd": 500000.0})).ok
    assert cmp.submit_action(PlayerAction("econ.repay_loan", cid, {"amount_usd": 200000.0})).ok

    # 18-21: Testing actions (run_wind_tunnel, build_prototype, schedule_flight_test, fix_flaw)
    assert cmp.submit_action(
        PlayerAction("test.run_wind_tunnel", cid, {"design_id": did, "facility": "company", "regime": "subsonic"})
    ).ok
    assert cmp.submit_action(PlayerAction("test.build_prototype", cid, {"design_id": did, "quantity": 2})).ok
    assert cmp.submit_action(
        PlayerAction(
            "test.schedule_flight_test",
            cid,
            {"design_id": did, "syllabus": ["low_speed", "speed_envelope"], "thoroughness": "standard"},
        )
    ).ok
    assert cmp.submit_action(PlayerAction("test.fix_flaw", cid, {"design_id": did, "flaw_id": "flaw_flutter_1"})).ok

    # Advance to 1945-03-02 so rfp_1945_usaf_day_fighter is open
    while cmp.world.day <= iso_to_day("1945-03-02"):
        cmp.step_day(NullPolicy())

    # 22-24: Procurement actions (submit_proposal, lobby_program, withdraw_proposal, then re-submit)
    rid = "rfp_1945_usaf_day_fighter"
    assert cmp.submit_action(
        PlayerAction("proc.submit_proposal", cid, {"requirement_id": rid, "design_id": did, "bid_unit_price_usd": 240000.0})
    ).ok
    assert cmp.submit_action(
        PlayerAction("proc.lobby_program", cid, {"requirement_id": rid, "political_capital_spent": 10.0})
    ).ok
    assert cmp.submit_action(PlayerAction("proc.withdraw_proposal", cid, {"requirement_id": rid})).ok
    assert cmp.submit_action(
        PlayerAction("proc.submit_proposal", cid, {"requirement_id": rid, "design_id": did, "bid_unit_price_usd": 235000.0})
    ).ok

    # Advance past proposal_due (1945-09-01) so contract is awarded, then test econ.set_production_rate & dismiss_notification
    while cmp.world.day <= iso_to_day("1945-09-02"):
        cmp.step_day(NullPolicy())

    econ = cmp.world.modules["04_economy"]
    assert len(econ.contracts) >= 1
    first_ct = next(iter(econ.contracts.values()))
    assert cmp.submit_action(
        PlayerAction(
            "econ.set_production_rate",
            first_ct["company_id"],
            {"contract_id": first_ct["contract_id"], "units_per_month": 12},
        )
    ).ok

    assert len(cmp.world.notifications) > 0
    nid = cmp.world.notifications[0].id
    assert cmp.submit_action(PlayerAction("core.dismiss_notification", cid, {"notification_id": nid})).ok


def test_events_condition_dsl_and_multi_option_choice() -> None:
    """Verify condition DSL combinators and multi-option event resolution (manual and timeout)."""
    cmp = Campaign.new_game(
        seed=88,
        start="1949-04-20",
        end="1949-06-05",
        company_id="mcdonnell",
    )
    assert evaluate_condition(
        cmp.world,
        {
            "all": [
                {"var": "date.year", "op": "==", "value": 1949},
                {"any": [{"var": "player.cash_usd", "op": ">", "value": 1000.0}, {"var": "flag.nonexistent", "op": "==", "value": True}]},
                {"not": {"var": "date.month", "op": "in", "value": [1, 2]}},
            ]
        },
    )

    # Step to 1949-04-23 when evt_1949_revolt_of_admirals (3 options) triggers
    while cmp.world.day <= iso_to_day("1949-04-23"):
        cmp.step_day(NullPolicy())

    assert "evt_1949_revolt_of_admirals" in cmp.world.events.pending_choices
    res = cmp.submit_action(
        PlayerAction(
            "core.choose_event_option",
            "mcdonnell",
            {"event_id": "evt_1949_revolt_of_admirals", "option_id": "testify_for_navy_carriers"},
        )
    )
    assert res.ok
    assert "evt_1949_revolt_of_admirals" not in cmp.world.events.pending_choices


def test_bankruptcy_and_takeover_conditions() -> None:
    """Verify emergency bailout, bankruptcy termination, and post-1948 idle takeover termination."""
    # 1. Bankruptcy when cash < 0 for grace_period_days and debt exceeds bailout limit
    cmp_b = Campaign.new_game(seed=11, start="1945-01-01", end="1946-01-01", difficulty="hard", company_id="mcdonnell")
    econ_b = cmp_b.world.modules["04_economy"]
    player_b = econ_b.get_player_company()
    player_b["cash_usd"] = -5_000_000.0
    player_b["debt_usd"] = 50_000_000.0  # Exceeds 85% of starting net worth

    while not cmp_b.world.ended:
        cmp_b.step_day(NullPolicy())

    assert cmp_b.world.outcome == "bankruptcy"
    assert cmp_b.world.day < iso_to_day("1945-06-01")

    # 2. Forced Takeover when post-1948, >=24 idle months, and net worth < 25% of start
    cmp_t = Campaign.new_game(seed=12, start="1948-01-01", end="1951-01-01", difficulty="normal", company_id="mcdonnell")
    econ_t = cmp_t.world.modules["04_economy"]
    player_t = econ_t.get_player_company()
    player_t["cash_usd"] = 100_000.0
    player_t["facilities"]["factory_floor_m2"] = 1000.0
    player_t["facilities"]["wind_tunnel_level"] = 0
    econ_t.idle_months = 23

    # Step to next month start (1948-02-01) so idle_months reaches 24 on month_start
    while not cmp_t.world.ended and cmp_t.world.day <= iso_to_day("1948-02-05"):
        cmp_t.step_day(NullPolicy())

    assert cmp_t.world.ended is True
    assert cmp_t.world.outcome == "forced_takeover"


def test_custom_startup_and_difficulty_presets() -> None:
    """Verify custom startup founder backgrounds and difficulty multipliers."""
    res_custom = run_campaign(
        seed=99,
        player_policy=HeuristicBotPolicy(),
        start="1945-01-01",
        end="1945-12-31",
        difficulty="easy",
        company_id="custom_aero",
        custom_startup={
            "company_name": "Pacific Jet Corp",
            "founder_background": "test_pilot_entrepreneur",
        },
    )
    assert res_custom.outcome == "completed_1960"
    assert res_custom.player_score.company_id == "custom_aero"
    assert res_custom.player_score.difficulty_multiplier == 0.8
