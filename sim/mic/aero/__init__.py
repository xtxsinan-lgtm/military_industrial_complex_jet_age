"""Module 01 Aerodynamics package (`sim.mic.aero`)."""

from .airfoil import (
    AirfoilSectionResult,
    evaluate_cst,
    fit_cst_to_coordinates,
    parse_and_analyze_airfoil,
)
from .diagnostics import compute_aero_diagnostics
from .drag import (
    HighLiftConfigProperties,
    WaveDragSummary,
    compute_cd0_subsonic,
    compute_cl_max_mach,
    compute_high_lift_properties,
    compute_induced_drag_k,
    compute_mdd_and_mcrit,
    compute_total_drag_cd,
    compute_wave_drag_cdw,
    compute_wave_drag_summary,
)
from .geometry import (
    DerivedAircraftGeometry,
    DerivedEmpennageGeometry,
    DerivedFuselageGeometry,
    DerivedWingGeometry,
    convert_sweep_rad,
    derive_aircraft_geometry,
    get_tech_value,
    validate_design,
)
from .mass import MassBreakdown, compute_mass_breakdown
from .tuning import load_aero_tuning
from .vlm import VLMResult, compute_cl_alpha_mach, solve_wing_vlm

__all__ = [
    "AirfoilSectionResult",
    "evaluate_cst",
    "fit_cst_to_coordinates",
    "parse_and_analyze_airfoil",
    "compute_aero_diagnostics",
    "HighLiftConfigProperties",
    "WaveDragSummary",
    "compute_cd0_subsonic",
    "compute_cl_max_mach",
    "compute_high_lift_properties",
    "compute_induced_drag_k",
    "compute_mdd_and_mcrit",
    "compute_total_drag_cd",
    "compute_wave_drag_cdw",
    "compute_wave_drag_summary",
    "DerivedAircraftGeometry",
    "DerivedEmpennageGeometry",
    "DerivedFuselageGeometry",
    "DerivedWingGeometry",
    "convert_sweep_rad",
    "derive_aircraft_geometry",
    "get_tech_value",
    "validate_design",
    "MassBreakdown",
    "compute_mass_breakdown",
    "load_aero_tuning",
    "VLMResult",
    "compute_cl_alpha_mach",
    "solve_wing_vlm",
]
