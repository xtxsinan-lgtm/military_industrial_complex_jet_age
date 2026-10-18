"""Four automated player bot archetypes for full 1945-1960 campaign Monte-Carlo evaluation.

Implements the 4 canonical validation bots:
1. `BalancedPrimeBot`: Balanced R&D, tailors designs to RFP weights, runs wind tunnel +
   Phase 1-3 flight tests, fixes severity >= 3 flaws, bids ~10% margin.
2. `SpeedDemonSkipTestBot` (Reckless Rusher): Pushes extreme speed/sweep, skips wind tunnel &
   runs minimal flight test, never fixes flaws before fly-off, bids aggressive schedule.
3. `ConservativeGoldPlaterBot` (Over-Tester / High-Price): Conservative geometry, runs all
   wind tunnels + all 4 flight test phases, fixes every flaw (severity >= 1), bids +25% margin.
4. `TechPioneerBot` (R&D Maximalist): Heavy ahead-of-time R&D investment (swept wing, area rule,
   titanium, afterburner), bids selectively on high-performance RFPs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from mic.econ.company import CompanyState
from mic.procurement.models import CriterionSpec, ProgramSpec
from mic.tech.catalog import TechCatalog
from mic.tech.research import CompanyTechState
from mic.testing.truth import LineageTestState


def _extract_target_criterion(program: ProgramSpec, key: str, default: float) -> Tuple[float, float, float]:
    """Return (threshold_val, objective_val, weight) for a criterion key on `program`."""
    for c in program.criteria:
        if c.key == key:
            obj = float(c.objective_value) if c.objective_value is not None else float(c.value) * 1.12
            return float(c.value), obj, float(c.weight)
    return default, default * 1.12, 0.0


def _select_era_engine(
    year: float,
    target_mach: float,
    min_engines: int,
    unlocked: Dict[str, float],
    push_experimental: bool = False,
) -> Tuple[str, bool]:
    """Choose best available engine ID and afterburner flag given year and unlocked propulsion tech."""
    has_ab_tech = "prop_1948_afterburner_1" in unlocked
    has_twin_spool = "prop_1952_twin_spool_compressor" in unlocked
    has_var_stator = "prop_1954_variable_stator_compressor" in unlocked
    has_high_flow = "prop_1956_high_massflow_cores" in unlocked

    if (year >= 1955.0 or (push_experimental and has_high_flow)) and target_mach >= 1.6:
        if min_engines == 1 and target_mach >= 1.75:
            return "J75-P-5", True
        return "J79-GE-3A", True

    if year >= 1953.5 or (push_experimental and has_var_stator):
        if target_mach >= 1.3:
            return "J79-GE-3A", True
        return "J57-P-16", target_mach >= 1.0

    if year >= 1950.0 or has_twin_spool:
        if target_mach >= 1.15:
            return "J57-P-21", True
        return "J57-P-7", (target_mach >= 0.95 and has_ab_tech)

    if year >= 1948.0 or has_ab_tech:
        if target_mach >= 0.90 and (has_ab_tech or push_experimental):
            return "J35-A-35", True
        return "J47-GE-27", False

    if year >= 1946.0:
        return "J47-GE-13", False
    return "J35-A-29", False


@dataclass
class CampaignBotArchetype:
    """Base strategy interface for an automated campaign player archetype."""

    bot_id: str
    name: str
    description: str
    rd_priority_queue: List[str] = field(default_factory=list)
    rd_engineer_fraction: float = 0.45
    irad_monthly_budget_1950_usd: float = 45000.0
    max_concurrent_rd_projects: int = 3
    max_ahead_of_time_years: float = 2.0
    price_margin: float = 0.10
    promise_z: float = 0.20
    schedule_offset_days: int = 0

    def decide_rd_allocation(
        self,
        tech_state: CompanyTechState,
        company: CompanyState,
        year: float,
        catalog: TechCatalog,
    ) -> Dict[str, int]:
        """Allocate R&D engineers to eligible tech nodes in `rd_priority_queue` order."""
        total_eng = int(max(18.0, company.total_engineers_fte * self.rd_engineer_fraction))
        max_n = max(1, int(self.max_concurrent_rd_projects))
        eligible: List[str] = []
        for tid in self.rd_priority_queue:
            if tid in catalog.nodes and tech_state.can_start_research(tid, catalog):
                node = catalog.nodes[tid]
                if node.historical_year <= year + self.max_ahead_of_time_years:
                    eligible.append(tid)
                if len(eligible) >= max_n:
                    break

        if not eligible:
            return {}
        active = eligible[:max_n]
        per_proj = max(10, min(42, total_eng // len(active)))
        return {tid: per_proj for tid in active}

    def should_bid_on_program(
        self,
        program: ProgramSpec,
        tech_state: CompanyTechState,
        company: CompanyState,
        year: float,
    ) -> bool:
        """Return True if the bot decides to enter a proposal for `program`."""
        return not company.is_bankrupt_or_acquired

    def design_aircraft_for_rfp(
        self,
        program: ProgramSpec,
        tech_state: CompanyTechState,
        company: CompanyState,
        year: float,
    ) -> Dict[str, Any]:
        """Synthesize a complete `AircraftDesign` dictionary for `program`."""
        raise NotImplementedError

    def select_wind_tunnel_campaigns(
        self,
        program: ProgramSpec,
        design: Dict[str, Any],
        tech_state: CompanyTechState,
        company: CompanyState,
    ) -> List[Tuple[str, str, str]]:
        """Return list of `(campaign_id, provider_id, depth)` wind-tunnel/ground campaigns."""
        return []

    def select_flight_test_plan(
        self,
        program: ProgramSpec,
        design: Dict[str, Any],
        tech_state: CompanyTechState,
    ) -> Tuple[Dict[str, str], str]:
        """Return `(syllabus_plan, flaw_resolution_policy)` for prototype flight testing."""
        return {"low_speed": "standard", "speed_envelope": "standard"}, "fix_severe_else_placard"

    def formulate_bid_parameters(
        self,
        program: ProgramSpec,
        state: LineageTestState,
        company: CompanyState,
    ) -> Dict[str, float]:
        """Return pricing margin, promise aggressiveness, and schedule offset."""
        return {
            "price_margin": self.price_margin,
            "promise_z": self.promise_z,
            "schedule_offset_days": float(self.schedule_offset_days),
        }

    def get_test_pilots(self) -> List[Any]:
        """Return test pilot roster tailored to the bot's testing philosophy."""
        from mic.testing.pilots import get_starter_pilots

        return get_starter_pilots()


