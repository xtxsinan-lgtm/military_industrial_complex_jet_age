"""Campaign end-condition checks (bankruptcy, hostile takeover) and 1960-12-31 scoring.

Owned by Module 09 (`docs/spec/09_core_loop.md`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CompanyScoreBreakdown:
    """Detailed score breakdown for a single manufacturer at campaign end."""

    company_id: str
    is_player: bool
    net_worth_nominal_usd: float
    net_worth_1950_usd: float
    aircraft_delivered: int
    contracts_won: int
    reputation_avg: float
    techs_unlocked: int
    net_worth_points: float
    delivery_points: float
    contract_points: float
    reputation_points: float
    tech_points: float
    raw_score: float
    difficulty_multiplier: float
    final_score: float
    grade_tier: str
    grade_title_key: str
    industry_rank: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_id": self.company_id,
            "is_player": self.is_player,
            "net_worth_nominal_usd": round(self.net_worth_nominal_usd, 2),
            "net_worth_1950_usd": round(self.net_worth_1950_usd, 2),
            "aircraft_delivered": self.aircraft_delivered,
            "contracts_won": self.contracts_won,
            "reputation_avg": round(self.reputation_avg, 4),
            "techs_unlocked": self.techs_unlocked,
            "net_worth_points": round(self.net_worth_points, 2),
            "delivery_points": round(self.delivery_points, 2),
            "contract_points": round(self.contract_points, 2),
            "reputation_points": round(self.reputation_points, 2),
            "tech_points": round(self.tech_points, 2),
            "raw_score": round(self.raw_score, 2),
            "difficulty_multiplier": round(self.difficulty_multiplier, 3),
            "final_score": round(self.final_score, 2),
            "grade_tier": self.grade_tier,
            "grade_title_key": self.grade_title_key,
            "industry_rank": self.industry_rank,
        }


@dataclass
class CampaignEndEvaluation:
    """Outcome of checking end-of-campaign / failure conditions."""

    ended: bool
    outcome: str = "ongoing"  # "ongoing" | "completed_1960" | "bankruptcy" | "forced_takeover"
    reason: str = ""
    player_score: Optional[CompanyScoreBreakdown] = None
    leaderboard: List[CompanyScoreBreakdown] = field(default_factory=list)


def check_failure_conditions(world: Any) -> Tuple[bool, str, str]:
    """Check whether the player company has suffered bankruptcy or forced takeover.

    Returns `(failed, outcome_code, reason_text)`.
    """
    econ = world.modules.get("04_economy")
    if econ is None or not hasattr(econ, "get_player_company"):
        return False, "ongoing", ""

    bt_cfg = world.tuning["bankruptcy_and_takeover"]
    grace_days = int(world.difficulty_preset.get("bankruptcy_grace_days", 90))
    player = econ.get_player_company()
    cid = str(player["id"])
    start_nw = max(1.0, float(econ.starting_net_worth_usd.get(cid, 10_000_000.0)))
    cur_nw = float(econ.compute_net_worth(cid))

    # 1. Insolvency / Bankruptcy check
    if int(getattr(econ, "insolvent_days", 0)) >= grace_days and float(player["cash_usd"]) < 0.0:
        debt_ratio = float(player["debt_usd"]) / start_nw
        limit_ratio = float(bt_cfg.get("emergency_bailout_debt_ratio_limit", 0.85))
        if debt_ratio <= limit_ratio:
            # Automatic emergency credit draw to restore cash to +$250k
            shortfall = abs(float(player["cash_usd"])) + 250_000.0
            player["cash_usd"] = float(player["cash_usd"]) + shortfall
            player["debt_usd"] = float(player["debt_usd"]) + shortfall
            econ.insolvent_days = 0
            world.emit_notification(
                category="emergency_bailout_loan",
                title_key="notif.emergency_bailout.title",
                body_key="notif.emergency_bailout.body",
                severity="warning",
                autopause_trigger="low_cash_warning",
                payload={"bailout_usd": shortfall, "debt_usd": player["debt_usd"]},
            )
        else:
            return (
                True,
                "bankruptcy",
                f"Insolvent for {grace_days} days with exhausted credit capacity (debt=${player['debt_usd']:,.0f})",
            )

    # 2. Forced Takeover / Board Ouster check (checked on month boundaries or post-1948)
    sched = world.current_schedule()
    min_year = int(bt_cfg.get("takeover_min_year", 1948))
    idle_months = int(getattr(econ, "idle_months", 0))
    warn_months = int(bt_cfg.get("takeover_warning_months", 18))
    max_idle_months = int(bt_cfg.get("takeover_idle_months_threshold", 24))
    nw_frac = float(bt_cfg.get("takeover_net_worth_fraction_of_start", 0.25))

    if sched.year >= min_year and sched.is_month_start:
        if idle_months == warn_months and cur_nw < start_nw * (nw_frac * 1.5):
            world.emit_notification(
                category="takeover_warning",
                title_key="notif.takeover_warning.title",
                body_key="notif.takeover_warning.body",
                severity="warning",
                autopause_trigger="low_cash_warning",
                payload={"idle_months": idle_months},
            )
        if idle_months >= max_idle_months and cur_nw < start_nw * nw_frac:
            return (
                True,
                "forced_takeover",
                f"No active production contracts for {idle_months} months and net worth fell below {nw_frac*100:.0f}% of initial capitalization",
            )

    return False, "ongoing", ""


def _resolve_grade_tier(final_score: float, thresholds: List[Dict[str, Any]]) -> Tuple[str, str]:
    for row in thresholds:
        if final_score >= float(row["min_score"]):
            return str(row["tier"]), str(row["title_key"])
    last = thresholds[-1]
    return str(last["tier"]), str(last["title_key"])


def compute_leaderboard_and_player_score(world: Any) -> Tuple[CompanyScoreBreakdown, List[CompanyScoreBreakdown]]:
    """Compute score breakdowns and industry rankings for all companies."""
    econ = world.modules.get("04_economy")
    tech = world.modules.get("03_tech")
    sc_cfg = world.tuning["scoring"]
    weights = sc_cfg["weights"]
    thresholds = sc_cfg["grade_thresholds"]

    nw_div = float(weights["net_worth_1950_usd_per_point"])
    deliv_w = float(weights["aircraft_delivered_points_each"])
    contract_w = float(weights["prime_contract_won_points"])
    rep_w = float(weights["reputation_avg_points_full"])
    tech_w = float(weights["tech_leadership_points_each"])
    diff_mult = float(world.difficulty_preset.get("score_multiplier", 1.0))

    rows: List[CompanyScoreBreakdown] = []
    for cid in sorted(world.company_ids):
        comp = econ.companies[cid] if (econ is not None and cid in econ.companies) else {}
        is_player = cid == world.player_company_id
        nw_nom = float(econ.compute_net_worth(cid)) if econ is not None else 0.0
        nw_1950 = float(world.macro.nominal_to_1950_usd(nw_nom))
        delivered = int(comp.get("aircraft_delivered_total", 0))
        won = int(comp.get("contracts_won_total", 0))
        rep_map = comp.get("reputation", {"USAF": 0.5, "USN": 0.5, "export": 0.5})
        rep_vals = [float(rep_map.get(k, 0.5)) for k in ("USAF", "USN", "export")]
        rep_avg = sum(rep_vals) / len(rep_vals)

        unlocked_list = (
            tech.unlocked_by_company.get(cid, ["baseline_1945"])
            if tech is not None and hasattr(tech, "unlocked_by_company")
            else ["baseline_1945"]
        )
        techs_beyond_start = max(0, len(unlocked_list) - 1)

        nw_pts = max(0.0, nw_1950 / nw_div)
        deliv_pts = delivered * deliv_w
        ct_pts = won * contract_w
        rep_pts = rep_avg * rep_w
        t_pts = techs_beyond_start * tech_w
        raw_score = nw_pts + deliv_pts + ct_pts + rep_pts + t_pts
        mult = diff_mult if is_player else 1.0
        final_score = raw_score * mult
        tier, title_key = _resolve_grade_tier(final_score, thresholds)

        rows.append(
            CompanyScoreBreakdown(
                company_id=cid,
                is_player=is_player,
                net_worth_nominal_usd=nw_nom,
                net_worth_1950_usd=nw_1950,
                aircraft_delivered=delivered,
                contracts_won=won,
                reputation_avg=rep_avg,
                techs_unlocked=techs_beyond_start,
                net_worth_points=nw_pts,
                delivery_points=deliv_pts,
                contract_points=ct_pts,
                reputation_points=rep_pts,
                tech_points=t_pts,
                raw_score=raw_score,
                difficulty_multiplier=mult,
                final_score=final_score,
                grade_tier=tier,
                grade_title_key=title_key,
            )
        )

    rows.sort(key=lambda r: (-r.final_score, r.company_id))
    player_row: Optional[CompanyScoreBreakdown] = None
    for idx, r in enumerate(rows, start=1):
        r.industry_rank = idx
        if r.is_player:
            player_row = r

    assert player_row is not None
    return player_row, rows
