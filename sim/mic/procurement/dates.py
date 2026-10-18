"""Date and calendar conversion utilities for Module 05 (Procurement).

Conforms to 00_conventions.md section 3:
- Simulation tick = 1 day.
- Date type = integer days since 1945-01-01 (1945-01-01 -> day 0).
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Union

EPOCH_DATE = date(1945, 1, 1)
DAYS_PER_YEAR = 365.25
DAYS_PER_MONTH = 30.4375


def date_to_day(d: Union[str, date, int]) -> int:
    """Convert an ISO string 'YYYY-MM-DD', datetime.date, or int day to days since 1945-01-01."""
    if isinstance(d, int):
        return d
    if isinstance(d, date):
        return (d - EPOCH_DATE).days
    if isinstance(d, str):
        parts = d.strip().split("-")
        if len(parts) != 3:
            raise ValueError(f"Invalid ISO date string: {d!r}")
        dt = date(int(parts[0]), int(parts[1]), int(parts[2]))
        return (dt - EPOCH_DATE).days
    raise TypeError(f"Unsupported date type: {type(d)!r}")


def day_to_date(day_index: int) -> date:
    """Convert integer days since 1945-01-01 to datetime.date."""
    return EPOCH_DATE + timedelta(days=int(day_index))


def day_to_iso(day_index: int) -> str:
    """Convert integer days since 1945-01-01 to ISO string 'YYYY-MM-DD'."""
    return day_to_date(day_index).isoformat()


def day_to_fractional_year(day_index: int) -> float:
    """Convert integer days since 1945-01-01 to fractional calendar year (e.g. 1952.70)."""
    return 1945.0 + float(day_index) / DAYS_PER_YEAR


def day_to_fiscal_year(day_index: int) -> int:
    """Return US federal fiscal year for a given day (pre-1976 US fiscal year starts July 1).

    Example: 1953-07-01 is in FY 1954; 1953-06-30 is in FY 1953.
    """
    dt = day_to_date(day_index)
    return dt.year + 1 if dt.month >= 7 else dt.year
