"""AI Airframer Company Lifecycle, Doctrine-Weighted R&D Selection, and Market Exit Logic.

Implements Module 07 (`sim/mic/ai/company_ai.py`):
- Loads the 13 historical US airframers (`airframers_us_1945_1960.json`) and 29 chief designers
  (`chief_designers_us_1945_1960.json`).
- Initializes non-player AI airframers with synchronized `CompanyState` (Module 04) and
  `CompanyTechState` (Module 03).
- Scores and selects tech tree research projects weighted by `ai_doctrine`, `traits`,
  customer affinity (`USAF` vs `USN`), and active Chief Designer branch bonuses.
- Executes deterministic monthly AI company ticks (`step_ai_company_month`) including
  chief designer succession, workforce/facility management, R&D progression, financial
  settlement, and dynamic/historical exit from prime fighter bidding.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from ..econ.company import CompanyState, step_company_month
from ..tech.catalog import TechCatalog, TechNode, load_catalog
from ..tech.context import TechContext
from ..tech.research import (
    CompanyTechState,
    ahead_of_time_multiplier,
    step_company_tech_day,
)
from .tuning import get_company_signature, load_ai_tuning

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_AIRFRAMERS_PATH = _DATA_DIR / "companies" / "airframers_us_1945_1960.json"
_DESIGNERS_PATH = _DATA_DIR / "companies" / "chief_designers_us_1945_1960.json"


def load_airframers_raw(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load raw airframer records from `sim/data/companies/airframers_us_1945_1960.json`."""
    p = Path(path) if path is not None else _AIRFRAMERS_PATH
    with open(p, "r", encoding="utf-8") as fh:
        return list(json.load(fh)["airframers"])


def load_chief_designers_map(path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """Load chief designer records keyed by `id` from `chief_designers_us_1945_1960.json`."""
    p = Path(path) if path is not None else _DESIGNERS_PATH
    with open(p, "r", encoding="utf-8") as fh:
        designers = json.load(fh)["designers"]
    return {str(d["id"]): dict(d) for d in designers}


def _year_month_to_day(year: int, month: int, day_of_month: int = 1) -> int:
    from datetime import date

    return (date(int(year), int(month), int(day_of_month)) - date(1945, 1, 1)).days


@dataclass
class AICompanyState:
    """Complete state for an AI-controlled aircraft manufacturer."""

    id: str
    name: str
    name_key: str
    hq_location: str
    company_code_usn: str
    tier: str
    company_state: CompanyState
    tech_state: CompanyTechState
    ai_doctrine: Dict[str, Any]
    traits: Dict[str, Any]
    chief_designer_id: str
    secondary_designer_id: Optional[str]
    active_designer_id: str
    designer_branch_bonuses: Dict[str, float] = field(default_factory=dict)
    designer_modifiers: Dict[str, float] = field(default_factory=dict)
    active_in_fighter_market: bool = True
    exit_reason: Optional[str] = None
    exit_year: Optional[int] = None
    won_major_production_contract: bool = False
    active_rfp_bids: List[str] = field(default_factory=list)
    model_seq: int = 100

    @property
    def cash_usd(self) -> float:
        return float(self.company_state.cash_usd)

    @property
    def reputation(self) -> Dict[str, float]:
        return self.company_state.reputation

    @property
    def engineers(self) -> Dict[str, float]:
        return self.company_state.engineers

    @property
    def facilities(self) -> Dict[str, Any]:
        return self.company_state.facilities

    def tech_context(self, catalog: Optional[TechCatalog] = None) -> TechContext:
        return self.tech_state.context(catalog=catalog)

    def next_model_designation(self) -> str:
        prefix = str(self.traits.get("model_prefix", self.id[:2].upper()))
        num = self.model_seq
        self.model_seq += 1
        return f"{prefix}-{num}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_key": self.name_key,
            "tier": self.tier,
            "cash_usd": round(self.company_state.cash_usd, 2),
            "debt_usd": round(self.company_state.debt_usd, 2),
            "credit_rating": self.company_state.credit_rating,
            "reputation": {k: round(float(v), 2) for k, v in sorted(self.company_state.reputation.items())},
            "political_capital": round(float(self.company_state.political_capital), 2),
            "engineers": {k: round(float(v), 2) for k, v in sorted(self.company_state.engineers.items())},
            "facilities": dict(self.company_state.facilities),
            "active_designer_id": self.active_designer_id,
            "unlocked_tech_count": len(self.tech_state.unlocked_maturity),
            "active_research_projects": sorted(self.tech_state.projects.keys()),
            "active_in_fighter_market": self.active_in_fighter_market,
            "exit_reason": self.exit_reason,
            "exit_year": self.exit_year,
            "won_major_production_contract": self.won_major_production_contract,
        }


