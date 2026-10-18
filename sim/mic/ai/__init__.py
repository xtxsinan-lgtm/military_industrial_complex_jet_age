"""Public API for Module 07 (`sim.mic.ai`): Competitor AI, Pre-Bid Rumors (D10), & Engine Vendors (D9)."""
from __future__ import annotations

from .bidding_ai import (
    AICompetitorEntry,
    prepare_ai_rfp_entry,
    prepare_all_ai_entries_for_rfp,
    run_ai_flyoff_progression,
    score_rfp_entry_for_ai,
    select_ai_bidders_for_rfp,
    step_all_ai_flyoff_finalists,
)
from .company_ai import (
    AICompanyState,
    create_ai_company_from_record,
    load_ai_airframers,
    load_airframers_raw,
    load_chief_designers_map,
    score_tech_node_for_ai,
    select_ai_research_projects,
    step_ai_company_month,
)
from .design_generator import (
    generate_ai_design_for_rfp,
    score_design_against_rfp,
)
from .engine_vendor_ai import (
    VENDOR_ALIASES,
    CustomEngineQuote,
    build_deck_from_calendar_entry,
    compare_vendor_quotes,
    get_available_catalog_engines,
    load_engine_makers_data,
    normalize_vendor_id,
    parse_date_to_day_and_year,
    quote_custom_engine,
)
from .rumors import (
    CompetitorRumor,
    generate_pre_bid_rumors,
    get_inquiry_cost,
)
from .tuning import (
    get_company_signature,
    load_ai_tuning,
)

__all__ = [
    "AICompetitorEntry",
    "AICompanyState",
    "CompetitorRumor",
    "CustomEngineQuote",
    "VENDOR_ALIASES",
    "build_deck_from_calendar_entry",
    "compare_vendor_quotes",
    "create_ai_company_from_record",
    "generate_ai_design_for_rfp",
    "generate_pre_bid_rumors",
    "get_available_catalog_engines",
    "get_company_signature",
    "get_inquiry_cost",
    "load_ai_airframers",
    "load_ai_tuning",
    "load_airframers_raw",
    "load_chief_designers_map",
    "load_engine_makers_data",
    "normalize_vendor_id",
    "parse_date_to_day_and_year",
    "prepare_ai_rfp_entry",
    "prepare_all_ai_entries_for_rfp",
    "quote_custom_engine",
    "run_ai_flyoff_progression",
    "score_design_against_rfp",
    "score_rfp_entry_for_ai",
    "score_tech_node_for_ai",
    "select_ai_bidders_for_rfp",
    "select_ai_research_projects",
    "step_ai_company_month",
    "step_all_ai_flyoff_finalists",
]
