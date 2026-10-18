"""Module 02: Engine cycle model, deck interpolation, diagnostics, and R&D projects."""
from __future__ import annotations

from .catalog import (
    design_input_from_hist_dict,
    list_historical_engines,
    load_historical_engine,
    load_historical_engine_data,
)
from .cycle import (
    CyclePointResult,
    EngineDesignInput,
    OnDesignReference,
    compute_inlet_recovery,
    evaluate_cycle_at_tt4,
    evaluate_off_design_point,
    max_available_tt4,
    solve_on_design,
)
from .deck import EngineDeckTables, EngineSpec, build_deck_tables, design_engine
from .diagnostics import compute_diagnostics
from .rnd import (
    DEFAULT_START_1945_ENGINE_TECH,
    EngineProjectEstimate,
    EngineProjectOutcome,
    EngineProjectState,
    allocate_rnd_priorities,
    compute_ambition,
    compute_third_party_engine_sale,
    evaluate_rnd_project,
    resolve_rnd_outcome,
    validate_engine_against_tech,
)
from .sizing import EnginePhysicalMetrics, duane_mtbf, estimate_physical_metrics
from .tuning import load_engine_tuning

__all__ = [
    "CyclePointResult",
    "DEFAULT_START_1945_ENGINE_TECH",
    "EngineDeckTables",
    "EngineDesignInput",
    "EnginePhysicalMetrics",
    "EngineProjectEstimate",
    "EngineProjectOutcome",
    "EngineProjectState",
    "EngineSpec",
    "OnDesignReference",
    "allocate_rnd_priorities",
    "build_deck_tables",
    "compute_ambition",
    "compute_diagnostics",
    "compute_inlet_recovery",
    "compute_third_party_engine_sale",
    "design_engine",
    "design_input_from_hist_dict",
    "duane_mtbf",
    "estimate_physical_metrics",
    "evaluate_cycle_at_tt4",
    "evaluate_off_design_point",
    "evaluate_rnd_project",
    "list_historical_engines",
    "load_engine_tuning",
    "load_historical_engine",
    "load_historical_engine_data",
    "max_available_tt4",
    "resolve_rnd_outcome",
    "solve_on_design",
    "validate_engine_against_tech",
]
