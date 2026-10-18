"""Unit and golden-vector tests for `sim/mic/rng.py` and `sim/mic/calendar.py`.

Owned by Module 09 (`docs/spec/09_core_loop.md`).
"""

from __future__ import annotations

import datetime
import json
import math
import sys
from pathlib import Path

import pytest

_SIM_DIR = Path(__file__).resolve().parents[1]
if str(_SIM_DIR) not in sys.path:
    sys.path.insert(0, str(_SIM_DIR))

from mic.calendar import (  # noqa: E402
    MVP_END_DAY,
    MVP_START_DAY,
    add_months,
    calendar_quarter,
    day_of_week,
    day_to_iso,
    day_to_ymd,
    days_in_month,
    fiscal_quarter,
    fiscal_year,
    fiscal_year_bounds,
    format_display_date,
    get_tick_schedule,
    is_leap_year,
    iso_to_day,
    prev_month_days,
    weekday_name,
    ymd_to_day,
)
from mic.rng import (  # noqa: E402
    PCG32,
    RngStreamRegistry,
    fnv1a_64,
    hex_to_u64,
    mtth_prob,
    u64_to_hex,
)

GOLDEN_DIR = _SIM_DIR / "golden"


def test_pcg32_canonical_oneill_reference_golden() -> None:
    """Verify PCG32(42, 54) matches M. E. O'Neill's canonical C reference and golden file."""
    golden = json.loads((GOLDEN_DIR / "core_rng_pcg32.json").read_text(encoding="utf-8"))
    ref = golden["pcg32_canonical_seed_42_54"]
    rng = PCG32(ref["initstate"], ref["initseq"])
    draws = [rng.next_u32() for _ in range(10)]
    assert draws == [
        2707161783,
        2068313097,
        3122475824,
        2211639955,
        3215226955,
        3421331566,
        3217466285,
        2167406445,
        3860803674,
        4181216144,
    ]
    assert draws == ref["first_10_u32"]
    assert rng.to_dict() == ref["state_after_10_u32"]


def test_rng_operations_golden() -> None:
    """Verify u64, float, next_bounded, Box-Muller normal, weighted_choice, and shuffle against golden."""
    golden = json.loads((GOLDEN_DIR / "core_rng_pcg32.json").read_text(encoding="utf-8"))
    sec = golden["rng_operations_seed_123456789_987654321"]
    rng = PCG32(sec["initstate"], sec["initseq"])

    u64_seq = [u64_to_hex(rng.next_u64()) for _ in range(4)]
    assert u64_seq == sec["u64_hex_4"]

    float_seq = [rng.next_float() for _ in range(6)]
    for got, exp in zip(float_seq, sec["float_6"]):
        assert math.isclose(got, exp, rel_tol=1e-15, abs_tol=0.0)

    bounded_seq = [rng.next_bounded(b) for b in (6, 10, 52, 100, 1000, 65536)]
    assert bounded_seq == sec["bounded_6_10_52_100_1000_65536"]

    normal_seq = [rng.normal(0.0, 1.0) for _ in range(6)]
    for got, exp in zip(normal_seq, sec["box_muller_normal_6"]):
        assert math.isclose(got, exp, rel_tol=1e-15, abs_tol=0.0)

    items = ["alpha", "beta", "gamma", "delta"]
    weights = [0.1, 0.2, 0.5, 0.2]
    picks = [rng.weighted_choice(items, weights) for _ in range(10)]
    assert picks == sec["weighted_choice_10"]

    deck = [0, 1, 2, 3, 4, 5, 6, 7]
    rng.shuffle(deck)
    assert deck == sec["shuffled_deck_8"]
    assert rng.to_dict() == sec["final_state"]


def test_fnv1a_64_and_stream_registry_isolation() -> None:
    """Verify FNV-1a 64 hashes and stream order-independence in RngStreamRegistry."""
    golden = json.loads((GOLDEN_DIR / "core_rng_pcg32.json").read_text(encoding="utf-8"))
    for name, expected_hex in golden["fnv1a_64_vectors"].items():
        assert u64_to_hex(fnv1a_64(name)) == expected_hex

    reg_a = RngStreamRegistry(19450101)
    reg_b = RngStreamRegistry(19450101)

    # Access streams in different orders on reg_a and reg_b
    _ = [reg_a.stream("ai.bidding").next_u32() for _ in range(4)]
    proc_a = [reg_a.stream("proc.eval").next_u32() for _ in range(4)]

    proc_b = [reg_b.stream("proc.eval").next_u32() for _ in range(4)]
    assert proc_a == proc_b
    assert proc_a == golden["stream_registry_master_19450101"]["proc.eval"]

    # Round-trip registry serialization
    restored = RngStreamRegistry.from_dict(reg_a.to_dict())
    assert [reg_a.stream("proc.eval").next_u32() for _ in range(5)] == [
        restored.stream("proc.eval").next_u32() for _ in range(5)
    ]


