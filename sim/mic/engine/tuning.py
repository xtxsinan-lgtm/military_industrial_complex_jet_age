"""Loader for sim/data/tuning/engine.json."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional

_TUNING_CACHE: Optional[Dict[str, Any]] = None


def _default_tuning_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "tuning" / "engine.json"


def load_engine_tuning(path: Optional[Path] = None, reload: bool = False) -> Dict[str, Any]:
    """Load engine tuning dictionary from JSON."""
    global _TUNING_CACHE
    if path is not None:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    if _TUNING_CACHE is None or reload:
        p = _default_tuning_path()
        with open(p, "r", encoding="utf-8") as f:
            _TUNING_CACHE = json.load(f)
    return copy.deepcopy(_TUNING_CACHE)