def _build_base_rfp_design(
    program: ProgramSpec,
    tech_state: CompanyTechState,
    company_id: str,
    year: float,
    *,
    speed_push: float = 0.0,
    conservative_margin: float = 0.0,
    push_experimental_engine: bool = False,
) -> Dict[str, Any]:
    """Construct a valid `AircraftDesign` dict tailored to `program` criteria and equipment gates."""
    ctx = tech_state.context()
    unlocked = tech_state.unlocked_maturity
    eq = program.equipment

    mach_th, mach_obj, mach_w = _extract_target_criterion(program, "max_mach_alt", 0.88)
    rad_th, rad_obj, rad_w = _extract_target_criterion(program, "combat_radius_m", 650000.0)
    stall_th, stall_obj, _ = _extract_target_criterion(program, "stall_speed_mps", 52.0)
    pay_th, pay_obj, _ = _extract_target_criterion(program, "payload_kg", 400.0)
    maint_th, _, _ = _extract_target_criterion(program, "maint_mh_per_fh", 99.0)

    target_mach = mach_th + (0.65 + 0.35 * speed_push - 0.25 * conservative_margin) * (mach_obj - mach_th)
    max_sweep_cap = float(ctx.get("aero.wing_sweep_max_deg"))
    min_tc_cap = float(ctx.get("aero.thin_wing_tc_min"))

    if target_mach >= 1.65:
        des_sweep = 48.0 + 7.0 * speed_push - 5.0 * conservative_margin
        des_tc = 0.048 - 0.008 * speed_push + 0.010 * conservative_margin
        des_ar = 2.9 - 0.3 * speed_push + 0.4 * conservative_margin
    elif target_mach >= 1.15:
        des_sweep = 40.0 + 5.0 * speed_push - 4.0 * conservative_margin
        des_tc = 0.065 - 0.008 * speed_push + 0.010 * conservative_margin
        des_ar = 3.6 - 0.3 * speed_push + 0.3 * conservative_margin
    elif target_mach >= 0.86:
        des_sweep = 34.0 + 4.0 * speed_push - 4.0 * conservative_margin
        des_tc = 0.090 - 0.006 * speed_push + 0.008 * conservative_margin
        des_ar = 4.4 + 0.3 * conservative_margin
    else:
        des_sweep = 12.0 + 8.0 * speed_push
        des_tc = 0.11
        des_ar = 5.4

    sweep_deg = min(max_sweep_cap, max(5.0, des_sweep))
    tc_root = max(min_tc_cap, min(0.13, des_tc))
    tc_tip = max(min_tc_cap, tc_root - 0.008)

    min_eng = max(1, int(eq.min_engines))
    if rad_th >= 1250000.0 and year >= 1950.0:
        min_eng = max(min_eng, 2)
    engine_id, use_ab = _select_era_engine(year, target_mach, min_eng, unlocked, push_experimental_engine)
    if maint_th <= 19.0 and min_eng >= 2:
        engine_id, use_ab = "J47-GE-27", True
    elif speed_push > 0.25 and target_mach >= 0.90:
        use_ab = True

    # Fuel sizing to meet combat_radius_m threshold + objective margin
    fuel_target_Factor = 1.0 + 0.08 * conservative_margin - 0.06 * speed_push
    fuel_kg = (2400.0 + max(0.0, (rad_th - 450000.0) * 0.0038) + (1100.0 if min_eng >= 2 else 0.0)) * fuel_target_Factor
    drop_tanks = 2 if rad_th >= 500000.0 else 0
    drop_tank_each = 950.0 if rad_th >= 900000.0 else 650.0

    # Wing area sized for carrier / stall limits vs high-speed low wave drag
    if eq.carrier_capable or stall_th <= 53.0:
        wing_area = 43.0 + (fuel_kg - 2400.0) * 0.0045 + 3.0 * conservative_margin - 2.5 * speed_push
        if stall_th <= 46.0:
            wing_area = max(wing_area, 48.0)
    elif min_eng >= 2 or rad_th >= 1100000.0:
        wing_area = 38.0 + 2.0 * conservative_margin - 2.0 * speed_push
    else:
        wing_area = 27.0 + 2.0 * conservative_margin - 2.0 * speed_push

    devices = ["fowler_flaps"]
    if speed_push < 0.65:
        if bool(ctx.get("aero.le_slats")) and (eq.carrier_capable or sweep_deg >= 25.0):
            devices.append("le_slats")
        if bool(ctx.get("aero.le_flaps")) and (target_mach >= 1.05 or eq.carrier_capable):
            devices.append("le_flaps")
        if sweep_deg >= 28.0:
            devices.append("wing_fences")
    if bool(ctx.get("aero.blown_flaps")) and eq.carrier_capable and speed_push < 0.65:
        devices.append("blown_flaps")

    area_ruled = bool(ctx.get("aero.area_rule")) and target_mach >= 0.95 and speed_push < 0.75
    all_moving = bool(ctx.get("aero.all_moving_tail")) and target_mach >= 0.88
    stab_aug = bool(ctx.get("systems.stability_augmentation")) and (target_mach >= 0.95 or conservative_margin > 0.0)
    if speed_push >= 0.65:
        stab_aug = False  # Reckless rusher skips SAS to rush prototype

    ti_cap = float(ctx.get("struct.material.ti_max_fraction")) if bool(ctx.get("struct.material.titanium_available")) else 0.0
    ti_frac = min(ti_cap, 0.18 if target_mach >= 1.5 else (0.08 if target_mach >= 1.1 else 0.0))
    steel_frac = 0.22 if target_mach >= 2.2 else 0.12
    al_frac = max(0.50, 1.0 - ti_frac - steel_frac)

    guns_n = max(int(eq.min_guns_20mm), 4 if not eq.missile_capability else 0)
    guns = [{"caliber_mm": 20, "count": guns_n, "rounds_each": 200}] if guns_n > 0 else []
    ext_stores_kg = max(0.0, pay_obj - 120.0) if pay_th >= 900.0 else 0.0

    techs_used: List[str] = []
    if sweep_deg >= 30.0 and "aero_1945_swept_wing_theory" in unlocked:
        techs_used.append("aero_1945_swept_wing_theory")
    if sweep_deg >= 40.0 and "aero_1950_high_sweep_45deg" in unlocked:
        techs_used.append("aero_1950_high_sweep_45deg")
    if area_ruled and "aero_1952_whitcomb_area_rule" in unlocked:
        techs_used.append("aero_1952_whitcomb_area_rule")
    if use_ab and "prop_1948_afterburner_1" in unlocked:
        techs_used.append("prop_1948_afterburner_1")
    if ti_frac > 0.01 and "struct_1951_titanium_metallurgy_1" in unlocked:
        techs_used.append("struct_1951_titanium_metallurgy_1")

    return {
        "id": f"des__{program.id}__{company_id}",
        "name": f"{company_id.upper()}-{program.id[-4:].upper()}",
        "company_id": company_id,
        "role_tags": [program.role] + (["carrier"] if eq.carrier_capable else []),
        "crew_count": max(1, int(eq.min_crew)),
        "fuselage": {
            "length_m": 14.5 if (min_eng >= 2 or fuel_kg >= 3600.0) else 12.2,
            "max_diameter_m": 1.68 if (min_eng >= 2 or fuel_kg >= 3600.0) else 1.44,
            "nose_fineness": 2.8 if target_mach >= 1.2 else 2.3,
            "tail_fineness": 3.0,
            "canopy_type": "bubble",
            "area_ruled": area_ruled,
        },
        "wing": {
            "area_m2": round(wing_area, 2),
            "aspect_ratio": round(des_ar, 2),
            "taper_ratio": 0.32 if target_mach >= 1.2 else 0.45,
            "sweep_qc_deg": round(sweep_deg, 1),
            "tc_root": round(tc_root, 3),
            "tc_tip": round(tc_tip, 3),
            "devices": devices,
        },
        "empennage": {
            "tailless": False,
            "t_tail": bool(speed_push >= 0.70 and target_mach >= 0.88),
            "all_moving_tail": all_moving,
            "ht_volume_coeff": 0.42 + 0.04 * conservative_margin,
            "vt_volume_coeff": 0.072 + 0.010 * conservative_margin,
        },
        "propulsion": {
            "engine_id": engine_id,
            "count": min_eng,
            "afterburner": use_ab,
        },
        "intake": {
            "type": "side" if eq.radar_required else "nose",
            "spike": bool(ctx.get("aero.inlet_spike")) and target_mach >= 1.4,
            "variable": bool(ctx.get("aero.inlet_variable")) and target_mach >= 1.75 and maint_th > 20.0,
        },
        "structure": {
            "design_load_factor_g": 7.33 + 0.67 * conservative_margin,
            "material_mix": {"al": al_frac, "steel": steel_frac, "ti": ti_frac},
            "carrier_capable": bool(eq.carrier_capable),
        },
        "fuel": {
            "internal_kg": round(fuel_kg, 1),
            "drop_tanks_count": drop_tanks,
            "drop_tank_fuel_kg_each": drop_tank_each,
            "combat_uses_drop_tanks": drop_tanks > 0,
        },
        "systems": {
            "radar_id": "apg30" if eq.radar_required else None,
            "avionics_level": 1 if maint_th <= 20.0 else (2 if eq.radar_required else 1),
            "powered_controls": True,
            "stability_augmentation": stab_aug,
            "ejection_seat": bool(speed_push < 0.75 or year >= 1950.0),
            "pressurized_cockpit": True,
        },
        "armament": {
            "guns": guns,
            "hardpoints": 4 if pay_th >= 900.0 else 2,
            "internal_bay": bool(eq.internal_bay_required),
            "missile_ids": list(eq.missile_capability),
            "combat_external_stores_kg": round(ext_stores_kg, 1),
        },
        "techs_used": techs_used,
    }


