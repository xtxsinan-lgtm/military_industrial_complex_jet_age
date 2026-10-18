"""Stub Engine Deck and Historical 1945-1960 Turbojet Catalog for Module 01.

Conforms to the shared `EngineSpec` contract (`00_conventions.md` §4.3):
- `engine.thrust_N(mach, alt_m, throttle, ab)` -> N (supports scalar float or np.ndarray)
- `engine.tsfc(mach, alt_m, throttle, ab)` -> kg/(N*s) (supports scalar float or np.ndarray)
- Static fields: `mass_kg`, `diameter_m`, `length_m`, `unit_cost`, `mtbf_h`, `maint_mh_per_fh`,
  plus `engine_id`, `name`, `mass_flow_kgps`, `dry_thrust_sl_N`, `ab_thrust_sl_N`, `has_afterburner`.

Also defines `TestEngineDeck` with exact analytical formulas used by the C# golden test suite.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Union
import numpy as np

from ..atmosphere import GAMMA_AIR, RHO0_SL_KGM3, T0_SL_K, density_kgm3, temperature_K

NumberOrArray = Union[float, np.ndarray]
LBF_TO_N: float = 4.4482216152605
LB_TO_KG: float = 0.45359237
# 1 (lb/hr)/lbf = (0.45359237 kg / 3600 s) / 4.4482216152605 N = 2.832546e-5 kg/(N*s)
TSFC_LBPH_LBF_TO_SI: float = LB_TO_KG / (3600.0 * LBF_TO_N)


@dataclass(frozen=True)
class StubEngineDeck:
    """Parametric uninstalled turbojet / afterburning turbojet deck (1945-1960)."""

    engine_id: str
    name: str
    dry_thrust_sl_N: float
    ab_thrust_sl_N: float
    has_afterburner: bool
    tsfc_dry_sl: float  # kg/(N*s)
    tsfc_ab_sl: float  # kg/(N*s)
    mass_kg: float
    diameter_m: float
    length_m: float
    mass_flow_kgps: float
    unit_cost: float
    mtbf_h: float
    maint_mh_per_fh: float
    alt_exp_dry: float = 0.78
    alt_exp_ab: float = 0.79
    ram_c1_dry: float = -0.16
    ram_c2_dry: float = 0.22
    ram_c1_ab: float = -0.08
    ram_c2_ab: float = 0.42
    throttle_ratio_tr: float = 1.36  # Compressor inlet total temperature ratio limit theta_0

    def thrust_N(
        self,
        mach: NumberOrArray,
        alt_m: NumberOrArray,
        throttle: float = 1.0,
        ab: bool = False,
    ) -> NumberOrArray:
        """Compute uninstalled net thrust [N] at (mach, alt_m, throttle, ab)."""
        is_scalar = np.ndim(mach) == 0 and np.ndim(alt_m) == 0
        m = np.maximum(np.asarray(mach, dtype=np.float64), 0.0)
        h = np.asarray(alt_m, dtype=np.float64)
        m_b, h_b = np.broadcast_arrays(m, h)

        thr = float(np.clip(throttle, 0.0, 1.0))
        use_ab = bool(ab and self.has_afterburner and self.ab_thrust_sl_N > self.dry_thrust_sl_N)

        sigma = np.asarray(density_kgm3(h_b), dtype=np.float64) / RHO0_SL_KGM3
        T_amb = np.asarray(temperature_K(h_b), dtype=np.float64)
        theta_0 = (T_amb / T0_SL_K) * (1.0 + 0.5 * (GAMMA_AIR - 1.0) * (m_b ** 2))

        # High-Mach compressor / turbine temperature protection above theta_0 = TR (Mattingly Ch. 7 theta-break)
        # Only active at supersonic Mach (M > 1.0) so subsonic sea-level climb is never throttled back
        tr_excess = np.where(m_b > 1.0, np.maximum(theta_0 - self.throttle_ratio_tr, 0.0), 0.0)
        temp_protect = np.exp(-42.0 * (tr_excess ** 2))

        # Stratospheric low-Reynolds-number compressor & combustor efficiency droop above 11 km
        strat_excess = np.maximum(h_b - 11000.0, 0.0) / 4600.0
        strat_factor = np.exp(-0.22 * (strat_excess ** 2))

        if use_ab:
            lapse = (sigma ** self.alt_exp_ab) * (1.0 + self.ram_c1_ab * m_b + self.ram_c2_ab * (m_b ** 2))
            t_max = self.ab_thrust_sl_N * np.maximum(lapse, 0.05) * temp_protect * strat_factor
        else:
            lapse = (sigma ** self.alt_exp_dry) * (1.0 + self.ram_c1_dry * m_b + self.ram_c2_dry * (m_b ** 2))
            t_max = self.dry_thrust_sl_N * np.maximum(lapse, 0.05) * temp_protect * strat_factor

        t_out = thr * t_max
        return float(t_out) if is_scalar else t_out

    def tsfc(
        self,
        mach: NumberOrArray,
        alt_m: NumberOrArray,
        throttle: float = 1.0,
        ab: bool = False,
    ) -> NumberOrArray:
        """Compute thrust-specific fuel consumption [kg/(N*s)] at (mach, alt_m, throttle, ab)."""
        is_scalar = np.ndim(mach) == 0 and np.ndim(alt_m) == 0
        m = np.maximum(np.asarray(mach, dtype=np.float64), 0.0)
        h = np.asarray(alt_m, dtype=np.float64)
        m_b, h_b = np.broadcast_arrays(m, h)

        thr = float(np.clip(throttle, 0.05, 1.0))
        use_ab = bool(ab and self.has_afterburner and self.ab_thrust_sl_N > self.dry_thrust_sl_N)

        T_amb = np.asarray(temperature_K(h_b), dtype=np.float64)
        sqrt_theta = np.sqrt(T_amb / T0_SL_K)

        # Part-throttle SFC bucket (minimum around throttle = 0.82, rising at very low throttle)
        part_thr_factor = 1.0 - 0.04 * (1.0 - thr) + 0.18 * (max(0.65 - thr, 0.0) ** 2)

        if use_ab:
            sfc = self.tsfc_ab_sl * sqrt_theta * (1.0 + 0.18 * m_b)
        else:
            sfc = self.tsfc_dry_sl * sqrt_theta * (1.0 + 0.26 * m_b) * part_thr_factor

        return float(sfc) if is_scalar else sfc


# Historical 1945-1960 US & Soviet Fighter Engine Catalog (sources: Jane's All the World's Aircraft,
# USAF Standard Aircraft Characteristics sheets, Loftin NASA SP-468, Wilkinson "Aircraft Engines of the World")
HISTORICAL_ENGINES: Dict[str, StubEngineDeck] = {
    "J33-A-9": StubEngineDeck(
        engine_id="J33-A-9",
        name="Allison J33-A-9/17 (P-80A)",
        dry_thrust_sl_N=3850.0 * LBF_TO_N,
        ab_thrust_sl_N=3850.0 * LBF_TO_N,
        has_afterburner=False,
        tsfc_dry_sl=1.14 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=1.14 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=825.0,
        diameter_m=1.28,
        length_m=2.62,
        mass_flow_kgps=34.5,
        unit_cost=42000.0,
        mtbf_h=120.0,
        maint_mh_per_fh=4.5,
        alt_exp_dry=0.88,
        throttle_ratio_tr=1.00,
    ),
    "J35-A-29": StubEngineDeck(
        engine_id="J35-A-29",
        name="Allison J35-A-29 (F-84G)",
        dry_thrust_sl_N=5600.0 * LBF_TO_N,
        ab_thrust_sl_N=5600.0 * LBF_TO_N,
        has_afterburner=False,
        tsfc_dry_sl=1.08 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=1.08 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=1025.0,
        diameter_m=0.94,
        length_m=3.71,
        mass_flow_kgps=43.0,
        unit_cost=48000.0,
        mtbf_h=160.0,
        maint_mh_per_fh=4.2,
        alt_exp_dry=0.88,
        throttle_ratio_tr=1.00,
    ),
    "J47-GE-13": StubEngineDeck(
        engine_id="J47-GE-13",
        name="General Electric J47-GE-13 (F-86A)",
        dry_thrust_sl_N=5200.0 * LBF_TO_N,
        ab_thrust_sl_N=5200.0 * LBF_TO_N,
        has_afterburner=False,
        tsfc_dry_sl=1.06 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=1.06 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=1145.0,
        diameter_m=0.93,
        length_m=3.66,
        mass_flow_kgps=42.5,
        unit_cost=50000.0,
        mtbf_h=200.0,
        maint_mh_per_fh=3.8,
        alt_exp_dry=0.78,
        throttle_ratio_tr=1.00,
    ),
    "J47-GE-27": StubEngineDeck(
        engine_id="J47-GE-27",
        name="General Electric J47-GE-27 (F-86F)",
        dry_thrust_sl_N=5910.0 * LBF_TO_N,
        ab_thrust_sl_N=5910.0 * LBF_TO_N,
        has_afterburner=False,
        tsfc_dry_sl=1.03 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=1.03 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=1180.0,
        diameter_m=0.93,
        length_m=3.66,
        mass_flow_kgps=46.0,
        unit_cost=54000.0,
        mtbf_h=240.0,
        maint_mh_per_fh=3.6,
        alt_exp_dry=0.78,
        throttle_ratio_tr=1.00,
    ),
    "VK-1": StubEngineDeck(
        engine_id="VK-1",
        name="Klimov VK-1 (MiG-15bis)",
        dry_thrust_sl_N=5953.0 * LBF_TO_N,
        ab_thrust_sl_N=5953.0 * LBF_TO_N,
        has_afterburner=False,
        tsfc_dry_sl=1.07 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=1.07 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=872.0,
        diameter_m=1.30,
        length_m=2.60,
        mass_flow_kgps=45.0,
        unit_cost=45000.0,
        mtbf_h=150.0,
        maint_mh_per_fh=4.0,
        alt_exp_dry=0.76,
        throttle_ratio_tr=1.00,
    ),
    "J35-A-35": StubEngineDeck(
        engine_id="J35-A-35",
        name="Allison J35-A-35 (F-89D)",
        dry_thrust_sl_N=5440.0 * LBF_TO_N,
        ab_thrust_sl_N=7200.0 * LBF_TO_N,
        has_afterburner=True,
        tsfc_dry_sl=1.08 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=2.15 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=1290.0,
        diameter_m=0.94,
        length_m=4.95,
        mass_flow_kgps=43.0,
        unit_cost=68000.0,
        mtbf_h=150.0,
        maint_mh_per_fh=5.0,
        alt_exp_dry=0.78,
        alt_exp_ab=0.80,
        throttle_ratio_tr=0.96,
    ),
    "J57-P-7": StubEngineDeck(
        engine_id="J57-P-7",
        name="Pratt & Whitney J57-P-7 (F-100A)",
        dry_thrust_sl_N=9700.0 * LBF_TO_N,
        ab_thrust_sl_N=14800.0 * LBF_TO_N,
        has_afterburner=True,
        tsfc_dry_sl=0.82 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=2.05 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=2220.0,
        diameter_m=1.02,
        length_m=6.20,
        mass_flow_kgps=75.0,
        unit_cost=135000.0,
        mtbf_h=180.0,
        maint_mh_per_fh=5.5,
        alt_exp_dry=0.78,
        alt_exp_ab=0.78,
        throttle_ratio_tr=0.96,
    ),
    "J57-P-21": StubEngineDeck(
        engine_id="J57-P-21",
        name="Pratt & Whitney J57-P-21 (F-100D)",
        dry_thrust_sl_N=10200.0 * LBF_TO_N,
        ab_thrust_sl_N=16000.0 * LBF_TO_N,
        has_afterburner=True,
        tsfc_dry_sl=0.80 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=2.02 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=2340.0,
        diameter_m=1.02,
        length_m=6.25,
        mass_flow_kgps=76.5,
        unit_cost=142000.0,
        mtbf_h=200.0,
        maint_mh_per_fh=5.4,
        alt_exp_dry=0.78,
        alt_exp_ab=0.78,
        throttle_ratio_tr=0.98,
    ),
    "J57-P-11": StubEngineDeck(
        engine_id="J57-P-11",
        name="Pratt & Whitney J57-P-11 (YF-102)",
        dry_thrust_sl_N=9700.0 * LBF_TO_N,
        ab_thrust_sl_N=14500.0 * LBF_TO_N,
        has_afterburner=True,
        tsfc_dry_sl=0.83 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=2.08 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=2180.0,
        diameter_m=1.02,
        length_m=6.15,
        mass_flow_kgps=74.0,
        unit_cost=132000.0,
        mtbf_h=175.0,
        maint_mh_per_fh=5.6,
        alt_exp_dry=0.80,
        alt_exp_ab=0.82,
        ram_c2_ab=0.22,
        throttle_ratio_tr=0.88,
    ),
    "J57-P-23": StubEngineDeck(
        engine_id="J57-P-23",
        name="Pratt & Whitney J57-P-23 (F-102A)",
        dry_thrust_sl_N=10200.0 * LBF_TO_N,
        ab_thrust_sl_N=16000.0 * LBF_TO_N,
        has_afterburner=True,
        tsfc_dry_sl=0.81 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=2.04 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=2290.0,
        diameter_m=1.02,
        length_m=6.20,
        mass_flow_kgps=76.5,
        unit_cost=140000.0,
        mtbf_h=195.0,
        maint_mh_per_fh=5.5,
        alt_exp_dry=0.77,
        alt_exp_ab=0.76,
        ram_c2_ab=0.35,
        throttle_ratio_tr=0.895,
    ),
    "J57-P-8B": StubEngineDeck(
        engine_id="J57-P-8B",
        name="Pratt & Whitney J57-P-8B (F4D-1 Skyray)",
        dry_thrust_sl_N=10200.0 * LBF_TO_N,
        ab_thrust_sl_N=16000.0 * LBF_TO_N,
        has_afterburner=True,
        tsfc_dry_sl=0.81 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=2.05 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=2250.0,
        diameter_m=1.02,
        length_m=6.20,
        mass_flow_kgps=76.0,
        unit_cost=138000.0,
        mtbf_h=185.0,
        maint_mh_per_fh=5.6,
        alt_exp_dry=0.77,
        alt_exp_ab=0.76,
        ram_c2_ab=0.32,
        throttle_ratio_tr=0.91,
    ),
    "J57-P-16": StubEngineDeck(
        engine_id="J57-P-16",
        name="Pratt & Whitney J57-P-16 (F8U-1 Crusader)",
        dry_thrust_sl_N=10700.0 * LBF_TO_N,
        ab_thrust_sl_N=18000.0 * LBF_TO_N,
        has_afterburner=True,
        tsfc_dry_sl=0.80 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=2.05 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=2295.0,
        diameter_m=1.02,
        length_m=6.30,
        mass_flow_kgps=78.0,
        unit_cost=148000.0,
        mtbf_h=205.0,
        maint_mh_per_fh=5.4,
        alt_exp_dry=0.75,
        alt_exp_ab=0.73,
        throttle_ratio_tr=1.10,
    ),
    "J57-P-13": StubEngineDeck(
        engine_id="J57-P-13",
        name="Pratt & Whitney J57-P-13 (F-101A Voodoo)",
        dry_thrust_sl_N=10200.0 * LBF_TO_N,
        ab_thrust_sl_N=15000.0 * LBF_TO_N,
        has_afterburner=True,
        tsfc_dry_sl=0.80 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=2.02 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=2270.0,
        diameter_m=1.02,
        length_m=6.20,
        mass_flow_kgps=76.0,
        unit_cost=140000.0,
        mtbf_h=200.0,
        maint_mh_per_fh=5.4,
        alt_exp_dry=0.74,
        alt_exp_ab=0.71,
        throttle_ratio_tr=1.02,
    ),
    "J79-GE-3A": StubEngineDeck(
        engine_id="J79-GE-3A",
        name="General Electric J79-GE-3A (F-104A Starfighter)",
        dry_thrust_sl_N=9600.0 * LBF_TO_N,
        ab_thrust_sl_N=14800.0 * LBF_TO_N,
        has_afterburner=True,
        tsfc_dry_sl=0.84 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=1.97 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=1665.0,
        diameter_m=0.97,
        length_m=5.28,
        mass_flow_kgps=73.5,
        unit_cost=155000.0,
        mtbf_h=190.0,
        maint_mh_per_fh=5.8,
        alt_exp_dry=0.72,
        alt_exp_ab=0.68,
        ram_c1_ab=-0.05,
        ram_c2_ab=0.45,
        throttle_ratio_tr=1.26,
    ),
    "J75-P-5": StubEngineDeck(
        engine_id="J75-P-5",
        name="Pratt & Whitney J75-P-5 (F-105B Thunderchief)",
        dry_thrust_sl_N=16100.0 * LBF_TO_N,
        ab_thrust_sl_N=23500.0 * LBF_TO_N,
        has_afterburner=True,
        tsfc_dry_sl=0.82 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=2.05 * TSFC_LBPH_LBF_TO_SI,
        mass_kg=2670.0,
        diameter_m=1.09,
        length_m=6.55,
        mass_flow_kgps=115.0,
        unit_cost=210000.0,
        mtbf_h=185.0,
        maint_mh_per_fh=6.5,
        alt_exp_dry=0.73,
        alt_exp_ab=0.70,
        ram_c1_ab=-0.06,
        ram_c2_ab=0.44,
        throttle_ratio_tr=1.27,
    ),
}

# Deterministic analytical test engines for C# golden vector verification
TEST_ENGINE_DRY = HISTORICAL_ENGINES["J47-GE-27"]
TEST_ENGINE_AB = HISTORICAL_ENGINES["J57-P-23"]


def resolve_engine(engine_or_id: Union[str, Any, None], default_id: str = "J47-GE-27") -> Any:
    """Resolve an engine object, engine ID string, or dict specification into an EngineSpec deck."""
    if engine_or_id is not None and hasattr(engine_or_id, "thrust_N") and hasattr(engine_or_id, "tsfc"):
        return engine_or_id

    if isinstance(engine_or_id, dict):
        eid = str(engine_or_id.get("engine_id", engine_or_id.get("id", default_id)))
        if eid in HISTORICAL_ENGINES and "dry_thrust_sl_N" not in engine_or_id:
            return HISTORICAL_ENGINES[eid]
        dry_n = float(engine_or_id.get("dry_thrust_sl_N", 26290.0))
        ab_n = float(engine_or_id.get("ab_thrust_sl_N", dry_n))
        return StubEngineDeck(
            engine_id=eid,
            name=str(engine_or_id.get("name", eid)),
            dry_thrust_sl_N=dry_n,
            ab_thrust_sl_N=ab_n,
            has_afterburner=bool(engine_or_id.get("has_afterburner", ab_n > dry_n * 1.05)),
            tsfc_dry_sl=float(engine_or_id.get("tsfc_dry_sl", 1.03 * TSFC_LBPH_LBF_TO_SI)),
            tsfc_ab_sl=float(engine_or_id.get("tsfc_ab_sl", 2.04 * TSFC_LBPH_LBF_TO_SI)),
            mass_kg=float(engine_or_id.get("mass_kg", 1180.0)),
            diameter_m=float(engine_or_id.get("diameter_m", 0.95)),
            length_m=float(engine_or_id.get("length_m", 3.8)),
            mass_flow_kgps=float(engine_or_id.get("mass_flow_kgps", dry_n / 570.0)),
            unit_cost=float(engine_or_id.get("unit_cost", 60000.0)),
            mtbf_h=float(engine_or_id.get("mtbf_h", 200.0)),
            maint_mh_per_fh=float(engine_or_id.get("maint_mh_per_fh", 4.0)),
        )

    eid_str = str(engine_or_id if engine_or_id is not None else default_id)
    # Check if Module 02 (`sim.mic.engine`) provides a loader first
    try:
        from .. import engine as mod_engine  # type: ignore

        if hasattr(mod_engine, "get_engine_deck"):
            deck = mod_engine.get_engine_deck(eid_str)
            if deck is not None:
                return deck
    except Exception:
        pass

    if eid_str in HISTORICAL_ENGINES:
        return HISTORICAL_ENGINES[eid_str]
    return HISTORICAL_ENGINES[default_id]
