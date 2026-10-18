"""Module 01 Performance package (`sim.mic.perf`)."""

from ._stub_engine import (
    HISTORICAL_ENGINES,
    TEST_ENGINE_AB,
    TEST_ENGINE_DRY,
    StubEngineDeck,
    resolve_engine,
)
from .performance import (
    PerformanceReport,
    compute_inlet_pressure_recovery,
    compute_installed_thrust_N,
    compute_installed_tsfc,
    evaluate,
)

__all__ = [
    "HISTORICAL_ENGINES",
    "TEST_ENGINE_AB",
    "TEST_ENGINE_DRY",
    "StubEngineDeck",
    "resolve_engine",
    "PerformanceReport",
    "compute_inlet_pressure_recovery",
    "compute_installed_thrust_N",
    "compute_installed_tsfc",
    "evaluate",
]
