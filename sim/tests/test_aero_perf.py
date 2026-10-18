"""Pytest suite and golden vector verification for Module 01 (`mic.atmosphere`, `mic.aero`, `mic.perf`)."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pytest

from mic.aero import (
    parse_and_analyze_airfoil as analyze_airfoil,
    compute_aero_diagnostics,
    compute_cd0_subsonic,
    compute_cl_alpha_mach,
    compute_high_lift_properties,
    compute_induced_drag_k,
    compute_mass_breakdown,
    compute_total_drag_cd,
    compute_wave_drag_summary,
    derive_aircraft_geometry,
    solve_wing_vlm,
    validate_design,
)
from mic.atmosphere import (
    density_kgm3,
    dynamic_pressure_Pa,
    isa_properties,
    pressure_Pa,
    recovery_temperature_K,
    speed_of_sound_mps,
    temperature_K,
)
from mic.perf import evaluate

REPO_ROOT = Path(__file__).resolve().parents[2]
HIST_DIR = REPO_ROOT / "sim" / "data" / "aircraft_hist"
GOLDEN_DIR = REPO_ROOT / "sim" / "golden"


def _ensure_golden_vectors() -> None:
    """Generate golden vectors if not yet present on disk."""
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    atm_af_file = GOLDEN_DIR / "aero_atmosphere_and_airfoil.json"
    perf_file = GOLDEN_DIR / "perf_historical_reports.json"

    if not atm_af_file.exists():
        alts = [0.0, 3048.0, 6096.0, 10668.0, 11000.0, 15000.0, 20000.0, 24000.0]
        atm_vectors = []
        for h in alts:
            props = isa_properties(h)
            atm_vectors.append(
                {
                    "alt_m": h,
                    "T_K": float(props.T_K),
                    "p_Pa": float(props.p_Pa),
                    "rho_kgm3": float(props.rho_kgm3),
                    "a_mps": float(props.a_mps),
                    "mu_Pas": float(props.mu_Pas),
                }
            )
        af_specs = ["0010", "2412", "23012", "64A007", "65-006", "biconvex_00336"]
        af_vectors = []
        for spec in af_specs:
            af = analyze_airfoil(spec)
            af_vectors.append(
                {
                    "spec": spec,
                    "tc_ratio": float(af.tc_ratio),
                    "x_tmax": float(af.x_tmax),
                    "max_camber": float(af.max_camber),
                    "cl_alpha_rad": float(af.cl_alpha_rad),
                    "cl_max_low_speed": float(af.cl_max_low_speed),
                    "korn_kappa_a": float(af.korn_kappa_a),
                    "m_dd_0": float(af.m_dd_0),
                }
            )
        atm_af_file.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "rel_tol": 1e-6,
                    "atmosphere": atm_vectors,
                    "airfoils": af_vectors,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    if not perf_file.exists():
        sample_ids = [
            "f86f_sabre",
            "yf102_pre_area_rule",
            "f102a_delta_dagger",
            "f104a_starfighter",
        ]
        reports = {}
        for sid in sample_ids:
            d = json.loads((HIST_DIR / f"{sid}.json").read_text(encoding="utf-8"))
            rep = evaluate(d)
            reports[sid] = rep.to_dict()
        perf_file.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "rel_tol": 1e-6,
                    "reports": reports,
                },
                indent=2,
            ),
            encoding="utf-8",
        )


_ensure_golden_vectors()


def test_isa_atmosphere_golden() -> None:
    data = json.loads((GOLDEN_DIR / "aero_atmosphere_and_airfoil.json").read_text(encoding="utf-8"))
    for row in data["atmosphere"]:
        p = isa_properties(row["alt_m"])
        assert math.isclose(p.T_K, row["T_K"], rel_tol=1e-6)
        assert math.isclose(p.p_Pa, row["p_Pa"], rel_tol=1e-6)
        assert math.isclose(p.rho_kgm3, row["rho_kgm3"], rel_tol=1e-6)
        assert math.isclose(p.a_mps, row["a_mps"], rel_tol=1e-6)
        assert math.isclose(p.mu_Pas, row["mu_Pas"], rel_tol=1e-6)

    # Check sea-level standard values explicitly
    p0 = isa_properties(0.0)
    assert math.isclose(p0.T_K, 288.15, rel_tol=1e-9)
    assert math.isclose(p0.p_Pa, 101325.0, rel_tol=1e-9)
    assert math.isclose(p0.rho_kgm3, 1.2250, rel_tol=1e-4)


def test_airfoil_golden_and_trends() -> None:
    data = json.loads((GOLDEN_DIR / "aero_atmosphere_and_airfoil.json").read_text(encoding="utf-8"))
    for row in data["airfoils"]:
        af = analyze_airfoil(row["spec"])
        assert math.isclose(af.tc_ratio, row["tc_ratio"], rel_tol=1e-6)
        assert math.isclose(af.cl_alpha_rad, row["cl_alpha_rad"], rel_tol=1e-6)
        assert math.isclose(af.cl_max_low_speed, row["cl_max_low_speed"], rel_tol=1e-6)
        assert math.isclose(af.m_dd_0, row["m_dd_0"], rel_tol=1e-6)

    # Thin NACA 64A007 must have higher Mdd than thick NACA 0012
    af_thin = analyze_airfoil("64A007")
    af_thick = analyze_airfoil("0012")
    assert af_thin.m_dd_0 > af_thick.m_dd_0 + 0.05
    assert af_thick.cl_max_low_speed > af_thin.cl_max_low_speed


def test_whitcomb_area_rule_yf102_vs_f102a() -> None:
    yf102 = json.loads((HIST_DIR / "yf102_pre_area_rule.json").read_text(encoding="utf-8"))
    f102a = json.loads((HIST_DIR / "f102a_delta_dagger.json").read_text(encoding="utf-8"))

    rep_yf = evaluate(yf102)
    rep_f102a = evaluate(f102a)

    # YF-102 pre-area-rule should have higher wave drag E_WD and be stuck near M ~ 1.0
    assert rep_yf.aero_diagnostics["wave_drag_ewd"] > rep_f102a.aero_diagnostics["wave_drag_ewd"] + 0.40
    assert rep_yf.max_mach_alt < 1.06
    assert rep_f102a.max_mach_alt > 1.20


def test_all_14_historical_aircraft_calibration_accuracy() -> None:
    files = sorted(HIST_DIR.glob("*.json"))
    assert len(files) >= 14
    abs_errors = []
    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        rep = evaluate(d)
        assert rep.is_valid, f"{d['id']} failed validation: {rep.validation_errors}"
        pub = d["published_performance"]
        for key in [
            "max_mach_alt",
            "max_mach_sl",
            "service_ceiling_m",
            "climb_rate_sl_mps",
            "empty_mass_kg",
            "combat_radius_m",
            "stall_speed_mps",
        ]:
            err = abs(rep[key] - pub[key]) / pub[key] * 100.0
            abs_errors.append(err)
    mean_mape = float(np.mean(abs_errors))
    assert mean_mape <= 8.0, f"Overall MAPE {mean_mape:.2f}% exceeded 8.0% threshold"


def test_golden_historical_reports() -> None:
    data = json.loads((GOLDEN_DIR / "perf_historical_reports.json").read_text(encoding="utf-8"))
    rel_tol = float(data["rel_tol"])
    for sid, expected in data["reports"].items():
        d = json.loads((HIST_DIR / f"{sid}.json").read_text(encoding="utf-8"))
        actual = evaluate(d).to_dict()
        for k, exp_v in expected.items():
            if isinstance(exp_v, (int, float)) and not isinstance(exp_v, bool):
                assert math.isclose(actual[k], exp_v, rel_tol=rel_tol, abs_tol=1e-9), f"{sid}.{k} mismatch"


def test_module_06_diagnostics_contract() -> None:
    f100 = json.loads((HIST_DIR / "f100a_super_sabre.json").read_text(encoding="utf-8"))
    rep = evaluate(f100)
    diag = rep.aero_diagnostics
    required_keys = [
        "shortal_maggin_excess",
        "m_dd",
        "mach_dd_excess",
        "wave_drag_ewd",
        "wave_drag_ratio",
        "cd_wave_peak",
        "ac_shift_mac",
        "inertia_coupling_index",
        "torsion_flex_index",
    ]
    for rk in required_keys:
        assert rk in diag, f"Missing diagnostic key {rk}"
        assert not math.isnan(diag[rk]) and not math.isinf(diag[rk])
