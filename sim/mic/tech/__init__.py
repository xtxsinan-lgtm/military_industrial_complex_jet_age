"""Module 03 — Technology Tree & Research Oracle (1945-1960)."""

from .catalog import (
    EffectKeySpec,
    TechCatalog,
    TechNode,
    date_str_to_day,
    day_to_year,
    load_catalog,
)
from .context import (
    TechContext,
    build_tech_context,
    extract_design_features,
    required_techs,
    required_techs_by_feature,
)
from .research import (
    CompanyTechState,
    DailyTechStepResult,
    ResearchProject,
    ahead_of_time_multiplier,
    apply_learning_by_doing,
    compute_daily_active_progress,
    effective_engineers,
    funding_multipliers,
    naca_report_multiplier,
    step_company_tech_day,
)

__all__ = [
    "EffectKeySpec",
    "TechCatalog",
    "TechNode",
    "date_str_to_day",
    "day_to_year",
    "load_catalog",
    "TechContext",
    "build_tech_context",
    "extract_design_features",
    "required_techs",
    "required_techs_by_feature",
    "CompanyTechState",
    "DailyTechStepResult",
    "ResearchProject",
    "ahead_of_time_multiplier",
    "apply_learning_by_doing",
    "compute_daily_active_progress",
    "effective_engineers",
    "funding_multipliers",
    "naca_report_multiplier",
    "step_company_tech_day",
]
