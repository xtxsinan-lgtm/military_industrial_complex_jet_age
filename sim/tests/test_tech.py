"""Comprehensive pytest suite for Module 03 (Tech Tree, TechContext, Research, Maturity)."""

import json
import math
from pathlib import Path
import pytest

from sim.mic.tech import (
    CompanyTechState,
    ahead_of_time_multiplier,
    apply_learning_by_doing,
    build_tech_context,
    date_str_to_day,
    day_to_year,
    effective_engineers,
    funding_multipliers,
    load_catalog,
    naca_report_multiplier,
    required_techs,
    required_techs_by_feature,
    step_company_tech_day,
)


GOLDEN_DIR = Path(__file__).resolve().parents[1] / "golden"


def test_catalog_integrity_and_dag():
    cat = load_catalog()
    assert len(cat.nodes) >= 60
    branches = {n.branch for n in cat.nodes.values()}
    assert branches == {
        "aero",
        "structures",
        "propulsion",
        "avionics",
        "armament",
        "manufacturing",
        "testing",
    }
    # Every key in effect_keys.json must be provided by at least one node
    provided = {k for n in cat.nodes.values() for k in n.effects}
    assert set(cat.keys.keys()) == provided


def test_start_1945_matches_effect_keys_spec():
    cat = load_catalog()
    state = CompanyTechState.create_starting_1945("north_american", date_day=0)
    ctx = state.context(cat)

    assert len(ctx.values) == len(cat.keys)
    for key, spec in cat.keys.items():
        val = ctx.get(key)
        if spec.value_type == "float":
            assert math.isclose(float(val), float(spec.start_1945), rel_tol=1e-9, abs_tol=1e-9), key
        else:
            assert val == spec.start_1945, key


def test_null_context_values():
    cat = load_catalog()
    ctx = build_tech_context("empty_co", date_day=0, unlocked_maturity={}, catalog=cat)
    for key, spec in cat.keys.items():
        assert ctx.get(key) == spec.null_value
        assert ctx.provider[key] is None
        assert ctx.maturity_of(key) == 1.0


def test_aggregation_and_tie_breakers():
    cat = load_catalog()
    # Unlock swept wing (35 deg), 45 deg sweep, and delta wing (60 deg)
    unlocked = {
        "aero_1945_compressible_subsonic": 0.90,
        "aero_1945_swept_wing_theory": 0.80,
        "aero_1950_high_sweep_45deg": 0.60,
        "aero_1948_tailless_delta_basics": 0.40,
        "struct_1945_stressed_skin_7075": 0.90,
        "struct_1946_thick_skin_box_spar": 0.70,
        "struct_1952_integrally_stiffened_skins": 0.50,
    }
    ctx = build_tech_context("convair", date_day=2000, unlocked_maturity=unlocked, catalog=cat)

    # max key: aero.wing_sweep_max_deg -> 60.0 from aero_1948_tailless_delta_basics (maturity 0.40)
    assert math.isclose(ctx.get("aero.wing_sweep_max_deg"), 60.0)
    assert ctx.provider["aero.wing_sweep_max_deg"] == "aero_1948_tailless_delta_basics"
    assert math.isclose(ctx.maturity_of("aero.wing_sweep_max_deg"), 0.40)

    # min key: aero.thin_wing_tc_min -> 0.06 from aero_1950_high_sweep_45deg (maturity 0.60)
    assert math.isclose(ctx.get("aero.thin_wing_tc_min"), 0.06)
    assert ctx.provider["aero.thin_wing_tc_min"] == "aero_1950_high_sweep_45deg"
    assert math.isclose(ctx.maturity_of("aero.thin_wing_tc_min"), 0.60)

    # mul key: struct.weight_factor -> 0.97 * 0.95 = 0.9215; lowest maturity contributor is 0.50
    assert math.isclose(ctx.get("struct.weight_factor"), 0.97 * 0.95, rel_tol=1e-9)
    assert ctx.provider["struct.weight_factor"] == "struct_1952_integrally_stiffened_skins"
    assert math.isclose(ctx.maturity_of("struct.weight_factor"), 0.50)


