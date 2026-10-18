"""Historical engine catalog loader from sim/data/engines_hist/*.json."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .cycle import EngineDesignInput
from .deck import EngineSpec, design_engine
from .tuning import load_engine_tuning


def _hist_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "engines_hist"


def list_historical_engines(directory: Optional[Path] = None) -> List[str]:
    """Return sorted list of engine_ids available in sim/data/engines_hist/."""
    d = directory or _hist_dir()
    if not d.exists():
        return []
    ids: List[str] = []
    for p in sorted(d.glob("*.json")):
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            ids.append(str(data.get("engine_id", p.stem)))
    return sorted(ids)


def load_historical_engine_data(
    engine_id: str,
    directory: Optional[Path] = None,
) -> Dict[str, Any]:
    """Load raw JSON dictionary for a historical engine."""
    d = directory or _hist_dir()
    direct_path = d / f"{engine_id}.json"
    if direct_path.exists():
        with open(direct_path, "r", encoding="utf-8") as f:
            return json.load(f)
    for p in sorted(d.glob("*.json")):
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data.get("engine_id") == engine_id:
                return data
    raise KeyError(f"Historical engine '{engine_id}' not found in {d}")


def design_input_from_hist_dict(data: Dict[str, Any]) -> EngineDesignInput:
    """Convert historical JSON record's `cycle_input` block into EngineDesignInput."""
    c = data["cycle_input"]
    return EngineDesignInput(
        engine_id=data["engine_id"],
        name=data["name"],
        compressor_type=c.get("compressor_type", "axial"),
        spools=int(c.get("spools", 1)),
        variable_stators=bool(c.get("variable_stators", False)),
        has_afterburner=bool(c.get("has_afterburner", False)),
        nozzle_type=c.get("nozzle_type", "convergent"),
        mass_flow_kgps=float(c["mass_flow_kgps"]),
        opr=float(c["opr"]),
        tit_K=float(c["tit_K"]),
        ab_temp_K=float(c.get("ab_temp_K", 0.0)),
        bypass_ratio=float(c.get("bypass_ratio", 0.0)),
        cooled_turbine=bool(c.get("cooled_turbine", False)),
        eta_c_poly=float(c.get("eta_c_poly", 0.84)),
        eta_t_poly=float(c.get("eta_t_poly", 0.86)),
        eta_burner=c.get("eta_burner"),
        pi_burner=c.get("pi_burner"),
        eta_ab=c.get("eta_ab"),
        pi_ab_dry=c.get("pi_ab_dry"),
        pi_ab_wet=c.get("pi_ab_wet"),
        nozzle_cv=c.get("nozzle_cv"),
        bleed_fraction=float(c.get("bleed_fraction", 0.0)),
        specific_weight_factor=float(c.get("specific_weight_factor", 1.0)),
        mtbf_factor=float(c.get("mtbf_factor", 1.0)),
        length_factor=float(c.get("length_factor", 1.0)),
        diameter_factor=float(c.get("diameter_factor", 1.0)),
        cumulative_test_hours=float(c.get("cumulative_test_hours", 1000.0)),
        extra=data.get("historical_reference", {}),
    )


def load_historical_engine(
    engine_id: str,
    build_deck: bool = True,
    use_published_statics: bool = False,
    directory: Optional[Path] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> EngineSpec:
    """Load a historical engine as a ready-to-use EngineSpec."""
    data = load_historical_engine_data(engine_id, directory=directory)
    inp = design_input_from_hist_dict(data)
    t = tuning or load_engine_tuning()

    overrides: Optional[Dict[str, float]] = None
    if use_published_statics and "historical_reference" in data:
        ref = data["historical_reference"]
        overrides = {}
        for k in ("mass_kg", "diameter_m", "length_m", "unit_cost_usd"):
            if k in ref and ref[k] is not None:
                out_k = "unit_cost" if k == "unit_cost_usd" else k
                overrides[out_k] = float(ref[k])

    return design_engine(
        inp,
        build_deck=build_deck,
        static_overrides=overrides,
        tuning=t,
    )
