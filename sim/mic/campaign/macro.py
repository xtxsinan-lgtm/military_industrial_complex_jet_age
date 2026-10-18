"""Macroeconomic environment and US Defense / Aircraft Procurement Budget (FY1945-FY1961).

Owned by Module 09 (`docs/spec/09_core_loop.md`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

_DEFAULT_TUNING_PATH = Path(__file__).resolve().parents[2] / "data" / "tuning" / "core.json"


def load_core_tuning(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load `sim/data/tuning/core.json`."""
    p = path or _DEFAULT_TUNING_PATH
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


@dataclass(frozen=True)
class FiscalYearBudget:
    """US National Defense and Military Aviation budget for a single Fiscal Year (then-year USD)."""

    fy: int
    dod_total_usd: float
    usaf_total_usd: float
    usn_aviation_usd: float
    aircraft_procurement_total_usd: float
    aircraft_procurement_usaf_usd: float
    aircraft_procurement_usn_usd: float
    aviation_rd_usd: float
    deflator_1950: float
    era_note: str

    @classmethod
    def from_tuning_entry(cls, entry: Dict[str, Any]) -> "FiscalYearBudget":
        m = 1_000_000.0
        return cls(
            fy=int(entry["fy"]),
            dod_total_usd=float(entry["dod_total_musd"]) * m,
            usaf_total_usd=float(entry["usaf_total_musd"]) * m,
            usn_aviation_usd=float(entry["usn_aviation_musd"]) * m,
            aircraft_procurement_total_usd=float(entry["aircraft_procurement_total_musd"]) * m,
            aircraft_procurement_usaf_usd=float(entry["aircraft_procurement_usaf_musd"]) * m,
            aircraft_procurement_usn_usd=float(entry["aircraft_procurement_usn_musd"]) * m,
            aviation_rd_usd=float(entry["aviation_rd_musd"]) * m,
            deflator_1950=float(entry["deflator_1950"]),
            era_note=str(entry.get("era_note", "")),
        )


class MacroEnvironment:
    """Tracks macroeconomic variables, geopolitical tension, and fiscal year budgets."""

    def __init__(self, tuning: Optional[Dict[str, Any]] = None) -> None:
        raw_tuning = tuning or load_core_tuning()
        fy_map_raw = raw_tuning["us_defense_budget_fy1945_1961"]["fiscal_years"]
        self._budgets: Dict[int, FiscalYearBudget] = {
            int(k): FiscalYearBudget.from_tuning_entry(v) for k, v in fy_map_raw.items()
        }
        self._min_fy = min(self._budgets.keys())
        self._max_fy = max(self._budgets.keys())
        self.vars: Dict[str, Any] = dict(raw_tuning.get("initial_macro_state", {}))
        self.current_fy: int = 1945

    def budget_for_fy(self, fy: int) -> FiscalYearBudget:
        """Return the historical `FiscalYearBudget` for `fy` (clamped to [1945, 1961] if out of bounds)."""
        clamped = max(self._min_fy, min(self._max_fy, int(fy)))
        return self._budgets[clamped]

    def current_budget(self) -> FiscalYearBudget:
        """Return the `FiscalYearBudget` for `self.current_fy`."""
        return self.budget_for_fy(self.current_fy)

    def effective_aircraft_procurement_usd(self, fy: Optional[int] = None) -> float:
        """Return annual aircraft procurement budget scaled by `procurement_budget_mult`."""
        b = self.budget_for_fy(fy if fy is not None else self.current_fy)
        mult = float(self.vars.get("procurement_budget_mult", 1.0))
        return b.aircraft_procurement_total_usd * mult

    def effective_rd_budget_usd(self, fy: Optional[int] = None) -> float:
        """Return annual aviation R&D budget scaled by `rd_budget_mult`."""
        b = self.budget_for_fy(fy if fy is not None else self.current_fy)
        mult = float(self.vars.get("rd_budget_mult", 1.0))
        return b.aviation_rd_usd * mult

    def nominal_to_1950_usd(self, nominal_usd: float, fy: Optional[int] = None) -> float:
        """Convert then-year nominal USD into constant 1950 USD using the FY deflator."""
        b = self.budget_for_fy(fy if fy is not None else self.current_fy)
        return float(nominal_usd) / b.deflator_1950

    def get_var(self, key: str, default: Any = None) -> Any:
        return self.vars.get(key, default)

    def set_var(self, key: str, value: Any) -> None:
        if key == "tension" and isinstance(value, (int, float)):
            value = max(0.0, min(1.0, float(value)))
        self.vars[key] = value

    def add_var(self, key: str, delta: float) -> float:
        cur = float(self.vars.get(key, 0.0))
        new_val = cur + float(delta)
        if key == "tension" or key.startswith("usaf_priority_") or key.startswith("usn_priority_"):
            new_val = max(0.0, min(1.0, new_val))
        self.vars[key] = new_val
        return new_val

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_fy": self.current_fy,
            "vars": {k: self.vars[k] for k in sorted(self.vars.keys())},
        }

    def load_dict(self, data: Dict[str, Any]) -> None:
        self.current_fy = int(data["current_fy"])
        self.vars = dict(data.get("vars", {}))