def test_required_techs_minimal_sufficient_and_caps():
    cat = load_catalog()
    unlocked = cat.baseline_unlocked_maturity()
    unlocked.update(
        {
            "aero_1945_swept_wing_theory": 0.85,  # 35 deg sweep
            "aero_1950_high_sweep_45deg": 0.50,  # 45 deg sweep, 0.06 t/c
            "aero_1948_tailless_delta_basics": 0.35,  # 60 deg sweep, delta
            "aero_1946_auto_le_slats": 0.75,
            "aero_1948_all_moving_tail": 0.70,
            "sys_1946_hydraulic_boost_controls": 0.80,
            "arm_1947_m3_high_rof_50cal": 0.90,
        }
    )
    ctx = build_tech_context("north_american", date_day=1800, unlocked_maturity=unlocked, catalog=cat)

    # F-86E style design: 35 deg sweep, 0.095 t/c, auto slats, all-moving tail, M3 .50 guns
    f86_design = {
        "wing": {
            "sweep_deg": 35.0,
            "tc_ratio": 0.095,
            "aspect_ratio": 4.79,
            "devices": ["le_slats", "fowler_flaps"],
        },
        "empennage": {"all_moving_tail": True},
        "systems": {"powered_controls": True, "avionics_level": 1},
        "armament": {"guns": ["m3_50"], "hardpoints": 4},
    }
    by_feat = required_techs_by_feature(f86_design, ctx, catalog=cat)
    # 35 deg sweep should only require aero_1945_swept_wing_theory (35 deg), NOT the 60 deg delta tech!
    assert by_feat["aero.wing_sweep_max_deg"] == "aero_1945_swept_wing_theory"
    assert by_feat["aero.thin_wing_tc_min"] == "aero_1950_high_sweep_45deg"
    assert by_feat["aero.le_slats"] == "aero_1946_auto_le_slats"
    assert by_feat["aero.all_moving_tail"] == "aero_1948_all_moving_tail"
    assert by_feat["unlock.gun.m3_50"] == "arm_1947_m3_high_rof_50cal"
    assert "aero_1948_tailless_delta_basics" not in required_techs(f86_design, ctx, catalog=cat)

    # Exceeding cap should raise TECH_CAP:<key>
    bad_design = {"aero.wing_sweep_max_deg": 65.0}
    with pytest.raises(ValueError, match="TECH_CAP:aero.wing_sweep_max_deg"):
        required_techs(bad_design, ctx, catalog=cat)


def test_ahead_of_time_and_brooks_law():
    cat = load_catalog()
    # Brooks's law: <= 15 is linear, > 15 is sublinear, capped at 40
    assert math.isclose(effective_engineers(10, cat), 10.0)
    assert math.isclose(effective_engineers(15, cat), 15.0)
    eff_30 = effective_engineers(30, cat)
    assert 15.0 < eff_30 < 30.0
    assert math.isclose(effective_engineers(500, cat), 40.0)

    # Ahead of time: researching a 1955.0 tech in 1948.0 (day ~1095) is heavily penalized
    day_1948 = date_str_to_day("1948-01-01")
    m_early = ahead_of_time_multiplier(day_1948, 1955.0, cat)
    assert m_early < 0.25

    # Within 0.5 yr lead window -> 1.0
    day_late_1954 = date_str_to_day("1954-09-01")
    assert math.isclose(ahead_of_time_multiplier(day_late_1954, 1955.0, cat), 1.0)

    # Behind time -> > 1.0 catchup bonus
    day_1958 = date_str_to_day("1958-01-01")
    m_late = ahead_of_time_multiplier(day_1958, 1955.0, cat)
    assert m_late > 1.50


