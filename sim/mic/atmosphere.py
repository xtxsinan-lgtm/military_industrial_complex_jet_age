"""ISA 1976 Standard Atmosphere model (0 to 32 km) for Module 01.

All units are strictly SI:
- Altitude h: m (geopotential approximation matching standard preliminary design practice)
- Temperature T: K
- Pressure p: Pa
- Density rho: kg/m^3
- Speed of sound a: m/s
- Dynamic viscosity mu: Pa*s (kg/(m*s))
- Kinematic viscosity nu: m^2/s

Supports both scalar float and numpy.ndarray inputs seamlessly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union
import numpy as np

NumberOrArray = Union[float, np.ndarray]

# Exact ISA 1976 physical constants
G0_MPS2: float = 9.80665
R_AIR_J_KGK: float = 287.05287
GAMMA_AIR: float = 1.4

T0_SL_K: float = 288.15
P0_SL_PA: float = 101325.0
RHO0_SL_KGM3: float = P0_SL_PA / (R_AIR_J_KGK * T0_SL_K)  # 1.225000018124288
A0_SL_MPS: float = float(np.sqrt(GAMMA_AIR * R_AIR_J_KGK * T0_SL_K))  # 340.29399...

# Layer boundaries and lapse rates
H1_TROPOPAUSE_M: float = 11000.0
H2_STRATO_M: float = 20000.0
H3_MAX_M: float = 32000.0

LAPSE_TROPO_K_PER_M: float = -0.0065
LAPSE_STRATO2_K_PER_M: float = 0.0010

T1_TROPOPAUSE_K: float = T0_SL_K + LAPSE_TROPO_K_PER_M * H1_TROPOPAUSE_M  # 216.65 K
P1_TROPOPAUSE_PA: float = P0_SL_PA * (T1_TROPOPAUSE_K / T0_SL_K) ** (-G0_MPS2 / (R_AIR_J_KGK * LAPSE_TROPO_K_PER_M))
P2_STRATO_PA: float = P1_TROPOPAUSE_PA * float(
    np.exp(-G0_MPS2 * (H2_STRATO_M - H1_TROPOPAUSE_M) / (R_AIR_J_KGK * T1_TROPOPAUSE_K))
)

# Sutherland's law constants for air
SUTHERLAND_MU_REF_PAS: float = 1.716e-5
SUTHERLAND_T_REF_K: float = 273.15
SUTHERLAND_S_K: float = 110.4


@dataclass(frozen=True)
class AtmosphereState:
    """Atmospheric properties at a single altitude or array of altitudes."""

    alt_m: NumberOrArray
    T_K: NumberOrArray
    p_Pa: NumberOrArray
    rho_kgm3: NumberOrArray
    a_mps: NumberOrArray
    mu_Pas: NumberOrArray
    nu_m2ps: NumberOrArray
    theta: NumberOrArray
    delta: NumberOrArray
    sigma: NumberOrArray


def _clamp_alt(alt_m: NumberOrArray) -> tuple[np.ndarray, bool]:
    is_scalar = np.ndim(alt_m) == 0
    h = np.asarray(alt_m, dtype=np.float64)
    h_clamped = np.clip(h, -500.0, H3_MAX_M)
    return h_clamped, is_scalar


def temperature_K(alt_m: NumberOrArray) -> NumberOrArray:
    """Compute ISA static temperature T(h) [K]."""
    h, is_scalar = _clamp_alt(alt_m)
    T = np.where(
        h <= H1_TROPOPAUSE_M,
        T0_SL_K + LAPSE_TROPO_K_PER_M * h,
        np.where(
            h <= H2_STRATO_M,
            T1_TROPOPAUSE_K,
            T1_TROPOPAUSE_K + LAPSE_STRATO2_K_PER_M * (h - H2_STRATO_M),
        ),
    )
    return float(T) if is_scalar else T


def pressure_Pa(alt_m: NumberOrArray) -> NumberOrArray:
    """Compute ISA static pressure p(h) [Pa]."""
    h, is_scalar = _clamp_alt(alt_m)
    T = np.asarray(temperature_K(h), dtype=np.float64)

    exp_tropo = -G0_MPS2 / (R_AIR_J_KGK * LAPSE_TROPO_K_PER_M)
    exp_strato2 = -G0_MPS2 / (R_AIR_J_KGK * LAPSE_STRATO2_K_PER_M)

    p_tropo = P0_SL_PA * (np.maximum(T, 100.0) / T0_SL_K) ** exp_tropo
    p_iso = P1_TROPOPAUSE_PA * np.exp(-G0_MPS2 * (h - H1_TROPOPAUSE_M) / (R_AIR_J_KGK * T1_TROPOPAUSE_K))
    p_strato2 = P2_STRATO_PA * (np.maximum(T, 100.0) / T1_TROPOPAUSE_K) ** exp_strato2

    p = np.where(h <= H1_TROPOPAUSE_M, p_tropo, np.where(h <= H2_STRATO_M, p_iso, p_strato2))
    return float(p) if is_scalar else p


def density_kgm3(alt_m: NumberOrArray) -> NumberOrArray:
    """Compute ISA air density rho(h) [kg/m^3]."""
    T = temperature_K(alt_m)
    p = pressure_Pa(alt_m)
    rho = p / (R_AIR_J_KGK * T)
    return float(rho) if np.ndim(alt_m) == 0 else rho


def speed_of_sound_mps(alt_m: NumberOrArray) -> NumberOrArray:
    """Compute ISA speed of sound a(h) [m/s]."""
    T = temperature_K(alt_m)
    a = np.sqrt(GAMMA_AIR * R_AIR_J_KGK * T)
    return float(a) if np.ndim(alt_m) == 0 else a


def dynamic_viscosity_Pas(T_K: NumberOrArray) -> NumberOrArray:
    """Compute dynamic viscosity mu(T) [Pa*s] via Sutherland's law."""
    is_scalar = np.ndim(T_K) == 0
    T = np.maximum(np.asarray(T_K, dtype=np.float64), 50.0)
    mu = (
        SUTHERLAND_MU_REF_PAS
        * (T / SUTHERLAND_T_REF_K) ** 1.5
        * (SUTHERLAND_T_REF_K + SUTHERLAND_S_K)
        / (T + SUTHERLAND_S_K)
    )
    return float(mu) if is_scalar else mu


