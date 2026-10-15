"""North American F-86E Sabre — approximate geometry for validation.

Sources:
  - Loftin, "Quest for Performance", NASA SP-468 (1985), ch. 11:
      AR 4.78, 35 deg sweep, streamwise t/c 9.5 % root -> 8.5 % tip.
  - Commonly published F-86E dimensions:
      span 37.1 ft (11.31 m), wing area 287.9 ft^2 (26.75 m^2),
      length 37.5 ft (11.43 m), horizontal tail ~35 ft^2.

Fuselage and tail shapes are eyeballed from three-views; they only need to
be good enough for wetted area / fineness ratio in a conceptual buildup.
All lengths in metres. x aft, y right, z up.
"""
import numpy as np
import aerosandbox as asb

from aero.airfoils import naca00xx

# --- Reference wing (trapezoidal, extended to the centreline) -------------
SPAN = 11.31
S_REF = 26.75
TAPER = 0.51
SWEEP_C4_DEG = 35.0
DIHEDRAL_DEG = 3.0

C_ROOT = 2 * S_REF / (SPAN * (1 + TAPER))  # ~3.13 m
C_TIP = C_ROOT * TAPER                      # ~1.60 m


def _le_sweep_offset(semi_span: float) -> float:
    """x-offset of the tip LE relative to root LE for a given c/4 sweep."""
    tan_c4 = np.tan(np.radians(SWEEP_C4_DEG))
    return semi_span * tan_c4 + 0.25 * (C_ROOT - C_TIP)


def make_f86e() -> asb.Airplane:
    semi = SPAN / 2
    x_wing = 3.70   # root LE station
    z_wing = -0.25  # low-mid wing

    wing = asb.Wing(
        name="Main Wing",
        symmetric=True,
        xsecs=[
            asb.WingXSec(
                xyz_le=[x_wing, 0, z_wing],
                chord=C_ROOT,
                twist=1.0,  # incidence
                airfoil=naca00xx(0.095),
            ),
            asb.WingXSec(
                xyz_le=[
                    x_wing + _le_sweep_offset(semi),
                    semi,
                    z_wing + semi * np.tan(np.radians(DIHEDRAL_DEG)),
                ],
                chord=C_TIP,
                twist=-1.0,  # washout
                airfoil=naca00xx(0.085),
            ),
        ],
    )

    # Horizontal tail: ~3.25 m^2, span ~3.9 m, 35 deg sweep
    ht_span, ht_cr, ht_ct = 3.90, 1.12, 0.55
    x_ht, z_ht = 9.20, 0.35
    htail = asb.Wing(
        name="Horizontal Stabilizer",
        symmetric=True,
        xsecs=[
            asb.WingXSec(xyz_le=[x_ht, 0, z_ht], chord=ht_cr,
                         twist=-1.0, airfoil=naca00xx(0.08)),
            asb.WingXSec(
                xyz_le=[x_ht + ht_span / 2 * np.tan(np.radians(38)),
                        ht_span / 2, z_ht + 0.15],
                chord=ht_ct, twist=-1.0, airfoil=naca00xx(0.08)),
        ],
    )

    # Vertical tail: ~3.3 m^2, height ~1.9 m above fuselage
    vt_h, vt_cr, vt_ct = 1.90, 2.30, 1.10
    x_vt, z_vt = 8.30, 0.55
    vtail = asb.Wing(
        name="Vertical Stabilizer",
        symmetric=False,
        xsecs=[
            asb.WingXSec(xyz_le=[x_vt, 0, z_vt], chord=vt_cr,
                         airfoil=naca00xx(0.09)),
            asb.WingXSec(
                xyz_le=[x_vt + vt_h * np.tan(np.radians(45)), 0, z_vt + vt_h],
                chord=vt_ct, airfoil=naca00xx(0.09)),
        ],
    )

    # Fuselage: equivalent-radius distribution (station x, radius).
    # Nose inlet is modelled as a small rounded nose; internal duct flow
    # is not modelled.
    fuse_stations = [
        (0.00, 0.30),
        (0.40, 0.44),
        (1.20, 0.58),
        (2.40, 0.70),  # cockpit / canopy
        (3.80, 0.77),
        (5.50, 0.78),  # max section around the engine
        (7.50, 0.72),
        (9.20, 0.58),
        (10.60, 0.44),
        (11.43, 0.36),  # exhaust nozzle
    ]
    fuselage = asb.Fuselage(
        name="Fuselage",
        xsecs=[asb.FuselageXSec(xyz_c=[x, 0, 0], radius=r)
               for x, r in fuse_stations],
    )

    # Moment reference near 25 % MAC.
    mac_le_x = x_wing + _le_sweep_offset(semi) * (1 + 2 * TAPER) / (3 * (1 + TAPER))
    mac = (2 / 3) * C_ROOT * (1 + TAPER + TAPER ** 2) / (1 + TAPER)
    xyz_ref = [mac_le_x + 0.25 * mac, 0, 0]

    return asb.Airplane(
        name="F-86E Sabre",
        xyz_ref=xyz_ref,
        wings=[wing, htail, vtail],
        fuselages=[fuselage],
        s_ref=S_REF,
        c_ref=mac,
        b_ref=SPAN,
    )


# Reference data used by validate_f86.py --------------------------------------
# Loftin, NASA SP-468, ch. 11 (Table V itself is not machine-readable in the
# NTRS text; values below follow from the text):
#   * "the zero-lift drag coefficients were about the same for both aircraft"
#     (F-86E vs P-80A). P-80A drag area 3.2 ft^2 / wing area 238 ft^2
#     -> CD0 ~ 0.0134.
#   * "P-80 [L/D max 17.6] had the advantage by about 17 percent"
#     -> F-86E (L/D)max ~ 17.6 / 1.17 ~ 15.0.
#   Note: Loftin's (L/D)max is itself derived from CD0 assuming e ~ 0.8,
#   so it is a flight-derived estimate, not a direct measurement.
HISTORICAL = {
    "CD0": 0.0134,
    "LD_max": 15.0,
}
