"""Comprehensive pytest suite for Module 02 (sim/mic/engine/)."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from mic.engine import (
    DEFAULT_START_1945_ENGINE_TECH,
    EngineDesignInput,
    EngineProjectState,
    EngineSpec,
    allocate_rnd_priorities,
    compute_ambition,
    compute_diagnostics,
    compute_inlet_recovery,
    compute_third_party_engine_sale,
    design_engine,
    design_input_from_hist_dict,
    duane_mtbf,
    evaluate_rnd_project,
    list_historical_engines,
    load_historical_engine,
    load_historical_engine_data,
    resolve_rnd_outcome,
    validate_engine_against_tech,
)

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "golden"


def test_contract_4_3_interface_and_static_fields():
    """Verify EngineSpec contract §4.3 callable signatures and static fields."""
    eng = load_historical_engine("j57_p_21", build_deck=True)
    assert isinstance(eng, EngineSpec)
    for attr in ("mass_kg", "diameter_m", "length_m", "unit_cost", "mtbf_h", "maint_mh_per_fh"):
        val = getattr(eng, attr)
        assert isinstance(val, float) and val > 0.0

    f_dry = eng.thrust_N(0.0, 0.0, 1.0, False)
    f_ab = eng.thrust_N(0.0, 0.0, 1.0, True)
    sfc_dry = eng.tsfc(0.0, 0.0, 1.0, False)
    sfc_ab = eng.tsfc(0.0, 0.0, 1.0, True)

    assert f_ab > f_dry > 30000.0
    assert sfc_ab > sfc_dry > 1e-5


def test_golden_cycle_sls():
    """Verify exact reproduction of sim/golden/engine_cycle_sls.json within 1e-6."""
    with open(GOLDEN_DIR / "engine_cycle_sls.json", "r", encoding="utf-8") as f:
        golden = json.load(f)
    tol = golden["tolerance_rel"]
    for case in golden["cases"]:
        sp = load_historical_engine(case["engine_id"], build_deck=False)
        for key in (
            "sls_dry_thrust_N",
            "sls_ab_thrust_N",
            "sls_dry_tsfc",
            "sls_ab_tsfc",
            "mass_kg",
            "diameter_m",
            "length_m",
            "unit_cost",
            "mtbf_h",
            "maint_mh_per_fh",
        ):
            assert getattr(sp, key) == pytest.approx(case[key], rel=tol, abs=1e-9)


def test_golden_deck_queries():
    """Verify exact reproduction of sim/golden/engine_deck_queries.json within 1e-6."""
    with open(GOLDEN_DIR / "engine_deck_queries.json", "r", encoding="utf-8") as f:
        golden = json.load(f)
    tol = golden["tolerance_rel"]

    loaded = {}
    for q in golden["deck_queries"]:
        eid = q["engine_id"]
        if eid not in loaded:
            loaded[eid] = load_historical_engine(eid, build_deck=True)
        sp = loaded[eid]
        assert sp.thrust_N(q["mach"], q["alt_m"], q["throttle"], q["ab"]) == pytest.approx(
            q["thrust_N"], rel=tol, abs=1e-6
        )
        assert sp.tsfc(q["mach"], q["alt_m"], q["throttle"], q["ab"]) == pytest.approx(
            q["tsfc"], rel=tol, abs=1e-12
        )
        assert sp.fuel_flow_kgps(q["mach"], q["alt_m"], q["throttle"], q["ab"]) == pytest.approx(
            q["fuel_flow_kgps"], rel=tol, abs=1e-8
        )

    for iq in golden["inlet_recovery_queries"]:
        mode = iq["inlet_type"]
        pi_d = compute_inlet_recovery(
            iq["mach"],
            inlet_type=mode,
            spike_inlet=(mode == "spike"),
            variable_inlet=(mode == "variable"),
        )
        assert pi_d == pytest.approx(iq["pi_d"], rel=tol, abs=1e-8)

    for dq in golden["duane_queries"]:
        val = duane_mtbf(dq["mtbf_init"], dq["hours"], dq["alpha"])
        assert val == pytest.approx(dq["mtbf_h"], rel=tol, abs=1e-6)


def test_golden_rnd_and_diagnostics():
    """Verify exact reproduction of sim/golden/engine_rnd_and_diagnostics.json."""
    with open(GOLDEN_DIR / "engine_rnd_and_diagnostics.json", "r", encoding="utf-8") as f:
        golden = json.load(f)
    tol = golden["tolerance_rel"]

    sp_j57 = load_historical_engine("j57_p_21", build_deck=False)
    diag = compute_diagnostics(
        sp_j57,
        design_max_mach=1.4,
        design_ceiling_m=15000.0,
        inlet_spike=True,
        inlet_variable=True,
    )
    for k, v in golden["diagnostics_j57"].items():
        if isinstance(v, dict):
            for sk, sv in v.items():
                assert diag[k][sk] == pytest.approx(sv, rel=tol)
        elif isinstance(v, float):
            assert diag[k] == pytest.approx(v, rel=tol)
        else:
            assert diag[k] == v

    sale = compute_third_party_engine_sale(sp_j57, quantity=100, is_inhouse_engine=True)
    for k, v in golden["third_party_sale_j57_100"].items():
        assert sale[k] == pytest.approx(v, rel=tol)


def test_all_12_historical_engines_within_10_percent():
    """Every historical engine must calibrate within +/-10% across all published specs."""
    eids = list_historical_engines()
    assert len(eids) >= 10
    for eid in eids:
        raw = load_historical_engine_data(eid)
        inp = design_input_from_hist_dict(raw)
        sp = design_engine(inp, build_deck=False)
        href = raw["historical_reference"]

        assert sp.sls_dry_thrust_N == pytest.approx(href["sls_dry_thrust_N"], rel=0.10)
        assert sp.sls_dry_tsfc == pytest.approx(href["sls_dry_tsfc_kg_per_Ns"], rel=0.10)
        assert sp.mass_kg == pytest.approx(href["mass_kg"], rel=0.10)
        assert sp.diameter_m == pytest.approx(href["diameter_m"], rel=0.10)
        assert sp.length_m == pytest.approx(href["length_m"], rel=0.10)

        if href.get("sls_ab_thrust_N") is not None:
            assert sp.sls_ab_thrust_N == pytest.approx(href["sls_ab_thrust_N"], rel=0.10)
        if href.get("sls_ab_tsfc_kg_per_Ns") is not None:
            assert sp.sls_ab_tsfc == pytest.approx(href["sls_ab_tsfc_kg_per_Ns"], rel=0.10)


def test_throttle_linearity_and_ab_continuity():
    """Dry thrust scales linearly with throttle; AB throttle=0 equals dry throttle=1."""
    eng = load_historical_engine("j79_ge_11a", build_deck=True)
    for m, h in [(0.0, 0.0), (0.85, 6000.0), (1.6, 11000.0)]:
        f_mil = eng.thrust_N(m, h, 1.0, ab=False)
        f_ab_0 = eng.thrust_N(m, h, 0.0, ab=True)
        f_ab_1 = eng.thrust_N(m, h, 1.0, ab=True)
        assert f_ab_0 == pytest.approx(f_mil, rel=1e-9)
        assert eng.thrust_N(m, h, 0.5, ab=False) == pytest.approx(0.5 * f_mil, rel=1e-9)
        assert eng.thrust_N(m, h, 0.5, ab=True) == pytest.approx(
            0.5 * (f_mil + f_ab_1), rel=1e-9
        )
        # Zero throttle gives zero thrust and finite positive TSFC
        assert eng.thrust_N(m, h, 0.0, ab=False) == 0.0
        sfc_0 = eng.tsfc(m, h, 0.0, ab=False)
        assert math.isfinite(sfc_0) and sfc_0 > 0.0


def test_non_ab_engine_ignores_ab_flag():
    """Calling ab=True on a non-afterburning engine returns dry thrust and TSFC."""
    j47 = load_historical_engine("j47_ge_27", build_deck=True)
    assert not j47.has_afterburner
    assert j47.thrust_N(0.8, 5000.0, 1.0, ab=True) == pytest.approx(
        j47.thrust_N(0.8, 5000.0, 1.0, ab=False), rel=1e-9
    )
    assert j47.tsfc(0.8, 5000.0, 1.0, ab=True) == pytest.approx(
        j47.tsfc(0.8, 5000.0, 1.0, ab=False), rel=1e-9
    )


def test_altitude_lapse_and_cooled_bleed_and_turbofan():
    """Verify altitude lapse, cooling bleed penalty, and low-bypass turbofan TSFC improvement."""
    base = EngineDesignInput(
        engine_id="t_base",
        name="Base",
        compressor_type="axial",
        spools=2,
        mass_flow_kgps=60.0,
        opr=9.0,
        tit_K=1180.0,
    )
    sp_base = design_engine(base, build_deck=False)
    assert sp_base.thrust_N(0.8, 0.0) > sp_base.thrust_N(0.8, 9000.0) > sp_base.thrust_N(0.8, 16000.0)

    cooled = EngineDesignInput(
        engine_id="t_cool",
        name="Cooled",
        compressor_type="axial",
        spools=2,
        mass_flow_kgps=60.0,
        opr=9.0,
        tit_K=1180.0,
        cooled_turbine=True,
        bleed_fraction=0.04,
    )
    sp_cool = design_engine(cooled, build_deck=False)
    assert sp_cool.sls_dry_thrust_N < sp_base.sls_dry_thrust_N

    turbofan = EngineDesignInput(
        engine_id="t_tf",
        name="Turbofan",
        compressor_type="axial",
        spools=2,
        mass_flow_kgps=60.0,
        opr=9.0,
        tit_K=1180.0,
        bypass_ratio=0.6,
    )
    sp_tf = design_engine(turbofan, build_deck=False)
    assert sp_tf.sls_dry_tsfc < sp_base.sls_dry_tsfc


def test_tech_validation_and_rnd_reproducibility():
    """Verify TechContext cap validation and deterministic RNG outcome reproduction."""
    ctx = dict(DEFAULT_START_1945_ENGINE_TECH)
    over_target = EngineDesignInput(
        engine_id="over",
        name="Over",
        compressor_type="axial",
        spools=2,
        variable_stators=True,
        has_afterburner=True,
        mass_flow_kgps=80.0,
        opr=10.0,
        tit_K=1200.0,
        ab_temp_K=1950.0,
        cooled_turbine=True,
    )
    errs = validate_engine_against_tech(over_target, ctx)
    expected_caps = {
        "TECH_CAP:engine.twin_spool",
        "TECH_CAP:engine.variable_stators",
        "TECH_CAP:engine.afterburner",
        "TECH_CAP:engine.afterburner_temp_max_K",
        "TECH_CAP:engine.cooled_turbine_blades",
        "TECH_CAP:engine.tit_max_K",
        "TECH_CAP:engine.opr_max",
        "TECH_CAP:engine.mass_flow_max_kgps",
    }
    assert expected_caps.issubset(set(errs))

    valid_1945 = EngineDesignInput(
        engine_id="v45",
        name="Valid 1945",
        compressor_type="centrifugal",
        spools=1,
        mass_flow_kgps=38.0,
        opr=4.2,
        tit_K=1075.0,
        eta_c_poly=0.80,
        eta_t_poly=0.84,
    )
    assert validate_engine_against_tech(valid_1945, ctx) == []

    est = evaluate_rnd_project(valid_1945, ctx, procurement_mode="custom_commission")
    out1 = resolve_rnd_outcome(valid_1945, est, rng=np.random.default_rng(42), build_deck=False)
    out2 = resolve_rnd_outcome(valid_1945, est, rng=np.random.default_rng(42), build_deck=False)
    assert out1.thrust_multiplier == out2.thrust_multiplier
    assert out1.actual_duration_days == out2.actual_duration_days
    assert out1.engine_spec.sls_dry_thrust_N == out2.engine_spec.sls_dry_thrust_N
