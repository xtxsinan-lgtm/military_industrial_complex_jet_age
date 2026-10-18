"""Named Engine Vendor AI & Custom Commission Quotes (Locked Decision D9).

Implements Module 07 (`sim/mic/ai/engine_vendor_ai.py`):
- Models the 5 historical US jet engine manufacturers from `engine_makers_us_1945_1960.json`:
  Pratt & Whitney (`pratt_whitney`), General Electric (`general_electric`),
  Allison (`allison`), Westinghouse (`westinghouse`), and Curtiss-Wright (`wright` / `curtiss_wright`).
- Provides the historical off-the-shelf engine release calendar (`get_available_catalog_engines`).
- Generates custom engine commission quotes (`quote_custom_engine(vendor_id, target_spec, date, rng)`)
  applying authentic vendor specialty modifiers:
  * Pratt & Whitney: twin-spool high-OPR low dry TSFC (`0.94x`) and superior durability (`1.25x` MTBF).
  * General Electric: variable-stator high-Mach afterburner thrust (`+4%`), high thermal throttle ratio,
    and fast supersonic development.
  * Allison: GM mass-production economy (`0.90x` unit & dev cost) and low dry SFC (`0.96x`).
  * Westinghouse: compact, lightweight axial compressors (`0.90x` weight, `0.94x` diameter) paired with
    elevated development schedule & thrust shortfall risk (`1.45x` risk, modeling the J40 crisis).
  * Curtiss-Wright (Wright Aeronautical): licensed derivative discount (`42%` dev cost & `35%` schedule
    reduction on derivative/licensed designs like the J65 Sapphire).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date as dt_date
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

from ..econ.inflation import aero_cost_index_1950
from ..perf._stub_engine import (
    HISTORICAL_ENGINES,
    LBF_TO_N,
    StubEngineDeck,
    TSFC_LBPH_LBF_TO_SI,
    resolve_engine,
)
from .tuning import load_ai_tuning

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_ENGINE_MAKERS_PATH = _DATA_DIR / "companies" / "engine_makers_us_1945_1960.json"

VENDOR_ALIASES: Dict[str, str] = {
    "pratt_whitney": "pratt_whitney",
    "pratt & whitney": "pratt_whitney",
    "pratt": "pratt_whitney",
    "pw": "pratt_whitney",
    "p&w": "pratt_whitney",
    "p": "pratt_whitney",
    "general_electric": "general_electric",
    "general electric": "general_electric",
    "ge": "general_electric",
    "allison": "allison",
    "a": "allison",
    "westinghouse": "westinghouse",
    "we": "westinghouse",
    "wright": "wright",
    "curtiss_wright": "wright",
    "curtiss-wright": "wright",
    "wright aeronautical": "wright",
    "w": "wright",
}


def normalize_vendor_id(vendor_id: str) -> str:
    """Resolve any vendor name, code, or alias to its canonical vendor ID."""
    key = str(vendor_id).strip().lower()
    if key in VENDOR_ALIASES:
        return VENDOR_ALIASES[key]
    raise KeyError(f"Unknown engine vendor '{vendor_id}'. Expected one of {sorted(set(VENDOR_ALIASES.values()))}")


def parse_date_to_day_and_year(date_val: Union[str, int, float]) -> Tuple[int, float, str]:
    """Convert an ISO date string ('YYYY-MM-DD') or integer day since 1945-01-01 to (day, year_float, iso_str)."""
    epoch = dt_date(1945, 1, 1)
    if isinstance(date_val, str):
        parts = [int(p) for p in date_val.strip().split("-")]
        d_obj = dt_date(parts[0], parts[1], parts[2] if len(parts) > 2 else 1)
        day_int = (d_obj - epoch).days
        yr_float = 1945.0 + day_int / 365.25
        return day_int, yr_float, d_obj.isoformat()
    day_int = int(round(float(date_val)))
    from datetime import timedelta

    d_obj = epoch + timedelta(days=day_int)
    yr_float = 1945.0 + day_int / 365.25
    return day_int, yr_float, d_obj.isoformat()


def load_engine_makers_data(path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """Load `sim/data/companies/engine_makers_us_1945_1960.json` keyed by canonical `id`."""
    p = Path(path) if path is not None else _ENGINE_MAKERS_PATH
    with open(p, "r", encoding="utf-8") as fh:
        makers = json.load(fh)["engine_makers"]
    return {str(m["id"]): dict(m) for m in makers}


def _rng_normal(rng: Any, mu: float = 0.0, sigma: float = 1.0) -> float:
    """Draw from a deterministic RNG stream if provided, else return `mu`."""
    if rng is None or sigma <= 0.0:
        return float(mu)
    if hasattr(rng, "normal") and callable(rng.normal):
        return float(rng.normal(mu, sigma))
    return float(mu)


@dataclass
class CustomEngineQuote:
    """Structured custom engine development commission quote from a named US engine vendor."""

    quote_id: str
    vendor_id: str
    vendor_name: str
    us_code: str
    specialty: str
    designation: str
    date_quoted: str
    is_derivative: bool
    promised_dry_thrust_sl_N: float
    promised_ab_thrust_sl_N: float
    has_afterburner: bool
    promised_tsfc_dry_sl: float
    promised_tsfc_ab_sl: float
    promised_mass_kg: float
    promised_diameter_m: float
    promised_length_m: float
    promised_mtbf_h: float
    unit_price_usd: float
    total_dev_cost_usd: float
    airframer_commission_fee_usd: float
    promised_delivery_days: int
    development_risk_index: float
    schedule_slip_prob: float
    shortfall_risk_prob: float
    engine_deck: StubEngineDeck
    vendor_notes: str

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quote_id": self.quote_id,
            "vendor_id": self.vendor_id,
            "vendor_name": self.vendor_name,
            "us_code": self.us_code,
            "specialty": self.specialty,
            "designation": self.designation,
            "date_quoted": self.date_quoted,
            "is_derivative": self.is_derivative,
            "promised_dry_thrust_sl_N": round(self.promised_dry_thrust_sl_N, 2),
            "promised_ab_thrust_sl_N": round(self.promised_ab_thrust_sl_N, 2),
            "has_afterburner": self.has_afterburner,
            "promised_tsfc_dry_sl": round(self.promised_tsfc_dry_sl, 8),
            "promised_tsfc_ab_sl": round(self.promised_tsfc_ab_sl, 8),
            "promised_mass_kg": round(self.promised_mass_kg, 2),
            "promised_diameter_m": round(self.promised_diameter_m, 3),
            "promised_length_m": round(self.promised_length_m, 3),
            "promised_mtbf_h": round(self.promised_mtbf_h, 1),
            "unit_price_usd": round(self.unit_price_usd, 2),
            "total_dev_cost_usd": round(self.total_dev_cost_usd, 2),
            "airframer_commission_fee_usd": round(self.airframer_commission_fee_usd, 2),
            "promised_delivery_days": int(self.promised_delivery_days),
            "development_risk_index": round(self.development_risk_index, 4),
            "schedule_slip_prob": round(self.schedule_slip_prob, 4),
            "shortfall_risk_prob": round(self.shortfall_risk_prob, 4),
            "vendor_notes": self.vendor_notes,
        }


def get_available_catalog_engines(
    date: Union[str, int, float],
    vendor_id: Optional[str] = None,
    require_afterburner: Optional[bool] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Return off-the-shelf historical engines released on or before `date`."""
    t = (tuning if tuning is not None else load_ai_tuning())["engine_vendor_ai"]
    q_day, _, _ = parse_date_to_day_and_year(date)
    norm_vendor = normalize_vendor_id(vendor_id) if vendor_id is not None else None

    available: List[Dict[str, Any]] = []
    for entry in t.get("historical_engine_calendar", []):
        avail_day, _, _ = parse_date_to_day_and_year(str(entry["available_date"]))
        if avail_day > q_day:
            continue
        if norm_vendor is not None and normalize_vendor_id(str(entry["vendor_id"])) != norm_vendor:
            continue
        if require_afterburner is not None and bool(entry["has_afterburner"]) != bool(require_afterburner):
            continue
        rec = dict(entry)
        rec["deck"] = build_deck_from_calendar_entry(entry)
        available.append(rec)

    available.sort(key=lambda r: (float(r["ab_thrust_sl_N"]), str(r["engine_id"])))
    return available