class BalancedPrimeBot(CampaignBotArchetype):
    """Archetype 1: Balanced R&D, tailors designs to RFP weights, wind tunnel + Phases 1-3 flight test."""

    def __init__(self) -> None:
        super().__init__(
            bot_id="balanced_prime",
            name="BalancedPrimeBot",
            description="Balanced R&D, tailors designs to RFP weights, wind tunnel + Phase 1-3 flight tests, fixes severity >= 3 flaws, bids ~10% margin.",
            rd_priority_queue=[
                "aero_1945_swept_wing_theory",
                "sys_1946_hydraulic_boost_controls",
                "struct_1946_thick_skin_box_spar",
                "aero_1946_auto_le_slats",
                "aero_1947_thin_airfoils_10pct",
                "prop_1947_nimonic_superalloys_1",
                "prop_1948_afterburner_1",
                "aero_1948_all_moving_tail",
                "sys_1949_stability_augmentation_sas",
                "test_1946_wallops_rocket_models",
                "test_1950_slotted_transonic_tunnel",
                "aero_1950_high_sweep_45deg",
                "struct_1951_titanium_metallurgy_1",
                "aero_1952_whitcomb_area_rule",
                "prop_1949_multi_stage_axial_refinement",
                "prop_1950_component_altitude_test_cells",
                "prop_1952_twin_spool_compressor",
                "aero_1953_supersonic_spike_inlet",
                "aero_1954_vortex_generators_excrescence",
            ],
            rd_engineer_fraction=0.48,
            irad_monthly_budget_1950_usd=42000.0,
            price_margin=0.08,
            promise_z=0.18,
            schedule_offset_days=-15,
        )

    def design_aircraft_for_rfp(
        self,
        program: ProgramSpec,
        tech_state: CompanyTechState,
        company: CompanyState,
        year: float,
    ) -> Dict[str, Any]:
        return _build_base_rfp_design(
            program, tech_state, company.id, year, speed_push=0.18, conservative_margin=0.12
        )

    def select_wind_tunnel_campaigns(
        self,
        program: ProgramSpec,
        design: Dict[str, Any],
        tech_state: CompanyTechState,
        company: CompanyState,
    ) -> List[Tuple[str, str, str]]:
        wt_lvl = int(company.facilities.get("wind_tunnel_level", 1))
        low_prov = "own" if wt_lvl >= 1 else "naca"
        ctx = tech_state.context()
        camps: List[Tuple[str, str, str]] = [
            ("low_speed_tunnel", low_prov, "standard"),
            ("static_structural", "own", "standard"),
        ]
        if bool(ctx.get("testing.transonic_tunnel")):
            camps.append(("transonic_slotted", "naca", "standard"))
        else:
            camps.append(("transonic_bump", "naca", "standard"))
        return camps

    def select_flight_test_plan(
        self,
        program: ProgramSpec,
        design: Dict[str, Any],
        tech_state: CompanyTechState,
    ) -> Tuple[Dict[str, str], str]:
        return (
            {
                "low_speed": "standard",
                "speed_envelope": "standard",
                "altitude_envelope": "standard",
                "maneuver": "standard",
            },
            "fix_severe_else_placard",
        )


