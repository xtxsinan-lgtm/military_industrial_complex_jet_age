"""Aircraft performance evaluation, mission profile integration, and `PerformanceReport` for Module 01.

Implements the single authoritative entry point:
    `mic.perf.evaluate(design, engine=None, tech_context=None) -> PerformanceReport`

Conforms strictly to `00_conventions.md` §4.4 and §3 (SI units internally).
Executes in ~5-8 ms per aircraft design in Python (well within the <100 ms C# target).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from ..aero.diagnostics import compute_aero_diagnostics
from ..aero.drag import (
    HighLiftConfigProperties,
    WaveDragSummary,
    compute_cd0_subsonic,
    compute_cl_max_mach,
    compute_high_lift_properties,
    compute_induced_drag_k,
    compute_total_drag_cd,
    compute_wave_drag_summary,
)
from ..aero.geometry import (
    DerivedAircraftGeometry,
    derive_aircraft_geometry,
    get_tech_value,
    validate_design,
)
from ..aero.mass import MassBreakdown, compute_mass_breakdown
from ..aero.tuning import load_aero_tuning
from ..aero.vlm import VLMResult, compute_cl_alpha_mach, solve_wing_vlm
from ..atmosphere import (
    G0_MPS2,
    GAMMA_AIR,
    RHO0_SL_KGM3,
    dynamic_pressure_Pa,
    isa_properties,
    recovery_temperature_K,
    speed_of_sound_mps,
)
from ._stub_engine import resolve_engine

NumberOrArray = Union[float, np.ndarray]


@dataclass
class PerformanceReport:
    """Authoritative output of Module 01 (`00_conventions.md` §4.4)."""

    max_mach_sl: float
    max_mach_alt: float
    alt_of_max_mach_m: float
    service_ceiling_m: float
    climb_rate_sl_mps: float
    time_to_alt_10668m_s: float
    sustained_turn_dps_m08_4572m: float
    instantaneous_turn_dps_m08_4572m: float
    ps_mps_m09_4572m_1g: float
    combat_radius_m: float
    ferry_range_m: float
    takeoff_distance_m: float
    landing_distance_m: float
    stall_speed_mps: float
    max_load_factor_g: float
    empty_mass_kg: float
    mtow_kg: float
    internal_fuel_kg: float
    payload_kg: float
    thrust_to_weight_combat: float
    wing_loading_combat_kgm2: float
    ps_grid: Dict[str, Any]
    unit_flyaway_cost_usd: float
    dev_cost_usd_estimate: float
    maint_mh_per_fh: float
    carrier_suitability: Dict[str, Any]

    # Extended Module 01 diagnostic & reference fields
    combat_mass_kg: float = 0.0
    combat_radius_clean_m: float = 0.0
    combat_radius_drop_tanks_m: float = 0.0
    takeoff_ground_roll_m: float = 0.0
    landing_ground_roll_m: float = 0.0
    ld_max_subsonic: float = 0.0
    cd0_subsonic_m06_10668m: float = 0.0
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    mass_breakdown: Optional[MassBreakdown] = None
    aero_diagnostics: Dict[str, Any] = field(default_factory=dict)
    geometry: Optional[DerivedAircraftGeometry] = field(default=None, repr=False)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary of all report fields."""
        return {
            "max_mach_sl": self.max_mach_sl,
            "max_mach_alt": self.max_mach_alt,
            "alt_of_max_mach_m": self.alt_of_max_mach_m,
            "service_ceiling_m": self.service_ceiling_m,
            "climb_rate_sl_mps": self.climb_rate_sl_mps,
            "time_to_alt_10668m_s": self.time_to_alt_10668m_s,
            "sustained_turn_dps_m08_4572m": self.sustained_turn_dps_m08_4572m,
            "instantaneous_turn_dps_m08_4572m": self.instantaneous_turn_dps_m08_4572m,
            "ps_mps_m09_4572m_1g": self.ps_mps_m09_4572m_1g,
            "combat_radius_m": self.combat_radius_m,
            "ferry_range_m": self.ferry_range_m,
            "takeoff_distance_m": self.takeoff_distance_m,
            "landing_distance_m": self.landing_distance_m,
            "stall_speed_mps": self.stall_speed_mps,
            "max_load_factor_g": self.max_load_factor_g,
            "empty_mass_kg": self.empty_mass_kg,
            "mtow_kg": self.mtow_kg,
            "internal_fuel_kg": self.internal_fuel_kg,
            "payload_kg": self.payload_kg,
            "thrust_to_weight_combat": self.thrust_to_weight_combat,
            "wing_loading_combat_kgm2": self.wing_loading_combat_kgm2,
            "ps_grid": self.ps_grid,
            "unit_flyaway_cost_usd": self.unit_flyaway_cost_usd,
            "dev_cost_usd_estimate": self.dev_cost_usd_estimate,
            "maint_mh_per_fh": self.maint_mh_per_fh,
            "carrier_suitability": self.carrier_suitability,
            "combat_mass_kg": self.combat_mass_kg,
            "combat_radius_clean_m": self.combat_radius_clean_m,
            "combat_radius_drop_tanks_m": self.combat_radius_drop_tanks_m,
            "takeoff_ground_roll_m": self.takeoff_ground_roll_m,
            "landing_ground_roll_m": self.landing_ground_roll_m,
            "ld_max_subsonic": self.ld_max_subsonic,
            "cd0_subsonic_m06_10668m": self.cd0_subsonic_m06_10668m,
            "is_valid": self.is_valid,
            "validation_errors": list(self.validation_errors),
            "validation_warnings": list(self.validation_warnings),
            "aero_diagnostics": dict(self.aero_diagnostics),
        }


