"""Loader and cache for Module 04 economy tunables (`sim/data/tuning/econ.json`)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_TUNING_PATH = _REPO_ROOT / "sim" / "data" / "tuning" / "econ.json"
_CACHE: Optional[Dict[str, Any]] = None


def load_econ_tuning(path: Optional[Path] = None, force_reload: bool = False) -> Dict[str, Any]:
    """Return the parsed `econ.json` dictionary (cached unless `force_reload=True`)."""
    global _CACHE
    if path is not None:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    if _CACHE is None or force_reload:
        with open(_DEFAULT_TUNING_PATH, "r", encoding="utf-8") as fh:
            _CACHE = json.load(fh)
    return _CACHE