class SpeedDemonSkipTestBot(CampaignBotArchetype):
    """Archetype 2: Reckless Rusher — extreme speed/sweep, skips wind tunnel, minimal flight test, never fixes flaws."""

    def __init__(self) -> None:
        super().__init__(
            bot_id="speed_demon_skip_test",
            name="SpeedDemonSkipTestBot",
            description="Pushes extreme speed/sweep, skips wind tunnel & runs minimal flight test, never fixes flaws before fly-off, bids aggressive schedule.",
            rd_priority_queue=[
                "aero_1945_swept_wing_theory",
                "prop_1947_nimonic_superalloys_1",
                "prop_1948_afterburner_1",
                "struct_1946_thick_skin_box_spar",
                "aero_1947_thin_airfoils_10pct",
                "aero_1948_tailless_delta_basics",
                "aero_1950_high_sweep_45deg",
                "prop_1949_multi_stage_axial_refinement",
                "prop_1950_component_altitude_test_cells",
                "prop_1952_twin_spool_compressor",
                "aero_1949_subsonic_duct_splitters",
                "aero_1953_supersonic_spike_inlet",
            ],
            rd_engineer_fraction=0.16,
            irad_monthly_budget_1950_usd=22000.0,
            max_concurrent_rd_projects=1,
            max_ahead_of_time_years=0.5,
            price_margin=0.04,
            promise_z=1.15,
            schedule_offset_days=-75,
        )

    def design_aircraft_for_rfp(
        self,
        program: ProgramSpec,
        tech_state: CompanyTechState,
        company: CompanyState,
        year: float,
    ) -> Dict[str, Any]:
        return _build_base_rfp_design(
            program,
            tech_state,
            company.id,
            year,
            speed_push=0.88,
            conservative_margin=-0.25,
            push_experimental_engine=True,
        )

    def select_wind_tunnel_campaigns(
        self,
        program: ProgramSpec,
        design: Dict[str, Any],
        tech_state: CompanyTechState,
        company: CompanyState,
    ) -> List[Tuple[str, str, str]]:
        return []

    def select_flight_test_plan(
        self,
        program: ProgramSpec,
        design: Dict[str, Any],
        tech_state: CompanyTechState,
    ) -> Tuple[Dict[str, str], str]:
        return (
            {
                "low_speed": "light",
                "speed_envelope": "thorough",
                "altitude_envelope": "standard",
                "maneuver": "standard",
                "high_aoa_spin": "light",
            },
            "ignore",
        )

    def get_test_pilots(self) -> List[Any]:
        from mic.testing.pilots import TestPilot

        return [
            TestPilot(
                id="pilot_rusher_1",
                name="Capt. 'Hotrod' Vance",
                age=25,
                hired_year=1945,
                skill=54.0,
                experience=20.0,
                traits=["daring"],
                salary_annual_usd=13000.0,
            ),
            TestPilot(
                id="pilot_rusher_2",
                name="Lt. 'Cowboy' Riker",
                age=24,
                hired_year=1945,
                skill=52.0,
                experience=18.0,
                traits=["daring"],
                salary_annual_usd=12000.0,
            ),
        ]


