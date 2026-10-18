"""Loader and cache for Module 01 global tuning parameters (`sim/data/tuning/aero.json`)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

_TUNING_CACHE: Optional[Dict[str, Any]] = None
_DEFAULT_TUNING_PATH = Path(__file__).resolve().parents[2] / "data" / "tuning" / "aero.json"


def load_aero_tuning(path: Optional[Path] = None, force_reload: bool = False) -> Dict[str, Any]:
    """Load and cache `sim/data/tuning/aero.json`."""
    global _TUNING_CACHE
    if _TUNING_CACHE is not None and not force_reload and path is None:
        return _TUNING_CACHE
    target = path if path is not None else _DEFAULT_TUNING_PATH
    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)
    if path is None:
        _TUNING_CACHE = data
    return data
