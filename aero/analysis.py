"""Aerodynamic analysis wrappers around AeroSandbox.

Everything here is "tier 1" (AeroBuildup: semi-empirical component buildup
with NeuralFoil section data) unless stated otherwise. Altitude and speed
enter only through Reynolds number, Mach number and dynamic pressure.
"""
from dataclasses import dataclass

import numpy as np
import aerosandbox as asb


def op_point(altitude_m: float, mach: float, alpha_deg) -> asb.OperatingPoint:
    atmo = asb.Atmosphere(altitude=altitude_m)
    return asb.OperatingPoint(
        atmosphere=atmo,
        velocity=mach * atmo.speed_of_sound(),
        alpha=alpha_deg,
    )


def buildup(airplane: asb.Airplane, altitude_m: float, mach: float, alpha_deg):
    """Tier-1 aero: returns dict with CL, CD, Cm (alpha may be an array)."""
    return asb.AeroBuildup(
        airplane=airplane,
        op_point=op_point(altitude_m, mach, alpha_deg),
    ).run()


def vlm_cl_alpha(airplane: asb.Airplane, altitude_m: float, mach: float) -> float:
    """Tier-2 check: inviscid vortex-lattice lift-curve slope [1/deg].

    Plain VLM is incompressible; Prandtl-Glauert is applied to the slope.
    Note: applying 1/beta to a whole swept configuration over-corrects at
    higher Mach (the DATCOM/Goethert form is milder), so compare at low Mach.
    The fuselage is not modelled by VLM.
    """
    cls = []
    for a in (0.0, 2.0):
        vlm = asb.VortexLatticeMethod(
            airplane=airplane,
            op_point=asb.OperatingPoint(velocity=100, alpha=a),
            spanwise_resolution=12,
            chordwise_resolution=6,
        )
        cls.append(vlm.run()["CL"])
    beta = np.sqrt(1 - mach ** 2)
    return float((cls[1] - cls[0]) / 2.0 / beta)


@dataclass
class PolarSummary:
    altitude_m: float
    mach: float
    reynolds_mac: float
    CD0: float          # CD at CL = 0
    K: float            # CD = CD0 + K * (CL - CL_minD)^2 fit
    oswald_e: float
    CL_alpha_per_deg: float
    LD_max: float
    CL_at_LD_max: float
    alpha_at_LD_max: float


def polar_summary(airplane: asb.Airplane, altitude_m: float, mach: float,
                  alphas=np.linspace(-4, 12, 33)) -> PolarSummary:
    r = buildup(airplane, altitude_m, mach, alphas)
    CL, CD = np.asarray(r["CL"]), np.asarray(r["CD"])

    CD0 = float(np.interp(0.0, CL, CD))
    # Classic parabolic polar CD = CD0 + K CL^2, fitted over attached flow
    mask = (CL > 0.05) & (CL < 0.5)
    K = float(np.polyfit(CL[mask] ** 2, CD[mask], 1)[0])
    AR = airplane.b_ref ** 2 / airplane.s_ref
    e = 1 / (np.pi * AR * K)

    lin = (alphas >= -2) & (alphas <= 4)
    cla = float(np.polyfit(alphas[lin], CL[lin], 1)[0])

    LD = CL / CD
    i = int(np.argmax(LD))
    op = op_point(altitude_m, mach, 0.0)
    return PolarSummary(
        altitude_m=altitude_m,
        mach=mach,
        reynolds_mac=float(op.reynolds(airplane.c_ref)),
        CD0=CD0,
        K=float(K),
        oswald_e=float(e),
        CL_alpha_per_deg=cla,
        LD_max=float(LD[i]),
        CL_at_LD_max=float(CL[i]),
        alpha_at_LD_max=float(alphas[i]),
    )
