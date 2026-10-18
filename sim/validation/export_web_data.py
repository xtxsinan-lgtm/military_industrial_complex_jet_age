#!/usr/bin/env python3
"""Exports all game data and Python-oracle reference curves into `web/data_bundle.js`
for the interactive GitHub Pages Web Prototype (`web/index.html`).
"""

import glob
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.mic.perf.performance import evaluate as evaluate_perf


def load_json(rel_path: str):
    with open(ROOT / rel_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_bundle() -> dict:
    # 1. Historical Aircraft + Oracle PerformanceReport
    aircraft_hist = {}
    for p in sorted((ROOT / "sim/data/aircraft_hist").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        aid = d.get("id", p.stem)
        rep = evaluate_perf(d)
        rep_dict = rep.to_dict() if hasattr(rep, "to_dict") else vars(rep)
        # Keep key scalar metrics and compact ps_grid for reference
        oracle_perf = {
            "max_mach_sl": round(float(rep_dict["max_mach_sl"]), 4),
            "max_mach_alt": round(float(rep_dict["max_mach_alt"]), 4),
            "alt_of_max_mach_m": round(float(rep_dict["alt_of_max_mach_m"]), 1),
            "service_ceiling_m": round(float(rep_dict["service_ceiling_m"]), 1),
            "climb_rate_sl_mps": round(float(rep_dict["climb_rate_sl_mps"]), 2),
            "time_to_alt_10668m_s": round(float(rep_dict["time_to_alt_10668m_s"]), 1),
            "sustained_turn_dps_m08_4572m": round(float(rep_dict["sustained_turn_dps_m08_4572m"]), 2),
            "instantaneous_turn_dps_m08_4572m": round(float(rep_dict["instantaneous_turn_dps_m08_4572m"]), 2),
            "ps_mps_m09_4572m_1g": round(float(rep_dict["ps_mps_m09_4572m_1g"]), 2),
            "combat_radius_m": round(float(rep_dict["combat_radius_m"]), 1),
            "ferry_range_m": round(float(rep_dict["ferry_range_m"]), 1),
            "takeoff_distance_m": round(float(rep_dict["takeoff_distance_m"]), 1),
            "landing_distance_m": round(float(rep_dict["landing_distance_m"]), 1),
            "stall_speed_mps": round(float(rep_dict["stall_speed_mps"]), 2),
            "max_load_factor_g": round(float(rep_dict["max_load_factor_g"]), 2),
            "empty_mass_kg": round(float(rep_dict["empty_mass_kg"]), 1),
            "mtow_kg": round(float(rep_dict["mtow_kg"]), 1),
            "internal_fuel_kg": round(float(rep_dict["internal_fuel_kg"]), 1),
            "thrust_to_weight_combat": round(float(rep_dict["thrust_to_weight_combat"]), 3),
            "wing_loading_combat_kgm2": round(float(rep_dict["wing_loading_combat_kgm2"]), 1),
            "unit_flyaway_cost_usd": round(float(rep_dict["unit_flyaway_cost_usd"]), 0),
            "dev_cost_usd_estimate": round(float(rep_dict["dev_cost_usd_estimate"]), 0),
            "maint_mh_per_fh": round(float(rep_dict["maint_mh_per_fh"]), 2),
        }
        aircraft_hist[p.stem] = {
            "stem": p.stem,
            "id": aid,
            "design": d,
            "oracle_perf": oracle_perf,
        }

    # 2. Historical Engines
    engines_hist = {}
    for p in sorted((ROOT / "sim/data/engines_hist").glob("*.json")):
        ed = json.loads(p.read_text(encoding="utf-8"))
        eid = ed.get("id", p.stem)
        engines_hist[eid] = ed

    # 3. Historical Procurement Programs (16 RFPs)
    programs = []
    for p in sorted((ROOT / "sim/data/programs").glob("*.json")):
        if p.stem in ("budget_index_1945_1960", "threats_1945_1960"):
            continue
        pd = json.loads(p.read_text(encoding="utf-8"))
        programs.append(pd)
    programs.sort(key=lambda x: x.get("issue_date", "1945-01-01"))

    # 4. Companies, Designers, Engine Makers, Startup Presets
    airframers = load_json("sim/data/companies/airframers_us_1945_1960.json")
    designers = load_json("sim/data/companies/chief_designers_us_1945_1960.json")
    engine_makers = load_json("sim/data/companies/engine_makers_us_1945_1960.json")
    startup_presets = load_json("sim/data/companies/startup_presets.json")

    # 5. Tech Tree & Components
    tech_nodes = load_json("sim/data/tech/tech_nodes_1945_1960.json")
    guns = load_json("sim/data/tech/components_guns.json")
    missiles = load_json("sim/data/tech/components_missiles.json")
    radars = load_json("sim/data/tech/components_radars.json")

    # 6. Testing, Flaws, Pilots
    flaws = load_json("sim/data/testing/flaws.json")
    test_sources = load_json("sim/data/testing/sources.json")
    flight_items = load_json("sim/data/testing/flight_items.json")
    pilot_names = load_json("sim/data/testing/pilot_names.json")

    # 7. Localization Names
    names_co = load_json("sim/data/names/companies_and_people.json")
    names_tech = load_json("sim/data/names/tech_and_components.json")

    return {
        "aircraft_hist": aircraft_hist,
        "engines_hist": engines_hist,
        "programs": programs,
        "airframers": airframers,
        "designers": designers,
        "engine_makers": engine_makers,
        "startup_presets": startup_presets,
        "tech_nodes": tech_nodes,
        "components": {
            "guns": guns,
            "missiles": missiles,
            "radars": radars,
        },
        "testing": {
            "flaws": flaws,
            "sources": test_sources,
            "flight_items": flight_items,
            "pilot_names": pilot_names,
        },
        "names": {
            "companies_and_people": names_co,
            "tech_and_components": names_tech,
        },
    }


def main():
    web_dir = ROOT / "web"
    web_dir.mkdir(parents=True, exist_ok=True)
    bundle = build_bundle()
    out_js = web_dir / "data_bundle.js"
    payload = "window.MIC_DATA = " + json.dumps(bundle, ensure_ascii=False, indent=2) + ";\n"
    out_js.write_text(payload, encoding="utf-8")
    print(f"Exported {out_js} ({len(payload) / 1024:.1f} KB)")
    print(f"  Aircraft: {len(bundle['aircraft_hist'])}, Engines: {len(bundle['engines_hist'])}, Programs: {len(bundle['programs'])}")


if __name__ == "__main__":
    main()
