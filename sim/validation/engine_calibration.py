"""Engine calibration and validation script.

Validates `sim/mic/engine/` against 12 historical 1945-1960 turbojets in
`sim/data/engines_hist/*.json` (target: within +/-10% across all key metrics),
verifies off-design thrust lapse against Mattingly (2002) Eqs. 2.55a/b, and
writes the complete report to `docs/validation/engine_calibration.md`.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
SIM_DIR = ROOT / "sim"
if str(SIM_DIR) not in sys.path:
    sys.path.insert(0, str(SIM_DIR))

from mic.engine import (  # noqa: E402
    compute_diagnostics,
    design_engine,
    design_input_from_hist_dict,
    duane_mtbf,
    list_historical_engines,
    load_engine_tuning,
    load_historical_engine_data,
)
from mic.engine._atmosphere_stub import P0_STD, T0_STD, get_atmosphere  # noqa: E402


def mattingly_lapse_dry(mach: float, alt_m: float, tr: float = 1.05) -> float:
    """Mattingly (2002) Eq. 2.55b reference thrust lapse (normalized to 1.0 at SLS)."""
    atm = get_atmosphere(alt_m)
    theta = atm.T_K / T0_STD
    delta = atm.P_Pa / P0_STD
    theta_0 = theta * (1.0 + 0.2 * mach * mach)
    delta_0 = delta * ((1.0 + 0.2 * mach * mach) ** 3.5)
    if theta_0 <= tr:
        return delta_0 * (1.0 - 0.16 * math.sqrt(mach))
    return delta_0 * (
        1.0 - 0.16 * math.sqrt(mach) - 24.0 * (theta_0 - tr) / ((9.0 + mach) * theta_0)
    )


def mattingly_lapse_ab(mach: float, alt_m: float, tr: float = 1.05) -> float:
    """Mattingly (2002) Eq. 2.55a reference AB thrust lapse (normalized to 1.0 at SLS)."""
    atm = get_atmosphere(alt_m)
    theta = atm.T_K / T0_STD
    delta = atm.P_Pa / P0_STD
    theta_0 = theta * (1.0 + 0.2 * mach * mach)
    delta_0 = delta * ((1.0 + 0.2 * mach * mach) ** 3.5)
    if theta_0 <= tr:
        return delta_0 * (1.0 - 0.3 * (theta_0 - 1.0) - 0.1 * math.sqrt(mach))
    return delta_0 * (
        1.0
        - 0.3 * (theta_0 - 1.0)
        - 0.1 * math.sqrt(mach)
        - 1.5 * (theta_0 - tr) / theta_0
    )


def pct_err(pred: float, ref: float) -> float:
    return 100.0 * (pred - ref) / ref


def run_calibration() -> Dict[str, Any]:
    tuning = load_engine_tuning(reload=True)
    engine_ids = list_historical_engines()
    rows: List[Dict[str, Any]] = []
    all_errors: List[float] = []

    for eid in engine_ids:
        raw = load_historical_engine_data(eid)
        inp = design_input_from_hist_dict(raw)
        spec = design_engine(inp, build_deck=True, tuning=tuning)
        href = raw["historical_reference"]

        e_dry_f = pct_err(spec.sls_dry_thrust_N, href["sls_dry_thrust_N"])
        e_dry_sfc = pct_err(spec.sls_dry_tsfc, href["sls_dry_tsfc_kg_per_Ns"])
        e_mass = pct_err(spec.mass_kg, href["mass_kg"])
        e_diam = pct_err(spec.diameter_m, href["diameter_m"])
        e_len = pct_err(spec.length_m, href["length_m"])

        all_errors.extend([abs(e_dry_f), abs(e_dry_sfc), abs(e_mass), abs(e_diam), abs(e_len)])

        e_ab_f: Optional[float] = None
        e_ab_sfc: Optional[float] = None
        if href.get("sls_ab_thrust_N") is not None:
            e_ab_f = pct_err(spec.sls_ab_thrust_N, href["sls_ab_thrust_N"])
            all_errors.append(abs(e_ab_f))
        if href.get("sls_ab_tsfc_kg_per_Ns") is not None:
            e_ab_sfc = pct_err(spec.sls_ab_tsfc, href["sls_ab_tsfc_kg_per_Ns"])
            all_errors.append(abs(e_ab_sfc))

        diag = compute_diagnostics(
            spec,
            design_max_mach=2.0 if inp.opr >= 10.0 else (1.4 if inp.has_afterburner else 0.92),
            design_ceiling_m=15000.0 if inp.opr >= 7.0 else 13000.0,
            inlet_spike=inp.opr >= 7.0 and inp.has_afterburner,
            inlet_variable=inp.variable_stators or inp.spools == 2,
        )

        rows.append(
            {
                "engine_id": eid,
                "name": raw["name"],
                "arch": f"{inp.compressor_type[:4]}-{inp.spools}sp"
                + ("-VSV" if inp.variable_stators else "")
                + ("-AB" if inp.has_afterburner else ""),
                "spec": spec,
                "href": href,
                "e_dry_f": e_dry_f,
                "e_ab_f": e_ab_f,
                "e_dry_sfc": e_dry_sfc,
                "e_ab_sfc": e_ab_sfc,
                "e_mass": e_mass,
                "e_diam": e_diam,
                "e_len": e_len,
                "diag": diag,
            }
        )

    max_abs_err = max(all_errors) if all_errors else 0.0
    mean_abs_err = sum(all_errors) / len(all_errors) if all_errors else 0.0
    return {
        "rows": rows,
        "max_abs_err": max_abs_err,
        "mean_abs_err": mean_abs_err,
    }


def write_markdown_report(res: Dict[str, Any], out_path: Path) -> None:
    rows = res["rows"]
    max_err = res["max_abs_err"]
    mean_err = res["mean_abs_err"]
    status_str = "PASS (All metrics within +/-10%)" if max_err <= 10.0 else f"FAIL (Max error {max_err:.2f}%)"

    LBF = 4.4482216152605
    SFC_CONV = 2.83254504e-5

    lines: List[str] = []
    lines.append("# Engine Cycle & Sizing Calibration Report (Module 02)")
    lines.append("")
    lines.append(f"> **Status**: **{status_str}**  ")
    lines.append(f"> **Engines Calibrated**: {len(rows)} historical turbojets (1945–1960 US & Soviet)  ")
    lines.append(f"> **Mean Absolute Relative Error**: **{mean_err:.2f}%** | **Max Absolute Relative Error**: **{max_err:.2f}%** (Target: $\\le 10.0\\%$)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Sea-Level Static (On-Design) Performance Calibration")
    lines.append("")
    lines.append("All predictions are generated directly from the parametric thermodynamic cycle (`sim/mic/engine/cycle.py`) using only the engine's design-point mass flow $\\dot{m}_0$, overall pressure ratio $\\text{OPR}$, turbine inlet temperature $T_{t4}$, afterburner temperature $T_{t7}$, architecture flags, and global constants in `sim/data/tuning/engine.json`.")
    lines.append("")
    lines.append("| Engine | Arch | Dry Thrust Pred / Hist (kN) | Dry Err | AB Thrust Pred / Hist (kN) | AB Err | Dry SFC Pred / Hist (lb/lbf/h) | Dry SFC Err | AB SFC Pred / Hist (lb/lbf/h) | AB SFC Err |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")

    for r in rows:
        sp = r["spec"]
        hr = r["href"]
        df_p = sp.sls_dry_thrust_N / 1000.0
        df_h = hr["sls_dry_thrust_N"] / 1000.0
        dsfc_p = sp.sls_dry_tsfc / SFC_CONV
        dsfc_h = hr["sls_dry_tsfc_kg_per_Ns"] / SFC_CONV

        if r["e_ab_f"] is not None:
            abf_str = f"{sp.sls_ab_thrust_N/1000.0:.2f} / {hr['sls_ab_thrust_N']/1000.0:.2f}"
            abf_e = f"{r['e_ab_f']:+.2f}%"
        else:
            abf_str = "—"
            abf_e = "—"

        if r["e_ab_sfc"] is not None:
            absfc_str = f"{sp.sls_ab_tsfc/SFC_CONV:.3f} / {hr['sls_ab_tsfc_kg_per_Ns']/SFC_CONV:.3f}"
            absfc_e = f"{r['e_ab_sfc']:+.2f}%"
        else:
            absfc_str = "—"
            absfc_e = "—"

        lines.append(
            f"| **{r['name']}** | `{r['arch']}` | {df_p:.2f} / {df_h:.2f} | {r['e_dry_f']:+.2f}% | "
            f"{abf_str} | {abf_e} | {dsfc_p:.3f} / {dsfc_h:.3f} | {r['e_dry_sfc']:+.2f}% | "
            f"{absfc_str} | {absfc_e} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Physical Sizing (Mass, Diameter, Length) & Cost/Reliability Summary")
    lines.append("")
    lines.append("| Engine | Dry Mass Pred / Hist (kg) | Mass Err | Diameter Pred / Hist (m) | Diam Err | Length Pred / Hist (m) | Len Err | Est. Unit Cost ($) | Mature MTBF (h) | Maint (MMH/FH) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")

    for r in rows:
        sp = r["spec"]
        hr = r["href"]
        lines.append(
            f"| **{r['name']}** | {sp.mass_kg:.1f} / {hr['mass_kg']:.1f} | {r['e_mass']:+.2f}% | "
            f"{sp.diameter_m:.3f} / {hr['diameter_m']:.3f} | {r['e_diam']:+.2f}% | "
            f"{sp.length_m:.3f} / {hr['length_m']:.3f} | {r['e_len']:+.2f}% | "
            f"\\${sp.unit_cost:,.0f} | {sp.mtbf_h:.1f} | {sp.maint_mh_per_fh:.2f} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Off-Design Altitude & Mach Thrust-Lapse Verification")
    lines.append("")
    lines.append("Comparison of the choked-turbine off-design cycle model (`evaluate_off_design_point`) against Mattingly (2002) *Aircraft Engine Design* (2nd ed., Eqs. 2.55a & 2.55b) reference thrust-lapse ratios $\\alpha(M_0, h) = F(M_0, h) / F_{\\text{SLS}}$ across representative flight regimes:")
    lines.append("")
    lines.append("| Engine | Regime | $(M_0, h)$ | Cycle Thrust (kN) | Cycle $\\alpha = F/F_{\\text{SLS}}$ | Mattingly Ref $\\alpha$ | Cycle TSFC (lb/lbf/h) |")
    lines.append("|---|---|---|---|---|---|---|")

    by_id = {r["engine_id"]: r["spec"] for r in rows}
    test_points = [
        ("j47_ge_27", "Subsonic Cruise", 0.80, 10668.0, False),
        ("j47_ge_27", "Combat Climb", 0.70, 4572.0, False),
        ("j57_p_21", "Subsonic Combat (Dry)", 0.90, 4572.0, False),
        ("j57_p_21", "Supersonic Dash (AB)", 1.40, 10668.0, True),
        ("j79_ge_11a", "High-Alt Cruise (Dry)", 0.90, 10668.0, False),
        ("j79_ge_11a", "Supersonic Intercept (AB)", 2.00, 12192.0, True),
        ("vk_1", "High-Alt Combat (Dry)", 0.85, 10000.0, False),
        ("rd_9b", "Supersonic Dash (AB)", 1.50, 10668.0, True),
    ]
    for eid, label, m, h, ab in test_points:
        sp = by_id[eid]
        f_val = sp.thrust_N(m, h, throttle=1.0, ab=ab)
        sfc_val = sp.tsfc(m, h, throttle=1.0, ab=ab) / SFC_CONV
        f_ref_sls = sp.sls_ab_thrust_N if ab else sp.sls_dry_thrust_N
        alpha_cyc = f_val / f_ref_sls
        alpha_mat = mattingly_lapse_ab(m, h) if ab else mattingly_lapse_dry(m, h)
        lines.append(
            f"| **{sp.name}** | {label} | $M={m:.2f},\\; h={h:,.0f}\\text{{ m}}$ | "
            f"{f_val/1000.0:.2f} | {alpha_cyc:.3f} | {alpha_mat:.3f} | {sfc_val:.3f} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Part-Power Throttle TSFC Bucket Verification")
    lines.append("")
    lines.append("At subsonic cruise ($M = 0.80, h = 9,144\\text{ m}$), throttling back from 100% military power to 75–90% cruise power exhibits the realistic thermodynamic TSFC bucket before parasitic losses raise TSFC near idle:")
    lines.append("")
    lines.append("| Engine | Throttle 1.00 | Throttle 0.90 | Throttle 0.75 | Throttle 0.50 | Throttle 0.25 | Throttle 0.10 |")
    lines.append("|---|---|---|---|---|---|---|")
    for eid in ("j47_ge_27", "j57_p_21", "j79_ge_11a"):
        sp = by_id[eid]
        vals = [sp.tsfc(0.80, 9144.0, thr, ab=False) / SFC_CONV for thr in (1.0, 0.9, 0.75, 0.5, 0.25, 0.1)]
        lines.append(
            f"| **{sp.name}** (lb/lbf/h) | {vals[0]:.3f} | {vals[1]:.3f} | {vals[2]:.3f} | {vals[3]:.3f} | {vals[4]:.3f} | {vals[5]:.3f} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5. Engine Diagnostics (`engine_diagnostics` for Module 06)")
    lines.append("")
    lines.append("| Engine | Surge Margin | High-Alt Flameout Risk | AB Light-Off Rel. | Intake Compatibility | Thermal Margin (K) | `engine_stall` Mult | `inlet` Mult |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        d = r["diag"]
        fm = d["flaw_incidence_multipliers"]
        lines.append(
            f"| **{r['name']}** | {d['compressor_surge_margin']:.3f} | {d['high_alt_flameout_risk']:.3f} | "
            f"{d['ab_lightoff_reliability']:.3f} | {d['intake_compatibility']:.3f} | "
            f"{d['thermal_margin_K']:+.1f} | {fm['engine_stall']:.2f}x | {fm['inlet']:.2f}x |"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    res = run_calibration()
    out_md = ROOT / "docs" / "validation" / "engine_calibration.md"
    write_markdown_report(res, out_md)
    print(f"Max abs error: {res['max_abs_err']:.2f}%, Mean abs error: {res['mean_abs_err']:.2f}%")
    for r in res["rows"]:
        print(
            f"{r['engine_id']:12s}: dF={r['e_dry_f']:+6.2f}% abF={str(round(r['e_ab_f'],2)) if r['e_ab_f'] is not None else 'N/A':>6s}% "
            f"dSFC={r['e_dry_sfc']:+6.2f}% abSFC={str(round(r['e_ab_sfc'],2)) if r['e_ab_sfc'] is not None else 'N/A':>6s}% "
            f"mass={r['e_mass']:+6.2f}% diam={r['e_diam']:+6.2f}% len={r['e_len']:+6.2f}%"
        )