class ConservativeGoldPlaterBot(CampaignBotArchetype):
    """Archetype 3: Over-Tester / High-Price — conservative geometry, all tunnels + 4 flight phases, fixes all flaws, +25% margin."""

    def __init__(self) -> None:
        super().__init__(
            bot_id="conservative_gold_plater",
            name="ConservativeGoldPlaterBot",
            description="Conservative geometry, runs all wind tunnels + all 4 flight test phases, fixes every flaw (severity >= 1), bids +25% price margin.",
            rd_priority_queue=[
                "struct_1946_thick_skin_box_spar",
                "sys_1946_hydraulic_boost_controls",
                "sys_1946_ejection_seat",
                "aero_1945_swept_wing_theory",
                "aero_1946_auto_le_slats",
                "struct_1948_jet_carrier_suitability",
                "sys_1949_stability_augmentation_sas",
                "aero_1948_all_moving_tail",
                "mfg_1947_flush_riveting_aerodynamic_smoothing",
                "mfg_1949_optical_tooling_jigs",
                "test_1946_wallops_rocket_models",
                "test_1948_fm_telemetry_oscillographs",
                "test_1950_slotted_transonic_tunnel",
                "test_1952_flutter_aeroelastic_analog",
            ],
            rd_engineer_fraction=0.30,
            irad_monthly_budget_1950_usd=36000.0,
            max_concurrent_rd_projects=2,
            max_ahead_of_time_years=0.8,
            price_margin=0.25,
            promise_z=-0.10,
            schedule_offset_days=30,
        )

    def design_aircraft_for_rfp(
        self,
        program: ProgramSpec,
        tech_state: CompanyTechState,
        company: CompanyState,
        year: float,
    ) -> Dict[str, Any]:
        return _build_base_rfp_design(
            program, tech_state, company.id, year, speed_push=-0.12, conservative_margin=0.65
        )

    def select_wind_tunnel_campaigns(
        self,
        program: ProgramSpec,
        design: Dict[str, Any],
        tech_state: CompanyTechState,
        company: CompanyState,
    ) -> List[Tuple[str, str, str]]:
        wt_lvl = int(company.facilities.get("wind_tunnel_level", 1))
        low_prov = "own" if wt_lvl >= 1 else "naca"
        ctx = tech_state.context()
        trans_camp = "transonic_slotted" if bool(ctx.get("testing.transonic_tunnel")) else "transonic_bump"
        return [
            ("low_speed_tunnel", low_prov, "comprehensive"),
            (trans_camp, "naca", "comprehensive"),
            ("supersonic_tunnel", "naca", "comprehensive"),
            ("spin_tunnel", "naca", "comprehensive"),
            ("flutter_model", "naca", "comprehensive"),
            ("engine_altitude_cell", "naca", "comprehensive"),
            ("static_structural", "own", "comprehensive"),
        ]

    def select_flight_test_plan(
        self,
        program: ProgramSpec,
        design: Dict[str, Any],
        tech_state: CompanyTechState,
    ) -> Tuple[Dict[str, str], str]:
        return (
            {
                "low_speed": "standard",
                "speed_envelope": "standard",
                "altitude_envelope": "standard",
                "maneuver": "standard",
                "high_aoa_spin": "standard",
                "weapons_stores": "standard",
            },
            "fix_all",
        )

    def get_test_pilots(self) -> List[Any]:
        from mic.testing.pilots import TestPilot

        return [
            TestPilot(
                id="pilot_gold_1",
                name="Col. Arthur 'Method' Sterling",
                age=38,
                hired_year=1945,
                skill=92.0,
                experience=85.0,
                traits=["engineer_pilot", "cautious", "carrier_qualified"],
                salary_annual_usd=24000.0,
            ),
            TestPilot(
                id="pilot_gold_2",
                name="Cdr. Walter 'Textbook' Hayes",
                age=36,
                hired_year=1945,
                skill=89.0,
                experience=80.0,
                traits=["engineer_pilot", "cautious", "carrier_qualified"],
                salary_annual_usd=22000.0,
            ),
        ]