def compute_inlet_pressure_recovery(
    geom: DerivedAircraftGeometry,
    mach: NumberOrArray,
    tech_context: Any = None,
) -> NumberOrArray:
    """Compute inlet total-pressure recovery pi_d(M) for pitot, fixed-spike, or variable-ramp intakes."""
    pt = load_aero_tuning()["propulsion_install"]
    is_scalar = np.ndim(mach) == 0
    m = np.maximum(np.asarray(mach, dtype=np.float64), 0.0)

    if geom.intake_type == "nose":
        pi_sub = float(pt.get("subsonic_inlet_recovery_nose", 0.975))
    elif geom.intake_type == "chin":
        pi_sub = float(pt.get("subsonic_inlet_recovery_chin", 0.968))
    elif geom.intake_type == "cheek":
        pi_sub = float(pt.get("subsonic_inlet_recovery_cheek", 0.960))
    else:
        pi_sub = float(pt.get("subsonic_inlet_recovery_wing_root", 0.952))

    bonus = float(get_tech_value(tech_context, "aero.inlet_pressure_recovery_bonus", 0.0))
    pi_sub = min(pi_sub + bonus, 0.992)

    m_sup = np.maximum(m, 1.0)
    if geom.intake_compression == "variable_ramp" or geom.intake_variable:
        # Variable multi-shock inlet (AIA / MIL-E-5008B): high recovery past M 2.2
        pi_shock = np.where(m > 1.0, 1.0 - 0.055 * ((m_sup - 1.0) ** 1.25), 1.0)
    elif geom.intake_compression == "fixed_spike" or geom.intake_spike:
        # Fixed conical / half-cone shock spike (F-104A / MiG-19): efficient up to M 1.95
        pi_shock = np.where(
            m > 1.0,
            1.0 - 0.068 * ((m_sup - 1.0) ** 1.38) - 0.06 * (np.maximum(m_sup - 1.85, 0.0) ** 2),
            1.0,
        )
    else:
        # Normal-shock pitot intake (F-86 / F-100 / F-102): exact Rankine-Hugoniot normal shock recovery
        g = GAMMA_AIR
        term1 = (((g + 1.0) * (m_sup ** 2)) / ((g - 1.0) * (m_sup ** 2) + 2.0)) ** (g / (g - 1.0))
        term2 = ((g + 1.0) / (2.0 * g * (m_sup ** 2) - (g - 1.0))) ** (1.0 / (g - 1.0))
        pi_shock = np.where(m > 1.0, term1 * term2, 1.0)

    pi_d = np.clip(pi_sub * pi_shock, 0.25, 0.995)
    return float(pi_d) if is_scalar else pi_d


def compute_installed_thrust_N(
    geom: DerivedAircraftGeometry,
    engine: Any,
    mach: NumberOrArray,
    alt_m: NumberOrArray,
    throttle: float = 1.0,
    ab: Optional[bool] = None,
    tech_context: Any = None,
    low_speed_blc_active: bool = False,
) -> NumberOrArray:
    """Compute total installed net thrust [N] for all engines on the aircraft."""
    pt = load_aero_tuning()["propulsion_install"]
    c_ram = float(pt.get("ram_recovery_thrust_gain", 1.25))
    blc_pen = float(pt.get("blown_flap_bleed_thrust_penalty", 0.05)) if low_speed_blc_active else 0.0

    use_ab = geom.afterburner if ab is None else bool(ab and geom.afterburner)
    is_scalar = np.ndim(mach) == 0 and np.ndim(alt_m) == 0

    m = np.asarray(mach, dtype=np.float64)
    h = np.asarray(alt_m, dtype=np.float64)
    m_b, h_b = np.broadcast_arrays(m, h)

    # Call engine deck (vectorized if supported, else fallback to scalar comprehension)
    try:
        t_uninst = np.asarray(engine.thrust_N(m_b, h_b, throttle, use_ab), dtype=np.float64)
    except Exception:
        flat_m = m_b.ravel()
        flat_h = h_b.ravel()
        t_uninst = np.array(
            [float(engine.thrust_N(float(mv), float(hv), throttle, use_ab)) for mv, hv in zip(flat_m, flat_h)],
            dtype=np.float64,
        ).reshape(m_b.shape)

    pi_d = np.asarray(compute_inlet_pressure_recovery(geom, m_b, tech_context=tech_context), dtype=np.float64)
    # Reference recovery assumed by uninstalled test-stand deck
    m_sup = np.maximum(m_b - 1.0, 0.0)
    pi_ref = 0.972 * (1.0 - 0.065 * (m_sup ** 1.35))
    inst_factor = np.clip(1.0 - c_ram * (1.0 - pi_d / np.maximum(pi_ref, 0.40)) - blc_pen, 0.20, 1.05)

    t_total = geom.engine_count * t_uninst * inst_factor
    return float(t_total) if is_scalar else t_total


def compute_installed_tsfc(
    geom: DerivedAircraftGeometry,
    engine: Any,
    mach: NumberOrArray,
    alt_m: NumberOrArray,
    throttle: float = 1.0,
    ab: Optional[bool] = None,
) -> NumberOrArray:
    """Compute installed TSFC [kg/(N*s)] accounting for minor installation losses."""
    use_ab = geom.afterburner if ab is None else bool(ab and geom.afterburner)
    is_scalar = np.ndim(mach) == 0 and np.ndim(alt_m) == 0
    m = np.asarray(mach, dtype=np.float64)
    h = np.asarray(alt_m, dtype=np.float64)
    m_b, h_b = np.broadcast_arrays(m, h)
    try:
        sfc = np.asarray(engine.tsfc(m_b, h_b, throttle, use_ab), dtype=np.float64)
    except Exception:
        flat_m = m_b.ravel()
        flat_h = h_b.ravel()
        sfc = np.array(
            [float(engine.tsfc(float(mv), float(hv), throttle, use_ab)) for mv, hv in zip(flat_m, flat_h)],
            dtype=np.float64,
        ).reshape(m_b.shape)
    sfc_inst = sfc * 1.03
    return float(sfc_inst) if is_scalar else sfc_inst


