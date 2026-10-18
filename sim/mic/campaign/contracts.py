"""Canonical update order, SimModule protocol, and player/bot Action API catalog.

Owned by Module 09 (`docs/spec/09_core_loop.md`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable

from mic.calendar import TickSchedule

# Canonical module execution order on Fiscal Year rollover (July 1, before daily tick)
CANONICAL_FY_ROLLOVER_ORDER: Tuple[str, ...] = (
    "09_macro",
    "05_procurement",
    "04_economy",
    "07_ai",
)

# Canonical module execution order on the 1st of every month (settles previous month)
CANONICAL_MONTHLY_ORDER: Tuple[str, ...] = (
    "03_tech",
    "02_engines",
    "06_testing",
    "05_procurement",
    "04_economy",
    "07_ai",
    "09_events_mtth",
    "09_scoring_and_end_check",
    "09_autosave",
)

# Canonical module execution order on every daily tick
CANONICAL_DAILY_ORDER: Tuple[str, ...] = (
    "09_events_date",
    "11_war_reserved",
    "03_tech",
    "02_engines",
    "01_aero_design",
    "06_testing",
    "04_economy",
    "05_procurement",
    "07_ai",
    "09_post_day",
)


@dataclass(frozen=True)
class ParamSpec:
    """Specification for a single parameter of a player/bot command."""

    name: str
    kind: str  # "str" | "int" | "float" | "bool" | "dict" | "list"
    required: bool = True
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    allowed_values: Optional[Tuple[Any, ...]] = None
    description: str = ""


@dataclass(frozen=True)
class ActionSpec:
    """Schema and routing rule for a player/bot action."""

    action_type: str
    owner_module: str
    params: Tuple[ParamSpec, ...]
    description: str = ""


@dataclass(frozen=True)
class PlayerAction:
    """A single command issued by the player or a bot policy on a given day."""

    action_type: str
    actor_company_id: str
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating a `PlayerAction` before execution."""

    ok: bool
    code: str = "OK"
    message: str = ""


@dataclass(frozen=True)
class ActionResult:
    """Result of executing a `PlayerAction`."""

    ok: bool
    code: str = "OK"
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Notification:
    """Structured notification emitted by simulation modules for UI/log/autopause."""

    id: str
    day: int
    category: str  # e.g. "rfp_issued", "contract_awarded", "historical_event_major", etc.
    title_key: str
    body_key: str
    severity: str = "info"  # "info" | "warning" | "critical" | "major"
    autopause_trigger: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    dismissed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "day": self.day,
            "category": self.category,
            "title_key": self.title_key,
            "body_key": self.body_key,
            "severity": self.severity,
            "autopause_trigger": self.autopause_trigger,
            "payload": dict(self.payload),
            "dismissed": self.dismissed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        return cls(
            id=str(data["id"]),
            day=int(data["day"]),
            category=str(data["category"]),
            title_key=str(data["title_key"]),
            body_key=str(data["body_key"]),
            severity=str(data.get("severity", "info")),
            autopause_trigger=data.get("autopause_trigger"),
            payload=dict(data.get("payload", {})),
            dismissed=bool(data.get("dismissed", False)),
        )


@dataclass
class LedgerEntry:
    """Cash-flow entry posted during a month and settled by Module 04 on month start."""

    day: int
    company_id: str
    category: str  # "payroll" | "facilities" | "rd" | "testing" | "contract_advance" | "delivery" | "loan" | "event"
    amount_usd: float  # positive = inflow, negative = outflow
    memo: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "day": self.day,
            "company_id": self.company_id,
            "category": self.category,
            "amount_usd": float(self.amount_usd),
            "memo": self.memo,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LedgerEntry":
        return cls(
            day=int(data["day"]),
            company_id=str(data["company_id"]),
            category=str(data["category"]),
            amount_usd=float(data["amount_usd"]),
            memo=str(data.get("memo", "")),
        )


