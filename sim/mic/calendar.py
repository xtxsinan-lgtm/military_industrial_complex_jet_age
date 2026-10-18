"""Proleptic Gregorian calendar, US Fiscal Year (July 1 start), and tick schedule.

Owned by Module 09 (`docs/spec/09_core_loop.md`).
Day 0 is 1945-01-01 (Monday). Pure integer math (Howard Hinnant's civil calendar
algorithms) guarantees identical behavior in Python and C# with no timezone/locale risk.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

EPOCH_YEAR: int = 1945
EPOCH_MONTH: int = 1
EPOCH_DAY: int = 1

# Howard Hinnant days-from-0000-03-01 offset for 1945-01-01
_CIVIL_OFFSET_1945_01_01: int = 710337

MVP_START_ISO: str = "1945-01-01"
MVP_END_ISO: str = "1960-12-31"
MVP_START_DAY: int = 0
MVP_END_DAY: int = 5843  # 1960-12-31 inclusive (5844 total days across 1945..1960)

_DAYS_IN_MONTH_COMMON: Tuple[int, ...] = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
_MONTH_ABBR: Tuple[str, ...] = (
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)
_WEEKDAY_NAMES: Tuple[str, ...] = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)

# Real-time seconds per simulated day for Paradox-style speeds 1..5 (0 = paused)
SPEED_SECONDS_PER_DAY: Dict[int, float] = {
    1: 2.00,
    2: 1.00,
    3: 0.40,
    4: 0.15,
    5: 0.05,
}


def is_leap_year(year: int) -> bool:
    """Return True if `year` is a proleptic Gregorian leap year."""
    y = int(year)
    return (y % 4 == 0) and ((y % 100 != 0) or (y % 400 == 0))


def days_in_month(year: int, month: int) -> int:
    """Return the number of days in `(year, month)` for `month` in 1..12."""
    m = int(month)
    if m < 1 or m > 12:
        raise ValueError(f"month must be in 1..12, got {month}")
    if m == 2 and is_leap_year(year):
        return 29
    return _DAYS_IN_MONTH_COMMON[m]


def validate_ymd(year: int, month: int, day: int) -> None:
    """Validate `(year, month, day)` and raise `ValueError` if out of range."""
    m = int(month)
    d = int(day)
    if m < 1 or m > 12:
        raise ValueError(f"Invalid month {month} in {year}-{month}-{day}")
    dim = days_in_month(year, m)
    if d < 1 or d > dim:
        raise ValueError(f"Invalid day {day} for {year:04d}-{m:02d} (max {dim})")


def _days_from_civil(year: int, month: int, day: int) -> int:
    """Howard Hinnant's `days_from_civil`: days since 0000-03-01."""
    y = int(year) - (1 if int(month) <= 2 else 0)
    era = y // 400
    yoe = y - era * 400
    m = int(month)
    d = int(day)
    doy = (153 * (m + (9 if m <= 2 else -3)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe


def _civil_from_days(z: int) -> Tuple[int, int, int]:
    """Howard Hinnant's `civil_from_days`: `(year, month, day)` from days since 0000-03-01."""
    era = z // 146097
    doe = z - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    y = yoe + era * 400
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + (3 if mp < 10 else -9)
    return y + (1 if m <= 2 else 0), m, d


def ymd_to_day(year: int, month: int, day: int) -> int:
    """Convert `(year, month, day)` to integer days since 1945-01-01 (`0 = 1945-01-01`)."""
    validate_ymd(year, month, day)
    return _days_from_civil(year, month, day) - _CIVIL_OFFSET_1945_01_01


def day_to_ymd(day_index: int) -> Tuple[int, int, int]:
    """Convert integer days since 1945-01-01 to `(year, month, day)`."""
    return _civil_from_days(int(day_index) + _CIVIL_OFFSET_1945_01_01)


def iso_to_day(iso_date: str) -> int:
    """Parse `'YYYY-MM-DD'` into integer days since 1945-01-01."""
    if not isinstance(iso_date, str):
        raise ValueError(f"Expected ISO date string 'YYYY-MM-DD', got {iso_date!r}")
    parts = iso_date.strip().split("-")
    if len(parts) != 3 or len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
        raise ValueError(f"Invalid ISO date format (expected YYYY-MM-DD): {iso_date!r}")
    try:
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError as exc:
        raise ValueError(f"Non-integer components in ISO date: {iso_date!r}") from exc
    return ymd_to_day(y, m, d)


def day_to_iso(day_index: int) -> str:
    """Format integer days since 1945-01-01 as `'YYYY-MM-DD'`."""
    y, m, d = day_to_ymd(day_index)
    return f"{y:04d}-{m:02d}-{d:02d}"


def format_display_date(day_index: int) -> str:
    """Format day index for UI display as `'DD Mon YYYY'` (e.g. `'01 Jan 1945'`)."""
    y, m, d = day_to_ymd(day_index)
    return f"{d:02d} {_MONTH_ABBR[m]} {y:04d}"


def day_of_week(day_index: int) -> int:
    """Return weekday index `0 = Monday .. 6 = Sunday` (1945-01-01 was Monday)."""
    return int(day_index) % 7


def weekday_name(day_index: int) -> str:
    """Return English weekday name for `day_index`."""
    return _WEEKDAY_NAMES[day_of_week(day_index)]


def fiscal_year(day_index: int) -> int:
    """Return the pre-1976 US Federal Fiscal Year (starts July 1 of calendar year `FY - 1`).

    Examples:
        - 1945-01-01 .. 1945-06-30 -> FY 1945
        - 1945-07-01 .. 1946-06-30 -> FY 1946
        - 1960-07-01 .. 1960-12-31 -> FY 1961
    """
    y, m, _ = day_to_ymd(day_index)
    return y + 1 if m >= 7 else y


def fiscal_quarter(day_index: int) -> int:
    """Return US Fiscal Quarter in `1..4` (Q1=Jul-Sep, Q2=Oct-Dec, Q3=Jan-Mar, Q4=Apr-Jun)."""
    _, m, _ = day_to_ymd(day_index)
    if m >= 7:
        return ((m - 7) // 3) + 1
    return ((m - 1) // 3) + 3


def calendar_quarter(day_index: int) -> int:
    """Return calendar quarter in `1..4` (Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec)."""
    _, m, _ = day_to_ymd(day_index)
    return ((m - 1) // 3) + 1


def fiscal_year_bounds(fy: int) -> Tuple[int, int]:
    """Return `(start_day_inclusive, end_day_inclusive)` for US Fiscal Year `fy`."""
    f = int(fy)
    return ymd_to_day(f - 1, 7, 1), ymd_to_day(f, 6, 30)


def prev_month_year_month(year: int, month: int) -> Tuple[int, int]:
    """Return `(prev_year, prev_month)` immediately preceding `(year, month)`."""
    if month == 1:
        return year - 1, 12
    return year, month - 1


def prev_month_days(day_index: int) -> int:
    """Return the number of days in the calendar month immediately preceding `day_index`'s month."""
    y, m, _ = day_to_ymd(day_index)
    py, pm = prev_month_year_month(y, m)
    return days_in_month(py, pm)


def add_months(day_index: int, months: int) -> int:
    """Add `months` calendar months to `day_index`, clamping day-of-month to valid range."""
    y, m, d = day_to_ymd(day_index)
    total_m = (y * 12 + (m - 1)) + int(months)
    ny = total_m // 12
    nm = (total_m % 12) + 1
    nd = min(d, days_in_month(ny, nm))
    return ymd_to_day(ny, nm, nd)


@dataclass(frozen=True)
class TickSchedule:
    """Complete calendar and cadence flags for a single simulation day tick."""

    day: int
    year: int
    month: int
    day_of_month: int
    iso: str
    weekday: int
    calendar_quarter: int
    fiscal_year: int
    fiscal_quarter: int
    is_month_start: bool
    is_month_end: bool
    is_quarter_start: bool
    is_fiscal_quarter_start: bool
    is_year_start: bool
    is_fiscal_year_start: bool
    days_in_current_month: int
    days_in_prev_month: int


def get_tick_schedule(day_index: int) -> TickSchedule:
    """Build the `TickSchedule` for `day_index`."""
    d_idx = int(day_index)
    y, m, dom = day_to_ymd(d_idx)
    dim = days_in_month(y, m)
    py, pm = prev_month_year_month(y, m)
    p_dim = days_in_month(py, pm)
    is_ms = dom == 1
    is_qs = is_ms and (m in (1, 4, 7, 10))
    return TickSchedule(
        day=d_idx,
        year=y,
        month=m,
        day_of_month=dom,
        iso=f"{y:04d}-{m:02d}-{dom:02d}",
        weekday=d_idx % 7,
        calendar_quarter=((m - 1) // 3) + 1,
        fiscal_year=y + 1 if m >= 7 else y,
        fiscal_quarter=(((m - 7) // 3) + 1) if m >= 7 else (((m - 1) // 3) + 3),
        is_month_start=is_ms,
        is_month_end=(dom == dim),
        is_quarter_start=is_qs,
        is_fiscal_quarter_start=is_qs,
        is_year_start=is_ms and (m == 1),
        is_fiscal_year_start=is_ms and (m == 7),
        days_in_current_month=dim,
        days_in_prev_month=p_dim,
    )
