"""Research progress, IRAD vs govt contracts, NACA diffusion, and maturity growth (Module 03)."""

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

from .catalog import TechCatalog, TechNode, day_to_year, load_catalog
from .context import TechContext, build_tech_context


LEARNING_EVENT_TUNABLE_KEYS: Dict[str, str] = {
    "sim_run": "maturity_gain_sim_run",
    "tunnel_campaign": "maturity_gain_tunnel_campaign",
    "first_flight": "maturity_gain_first_flight",
    "flight_test_sortie": "maturity_gain_flight_test_sortie",
    "flaw_fixed": "maturity_gain_flaw_fixed",
    "production_10_units": "maturity_gain_production_10_units",
}


@dataclass
class ResearchProject:
    """Active or partially progressed research project on a single tech node."""

    tech_id: str
    assigned_engineers: int = 0
    funding_mode: str = "irad"  # "irad" | "govt_contract"
    progress_eng_days: float = 0.0
    company_usd_spent: float = 0.0
    govt_usd_spent: float = 0.0
    budget_throttle: float = 1.0  # in [0, 1]


@dataclass
class DailyTechStepResult:
    """Summary of one daily tick for a company's tech & research state."""

    date_day: int
    newly_unlocked: List[str]
    progress_deltas: Dict[str, float]
    company_cost_usd: float
    govt_cost_usd: float
    context: TechContext


@dataclass
class CompanyTechState:
    """Mutable tech & research state for one company."""

    company_id: str
    date_day: int = 0
    unlocked_maturity: Dict[str, float] = field(default_factory=dict)
    projects: Dict[str, ResearchProject] = field(default_factory=dict)
    partial_progress: Dict[str, float] = field(default_factory=dict)
    designer_branch_bonuses: Dict[str, float] = field(default_factory=dict)
    _cached_context: Optional[TechContext] = field(default=None, init=False, repr=False)

    @classmethod
    def create_starting_1945(
        cls,
        company_id: str,
        date_day: int = 0,
        extra_unlocked: Optional[Mapping[str, float]] = None,
        designer_branch_bonuses: Optional[Mapping[str, float]] = None,
        catalog: Optional[TechCatalog] = None,
    ) -> "CompanyTechState":
        cat = catalog if catalog is not None else load_catalog()
        unlocked = cat.baseline_unlocked_maturity()
        if extra_unlocked:
            for tid, mat in extra_unlocked.items():
                if tid not in cat.nodes:
                    raise KeyError(f"Unknown starting tech_id: {tid}")
                unlocked[str(tid)] = max(0.0, min(1.0, float(mat)))
        bonuses = dict(designer_branch_bonuses) if designer_branch_bonuses else {}
        return cls(
            company_id=company_id,
            date_day=date_day,
            unlocked_maturity=unlocked,
            designer_branch_bonuses=bonuses,
        )

    def context(self, catalog: Optional[TechCatalog] = None) -> TechContext:
        if self._cached_context is None or self._cached_context.date_day != self.date_day:
            self._cached_context = build_tech_context(
                company_id=self.company_id,
                date_day=self.date_day,
                unlocked_maturity=self.unlocked_maturity,
                catalog=catalog,
            )
        return self._cached_context

    def invalidate_context(self) -> None:
        self._cached_context = None

    def can_start_research(self, tech_id: str, catalog: Optional[TechCatalog] = None) -> bool:
        cat = catalog if catalog is not None else load_catalog()
        node = cat.get_node(tech_id)
        if tech_id in self.unlocked_maturity:
            return False
        return all(p in self.unlocked_maturity for p in node.prereqs)

    def start_or_update_project(
        self,
        tech_id: str,
        assigned_engineers: int,
        funding_mode: str = "irad",
        budget_throttle: float = 1.0,
        catalog: Optional[TechCatalog] = None,
    ) -> ResearchProject:
        cat = catalog if catalog is not None else load_catalog()
        node = cat.get_node(tech_id)
        if tech_id in self.unlocked_maturity:
            raise ValueError(f"Tech {tech_id} is already unlocked")
        missing = [p for p in node.prereqs if p not in self.unlocked_maturity]
        if missing:
            raise ValueError(f"Cannot research {tech_id}; missing prereqs: {missing}")
        if funding_mode not in ("irad", "govt_contract"):
            raise ValueError(f"Invalid funding_mode: {funding_mode}")
        if funding_mode == "govt_contract" and not node.govt_contract_eligible:
            raise ValueError(f"Tech {tech_id} is not eligible for government contract funding")
        if assigned_engineers < 0:
            raise ValueError("assigned_engineers must be >= 0")

        existing = self.projects.get(tech_id)
        init_prog = self.partial_progress.get(tech_id, 0.0)
        if existing is not None:
            existing.assigned_engineers = int(assigned_engineers)
            existing.funding_mode = funding_mode
            existing.budget_throttle = max(0.0, min(1.0, float(budget_throttle)))
            return existing

        proj = ResearchProject(
            tech_id=tech_id,
            assigned_engineers=int(assigned_engineers),
            funding_mode=funding_mode,
            progress_eng_days=init_prog,
            budget_throttle=max(0.0, min(1.0, float(budget_throttle))),
        )
        self.projects[tech_id] = proj
        return proj