def test_pcg32_edge_cases_and_serialization() -> None:
    rng = PCG32(999, 777)
    snap = rng.to_dict()
    clone = PCG32.from_dict(snap)
    assert [rng.next_u32() for _ in range(20)] == [clone.next_u32() for _ in range(20)]

    assert hex_to_u64("0x000000000000002a") == 42
    assert hex_to_u64("42") == 42

    assert rng.bernoulli(0.0) is False
    assert rng.bernoulli(1.0) is True
    for _ in range(50):
        v = rng.randint(10, 20)
        assert 10 <= v < 20
        vi = rng.randint_inclusive(10, 10)
        assert vi == 10

    with pytest.raises(ValueError):
        rng.next_bounded(0)
    with pytest.raises(ValueError):
        rng.choice([])
    with pytest.raises(ValueError):
        rng.weighted_choice(["a", "b"], [0.0, 0.0])
    with pytest.raises(ValueError):
        rng.weighted_choice(["a", "b"], [1.0, -0.5])
    with pytest.raises(ValueError):
        PCG32.from_raw_state(123, 4)  # even inc is invalid


def test_mtth_prob_properties() -> None:
    assert math.isclose(mtth_prob(30.0, 30), 0.5, rel_tol=1e-15)
    assert mtth_prob(30.0, 0) == 0.0
    assert mtth_prob(0.0, 10) == 1.0


def test_calendar_exhaustive_1945_to_1961_and_golden() -> None:
    """Verify every single day from 1944-01-01 through 1962-12-31 against Python datetime.date."""
    base = datetime.date(1945, 1, 1)
    assert MVP_START_DAY == 0
    assert MVP_END_DAY == 5843
    assert iso_to_day("1945-01-01") == 0
    assert iso_to_day("1960-12-31") == 5843

    for offset in range(-366, 6600):
        dt = base + datetime.timedelta(days=offset)
        assert ymd_to_day(dt.year, dt.month, dt.day) == offset
        assert day_to_ymd(offset) == (dt.year, dt.month, dt.day)
        assert day_to_iso(offset) == dt.isoformat()
        assert day_of_week(offset) == dt.weekday()

    # Golden vector verification
    golden = json.loads((GOLDEN_DIR / "core_calendar.json").read_text(encoding="utf-8"))
    for vec in golden["date_vectors"]:
        d = iso_to_day(vec["iso"])
        assert d == vec["day"]
        sched = get_tick_schedule(d)
        assert sched.year == vec["year"]
        assert sched.month == vec["month"]
        assert sched.day_of_month == vec["day_of_month"]
        assert sched.weekday == vec["weekday"]
        assert weekday_name(d) == vec["weekday_name"]
        assert sched.calendar_quarter == vec["calendar_quarter"]
        assert sched.fiscal_year == vec["fiscal_year"]
        assert sched.fiscal_quarter == vec["fiscal_quarter"]
        assert sched.is_month_start == vec["is_month_start"]
        assert sched.is_month_end == vec["is_month_end"]
        assert sched.is_quarter_start == vec["is_quarter_start"]
        assert sched.is_year_start == vec["is_year_start"]
        assert sched.is_fiscal_year_start == vec["is_fiscal_year_start"]
        assert sched.days_in_current_month == vec["days_in_current_month"]
        assert sched.days_in_prev_month == vec["days_in_prev_month"]


def test_calendar_fiscal_year_and_edge_cases() -> None:
    # June 30, 1945 is the last day of FY1945 (Q4); July 1, 1945 is the first day of FY1946 (Q1)
    d_jun30 = iso_to_day("1945-06-30")
    d_jul01 = iso_to_day("1945-07-01")
    assert fiscal_year(d_jun30) == 1945
    assert fiscal_quarter(d_jun30) == 4
    assert fiscal_year(d_jul01) == 1946
    assert fiscal_quarter(d_jul01) == 1
    assert get_tick_schedule(d_jul01).is_fiscal_year_start is True

    s_1950, e_1950 = fiscal_year_bounds(1950)
    assert day_to_iso(s_1950) == "1949-07-01"
    assert day_to_iso(e_1950) == "1950-06-30"

    assert is_leap_year(1948) is True
    assert is_leap_year(1900) is False
    assert is_leap_year(2000) is True
    assert days_in_month(1948, 2) == 29
    assert days_in_month(1949, 2) == 28
    assert prev_month_days(iso_to_day("1948-03-15")) == 29
    assert calendar_quarter(iso_to_day("1950-11-08")) == 4
    assert format_display_date(0) == "01 Jan 1945"
    assert day_to_iso(add_months(iso_to_day("1945-01-31"), 1)) == "1945-02-28"

    with pytest.raises(ValueError):
        ymd_to_day(1945, 2, 29)
    with pytest.raises(ValueError):
        ymd_to_day(1945, 13, 1)
    with pytest.raises(ValueError):
        iso_to_day("1945/01/01")