def create_ai_company_from_record(
    record: Mapping[str, Any],
    date_day: int = 0,
    designers_map: Optional[Mapping[str, Dict[str, Any]]] = None,
    catalog: Optional[TechCatalog] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> AICompanyState:
    """Create an `AICompanyState` from a JSON entry in `airframers_us_1945_1960.json`."""
    cat = catalog if catalog is not None else load_catalog()
    d_map = designers_map if designers_map is not None else load_chief_designers_map()
    t = tuning if tuning is not None else load_ai_tuning()

    cid = str(record["id"])
    raw_rep = dict(record.get("reputation", {"USAF": 0.60, "USN": 0.60, "export": 0.50}))
    rep_100: Dict[str, float] = {}
    for k, v in raw_rep.items():
        fv = float(v)
        rep_100[str(k)] = fv * 100.0 if fv <= 1.0 else fv

    raw_pc = float(record.get("political_capital", 0.50))
    pc_100 = raw_pc * 100.0 if raw_pc <= 1.0 else raw_pc

    eng_dict = {
        str(k): float(v)
        for k, v in record.get(
            "engineers", {"aero": 45.0, "structures": 45.0, "propulsion": 15.0, "systems": 35.0}
        ).items()
    }
    fac_raw = dict(record.get("facilities", {}))
    facilities = {
        "wind_tunnel_level": int(fac_raw.get("wind_tunnel_level", 1)),
        "factory_floor_m2": float(fac_raw.get("factory_floor_m2", 120000.0)),
        "goco_floor_m2": float(fac_raw.get("goco_floor_m2", 0.0)),
        "test_site": bool(fac_raw.get("test_site", False)),
        "nc_machining_installed": bool(fac_raw.get("nc_machining_installed", False)),
    }

    tier = str(record.get("tier", "mid_prime"))
    if tier in ("major_prime", "legacy_giant"):
        comm_buffer = "civil_diversified" if cid in ("douglas", "lockheed", "convair", "boeing", "curtiss_wright") else "subcontracting"
        fleet_init = 600
    else:
        comm_buffer = "subcontracting"
        fleet_init = 280

    primary_des_id = str(record.get("chief_designer_id", ""))
    secondary_des_id = record.get("secondary_designer_id")
    secondary_des_str = str(secondary_des_id) if secondary_des_id else None

    des_info = d_map.get(primary_des_id, {})
    branch_bonuses = {
        str(k): float(v) for k, v in des_info.get("research_branch_bonuses", {}).items()
    }
    des_modifiers = {
        "cd0_refinement_factor": 1.0,
        "prototype_build_time_factor": 1.0,
        "structural_mass_factor": 1.0,
    }
    for mk, mv in des_info.get("design_modifiers", {}).items():
        des_modifiers[str(mk)] = float(mv)

    extra_tech = {
        str(k): float(v) for k, v in record.get("starting_tech_overrides", {}).items()
    }
    tech_state = CompanyTechState.create_starting_1945(
        company_id=cid,
        date_day=date_day,
        extra_unlocked=extra_tech,
        designer_branch_bonuses=branch_bonuses,
        catalog=cat,
    )

    comp_state = CompanyState(
        id=cid,
        name=str(record.get("name_key", cid)),
        is_player=False,
        cash_usd=float(record.get("cash_usd", 20000000.0)),
        debt_usd=float(record.get("debt_usd", 0.0)),
        reputation=rep_100,
        political_capital=pc_100,
        engineers=eng_dict,
        facilities=facilities,
        tech_unlocked=sorted(tech_state.unlocked_maturity.keys()),
        commercial_buffer_level=comm_buffer,
        active_delivered_fleet=fleet_init,
    )

    doctrine = dict(record.get("ai_doctrine", {}))
    sig = get_company_signature(cid, tuning=t)
    traits = {**sig, **doctrine}

    return AICompanyState(
        id=cid,
        name=str(record.get("name_key", cid)),
        name_key=str(record.get("name_key", f"company.{cid}.name")),
        hq_location=str(record.get("hq_location", "USA")),
        company_code_usn=str(record.get("company_code_usn", cid[:1].upper())),
        tier=tier,
        company_state=comp_state,
        tech_state=tech_state,
        ai_doctrine=doctrine,
        traits=traits,
        chief_designer_id=primary_des_id,
        secondary_designer_id=secondary_des_str,
        active_designer_id=primary_des_id,
        designer_branch_bonuses=branch_bonuses,
        designer_modifiers=des_modifiers,
    )


def load_ai_airframers(
    exclude_player_company_id: Optional[str] = "north_american",
    date_day: int = 0,
    catalog: Optional[TechCatalog] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, AICompanyState]:
    """Load all non-player US airframers (12 when player selects a historical airframer, 13 for custom startup)."""
    cat = catalog if catalog is not None else load_catalog()
    t = tuning if tuning is not None else load_ai_tuning()
    d_map = load_chief_designers_map()
    raw_list = load_airframers_raw()

    out: Dict[str, AICompanyState] = {}
    for rec in raw_list:
        cid = str(rec["id"])
        if exclude_player_company_id and cid == exclude_player_company_id:
            continue
        out[cid] = create_ai_company_from_record(
            rec,
            date_day=date_day,
            designers_map=d_map,
            catalog=cat,
            tuning=t,
        )
    return out


def score_tech_node_for_ai(
    node: TechNode,
    ai_company: AICompanyState,
    date_day: int,
    catalog: Optional[TechCatalog] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute deterministic doctrine-weighted priority score for an unlockable `TechNode`."""
    cat = catalog if catalog is not None else load_catalog()
    t = (tuning if tuning is not None else load_ai_tuning())["company_ai"]

    current_year = 1945.0 + float(date_day) / 365.25
    years_ahead = float(node.historical_year) - current_year
    ambition = float(ai_company.ai_doctrine.get("aerodynamic_ambition", 0.75))
    max_lead = float(t["rnd_year_window_lead"]) + (1.0 if ambition >= 0.90 else 0.0)
    if years_ahead > max_lead:
        return -1.0

    m_aot = ahead_of_time_multiplier(date_day, node.historical_year, catalog=cat)
    aot_factor = m_aot ** float(t["rnd_aot_penalty_weight"])

    align = 1.0
    # 1. Chief designer branch bonus
    branch_bonus = float(ai_company.designer_branch_bonuses.get(node.branch, 0.0))
    align += float(t["rnd_designer_bonus_scale"]) * branch_bonus

    # 2. Company doctrine & signature alignment
    speed_bias = float(ai_company.ai_doctrine.get("speed_vs_maneuver_bias", 0.50))
    mfg_focus = float(ai_company.ai_doctrine.get("production_scalability_focus", 0.75))
    pref_cust = list(ai_company.ai_doctrine.get("preferred_customers", ["USAF"]))
    delta_bias = float(ai_company.traits.get("delta_bias", 0.10))

    if node.branch == "aero":
        align += float(t["rnd_doctrine_aero_weight"]) * ambition
    elif node.branch == "manufacturing":
        align += 0.35 * mfg_focus
    elif node.branch == "structures":
        align += 0.25 * float(ai_company.traits.get("ruggedness_g_bias", 0.10) + 0.5)

    eff_keys = set(node.effects.keys())
    if "aero.delta_wing" in eff_keys or "aero.conical_camber" in eff_keys:
        align += 0.85 * delta_bias - 0.20 * (1.0 - delta_bias)
    if any(
        k in eff_keys
        for k in (
            "aero.wing_sweep_max_deg",
            "aero.thin_wing_tc_min",
            "aero.area_rule",
            "aero.inlet_spike",
            "aero.inlet_variable",
            "engine.afterburner",
        )
    ):
        align += float(t["rnd_doctrine_speed_weight"]) * speed_bias

    # Carrier technology affinity for USN vs USAF specialists
    is_carrier_node = "carrier" in node.id or any("carrier" in k for k in eff_keys)
    if is_carrier_node:
        if "USN" in pref_cust:
            align += float(t["rnd_carrier_weight_usn"]) * (1.3 if pref_cust[0] == "USN" else 0.8)
        else:
            align -= 0.45

    cost_factor = (500.0 / max(150.0, float(node.cost_eng_days))) ** 0.25
    # Slight boost for nodes that are already past their historical year (catch-up urgency)
    catchup_urgency = 1.0 + max(0.0, min(0.60, (current_year - float(node.historical_year)) * 0.15))

    return max(0.01, align * aot_factor * cost_factor * catchup_urgency)


def select_ai_research_projects(
    ai_company: AICompanyState,
    date_day: int,
    catalog: Optional[TechCatalog] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> List[Tuple[str, int]]:
    """Select and allocate engineers to up to `rnd_max_concurrent_projects` tech nodes."""
    cat = catalog if catalog is not None else load_catalog()
    t = (tuning if tuning is not None else load_ai_tuning())["company_ai"]

    if ai_company.company_state.cash_usd < float(t["rnd_irad_cash_floor_usd"]):
        # Pause discretionary IR&D when cash drops below safety floor
        for proj in ai_company.tech_state.projects.values():
            proj.assigned_engineers = 0
        return []

    scored: List[Tuple[float, str]] = []
    for tid, node in sorted(cat.nodes.items()):
        if not ai_company.tech_state.can_start_research(tid, catalog=cat):
            continue
        sc = score_tech_node_for_ai(node, ai_company, date_day, catalog=cat, tuning=tuning)
        if sc > 0.0:
            # Bonus for continuing an already partially researched project
            if tid in ai_company.tech_state.projects or ai_company.tech_state.partial_progress.get(tid, 0.0) > 0.0:
                sc *= 1.25
            scored.append((sc, tid))

    scored.sort(key=lambda item: (-item[0], item[1]))
    max_proj = int(t["rnd_max_concurrent_projects"])
    chosen = scored[:max_proj]

    # Clear allocations on non-chosen projects
    chosen_ids = {tid for _, tid in chosen}
    for tid, proj in list(ai_company.tech_state.projects.items()):
        if tid not in chosen_ids:
            proj.assigned_engineers = 0

    if not chosen:
        return []

    total_eng = ai_company.company_state.total_engineers_fte
    avail_rnd_eng = int(round(max(20.0, total_eng * 0.45)))
    min_per = int(t["rnd_min_engineers_per_project"])
    max_per = int(t["rnd_max_engineers_per_project"])

    total_score = sum(sc for sc, _ in chosen)
    allocations: List[Tuple[str, int]] = []
    for sc, tid in chosen:
        share = sc / max(1e-6, total_score)
        eng_assigned = max(min_per, min(max_per, int(round(avail_rnd_eng * share))))
        ai_company.tech_state.start_or_update_project(
            tech_id=tid,
            assigned_engineers=eng_assigned,
            funding_mode="irad",
            budget_throttle=1.0,
            catalog=cat,
        )
        allocations.append((tid, eng_assigned))

    return allocations


def _update_chief_designer_succession(
    ai_company: AICompanyState,
    year: int,
    designers_map: Optional[Mapping[str, Dict[str, Any]]] = None,
) -> bool:
    """Check and execute historical Chief Designer succession if applicable."""
    if not ai_company.secondary_designer_id:
        return False
    if ai_company.active_designer_id == ai_company.secondary_designer_id:
        return False
    d_map = designers_map if designers_map is not None else load_chief_designers_map()
    prim = d_map.get(ai_company.chief_designer_id)
    sec = d_map.get(ai_company.secondary_designer_id)
    if not prim or not sec:
        return False

    prim_end = int(prim.get("active_years", [1945, 1960])[1])
    sec_start = int(sec.get("active_years", [1945, 1960])[0])
    if year > prim_end and year >= sec_start:
        ai_company.active_designer_id = ai_company.secondary_designer_id
        ai_company.designer_branch_bonuses = {
            str(k): float(v) for k, v in sec.get("research_branch_bonuses", {}).items()
        }
        ai_company.tech_state.designer_branch_bonuses = dict(ai_company.designer_branch_bonuses)
        for mk, mv in sec.get("design_modifiers", {}).items():
            ai_company.designer_modifiers[str(mk)] = float(mv)
        return True
    return False


def step_ai_company_month(
    ai_company: AICompanyState,
    year: int,
    month: int,
    days_in_month: int = 30,
    run_full_econ: bool = True,
    catalog: Optional[TechCatalog] = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute one deterministic monthly lifecycle tick for an AI airframer (`step_ai_company_month`).

    1. Checks Chief Designer succession (`chief_designers_us_1945_1960.json`).
    2. Selects & allocates engineers to tech tree research projects weighted by company doctrine.
    3. Advances daily tech research & NACA diffusion across `days_in_month`.
    4. Adjusts target engineering workforce, wind-tunnel upgrades, and lobbying spend.
    5. Settles monthly corporate finances via `step_company_month` (Module 04).
    6. Evaluates solvency and historical/dynamic prime fighter market exit rules.
    """
    cat = catalog if catalog is not None else load_catalog()
    t_all = tuning if tuning is not None else load_ai_tuning()
    t = t_all["company_ai"]

    date_day = _year_month_to_day(year, month, 1)
    ai_company.tech_state.date_day = date_day

    designer_switched = _update_chief_designer_succession(ai_company, year)
    allocations = select_ai_research_projects(ai_company, date_day, catalog=cat, tuning=t_all)

    newly_unlocked_month: List[str] = []
    irad_tech_spend_usd = 0.0
    for _ in range(max(1, int(days_in_month))):
        step_res = step_company_tech_day(ai_company.tech_state, catalog=cat)
        if step_res.newly_unlocked:
            newly_unlocked_month.extend(step_res.newly_unlocked)
        irad_tech_spend_usd += step_res.company_cost_usd

    ai_company.company_state.tech_unlocked = sorted(ai_company.tech_state.unlocked_maturity.keys())
    ai_company.company_state.irad_monthly_spend_usd = irad_tech_spend_usd

    # Facility upgrade decision (wind tunnel)
    wt_lvl = int(ai_company.company_state.facilities.get("wind_tunnel_level", 1))
    ambition = float(ai_company.ai_doctrine.get("aerodynamic_ambition", 0.75))
    tunnel_upgraded = False
    if (
        wt_lvl < 2
        and year >= int(t["tunnel_upgrade_year_lvl2"])
        and ai_company.company_state.cash_usd >= float(t["min_cash_usd_for_tunnel_upgrade"])
        and ambition >= 0.75
    ):
        ai_company.company_state.facilities["wind_tunnel_level"] = 2
        ai_company.company_state.cash_usd -= 1200000.0
        tunnel_upgraded = True
    elif (
        wt_lvl == 2
        and year >= int(t["tunnel_upgrade_year_lvl3"])
        and ai_company.company_state.cash_usd >= float(t["min_cash_usd_for_tunnel_upgrade"]) * 1.35
        and ambition >= 0.85
    ):
        ai_company.company_state.facilities["wind_tunnel_level"] = 3
        ai_company.company_state.cash_usd -= 2350000.0
        tunnel_upgraded = True

    # Workforce target & lobbying budget
    active_contracts = [c for c in ai_company.company_state.contracts if not c.completed]
    if any(c.phase == "production" and c.quantity >= 50 for c in active_contracts):
        ai_company.won_major_production_contract = True

    est_monthly_burn = max(250000.0, ai_company.company_state.total_engineers_fte * 1400.0)
    runway_months = ai_company.company_state.cash_usd / est_monthly_burn

    target_eng: Dict[str, float] = {}
    if active_contracts and runway_months >= float(t["min_cash_months_for_hiring"]):
        growth = 1.0 + min(float(t["target_eng_growth_rate_max"]), 0.02)
        for d, v in ai_company.company_state.engineers.items():
            target_eng[d] = min(140.0, float(v) * growth)
    elif not active_contracts and runway_months < float(t["distress_cash_months_for_layoffs"]):
        shrink = 1.0 - min(float(t["target_eng_shrink_rate_max"]), 0.03)
        for d, v in ai_company.company_state.engineers.items():
            target_eng[d] = max(12.0, float(v) * shrink)
    else:
        target_eng = dict(ai_company.company_state.engineers)

    if ai_company.company_state.cash_usd > 8000000.0 and ai_company.active_in_fighter_market:
        ai_company.company_state.lobbying_monthly_spend_usd = min(
            float(t["lobbying_max_monthly_usd"]),
            ai_company.company_state.cash_usd * float(t["lobbying_budget_frac_of_cash"]),
        )
    else:
        ai_company.company_state.lobbying_monthly_spend_usd = 0.0

    if run_full_econ:
        econ_report = step_company_month(
            ai_company.company_state,
            year=year,
            month=month,
            target_engineers=target_eng,
            advance_projects_in_month=True,
            auto_borrow_revolver=True,
            allow_chapter_xi=True,
        )
    else:
        econ_report = {
            "ending_cash_usd": ai_company.company_state.cash_usd,
            "is_bankrupt_or_acquired": ai_company.company_state.is_bankrupt_or_acquired,
        }

    # Market exit evaluation
    hist_exits = t.get("historical_exit_years", {})
    if ai_company.active_in_fighter_market:
        if (
            ai_company.company_state.is_bankrupt_or_acquired
            or ai_company.company_state.cash_usd < float(t["insolvency_exit_cash_threshold_usd"])
        ):
            ai_company.active_in_fighter_market = False
            ai_company.exit_reason = "insolvency"
            ai_company.exit_year = int(year)
        elif ai_company.id in hist_exits and int(year) >= int(hist_exits[ai_company.id]):
            keep_alive = bool(t.get("alt_history_contract_keeps_alive", True))
            has_fighter_work = bool(active_contracts) or (
                keep_alive and ai_company.won_major_production_contract
            )
            if not has_fighter_work:
                ai_company.active_in_fighter_market = False
                ai_company.exit_reason = "historical_pivot_to_bombers_or_missiles"
                ai_company.exit_year = int(year)

    return {
        "company_id": ai_company.id,
        "year": int(year),
        "month": int(month),
        "designer_switched": designer_switched,
        "active_designer_id": ai_company.active_designer_id,
        "research_allocations": allocations,
        "newly_unlocked_techs": newly_unlocked_month,
        "tunnel_upgraded": tunnel_upgraded,
        "ending_cash_usd": float(ai_company.company_state.cash_usd),
        "active_in_fighter_market": ai_company.active_in_fighter_market,
        "exit_reason": ai_company.exit_reason,
        "econ_report": econ_report,
    }
