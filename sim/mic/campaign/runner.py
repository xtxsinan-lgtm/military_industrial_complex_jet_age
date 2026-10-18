"""Headless campaign runner, WorldState, PlayerPolicy protocol, and `run_campaign()` entrypoint.

Owned by Module 09 (`docs/spec/09_core_loop.md`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Sequence, Union, runtime_checkable

from mic.calendar import (
    MVP_END_DAY,
    MVP_START_DAY,
    TickSchedule,
    fiscal_year,
    get_tick_schedule,
    iso_to_day,
)
from mic.campaign.contracts import (
    ACTION_CATALOG,
    ActionResult,
    Notification,
    PlayerAction,
    SimModule,
    ValidationResult,
    validate_action_schema,
)
from mic.campaign.events import EventEngine
from mic.campaign.macro import MacroEnvironment, load_core_tuning
from mic.campaign.save_load import (
    build_save_envelope,
    compute_state_hash,
    load_envelope_from_file,
    migrate_save_envelope,
    save_to_file,
)
from mic.campaign.scoring import (
    CompanyScoreBreakdown,
    check_failure_conditions,
    compute_leaderboard_and_player_score,
)
from mic.campaign.stubs import create_default_stub_modules
from mic.rng import RngStreamRegistry


def _parse_day_arg(val: Union[int, str]) -> int:
    if isinstance(val, int):
        return val
    return iso_to_day(str(val))


@runtime_checkable
class PlayerPolicy(Protocol):
    """Protocol for automated bot policies or scripted test policies."""

    def decide_actions(self, world: "WorldState", schedule: TickSchedule) -> Sequence[PlayerAction]:
        """Return an ordered sequence of `PlayerAction` commands to execute on `schedule.day`."""
        ...


class NullPolicy:
    """Passive policy that issues no commands."""

    def decide_actions(self, world: "WorldState", schedule: TickSchedule) -> Sequence[PlayerAction]:
        return ()


class HeuristicBotPolicy:
    """Reference bot policy that researches tech, resolves events, designs/tests aircraft, and bids on RFPs."""

    def __init__(self) -> None:
        self._handled_rfps: set[str] = set()

    def decide_actions(self, world: "WorldState", schedule: TickSchedule) -> Sequence[PlayerAction]:
        actions: List[PlayerAction] = []
        cid = world.player_company_id

        # 1. Resolve any pending multi-option events immediately using the first option
        for eid in sorted(world.events.pending_choices.keys()):
            pend = world.events.pending_choices[eid]
            if pend.option_ids:
                actions.append(
                    PlayerAction(
                        action_type="core.choose_event_option",
                        actor_company_id=cid,
                        params={"event_id": eid, "option_id": pend.option_ids[0]},
                    )
                )

        # 2. On game start or Jan 1, assign aero engineers to an unresearched tech node
        if schedule.day == world.start_day or schedule.is_year_start:
            tech_mod = world.modules.get("03_tech")
            if tech_mod is not None and hasattr(tech_mod, "unlocked_by_company"):
                unlocked = set(tech_mod.unlocked_by_company.get(cid, []))
                for candidate in ("swept_wing_35", "all_moving_tail", "transonic_area_rule", "mach2_inlet_variable"):
                    if candidate not in unlocked:
                        actions.append(
                            PlayerAction(
                                action_type="tech.set_allocation",
                                actor_company_id=cid,
                                params={"tech_id": candidate, "engineers_assigned": 16},
                            )
                        )
                        break

        # 3. Check open RFPs and submit a competitive proposal 5 days after issue
        proc = world.modules.get("05_procurement")
        if proc is not None and hasattr(proc, "get_open_requirements"):
            for req in proc.get_open_requirements():
                rid = str(req["id"])
                if rid in self._handled_rfps or schedule.day < int(req["issue_day"]) + 5:
                    continue
                if cid in proc.proposals.get(rid, {}):
                    self._handled_rfps.add(rid)
                    continue
                self._handled_rfps.add(rid)
                target_mach = float(req.get("target_mach", 0.9))
                thrust_n = 26000.0 + (schedule.year - 1945) * 3600.0
                actions.append(
                    PlayerAction(
                        action_type="design.create",
                        actor_company_id=cid,
                        params={
                            "name": f"Player-{rid[-4:].upper()}",
                            "role_tags": ["day_fighter"],
                            "spec": {
                                "sweep_deg": 35.0 if target_mach >= 0.85 else 15.0,
                                "thrust_N": thrust_n,
                                "wing_area_m2": 25.0,
                                "afterburner": target_mach >= 1.2,
                            },
                        },
                    )
                )
        return actions


class WorldState:
    """Authoritative container for campaign-wide state and registered domain modules."""

    def __init__(
        self,
        *,
        seed: int,
        start_day: int = MVP_START_DAY,
        end_day: int = MVP_END_DAY,
        difficulty: str = "normal",
        player_company_id: str = "mcdonnell",
        custom_startup: Optional[Dict[str, Any]] = None,
        tuning: Optional[Dict[str, Any]] = None,
        modules: Optional[Dict[str, SimModule]] = None,
        campaign_id: str = "cmp_default",
    ) -> None:
        self.tuning: Dict[str, Any] = tuning or load_core_tuning()
        if difficulty not in self.tuning["difficulty_presets"]:
            raise ValueError(f"Unknown difficulty preset: {difficulty!r}")

        self.campaign_id: str = str(campaign_id)
        self.seed: int = int(seed)
        self.start_day: int = int(start_day)
        self.end_day: int = int(end_day)
        self.day: int = int(start_day)
        self.difficulty_id: str = str(difficulty)
        self.difficulty_preset: Dict[str, Any] = dict(self.tuning["difficulty_presets"][difficulty])
        self.player_company_id: str = str(player_company_id)
        self.custom_startup: Optional[Dict[str, Any]] = dict(custom_startup) if custom_startup else None

        hist_ids = [
            str(p["company_id"]) for p in self.tuning["startup_packages"]["historical_companies"]
        ]
        if self.player_company_id not in hist_ids:
            hist_ids.append(self.player_company_id)
        self.company_ids: List[str] = sorted(set(hist_ids))

        self.rng: RngStreamRegistry = RngStreamRegistry(self.seed)
        self.macro: MacroEnvironment = MacroEnvironment(self.tuning)
        self.macro.current_fy = fiscal_year(self.start_day)

        evt_cfg = self.tuning.get("events", {})
        self.events: EventEngine = EventEngine(
            event_defs=self.tuning.get("historical_events", []),
            choice_timeout_days=int(evt_cfg.get("choice_timeout_days", 30)),
            max_mtth_events_per_month=int(evt_cfg.get("max_mtth_events_per_month", 2)),
        )

        self.flags: Dict[str, bool] = {}
        self.notifications: List[Notification] = []
        self._notif_seq: int = 1
        self.autosave_log: List[str] = []
        self.ended: bool = False
        self.outcome: str = "ongoing"
        self.outcome_reason: str = ""

        self.modules: Dict[str, SimModule] = (
            dict(modules) if modules is not None else create_default_stub_modules()
        )

    def current_schedule(self) -> TickSchedule:
        return get_tick_schedule(self.day)

    def emit_notification(
        self,
        *,
        category: str,
        title_key: str,
        body_key: str,
        severity: str = "info",
        autopause_trigger: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        nid = f"ntf_{self._notif_seq:05d}"
        self._notif_seq += 1
        notif = Notification(
            id=nid,
            day=self.day,
            category=category,
            title_key=title_key,
            body_key=body_key,
            severity=severity,
            autopause_trigger=autopause_trigger,
            payload=dict(payload) if payload else {},
        )
        self.notifications.append(notif)
        return notif

    def to_core_dict(self) -> Dict[str, Any]:
        return {
            "seed": self.seed,
            "start_day": self.start_day,
            "end_day": self.end_day,
            "day": self.day,
            "difficulty_id": self.difficulty_id,
            "player_company_id": self.player_company_id,
            "company_ids": list(self.company_ids),
            "custom_startup": dict(self.custom_startup) if self.custom_startup else None,
            "rng": self.rng.to_dict(),
            "macro": self.macro.to_dict(),
            "events": self.events.to_dict(),
            "flags": {k: bool(self.flags[k]) for k in sorted(self.flags.keys())},
            "notif_seq": self._notif_seq,
            "notifications": [n.to_dict() for n in self.notifications],
            "autosave_log": list(self.autosave_log),
            "ended": self.ended,
            "outcome": self.outcome,
            "outcome_reason": self.outcome_reason,
        }

    def load_core_dict(self, data: Dict[str, Any]) -> None:
        self.seed = int(data["seed"])
        self.start_day = int(data["start_day"])
        self.end_day = int(data["end_day"])
        self.day = int(data["day"])
        self.difficulty_id = str(data["difficulty_id"])
        self.difficulty_preset = dict(self.tuning["difficulty_presets"][self.difficulty_id])
        self.player_company_id = str(data["player_company_id"])
        self.company_ids = [str(x) for x in data["company_ids"]]
        cs = data.get("custom_startup")
        self.custom_startup = dict(cs) if isinstance(cs, dict) else None
        self.rng = RngStreamRegistry.from_dict(data["rng"])
        self.macro.load_dict(data["macro"])
        self.events.load_dict(data["events"])
        self.flags = {str(k): bool(v) for k, v in data.get("flags", {}).items()}
        self._notif_seq = int(data.get("notif_seq", 1))
        self.notifications = [Notification.from_dict(x) for x in data.get("notifications", [])]
        self.autosave_log = [str(x) for x in data.get("autosave_log", [])]
        self.ended = bool(data.get("ended", False))
        self.outcome = str(data.get("outcome", "ongoing"))
        self.outcome_reason = str(data.get("outcome_reason", ""))


@dataclass
class CampaignResult:
    """Summary returned by `run_campaign()`."""

    seed: int
    start_day: int
    end_day: int
    final_day: int
    days_simulated: int
    ended: bool
    outcome: str
    outcome_reason: str
    state_hash: str
    player_score: CompanyScoreBreakdown
    leaderboard: List[CompanyScoreBreakdown]
    events_fired_count: int
    notifications_count: int
    autosaves_recorded: List[str] = field(default_factory=list)


class Campaign:
    """Deterministic simulation controller orchestrating modules 01..10 across daily/monthly ticks."""

    def __init__(self, world: WorldState, *, initialize_modules: bool = True) -> None:
        self.world: WorldState = world
        if initialize_modules:
            for mid in sorted(self.world.modules.keys()):
                self.world.modules[mid].init_new_game(self.world)

    @classmethod
    def new_game(
        cls,
        *,
        seed: int = 42,
        start: Union[int, str] = MVP_START_DAY,
        end: Union[int, str] = MVP_END_DAY,
        difficulty: str = "normal",
        company_id: str = "mcdonnell",
        custom_startup: Optional[Dict[str, Any]] = None,
        modules: Optional[Dict[str, SimModule]] = None,
        campaign_id: str = "cmp_default",
    ) -> "Campaign":
        s_day = _parse_day_arg(start)
        e_day = _parse_day_arg(end)
        if e_day < s_day:
            raise ValueError(f"end ({e_day}) must be >= start ({s_day})")
        world = WorldState(
            seed=seed,
            start_day=s_day,
            end_day=e_day,
            difficulty=difficulty,
            player_company_id=company_id,
            custom_startup=custom_startup,
            modules=modules,
            campaign_id=campaign_id,
        )
        return cls(world, initialize_modules=True)

    def validate_action(self, action: PlayerAction) -> ValidationResult:
        """Validate `action` against both the catalog schema and domain module state."""
        schema_res = validate_action_schema(action)
        if not schema_res.ok:
            return schema_res

        spec = ACTION_CATALOG[action.action_type]
        if spec.owner_module == "09_core_loop":
            return self._validate_core_action(action)

        mod = self.world.modules.get(spec.owner_module)
        if mod is None:
            return ValidationResult(False, "ERR_MODULE_MISSING", f"Module {spec.owner_module} not registered")
        return mod.validate_action(self.world, action)

    def submit_action(self, action: PlayerAction) -> ActionResult:
        """Validate and execute a single `PlayerAction`."""
        val = self.validate_action(action)
        if not val.ok:
            return ActionResult(ok=False, code=val.code, message=val.message)

        spec = ACTION_CATALOG[action.action_type]
        if spec.owner_module == "09_core_loop":
            return self._apply_core_action(action)

        mod = self.world.modules[spec.owner_module]
        res = mod.apply_action(self.world, action)

        # Convenience auto-chaining for HeuristicBotPolicy when a design is created during an open RFP:
        return res

    def _validate_core_action(self, action: PlayerAction) -> ValidationResult:
        if action.action_type == "core.choose_event_option":
            eid = str(action.params["event_id"])
            oid = str(action.params["option_id"])
            pend = self.world.events.pending_choices.get(eid)
            if pend is None:
                return ValidationResult(False, "ERR_EVENT_NOT_PENDING", f"Event {eid} is not pending choice")
            if oid not in pend.option_ids:
                return ValidationResult(False, "ERR_INVALID_EVENT_OPTION", f"Invalid option {oid} for {eid}")
            return ValidationResult(True)

        if action.action_type == "core.dismiss_notification":
            nid = str(action.params["notification_id"])
            for n in self.world.notifications:
                if n.id == nid:
                    return ValidationResult(True)
            return ValidationResult(False, "ERR_NOTIFICATION_NOT_FOUND", f"Notification {nid} not found")

        return ValidationResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def _apply_core_action(self, action: PlayerAction) -> ActionResult:
        if action.action_type == "core.choose_event_option":
            eid = str(action.params["event_id"])
            oid = str(action.params["option_id"])
            self.world.events.choose_option(self.world, eid, oid)
            return ActionResult(True, "OK", "Event option selected", {"event_id": eid, "option_id": oid})

        if action.action_type == "core.dismiss_notification":
            nid = str(action.params["notification_id"])
            for n in self.world.notifications:
                if n.id == nid:
                    n.dismissed = True
                    return ActionResult(True, "OK", "Notification dismissed", {"notification_id": nid})
            return ActionResult(False, "ERR_NOTIFICATION_NOT_FOUND", f"Notification {nid} not found")

        return ActionResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def step_day(self, player_policy: Optional[PlayerPolicy] = None) -> TickSchedule:
        """Advance the campaign by one simulated day following the canonical update order."""
        if self.world.ended:
            return self.world.current_schedule()

        schedule = self.world.current_schedule()

        # Phase A: Monthly settlement on the 1st of the month (for the month that just ended)
        if schedule.is_month_start and schedule.day > self.world.start_day:
            self._run_monthly_tick(schedule)
            if self.world.ended:
                return schedule

        # Phase B: US Federal Fiscal Year rollover on July 1
        if schedule.is_fiscal_year_start:
            self._run_fiscal_year_rollover(schedule.fiscal_year)

        # Phase C: Canonical Daily Tick across all modules
        # 1. Date-triggered & scheduled historical events
        self.world.events.on_day_tick(self.world, schedule)

        # 2. Reserved war module slot + 03_tech, 02_engines, 01_aero_design, 06_testing, 04_economy, 05_procurement, 07_ai
        for mid in (
            "11_war_reserved",
            "03_tech",
            "02_engines",
            "01_aero_design",
            "06_testing",
            "04_economy",
            "05_procurement",
            "07_ai",
        ):
            mod = self.world.modules.get(mid)
            if mod is not None:
                mod.on_day_tick(self.world, schedule)

        # 3. Execute player/bot policy actions for today
        if player_policy is not None:
            actions = player_policy.decide_actions(self.world, schedule)
            for act in actions:
                res = self.submit_action(act)
                if res.ok and act.action_type == "design.create" and isinstance(player_policy, HeuristicBotPolicy):
                    did = str(res.data["design_id"])
                    self.submit_action(
                        PlayerAction("design.freeze", act.actor_company_id, {"design_id": did})
                    )
                    self.submit_action(
                        PlayerAction(
                            "test.run_wind_tunnel",
                            act.actor_company_id,
                            {"design_id": did, "facility": "company", "regime": "subsonic"},
                        )
                    )
                    proc = self.world.modules.get("05_procurement")
                    if proc is not None and hasattr(proc, "get_open_requirements"):
                        for req in proc.get_open_requirements():
                            rid = str(req["id"])
                            if act.actor_company_id not in proc.proposals.get(rid, {}):
                                self.submit_action(
                                    PlayerAction(
                                        "proc.submit_proposal",
                                        act.actor_company_id,
                                        {
                                            "requirement_id": rid,
                                            "design_id": did,
                                            "bid_unit_price_usd": round(
                                                float(req["unit_price_ceiling_usd"]) * 0.90, 2
                                            ),
                                        },
                                    )
                                )
                                break

        # 4. Post-day failure & end-of-campaign check
        failed, out_code, reason = check_failure_conditions(self.world)
        if failed:
            self.world.ended = True
            self.world.outcome = out_code
            self.world.outcome_reason = reason
            return schedule

        if schedule.day >= self.world.end_day:
            self.world.ended = True
            self.world.outcome = "completed_1960"
            self.world.outcome_reason = f"Reached campaign end date {schedule.iso}"
            return schedule

        self.world.day += 1
        return schedule

    def _run_monthly_tick(self, schedule: TickSchedule) -> None:
        for mid in ("03_tech", "02_engines", "06_testing", "05_procurement", "04_economy", "07_ai"):
            mod = self.world.modules.get(mid)
            if mod is not None:
                mod.on_month_start(self.world, schedule)

        self.world.events.on_month_start(self.world, schedule)

        failed, out_code, reason = check_failure_conditions(self.world)
        if failed:
            self.world.ended = True
            self.world.outcome = out_code
            self.world.outcome_reason = reason
            return

        # Record rotating monthly autosave slot (0, 1, 2) + Jan 1 yearly archive
        slots = int(self.world.tuning["autosave"]["monthly_rotating_slots"])
        month_seq = (schedule.year - 1945) * 12 + (schedule.month - 1)
        slot_idx = month_seq % slots
        self.world.autosave_log.append(f"autosave_slot_{slot_idx}:{schedule.iso}")
        if schedule.is_year_start and self.world.tuning["autosave"].get("yearly_archive_on_jan1", True):
            self.world.autosave_log.append(f"autosave_yearly_{schedule.year}:{schedule.iso}")

    def _run_fiscal_year_rollover(self, new_fy: int) -> None:
        self.world.macro.current_fy = new_fy
        for mid in ("05_procurement", "04_economy", "07_ai"):
            mod = self.world.modules.get(mid)
            if mod is not None:
                mod.on_fiscal_year_start(self.world, new_fy)

    def state_hash(self) -> str:
        """Compute canonical SHA-256 hash of the entire campaign state."""
        return compute_state_hash(self.world)

    def to_envelope(self) -> Dict[str, Any]:
        return build_save_envelope(self.world)

    @classmethod
    def from_envelope(
        cls,
        envelope: Dict[str, Any],
        *,
        modules: Optional[Dict[str, SimModule]] = None,
    ) -> "Campaign":
        mods = dict(modules) if modules is not None else create_default_stub_modules()
        target_mod_versions = {mid: int(getattr(m, "schema_version", 1)) for mid, m in mods.items()}
        migrated = migrate_save_envelope(envelope, target_module_versions=target_mod_versions)

        wdata = migrated["world_state"]
        world = WorldState(
            seed=int(wdata["seed"]),
            start_day=int(wdata["start_day"]),
            end_day=int(wdata["end_day"]),
            difficulty=str(wdata["difficulty_id"]),
            player_company_id=str(wdata["player_company_id"]),
            custom_startup=wdata.get("custom_startup"),
            modules=mods,
            campaign_id=str(migrated.get("campaign_id", "cmp_default")),
        )
        world.load_core_dict(wdata)
        for mid, mblock in sorted(migrated.get("modules", {}).items()):
            if mid in world.modules:
                world.modules[mid].load_dict(mblock["state"])

        return cls(world, initialize_modules=False)

    def save(self, path: Union[str, Path], *, compress: bool = False) -> Path:
        return save_to_file(self.world, path, compress=compress)

    @classmethod
    def load(cls, path: Union[str, Path], *, modules: Optional[Dict[str, SimModule]] = None) -> "Campaign":
        env = load_envelope_from_file(path)
        return cls.from_envelope(env, modules=modules)


def run_campaign(
    seed: int = 42,
    player_policy: Optional[PlayerPolicy] = None,
    start: Union[int, str] = MVP_START_DAY,
    end: Union[int, str] = MVP_END_DAY,
    *,
    difficulty: str = "normal",
    company_id: str = "mcdonnell",
    custom_startup: Optional[Dict[str, Any]] = None,
    modules: Optional[Dict[str, SimModule]] = None,
) -> CampaignResult:
    """Run a deterministic headless campaign from `start` to `end` (or early termination)."""
    policy = player_policy if player_policy is not None else HeuristicBotPolicy()
    cmp = Campaign.new_game(
        seed=seed,
        start=start,
        end=end,
        difficulty=difficulty,
        company_id=company_id,
        custom_startup=custom_startup,
        modules=modules,
    )
    days_sim = 0
    while not cmp.world.ended:
        cmp.step_day(policy)
        days_sim += 1

    player_score, leaderboard = compute_leaderboard_and_player_score(cmp.world)
    return CampaignResult(
        seed=cmp.world.seed,
        start_day=cmp.world.start_day,
        end_day=cmp.world.end_day,
        final_day=cmp.world.day,
        days_simulated=days_sim,
        ended=cmp.world.ended,
        outcome=cmp.world.outcome,
        outcome_reason=cmp.world.outcome_reason,
        state_hash=cmp.state_hash(),
        player_score=player_score,
        leaderboard=leaderboard,
        events_fired_count=len(cmp.world.events.history),
        notifications_count=len(cmp.world.notifications),
        autosaves_recorded=list(cmp.world.autosave_log),
    )
