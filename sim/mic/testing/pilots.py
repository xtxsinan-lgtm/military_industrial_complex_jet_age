"""Test pilot roster, hiring market, skill progression, and crash/detection multipliers."""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .data_loader import get_inflation_factor, load_pilot_names_data
from .hashing import keyed_normal, keyed_u01


@dataclass
class TestPilot:
    id: str
    name: str
    age: int
    hired_year: int
    skill: float
    experience: float
    traits: List[str] = field(default_factory=list)
    salary_annual_usd: float = 12000.0
    status: str = "active"  # "active" | "injured" | "deceased" | "retired"
    injured_until_day: int = 0
    assigned_prototype_idx: int = 0
    flights_flown: int = 0

    def is_available(self, day: int) -> bool:
        if self.status == "injured" and day >= self.injured_until_day:
            self.status = "active"
        return self.status == "active"


def get_starter_pilots() -> List[TestPilot]:
    """Return deep copy of the 1945 starter test-pilot roster."""
    pdata = load_pilot_names_data()
    out: List[TestPilot] = []
    for entry in pdata["starter_roster_1945"]:
        out.append(TestPilot(**copy.deepcopy(entry)))
    return out


def compute_pilot_multipliers(pilot: TestPilot) -> Dict[str, float]:
    """Compute crash avoidance, flaw detection, and telemetry precision multipliers (§5.7.1)."""
    traits_spec = load_pilot_names_data()["traits"]
    s = float(pilot.skill)
    x = float(pilot.experience)

    crash_mult = math.exp(-0.014 * (s - 50.0) - 0.005 * (x - 40.0))
    detect_mult = 0.75 + 0.004 * s + 0.002 * x
    data_sigma_mult = 1.15 - 0.003 * s

    for t in pilot.traits:
        if t in traits_spec:
            t_info = traits_spec[t]
            crash_mult *= float(t_info["crash_mult"])
            detect_mult *= float(t_info["detect_mult"])
            data_sigma_mult *= float(t_info["data_sigma_mult"])

    return {
        "crash_mult": max(0.35, min(2.00, crash_mult)),
        "detect_mult": max(0.60, min(1.80, detect_mult)),
        "data_sigma_mult": max(0.65, min(1.35, data_sigma_mult)),
    }


def generate_pilot_pool(
    campaign_seed: int,
    year: int,
    count: int = 4,
) -> List[TestPilot]:
    """Deterministically generate `count` candidate test pilots for the yearly hiring market."""
    pdata = load_pilot_names_data()
    ranks = pdata["ranks"]
    firsts = pdata["first_names"]
    lasts = pdata["last_names"]
    infl = get_inflation_factor(year)

    pool: List[TestPilot] = []
    for idx in range(count):
        u_r = keyed_u01(campaign_seed, "pilot_pool", year, idx, "rank")
        u_f = keyed_u01(campaign_seed, "pilot_pool", year, idx, "first")
        u_l = keyed_u01(campaign_seed, "pilot_pool", year, idx, "last")
        rank = ranks[int(u_r * len(ranks)) % len(ranks)]
        first = firsts[int(u_f * len(firsts)) % len(firsts)]
        last = lasts[int(u_l * len(lasts)) % len(lasts)]
        name = f"{rank} {first} {last}"

        z_s = keyed_normal(campaign_seed, "pilot_pool", year, idx, "skill")
        z_x = keyed_normal(campaign_seed, "pilot_pool", year, idx, "exp")
        skill = round(max(40.0, min(94.0, 68.0 + 11.0 * z_s)), 1)
        exp = round(max(20.0, min(90.0, 52.0 + 15.0 * z_x)), 1)
        age = 25 + int(keyed_u01(campaign_seed, "pilot_pool", year, idx, "age") * 12)

        traits: List[str] = []
        if keyed_u01(campaign_seed, "pilot_pool", year, idx, "tr_eng") < 0.30:
            traits.append("engineer_pilot")
        u_style = keyed_u01(campaign_seed, "pilot_pool", year, idx, "tr_style")
        if u_style < 0.30:
            traits.append("cautious")
        elif u_style > 0.72:
            traits.append("daring")
        if keyed_u01(campaign_seed, "pilot_pool", year, idx, "tr_nav") < 0.25:
            traits.append("carrier_qualified")

        base_sal = (9000.0 + 110.0 * (skill - 40.0) + 45.0 * exp) * infl
        for t in traits:
            base_sal *= float(pdata["traits"][t]["salary_mult"])

        pool.append(
            TestPilot(
                id=f"pilot_{year}_{idx + 1}",
                name=name,
                age=age,
                hired_year=year,
                skill=skill,
                experience=exp,
                traits=traits,
                salary_annual_usd=round(base_sal, -2),
                status="active",
            )
        )
    return pool
