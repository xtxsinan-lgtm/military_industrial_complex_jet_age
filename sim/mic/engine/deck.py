"""EngineSpec deck generator and bilinear/trilinear lookup table (contract §4.3)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .cycle import (
    EngineDesignInput,
    OnDesignReference,
    evaluate_off_design_point,
    solve_on_design,
)
from .sizing import estimate_physical_metrics
from .tuning import load_engine_tuning


def _find_bracket(grid: Sequence[float], val: float) -> Tuple[int, int, float]:
    """Return (i0, i1, frac) for clamping linear interpolation on strictly increasing 1D grid."""
    n = len(grid)
    if val <= grid[0]:
        return 0, 0, 0.0
    if val >= grid[-1]:
        return n - 1, n - 1, 0.0
    # Binary search
    lo = 0
    hi = n - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if grid[mid] <= val:
            lo = mid
        else:
            hi = mid
    span = grid[hi] - grid[lo]
    frac = (val - grid[lo]) / span if span > 1e-12 else 0.0
    return lo, hi, frac


def _bilinear_2d(
    table: np.ndarray,
    x_grid: Sequence[float],
    y_grid: Sequence[float],
    x: float,
    y: float,
) -> float:
    """Bilinear interpolation on 2D array table[ix, iy]."""
    ix0, ix1, fx = _find_bracket(x_grid, x)
    iy0, iy1, fy = _find_bracket(y_grid, y)
    v00 = float(table[ix0, iy0])
    v01 = float(table[ix0, iy1])
    v10 = float(table[ix1, iy0])
    v11 = float(table[ix1, iy1])
    v0 = v00 + fy * (v01 - v00)
    v1 = v10 + fy * (v11 - v10)
    return v0 + fx * (v1 - v0)


def _trilinear_3d(
    table: np.ndarray,
    x_grid: Sequence[float],
    y_grid: Sequence[float],
    z_grid: Sequence[float],
    x: float,
    y: float,
    z: float,
) -> float:
    """Bilinear in (mach, alt_m) + linear in throttle on 3D array table[ix, iy, iz]."""
    ix0, ix1, fx = _find_bracket(x_grid, x)
    iy0, iy1, fy = _find_bracket(y_grid, y)
    iz0, iz1, fz = _find_bracket(z_grid, z)

    def _interp_xy(iz: int) -> float:
        v00 = float(table[ix0, iy0, iz])
        v01 = float(table[ix0, iy1, iz])
        v10 = float(table[ix1, iy0, iz])
        v11 = float(table[ix1, iy1, iz])
        v0 = v00 + fy * (v01 - v00)
        v1 = v10 + fy * (v11 - v10)
        return v0 + fx * (v1 - v0)

    if iz0 == iz1:
        return _interp_xy(iz0)
    vz0 = _interp_xy(iz0)
    vz1 = _interp_xy(iz1)
    return vz0 + fz * (vz1 - vz0)


@dataclass
class EngineDeckTables:
    """Precomputed Mach x Alt x Throttle lookup tables for fast simulation queries."""

    mach_grid: List[float]
    alt_m_grid: List[float]
    dry_throttle_grid: List[float]
    ab_throttle_grid: List[float]
    # 2D arrays [n_mach, n_alt]
    max_dry_thrust_N: np.ndarray
    max_ab_thrust_N: np.ndarray
    mil_fuel_flow_kgps: np.ndarray
    # 3D arrays [n_mach, n_alt, n_thr]
    dry_tsfc: np.ndarray
    ab_tsfc: np.ndarray

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mach_grid": list(self.mach_grid),
            "alt_m_grid": list(self.alt_m_grid),
            "dry_throttle_grid": list(self.dry_throttle_grid),
            "ab_throttle_grid": list(self.ab_throttle_grid),
            "max_dry_thrust_N": self.max_dry_thrust_N.tolist(),
            "max_ab_thrust_N": self.max_ab_thrust_N.tolist(),
            "mil_fuel_flow_kgps": self.mil_fuel_flow_kgps.tolist(),
            "dry_tsfc": self.dry_tsfc.tolist(),
            "ab_tsfc": self.ab_tsfc.tolist(),
        }


@dataclass
class EngineSpec:
    """Authoritative EngineSpec contract per 00_conventions.md §4.3.

    Exposes:
    - engine.thrust_N(mach, alt_m, throttle, ab) -> float [N]
    - engine.tsfc(mach, alt_m, throttle, ab) -> float [kg/(N*s)]
    - static fields: mass_kg, diameter_m, length_m, unit_cost, mtbf_h, maint_mh_per_fh
    """

    engine_id: str
    name: str
    mass_kg: float
    diameter_m: float
    length_m: float
    unit_cost: float
    mtbf_h: float
    maint_mh_per_fh: float
    has_afterburner: bool = False
    compressor_type: str = "axial"
    spools: int = 1
    variable_stators: bool = False
    sls_dry_thrust_N: float = 0.0
    sls_ab_thrust_N: float = 0.0
    sls_dry_tsfc: float = 0.0
    sls_ab_tsfc: float = 0.0
    design_input: Optional[EngineDesignInput] = None
    on_design_ref: Optional[OnDesignReference] = None
    deck: Optional[EngineDeckTables] = None
    inlet_config: Dict[str, Any] = field(
        default_factory=lambda: {
            "inlet_type": "mil_spec",
            "inlet_location": "nose",
            "variable_inlet": False,
            "spike_inlet": False,
            "recovery_bonus": 0.0,
        }
    )

    def thrust_N(
        self,
        mach: float,
        alt_m: float,
        throttle: float = 1.0,
        ab: bool = False,
    ) -> float:
        """Return net thrust [N] at (mach, alt_m, throttle in [0,1], ab:bool).

        - Dry (ab=False): thrust_N = throttle * F_dry_max(mach, alt_m)
        - Afterburning (ab=True and has_afterburner):
          thrust_N = F_dry_max + throttle * (F_ab_max - F_dry_max)
          (if engine has no afterburner, ab=True is treated as ab=False).
        """
        thr = max(0.0, min(1.0, float(throttle)))
        m = max(0.0, float(mach))
        h = max(0.0, float(alt_m))

        if self.deck is not None:
            f_dry = _bilinear_2d(
                self.deck.max_dry_thrust_N,
                self.deck.mach_grid,
                self.deck.alt_m_grid,
                m,
                h,
            )
            if ab and self.has_afterburner:
                f_ab = _bilinear_2d(
                    self.deck.max_ab_thrust_N,
                    self.deck.mach_grid,
                    self.deck.alt_m_grid,
                    m,
                    h,
                )
                return max(0.0, f_dry + thr * (f_ab - f_dry))
            return max(0.0, thr * f_dry)

        if self.on_design_ref is not None:
            pt = evaluate_off_design_point(
                self.on_design_ref,
                mach=m,
                alt_m=h,
                throttle=thr,
                ab=ab and self.has_afterburner,
                **self.inlet_config,
            )
            return pt.thrust_N

        raise RuntimeError(f"EngineSpec '{self.engine_id}' has neither deck nor on_design_ref.")

    def tsfc(
        self,
        mach: float,
        alt_m: float,
        throttle: float = 1.0,
        ab: bool = False,
    ) -> float:
        """Return thrust specific fuel consumption [kg/(N*s)] at (mach, alt_m, throttle, ab)."""
        thr = max(0.0, min(1.0, float(throttle)))
        m = max(0.0, float(mach))
        h = max(0.0, float(alt_m))

        if self.deck is not None:
            if ab and self.has_afterburner:
                return _trilinear_3d(
                    self.deck.ab_tsfc,
                    self.deck.mach_grid,
                    self.deck.alt_m_grid,
                    self.deck.ab_throttle_grid,
                    m,
                    h,
                    thr,
                )
            if thr >= self.deck.dry_throttle_grid[0]:
                return _trilinear_3d(
                    self.deck.dry_tsfc,
                    self.deck.mach_grid,
                    self.deck.alt_m_grid,
                    self.deck.dry_throttle_grid,
                    m,
                    h,
                    thr,
                )
            # Below dry_throttle_grid[0] (0.10): interpolate fuel flow to idle and divide by clamped thrust
            tsfc_10 = _trilinear_3d(
                self.deck.dry_tsfc,
                self.deck.mach_grid,
                self.deck.alt_m_grid,
                self.deck.dry_throttle_grid,
                m,
                h,
                self.deck.dry_throttle_grid[0],
            )
            f_dry_max = _bilinear_2d(
                self.deck.max_dry_thrust_N,
                self.deck.mach_grid,
                self.deck.alt_m_grid,
                m,
                h,
            )
            ff_mil = _bilinear_2d(
                self.deck.mil_fuel_flow_kgps,
                self.deck.mach_grid,
                self.deck.alt_m_grid,
                m,
                h,
            )
            ff_10 = tsfc_10 * (0.10 * f_dry_max)
            idle_ff = 0.14 * ff_mil
            ff = idle_ff + (thr / 0.10) * max(0.0, ff_10 - idle_ff)
            denom = max(0.05 * f_dry_max, thr * f_dry_max, 1.0)
            return ff / denom

        if self.on_design_ref is not None:
            pt = evaluate_off_design_point(
                self.on_design_ref,
                mach=m,
                alt_m=h,
                throttle=thr,
                ab=ab and self.has_afterburner,
                **self.inlet_config,
            )
            return pt.tsfc_kg_per_Ns

        raise RuntimeError(f"EngineSpec '{self.engine_id}' has neither deck nor on_design_ref.")

    def fuel_flow_kgps(
        self,
        mach: float,
        alt_m: float,
        throttle: float = 1.0,
        ab: bool = False,
    ) -> float:
        """Return fuel mass flow rate [kg/s] at (mach, alt_m, throttle, ab)."""
        thr = max(0.0, min(1.0, float(throttle)))
        if not (ab and self.has_afterburner) and thr < 0.10 and self.deck is not None:
            m = max(0.0, float(mach))
            h = max(0.0, float(alt_m))
            tsfc_10 = self.tsfc(m, h, 0.10, ab=False)
            f_dry_max = self.thrust_N(m, h, 1.0, ab=False)
            ff_mil = _bilinear_2d(
                self.deck.mil_fuel_flow_kgps,
                self.deck.mach_grid,
                self.deck.alt_m_grid,
                m,
                h,
            )
            ff_10 = tsfc_10 * (0.10 * f_dry_max)
            idle_ff = 0.14 * ff_mil
            return idle_ff + (thr / 0.10) * max(0.0, ff_10 - idle_ff)
        return self.thrust_N(mach, alt_m, thr, ab) * self.tsfc(mach, alt_m, thr, ab)


def build_deck_tables(
    ref: OnDesignReference,
    inlet_type: str = "mil_spec",
    inlet_location: str = "nose",
    variable_inlet: bool = False,
    spike_inlet: bool = False,
    recovery_bonus: float = 0.0,
    uninstalled_bellmouth: bool = False,
    tuning: Optional[Dict[str, Any]] = None,
) -> EngineDeckTables:
    """Generate Mach x Alt x Throttle performance lookup tables for an OnDesignReference."""
    t = tuning or load_engine_tuning()
    grid_cfg = t["deck_grid"]
    mach_grid = [float(x) for x in grid_cfg["mach_grid"]]
    alt_grid = [float(x) for x in grid_cfg["alt_m_grid"]]
    dry_thr_grid = [float(x) for x in grid_cfg["dry_throttle_grid"]]
    ab_thr_grid = [float(x) for x in grid_cfg["ab_throttle_grid"]]

    nm = len(mach_grid)
    na = len(alt_grid)
    ndt = len(dry_thr_grid)
    nat = len(ab_thr_grid)

    max_dry = np.zeros((nm, na), dtype=np.float64)
    max_ab = np.zeros((nm, na), dtype=np.float64)
    mil_ff = np.zeros((nm, na), dtype=np.float64)
    dry_tsfc = np.zeros((nm, na, ndt), dtype=np.float64)
    ab_tsfc = np.zeros((nm, na, nat), dtype=np.float64)

    has_ab = bool(ref.design.has_afterburner and ref.design.ab_temp_K > ref.design.tit_K)

    for im, m in enumerate(mach_grid):
        for ia, h in enumerate(alt_grid):
            mil_pt = evaluate_off_design_point(
                ref,
                mach=m,
                alt_m=h,
                throttle=1.0,
                ab=False,
                inlet_type=inlet_type,
                inlet_location=inlet_location,
                variable_inlet=variable_inlet,
                spike_inlet=spike_inlet,
                recovery_bonus=recovery_bonus,
                uninstalled_bellmouth=uninstalled_bellmouth,
                tuning=t,
            )
            max_dry[im, ia] = mil_pt.thrust_N
            mil_ff[im, ia] = mil_pt.fuel_flow_kgps

            for it, thr in enumerate(dry_thr_grid):
                if abs(thr - 1.0) < 1e-9:
                    dry_tsfc[im, ia, it] = mil_pt.tsfc_kg_per_Ns
                else:
                    pt = evaluate_off_design_point(
                        ref,
                        mach=m,
                        alt_m=h,
                        throttle=thr,
                        ab=False,
                        inlet_type=inlet_type,
                        inlet_location=inlet_location,
                        variable_inlet=variable_inlet,
                        spike_inlet=spike_inlet,
                        recovery_bonus=recovery_bonus,
                        uninstalled_bellmouth=uninstalled_bellmouth,
                        tuning=t,
                    )
                    dry_tsfc[im, ia, it] = pt.tsfc_kg_per_Ns

            if has_ab:
                ab_max_pt = evaluate_off_design_point(
                    ref,
                    mach=m,
                    alt_m=h,
                    throttle=1.0,
                    ab=True,
                    inlet_type=inlet_type,
                    inlet_location=inlet_location,
                    variable_inlet=variable_inlet,
                    spike_inlet=spike_inlet,
                    recovery_bonus=recovery_bonus,
                    uninstalled_bellmouth=uninstalled_bellmouth,
                    tuning=t,
                )
                max_ab[im, ia] = ab_max_pt.thrust_N
                for it, thr in enumerate(ab_thr_grid):
                    if abs(thr - 1.0) < 1e-9:
                        ab_tsfc[im, ia, it] = ab_max_pt.tsfc_kg_per_Ns
                    elif abs(thr - 0.0) < 1e-9:
                        ab_tsfc[im, ia, it] = mil_pt.tsfc_kg_per_Ns
                    else:
                        pt = evaluate_off_design_point(
                            ref,
                            mach=m,
                            alt_m=h,
                            throttle=thr,
                            ab=True,
                            inlet_type=inlet_type,
                            inlet_location=inlet_location,
                            variable_inlet=variable_inlet,
                            spike_inlet=spike_inlet,
                            recovery_bonus=recovery_bonus,
                            uninstalled_bellmouth=uninstalled_bellmouth,
                            tuning=t,
                        )
                        ab_tsfc[im, ia, it] = pt.tsfc_kg_per_Ns
            else:
                max_ab[im, ia] = mil_pt.thrust_N
                ab_tsfc[im, ia, :] = mil_pt.tsfc_kg_per_Ns

    return EngineDeckTables(
        mach_grid=mach_grid,
        alt_m_grid=alt_grid,
        dry_throttle_grid=dry_thr_grid,
        ab_throttle_grid=ab_thr_grid,
        max_dry_thrust_N=max_dry,
        max_ab_thrust_N=max_ab,
        mil_fuel_flow_kgps=mil_ff,
        dry_tsfc=dry_tsfc,
        ab_tsfc=ab_tsfc,
    )


def design_engine(
    design: EngineDesignInput,
    build_deck: bool = True,
    inlet_type: str = "mil_spec",
    inlet_location: str = "nose",
    variable_inlet: bool = False,
    spike_inlet: bool = False,
    recovery_bonus: float = 0.0,
    uninstalled_bellmouth: bool = False,
    static_overrides: Optional[Dict[str, float]] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> EngineSpec:
    """Create a complete EngineSpec from parametric EngineDesignInput."""
    t = tuning or load_engine_tuning()
    ref = solve_on_design(design, uninstalled_bellmouth=True, tuning=t)
    phys = estimate_physical_metrics(design, tuning=t)

    deck = (
        build_deck_tables(
            ref,
            inlet_type=inlet_type,
            inlet_location=inlet_location,
            variable_inlet=variable_inlet,
            spike_inlet=spike_inlet,
            recovery_bonus=recovery_bonus,
            uninstalled_bellmouth=uninstalled_bellmouth,
            tuning=t,
        )
        if build_deck
        else None
    )

    ov = static_overrides or {}
    return EngineSpec(
        engine_id=design.engine_id,
        name=design.name,
        mass_kg=float(ov.get("mass_kg", phys.mass_kg)),
        diameter_m=float(ov.get("diameter_m", phys.diameter_m)),
        length_m=float(ov.get("length_m", phys.length_m)),
        unit_cost=float(ov.get("unit_cost", phys.unit_cost_usd)),
        mtbf_h=float(ov.get("mtbf_h", phys.mtbf_h)),
        maint_mh_per_fh=float(ov.get("maint_mh_per_fh", phys.maint_mh_per_fh)),
        has_afterburner=design.has_afterburner,
        compressor_type=design.compressor_type,
        spools=design.spools,
        variable_stators=design.variable_stators,
        sls_dry_thrust_N=ref.sls_dry.thrust_N,
        sls_ab_thrust_N=ref.sls_ab.thrust_N if ref.sls_ab is not None else ref.sls_dry.thrust_N,
        sls_dry_tsfc=ref.sls_dry.tsfc_kg_per_Ns,
        sls_ab_tsfc=(
            ref.sls_ab.tsfc_kg_per_Ns if ref.sls_ab is not None else ref.sls_dry.tsfc_kg_per_Ns
        ),
        design_input=design,
        on_design_ref=ref,
        deck=deck,
        inlet_config={
            "inlet_type": inlet_type,
            "inlet_location": inlet_location,
            "variable_inlet": variable_inlet,
            "spike_inlet": spike_inlet,
            "recovery_bonus": recovery_bonus,
            "uninstalled_bellmouth": uninstalled_bellmouth,
        },
    )