def test_irad_vs_govt_contract_and_naca_diffusion():
    cat = load_catalog()
    # Compare IRAD vs govt_contract on aero_1945_swept_wing_theory starting 1945-07-01
    start_day = date_str_to_day("1945-07-01")
    st_irad = CompanyTechState.create_starting_1945("lockheed", date_day=start_day, catalog=cat)
    st_govt = CompanyTechState.create_starting_1945("north_american", date_day=start_day, catalog=cat)

    st_irad.start_or_update_project("aero_1945_swept_wing_theory", assigned_engineers=15, funding_mode="irad")
    st_govt.start_or_update_project("aero_1945_swept_wing_theory", assigned_engineers=15, funding_mode="govt_contract")

    res_irad = step_company_tech_day(st_irad, cat)
    res_govt = step_company_tech_day(st_govt, cat)

    # Govt contract progresses 15% faster and costs company only 20% of direct USD per eng-day
    assert math.isclose(
        res_govt.progress_deltas["aero_1945_swept_wing_theory"],
        res_irad.progress_deltas["aero_1945_swept_wing_theory"] * 1.15,
        rel_tol=1e-6,
    )
    assert res_govt.company_cost_usd < res_irad.company_cost_usd * 0.30
    assert res_govt.govt_cost_usd > 0.0

    # NACA passive diffusion after historical_year + 2.0 years with 0 engineers assigned
    day_1948 = date_str_to_day("1948-01-01")
    st_passive = CompanyTechState.create_starting_1945("grumman", date_day=day_1948, catalog=cat)
    res_p = step_company_tech_day(st_passive, cat)
    assert res_p.progress_deltas.get("aero_1945_swept_wing_theory", 0.0) > 0.0


def test_learning_by_doing_and_passive_maturity_cap():
    cat = load_catalog()
    st = CompanyTechState.create_starting_1945("mcdonnell", date_day=0, catalog=cat)
    st.unlocked_maturity["aero_1945_swept_wing_theory"] = 0.35

    # Passive maturity cannot exceed passive_maturity_cap (0.65)
    st.unlocked_maturity["prop_1945_early_axial_compressor"] = 0.6499
    step_company_tech_day(st, cat)
    assert math.isclose(st.unlocked_maturity["prop_1945_early_axial_compressor"], 0.65, abs_tol=1e-6)
    step_company_tech_day(st, cat)
    assert math.isclose(st.unlocked_maturity["prop_1945_early_axial_compressor"], 0.65, abs_tol=1e-6)

    # Learning by doing boosts maturity above 0.65 asymptotically toward 1.0
    updated = apply_learning_by_doing(
        st,
        ["prop_1945_early_axial_compressor", "aero_1945_swept_wing_theory"],
        event_type="first_flight",
        catalog=cat,
    )
    assert updated["prop_1945_early_axial_compressor"] > 0.65
    assert math.isclose(
        updated["prop_1945_early_axial_compressor"],
        0.65 + 0.12 * (1.0 - 0.65),
        rel_tol=1e-6,
    )


def test_golden_vectors_match():
    cat = load_catalog()

    with open(GOLDEN_DIR / "tech_context_start_1945.json", "r", encoding="utf-8") as f:
        golden_start = json.load(f)
    st = CompanyTechState.create_starting_1945(
        golden_start["company_id"],
        date_day=golden_start["date_day"],
        catalog=cat,
    )
    ctx_dict = st.context(cat).to_dict()
    assert ctx_dict["unlocked"] == golden_start["unlocked"]
    for k, expected_v in golden_start["values"].items():
        actual_v = ctx_dict["values"][k]
        if isinstance(expected_v, float):
            assert math.isclose(float(actual_v), expected_v, rel_tol=1e-6, abs_tol=1e-9), k
        else:
            assert actual_v == expected_v, k

    with open(GOLDEN_DIR / "tech_aggregation_and_required.json", "r", encoding="utf-8") as f:
        golden_agg = json.load(f)
    for case in golden_agg["cases"]:
        c = build_tech_context(
            company_id=case["company_id"],
            date_day=case["date_day"],
            unlocked_maturity=case["unlocked_maturity"],
            catalog=cat,
        )
        for k, exp_v in case["expected_values"].items():
            act_v = c.get(k)
            if isinstance(exp_v, float):
                assert math.isclose(float(act_v), exp_v, rel_tol=1e-6, abs_tol=1e-9)
            else:
                assert act_v == exp_v
        for k, exp_m in case["expected_maturity"].items():
            assert math.isclose(c.maturity_of(k), exp_m, rel_tol=1e-6, abs_tol=1e-9)
        req = required_techs(case["design_features"], c, catalog=cat)
        assert req == case["expected_required_techs"]

    with open(GOLDEN_DIR / "tech_research_and_maturity.json", "r", encoding="utf-8") as f:
        golden_res = json.load(f)
    for vec in golden_res["aot_vectors"]:
        m = ahead_of_time_multiplier(vec["date_day"], vec["historical_year"], cat)
        assert math.isclose(m, vec["expected_multiplier"], rel_tol=1e-6)
    for vec in golden_res["brooks_vectors"]:
        e = effective_engineers(vec["assigned_engineers"], cat)
        assert math.isclose(e, vec["expected_effective"], rel_tol=1e-6)