@runtime_checkable
class SimModule(Protocol):
    """Protocol implemented by all simulation domain modules (01..07) and stubs."""

    module_id: str
    schema_version: int

    def init_new_game(self, world: Any) -> None:
        """Initialize state at the start of a new campaign."""
        ...

    def on_fiscal_year_start(self, world: Any, fy: int) -> None:
        """Called on July 1 when the US Federal Fiscal Year rolls over to `fy`."""
        ...

    def on_month_start(self, world: Any, schedule: TickSchedule) -> None:
        """Called on the 1st of each calendar month to settle the preceding month."""
        ...

    def on_day_tick(self, world: Any, schedule: TickSchedule) -> None:
        """Called once per simulation day in `CANONICAL_DAILY_ORDER`."""
        ...

    def validate_action(self, world: Any, action: PlayerAction) -> ValidationResult:
        """Validate whether `action` is currently legal in domain state."""
        ...

    def apply_action(self, world: Any, action: PlayerAction) -> ActionResult:
        """Execute a validated `action` and mutate domain state deterministically."""
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Serialize module state to a JSON-compatible dictionary."""
        ...

    def load_dict(self, data: Dict[str, Any]) -> None:
        """Restore module state from `to_dict()` output."""
        ...


# Complete MVP Player/Bot Action Catalog
ACTION_CATALOG: Dict[str, ActionSpec] = {
    # --- Module 01: Aircraft Design ---
    "design.create": ActionSpec(
        action_type="design.create",
        owner_module="01_aero_design",
        params=(
            ParamSpec("name", "str", required=True, description="Display name of the new aircraft design"),
            ParamSpec("role_tags", "list", required=True, description="List of role tags, e.g. ['day_fighter']"),
            ParamSpec("spec", "dict", required=True, description="Initial AircraftDesign geometry and propulsion dict"),
        ),
        description="Create a new editable aircraft design project.",
    ),
    "design.modify": ActionSpec(
        action_type="design.modify",
        owner_module="01_aero_design",
        params=(
            ParamSpec("design_id", "str", required=True, description="Target aircraft design ID"),
            ParamSpec("patch", "dict", required=True, description="Updated geometry/systems fields"),
        ),
        description="Modify parameters on an uncommitted draft aircraft design.",
    ),
    "design.clone": ActionSpec(
        action_type="design.clone",
        owner_module="01_aero_design",
        params=(
            ParamSpec("source_design_id", "str", required=True, description="Existing design ID to clone"),
            ParamSpec("new_name", "str", required=True, description="Name for the cloned variant"),
        ),
        description="Clone an existing design as the basis for a variant or mark.",
    ),
    "design.freeze": ActionSpec(
        action_type="design.freeze",
        owner_module="01_aero_design",
        params=(
            ParamSpec("design_id", "str", required=True, description="Design ID to freeze for testing/bidding"),
        ),
        description="Freeze a draft design so wind-tunnel, prototype, and bid actions can reference it.",
    ),
    # --- Module 02: Engines ---
    "engine.start_project": ActionSpec(
        action_type="engine.start_project",
        owner_module="02_engines",
        params=(
            ParamSpec("name", "str", required=True, description="Engine designation"),
            ParamSpec(
                "architecture",
                "str",
                required=True,
                allowed_values=("centrifugal_jet", "axial_jet", "twin_spool_jet", "turbofan"),
                description="Compressor/cycle architecture",
            ),
            ParamSpec("target_thrust_dry_N", "float", required=True, min_val=2000.0, max_val=250000.0),
            ParamSpec("afterburner", "bool", required=True),
            ParamSpec("opr", "float", required=True, min_val=2.5, max_val=20.0),
            ParamSpec("tit_K", "float", required=True, min_val=950.0, max_val=1600.0),
            ParamSpec("engineers_assigned", "int", required=True, min_val=1, max_val=500),
            ParamSpec("base_engine_id", "str", required=False, description="Optional parent engine ID for derivative"),
        ),
        description="Launch a new in-house engine development or derivative project.",
    ),
    "engine.set_engineers": ActionSpec(
        action_type="engine.set_engineers",
        owner_module="02_engines",
        params=(
            ParamSpec("project_id", "str", required=True),
            ParamSpec("engineers_assigned", "int", required=True, min_val=0, max_val=500),
        ),
        description="Adjust propulsion engineers assigned to an active engine R&D project.",
    ),
    "engine.cancel_project": ActionSpec(
        action_type="engine.cancel_project",
        owner_module="02_engines",
        params=(ParamSpec("project_id", "str", required=True),),
        description="Cancel an active engine R&D project and release assigned engineers.",
    ),
    # --- Module 03: Technology Tree ---
    "tech.set_allocation": ActionSpec(
        action_type="tech.set_allocation",
        owner_module="03_tech",
        params=(
            ParamSpec("tech_id", "str", required=True, description="Target tech node ID"),
            ParamSpec("engineers_assigned", "int", required=True, min_val=0, max_val=500),
        ),
        description="Allocate discipline engineers to research a technology node.",
    ),
    "tech.cancel_research": ActionSpec(
        action_type="tech.cancel_research",
        owner_module="03_tech",
        params=(ParamSpec("tech_id", "str", required=True),),
        description="Stop active research on a tech node (accumulated progress is retained).",
    ),
    # --- Module 04: Economy, Staff, Facilities, Production, Finance ---
    "econ.hire_engineers": ActionSpec(
        action_type="econ.hire_engineers",
        owner_module="04_economy",
        params=(
            ParamSpec(
                "discipline",
                "str",
                required=True,
                allowed_values=("aero", "structures", "propulsion", "systems"),
            ),
            ParamSpec("count", "int", required=True, min_val=1, max_val=200),
        ),
        description="Hire engineers in a specific discipline.",
    ),
    "econ.fire_engineers": ActionSpec(
        action_type="econ.fire_engineers",
        owner_module="04_economy",
        params=(
            ParamSpec(
                "discipline",
                "str",
                required=True,
                allowed_values=("aero", "structures", "propulsion", "systems"),
            ),
            ParamSpec("count", "int", required=True, min_val=1, max_val=200),
        ),
        description="Lay off engineers in a specific discipline (incurs severance cost).",
    ),
    "econ.upgrade_wind_tunnel": ActionSpec(
        action_type="econ.upgrade_wind_tunnel",
        owner_module="04_economy",
        params=(
            ParamSpec("target_level", "int", required=True, min_val=1, max_val=4),
        ),
        description="Upgrade company wind-tunnel facility level (1=subsonic, 2=high-speed, 3=transonic, 4=supersonic).",
    ),
    "econ.expand_factory": ActionSpec(
        action_type="econ.expand_factory",
        owner_module="04_economy",
        params=(
            ParamSpec("additional_floor_m2", "float", required=True, min_val=1000.0, max_val=200000.0),
        ),
        description="Construct additional factory floor area in square meters.",
    ),
    "econ.build_test_site": ActionSpec(
        action_type="econ.build_test_site",
        owner_module="04_economy",
        params=(),
        description="Acquire dedicated flight test facility instrumentation.",
    ),
    "econ.take_loan": ActionSpec(
        action_type="econ.take_loan",
        owner_module="04_economy",
        params=(
            ParamSpec("principal_usd", "float", required=True, min_val=100000.0, max_val=100000000.0),
        ),
        description="Draw a commercial/V-Loan credit line up to company debt capacity.",
    ),
    "econ.repay_loan": ActionSpec(
        action_type="econ.repay_loan",
        owner_module="04_economy",
        params=(
            ParamSpec("amount_usd", "float", required=True, min_val=10000.0, max_val=100000000.0),
        ),
        description="Repay outstanding debt principal from available cash.",
    ),
    "econ.set_production_rate": ActionSpec(
        action_type="econ.set_production_rate",
        owner_module="04_economy",
        params=(
            ParamSpec("contract_id", "str", required=True),
            ParamSpec("units_per_month", "int", required=True, min_val=0, max_val=200),
        ),
        description="Set target monthly aircraft output for an active production contract.",
    ),
    # --- Module 05: Procurement & Bidding ---
    "proc.submit_proposal": ActionSpec(
        action_type="proc.submit_proposal",
        owner_module="05_procurement",
        params=(
            ParamSpec("requirement_id", "str", required=True),
            ParamSpec("design_id", "str", required=True),
            ParamSpec("bid_unit_price_usd", "float", required=True, min_val=10000.0, max_val=50000000.0),
            ParamSpec("promised_performance", "dict", required=False, description="Optional overrides of promised performance"),
        ),
        description="Submit a formal proposal to an open military Requirement (RFP).",
    ),
    "proc.withdraw_proposal": ActionSpec(
        action_type="proc.withdraw_proposal",
        owner_module="05_procurement",
        params=(
            ParamSpec("requirement_id", "str", required=True),
        ),
        description="Withdraw a previously submitted proposal before the evaluation deadline.",
    ),
    "proc.lobby_program": ActionSpec(
        action_type="proc.lobby_program",
        owner_module="05_procurement",
        params=(
            ParamSpec("requirement_id", "str", required=True),
            ParamSpec("political_capital_spent", "float", required=True, min_val=1.0, max_val=50.0),
        ),
        description="Spend political capital to improve evaluation bias on an active Requirement.",
    ),
    # --- Module 06: Testing & Uncertainty ---
    "test.run_wind_tunnel": ActionSpec(
        action_type="test.run_wind_tunnel",
        owner_module="06_testing",
        params=(
            ParamSpec("design_id", "str", required=True),
            ParamSpec("facility", "str", required=True, allowed_values=("company", "naca")),
            ParamSpec(
                "regime",
                "str",
                required=True,
                allowed_values=("subsonic", "transonic", "supersonic", "high_alpha"),
            ),
        ),
        description="Schedule a wind-tunnel test campaign on a frozen design to narrow uncertainty and uncover flaws.",
    ),
    "test.build_prototype": ActionSpec(
        action_type="test.build_prototype",
        owner_module="06_testing",
        params=(
            ParamSpec("design_id", "str", required=True),
            ParamSpec("quantity", "int", required=True, min_val=1, max_val=6),
        ),
        description="Authorize construction of flight-test prototype airframes.",
    ),
    "test.schedule_flight_test": ActionSpec(
        action_type="test.schedule_flight_test",
        owner_module="06_testing",
        params=(
            ParamSpec("design_id", "str", required=True),
            ParamSpec(
                "syllabus",
                "list",
                required=True,
                description="List of flight-test cards: low_speed, speed_envelope, altitude, maneuver, high_aoa_spin, weapons",
            ),
            ParamSpec("thoroughness", "str", required=True, allowed_values=("minimal", "standard", "exhaustive")),
        ),
        description="Schedule a prototype flight-test campaign across selected test cards.",
    ),
    "test.fix_flaw": ActionSpec(
        action_type="test.fix_flaw",
        owner_module="06_testing",
        params=(
            ParamSpec("design_id", "str", required=True),
            ParamSpec("flaw_id", "str", required=True),
        ),
        description="Commit engineering time and funds to rectify a discovered HiddenFlaw.",
    ),
    # --- Module 09: Core Loop / Events / Notifications ---
    "core.choose_event_option": ActionSpec(
        action_type="core.choose_event_option",
        owner_module="09_core_loop",
        params=(
            ParamSpec("event_id", "str", required=True),
            ParamSpec("option_id", "str", required=True),
        ),
        description="Select an option for a pending interactive event.",
    ),
    "core.dismiss_notification": ActionSpec(
        action_type="core.dismiss_notification",
        owner_module="09_core_loop",
        params=(
            ParamSpec("notification_id", "str", required=True),
        ),
        description="Mark a notification as dismissed.",
    ),
}


def validate_action_schema(action: PlayerAction) -> ValidationResult:
    """Validate `action` against `ACTION_CATALOG` schema (types, required keys, bounds)."""
    if not isinstance(action.action_type, str) or action.action_type not in ACTION_CATALOG:
        return ValidationResult(
            ok=False,
            code="ERR_UNKNOWN_ACTION",
            message=f"Unknown action_type: {action.action_type!r}",
        )
    if not isinstance(action.actor_company_id, str) or not action.actor_company_id.strip():
        return ValidationResult(
            ok=False,
            code="ERR_INVALID_ACTOR",
            message="actor_company_id must be a non-empty string",
        )
    spec = ACTION_CATALOG[action.action_type]
    params = action.params if isinstance(action.params, dict) else {}

    known_names = {p.name for p in spec.params}
    for key in params.keys():
        if key not in known_names:
            return ValidationResult(
                ok=False,
                code="ERR_UNEXPECTED_PARAM",
                message=f"Unexpected parameter {key!r} for {action.action_type}",
            )

    for p in spec.params:
        if p.name not in params or params[p.name] is None:
            if p.required:
                return ValidationResult(
                    ok=False,
                    code="ERR_MISSING_PARAM",
                    message=f"Missing required parameter {p.name!r} for {action.action_type}",
                )
            continue

        val = params[p.name]
        if p.kind == "str":
            if not isinstance(val, str) or not val.strip():
                return ValidationResult(
                    ok=False,
                    code="ERR_PARAM_TYPE",
                    message=f"Parameter {p.name!r} must be a non-empty string",
                )
        elif p.kind == "bool":
            if not isinstance(val, bool):
                return ValidationResult(
                    ok=False,
                    code="ERR_PARAM_TYPE",
                    message=f"Parameter {p.name!r} must be a bool",
                )
        elif p.kind == "int":
            if isinstance(val, bool) or not isinstance(val, int):
                return ValidationResult(
                    ok=False,
                    code="ERR_PARAM_TYPE",
                    message=f"Parameter {p.name!r} must be an int",
                )
        elif p.kind == "float":
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                return ValidationResult(
                    ok=False,
                    code="ERR_PARAM_TYPE",
                    message=f"Parameter {p.name!r} must be a number",
                )
            if math.isnan(float(val)) or math.isinf(float(val)):
                return ValidationResult(
                    ok=False,
                    code="ERR_PARAM_NAN",
                    message=f"Parameter {p.name!r} must be finite",
                )
        elif p.kind == "dict":
            if not isinstance(val, dict):
                return ValidationResult(
                    ok=False,
                    code="ERR_PARAM_TYPE",
                    message=f"Parameter {p.name!r} must be a dict",
                )
        elif p.kind == "list":
            if not isinstance(val, list) or len(val) == 0:
                return ValidationResult(
                    ok=False,
                    code="ERR_PARAM_TYPE",
                    message=f"Parameter {p.name!r} must be a non-empty list",
                )

        if p.kind in ("int", "float"):
            fval = float(val)
            if p.min_val is not None and fval < p.min_val:
                return ValidationResult(
                    ok=False,
                    code="ERR_PARAM_RANGE",
                    message=f"Parameter {p.name!r}={val} below minimum {p.min_val}",
                )
            if p.max_val is not None and fval > p.max_val:
                return ValidationResult(
                    ok=False,
                    code="ERR_PARAM_RANGE",
                    message=f"Parameter {p.name!r}={val} above maximum {p.max_val}",
                )

        if p.allowed_values is not None and val not in p.allowed_values:
            return ValidationResult(
                ok=False,
                code="ERR_PARAM_ENUM",
                message=f"Parameter {p.name!r}={val!r} not in {p.allowed_values}",
            )

    return ValidationResult(ok=True, code="OK", message="")
