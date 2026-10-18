"""Historical US inflation, aerospace cost escalation, wage, and interest rate lookups (1945-2030)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_INFLATION_PATH = _REPO_ROOT / "sim" / "data" / "economy" / "inflation_usd.json"
_CACHE: Optional[Dict[str, Any]] = None


def load_inflation_table(path: Optional[Path] = None, force_reload: bool = False) -> Dict[str, Any]:
    """Load `sim/data/economy/inflation_usd.json`."""
    global _CACHE
    if path is not None:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    if _CACHE is None or force_reload:
        with open(_DEFAULT_INFLATION_PATH, "r", encoding="utf-8") as fh:
            _CACHE = json.load(fh)
    return _CACHE


def _interpolate_field(year: float, field: str, table: Optional[Dict[str, Any]] = None) -> float:
    data = table if table is not None else load_inflation_table()
    years_dict = data["years"]
    str_year = str(int(round(year)))
    if float(year) == int(round(year)) and str_year in years_dict:
        return float(years_dict[str_year][field])

    sorted_years: List[int] = sorted(int(k) for k in years_dict.keys())
    if year <= sorted_years[0]:
        return float(years_dict[str(sorted_years[0])][field])
    if year >= sorted_years[-1]:
        return float(years_dict[str(sorted_years[-1])][field])

    for i in range(len(sorted_years) - 1):
        y0, y1 = sorted_years[i], sorted_years[i + 1]
        if y0 <= year <= y1:
            v0 = float(years_dict[str(y0)][field])
            v1 = float(years_dict[str(y1)][field])
            frac = (float(year) - y0) / float(y1 - y0)
            return v0 + frac * (v1 - v0)
    return float(years_dict[str(sorted_years[-1])][field])


def cpi_index_1950(year: float, table: Optional[Dict[str, Any]] = None) -> float:
    """Return US CPI-U index normalized so 1950 = 1.0000."""
    return _interpolate_field(year, "cpi_index_1950", table)


def aero_cost_index_1950(year: float, table: Optional[Dict[str, Any]] = None) -> float:
    """Return aerospace industry composite cost escalation index (1950 = 1.0000)."""
    return _interpolate_field(year, "aero_cost_index_1950", table)


def to_then_year_usd(amount_1950_usd: float, year: float, use_aero_index: bool = False) -> float:
    """Convert constant-1950 USD to nominal then-year USD."""
    idx = aero_cost_index_1950(year) if use_aero_index else cpi_index_1950(year)
    return float(amount_1950_usd) * idx


def to_constant_1950_usd(then_year_usd: float, year: float, use_aero_index: bool = False) -> float:
    """Convert nominal then-year USD to constant-1950 USD (per `00_conventions.md` §3)."""
    idx = aero_cost_index_1950(year) if use_aero_index else cpi_index_1950(year)
    return float(then_year_usd) / max(idx, 1e-9)


def convert_usd_between_years(amount_usd: float, from_year: float, to_year: float, use_aero_index: bool = False) -> float:
    """Convert nominal USD from `from_year` to `to_year`."""
    c1950 = to_constant_1950_usd(amount_usd, from_year, use_aero_index=use_aero_index)
    return to_then_year_usd(c1950, to_year, use_aero_index=use_aero_index)


def benchmark_engineer_salary_usd_yr(year: float, table: Optional[Dict[str, Any]] = None) -> float:
    """Return industry benchmark annual salary for an aerospace engineer in then-year USD."""
    return _interpolate_field(year, "eng_salary_usd_yr", table)


def benchmark_mfg_wage_usd_hr(year: float, table: Optional[Dict[str, Any]] = None) -> float:
    """Return industry benchmark hourly wage for production workers in then-year USD."""
    return _interpolate_field(year, "mfg_wage_usd_hr", table)


def prime_interest_rate(year: float, table: Optional[Dict[str, Any]] = None) -> float:
    """Return US commercial bank prime loan interest rate (annualized fraction)."""
    return _interpolate_field(year, "prime_rate", table)


def corporate_aaa_bond_rate(year: float, table: Optional[Dict[str, Any]] = None) -> float:
    """Return Moody's AAA corporate bond yield (annualized fraction)."""
    return _interpolate_field(year, "corporate_aaa_rate", table)


def labor_market_tightness(year: float, table: Optional[Dict[str, Any]] = None) -> float:
    """Return macro aerospace labor market tightness index (1.0 = normal, >1 = tight/Korea surge)."""
    return _interpolate_field(year, "labor_market_tightness", table)