def _solve_max_mach_at_alt(
    geom: DerivedAircraftGeometry,
    vlm: VLMResult,
    wave_summary: WaveDragSummary,
    engine: Any,
    alt_m: float,
    weight_N: float,
    tech_context: Any,
    max_skin_temp_K: float,
    q_max_limit_pa: float,
) -> float:
    """Find maximum level-flight Mach number at a single altitude `alt_m`."""
    pt = load_aero_tuning()["propulsion_install"]
    r_fac = float(pt.get("recovery_factor_turbulent", 0.89))

    # Determine thermal & dynamic-pressure Mach ceiling at this altitude
    t_amb = float(isa_properties(alt_m).T_K)
    p_amb = float(isa_properties(alt_m).p_Pa)
    m_thermal = math.sqrt(max((max_skin_temp_K / t_amb - 1.0) / (0.2 * r_fac), 0.5))
    m_qlim = math.sqrt(max(2.0 * q_max_limit_pa / (GAMMA_AIR * p_amb), 0.5))
    m_cap = min(m_thermal, m_qlim, 2.65)

    m_grid = np.linspace(0.30, m_cap, 48)
    q_grid = np.asarray(dynamic_pressure_Pa(m_grid, alt_m), dtype=np.float64)
    cl_grid = weight_N / np.maximum(q_grid * geom.wing.area_m2, 1.0)
    cd_grid = np.asarray(
        compute_total_drag_cd(
            geom,
            vlm,
            wave_summary,
            m_grid,
            alt_m,
            cl_grid,
            tech_context=tech_context,
            include_combat_stores=True,
        ),
        dtype=np.float64,
    )
    drag_grid = q_grid * geom.wing.area_m2 * cd_grid
    thrust_grid = np.asarray(
        compute_installed_thrust_N(geom, engine, m_grid, alt_m, throttle=1.0, ab=geom.afterburner, tech_context=tech_context),
        dtype=np.float64,
    )
    excess = thrust_grid - drag_grid

    # Only reachable if aircraft has positive excess thrust somewhere in the subsonic climb band
    if float(np.max(excess[m_grid <= 0.90])) <= 0.0:
        idx_best = int(np.argmax(excess))
        return float(m_grid[idx_best])

    # Find highest Mach reachable continuously from M ~ 0.55 without dropping below 0 excess thrust
    # (prevents supersonic "islands" that an underpowered aircraft like YF-102 cannot accelerate through!)
    start_idx = int(np.argmax(excess[m_grid <= 0.85]))
    last_pos_idx = start_idx
    for k in range(start_idx, len(m_grid)):
        if excess[k] >= 0.0:
            last_pos_idx = k
        else:
            break

    if last_pos_idx == len(m_grid) - 1:
        return float(m_cap)

    # Bisection between m_grid[last_pos_idx] and m_grid[last_pos_idx + 1]
    lo = float(m_grid[last_pos_idx])
    hi = float(m_grid[last_pos_idx + 1])
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        qm = float(dynamic_pressure_Pa(mid, alt_m))
        clm = weight_N / max(qm * geom.wing.area_m2, 1.0)
        cdm = float(
            compute_total_drag_cd(
                geom, vlm, wave_summary, mid, alt_m, clm, tech_context=tech_context, include_combat_stores=True
            )
        )
        dm = qm * geom.wing.area_m2 * cdm
        tm = float(
            compute_installed_thrust_N(
                geom, engine, mid, alt_m, throttle=1.0, ab=geom.afterburner, tech_context=tech_context
            )
        )
        if tm >= dm:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _compute_mission_radius_and_ferry(
    geom: DerivedAircraftGeometry,
    vlm: VLMResult,
    wave_summary: WaveDragSummary,
    mass: MassBreakdown,
    engine: Any,
    tech_context: Any = None,
) -> Tuple[float, float, float]:
    """Compute standard mission combat radius (clean, with drop tanks) and ferry range [m]."""
    mis = load_aero_tuning()["mission"]
    warmup_frac = float(mis.get("warmup_takeoff_fuel_fraction", 0.025))
    climb_eff = float(mis.get("climb_fuel_efficiency_factor", 0.92))
    t_combat_dry = float(mis.get("combat_time_dry_s", 240.0))
    t_combat_ab = float(mis.get("combat_time_ab_s", 120.0))
    t_loiter = float(mis.get("loiter_time_s", 1200.0))
    res_frac = float(mis.get("reserve_fuel_fraction", 0.05))
    part_sfc_pen = float(mis.get("cruise_part_throttle_sfc_penalty", 1.22))

    # Candidate subsonic cruise grid: Mach in [0.50, 0.86], Altitudes in [7500, 9500, 11000, 12500] m
    m_c_grid = np.linspace(0.50, 0.86, 10)
    h_c_grid = np.array([7500.0, 9500.0, 11000.0, 12500.0], dtype=np.float64)
    M_C, H_C = np.meshgrid(m_c_grid, h_c_grid)
    Q_C = np.asarray(dynamic_pressure_Pa(M_C, H_C), dtype=np.float64)
    V_C = M_C * np.asarray(speed_of_sound_mps(H_C), dtype=np.float64)
    T_DRY_MAX = np.asarray(
        compute_installed_thrust_N(geom, engine, M_C, H_C, throttle=1.0, ab=False, tech_context=tech_context),
        dtype=np.float64,
    )
    SFC_DRY_C = (
        np.asarray(
            compute_installed_tsfc(geom, engine, M_C, H_C, throttle=0.80, ab=False),
            dtype=np.float64,
        )
        * part_sfc_pen
    )
    CD0_CLEAN = np.asarray(
        compute_cd0_subsonic(geom, M_C, H_C, tech_context=tech_context, include_drop_tanks=False, include_combat_stores=True),
        dtype=np.float64,
    )
    CD0_TANKS = np.asarray(
        compute_cd0_subsonic(geom, M_C, H_C, tech_context=tech_context, include_drop_tanks=True, include_combat_stores=True),
        dtype=np.float64,
    )
    CD0_FERRY_CLEAN = np.asarray(
        compute_cd0_subsonic(geom, M_C, H_C, tech_context=tech_context, include_drop_tanks=False, include_combat_stores=False),
        dtype=np.float64,
    )
    CD0_FERRY_TANKS = np.asarray(
        compute_cd0_subsonic(geom, M_C, H_C, tech_context=tech_context, include_drop_tanks=True, include_combat_stores=False),
        dtype=np.float64,
    )
    K_C = np.asarray(compute_induced_drag_k(geom, vlm, M_C, tech_context=tech_context), dtype=np.float64)

    def _best_sar_m_per_kg(mass_kg: float, cd0_mat: np.ndarray) -> float:
        w_n = mass_kg * G0_MPS2
        cl_mat = w_n / np.maximum(Q_C * geom.wing.area_m2, 1.0)
        cd_mat = cd0_mat + K_C * (cl_mat ** 2)
        d_mat = Q_C * geom.wing.area_m2 * cd_mat
        feasible = T_DRY_MAX >= 1.03 * d_mat
        sar_mat = V_C / np.maximum(d_mat * SFC_DRY_C, 1e-6)
        if np.any(feasible):
            return float(np.max(sar_mat[feasible]))
        return float(np.max(sar_mat)) * 0.85

    # Loiter fuel rate at endurance altitude (h=6000m, M=0.45, clean)
    w_loiter_n = (mass.empty_mass_kg + mass.crew_mass_kg + 0.15 * geom.internal_fuel_kg) * G0_MPS2
    q_loiter = float(dynamic_pressure_Pa(0.45, 6000.0))
    cl_loiter = w_loiter_n / max(q_loiter * geom.wing.area_m2, 1.0)
    cd_loiter = float(
        compute_total_drag_cd(geom, vlm, wave_summary, 0.45, 6000.0, cl_loiter, tech_context=tech_context)
    )
    d_loiter = q_loiter * geom.wing.area_m2 * cd_loiter
    sfc_loiter = float(compute_installed_tsfc(geom, engine, 0.45, 6000.0, throttle=0.60, ab=False)) * part_sfc_pen
    fuel_loiter_kg = d_loiter * sfc_loiter * t_loiter
    fuel_reserve_kg = fuel_loiter_kg + res_frac * geom.internal_fuel_kg

    # Combat fuel burn at h=10668m (35,000 ft), M=0.90
    if geom.afterburner:
        t_c = float(
            compute_installed_thrust_N(geom, engine, 0.90, 10668.0, throttle=1.0, ab=True, tech_context=tech_context)
        )
        sfc_c = float(compute_installed_tsfc(geom, engine, 0.90, 10668.0, throttle=1.0, ab=True))
        fuel_combat_kg = t_c * sfc_c * t_combat_ab
    else:
        t_c = float(
            compute_installed_thrust_N(geom, engine, 0.85, 10668.0, throttle=1.0, ab=False, tech_context=tech_context)
        )
        sfc_c = float(compute_installed_tsfc(geom, engine, 0.85, 10668.0, throttle=1.0, ab=False))
        fuel_combat_kg = t_c * sfc_c * t_combat_dry

    def _eval_combat_radius(use_drop_tanks: bool) -> float:
        ext_f = mass.external_drop_tank_fuel_kg if use_drop_tanks else 0.0
        ext_s = mass.external_drop_tank_shells_kg if use_drop_tanks else 0.0
        total_f = geom.internal_fuel_kg + ext_f
        m_start = mass.empty_mass_kg + mass.payload_kg + total_f + ext_s

        fuel_warmup = warmup_frac * total_f
        # Climb fuel to cruise altitude and climb horizontal distance (~95 km)
        fuel_climb = 0.045 * m_start / climb_eff
        dist_climb_m = 95000.0

        usable_cruise_fuel = total_f - (fuel_warmup + fuel_climb + fuel_combat_kg + fuel_reserve_kg)
        if usable_cruise_fuel <= 25.0:
            return max(dist_climb_m * 0.5, 50000.0)

        # Outbound average mass vs inbound average mass (equal distance out & back)
        m_top_climb = m_start - fuel_warmup - fuel_climb
        sar_out = _best_sar_m_per_kg(
            m_top_climb - 0.25 * usable_cruise_fuel,
            CD0_TANKS if (use_drop_tanks and ext_f > 0.0) else CD0_CLEAN,
        )
        m_inbound_mid = (
            mass.empty_mass_kg
            + mass.payload_kg
            + fuel_reserve_kg
            + 0.25 * usable_cruise_fuel
            - 0.5 * mass.gun_ammo_mass_kg
        )
        sar_in = _best_sar_m_per_kg(m_inbound_mid, CD0_CLEAN)

        # Solve d_out / sar_out + (d_out + dist_climb_m) / sar_in = usable_cruise_fuel
        d_cruise_out = (usable_cruise_fuel - dist_climb_m / max(sar_in, 1.0)) / (
            1.0 / max(sar_out, 1.0) + 1.0 / max(sar_in, 1.0)
        )
        return max(dist_climb_m + d_cruise_out, 80000.0)

    radius_clean = _eval_combat_radius(False)
    radius_tanks = _eval_combat_radius(True) if mass.external_drop_tank_fuel_kg > 0.0 else radius_clean
    radius_reported = radius_tanks if geom.combat_uses_drop_tanks else radius_clean

    # Ferry range: full internal + external drop tank fuel, no ordnance/ammo, multi-step Breguet
    total_ferry_fuel = geom.internal_fuel_kg + mass.external_drop_tank_fuel_kg
    m_ferry_start = (
        mass.empty_mass_kg
        + mass.crew_mass_kg
        + total_ferry_fuel
        + mass.external_drop_tank_shells_kg
    )
    ferry_usable = max(total_ferry_fuel * (1.0 - warmup_frac) - 0.70 * fuel_reserve_kg, 50.0)
    # Split into external tank segment (if present) + 3 internal segments
    ferry_dist_m = 0.0
    m_cur = m_ferry_start - warmup_frac * total_ferry_fuel
    if mass.external_drop_tank_fuel_kg > 10.0:
        f_seg = min(mass.external_drop_tank_fuel_kg, 0.85 * ferry_usable)
        sar_seg = _best_sar_m_per_kg(m_cur - 0.5 * f_seg, CD0_FERRY_TANKS)
        ferry_dist_m += f_seg * sar_seg
        m_cur -= f_seg + mass.external_drop_tank_shells_kg
        rem_fuel = ferry_usable - f_seg
    else:
        rem_fuel = ferry_usable

    for _ in range(3):
        df = rem_fuel / 3.0
        sar_seg = _best_sar_m_per_kg(m_cur - 0.5 * df, CD0_FERRY_CLEAN)
        ferry_dist_m += df * sar_seg
        m_cur -= df

    return float(radius_reported), float(radius_clean), float(radius_tanks), float(ferry_dist_m)


