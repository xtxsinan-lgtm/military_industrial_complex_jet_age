"""Self-contained deterministic stub modules (01..07) for standalone campaign execution.

Owned by Module 09 (`docs/spec/09_core_loop.md`) per `00_conventions.md` §5.1:
"Cross-module dependency before the other module exists: write a minimal clearly-labelled
stub inside your own package and replace it later; never edit another module's files."
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mic.calendar import TickSchedule, iso_to_day
from mic.campaign.contracts import (
    ActionResult,
    PlayerAction,
    SimModule,
    ValidationResult,
)


class StubTechModule(SimModule):
    """Stub for Module 03 (`03_tech`): tracks tech nodes, engineer allocations, and boosts."""

    module_id: str = "03_tech"
    schema_version: int = 1

    _DEFAULT_NODES: Dict[str, Dict[str, Any]] = {
        "swept_wing_35": {"discipline": "aero", "cost": 300.0, "year": 1945},
        "axial_compressor_1": {"discipline": "propulsion", "cost": 350.0, "year": 1945},
        "transonic_area_rule": {"discipline": "aero", "cost": 550.0, "year": 1951},
        "afterburner_1": {"discipline": "propulsion", "cost": 400.0, "year": 1947},
        "all_moving_tail": {"discipline": "aero", "cost": 320.0, "year": 1947},
        "titanium_structures": {"discipline": "structures", "cost": 500.0, "year": 1950},
        "pulse_radar_fcs": {"discipline": "systems", "cost": 420.0, "year": 1948},
        "mach2_inlet_variable": {"discipline": "aero", "cost": 650.0, "year": 1953},
    }

    def __init__(self) -> None:
        self.unlocked_by_company: Dict[str, List[str]] = {}
        self.progress_by_company: Dict[str, Dict[str, float]] = {}
        self.allocations_by_company: Dict[str, Dict[str, int]] = {}

    def init_new_game(self, world: Any) -> None:
        for cid in sorted(world.company_ids):
            self.unlocked_by_company[cid] = ["baseline_1945"]
            self.progress_by_company[cid] = {}
            self.allocations_by_company[cid] = {}

    def on_fiscal_year_start(self, world: Any, fy: int) -> None:
        pass

    def on_month_start(self, world: Any, schedule: TickSchedule) -> None:
        pass

    def on_day_tick(self, world: Any, schedule: TickSchedule) -> None:
        for cid in sorted(self.allocations_by_company.keys()):
            allocs = self.allocations_by_company[cid]
            unlocked = self.unlocked_by_company.setdefault(cid, [])
            prog = self.progress_by_company.setdefault(cid, {})
            for tech_id in sorted(list(allocs.keys())):
                eng = int(allocs.get(tech_id, 0))
                if eng <= 0 or tech_id in unlocked:
                    continue
                node = self._DEFAULT_NODES.get(tech_id, {"cost": 400.0})
                cost = float(node["cost"])
                prog[tech_id] = float(prog.get(tech_id, 0.0)) + eng * 0.25
                if prog[tech_id] >= cost:
                    unlocked.append(tech_id)
                    unlocked.sort()
                    allocs[tech_id] = 0
                    if cid == world.player_company_id:
                        world.emit_notification(
                            category="tech_unlocked",
                            title_key="notif.tech_unlocked.title",
                            body_key="notif.tech_unlocked.body",
                            severity="info",
                            autopause_trigger="tech_unlocked",
                            payload={"tech_id": tech_id},
                        )

    def apply_research_boost(self, company_id: str, discipline: str, points: float) -> None:
        unlocked = self.unlocked_by_company.setdefault(company_id, [])
        prog = self.progress_by_company.setdefault(company_id, {})
        for tech_id in sorted(self._DEFAULT_NODES.keys()):
            if tech_id in unlocked:
                continue
            node = self._DEFAULT_NODES[tech_id]
            if node["discipline"] == discipline:
                prog[tech_id] = float(prog.get(tech_id, 0.0)) + float(points)
                if prog[tech_id] >= float(node["cost"]):
                    unlocked.append(tech_id)
                    unlocked.sort()
                break

    def validate_action(self, world: Any, action: PlayerAction) -> ValidationResult:
        cid = action.actor_company_id
        if action.action_type == "tech.set_allocation":
            tech_id = str(action.params["tech_id"])
            if tech_id in self.unlocked_by_company.get(cid, []):
                return ValidationResult(False, "ERR_TECH_ALREADY_UNLOCKED", f"{tech_id} already unlocked")
            return ValidationResult(True)
        if action.action_type == "tech.cancel_research":
            return ValidationResult(True)
        return ValidationResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def apply_action(self, world: Any, action: PlayerAction) -> ActionResult:
        cid = action.actor_company_id
        allocs = self.allocations_by_company.setdefault(cid, {})
        if action.action_type == "tech.set_allocation":
            tech_id = str(action.params["tech_id"])
            eng = int(action.params["engineers_assigned"])
            allocs[tech_id] = eng
            return ActionResult(True, "OK", "Allocation updated", {"tech_id": tech_id, "engineers": eng})
        if action.action_type == "tech.cancel_research":
            tech_id = str(action.params["tech_id"])
            allocs.pop(tech_id, None)
            return ActionResult(True, "OK", "Research cancelled", {"tech_id": tech_id})
        return ActionResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unlocked_by_company": {
                k: list(self.unlocked_by_company[k]) for k in sorted(self.unlocked_by_company.keys())
            },
            "progress_by_company": {
                k: dict(self.progress_by_company[k]) for k in sorted(self.progress_by_company.keys())
            },
            "allocations_by_company": {
                k: dict(self.allocations_by_company[k]) for k in sorted(self.allocations_by_company.keys())
            },
        }

    def load_dict(self, data: Dict[str, Any]) -> None:
        self.unlocked_by_company = {
            k: [str(x) for x in v] for k, v in data.get("unlocked_by_company", {}).items()
        }
        self.progress_by_company = {
            k: { str(tk): float(tv) for tk, tv in v.items() }
            for k, v in data.get("progress_by_company", {}).items()
        }
        self.allocations_by_company = {
            k: { str(tk): int(tv) for tk, tv in v.items() }
            for k, v in data.get("allocations_by_company", {}).items()
        }


class StubEngineModule(SimModule):
    """Stub for Module 02 (`02_engines`): manages catalog engines and engine R&D projects."""

    module_id: str = "02_engines"
    schema_version: int = 1

    def __init__(self) -> None:
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.available_engines: List[str] = ["j33_a_35", "j34_we_34", "j35_a_17", "j47_ge_13", "j57_p_1", "j79_ge_2"]
        self._next_seq: int = 1

    def init_new_game(self, world: Any) -> None:
        self.projects = {}
        self._next_seq = 1

    def on_fiscal_year_start(self, world: Any, fy: int) -> None:
        pass

    def on_month_start(self, world: Any, schedule: TickSchedule) -> None:
        pass

    def on_day_tick(self, world: Any, schedule: TickSchedule) -> None:
        for pid in sorted(self.projects.keys()):
            proj = self.projects[pid]
            if proj.get("status") != "active":
                continue
            eng = int(proj.get("engineers_assigned", 0))
            if eng <= 0:
                continue
            proj["progress_days"] = float(proj.get("progress_days", 0.0)) + min(3.0, eng / 10.0)
            if proj["progress_days"] >= float(proj["required_days"]):
                proj["status"] = "completed"
                engine_id = f"eng_{pid}"
                if engine_id not in self.available_engines:
                    self.available_engines.append(engine_id)
                if proj["company_id"] == world.player_company_id:
                    world.emit_notification(
                        category="engine_rd_complete",
                        title_key="notif.engine_complete.title",
                        body_key="notif.engine_complete.body",
                        severity="info",
                        autopause_trigger="engine_rd_complete",
                        payload={"project_id": pid, "engine_id": engine_id},
                    )

    def validate_action(self, world: Any, action: PlayerAction) -> ValidationResult:
        if action.action_type == "engine.start_project":
            return ValidationResult(True)
        if action.action_type in ("engine.set_engineers", "engine.cancel_project"):
            pid = str(action.params["project_id"])
            if pid not in self.projects:
                return ValidationResult(False, "ERR_ENGINE_PROJECT_NOT_FOUND", f"Unknown project {pid}")
            return ValidationResult(True)
        return ValidationResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def apply_action(self, world: Any, action: PlayerAction) -> ActionResult:
        if action.action_type == "engine.start_project":
            pid = f"eproj_{self._next_seq:03d}"
            self._next_seq += 1
            self.projects[pid] = {
                "project_id": pid,
                "company_id": action.actor_company_id,
                "name": str(action.params["name"]),
                "architecture": str(action.params["architecture"]),
                "target_thrust_dry_N": float(action.params["target_thrust_dry_N"]),
                "afterburner": bool(action.params["afterburner"]),
                "opr": float(action.params["opr"]),
                "tit_K": float(action.params["tit_K"]),
                "engineers_assigned": int(action.params["engineers_assigned"]),
                "progress_days": 0.0,
                "required_days": 180.0,
                "status": "active",
            }
            return ActionResult(True, "OK", "Engine project started", {"project_id": pid})

        if action.action_type == "engine.set_engineers":
            pid = str(action.params["project_id"])
            self.projects[pid]["engineers_assigned"] = int(action.params["engineers_assigned"])
            return ActionResult(True, "OK", "Engine project engineers updated", {"project_id": pid})

        if action.action_type == "engine.cancel_project":
            pid = str(action.params["project_id"])
            self.projects[pid]["status"] = "cancelled"
            self.projects[pid]["engineers_assigned"] = 0
            return ActionResult(True, "OK", "Engine project cancelled", {"project_id": pid})

        return ActionResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "next_seq": self._next_seq,
            "available_engines": list(self.available_engines),
            "projects": {k: dict(self.projects[k]) for k in sorted(self.projects.keys())},
        }

    def load_dict(self, data: Dict[str, Any]) -> None:
        self._next_seq = int(data.get("next_seq", 1))
        self.available_engines = [str(x) for x in data.get("available_engines", [])]
        self.projects = {k: dict(v) for k, v in data.get("projects", {}).items()}


class StubAeroDesignModule(SimModule):
    """Stub for Module 01 (`01_aero_design`): manages `AircraftDesign` records and performance estimates."""

    module_id: str = "01_aero_design"
    schema_version: int = 1

    def __init__(self) -> None:
        self.designs: Dict[str, Dict[str, Any]] = {}
        self._next_seq: int = 1

    def init_new_game(self, world: Any) -> None:
        self.designs = {}
        self._next_seq = 1

    def on_fiscal_year_start(self, world: Any, fy: int) -> None:
        pass

    def on_month_start(self, world: Any, schedule: TickSchedule) -> None:
        pass

    def on_day_tick(self, world: Any, schedule: TickSchedule) -> None:
        pass

    def get_design(self, design_id: str) -> Optional[Dict[str, Any]]:
        return self.designs.get(design_id)

    def _compute_stub_performance(self, spec: Dict[str, Any], created_day: int) -> Dict[str, float]:
        sweep_deg = float(spec.get("sweep_deg", 0.0))
        thrust_n = float(spec.get("thrust_N", 22000.0))
        wing_area_m2 = max(12.0, float(spec.get("wing_area_m2", 26.0)))
        afterburner = bool(spec.get("afterburner", False))
        year_bonus = max(0.0, (created_day / 365.25) * 0.04)
        ab_bonus = 0.35 if afterburner else 0.0
        max_mach_alt = min(2.4, 0.78 + (sweep_deg / 45.0) * 0.25 + (thrust_n / 60000.0) * 0.30 + ab_bonus + year_bonus)
        return {
            "max_mach_sl": round(max_mach_alt * 0.82, 4),
            "max_mach_alt": round(max_mach_alt, 4),
            "service_ceiling_m": round(11500.0 + (thrust_n / wing_area_m2) * 3.2, 1),
            "climb_rate_sl_mps": round(28.0 + (thrust_n / 1000.0) * 1.4, 2),
            "combat_radius_m": round(550000.0 + wing_area_m2 * 12000.0, 1),
            "unit_flyaway_cost_usd": round(180000.0 + thrust_n * 8.5 + (60000.0 if afterburner else 0.0), 2),
        }

    def validate_action(self, world: Any, action: PlayerAction) -> ValidationResult:
        if action.action_type == "design.create":
            return ValidationResult(True)
        if action.action_type in ("design.modify", "design.freeze"):
            did = str(action.params["design_id"])
            d = self.designs.get(did)
            if d is None:
                return ValidationResult(False, "ERR_DESIGN_NOT_FOUND", f"Design {did} not found")
            if d["company_id"] != action.actor_company_id:
                return ValidationResult(False, "ERR_DESIGN_OWNERSHIP", f"Design {did} not owned by actor")
            if d.get("frozen", False):
                return ValidationResult(False, "ERR_DESIGN_FROZEN", f"Design {did} is already frozen")
            return ValidationResult(True)
        if action.action_type == "design.clone":
            src = str(action.params["source_design_id"])
            if src not in self.designs:
                return ValidationResult(False, "ERR_DESIGN_NOT_FOUND", f"Source design {src} not found")
            return ValidationResult(True)
        return ValidationResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def apply_action(self, world: Any, action: PlayerAction) -> ActionResult:
        if action.action_type == "design.create":
            did = f"dsn_{self._next_seq:03d}"
            self._next_seq += 1
            spec = dict(action.params["spec"])
            perf = self._compute_stub_performance(spec, world.day)
            self.designs[did] = {
                "id": did,
                "name": str(action.params["name"]),
                "company_id": action.actor_company_id,
                "created_date": world.day,
                "role_tags": [str(x) for x in action.params["role_tags"]],
                "spec": spec,
                "performance": perf,
                "frozen": False,
            }
            return ActionResult(True, "OK", "Design created", {"design_id": did, "performance": perf})

        if action.action_type == "design.modify":
            did = str(action.params["design_id"])
            d = self.designs[did]
            d["spec"].update(dict(action.params["patch"]))
            d["performance"] = self._compute_stub_performance(d["spec"], d["created_date"])
            return ActionResult(True, "OK", "Design modified", {"design_id": did})

        if action.action_type == "design.clone":
            src_id = str(action.params["source_design_id"])
            src = self.designs[src_id]
            did = f"dsn_{self._next_seq:03d}"
            self._next_seq += 1
            spec = dict(src["spec"])
            perf = self._compute_stub_performance(spec, world.day)
            self.designs[did] = {
                "id": did,
                "name": str(action.params["new_name"]),
                "company_id": action.actor_company_id,
                "created_date": world.day,
                "role_tags": list(src["role_tags"]),
                "spec": spec,
                "performance": perf,
                "frozen": False,
            }
            return ActionResult(True, "OK", "Design cloned", {"design_id": did})

        if action.action_type == "design.freeze":
            did = str(action.params["design_id"])
            self.designs[did]["frozen"] = True
            return ActionResult(True, "OK", "Design frozen", {"design_id": did})

        return ActionResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "next_seq": self._next_seq,
            "designs": {k: dict(self.designs[k]) for k in sorted(self.designs.keys())},
        }

    def load_dict(self, data: Dict[str, Any]) -> None:
        self._next_seq = int(data.get("next_seq", 1))
        self.designs = {k: dict(v) for k, v in data.get("designs", {}).items()}


class StubTestingModule(SimModule):
    """Stub for Module 06 (`06_testing`): wind tunnel, prototypes, flight test, and hidden flaws."""

    module_id: str = "06_testing"
    schema_version: int = 1

    def __init__(self) -> None:
        self.by_design: Dict[str, Dict[str, Any]] = {}

    def init_new_game(self, world: Any) -> None:
        self.by_design = {}

    def on_fiscal_year_start(self, world: Any, fy: int) -> None:
        pass

    def on_month_start(self, world: Any, schedule: TickSchedule) -> None:
        pass

    def on_day_tick(self, world: Any, schedule: TickSchedule) -> None:
        for did in sorted(self.by_design.keys()):
            rec = self.by_design[did]
            if rec.get("proto_days_remaining", 0) > 0:
                rec["proto_days_remaining"] -= 1
                if rec["proto_days_remaining"] == 0:
                    rec["prototypes_ready"] = int(rec.get("prototypes_ordered", 1))
                    world.emit_notification(
                        category="prototype_first_flight",
                        title_key="notif.proto_ready.title",
                        body_key="notif.proto_ready.body",
                        severity="info",
                        autopause_trigger="prototype_first_flight",
                        payload={"design_id": did},
                    )
            if rec.get("flight_test_days_remaining", 0) > 0:
                rec["flight_test_days_remaining"] -= 1
                if rec["flight_test_days_remaining"] == 0:
                    rec["sigma"] = max(0.01, float(rec.get("sigma", 0.08)) * 0.4)
                    rec["flight_tested"] = True

    def get_testing_bonus(self, design_id: str) -> float:
        rec = self.by_design.get(design_id, {})
        bonus = 0.0
        if rec.get("tunnel_tested"):
            bonus += 0.06
        if rec.get("prototypes_ready", 0) > 0:
            bonus += 0.08
        if rec.get("flight_tested"):
            bonus += 0.10
        return bonus

    def _ensure_rec(self, design_id: str) -> Dict[str, Any]:
        if design_id not in self.by_design:
            self.by_design[design_id] = {
                "sigma": 0.12,
                "tunnel_tested": False,
                "prototypes_ordered": 0,
                "prototypes_ready": 0,
                "proto_days_remaining": 0,
                "flight_test_days_remaining": 0,
                "flight_tested": False,
                "flaws": {"flaw_flutter_1": {"fixed": False, "cost_usd": 120000.0}},
            }
        return self.by_design[design_id]

    def validate_action(self, world: Any, action: PlayerAction) -> ValidationResult:
        did = str(action.params.get("design_id", ""))
        aero = world.modules.get("01_aero_design")
        if aero is not None:
            d = aero.get_design(did)
            if d is None:
                return ValidationResult(False, "ERR_DESIGN_NOT_FOUND", f"Design {did} not found")
            if not d.get("frozen", False):
                return ValidationResult(False, "ERR_DESIGN_NOT_FROZEN", f"Design {did} must be frozen before testing")
        if action.action_type == "test.schedule_flight_test":
            rec = self._ensure_rec(did)
            if rec.get("prototypes_ready", 0) <= 0 and rec.get("prototypes_ordered", 0) <= 0:
                return ValidationResult(False, "ERR_NO_PROTOTYPE", f"Design {did} has no prototype ordered/ready")
        if action.action_type == "test.fix_flaw":
            rec = self._ensure_rec(did)
            flaw_id = str(action.params["flaw_id"])
            if flaw_id not in rec.get("flaws", {}):
                return ValidationResult(False, "ERR_FLAW_NOT_FOUND", f"Flaw {flaw_id} not found on {did}")
        return ValidationResult(True)

    def apply_action(self, world: Any, action: PlayerAction) -> ActionResult:
        did = str(action.params["design_id"])
        rec = self._ensure_rec(did)
        econ = world.modules.get("04_economy")

        if action.action_type == "test.run_wind_tunnel":
            cost = 45000.0 if action.params["facility"] == "naca" else 20000.0
            if econ is not None:
                econ.post_expense(action.actor_company_id, cost, "testing", "wind_tunnel")
            rec["tunnel_tested"] = True
            rec["sigma"] = max(0.03, float(rec["sigma"]) * 0.65)
            return ActionResult(True, "OK", "Wind tunnel test completed", {"design_id": did, "sigma": rec["sigma"]})

        if action.action_type == "test.build_prototype":
            qty = int(action.params["quantity"])
            cost = 350000.0 * qty
            if econ is not None:
                econ.post_expense(action.actor_company_id, cost, "testing", "build_prototype")
            rec["prototypes_ordered"] = qty
            rec["proto_days_remaining"] = 30
            return ActionResult(True, "OK", "Prototype construction started", {"design_id": did, "quantity": qty})

        if action.action_type == "test.schedule_flight_test":
            cost = 150000.0
            if econ is not None:
                econ.post_expense(action.actor_company_id, cost, "testing", "flight_test")
            rec["flight_test_days_remaining"] = 20
            return ActionResult(True, "OK", "Flight test scheduled", {"design_id": did})

        if action.action_type == "test.fix_flaw":
            flaw_id = str(action.params["flaw_id"])
            flaw = rec["flaws"][flaw_id]
            cost = float(flaw.get("cost_usd", 100000.0))
            if econ is not None:
                econ.post_expense(action.actor_company_id, cost, "testing", f"fix_{flaw_id}")
            flaw["fixed"] = True
            return ActionResult(True, "OK", "Flaw fixed", {"design_id": did, "flaw_id": flaw_id})

        return ActionResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def to_dict(self) -> Dict[str, Any]:
        return {"by_design": {k: dict(self.by_design[k]) for k in sorted(self.by_design.keys())}}

    def load_dict(self, data: Dict[str, Any]) -> None:
        self.by_design = {k: dict(v) for k, v in data.get("by_design", {}).items()}


class StubEconomyModule(SimModule):
    """Stub for Module 04 (`04_economy`): company finances, engineers, facilities, production, loans."""

    module_id: str = "04_economy"
    schema_version: int = 1

    def __init__(self) -> None:
        self.companies: Dict[str, Dict[str, Any]] = {}
        self.contracts: Dict[str, Dict[str, Any]] = {}
        self.starting_net_worth_usd: Dict[str, float] = {}
        self.insolvent_days: int = 0
        self.idle_months: int = 0

    def init_new_game(self, world: Any) -> None:
        self.companies = {}
        self.contracts = {}
        self.starting_net_worth_usd = {}
        self.insolvent_days = 0
        self.idle_months = 0

        diff = world.difficulty_preset
        cash_mult = float(diff.get("starting_cash_mult", 1.0))

        hist_pkgs = {
            str(p["company_id"]): p
            for p in world.tuning["startup_packages"]["historical_companies"]
        }

        for cid in sorted(world.company_ids):
            is_player = cid == world.player_company_id
            if is_player and world.custom_startup is not None:
                base = dict(world.tuning["startup_packages"]["custom_startup_base"])
                bg_id = str(world.custom_startup.get("founder_background", "ex_naca_aerodynamicist"))
                bg = world.tuning["startup_packages"]["founder_backgrounds"].get(bg_id, {})
                cash = (float(base["starting_cash_usd"]) + float(bg.get("cash_delta_usd", 0.0))) * cash_mult
                rep = dict(base["reputation"])
                for rk, rv in bg.get("reputation_delta", {}).items():
                    rep[rk] = max(0.05, min(0.95, float(rep.get(rk, 0.35)) + float(rv)))
                eng = dict(base["engineers"])
                for ek, ev in bg.get("engineers_delta", {}).items():
                    eng[ek] = max(2, int(eng.get(ek, 10)) + int(ev))
                fac = dict(base["facilities"])
                fac["factory_floor_m2"] = float(fac["factory_floor_m2"]) + float(
                    bg.get("factory_floor_delta_m2", 0.0)
                )
                if bg.get("grant_test_site"):
                    fac["test_site"] = True
                pol = float(base["political_capital"]) + float(bg.get("political_capital_delta", 0.0))
                name = str(world.custom_startup.get("company_name", "Custom Aero Corp"))
            else:
                pkg = hist_pkgs.get(cid, world.tuning["startup_packages"]["historical_companies"][0])
                cash = float(pkg["starting_cash_usd"]) * (cash_mult if is_player else 1.0)
                rep = dict(pkg["reputation"])
                eng = dict(pkg["engineers"])
                fac = dict(pkg["facilities"])
                pol = float(pkg["political_capital"])
                name = str(pkg["display_name_key"])

            self.companies[cid] = {
                "id": cid,
                "name": name,
                "is_player": is_player,
                "cash_usd": cash,
                "debt_usd": 0.0,
                "reputation": rep,
                "political_capital": pol,
                "engineers": eng,
                "facilities": fac,
                "aircraft_delivered_total": 0,
                "contracts_won_total": 0,
            }
            self.starting_net_worth_usd[cid] = self.compute_net_worth(cid)

    def get_player_company(self) -> Dict[str, Any]:
        for c in self.companies.values():
            if c.get("is_player"):
                return c
        return next(iter(self.companies.values()))

    def compute_net_worth(self, company_id: str) -> float:
        c = self.companies[company_id]
        fac = c["facilities"]
        fac_val = (
            float(fac["factory_floor_m2"]) * 45.0
            + int(fac["wind_tunnel_level"]) * 450000.0
            + (600000.0 if fac.get("test_site") else 0.0)
        )
        return float(c["cash_usd"]) - float(c["debt_usd"]) + fac_val

    def adjust_player_cash(self, delta_usd: float, memo: str = "") -> None:
        comp = self.get_player_company()
        comp["cash_usd"] = float(comp["cash_usd"]) + float(delta_usd)

    def adjust_player_reputation(self, customer: str, delta: float) -> None:
        comp = self.get_player_company()
        rep = comp["reputation"]
        rep[customer] = max(0.0, min(1.0, float(rep.get(customer, 0.5)) + float(delta)))

    def adjust_player_political_capital(self, delta: float) -> None:
        comp = self.get_player_company()
        comp["political_capital"] = max(0.0, min(100.0, float(comp["political_capital"]) + float(delta)))

    def post_expense(self, company_id: str, amount_usd: float, category: str, memo: str = "") -> None:
        c = self.companies[company_id]
        c["cash_usd"] = float(c["cash_usd"]) - abs(float(amount_usd))

    def register_contract_award(
        self,
        contract_id: str,
        company_id: str,
        requirement_id: str,
        design_id: str,
        unit_price_usd: float,
        quantity: int,
        dev_payment_usd: float,
    ) -> None:
        c = self.companies[company_id]
        c["cash_usd"] = float(c["cash_usd"]) + float(dev_payment_usd)
        c["contracts_won_total"] = int(c.get("contracts_won_total", 0)) + 1
        self.contracts[contract_id] = {
            "contract_id": contract_id,
            "company_id": company_id,
            "requirement_id": requirement_id,
            "design_id": design_id,
            "unit_price_usd": float(unit_price_usd),
            "quantity_total": int(quantity),
            "quantity_delivered": 0,
            "units_per_month": max(4, min(24, int(quantity) // 24)),
            "active": True,
        }

    def on_fiscal_year_start(self, world: Any, fy: int) -> None:
        pass

    def on_month_start(self, world: Any, schedule: TickSchedule) -> None:
        interest_mult = float(world.difficulty_preset.get("loan_interest_rate_mult", 1.0))
        monthly_rate = (0.045 * interest_mult) / 12.0

        for cid in sorted(self.companies.keys()):
            c = self.companies[cid]
            eng_total = sum(int(v) for v in c["engineers"].values())
            payroll_usd = eng_total * 620.0
            overhead_usd = float(c["facilities"]["factory_floor_m2"]) * 0.85
            interest_usd = float(c["debt_usd"]) * monthly_rate

            revenue_usd = 0.0
            mfg_cost_usd = 0.0
            active_for_company = 0
            for k in sorted(self.contracts.keys()):
                ct = self.contracts[k]
                if ct["company_id"] != cid or not ct.get("active", False):
                    continue
                active_for_company += 1
                rem = int(ct["quantity_total"]) - int(ct["quantity_delivered"])
                deliver = min(rem, int(ct.get("units_per_month", 8)))
                if deliver > 0:
                    ct["quantity_delivered"] = int(ct["quantity_delivered"]) + deliver
                    c["aircraft_delivered_total"] = int(c.get("aircraft_delivered_total", 0)) + deliver
                    unit_p = float(ct["unit_price_usd"])
                    revenue_usd += deliver * unit_p
                    mfg_cost_usd += deliver * (unit_p * 0.82)
                if ct["quantity_delivered"] >= ct["quantity_total"]:
                    ct["active"] = False

            # Baseline parts/subcontract sustainment revenue so peacetime companies survive if prudent
            sustainment_usd = float(c["facilities"]["factory_floor_m2"]) * 0.70 + eng_total * 280.0
            net_delta = revenue_usd + sustainment_usd - (payroll_usd + overhead_usd + interest_usd + mfg_cost_usd)
            c["cash_usd"] = float(c["cash_usd"]) + net_delta

            if c.get("is_player"):
                if active_for_company == 0:
                    self.idle_months += 1
                else:
                    self.idle_months = 0

    def on_day_tick(self, world: Any, schedule: TickSchedule) -> None:
        p = self.get_player_company()
        if float(p["cash_usd"]) < 0.0:
            self.insolvent_days += 1
            if self.insolvent_days == 1:
                world.emit_notification(
                    category="low_cash_warning",
                    title_key="notif.insolvency_warning.title",
                    body_key="notif.insolvency_warning.body",
                    severity="critical",
                    autopause_trigger="low_cash_warning",
                    payload={"cash_usd": p["cash_usd"]},
                )
        else:
            self.insolvent_days = 0

    def validate_action(self, world: Any, action: PlayerAction) -> ValidationResult:
        cid = action.actor_company_id
        if cid not in self.companies:
            return ValidationResult(False, "ERR_UNKNOWN_COMPANY", f"Unknown company {cid}")
        c = self.companies[cid]

        if action.action_type == "econ.hire_engineers":
            cost = int(action.params["count"]) * 2500.0
            if float(c["cash_usd"]) < cost:
                return ValidationResult(False, "ERR_INSUFFICIENT_FUNDS", "Insufficient cash to hire engineers")
            return ValidationResult(True)

        if action.action_type == "econ.fire_engineers":
            disc = str(action.params["discipline"])
            cnt = int(action.params["count"])
            if int(c["engineers"].get(disc, 0)) < cnt:
                return ValidationResult(False, "ERR_NOT_ENOUGH_ENGINEERS", f"Cannot fire {cnt} in {disc}")
            return ValidationResult(True)

        if action.action_type == "econ.upgrade_wind_tunnel":
            lvl = int(action.params["target_level"])
            cur = int(c["facilities"]["wind_tunnel_level"])
            if lvl <= cur:
                return ValidationResult(False, "ERR_INVALID_LEVEL", f"Tunnel already at level {cur}")
            cost = (lvl - cur) * 850000.0
            if float(c["cash_usd"]) < cost:
                return ValidationResult(False, "ERR_INSUFFICIENT_FUNDS", "Insufficient cash for wind tunnel upgrade")
            return ValidationResult(True)

        if action.action_type == "econ.expand_factory":
            add_m2 = float(action.params["additional_floor_m2"])
            cost = add_m2 * 60.0
            if float(c["cash_usd"]) < cost:
                return ValidationResult(False, "ERR_INSUFFICIENT_FUNDS", "Insufficient cash for factory expansion")
            return ValidationResult(True)

        if action.action_type == "econ.build_test_site":
            if c["facilities"].get("test_site"):
                return ValidationResult(False, "ERR_ALREADY_BUILT", "Test site already built")
            if float(c["cash_usd"]) < 750000.0:
                return ValidationResult(False, "ERR_INSUFFICIENT_FUNDS", "Insufficient cash for test site")
            return ValidationResult(True)

        if action.action_type == "econ.take_loan":
            amt = float(action.params["principal_usd"])
            nw = max(1000000.0, self.compute_net_worth(cid))
            if float(c["debt_usd"]) + amt > nw * 1.5:
                return ValidationResult(False, "ERR_DEBT_LIMIT_EXCEEDED", "Loan exceeds credit capacity")
            return ValidationResult(True)

        if action.action_type == "econ.repay_loan":
            amt = float(action.params["amount_usd"])
            if float(c["debt_usd"]) <= 0.0:
                return ValidationResult(False, "ERR_NO_DEBT", "Company has no outstanding debt")
            if float(c["cash_usd"]) < amt:
                return ValidationResult(False, "ERR_INSUFFICIENT_FUNDS", "Insufficient cash to repay loan")
            return ValidationResult(True)

        if action.action_type == "econ.set_production_rate":
            ct_id = str(action.params["contract_id"])
            ct = self.contracts.get(ct_id)
            if ct is None or ct["company_id"] != cid:
                return ValidationResult(False, "ERR_CONTRACT_NOT_FOUND", f"Contract {ct_id} not found")
            return ValidationResult(True)

        return ValidationResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def apply_action(self, world: Any, action: PlayerAction) -> ActionResult:
        cid = action.actor_company_id
        c = self.companies[cid]

        if action.action_type == "econ.hire_engineers":
            disc = str(action.params["discipline"])
            cnt = int(action.params["count"])
            c["cash_usd"] = float(c["cash_usd"]) - cnt * 2500.0
            c["engineers"][disc] = int(c["engineers"].get(disc, 0)) + cnt
            return ActionResult(True, "OK", "Engineers hired", {"discipline": disc, "total": c["engineers"][disc]})

        if action.action_type == "econ.fire_engineers":
            disc = str(action.params["discipline"])
            cnt = int(action.params["count"])
            c["cash_usd"] = float(c["cash_usd"]) - cnt * 1200.0
            c["engineers"][disc] = int(c["engineers"][disc]) - cnt
            return ActionResult(True, "OK", "Engineers laid off", {"discipline": disc, "total": c["engineers"][disc]})

        if action.action_type == "econ.upgrade_wind_tunnel":
            lvl = int(action.params["target_level"])
            cur = int(c["facilities"]["wind_tunnel_level"])
            cost = (lvl - cur) * 850000.0
            c["cash_usd"] = float(c["cash_usd"]) - cost
            c["facilities"]["wind_tunnel_level"] = lvl
            return ActionResult(True, "OK", "Wind tunnel upgraded", {"wind_tunnel_level": lvl})

        if action.action_type == "econ.expand_factory":
            add_m2 = float(action.params["additional_floor_m2"])
            c["cash_usd"] = float(c["cash_usd"]) - add_m2 * 60.0
            c["facilities"]["factory_floor_m2"] = float(c["facilities"]["factory_floor_m2"]) + add_m2
            return ActionResult(True, "OK", "Factory expanded", {"factory_floor_m2": c["facilities"]["factory_floor_m2"]})

        if action.action_type == "econ.build_test_site":
            c["cash_usd"] = float(c["cash_usd"]) - 750000.0
            c["facilities"]["test_site"] = True
            return ActionResult(True, "OK", "Test site constructed", {"test_site": True})

        if action.action_type == "econ.take_loan":
            amt = float(action.params["principal_usd"])
            c["cash_usd"] = float(c["cash_usd"]) + amt
            c["debt_usd"] = float(c["debt_usd"]) + amt
            return ActionResult(True, "OK", "Loan drawn", {"cash_usd": c["cash_usd"], "debt_usd": c["debt_usd"]})

        if action.action_type == "econ.repay_loan":
            amt = min(float(action.params["amount_usd"]), float(c["debt_usd"]))
            c["cash_usd"] = float(c["cash_usd"]) - amt
            c["debt_usd"] = float(c["debt_usd"]) - amt
            return ActionResult(True, "OK", "Loan repaid", {"cash_usd": c["cash_usd"], "debt_usd": c["debt_usd"]})

        if action.action_type == "econ.set_production_rate":
            ct_id = str(action.params["contract_id"])
            rate = int(action.params["units_per_month"])
            self.contracts[ct_id]["units_per_month"] = rate
            return ActionResult(True, "OK", "Production rate updated", {"contract_id": ct_id, "units_per_month": rate})

        return ActionResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "insolvent_days": self.insolvent_days,
            "idle_months": self.idle_months,
            "starting_net_worth_usd": {
                k: float(self.starting_net_worth_usd[k]) for k in sorted(self.starting_net_worth_usd.keys())
            },
            "companies": {k: dict(self.companies[k]) for k in sorted(self.companies.keys())},
            "contracts": {k: dict(self.contracts[k]) for k in sorted(self.contracts.keys())},
        }

    def load_dict(self, data: Dict[str, Any]) -> None:
        self.insolvent_days = int(data.get("insolvent_days", 0))
        self.idle_months = int(data.get("idle_months", 0))
        self.starting_net_worth_usd = {
            str(k): float(v) for k, v in data.get("starting_net_worth_usd", {}).items()
        }
        self.companies = {str(k): dict(v) for k, v in data.get("companies", {}).items()}
        self.contracts = {str(k): dict(v) for k, v in data.get("contracts", {}).items()}


class StubProcurementModule(SimModule):
    """Stub for Module 05 (`05_procurement`): historical RFPs, proposals, lobbying, and contract awards."""

    module_id: str = "05_procurement"
    schema_version: int = 1

    _HISTORICAL_RFPS: List[Dict[str, Any]] = [
        {
            "id": "rfp_1945_usaf_day_fighter",
            "program_name": "XP-86 Swept-Wing Day Fighter Request",
            "customer": "USAF",
            "issue_date": "1945-03-01",
            "proposal_due": "1945-09-01",
            "target_mach": 0.88,
            "unit_price_ceiling_usd": 280000.0,
            "quantity_planned": 180,
            "dev_usd": 2200000.0,
        },
        {
            "id": "rfp_1946_usn_carrier_jet",
            "program_name": "XF9F Carrier Jet Fighter Specification",
            "customer": "USN",
            "issue_date": "1946-04-01",
            "proposal_due": "1946-10-01",
            "target_mach": 0.84,
            "unit_price_ceiling_usd": 310000.0,
            "quantity_planned": 160,
            "dev_usd": 2400000.0,
        },
        {
            "id": "rfp_1948_usaf_all_weather_int",
            "program_name": "1954 Ultimate Interceptor (F-102 WS-201A)",
            "customer": "USAF",
            "issue_date": "1949-01-15",
            "proposal_due": "1949-08-15",
            "target_mach": 1.25,
            "unit_price_ceiling_usd": 650000.0,
            "quantity_planned": 220,
            "dev_usd": 4500000.0,
        },
        {
            "id": "rfp_1951_usaf_supersonic_superiority",
            "program_name": "Sabre 45 / F-100 Supersonic Day Fighter",
            "customer": "USAF",
            "issue_date": "1951-02-01",
            "proposal_due": "1951-08-01",
            "target_mach": 1.30,
            "unit_price_ceiling_usd": 720000.0,
            "quantity_planned": 280,
            "dev_usd": 5200000.0,
        },
        {
            "id": "rfp_1952_usn_mach15_fleet_fighter",
            "program_name": "XF8U-1 Supersonic Carrier Day Fighter",
            "customer": "USN",
            "issue_date": "1952-09-01",
            "proposal_due": "1953-04-01",
            "target_mach": 1.55,
            "unit_price_ceiling_usd": 880000.0,
            "quantity_planned": 200,
            "dev_usd": 5800000.0,
        },
        {
            "id": "rfp_1954_usn_all_weather_fleet_defense",
            "program_name": "XF4H-1 Twin-Engine Fleet Air Defense Fighter",
            "customer": "USN",
            "issue_date": "1954-10-01",
            "proposal_due": "1955-05-01",
            "target_mach": 2.05,
            "unit_price_ceiling_usd": 1450000.0,
            "quantity_planned": 240,
            "dev_usd": 8500000.0,
        },
        {
            "id": "rfp_1957_usaf_mach2_tactical_strike",
            "program_name": "WS-300A Mach 2 Tactical Fighter-Bomber",
            "customer": "USAF",
            "issue_date": "1957-03-01",
            "proposal_due": "1957-10-01",
            "target_mach": 2.00,
            "unit_price_ceiling_usd": 1650000.0,
            "quantity_planned": 220,
            "dev_usd": 9000000.0,
        },
    ]

    def __init__(self) -> None:
        self.requirements: Dict[str, Dict[str, Any]] = {}
        self.proposals: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.lobby_bonus: Dict[str, Dict[str, float]] = {}
        self._contract_seq: int = 1

    def init_new_game(self, world: Any) -> None:
        self.requirements = {}
        self.proposals = {}
        self.lobby_bonus = {}
        self._contract_seq = 1
        for raw in self._HISTORICAL_RFPS:
            rid = str(raw["id"])
            self.requirements[rid] = {
                "id": rid,
                "program_name": str(raw["program_name"]),
                "customer": str(raw["customer"]),
                "issue_day": iso_to_day(str(raw["issue_date"])),
                "proposal_due_day": iso_to_day(str(raw["proposal_due"])),
                "target_mach": float(raw["target_mach"]),
                "unit_price_ceiling_usd": float(raw["unit_price_ceiling_usd"]),
                "quantity_planned": int(raw["quantity_planned"]),
                "dev_usd": float(raw["dev_usd"]),
                "status": "scheduled",
                "winner_company_id": None,
            }

    def get_open_requirements(self) -> List[Dict[str, Any]]:
        return [
            self.requirements[rid]
            for rid in sorted(self.requirements.keys())
            if self.requirements[rid]["status"] == "open"
        ]

    def on_fiscal_year_start(self, world: Any, fy: int) -> None:
        pass

    def on_month_start(self, world: Any, schedule: TickSchedule) -> None:
        pass

    def on_day_tick(self, world: Any, schedule: TickSchedule) -> None:
        for rid in sorted(self.requirements.keys()):
            req = self.requirements[rid]
            if req["status"] == "scheduled" and schedule.day >= int(req["issue_day"]):
                req["status"] = "open"
                world.emit_notification(
                    category="rfp_issued",
                    title_key="notif.rfp_issued.title",
                    body_key="notif.rfp_issued.body",
                    severity="info",
                    autopause_trigger="rfp_issued",
                    payload={"requirement_id": rid, "program_name": req["program_name"]},
                )
            elif req["status"] == "open" and schedule.day == int(req["proposal_due_day"]) - 7:
                if world.player_company_id not in self.proposals.get(rid, {}):
                    world.emit_notification(
                        category="proposal_due_7d",
                        title_key="notif.proposal_due_7d.title",
                        body_key="notif.proposal_due_7d.body",
                        severity="warning",
                        autopause_trigger="proposal_due_7d",
                        payload={"requirement_id": rid},
                    )
            elif req["status"] == "open" and schedule.day >= int(req["proposal_due_day"]):
                self._evaluate_and_award(world, req)

    def _evaluate_and_award(self, world: Any, req: Dict[str, Any]) -> None:
        rid = str(req["id"])
        bids = self.proposals.get(rid, {})
        if not bids:
            req["status"] = "cancelled"
            return

        rng = world.rng.stream("proc.eval")
        aero = world.modules.get("01_aero_design")
        testing = world.modules.get("06_testing")
        econ = world.modules.get("04_economy")

        best_cid: Optional[str] = None
        best_score = -1e9
        customer = str(req["customer"])
        target_mach = float(req["target_mach"])
        ceiling_usd = float(req["unit_price_ceiling_usd"])

        for cid in sorted(bids.keys()):
            bid = bids[cid]
            did = str(bid["design_id"])
            price = float(bid["bid_unit_price_usd"])
            mach = target_mach
            if aero is not None:
                d = aero.get_design(did)
                if d is not None:
                    mach = float(d["performance"].get("max_mach_alt", target_mach))

            perf_score = (mach / max(0.5, target_mach)) * 50.0
            price_score = max(-30.0, ((ceiling_usd - price) / ceiling_usd) * 30.0)
            test_bonus = testing.get_testing_bonus(did) * 40.0 if testing is not None else 0.0
            rep_bonus = 0.0
            if econ is not None and cid in econ.companies:
                rep_bonus = float(econ.companies[cid]["reputation"].get(customer, 0.5)) * 15.0
            lobby = float(self.lobby_bonus.get(rid, {}).get(cid, 0.0))
            noise = rng.normal(0.0, 2.5)
            total = perf_score + price_score + test_bonus + rep_bonus + lobby + noise
            if total > best_score:
                best_score = total
                best_cid = cid

        req["status"] = "awarded"
        req["winner_company_id"] = best_cid
        if best_cid is not None and econ is not None:
            winning_bid = bids[best_cid]
            ct_id = f"ct_{self._contract_seq:03d}"
            self._contract_seq += 1
            mult = float(world.macro.get_var("procurement_budget_mult", 1.0))
            qty = max(20, int(round(int(req["quantity_planned"]) * mult)))
            econ.register_contract_award(
                contract_id=ct_id,
                company_id=best_cid,
                requirement_id=rid,
                design_id=str(winning_bid["design_id"]),
                unit_price_usd=float(winning_bid["bid_unit_price_usd"]),
                quantity=qty,
                dev_payment_usd=float(req["dev_usd"]),
            )
            world.emit_notification(
                category="contract_awarded",
                title_key="notif.contract_awarded.title",
                body_key="notif.contract_awarded.body",
                severity="major" if best_cid == world.player_company_id else "info",
                autopause_trigger="contract_awarded",
                payload={"requirement_id": rid, "winner_company_id": best_cid, "contract_id": ct_id},
            )

    def validate_action(self, world: Any, action: PlayerAction) -> ValidationResult:
        rid = str(action.params.get("requirement_id", ""))
        req = self.requirements.get(rid)
        if req is None:
            return ValidationResult(False, "ERR_REQUIREMENT_NOT_FOUND", f"Requirement {rid} not found")
        if req["status"] != "open":
            return ValidationResult(False, "ERR_REQUIREMENT_NOT_OPEN", f"Requirement {rid} is {req['status']}")

        if action.action_type == "proc.submit_proposal":
            did = str(action.params["design_id"])
            aero = world.modules.get("01_aero_design")
            if aero is not None:
                d = aero.get_design(did)
                if d is None:
                    return ValidationResult(False, "ERR_DESIGN_NOT_FOUND", f"Design {did} not found")
                if not d.get("frozen", False):
                    return ValidationResult(False, "ERR_DESIGN_NOT_FROZEN", f"Design {did} must be frozen to bid")
            return ValidationResult(True)

        if action.action_type == "proc.withdraw_proposal":
            if action.actor_company_id not in self.proposals.get(rid, {}):
                return ValidationResult(False, "ERR_NO_PROPOSAL", "No submitted proposal to withdraw")
            return ValidationResult(True)

        if action.action_type == "proc.lobby_program":
            econ = world.modules.get("04_economy")
            pts = float(action.params["political_capital_spent"])
            if econ is not None:
                c = econ.companies.get(action.actor_company_id, {})
                if float(c.get("political_capital", 0.0)) < pts:
                    return ValidationResult(False, "ERR_INSUFFICIENT_POLITICAL_CAPITAL", "Not enough political capital")
            return ValidationResult(True)

        return ValidationResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def apply_action(self, world: Any, action: PlayerAction) -> ActionResult:
        rid = str(action.params["requirement_id"])
        cid = action.actor_company_id

        if action.action_type == "proc.submit_proposal":
            self.proposals.setdefault(rid, {})[cid] = {
                "company_id": cid,
                "design_id": str(action.params["design_id"]),
                "bid_unit_price_usd": float(action.params["bid_unit_price_usd"]),
                "submitted_day": world.day,
            }
            return ActionResult(True, "OK", "Proposal submitted", {"requirement_id": rid})

        if action.action_type == "proc.withdraw_proposal":
            self.proposals.get(rid, {}).pop(cid, None)
            return ActionResult(True, "OK", "Proposal withdrawn", {"requirement_id": rid})

        if action.action_type == "proc.lobby_program":
            pts = float(action.params["political_capital_spent"])
            econ = world.modules.get("04_economy")
            if econ is not None and cid in econ.companies:
                econ.companies[cid]["political_capital"] = float(econ.companies[cid]["political_capital"]) - pts
            cur = float(self.lobby_bonus.setdefault(rid, {}).get(cid, 0.0))
            self.lobby_bonus[rid][cid] = cur + pts * 0.35
            return ActionResult(True, "OK", "Lobbying applied", {"requirement_id": rid, "bonus": self.lobby_bonus[rid][cid]})

        return ActionResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_seq": self._contract_seq,
            "requirements": {k: dict(self.requirements[k]) for k in sorted(self.requirements.keys())},
            "proposals": {
                k: {ck: dict(cv) for ck, cv in sorted(self.proposals[k].items())}
                for k in sorted(self.proposals.keys())
            },
            "lobby_bonus": {
                k: {ck: float(cv) for ck, cv in sorted(self.lobby_bonus[k].items())}
                for k in sorted(self.lobby_bonus.keys())
            },
        }

    def load_dict(self, data: Dict[str, Any]) -> None:
        self._contract_seq = int(data.get("contract_seq", 1))
        self.requirements = {str(k): dict(v) for k, v in data.get("requirements", {}).items()}
        self.proposals = {
            str(k): {str(ck): dict(cv) for ck, cv in v.items()}
            for k, v in data.get("proposals", {}).items()
        }
        self.lobby_bonus = {
            str(k): {str(ck): float(cv) for ck, cv in v.items()}
            for k, v in data.get("lobby_bonus", {}).items()
        }


class StubCompetitorAiModule(SimModule):
    """Stub for Module 07 (`07_ai`): deterministic AI competitors submit designs and bids."""

    module_id: str = "07_ai"
    schema_version: int = 1

    def __init__(self) -> None:
        self.ai_bids_placed: List[str] = []

    def init_new_game(self, world: Any) -> None:
        self.ai_bids_placed = []

    def on_fiscal_year_start(self, world: Any, fy: int) -> None:
        pass

    def on_month_start(self, world: Any, schedule: TickSchedule) -> None:
        pass

    def on_day_tick(self, world: Any, schedule: TickSchedule) -> None:
        proc = world.modules.get("05_procurement")
        aero = world.modules.get("01_aero_design")
        if proc is None or aero is None:
            return
        rng = world.rng.stream("ai.bidding")
        ai_mult = float(world.difficulty_preset.get("ai_competence_mult", 1.0))

        for req in proc.get_open_requirements():
            rid = str(req["id"])
            if schedule.day != int(req["issue_day"]) + 14:
                continue
            for cid in sorted(world.company_ids):
                if cid == world.player_company_id:
                    continue
                key = f"{rid}:{cid}"
                if key in self.ai_bids_placed:
                    continue
                if rng.bernoulli(0.55):
                    self.ai_bids_placed.append(key)
                    sweep = 35.0 if schedule.year >= 1945 else 15.0
                    thrust = (22000.0 + (schedule.year - 1945) * 3200.0) * ai_mult
                    res = aero.apply_action(
                        world,
                        PlayerAction(
                            action_type="design.create",
                            actor_company_id=cid,
                            params={
                                "name": f"{cid.upper()}-{rid[-4:]}",
                                "role_tags": ["day_fighter"],
                                "spec": {
                                    "sweep_deg": sweep,
                                    "thrust_N": thrust,
                                    "wing_area_m2": 26.0,
                                    "afterburner": schedule.year >= 1950,
                                },
                            },
                        ),
                    )
                    did = str(res.data["design_id"])
                    aero.apply_action(
                        world,
                        PlayerAction(
                            action_type="design.freeze",
                            actor_company_id=cid,
                            params={"design_id": did},
                        ),
                    )
                    price = float(req["unit_price_ceiling_usd"]) * rng.uniform(0.84, 0.98)
                    proc.apply_action(
                        world,
                        PlayerAction(
                            action_type="proc.submit_proposal",
                            actor_company_id=cid,
                            params={
                                "requirement_id": rid,
                                "design_id": did,
                                "bid_unit_price_usd": round(price, 2),
                            },
                        ),
                    )

    def validate_action(self, world: Any, action: PlayerAction) -> ValidationResult:
        return ValidationResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def apply_action(self, world: Any, action: PlayerAction) -> ActionResult:
        return ActionResult(False, "ERR_UNHANDLED_ACTION", action.action_type)

    def to_dict(self) -> Dict[str, Any]:
        return {"ai_bids_placed": sorted(self.ai_bids_placed)}

    def load_dict(self, data: Dict[str, Any]) -> None:
        self.ai_bids_placed = [str(x) for x in data.get("ai_bids_placed", [])]


def create_default_stub_modules() -> Dict[str, SimModule]:
    """Create the default set of stub domain modules (01..07) keyed by canonical module_id."""
    mods: List[SimModule] = [
        StubAeroDesignModule(),
        StubEngineModule(),
        StubTechModule(),
        StubEconomyModule(),
        StubProcurementModule(),
        StubTestingModule(),
        StubCompetitorAiModule(),
    ]
    return {m.module_id: m for m in mods}
