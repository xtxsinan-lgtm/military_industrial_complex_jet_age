"""Data loader and calendar helpers for Module 06 (`sim/mic/testing`)."""
from __future__ import annotations

import datetime
import functools
import json
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_TESTING_DIR = REPO_ROOT / "sim" / "data" / "testing"
DATA_TUNING_DIR = REPO_ROOT / "sim" / "data" / "tuning"

EPOCH_DATE = datetime.date(1945, 1, 1)


def date_str_to_day(date_str: str) -> int:
    """Convert 'YYYY-MM-DD' to integer days since 1945-01-01."""
    parts = [int(p) for p in date_str.split("-")]
    dt = datetime.date(parts[0], parts[1], parts[2])
    return (dt - EPOCH_DATE).days


def day_to_date(day: int) -> datetime.date:
    """Convert days since 1945-01-01 to datetime.date."""
    return EPOCH_DATE + datetime.timedelta(days=int(day))


def day_to_year(day: int) -> int:
    """Return calendar year for a given day index since 1945-01-01."""
    return day_to_date(day).year


@functools.lru_cache(maxsize=None)
def load_testing_tuning() -> Dict[str, Any]:
    with open(DATA_TUNING_DIR / "testing.json", "r", encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=None)
def load_drivers_data() -> Dict[str, Any]:
    with open(DATA_TESTING_DIR / "drivers.json", "r", encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=None)
def load_novelty_features_data() -> Dict[str, Any]:
    with open(DATA_TESTING_DIR / "novelty_features.json", "r", encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=None)
def load_sources_data() -> Dict[str, Any]:
    with open(DATA_TESTING_DIR / "sources.json", "r", encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=None)
def load_flight_items_data() -> Dict[str, Any]:
    with open(DATA_TESTING_DIR / "flight_items.json", "r", encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=None)
def load_flaws_data() -> Dict[str, Any]:
    with open(DATA_TESTING_DIR / "flaws.json", "r", encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=None)
def load_pilot_names_data() -> Dict[str, Any]:
    with open(DATA_TESTING_DIR / "pilot_names.json", "r", encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(maxsize=None)
def load_report_templates() -> Dict[str, str]:
    with open(DATA_TESTING_DIR / "report_templates.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_inflation_factor(year: int) -> float:
    """Return nominal USD multiplier relative to 1950-USD."""
    tuning = load_testing_tuning()
    table = tuning.get("inflation_1950_index", {})
    y_clamped = max(1945, min(1960, int(year)))
    return float(table.get(str(y_clamped), 1.0))