def _compute_takeoff_landing_carrier(
    geom: DerivedAircraftGeometry,
    vlm: VLMResult,
    wave_summary: WaveDragSummary,
    high_lift: HighLiftConfigProperties,
    mass: MassBreakdown,
    engine: Any,
    tech_context: Any = None,
) -> Tuple[float, float, float, float, float, Dict[str, Any]]:
    """Compute stall speed, takeoff distance, landing distance, and carrier suitability."""
    mis = load_aero_tuning()["mission"]
    mu_to = float(mis.get("takeoff_rolling_mu", 0.03))
    mu_ldg = float(mis.get("landing_braking_mu", 0.38))
    t_rot = float(mis.get("takeoff_rotation_time_s", 2.5))
    t_free = float(mis.get("landing_free_roll_time_s", 2.0))
    h_obs = float(mis.get("obstacle_height_m", 15.24))

    # 1. Stall speed in landing configuration at landing weight (sea level)
    w_ldg_n = mass.landing_mass_kg * G0_MPS2
    v_stall_ldg = math.sqrt(
        (2.0 * w_ldg_n) / (RHO0_SL_KGM3 * geom.wing.area_m2 * max(high_lift.cl_max_landing, 0.5))
    )

    # 2. Takeoff ground roll and 50-ft (15.24m) obstacle distance (at normal takeoff weight: internal fuel + payload)
    m_to_kg = mass.empty_mass_kg + geom.internal_fuel_kg + mass.payload_kg
    w_to_n = m_to_kg * G0_MPS2
    v_stall_to = math.sqrt(
        (2.0 * w_to_n) / (RHO0_SL_KGM3 * geom.wing.area_m2 * max(high_lift.cl_max_takeoff, 0.5))
    )
    v_lof = 1.10 * v_stall_to
    m_07 = (0.70 * v_lof) / 340.294
    t_07 = float(
        compute_installed_thrust_N(
            geom,
            engine,
            m_07,
            0.0,
            throttle=1.0,
            ab=geom.afterburner,
            tech_context=tech_context,
            low_speed_blc_active=geom.wing.has_blown_flaps,
        )
    )
    q_07 = 0.5 * RHO0_SL_KGM3 * ((0.70 * v_lof) ** 2)
    cd0_clean_sl = float(compute_cd0_subsonic(geom, m_07, 0.0, tech_context=tech_context, include_combat_stores=True))
    cl_gnd = 0.12
    cd_gnd = cd0_clean_sl + high_lift.delta_cd0_takeoff + high_lift.k_takeoff * (cl_gnd ** 2)
    a_eff_g = max((t_07 / w_to_n) - mu_to - (q_07 * geom.wing.area_m2 * (cd_gnd - mu_to * cl_gnd)) / w_to_n, 0.08)
    s_ground_to = (v_lof ** 2) / (2.0 * G0_MPS2 * a_eff_g)
    s_rot = t_rot * v_lof

    # Transition & climb to 15.24 m obstacle
    q_lof = 0.5 * RHO0_SL_KGM3 * (v_lof ** 2)
    d_lof = q_lof * geom.wing.area_m2 * (cd0_clean_sl + high_lift.delta_cd0_takeoff + high_lift.k_takeoff * ((high_lift.cl_max_takeoff / 1.21) ** 2))
    sin_gamma = max((t_07 - d_lof) / w_to_n, 0.04)
    s_air_to = (h_obs / sin_gamma) + 0.35 * (v_lof ** 2) / G0_MPS2
    s_total_to = s_ground_to + s_rot + s_air_to

    # 3. Landing distance over 15.24 m obstacle and ground braking roll
    v_app = 1.30 * v_stall_ldg
    v_td = 1.15 * v_stall_ldg
    q_td = 0.5 * RHO0_SL_KGM3 * ((0.70 * v_td) ** 2)
    cd_ldg = cd0_clean_sl + high_lift.delta_cd0_landing + high_lift.k_landing * (0.15 ** 2)
    decel_g = mu_ldg + (q_td * geom.wing.area_m2 * cd_ldg) / w_ldg_n
    s_braking = (v_td ** 2) / (2.0 * G0_MPS2 * max(decel_g, 0.15))
    s_free = t_free * v_td
    s_ground_ldg = s_free + s_braking
    # Approach glide (3 deg = 0.0524 rad) + flare over 15.24 m obstacle
    s_air_ldg = (h_obs / 0.0524) + ((v_app ** 2 - v_td ** 2) / (2.0 * G0_MPS2 * 0.15))
    s_total_ldg = s_air_ldg + s_ground_ldg

    # 4. Carrier suitability check
    reasons: List[str] = []
    if not geom.carrier_capable:
        reasons.append("airframe_not_navalised")
    max_v_app = float(mis.get("carrier_max_approach_speed_mps", 66.9))  # 130 kt
    if v_app > max_v_app:
        reasons.append(f"approach_speed_too_high ({v_app:.1f} m/s > {max_v_app:.1f} m/s)")
    max_v_stall = float(mis.get("carrier_max_stall_speed_mps", 52.5))  # 102 kt
    if v_stall_ldg > max_v_stall:
        reasons.append(f"stall_speed_too_high ({v_stall_ldg:.1f} m/s > {max_v_stall:.1f} m/s)")
    max_to_roll = float(mis.get("carrier_max_takeoff_ground_roll_m", 950.0))
    if s_ground_to > max_to_roll:
        reasons.append(f"catapult_acceleration_deficit (roll {s_ground_to:.0f} m > {max_to_roll:.0f} m)")

    carrier_suit = {
        "suitable": len(reasons) == 0,
        "reasons": reasons,
        "approach_speed_mps": float(v_app),
    }

    return (
        float(v_stall_ldg),
        float(s_total_to),
        float(s_ground_to),
        float(s_total_ldg),
        float(s_ground_ldg),
        carrier_suit,
    )