def isa_properties(alt_m: NumberOrArray) -> AtmosphereState:
    """Return full ISA 1976 state at altitude(s) `alt_m` [m]."""
    is_scalar = np.ndim(alt_m) == 0
    T = temperature_K(alt_m)
    p = pressure_Pa(alt_m)
    rho = p / (R_AIR_J_KGK * T)
    a = np.sqrt(GAMMA_AIR * R_AIR_J_KGK * T)
    mu = dynamic_viscosity_Pas(T)
    nu = mu / rho
    theta = T / T0_SL_K
    delta = p / P0_SL_PA
    sigma = rho / RHO0_SL_KGM3
    if is_scalar:
        return AtmosphereState(
            alt_m=float(alt_m),
            T_K=float(T),
            p_Pa=float(p),
            rho_kgm3=float(rho),
            a_mps=float(a),
            mu_Pas=float(mu),
            nu_m2ps=float(nu),
            theta=float(theta),
            delta=float(delta),
            sigma=float(sigma),
        )
    return AtmosphereState(
        alt_m=np.asarray(alt_m, dtype=np.float64),
        T_K=T,
        p_Pa=p,
        rho_kgm3=rho,
        a_mps=a,
        mu_Pas=mu,
        nu_m2ps=nu,
        theta=theta,
        delta=delta,
        sigma=sigma,
    )


def dynamic_pressure_Pa(mach: NumberOrArray, alt_m: NumberOrArray) -> NumberOrArray:
    """Compute compressible dynamic pressure q = 0.5 * gamma * p * M^2 [Pa]."""
    p = pressure_Pa(alt_m)
    m = np.asarray(mach, dtype=np.float64)
    q = 0.5 * GAMMA_AIR * p * (m ** 2)
    if np.ndim(mach) == 0 and np.ndim(alt_m) == 0:
        return float(q)
    return q


def reynolds_per_meter(mach: NumberOrArray, alt_m: NumberOrArray) -> NumberOrArray:
    """Compute Reynolds number per unit characteristic length Re/L = rho * V / mu [1/m]."""
    state = isa_properties(alt_m)
    v = np.asarray(mach, dtype=np.float64) * state.a_mps
    re_l = state.rho_kgm3 * v / state.mu_Pas
    if np.ndim(mach) == 0 and np.ndim(alt_m) == 0:
        return float(re_l)
    return re_l


def total_temperature_K(mach: NumberOrArray, alt_m: NumberOrArray) -> NumberOrArray:
    """Compute stagnation (total) temperature T0 = T * (1 + 0.5*(gamma-1)*M^2) [K]."""
    T = temperature_K(alt_m)
    m = np.asarray(mach, dtype=np.float64)
    T_tot = T * (1.0 + 0.5 * (GAMMA_AIR - 1.0) * (m ** 2))
    if np.ndim(mach) == 0 and np.ndim(alt_m) == 0:
        return float(T_tot)
    return T_tot


def recovery_temperature_K(mach: NumberOrArray, alt_m: NumberOrArray, recovery_factor: float = 0.89) -> NumberOrArray:
    """Compute adiabatic wall recovery temperature T_r = T * (1 + r * 0.5*(gamma-1)*M^2) [K]."""
    T = temperature_K(alt_m)
    m = np.asarray(mach, dtype=np.float64)
    T_rec = T * (1.0 + recovery_factor * 0.5 * (GAMMA_AIR - 1.0) * (m ** 2))
    if np.ndim(mach) == 0 and np.ndim(alt_m) == 0:
        return float(T_rec)
    return T_rec


def tas_to_eas_mps(v_tas_mps: NumberOrArray, alt_m: NumberOrArray) -> NumberOrArray:
    """Convert True Airspeed (TAS) to Equivalent Airspeed (EAS) [m/s]."""
    sigma = density_kgm3(alt_m) / RHO0_SL_KGM3
    v_eas = np.asarray(v_tas_mps, dtype=np.float64) * np.sqrt(sigma)
    if np.ndim(v_tas_mps) == 0 and np.ndim(alt_m) == 0:
        return float(v_eas)
    return v_eas


def eas_to_tas_mps(v_eas_mps: NumberOrArray, alt_m: NumberOrArray) -> NumberOrArray:
    """Convert Equivalent Airspeed (EAS) to True Airspeed (TAS) [m/s]."""
    sigma = density_kgm3(alt_m) / RHO0_SL_KGM3
    v_tas = np.asarray(v_eas_mps, dtype=np.float64) / np.sqrt(np.maximum(sigma, 1e-6))
    if np.ndim(v_eas_mps) == 0 and np.ndim(alt_m) == 0:
        return float(v_tas)
    return v_tas