def build_deck_from_calendar_entry(entry: Mapping[str, Any]) -> StubEngineDeck:
    """Build or retrieve a `StubEngineDeck` for a calendar entry."""
    eid = str(entry["engine_id"])
    if eid in HISTORICAL_ENGINES:
        return HISTORICAL_ENGINES[eid]
    dry_n = float(entry["dry_thrust_sl_N"])
    ab_n = float(entry["ab_thrust_sl_N"])
    has_ab = bool(entry["has_afterburner"])
    deck = StubEngineDeck(
        engine_id=eid,
        name=f"{entry['vendor_id'].replace('_', ' ').title()} {eid}",
        dry_thrust_sl_N=dry_n,
        ab_thrust_sl_N=ab_n,
        has_afterburner=has_ab,
        tsfc_dry_sl=0.88 * TSFC_LBPH_LBF_TO_SI,
        tsfc_ab_sl=(2.05 if has_ab else 0.88) * TSFC_LBPH_LBF_TO_SI,
        mass_kg=float(entry["mass_kg"]),
        diameter_m=float(entry["diameter_m"]),
        length_m=float(entry["length_m"]),
        mass_flow_kgps=dry_n / 580.0,
        unit_cost=float(entry["unit_cost_usd"]),
        mtbf_h=190.0,
        maint_mh_per_fh=5.0 if has_ab else 3.8,
        throttle_ratio_tr=1.08 if has_ab else 1.00,
    )
    HISTORICAL_ENGINES[eid] = deck
    return deck


