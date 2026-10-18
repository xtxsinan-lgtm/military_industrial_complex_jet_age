"""Data-driven historical and MTTH random event engine.

Owned by Module 09 (`docs/spec/09_core_loop.md`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from mic.calendar import TickSchedule, iso_to_day
from mic.rng import mtth_prob


@dataclass
class PendingEventChoice:
    """An active multi-option event awaiting a player decision."""

    event_id: str
    triggered_day: int
    expires_day: int
    option_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "triggered_day": self.triggered_day,
            "expires_day": self.expires_day,
            "option_ids": list(self.option_ids),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PendingEventChoice":
        return cls(
            event_id=str(data["event_id"]),
            triggered_day=int(data["triggered_day"]),
            expires_day=int(data["expires_day"]),
            option_ids=[str(x) for x in data["option_ids"]],
        )


@dataclass
class ScheduledEvent:
    """An event scheduled to fire on a specific future day."""

    event_id: str
    fire_day: int

    def to_dict(self) -> Dict[str, Any]:
        return {"event_id": self.event_id, "fire_day": self.fire_day}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScheduledEvent":
        return cls(event_id=str(data["event_id"]), fire_day=int(data["fire_day"]))


@dataclass
class EventLogEntry:
    """Audit record of a fired and resolved event."""

    event_id: str
    day: int
    chosen_option_id: str
    auto_resolved: bool = False
    effects_summary: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "day": self.day,
            "chosen_option_id": self.chosen_option_id,
            "auto_resolved": self.auto_resolved,
            "effects_summary": list(self.effects_summary),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventLogEntry":
        return cls(
            event_id=str(data["event_id"]),
            day=int(data["day"]),
            chosen_option_id=str(data["chosen_option_id"]),
            auto_resolved=bool(data.get("auto_resolved", False)),
            effects_summary=[str(x) for x in data.get("effects_summary", [])],
        )


def resolve_condition_var(world: Any, var_path: str) -> Any:
    """Resolve a dotted variable path against `world` state."""
    if var_path.startswith("date."):
        sched = world.current_schedule()
        sub = var_path[len("date.") :]
        if sub == "day":
            return sched.day
        if sub == "year":
            return sched.year
        if sub == "month":
            return sched.month
        if sub == "day_of_month":
            return sched.day_of_month
        if sub == "fiscal_year":
            return sched.fiscal_year
        if sub == "fiscal_quarter":
            return sched.fiscal_quarter
        raise KeyError(f"Unknown date variable: {var_path}")

    if var_path.startswith("flag."):
        flag_name = var_path[len("flag.") :]
        return bool(world.flags.get(flag_name, False))

    if var_path.startswith("macro."):
        macro_key = var_path[len("macro.") :]
        return world.macro.get_var(macro_key)

    if var_path.startswith("player."):
        sub = var_path[len("player.") :]
        econ = world.modules.get("04_economy")
        if econ is None or not hasattr(econ, "get_player_company"):
            return 0.0
        comp = econ.get_player_company()
        if sub == "cash_usd":
            return float(comp.get("cash_usd", 0.0))
        if sub == "debt_usd":
            return float(comp.get("debt_usd", 0.0))
        if sub == "political_capital":
            return float(comp.get("political_capital", 0.0))
        if sub.startswith("reputation."):
            cust = sub.split(".", 1)[1]
            return float(comp.get("reputation", {}).get(cust, 0.0))
        raise KeyError(f"Unknown player variable: {var_path}")

    raise KeyError(f"Unsupported condition variable path: {var_path}")


def evaluate_condition(world: Any, cond: Optional[Dict[str, Any]]) -> bool:
    """Evaluate a recursive JSON condition expression tree against `world`."""
    if not cond:
        return True
    if "all" in cond:
        return all(evaluate_condition(world, c) for c in cond["all"])
    if "any" in cond:
        return any(evaluate_condition(world, c) for c in cond["any"])
    if "not" in cond:
        return not evaluate_condition(world, cond["not"])

    var_path = str(cond["var"])
    op = str(cond["op"])
    rhs = cond["value"]
    lhs = resolve_condition_var(world, var_path)

    if op == "==":
        return lhs == rhs
    if op == "!=":
        return lhs != rhs
    if op == "<":
        return lhs < rhs
    if op == "<=":
        return lhs <= rhs
    if op == ">":
        return lhs > rhs
    if op == ">=":
        return lhs >= rhs
    if op == "in":
        return lhs in rhs
    raise ValueError(f"Unsupported condition operator: {op!r}")


class EventEngine:
    """Deterministic engine for date-triggered, scheduled, and monthly MTTH events."""

    def __init__(
        self,
        event_defs: List[Dict[str, Any]],
        choice_timeout_days: int = 30,
        max_mtth_events_per_month: int = 2,
    ) -> None:
        # Sort definitions by id for strict iteration order
        self._defs_by_id: Dict[str, Dict[str, Any]] = {}
        self._date_index: Dict[int, List[str]] = {}
        self._mtth_ids: List[str] = []

        for edef in sorted(event_defs, key=lambda d: str(d["id"])):
            eid = str(edef["id"])
            self._defs_by_id[eid] = edef
            trig = edef.get("trigger", {})
            ttype = trig.get("type", "date")
            if ttype == "date":
                fday = iso_to_day(str(trig["date"]))
                self._date_index.setdefault(fday, []).append(eid)
            elif ttype == "mtth":
                self._mtth_ids.append(eid)

        self.choice_timeout_days = int(choice_timeout_days)
        self.max_mtth_events_per_month = int(max_mtth_events_per_month)

        self.fired_once_ids: List[str] = []
        self.pending_choices: Dict[str, PendingEventChoice] = {}
        self.scheduled_events: List[ScheduledEvent] = []
        self.history: List[EventLogEntry] = []

    def get_event_def(self, event_id: str) -> Optional[Dict[str, Any]]:
        return self._defs_by_id.get(event_id)

    def can_fire(self, world: Any, edef: Dict[str, Any]) -> bool:
        eid = str(edef["id"])
        if edef.get("fire_once", True) and eid in self.fired_once_ids:
            return False
        if eid in self.pending_choices:
            return False
        trig = edef.get("trigger", {})
        cond = trig.get("condition")
        return evaluate_condition(world, cond)

    def on_day_tick(self, world: Any, schedule: TickSchedule) -> None:
        """Fire date-triggered and scheduled events for `schedule.day` and expire overdue choices."""
        # 1. Auto-resolve any expired pending choices first
        for eid in sorted(list(self.pending_choices.keys())):
            pend = self.pending_choices[eid]
            if schedule.day >= pend.expires_day:
                self._auto_resolve_pending(world, eid, schedule.day)

        # 2. Fire date-indexed events
        for eid in self._date_index.get(schedule.day, []):
            edef = self._defs_by_id[eid]
            if self.can_fire(world, edef):
                self._trigger_event(world, edef, schedule.day)

        # 3. Fire scheduled events due today
        remaining: List[ScheduledEvent] = []
        due_ids: List[str] = []
        for item in self.scheduled_events:
            if item.fire_day <= schedule.day:
                due_ids.append(item.event_id)
            else:
                remaining.append(item)
        self.scheduled_events = remaining
        for eid in sorted(due_ids):
            edef = self._defs_by_id.get(eid)
            if edef is not None and self.can_fire(world, edef):
                self._trigger_event(world, edef, schedule.day)

    def on_month_start(self, world: Any, schedule: TickSchedule) -> None:
        """Evaluate MTTH events on the 1st of the month over `schedule.days_in_prev_month`."""
        rng = world.rng.stream("core.events.mtth")
        fired_this_month = 0
        for eid in self._mtth_ids:
            if fired_this_month >= self.max_mtth_events_per_month:
                break
            edef = self._defs_by_id[eid]
            if not self.can_fire(world, edef):
                continue
            mtth_days = float(edef["trigger"]["mtth_days"])
            p = mtth_prob(mtth_days, schedule.days_in_prev_month)
            if rng.bernoulli(p):
                self._trigger_event(world, edef, schedule.day)
                fired_this_month += 1

    def choose_option(self, world: Any, event_id: str, option_id: str) -> bool:
        """Resolve a pending multi-option event with the player's chosen `option_id`."""
        pend = self.pending_choices.get(event_id)
        if pend is None or option_id not in pend.option_ids:
            return False
        edef = self._defs_by_id[event_id]
        del self.pending_choices[event_id]
        self._apply_option(world, edef, option_id, world.day, auto_resolved=False)
        return True

    def _trigger_event(self, world: Any, edef: Dict[str, Any], day: int) -> None:
        eid = str(edef["id"])
        if edef.get("fire_once", True) and eid not in self.fired_once_ids:
            self.fired_once_ids.append(eid)

        options = edef.get("options", [])
        if len(options) <= 1:
            opt_id = str(options[0]["id"]) if options else "default"
            self._apply_option(world, edef, opt_id, day, auto_resolved=True)
            is_major = bool(edef.get("major", False))
            world.emit_notification(
                category="historical_event_major" if is_major else "event_info",
                title_key=str(edef.get("title_key", eid)),
                body_key=str(edef.get("desc_key", eid)),
                severity="major" if is_major else "info",
                autopause_trigger="historical_event_major" if is_major else None,
                payload={"event_id": eid, "option_id": opt_id},
            )
        else:
            opt_ids = [str(o["id"]) for o in options]
            self.pending_choices[eid] = PendingEventChoice(
                event_id=eid,
                triggered_day=day,
                expires_day=day + self.choice_timeout_days,
                option_ids=opt_ids,
            )
            world.emit_notification(
                category="event_choice_required",
                title_key=str(edef.get("title_key", eid)),
                body_key=str(edef.get("desc_key", eid)),
                severity="warning",
                autopause_trigger="event_choice_required",
                payload={"event_id": eid, "options": opt_ids},
            )

    def _auto_resolve_pending(self, world: Any, event_id: str, day: int) -> None:
        pend = self.pending_choices.pop(event_id, None)
        if pend is None:
            return
        edef = self._defs_by_id[event_id]
        options = edef.get("options", [])
        rng = world.rng.stream("core.events.choice")
        opt_ids = [str(o["id"]) for o in options]
        weights = [max(0.0, float(o.get("ai_weight", 1.0))) for o in options]
        if sum(weights) <= 0.0:
            chosen = opt_ids[0]
        else:
            chosen = rng.weighted_choice(opt_ids, weights)
        self._apply_option(world, edef, chosen, day, auto_resolved=True)

    def _apply_option(
        self,
        world: Any,
        edef: Dict[str, Any],
        option_id: str,
        day: int,
        *,
        auto_resolved: bool,
    ) -> None:
        eid = str(edef["id"])
        options = edef.get("options", [])
        chosen_opt: Optional[Dict[str, Any]] = None
        for opt in options:
            if str(opt["id"]) == option_id:
                chosen_opt = opt
                break
        if chosen_opt is None and options:
            chosen_opt = options[0]

        summary: List[str] = []
        if chosen_opt is not None:
            for eff in chosen_opt.get("effects", []):
                summary.append(self._execute_effect(world, eff, day))

        self.history.append(
            EventLogEntry(
                event_id=eid,
                day=day,
                chosen_option_id=option_id,
                auto_resolved=auto_resolved,
                effects_summary=summary,
            )
        )

    def _execute_effect(self, world: Any, eff: Dict[str, Any], day: int) -> str:
        op = str(eff["op"])
        if op == "set_flag":
            flag = str(eff["flag"])
            val = bool(eff["value"])
            world.flags[flag] = val
            return f"set_flag:{flag}={val}"

        if op == "set_macro":
            key = str(eff["key"])
            val = eff["value"]
            world.macro.set_var(key, val)
            return f"set_macro:{key}={val}"

        if op == "add_macro":
            key = str(eff["key"])
            delta = float(eff["delta"])
            new_val = world.macro.add_var(key, delta)
            return f"add_macro:{key}+={delta}->{new_val:.4f}"

        if op == "add_cash":
            delta_usd = float(eff["delta_usd"])
            econ = world.modules.get("04_economy")
            if econ is not None and hasattr(econ, "adjust_player_cash"):
                econ.adjust_player_cash(delta_usd, memo="event")
            return f"add_cash:{delta_usd:+.2f}"

        if op == "add_reputation":
            customer = str(eff["customer"])
            delta = float(eff["delta"])
            econ = world.modules.get("04_economy")
            if econ is not None and hasattr(econ, "adjust_player_reputation"):
                econ.adjust_player_reputation(customer, delta)
            return f"add_reputation:{customer}:{delta:+.3f}"

        if op == "add_political_capital":
            delta = float(eff["delta"])
            econ = world.modules.get("04_economy")
            if econ is not None and hasattr(econ, "adjust_player_political_capital"):
                econ.adjust_player_political_capital(delta)
            return f"add_political_capital:{delta:+.2f}"

        if op == "tech_boost":
            discipline = str(eff["discipline"])
            points = float(eff["points"])
            tech_mod = world.modules.get("03_tech")
            if tech_mod is not None and hasattr(tech_mod, "apply_research_boost"):
                tech_mod.apply_research_boost(world.player_company_id, discipline, points)
            return f"tech_boost:{discipline}:{points:+.1f}"

        if op == "schedule_event":
            target_id = str(eff["event_id"])
            delay_days = int(eff.get("delay_days", 1))
            self.scheduled_events.append(ScheduledEvent(event_id=target_id, fire_day=day + delay_days))
            return f"schedule_event:{target_id}@{day + delay_days}"

        raise ValueError(f"Unsupported event effect op: {op!r}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fired_once_ids": sorted(self.fired_once_ids),
            "pending_choices": {
                k: self.pending_choices[k].to_dict() for k in sorted(self.pending_choices.keys())
            },
            "scheduled_events": [s.to_dict() for s in self.scheduled_events],
            "history": [h.to_dict() for h in self.history],
        }

    def load_dict(self, data: Dict[str, Any]) -> None:
        self.fired_once_ids = [str(x) for x in data.get("fired_once_ids", [])]
        self.pending_choices = {
            str(k): PendingEventChoice.from_dict(v)
            for k, v in sorted(data.get("pending_choices", {}).items())
        }
        self.scheduled_events = [
            ScheduledEvent.from_dict(x) for x in data.get("scheduled_events", [])
        ]
        self.history = [EventLogEntry.from_dict(x) for x in data.get("history", [])]