def effective_engineers(
    assigned_engineers: int,
    catalog: Optional[TechCatalog] = None,
) -> float:
    """Compute Brooks's Law effective engineer-equivalents for a single research project."""
    if assigned_engineers <= 0:
        return 0.0
    cat = catalog if catalog is not None else load_catalog()
    t = cat.tunables
    thresh = t["diminishing_returns_threshold_eng"]
    exp = t["diminishing_returns_exponent"]
    max_eff = t["max_effective_engineers_per_project"]

    n = float(assigned_engineers)
    if n <= thresh:
        eff = n
    else:
        eff = thresh + ((n - thresh) ** exp)
    return min(max_eff, eff)


def ahead_of_time_multiplier(
    date_day: int,
    historical_year: float,
    catalog: Optional[TechCatalog] = None,
) -> float:
    """Compute ahead-of-time penalty (<1) or behind-time catch-up bonus (>1) at date_day."""
    cat = catalog if catalog is not None else load_catalog()
    t = cat.tunables
    current_yr = day_to_year(date_day)
    free_lead = t["aot_free_lead_years"]
    early_years = (float(historical_year) - free_lead) - current_yr

    if early_years > 0.0:
        rate = t["aot_rate_per_year"]
        exp = t["aot_exponent"]
        floor = t["aot_min_speed_multiplier"]
        mult = 1.0 / (1.0 + rate * (early_years ** exp))
        return max(floor, mult)

    if current_yr > float(historical_year):
        late_years = current_yr - float(historical_year)
        catchup_rate = t["catchup_rate_per_year"]
        catchup_max = t["catchup_max_speed_multiplier"]
        return min(catchup_max, 1.0 + catchup_rate * late_years)

    return 1.0


def naca_report_multiplier(
    node: TechNode,
    date_day: int,
    catalog: Optional[TechCatalog] = None,
) -> float:
    """Return NACA Technical Note speed bonus if node is NACA-diffused and past diffusion lag."""
    cat = catalog if catalog is not None else load_catalog()
    if not node.naca_diffusion:
        return 1.0
    t = cat.tunables
    current_yr = day_to_year(date_day)
    if current_yr >= node.historical_year + t["naca_diffusion_lag_years"]:
        return t["naca_report_speed_multiplier"]
    return 1.0


