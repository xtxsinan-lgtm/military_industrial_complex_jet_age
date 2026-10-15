"""Airfoil helpers.

AeroSandbox's built-in NACA generator only accepts integer thickness
percentages (e.g. "naca0010"). Historical jet-age wings use fractional
thicknesses (the F-86 goes from 9.5% at the root to 8.5% at the tip,
streamwise), so we generate symmetric NACA 4-digit sections ourselves.
"""
import numpy as np
import aerosandbox as asb


def naca00xx(thickness: float, n_points_per_side: int = 100) -> asb.Airfoil:
    """Symmetric NACA 4-digit airfoil with arbitrary thickness ratio.

    Args:
        thickness: thickness-to-chord ratio, e.g. 0.095 for 9.5 %.
        n_points_per_side: number of points on each surface (cosine-spaced).
    """
    beta = np.linspace(0, np.pi, n_points_per_side)
    x = 0.5 * (1 - np.cos(beta))  # cosine spacing, clusters at LE and TE
    # Closed-trailing-edge variant of the NACA thickness distribution.
    yt = 5 * thickness * (
        0.2969 * np.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x ** 2
        + 0.2843 * x ** 3
        - 0.1036 * x ** 4
    )
    # Selig format: upper surface TE -> LE, then lower surface LE -> TE.
    upper = np.stack([x[::-1], yt[::-1]], axis=1)
    lower = np.stack([x[1:], -yt[1:]], axis=1)
    coords = np.concatenate([upper, lower], axis=0)
    return asb.Airfoil(name=f"NACA00{thickness * 100:.1f}", coordinates=coords)
