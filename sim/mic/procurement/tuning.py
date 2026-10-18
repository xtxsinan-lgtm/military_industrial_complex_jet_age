"""Loader for Module 05 tunables (sim/data/tuning/procurement.json)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_TUNING_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "tuning" / "procurement.json"
)

_CACHED_TUNING: Optional[Dict[str, Any]] = None


def load_tuning(path: Optional[Path] = None, reload: bool = False) -> Dict[str, Any]:
    """Load procurement tuning dictionary from JSON."""
    global _CACHED_TUNING
    if path is None and _CACHED_TUNING is not None and not reload:
        return _CACHED_TUNING
    target = path if path is not None else DEFAULT_TUNING_PATH
    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)
    if path is None:
        _CACHED_TUNING = data
    return data
