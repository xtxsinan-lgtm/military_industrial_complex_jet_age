"""Engineering workforce management, hiring/firing, Brooks's Law, and project allocation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import math
from typing import Any, Dict, List, Mapping, Optional, Tuple

from .inflation import aero_cost_index_1950, benchmark_engineer_salary_usd_yr, labor_market_tightness
from .tuning import load_econ_tuning

DISCIPLINES: Tuple[str, ...] = ("aero", "structures", "propulsion", "systems")


@dataclass
class EngineeringProjectTask:
    """Engineering project consuming monthly/daily engineer hours inside `CompanyState.projects`."""

    project_id: str
    name: str
    kind: str = "airframe_subsonic"  # airframe_subsonic | airframe_supersonic | interceptor_all_weather | engine_dev | irad
    total_hours_required: float = 200000.0
    hours_completed: float = 0.0
    allocated_engineers: Dict[str, float] = field(
        default_factory=lambda: {"aero": 0.0, "structures": 0.0, "propulsion": 0.0, "systems": 0.0}
    )
    required_shares: Optional[Dict[str, float]] = None
    contract_id: Optional[str] = None
    is_irad_or_bp: bool = False
    completed: bool = False

    @property
    def progress_fraction(self) -> float:
        if self.total_hours_required <= 0.0:
            return 1.0
        return min(1.0, max(0.0, self.hours_completed / self.total_hours_required))

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["progress_fraction"] = self.progress_fraction
        return d


def brooks_law_efficiency(
    total_allocated_fte: float,
    newly_hired_fraction: float = 0.0,
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute team-scale & onboarding efficiency factor in `(0.25, 1.0]`.

    Models Fred Brooks's (*The Mythical Man-Month*, 1975) communication overhead on large
    engineering teams (`N > N_ref` scales effective throughput as `(N / N_ref)^(alpha - 1)`)
    and onboarding drag when a high fraction of engineers are newly hired (`newly_hired_fraction`).
    """
    cfg = (tuning if tuning is not None else load_econ_tuning())["workforce"]
    fte = max(0.0, float(total_allocated_fte))
    if fte <= 1e-6:
        return 1.0
    ref_fte = float(cfg["brooks_law_ref_team_fte"])
    exp_b = float(cfg["brooks_law_diminishing_exp"])
    scale_eff = 1.0 if fte <= ref_fte else ((fte / ref_fte) ** (exp_b - 1.0))
    onboard_drag = 1.0 - float(cfg["brooks_law_onboarding_drag"]) * min(max(float(newly_hired_fraction), 0.0), 1.0)
    return float(max(0.25, min(1.0, scale_eff * onboard_drag)))


