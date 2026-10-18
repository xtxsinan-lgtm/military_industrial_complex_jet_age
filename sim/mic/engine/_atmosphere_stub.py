"""ISA 1976 atmosphere helper for mic.engine.

Clearly-labelled internal fallback stub per 00_conventions.md §5.1.
Delegates to `mic.atmosphere` if available; otherwise uses the exact ISA 1976
piecewise hydrostatic atmosphere up to 25,000 m.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

G0 = 9.80665
R_AIR = 287.05287
GAMMA_AIR = 1.4
T0_STD = 288.15
P0_STD = 101325.0
RHO0_STD = P0_STD / (R_AIR * T0_STD)


@dataclass(frozen=True)
class AtmosphereState:
    alt_m: float
    T_K: float
    P_Pa: float
    rho_kgm3: float
    a_mps: float


def _isa_1976_internal(alt_m: float) -> Tuple[float, float, float, float]:
    """Compute (T_K, P_Pa, rho_kgm3, a_mps) at geometric/geopotential altitude alt_m."""
    h = max(-1000.0, min(30000.0, float(alt_m)))
    # Troposphere: 0 to 11,000 m (lapse -0.0065 K/m)
    L0 = -0.0065
    if h <= 11000.0:
        T = T0_STD + L0 * h
        P = P0_STD * (T / T0_STD) ** (-G0 / (L0 * R_AIR))
    else:
        T11 = T0_STD + L0 * 11000.0  # 216.65 K
        P11 = P0_STD * (T11 / T0_STD) ** (-G0 / (L0 * R_AIR))
        if h <= 20000.0:
            # Lower stratosphere: isothermal 216.65 K
            T = T11
            P = P11 * math.exp(-G0 * (h - 11000.0) / (R_AIR * T11))
        else:
            # Mid stratosphere: 20,000 to 32,000 m (lapse +0.001 K/m)
            P20 = P11 * math.exp(-G0 * (20000.0 - 11000.0) / (R_AIR * T11))
            L2 = 0.001
            T = T11 + L2 * (h - 20000.0)
            P = P20 * (T / T11) ** (-G0 / (L2 * R_AIR))
    rho = P / (R_AIR * T)
    a = math.sqrt(GAMMA_AIR * R_AIR * T)
    return T, P, rho, a


def get_atmosphere(alt_m: float) -> AtmosphereState:
    """Return ISA 1976 state, delegating to mic.atmosphere if present."""
    try:
        import mic.atmosphere as _atm  # type: ignore

        if hasattr(_atm, "isa"):
            st = _atm.isa(alt_m)
            if hasattr(st, "T_K") and hasattr(st, "P_Pa"):
                return AtmosphereState(
                    alt_m=float(alt_m),
                    T_K=float(st.T_K),
                    P_Pa=float(st.P_Pa),
                    rho_kgm3=float(getattr(st, "rho_kgm3", st.P_Pa / (R_AIR * st.T_K))),
                    a_mps=float(getattr(st, "a_mps", math.sqrt(GAMMA_AIR * R_AIR * st.T_K))),
                )
    except Exception:
        pass
    T, P, rho, a = _isa_1976_internal(alt_m)
    return AtmosphereState(alt_m=float(alt_m), T_K=T, P_Pa=P, rho_kgm3=rho, a_mps=a)