def funding_multipliers(
    funding_mode: str,
    node: TechNode,
    catalog: Optional[TechCatalog] = None,
) -> Tuple[float, float]:
    """Return (speed_multiplier, company_cost_share) for 'irad' vs 'govt_contract'."""
    cat = catalog if catalog is not None else load_catalog()
    t = cat.tunables
    if funding_mode == "irad":
        return 1.0, t["irad_company_cost_share"]
    if funding_mode == "govt_contract":
        if not node.govt_contract_eligible:
            raise ValueError(f"Node {node.id} is not eligible for government contract funding")
        return t["govt_contract_speed_multiplier"], t["govt_contract_company_cost_share"]
    raise ValueError(f"Unknown funding_mode: {funding_mode}")


def compute_daily_active_progress(
    node: TechNode,
    project: ResearchProject,
    date_day: int,
    ctx: TechContext,
    designer_branch_bonus: float = 0.0,
    catalog: Optional[TechCatalog] = None,
) -> Tuple[float, float, float]:
    """Compute (active_eng_days_progress, company_usd, govt_usd) for one day on project."""
    cat = catalog if catalog is not None else load_catalog()
    t = cat.tunables
    if project.assigned_engineers <= 0 or project.budget_throttle <= 0.0:
        return 0.0, 0.0, 0.0

    n_eff = effective_engineers(project.assigned_engineers, catalog=cat)
    m_aot = ahead_of_time_multiplier(date_day, node.historical_year, catalog=cat)
    m_naca = naca_report_multiplier(node, date_day, catalog=cat)
    m_fund, company_share = funding_multipliers(project.funding_mode, node, catalog=cat)
    disc_key = f"research.speed_factor.{node.discipline}"
    m_disc = float(ctx.get(disc_key)) if disc_key in ctx.values else 1.0
    m_designer = max(0.5, 1.0 + float(designer_branch_bonus))

    raw_progress = (
        t["eng_efficiency_per_day"]
        * n_eff
        * m_aot
        * m_naca
        * m_fund
        * m_disc
        * m_designer
        * project.budget_throttle
    )
    remaining = max(0.0, float(node.cost_eng_days) - project.progress_eng_days)
    actual_progress = min(remaining, raw_progress)

    frac_completed = actual_progress / float(node.cost_eng_days) if node.cost_eng_days > 0 else 0.0
    total_usd_step = frac_completed * node.cost_usd
    comp_usd = total_usd_step * company_share
    govt_usd = total_usd_step * (1.0 - company_share)
    return actual_progress, comp_usd, govt_usd