def discipline_mix_efficiency(
    allocated_by_disc: Mapping[str, float],
    required_shares: Mapping[str, float],
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Compute discipline-balance efficiency factor in `[0.35, 1.0]` using total-variation distance.

    When a project needs share vector `q_d` across `(aero, structures, propulsion, systems)`
    and receives actual share vector `p_d`, total variation `TV = 0.5 * sum_d |p_d - q_d| in [0, 1]`
    reduces effective throughput by `1 - k * TV`.
    """
    cfg = (tuning if tuning is not None else load_econ_tuning())["workforce"]
    total = sum(max(0.0, float(allocated_by_disc.get(d, 0.0))) for d in DISCIPLINES)
    if total <= 1e-6:
        return 0.0
    req_sum = max(1e-9, sum(max(0.0, float(required_shares.get(d, 0.25))) for d in DISCIPLINES))
    tv = 0.5 * sum(
        abs((max(0.0, float(allocated_by_disc.get(d, 0.0))) / total) - (max(0.0, float(required_shares.get(d, 0.25))) / req_sum))
        for d in DISCIPLINES
    )
    k_pen = float(cfg["discipline_mismatch_penalty_k"])
    return float(max(0.35, 1.0 - k_pen * tv))


def compute_project_monthly_hours(
    allocated_by_disc: Mapping[str, float],
    project_kind: str = "airframe_subsonic",
    required_shares: Optional[Mapping[str, float]] = None,
    morale: float = 1.0,
    newly_hired_fraction: float = 0.0,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    """Return raw and effective engineering hours generated in one month on a project."""
    cfg = (tuning if tuning is not None else load_econ_tuning())["workforce"]
    hrs_per_fte = float(cfg["hours_per_fte_month"])
    total_fte = sum(max(0.0, float(allocated_by_disc.get(d, 0.0))) for d in DISCIPLINES)
    raw_hours = total_fte * hrs_per_fte

    if required_shares is None:
        shares_map = cfg["default_project_discipline_shares"]
        required_shares = shares_map.get(project_kind, shares_map["airframe_subsonic"])

    mix_eff = discipline_mix_efficiency(allocated_by_disc, required_shares, tuning=tuning)
    brooks_eff = brooks_law_efficiency(total_fte, newly_hired_fraction=newly_hired_fraction, tuning=tuning)
    morale_clamped = min(
        max(float(morale), float(cfg["morale_productivity_floor"])),
        float(cfg["morale_productivity_ceiling"]),
    )
    effective_hours = raw_hours * mix_eff * brooks_eff * morale_clamped
    return {
        "total_fte": float(total_fte),
        "raw_hours": float(raw_hours),
        "mix_efficiency": float(mix_eff),
        "brooks_efficiency": float(brooks_eff),
        "morale_factor": float(morale_clamped),
        "effective_hours": float(effective_hours),
    }


def step_workforce_month(
    engineers: Dict[str, float],
    target_engineers: Optional[Mapping[str, float]],
    year: float,
    salary_multiplier: float = 1.0,
    morale: float = 1.0,
    recent_hire_fraction: float = 0.0,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Settle one month of engineering workforce attrition, hiring/layoffs, and direct salary cost.

    Modifies `engineers` in-place (and returns a summary dict with `direct_payroll_usd`,
    `recruiting_cost_usd`, `severance_cost_usd`, `hired_fte`, `fired_fte`, `attrition_fte`,
    `morale`, `recent_hire_fraction`).
    """
    cfg = (tuning if tuning is not None else load_econ_tuning())["workforce"]
    bench_sal_yr = benchmark_engineer_salary_usd_yr(year)
    monthly_salary_per_fte = (bench_sal_yr * float(salary_multiplier)) / 12.0
    tightness = labor_market_tightness(year)

    # 1. Voluntary monthly attrition (decreases when salary_multiplier > 1 or morale > 1, increases in tight labor market)
    base_attr = float(cfg["base_monthly_attrition_rate"])
    sal_elast_attr = float(cfg["salary_premium_attrition_elasticity"])
    attr_rate = base_attr * tightness * math.exp(-sal_elast_attr * (float(salary_multiplier) - 1.0)) / max(0.6, float(morale))
    attr_rate = min(max(attr_rate, 0.001), 0.05)

    total_before = sum(max(0.0, float(engineers.get(d, 0.0))) for d in DISCIPLINES)
    attrition_total = 0.0
    hired_total = 0.0
    fired_total = 0.0

    max_hire_rate = float(cfg["base_monthly_hiring_rate_frac"]) * (
        (float(salary_multiplier) ** float(cfg["salary_premium_hiring_elasticity"])) / max(0.5, tightness)
    )
    max_hire_abs = float(cfg["max_monthly_hiring_fte_per_disc"]) / max(0.5, tightness)

    for d in DISCIPLINES:
        cur = max(0.0, float(engineers.get(d, 0.0)))
        lost = cur * attr_rate
        cur_after_attr = max(0.0, cur - lost)
        attrition_total += lost

        if target_engineers is not None and d in target_engineers:
            tgt = max(0.0, float(target_engineers[d]))
            diff = tgt - cur_after_attr
            if diff > 1e-6:
                cap = min(max_hire_abs, max(4.0, cur_after_attr * max_hire_rate))
                hired = min(diff, cap)
                cur_after_attr += hired
                hired_total += hired
            elif diff < -1e-6:
                fired = min(cur_after_attr, -diff)
                cur_after_attr -= fired
                fired_total += fired

        engineers[d] = float(cur_after_attr)

    total_after = sum(engineers.values())
    direct_payroll_usd = total_after * monthly_salary_per_fte
    recruiting_cost_usd = hired_total * monthly_salary_per_fte * float(cfg["hiring_recruiting_cost_months_salary"])
    severance_cost_usd = fired_total * monthly_salary_per_fte * float(cfg["firing_severance_months_salary"])

    # Update morale & onboarding dilution
    new_morale = float(morale) + float(cfg["morale_recovery_rate_per_month"]) * (1.0 - float(morale))
    if fired_total > 0.0 and total_before > 0.0:
        layoff_pct_10 = (fired_total / total_before) * 10.0
        new_morale += float(cfg["firing_morale_shock_per_10pct"]) * layoff_pct_10
    new_morale = min(
        max(new_morale, float(cfg["morale_productivity_floor"])),
        float(cfg["morale_productivity_ceiling"]),
    )

    decay = math.exp(-1.0 / max(1.0, float(cfg["experience_onboarding_months"])))
    new_recent_hire_frac = (
        (float(recent_hire_fraction) * decay * max(0.0, total_after - hired_total) + hired_total)
        / max(1.0, total_after)
    )

    return {
        "total_engineers_fte": float(total_after),
        "monthly_salary_per_fte_usd": float(monthly_salary_per_fte),
        "direct_payroll_usd": float(direct_payroll_usd),
        "recruiting_cost_usd": float(recruiting_cost_usd),
        "severance_cost_usd": float(severance_cost_usd),
        "hired_fte": float(hired_total),
        "fired_fte": float(fired_total),
        "attrition_fte": float(attrition_total),
        "morale": float(new_morale),
        "recent_hire_fraction": float(min(1.0, max(0.0, new_recent_hire_frac))),
    }