class TechPioneerBot(CampaignBotArchetype):
    """Archetype 4: R&D Maximalist — heavy ahead-of-time R&D investment, bids selectively on high-performance RFPs."""

    def __init__(self) -> None:
        super().__init__(
            bot_id="tech_pioneer",
            name="TechPioneerBot",
            description="Heavy ahead-of-time R&D investment (swept wing, area rule, titanium, afterburner), bids selectively on high-performance RFPs.",
            rd_priority_queue=[
                "aero_1945_swept_wing_theory",
                "struct_1946_thick_skin_box_spar",
                "aero_1947_thin_airfoils_10pct",
                "prop_1947_nimonic_superalloys_1",
                "prop_1948_afterburner_1",
                "sys_1946_hydraulic_boost_controls",
                "aero_1948_all_moving_tail",
                "test_1946_wallops_rocket_models",
                "test_1950_slotted_transonic_tunnel",
                "aero_1950_high_sweep_45deg",
                "struct_1951_titanium_metallurgy_1",
                "aero_1952_whitcomb_area_rule",
                "prop_1949_multi_stage_axial_refinement",
                "prop_1950_component_altitude_test_cells",
                "prop_1952_twin_spool_compressor",
                "mfg_1947_flush_riveting_aerodynamic_smoothing",
                "mfg_1949_optical_tooling_jigs",
                "mfg_1950_heavy_forging_presses",
                "struct_1952_integrally_stiffened_skins",
                "aero_1953_razor_thin_wing_3pct",
                "aero_1949_subsonic_duct_splitters",
                "aero_1953_supersonic_spike_inlet",
                "aero_1955_variable_geometry_inlet",
                "aero_1954_vortex_generators_excrescence",
                "aero_1956_supersonic_area_rule",
                "mfg_1954_titanium_forming_chem_mill",
                "struct_1956_ti_6al_4v_structural",
                "prop_1954_waspaloy_vacuum_superalloys",
                "prop_1954_variable_stator_compressor",
                "prop_1956_high_massflow_cores",
            ],
            rd_engineer_fraction=0.72,
            irad_monthly_budget_1950_usd=78000.0,
            max_concurrent_rd_projects=5,
            max_ahead_of_time_years=5.0,
            price_margin=0.11,
            promise_z=0.28,
            schedule_offset_days=-15,
        )

    def decide_rd_allocation(
        self,
        tech_state: CompanyTechState,
        company: CompanyState,
        year: float,
        catalog: TechCatalog,
    ) -> Dict[str, int]:
        """Aggressively push up to 5 concurrent R&D projects up to 5.0 years ahead of historical year."""
        total_eng = int(max(95.0, company.total_engineers_fte * self.rd_engineer_fraction))
        eligible: List[str] = []
        for tid in self.rd_priority_queue:
            if tid in catalog.nodes and tech_state.can_start_research(tid, catalog):
                eligible.append(tid)
        if not eligible:
            return {}
        active = eligible[:5]
        per_proj = max(18, min(48, total_eng // len(active)))
        return {tid: per_proj for tid in active}

    def should_bid_on_program(
        self,
        program: ProgramSpec,
        tech_state: CompanyTechState,
        company: CompanyState,
        year: float,
    ) -> bool:
        """Selectively bid on high-performance / flagship RFPs (skipping low-margin subsonic/light utility RFPs)."""
        if company.is_bankrupt_or_acquired:
            return False
        mach_th, mach_obj, _ = _extract_target_criterion(program, "max_mach_alt", 0.85)
        # Skip low-Mach subsonic night fighter & lightweight low-cost fighter if not desperate
        if program.id in ("usn_night_1945", "usn_f11f_1953", "usaf_gor127_n156_1956"):
            return False
        if year >= 1949.0 and mach_obj < 0.96:
            return False
        return True

    def design_aircraft_for_rfp(
        self,
        program: ProgramSpec,
        tech_state: CompanyTechState,
        company: CompanyState,
        year: float,
    ) -> Dict[str, Any]:
        return _build_base_rfp_design(
            program,
            tech_state,
            company.id,
            year,
            speed_push=0.45,
            conservative_margin=0.15,
            push_experimental_engine=True,
        )

    def select_wind_tunnel_campaigns(
        self,
        program: ProgramSpec,
        design: Dict[str, Any],
        tech_state: CompanyTechState,
        company: CompanyState,
    ) -> List[Tuple[str, str, str]]:
        wt_lvl = int(company.facilities.get("wind_tunnel_level", 1))
        low_prov = "own" if wt_lvl >= 1 else "naca"
        ctx = tech_state.context()
        trans_id = "transonic_slotted" if bool(ctx.get("testing.transonic_tunnel")) else "transonic_bump"
        camps = [
            ("low_speed_tunnel", low_prov, "standard"),
            (trans_id, "naca", "comprehensive"),
            ("flutter_model", "naca", "standard"),
        ]
        if float(design.get("wing", {}).get("sweep_quarter_chord_deg", 0.0)) >= 35.0:
            camps.append(("supersonic_tunnel", "naca", "standard"))
        return camps

    def select_flight_test_plan(
        self,
        program: ProgramSpec,
        design: Dict[str, Any],
        tech_state: CompanyTechState,
    ) -> Tuple[Dict[str, str], str]:
        return (
            {
                "low_speed": "standard",
                "speed_envelope": "thorough",
                "altitude_envelope": "standard",
                "maneuver": "standard",
                "high_aoa_spin": "standard",
            },
            "fix_severe_else_placard",
        )

    def get_test_pilots(self) -> List[Any]:
        from mic.testing.pilots import TestPilot

        return [
            TestPilot(
                id="pilot_tech_1",
                name="Maj. Richard 'Mach' Yeager",
                age=32,
                hired_year=1945,
                skill=90.0,
                experience=82.0,
                traits=["engineer_pilot", "cautious"],
                salary_annual_usd=21000.0,
            ),
            TestPilot(
                id="pilot_tech_2",
                name="Capt. Paul 'Data' Crossfield",
                age=31,
                hired_year=1945,
                skill=86.0,
                experience=76.0,
                traits=["engineer_pilot", "cautious"],
                salary_annual_usd=18500.0,
            ),
        ]



def create_all_bots() -> List[CampaignBotArchetype]:
    """Return instances of all 4 canonical validation bot archetypes."""
    return [
        BalancedPrimeBot(),
        SpeedDemonSkipTestBot(),
        ConservativeGoldPlaterBot(),
        TechPioneerBot(),
    ]


def get_bot_by_id(bot_id: str) -> CampaignBotArchetype:
    """Return a bot archetype instance by `bot_id` or class name."""
    for b in create_all_bots():
        if b.bot_id == bot_id or b.name == bot_id:
            return b
    raise KeyError(f"Unknown bot archetype: {bot_id!r}")