def test_content_and_names_integrity():
    cat = load_catalog()
    data_dir = Path(__file__).resolve().parents[1] / "data"

    with open(data_dir / "names" / "companies_and_people.json", "r", encoding="utf-8") as f:
        names_cp = json.load(f)["strings"]
    with open(data_dir / "names" / "tech_and_components.json", "r", encoding="utf-8") as f:
        names_tc = json.load(f)["strings"]
    with open(data_dir / "names" / "designation_rules_us_pre1962.json", "r", encoding="utf-8") as f:
        desig_rules = json.load(f)

    all_strings = {}
    all_strings.update(names_cp)
    all_strings.update(names_tc)

    # Check all tech node and component name_keys
    for node in cat.nodes.values():
        assert node.name_key in all_strings, f"Missing name_key {node.name_key}"
    for ctype, cmap in cat.components.items():
        for cid, cdata in cmap.items():
            assert cdata["name_key"] in all_strings, f"Missing component name_key {cdata['name_key']}"

    # Check chief designers
    with open(data_dir / "companies" / "chief_designers_us_1945_1960.json", "r", encoding="utf-8") as f:
        designers = {d["id"]: d for d in json.load(f)["designers"]}
    for did, d in designers.items():
        assert d["name_key"] in all_strings
        assert d["title_key"] in all_strings
        for br, bonus in d["research_branch_bonuses"].items():
            assert -0.15 <= bonus <= 0.15

    # Check airframers
    with open(data_dir / "companies" / "airframers_us_1945_1960.json", "r", encoding="utf-8") as f:
        airframers = json.load(f)["airframers"]
    assert len(airframers) == 13
    for af in airframers:
        assert af["name_key"] in all_strings
        assert af["short_name_key"] in all_strings
        assert af["chief_designer_id"] in designers
        if af["secondary_designer_id"] is not None:
            assert af["secondary_designer_id"] in designers
        assert af["id"] in desig_rules["usn_buaer_fighter_rules"]["manufacturer_letters"]
        st = CompanyTechState.create_starting_1945(
            af["id"],
            extra_unlocked=af["starting_tech_overrides"],
            catalog=cat,
        )
        assert len(st.context(cat).values) == len(cat.keys)

    # Check engine makers
    with open(data_dir / "companies" / "engine_makers_us_1945_1960.json", "r", encoding="utf-8") as f:
        engine_makers = json.load(f)["engine_makers"]
    assert len(engine_makers) == 5
    for em in engine_makers:
        assert em["name_key"] in all_strings
        assert em["short_name_key"] in all_strings
        assert em["chief_designer_id"] in designers
        for tid in em["starting_tech_overrides"]:
            assert tid in cat.nodes

    # Check startup presets
    with open(data_dir / "companies" / "startup_presets.json", "r", encoding="utf-8") as f:
        presets = json.load(f)["presets"]
    assert len(presets) == 4
    for pr in presets:
        assert pr["name_key"] in all_strings
        assert pr["desc_key"] in all_strings
        assert pr["chief_designer_id"] in designers
