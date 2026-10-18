"""Tuning loader and typed configuration helpers for Module 07 (`mic.ai`)."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional

_DEFAULT_TUNING_PATH = Path(__file__).resolve().parents[2] / "data" / "tuning" / "ai.json"
_CACHED_TUNING: Optional[Dict[str, Any]] = None


def load_ai_tuning(path: Optional[Path] = None, reload: bool = False) -> Dict[str, Any]:
    """Load and cache `sim/data/tuning/ai.json`."""
    global _CACHED_TUNING
    if path is None and _CACHED_TUNING is not None and not reload:
        return copy.deepcopy(_CACHED_TUNING)

    target = Path(path) if path is not None else _DEFAULT_TUNING_PATH
    with open(target, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if path is None:
        _CACHED_TUNING = data
    return copy.deepcopy(data)


def get_company_signature(
    company_id: str,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return the AI signature style profile for `company_id` (with balanced fallback)."""
    t = tuning if tuning is not None else load_ai_tuning()
    sigs = t.get("company_ai", {}).get("company_signatures", {})
    if company_id in sigs:
        return dict(sigs[company_id])
    return {
        "preferred_planform": "swept",
        "delta_bias": 0.10,
        "sweep_bias_deg": 0.0,
        "tc_bias": 0.0,
        "aspect_ratio_bias": 0.0,
        "twin_engine_bias": 0.25,
        "internal_fuel_bias": 1.00,
        "ruggedness_g_bias": 0.0,
        "area_rule_adoption_bias": 0.75,
        "preferred_intake": "nose",
        "model_prefix": company_id[:2].upper() if company_id else "AI",
    }