def quote_custom_engine(
    vendor_id: str,
    target_spec: Mapping[str, Any],
    date: Union[str, int, float],
    rng: Any = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> CustomEngineQuote:
    """Generate a custom engine commission quote from one of the 5 named US engine vendors (D9).

    Applies vendor specialty traits, era thermodynamic limits, derivative discounts, and
    returns a `CustomEngineQuote` with a callable `EngineSpec` deck (`quote.engine_deck`).
    """
    t = (tuning if tuning is not None else load_ai_tuning())["engine_vendor_ai"]
    v_id = normalize_vendor_id(vendor_id)
    v_prof = dict(t["vendor_profiles"][v_id])
    makers = load_engine_makers_data()
    maker_rec = makers.get(v_id, {})

    q_day, q_year, q_iso = parse_date_to_day_and_year(date)
    yr_int = max(1945, min(1960, int(math.floor(q_year))))
    idx_aero = aero_cost_index_1950(yr_int)

    # Extract requested target parameters
    req_dry_N = float(
        target_spec.get(
            "target_thrust_dry_N",
            target_spec.get("dry_thrust_sl_N", 35000.0),
        )
    )
    req_dry_N = max(8000.0, min(140000.0, req_dry_N))
    has_ab = bool(target_spec.get("afterburner", target_spec.get("has_afterburner", q_year >= 1949.0)))
    default_ab_ratio = 1.46 if q_year < 1952.0 else 1.54
    req_ab_N = float(
        target_spec.get(
            "target_thrust_ab_N",
            target_spec.get("ab_thrust_sl_N", req_dry_N * (default_ab_ratio if has_ab else 1.0)),
        )
    )
    if not has_ab:
        req_ab_N = req_dry_N
    else:
        req_ab_N = max(req_dry_N * 1.25, min(req_dry_N * 1.70, req_ab_N))

    is_derivative = bool(target_spec.get("is_derivative", bool(target_spec.get("base_engine_id"))))
    target_mach = float(target_spec.get("target_mach", 1.6 if has_ab and q_year >= 1952 else 0.95))
    customer = str(target_spec.get("customer", "USAF")).upper()

    # Apply vendor specialty thrust & SFC modifiers
    dry_bonus = float(v_prof["thrust_dry_bonus_frac"])
    ab_bonus = float(v_prof["thrust_ab_bonus_frac"])
    # GE excels at Mach 1.6+ variable-stator afterburning engines
    if v_id == "general_electric" and target_mach >= 1.5 and q_year >= 1952.0:
        ab_bonus += 0.03

    noise_thrust = _rng_normal(rng, 0.0, 0.012)
    prom_dry_N = req_dry_N * (1.0 + dry_bonus + noise_thrust)
    prom_ab_N = (req_ab_N * (1.0 + ab_bonus + noise_thrust)) if has_ab else prom_dry_N

    # Baseline era dry & AB TSFC in (lb/hr)/lbf converted to SI kg/(N*s)
    era_progress = max(0.0, min(1.0, (q_year - 1945.0) / 15.0))
    base_dry_lbph = 1.10 - 0.30 * era_progress
    base_ab_lbph = 2.18 - 0.22 * era_progress

    prom_tsfc_dry = base_dry_lbph * float(v_prof["tsfc_dry_mult"]) * TSFC_LBPH_LBF_TO_SI
    prom_tsfc_ab = (
        base_ab_lbph * float(v_prof["tsfc_ab_mult"]) * TSFC_LBPH_LBF_TO_SI
        if has_ab
        else prom_tsfc_dry
    )

    # Engine mass, diameter, length from thrust & era thrust-to-weight progression
    # In 1945, dry T/W ~ 2.2 (specific mass ~ 0.046 kg/N); by 1956, dry T/W ~ 3.2 (0.032 kg/N)
    base_spec_mass_kg_per_N = 0.046 - 0.014 * era_progress
    ab_mass_factor = 1.16 if has_ab else 1.00
    spec_wt_mult = float(v_prof["specific_weight_mult"])
    prom_mass_kg = max(450.0, prom_dry_N * base_spec_mass_kg_per_N * ab_mass_factor * spec_wt_mult)

    mass_flow_kgps = prom_dry_N / (520.0 + 95.0 * era_progress)
    diam_mult = 0.94 if v_id == "westinghouse" else (0.97 if v_id == "general_electric" else 1.00)
    prom_diameter_m = max(0.68, min(1.35, 0.52 + 0.052 * math.sqrt(mass_flow_kgps) * diam_mult))
    prom_length_m = max(2.20, min(7.00, (3.10 + 0.025 * mass_flow_kgps) * (1.32 if has_ab else 1.00)))

    # Reliability (MTBF)
    base_mtbf_h = 135.0 + 75.0 * era_progress
    prom_mtbf_h = base_mtbf_h * float(v_prof["mtbf_mult"])

    # Ambition & Risk calculation
    era_frontier_dry_N = (20000.0 + 4200.0 * max(0.0, q_year - 1945.0))
    size_ambition = max(0.10, min(1.40, req_dry_N / era_frontier_dry_N))
    mach_ambition = max(0.0, (target_mach - (0.90 + 0.08 * (q_year - 1945.0))) * 0.65)
    raw_ambition = max(0.15, min(1.45, 0.70 * size_ambition + mach_ambition + (0.15 if has_ab and q_year < 1949.0 else 0.0)))

    if is_derivative:
        # Curtiss-Wright gets an extra derivative discount modeling licensed Sapphire/Olympus production
        deriv_disc = 0.50 if v_id == "wright" else float(t["derivative_dev_cost_discount"])
        raw_ambition *= (1.0 - 0.35 * deriv_disc)

    risk_mult = float(v_prof["dev_risk_mult"])
    # Westinghouse J40 historical risk spike for ambitious afterburning engines in 1948-1955
    if v_id == "westinghouse" and has_ab and prom_dry_N >= 32000.0 and 1948.0 <= q_year <= 1955.5:
        risk_mult *= 1.22

    dev_risk_index = max(0.05, min(0.95, 0.32 * raw_ambition * risk_mult))
    schedule_slip_prob = max(0.04, min(0.90, dev_risk_index * 0.85))
    shortfall_risk_prob = max(0.03, min(0.85, dev_risk_index * 0.75))

    # Development Cost & Unit Price
    base_dev_1950 = float(t["base_commission_dev_cost_1950_usd"])
    total_dev_usd = (
        base_dev_1950
        * idx_aero
        * (0.55 + 0.85 * (raw_ambition ** 1.35))
        * float(v_prof["dev_cost_mult"])
    )
    if is_derivative:
        deriv_cost_disc = 0.48 if v_id == "wright" else float(t["derivative_dev_cost_discount"])
        total_dev_usd *= (1.0 - deriv_cost_disc)

    share_frac = float(target_spec.get("player_share_fraction", t["player_share_fraction_default"]))
    commission_fee_usd = total_dev_usd * share_frac

    base_unit_1950 = 32000.0 + 1.85 * prom_dry_N * (1.22 if has_ab else 1.00)
    unit_price_usd = base_unit_1950 * idx_aero * float(v_prof["unit_cost_mult"])

    # Schedule duration
    base_days = float(t["base_commission_duration_days"])
    eng_staff = float(maker_rec.get("propulsion_engineers", 90))
    cell_lvl = int(maker_rec.get("altitude_test_cell_level", 1))
    facility_speedup = 1.0 - 0.04 * (cell_lvl - 1) - 0.001 * (eng_staff - 85.0)
    dev_days = int(
        round(
            base_days
            * (0.65 + 0.55 * raw_ambition)
            * float(v_prof["dev_days_mult"])
            * max(0.82, min(1.15, facility_speedup))
        )
    )
    if is_derivative:
        deriv_days_disc = 0.42 if v_id == "wright" else float(t["derivative_duration_discount"])
        dev_days = int(round(dev_days * (1.0 - deriv_days_disc)))
    dev_days = max(150, dev_days)

    # Authentic US Military Joint J-number Designation (even for USN, odd for USAF)
    base_j_num = 30 + 2 * int(max(0, min(35, round((q_year - 1945.0) * 3.8 + prom_dry_N / 25000.0))))
    if customer == "USAF" and base_j_num % 2 == 0:
        base_j_num += 1
    elif customer == "USN" and base_j_num % 2 == 1:
        base_j_num += 1
    us_code = str(v_prof["us_code"])
    dash_num = 3 if is_derivative else 1
    designation = f"XJ{base_j_num}-{us_code}-{dash_num}"

    tr_ratio = (1.08 if has_ab else 1.00) + 0.14 * era_progress + float(v_prof["throttle_ratio_tr_bonus"])
    deck = StubEngineDeck(
        engine_id=designation,
        name=f"{v_prof['display_name']} {designation}",
        dry_thrust_sl_N=prom_dry_N,
        ab_thrust_sl_N=prom_ab_N,
        has_afterburner=has_ab,
        tsfc_dry_sl=prom_tsfc_dry,
        tsfc_ab_sl=prom_tsfc_ab,
        mass_kg=prom_mass_kg,
        diameter_m=prom_diameter_m,
        length_m=prom_length_m,
        mass_flow_kgps=mass_flow_kgps,
        unit_cost=unit_price_usd,
        mtbf_h=prom_mtbf_h,
        maint_mh_per_fh=max(2.5, (5.6 if has_ab else 4.0) / float(v_prof["mtbf_mult"])),
        alt_exp_dry=0.75 if v_id in ("pratt_whitney", "general_electric") else 0.78,
        alt_exp_ab=0.72 if v_id == "general_electric" else 0.76,
        ram_c2_ab=0.45 if v_id == "general_electric" else 0.36,
        throttle_ratio_tr=tr_ratio,
    )

    notes_map = {
        "pratt_whitney": "Dual-spool high-OPR architecture with Willgoos altitude test cell verification; lowest dry SFC and highest fleet TBO/MTBF.",
        "general_electric": "High-Mach variable-stator / afterburner design optimized for supersonic dash and fast altitude climb.",
        "allison": "General Motors high-rate production tooling; lowest recurring unit price and dependable subsonic cruise economy.",
        "westinghouse": "Ultra-compact small-diameter axial layout with low dry weight, but limited altitude test-cell capacity increases schedule & thrust shortfall risk.",
        "wright": "Fast-tracked licensed derivative tooling with reduced R&D cost and early prototype delivery.",
    }

    return CustomEngineQuote(
        quote_id=f"quote_{v_id}_{q_day}_{int(round(req_dry_N))}",
        vendor_id=v_id,
        vendor_name=str(v_prof["display_name"]),
        us_code=us_code,
        specialty=str(v_prof["specialty"]),
        designation=designation,
        date_quoted=q_iso,
        is_derivative=is_derivative,
        promised_dry_thrust_sl_N=prom_dry_N,
        promised_ab_thrust_sl_N=prom_ab_N,
        has_afterburner=has_ab,
        promised_tsfc_dry_sl=prom_tsfc_dry,
        promised_tsfc_ab_sl=prom_tsfc_ab,
        promised_mass_kg=prom_mass_kg,
        promised_diameter_m=prom_diameter_m,
        promised_length_m=prom_length_m,
        promised_mtbf_h=prom_mtbf_h,
        unit_price_usd=unit_price_usd,
        total_dev_cost_usd=total_dev_usd,
        airframer_commission_fee_usd=commission_fee_usd,
        promised_delivery_days=dev_days,
        development_risk_index=dev_risk_index,
        schedule_slip_prob=schedule_slip_prob,
        shortfall_risk_prob=shortfall_risk_prob,
        engine_deck=deck,
        vendor_notes=notes_map.get(v_id, ""),
    )


def compare_vendor_quotes(
    target_spec: Mapping[str, Any],
    date: Union[str, int, float],
    rng: Any = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> List[CustomEngineQuote]:
    """Generate and return custom engine commission quotes across all 5 historical US vendors."""
    vendors = ["pratt_whitney", "general_electric", "allison", "wright", "westinghouse"]
    return [
        quote_custom_engine(vid, target_spec=target_spec, date=date, rng=rng, tuning=tuning)
        for vid in vendors
    ]