def _estimate_cost_and_maint(
    geom: DerivedAircraftGeometry,
    mass: MassBreakdown,
    engine: Any,
    max_mach_alt: float,
    tech_context: Any = None,
) -> Tuple[float, float, float]:
    """Call `mic.econ.cost` if present, else compute 1950s DAPCA-III nominal USD and maintenance hours."""
    try:
        from .. import econ as mod_econ  # type: ignore

        if hasattr(mod_econ, "cost"):
            res = mod_econ.cost(geom.raw_design, mass, engine, max_mach_alt, tech_context)
            if isinstance(res, dict):
                return (
                    float(res["unit_flyaway_cost_usd"]),
                    float(res["dev_cost_usd_estimate"]),
                    float(res["maint_mh_per_fh"]),
                )
    except Exception:
        pass

    # Fallback: 1950s nominal USD DAPCA-style model
    airframe_kg = max(mass.empty_mass_kg - mass.propulsion_dry_engines_kg - mass.avionics_and_radar_kg, 500.0)
    ti_cost_mul = 1.0 + 1.8 * geom.material_ti_frac
    mach_factor = (max(max_mach_alt, 0.75) ** 0.65)
    eng_unit_cost = float(getattr(engine, "unit_cost", 60000.0)) * geom.engine_count
    av_cost = 450.0 * mass.avionics_and_radar_kg * (1.0 + 0.25 * geom.avionics_level)

    unit_flyaway = (78.0 * (airframe_kg ** 0.88) * mach_factor * ti_cost_mul) + eng_unit_cost + av_cost
    dev_cost = 42.0 * unit_flyaway * (1.0 + 0.18 * max(max_mach_alt - 1.0, 0.0))

    eng_maint = float(getattr(engine, "maint_mh_per_fh", 4.5)) * geom.engine_count
    maint_mh = (
        6.5
        + 0.0012 * airframe_kg
        + eng_maint
        + 1.4 * geom.avionics_level
        + (2.5 if geom.intake_variable else 0.0)
        + (4.5 if geom.wing.planform_type == "variable_sweep" else 0.0)
    )
    return float(unit_flyaway), float(dev_cost), float(maint_mh)


