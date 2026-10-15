"""Generate an aero lookup table CL/CD/Cm/(L/D) over (altitude, Mach, alpha).

This is the "precompute offline, interpolate at runtime" path: the game
engine only needs to read the CSV and do trilinear interpolation, which is
also the shape of data JSBSim / DCS SFM expect.

Run from the repo root:
    .venv/bin/python -m aero.scripts.make_table
"""
import csv
import time
from pathlib import Path

import numpy as np

from aero.aircraft.f86 import make_f86e
from aero.analysis import buildup

OUT = Path(__file__).resolve().parents[2] / "output"

ALTITUDES_M = [0, 3000, 6000, 9000, 12000, 15000]
MACHS = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
ALPHAS_DEG = np.arange(-4, 18.1, 1.0)


def main():
    OUT.mkdir(exist_ok=True)
    ac = make_f86e()
    path = OUT / "f86_aero_table.csv"
    t0 = time.time()
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["altitude_m", "mach", "alpha_deg", "CL", "CD", "Cm", "L_over_D"])
        for h in ALTITUDES_M:
            for M in MACHS:
                r = buildup(ac, h, M, ALPHAS_DEG)  # vectorised over alpha
                CL, CD, Cm = (np.asarray(r[k]) for k in ("CL", "CD", "Cm"))
                for a, cl, cd, cm in zip(ALPHAS_DEG, CL, CD, Cm):
                    w.writerow([h, M, a, f"{cl:.5f}", f"{cd:.5f}",
                                f"{cm:.5f}", f"{cl / cd:.3f}"])
    n = len(ALTITUDES_M) * len(MACHS) * len(ALPHAS_DEG)
    print(f"{n} points in {time.time() - t0:.1f} s -> {path}")


if __name__ == "__main__":
    main()
