"""Validate the tier-1 aero model against historical F-86E data.

Run from the repo root:
    .venv/bin/python -m aero.scripts.validate_f86
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from aero.aircraft.f86 import make_f86e, HISTORICAL
from aero.analysis import buildup, polar_summary, vlm_cl_alpha

OUT = Path(__file__).resolve().parents[2] / "output"
FT = 0.3048


def main():
    OUT.mkdir(exist_ok=True)
    ac = make_f86e()
    AR = ac.b_ref ** 2 / ac.s_ref
    print(f"{ac.name}: S={ac.s_ref:.2f} m^2  b={ac.b_ref:.2f} m  AR={AR:.2f}  "
          f"MAC={ac.c_ref:.2f} m  S_wet={sum(w.area('wetted') for w in ac.wings) + sum(f.area_wetted() for f in ac.fuselages):.1f} m^2")

    # ---- 1. Polar summaries at representative conditions -----------------
    cases = [(0.0, 0.5, "sea level, M0.5"),
             (25000 * FT, 0.7, "25k ft, M0.7"),
             (35000 * FT, 0.6, "35k ft, M0.6"),
             (35000 * FT, 0.8, "35k ft, M0.8")]
    print("\n--- Tier 1 (AeroBuildup) polar summaries ---")
    print(f"{'condition':18s} {'Re_MAC':>8s} {'CD0':>7s} {'e':>5s} "
          f"{'CLa/deg':>8s} {'L/Dmax':>7s} {'@CL':>5s} {'@alpha':>6s}")
    summaries = []
    for h, M, label in cases:
        s = polar_summary(ac, h, M)
        summaries.append((label, s))
        print(f"{label:18s} {s.reynolds_mac / 1e6:7.1f}M {s.CD0:7.4f} {s.oswald_e:5.2f} "
              f"{s.CL_alpha_per_deg:8.4f} {s.LD_max:7.2f} {s.CL_at_LD_max:5.2f} "
              f"{s.alpha_at_LD_max:6.1f}")

    # ---- 2. Compare against history --------------------------------------
    ref = dict(summaries)["35k ft, M0.6"]
    print("\n--- vs. historical (Loftin, NASA SP-468) ---")
    for key, model in (("CD0", ref.CD0), ("LD_max", ref.LD_max)):
        hist = HISTORICAL[key]
        print(f"{key:7s} model={model:.4f}  historical={hist:.4f}  "
              f"error={100 * (model - hist) / hist:+.1f}%")

    # ---- 3. Tier 2 cross-check: lift-curve slope at low Mach -------------
    low = polar_summary(ac, 0.0, 0.2)
    cla_vlm = vlm_cl_alpha(ac, 0.0, 0.2)
    print(f"\nCL_alpha @M0.2  tier1={low.CL_alpha_per_deg:.4f}/deg  "
          f"tier2 VLM={cla_vlm:.4f}/deg  "
          f"diff={100 * (low.CL_alpha_per_deg - cla_vlm) / cla_vlm:+.1f}%")

    # ---- 4. Plots --------------------------------------------------------
    alphas = np.linspace(-4, 14, 37)
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.5))
    for h, M, label in cases:
        r = buildup(ac, h, M, alphas)
        CL, CD = np.asarray(r["CL"]), np.asarray(r["CD"])
        axs[0].plot(alphas, CL, label=label)
        axs[1].plot(CD, CL, label=label)
        axs[2].plot(alphas, CL / CD, label=label)
    axs[2].axhline(HISTORICAL["LD_max"], color="k", ls="--", lw=1,
                   label="historical (L/D)max")
    axs[0].set(xlabel="alpha [deg]", ylabel="CL", title="Lift curve")
    axs[1].set(xlabel="CD", ylabel="CL", title="Drag polar")
    axs[2].set(xlabel="alpha [deg]", ylabel="L/D", title="Lift-to-drag")
    for a in axs:
        a.grid(alpha=0.3)
        a.legend(fontsize=8)
    fig.suptitle("F-86E — tier 1 AeroBuildup")
    fig.tight_layout()
    fig.savefig(OUT / "f86_polars.png", dpi=120)

    # Drag rise at constant CL (approx. cruise lift at 35k ft)
    machs = np.linspace(0.4, 1.05, 27)
    cd_at_cl = []
    for M in machs:
        r = buildup(ac, 35000 * FT, M, alphas)
        CL, CD = np.asarray(r["CL"]), np.asarray(r["CD"])
        cd_at_cl.append(np.interp(0.2, CL, CD))
    cd_at_cl = np.array(cd_at_cl)
    dcd = np.gradient(cd_at_cl, machs)
    i_dd = np.argmax(dcd > 0.1) if np.any(dcd > 0.1) else -1
    m_dd = machs[i_dd] if i_dd >= 0 else float("nan")
    print(f"Drag-divergence Mach (dCD/dM = 0.1, CL=0.2): {m_dd:.2f}")

    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.plot(machs, cd_at_cl, "o-", ms=3)
    ax.axvline(m_dd, color="r", ls="--", lw=1, label=f"M_dd ~ {m_dd:.2f}")
    ax.set(xlabel="Mach", ylabel="CD @ CL=0.2", title="F-86E drag rise, 35k ft")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "f86_drag_rise.png", dpi=120)

    ac.draw_three_view(show=False)
    plt.savefig(OUT / "f86_three_view.png", dpi=120)
    print(f"\nPlots written to {OUT}")


if __name__ == "__main__":
    main()