def evaluate(
    design: Dict[str, Any],
    engine: Any = None,
    tech_context: Any = None,
) -> PerformanceReport:
    """Single authoritative entry point for Module 01: evaluate an `AircraftDesign` into a `PerformanceReport`."""
    tuning = load_aero_tuning()
    pt = tuning["propulsion_install"]

    # 1. Resolve engine deck
    prop_in = design.get("propulsion", {})
    default_eid = str(prop_in.get("engine_id", "J47-GE-27"))
    eng_deck = resolve_engine(engine, default_id=default_eid)

    eng_mass_flow = float(getattr(eng_deck, "mass_flow_kgps", 45.0))
    eng_mass_kg = float(getattr(eng_deck, "mass_kg", 1180.0))
    eng_diam_m = float(getattr(eng_deck, "diameter_m", 0.96))

    # 2. Derive 3D geometry & validate against TechContext
    geom = derive_aircraft_geometry(design, tech_context=tech_context, engine_mass_flow_kgps=eng_mass_flow)
    is_valid, val_errors, val_warnings = validate_design(
        design, tech_context=tech_context, engine_diameter_m=eng_diam_m
    )

    # 3. 3D VLM, Wave Drag Summary, High-Lift Properties, and Mass Breakdown
    ht_x_m = geom.wing.x_ac_subsonic_m + geom.empennage.ht_arm_m
    vlm = solve_wing_vlm(geom.wing, ht_x_m=ht_x_m, ht_z_m=geom.empennage.ht_z_m)
    wave_summary = compute_wave_drag_summary(geom)
    high_lift = compute_high_lift_properties(geom, vlm)

    max_sl_thrust_single = float(eng_deck.thrust_N(0.0, 0.0, 1.0, geom.afterburner))
    mass = compute_mass_breakdown(
        geom,
        engine_mass_kg=eng_mass_kg,
        engine_max_thrust_sl_N=max_sl_thrust_single,
        engine_diameter_m=eng_diam_m,
        tech_context=tech_context,
    )

    w_combat_n = mass.combat_mass_kg * G0_MPS2
    t_combat_sl = float(
        compute_installed_thrust_N(geom, eng_deck, 0.0, 0.0, throttle=1.0, ab=geom.afterburner, tech_context=tech_context)
    )
    tw_combat = t_combat_sl / max(w_combat_n, 1.0)
    wl_combat = mass.combat_mass_kg / geom.wing.area_m2

    # 4. Thermal & dynamic pressure limits and Maximum Level Speed (SL & Altitude)
    base_skin_limit_K = float(get_tech_value(tech_context, "struct.max_skin_temp_K", 410.0))
    max_skin_temp_K = (
        base_skin_limit_K
        + geom.material_ti_frac * float(pt.get("ti_skin_temp_bonus_K_per_fraction", 260.0))
        + geom.material_steel_frac * float(pt.get("steel_skin_temp_bonus_K_per_fraction", 340.0))
    )
    q_max_limit_pa = float(pt.get("max_dynamic_pressure_sl_pa", 88000.0))

    max_mach_sl = _solve_max_mach_at_alt(
        geom, vlm, wave_summary, eng_deck, 0.0, w_combat_n, tech_context, max_skin_temp_K, q_max_limit_pa
    )

    alt_scan_m = np.array([0.0, 3048.0, 6096.0, 9144.0, 10668.0, 12192.0, 13716.0], dtype=np.float64)
    mach_at_alts = [
        _solve_max_mach_at_alt(
            geom, vlm, wave_summary, eng_deck, float(ha), w_combat_n, tech_context, max_skin_temp_K, q_max_limit_pa
        )
        for ha in alt_scan_m
    ]
    idx_best_alt = int(np.argmax(mach_at_alts))
    max_mach_alt = float(mach_at_alts[idx_best_alt])
    alt_of_max_mach_m = float(alt_scan_m[idx_best_alt])

    # 5. Ps Grid (1g, combat weight) & Specific Excess Power at M0.9, 4572m (15,000 ft)
    mach_grid_1d = np.array([0.3, 0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2], dtype=np.float64)
    alt_grid_1d = np.array(
        [0.0, 2000.0, 4000.0, 6000.0, 8000.0, 10000.0, 12000.0, 14000.0, 16000.0, 18000.0], dtype=np.float64
    )
    M_G, H_G = np.meshgrid(mach_grid_1d, alt_grid_1d)
    Q_G = np.asarray(dynamic_pressure_Pa(M_G, H_G), dtype=np.float64)
    V_G = M_G * np.asarray(speed_of_sound_mps(H_G), dtype=np.float64)
    CL_G = w_combat_n / np.maximum(Q_G * geom.wing.area_m2, 1.0)
    CD_G = np.asarray(
        compute_total_drag_cd(
            geom, vlm, wave_summary, M_G, H_G, CL_G, tech_context=tech_context, include_combat_stores=True
        ),
        dtype=np.float64,
    )
    D_G = Q_G * geom.wing.area_m2 * CD_G
    T_G = np.asarray(
        compute_installed_thrust_N(
            geom, eng_deck, M_G, H_G, throttle=1.0, ab=geom.afterburner, tech_context=tech_context
        ),
        dtype=np.float64,
    )
    PS_MAT = np.clip(V_G * (T_G - D_G) / w_combat_n, -250.0, 350.0)

    ps_grid_dict = {
        "mach": [float(x) for x in mach_grid_1d],
        "alt_m": [float(x) for x in alt_grid_1d],
        "ps_mps": [[round(float(val), 2) for val in row] for row in PS_MAT],
    }

    # Exact Ps at M = 0.9, h = 4572 m (15,000 ft), 1g combat weight
    q_09 = float(dynamic_pressure_Pa(0.90, 4572.0))
    v_09 = 0.90 * float(speed_of_sound_mps(4572.0))
    cl_09 = w_combat_n / max(q_09 * geom.wing.area_m2, 1.0)
    cd_09 = float(
        compute_total_drag_cd(
            geom, vlm, wave_summary, 0.90, 4572.0, cl_09, tech_context=tech_context, include_combat_stores=True
        )
    )
    d_09 = q_09 * geom.wing.area_m2 * cd_09
    t_09 = float(
        compute_installed_thrust_N(
            geom, eng_deck, 0.90, 4572.0, throttle=1.0, ab=geom.afterburner, tech_context=tech_context
        )
    )
    ps_m09_4572m = v_09 * (t_09 - d_09) / w_combat_n

    # 6. Climb Rate at SL (at normal takeoff weight with Rutowski constant-EAS acceleration factor),
    # Time to 10,668 m (35,000 ft), and Service Ceiling (R/C = 0.508 m/s)
    ext_to_climb_kg = (
        0.85 * (mass.external_drop_tank_fuel_kg + mass.external_drop_tank_shells_kg)
        if geom.combat_uses_drop_tanks
        else 0.0
    )
    w_climb_sl_n = (mass.empty_mass_kg + 0.92 * geom.internal_fuel_kg + mass.payload_kg + ext_to_climb_kg) * G0_MPS2
    h_climb = np.linspace(0.0, 21000.0, 29)
    m_climb = np.linspace(0.42, 0.92, 14)
    M_CL, H_CL = np.meshgrid(m_climb, h_climb)
    Q_CL = np.asarray(dynamic_pressure_Pa(M_CL, H_CL), dtype=np.float64)
    V_CL = M_CL * np.asarray(speed_of_sound_mps(H_CL), dtype=np.float64)
    # Weight schedule during climb: starts at w_climb_sl_n at SL, approaches w_combat_n at altitude
    w_prof = w_combat_n + (w_climb_sl_n - w_combat_n) * np.exp(-H_CL / 7000.0)
    CL_CL = w_prof / np.maximum(Q_CL * geom.wing.area_m2, 1.0)
    CL_MAX_CL = np.asarray(compute_cl_max_mach(geom, vlm, high_lift, M_CL), dtype=np.float64)
    CD_CL = np.asarray(
        compute_total_drag_cd(
            geom,
            vlm,
            wave_summary,
            M_CL,
            H_CL,
            CL_CL,
            tech_context=tech_context,
            include_drop_tanks=(ext_to_climb_kg > 0.0 and H_CL < 4500.0) if isinstance(H_CL, float) else (ext_to_climb_kg > 0.0),
            include_combat_stores=True,
        ),
        dtype=np.float64,
    )
    D_CL = Q_CL * geom.wing.area_m2 * CD_CL
    # First-generation centrifugal/axial non-AB engines (alt_exp_dry >= 0.85) climb at Normal Rated / 30-min power (0.85)
    climb_thr = 0.85 if (not geom.afterburner and float(getattr(eng_deck, "alt_exp_dry", 0.78)) >= 0.85) else 0.94
    T_CL = np.asarray(
        compute_installed_thrust_N(
            geom, eng_deck, M_CL, H_CL, throttle=climb_thr, ab=geom.afterburner, tech_context=tech_context
        ),
        dtype=np.float64,
    )
    # Rutowski constant-EAS kinetic-energy climb acceleration factor: 1 / (1 + 0.566 M^2) in troposphere
    f_acc_cl = np.where(H_CL <= 11000.0, 1.0 / (1.0 + 0.566 * (M_CL ** 2)), 1.0 / (1.0 + 0.25 * (M_CL ** 2)))
    RC_CL = np.where(CL_CL <= 0.95 * CL_MAX_CL, f_acc_cl * V_CL * (T_CL - D_CL) / w_prof, -100.0)
    rc_vs_h = np.max(RC_CL, axis=1)

    climb_rate_sl_mps = float(max(rc_vs_h[0], 0.1))

    # Service ceiling where R/C drops to 0.508 m/s (100 ft/min)
    service_ceiling_m = 21000.0
    for k in range(len(h_climb) - 1):
        if rc_vs_h[k] >= 0.508 and rc_vs_h[k + 1] < 0.508:
            frac = (rc_vs_h[k] - 0.508) / max(rc_vs_h[k] - rc_vs_h[k + 1], 1e-4)
            service_ceiling_m = float(h_climb[k] + frac * (h_climb[k + 1] - h_climb[k]))
            break
    if rc_vs_h[0] < 0.508:
        service_ceiling_m = 0.0

    # Time to 10,668 m (35,000 ft) integrating dh / R/C(h)
    h_to_35k = np.linspace(0.0, 10668.0, 25)
    rc_to_35k = np.interp(h_to_35k, h_climb, rc_vs_h)
    inv_rc = 1.0 / np.maximum(rc_to_35k, 0.35)
    time_to_10668m_s = float(np.trapezoid(inv_rc, h_to_35k))

    # 7. Sustained and Instantaneous Turn Rate at M = 0.8, h = 4,572 m (15,000 ft)
    m_turn = 0.80
    h_turn = 4572.0
    q_turn = float(dynamic_pressure_Pa(m_turn, h_turn))
    v_turn = m_turn * float(speed_of_sound_mps(h_turn))
    cl_max_turn = float(compute_cl_max_mach(geom, vlm, high_lift, m_turn))

    n_aero_max = (q_turn * geom.wing.area_m2 * cl_max_turn) / w_combat_n
    n_inst = min(n_aero_max, geom.design_load_factor_g)
    if n_inst > 1.0:
        inst_turn_dps = math.degrees((G0_MPS2 * math.sqrt(n_inst ** 2 - 1.0)) / v_turn)
    else:
        inst_turn_dps = 0.0

    t_turn = float(
        compute_installed_thrust_N(
            geom, eng_deck, m_turn, h_turn, throttle=1.0, ab=geom.afterburner, tech_context=tech_context
        )
    )
    # Solve by bisection for maximum sustained load factor n_sus in [1.0, n_inst] where D(n) <= T_turn
    lo_n, hi_n = 1.0, max(n_inst, 1.0)
    cl_1g_turn = w_combat_n / max(q_turn * geom.wing.area_m2, 1.0)
    d_1g_turn = (
        q_turn
        * geom.wing.area_m2
        * float(
            compute_total_drag_cd(
                geom, vlm, wave_summary, m_turn, h_turn, cl_1g_turn, tech_context=tech_context, include_combat_stores=True
            )
        )
    )
    if t_turn <= d_1g_turn or n_inst <= 1.0:
        sust_turn_dps = 0.0
    else:
        for _ in range(16):
            mid_n = 0.5 * (lo_n + hi_n)
            cl_n = mid_n * cl_1g_turn
            cd_n = float(
                compute_total_drag_cd(
                    geom, vlm, wave_summary, m_turn, h_turn, cl_n, tech_context=tech_context, include_combat_stores=True
                )
            )
            if q_turn * geom.wing.area_m2 * cd_n <= t_turn:
                lo_n = mid_n
            else:
                hi_n = mid_n
        n_sus = 0.5 * (lo_n + hi_n)
        sust_turn_dps = math.degrees((G0_MPS2 * math.sqrt(max(n_sus ** 2 - 1.0, 0.0))) / v_turn)

    # 8. Mission Combat Radius & Ferry Range
    combat_radius_m, radius_clean_m, radius_tanks_m, ferry_range_m = _compute_mission_radius_and_ferry(
        geom, vlm, wave_summary, mass, eng_deck, tech_context=tech_context
    )

    # 9. Takeoff, Landing, Stall Speed, and Carrier Suitability
    (
        stall_speed_mps,
        takeoff_distance_m,
        takeoff_ground_roll_m,
        landing_distance_m,
        landing_ground_roll_m,
        carrier_suit,
    ) = _compute_takeoff_landing_carrier(
        geom, vlm, wave_summary, high_lift, mass, eng_deck, tech_context=tech_context
    )

    # 10. Subsonic CD0 & (L/D)_max reference metrics
    cd0_m06 = float(compute_cd0_subsonic(geom, 0.60, 10668.0, tech_context=tech_context))
    k_m06 = float(compute_induced_drag_k(geom, vlm, 0.60, tech_context=tech_context))
    ld_max_sub = 1.0 / (2.0 * math.sqrt(max(cd0_m06 * k_m06, 1e-6)))

    # 11. Cost & Maintenance
    unit_cost, dev_cost, maint_mh = _estimate_cost_and_maint(
        geom, mass, eng_deck, max_mach_alt, tech_context=tech_context
    )

    # 12. Diagnostics dictionary for Module 06
    diag = compute_aero_diagnostics(
        geom,
        vlm,
        wave_summary,
        high_lift,
        mass,
        max_mach_sl=max_mach_sl,
        max_mach_alt=max_mach_alt,
        alt_of_max_mach_m=alt_of_max_mach_m,
        tech_context=tech_context,
    )

    return PerformanceReport(
        max_mach_sl=float(max_mach_sl),
        max_mach_alt=float(max_mach_alt),
        alt_of_max_mach_m=float(alt_of_max_mach_m),
        service_ceiling_m=float(service_ceiling_m),
        climb_rate_sl_mps=float(climb_rate_sl_mps),
        time_to_alt_10668m_s=float(time_to_10668m_s),
        sustained_turn_dps_m08_4572m=float(sust_turn_dps),
        instantaneous_turn_dps_m08_4572m=float(inst_turn_dps),
        ps_mps_m09_4572m_1g=float(ps_m09_4572m),
        combat_radius_m=float(combat_radius_m),
        ferry_range_m=float(ferry_range_m),
        takeoff_distance_m=float(takeoff_distance_m),
        landing_distance_m=float(landing_distance_m),
        stall_speed_mps=float(stall_speed_mps),
        max_load_factor_g=float(geom.design_load_factor_g),
        empty_mass_kg=float(mass.empty_mass_kg),
        mtow_kg=float(mass.mtow_kg),
        internal_fuel_kg=float(geom.internal_fuel_kg),
        payload_kg=float(mass.payload_kg),
        thrust_to_weight_combat=float(tw_combat),
        wing_loading_combat_kgm2=float(wl_combat),
        ps_grid=ps_grid_dict,
        unit_flyaway_cost_usd=float(unit_cost),
        dev_cost_usd_estimate=float(dev_cost),
        maint_mh_per_fh=float(maint_mh),
        carrier_suitability=carrier_suit,
        combat_mass_kg=float(mass.combat_mass_kg),
        combat_radius_clean_m=float(radius_clean_m),
        combat_radius_drop_tanks_m=float(radius_tanks_m),
        takeoff_ground_roll_m=float(takeoff_ground_roll_m),
        landing_ground_roll_m=float(landing_ground_roll_m),
        ld_max_subsonic=float(ld_max_sub),
        cd0_subsonic_m06_10668m=float(cd0_m06),
        is_valid=is_valid,
        validation_errors=val_errors,
        validation_warnings=val_warnings,
        mass_breakdown=mass,
        aero_diagnostics=diag,
        geometry=geom,
    )
