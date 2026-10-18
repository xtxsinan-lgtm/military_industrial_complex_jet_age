"""Political capital generation, Congressional district footprint, lobbying diminishing returns, and political actions."""

from __future__ import annotations

import math
from typing import Any, Dict, Optional

from .inflation import aero_cost_index_1950
from .tuning import load_econ_tuning


def step_political_capital_month(
    current_pc: float,
    total_employees_fte: float,
    lobbying_spend_then_year_usd: float,
    year: float,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    """Update `political_capital` (`[0, 100]`) for one month."""
    cfg = (tuning if tuning is not None else load_econ_tuning())["politics"]
    pc_max = float(cfg["political_capital_max"])
    decay = float(cfg["political_capital_monthly_decay"])

    # 1. Passive generation from employment footprint (Congressional district leverage)
    passive_gain = (max(0.0, float(total_employees_fte)) / 1000.0) * float(cfg["base_pc_gen_per_1000_employees"])

    # 2. Active lobbying spend (concave saturating exponential in constant-1950 USD)
    idx = aero_cost_index_1950(year)
    spend_1950 = max(0.0, float(lobbying_spend_then_year_usd)) / max(1e-9, idx)
    ref_spend = float(cfg["lobbying_diminishing_ref_1950_usd_month"])
    max_lobby_pc = float(cfg["lobbying_max_pc_per_month"])
    lobby_gain = max_lobby_pc * (1.0 - math.exp(-spend_1950 / max(1.0, ref_spend)))

    decayed_loss = max(0.0, float(current_pc)) * decay
    new_pc = min(pc_max, max(0.0, float(current_pc) - decayed_loss + passive_gain + lobby_gain))

    return {
        "new_political_capital": float(new_pc),
        "passive_pc_gain": float(passive_gain),
        "lobbying_pc_gain": float(lobby_gain),
        "pc_decay_loss": float(decayed_loss),
    }


def can_afford_political_action(
    current_pc: float,
    action_key: str,
    tuning: Optional[Dict[str, Any]] = None,
) -> bool:
    """Return True if `current_pc` is sufficient to execute `action_key`."""
    cfg = (tuning if tuning is not None else load_econ_tuning())["politics"]
    cost = float(cfg["actions_pc_cost"].get(action_key, 999.0))
    return float(current_pc) >= cost


def spend_political_capital(
    current_pc: float,
    action_key: str,
    tuning: Optional[Dict[str, Any]] = None,
) -> float:
    """Deduct the political capital cost of `action_key` and return new `political_capital` (raises ValueError if insufficient)."""
    cfg = (tuning if tuning is not None else load_econ_tuning())["politics"]
    if action_key not in cfg["actions_pc_cost"]:
        raise KeyError(f"Unknown political action: {action_key}")
    cost = float(cfg["actions_pc_cost"][action_key])
    if float(current_pc) < cost:
        raise ValueError(f"Insufficient political capital ({current_pc:.2f} < {cost:.2f}) for {action_key}")
    return float(current_pc - cost)