def step_company_tech_day(
    state: CompanyTechState,
    catalog: Optional[TechCatalog] = None,
) -> DailyTechStepResult:
    """Advance a company's research projects, NACA diffusion, and tech maturities by 1 day."""
    cat = catalog if catalog is not None else load_catalog()
    t = cat.tunables
    date_day = state.date_day
    current_yr = day_to_year(date_day)
    ctx = state.context(catalog=cat)

    # 1. Passive daily maturity growth for already-unlocked techs (before today's new unlocks)
    passive_rate = t["passive_maturity_rate_per_day"]
    passive_cap = t["passive_maturity_cap"]
    maturity_changed = False
    for tid in list(state.unlocked_maturity.keys()):
        cur_m = state.unlocked_maturity[tid]
        if cur_m < passive_cap:
            new_m = min(passive_cap, cur_m + passive_rate)
            if new_m != cur_m:
                state.unlocked_maturity[tid] = new_m
                maturity_changed = True

    progress_deltas: Dict[str, float] = {}
    total_company_usd = 0.0
    total_govt_usd = 0.0
    newly_unlocked: List[str] = []

    # 2. Active research projects
    for tid, proj in sorted(state.projects.items()):
        if tid in state.unlocked_maturity:
            continue
        node = cat.get_node(tid)
        branch_bonus = state.designer_branch_bonuses.get(node.branch, 0.0)
        act_prog, comp_usd, govt_usd = compute_daily_active_progress(
            node=node,
            project=proj,
            date_day=date_day,
            ctx=ctx,
            designer_branch_bonus=branch_bonus,
            catalog=cat,
        )
        if act_prog > 0.0:
            proj.progress_eng_days += act_prog
            proj.company_usd_spent += comp_usd
            proj.govt_usd_spent += govt_usd
            state.partial_progress[tid] = proj.progress_eng_days
            progress_deltas[tid] = progress_deltas.get(tid, 0.0) + act_prog
            total_company_usd += comp_usd
            total_govt_usd += govt_usd

    # 3. Passive NACA diffusion drip across all eligible nodes whose prereqs were met at start of day
    naca_lag = t["naca_diffusion_lag_years"]
    naca_drip_frac = t["naca_passive_drip_frac_per_day"]
    if naca_drip_frac > 0.0:
        for tid, node in sorted(cat.nodes.items()):
            if tid in state.unlocked_maturity:
                continue
            if not node.naca_diffusion:
                continue
            if current_yr < node.historical_year + naca_lag:
                continue
            if not all(p in state.unlocked_maturity for p in node.prereqs):
                continue
            cur_prog = state.projects[tid].progress_eng_days if tid in state.projects else state.partial_progress.get(tid, 0.0)
            drip = min(max(0.0, float(node.cost_eng_days) - cur_prog), naca_drip_frac * float(node.cost_eng_days))
            if drip > 0.0:
                new_prog = cur_prog + drip
                state.partial_progress[tid] = new_prog
                if tid in state.projects:
                    state.projects[tid].progress_eng_days = new_prog
                progress_deltas[tid] = progress_deltas.get(tid, 0.0) + drip

    # 4. Check completions
    for tid in sorted(progress_deltas.keys()):
        node = cat.get_node(tid)
        prog = state.partial_progress.get(tid, 0.0)
        if prog + 1e-9 >= float(node.cost_eng_days):
            init_mat = node.initial_maturity if node.initial_maturity > 0.0 else t["default_unlock_maturity"]
            state.unlocked_maturity[tid] = init_mat
            state.partial_progress.pop(tid, None)
            state.projects.pop(tid, None)
            newly_unlocked.append(tid)
            maturity_changed = True

    state.date_day += 1
    if maturity_changed or newly_unlocked:
        state.invalidate_context()
    new_ctx = state.context(catalog=cat)

    return DailyTechStepResult(
        date_day=state.date_day,
        newly_unlocked=newly_unlocked,
        progress_deltas=progress_deltas,
        company_cost_usd=total_company_usd,
        govt_cost_usd=total_govt_usd,
        context=new_ctx,
    )


def apply_learning_by_doing(
    state: CompanyTechState,
    tech_ids: Iterable[str],
    event_type: str,
    scale: float = 1.0,
    catalog: Optional[TechCatalog] = None,
) -> Dict[str, float]:
    """Apply asymptotic learning-by-doing maturity boost to unlocked techs in tech_ids.

    Formula: m_new = min(max_maturity, m_old + gain * scale * (1.0 - m_old))
    Returns {tech_id: new_maturity} for updated techs.
    """
    if event_type not in LEARNING_EVENT_TUNABLE_KEYS:
        raise ValueError(f"Unknown learning event_type: {event_type}")
    cat = catalog if catalog is not None else load_catalog()
    t = cat.tunables
    gain_key = LEARNING_EVENT_TUNABLE_KEYS[event_type]
    base_gain = t[gain_key] * max(0.0, float(scale))
    max_mat = t["max_maturity"]

    updated: Dict[str, float] = {}
    for tid in sorted(set(tech_ids)):
        if tid not in state.unlocked_maturity:
            continue
        old_m = state.unlocked_maturity[tid]
        new_m = min(max_mat, old_m + base_gain * (1.0 - old_m))
        state.unlocked_maturity[tid] = new_m
        updated[tid] = new_m

    if updated:
        state.invalidate_context()
    return updated
