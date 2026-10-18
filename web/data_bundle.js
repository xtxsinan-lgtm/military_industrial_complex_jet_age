window.MIC_DATA = {
  "aircraft_hist": {
    "f100a_super_sabre": {
      "stem": "f100a_super_sabre",
      "id": "f100a_super_sabre",
      "design": {
        "id": "f100a_super_sabre",
        "name": "North American F-100A Super Sabre",
        "company_id": "north_american",
        "created_date": "1953-05-25",
        "crew_count": 1,
        "role_tags": [
          "day_fighter"
        ],
        "wing": {
          "area_m2": 35.79,
          "aspect_ratio": 3.86,
          "sweep_qc_deg": 45.0,
          "taper_ratio": 0.27,
          "tc_root": 0.07,
          "tc_tip": 0.07,
          "airfoil_ref": "64A007",
          "planform_type": "conventional",
          "position": "low",
          "x_le_root_frac": 0.34,
          "dihedral_deg": 0.0,
          "incidence_deg": 0.5,
          "twist_deg": -1.5,
          "devices": [
            "plain_flaps",
            "le_slats"
          ]
        },
        "fuselage": {
          "length_m": 14.33,
          "max_diameter_m": 1.62,
          "nose_fineness": 2.6,
          "tail_fineness": 3.1,
          "canopy_type": "faired",
          "area_ruled": false
        },
        "empennage": {
          "tailless": false,
          "t_tail": false,
          "all_moving_tail": true,
          "ht_area_m2": 8.95,
          "ht_aspect_ratio": 3.5,
          "ht_sweep_qc_deg": 45.0,
          "vt_area_m2": 4.1,
          "vt_aspect_ratio": 1.45,
          "vt_sweep_qc_deg": 45.0
        },
        "intake": {
          "type": "nose",
          "compression": "pitot",
          "variable": false,
          "spike": false
        },
        "propulsion": {
          "engine_id": "J57-P-7",
          "count": 1,
          "afterburner": true,
          "x_cg_frac": 0.6
        },
        "structure": {
          "design_load_factor_g": 7.33,
          "material_mix": {
            "al": 0.8,
            "steel": 0.14,
            "ti": 0.06
          },
          "carrier_capable": false
        },
        "fuel": {
          "internal_kg": 2310.0,
          "drop_tanks_count": 2,
          "drop_tank_fuel_kg_each": 775.0,
          "combat_uses_drop_tanks": true
        },
        "systems": {
          "radar_id": "apg30",
          "fire_control_id": null,
          "avionics_level": 2,
          "powered_controls": true,
          "stability_augmentation": false,
          "ejection_seat": true,
          "inflight_refuel": false,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [
            {
              "gun_id": "m39_20mm",
              "count": 4,
              "rounds_per_gun": 200
            }
          ],
          "hardpoints": 4,
          "internal_bay": false,
          "missile_ids": []
        },
        "published_performance": {
          "empty_mass_kg": 8695.0,
          "combat_mass_kg": 10450.0,
          "mtow_kg": 13500.0,
          "max_mach_sl": 0.99,
          "max_mach_alt": 1.29,
          "alt_of_max_mach_m": 10668.0,
          "climb_rate_sl_mps": 98.0,
          "service_ceiling_m": 15240.0,
          "combat_radius_m": 880000.0,
          "ferry_range_m": 2400000.0,
          "stall_speed_mps": 63.0,
          "takeoff_distance_m": 1380.0,
          "sources": [
            "USAF Standard Aircraft Characteristics: F-100A Super Sabre (1954)",
            "Knaack, Encyclopedia of US Air Force Aircraft and Missile Systems Vol. 1, pp. 114-120 (1978)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 1.0,
        "max_mach_alt": 1.3774,
        "alt_of_max_mach_m": 12192.0,
        "service_ceiling_m": 16138.6,
        "climb_rate_sl_mps": 86.55,
        "time_to_alt_10668m_s": 179.0,
        "sustained_turn_dps_m08_4572m": 10.71,
        "instantaneous_turn_dps_m08_4572m": 15.83,
        "ps_mps_m09_4572m_1g": 129.04,
        "combat_radius_m": 917100.2,
        "ferry_range_m": 2588194.4,
        "takeoff_distance_m": 1047.3,
        "landing_distance_m": 1641.1,
        "stall_speed_mps": 64.85,
        "max_load_factor_g": 7.33,
        "empty_mass_kg": 8349.5,
        "mtow_kg": 12640.3,
        "internal_fuel_kg": 2310.0,
        "thrust_to_weight_combat": 0.687,
        "wing_loading_combat_kgm2": 273.9,
        "unit_flyaway_cost_usd": 496965.0,
        "dev_cost_usd_estimate": 22290310.0,
        "maint_mh_per_fh": 21.91
      }
    },
    "f101a_voodoo": {
      "stem": "f101a_voodoo",
      "id": "f101a_voodoo",
      "design": {
        "id": "f101a_voodoo",
        "name": "McDonnell F-101A Voodoo",
        "company_id": "mcdonnell",
        "created_date": "1954-09-29",
        "crew_count": 1,
        "role_tags": [
          "day_fighter",
          "fighter_bomber"
        ],
        "wing": {
          "area_m2": 34.19,
          "aspect_ratio": 4.16,
          "sweep_qc_deg": 35.0,
          "taper_ratio": 0.29,
          "tc_root": 0.065,
          "tc_tip": 0.06,
          "airfoil_ref": "65A006",
          "planform_type": "conventional",
          "position": "mid",
          "x_le_root_frac": 0.36,
          "dihedral_deg": 0.0,
          "incidence_deg": 1.0,
          "twist_deg": -1.5,
          "devices": [
            "slotted_flaps"
          ]
        },
        "fuselage": {
          "length_m": 20.55,
          "max_diameter_m": 1.85,
          "nose_fineness": 2.9,
          "tail_fineness": 3.4,
          "canopy_type": "faired",
          "area_ruled": false
        },
        "empennage": {
          "tailless": false,
          "t_tail": true,
          "all_moving_tail": true,
          "ht_area_m2": 5.65,
          "ht_aspect_ratio": 3.8,
          "ht_sweep_qc_deg": 35.0,
          "vt_area_m2": 6.4,
          "vt_aspect_ratio": 1.35,
          "vt_sweep_qc_deg": 40.0
        },
        "intake": {
          "type": "wing_root",
          "compression": "pitot",
          "variable": false,
          "spike": false
        },
        "propulsion": {
          "engine_id": "J57-P-13",
          "count": 2,
          "afterburner": true,
          "x_cg_frac": 0.56
        },
        "structure": {
          "design_load_factor_g": 7.33,
          "material_mix": {
            "al": 0.78,
            "steel": 0.14,
            "ti": 0.08
          },
          "carrier_capable": false
        },
        "fuel": {
          "internal_kg": 6150.0,
          "drop_tanks_count": 2,
          "drop_tank_fuel_kg_each": 1350.0,
          "combat_uses_drop_tanks": false
        },
        "systems": {
          "radar_id": "aps21",
          "fire_control_id": null,
          "avionics_level": 3,
          "powered_controls": true,
          "stability_augmentation": true,
          "ejection_seat": true,
          "inflight_refuel": true,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [
            {
              "gun_id": "m39_20mm",
              "count": 4,
              "rounds_per_gun": 200
            }
          ],
          "hardpoints": 2,
          "internal_bay": false,
          "missile_ids": []
        },
        "published_performance": {
          "empty_mass_kg": 11520.0,
          "combat_mass_kg": 15200.0,
          "mtow_kg": 21500.0,
          "max_mach_sl": 0.99,
          "max_mach_alt": 1.52,
          "alt_of_max_mach_m": 10668.0,
          "climb_rate_sl_mps": 135.0,
          "service_ceiling_m": 16900.0,
          "combat_radius_m": 1050000.0,
          "ferry_range_m": 3800000.0,
          "stall_speed_mps": 69.0,
          "takeoff_distance_m": 1350.0,
          "sources": [
            "USAF Standard Aircraft Characteristics: F-101A Voodoo (1956)",
            "Knaack, Encyclopedia of US Air Force Aircraft and Missile Systems Vol. 1, pp. 136-143 (1978)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 1.0,
        "max_mach_alt": 1.6413,
        "alt_of_max_mach_m": 12192.0,
        "service_ceiling_m": 16503.7,
        "climb_rate_sl_mps": 142.52,
        "time_to_alt_10668m_s": 113.0,
        "sustained_turn_dps_m08_4572m": 10.15,
        "instantaneous_turn_dps_m08_4572m": 12.17,
        "ps_mps_m09_4572m_1g": 184.19,
        "combat_radius_m": 924581.2,
        "ferry_range_m": 3710793.2,
        "takeoff_distance_m": 1610.8,
        "landing_distance_m": 2331.9,
        "stall_speed_mps": 80.7,
        "max_load_factor_g": 7.33,
        "empty_mass_kg": 12237.7,
        "mtow_kg": 21616.2,
        "internal_fuel_kg": 6150.0,
        "thrust_to_weight_combat": 0.849,
        "wing_loading_combat_kgm2": 456.6,
        "unit_flyaway_cost_usd": 967794.0,
        "dev_cost_usd_estimate": 45339464.0,
        "maint_mh_per_fh": 30.16
      }
    },
    "f102a_delta_dagger": {
      "stem": "f102a_delta_dagger",
      "id": "f102a_delta_dagger",
      "design": {
        "id": "f102a_delta_dagger",
        "name": "Convair F-102A Delta Dagger (Area-Ruled)",
        "company_id": "convair",
        "created_date": "1954-12-20",
        "crew_count": 1,
        "role_tags": [
          "interceptor"
        ],
        "wing": {
          "area_m2": 64.57,
          "aspect_ratio": 2.09,
          "sweep_qc_deg": 52.5,
          "taper_ratio": 0.05,
          "tc_root": 0.04,
          "tc_tip": 0.04,
          "airfoil_ref": "0004",
          "planform_type": "delta",
          "position": "mid",
          "x_le_root_frac": 0.3,
          "dihedral_deg": 0.0,
          "incidence_deg": 0.0,
          "twist_deg": 0.0,
          "conical_camber": true,
          "devices": [
            "plain_flaps"
          ]
        },
        "fuselage": {
          "length_m": 20.83,
          "max_diameter_m": 1.72,
          "nose_fineness": 3.2,
          "tail_fineness": 3.4,
          "canopy_type": "faired",
          "area_ruled": true,
          "area_rule_waist_frac": 0.65
        },
        "empennage": {
          "tailless": true,
          "t_tail": false,
          "all_moving_tail": false,
          "ht_area_m2": 0.0,
          "vt_area_m2": 8.8,
          "vt_aspect_ratio": 1.35,
          "vt_sweep_qc_deg": 52.5
        },
        "intake": {
          "type": "cheek",
          "compression": "pitot",
          "variable": false,
          "spike": false
        },
        "propulsion": {
          "engine_id": "J57-P-23",
          "count": 1,
          "afterburner": true,
          "x_cg_frac": 0.64
        },
        "structure": {
          "design_load_factor_g": 7.0,
          "material_mix": {
            "al": 0.82,
            "steel": 0.12,
            "ti": 0.06
          },
          "carrier_capable": false
        },
        "fuel": {
          "internal_kg": 3340.0,
          "drop_tanks_count": 2,
          "drop_tank_fuel_kg_each": 460.0,
          "combat_uses_drop_tanks": true
        },
        "systems": {
          "radar_id": "mg10",
          "fire_control_id": null,
          "avionics_level": 4,
          "powered_controls": true,
          "stability_augmentation": true,
          "ejection_seat": true,
          "inflight_refuel": false,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [],
          "hardpoints": 0,
          "internal_bay": true,
          "missile_ids": [
            "aim4a_falcon",
            "aim4a_falcon",
            "aim4a_falcon",
            "aim4c_falcon",
            "aim4c_falcon",
            "aim4c_falcon"
          ]
        },
        "published_performance": {
          "empty_mass_kg": 8777.0,
          "combat_mass_kg": 11100.0,
          "mtow_kg": 14288.0,
          "max_mach_sl": 0.98,
          "max_mach_alt": 1.25,
          "alt_of_max_mach_m": 10668.0,
          "climb_rate_sl_mps": 88.9,
          "service_ceiling_m": 16276.0,
          "combat_radius_m": 820000.0,
          "ferry_range_m": 2170000.0,
          "stall_speed_mps": 55.0,
          "takeoff_distance_m": 1180.0,
          "sources": [
            "USAF Standard Aircraft Characteristics: F-102A Delta Dagger (1956)",
            "Loftin, Quest for Performance, NASA SP-468, Table V (1985)",
            "Knaack, Encyclopedia of US Air Force Aircraft and Missile Systems Vol. 1, pp. 163-170 (1978)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 1.0,
        "max_mach_alt": 1.3524,
        "alt_of_max_mach_m": 12192.0,
        "service_ceiling_m": 15918.8,
        "climb_rate_sl_mps": 75.54,
        "time_to_alt_10668m_s": 204.4,
        "sustained_turn_dps_m08_4572m": 9.9,
        "instantaneous_turn_dps_m08_4572m": 15.1,
        "ps_mps_m09_4572m_1g": 111.3,
        "combat_radius_m": 892001.6,
        "ferry_range_m": 2565694.7,
        "takeoff_distance_m": 862.7,
        "landing_distance_m": 1344.3,
        "stall_speed_mps": 56.49,
        "max_load_factor_g": 7.0,
        "empty_mass_kg": 8722.5,
        "mtow_kg": 13494.7,
        "internal_fuel_kg": 3340.0,
        "thrust_to_weight_combat": 0.66,
        "wing_loading_combat_kgm2": 167.7,
        "unit_flyaway_cost_usd": 1260880.0,
        "dev_cost_usd_estimate": 56316093.0,
        "maint_mh_per_fh": 24.09
      }
    },
    "f104a_starfighter": {
      "stem": "f104a_starfighter",
      "id": "f104a_starfighter",
      "design": {
        "id": "f104a_starfighter",
        "name": "Lockheed F-104A Starfighter",
        "company_id": "lockheed",
        "created_date": "1956-02-17",
        "crew_count": 1,
        "role_tags": [
          "interceptor",
          "day_fighter"
        ],
        "wing": {
          "area_m2": 18.22,
          "aspect_ratio": 2.45,
          "sweep_qc_deg": 18.1,
          "taper_ratio": 0.38,
          "tc_root": 0.0336,
          "tc_tip": 0.0336,
          "airfoil_ref": "biconvex:0.0336",
          "planform_type": "conventional",
          "position": "mid",
          "x_le_root_frac": 0.44,
          "dihedral_deg": -10.0,
          "incidence_deg": 0.0,
          "twist_deg": 0.0,
          "devices": [
            "plain_flaps",
            "blown_flaps",
            "le_flaps"
          ]
        },
        "fuselage": {
          "length_m": 16.66,
          "max_diameter_m": 1.38,
          "nose_fineness": 3.6,
          "tail_fineness": 3.5,
          "canopy_type": "faired",
          "area_ruled": true,
          "area_rule_waist_frac": 0.5
        },
        "empennage": {
          "tailless": false,
          "t_tail": true,
          "all_moving_tail": true,
          "ht_area_m2": 4.48,
          "ht_aspect_ratio": 2.9,
          "ht_sweep_qc_deg": 18.0,
          "vt_area_m2": 4.05,
          "vt_aspect_ratio": 1.2,
          "vt_sweep_qc_deg": 35.0
        },
        "intake": {
          "type": "cheek",
          "compression": "fixed_spike",
          "variable": false,
          "spike": true
        },
        "propulsion": {
          "engine_id": "J79-GE-3A",
          "count": 1,
          "afterburner": true,
          "x_cg_frac": 0.62
        },
        "structure": {
          "design_load_factor_g": 7.33,
          "material_mix": {
            "al": 0.76,
            "steel": 0.14,
            "ti": 0.1
          },
          "carrier_capable": false
        },
        "fuel": {
          "internal_kg": 2690.0,
          "drop_tanks_count": 2,
          "drop_tank_fuel_kg_each": 510.0,
          "combat_uses_drop_tanks": false
        },
        "systems": {
          "radar_id": "apg30",
          "fire_control_id": null,
          "avionics_level": 3,
          "powered_controls": true,
          "stability_augmentation": true,
          "ejection_seat": true,
          "inflight_refuel": false,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [
            {
              "gun_id": "m61_20mm",
              "count": 1,
              "rounds_per_gun": 725
            }
          ],
          "hardpoints": 2,
          "internal_bay": false,
          "missile_ids": [
            "aim9b_sidewinder",
            "aim9b_sidewinder"
          ]
        },
        "published_performance": {
          "empty_mass_kg": 6070.0,
          "combat_mass_kg": 7850.0,
          "mtow_kg": 10450.0,
          "max_mach_sl": 1.12,
          "max_mach_alt": 2.0,
          "alt_of_max_mach_m": 10668.0,
          "climb_rate_sl_mps": 165.0,
          "service_ceiling_m": 18200.0,
          "combat_radius_m": 620000.0,
          "ferry_range_m": 2250000.0,
          "stall_speed_mps": 66.0,
          "takeoff_distance_m": 1150.0,
          "sources": [
            "USAF Standard Aircraft Characteristics: F-104A Starfighter (1958)",
            "Loftin, Quest for Performance, NASA SP-468, Table V & Ch. 11 (1985)",
            "Knaack, Encyclopedia of US Air Force Aircraft and Missile Systems Vol. 1, pp. 176-183 (1978)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 1.1139,
        "max_mach_alt": 2.1278,
        "alt_of_max_mach_m": 12192.0,
        "service_ceiling_m": 16282.3,
        "climb_rate_sl_mps": 143.16,
        "time_to_alt_10668m_s": 108.7,
        "sustained_turn_dps_m08_4572m": 9.11,
        "instantaneous_turn_dps_m08_4572m": 15.27,
        "ps_mps_m09_4572m_1g": 188.1,
        "combat_radius_m": 547074.7,
        "ferry_range_m": 2399018.6,
        "takeoff_distance_m": 958.4,
        "landing_distance_m": 1396.9,
        "stall_speed_mps": 57.81,
        "max_load_factor_g": 7.33,
        "empty_mass_kg": 5821.8,
        "mtow_kg": 10039.4,
        "internal_fuel_kg": 2690.0,
        "thrust_to_weight_combat": 0.871,
        "wing_loading_combat_kgm2": 416.4,
        "unit_flyaway_cost_usd": 630160.0,
        "dev_cost_usd_estimate": 31839386.0,
        "maint_mh_per_fh": 21.09
      }
    },
    "f105b_thunderchief": {
      "stem": "f105b_thunderchief",
      "id": "f105b_thunderchief",
      "design": {
        "id": "f105b_thunderchief",
        "name": "Republic F-105B Thunderchief",
        "company_id": "republic",
        "created_date": "1956-05-26",
        "crew_count": 1,
        "role_tags": [
          "fighter_bomber"
        ],
        "wing": {
          "area_m2": 35.76,
          "aspect_ratio": 3.16,
          "sweep_qc_deg": 45.0,
          "taper_ratio": 0.47,
          "tc_root": 0.055,
          "tc_tip": 0.04,
          "airfoil_ref": "65A005.5",
          "planform_type": "conventional",
          "position": "mid",
          "x_le_root_frac": 0.38,
          "dihedral_deg": -3.5,
          "incidence_deg": 0.5,
          "twist_deg": -1.0,
          "conical_camber": true,
          "devices": [
            "slotted_flaps",
            "le_flaps"
          ]
        },
        "fuselage": {
          "length_m": 19.2,
          "max_diameter_m": 1.82,
          "nose_fineness": 3.1,
          "tail_fineness": 3.4,
          "canopy_type": "faired",
          "area_ruled": true,
          "area_rule_waist_frac": 0.65
        },
        "empennage": {
          "tailless": false,
          "t_tail": false,
          "all_moving_tail": true,
          "ht_area_m2": 5.5,
          "ht_aspect_ratio": 3.4,
          "ht_sweep_qc_deg": 45.0,
          "vt_area_m2": 5.6,
          "vt_aspect_ratio": 1.4,
          "vt_sweep_qc_deg": 46.0
        },
        "intake": {
          "type": "wing_root",
          "compression": "variable_ramp",
          "variable": true,
          "spike": false
        },
        "propulsion": {
          "engine_id": "J75-P-5",
          "count": 1,
          "afterburner": true,
          "x_cg_frac": 0.62
        },
        "structure": {
          "design_load_factor_g": 8.0,
          "material_mix": {
            "al": 0.78,
            "steel": 0.14,
            "ti": 0.08
          },
          "carrier_capable": false
        },
        "fuel": {
          "internal_kg": 3550.0,
          "drop_tanks_count": 2,
          "drop_tank_fuel_kg_each": 1150.0,
          "combat_uses_drop_tanks": true
        },
        "systems": {
          "radar_id": "ma1",
          "fire_control_id": null,
          "avionics_level": 4,
          "powered_controls": true,
          "stability_augmentation": true,
          "ejection_seat": true,
          "inflight_refuel": true,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [
            {
              "gun_id": "m61_20mm",
              "count": 1,
              "rounds_per_gun": 1028
            }
          ],
          "hardpoints": 5,
          "internal_bay": true,
          "missile_ids": []
        },
        "published_performance": {
          "empty_mass_kg": 11790.0,
          "combat_mass_kg": 14600.0,
          "mtow_kg": 21000.0,
          "max_mach_sl": 1.11,
          "max_mach_alt": 2.02,
          "alt_of_max_mach_m": 10668.0,
          "climb_rate_sl_mps": 160.0,
          "service_ceiling_m": 15850.0,
          "combat_radius_m": 1150000.0,
          "ferry_range_m": 3200000.0,
          "stall_speed_mps": 72.0,
          "takeoff_distance_m": 1420.0,
          "sources": [
            "USAF Standard Aircraft Characteristics: F-105B Thunderchief (1958)",
            "Knaack, Encyclopedia of US Air Force Aircraft and Missile Systems Vol. 1, pp. 191-198 (1978)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 1.1139,
        "max_mach_alt": 2.1395,
        "alt_of_max_mach_m": 12192.0,
        "service_ceiling_m": 16454.6,
        "climb_rate_sl_mps": 117.43,
        "time_to_alt_10668m_s": 127.1,
        "sustained_turn_dps_m08_4572m": 9.99,
        "instantaneous_turn_dps_m08_4572m": 14.05,
        "ps_mps_m09_4572m_1g": 175.83,
        "combat_radius_m": 947225.4,
        "ferry_range_m": 2652557.6,
        "takeoff_distance_m": 1130.2,
        "landing_distance_m": 1829.9,
        "stall_speed_mps": 69.29,
        "max_load_factor_g": 8.0,
        "empty_mass_kg": 10906.9,
        "mtow_kg": 17309.5,
        "internal_fuel_kg": 3550.0,
        "thrust_to_weight_combat": 0.796,
        "wing_loading_combat_kgm2": 364.6,
        "unit_flyaway_cost_usd": 1560005.0,
        "dev_cost_usd_estimate": 78958700.0,
        "maint_mh_per_fh": 29.66
      }
    },
    "f4d1_skyray": {
      "stem": "f4d1_skyray",
      "id": "f4d1_skyray",
      "design": {
        "id": "f4d1_skyray",
        "name": "Douglas F4D-1 Skyray",
        "company_id": "douglas",
        "created_date": "1954-06-05",
        "crew_count": 1,
        "role_tags": [
          "interceptor",
          "carrier"
        ],
        "wing": {
          "area_m2": 51.75,
          "aspect_ratio": 2.0,
          "sweep_qc_deg": 46.0,
          "taper_ratio": 0.14,
          "tc_root": 0.07,
          "tc_tip": 0.055,
          "airfoil_ref": "0006.5",
          "planform_type": "delta",
          "position": "mid",
          "x_le_root_frac": 0.24,
          "dihedral_deg": 0.0,
          "incidence_deg": 0.0,
          "twist_deg": -1.0,
          "devices": [
            "plain_flaps",
            "le_slats"
          ]
        },
        "fuselage": {
          "length_m": 13.8,
          "max_diameter_m": 1.65,
          "nose_fineness": 2.4,
          "tail_fineness": 2.5,
          "canopy_type": "faired",
          "area_ruled": false
        },
        "empennage": {
          "tailless": true,
          "t_tail": false,
          "all_moving_tail": false,
          "ht_area_m2": 0.0,
          "vt_area_m2": 4.9,
          "vt_aspect_ratio": 1.4,
          "vt_sweep_qc_deg": 48.0
        },
        "intake": {
          "type": "wing_root",
          "compression": "pitot",
          "variable": false,
          "spike": false
        },
        "propulsion": {
          "engine_id": "J57-P-8B",
          "count": 1,
          "afterburner": true,
          "x_cg_frac": 0.58
        },
        "structure": {
          "design_load_factor_g": 7.0,
          "material_mix": {
            "al": 0.85,
            "steel": 0.12,
            "ti": 0.03
          },
          "carrier_capable": true
        },
        "fuel": {
          "internal_kg": 1980.0,
          "drop_tanks_count": 2,
          "drop_tank_fuel_kg_each": 900.0,
          "combat_uses_drop_tanks": false
        },
        "systems": {
          "radar_id": "apq50",
          "fire_control_id": null,
          "avionics_level": 3,
          "powered_controls": true,
          "stability_augmentation": true,
          "ejection_seat": true,
          "inflight_refuel": true,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [
            {
              "gun_id": "mk12_20mm",
              "count": 4,
              "rounds_per_gun": 70
            }
          ],
          "hardpoints": 6,
          "internal_bay": false,
          "missile_ids": [
            "aim9b_sidewinder",
            "aim9b_sidewinder"
          ]
        },
        "published_performance": {
          "empty_mass_kg": 7268.0,
          "combat_mass_kg": 8950.0,
          "mtow_kg": 12300.0,
          "max_mach_sl": 0.96,
          "max_mach_alt": 1.15,
          "alt_of_max_mach_m": 10668.0,
          "climb_rate_sl_mps": 93.0,
          "service_ceiling_m": 16764.0,
          "combat_radius_m": 390000.0,
          "ferry_range_m": 1930000.0,
          "stall_speed_mps": 50.0,
          "takeoff_distance_m": 880.0,
          "sources": [
            "US Navy Standard Aircraft Characteristics: F4D-1 Skyray, NAVAER 1335A (1957)",
            "Loftin, Quest for Performance, NASA SP-468, Table V (1985)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 1.0,
        "max_mach_alt": 1.2121,
        "alt_of_max_mach_m": 12192.0,
        "service_ceiling_m": 17073.6,
        "climb_rate_sl_mps": 119.62,
        "time_to_alt_10668m_s": 135.1,
        "sustained_turn_dps_m08_4572m": 12.35,
        "instantaneous_turn_dps_m08_4572m": 15.1,
        "ps_mps_m09_4572m_1g": 149.83,
        "combat_radius_m": 401639.7,
        "ferry_range_m": 2880477.3,
        "takeoff_distance_m": 611.9,
        "landing_distance_m": 1211.3,
        "stall_speed_mps": 52.41,
        "max_load_factor_g": 7.0,
        "empty_mass_kg": 7066.7,
        "mtow_kg": 11305.7,
        "internal_fuel_kg": 1980.0,
        "thrust_to_weight_combat": 0.846,
        "wing_loading_combat_kgm2": 161.6,
        "unit_flyaway_cost_usd": 701765.0,
        "dev_cost_usd_estimate": 30599656.0,
        "maint_mh_per_fh": 21.44
      }
    },
    "f84g_thunderjet": {
      "stem": "f84g_thunderjet",
      "id": "f84g_thunderjet",
      "design": {
        "id": "f84g_thunderjet",
        "name": "Republic F-84G Thunderjet",
        "company_id": "republic",
        "created_date": "1951-06-01",
        "crew_count": 1,
        "role_tags": [
          "fighter_bomber",
          "day_fighter"
        ],
        "wing": {
          "area_m2": 24.15,
          "aspect_ratio": 5.1,
          "sweep_qc_deg": 3.5,
          "taper_ratio": 0.56,
          "tc_root": 0.12,
          "tc_tip": 0.12,
          "airfoil_ref": "0012",
          "planform_type": "conventional",
          "position": "mid",
          "x_le_root_frac": 0.36,
          "dihedral_deg": 5.0,
          "incidence_deg": 1.5,
          "twist_deg": -1.5,
          "devices": [
            "slotted_flaps"
          ]
        },
        "fuselage": {
          "length_m": 11.6,
          "max_diameter_m": 1.42,
          "nose_fineness": 2.5,
          "tail_fineness": 2.9,
          "canopy_type": "bubble",
          "area_ruled": false
        },
        "empennage": {
          "tailless": false,
          "t_tail": false,
          "all_moving_tail": false,
          "ht_area_m2": 4.45,
          "ht_aspect_ratio": 4.1,
          "ht_sweep_qc_deg": 5.0,
          "vt_area_m2": 2.85,
          "vt_aspect_ratio": 1.5,
          "vt_sweep_qc_deg": 15.0
        },
        "intake": {
          "type": "nose",
          "compression": "pitot",
          "variable": false,
          "spike": false
        },
        "propulsion": {
          "engine_id": "J35-A-29",
          "count": 1,
          "afterburner": false,
          "x_cg_frac": 0.58
        },
        "structure": {
          "design_load_factor_g": 7.33,
          "material_mix": {
            "al": 0.88,
            "steel": 0.12,
            "ti": 0.0
          },
          "carrier_capable": false
        },
        "fuel": {
          "internal_kg": 1365.0,
          "drop_tanks_count": 2,
          "drop_tank_fuel_kg_each": 660.0,
          "combat_uses_drop_tanks": true
        },
        "systems": {
          "radar_id": "apg30",
          "fire_control_id": null,
          "avionics_level": 2,
          "powered_controls": true,
          "stability_augmentation": false,
          "ejection_seat": true,
          "inflight_refuel": true,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [
            {
              "gun_id": "m3_50",
              "count": 6,
              "rounds_per_gun": 300
            }
          ],
          "hardpoints": 4,
          "internal_bay": false,
          "missile_ids": []
        },
        "published_performance": {
          "empty_mass_kg": 5203.0,
          "combat_mass_kg": 6450.0,
          "mtow_kg": 8650.0,
          "max_mach_sl": 0.81,
          "max_mach_alt": 0.82,
          "alt_of_max_mach_m": 3048.0,
          "climb_rate_sl_mps": 19.1,
          "service_ceiling_m": 12344.0,
          "combat_radius_m": 1150000.0,
          "ferry_range_m": 2750000.0,
          "stall_speed_mps": 58.0,
          "takeoff_distance_m": 1450.0,
          "sources": [
            "USAF Standard Aircraft Characteristics: F-84G Thunderjet (1952)",
            "Knaack, Encyclopedia of US Air Force Aircraft and Missile Systems Vol. 1, pp. 38-42 (1978)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 0.785,
        "max_mach_alt": 0.7928,
        "alt_of_max_mach_m": 6096.0,
        "service_ceiling_m": 12762.3,
        "climb_rate_sl_mps": 23.21,
        "time_to_alt_10668m_s": 878.2,
        "sustained_turn_dps_m08_4572m": 0.0,
        "instantaneous_turn_dps_m08_4572m": 15.83,
        "ps_mps_m09_4572m_1g": -233.37,
        "combat_radius_m": 871854.4,
        "ferry_range_m": 2278414.6,
        "takeoff_distance_m": 1236.2,
        "landing_distance_m": 1349.8,
        "stall_speed_mps": 56.8,
        "max_load_factor_g": 7.33,
        "empty_mass_kg": 5191.4,
        "mtow_kg": 8296.0,
        "internal_fuel_kg": 1365.0,
        "thrust_to_weight_combat": 0.413,
        "wing_loading_combat_kgm2": 256.0,
        "unit_flyaway_cost_usd": 286008.0,
        "dev_cost_usd_estimate": 12012347.0,
        "maint_mh_per_fh": 18.25
      }
    },
    "f86a_sabre": {
      "stem": "f86a_sabre",
      "id": "f86a_sabre",
      "design": {
        "id": "f86a_sabre",
        "name": "North American F-86A-5 Sabre",
        "company_id": "north_american",
        "created_date": "1949-03-01",
        "crew_count": 1,
        "role_tags": [
          "day_fighter"
        ],
        "wing": {
          "area_m2": 26.75,
          "aspect_ratio": 4.79,
          "sweep_qc_deg": 35.0,
          "taper_ratio": 0.5,
          "tc_root": 0.095,
          "tc_tip": 0.085,
          "airfoil_ref": "0009.5",
          "planform_type": "conventional",
          "position": "low",
          "x_le_root_frac": 0.34,
          "dihedral_deg": 3.0,
          "incidence_deg": 1.0,
          "twist_deg": -2.0,
          "devices": [
            "slotted_flaps",
            "le_slats"
          ]
        },
        "fuselage": {
          "length_m": 11.43,
          "max_diameter_m": 1.45,
          "nose_fineness": 2.4,
          "tail_fineness": 2.8,
          "canopy_type": "bubble",
          "area_ruled": false
        },
        "empennage": {
          "tailless": false,
          "t_tail": false,
          "all_moving_tail": false,
          "ht_area_m2": 3.25,
          "ht_aspect_ratio": 4.6,
          "ht_sweep_qc_deg": 35.0,
          "vt_area_m2": 3.05,
          "vt_aspect_ratio": 1.7,
          "vt_sweep_qc_deg": 35.0
        },
        "intake": {
          "type": "nose",
          "compression": "pitot",
          "variable": false,
          "spike": false
        },
        "propulsion": {
          "engine_id": "J47-GE-13",
          "count": 1,
          "afterburner": false,
          "x_cg_frac": 0.58
        },
        "structure": {
          "design_load_factor_g": 7.33,
          "material_mix": {
            "al": 0.88,
            "steel": 0.12,
            "ti": 0.0
          },
          "carrier_capable": false
        },
        "fuel": {
          "internal_kg": 1315.0,
          "drop_tanks_count": 2,
          "drop_tank_fuel_kg_each": 365.0,
          "combat_uses_drop_tanks": true
        },
        "systems": {
          "radar_id": "apg30",
          "fire_control_id": null,
          "avionics_level": 1,
          "powered_controls": true,
          "stability_augmentation": false,
          "ejection_seat": true,
          "inflight_refuel": false,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [
            {
              "gun_id": "m3_50",
              "count": 6,
              "rounds_per_gun": 300
            }
          ],
          "hardpoints": 2,
          "internal_bay": false,
          "missile_ids": []
        },
        "published_performance": {
          "empty_mass_kg": 4780.0,
          "combat_mass_kg": 5850.0,
          "mtow_kg": 7350.0,
          "max_mach_sl": 0.89,
          "max_mach_alt": 0.9,
          "alt_of_max_mach_m": 6096.0,
          "climb_rate_sl_mps": 38.0,
          "service_ceiling_m": 14630.0,
          "combat_radius_m": 660000.0,
          "ferry_range_m": 1950000.0,
          "stall_speed_mps": 53.5,
          "takeoff_distance_m": 1120.0,
          "sources": [
            "USAF Standard Aircraft Characteristics: F-86A-5 Sabre (1950)",
            "Loftin, Quest for Performance, NASA SP-468, Ch. 11 (1985)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 0.8703,
        "max_mach_alt": 0.9031,
        "alt_of_max_mach_m": 10668.0,
        "service_ceiling_m": 14227.2,
        "climb_rate_sl_mps": 29.45,
        "time_to_alt_10668m_s": 580.8,
        "sustained_turn_dps_m08_4572m": 7.56,
        "instantaneous_turn_dps_m08_4572m": 15.83,
        "ps_mps_m09_4572m_1g": -8.18,
        "combat_radius_m": 694045.6,
        "ferry_range_m": 1949455.0,
        "takeoff_distance_m": 1021.4,
        "landing_distance_m": 1158.7,
        "stall_speed_mps": 51.03,
        "max_load_factor_g": 7.33,
        "empty_mass_kg": 4637.3,
        "mtow_kg": 7051.7,
        "internal_fuel_kg": 1315.0,
        "thrust_to_weight_combat": 0.423,
        "wing_loading_combat_kgm2": 209.4,
        "unit_flyaway_cost_usd": 219523.0,
        "dev_cost_usd_estimate": 9219950.0,
        "maint_mh_per_fh": 15.73
      }
    },
    "f86f_sabre": {
      "stem": "f86f_sabre",
      "id": "f86f_sabre",
      "design": {
        "id": "f86f_sabre",
        "name": "North American F-86F-30 Sabre",
        "company_id": "north_american",
        "created_date": "1952-10-01",
        "crew_count": 1,
        "role_tags": [
          "day_fighter"
        ],
        "wing": {
          "area_m2": 28.18,
          "aspect_ratio": 4.55,
          "sweep_qc_deg": 35.4,
          "taper_ratio": 0.51,
          "tc_root": 0.095,
          "tc_tip": 0.085,
          "airfoil_ref": "0009.5",
          "planform_type": "conventional",
          "position": "low",
          "x_le_root_frac": 0.34,
          "dihedral_deg": 3.0,
          "incidence_deg": 1.0,
          "twist_deg": -2.0,
          "devices": [
            "slotted_flaps",
            "le_slats"
          ]
        },
        "fuselage": {
          "length_m": 11.43,
          "max_diameter_m": 1.45,
          "nose_fineness": 2.4,
          "tail_fineness": 2.8,
          "canopy_type": "bubble",
          "area_ruled": false
        },
        "empennage": {
          "tailless": false,
          "t_tail": false,
          "all_moving_tail": true,
          "ht_area_m2": 3.25,
          "ht_aspect_ratio": 4.6,
          "ht_sweep_qc_deg": 35.0,
          "vt_area_m2": 3.1,
          "vt_aspect_ratio": 1.7,
          "vt_sweep_qc_deg": 35.0
        },
        "intake": {
          "type": "nose",
          "compression": "pitot",
          "variable": false,
          "spike": false
        },
        "propulsion": {
          "engine_id": "J47-GE-27",
          "count": 1,
          "afterburner": false,
          "x_cg_frac": 0.58
        },
        "structure": {
          "design_load_factor_g": 7.33,
          "material_mix": {
            "al": 0.88,
            "steel": 0.12,
            "ti": 0.0
          },
          "carrier_capable": false
        },
        "fuel": {
          "internal_kg": 1315.0,
          "drop_tanks_count": 2,
          "drop_tank_fuel_kg_each": 455.0,
          "combat_uses_drop_tanks": true
        },
        "systems": {
          "radar_id": "apg30",
          "fire_control_id": null,
          "avionics_level": 2,
          "powered_controls": true,
          "stability_augmentation": false,
          "ejection_seat": true,
          "inflight_refuel": false,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [
            {
              "gun_id": "m3_50",
              "count": 6,
              "rounds_per_gun": 300
            }
          ],
          "hardpoints": 2,
          "internal_bay": false,
          "missile_ids": []
        },
        "published_performance": {
          "empty_mass_kg": 5046.0,
          "combat_mass_kg": 6150.0,
          "mtow_kg": 8230.0,
          "max_mach_sl": 0.9,
          "max_mach_alt": 0.91,
          "alt_of_max_mach_m": 6096.0,
          "climb_rate_sl_mps": 47.2,
          "service_ceiling_m": 15100.0,
          "combat_radius_m": 740000.0,
          "ferry_range_m": 2450000.0,
          "stall_speed_mps": 55.5,
          "takeoff_distance_m": 1100.0,
          "sources": [
            "USAF Standard Aircraft Characteristics: F-86F-30 Sabre (1953)",
            "Knaack, Encyclopedia of US Air Force Aircraft and Missile Systems Vol. 1, pp. 62-68 (1978)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 0.8852,
        "max_mach_alt": 0.9145,
        "alt_of_max_mach_m": 10668.0,
        "service_ceiling_m": 14606.4,
        "climb_rate_sl_mps": 33.76,
        "time_to_alt_10668m_s": 492.9,
        "sustained_turn_dps_m08_4572m": 8.47,
        "instantaneous_turn_dps_m08_4572m": 15.83,
        "ps_mps_m09_4572m_1g": 2.19,
        "combat_radius_m": 764012.8,
        "ferry_range_m": 2107688.0,
        "takeoff_distance_m": 934.0,
        "landing_distance_m": 1153.4,
        "stall_speed_mps": 50.87,
        "max_load_factor_g": 7.33,
        "empty_mass_kg": 4810.8,
        "mtow_kg": 7420.6,
        "internal_fuel_kg": 1315.0,
        "thrust_to_weight_combat": 0.466,
        "wing_loading_combat_kgm2": 205.0,
        "unit_flyaway_cost_usd": 288617.0,
        "dev_cost_usd_estimate": 12121899.0,
        "maint_mh_per_fh": 17.01
      }
    },
    "f89d_scorpion": {
      "stem": "f89d_scorpion",
      "id": "f89d_scorpion",
      "design": {
        "id": "f89d_scorpion",
        "name": "Northrop F-89D Scorpion",
        "company_id": "northrop",
        "created_date": "1953-01-01",
        "crew_count": 2,
        "role_tags": [
          "interceptor"
        ],
        "wing": {
          "area_m2": 56.3,
          "aspect_ratio": 5.38,
          "sweep_qc_deg": 2.0,
          "taper_ratio": 0.45,
          "tc_root": 0.088,
          "tc_tip": 0.088,
          "airfoil_ref": "0009",
          "planform_type": "conventional",
          "position": "mid",
          "x_le_root_frac": 0.36,
          "dihedral_deg": 2.0,
          "incidence_deg": 1.0,
          "twist_deg": -1.5,
          "devices": [
            "slotted_flaps"
          ]
        },
        "fuselage": {
          "length_m": 16.4,
          "max_diameter_m": 1.88,
          "nose_fineness": 2.6,
          "tail_fineness": 3.0,
          "canopy_type": "bubble",
          "area_ruled": false
        },
        "empennage": {
          "tailless": false,
          "t_tail": true,
          "all_moving_tail": false,
          "ht_area_m2": 10.2,
          "ht_aspect_ratio": 4.2,
          "ht_sweep_qc_deg": 5.0,
          "vt_area_m2": 5.2,
          "vt_aspect_ratio": 1.4,
          "vt_sweep_qc_deg": 20.0
        },
        "intake": {
          "type": "cheek",
          "compression": "pitot",
          "variable": false,
          "spike": false
        },
        "propulsion": {
          "engine_id": "J35-A-35",
          "count": 2,
          "afterburner": true,
          "x_cg_frac": 0.56
        },
        "structure": {
          "design_load_factor_g": 6.5,
          "material_mix": {
            "al": 0.88,
            "steel": 0.12,
            "ti": 0.0
          },
          "carrier_capable": false
        },
        "fuel": {
          "internal_kg": 4400.0,
          "drop_tanks_count": 2,
          "drop_tank_fuel_kg_each": 900.0,
          "combat_uses_drop_tanks": false
        },
        "systems": {
          "radar_id": "apg40",
          "fire_control_id": null,
          "avionics_level": 4,
          "powered_controls": true,
          "stability_augmentation": true,
          "ejection_seat": true,
          "inflight_refuel": false,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [],
          "hardpoints": 2,
          "internal_bay": false,
          "missile_ids": [
            "ffar_2_75in",
            "ffar_2_75in"
          ]
        },
        "published_performance": {
          "empty_mass_kg": 11428.0,
          "combat_mass_kg": 14500.0,
          "mtow_kg": 19160.0,
          "max_mach_sl": 0.84,
          "max_mach_alt": 0.86,
          "alt_of_max_mach_m": 6096.0,
          "climb_rate_sl_mps": 42.5,
          "service_ceiling_m": 15000.0,
          "combat_radius_m": 610000.0,
          "ferry_range_m": 2200000.0,
          "stall_speed_mps": 56.0,
          "takeoff_distance_m": 1350.0,
          "sources": [
            "USAF Standard Aircraft Characteristics: F-89D Scorpion (1954)",
            "Knaack, Encyclopedia of US Air Force Aircraft and Missile Systems Vol. 1, pp. 90-95 (1978)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 0.8429,
        "max_mach_alt": 0.8673,
        "alt_of_max_mach_m": 10668.0,
        "service_ceiling_m": 15441.5,
        "climb_rate_sl_mps": 52.84,
        "time_to_alt_10668m_s": 316.4,
        "sustained_turn_dps_m08_4572m": 8.77,
        "instantaneous_turn_dps_m08_4572m": 14.0,
        "ps_mps_m09_4572m_1g": -83.24,
        "combat_radius_m": 691953.1,
        "ferry_range_m": 2841804.2,
        "takeoff_distance_m": 1078.0,
        "landing_distance_m": 1229.9,
        "stall_speed_mps": 53.24,
        "max_load_factor_g": 6.5,
        "empty_mass_kg": 10397.9,
        "mtow_kg": 17370.9,
        "internal_fuel_kg": 4400.0,
        "thrust_to_weight_combat": 0.487,
        "wing_loading_combat_kgm2": 234.8,
        "unit_flyaway_cost_usd": 975711.0,
        "dev_cost_usd_estimate": 40979876.0,
        "maint_mh_per_fh": 30.59
      }
    },
    "f8u1_crusader": {
      "stem": "f8u1_crusader",
      "id": "f8u1_crusader",
      "design": {
        "id": "f8u1_crusader",
        "name": "Vought F8U-1 (F-8A) Crusader",
        "company_id": "vought",
        "created_date": "1955-03-25",
        "crew_count": 1,
        "role_tags": [
          "day_fighter",
          "carrier"
        ],
        "wing": {
          "area_m2": 34.84,
          "aspect_ratio": 3.4,
          "sweep_qc_deg": 42.0,
          "taper_ratio": 0.25,
          "tc_root": 0.06,
          "tc_tip": 0.05,
          "airfoil_ref": "65A006",
          "planform_type": "conventional",
          "position": "high",
          "x_le_root_frac": 0.34,
          "dihedral_deg": -5.0,
          "incidence_deg": 1.0,
          "twist_deg": -1.5,
          "devices": [
            "fowler_flaps",
            "le_flaps"
          ]
        },
        "fuselage": {
          "length_m": 16.53,
          "max_diameter_m": 1.54,
          "nose_fineness": 2.9,
          "tail_fineness": 3.4,
          "canopy_type": "faired",
          "area_ruled": true,
          "area_rule_waist_frac": 0.55
        },
        "empennage": {
          "tailless": false,
          "t_tail": false,
          "all_moving_tail": true,
          "ht_area_m2": 8.68,
          "ht_aspect_ratio": 3.5,
          "ht_sweep_qc_deg": 45.0,
          "vt_area_m2": 10.1,
          "vt_aspect_ratio": 1.5,
          "vt_sweep_qc_deg": 45.0
        },
        "intake": {
          "type": "chin",
          "compression": "pitot",
          "variable": false,
          "spike": false
        },
        "propulsion": {
          "engine_id": "J57-P-16",
          "count": 1,
          "afterburner": true,
          "x_cg_frac": 0.62
        },
        "structure": {
          "design_load_factor_g": 7.33,
          "material_mix": {
            "al": 0.78,
            "steel": 0.12,
            "ti": 0.1
          },
          "carrier_capable": true
        },
        "fuel": {
          "internal_kg": 4130.0,
          "drop_tanks_count": 0,
          "drop_tank_fuel_kg_each": 0.0,
          "combat_uses_drop_tanks": false
        },
        "systems": {
          "radar_id": "apg30",
          "fire_control_id": null,
          "avionics_level": 2,
          "powered_controls": true,
          "stability_augmentation": true,
          "ejection_seat": true,
          "inflight_refuel": true,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [
            {
              "gun_id": "mk12_20mm",
              "count": 4,
              "rounds_per_gun": 144
            }
          ],
          "hardpoints": 2,
          "internal_bay": false,
          "missile_ids": [
            "aim9b_sidewinder",
            "aim9b_sidewinder"
          ]
        },
        "published_performance": {
          "empty_mass_kg": 7956.0,
          "combat_mass_kg": 10450.0,
          "mtow_kg": 12700.0,
          "max_mach_sl": 1.02,
          "max_mach_alt": 1.66,
          "alt_of_max_mach_m": 10668.0,
          "climb_rate_sl_mps": 115.0,
          "service_ceiling_m": 17370.0,
          "combat_radius_m": 780000.0,
          "ferry_range_m": 2250000.0,
          "stall_speed_mps": 55.0,
          "takeoff_distance_m": 1050.0,
          "sources": [
            "US Navy Standard Aircraft Characteristics: F8U-1 Crusader, NAVAER 1335A (1958)",
            "Loftin, Quest for Performance, NASA SP-468, Table V (1985)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 1.0631,
        "max_mach_alt": 1.7574,
        "alt_of_max_mach_m": 12192.0,
        "service_ceiling_m": 16524.0,
        "climb_rate_sl_mps": 112.48,
        "time_to_alt_10668m_s": 139.2,
        "sustained_turn_dps_m08_4572m": 10.42,
        "instantaneous_turn_dps_m08_4572m": 15.83,
        "ps_mps_m09_4572m_1g": 149.4,
        "combat_radius_m": 882450.8,
        "ferry_range_m": 2594989.9,
        "takeoff_distance_m": 1054.7,
        "landing_distance_m": 1447.5,
        "stall_speed_mps": 59.49,
        "max_load_factor_g": 7.33,
        "empty_mass_kg": 8338.9,
        "mtow_kg": 12848.9,
        "internal_fuel_kg": 4130.0,
        "thrust_to_weight_combat": 0.753,
        "wing_loading_combat_kgm2": 309.5,
        "unit_flyaway_cost_usd": 561498.0,
        "dev_cost_usd_estimate": 26798121.0,
        "maint_mh_per_fh": 21.7
      }
    },
    "mig15bis": {
      "stem": "mig15bis",
      "id": "mig15bis",
      "design": {
        "id": "mig15bis",
        "name": "Mikoyan-Gurevich MiG-15bis",
        "company_id": "mikoyan",
        "created_date": "1950-07-01",
        "crew_count": 1,
        "role_tags": [
          "day_fighter",
          "interceptor"
        ],
        "wing": {
          "area_m2": 20.6,
          "aspect_ratio": 4.85,
          "sweep_qc_deg": 35.0,
          "taper_ratio": 0.56,
          "tc_root": 0.1,
          "tc_tip": 0.11,
          "airfoil_ref": "0010",
          "planform_type": "conventional",
          "position": "mid",
          "x_le_root_frac": 0.34,
          "dihedral_deg": -2.0,
          "incidence_deg": 1.0,
          "twist_deg": -1.0,
          "devices": [
            "fowler_flaps"
          ]
        },
        "fuselage": {
          "length_m": 10.11,
          "max_diameter_m": 1.45,
          "nose_fineness": 2.1,
          "tail_fineness": 2.5,
          "canopy_type": "bubble",
          "area_ruled": false
        },
        "empennage": {
          "tailless": false,
          "t_tail": true,
          "all_moving_tail": false,
          "ht_area_m2": 3.0,
          "ht_aspect_ratio": 4.2,
          "ht_sweep_qc_deg": 40.0,
          "vt_area_m2": 2.95,
          "vt_aspect_ratio": 1.45,
          "vt_sweep_qc_deg": 55.0
        },
        "intake": {
          "type": "nose",
          "compression": "pitot",
          "variable": false,
          "spike": false
        },
        "propulsion": {
          "engine_id": "VK-1",
          "count": 1,
          "afterburner": false,
          "x_cg_frac": 0.55
        },
        "structure": {
          "design_load_factor_g": 8.0,
          "material_mix": {
            "al": 0.9,
            "steel": 0.1,
            "ti": 0.0
          },
          "carrier_capable": false
        },
        "fuel": {
          "internal_kg": 1170.0,
          "drop_tanks_count": 2,
          "drop_tank_fuel_kg_each": 310.0,
          "combat_uses_drop_tanks": false
        },
        "systems": {
          "radar_id": null,
          "fire_control_id": null,
          "avionics_level": 1,
          "powered_controls": true,
          "stability_augmentation": false,
          "ejection_seat": true,
          "inflight_refuel": false,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [
            {
              "gun_id": "nr23_23mm",
              "count": 2,
              "rounds_per_gun": 80
            },
            {
              "gun_id": "n37_37mm",
              "count": 1,
              "rounds_per_gun": 40
            }
          ],
          "hardpoints": 2,
          "internal_bay": false,
          "missile_ids": []
        },
        "published_performance": {
          "empty_mass_kg": 3681.0,
          "combat_mass_kg": 4450.0,
          "mtow_kg": 6105.0,
          "max_mach_sl": 0.88,
          "max_mach_alt": 0.92,
          "alt_of_max_mach_m": 6096.0,
          "climb_rate_sl_mps": 59.2,
          "service_ceiling_m": 15500.0,
          "combat_radius_m": 420000.0,
          "ferry_range_m": 1860000.0,
          "stall_speed_mps": 54.0,
          "takeoff_distance_m": 920.0,
          "sources": [
            "Gordon, Mikoyan-Gurevich MiG-15: The Soviet Union's Long-Lived Korean War Fighter (2001)",
            "USAF Foreign Technology Division Evaluation of Captured MiG-15bis (1953)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 0.8873,
        "max_mach_alt": 0.9164,
        "alt_of_max_mach_m": 10668.0,
        "service_ceiling_m": 15738.3,
        "climb_rate_sl_mps": 55.64,
        "time_to_alt_10668m_s": 300.8,
        "sustained_turn_dps_m08_4572m": 9.82,
        "instantaneous_turn_dps_m08_4572m": 17.3,
        "ps_mps_m09_4572m_1g": 2.78,
        "combat_radius_m": 365113.4,
        "ferry_range_m": 1902419.7,
        "takeoff_distance_m": 911.3,
        "landing_distance_m": 1264.2,
        "stall_speed_mps": 54.34,
        "max_load_factor_g": 8.0,
        "empty_mass_kg": 3853.7,
        "mtow_kg": 5891.8,
        "internal_fuel_kg": 1170.0,
        "thrust_to_weight_combat": 0.585,
        "wing_loading_combat_kgm2": 225.0,
        "unit_flyaway_cost_usd": 180209.0,
        "dev_cost_usd_estimate": 7568765.0,
        "maint_mh_per_fh": 15.36
      }
    },
    "p80a_shooting_star": {
      "stem": "p80a_shooting_star",
      "id": "p80a_shooting_star",
      "design": {
        "id": "p80a_shooting_star",
        "name": "Lockheed P-80A Shooting Star",
        "company_id": "lockheed",
        "created_date": "1945-02-01",
        "crew_count": 1,
        "role_tags": [
          "day_fighter"
        ],
        "wing": {
          "area_m2": 22.07,
          "aspect_ratio": 6.37,
          "sweep_qc_deg": 4.8,
          "taper_ratio": 0.38,
          "tc_root": 0.13,
          "tc_tip": 0.13,
          "airfoil_ref": "65-213",
          "planform_type": "conventional",
          "position": "low",
          "x_le_root_frac": 0.35,
          "dihedral_deg": 3.8,
          "incidence_deg": 1.0,
          "twist_deg": -1.5,
          "devices": [
            "split_flaps",
            "plain_flaps"
          ]
        },
        "fuselage": {
          "length_m": 10.52,
          "max_diameter_m": 1.32,
          "nose_fineness": 2.4,
          "tail_fineness": 3.0,
          "canopy_type": "bubble",
          "area_ruled": false
        },
        "empennage": {
          "tailless": false,
          "t_tail": false,
          "all_moving_tail": false,
          "ht_area_m2": 3.5,
          "ht_aspect_ratio": 4.2,
          "ht_sweep_qc_deg": 6.0,
          "vt_area_m2": 2.1,
          "vt_aspect_ratio": 1.6,
          "vt_sweep_qc_deg": 18.0
        },
        "intake": {
          "type": "cheek",
          "compression": "pitot",
          "variable": false,
          "spike": false
        },
        "propulsion": {
          "engine_id": "J33-A-9",
          "count": 1,
          "afterburner": false,
          "x_cg_frac": 0.56
        },
        "structure": {
          "design_load_factor_g": 7.33,
          "material_mix": {
            "al": 0.9,
            "steel": 0.1,
            "ti": 0.0
          },
          "carrier_capable": false
        },
        "fuel": {
          "internal_kg": 1220.0,
          "drop_tanks_count": 2,
          "drop_tank_fuel_kg_each": 470.0,
          "combat_uses_drop_tanks": false
        },
        "systems": {
          "radar_id": null,
          "fire_control_id": null,
          "avionics_level": 1,
          "powered_controls": true,
          "stability_augmentation": false,
          "ejection_seat": false,
          "inflight_refuel": false,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [
            {
              "gun_id": "an_m2_50",
              "count": 6,
              "rounds_per_gun": 300
            }
          ],
          "hardpoints": 2,
          "internal_bay": false,
          "missile_ids": []
        },
        "published_performance": {
          "empty_mass_kg": 3592.0,
          "combat_mass_kg": 4650.0,
          "mtow_kg": 6350.0,
          "max_mach_sl": 0.73,
          "max_mach_alt": 0.76,
          "alt_of_max_mach_m": 6096.0,
          "climb_rate_sl_mps": 23.3,
          "service_ceiling_m": 12500.0,
          "combat_radius_m": 440000.0,
          "ferry_range_m": 1930000.0,
          "stall_speed_mps": 51.0,
          "takeoff_distance_m": 1150.0,
          "sources": [
            "USAAF Standard Aircraft Characteristics: P-80A-1-LO (1946)",
            "Loftin, Quest for Performance, NASA SP-468, Table V (1985)",
            "Knaack, Encyclopedia of US Air Force Aircraft and Missile Systems Vol. 1 (1978)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 0.7777,
        "max_mach_alt": 0.7886,
        "alt_of_max_mach_m": 6096.0,
        "service_ceiling_m": 12902.4,
        "climb_rate_sl_mps": 24.43,
        "time_to_alt_10668m_s": 899.4,
        "sustained_turn_dps_m08_4572m": 0.0,
        "instantaneous_turn_dps_m08_4572m": 15.83,
        "ps_mps_m09_4572m_1g": -336.29,
        "combat_radius_m": 434719.6,
        "ferry_range_m": 2285932.0,
        "takeoff_distance_m": 1101.8,
        "landing_distance_m": 1125.4,
        "stall_speed_mps": 49.99,
        "max_load_factor_g": 7.33,
        "empty_mass_kg": 3599.8,
        "mtow_kg": 6147.1,
        "internal_fuel_kg": 1220.0,
        "thrust_to_weight_combat": 0.381,
        "wing_loading_combat_kgm2": 204.7,
        "unit_flyaway_cost_usd": 164904.0,
        "dev_cost_usd_estimate": 6925984.0,
        "maint_mh_per_fh": 15.62
      }
    },
    "yf102_pre_area_rule": {
      "stem": "yf102_pre_area_rule",
      "id": "yf102_pre_area_rule",
      "design": {
        "id": "yf102_pre_area_rule",
        "name": "Convair YF-102 Delta Dagger (Pre-Area-Rule)",
        "company_id": "convair",
        "created_date": "1953-10-24",
        "crew_count": 1,
        "role_tags": [
          "interceptor"
        ],
        "wing": {
          "area_m2": 61.45,
          "aspect_ratio": 2.17,
          "sweep_qc_deg": 52.5,
          "taper_ratio": 0.05,
          "tc_root": 0.04,
          "tc_tip": 0.04,
          "airfoil_ref": "0004",
          "planform_type": "delta",
          "position": "mid",
          "x_le_root_frac": 0.28,
          "dihedral_deg": 0.0,
          "incidence_deg": 0.0,
          "twist_deg": 0.0,
          "conical_camber": false,
          "devices": [
            "plain_flaps"
          ]
        },
        "fuselage": {
          "length_m": 16.05,
          "max_diameter_m": 1.84,
          "nose_fineness": 1.9,
          "tail_fineness": 2.0,
          "canopy_type": "faired",
          "area_ruled": false
        },
        "empennage": {
          "tailless": true,
          "t_tail": false,
          "all_moving_tail": false,
          "ht_area_m2": 0.0,
          "vt_area_m2": 6.4,
          "vt_aspect_ratio": 1.35,
          "vt_sweep_qc_deg": 52.0
        },
        "intake": {
          "type": "cheek",
          "compression": "pitot",
          "variable": false,
          "spike": false
        },
        "propulsion": {
          "engine_id": "J57-P-11",
          "count": 1,
          "afterburner": true,
          "x_cg_frac": 0.62
        },
        "structure": {
          "design_load_factor_g": 7.0,
          "material_mix": {
            "al": 0.85,
            "steel": 0.12,
            "ti": 0.03
          },
          "carrier_capable": false
        },
        "fuel": {
          "internal_kg": 2480.0,
          "drop_tanks_count": 0,
          "drop_tank_fuel_kg_each": 0.0,
          "combat_uses_drop_tanks": false
        },
        "systems": {
          "radar_id": "mg10",
          "fire_control_id": null,
          "avionics_level": 4,
          "powered_controls": true,
          "stability_augmentation": true,
          "ejection_seat": true,
          "inflight_refuel": false,
          "pressurized_cockpit": true
        },
        "armament": {
          "guns": [],
          "hardpoints": 0,
          "internal_bay": true,
          "missile_ids": [
            "aim4a_falcon",
            "aim4a_falcon",
            "aim4a_falcon",
            "aim4a_falcon",
            "aim4a_falcon",
            "aim4a_falcon"
          ]
        },
        "published_performance": {
          "empty_mass_kg": 8550.0,
          "combat_mass_kg": 10600.0,
          "mtow_kg": 12200.0,
          "max_mach_sl": 0.94,
          "max_mach_alt": 0.98,
          "alt_of_max_mach_m": 10668.0,
          "climb_rate_sl_mps": 75.0,
          "service_ceiling_m": 14600.0,
          "combat_radius_m": 520000.0,
          "ferry_range_m": 1650000.0,
          "stall_speed_mps": 55.0,
          "takeoff_distance_m": 1250.0,
          "sources": [
            "Loftin, Quest for Performance, NASA SP-468, Ch. 11 (YF-102 transonic area-rule case study)",
            "Knaack, Encyclopedia of US Air Force Aircraft and Missile Systems Vol. 1, pp. 159-163 (1978)"
          ]
        }
      },
      "oracle_perf": {
        "max_mach_sl": 1.0,
        "max_mach_alt": 1.0321,
        "alt_of_max_mach_m": 12192.0,
        "service_ceiling_m": 15400.4,
        "climb_rate_sl_mps": 79.08,
        "time_to_alt_10668m_s": 223.4,
        "sustained_turn_dps_m08_4572m": 9.41,
        "instantaneous_turn_dps_m08_4572m": 15.1,
        "ps_mps_m09_4572m_1g": 93.04,
        "combat_radius_m": 467319.2,
        "ferry_range_m": 1620629.2,
        "takeoff_distance_m": 790.5,
        "landing_distance_m": 1316.0,
        "stall_speed_mps": 55.68,
        "max_load_factor_g": 7.0,
        "empty_mass_kg": 8069.9,
        "mtow_kg": 10968.9,
        "internal_fuel_kg": 2480.0,
        "thrust_to_weight_combat": 0.666,
        "wing_loading_combat_kgm2": 158.3,
        "unit_flyaway_cost_usd": 1197527.0,
        "dev_cost_usd_estimate": 50586825.0,
        "maint_mh_per_fh": 23.54
      }
    }
  },
  "engines_hist": {
    "j33_a_35": {
      "engine_id": "j33_a_35",
      "name": "Allison J33-A-35",
      "manufacturer": "Allison (GM)",
      "country": "USA",
      "first_run_year": 1944,
      "service_entry_year": 1948,
      "applications": [
        "Lockheed F-80C Shooting Star",
        "Lockheed T-33A"
      ],
      "cycle_input": {
        "compressor_type": "centrifugal",
        "spools": 1,
        "variable_stators": false,
        "has_afterburner": false,
        "nozzle_type": "convergent",
        "mass_flow_kgps": 40.82,
        "opr": 4.4,
        "tit_K": 1090.0,
        "ab_temp_K": 0.0,
        "bypass_ratio": 0.0,
        "cooled_turbine": false,
        "eta_c_poly": 0.785,
        "eta_t_poly": 0.835,
        "eta_burner": 0.94,
        "pi_burner": 0.935,
        "specific_weight_factor": 1.03,
        "mtbf_factor": 1.15,
        "length_factor": 1.0,
        "diameter_factor": 1.0,
        "cumulative_test_hours": 2500.0
      },
      "historical_reference": {
        "sls_dry_thrust_N": 20461.8,
        "sls_ab_thrust_N": null,
        "sls_dry_tsfc_kg_per_Ns": 3.17245e-05,
        "sls_ab_tsfc_kg_per_Ns": null,
        "mass_kg": 825.5,
        "diameter_m": 1.2827,
        "length_m": 2.7178,
        "unit_cost_usd": 18000.0,
        "tbo_hours_service": 500.0,
        "sources": [
          "Jane's All the World's Aircraft 1955-56",
          "Wilkinson, Aircraft Engines of the World 1957, pp. 68-69",
          "NMUSAF Fact Sheet: Allison J33"
        ]
      }
    },
    "j35_a_29": {
      "engine_id": "j35_a_29",
      "name": "Allison J35-A-29",
      "manufacturer": "Allison (GM)",
      "country": "USA",
      "first_run_year": 1944,
      "service_entry_year": 1951,
      "applications": [
        "Republic F-84G Thunderjet"
      ],
      "cycle_input": {
        "compressor_type": "axial",
        "spools": 1,
        "variable_stators": false,
        "has_afterburner": false,
        "nozzle_type": "convergent",
        "mass_flow_kgps": 40.5,
        "opr": 5.1,
        "tit_K": 1125.0,
        "ab_temp_K": 0.0,
        "bypass_ratio": 0.0,
        "cooled_turbine": false,
        "eta_c_poly": 0.815,
        "eta_t_poly": 0.84,
        "eta_burner": 0.94,
        "pi_burner": 0.94,
        "specific_weight_factor": 1.22,
        "mtbf_factor": 0.95,
        "length_factor": 1.04,
        "diameter_factor": 1.04,
        "cumulative_test_hours": 1500.0
      },
      "historical_reference": {
        "sls_dry_thrust_N": 24732.1,
        "sls_ab_thrust_N": null,
        "sls_dry_tsfc_kg_per_Ns": 3.05915e-05,
        "sls_ab_tsfc_kg_per_Ns": null,
        "mass_kg": 1045.5,
        "diameter_m": 0.9398,
        "length_m": 3.7084,
        "unit_cost_usd": 46000.0,
        "tbo_hours_service": 300.0,
        "sources": [
          "Wilkinson, Aircraft Engines of the World 1953, pp. 60-62",
          "NACA RM E53G24 (NTRS 19930086171)"
        ]
      }
    },
    "j47_ge_27": {
      "engine_id": "j47_ge_27",
      "name": "General Electric J47-GE-27",
      "manufacturer": "General Electric",
      "country": "USA",
      "first_run_year": 1947,
      "service_entry_year": 1952,
      "applications": [
        "North American F-86F Sabre",
        "North American FJ-2 Fury"
      ],
      "cycle_input": {
        "compressor_type": "axial",
        "spools": 1,
        "variable_stators": false,
        "has_afterburner": false,
        "nozzle_type": "convergent",
        "mass_flow_kgps": 42.2,
        "opr": 5.35,
        "tit_K": 1130.0,
        "ab_temp_K": 0.0,
        "bypass_ratio": 0.0,
        "cooled_turbine": false,
        "eta_c_poly": 0.84,
        "eta_t_poly": 0.86,
        "eta_burner": 0.955,
        "pi_burner": 0.95,
        "specific_weight_factor": 1.3,
        "mtbf_factor": 1.25,
        "length_factor": 1.02,
        "diameter_factor": 1.03,
        "cumulative_test_hours": 3000.0
      },
      "historical_reference": {
        "sls_dry_thrust_N": 26555.9,
        "sls_ab_thrust_N": null,
        "sls_dry_tsfc_kg_per_Ns": 2.87219e-05,
        "sls_ab_tsfc_kg_per_Ns": null,
        "mass_kg": 1158.5,
        "diameter_m": 0.9335,
        "length_m": 3.683,
        "unit_cost_usd": 47000.0,
        "tbo_hours_service": 625.0,
        "sources": [
          "Jane's All the World's Aircraft 1955-56",
          "Flight, 11 May 1956, p. 590",
          "NMUSAF Fact Sheet: General Electric J47"
        ]
      }
    },
    "j57_p_21": {
      "engine_id": "j57_p_21",
      "name": "Pratt & Whitney J57-P-21",
      "manufacturer": "Pratt & Whitney",
      "country": "USA",
      "first_run_year": 1950,
      "service_entry_year": 1955,
      "applications": [
        "North American F-100C/D Super Sabre"
      ],
      "cycle_input": {
        "compressor_type": "axial",
        "spools": 2,
        "variable_stators": false,
        "has_afterburner": true,
        "nozzle_type": "convergent",
        "mass_flow_kgps": 75.75,
        "opr": 11.5,
        "tit_K": 1144.0,
        "ab_temp_K": 1980.0,
        "bypass_ratio": 0.0,
        "cooled_turbine": false,
        "eta_c_poly": 0.875,
        "eta_t_poly": 0.885,
        "eta_burner": 0.975,
        "pi_burner": 0.96,
        "eta_ab": 0.86,
        "specific_weight_factor": 0.95,
        "mtbf_factor": 1.15,
        "length_factor": 0.99,
        "diameter_factor": 1.01,
        "cumulative_test_hours": 2500.0
      },
      "historical_reference": {
        "sls_dry_thrust_N": 45371.9,
        "sls_ab_thrust_N": 71171.5,
        "sls_dry_tsfc_kg_per_Ns": 2.22355e-05,
        "sls_ab_tsfc_kg_per_Ns": 5.80672e-05,
        "mass_kg": 2347.3,
        "diameter_m": 1.016,
        "length_m": 6.1976,
        "unit_cost_usd": 245000.0,
        "tbo_hours_service": 800.0,
        "sources": [
          "USAF Standard Aircraft Characteristics: F-100D",
          "NMUSAF Fact Sheet: Pratt & Whitney J57"
        ]
      }
    },
    "j65_w_3": {
      "engine_id": "j65_w_3",
      "name": "Wright J65-W-3",
      "manufacturer": "Curtiss-Wright",
      "country": "USA",
      "first_run_year": 1951,
      "service_entry_year": 1954,
      "applications": [
        "Republic F-84F Thunderstreak",
        "North American FJ-3 Fury"
      ],
      "cycle_input": {
        "compressor_type": "axial",
        "spools": 1,
        "variable_stators": false,
        "has_afterburner": false,
        "nozzle_type": "convergent",
        "mass_flow_kgps": 54.0,
        "opr": 7.0,
        "tit_K": 1110.0,
        "ab_temp_K": 0.0,
        "bypass_ratio": 0.0,
        "cooled_turbine": false,
        "eta_c_poly": 0.855,
        "eta_t_poly": 0.87,
        "eta_burner": 0.965,
        "pi_burner": 0.955,
        "specific_weight_factor": 1.07,
        "mtbf_factor": 0.95,
        "length_factor": 0.84,
        "diameter_factor": 1.01,
        "cumulative_test_hours": 1500.0
      },
      "historical_reference": {
        "sls_dry_thrust_N": 32116.2,
        "sls_ab_thrust_N": null,
        "sls_dry_tsfc_kg_per_Ns": 2.60028e-05,
        "sls_ab_tsfc_kg_per_Ns": null,
        "mass_kg": 1259.2,
        "diameter_m": 0.953,
        "length_m": 3.2258,
        "unit_cost_usd": 75000.0,
        "tbo_hours_service": 400.0,
        "sources": [
          "Flight, 6 Jan 1956, pp. 20-22",
          "Gunston, World Encyclopaedia of Aero Engines (1989)"
        ]
      }
    },
    "j71_a_2": {
      "engine_id": "j71_a_2",
      "name": "Allison J71-A-2",
      "manufacturer": "Allison (GM)",
      "country": "USA",
      "first_run_year": 1951,
      "service_entry_year": 1955,
      "applications": [
        "McDonnell F3H-2 Demon"
      ],
      "cycle_input": {
        "compressor_type": "axial",
        "spools": 1,
        "variable_stators": false,
        "has_afterburner": true,
        "nozzle_type": "convergent",
        "mass_flow_kgps": 72.57,
        "opr": 8.0,
        "tit_K": 1135.0,
        "ab_temp_K": 1730.0,
        "bypass_ratio": 0.0,
        "cooled_turbine": false,
        "eta_c_poly": 0.865,
        "eta_t_poly": 0.875,
        "eta_burner": 0.97,
        "pi_burner": 0.96,
        "eta_ab": 0.85,
        "specific_weight_factor": 1.14,
        "mtbf_factor": 0.9,
        "length_factor": 1.14,
        "diameter_factor": 1.01,
        "cumulative_test_hours": 1200.0
      },
      "historical_reference": {
        "sls_dry_thrust_N": 44482.2,
        "sls_ab_thrust_N": 62275.1,
        "sls_dry_tsfc_kg_per_Ns": 2.30852e-05,
        "sls_ab_tsfc_kg_per_Ns": 5.09858e-05,
        "mass_kg": 2218.1,
        "diameter_m": 1.0033,
        "length_m": 7.2263,
        "unit_cost_usd": 180000.0,
        "tbo_hours_service": 350.0,
        "sources": [
          "Wilkinson, Aircraft Engines of the World 1957, pp. 74-75",
          "McDonnell F3H-2 Demon Flight Manual"
        ]
      }
    },
    "j73_ge_3": {
      "engine_id": "j73_ge_3",
      "name": "General Electric J73-GE-3",
      "manufacturer": "General Electric",
      "country": "USA",
      "first_run_year": 1951,
      "service_entry_year": 1954,
      "applications": [
        "North American F-86H Sabre"
      ],
      "cycle_input": {
        "compressor_type": "axial",
        "spools": 1,
        "variable_stators": false,
        "has_afterburner": false,
        "nozzle_type": "convergent",
        "mass_flow_kgps": 70.31,
        "opr": 7.5,
        "tit_K": 1117.0,
        "ab_temp_K": 0.0,
        "bypass_ratio": 0.0,
        "cooled_turbine": false,
        "eta_c_poly": 0.855,
        "eta_t_poly": 0.87,
        "eta_burner": 0.965,
        "pi_burner": 0.955,
        "specific_weight_factor": 1.11,
        "mtbf_factor": 1.0,
        "length_factor": 1.22,
        "diameter_factor": 1.01,
        "cumulative_test_hours": 1000.0
      },
      "historical_reference": {
        "sls_dry_thrust_N": 40034.0,
        "sls_ab_thrust_N": null,
        "sls_dry_tsfc_kg_per_Ns": 2.54929e-05,
        "sls_ab_tsfc_kg_per_Ns": null,
        "mass_kg": 1655.6,
        "diameter_m": 1.0033,
        "length_m": 5.08,
        "unit_cost_usd": 100000.0,
        "tbo_hours_service": 350.0,
        "sources": [
          "Flight, 9 April 1954, p. 457",
          "Wilkinson, Aircraft Engines of the World 1953, pp. 82-83",
          "NMUSAF Fact Sheet: General Electric J73"
        ]
      }
    },
    "j75_p_19w": {
      "engine_id": "j75_p_19w",
      "name": "Pratt & Whitney J75-P-19W",
      "manufacturer": "Pratt & Whitney",
      "country": "USA",
      "first_run_year": 1955,
      "service_entry_year": 1959,
      "applications": [
        "Republic F-105D Thunderchief",
        "Convair F-106A/B Delta Dart"
      ],
      "cycle_input": {
        "compressor_type": "axial",
        "spools": 2,
        "variable_stators": false,
        "has_afterburner": true,
        "nozzle_type": "convergent_divergent",
        "mass_flow_kgps": 114.3,
        "opr": 12.0,
        "tit_K": 1145.0,
        "ab_temp_K": 1950.0,
        "bypass_ratio": 0.0,
        "cooled_turbine": false,
        "eta_c_poly": 0.865,
        "eta_t_poly": 0.875,
        "eta_burner": 0.97,
        "pi_burner": 0.955,
        "eta_ab": 0.83,
        "specific_weight_factor": 0.74,
        "mtbf_factor": 1.25,
        "length_factor": 0.96,
        "diameter_factor": 1.0,
        "cumulative_test_hours": 2500.0
      },
      "historical_reference": {
        "sls_dry_thrust_N": 71616.4,
        "sls_ab_thrust_N": 108981.4,
        "sls_dry_tsfc_kg_per_Ns": 2.23771e-05,
        "sls_ab_tsfc_kg_per_Ns": 5.94834e-05,
        "mass_kg": 2698.9,
        "diameter_m": 1.0922,
        "length_m": 6.5786,
        "unit_cost_usd": 320000.0,
        "tbo_hours_service": 800.0,
        "sources": [
          "Jane's All the World's Aircraft 1962-63",
          "Wilkinson, Aircraft Engines of the World 1966/67"
        ]
      }
    },
    "j79_ge_11a": {
      "engine_id": "j79_ge_11a",
      "name": "General Electric J79-GE-11A",
      "manufacturer": "General Electric",
      "country": "USA",
      "first_run_year": 1954,
      "service_entry_year": 1958,
      "applications": [
        "Lockheed F-104G Starfighter",
        "McDonnell F4H-1 / F-4B Phantom II"
      ],
      "cycle_input": {
        "compressor_type": "axial",
        "spools": 1,
        "variable_stators": true,
        "has_afterburner": true,
        "nozzle_type": "convergent_divergent",
        "mass_flow_kgps": 74.0,
        "opr": 12.5,
        "tit_K": 1160.0,
        "ab_temp_K": 1965.0,
        "bypass_ratio": 0.0,
        "cooled_turbine": false,
        "eta_c_poly": 0.845,
        "eta_t_poly": 0.86,
        "eta_burner": 0.955,
        "pi_burner": 0.945,
        "eta_ab": 0.88,
        "pi_ab_dry": 0.955,
        "specific_weight_factor": 0.89,
        "mtbf_factor": 1.3,
        "length_factor": 0.92,
        "diameter_factor": 0.98,
        "cumulative_test_hours": 3000.0
      },
      "historical_reference": {
        "sls_dry_thrust_N": 44482.2,
        "sls_ab_thrust_N": 70281.9,
        "sls_dry_tsfc_kg_per_Ns": 2.37934e-05,
        "sls_ab_tsfc_kg_per_Ns": 5.58011e-05,
        "mass_kg": 1626.1,
        "diameter_m": 0.983,
        "length_m": 5.2781,
        "unit_cost_usd": 200000.0,
        "tbo_hours_service": 1000.0,
        "sources": [
          "Jane's All the World's Aircraft 1974-75, pp. 747-748",
          "Lockheed F-104G Flight Manual",
          "NMUSAF Fact Sheet: General Electric J79"
        ]
      }
    },
    "rd_9b": {
      "engine_id": "rd_9b",
      "name": "Tumansky RD-9B",
      "manufacturer": "OKB-300 Mikulin / Tumansky",
      "country": "USSR",
      "first_run_year": 1953,
      "service_entry_year": 1955,
      "applications": [
        "Mikoyan-Gurevich MiG-19S / PF / PM"
      ],
      "cycle_input": {
        "compressor_type": "axial",
        "spools": 1,
        "variable_stators": false,
        "has_afterburner": true,
        "nozzle_type": "convergent",
        "mass_flow_kgps": 43.5,
        "opr": 7.14,
        "tit_K": 1120.0,
        "ab_temp_K": 1415.0,
        "bypass_ratio": 0.0,
        "cooled_turbine": true,
        "eta_c_poly": 0.85,
        "eta_t_poly": 0.865,
        "eta_burner": 0.96,
        "pi_burner": 0.955,
        "eta_ab": 0.83,
        "pi_ab_dry": 0.985,
        "pi_ab_wet": 0.945,
        "specific_weight_factor": 0.57,
        "mtbf_factor": 0.55,
        "length_factor": 1.0,
        "diameter_factor": 0.88,
        "cumulative_test_hours": 800.0
      },
      "historical_reference": {
        "sls_dry_thrust_N": 25510.0,
        "sls_ab_thrust_N": 31900.0,
        "sls_dry_tsfc_kg_per_Ns": 2.63889e-05,
        "sls_ab_tsfc_kg_per_Ns": 4.52778e-05,
        "mass_kg": 695.0,
        "diameter_m": 0.801,
        "length_m": 5.555,
        "unit_cost_usd": 22000.0,
        "tbo_hours_service": 150.0,
        "sources": [
          "LeteckeMotory.cz: RD-9B (M-07) Official Technical Manual",
          "Gunston, World Encyclopaedia of Aero Engines (1989)"
        ]
      }
    },
    "vk_1": {
      "engine_id": "vk_1",
      "name": "Klimov VK-1",
      "manufacturer": "OKB-117 Klimov",
      "country": "USSR",
      "first_run_year": 1947,
      "service_entry_year": 1949,
      "applications": [
        "Mikoyan-Gurevich MiG-15bis",
        "Ilyushin Il-28"
      ],
      "cycle_input": {
        "compressor_type": "centrifugal",
        "spools": 1,
        "variable_stators": false,
        "has_afterburner": false,
        "nozzle_type": "convergent",
        "mass_flow_kgps": 48.2,
        "opr": 4.42,
        "tit_K": 1148.0,
        "ab_temp_K": 0.0,
        "bypass_ratio": 0.0,
        "cooled_turbine": false,
        "eta_c_poly": 0.795,
        "eta_t_poly": 0.85,
        "eta_burner": 0.955,
        "pi_burner": 0.945,
        "specific_weight_factor": 0.94,
        "mtbf_factor": 0.65,
        "length_factor": 0.97,
        "diameter_factor": 0.98,
        "cumulative_test_hours": 1000.0
      },
      "historical_reference": {
        "sls_dry_thrust_N": 26476.0,
        "sls_ab_thrust_N": null,
        "sls_dry_tsfc_kg_per_Ns": 3.03082e-05,
        "sls_ab_tsfc_kg_per_Ns": null,
        "mass_kg": 872.0,
        "diameter_m": 1.2733,
        "length_m": 2.6518,
        "unit_cost_usd": 22500.0,
        "tbo_hours_service": 200.0,
        "sources": [
          "LeteckeMotory.cz: VK-1 Official Technical Manual",
          "Gunston, World Encyclopaedia of Aero Engines (1989)"
        ]
      }
    },
    "vk_1f": {
      "engine_id": "vk_1f",
      "name": "Klimov VK-1F",
      "manufacturer": "OKB-117 Klimov",
      "country": "USSR",
      "first_run_year": 1951,
      "service_entry_year": 1953,
      "applications": [
        "Mikoyan-Gurevich MiG-17F"
      ],
      "cycle_input": {
        "compressor_type": "centrifugal",
        "spools": 1,
        "variable_stators": false,
        "has_afterburner": true,
        "nozzle_type": "convergent",
        "mass_flow_kgps": 48.2,
        "opr": 4.42,
        "tit_K": 1148.0,
        "ab_temp_K": 1575.0,
        "bypass_ratio": 0.0,
        "cooled_turbine": false,
        "eta_c_poly": 0.795,
        "eta_t_poly": 0.85,
        "eta_burner": 0.955,
        "pi_burner": 0.945,
        "eta_ab": 0.68,
        "pi_ab_dry": 0.985,
        "pi_ab_wet": 0.92,
        "specific_weight_factor": 0.89,
        "mtbf_factor": 0.6,
        "length_factor": 0.98,
        "diameter_factor": 0.98,
        "cumulative_test_hours": 1000.0
      },
      "historical_reference": {
        "sls_dry_thrust_N": 26466.9,
        "sls_ab_thrust_N": 33120.0,
        "sls_dry_tsfc_kg_per_Ns": 3.08747e-05,
        "sls_ab_tsfc_kg_per_Ns": 7.22299e-05,
        "mass_kg": 1024.0,
        "diameter_m": 1.273,
        "length_m": 3.96,
        "unit_cost_usd": 28000.0,
        "tbo_hours_service": 150.0,
        "sources": [
          "LeteckeMotory.cz: VK-1F Official Technical Manual",
          "Gunston, World Encyclopaedia of Aero Engines (1989)"
        ]
      }
    }
  },
  "programs": [
    {
      "schema_version": 1,
      "id": "usaf_aw_int_1945",
      "name_key": "program.usaf_aw_int_1945.name",
      "program_name": "1945 USAAF All-Weather Interceptor (MX-785)",
      "customer": "USAF",
      "role": "interceptor",
      "mvp_core": true,
      "issue_date": "1945-08-28",
      "proposal_due": "1946-03-15",
      "first_flight_due": "1948-09-01",
      "ioc_due": "1950-09-01",
      "equipment": {
        "carrier_capable": false,
        "radar_required": true,
        "min_crew": 2,
        "min_engines": 2,
        "internal_bay_required": false,
        "min_guns_20mm": 4,
        "missile_capability": []
      },
      "criteria": [
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 0.78,
          "objective_value": 0.88,
          "weight": 0.35,
          "unit": "mach",
          "description": "Max speed >= 525 mph (M0.78) threshold, 600+ mph (M0.88) objective"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 15.24,
          "objective_value": 35.56,
          "weight": 0.3,
          "unit": "mps",
          "description": "Rate of climb (3,000 ft/min threshold, 7,000 ft/min objective)"
        },
        {
          "key": "service_ceiling_m",
          "kind": "objective",
          "op": ">=",
          "value": 10972.8,
          "objective_value": 14630.4,
          "weight": 0.2,
          "unit": "m",
          "description": "Service ceiling (36,000 ft threshold, 48,000 ft objective)"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 666720.0,
          "objective_value": 926000.0,
          "weight": 0.15,
          "unit": "m",
          "description": "All-weather intercept radius (360-500 nmi)"
        }
      ],
      "budget": {
        "dev_usd": 14000000.0,
        "unit_price_ceiling_usd": 1150000.0,
        "quantity_planned": 450
      },
      "acquisition": {
        "style": "flyoff",
        "downselect_count": 2,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 5,
        "urgency": 0.7
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.45,
          "cost": 0.2,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "northrop": 0.45,
          "curtiss_wright": 0.35,
          "douglas": 0.2,
          "convair": 0.15
        },
        "congressional_interest": 0.4,
        "industrial_base_need": {
          "northrop": 0.4,
          "curtiss_wright": 0.5
        }
      },
      "historical": {
        "winner_company_id": "northrop",
        "winner_design_name": "N-24 (XP-89 / F-89 Scorpion)",
        "award_date": "1948-10-14",
        "outcome": "produced",
        "production_delivered": 1050,
        "notes": "Northrop N-24 (XP-89) and Curtiss Model 29A (XP-87) were built for fly-off. In Oct 1948 the board selected Northrop F-89 over the overweight 4-engine Curtiss XF-87, forcing Curtiss-Wright to exit aviation manufacturing.",
        "citations": [
          "https://en.wikipedia.org/wiki/Northrop_F-89_Scorpion",
          "https://en.wikipedia.org/wiki/Curtiss_XF-87_Blackhawk",
          "https://www.nationalmuseum.af.mil/Visit/Museum-Exhibits/Fact-Sheets/Display/Article/195815/northrop-f-89-scorpion/"
        ],
        "competitors": [
          {
            "company_id": "northrop",
            "design_name": "N-24 (XP-89 Scorpion)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1948-08-16",
            "unit_price_bid_usd": 980000.0,
            "dev_cost_bid_usd": 10500000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 2,
              "engines": 2,
              "internal_bay": false,
              "guns_20mm": 6,
              "missile_capability": []
            },
            "reputation_at_bid": 74.0,
            "track_record_at_bid": 0.65,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 0.87,
              "climb_rate_sl_mps": 37.8,
              "service_ceiling_m": 14996.2,
              "combat_radius_m": 707464.0
            },
            "flyoff_flaws_unfixed_severity": 1,
            "published_notes": "636 mph (552 kn) at 10,600 ft, 49,200 ft ceiling, 7,440 ft/min climb, 2x Allison J35."
          },
          {
            "company_id": "curtiss_wright",
            "design_name": "Model 29A (XP-87 Blackhawk)",
            "is_historical_winner": false,
            "built_prototype": true,
            "first_flight_date": "1948-02-15",
            "unit_price_bid_usd": 1080000.0,
            "dev_cost_bid_usd": 11300000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 2,
              "engines": 4,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 52.0,
            "track_record_at_bid": 0.42,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "promised_overrides": {
              "max_mach_alt": 0.84,
              "climb_rate_sl_mps": 29.46,
              "service_ceiling_m": 13106.4
            },
            "anchor_performance": {
              "max_mach_alt": 0.79,
              "climb_rate_sl_mps": 22.86,
              "service_ceiling_m": 12496.8,
              "combat_radius_m": 966744.0
            },
            "flyoff_flaws_unfixed_severity": 3,
            "published_notes": "600 mph (451.5 kn at alt), 41,000 ft ceiling, ~4,500 ft/min climb, 49,687 lb gross, tail buffeting."
          },
          {
            "company_id": "douglas",
            "design_name": "Model 560 (USAF F3D Proposal)",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": "1948-03-23",
            "unit_price_bid_usd": 780000.0,
            "dev_cost_bid_usd": 9500000.0,
            "novelty": {
              "unproven_tech_count": 0,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": true,
              "crew": 2,
              "engines": 2,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 68.0,
            "track_record_at_bid": 0.6,
            "district_weight": 0.5,
            "cross_service_derivative": true,
            "promised_overrides": {
              "max_mach_alt": 0.79,
              "service_ceiling_m": 11582.4
            },
            "anchor_performance": {
              "max_mach_alt": 0.77,
              "climb_rate_sl_mps": 22.86,
              "service_ceiling_m": 11186.2,
              "combat_radius_m": 926000.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Subsonic Navy night fighter adaptation, 565 mph, 36,700 ft ceiling."
          },
          {
            "company_id": "convair",
            "design_name": "Model 7002 (XP-92 Delta Proposal)",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": "1948-09-18",
            "unit_price_bid_usd": 1120000.0,
            "dev_cost_bid_usd": 13500000.0,
            "novelty": {
              "unproven_tech_count": 3,
              "unflown_engine": true,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 60.0,
            "track_record_at_bid": 0.5,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 0.92,
              "climb_rate_sl_mps": 40.64,
              "service_ceiling_m": 13716.0,
              "combat_radius_m": 574120.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Single-seat ramjet/turbojet delta proposal; rejected for all-weather role (single crew/engine), built as XF-92A research aircraft."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": null,
        "follow_on_program_id": "usaf_ws201a_1950",
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usn_night_1945",
      "name_key": "program.usn_night_1945.name",
      "program_name": "1945 BuAer Carrier Night / All-Weather Fighter",
      "customer": "USN",
      "role": "carrier_interceptor",
      "mvp_core": true,
      "issue_date": "1945-10-15",
      "proposal_due": "1946-03-15",
      "first_flight_due": "1948-04-01",
      "ioc_due": "1950-10-01",
      "equipment": {
        "carrier_capable": true,
        "radar_required": true,
        "min_crew": 2,
        "min_engines": 2,
        "internal_bay_required": false,
        "min_guns_20mm": 4,
        "missile_capability": []
      },
      "criteria": [
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 777840.0,
          "objective_value": 963040.0,
          "weight": 0.3,
          "unit": "m",
          "description": "Over-water night patrol radius (420 nmi threshold, 520 nmi objective)"
        },
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 0.68,
          "objective_value": 0.78,
          "weight": 0.25,
          "unit": "mach",
          "description": "Maximum level Mach at altitude (430-490 kt)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 14.22,
          "objective_value": 21.34,
          "weight": 0.2,
          "unit": "mps",
          "description": "Initial climb rate (2,800-4,200 ft/min)"
        },
        {
          "key": "stall_speed_mps",
          "kind": "objective",
          "op": "<=",
          "value": 45.27,
          "objective_value": 40.13,
          "weight": 0.25,
          "unit": "mps",
          "description": "Essex-class night carrier approach/stall speed (<= 88 kt)"
        },
        {
          "key": "carrier_suitability",
          "kind": "threshold",
          "op": ">=",
          "value": 1.0,
          "weight": 0.0,
          "unit": "bool",
          "description": "Straight-deck Essex carrier suitability"
        }
      ],
      "budget": {
        "dev_usd": 8500000.0,
        "unit_price_ceiling_usd": 500000.0,
        "quantity_planned": 250
      },
      "acquisition": {
        "style": "paper_award",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 3,
        "allow_dual_award": false,
        "production_lots": 4,
        "urgency": 0.6
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.45,
          "cost": 0.2,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "grumman": 0.4,
          "douglas": 0.35,
          "curtiss_wright": 0.15
        },
        "congressional_interest": 0.3,
        "industrial_base_need": {
          "douglas": 0.3,
          "grumman": 0.3
        }
      },
      "historical": {
        "winner_company_id": "douglas",
        "winner_design_name": "Model 548 (XF3D-1 Skyknight)",
        "award_date": "1946-04-03",
        "outcome": "produced",
        "production_delivered": 268,
        "notes": "Ed Heinemann's Douglas Model 548 won on April 3, 1946 with a clean twin-J34 layout, side-by-side cockpit for APQ-35 radar, and ventral escape chute, beating Grumman's heavy 4-engine G-75.",
        "citations": [
          "https://en.wikipedia.org/wiki/Douglas_F3D_Skyknight",
          "https://thanlont.blogspot.com/2011/12/grumman-comes-from-behind-to-win.html"
        ],
        "competitors": [
          {
            "company_id": "douglas",
            "design_name": "Model 548 (XF3D-1 Skyknight)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1948-03-23",
            "unit_price_bid_usd": 390000.0,
            "dev_cost_bid_usd": 6800000.0,
            "novelty": {
              "unproven_tech_count": 0,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": true,
              "crew": 2,
              "engines": 2,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 78.0,
            "track_record_at_bid": 0.72,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "combat_radius_m": 926000.0,
              "max_mach_alt": 0.76,
              "climb_rate_sl_mps": 20.32,
              "stall_speed_mps": 41.16,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "460-491 kt, 500 nmi combat radius, 2x Westinghouse J34, $390k unit cost."
          },
          {
            "company_id": "grumman",
            "design_name": "Design 75 (XF9F-1 Four-Jet Night Fighter)",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 475000.0,
            "dev_cost_bid_usd": 8200000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": true,
              "crew": 2,
              "engines": 4,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 82.0,
            "track_record_at_bid": 0.75,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "combat_radius_m": 814880.0,
              "max_mach_alt": 0.69,
              "climb_rate_sl_mps": 15.24,
              "stall_speed_mps": 43.73,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "4x Westinghouse J30 in paired nacelles; excessive weight/drag led to cancellation in Oct 1946 in favor of G-79 Panther."
          },
          {
            "company_id": "curtiss_wright",
            "design_name": "Model 29N (Naval XP-87 Adaptation)",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 620000.0,
            "dev_cost_bid_usd": 9500000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 2,
              "engines": 4,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 50.0,
            "track_record_at_bid": 0.45,
            "district_weight": 0.4,
            "cross_service_derivative": true,
            "anchor_performance": {
              "combat_radius_m": 888960.0,
              "max_mach_alt": 0.74,
              "climb_rate_sl_mps": 15.75,
              "stall_speed_mps": 49.39,
              "carrier_suitability": 0.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Rejected by BuAer as far too large and heavy for Essex-class carrier decks."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": null,
        "follow_on_program_id": "usn_gp_fighter_1949",
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usn_os105_1946",
      "name_key": "program.usn_os105_1946.name",
      "program_name": "OS-105 BuAer Carrier Swept-Wing Day Fighter",
      "customer": "USN",
      "role": "carrier_day_fighter",
      "mvp_core": false,
      "issue_date": "1946-01-15",
      "proposal_due": "1946-05-15",
      "first_flight_due": "1948-10-01",
      "ioc_due": "1951-07-01",
      "equipment": {
        "carrier_capable": true,
        "radar_required": false,
        "min_crew": 1,
        "min_engines": 1,
        "internal_bay_required": false,
        "min_guns_20mm": 4,
        "missile_capability": []
      },
      "criteria": [
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 0.85,
          "objective_value": 0.93,
          "weight": 0.4,
          "unit": "mach",
          "description": "Top speed >= 600 mph (521 kt / M0.85+)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 40.64,
          "objective_value": 63.5,
          "weight": 0.3,
          "unit": "mps",
          "description": "High sea-level climb rate (8,000-12,500 ft/min)"
        },
        {
          "key": "service_ceiling_m",
          "kind": "objective",
          "op": ">=",
          "value": 11887.2,
          "objective_value": 13106.4,
          "weight": 0.15,
          "unit": "m",
          "description": "Service ceiling >= 40,000 ft"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 555600.0,
          "objective_value": 740800.0,
          "weight": 0.15,
          "unit": "m",
          "description": "Combat radius (300-400 nmi)"
        },
        {
          "key": "carrier_suitability",
          "kind": "threshold",
          "op": ">=",
          "value": 1.0,
          "weight": 0.0,
          "unit": "bool",
          "description": "Carrier deck suitability"
        }
      ],
      "budget": {
        "dev_usd": 11000000.0,
        "unit_price_ceiling_usd": 800000.0,
        "quantity_planned": 300
      },
      "acquisition": {
        "style": "paper_award",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 3,
        "allow_dual_award": false,
        "production_lots": 4,
        "urgency": 0.55
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.5,
          "cost": 0.15,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "vought": 0.45,
          "north_american": 0.2,
          "curtiss_wright": 0.15
        },
        "congressional_interest": 0.35,
        "industrial_base_need": {
          "vought": 0.45
        }
      },
      "historical": {
        "winner_company_id": "vought",
        "winner_design_name": "V-346 (XF7U-1 Cutlass)",
        "award_date": "1946-06-25",
        "outcome": "produced",
        "production_delivered": 320,
        "notes": "Vought V-346 won OS-105 in June 1946 based on German Arado tailless swept-wing research promising >600 mph and 13,000 ft/min climb.",
        "citations": [
          "https://en.wikipedia.org/wiki/Vought_F7U_Cutlass",
          "https://thanlont.blogspot.com/2011/04/bell-l-39-wing-sweep-evaluation.html"
        ],
        "competitors": [
          {
            "company_id": "vought",
            "design_name": "V-346 (XF7U-1 Cutlass)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1948-09-29",
            "unit_price_bid_usd": 650000.0,
            "dev_cost_bid_usd": 9200000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": false,
              "crew": 1,
              "engines": 2,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 78.0,
            "track_record_at_bid": 0.7,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 0.92,
              "climb_rate_sl_mps": 66.04,
              "service_ceiling_m": 12192.0,
              "combat_radius_m": 648200.0,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 3,
            "published_notes": "606 kt (M0.92), 13,000 ft/min climb, 40,000 ft ceiling, 350 nmi radius."
          },
          {
            "company_id": "north_american",
            "design_name": "NA-140 Naval Swept Study",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 690000.0,
            "dev_cost_bid_usd": 9800000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": false,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 66.0,
            "track_record_at_bid": 0.6,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 0.87,
              "climb_rate_sl_mps": 44.7,
              "service_ceiling_m": 12192.0,
              "combat_radius_m": 611160.0,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Single-J35 swept-wing study; lower climb rate than twin-AB Vought V-346."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": null,
        "follow_on_program_id": "usn_os130_1952",
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usaf_pen_fighter_1946",
      "name_key": "program.usaf_pen_fighter_1946.name",
      "program_name": "1946 USAAF Long-Range Penetration Fighter & 1950 Fly-Off",
      "customer": "USAF",
      "role": "escort_fighter",
      "mvp_core": true,
      "issue_date": "1946-02-15",
      "proposal_due": "1946-06-15",
      "first_flight_due": "1949-06-01",
      "ioc_due": "1951-06-01",
      "equipment": {
        "carrier_capable": false,
        "radar_required": false,
        "min_crew": 1,
        "min_engines": 1,
        "internal_bay_required": false,
        "min_guns_20mm": 6,
        "missile_capability": []
      },
      "criteria": [
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 1203800.0,
          "objective_value": 1481600.0,
          "weight": 0.35,
          "unit": "m",
          "description": "Long-range bomber escort radius (650-800 nmi)"
        },
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 0.88,
          "objective_value": 0.98,
          "weight": 0.3,
          "unit": "mach",
          "description": "High-subsonic / transonic level speed (600-706 mph)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 27.94,
          "objective_value": 45.72,
          "weight": 0.2,
          "unit": "mps",
          "description": "Initial rate of climb (5,500-9,000 ft/min)"
        },
        {
          "key": "service_ceiling_m",
          "kind": "objective",
          "op": ">=",
          "value": 11734.8,
          "objective_value": 13716.0,
          "weight": 0.15,
          "unit": "m",
          "description": "Service ceiling (38,500-45,000 ft)"
        }
      ],
      "budget": {
        "dev_usd": 12000000.0,
        "unit_price_ceiling_usd": 850000.0,
        "quantity_planned": 150
      },
      "acquisition": {
        "style": "flyoff",
        "downselect_count": 3,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 3,
        "urgency": 0.45
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.45,
          "cost": 0.2,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "mcdonnell": 0.35,
          "north_american": 0.3,
          "lockheed": 0.25
        },
        "congressional_interest": 0.35,
        "industrial_base_need": {
          "mcdonnell": 0.5,
          "lockheed": 0.2,
          "north_american": 0.1
        }
      },
      "historical": {
        "winner_company_id": "mcdonnell",
        "winner_design_name": "Model 36 (XF-88A Voodoo)",
        "award_date": "1950-08-25",
        "outcome": "cancelled_after_flyoff",
        "production_delivered": 2,
        "notes": "McDonnell XF-88A won the August 1950 Edwards AFB fly-off over Lockheed XF-90A (overweight/underpowered) and North American YF-93A (NACA flush inlet stall & shorter range). Program was cancelled immediately due to Korean War budget reallocation and SAC B-47 doctrine, then revived in Jan 1951 as GOR 101 (F-101 Voodoo).",
        "citations": [
          "https://en.wikipedia.org/wiki/McDonnell_XF-88_Voodoo",
          "https://en.wikipedia.org/wiki/Lockheed_XF-90",
          "https://en.wikipedia.org/wiki/North_American_YF-93"
        ],
        "competitors": [
          {
            "company_id": "mcdonnell",
            "design_name": "Model 36 (XF-88A Voodoo)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1948-10-20",
            "unit_price_bid_usd": 640000.0,
            "dev_cost_bid_usd": 6600000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": false,
              "crew": 1,
              "engines": 2,
              "internal_bay": false,
              "guns_20mm": 6,
              "missile_capability": []
            },
            "reputation_at_bid": 70.0,
            "track_record_at_bid": 0.65,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "combat_radius_m": 1398260.0,
              "max_mach_alt": 0.96,
              "climb_rate_sl_mps": 40.64,
              "service_ceiling_m": 12009.1
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "706 mph (613 kn), 8,000 ft/min climb, 1,509 nmi range (755 nmi radius), 12,140 lb empty, $6.6M R&D."
          },
          {
            "company_id": "lockheed",
            "design_name": "Model 90 (XF-90A)",
            "is_historical_winner": false,
            "built_prototype": true,
            "first_flight_date": "1949-06-03",
            "unit_price_bid_usd": 740000.0,
            "dev_cost_bid_usd": 5100000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": false,
              "crew": 1,
              "engines": 2,
              "internal_bay": false,
              "guns_20mm": 6,
              "missile_capability": []
            },
            "reputation_at_bid": 75.0,
            "track_record_at_bid": 0.6,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "promised_overrides": {
              "max_mach_alt": 0.95,
              "climb_rate_sl_mps": 39.62,
              "service_ceiling_m": 12496.8
            },
            "anchor_performance": {
              "combat_radius_m": 1518640.0,
              "max_mach_alt": 0.89,
              "climb_rate_sl_mps": 28.22,
              "service_ceiling_m": 11887.2
            },
            "flyoff_flaws_unfixed_severity": 3,
            "published_notes": "Severely overweight (18,050 lb empty, 31,060 lb MTOW) due to 75ST structure; needed RATO to take off with full fuel; 5,555 ft/min climb."
          },
          {
            "company_id": "north_american",
            "design_name": "NA-157 (YF-93A)",
            "is_historical_winner": false,
            "built_prototype": true,
            "first_flight_date": "1950-01-25",
            "unit_price_bid_usd": 790000.0,
            "dev_cost_bid_usd": 11500000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": false,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 6,
              "missile_capability": []
            },
            "reputation_at_bid": 76.0,
            "track_record_at_bid": 0.65,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "promised_overrides": {
              "combat_radius_m": 1407520.0
            },
            "anchor_performance": {
              "combat_radius_m": 1250100.0,
              "max_mach_alt": 0.94,
              "climb_rate_sl_mps": 60.76,
              "service_ceiling_m": 14264.6
            },
            "flyoff_flaws_unfixed_severity": 3,
            "published_notes": "Flush NACA side intakes suffered severe airflow separation at high AoA; shorter combat radius; $11.5M R&D cost."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": null,
        "follow_on_program_id": "usaf_gor101_1951",
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.9
      }
    },
    {
      "schema_version": 1,
      "id": "usn_short_int_1947",
      "name_key": "program.usn_short_int_1947.name",
      "program_name": "1947 BuAer Carrier Point-Defense Interceptor",
      "customer": "USN",
      "role": "carrier_interceptor",
      "mvp_core": false,
      "issue_date": "1947-06-01",
      "proposal_due": "1948-06-01",
      "first_flight_due": "1951-02-01",
      "ioc_due": "1954-06-01",
      "equipment": {
        "carrier_capable": true,
        "radar_required": true,
        "min_crew": 1,
        "min_engines": 1,
        "internal_bay_required": false,
        "min_guns_20mm": 4,
        "missile_capability": []
      },
      "criteria": [
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 71.12,
          "objective_value": 91.44,
          "weight": 0.4,
          "unit": "mps",
          "description": "Emergency deck-launch climb rate (14,000-18,300 ft/min)"
        },
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 0.92,
          "objective_value": 1.02,
          "weight": 0.3,
          "unit": "mach",
          "description": "Transonic/supersonic intercept speed"
        },
        {
          "key": "service_ceiling_m",
          "kind": "objective",
          "op": ">=",
          "value": 14630.4,
          "objective_value": 16764.0,
          "weight": 0.2,
          "unit": "m",
          "description": "Service ceiling (48,000-55,000 ft)"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 444480.0,
          "objective_value": 592640.0,
          "weight": 0.1,
          "unit": "m",
          "description": "Point-defense intercept radius (240-320 nmi)"
        },
        {
          "key": "carrier_suitability",
          "kind": "threshold",
          "op": ">=",
          "value": 1.0,
          "weight": 0.0,
          "unit": "bool",
          "description": "Carrier deck suitability"
        }
      ],
      "budget": {
        "dev_usd": 18000000.0,
        "unit_price_ceiling_usd": 1200000.0,
        "quantity_planned": 400
      },
      "acquisition": {
        "style": "paper_award",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 4,
        "urgency": 0.65
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.5,
          "cost": 0.15,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "douglas": 0.45,
          "grumman": 0.25
        },
        "congressional_interest": 0.35,
        "industrial_base_need": {
          "douglas": 0.3
        }
      },
      "historical": {
        "winner_company_id": "douglas",
        "winner_design_name": "D-571 (XF4D-1 Skyray)",
        "award_date": "1948-12-16",
        "outcome": "produced",
        "production_delivered": 423,
        "notes": "Ed Heinemann's batwing delta D-571 won prototype contract Dec 16, 1948; re-engined from Westinghouse J40 to P&W J57, setting world speed and time-to-climb records.",
        "citations": [
          "https://en.wikipedia.org/wiki/Douglas_F4D_Skyray"
        ],
        "competitors": [
          {
            "company_id": "douglas",
            "design_name": "D-571 (XF4D-1 Skyray)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1951-01-23",
            "unit_price_bid_usd": 980000.0,
            "dev_cost_bid_usd": 15000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": true,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 82.0,
            "track_record_at_bid": 0.75,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "climb_rate_sl_mps": 92.96,
              "max_mach_alt": 0.98,
              "service_ceiling_m": 16764.0,
              "combat_radius_m": 518560.0,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "627 kt (M0.95 SL, M1.05 dive), 18,300 ft/min climb, 55,000 ft ceiling."
          },
          {
            "company_id": "grumman",
            "design_name": "G-85 Swept Point Interceptor Study",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1050000.0,
            "dev_cost_bid_usd": 16500000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": true,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 78.0,
            "track_record_at_bid": 0.7,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "climb_rate_sl_mps": 73.66,
              "max_mach_alt": 0.93,
              "service_ceiling_m": 14935.2,
              "combat_radius_m": 537080.0,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Higher wing loading than Douglas low-aspect-ratio delta batwing."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": null,
        "follow_on_program_id": null,
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usn_gp_fighter_1949",
      "name_key": "program.usn_gp_fighter_1949.name",
      "program_name": "1949 BuAer Carrier General-Purpose All-Weather Fighter",
      "customer": "USN",
      "role": "carrier_interceptor",
      "mvp_core": false,
      "issue_date": "1949-01-15",
      "proposal_due": "1949-05-01",
      "first_flight_due": "1951-08-15",
      "ioc_due": "1955-03-01",
      "equipment": {
        "carrier_capable": true,
        "radar_required": true,
        "min_crew": 1,
        "min_engines": 1,
        "internal_bay_required": false,
        "min_guns_20mm": 4,
        "missile_capability": []
      },
      "criteria": [
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 0.9,
          "objective_value": 0.98,
          "weight": 0.35,
          "unit": "mach",
          "description": "High transonic speed (>600 kt)"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 740800.0,
          "objective_value": 926000.0,
          "weight": 0.3,
          "unit": "m",
          "description": "Fleet defense combat radius (400-500 nmi)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 50.8,
          "objective_value": 71.12,
          "weight": 0.2,
          "unit": "mps",
          "description": "Sea-level climb rate (10,000-14,000 ft/min)"
        },
        {
          "key": "service_ceiling_m",
          "kind": "objective",
          "op": ">=",
          "value": 10668.0,
          "objective_value": 13716.0,
          "weight": 0.15,
          "unit": "m",
          "description": "Service ceiling"
        },
        {
          "key": "carrier_suitability",
          "kind": "threshold",
          "op": ">=",
          "value": 1.0,
          "weight": 0.0,
          "unit": "bool",
          "description": "Carrier deck suitability"
        }
      ],
      "budget": {
        "dev_usd": 22000000.0,
        "unit_price_ceiling_usd": 1350000.0,
        "quantity_planned": 500
      },
      "acquisition": {
        "style": "paper_award",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 5,
        "urgency": 0.65
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.45,
          "cost": 0.2,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "mcdonnell": 0.45,
          "grumman": 0.3,
          "douglas": 0.25
        },
        "congressional_interest": 0.4,
        "industrial_base_need": {
          "mcdonnell": 0.4
        }
      },
      "historical": {
        "winner_company_id": "mcdonnell",
        "winner_design_name": "Model 58 (XF3H-1 Demon)",
        "award_date": "1949-05-21",
        "outcome": "produced",
        "production_delivered": 519,
        "notes": "Six companies submitted 11 designs; McDonnell Model 58 won on May 21, 1949. Plagued by the Westinghouse J40 engine fiasco in F3H-1N, it was re-engined with Allison J71 as F3H-2 with Sparrow III missiles.",
        "citations": [
          "https://en.wikipedia.org/wiki/McDonnell_F3H_Demon",
          "https://thanlont.blogspot.com/2011/03/from-hero-to-zero.html"
        ],
        "competitors": [
          {
            "company_id": "mcdonnell",
            "design_name": "Model 58 (XF3H-1 Demon)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1951-08-07",
            "unit_price_bid_usd": 1150000.0,
            "dev_cost_bid_usd": 18500000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": true,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 80.0,
            "track_record_at_bid": 0.72,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 0.95,
              "combat_radius_m": 926000.0,
              "climb_rate_sl_mps": 65.0,
              "service_ceiling_m": 12801.6,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 2,
            "published_notes": "622 kt (M0.94), 500 nmi radius, 12,795 ft/min climb."
          },
          {
            "company_id": "grumman",
            "design_name": "G-89 Swept Fighter Study",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1220000.0,
            "dev_cost_bid_usd": 19500000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": true,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 76.0,
            "track_record_at_bid": 0.68,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 0.91,
              "combat_radius_m": 796360.0,
              "climb_rate_sl_mps": 56.9,
              "service_ceiling_m": 12344.4,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Smaller internal fuel volume and nose radar bay than McDonnell Model 58."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": "usn_night_1945",
        "follow_on_program_id": "usn_fad_1955",
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usaf_ws201a_1950",
      "name_key": "program.usaf_ws201a_1950.name",
      "program_name": "WS-201A '1954 Ultimate Interceptor' (Project MX-1554)",
      "customer": "USAF",
      "role": "interceptor",
      "mvp_core": true,
      "issue_date": "1950-06-18",
      "proposal_due": "1951-01-31",
      "first_flight_due": "1953-11-01",
      "ioc_due": "1955-12-01",
      "equipment": {
        "carrier_capable": false,
        "radar_required": true,
        "min_crew": 1,
        "min_engines": 1,
        "internal_bay_required": true,
        "min_guns_20mm": 0,
        "missile_capability": [
          "sarh"
        ]
      },
      "criteria": [
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 1.2,
          "objective_value": 1.5,
          "weight": 0.35,
          "unit": "mach",
          "description": "Supersonic level intercept speed (Mach 1.20 threshold, 1.50 objective)"
        },
        {
          "key": "service_ceiling_m",
          "kind": "objective",
          "op": ">=",
          "value": 15240.0,
          "objective_value": 17068.8,
          "weight": 0.25,
          "unit": "m",
          "description": "Combat ceiling >= 50,000 ft (56,000 ft objective)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 60.96,
          "objective_value": 86.36,
          "weight": 0.25,
          "unit": "mps",
          "description": "Initial rate of climb (12,000-17,400 ft/min)"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 592640.0,
          "objective_value": 777840.0,
          "weight": 0.15,
          "unit": "m",
          "description": "GCI/SAGE intercept radius (320-420 nmi)"
        }
      ],
      "budget": {
        "dev_usd": 45000000.0,
        "unit_price_ceiling_usd": 1400000.0,
        "quantity_planned": 750
      },
      "acquisition": {
        "style": "paper_award",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 5,
        "urgency": 0.85
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.45,
          "cost": 0.2,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "convair": 0.45,
          "lockheed": 0.3,
          "republic": 0.25,
          "north_american": 0.2
        },
        "congressional_interest": 0.5,
        "industrial_base_need": {
          "convair": 0.5,
          "lockheed": 0.2,
          "republic": 0.2
        }
      },
      "historical": {
        "winner_company_id": "convair",
        "winner_design_name": "Model 8-80 (YF-102 / F-102A Delta Dagger)",
        "award_date": "1951-09-11",
        "outcome": "produced",
        "production_delivered": 1000,
        "notes": "Six contractors submitted 9 proposals. Convair won WS-201A on its XF-92A delta-wing experience. Early YF-102 prototypes failed to break Mach 1 due to transonic wave drag until redesigned with Whitcomb's Area Rule into the YF-102A (M1.25) and later J75-powered F-106A (M2.3).",
        "citations": [
          "https://en.wikipedia.org/wiki/Convair_F-102_Delta_Dagger",
          "https://en.wikipedia.org/wiki/Convair_F-106_Delta_Dart",
          "https://en.wikipedia.org/wiki/Republic_XF-103"
        ],
        "competitors": [
          {
            "company_id": "convair",
            "design_name": "Model 8-80 (YF-102 / F-102A Delta Dagger)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1953-10-23",
            "unit_price_bid_usd": 1184000.0,
            "dev_cost_bid_usd": 38000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": true,
              "guns_20mm": 0,
              "missile_capability": [
                "sarh"
              ]
            },
            "reputation_at_bid": 78.0,
            "track_record_at_bid": 0.7,
            "district_weight": 0.55,
            "cross_service_derivative": false,
            "promised_overrides": {
              "max_mach_alt": 1.38,
              "service_ceiling_m": 16764.0,
              "climb_rate_sl_mps": 83.82
            },
            "anchor_performance": {
              "max_mach_alt": 1.25,
              "service_ceiling_m": 16276.3,
              "climb_rate_sl_mps": 78.23,
              "combat_radius_m": 616716.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "F-102A achieved M1.25 (825 mph) at 40k ft, 53,400 ft ceiling, 13,000-17,400 ft/min climb, 6x AIM-4 Falcon in internal bay, $1.184M unit cost."
          },
          {
            "company_id": "republic",
            "design_name": "AP-57 (XF-103 Titanium Ramjet/Turbojet)",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1680000.0,
            "dev_cost_bid_usd": 58000000.0,
            "novelty": {
              "unproven_tech_count": 4,
              "unflown_engine": true,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": true,
              "guns_20mm": 0,
              "missile_capability": [
                "sarh"
              ]
            },
            "reputation_at_bid": 72.0,
            "track_record_at_bid": 0.6,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 2.2,
              "service_ceiling_m": 19812.0,
              "climb_rate_sl_mps": 71.12,
              "combat_radius_m": 703760.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Extreme technical/schedule/cost risk (titanium + dual-cycle XJ67/XRJ55); funded only as experimental hedge WS-204A, cancelled at mockup stage after $104M."
          },
          {
            "company_id": "lockheed",
            "design_name": "Model L-205 Interceptor Proposal",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1320000.0,
            "dev_cost_bid_usd": 42000000.0,
            "novelty": {
              "unproven_tech_count": 2,
              "unflown_engine": true,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": true,
              "guns_20mm": 0,
              "missile_capability": [
                "sarh"
              ]
            },
            "reputation_at_bid": 74.0,
            "track_record_at_bid": 0.65,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.28,
              "service_ceiling_m": 15849.6,
              "climb_rate_sl_mps": 72.14,
              "combat_radius_m": 629680.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Selected for Phase I mockup alongside Convair and Republic in July 1951, dropped Sep 1951 in favor of Convair's XF-92A delta experience."
          },
          {
            "company_id": "north_american",
            "design_name": "NA-177 Interceptor Proposal",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1290000.0,
            "dev_cost_bid_usd": 41000000.0,
            "novelty": {
              "unproven_tech_count": 2,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": true,
              "guns_20mm": 0,
              "missile_capability": [
                "sarh"
              ]
            },
            "reputation_at_bid": 75.0,
            "track_record_at_bid": 0.68,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.22,
              "service_ceiling_m": 15392.4,
              "climb_rate_sl_mps": 68.58,
              "combat_radius_m": 611160.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Swept-wing interceptor derivative; lower high-altitude ceiling and internal bay volume than Convair delta."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": "usaf_aw_int_1945",
        "follow_on_program_id": "usaf_ws202a_1955",
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usaf_sabre45_1951",
      "name_key": "program.usaf_sabre45_1951.name",
      "program_name": "1951 USAF Supersonic Day Fighter (Sabre 45 / GOR 1951)",
      "customer": "USAF",
      "role": "day_fighter",
      "mvp_core": false,
      "issue_date": "1951-01-15",
      "proposal_due": "1951-10-01",
      "first_flight_due": "1953-06-01",
      "ioc_due": "1954-09-01",
      "equipment": {
        "carrier_capable": false,
        "radar_required": false,
        "min_crew": 1,
        "min_engines": 1,
        "internal_bay_required": false,
        "min_guns_20mm": 4,
        "missile_capability": []
      },
      "criteria": [
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 1.1,
          "objective_value": 1.3,
          "weight": 0.35,
          "unit": "mach",
          "description": "Level flight supersonic speed (Mach 1.15-1.30)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 71.12,
          "objective_value": 101.6,
          "weight": 0.3,
          "unit": "mps",
          "description": "Rate of climb (14,000-20,000 ft/min)"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 648200.0,
          "objective_value": 888960.0,
          "weight": 0.2,
          "unit": "m",
          "description": "Day fighter combat radius (350-480 nmi)"
        },
        {
          "key": "service_ceiling_m",
          "kind": "objective",
          "op": ">=",
          "value": 13411.2,
          "objective_value": 15240.0,
          "weight": 0.15,
          "unit": "m",
          "description": "Service ceiling (44,000-50,000 ft)"
        }
      ],
      "budget": {
        "dev_usd": 30000000.0,
        "unit_price_ceiling_usd": 1200000.0,
        "quantity_planned": 800
      },
      "acquisition": {
        "style": "sole_source",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 5,
        "urgency": 0.9
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.45,
          "cost": 0.2,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "north_american": 0.65,
          "republic": 0.25
        },
        "congressional_interest": 0.45,
        "industrial_base_need": {
          "north_american": 0.35
        }
      },
      "historical": {
        "winner_company_id": "north_american",
        "winner_design_name": "NA-180 (YF-100A / F-100 Super Sabre)",
        "award_date": "1951-11-30",
        "outcome": "produced",
        "production_delivered": 2294,
        "notes": "Unsolicited 'Sabre 45' proposal submitted Jan 1951 during Korean War MiG-15 urgency; awarded sole-source under Cook-Craigie Plan. Suffered fatal yaw-roll inertia coupling in 1954 until tail area was enlarged 27%.",
        "citations": [
          "https://en.wikipedia.org/wiki/North_American_F-100_Super_Sabre",
          "https://www.nationalmuseum.af.mil/Visit/Museum-Exhibits/Fact-Sheets/Display/Article/195828/north-american-f-100a-super-sabre/"
        ],
        "competitors": [
          {
            "company_id": "north_american",
            "design_name": "NA-180 (YF-100A Super Sabre)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1953-05-25",
            "unit_price_bid_usd": 920000.0,
            "dev_cost_bid_usd": 24000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": false,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 90.0,
            "track_record_at_bid": 0.85,
            "district_weight": 0.55,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.25,
              "climb_rate_sl_mps": 96.52,
              "combat_radius_m": 814880.0,
              "service_ceiling_m": 14051.3
            },
            "flyoff_flaws_unfixed_severity": 3,
            "published_notes": "M1.15-1.30, 14,800-22,400 ft/min climb, P&W J57, 4x 20mm M39 cannon."
          },
          {
            "company_id": "republic",
            "design_name": "AP-50 Advanced Swept F-84J Study",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 980000.0,
            "dev_cost_bid_usd": 25000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": false,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 74.0,
            "track_record_at_bid": 0.65,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.12,
              "climb_rate_sl_mps": 73.66,
              "combat_radius_m": 777840.0,
              "service_ceiling_m": 13411.2
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Transonic/low-supersonic swept F-84 evolution."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": null,
        "follow_on_program_id": "usaf_ws303a_1952",
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usaf_gor101_1951",
      "name_key": "program.usaf_gor101_1951.name",
      "program_name": "GOR 101 Long-Range Strategic Fighter Escort (WS-105A)",
      "customer": "USAF",
      "role": "escort_fighter",
      "mvp_core": false,
      "issue_date": "1951-02-06",
      "proposal_due": "1951-05-15",
      "first_flight_due": "1954-10-01",
      "ioc_due": "1956-10-01",
      "equipment": {
        "carrier_capable": false,
        "radar_required": true,
        "min_crew": 1,
        "min_engines": 2,
        "internal_bay_required": false,
        "min_guns_20mm": 4,
        "missile_capability": []
      },
      "criteria": [
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 1389000.0,
          "objective_value": 1666800.0,
          "weight": 0.35,
          "unit": "m",
          "description": "Long unrefueled strategic escort radius (750-900 nmi)"
        },
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 1.35,
          "objective_value": 1.6,
          "weight": 0.3,
          "unit": "mach",
          "description": "Supersonic speed (Mach 1.35-1.60)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 111.76,
          "objective_value": 177.8,
          "weight": 0.2,
          "unit": "mps",
          "description": "Rate of climb (22,000-35,000 ft/min)"
        },
        {
          "key": "service_ceiling_m",
          "kind": "objective",
          "op": ">=",
          "value": 14630.4,
          "objective_value": 16764.0,
          "weight": 0.15,
          "unit": "m",
          "description": "Service ceiling (48,000-55,800 ft)"
        }
      ],
      "budget": {
        "dev_usd": 42000000.0,
        "unit_price_ceiling_usd": 2200000.0,
        "quantity_planned": 500
      },
      "acquisition": {
        "style": "paper_award",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 5,
        "urgency": 0.75
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.45,
          "cost": 0.2,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "mcdonnell": 0.55,
          "lockheed": 0.25,
          "north_american": 0.25,
          "northrop": 0.2
        },
        "congressional_interest": 0.4,
        "industrial_base_need": {
          "mcdonnell": 0.45
        }
      },
      "historical": {
        "winner_company_id": "mcdonnell",
        "winner_design_name": "Model 36W (F-101A/B Voodoo)",
        "award_date": "1951-05-31",
        "outcome": "produced",
        "production_delivered": 705,
        "notes": "Revival of the 1946 Penetration Fighter requirement under SAC GOR 101. McDonnell scaled the winning XF-88 around two P&W J57 engines, beating derivatives of the F-90, F-93, F-89, and F-84F.",
        "citations": [
          "https://en.wikipedia.org/wiki/McDonnell_F-101_Voodoo",
          "https://www.nationalmuseum.af.mil/Visit/Museum-Exhibits/Fact-Sheets/Display/Article/195832/mcdonnell-f-101a-voodoo/"
        ],
        "competitors": [
          {
            "company_id": "mcdonnell",
            "design_name": "Model 36W (F-101A Voodoo)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1954-09-29",
            "unit_price_bid_usd": 1754000.0,
            "dev_cost_bid_usd": 34000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 2,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": [
                "sarh"
              ]
            },
            "reputation_at_bid": 80.0,
            "track_record_at_bid": 0.75,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "combat_radius_m": 1611240.0,
              "max_mach_alt": 1.56,
              "climb_rate_sl_mps": 185.42,
              "service_ceiling_m": 17007.8
            },
            "flyoff_flaws_unfixed_severity": 2,
            "published_notes": "M1.52-1.66 (1,009-1,093 mph), 870 nmi combat radius, 36,500 ft/min climb, 55,800 ft ceiling, 2x P&W J57."
          },
          {
            "company_id": "lockheed",
            "design_name": "Model 90D (J57 XF-90 Derivative)",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1920000.0,
            "dev_cost_bid_usd": 37000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 2,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 74.0,
            "track_record_at_bid": 0.62,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "combat_radius_m": 1500120.0,
              "max_mach_alt": 1.38,
              "climb_rate_sl_mps": 121.92,
              "service_ceiling_m": 15240.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Enlarged XF-90 derivative; penalized by XF-90A's structural weight history."
          },
          {
            "company_id": "northrop",
            "design_name": "N-68 Advanced Swept F-89E Escort",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1850000.0,
            "dev_cost_bid_usd": 35000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 2,
              "engines": 2,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": []
            },
            "reputation_at_bid": 72.0,
            "track_record_at_bid": 0.65,
            "district_weight": 0.48,
            "cross_service_derivative": false,
            "promised_overrides": {
              "max_mach_alt": 1.35
            },
            "anchor_performance": {
              "combat_radius_m": 1444560.0,
              "max_mach_alt": 1.25,
              "climb_rate_sl_mps": 114.3,
              "service_ceiling_m": 15544.8
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Swept-wing F-89 derivative; slower than McDonnell Model 36W."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": "usaf_pen_fighter_1946",
        "follow_on_program_id": null,
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usaf_ws306a_1952",
      "name_key": "program.usaf_ws306a_1952.name",
      "program_name": "WS-306A Supersonic Tactical Nuclear Strike Fighter",
      "customer": "USAF",
      "role": "fighter_bomber",
      "mvp_core": false,
      "issue_date": "1952-04-15",
      "proposal_due": "1952-09-01",
      "first_flight_due": "1955-10-15",
      "ioc_due": "1958-05-01",
      "equipment": {
        "carrier_capable": false,
        "radar_required": true,
        "min_crew": 1,
        "min_engines": 1,
        "internal_bay_required": true,
        "min_guns_20mm": 1,
        "missile_capability": [
          "ir"
        ]
      },
      "criteria": [
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 1.75,
          "objective_value": 2.05,
          "weight": 0.3,
          "unit": "mach",
          "description": "Mach 2.0 altitude speed & Mach 1.1+ sea-level nuclear dash"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 926000.0,
          "objective_value": 1250100.0,
          "weight": 0.3,
          "unit": "m",
          "description": "Hi-lo-hi nuclear strike radius (500-676 nmi)"
        },
        {
          "key": "payload_kg",
          "kind": "objective",
          "op": ">=",
          "value": 3628.7,
          "objective_value": 6350.3,
          "weight": 0.25,
          "unit": "kg",
          "description": "Internal nuclear bay + external ordnance payload (8,000-14,000 lb)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 127.0,
          "objective_value": 195.58,
          "weight": 0.15,
          "unit": "mps",
          "description": "Rate of climb (25,000-38,500 ft/min)"
        }
      ],
      "budget": {
        "dev_usd": 52000000.0,
        "unit_price_ceiling_usd": 2400000.0,
        "quantity_planned": 600
      },
      "acquisition": {
        "style": "sole_source",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 5,
        "urgency": 0.7
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.45,
          "cost": 0.2,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "republic": 0.65,
          "north_american": 0.25
        },
        "congressional_interest": 0.45,
        "industrial_base_need": {
          "republic": 0.45
        }
      },
      "historical": {
        "winner_company_id": "republic",
        "winner_design_name": "AP-63-31 (YF-105A / F-105D Thunderchief)",
        "award_date": "1952-09-15",
        "outcome": "produced",
        "production_delivered": 833,
        "notes": "Republic's unsolicited AP-63 successor to the F-84F with an internal thermonuclear bomb bay, P&W J75 engine, and M61 Vulcan cannon.",
        "citations": [
          "https://en.wikipedia.org/wiki/Republic_F-105_Thunderchief",
          "https://www.nationalmuseum.af.mil/Visit/Museum-Exhibits/Fact-Sheets/Display/Article/195844/republic-f-105d-thunderchief/"
        ],
        "competitors": [
          {
            "company_id": "republic",
            "design_name": "AP-63-31 (F-105 Thunderchief)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1955-10-22",
            "unit_price_bid_usd": 2137000.0,
            "dev_cost_bid_usd": 46000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": true,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": true,
              "guns_20mm": 1,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 84.0,
            "track_record_at_bid": 0.76,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 2.08,
              "combat_radius_m": 1251952.0,
              "payload_kg": 6350.3,
              "climb_rate_sl_mps": 195.58
            },
            "flyoff_flaws_unfixed_severity": 1,
            "published_notes": "M2.08 (1,372 mph) at 36k ft, M1.13 at SL, 676 nmi hi-lo-hi radius, 14,000 lb ordnance, P&W J75."
          },
          {
            "company_id": "north_american",
            "design_name": "NA-195 Fighter-Bomber Study",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 2050000.0,
            "dev_cost_bid_usd": 44000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": true,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": true,
              "guns_20mm": 4,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 82.0,
            "track_record_at_bid": 0.75,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.75,
              "combat_radius_m": 981560.0,
              "payload_kg": 4082.3,
              "climb_rate_sl_mps": 147.32
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Enlarged F-100 strike concept; smaller internal bay and lower SL dash speed than Republic AP-63."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": null,
        "follow_on_program_id": null,
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usn_os130_1952",
      "name_key": "program.usn_os130_1952.name",
      "program_name": "OS-130 BuAer Carrier Supersonic Day Fighter",
      "customer": "USN",
      "role": "carrier_day_fighter",
      "mvp_core": true,
      "issue_date": "1952-09-15",
      "proposal_due": "1953-01-15",
      "first_flight_due": "1955-04-01",
      "ioc_due": "1957-03-01",
      "equipment": {
        "carrier_capable": true,
        "radar_required": false,
        "min_crew": 1,
        "min_engines": 1,
        "internal_bay_required": false,
        "min_guns_20mm": 4,
        "missile_capability": [
          "ir"
        ]
      },
      "criteria": [
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 1.2,
          "objective_value": 1.55,
          "weight": 0.3,
          "unit": "mach",
          "description": "Level flight supersonic speed at 30,000-35,000 ft (Mach 1.20 threshold, 1.55 objective)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 101.6,
          "objective_value": 134.62,
          "weight": 0.25,
          "unit": "mps",
          "description": "Sea-level initial rate of climb (20,000-26,500 ft/min)"
        },
        {
          "key": "service_ceiling_m",
          "kind": "objective",
          "op": ">=",
          "value": 15240.0,
          "objective_value": 16764.0,
          "weight": 0.15,
          "unit": "m",
          "description": "Service ceiling (50,000-55,000 ft)"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 555600.0,
          "objective_value": 740800.0,
          "weight": 0.15,
          "unit": "m",
          "description": "Combat radius on internal fuel (300-400 nmi)"
        },
        {
          "key": "stall_speed_mps",
          "kind": "objective",
          "op": "<=",
          "value": 54.02,
          "objective_value": 48.87,
          "weight": 0.15,
          "unit": "mps",
          "description": "Carrier approach/stall speed (<= 100-105 kt)"
        },
        {
          "key": "carrier_suitability",
          "kind": "threshold",
          "op": ">=",
          "value": 1.0,
          "weight": 0.0,
          "unit": "bool",
          "description": "Essex deck spot factor (25 aircraft in aft 200 ft) & carrier suitability"
        }
      ],
      "budget": {
        "dev_usd": 32000000.0,
        "unit_price_ceiling_usd": 1150000.0,
        "quantity_planned": 550
      },
      "acquisition": {
        "style": "paper_award",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 5,
        "urgency": 0.7
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.45,
          "cost": 0.2,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "grumman": 0.35,
          "douglas": 0.3,
          "mcdonnell": 0.25,
          "vought": 0.25,
          "north_american": 0.15,
          "lockheed": 0.05
        },
        "congressional_interest": 0.4,
        "industrial_base_need": {
          "vought": 0.65,
          "grumman": 0.2,
          "douglas": -0.25
        }
      },
      "historical": {
        "winner_company_id": "vought",
        "winner_design_name": "V-383 (XF8U-1 Crusader)",
        "award_date": "1953-05-29",
        "outcome": "produced",
        "production_delivered": 1261,
        "notes": "Eight companies competed. Vought V-383 won in May 1953 on its brilliant two-position variable-incidence wing (solving carrier approach visibility and sub-100 kt landing speed), Essex deck spot factor compliance, and Mach 1.55+ J57 performance.",
        "citations": [
          "https://en.wikipedia.org/wiki/Vought_F-8_Crusader",
          "https://thanlont.blogspot.com/2017/10/the-first-supersonic-us-navy-fighter.html",
          "https://thanlont.blogspot.com/2010/07/fitting-in-ii.html"
        ],
        "competitors": [
          {
            "company_id": "vought",
            "design_name": "V-383 (XF8U-1 Crusader)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1955-03-25",
            "unit_price_bid_usd": 780000.0,
            "dev_cost_bid_usd": 26000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 72.0,
            "track_record_at_bid": 0.58,
            "district_weight": 0.48,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.55,
              "climb_rate_sl_mps": 127.0,
              "service_ceiling_m": 16306.8,
              "combat_radius_m": 722280.0,
              "stall_speed_mps": 49.9,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "M1.35-1.70 (F8U-1/2), 25,000+ ft/min climb, 51,500-58,000 ft ceiling, 390 nmi radius, variable-incidence wing."
          },
          {
            "company_id": "douglas",
            "design_name": "Model 656 (F5D-1 Skylancer Precursor)",
            "is_historical_winner": false,
            "built_prototype": true,
            "first_flight_date": "1956-04-21",
            "unit_price_bid_usd": 1120000.0,
            "dev_cost_bid_usd": 29000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 84.0,
            "track_record_at_bid": 0.78,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.35,
              "climb_rate_sl_mps": 105.31,
              "service_ceiling_m": 17526.0,
              "combat_radius_m": 648200.0,
              "stall_speed_mps": 52.99,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Thin-wing F4D evolution (F5D Skylancer); slower than V-383, higher AoA over-nose visibility limitation, and Douglas already held AD/A3D/A4D/F4D contracts."
          },
          {
            "company_id": "grumman",
            "design_name": "Design 98 (F9F-9 / F11F-1 Tiger)",
            "is_historical_winner": false,
            "built_prototype": true,
            "first_flight_date": "1954-07-30",
            "unit_price_bid_usd": 980000.0,
            "dev_cost_bid_usd": 22000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": true,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": false,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 80.0,
            "track_record_at_bid": 0.72,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "promised_overrides": {
              "max_mach_alt": 1.22,
              "combat_radius_m": 555600.0
            },
            "anchor_performance": {
              "max_mach_alt": 1.1,
              "climb_rate_sl_mps": 82.8,
              "service_ceiling_m": 14935.2,
              "combat_radius_m": 463000.0,
              "stall_speed_mps": 50.42,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 2,
            "published_notes": "Wright J65 engine lacked thrust; tight area-ruled fuselage left only 250 nmi combat radius and Mach 1.10 speed."
          },
          {
            "company_id": "north_american",
            "design_name": "NA-208 (Super Fury Naval F-100)",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1020000.0,
            "dev_cost_bid_usd": 27000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": false,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 72.0,
            "track_record_at_bid": 0.68,
            "district_weight": 0.5,
            "cross_service_derivative": true,
            "anchor_performance": {
              "max_mach_alt": 1.32,
              "climb_rate_sl_mps": 111.76,
              "service_ceiling_m": 15240.0,
              "combat_radius_m": 648200.0,
              "stall_speed_mps": 53.5,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Navalized F-100 Super Sabre; penalized by high approach speed and cross-service origin."
          },
          {
            "company_id": "lockheed",
            "design_name": "Model L-242 (Naval Starfighter)",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1050000.0,
            "dev_cost_bid_usd": 28000000.0,
            "novelty": {
              "unproven_tech_count": 2,
              "unflown_engine": true,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": false,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 1,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 62.0,
            "track_record_at_bid": 0.6,
            "district_weight": 0.5,
            "cross_service_derivative": true,
            "anchor_performance": {
              "max_mach_alt": 1.85,
              "climb_rate_sl_mps": 152.4,
              "service_ceiling_m": 16764.0,
              "combat_radius_m": 555600.0,
              "stall_speed_mps": 59.16,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Carrier L-246 derivative; failed 4x20mm gun gate and sub-105 kt carrier stall speed."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": "usn_os105_1946",
        "follow_on_program_id": "usn_fad_1955",
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usaf_ws303a_1952",
      "name_key": "program.usaf_ws303a_1952.name",
      "program_name": "WS-303A Lightweight Air-Superiority Day Fighter (GOR Dec 1952)",
      "customer": "USAF",
      "role": "day_fighter",
      "mvp_core": true,
      "issue_date": "1952-12-12",
      "proposal_due": "1953-01-31",
      "first_flight_due": "1954-06-01",
      "ioc_due": "1957-06-01",
      "equipment": {
        "carrier_capable": false,
        "radar_required": false,
        "min_crew": 1,
        "min_engines": 1,
        "internal_bay_required": false,
        "min_guns_20mm": 1,
        "missile_capability": [
          "ir"
        ]
      },
      "criteria": [
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 1.8,
          "objective_value": 2.2,
          "weight": 0.35,
          "unit": "mach",
          "description": "Mach 2.0+ speed at 40,000 ft (Mach 1.80 threshold, 2.20 objective)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 177.8,
          "objective_value": 243.84,
          "weight": 0.3,
          "unit": "mps",
          "description": "Extraordinary climb rate (35,000-48,000 ft/min)"
        },
        {
          "key": "service_ceiling_m",
          "kind": "objective",
          "op": ">=",
          "value": 16459.2,
          "objective_value": 17678.4,
          "weight": 0.2,
          "unit": "m",
          "description": "Service ceiling (54,000-58,000 ft, >80,000 ft zoom)"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 611160.0,
          "objective_value": 777840.0,
          "weight": 0.15,
          "unit": "m",
          "description": "Day air-superiority combat radius (330-420 nmi)"
        }
      ],
      "budget": {
        "dev_usd": 35000000.0,
        "unit_price_ceiling_usd": 1400000.0,
        "quantity_planned": 300
      },
      "acquisition": {
        "style": "paper_award",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 4,
        "urgency": 0.8
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.5,
          "cost": 0.2,
          "sched": 0.15,
          "risk": 0.15
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "lockheed": 0.45,
          "north_american": 0.25,
          "republic": 0.2,
          "northrop": 0.2
        },
        "congressional_interest": 0.4,
        "industrial_base_need": {
          "lockheed": 0.55,
          "northrop": 0.3,
          "north_american": -0.25,
          "republic": -0.25
        }
      },
      "historical": {
        "winner_company_id": "lockheed",
        "winner_design_name": "Model L-246 (XF-104 Starfighter)",
        "award_date": "1953-03-11",
        "outcome": "produced",
        "production_delivered": 296,
        "notes": "Originated from Kelly Johnson's Nov 1952 unsolicited L-246 proposal after interviewing Korean War pilots. Lockheed won over Northrop N-102 Fang, Republic AP-55, and NAA NA-212 on unmatched Mach 2.2 / 48,000 ft/min performance and USAF's desire to prevent NAA and Republic from monopolizing fighter production (Knaack, p. 175).",
        "citations": [
          "https://en.wikipedia.org/wiki/Lockheed_F-104_Starfighter",
          "https://en.wikipedia.org/wiki/Northrop_N-102_Fang",
          "https://www.nationalmuseum.af.mil/Visit/Museum-Exhibits/Fact-Sheets/Display/Article/195837/lockheed-f-104a-starfighter/"
        ],
        "competitors": [
          {
            "company_id": "lockheed",
            "design_name": "Model L-246 (XF-104 Starfighter)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1954-03-04",
            "unit_price_bid_usd": 1006000.0,
            "dev_cost_bid_usd": 27000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": true,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 1,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 84.0,
            "track_record_at_bid": 0.78,
            "district_weight": 0.55,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 2.2,
              "climb_rate_sl_mps": 243.84,
              "service_ceiling_m": 17678.4,
              "combat_radius_m": 675980.0
            },
            "flyoff_flaws_unfixed_severity": 1,
            "published_notes": "1,450 mph (M2.2), 48,000 ft/min climb, 58,000 ft ceiling, GE J79 + M61 Vulcan, flew March 1954 on interim J65."
          },
          {
            "company_id": "northrop",
            "design_name": "N-102 Fang",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1080000.0,
            "dev_cost_bid_usd": 29000000.0,
            "novelty": {
              "unproven_tech_count": 2,
              "unflown_engine": true,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 2,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 70.0,
            "track_record_at_bid": 0.62,
            "district_weight": 0.48,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 2.0,
              "climb_rate_sl_mps": 203.2,
              "service_ceiling_m": 16764.0,
              "combat_radius_m": 703760.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Shoulder-mounted delta wing with ventral chin intake and J79; lower top speed and climb than L-246."
          },
          {
            "company_id": "republic",
            "design_name": "AP-55 Lightweight Day Fighter",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1180000.0,
            "dev_cost_bid_usd": 31000000.0,
            "novelty": {
              "unproven_tech_count": 2,
              "unflown_engine": true,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 2,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 75.0,
            "track_record_at_bid": 0.65,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.95,
              "climb_rate_sl_mps": 193.04,
              "service_ceiling_m": 16764.0,
              "combat_radius_m": 666720.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Republic already held F-84F, XF-103, and F-105 contracts."
          },
          {
            "company_id": "north_american",
            "design_name": "NA-212 Advanced Day Fighter",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1150000.0,
            "dev_cost_bid_usd": 30000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": true,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 2,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 82.0,
            "track_record_at_bid": 0.75,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.9,
              "climb_rate_sl_mps": 190.5,
              "service_ceiling_m": 16611.6,
              "combat_radius_m": 694500.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "NAA already held F-86 and F-100 production."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": "usaf_sabre45_1951",
        "follow_on_program_id": "usaf_gor127_n156_1956",
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usn_f11f_1953",
      "name_key": "program.usn_f11f_1953.name",
      "program_name": "1953 BuAer Lightweight Area-Ruled Carrier Day Fighter (XF9F-9)",
      "customer": "USN",
      "role": "carrier_day_fighter",
      "mvp_core": false,
      "issue_date": "1953-03-01",
      "proposal_due": "1953-04-20",
      "first_flight_due": "1954-08-01",
      "ioc_due": "1956-10-01",
      "equipment": {
        "carrier_capable": true,
        "radar_required": false,
        "min_crew": 1,
        "min_engines": 1,
        "internal_bay_required": false,
        "min_guns_20mm": 4,
        "missile_capability": [
          "ir"
        ]
      },
      "criteria": [
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 1.05,
          "objective_value": 1.2,
          "weight": 0.35,
          "unit": "mach",
          "description": "Transonic/supersonic speed with J65 (Mach 1.05-1.20)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 71.12,
          "objective_value": 91.44,
          "weight": 0.3,
          "unit": "mps",
          "description": "Rate of climb (14,000-18,000 ft/min)"
        },
        {
          "key": "stall_speed_mps",
          "kind": "objective",
          "op": "<=",
          "value": 52.47,
          "objective_value": 48.36,
          "weight": 0.2,
          "unit": "mps",
          "description": "Carrier approach stall speed"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 444480.0,
          "objective_value": 592640.0,
          "weight": 0.15,
          "unit": "m",
          "description": "Day intercept combat radius (240-320 nmi)"
        },
        {
          "key": "carrier_suitability",
          "kind": "threshold",
          "op": ">=",
          "value": 1.0,
          "weight": 0.0,
          "unit": "bool",
          "description": "Carrier deck suitability"
        }
      ],
      "budget": {
        "dev_usd": 18000000.0,
        "unit_price_ceiling_usd": 1150000.0,
        "quantity_planned": 200
      },
      "acquisition": {
        "style": "sole_source",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 3,
        "urgency": 0.5
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.45,
          "cost": 0.2,
          "sched": 0.2,
          "risk": 0.15
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "grumman": 0.6,
          "vought": 0.2
        },
        "congressional_interest": 0.35,
        "industrial_base_need": {
          "grumman": 0.45
        }
      },
      "historical": {
        "winner_company_id": "grumman",
        "winner_design_name": "Design 98 (XF9F-9 / F11F-1 Tiger)",
        "award_date": "1953-04-27",
        "outcome": "produced",
        "production_delivered": 201,
        "notes": "Ordered in April 1953 as a lightweight Whitcomb area-ruled 'Jet Bearcat' hedge under the XF9F-9 Cougar budget cover. Outclassed by the F8U Crusader in range and speed, serving briefly in fleet squadrons before becoming the iconic Blue Angels mount.",
        "citations": [
          "https://en.wikipedia.org/wiki/Grumman_F-11_Tiger",
          "https://tailhooktopics.blogspot.com/2018/01/the-grumman-xf9f-9-too-little-too-soon.html"
        ],
        "competitors": [
          {
            "company_id": "grumman",
            "design_name": "Design 98 (XF9F-9 / F11F-1 Tiger)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1954-07-30",
            "unit_price_bid_usd": 980000.0,
            "dev_cost_bid_usd": 15000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": false,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 84.0,
            "track_record_at_bid": 0.78,
            "district_weight": 0.48,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.12,
              "climb_rate_sl_mps": 82.8,
              "stall_speed_mps": 49.39,
              "combat_radius_m": 472260.0,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 1,
            "published_notes": "631 kt (M1.1) at 35k ft, 16,300 ft/min climb, 250 nmi radius, 1st area-ruled Navy fighter."
          },
          {
            "company_id": "vought",
            "design_name": "V-384 Lightweight J65 Study",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 1020000.0,
            "dev_cost_bid_usd": 16500000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": false,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 70.0,
            "track_record_at_bid": 0.6,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.08,
              "climb_rate_sl_mps": 76.2,
              "stall_speed_mps": 50.42,
              "combat_radius_m": 463000.0,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Vought's smaller Wright J65 alternative to the J57-powered V-383."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": null,
        "follow_on_program_id": null,
        "suppress_if_role_satisfied": true,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usn_fad_1955",
      "name_key": "program.usn_fad_1955.name",
      "program_name": "1955 BuAer Fleet Air Defense Mach 2 Interceptor & 1958 Fly-Off",
      "customer": "USN",
      "role": "carrier_interceptor",
      "mvp_core": true,
      "issue_date": "1955-05-26",
      "proposal_due": "1955-10-15",
      "first_flight_due": "1958-06-15",
      "ioc_due": "1960-12-01",
      "equipment": {
        "carrier_capable": true,
        "radar_required": true,
        "min_crew": 1,
        "min_engines": 1,
        "internal_bay_required": false,
        "min_guns_20mm": 0,
        "missile_capability": [
          "sarh",
          "ir"
        ]
      },
      "criteria": [
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 2.0,
          "objective_value": 2.3,
          "weight": 0.25,
          "unit": "mach",
          "description": "Mach 2.0+ fleet air defense intercept speed (M2.00 threshold, M2.30 objective)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 142.24,
          "objective_value": 208.28,
          "weight": 0.25,
          "unit": "mps",
          "description": "Initial rate of climb (28,000-41,300 ft/min)"
        },
        {
          "key": "payload_kg",
          "kind": "objective",
          "op": ">=",
          "value": 1134.0,
          "objective_value": 3401.9,
          "weight": 0.25,
          "unit": "kg",
          "description": "All-weather missile & multi-mission ordnance load (4x Sparrow III + 4x Sidewinder & growth)"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 648200.0,
          "objective_value": 926000.0,
          "weight": 0.15,
          "unit": "m",
          "description": "CAP / Fleet defense combat radius (350-500 nmi)"
        },
        {
          "key": "service_ceiling_m",
          "kind": "objective",
          "op": ">=",
          "value": 16764.0,
          "objective_value": 18897.6,
          "weight": 0.1,
          "unit": "m",
          "description": "Service ceiling (55,000-62,000 ft)"
        },
        {
          "key": "carrier_suitability",
          "kind": "threshold",
          "op": ">=",
          "value": 1.0,
          "weight": 0.0,
          "unit": "bool",
          "description": "Forrestal/Midway/Essex carrier suitability"
        }
      ],
      "budget": {
        "dev_usd": 65000000.0,
        "unit_price_ceiling_usd": 2400000.0,
        "quantity_planned": 650
      },
      "acquisition": {
        "style": "flyoff",
        "downselect_count": 2,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 5,
        "urgency": 0.85
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.45,
          "cost": 0.2,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "mcdonnell": 0.45,
          "vought": 0.35,
          "grumman": 0.25
        },
        "congressional_interest": 0.45,
        "industrial_base_need": {
          "mcdonnell": 0.4,
          "vought": 0.2
        }
      },
      "historical": {
        "winner_company_id": "mcdonnell",
        "winner_design_name": "Model 98B (XF4H-1 / F-4B Phantom II)",
        "award_date": "1958-12-17",
        "outcome": "produced",
        "production_delivered": 5195,
        "notes": "Legendary 1958 fly-off at Edwards AFB and NAS Patuxent River between McDonnell XF4H-1 Phantom II and Vought XF8U-3 Crusader III. While the single-seat XF8U-3 achieved Mach 2.39, the Navy selected the twin-J79, two-seat (Pilot + RIO), 4-Sparrow XF4H-1 on Dec 17, 1958 for its superior climb, radar workload management, twin-engine safety, and multi-mission payload.",
        "citations": [
          "https://en.wikipedia.org/wiki/McDonnell_Douglas_F-4_Phantom_II",
          "https://en.wikipedia.org/wiki/Vought_XF8U-3_Crusader_III",
          "https://thanlont.blogspot.com/2018/11/birth-of-legend-mcdonnell-f4h-1-phantom.html",
          "https://thanlont.blogspot.com/2019/09/f8u-3-vs-f4h-1-dogfights-at-patuxent.html"
        ],
        "competitors": [
          {
            "company_id": "mcdonnell",
            "design_name": "Model 98B (XF4H-1 Phantom II)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1958-05-27",
            "unit_price_bid_usd": 1900000.0,
            "dev_cost_bid_usd": 52000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": true,
              "crew": 2,
              "engines": 2,
              "internal_bay": false,
              "guns_20mm": 0,
              "missile_capability": [
                "sarh",
                "ir"
              ]
            },
            "reputation_at_bid": 84.0,
            "track_record_at_bid": 0.78,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 2.23,
              "climb_rate_sl_mps": 209.8,
              "payload_kg": 3810.2,
              "combat_radius_m": 796360.0,
              "service_ceiling_m": 18288.0,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "1,280 kt (M2.23), 41,300 ft/min climb, 60,000 ft ceiling, 2-man crew (Pilot+RIO), 4x Sparrow III semi-recessed + 4x Sidewinder (up to 16,000+ lb ordnance), 2x GE J79."
          },
          {
            "company_id": "vought",
            "design_name": "V-401 (XF8U-3 Crusader III)",
            "is_historical_winner": false,
            "built_prototype": true,
            "first_flight_date": "1958-06-02",
            "unit_price_bid_usd": 2250000.0,
            "dev_cost_bid_usd": 56000000.0,
            "novelty": {
              "unproven_tech_count": 2,
              "unflown_engine": false,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 0,
              "missile_capability": [
                "sarh",
                "ir"
              ]
            },
            "reputation_at_bid": 82.0,
            "track_record_at_bid": 0.76,
            "district_weight": 0.48,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 2.39,
              "climb_rate_sl_mps": 165.1,
              "payload_kg": 1451.5,
              "combat_radius_m": 926000.0,
              "service_ceiling_m": 19812.0,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 2,
            "published_notes": "M2.39 at 50,000 ft, 32,500 ft/min climb, 3x Sparrow III; single pilot overloaded by manual APQ-50/Sparrow III radar intercept workload, folding ventral fins."
          },
          {
            "company_id": "grumman",
            "design_name": "Design 98J / G-118 Super Tiger FAD Proposal",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": "1956-05-25",
            "unit_price_bid_usd": 1750000.0,
            "dev_cost_bid_usd": 42000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": true,
              "radar_installed": true,
              "crew": 1,
              "engines": 1,
              "internal_bay": false,
              "guns_20mm": 4,
              "missile_capability": [
                "sarh",
                "ir"
              ]
            },
            "reputation_at_bid": 76.0,
            "track_record_at_bid": 0.68,
            "district_weight": 0.45,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 2.04,
              "climb_rate_sl_mps": 111.76,
              "payload_kg": 1179.3,
              "combat_radius_m": 574120.0,
              "service_ceiling_m": 17983.2,
              "carrier_suitability": 1.0
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "J79-powered F11F-1F Super Tiger (M2.04); airframe too small for large 32-in dish radar, 4x Sparrow III load, and 350 nmi radius."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": "usn_os130_1952",
        "follow_on_program_id": null,
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    },
    {
      "schema_version": 1,
      "id": "usaf_ws202a_1955",
      "name_key": "program.usaf_ws202a_1955.name",
      "program_name": "GOR 114 / WS-202A Long-Range Mach 3 Interceptor (LRI-X)",
      "customer": "USAF",
      "role": "interceptor",
      "mvp_core": true,
      "issue_date": "1955-10-06",
      "proposal_due": "1957-04-15",
      "first_flight_due": "1961-03-01",
      "ioc_due": "1963-06-01",
      "equipment": {
        "carrier_capable": false,
        "radar_required": true,
        "min_crew": 2,
        "min_engines": 2,
        "internal_bay_required": true,
        "min_guns_20mm": 0,
        "missile_capability": [
          "sarh"
        ]
      },
      "criteria": [
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 2.75,
          "objective_value": 3.1,
          "weight": 0.35,
          "unit": "mach",
          "description": "Mach 3.0 cruise and intercept at 70,000+ ft"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 1574200.0,
          "objective_value": 1889040.0,
          "weight": 0.3,
          "unit": "m",
          "description": "Long-range Arctic intercept radius (850-1,010 nmi)"
        },
        {
          "key": "service_ceiling_m",
          "kind": "objective",
          "op": ">=",
          "value": 21336.0,
          "objective_value": 24384.0,
          "weight": 0.2,
          "unit": "m",
          "description": "Combat ceiling (70,000-80,100 ft)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 177.8,
          "objective_value": 228.6,
          "weight": 0.15,
          "unit": "mps",
          "description": "Rate of climb (35,000-45,000 ft/min)"
        }
      ],
      "budget": {
        "dev_usd": 180000000.0,
        "unit_price_ceiling_usd": 5200000.0,
        "quantity_planned": 480
      },
      "acquisition": {
        "style": "paper_award",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 2,
        "allow_dual_award": false,
        "production_lots": 5,
        "urgency": 0.75
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.45,
          "cost": 0.2,
          "sched": 0.15,
          "risk": 0.2
        },
        "flyoff": {
          "perf": 0.6,
          "cost": 0.15,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "north_american": 0.55,
          "lockheed": 0.3,
          "northrop": 0.2
        },
        "congressional_interest": 0.5,
        "industrial_base_need": {
          "north_american": 0.5,
          "lockheed": 0.25
        }
      },
      "historical": {
        "winner_company_id": "north_american",
        "winner_design_name": "NA-236 / NA-257 (XF-108 Rapier)",
        "award_date": "1957-06-06",
        "outcome": "cancelled_in_dev",
        "production_delivered": 0,
        "notes": "North American won WS-202A on June 6, 1957 over Lockheed CL-325 and Northrop N-167 due to Mach 3 stainless-steel honeycomb and GE J93 engine commonality with the XB-70 Valkyrie. Cancelled Sep 23, 1959 after $141.9M spent as Soviet threat shifted from bombers to ICBMs; its ASG-18 radar and GAR-9 missile lived on in the YF-12A and F-14 AWG-9/AIM-54 Phoenix.",
        "citations": [
          "https://en.wikipedia.org/wiki/North_American_XF-108_Rapier",
          "https://www.nationalmuseum.af.mil/Visit/Museum-Exhibits/Fact-Sheets/Display/Article/195840/north-american-xf-108-rapier/"
        ],
        "competitors": [
          {
            "company_id": "north_american",
            "design_name": "NA-257 (XF-108 Rapier)",
            "is_historical_winner": true,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 4200000.0,
            "dev_cost_bid_usd": 145000000.0,
            "novelty": {
              "unproven_tech_count": 2,
              "unflown_engine": true,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 2,
              "engines": 2,
              "internal_bay": true,
              "guns_20mm": 0,
              "missile_capability": [
                "sarh"
              ]
            },
            "reputation_at_bid": 88.0,
            "track_record_at_bid": 0.8,
            "district_weight": 0.55,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 3.05,
              "combat_radius_m": 1870520.0,
              "service_ceiling_m": 24414.5,
              "climb_rate_sl_mps": 228.6
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Mach 3+ (1,720 kn), 80,100 ft ceiling, 1,010 nmi combat radius, 45,000 ft/min climb, 2x GE YJ93 + 3x GAR-9 in rotary bay."
          },
          {
            "company_id": "lockheed",
            "design_name": "CL-325 Mach 3 LRI-X Proposal",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 4550000.0,
            "dev_cost_bid_usd": 165000000.0,
            "novelty": {
              "unproven_tech_count": 3,
              "unflown_engine": true,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 2,
              "engines": 2,
              "internal_bay": true,
              "guns_20mm": 0,
              "missile_capability": [
                "sarh"
              ]
            },
            "reputation_at_bid": 84.0,
            "track_record_at_bid": 0.76,
            "district_weight": 0.52,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 3.0,
              "combat_radius_m": 1740880.0,
              "service_ceiling_m": 23774.4,
              "climb_rate_sl_mps": 213.36
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "High-altitude Mach 3 interceptor proposal; lacked NAA's XB-70 J93/brazed-honeycomb cost-sharing synergy."
          },
          {
            "company_id": "northrop",
            "design_name": "N-167 Long-Range Interceptor",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 4400000.0,
            "dev_cost_bid_usd": 160000000.0,
            "novelty": {
              "unproven_tech_count": 3,
              "unflown_engine": true,
              "unconventional_config": true
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": true,
              "crew": 2,
              "engines": 2,
              "internal_bay": true,
              "guns_20mm": 0,
              "missile_capability": [
                "sarh"
              ]
            },
            "reputation_at_bid": 74.0,
            "track_record_at_bid": 0.68,
            "district_weight": 0.48,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 2.85,
              "combat_radius_m": 1685320.0,
              "service_ceiling_m": 22555.2,
              "climb_rate_sl_mps": 198.12
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Northrop LRI-X proposal; lower cruise Mach and ceiling than NA-257."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": "usaf_ws201a_1950",
        "follow_on_program_id": null,
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.85
      }
    },
    {
      "schema_version": 1,
      "id": "usaf_gor127_n156_1956",
      "name_key": "program.usaf_gor127_n156_1956.name",
      "program_name": "GOR 127 / N-156 Lightweight Twin-J85 Supersonic Fighter/Trainer",
      "customer": "USAF",
      "role": "day_fighter",
      "mvp_core": false,
      "issue_date": "1956-06-01",
      "proposal_due": "1956-12-01",
      "first_flight_due": "1959-08-01",
      "ioc_due": "1961-06-01",
      "equipment": {
        "carrier_capable": false,
        "radar_required": false,
        "min_crew": 1,
        "min_engines": 2,
        "internal_bay_required": false,
        "min_guns_20mm": 2,
        "missile_capability": [
          "ir"
        ]
      },
      "criteria": [
        {
          "key": "max_mach_alt",
          "kind": "objective",
          "op": ">=",
          "value": 1.25,
          "objective_value": 1.45,
          "weight": 0.25,
          "unit": "mach",
          "description": "Supersonic speed (Mach 1.25-1.45)"
        },
        {
          "key": "climb_rate_sl_mps",
          "kind": "objective",
          "op": ">=",
          "value": 121.92,
          "objective_value": 152.4,
          "weight": 0.25,
          "unit": "mps",
          "description": "Rate of climb (24,000-30,000 ft/min)"
        },
        {
          "key": "combat_radius_m",
          "kind": "objective",
          "op": ">=",
          "value": 777840.0,
          "objective_value": 1064900.0,
          "weight": 0.25,
          "unit": "m",
          "description": "Hi-lo-hi combat radius with tanks (420-575 nmi)"
        },
        {
          "key": "maint_mh_per_fh",
          "kind": "objective",
          "op": "<=",
          "value": 18.0,
          "objective_value": 12.0,
          "weight": 0.25,
          "unit": "float",
          "description": "Low maintenance man-hours per flight hour (<= 15 MMH/FH)"
        }
      ],
      "budget": {
        "dev_usd": 24000000.0,
        "unit_price_ceiling_usd": 850000.0,
        "quantity_planned": 850
      },
      "acquisition": {
        "style": "paper_award",
        "downselect_count": 1,
        "prototype_quantity_per_winner": 3,
        "allow_dual_award": false,
        "production_lots": 5,
        "urgency": 0.6
      },
      "eval_weights": {
        "proposal": {
          "perf": 0.4,
          "cost": 0.3,
          "sched": 0.15,
          "risk": 0.15
        },
        "flyoff": {
          "perf": 0.5,
          "cost": 0.25,
          "sched": 0.1,
          "risk": 0.15
        }
      },
      "politics": {
        "incumbent_bias": {
          "northrop": 0.5,
          "north_american": 0.25,
          "lockheed": 0.2
        },
        "congressional_interest": 0.35,
        "industrial_base_need": {
          "northrop": 0.55
        }
      },
      "historical": {
        "winner_company_id": "northrop",
        "winner_design_name": "N-156 (YT-38 Talon / F-5A Freedom Fighter)",
        "award_date": "1956-12-15",
        "outcome": "produced",
        "production_delivered": 2034,
        "notes": "Northrop private venture led by Edgar Schmued and Welko Gasich around twin compact GE J85 engines. Won GOR 127 (T-38 Talon) in Dec 1956 and MAP Project FX (F-5A Freedom Fighter) over NAA NA-241 and Lockheed CL-419.",
        "citations": [
          "https://en.wikipedia.org/wiki/Northrop_F-5",
          "https://en.wikipedia.org/wiki/Northrop_T-38_Talon"
        ],
        "competitors": [
          {
            "company_id": "northrop",
            "design_name": "N-156 (YT-38 / F-5A Freedom Fighter)",
            "is_historical_winner": true,
            "built_prototype": true,
            "first_flight_date": "1959-04-10",
            "unit_price_bid_usd": 638000.0,
            "dev_cost_bid_usd": 18500000.0,
            "novelty": {
              "unproven_tech_count": 0,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": false,
              "crew": 1,
              "engines": 2,
              "internal_bay": false,
              "guns_20mm": 2,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 80.0,
            "track_record_at_bid": 0.76,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.4,
              "climb_rate_sl_mps": 145.8,
              "combat_radius_m": 1064900.0,
              "maint_mh_per_fh": 12.5
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "M1.40 (925 mph), 28,700-33,600 ft/min climb, 575 nmi radius, $638k-$756k unit cost, twin GE J85."
          },
          {
            "company_id": "north_american",
            "design_name": "NA-241 Supersonic Trainer/Light Fighter",
            "is_historical_winner": false,
            "built_prototype": false,
            "first_flight_date": null,
            "unit_price_bid_usd": 780000.0,
            "dev_cost_bid_usd": 22000000.0,
            "novelty": {
              "unproven_tech_count": 1,
              "unflown_engine": false,
              "unconventional_config": false
            },
            "equipment": {
              "carrier_capable": false,
              "radar_installed": false,
              "crew": 1,
              "engines": 2,
              "internal_bay": false,
              "guns_20mm": 2,
              "missile_capability": [
                "ir"
              ]
            },
            "reputation_at_bid": 78.0,
            "track_record_at_bid": 0.72,
            "district_weight": 0.5,
            "cross_service_derivative": false,
            "anchor_performance": {
              "max_mach_alt": 1.3,
              "climb_rate_sl_mps": 127.0,
              "combat_radius_m": 870440.0,
              "maint_mh_per_fh": 16.5
            },
            "flyoff_flaws_unfixed_severity": 0,
            "published_notes": "Heavier airframe and higher unit cost than Northrop N-156."
          }
        ]
      },
      "alt_history": {
        "predecessor_program_id": "usaf_ws303a_1952",
        "follow_on_program_id": null,
        "suppress_if_role_satisfied": false,
        "historical_cancellation_shock": 0.0
      }
    }
  ],
  "airframers": {
    "schema_version": "1.0",
    "era": "1945-1960",
    "country": "USA",
    "description": "Historical US fighter airframe manufacturers (1945-01-01 starting state, facilities, reputations, engineering staff, and AI design doctrine).",
    "airframers": [
      {
        "id": "north_american",
        "name_key": "company.north_american.name",
        "short_name_key": "company.north_american.short",
        "hq_location": "Inglewood, California",
        "company_code_usn": "J",
        "playable_default": true,
        "tier": "major_prime",
        "cash_usd": 38000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.92,
          "USN": 0.55,
          "export": 0.8
        },
        "political_capital": 0.85,
        "engineers": {
          "aero": 65,
          "structures": 70,
          "propulsion": 20,
          "systems": 45
        },
        "facilities": {
          "wind_tunnel_level": 2,
          "factory_floor_m2": 260000.0,
          "test_site": true
        },
        "chief_designer_id": "designer_edgar_schmued",
        "secondary_designer_id": "designer_harrison_storms",
        "starting_tech_overrides": {
          "aero_1945_compressible_subsonic": 0.95,
          "struct_1945_stressed_skin_7075": 0.94,
          "mfg_1945_ww2_mass_production_line": 0.95
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USAF",
            "USN"
          ],
          "speed_vs_maneuver_bias": 0.35,
          "production_scalability_focus": 0.9,
          "aerodynamic_ambition": 0.85,
          "risk_tolerance": 0.65
        },
        "historical_aircraft_1945_1960": [
          "FJ-1 Fury",
          "F-86 Sabre",
          "F-86D Sabre Dog",
          "FJ-2/3/4 Fury",
          "F-100 Super Sabre",
          "F-107A",
          "XF-108 Rapier"
        ],
        "historical_summary": "Wartime mass-production titan (P-51 Mustang, B-25) that pivoted fastest to swept-wing transonic and supersonic fighters with the F-86 Sabre and F-100 Super Sabre."
      },
      {
        "id": "lockheed",
        "name_key": "company.lockheed.name",
        "short_name_key": "company.lockheed.short",
        "hq_location": "Burbank, California",
        "company_code_usn": "V",
        "playable_default": true,
        "tier": "major_prime",
        "cash_usd": 34000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.9,
          "USN": 0.5,
          "export": 0.82
        },
        "political_capital": 0.82,
        "engineers": {
          "aero": 62,
          "structures": 58,
          "propulsion": 18,
          "systems": 42
        },
        "facilities": {
          "wind_tunnel_level": 2,
          "factory_floor_m2": 220000.0,
          "test_site": true
        },
        "chief_designer_id": "designer_kelly_johnson",
        "secondary_designer_id": "designer_willis_hawkins",
        "starting_tech_overrides": {
          "aero_1945_compressible_subsonic": 0.94,
          "struct_1945_stressed_skin_7075": 0.92,
          "sys_1946_hydraulic_boost_controls": 0.45
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USAF"
          ],
          "speed_vs_maneuver_bias": 0.8,
          "production_scalability_focus": 0.75,
          "aerodynamic_ambition": 0.92,
          "risk_tolerance": 0.78
        },
        "historical_aircraft_1945_1960": [
          "P-80 / F-80 Shooting Star",
          "T-33",
          "F-94 Starfire",
          "XF-90",
          "XFV-1",
          "F-104 Starfighter",
          "U-2"
        ],
        "historical_summary": "Builder of America's first operational jet fighter (P-80 Shooting Star); Kelly Johnson's Advanced Development Projects unit excelled at rapid, extreme-speed prototypes."
      },
      {
        "id": "republic",
        "name_key": "company.republic.name",
        "short_name_key": "company.republic.short",
        "hq_location": "Farmingdale, Long Island, New York",
        "company_code_usn": "P",
        "playable_default": true,
        "tier": "major_prime",
        "cash_usd": 24000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.86,
          "USN": 0.25,
          "export": 0.75
        },
        "political_capital": 0.76,
        "engineers": {
          "aero": 45,
          "structures": 58,
          "propulsion": 22,
          "systems": 38
        },
        "facilities": {
          "wind_tunnel_level": 1,
          "factory_floor_m2": 175000.0,
          "test_site": false
        },
        "chief_designer_id": "designer_alexander_kartveli",
        "secondary_designer_id": null,
        "starting_tech_overrides": {
          "struct_1945_stressed_skin_7075": 0.95,
          "prop_1945_early_axial_compressor": 0.65
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USAF"
          ],
          "speed_vs_maneuver_bias": 0.7,
          "production_scalability_focus": 0.8,
          "aerodynamic_ambition": 0.75,
          "risk_tolerance": 0.72
        },
        "historical_aircraft_1945_1960": [
          "F-84 Thunderjet",
          "F-84F Thunderstreak",
          "XF-91 Thunderceptor",
          "XF-84H",
          "F-105 Thunderchief",
          "XF-103"
        ],
        "historical_summary": "TAC's premier heavy fighter-bomber house; Kartveli's designs combined rugged structural strength, massive internal fuel/payload, and high low-altitude dash speed."
      },
      {
        "id": "convair",
        "name_key": "company.convair.name",
        "short_name_key": "company.convair.short",
        "hq_location": "San Diego, California",
        "company_code_usn": "Y",
        "playable_default": true,
        "tier": "major_prime",
        "cash_usd": 36000000.0,
        "debt_usd": 2000000.0,
        "reputation": {
          "USAF": 0.84,
          "USN": 0.52,
          "export": 0.6
        },
        "political_capital": 0.88,
        "engineers": {
          "aero": 60,
          "structures": 62,
          "propulsion": 18,
          "systems": 55
        },
        "facilities": {
          "wind_tunnel_level": 2,
          "factory_floor_m2": 250000.0,
          "test_site": true
        },
        "chief_designer_id": "designer_frank_davis",
        "secondary_designer_id": "designer_ralph_shick",
        "starting_tech_overrides": {
          "struct_1945_stressed_skin_7075": 0.92,
          "av_1945_vhf_gyro_sight_scr720": 0.88
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USAF",
            "USN"
          ],
          "speed_vs_maneuver_bias": 0.75,
          "production_scalability_focus": 0.72,
          "aerodynamic_ambition": 0.95,
          "risk_tolerance": 0.85
        },
        "historical_aircraft_1945_1960": [
          "XF-92A",
          "F2Y Sea Dart",
          "XFY-1 Pogo",
          "F-102 Delta Dagger",
          "F-106 Delta Dart",
          "B-58 Hustler"
        ],
        "historical_summary": "Pioneer of the tailless 60-degree delta wing, Weapon System concept integration (WS-201A), area-ruled interceptors, and Mach 2 honeycomb structures."
      },
      {
        "id": "mcdonnell",
        "name_key": "company.mcdonnell.name",
        "short_name_key": "company.mcdonnell.short",
        "hq_location": "St. Louis, Missouri",
        "company_code_usn": "H",
        "playable_default": true,
        "tier": "rising_prime",
        "cash_usd": 14000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.62,
          "USN": 0.78,
          "export": 0.55
        },
        "political_capital": 0.68,
        "engineers": {
          "aero": 42,
          "structures": 46,
          "propulsion": 16,
          "systems": 36
        },
        "facilities": {
          "wind_tunnel_level": 1,
          "factory_floor_m2": 115000.0,
          "test_site": false
        },
        "chief_designer_id": "designer_kendall_perkins",
        "secondary_designer_id": "designer_herman_barkey",
        "starting_tech_overrides": {
          "prop_1945_early_axial_compressor": 0.65,
          "aero_1945_compressible_subsonic": 0.92
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USN",
            "USAF"
          ],
          "speed_vs_maneuver_bias": 0.6,
          "production_scalability_focus": 0.78,
          "aerodynamic_ambition": 0.82,
          "risk_tolerance": 0.75
        },
        "historical_aircraft_1945_1960": [
          "FH-1 Phantom",
          "F2H Banshee",
          "XF-85 Goblin",
          "XF-88 Voodoo",
          "F3H Demon",
          "F-101 Voodoo",
          "F4H-1 (F-4) Phantom II"
        ],
        "historical_summary": "Founded in 1939; rose from a small St. Louis newcomer with the Navy's first carrier jet (FH-1) to dominate the late 1950s with the F-101 Voodoo and F4H Phantom II."
      },
      {
        "id": "grumman",
        "name_key": "company.grumman.name",
        "short_name_key": "company.grumman.short",
        "hq_location": "Bethpage, Long Island, New York",
        "company_code_usn": "F",
        "playable_default": true,
        "tier": "major_prime",
        "cash_usd": 28000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.35,
          "USN": 0.95,
          "export": 0.6
        },
        "political_capital": 0.8,
        "engineers": {
          "aero": 46,
          "structures": 56,
          "propulsion": 15,
          "systems": 38
        },
        "facilities": {
          "wind_tunnel_level": 1,
          "factory_floor_m2": 180000.0,
          "test_site": true
        },
        "chief_designer_id": "designer_william_schwendler",
        "secondary_designer_id": "designer_richard_hutton",
        "starting_tech_overrides": {
          "struct_1945_stressed_skin_7075": 0.95,
          "struct_1948_jet_carrier_suitability": 0.55
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USN"
          ],
          "speed_vs_maneuver_bias": 0.3,
          "production_scalability_focus": 0.85,
          "aerodynamic_ambition": 0.72,
          "risk_tolerance": 0.55
        },
        "historical_aircraft_1945_1960": [
          "F9F-2/5 Panther",
          "F9F-6/8 Cougar",
          "XF10F-1 Jaguar",
          "F11F-1 Tiger",
          "F11F-1F Super Tiger"
        ],
        "historical_summary": "The 'Iron Works' of US Naval Aviation; unmatched carrier deck ruggedness and BuAer trust, transitioning from the F9F Panther/Cougar to the area-ruled F11F Tiger."
      },
      {
        "id": "douglas",
        "name_key": "company.douglas.name",
        "short_name_key": "company.douglas.short",
        "hq_location": "El Segundo & Santa Monica, California",
        "company_code_usn": "D",
        "playable_default": true,
        "tier": "major_prime",
        "cash_usd": 42000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.72,
          "USN": 0.9,
          "export": 0.85
        },
        "political_capital": 0.86,
        "engineers": {
          "aero": 60,
          "structures": 64,
          "propulsion": 18,
          "systems": 44
        },
        "facilities": {
          "wind_tunnel_level": 2,
          "factory_floor_m2": 270000.0,
          "test_site": true
        },
        "chief_designer_id": "designer_ed_heinemann",
        "secondary_designer_id": null,
        "starting_tech_overrides": {
          "aero_1945_compressible_subsonic": 0.94,
          "struct_1945_stressed_skin_7075": 0.94
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USN",
            "USAF"
          ],
          "speed_vs_maneuver_bias": 0.45,
          "production_scalability_focus": 0.88,
          "aerodynamic_ambition": 0.86,
          "risk_tolerance": 0.65
        },
        "historical_aircraft_1945_1960": [
          "D-558-1 Skystreak",
          "D-558-2 Skyrocket",
          "F3D Skyknight",
          "X-3 Stiletto",
          "F4D Skyray",
          "F5D Skylancer",
          "A4D Skyhawk"
        ],
        "historical_summary": "Ed Heinemann's El Segundo division championed structural simplicity and weight discipline ('Simplicate and add lightness'), building the F3D, F4D Skyray, A4D Skyhawk, and NACA D-558 research aircraft."
      },
      {
        "id": "vought",
        "name_key": "company.vought.name",
        "short_name_key": "company.vought.short",
        "hq_location": "Stratford, Connecticut (Dallas, Texas from 1948)",
        "company_code_usn": "U",
        "playable_default": true,
        "tier": "mid_prime",
        "cash_usd": 19000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.3,
          "USN": 0.84,
          "export": 0.58
        },
        "political_capital": 0.66,
        "engineers": {
          "aero": 42,
          "structures": 44,
          "propulsion": 14,
          "systems": 32
        },
        "facilities": {
          "wind_tunnel_level": 1,
          "factory_floor_m2": 135000.0,
          "test_site": false
        },
        "chief_designer_id": "designer_john_russell_clark",
        "secondary_designer_id": "designer_rex_beisel",
        "starting_tech_overrides": {
          "struct_1945_stressed_skin_7075": 0.9
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USN"
          ],
          "speed_vs_maneuver_bias": 0.65,
          "production_scalability_focus": 0.7,
          "aerodynamic_ambition": 0.9,
          "risk_tolerance": 0.85
        },
        "historical_aircraft_1945_1960": [
          "F6U Pirate",
          "F7U Cutlass",
          "F8U (F-8) Crusader",
          "XF8U-3 Crusader III"
        ],
        "historical_summary": "Bold naval innovator that gambled on the radical tailless F7U Cutlass before redeeming itself with the Collier-Trophy-winning supersonic F8U Crusader and Mach 2.3+ XF8U-3."
      },
      {
        "id": "northrop",
        "name_key": "company.northrop.name",
        "short_name_key": "company.northrop.short",
        "hq_location": "Hawthorne, California",
        "company_code_usn": "N",
        "playable_default": true,
        "tier": "mid_prime",
        "cash_usd": 17000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.76,
          "USN": 0.3,
          "export": 0.72
        },
        "political_capital": 0.64,
        "engineers": {
          "aero": 46,
          "structures": 40,
          "propulsion": 14,
          "systems": 38
        },
        "facilities": {
          "wind_tunnel_level": 1,
          "factory_floor_m2": 125000.0,
          "test_site": false
        },
        "chief_designer_id": "designer_jack_northrop",
        "secondary_designer_id": "designer_welko_gasich",
        "starting_tech_overrides": {
          "av_1945_vhf_gyro_sight_scr720": 0.92,
          "aero_1945_compressible_subsonic": 0.92
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USAF"
          ],
          "speed_vs_maneuver_bias": 0.4,
          "production_scalability_focus": 0.76,
          "aerodynamic_ambition": 0.88,
          "risk_tolerance": 0.74
        },
        "historical_aircraft_1945_1960": [
          "XP-79B",
          "X-4 Bantam",
          "F-89 Scorpion",
          "N-156F / F-5A Freedom Fighter",
          "T-38 Talon"
        ],
        "historical_summary": "Night/all-weather fighter specialist (P-61 Black Widow, F-89 Scorpion) and flying-wing pioneer that pivoted in the mid-1950s to lightweight, high-agility supersonic fighters (N-156F / F-5)."
      },
      {
        "id": "bell",
        "name_key": "company.bell.name",
        "short_name_key": "company.bell.short",
        "hq_location": "Buffalo / Niagara Falls, New York",
        "company_code_usn": "L",
        "playable_default": true,
        "tier": "specialist_prime",
        "cash_usd": 15000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.7,
          "USN": 0.42,
          "export": 0.5
        },
        "political_capital": 0.62,
        "engineers": {
          "aero": 44,
          "structures": 36,
          "propulsion": 18,
          "systems": 28
        },
        "facilities": {
          "wind_tunnel_level": 1,
          "factory_floor_m2": 110000.0,
          "test_site": false
        },
        "chief_designer_id": "designer_robert_woods",
        "secondary_designer_id": null,
        "starting_tech_overrides": {
          "test_1945_sub_and_supersonic_blowdown_tunnels": 0.92,
          "aero_1945_compressible_subsonic": 0.9
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USAF"
          ],
          "speed_vs_maneuver_bias": 0.75,
          "production_scalability_focus": 0.55,
          "aerodynamic_ambition": 0.96,
          "risk_tolerance": 0.9
        },
        "historical_aircraft_1945_1960": [
          "P-59 Airacomet",
          "XP-83",
          "X-1",
          "X-1A/E",
          "X-2",
          "X-5",
          "X-14",
          "XF-109 (D188A)"
        ],
        "historical_summary": "Builder of America's very first jet (P-59) and the legendary X-1, X-2, and X-5 supersonic/variable-sweep research aircraft; brilliant at X-planes but struggled to win postwar series fighter production."
      },
      {
        "id": "curtiss_wright",
        "name_key": "company.curtiss_wright.name",
        "short_name_key": "company.curtiss_wright.short",
        "hq_location": "Columbus, Ohio & Buffalo, New York",
        "company_code_usn": "C",
        "playable_default": true,
        "tier": "legacy_giant",
        "cash_usd": 32000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.65,
          "USN": 0.62,
          "export": 0.68
        },
        "political_capital": 0.7,
        "engineers": {
          "aero": 34,
          "structures": 42,
          "propulsion": 20,
          "systems": 28
        },
        "facilities": {
          "wind_tunnel_level": 1,
          "factory_floor_m2": 195000.0,
          "test_site": false
        },
        "chief_designer_id": "designer_donovan_berlin",
        "secondary_designer_id": null,
        "starting_tech_overrides": {
          "mfg_1945_ww2_mass_production_line": 0.9
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USAF",
            "USN"
          ],
          "speed_vs_maneuver_bias": 0.4,
          "production_scalability_focus": 0.75,
          "aerodynamic_ambition": 0.5,
          "risk_tolerance": 0.45
        },
        "historical_aircraft_1945_1960": [
          "XF15C-1",
          "XP-87 / XF-87 Blackhawk"
        ],
        "historical_summary": "America's second-largest WWII industrial corporation; conservative management starved jet R&D, making the XF-87 Blackhawk its final stand as an airframe builder in 1948."
      },
      {
        "id": "martin",
        "name_key": "company.martin.name",
        "short_name_key": "company.martin.short",
        "hq_location": "Middle River, Maryland",
        "company_code_usn": "M",
        "playable_default": false,
        "tier": "mid_prime",
        "cash_usd": 26000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.74,
          "USN": 0.76,
          "export": 0.55
        },
        "political_capital": 0.75,
        "engineers": {
          "aero": 38,
          "structures": 48,
          "propulsion": 16,
          "systems": 36
        },
        "facilities": {
          "wind_tunnel_level": 1,
          "factory_floor_m2": 165000.0,
          "test_site": false
        },
        "chief_designer_id": "designer_george_trimble",
        "secondary_designer_id": null,
        "starting_tech_overrides": {
          "struct_1945_stressed_skin_7075": 0.9
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USAF",
            "USN"
          ],
          "speed_vs_maneuver_bias": 0.6,
          "production_scalability_focus": 0.78,
          "aerodynamic_ambition": 0.68,
          "risk_tolerance": 0.6
        },
        "historical_aircraft_1945_1960": [
          "XB-48",
          "XB-51",
          "B-57 Canberra"
        ],
        "historical_summary": "Major tactical bomber and patrol-plane house that competed for USAF tactical strike contracts (XB-51, B-57) before pivoting toward missiles and space."
      },
      {
        "id": "boeing",
        "name_key": "company.boeing.name",
        "short_name_key": "company.boeing.short",
        "hq_location": "Seattle, Washington & Wichita, Kansas",
        "company_code_usn": "B",
        "playable_default": false,
        "tier": "major_prime",
        "cash_usd": 45000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.95,
          "USN": 0.4,
          "export": 0.8
        },
        "political_capital": 0.92,
        "engineers": {
          "aero": 68,
          "structures": 72,
          "propulsion": 22,
          "systems": 48
        },
        "facilities": {
          "wind_tunnel_level": 2,
          "factory_floor_m2": 290000.0,
          "test_site": true
        },
        "chief_designer_id": "designer_george_schairer",
        "secondary_designer_id": null,
        "starting_tech_overrides": {
          "aero_1945_compressible_subsonic": 0.95,
          "test_1945_sub_and_supersonic_blowdown_tunnels": 0.92,
          "struct_1945_stressed_skin_7075": 0.95
        },
        "ai_doctrine": {
          "preferred_customers": [
            "USAF"
          ],
          "speed_vs_maneuver_bias": 0.65,
          "production_scalability_focus": 0.92,
          "aerodynamic_ambition": 0.88,
          "risk_tolerance": 0.62
        },
        "historical_aircraft_1945_1960": [
          "XF8B-1",
          "B-47 Stratojet",
          "B-52 Stratofortress",
          "XF-99 Bowmarc"
        ],
        "historical_summary": "Strategic bomber powerhouse whose private high-speed wind tunnel and George Schairer's immediate 1945 adoption of German swept-wing data produced the revolutionary XB-47."
      }
    ]
  },
  "designers": {
    "schema_version": "1.0",
    "era": "1945-1960",
    "description": "Historical and custom chief designers (1945-1960) with modest, data-driven engineering trait modifiers (bounded within +/-15%).",
    "designers": [
      {
        "id": "designer_edgar_schmued",
        "name_key": "designer.edgar_schmued.name",
        "title_key": "designer.edgar_schmued.title",
        "company_id": "north_american",
        "active_years": [
          1945,
          1957
        ],
        "specialty": "swept_wing_and_drag_refinement",
        "research_branch_bonuses": {
          "aero": 0.12,
          "manufacturing": 0.08
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.97,
          "prototype_build_time_factor": 0.94,
          "structural_mass_factor": 1.0
        },
        "historical_note": "Chief Designer of P-51 Mustang, F-86 Sabre, and F-100 Super Sabre (later VP of Engineering at Northrop for T-38/F-5)."
      },
      {
        "id": "designer_harrison_storms",
        "name_key": "designer.harrison_storms.name",
        "title_key": "designer.harrison_storms.title",
        "company_id": "north_american",
        "active_years": [
          1948,
          1960
        ],
        "specialty": "high_mach_and_flight_test",
        "research_branch_bonuses": {
          "aero": 0.1,
          "structures": 0.1,
          "testing": 0.1
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.98,
          "prototype_build_time_factor": 0.92,
          "structural_mass_factor": 0.98
        },
        "historical_note": "Dynamic NAA chief engineer driving the F-100, F-107A, X-15, and XB-70 Valkyrie."
      },
      {
        "id": "designer_kelly_johnson",
        "name_key": "designer.kelly_johnson.name",
        "title_key": "designer.kelly_johnson.title",
        "company_id": "lockheed",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "rapid_prototyping_and_supersonics",
        "research_branch_bonuses": {
          "aero": 0.15,
          "testing": 0.12
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.96,
          "prototype_build_time_factor": 0.85,
          "structural_mass_factor": 0.97
        },
        "historical_note": "Legendary head of Lockheed Advanced Development Projects (P-80 in 143 days, F-104 Starfighter, U-2, A-12)."
      },
      {
        "id": "designer_willis_hawkins",
        "name_key": "designer.willis_hawkins.name",
        "title_key": "designer.willis_hawkins.title",
        "company_id": "lockheed",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "preliminary_design_and_structures",
        "research_branch_bonuses": {
          "structures": 0.1,
          "avionics": 0.08
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.99,
          "prototype_build_time_factor": 0.95,
          "structural_mass_factor": 0.98
        },
        "historical_note": "Head of Lockheed preliminary design; key architect on F-80, F-94, and XF-90."
      },
      {
        "id": "designer_alexander_kartveli",
        "name_key": "designer.alexander_kartveli.name",
        "title_key": "designer.alexander_kartveli.title",
        "company_id": "republic",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "heavy_strike_and_area_ruled_structures",
        "research_branch_bonuses": {
          "structures": 0.14,
          "propulsion": 0.08,
          "armament": 0.1
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.98,
          "prototype_build_time_factor": 0.98,
          "structural_mass_factor": 0.96
        },
        "historical_note": "Georgian-born Chief Engineer of Republic Aviation (P-47, F-84, F-84F, XF-91, F-105 Thunderchief, XF-103)."
      },
      {
        "id": "designer_frank_davis",
        "name_key": "designer.frank_davis.name",
        "title_key": "designer.frank_davis.title",
        "company_id": "convair",
        "active_years": [
          1948,
          1960
        ],
        "specialty": "delta_wing_and_weapon_system_integration",
        "research_branch_bonuses": {
          "aero": 0.12,
          "avionics": 0.12
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.97,
          "prototype_build_time_factor": 0.96,
          "structural_mass_factor": 0.99
        },
        "historical_note": "Former test pilot and Convair Chief Engineer on XF-92A, F-102A Delta Dagger, F-106A Delta Dart, and B-58."
      },
      {
        "id": "designer_ralph_shick",
        "name_key": "designer.ralph_shick.name",
        "title_key": "designer.ralph_shick.title",
        "company_id": "convair",
        "active_years": [
          1945,
          1956
        ],
        "specialty": "delta_aerodynamics",
        "research_branch_bonuses": {
          "aero": 0.12,
          "testing": 0.08
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.98,
          "prototype_build_time_factor": 1.0,
          "structural_mass_factor": 1.0
        },
        "historical_note": "Convair aerodynamicist who collaborated with Lippisch and NACA on the 60-degree tailless delta layout."
      },
      {
        "id": "designer_kendall_perkins",
        "name_key": "designer.kendall_perkins.name",
        "title_key": "designer.kendall_perkins.title",
        "company_id": "mcdonnell",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "twin_engine_carrier_and_long_range_fighters",
        "research_branch_bonuses": {
          "aero": 0.08,
          "structures": 0.1,
          "avionics": 0.1
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.98,
          "prototype_build_time_factor": 0.95,
          "structural_mass_factor": 0.98
        },
        "historical_note": "McDonnell VP of Engineering overseeing the FH-1, F2H Banshee, F-101 Voodoo, and F4H-1 Phantom II."
      },
      {
        "id": "designer_herman_barkey",
        "name_key": "designer.herman_barkey.name",
        "title_key": "designer.herman_barkey.title",
        "company_id": "mcdonnell",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "carrier_fighter_detail_design",
        "research_branch_bonuses": {
          "structures": 0.1,
          "manufacturing": 0.08
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.99,
          "prototype_build_time_factor": 0.95,
          "structural_mass_factor": 0.97
        },
        "historical_note": "Project engineer on F2H Banshee and Chief Project Engineer on the F4H-1 (F-4) Phantom II."
      },
      {
        "id": "designer_william_schwendler",
        "name_key": "designer.william_schwendler.name",
        "title_key": "designer.william_schwendler.title",
        "company_id": "grumman",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "rugged_carrier_structures",
        "research_branch_bonuses": {
          "structures": 0.14,
          "manufacturing": 0.1
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.99,
          "prototype_build_time_factor": 0.94,
          "structural_mass_factor": 0.97
        },
        "historical_note": "Grumman Chief Engineer & co-founder ('Iron Works'); designed F9F Panther/Cougar and oversaw F11F Tiger."
      },
      {
        "id": "designer_richard_hutton",
        "name_key": "designer.richard_hutton.name",
        "title_key": "designer.richard_hutton.title",
        "company_id": "grumman",
        "active_years": [
          1950,
          1960
        ],
        "specialty": "area_ruled_naval_supersonics",
        "research_branch_bonuses": {
          "aero": 0.12,
          "structures": 0.08
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.97,
          "prototype_build_time_factor": 0.95,
          "structural_mass_factor": 0.98
        },
        "historical_note": "Grumman Chief Development Engineer who immediately applied Whitcomb's area rule to create the F11F-1 Tiger."
      },
      {
        "id": "designer_ed_heinemann",
        "name_key": "designer.ed_heinemann.name",
        "title_key": "designer.ed_heinemann.title",
        "company_id": "douglas",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "lightweight_structural_simplicity",
        "research_branch_bonuses": {
          "structures": 0.15,
          "aero": 0.1,
          "manufacturing": 0.1
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.97,
          "prototype_build_time_factor": 0.88,
          "structural_mass_factor": 0.92
        },
        "historical_note": "Chief Engineer of Douglas El Segundo (D-558, F3D, F4D Skyray, A4D Skyhawk); famous for delivering the A4D at half the Navy's weight specification."
      },
      {
        "id": "designer_john_russell_clark",
        "name_key": "designer.john_russell_clark.name",
        "title_key": "designer.john_russell_clark.title",
        "company_id": "vought",
        "active_years": [
          1948,
          1960
        ],
        "specialty": "supersonic_carrier_fighters_and_titanium",
        "research_branch_bonuses": {
          "aero": 0.12,
          "structures": 0.12
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.97,
          "prototype_build_time_factor": 0.92,
          "structural_mass_factor": 0.97
        },
        "historical_note": "Leader of Vought's F8U-1 Crusader (variable-incidence wing, titanium aft fuselage) and XF8U-3 Crusader III."
      },
      {
        "id": "designer_rex_beisel",
        "name_key": "designer.rex_beisel.name",
        "title_key": "designer.rex_beisel.title",
        "company_id": "vought",
        "active_years": [
          1945,
          1949
        ],
        "specialty": "experimental_tailless_naval_fighters",
        "research_branch_bonuses": {
          "aero": 0.1,
          "testing": 0.08
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.98,
          "prototype_build_time_factor": 1.02,
          "structural_mass_factor": 1.02
        },
        "historical_note": "Designer of the F4U Corsair and the radical tailless swept-wing F7U Cutlass."
      },
      {
        "id": "designer_jack_northrop",
        "name_key": "designer.jack_northrop.name",
        "title_key": "designer.jack_northrop.title",
        "company_id": "northrop",
        "active_years": [
          1945,
          1952
        ],
        "specialty": "all_wing_and_all_weather_interceptors",
        "research_branch_bonuses": {
          "aero": 0.14,
          "avionics": 0.08
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.96,
          "prototype_build_time_factor": 1.0,
          "structural_mass_factor": 0.98
        },
        "historical_note": "Visionary founder of Northrop Aircraft (YB-49 Flying Wing, X-4 Bantam, F-89 Scorpion)."
      },
      {
        "id": "designer_welko_gasich",
        "name_key": "designer.welko_gasich.name",
        "title_key": "designer.welko_gasich.title",
        "company_id": "northrop",
        "active_years": [
          1953,
          1960
        ],
        "specialty": "lightweight_supersonic_area_rule",
        "research_branch_bonuses": {
          "aero": 0.1,
          "manufacturing": 0.12
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.97,
          "prototype_build_time_factor": 0.93,
          "structural_mass_factor": 0.94
        },
        "historical_note": "Chief of Preliminary Design (with Edgar Schmued) on the N-156 / T-38 Talon and F-5 Freedom Fighter."
      },
      {
        "id": "designer_robert_woods",
        "name_key": "designer.robert_woods.name",
        "title_key": "designer.robert_woods.title",
        "company_id": "bell",
        "active_years": [
          1945,
          1956
        ],
        "specialty": "x_plane_transonic_and_variable_sweep",
        "research_branch_bonuses": {
          "aero": 0.14,
          "testing": 0.15
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.97,
          "prototype_build_time_factor": 0.92,
          "structural_mass_factor": 1.0
        },
        "historical_note": "Bell co-founder and Chief Design Engineer who championed the X-1, X-2, and variable-sweep X-5 with NACA."
      },
      {
        "id": "designer_donovan_berlin",
        "name_key": "designer.donovan_berlin.name",
        "title_key": "designer.donovan_berlin.title",
        "company_id": "curtiss_wright",
        "active_years": [
          1945,
          1952
        ],
        "specialty": "conventional_mass_production",
        "research_branch_bonuses": {
          "manufacturing": 0.08,
          "structures": 0.06
        },
        "design_modifiers": {
          "cd0_refinement_factor": 1.01,
          "prototype_build_time_factor": 0.98,
          "structural_mass_factor": 1.01
        },
        "historical_note": "Designer of P-36/P-40 who returned to Curtiss-Wright for the heavy four-jet XP-87 Blackhawk."
      },
      {
        "id": "designer_george_trimble",
        "name_key": "designer.george_trimble.name",
        "title_key": "designer.george_trimble.title",
        "company_id": "martin",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "high_speed_tactical_strike",
        "research_branch_bonuses": {
          "aero": 0.08,
          "armament": 0.1
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.98,
          "prototype_build_time_factor": 0.96,
          "structural_mass_factor": 0.99
        },
        "historical_note": "Head of Martin aerodynamics and advanced design (three-jet swept-wing XB-51 and B-57)."
      },
      {
        "id": "designer_george_schairer",
        "name_key": "designer.george_schairer.name",
        "title_key": "designer.george_schairer.title",
        "company_id": "boeing",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "swept_wing_wind_tunnel_mastery",
        "research_branch_bonuses": {
          "aero": 0.14,
          "testing": 0.12,
          "structures": 0.08
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.96,
          "prototype_build_time_factor": 0.96,
          "structural_mass_factor": 0.98
        },
        "historical_note": "Boeing Chief Aerodynamicist whose May 1945 letter from Germany triggered the swept-wing XB-47 and B-52."
      },
      {
        "id": "designer_gerhard_neumann",
        "name_key": "designer.gerhard_neumann.name",
        "title_key": "designer.gerhard_neumann.title",
        "company_id": "general_electric",
        "active_years": [
          1948,
          1960
        ],
        "specialty": "variable_stator_high_mach_turbojets",
        "research_branch_bonuses": {
          "propulsion": 0.15
        },
        "design_modifiers": {
          "cd0_refinement_factor": 1.0,
          "prototype_build_time_factor": 0.92,
          "structural_mass_factor": 1.0
        },
        "historical_note": "Leader of GE's variable-stator J79 development team (Collier Trophy 1958)."
      },
      {
        "id": "designer_luke_hobbs",
        "name_key": "designer.luke_hobbs.name",
        "title_key": "designer.luke_hobbs.title",
        "company_id": "pratt_whitney",
        "active_years": [
          1945,
          1958
        ],
        "specialty": "twin_spool_high_pressure_compressors",
        "research_branch_bonuses": {
          "propulsion": 0.15
        },
        "design_modifiers": {
          "cd0_refinement_factor": 1.0,
          "prototype_build_time_factor": 0.94,
          "structural_mass_factor": 1.0
        },
        "historical_note": "Pratt & Whitney VP of Engineering who conceived the twin-spool J57 (JT3) and won the 1952 Collier Trophy."
      },
      {
        "id": "designer_ronald_hazen",
        "name_key": "designer.ronald_hazen.name",
        "title_key": "designer.ronald_hazen.title",
        "company_id": "allison",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "production_turbojet_reliability",
        "research_branch_bonuses": {
          "propulsion": 0.1,
          "manufacturing": 0.08
        },
        "design_modifiers": {
          "cd0_refinement_factor": 1.0,
          "prototype_build_time_factor": 0.95,
          "structural_mass_factor": 1.0
        },
        "historical_note": "Director of Engineering at Allison Division of GM overseeing J33, J35, J71, and T56."
      },
      {
        "id": "designer_reinout_kroon",
        "name_key": "designer.reinout_kroon.name",
        "title_key": "designer.reinout_kroon.title",
        "company_id": "westinghouse",
        "active_years": [
          1945,
          1955
        ],
        "specialty": "compact_axial_compressors",
        "research_branch_bonuses": {
          "propulsion": 0.08
        },
        "design_modifiers": {
          "cd0_refinement_factor": 1.0,
          "prototype_build_time_factor": 1.0,
          "structural_mass_factor": 1.0
        },
        "historical_note": "Chief Engineer of Westinghouse Aviation Gas Turbine Division (19XB/J30 and 24C/J34)."
      },
      {
        "id": "designer_william_lundquist",
        "name_key": "designer.william_lundquist.name",
        "title_key": "designer.william_lundquist.title",
        "company_id": "wright",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "licensed_turbojet_production",
        "research_branch_bonuses": {
          "propulsion": 0.08,
          "manufacturing": 0.06
        },
        "design_modifiers": {
          "cd0_refinement_factor": 1.0,
          "prototype_build_time_factor": 0.96,
          "structural_mass_factor": 1.0
        },
        "historical_note": "VP of Engineering at Wright Aeronautical overseeing J65 Sapphire industrialization."
      },
      {
        "id": "designer_custom_aero_visionary",
        "name_key": "designer.custom_aero_visionary.name",
        "title_key": "designer.custom_aero_visionary.title",
        "company_id": "preset_skunk_works_spinoff",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "rapid_prototyping_and_supersonics",
        "research_branch_bonuses": {
          "aero": 0.12,
          "testing": 0.1
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.97,
          "prototype_build_time_factor": 0.9,
          "structural_mass_factor": 0.98
        },
        "historical_note": "Custom startup chief designer archetype focused on small-team rapid prototyping and clean aerodynamics."
      },
      {
        "id": "designer_custom_production_master",
        "name_key": "designer.custom_production_master.name",
        "title_key": "designer.custom_production_master.title",
        "company_id": "preset_wartime_subcontractor",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "tooling_and_mass_production",
        "research_branch_bonuses": {
          "manufacturing": 0.14,
          "structures": 0.1
        },
        "design_modifiers": {
          "cd0_refinement_factor": 1.0,
          "prototype_build_time_factor": 0.95,
          "structural_mass_factor": 0.97
        },
        "historical_note": "Custom startup chief designer archetype focused on tooling efficiency and structural manufacturability."
      },
      {
        "id": "designer_custom_transonic_theorist",
        "name_key": "designer.custom_transonic_theorist.name",
        "title_key": "designer.custom_transonic_theorist.title",
        "company_id": "preset_naca_alumni_syndicate",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "wind_tunnel_and_transonic_theory",
        "research_branch_bonuses": {
          "aero": 0.14,
          "testing": 0.14
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.96,
          "prototype_build_time_factor": 0.98,
          "structural_mass_factor": 0.99
        },
        "historical_note": "Custom startup chief designer archetype with deep NACA wind-tunnel and compressibility background."
      },
      {
        "id": "designer_custom_systems_integrator",
        "name_key": "designer.custom_systems_integrator.name",
        "title_key": "designer.custom_systems_integrator.title",
        "company_id": "preset_industrialist_venture",
        "active_years": [
          1945,
          1960
        ],
        "specialty": "all_weather_weapon_systems",
        "research_branch_bonuses": {
          "avionics": 0.14,
          "armament": 0.1
        },
        "design_modifiers": {
          "cd0_refinement_factor": 0.99,
          "prototype_build_time_factor": 0.94,
          "structural_mass_factor": 0.99
        },
        "historical_note": "Custom startup chief designer archetype focused on radar, fire control, and guided missile integration."
      }
    ]
  },
  "engine_makers": {
    "schema_version": "1.0",
    "era": "1945-1960",
    "country": "USA",
    "description": "Historical US jet engine manufacturers (1945-1960): starting propulsion tech maturities, test facilities, engineering staff, and architectural focus.",
    "engine_makers": [
      {
        "id": "general_electric",
        "name_key": "company.general_electric.name",
        "short_name_key": "company.general_electric.short",
        "manufacturer_code_us": "GE",
        "hq_location": "Lynn, Massachusetts & Evendale, Ohio",
        "cash_usd": 40000000.0,
        "reputation": {
          "USAF": 0.92,
          "USN": 0.72,
          "export": 0.85
        },
        "propulsion_engineers": 120,
        "altitude_test_cell_level": 2,
        "chief_designer_id": "designer_gerhard_neumann",
        "starting_tech_overrides": {
          "prop_1945_centrifugal_turbojet": 0.92,
          "prop_1945_early_axial_compressor": 0.7
        },
        "architecture_focus": [
          "axial_single_spool",
          "variable_stators",
          "afterburner",
          "turbofan"
        ],
        "historical_engines_1945_1960": [
          "I-16 (J31)",
          "I-40 (J33)",
          "TG-180 (J35)",
          "J47",
          "J73",
          "J79",
          "J85",
          "J93"
        ],
        "historical_summary": "Chosen by Gen. Hap Arnold in 1941 to build Whittle's jet; developed the axial TG-180 (J35), workhorse J47 (F-86), variable-stator Mach-2 J79 (F-104, F4H-1, B-58), and Mach-3 J93."
      },
      {
        "id": "pratt_whitney",
        "name_key": "company.pratt_whitney.name",
        "short_name_key": "company.pratt_whitney.short",
        "manufacturer_code_us": "P",
        "hq_location": "East Hartford, Connecticut",
        "cash_usd": 48000000.0,
        "reputation": {
          "USAF": 0.9,
          "USN": 0.94,
          "export": 0.88
        },
        "propulsion_engineers": 135,
        "altitude_test_cell_level": 3,
        "chief_designer_id": "designer_luke_hobbs",
        "starting_tech_overrides": {
          "prop_1945_centrifugal_turbojet": 0.65,
          "prop_1945_early_axial_compressor": 0.45
        },
        "architecture_focus": [
          "twin_spool",
          "high_opr",
          "high_massflow",
          "turbofan"
        ],
        "historical_engines_1945_1960": [
          "J42 (Nene)",
          "J48 (Tay)",
          "J57 (JT3)",
          "J75 (JT4)",
          "J52",
          "J58 (JT11)",
          "TF33 (JT3D)"
        ],
        "historical_summary": "Barred from wartime jet work to focus on R-2800/R-4360 radials; licensed Rolls-Royce Nene/Tay (J42/J48) to catch up, built the Willgoos Turbine Lab, and leapfrogged the world with the twin-spool J57 and J75."
      },
      {
        "id": "allison",
        "name_key": "company.allison.name",
        "short_name_key": "company.allison.short",
        "manufacturer_code_us": "A",
        "hq_location": "Indianapolis, Indiana",
        "cash_usd": 35000000.0,
        "reputation": {
          "USAF": 0.85,
          "USN": 0.78,
          "export": 0.75
        },
        "propulsion_engineers": 95,
        "altitude_test_cell_level": 2,
        "chief_designer_id": "designer_ronald_hazen",
        "starting_tech_overrides": {
          "prop_1945_centrifugal_turbojet": 0.88,
          "prop_1945_early_axial_compressor": 0.65
        },
        "architecture_focus": [
          "centrifugal",
          "axial_single_spool",
          "turboprop"
        ],
        "historical_engines_1945_1960": [
          "J33",
          "J35",
          "J71",
          "T40",
          "T56"
        ],
        "historical_summary": "General Motors division handed mass production and development of both the J33 (P-80, F9F-2/5) and J35 (F-84, F-89) in 1945, later developing the J71 (F3H-2, B-66)."
      },
      {
        "id": "westinghouse",
        "name_key": "company.westinghouse.name",
        "short_name_key": "company.westinghouse.short",
        "manufacturer_code_us": "WE",
        "hq_location": "Essington / South Philadelphia, Pennsylvania & Kansas City, Missouri",
        "cash_usd": 25000000.0,
        "reputation": {
          "USAF": 0.45,
          "USN": 0.86,
          "export": 0.5
        },
        "propulsion_engineers": 75,
        "altitude_test_cell_level": 1,
        "chief_designer_id": "designer_reinout_kroon",
        "starting_tech_overrides": {
          "prop_1945_centrifugal_turbojet": 0.6,
          "prop_1945_early_axial_compressor": 0.75
        },
        "architecture_focus": [
          "axial_single_spool",
          "afterburner"
        ],
        "historical_engines_1945_1960": [
          "J30 (19XB)",
          "J34 (24C)",
          "J46",
          "J40"
        ],
        "historical_summary": "Pioneered indigenous US axial-flow turbojets for the Navy (J30 on FH-1, J34 on F2H/F3D/F7U), but catastrophic development delays on the ambitious J40 crippled a generation of USN fighters."
      },
      {
        "id": "wright",
        "name_key": "company.wright.name",
        "short_name_key": "company.wright.short",
        "manufacturer_code_us": "W",
        "hq_location": "Wood-Ridge, New Jersey",
        "cash_usd": 28000000.0,
        "reputation": {
          "USAF": 0.75,
          "USN": 0.75,
          "export": 0.7
        },
        "propulsion_engineers": 70,
        "altitude_test_cell_level": 1,
        "chief_designer_id": "designer_william_lundquist",
        "starting_tech_overrides": {
          "prop_1945_centrifugal_turbojet": 0.65,
          "prop_1945_early_axial_compressor": 0.5
        },
        "architecture_focus": [
          "axial_single_spool"
        ],
        "historical_engines_1945_1960": [
          "XJ37",
          "J65 (Sapphire)",
          "J67 (Olympus)"
        ],
        "historical_summary": "Engine arm of Curtiss-Wright; entered the jet race late by licensing the Armstrong Siddeley Sapphire as the Wright J65 (powering the F-84F, B-57, FJ-3/4, F11F-1, and A4D-1/2)."
      }
    ]
  },
  "startup_presets": {
    "schema_version": "1.0",
    "era": "1945-1960",
    "description": "Custom player-founded aircraft company startup presets for 1945-01-01 campaign start.",
    "presets": [
      {
        "id": "preset_skunk_works_spinoff",
        "name_key": "preset.skunk_works_spinoff.name",
        "desc_key": "preset.skunk_works_spinoff.desc",
        "default_hq_location": "Burbank / Mojave, California",
        "company_code_usn": "X",
        "cash_usd": 12000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.65,
          "USN": 0.55,
          "export": 0.45
        },
        "political_capital": 0.55,
        "engineers": {
          "aero": 38,
          "structures": 32,
          "propulsion": 14,
          "systems": 26
        },
        "facilities": {
          "wind_tunnel_level": 1,
          "factory_floor_m2": 65000.0,
          "test_site": true
        },
        "starting_tech_overrides": {
          "aero_1945_compressible_subsonic": 0.94,
          "prop_1945_early_axial_compressor": 0.65
        },
        "chief_designer_id": "designer_custom_aero_visionary"
      },
      {
        "id": "preset_wartime_subcontractor",
        "name_key": "preset.wartime_subcontractor.name",
        "desc_key": "preset.wartime_subcontractor.desc",
        "default_hq_location": "Wichita, Kansas",
        "company_code_usn": "W",
        "cash_usd": 22000000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.6,
          "USN": 0.6,
          "export": 0.5
        },
        "political_capital": 0.68,
        "engineers": {
          "aero": 26,
          "structures": 44,
          "propulsion": 10,
          "systems": 22
        },
        "facilities": {
          "wind_tunnel_level": 0,
          "factory_floor_m2": 160000.0,
          "test_site": false
        },
        "starting_tech_overrides": {
          "mfg_1945_ww2_mass_production_line": 0.95,
          "struct_1945_stressed_skin_7075": 0.92
        },
        "chief_designer_id": "designer_custom_production_master"
      },
      {
        "id": "preset_naca_alumni_syndicate",
        "name_key": "preset.naca_alumni_syndicate.name",
        "desc_key": "preset.naca_alumni_syndicate.desc",
        "default_hq_location": "Hampton, Virginia",
        "company_code_usn": "A",
        "cash_usd": 9500000.0,
        "debt_usd": 0.0,
        "reputation": {
          "USAF": 0.55,
          "USN": 0.55,
          "export": 0.35
        },
        "political_capital": 0.45,
        "engineers": {
          "aero": 45,
          "structures": 28,
          "propulsion": 16,
          "systems": 24
        },
        "facilities": {
          "wind_tunnel_level": 2,
          "factory_floor_m2": 48000.0,
          "test_site": false
        },
        "starting_tech_overrides": {
          "aero_1945_compressible_subsonic": 0.96,
          "test_1945_sub_and_supersonic_blowdown_tunnels": 0.95
        },
        "chief_designer_id": "designer_custom_transonic_theorist"
      },
      {
        "id": "preset_industrialist_venture",
        "name_key": "preset.industrialist_venture.name",
        "desc_key": "preset.industrialist_venture.desc",
        "default_hq_location": "Culver City, California",
        "company_code_usn": "K",
        "cash_usd": 30000000.0,
        "debt_usd": 4000000.0,
        "reputation": {
          "USAF": 0.48,
          "USN": 0.48,
          "export": 0.6
        },
        "political_capital": 0.72,
        "engineers": {
          "aero": 32,
          "structures": 32,
          "propulsion": 14,
          "systems": 36
        },
        "facilities": {
          "wind_tunnel_level": 1,
          "factory_floor_m2": 120000.0,
          "test_site": true
        },
        "starting_tech_overrides": {
          "av_1945_vhf_gyro_sight_scr720": 0.92
        },
        "chief_designer_id": "designer_custom_systems_integrator"
      }
    ]
  },
  "tech_nodes": {
    "schema_version": "1.0",
    "era": "1945-1960",
    "description": "Detailed US Jet Age technology tree (1945-1960) across 7 branches: aero, structures, propulsion, avionics, armament, manufacturing, testing.",
    "nodes": [
      {
        "id": "aero_1945_compressible_subsonic",
        "name_key": "tech.aero_1945_compressible_subsonic.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1944.0,
        "historical_date": "1944-01-01",
        "granted_at_start": true,
        "initial_maturity": 0.9,
        "prereqs": [],
        "cost_eng_days": 600,
        "cost_usd": 45000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "aero.wing_sweep_max_deg": 10.0,
          "aero.thin_wing_tc_min": 0.12,
          "aero.fowler_flaps": true,
          "aero.t_tail": true
        },
        "historical_note": "NACA 6-series laminar-flow airfoils, Prandtl-Glauert compressibility correction, and WWII high-speed dive recovery flaps (P-80A, FH-1)."
      },
      {
        "id": "aero_1945_swept_wing_theory",
        "name_key": "tech.aero_1945_swept_wing_theory.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1945.5,
        "historical_date": "1945-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "aero_1945_compressible_subsonic"
        ],
        "cost_eng_days": 1800,
        "cost_usd": 140000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "aero.wing_sweep_max_deg": 35.0,
          "testing.flaw_incidence.pitch_up": 0.92
        },
        "historical_note": "Robert T. Jones NACA TN-1033 (1945) & Operation Lusty German Busemann/Lippisch data enabling 35-deg swept wings (XP-86, XF-88)."
      },
      {
        "id": "aero_1946_auto_le_slats",
        "name_key": "tech.aero_1946_auto_le_slats.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1946.5,
        "historical_date": "1946-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "aero_1945_swept_wing_theory"
        ],
        "cost_eng_days": 1400,
        "cost_usd": 110000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "aero.le_slats": true,
          "testing.flaw_incidence.pitch_up": 0.85,
          "testing.flaw_incidence.spin": 0.88
        },
        "historical_note": "Aerodynamically actuated leading-edge slats derived from Me 262 experience, taming swept-wing tip stall on the F-86A Sabre."
      },
      {
        "id": "aero_1947_thin_airfoils_10pct",
        "name_key": "tech.aero_1947_thin_airfoils_10pct.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1947.0,
        "historical_date": "1947-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "aero_1945_compressible_subsonic",
          "struct_1946_thick_skin_box_spar"
        ],
        "cost_eng_days": 1600,
        "cost_usd": 125000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "aero.thin_wing_tc_min": 0.09
        },
        "historical_note": "NACA 64A/65A-series transonic sections down to 9-10% t/c with straight trailing-edge slopes (Bell X-1 8%/10% wing, F-86 9.5% root)."
      },
      {
        "id": "aero_1948_all_moving_tail",
        "name_key": "tech.aero_1948_all_moving_tail.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1948.0,
        "historical_date": "1948-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "aero_1945_swept_wing_theory",
          "sys_1946_hydraulic_boost_controls"
        ],
        "cost_eng_days": 2200,
        "cost_usd": 180000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "aero.all_moving_tail": true,
          "testing.flaw_incidence.transonic_control_loss": 0.55
        },
        "historical_note": "Bell X-1 movable horizontal stabilizer discovery (1947) and F-86E 'flying tail' solving transonic shock-induced elevator lock."
      },
      {
        "id": "aero_1948_tailless_delta_basics",
        "name_key": "tech.aero_1948_tailless_delta_basics.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1948.5,
        "historical_date": "1948-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.3,
        "prereqs": [
          "aero_1945_swept_wing_theory"
        ],
        "cost_eng_days": 2600,
        "cost_usd": 220000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "aero.delta_wing": true,
          "aero.wing_sweep_max_deg": 60.0,
          "aero.aspect_ratio_min": 2.0
        },
        "historical_note": "Convair XF-92A (1948) and Douglas XF4D-1 Skyray pioneering low-aspect-ratio 60-deg delta and modified-delta planforms."
      },
      {
        "id": "aero_1949_subsonic_duct_splitters",
        "name_key": "tech.aero_1949_subsonic_duct_splitters.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1949.0,
        "historical_date": "1949-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "aero_1945_compressible_subsonic"
        ],
        "cost_eng_days": 1500,
        "cost_usd": 115000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "aero.inlet_pressure_recovery_bonus": 0.02,
          "testing.flaw_incidence.inlet": 0.8
        },
        "historical_note": "NACA boundary-layer diverters and cheek/wing-root splitter plates preventing fuselage boundary-layer ingestion."
      },
      {
        "id": "aero_1950_high_sweep_45deg",
        "name_key": "tech.aero_1950_high_sweep_45deg.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1950.5,
        "historical_date": "1950-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "aero_1945_swept_wing_theory",
          "aero_1947_thin_airfoils_10pct"
        ],
        "cost_eng_days": 2400,
        "cost_usd": 195000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "aero.wing_sweep_max_deg": 45.0,
          "aero.thin_wing_tc_min": 0.06,
          "testing.flaw_incidence.pitch_up": 0.85
        },
        "historical_note": "45-deg quarter-chord sweep with 6-7% t/c airfoils for supersonic level flight (North American YF-100A, Vought XF8U-1)."
      },
      {
        "id": "aero_1951_le_droop_krueger_flaps",
        "name_key": "tech.aero_1951_le_droop_krueger_flaps.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1951.0,
        "historical_date": "1951-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "aero_1946_auto_le_slats",
          "aero_1947_thin_airfoils_10pct"
        ],
        "cost_eng_days": 1500,
        "cost_usd": 120000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "aero.le_flaps": true,
          "testing.flaw_incidence.spin": 0.88
        },
        "historical_note": "Full-span leading-edge camber droop and Krueger flaps restoring CLmax on sharp-nosed thin supersonic wings."
      },
      {
        "id": "aero_1951_variable_sweep_exp",
        "name_key": "tech.aero_1951_variable_sweep_exp.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1951.5,
        "historical_date": "1951-06-20",
        "granted_at_start": false,
        "initial_maturity": 0.25,
        "prereqs": [
          "aero_1950_high_sweep_45deg"
        ],
        "cost_eng_days": 3800,
        "cost_usd": 360000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "aero.variable_sweep": true
        },
        "historical_note": "Bell X-5 (1951) and Grumman XF10F-1 Jaguar translating-pivot variable-sweep mechanisms; heavy and mechanically complex in the 1950s."
      },
      {
        "id": "aero_1952_whitcomb_area_rule",
        "name_key": "tech.aero_1952_whitcomb_area_rule.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1952.5,
        "historical_date": "1952-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "test_1950_slotted_transonic_tunnel"
        ],
        "cost_eng_days": 2800,
        "cost_usd": 240000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "aero.area_rule": true,
          "aero.wave_drag_area_rule_eff": 0.6
        },
        "historical_note": "Richard Whitcomb's NACA RM-L52H08 transonic area rule ('wasp waist'), cutting transonic wave drag by ~50-60% on YF-102A and F11F-1."
      },
      {
        "id": "aero_1953_supersonic_spike_inlet",
        "name_key": "tech.aero_1953_supersonic_spike_inlet.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1953.0,
        "historical_date": "1953-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "aero_1949_subsonic_duct_splitters"
        ],
        "cost_eng_days": 2200,
        "cost_usd": 185000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "aero.inlet_spike": true,
          "aero.inlet_pressure_recovery_bonus": 0.015,
          "testing.flaw_incidence.inlet": 0.85
        },
        "historical_note": "Ferri/NACA oblique-shock cone and half-cone inlets (Lockheed XF-104 fixed shock cones) for efficient pressure recovery above M1.4."
      },
      {
        "id": "aero_1953_razor_thin_wing_3pct",
        "name_key": "tech.aero_1953_razor_thin_wing_3pct.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1953.5,
        "historical_date": "1953-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "aero_1950_high_sweep_45deg",
          "struct_1952_integrally_stiffened_skins"
        ],
        "cost_eng_days": 2700,
        "cost_usd": 230000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "aero.thin_wing_tc_min": 0.034,
          "aero.aspect_ratio_min": 2.2
        },
        "historical_note": "Biconvex 3.36% t/c low-aspect-ratio supersonic wings (Douglas X-3, Lockheed XF-104 Starfighter) minimizing supersonic wave drag."
      },
      {
        "id": "aero_1954_vortex_generators_excrescence",
        "name_key": "tech.aero_1954_vortex_generators_excrescence.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1954.0,
        "historical_date": "1954-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.45,
        "prereqs": [
          "aero_1950_high_sweep_45deg"
        ],
        "cost_eng_days": 1400,
        "cost_usd": 105000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "aero.drag_skin_factor": 0.96,
          "testing.flaw_incidence.transonic_control_loss": 0.85,
          "testing.flaw_incidence.pitch_up": 0.88
        },
        "historical_note": "Wing fences, sawtooth leading edges, vortex generators, and flush antenna fairings reducing interference/excrescence drag and shock-induced separation."
      },
      {
        "id": "aero_1955_conical_camber",
        "name_key": "tech.aero_1955_conical_camber.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1955.0,
        "historical_date": "1955-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "aero_1948_tailless_delta_basics",
          "aero_1952_whitcomb_area_rule"
        ],
        "cost_eng_days": 2000,
        "cost_usd": 165000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "aero.conical_camber": true,
          "aero.aspect_ratio_min": 1.8
        },
        "historical_note": "NACA conical camber leading edge for delta wings (production F-102A, F-106A, B-58), substantially cutting induced drag at high altitude."
      },
      {
        "id": "aero_1955_blc_blown_flaps",
        "name_key": "tech.aero_1955_blc_blown_flaps.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1955.5,
        "historical_date": "1955-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "aero_1951_le_droop_krueger_flaps",
          "prop_1952_twin_spool_compressor"
        ],
        "cost_eng_days": 2400,
        "cost_usd": 210000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "aero.blown_flaps": true
        },
        "historical_note": "Compressor-bleed boundary-layer control (BLC) blowing over trailing-edge flaps (F-104C/G, F4H-1 Phantom II) cutting approach speeds by 15-20 kt."
      },
      {
        "id": "aero_1955_variable_geometry_inlet",
        "name_key": "tech.aero_1955_variable_geometry_inlet.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1955.5,
        "historical_date": "1955-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.3,
        "prereqs": [
          "aero_1953_supersonic_spike_inlet"
        ],
        "cost_eng_days": 3000,
        "cost_usd": 275000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "aero.inlet_variable": true,
          "aero.inlet_pressure_recovery_bonus": 0.025,
          "testing.flaw_incidence.inlet": 0.78
        },
        "historical_note": "Multi-shock variable-angle external/internal compression ramps and translating cones with boundary-layer bleed (F-105, F-106, F-107A, F4H-1) for Mach 2+."
      },
      {
        "id": "aero_1956_supersonic_area_rule",
        "name_key": "tech.aero_1956_supersonic_area_rule.name",
        "branch": "aero",
        "discipline": "aero",
        "historical_year": 1956.0,
        "historical_date": "1956-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "aero_1952_whitcomb_area_rule",
          "aero_1954_vortex_generators_excrescence"
        ],
        "cost_eng_days": 2900,
        "cost_usd": 255000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "aero.wave_drag_area_rule_eff": 0.8,
          "aero.drag_skin_factor": 0.97
        },
        "historical_note": "Jones/Whitcomb Mach-cone oblique-plane supersonic area rule optimizing cross-sectional distribution for Mach 1.5-2.2 cruise/dash (F-106A, F8U-3)."
      },
      {
        "id": "struct_1945_stressed_skin_7075",
        "name_key": "tech.struct_1945_stressed_skin_7075.name",
        "branch": "structures",
        "discipline": "structures",
        "historical_year": 1944.0,
        "historical_date": "1944-01-01",
        "granted_at_start": true,
        "initial_maturity": 0.9,
        "prereqs": [],
        "cost_eng_days": 600,
        "cost_usd": 40000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "struct.material.al7075_available": true,
          "struct.max_skin_temp_K": 410.0,
          "struct.design_load_max_g": 8.0
        },
        "historical_note": "Alcoa 75S (7075-T6) high-strength aluminum alloy semi-monocoque construction and 8.0g USAAF fighter limit load standards."
      },
      {
        "id": "struct_1946_thick_skin_box_spar",
        "name_key": "tech.struct_1946_thick_skin_box_spar.name",
        "branch": "structures",
        "discipline": "structures",
        "historical_year": 1946.5,
        "historical_date": "1946-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "struct_1945_stressed_skin_7075"
        ],
        "cost_eng_days": 1700,
        "cost_usd": 135000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "struct.weight_factor": 0.97,
          "testing.flaw_incidence.aileron_reversal": 0.8,
          "testing.flaw_incidence.flutter": 0.88
        },
        "historical_note": "Double-skinned torsion-box wing structure with tapered heavy aluminum plates (F-86 Sabre), resisting aeroelastic twist on swept wings."
      },
      {
        "id": "struct_1948_jet_carrier_suitability",
        "name_key": "tech.struct_1948_jet_carrier_suitability.name",
        "branch": "structures",
        "discipline": "structures",
        "historical_year": 1948.0,
        "historical_date": "1948-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "struct_1946_thick_skin_box_spar"
        ],
        "cost_eng_days": 1900,
        "cost_usd": 150000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "struct.carrier_weight_factor": 0.9,
          "struct.design_load_max_g": 8.5
        },
        "historical_note": "BuAer jet carrier suitability standards: high-sink-rate oleo struts, hydraulic wing-fold joints, and keel-mounted arresting hooks (F2H, F9F)."
      },
      {
        "id": "struct_1951_titanium_metallurgy_1",
        "name_key": "tech.struct_1951_titanium_metallurgy_1.name",
        "branch": "structures",
        "discipline": "structures",
        "historical_year": 1951.0,
        "historical_date": "1951-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.3,
        "prereqs": [
          "struct_1946_thick_skin_box_spar"
        ],
        "cost_eng_days": 2600,
        "cost_usd": 240000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "struct.material.titanium_available": true,
          "struct.material.ti_max_fraction": 0.12,
          "struct.max_skin_temp_K": 445.0
        },
        "historical_note": "Kroll-process commercially pure and early Ti-8Mn alloy sheets for aft-fuselage afterburner heat shields and frames (X-3, F-100A, F4D-1)."
      },
      {
        "id": "struct_1952_integrally_stiffened_skins",
        "name_key": "tech.struct_1952_integrally_stiffened_skins.name",
        "branch": "structures",
        "discipline": "structures",
        "historical_year": 1952.5,
        "historical_date": "1952-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "struct_1946_thick_skin_box_spar",
          "mfg_1950_heavy_forging_presses"
        ],
        "cost_eng_days": 2300,
        "cost_usd": 200000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": false,
        "effects": {
          "struct.weight_factor": 0.95,
          "struct.design_load_max_g": 9.0,
          "testing.flaw_incidence.structural_fatigue": 0.85
        },
        "historical_note": "One-piece machined integrally stiffened wing skins eliminating thousands of rivets and sealing integral wing fuel tanks (F-100, F-104, A4D)."
      },
      {
        "id": "struct_1954_bonded_honeycomb",
        "name_key": "tech.struct_1954_bonded_honeycomb.name",
        "branch": "structures",
        "discipline": "structures",
        "historical_year": 1954.0,
        "historical_date": "1954-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "struct_1952_integrally_stiffened_skins"
        ],
        "cost_eng_days": 2400,
        "cost_usd": 210000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": false,
        "effects": {
          "struct.honeycomb": true,
          "struct.weight_factor": 0.96,
          "testing.flaw_incidence.flutter": 0.85
        },
        "historical_note": "Adhesive-bonded aluminum and fiberglass honeycomb core sandwich panels for high stiffness-to-weight control surfaces and delta wings (F-102, B-58)."
      },
      {
        "id": "struct_1955_fatigue_failsafe_design",
        "name_key": "tech.struct_1955_fatigue_failsafe_design.name",
        "branch": "structures",
        "discipline": "structures",
        "historical_year": 1955.0,
        "historical_date": "1955-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.45,
        "prereqs": [
          "struct_1952_integrally_stiffened_skins"
        ],
        "cost_eng_days": 2000,
        "cost_usd": 170000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "testing.flaw_incidence.structural_fatigue": 0.65,
          "struct.carrier_weight_factor": 0.94
        },
        "historical_note": "Fail-safe multi-load-path structural design and cyclic spectrum fatigue testing following early jet service crack discoveries."
      },
      {
        "id": "struct_1956_ti_6al_4v_structural",
        "name_key": "tech.struct_1956_ti_6al_4v_structural.name",
        "branch": "structures",
        "discipline": "structures",
        "historical_year": 1956.0,
        "historical_date": "1956-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "struct_1951_titanium_metallurgy_1",
          "mfg_1954_titanium_forming_chem_mill"
        ],
        "cost_eng_days": 3000,
        "cost_usd": 280000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "struct.material.ti_max_fraction": 0.3,
          "struct.max_skin_temp_K": 495.0,
          "struct.weight_factor": 0.96
        },
        "historical_note": "Vacuum-melted Ti-6Al-4V alpha-beta alloy forgings and skins solving hydrogen embrittlement (F8U-1/2/3, F-101B, F4H-1)."
      },
      {
        "id": "struct_1958_ph_stainless_brazed_thermal",
        "name_key": "tech.struct_1958_ph_stainless_brazed_thermal.name",
        "branch": "structures",
        "discipline": "structures",
        "historical_year": 1958.0,
        "historical_date": "1958-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.3,
        "prereqs": [
          "struct_1954_bonded_honeycomb",
          "struct_1956_ti_6al_4v_structural"
        ],
        "cost_eng_days": 3600,
        "cost_usd": 350000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "struct.material.steel_max_fraction": 0.65,
          "struct.material.ti_max_fraction": 0.5,
          "struct.max_skin_temp_K": 585.0
        },
        "historical_note": "PH 15-7Mo precipitation-hardening stainless steel brazed honeycomb and high-fraction titanium for sustained Mach 2.4-3.0 thermal structures (XF-108, YF-12/A-12)."
      },
      {
        "id": "prop_1945_centrifugal_turbojet",
        "name_key": "tech.prop_1945_centrifugal_turbojet.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1944.0,
        "historical_date": "1944-01-01",
        "granted_at_start": true,
        "initial_maturity": 0.85,
        "prereqs": [],
        "cost_eng_days": 800,
        "cost_usd": 60000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "engine.centrifugal_compressor": true,
          "engine.tit_max_K": 1090.0,
          "engine.opr_max": 4.2,
          "engine.eta_compressor_poly": 0.8,
          "engine.eta_turbine_poly": 0.85,
          "engine.mass_flow_max_kgps": 40.0
        },
        "historical_note": "Whittle/GE I-40 (Allison J33) double-sided centrifugal turbojet with Hastelloy-B/Vitallium hot section."
      },
      {
        "id": "prop_1945_early_axial_compressor",
        "name_key": "tech.prop_1945_early_axial_compressor.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1945.0,
        "historical_date": "1945-01-01",
        "granted_at_start": true,
        "initial_maturity": 0.55,
        "prereqs": [],
        "cost_eng_days": 1000,
        "cost_usd": 80000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "engine.axial_compressor": true,
          "engine.opr_max": 5.0,
          "engine.opr_max_single_spool_fixed": 5.0,
          "engine.eta_compressor_poly": 0.83,
          "engine.eta_turbine_poly": 0.86
        },
        "historical_note": "NACA 8-stage axial compressor cascade research & GE TG-180 (J35) / Westinghouse 19XB (J30/J34) single-spool axial turbojets."
      },
      {
        "id": "prop_1947_nimonic_superalloys_1",
        "name_key": "tech.prop_1947_nimonic_superalloys_1.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1947.0,
        "historical_date": "1947-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "prop_1945_early_axial_compressor"
        ],
        "cost_eng_days": 2000,
        "cost_usd": 175000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "engine.tit_max_K": 1135.0,
          "engine.mtbf_factor": 1.25
        },
        "historical_note": "S-816 cobalt-base and Inconel X/Nimonic 80A wrought nickel-chromium turbine buckets enabling J47 and J48 durability."
      },
      {
        "id": "prop_1948_afterburner_1",
        "name_key": "tech.prop_1948_afterburner_1.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1948.0,
        "historical_date": "1948-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.3,
        "prereqs": [
          "prop_1945_early_axial_compressor",
          "prop_1947_nimonic_superalloys_1"
        ],
        "cost_eng_days": 2400,
        "cost_usd": 210000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "engine.afterburner": true,
          "engine.afterburner_temp_max_K": 1750.0
        },
        "historical_note": "NACA Lewis tailpipe reheat flameholders and two-position clamshell eyelids (Solar/Westinghouse J34-WE-32 on XF6U-1, F-94A, F-89A)."
      },
      {
        "id": "prop_1949_multi_stage_axial_refinement",
        "name_key": "tech.prop_1949_multi_stage_axial_refinement.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1949.0,
        "historical_date": "1949-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "prop_1945_early_axial_compressor"
        ],
        "cost_eng_days": 2200,
        "cost_usd": 190000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "engine.opr_max": 7.0,
          "engine.opr_max_single_spool_fixed": 7.0,
          "engine.eta_compressor_poly": 0.855,
          "engine.mass_flow_max_kgps": 65.0,
          "testing.flaw_incidence.engine_stall": 0.85
        },
        "historical_note": "12-stage fixed-geometry axial compressors with interstage bleed valves (GE J47-GE-13/27, Allison J35-A-29, Wright J65)."
      },
      {
        "id": "prop_1950_component_altitude_test_cells",
        "name_key": "tech.prop_1950_component_altitude_test_cells.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1950.0,
        "historical_date": "1950-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.45,
        "prereqs": [
          "prop_1949_multi_stage_axial_refinement"
        ],
        "cost_eng_days": 1900,
        "cost_usd": 180000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "engine.dev_cost_factor": 0.9,
          "engine.dev_risk_factor": 0.85,
          "testing.flaw_incidence.engine_stall": 0.82
        },
        "historical_note": "P&W Willgoos Turbine Lab and NACA Lewis Propulsion Systems Lab refrigerated high-altitude test cells preventing costly flight-test surprises."
      },
      {
        "id": "prop_1952_twin_spool_compressor",
        "name_key": "tech.prop_1952_twin_spool_compressor.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1952.0,
        "historical_date": "1952-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "prop_1949_multi_stage_axial_refinement",
          "prop_1950_component_altitude_test_cells"
        ],
        "cost_eng_days": 3400,
        "cost_usd": 320000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "engine.twin_spool": true,
          "engine.opr_max": 12.5,
          "engine.eta_compressor_poly": 0.875,
          "engine.eta_turbine_poly": 0.88,
          "engine.mass_flow_max_kgps": 85.0,
          "testing.flaw_incidence.engine_stall": 0.8
        },
        "historical_note": "Pratt & Whitney JT3 / J57 split-compressor (two-spool) architecture achieving OPR 11.5-12.5 without low-RPM compressor surge (Collier Trophy 1952)."
      },
      {
        "id": "prop_1953_modulated_afterburner",
        "name_key": "tech.prop_1953_modulated_afterburner.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1953.0,
        "historical_date": "1953-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "prop_1948_afterburner_1",
          "prop_1949_multi_stage_axial_refinement"
        ],
        "cost_eng_days": 2400,
        "cost_usd": 220000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "engine.afterburner_temp_max_K": 1950.0,
          "engine.mtbf_factor": 1.2
        },
        "historical_note": "Continuously variable iris/petal convergent-divergent nozzles and screech-damped flameholders (J57-P-7/P-21 on F-100/F-102)."
      },
      {
        "id": "prop_1954_waspaloy_vacuum_superalloys",
        "name_key": "tech.prop_1954_waspaloy_vacuum_superalloys.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1954.0,
        "historical_date": "1954-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "prop_1947_nimonic_superalloys_1",
          "struct_1951_titanium_metallurgy_1"
        ],
        "cost_eng_days": 2600,
        "cost_usd": 245000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "engine.tit_max_K": 1200.0,
          "engine.specific_weight_factor": 0.9,
          "engine.mtbf_factor": 1.25
        },
        "historical_note": "Vacuum-induction-melted Waspaloy/M-252 turbine blades and titanium LP compressor rotors saving ~200 kg per J57 engine."
      },
      {
        "id": "prop_1954_variable_stator_compressor",
        "name_key": "tech.prop_1954_variable_stator_compressor.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1954.5,
        "historical_date": "1954-06-08",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "prop_1949_multi_stage_axial_refinement",
          "prop_1954_waspaloy_vacuum_superalloys"
        ],
        "cost_eng_days": 3500,
        "cost_usd": 340000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "engine.variable_stators": true,
          "engine.opr_max": 13.5,
          "engine.eta_compressor_poly": 0.885,
          "engine.specific_weight_factor": 0.88,
          "testing.flaw_incidence.engine_stall": 0.78
        },
        "historical_note": "Gerhard Neumann's GE J79 17-stage single-spool compressor with variable stator vanes: high OPR (12-13.5) at far lower weight and frontal area than twin-spool."
      },
      {
        "id": "prop_1956_high_massflow_cores",
        "name_key": "tech.prop_1956_high_massflow_cores.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1956.0,
        "historical_date": "1956-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "prop_1952_twin_spool_compressor",
          "prop_1954_waspaloy_vacuum_superalloys"
        ],
        "cost_eng_days": 2800,
        "cost_usd": 270000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "engine.mass_flow_max_kgps": 125.0,
          "engine.eta_turbine_poly": 0.895,
          "engine.afterburner_temp_max_K": 2050.0,
          "engine.dev_cost_factor": 0.92,
          "engine.dev_risk_factor": 0.88
        },
        "historical_note": "NACA transonic compressor rotor blading enabling 24,500 lbf class high-airflow cores (Pratt & Whitney J75 / JT4A on F-105, F-106)."
      },
      {
        "id": "prop_1958_cooled_turbine_blades",
        "name_key": "tech.prop_1958_cooled_turbine_blades.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1958.0,
        "historical_date": "1958-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.3,
        "prereqs": [
          "prop_1954_waspaloy_vacuum_superalloys",
          "prop_1956_high_massflow_cores"
        ],
        "cost_eng_days": 3600,
        "cost_usd": 360000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "engine.cooled_turbine_blades": true,
          "engine.tit_max_K": 1340.0,
          "engine.afterburner_temp_max_K": 2120.0
        },
        "historical_note": "Internal convection air-cooled HP turbine vanes and blades (J58, J93, late J79), pushing TIT beyond uncooled alloy melting limits."
      },
      {
        "id": "prop_1959_low_bypass_turbofan",
        "name_key": "tech.prop_1959_low_bypass_turbofan.name",
        "branch": "propulsion",
        "discipline": "propulsion",
        "historical_year": 1959.0,
        "historical_date": "1959-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.3,
        "prereqs": [
          "prop_1952_twin_spool_compressor",
          "prop_1956_high_massflow_cores"
        ],
        "cost_eng_days": 3800,
        "cost_usd": 380000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "engine.low_bypass_turbofan": true,
          "engine.bypass_ratio_max": 1.4,
          "engine.opr_max": 16.0
        },
        "historical_note": "Front-fan / aft-fan turbofan architectures (P&W JT3D / TF33, GE CJ805-23, early TF30 studies) slashing subsonic cruise TSFC."
      },
      {
        "id": "av_1945_vhf_gyro_sight_scr720",
        "name_key": "tech.av_1945_vhf_gyro_sight_scr720.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1944.0,
        "historical_date": "1944-01-01",
        "granted_at_start": true,
        "initial_maturity": 0.85,
        "prereqs": [],
        "cost_eng_days": 600,
        "cost_usd": 45000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "avionics.radar_search": true,
          "avionics.level_max": 1,
          "systems.pressurized_cockpit": true,
          "unlock.radar.scr720": true,
          "unlock.radar.apg5": true
        },
        "historical_note": "WWII SCR-522 VHF radio, Mk 18 / K-14 lead-computing gyro sight, cockpit pressurization, SCR-720 night-fighter AI radar, and AN/APG-5 gun-ranging radar."
      },
      {
        "id": "sys_1946_hydraulic_boost_controls",
        "name_key": "tech.sys_1946_hydraulic_boost_controls.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1946.0,
        "historical_date": "1946-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.45,
        "prereqs": [
          "av_1945_vhf_gyro_sight_scr720"
        ],
        "cost_eng_days": 1600,
        "cost_usd": 120000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "systems.powered_controls": true,
          "testing.flaw_incidence.aileron_reversal": 0.85,
          "testing.flaw_incidence.transonic_control_loss": 0.8
        },
        "historical_note": "3,000 psi irreversible hydraulic flight control actuators with artificial feel (F-86, F-84E, F-100), overcoming transonic hinge moments."
      },
      {
        "id": "sys_1946_ejection_seat",
        "name_key": "tech.sys_1946_ejection_seat.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1946.5,
        "historical_date": "1946-08-01",
        "granted_at_start": false,
        "initial_maturity": 0.45,
        "prereqs": [
          "av_1945_vhf_gyro_sight_scr720"
        ],
        "cost_eng_days": 1200,
        "cost_usd": 90000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "systems.ejection_seat": true
        },
        "historical_note": "Ballistic catapult pilot ejection seat (tested on P-61B and FJ-1 in 1946); mandatory for high-speed jet bailout."
      },
      {
        "id": "av_1946_xband_navy_ai_radar",
        "name_key": "tech.av_1946_xband_navy_ai_radar.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1946.5,
        "historical_date": "1946-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "av_1945_vhf_gyro_sight_scr720"
        ],
        "cost_eng_days": 1700,
        "cost_usd": 135000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "unlock.radar.aps19": true
        },
        "historical_note": "Sperry AN/APS-19 3-cm X-band radar allowing single-seat carrier night fighters (F4U-5N, F2H-2N)."
      },
      {
        "id": "av_1948_radar_ranging_gunsight",
        "name_key": "tech.av_1948_radar_ranging_gunsight.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1948.0,
        "historical_date": "1948-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "av_1945_vhf_gyro_sight_scr720"
        ],
        "cost_eng_days": 1800,
        "cost_usd": 145000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "avionics.level_max": 2,
          "unlock.radar.apg30": true
        },
        "historical_note": "Sperry A-1CM / A-4 analog computing sight coupled to GE AN/APG-30 automatic rangefinder radar (F-86A/E/F)."
      },
      {
        "id": "sys_1949_stability_augmentation_sas",
        "name_key": "tech.sys_1949_stability_augmentation_sas.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1949.0,
        "historical_date": "1949-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "sys_1946_hydraulic_boost_controls"
        ],
        "cost_eng_days": 2000,
        "cost_usd": 165000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "systems.stability_augmentation": true,
          "testing.flaw_incidence.inertia_coupling": 0.75,
          "testing.flaw_incidence.spin": 0.85
        },
        "historical_note": "Rate-gyro yaw and pitch dampers (first flown on Boeing XB-47 and Northrop F-89) suppressing Dutch roll and gun-platform oscillation."
      },
      {
        "id": "av_1949_all_weather_fcs_e1",
        "name_key": "tech.av_1949_all_weather_fcs_e1.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1949.5,
        "historical_date": "1949-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "av_1946_xband_navy_ai_radar",
          "av_1948_radar_ranging_gunsight"
        ],
        "cost_eng_days": 2400,
        "cost_usd": 210000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "avionics.level_max": 3,
          "unlock.radar.apg33": true,
          "unlock.radar.aps21": true
        },
        "historical_note": "Hughes E-1 (AN/APG-33) and Westinghouse AN/APS-21 automatic radar target tracking and lead-pursuit steering display (F-94A/B, F-89B/C, F3D-2)."
      },
      {
        "id": "sys_1950_inflight_refueling",
        "name_key": "tech.sys_1950_inflight_refueling.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1950.5,
        "historical_date": "1950-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.45,
        "prereqs": [
          "av_1945_vhf_gyro_sight_scr720"
        ],
        "cost_eng_days": 1400,
        "cost_usd": 110000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "systems.inflight_refuel": true
        },
        "historical_note": "Flight Refuelling probe-and-drogue and Boeing flying-boom receptacles (tested operationally on F-80C and F-84G)."
      },
      {
        "id": "av_1951_lead_collision_fcs_e4",
        "name_key": "tech.av_1951_lead_collision_fcs_e4.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1951.5,
        "historical_date": "1951-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.3,
        "prereqs": [
          "av_1949_all_weather_fcs_e1",
          "sys_1949_stability_augmentation_sas"
        ],
        "cost_eng_days": 2800,
        "cost_usd": 250000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "avionics.lead_collision_fcs": true,
          "avionics.level_max": 4,
          "unlock.radar.apg37": true,
          "unlock.radar.apg40": true
        },
        "historical_note": "Hughes E-4/E-5/E-9 (AN/APG-37 and AN/APG-40) analog fire-control computers steering interceptors onto a single-pass collision course to automatically ripple-fire FFAR rockets (F-86D, F-94C, F-89D)."
      },
      {
        "id": "av_1954_subminiature_tubes_pcb",
        "name_key": "tech.av_1954_subminiature_tubes_pcb.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1954.0,
        "historical_date": "1954-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "av_1951_lead_collision_fcs_e4"
        ],
        "cost_eng_days": 2100,
        "cost_usd": 185000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "avionics.radar_mass_factor": 0.88,
          "avionics.reliability_factor": 1.35,
          "testing.flaw_incidence.systems": 0.82
        },
        "historical_note": "Mil-spec subminiature vacuum tubes, potted modules, and etched printed-circuit boards reducing avionics weight and vibration failures."
      },
      {
        "id": "av_1955_awcs_mg10_apq50",
        "name_key": "tech.av_1955_awcs_mg10_apq50.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1955.0,
        "historical_date": "1955-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "av_1951_lead_collision_fcs_e4",
          "av_1954_subminiature_tubes_pcb"
        ],
        "cost_eng_days": 3000,
        "cost_usd": 280000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "avionics.radar_range_factor": 1.1,
          "unlock.radar.mg10": true,
          "unlock.radar.apq50": true
        },
        "historical_note": "Hughes MG-10/MG-13 AWCS (F-102A, F-101B) and Westinghouse AN/APQ-50 (F4D-1, F3H-2) coupling CW illuminators and autopilot steering for Falcon and Sparrow missiles."
      },
      {
        "id": "av_1956_sage_gci_datalink",
        "name_key": "tech.av_1956_sage_gci_datalink.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1956.5,
        "historical_date": "1956-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "av_1955_awcs_mg10_apq50"
        ],
        "cost_eng_days": 2500,
        "cost_usd": 230000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "avionics.datalink_ground": true
        },
        "historical_note": "MIT Lincoln Lab / USAF AN/FSQ-7 SAGE ground-to-air Time Division Data Link (AN/ARR-60/61), vectoring ADC interceptors hands-off to target intercept."
      },
      {
        "id": "av_1957_solid_state_transistor_avionics",
        "name_key": "tech.av_1957_solid_state_transistor_avionics.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1957.5,
        "historical_date": "1957-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "av_1954_subminiature_tubes_pcb",
          "test_1953_ibm_701_digital_computing"
        ],
        "cost_eng_days": 2900,
        "cost_usd": 270000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "avionics.radar_mass_factor": 0.85,
          "avionics.reliability_factor": 1.5,
          "research.speed_factor.systems": 1.15,
          "testing.flaw_incidence.systems": 0.78
        },
        "historical_note": "Silicon junction transistors and magnetic-core airborne digital memory replacing high-failure vacuum-tube racks."
      },
      {
        "id": "av_1958_irst_sensor",
        "name_key": "tech.av_1958_irst_sensor.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1958.0,
        "historical_date": "1958-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "av_1955_awcs_mg10_apq50",
          "arm_1955_ir_homing_gen1"
        ],
        "cost_eng_days": 2200,
        "cost_usd": 200000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "avionics.irst": true
        },
        "historical_note": "Passive lead-sulfide infrared search and track (IRST) sensors (F-101B, F-102A, F-106A, F4H-1, F8U-2N) for ECM-resistant target tracking."
      },
      {
        "id": "av_1958_integrated_digital_awcs_ma1_apq72",
        "name_key": "tech.av_1958_integrated_digital_awcs_ma1_apq72.name",
        "branch": "avionics",
        "discipline": "systems",
        "historical_year": 1958.5,
        "historical_date": "1958-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.3,
        "prereqs": [
          "av_1956_sage_gci_datalink",
          "av_1957_solid_state_transistor_avionics"
        ],
        "cost_eng_days": 3800,
        "cost_usd": 370000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "avionics.level_max": 5,
          "avionics.radar_range_factor": 1.15,
          "unlock.radar.ma1": true,
          "unlock.radar.apq72": true
        },
        "historical_note": "Hughes MA-1 Digitair (F-106A) and Westinghouse AN/APQ-72 (F4H-1 Phantom II) long-range high-power radars and integrated weapon systems."
      },
      {
        "id": "arm_1945_ww2_guns_and_hvar",
        "name_key": "tech.arm_1945_ww2_guns_and_hvar.name",
        "branch": "armament",
        "discipline": "systems",
        "historical_year": 1944.0,
        "historical_date": "1944-01-01",
        "granted_at_start": true,
        "initial_maturity": 0.9,
        "prereqs": [],
        "cost_eng_days": 500,
        "cost_usd": 35000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "armament.hardpoints_max": 6,
          "unlock.gun.an_m2_50": true,
          "unlock.gun.an_m3_20mm": true,
          "unlock.rocket.hvar_5in": true
        },
        "historical_note": "WWII standard Browning AN/M2 .50-cal machine guns, US Navy Hispano AN/M3 20mm cannon, 5-inch HVAR rockets, and 6-pylon wing racks."
      },
      {
        "id": "arm_1947_m3_high_rof_50cal",
        "name_key": "tech.arm_1947_m3_high_rof_50cal.name",
        "branch": "armament",
        "discipline": "systems",
        "historical_year": 1947.0,
        "historical_date": "1947-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.5,
        "prereqs": [
          "arm_1945_ww2_guns_and_hvar"
        ],
        "cost_eng_days": 1100,
        "cost_usd": 80000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "unlock.gun.m3_50": true
        },
        "historical_note": "Browning AN/M3 .50-caliber machine gun firing 1,200 rpm for brief jet firing windows (F-84, F-86A/E/F)."
      },
      {
        "id": "arm_1949_ffar_m24_interceptor_ordnance",
        "name_key": "tech.arm_1949_ffar_m24_interceptor_ordnance.name",
        "branch": "armament",
        "discipline": "systems",
        "historical_year": 1949.0,
        "historical_date": "1949-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "arm_1947_m3_high_rof_50cal"
        ],
        "cost_eng_days": 1700,
        "cost_usd": 135000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "unlock.gun.m24_20mm": true,
          "unlock.rocket.ffar_2_75in": true
        },
        "historical_note": "NOTS 2.75-inch Mk 4 Mighty Mouse folding-fin aerial rocket and electrically primed M24 20mm cannon for anti-bomber interception."
      },
      {
        "id": "arm_1952_revolver_and_navy_20mm_cannons",
        "name_key": "tech.arm_1952_revolver_and_navy_20mm_cannons.name",
        "branch": "armament",
        "discipline": "systems",
        "historical_year": 1952.5,
        "historical_date": "1952-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "arm_1949_ffar_m24_interceptor_ordnance"
        ],
        "cost_eng_days": 2100,
        "cost_usd": 175000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "unlock.gun.m39_20mm": true,
          "unlock.gun.mk12_20mm": true
        },
        "historical_note": "Pontiac T-160 / M39 20mm revolver cannon (tested in Korea on F-86F-2 GunVal; standard on F-100/F-101) and Colt Mk 12 20mm Navy cannon."
      },
      {
        "id": "arm_1952_labs_tactical_nuclear_delivery",
        "name_key": "tech.arm_1952_labs_tactical_nuclear_delivery.name",
        "branch": "armament",
        "discipline": "systems",
        "historical_year": 1952.5,
        "historical_date": "1952-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "arm_1947_m3_high_rof_50cal",
          "av_1948_radar_ranging_gunsight"
        ],
        "cost_eng_days": 1900,
        "cost_usd": 160000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "armament.nuclear_delivery": true,
          "armament.hardpoints_max": 8
        },
        "historical_note": "Low-Altitude Bombing System (LABS) gyro-timed over-the-shoulder toss-bombing computer and Mk 7 tactical nuclear store wiring (F-84G, F-100D, F-105)."
      },
      {
        "id": "arm_1953_internal_weapons_bay",
        "name_key": "tech.arm_1953_internal_weapons_bay.name",
        "branch": "armament",
        "discipline": "structures",
        "historical_year": 1953.0,
        "historical_date": "1953-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "arm_1949_ffar_m24_interceptor_ordnance",
          "struct_1952_integrally_stiffened_skins"
        ],
        "cost_eng_days": 2200,
        "cost_usd": 190000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "armament.internal_bay": true
        },
        "historical_note": "High-speed snap-action internal weapons bay doors and trapeze launchers eliminating external store wave drag on supersonic interceptors (F-102A, F-101B, F-105, F-106A)."
      },
      {
        "id": "arm_1954_beam_riding_sparrow1",
        "name_key": "tech.arm_1954_beam_riding_sparrow1.name",
        "branch": "armament",
        "discipline": "systems",
        "historical_year": 1954.0,
        "historical_date": "1954-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.3,
        "prereqs": [
          "av_1949_all_weather_fcs_e1",
          "arm_1949_ffar_m24_interceptor_ordnance"
        ],
        "cost_eng_days": 2400,
        "cost_usd": 220000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "armament.missile_beamrider": true,
          "unlock.missile.aim7a_sparrow1": true
        },
        "historical_note": "Project Hotshot / Sperry AAM-N-2 (AIM-7A) Sparrow I radar beam-riding air-to-air missile."
      },
      {
        "id": "arm_1955_sarh_homing_gen1_falcon",
        "name_key": "tech.arm_1955_sarh_homing_gen1_falcon.name",
        "branch": "armament",
        "discipline": "systems",
        "historical_year": 1955.0,
        "historical_date": "1955-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.3,
        "prereqs": [
          "av_1951_lead_collision_fcs_e4",
          "arm_1953_internal_weapons_bay"
        ],
        "cost_eng_days": 2800,
        "cost_usd": 260000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "armament.missile_sarh_gen": 1,
          "unlock.missile.aim4a_falcon": true
        },
        "historical_note": "Hughes MX-904 / GAR-1 (AIM-4A) Falcon first-generation semi-active radar homing interceptor missile."
      },
      {
        "id": "arm_1955_ir_homing_gen1",
        "name_key": "tech.arm_1955_ir_homing_gen1.name",
        "branch": "armament",
        "discipline": "systems",
        "historical_year": 1955.5,
        "historical_date": "1955-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "arm_1954_beam_riding_sparrow1"
        ],
        "cost_eng_days": 2600,
        "cost_usd": 235000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "armament.missile_ir_gen": 1,
          "unlock.missile.aim9b_sidewinder": true,
          "unlock.missile.aim4c_falcon": true
        },
        "historical_note": "Bill McLean's China Lake AIM-9B Sidewinder and Hughes GAR-2A (AIM-4C) uncooled lead-sulfide (PbS) rear-aspect IR homing missiles."
      },
      {
        "id": "arm_1956_m61_vulcan_rotary_cannon",
        "name_key": "tech.arm_1956_m61_vulcan_rotary_cannon.name",
        "branch": "armament",
        "discipline": "systems",
        "historical_year": 1956.0,
        "historical_date": "1956-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "arm_1952_revolver_and_navy_20mm_cannons"
        ],
        "cost_eng_days": 2500,
        "cost_usd": 230000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "unlock.gun.m61_20mm": true
        },
        "historical_note": "General Electric Project Vulcan T-171 / M61 20mm 6-barrel Gatling gun (6,000 rpm) for F-104 and F-105."
      },
      {
        "id": "arm_1957_nuclear_air_to_air_rockets",
        "name_key": "tech.arm_1957_nuclear_air_to_air_rockets.name",
        "branch": "armament",
        "discipline": "systems",
        "historical_year": 1957.0,
        "historical_date": "1957-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "arm_1952_labs_tactical_nuclear_delivery",
          "av_1955_awcs_mg10_apq50"
        ],
        "cost_eng_days": 2700,
        "cost_usd": 265000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "armament.nuclear_aam": true,
          "unlock.missile.air2a_genie": true
        },
        "historical_note": "Douglas MB-1 / AIR-2A Genie unguided nuclear rocket (1.5 kt W25 warhead, live-tested in Operation Plumbbob Shot John 1957)."
      },
      {
        "id": "arm_1958_sarh_gen2_sparrow3_nuclear_falcon",
        "name_key": "tech.arm_1958_sarh_gen2_sparrow3_nuclear_falcon.name",
        "branch": "armament",
        "discipline": "systems",
        "historical_year": 1958.5,
        "historical_date": "1958-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.3,
        "prereqs": [
          "arm_1955_sarh_homing_gen1_falcon",
          "av_1958_integrated_digital_awcs_ma1_apq72"
        ],
        "cost_eng_days": 3400,
        "cost_usd": 330000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "armament.missile_sarh_gen": 2,
          "armament.hardpoints_max": 11,
          "unlock.missile.aim7c_sparrow3": true,
          "unlock.missile.aim26a_nuclear_falcon": true
        },
        "historical_note": "Raytheon AIM-7C Sparrow III CW semi-active radar homing BVR missile (F3H-2M, F4H-1) and Hughes GAR-11 (AIM-26A) Nuclear Falcon."
      },
      {
        "id": "mfg_1945_ww2_mass_production_line",
        "name_key": "tech.mfg_1945_ww2_mass_production_line.name",
        "branch": "manufacturing",
        "discipline": "structures",
        "historical_year": 1944.0,
        "historical_date": "1944-01-01",
        "granted_at_start": true,
        "initial_maturity": 0.9,
        "prereqs": [],
        "cost_eng_days": 500,
        "cost_usd": 35000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": false,
        "effects": {
          "mfg.learning_curve_rate": 0.8
        },
        "historical_note": "T.P. Wright's 80% aircraft learning curve, master plaster lofting, and WWII moving assembly line practices."
      },
      {
        "id": "mfg_1947_flush_riveting_aerodynamic_smoothing",
        "name_key": "tech.mfg_1947_flush_riveting_aerodynamic_smoothing.name",
        "branch": "manufacturing",
        "discipline": "structures",
        "historical_year": 1947.0,
        "historical_date": "1947-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.45,
        "prereqs": [
          "mfg_1945_ww2_mass_production_line"
        ],
        "cost_eng_days": 1400,
        "cost_usd": 105000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "mfg.surface_finish_factor": 0.96,
          "mfg.quality_defect_factor": 0.92
        },
        "historical_note": "NACA coin-dimpled flush riveting and milled butt-joint skin tolerances reducing turbulent skin-friction drag on jet fighters."
      },
      {
        "id": "mfg_1949_optical_tooling_jigs",
        "name_key": "tech.mfg_1949_optical_tooling_jigs.name",
        "branch": "manufacturing",
        "discipline": "structures",
        "historical_year": 1949.0,
        "historical_date": "1949-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.45,
        "prereqs": [
          "mfg_1947_flush_riveting_aerodynamic_smoothing"
        ],
        "cost_eng_days": 1600,
        "cost_usd": 130000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": false,
        "effects": {
          "mfg.tooling_cost_factor": 0.9,
          "mfg.labor_hours_factor": 0.94,
          "testing.flaw_incidence.manufacturing": 0.85
        },
        "historical_note": "Optical alignment telescopes and collimator reference lines replacing heavy steel master gauges for swept-wing assembly jigs."
      },
      {
        "id": "mfg_1950_heavy_forging_presses",
        "name_key": "tech.mfg_1950_heavy_forging_presses.name",
        "branch": "manufacturing",
        "discipline": "structures",
        "historical_year": 1950.5,
        "historical_date": "1950-07-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "mfg_1949_optical_tooling_jigs"
        ],
        "cost_eng_days": 2200,
        "cost_usd": 210000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "mfg.labor_hours_factor": 0.93,
          "mfg.material_cost_factor": 0.95,
          "mfg.surface_finish_factor": 0.97
        },
        "historical_note": "USAF Heavy Press Program (35,000 and 50,000-ton Wyman-Gordon/Alcoa closed-die forging presses) producing single-piece wing bulkheads and spars."
      },
      {
        "id": "mfg_1953_statistical_quality_control",
        "name_key": "tech.mfg_1953_statistical_quality_control.name",
        "branch": "manufacturing",
        "discipline": "structures",
        "historical_year": 1953.0,
        "historical_date": "1953-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.45,
        "prereqs": [
          "mfg_1949_optical_tooling_jigs"
        ],
        "cost_eng_days": 1800,
        "cost_usd": 145000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": false,
        "effects": {
          "mfg.quality_defect_factor": 0.78,
          "mfg.learning_curve_rate": 0.78,
          "testing.flaw_incidence.manufacturing": 0.75
        },
        "historical_note": "MIL-Q-5923 ultrasonic/X-ray non-destructive inspection and statistical process control on Korean War surge production lines."
      },
      {
        "id": "mfg_1954_titanium_forming_chem_mill",
        "name_key": "tech.mfg_1954_titanium_forming_chem_mill.name",
        "branch": "manufacturing",
        "discipline": "structures",
        "historical_year": 1954.0,
        "historical_date": "1954-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "mfg_1950_heavy_forging_presses",
          "struct_1951_titanium_metallurgy_1"
        ],
        "cost_eng_days": 2400,
        "cost_usd": 225000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "mfg.titanium_cost_factor": 0.7,
          "mfg.material_cost_factor": 0.96,
          "mfg.surface_finish_factor": 0.98
        },
        "historical_note": "North American Aviation 'Chem-Mill' chemical etching of curved skins and heated-die inert-gas titanium forming/welding."
      },
      {
        "id": "mfg_1956_nc_machining",
        "name_key": "tech.mfg_1956_nc_machining.name",
        "branch": "manufacturing",
        "discipline": "structures",
        "historical_year": 1956.0,
        "historical_date": "1956-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.35,
        "prereqs": [
          "mfg_1950_heavy_forging_presses",
          "mfg_1953_statistical_quality_control",
          "test_1953_ibm_701_digital_computing"
        ],
        "cost_eng_days": 2900,
        "cost_usd": 280000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": true,
        "effects": {
          "mfg.nc_machining": true,
          "mfg.labor_hours_factor": 0.88,
          "mfg.tooling_cost_factor": 0.88,
          "mfg.titanium_cost_factor": 0.8,
          "mfg.learning_curve_rate": 0.76
        },
        "historical_note": "MIT Servomechanisms Lab / USAF APT punched-tape 3-axis numerically controlled (NC) skin and spar mills."
      },
      {
        "id": "test_1945_sub_and_supersonic_blowdown_tunnels",
        "name_key": "tech.test_1945_sub_and_supersonic_blowdown_tunnels.name",
        "branch": "testing",
        "discipline": "aero",
        "historical_year": 1944.0,
        "historical_date": "1944-01-01",
        "granted_at_start": true,
        "initial_maturity": 0.85,
        "prereqs": [],
        "cost_eng_days": 600,
        "cost_usd": 45000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "testing.supersonic_tunnel": true
        },
        "historical_note": "NACA high-speed subsonic tunnels (choked at M0.85-1.18) and small intermittent supersonic nozzle tunnels above M1.2."
      },
      {
        "id": "test_1946_wallops_rocket_models",
        "name_key": "tech.test_1946_wallops_rocket_models.name",
        "branch": "testing",
        "discipline": "aero",
        "historical_year": 1946.0,
        "historical_date": "1946-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.45,
        "prereqs": [
          "test_1945_sub_and_supersonic_blowdown_tunnels"
        ],
        "cost_eng_days": 1400,
        "cost_usd": 110000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "testing.rocket_model_testing": true,
          "testing.sim_sigma_factor": 0.93
        },
        "historical_note": "NACA Wallops Island Pilotless Aircraft Research Division (PARD) rocket-boosted free-flight models and wing-flow transonic bumps bridging the transonic gap before slotted tunnels."
      },
      {
        "id": "test_1948_fm_telemetry_oscillographs",
        "name_key": "tech.test_1948_fm_telemetry_oscillographs.name",
        "branch": "testing",
        "discipline": "systems",
        "historical_year": 1948.0,
        "historical_date": "1948-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.45,
        "prereqs": [
          "test_1945_sub_and_supersonic_blowdown_tunnels"
        ],
        "cost_eng_days": 1600,
        "cost_usd": 130000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "testing.flight_sigma_factor": 0.85,
          "testing.flight_test_time_factor": 0.88,
          "testing.flaw_detect_factor": 1.15
        },
        "historical_note": "NACA Muroc multi-channel strain-gauge oscillographs and FM/FM real-time radio telemetry from X-1/D-558 test flights."
      },
      {
        "id": "test_1950_slotted_transonic_tunnel",
        "name_key": "tech.test_1950_slotted_transonic_tunnel.name",
        "branch": "testing",
        "discipline": "aero",
        "historical_year": 1950.5,
        "historical_date": "1950-12-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "test_1946_wallops_rocket_models"
        ],
        "cost_eng_days": 2800,
        "cost_usd": 260000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "testing.transonic_tunnel": true,
          "testing.tunnel_sigma_factor": 0.82,
          "testing.flaw_detect_factor": 1.2,
          "research.speed_factor.aero": 1.12
        },
        "historical_note": "Ray Wright & Richard Whitcomb's NACA Langley 8-Foot and 16-Foot slotted-throat transonic wind tunnels (Collier Trophy 1951), eliminating transonic choking."
      },
      {
        "id": "test_1952_flutter_aeroelastic_analog",
        "name_key": "tech.test_1952_flutter_aeroelastic_analog.name",
        "branch": "testing",
        "discipline": "structures",
        "historical_year": 1952.0,
        "historical_date": "1952-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "test_1950_slotted_transonic_tunnel",
          "struct_1946_thick_skin_box_spar"
        ],
        "cost_eng_days": 2100,
        "cost_usd": 180000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": false,
        "effects": {
          "testing.flaw_incidence.flutter": 0.72,
          "testing.flaw_incidence.aileron_reversal": 0.78,
          "research.speed_factor.structures": 1.12
        },
        "historical_note": "Dynamic aeroelastic wind-tunnel models, ground vibration shake tests, and Reeves REAC analog computers solving coupled bending-torsion flutter equations."
      },
      {
        "id": "test_1953_ibm_701_digital_computing",
        "name_key": "tech.test_1953_ibm_701_digital_computing.name",
        "branch": "testing",
        "discipline": "aero",
        "historical_year": 1953.5,
        "historical_date": "1953-04-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "test_1950_slotted_transonic_tunnel"
        ],
        "cost_eng_days": 2600,
        "cost_usd": 250000.0,
        "naca_diffusion": false,
        "govt_contract_eligible": false,
        "effects": {
          "testing.sim_sigma_factor": 0.84,
          "testing.sim_time_factor": 0.75,
          "research.speed_factor.aero": 1.15,
          "research.speed_factor.structures": 1.15,
          "research.speed_factor.propulsion": 1.12
        },
        "historical_note": "IBM 701 'Defense Calculator' (delivered to Lockheed, North American, Douglas, Convair, Boeing, GE in 1953) and IBM 704 FORTRAN (1956) revolutionizing aero/structural matrix calculations."
      },
      {
        "id": "test_1955_inertia_coupling_6dof_sim",
        "name_key": "tech.test_1955_inertia_coupling_6dof_sim.name",
        "branch": "testing",
        "discipline": "aero",
        "historical_year": 1955.0,
        "historical_date": "1955-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.4,
        "prereqs": [
          "test_1952_flutter_aeroelastic_analog",
          "test_1953_ibm_701_digital_computing",
          "sys_1949_stability_augmentation_sas"
        ],
        "cost_eng_days": 2400,
        "cost_usd": 210000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "testing.flaw_incidence.inertia_coupling": 0.55,
          "testing.flaw_incidence.spin": 0.78,
          "testing.sim_sigma_factor": 0.9,
          "testing.flaw_detect_factor": 1.15
        },
        "historical_note": "NACA/Edwards 5-DOF & 6-DOF real-time analog-digital flight simulators following the 1954 X-3 and F-100A roll-inertia coupling accidents (validating Phillips' 1948 NACA TN-1627)."
      },
      {
        "id": "test_1957_high_speed_flight_station_datcom",
        "name_key": "tech.test_1957_high_speed_flight_station_datcom.name",
        "branch": "testing",
        "discipline": "aero",
        "historical_year": 1957.0,
        "historical_date": "1957-01-01",
        "granted_at_start": false,
        "initial_maturity": 0.45,
        "prereqs": [
          "test_1948_fm_telemetry_oscillographs",
          "test_1955_inertia_coupling_6dof_sim"
        ],
        "cost_eng_days": 2700,
        "cost_usd": 245000.0,
        "naca_diffusion": true,
        "govt_contract_eligible": true,
        "effects": {
          "testing.tunnel_sigma_factor": 0.85,
          "testing.flight_sigma_factor": 0.82,
          "testing.flight_test_time_factor": 0.82,
          "testing.sim_time_factor": 0.8,
          "research.speed_factor.propulsion": 1.12
        },
        "historical_note": "USAF/NACA Stability and Control Handbook (early DATCOM), AEDC Tullahoma Propulsion Wind Tunnel, and automated magnetic-tape flight-test data reduction."
      }
    ]
  },
  "components": {
    "guns": {
      "schema_version": "1.0",
      "component_type": "gun",
      "description": "Aircraft internal/podded gun armament catalog (1945-1960). SI units. Unlock key for each entry is unlock.gun.<id>.",
      "components": [
        {
          "id": "an_m2_50",
          "unlock_key": "unlock.gun.an_m2_50",
          "name_key": "comp.gun.an_m2_50",
          "historical_designation": "Browning AN/M2 .50 cal",
          "caliber_mm": 12.7,
          "gun_mass_kg": 29.5,
          "feed_and_mount_mass_kg": 11.5,
          "round_mass_kg": 0.118,
          "std_rounds_per_gun": 300,
          "installed_mass_with_std_ammo_kg": 76.4,
          "rate_of_fire_rpm": 800,
          "muzzle_velocity_mps": 865.0,
          "burst_mass_kgps": 1.57,
          "wvr_lethality_score": 1.0,
          "reliability_mtbf_rounds": 4500,
          "unit_cost_usd": 650.0,
          "historical_year": 1940,
          "granted_at_start": true,
          "notes": "Standard WWII USAAF/USN .50 BMG aircraft machine gun; 6x installed in P-80A/B."
        },
        {
          "id": "m3_50",
          "unlock_key": "unlock.gun.m3_50",
          "name_key": "comp.gun.m3_50",
          "historical_designation": "Browning AN/M3 .50 cal",
          "caliber_mm": 12.7,
          "gun_mass_kg": 29.0,
          "feed_and_mount_mass_kg": 13.0,
          "round_mass_kg": 0.118,
          "std_rounds_per_gun": 300,
          "installed_mass_with_std_ammo_kg": 77.4,
          "rate_of_fire_rpm": 1200,
          "muzzle_velocity_mps": 875.0,
          "burst_mass_kgps": 2.36,
          "wvr_lethality_score": 1.45,
          "reliability_mtbf_rounds": 3500,
          "unit_cost_usd": 900.0,
          "historical_year": 1947,
          "granted_at_start": false,
          "notes": "High-rate boosted .50 BMG with electric feed booster; 6x installed in F-84 and F-86A/E/F."
        },
        {
          "id": "an_m3_20mm",
          "unlock_key": "unlock.gun.an_m3_20mm",
          "name_key": "comp.gun.an_m3_20mm",
          "historical_designation": "Hispano-Suiza AN/M3 20mm",
          "caliber_mm": 20.0,
          "gun_mass_kg": 50.0,
          "feed_and_mount_mass_kg": 18.0,
          "round_mass_kg": 0.258,
          "std_rounds_per_gun": 190,
          "installed_mass_with_std_ammo_kg": 117.0,
          "rate_of_fire_rpm": 750,
          "muzzle_velocity_mps": 840.0,
          "burst_mass_kgps": 3.23,
          "wvr_lethality_score": 2.1,
          "reliability_mtbf_rounds": 1800,
          "unit_cost_usd": 1400.0,
          "historical_year": 1945,
          "granted_at_start": true,
          "notes": "US Navy standard 20x110mm cannon in FH-1, F2H, F9F, F7U."
        },
        {
          "id": "m24_20mm",
          "unlock_key": "unlock.gun.m24_20mm",
          "name_key": "comp.gun.m24_20mm",
          "historical_designation": "M24A1 20mm",
          "caliber_mm": 20.0,
          "gun_mass_kg": 48.0,
          "feed_and_mount_mass_kg": 18.0,
          "round_mass_kg": 0.258,
          "std_rounds_per_gun": 200,
          "installed_mass_with_std_ammo_kg": 117.6,
          "rate_of_fire_rpm": 800,
          "muzzle_velocity_mps": 850.0,
          "burst_mass_kgps": 3.44,
          "wvr_lethality_score": 2.3,
          "reliability_mtbf_rounds": 2500,
          "unit_cost_usd": 1650.0,
          "historical_year": 1949,
          "granted_at_start": false,
          "notes": "Electrically primed derivative of AN/M3 20mm for USAF interceptors (F-89C, F-86K)."
        },
        {
          "id": "m39_20mm",
          "unlock_key": "unlock.gun.m39_20mm",
          "name_key": "comp.gun.m39_20mm",
          "historical_designation": "Pontiac M39 20mm",
          "caliber_mm": 20.0,
          "gun_mass_kg": 81.0,
          "feed_and_mount_mass_kg": 22.0,
          "round_mass_kg": 0.255,
          "std_rounds_per_gun": 200,
          "installed_mass_with_std_ammo_kg": 154.0,
          "rate_of_fire_rpm": 1500,
          "muzzle_velocity_mps": 1030.0,
          "burst_mass_kgps": 6.38,
          "wvr_lethality_score": 4.2,
          "reliability_mtbf_rounds": 3200,
          "unit_cost_usd": 3800.0,
          "historical_year": 1952,
          "granted_at_start": false,
          "notes": "Revolver cannon derived from Mauser MG 213C (tested as T-160 in F-86F-2 GunVal); standard on F-100, F-101, F-5."
        },
        {
          "id": "mk12_20mm",
          "unlock_key": "unlock.gun.mk12_20mm",
          "name_key": "comp.gun.mk12_20mm",
          "historical_designation": "Colt Mk 12 20mm",
          "caliber_mm": 20.0,
          "gun_mass_kg": 46.0,
          "feed_and_mount_mass_kg": 16.0,
          "round_mass_kg": 0.235,
          "std_rounds_per_gun": 150,
          "installed_mass_with_std_ammo_kg": 97.3,
          "rate_of_fire_rpm": 1000,
          "muzzle_velocity_mps": 1010.0,
          "burst_mass_kgps": 3.92,
          "wvr_lethality_score": 2.9,
          "reliability_mtbf_rounds": 1500,
          "unit_cost_usd": 2400.0,
          "historical_year": 1953,
          "granted_at_start": false,
          "notes": "Light high-velocity USN 20mm cannon (F4D, F11F, F3H, F8U, A4D); prone to jamming under high-G."
        },
        {
          "id": "m61_20mm",
          "unlock_key": "unlock.gun.m61_20mm",
          "name_key": "comp.gun.m61_20mm",
          "historical_designation": "GE M61 Vulcan 20mm",
          "caliber_mm": 20.0,
          "gun_mass_kg": 112.0,
          "feed_and_mount_mass_kg": 68.0,
          "round_mass_kg": 0.255,
          "std_rounds_per_gun": 725,
          "installed_mass_with_std_ammo_kg": 364.9,
          "rate_of_fire_rpm": 6000,
          "muzzle_velocity_mps": 1050.0,
          "burst_mass_kgps": 25.5,
          "wvr_lethality_score": 8.5,
          "reliability_mtbf_rounds": 12000,
          "unit_cost_usd": 14500.0,
          "historical_year": 1956,
          "granted_at_start": false,
          "notes": "Project Vulcan 6-barrel Gatling cannon; installed as single gun in F-104, F-105, F-106B/later."
        }
      ]
    },
    "missiles": {
      "schema_version": "1.0",
      "component_type": "missile",
      "description": "Air-to-air missile and nuclear rocket catalog (1945-1960). SI units. Unlock key is unlock.missile.<id>.",
      "components": [
        {
          "id": "aim7a_sparrow1",
          "unlock_key": "unlock.missile.aim7a_sparrow1",
          "name_key": "comp.missile.aim7a_sparrow1",
          "historical_designation": "Sperry AAM-N-2 (AIM-7A) Sparrow I",
          "guidance_type": "beam_rider",
          "generation": 1,
          "mass_kg": 143.0,
          "pylon_mass_kg": 28.0,
          "installed_mass_per_round_kg": 171.0,
          "length_m": 3.74,
          "diameter_m": 0.203,
          "drag_area_m2": 0.042,
          "max_mach": 2.5,
          "min_range_m": 1200.0,
          "max_effective_range_m": 9000.0,
          "all_aspect": false,
          "all_weather": true,
          "base_pk": 0.14,
          "bvr_capability_score": 2.5,
          "wvr_capability_score": 0.8,
          "requires_internal_bay": false,
          "unit_cost_usd": 14000.0,
          "historical_year": 1954,
          "granted_at_start": false,
          "notes": "First operational US Navy beam-riding AAM (F3D-2M, F7U-3M, F3H-2M); pilot must hold radar beam on target."
        },
        {
          "id": "aim4a_falcon",
          "unlock_key": "unlock.missile.aim4a_falcon",
          "name_key": "comp.missile.aim4a_falcon",
          "historical_designation": "Hughes GAR-1 (AIM-4A) Falcon",
          "guidance_type": "sarh",
          "generation": 1,
          "mass_kg": 54.0,
          "pylon_mass_kg": 16.0,
          "installed_mass_per_round_kg": 70.0,
          "length_m": 1.98,
          "diameter_m": 0.163,
          "drag_area_m2": 0.018,
          "max_mach": 2.8,
          "min_range_m": 900.0,
          "max_effective_range_m": 8000.0,
          "all_aspect": false,
          "all_weather": true,
          "base_pk": 0.18,
          "bvr_capability_score": 3.2,
          "wvr_capability_score": 1.2,
          "requires_internal_bay": false,
          "unit_cost_usd": 9500.0,
          "historical_year": 1955,
          "granted_at_start": false,
          "notes": "USAF ADC interceptor SARH missile (F-89H, F-102A, F-101B, F-106A); impact fuse only (no proximity fuse)."
        },
        {
          "id": "aim4c_falcon",
          "unlock_key": "unlock.missile.aim4c_falcon",
          "name_key": "comp.missile.aim4c_falcon",
          "historical_designation": "Hughes GAR-2A (AIM-4C) Falcon",
          "guidance_type": "ir",
          "generation": 1,
          "mass_kg": 55.0,
          "pylon_mass_kg": 16.0,
          "installed_mass_per_round_kg": 71.0,
          "length_m": 2.02,
          "diameter_m": 0.163,
          "drag_area_m2": 0.018,
          "max_mach": 2.8,
          "min_range_m": 800.0,
          "max_effective_range_m": 9500.0,
          "all_aspect": false,
          "all_weather": false,
          "base_pk": 0.24,
          "bvr_capability_score": 2.0,
          "wvr_capability_score": 2.8,
          "requires_internal_bay": false,
          "unit_cost_usd": 8800.0,
          "historical_year": 1956,
          "granted_at_start": false,
          "notes": "Rear-aspect uncooled PbS infrared homing variant of Falcon; paired with GAR-1 in mixed loads on F-102/F-106."
        },
        {
          "id": "aim9b_sidewinder",
          "unlock_key": "unlock.missile.aim9b_sidewinder",
          "name_key": "comp.missile.aim9b_sidewinder",
          "historical_designation": "NWC / Philco AIM-9B (AAM-N-7 / GAR-8) Sidewinder",
          "guidance_type": "ir",
          "generation": 1,
          "mass_kg": 70.4,
          "pylon_mass_kg": 18.0,
          "installed_mass_per_round_kg": 88.4,
          "length_m": 2.83,
          "diameter_m": 0.127,
          "drag_area_m2": 0.016,
          "max_mach": 2.5,
          "min_range_m": 900.0,
          "max_effective_range_m": 4800.0,
          "all_aspect": false,
          "all_weather": false,
          "base_pk": 0.28,
          "bvr_capability_score": 1.0,
          "wvr_capability_score": 4.8,
          "requires_internal_bay": false,
          "unit_cost_usd": 3200.0,
          "historical_year": 1956,
          "granted_at_start": false,
          "notes": "Simple, reliable USN China Lake IR homing dogfight missile with rollerons and proximity fuse (F9F-8, FJ-4, F8U, F-100, F-104)."
        },
        {
          "id": "air2a_genie",
          "unlock_key": "unlock.missile.air2a_genie",
          "name_key": "comp.missile.air2a_genie",
          "historical_designation": "Douglas MB-1 (AIR-2A) Genie",
          "guidance_type": "unguided_nuclear",
          "generation": 1,
          "mass_kg": 373.0,
          "pylon_mass_kg": 45.0,
          "installed_mass_per_round_kg": 418.0,
          "length_m": 2.95,
          "diameter_m": 0.44,
          "drag_area_m2": 0.085,
          "max_mach": 3.3,
          "min_range_m": 2500.0,
          "max_effective_range_m": 9600.0,
          "all_aspect": true,
          "all_weather": true,
          "base_pk": 0.85,
          "bvr_capability_score": 7.5,
          "wvr_capability_score": 0.0,
          "requires_internal_bay": false,
          "unit_cost_usd": 42000.0,
          "historical_year": 1957,
          "granted_at_start": false,
          "notes": "Unguided air-to-air rocket with 1.5 kt W25 nuclear warhead (300 m lethal radius vs bomber formations); F-89J, F-101B, F-106A."
        },
        {
          "id": "aim7c_sparrow3",
          "unlock_key": "unlock.missile.aim7c_sparrow3",
          "name_key": "comp.missile.aim7c_sparrow3",
          "historical_designation": "Raytheon AAM-N-6 (AIM-7C) Sparrow III",
          "guidance_type": "sarh",
          "generation": 2,
          "mass_kg": 172.0,
          "pylon_mass_kg": 30.0,
          "installed_mass_per_round_kg": 202.0,
          "length_m": 3.66,
          "diameter_m": 0.203,
          "drag_area_m2": 0.036,
          "max_mach": 3.5,
          "min_range_m": 1500.0,
          "max_effective_range_m": 14000.0,
          "all_aspect": true,
          "all_weather": true,
          "base_pk": 0.3,
          "bvr_capability_score": 6.8,
          "wvr_capability_score": 1.5,
          "requires_internal_bay": false,
          "unit_cost_usd": 19500.0,
          "historical_year": 1958,
          "granted_at_start": false,
          "notes": "All-weather semi-active radar homing BVR missile; primary armament of F3H-2M and F4H-1 Phantom II."
        },
        {
          "id": "aim26a_nuclear_falcon",
          "unlock_key": "unlock.missile.aim26a_nuclear_falcon",
          "name_key": "comp.missile.aim26a_nuclear_falcon",
          "historical_designation": "Hughes GAR-11 (AIM-26A) Nuclear Falcon",
          "guidance_type": "sarh_nuclear",
          "generation": 2,
          "mass_kg": 92.0,
          "pylon_mass_kg": 22.0,
          "installed_mass_per_round_kg": 114.0,
          "length_m": 2.13,
          "diameter_m": 0.279,
          "drag_area_m2": 0.032,
          "max_mach": 2.2,
          "min_range_m": 1800.0,
          "max_effective_range_m": 12000.0,
          "all_aspect": true,
          "all_weather": true,
          "base_pk": 0.78,
          "bvr_capability_score": 7.2,
          "wvr_capability_score": 0.0,
          "requires_internal_bay": true,
          "unit_cost_usd": 36000.0,
          "historical_year": 1960,
          "granted_at_start": false,
          "notes": "Guided SARH missile with W54 sub-kiloton nuclear warhead and radar proximity fuse for F-102A/F-106A internal bay."
        }
      ]
    },
    "radars": {
      "schema_version": "1.0",
      "component_type": "radar",
      "description": "Airborne radar and integrated fire-control systems catalog (1945-1960). SI units. Unlock key is unlock.radar.<id>.",
      "components": [
        {
          "id": "scr720",
          "unlock_key": "unlock.radar.scr720",
          "name_key": "comp.radar.scr720",
          "historical_designation": "Western Electric SCR-720",
          "category": "ai_search",
          "band": "S",
          "mass_kg": 185.0,
          "dish_diameter_m": 0.74,
          "min_nose_diameter_m": 0.85,
          "power_kw": 1.5,
          "detection_range_bomber_m": 14000.0,
          "detection_range_fighter_m": 8000.0,
          "supports_lead_collision": false,
          "supports_sarh_cw": false,
          "supports_beam_rider": false,
          "supports_sage_datalink": false,
          "mtbf_h": 22.0,
          "bvr_sensor_score": 1.2,
          "unit_cost_usd": 12000.0,
          "historical_year": 1943,
          "granted_at_start": true,
          "notes": "WWII S-band centimetric AI radar (P-61, F-82); requires dedicated radar operator."
        },
        {
          "id": "apg5",
          "unlock_key": "unlock.radar.apg5",
          "name_key": "comp.radar.apg5",
          "historical_designation": "AN/APG-5 Gun-Ranging Radar",
          "category": "gun_ranging",
          "band": "S",
          "mass_kg": 16.0,
          "dish_diameter_m": 0.2,
          "min_nose_diameter_m": 0.3,
          "power_kw": 0.3,
          "detection_range_bomber_m": 2300.0,
          "detection_range_fighter_m": 1800.0,
          "supports_lead_collision": false,
          "supports_sarh_cw": false,
          "supports_beam_rider": false,
          "supports_sage_datalink": false,
          "mtbf_h": 55.0,
          "bvr_sensor_score": 0.2,
          "unit_cost_usd": 2200.0,
          "historical_year": 1945,
          "granted_at_start": true,
          "notes": "Early range-only radar feeding gyro gunsight (late P-51/F-86A prototypes)."
        },
        {
          "id": "aps19",
          "unlock_key": "unlock.radar.aps19",
          "name_key": "comp.radar.aps19",
          "historical_designation": "Sperry AN/APS-19",
          "category": "ai_search",
          "band": "X",
          "mass_kg": 76.0,
          "dish_diameter_m": 0.43,
          "min_nose_diameter_m": 0.52,
          "power_kw": 0.8,
          "detection_range_bomber_m": 16000.0,
          "detection_range_fighter_m": 9500.0,
          "supports_lead_collision": false,
          "supports_sarh_cw": false,
          "supports_beam_rider": false,
          "supports_sage_datalink": false,
          "mtbf_h": 32.0,
          "bvr_sensor_score": 1.8,
          "unit_cost_usd": 9800.0,
          "historical_year": 1946,
          "granted_at_start": false,
          "notes": "Compact X-band single-seat Navy night-fighter search/gun-aiming radar (F4U-5N, F2H-2N, F9F)."
        },
        {
          "id": "apg30",
          "unlock_key": "unlock.radar.apg30",
          "name_key": "comp.radar.apg30",
          "historical_designation": "GE AN/APG-30 (with A-1CM Sight)",
          "category": "gun_ranging",
          "band": "X",
          "mass_kg": 18.5,
          "dish_diameter_m": 0.22,
          "min_nose_diameter_m": 0.3,
          "power_kw": 0.35,
          "detection_range_bomber_m": 2700.0,
          "detection_range_fighter_m": 2500.0,
          "supports_lead_collision": false,
          "supports_sarh_cw": false,
          "supports_beam_rider": false,
          "supports_sage_datalink": false,
          "mtbf_h": 65.0,
          "bvr_sensor_score": 0.4,
          "unit_cost_usd": 3100.0,
          "historical_year": 1948,
          "granted_at_start": false,
          "notes": "Compact X-band radar rangefinder feeding the A-1CM/A-4 gyro gunsight; decisive in MiG Alley (F-86A/E/F, F-84E/G, F-100)."
        },
        {
          "id": "apg33",
          "unlock_key": "unlock.radar.apg33",
          "name_key": "comp.radar.apg33",
          "historical_designation": "Hughes AN/APG-33 (E-1 FCS)",
          "category": "ai_fcs",
          "band": "X",
          "mass_kg": 195.0,
          "dish_diameter_m": 0.61,
          "min_nose_diameter_m": 0.72,
          "power_kw": 1.8,
          "detection_range_bomber_m": 28000.0,
          "detection_range_fighter_m": 16000.0,
          "supports_lead_collision": false,
          "supports_sarh_cw": false,
          "supports_beam_rider": false,
          "supports_sage_datalink": false,
          "mtbf_h": 24.0,
          "bvr_sensor_score": 2.8,
          "unit_cost_usd": 22000.0,
          "historical_year": 1949,
          "granted_at_start": false,
          "notes": "First post-war Hughes search & automatic tracking radar for E-1 lead-pursuit FCS (F-94A/B, F-89A/B/C)."
        },
        {
          "id": "aps21",
          "unlock_key": "unlock.radar.aps21",
          "name_key": "comp.radar.aps21",
          "historical_designation": "Westinghouse AN/APS-21 (APQ-35)",
          "category": "ai_fcs",
          "band": "X",
          "mass_kg": 215.0,
          "dish_diameter_m": 0.66,
          "min_nose_diameter_m": 0.76,
          "power_kw": 2.0,
          "detection_range_bomber_m": 32000.0,
          "detection_range_fighter_m": 18500.0,
          "supports_lead_collision": false,
          "supports_sarh_cw": false,
          "supports_beam_rider": true,
          "supports_sage_datalink": false,
          "mtbf_h": 26.0,
          "bvr_sensor_score": 3.1,
          "unit_cost_usd": 26000.0,
          "historical_year": 1950,
          "granted_at_start": false,
          "notes": "US Navy all-weather intercept radar suite (core of APQ-35/36/41 in F3D-2, F2H-3/4, F7U-3M)."
        },
        {
          "id": "apg37",
          "unlock_key": "unlock.radar.apg37",
          "name_key": "comp.radar.apg37",
          "historical_designation": "Hughes AN/APG-37 (E-4/E-5/E-6 FCS)",
          "category": "ai_fcs",
          "band": "X",
          "mass_kg": 240.0,
          "dish_diameter_m": 0.68,
          "min_nose_diameter_m": 0.78,
          "power_kw": 2.4,
          "detection_range_bomber_m": 37000.0,
          "detection_range_fighter_m": 22000.0,
          "supports_lead_collision": true,
          "supports_sarh_cw": false,
          "supports_beam_rider": false,
          "supports_sage_datalink": false,
          "mtbf_h": 28.0,
          "bvr_sensor_score": 4.2,
          "unit_cost_usd": 38000.0,
          "historical_year": 1951,
          "granted_at_start": false,
          "notes": "Single-seat automatic lead-collision rocket-firing radar/FCS (F-86D Sabre Dog, F-94C Starfire)."
        },
        {
          "id": "apg40",
          "unlock_key": "unlock.radar.apg40",
          "name_key": "comp.radar.apg40",
          "historical_designation": "Hughes AN/APG-40 (E-9 FCS)",
          "category": "ai_fcs",
          "band": "X",
          "mass_kg": 265.0,
          "dish_diameter_m": 0.74,
          "min_nose_diameter_m": 0.84,
          "power_kw": 2.8,
          "detection_range_bomber_m": 44000.0,
          "detection_range_fighter_m": 26000.0,
          "supports_lead_collision": true,
          "supports_sarh_cw": true,
          "supports_beam_rider": false,
          "supports_sage_datalink": false,
          "mtbf_h": 30.0,
          "bvr_sensor_score": 5.0,
          "unit_cost_usd": 45000.0,
          "historical_year": 1953,
          "granted_at_start": false,
          "notes": "High-power radar for Hughes E-9 fire control system supporting FFAR rockets and GAR-1 Falcon missiles (F-89D/H)."
        },
        {
          "id": "mg10",
          "unlock_key": "unlock.radar.mg10",
          "name_key": "comp.radar.mg10",
          "historical_designation": "Hughes MG-10 / MG-13 AWCS",
          "category": "awcs",
          "band": "X",
          "mass_kg": 380.0,
          "dish_diameter_m": 0.81,
          "min_nose_diameter_m": 0.92,
          "power_kw": 3.5,
          "detection_range_bomber_m": 55000.0,
          "detection_range_fighter_m": 33000.0,
          "supports_lead_collision": true,
          "supports_sarh_cw": true,
          "supports_beam_rider": false,
          "supports_sage_datalink": true,
          "mtbf_h": 34.0,
          "bvr_sensor_score": 6.6,
          "unit_cost_usd": 68000.0,
          "historical_year": 1955,
          "granted_at_start": false,
          "notes": "Automatic weapon control system coupling radar, Falcon/Genie fire control, and autopilot (F-102A, F-101B)."
        },
        {
          "id": "apq50",
          "unlock_key": "unlock.radar.apq50",
          "name_key": "comp.radar.apq50",
          "historical_designation": "Westinghouse AN/APQ-50 (Aero 13 FCS)",
          "category": "ai_fcs",
          "band": "X",
          "mass_kg": 230.0,
          "dish_diameter_m": 0.61,
          "min_nose_diameter_m": 0.72,
          "power_kw": 2.6,
          "detection_range_bomber_m": 46000.0,
          "detection_range_fighter_m": 28000.0,
          "supports_lead_collision": true,
          "supports_sarh_cw": true,
          "supports_beam_rider": true,
          "supports_sage_datalink": false,
          "mtbf_h": 42.0,
          "bvr_sensor_score": 5.8,
          "unit_cost_usd": 52000.0,
          "historical_year": 1955,
          "granted_at_start": false,
          "notes": "Standard late-1950s US Navy all-weather fighter radar supporting Sparrow I and III (F4D-1, F3H-2, early F4H-1)."
        },
        {
          "id": "ma1",
          "unlock_key": "unlock.radar.ma1",
          "name_key": "comp.radar.ma1",
          "historical_designation": "Hughes MA-1 AWCS (with Digitair Computer)",
          "category": "awcs",
          "band": "X",
          "mass_kg": 540.0,
          "dish_diameter_m": 0.86,
          "min_nose_diameter_m": 0.98,
          "power_kw": 4.8,
          "detection_range_bomber_m": 70000.0,
          "detection_range_fighter_m": 44000.0,
          "supports_lead_collision": true,
          "supports_sarh_cw": true,
          "supports_beam_rider": false,
          "supports_sage_datalink": true,
          "mtbf_h": 38.0,
          "bvr_sensor_score": 8.4,
          "unit_cost_usd": 135000.0,
          "historical_year": 1958,
          "granted_at_start": false,
          "notes": "First airborne digital computer fire-control system (F-106A Delta Dart); automated SAGE ground-controlled intercept from takeoff to weapon release."
        },
        {
          "id": "apq72",
          "unlock_key": "unlock.radar.apq72",
          "name_key": "comp.radar.apq72",
          "historical_designation": "Westinghouse AN/APQ-72 (Aero 1A FCS)",
          "category": "awcs",
          "band": "X",
          "mass_kg": 395.0,
          "dish_diameter_m": 0.81,
          "min_nose_diameter_m": 0.94,
          "power_kw": 5.0,
          "detection_range_bomber_m": 83000.0,
          "detection_range_fighter_m": 52000.0,
          "supports_lead_collision": true,
          "supports_sarh_cw": true,
          "supports_beam_rider": false,
          "supports_sage_datalink": true,
          "mtbf_h": 45.0,
          "bvr_sensor_score": 9.0,
          "unit_cost_usd": 115000.0,
          "historical_year": 1959,
          "granted_at_start": false,
          "notes": "32-inch dish high-power fleet air defense radar + CW illuminator for AIM-7C Sparrow III on F4H-1 (F-4A/B) Phantom II."
        }
      ]
    }
  },
  "testing": {
    "flaws": {
      "flaws": [
        {
          "id": "swept_wing_pitch_up",
          "name": "Swept-Wing Sabre Dance / Pitch-Up",
          "family": "pitch_up",
          "category": "aerodynamics",
          "base_severity": 4,
          "known_from_year": 1949,
          "unknown_symptom_label": "Unexplained violent high-alpha nose-up departure",
          "historical_examples": [
            "F-86A/E Sabre",
            "F-100A Super Sabre",
            "F-101A Voodoo"
          ],
          "max_prob": 0.85,
          "novelty_features": [
            "swept_wing",
            "high_sweep",
            "t_tail"
          ],
          "trigger": {
            "base": 0.04,
            "gates": [
              {
                "feature": "sweep_deg",
                "min": 22.0,
                "full": 32.0
              }
            ],
            "ramps": [
              {
                "feature": "shortal_maggin_excess",
                "x0": -0.5,
                "x1": 1.5,
                "weight": 0.42
              }
            ],
            "flags": [
              {
                "feature": "is_t_tail",
                "add": 0.22
              }
            ],
            "multipliers": [
              {
                "feature": "has_le_slats",
                "mul": 0.45
              },
              {
                "feature": "has_wing_fences",
                "mul": 0.55
              },
              {
                "feature": "has_sawtooth_le",
                "mul": 0.5
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.08,
            "low_speed_tunnel": 0.35,
            "transonic_slotted": 0.5,
            "spin_tunnel": 0.4,
            "flight:low_speed": 0.45,
            "flight:maneuver": 0.82,
            "flight:high_aoa_spin": 0.88
          },
          "flight_incident": {
            "encounter_weight": 0.35,
            "crash_prob_given_encounter": 0.18
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "instantaneous_turn_dps_m08_4572m": 0.86,
              "sustained_turn_dps_m08_4572m": 0.92
            }
          },
          "placard": {
            "name": "AoA / G-Limiter Placard",
            "metric_multipliers": {
              "instantaneous_turn_dps_m08_4572m": 0.8,
              "sustained_turn_dps_m08_4572m": 0.88,
              "max_load_factor_g": 0.85
            },
            "residual_hazard_factor": 0.25
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.55,
            "accident_rate_per_1000fh": 0.18,
            "grounding_days": 45,
            "rep_penalty": 8.0
          },
          "fixes": [
            {
              "id": "wing_fences",
              "name": "Install Boundary-Layer Wing Fences",
              "available_year": 1948,
              "required_tech": null,
              "base_cost_1950_usd": 45000.0,
              "retrofit_kit_1950_usd": 1800.0,
              "fix_days": 21,
              "residual_factor": 0.2,
              "driver_log_deltas": {
                "cd0": 0.015,
                "mass": 0.004
              },
              "metric_multipliers": {}
            },
            {
              "id": "sawtooth_le_dogtooth",
              "name": "Sawtooth / Dogtooth Leading-Edge Extension",
              "available_year": 1952,
              "required_tech": null,
              "base_cost_1950_usd": 95000.0,
              "retrofit_kit_1950_usd": 4200.0,
              "fix_days": 38,
              "residual_factor": 0.1,
              "driver_log_deltas": {
                "cd0": 0.008,
                "mass": 0.006
              },
              "metric_multipliers": {}
            },
            {
              "id": "auto_le_slats",
              "name": "Retrofit Automatic Leading-Edge Slats",
              "available_year": 1947,
              "required_tech": "aero.le_slats",
              "base_cost_1950_usd": 140000.0,
              "retrofit_kit_1950_usd": 6500.0,
              "fix_days": 50,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "cd0": 0.012,
                "clmax": 0.08,
                "mass": 0.018
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "deep_stall_t_tail",
          "name": "T-Tail Locked-In Deep Stall",
          "family": "pitch_up",
          "category": "aerodynamics",
          "base_severity": 5,
          "known_from_year": 1954,
          "unknown_symptom_label": "Irrecoverable high-alpha tail blanketing stall",
          "historical_examples": [
            "F-101A Voodoo",
            "XF-104 Starfighter"
          ],
          "max_prob": 0.8,
          "novelty_features": [
            "t_tail",
            "high_sweep"
          ],
          "trigger": {
            "base": 0.08,
            "gates": [
              {
                "feature": "is_t_tail",
                "min": 0.5,
                "full": 1.0
              },
              {
                "feature": "sweep_deg",
                "min": 24.0,
                "full": 36.0
              }
            ],
            "ramps": [
              {
                "feature": "shortal_maggin_excess",
                "x0": -0.8,
                "x1": 1.2,
                "weight": 0.35
              },
              {
                "feature": "wing_loading_kgm2",
                "x0": 260.0,
                "x1": 480.0,
                "weight": 0.18
              }
            ],
            "flags": [],
            "multipliers": [
              {
                "feature": "has_le_flaps",
                "mul": 0.7
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.04,
            "low_speed_tunnel": 0.25,
            "spin_tunnel": 0.55,
            "flight:low_speed": 0.35,
            "flight:maneuver": 0.65,
            "flight:high_aoa_spin": 0.85
          },
          "flight_incident": {
            "encounter_weight": 0.3,
            "crash_prob_given_encounter": 0.32
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "instantaneous_turn_dps_m08_4572m": 0.84
            }
          },
          "placard": {
            "name": "Hard Pitch / AoA Horn Restriction",
            "metric_multipliers": {
              "instantaneous_turn_dps_m08_4572m": 0.76,
              "max_load_factor_g": 0.82
            },
            "residual_hazard_factor": 0.22
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.45,
            "accident_rate_per_1000fh": 0.24,
            "grounding_days": 60,
            "rep_penalty": 11.0
          },
          "fixes": [
            {
              "id": "active_stick_pusher",
              "name": "Install Automatic Pneumatic Stick Pusher & AoA Vane",
              "available_year": 1954,
              "required_tech": null,
              "base_cost_1950_usd": 75000.0,
              "retrofit_kit_1950_usd": 3200.0,
              "fix_days": 30,
              "residual_factor": 0.15,
              "driver_log_deltas": {
                "mass": 0.005,
                "maint": 0.03
              },
              "metric_multipliers": {
                "instantaneous_turn_dps_m08_4572m": 0.94
              }
            },
            {
              "id": "lower_stabilizer_relocation",
              "name": "Relocate Horizontal Tail to Low Fuselage Position",
              "available_year": 1945,
              "required_tech": null,
              "base_cost_1950_usd": 240000.0,
              "retrofit_kit_1950_usd": 14000.0,
              "fix_days": 75,
              "residual_factor": 0.04,
              "driver_log_deltas": {
                "mass": 0.022,
                "cd0": 0.01
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "inertia_roll_coupling",
          "name": "Supersonic Roll-Inertia Pitch/Yaw Coupling",
          "family": "inertia_coupling",
          "category": "stability_control",
          "base_severity": 5,
          "known_from_year": 1954,
          "unknown_symptom_label": "Catastrophic unexplained yaw-pitch structural divergence in rapid roll",
          "historical_examples": [
            "F-100A Super Sabre (George Welch crash)",
            "Douglas X-3 Stiletto",
            "F-104A"
          ],
          "max_prob": 0.85,
          "novelty_features": [
            "supersonic_level",
            "thin_wing",
            "high_sweep"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [
              {
                "feature": "max_mach_nom",
                "min": 0.94,
                "full": 1.25
              }
            ],
            "ramps": [
              {
                "feature": "inertia_coupling_index",
                "x0": 2.2,
                "x1": 6.5,
                "weight": 0.52
              },
              {
                "feature": "fuselage_to_span_ratio",
                "x0": 1.15,
                "x1": 2.1,
                "weight": 0.25
              }
            ],
            "flags": [],
            "multipliers": [
              {
                "feature": "has_sas",
                "mul": 0.45
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.03,
            "supersonic_tunnel": 0.28,
            "flight:speed_envelope": 0.72,
            "flight:maneuver": 0.78
          },
          "flight_incident": {
            "encounter_weight": 0.38,
            "crash_prob_given_encounter": 0.35
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "sustained_turn_dps_m08_4572m": 0.9
            }
          },
          "placard": {
            "name": "Half-Deflection Aileron & Supersonic Roll Placard",
            "metric_multipliers": {
              "instantaneous_turn_dps_m08_4572m": 0.82,
              "sustained_turn_dps_m08_4572m": 0.86
            },
            "residual_hazard_factor": 0.25
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.65,
            "accident_rate_per_1000fh": 0.28,
            "grounding_days": 75,
            "rep_penalty": 12.0
          },
          "fixes": [
            {
              "id": "enlarged_vertical_fin",
              "name": "27% Enlarged Tall Vertical Fin & Wingtip Extensions (F-100A Fix)",
              "available_year": 1945,
              "required_tech": null,
              "base_cost_1950_usd": 165000.0,
              "retrofit_kit_1950_usd": 7800.0,
              "fix_days": 52,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "cd0": 0.016,
                "cdw": 0.015,
                "mass": 0.018
              },
              "metric_multipliers": {}
            },
            {
              "id": "three_axis_sas_damper",
              "name": "Install 3-Axis Stability Augmentation Yaw/Pitch Damper",
              "available_year": 1951,
              "required_tech": "systems.stability_augmentation",
              "base_cost_1950_usd": 120000.0,
              "retrofit_kit_1950_usd": 5500.0,
              "fix_days": 40,
              "residual_factor": 0.12,
              "driver_log_deltas": {
                "mass": 0.008,
                "maint": 0.05
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "supersonic_directional_instability",
          "name": "Supersonic Cn_beta Weathercock Instability",
          "family": "inertia_coupling",
          "category": "stability_control",
          "base_severity": 4,
          "known_from_year": 1953,
          "unknown_symptom_label": "High-Mach directional divergence and vertical fin unloading",
          "historical_examples": [
            "F-100C",
            "F-102A",
            "F8U-1 Crusader",
            "F-104A"
          ],
          "max_prob": 0.8,
          "novelty_features": [
            "supersonic_level",
            "mach2_regime"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [
              {
                "feature": "max_mach_nom",
                "min": 1.2,
                "full": 1.65
              }
            ],
            "ramps": [
              {
                "feature": "vv_deficit",
                "x0": -0.01,
                "x1": 0.04,
                "weight": 0.45
              },
              {
                "feature": "max_mach_nom",
                "x0": 1.3,
                "x1": 2.1,
                "weight": 0.25
              }
            ],
            "flags": [],
            "multipliers": [
              {
                "feature": "has_sas",
                "mul": 0.55
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.05,
            "supersonic_tunnel": 0.58,
            "flight:speed_envelope": 0.82
          },
          "flight_incident": {
            "encounter_weight": 0.3,
            "crash_prob_given_encounter": 0.24
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "max_mach_alt": 0.93
            }
          },
          "placard": {
            "name": "Supersonic Mach Limit Placard",
            "metric_multipliers": {
              "max_mach_alt": 0.88
            },
            "residual_hazard_factor": 0.2
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.5,
            "accident_rate_per_1000fh": 0.2,
            "grounding_days": 45,
            "rep_penalty": 7.5
          },
          "fixes": [
            {
              "id": "ventral_dorsal_fins",
              "name": "Install Ventral Strake & Extended Dorsal Fin",
              "available_year": 1952,
              "required_tech": null,
              "base_cost_1950_usd": 85000.0,
              "retrofit_kit_1950_usd": 3800.0,
              "fix_days": 32,
              "residual_factor": 0.1,
              "driver_log_deltas": {
                "cd0": 0.012,
                "mass": 0.009
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "transonic_mach_tuck",
          "name": "Transonic Nose-Down Mach Tuck & Elevator Lock",
          "family": "transonic_control_loss",
          "category": "stability_control",
          "base_severity": 3,
          "known_from_year": 1945,
          "unknown_symptom_label": "Severe transonic dive recovery loss",
          "historical_examples": [
            "P-80A Shooting Star",
            "F-86A Sabre",
            "F9F Panther"
          ],
          "max_prob": 0.85,
          "novelty_features": [
            "transonic_target",
            "swept_wing"
          ],
          "trigger": {
            "base": 0.08,
            "gates": [
              {
                "feature": "max_mach_nom",
                "min": 0.8,
                "full": 0.94
              }
            ],
            "ramps": [
              {
                "feature": "ac_shift_mac",
                "x0": 0.02,
                "x1": 0.12,
                "weight": 0.45
              },
              {
                "feature": "mach_dd_excess",
                "x0": -0.04,
                "x1": 0.12,
                "weight": 0.3
              }
            ],
            "flags": [],
            "multipliers": [
              {
                "feature": "has_all_moving_tail",
                "mul": 0.2
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.12,
            "transonic_bump": 0.48,
            "rocket_model": 0.52,
            "transonic_slotted": 0.68,
            "flight:speed_envelope": 0.88
          },
          "flight_incident": {
            "encounter_weight": 0.32,
            "crash_prob_given_encounter": 0.16
          },
          "truth_effects": {
            "driver_log_deltas": {
              "cdw": 0.04
            },
            "metric_multipliers": {
              "max_mach_sl": 0.95,
              "max_mach_alt": 0.95
            }
          },
          "placard": {
            "name": "Redline Dive Mach Placard (M 0.90)",
            "metric_multipliers": {
              "max_mach_sl": 0.91,
              "max_mach_alt": 0.91
            },
            "residual_hazard_factor": 0.2
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.5,
            "accident_rate_per_1000fh": 0.15,
            "grounding_days": 30,
            "rep_penalty": 6.0
          },
          "fixes": [
            {
              "id": "all_flying_tail_conversion",
              "name": "Convert to All-Moving Power Stabilator (F-86E Type)",
              "available_year": 1948,
              "required_tech": "aero.all_moving_tail",
              "base_cost_1950_usd": 150000.0,
              "retrofit_kit_1950_usd": 7200.0,
              "fix_days": 48,
              "residual_factor": 0.06,
              "driver_log_deltas": {
                "mass": 0.012,
                "cdw": -0.02
              },
              "metric_multipliers": {}
            },
            {
              "id": "mach_trim_compensator",
              "name": "Install Electric Mach Trim Pitch Compensator",
              "available_year": 1946,
              "required_tech": null,
              "base_cost_1950_usd": 55000.0,
              "retrofit_kit_1950_usd": 2200.0,
              "fix_days": 24,
              "residual_factor": 0.22,
              "driver_log_deltas": {
                "mass": 0.003,
                "maint": 0.02
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "transonic_control_heaviness",
          "name": "Transonic Hinge-Moment Control Freezing",
          "family": "transonic_control_loss",
          "category": "stability_control",
          "base_severity": 3,
          "known_from_year": 1946,
          "unknown_symptom_label": "Extreme stick force lockup at high dynamic pressure",
          "historical_examples": [
            "F-84B Thunderjet",
            "F2H Banshee"
          ],
          "max_prob": 0.85,
          "novelty_features": [
            "transonic_target"
          ],
          "trigger": {
            "base": 0.06,
            "gates": [
              {
                "feature": "max_mach_nom",
                "min": 0.82,
                "full": 0.94
              }
            ],
            "ramps": [
              {
                "feature": "q_dive_kpa",
                "x0": 45.0,
                "x1": 90.0,
                "weight": 0.55
              }
            ],
            "flags": [],
            "multipliers": [
              {
                "feature": "has_powered_controls",
                "mul": 0.12
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.15,
            "transonic_slotted": 0.45,
            "flight:speed_envelope": 0.86,
            "flight:maneuver": 0.75
          },
          "flight_incident": {
            "encounter_weight": 0.25,
            "crash_prob_given_encounter": 0.12
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "instantaneous_turn_dps_m08_4572m": 0.85,
              "sustained_turn_dps_m08_4572m": 0.9
            }
          },
          "placard": {
            "name": "High-Speed IAS Maneuver Restriction",
            "metric_multipliers": {
              "instantaneous_turn_dps_m08_4572m": 0.8,
              "max_mach_sl": 0.93
            },
            "residual_hazard_factor": 0.22
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.45,
            "accident_rate_per_1000fh": 0.12,
            "grounding_days": 20,
            "rep_penalty": 5.0
          },
          "fixes": [
            {
              "id": "hydraulic_irreversible_boost",
              "name": "Install Irreversible Hydraulic Flight Control Actuators",
              "available_year": 1947,
              "required_tech": "systems.powered_controls",
              "base_cost_1950_usd": 135000.0,
              "retrofit_kit_1950_usd": 6200.0,
              "fix_days": 45,
              "residual_factor": 0.05,
              "driver_log_deltas": {
                "mass": 0.015,
                "maint": 0.04
              },
              "metric_multipliers": {}
            },
            {
              "id": "spring_servo_tabs",
              "name": "Geared Aerodynamic Balance & Spring Servo Tabs",
              "available_year": 1945,
              "required_tech": null,
              "base_cost_1950_usd": 48000.0,
              "retrofit_kit_1950_usd": 1900.0,
              "fix_days": 20,
              "residual_factor": 0.25,
              "driver_log_deltas": {
                "cd0": 0.008
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "transonic_buffet_boundary",
          "name": "Severe Transonic Shock-Induced Wing Buffet",
          "family": "transonic_control_loss",
          "category": "aerodynamics",
          "base_severity": 3,
          "known_from_year": 1947,
          "unknown_symptom_label": "Violent airframe buffeting limiting usable g at Mach 0.8+",
          "historical_examples": [
            "F-86A",
            "F9F-2",
            "F3D Skyknight"
          ],
          "max_prob": 0.8,
          "novelty_features": [
            "transonic_target",
            "swept_wing"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [
              {
                "feature": "max_mach_nom",
                "min": 0.76,
                "full": 0.88
              }
            ],
            "ramps": [
              {
                "feature": "tc_ratio",
                "x0": 0.075,
                "x1": 0.125,
                "weight": 0.42
              },
              {
                "feature": "mach_dd_excess",
                "x0": -0.03,
                "x1": 0.1,
                "weight": 0.3
              }
            ],
            "flags": [],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.1,
            "transonic_bump": 0.45,
            "transonic_slotted": 0.62,
            "flight:speed_envelope": 0.72,
            "flight:maneuver": 0.84
          },
          "flight_incident": {
            "encounter_weight": 0.2,
            "crash_prob_given_encounter": 0.06
          },
          "truth_effects": {
            "driver_log_deltas": {
              "kind": 0.06
            },
            "metric_multipliers": {
              "sustained_turn_dps_m08_4572m": 0.89,
              "instantaneous_turn_dps_m08_4572m": 0.88
            }
          },
          "placard": {
            "name": "Transonic Buffet G-Limit Table",
            "metric_multipliers": {
              "sustained_turn_dps_m08_4572m": 0.85,
              "instantaneous_turn_dps_m08_4572m": 0.84
            },
            "residual_hazard_factor": 0.2
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.4,
            "accident_rate_per_1000fh": 0.06,
            "grounding_days": 0,
            "rep_penalty": 4.5
          },
          "fixes": [
            {
              "id": "vortex_generators",
              "name": "Install Upper-Surface Wing Vortex Generators",
              "available_year": 1949,
              "required_tech": null,
              "base_cost_1950_usd": 38000.0,
              "retrofit_kit_1950_usd": 1400.0,
              "fix_days": 16,
              "residual_factor": 0.18,
              "driver_log_deltas": {
                "cd0": 0.01
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "control_surface_buzz",
          "name": "Transonic Shock-Oscillation Aileron Buzz",
          "family": "transonic_control_loss",
          "category": "aeroelasticity",
          "base_severity": 2,
          "known_from_year": 1946,
          "unknown_symptom_label": "High-frequency control surface oscillation near M 0.82",
          "historical_examples": [
            "P-80A Shooting Star",
            "F-84C"
          ],
          "max_prob": 0.75,
          "novelty_features": [
            "transonic_target"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [
              {
                "feature": "max_mach_nom",
                "min": 0.78,
                "full": 0.88
              }
            ],
            "ramps": [
              {
                "feature": "tc_ratio",
                "x0": 0.08,
                "x1": 0.13,
                "weight": 0.48
              }
            ],
            "flags": [],
            "multipliers": [
              {
                "feature": "has_powered_controls",
                "mul": 0.35
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.06,
            "transonic_bump": 0.45,
            "transonic_slotted": 0.58,
            "flutter_model": 0.55,
            "flight:speed_envelope": 0.8
          },
          "flight_incident": {
            "encounter_weight": 0.22,
            "crash_prob_given_encounter": 0.08
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "max_mach_sl": 0.96
            }
          },
          "placard": {
            "name": "Mach 0.82 Buzz Placard",
            "metric_multipliers": {
              "max_mach_sl": 0.92,
              "max_mach_alt": 0.93
            },
            "residual_hazard_factor": 0.2
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.38,
            "accident_rate_per_1000fh": 0.08,
            "grounding_days": 0,
            "rep_penalty": 3.5
          },
          "fixes": [
            {
              "id": "viscous_hinge_dampers",
              "name": "Install Hydraulic Viscous Control Hinge Dampers",
              "available_year": 1946,
              "required_tech": null,
              "base_cost_1950_usd": 42000.0,
              "retrofit_kit_1950_usd": 1600.0,
              "fix_days": 18,
              "residual_factor": 0.1,
              "driver_log_deltas": {
                "mass": 0.004,
                "maint": 0.015
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "aileron_reversal",
          "name": "High-Q Aeroelastic Aileron Reversal",
          "family": "aileron_reversal",
          "category": "aeroelasticity",
          "base_severity": 4,
          "known_from_year": 1947,
          "unknown_symptom_label": "Control reversal in high-speed dive due to wing twist",
          "historical_examples": [
            "F-86A",
            "F-84F",
            "B-47 Stratojet"
          ],
          "max_prob": 0.82,
          "novelty_features": [
            "swept_wing",
            "high_sweep",
            "thin_wing"
          ],
          "trigger": {
            "base": 0.04,
            "gates": [
              {
                "feature": "q_dive_kpa",
                "min": 45.0,
                "full": 85.0
              }
            ],
            "ramps": [
              {
                "feature": "torsion_flex_index",
                "x0": 3.5,
                "x1": 12.0,
                "weight": 0.52
              },
              {
                "feature": "sweep_deg",
                "x0": 25.0,
                "x1": 45.0,
                "weight": 0.2
              }
            ],
            "flags": [],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.08,
            "flutter_model": 0.62,
            "transonic_slotted": 0.4,
            "flight:speed_envelope": 0.84,
            "flight:maneuver": 0.68
          },
          "flight_incident": {
            "encounter_weight": 0.3,
            "crash_prob_given_encounter": 0.18
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "max_mach_sl": 0.94
            }
          },
          "placard": {
            "name": "Low-Altitude Vne IAS Limit Placard",
            "metric_multipliers": {
              "max_mach_sl": 0.89
            },
            "residual_hazard_factor": 0.22
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.48,
            "accident_rate_per_1000fh": 0.16,
            "grounding_days": 35,
            "rep_penalty": 7.0
          },
          "fixes": [
            {
              "id": "wing_torsion_box_stiffening",
              "name": "Heavy-Gauge Wing Torsion Box & Inboard Aileron Lockout",
              "available_year": 1947,
              "required_tech": null,
              "base_cost_1950_usd": 130000.0,
              "retrofit_kit_1950_usd": 5800.0,
              "fix_days": 42,
              "residual_factor": 0.1,
              "driver_log_deltas": {
                "mass": 0.024,
                "cost_unit": 0.018
              },
              "metric_multipliers": {}
            },
            {
              "id": "spoiler_roll_control",
              "name": "Mid-Chord Roll Spoilers & Differential Tail",
              "available_year": 1952,
              "required_tech": "systems.powered_controls",
              "base_cost_1950_usd": 160000.0,
              "retrofit_kit_1950_usd": 7200.0,
              "fix_days": 48,
              "residual_factor": 0.06,
              "driver_log_deltas": {
                "mass": 0.012,
                "maint": 0.03
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "wing_bending_torsion_flutter",
          "name": "Explosive Wing Bending-Torsion Flutter",
          "family": "flutter",
          "category": "aeroelasticity",
          "base_severity": 5,
          "known_from_year": 1945,
          "unknown_symptom_label": "Catastrophic in-flight wing disintegration at high IAS",
          "historical_examples": [
            "F-84B",
            "XF-104",
            "F-100C with external stores"
          ],
          "max_prob": 0.8,
          "novelty_features": [
            "thin_wing",
            "swept_wing",
            "transonic_target"
          ],
          "trigger": {
            "base": 0.03,
            "gates": [
              {
                "feature": "q_dive_kpa",
                "min": 50.0,
                "full": 95.0
              }
            ],
            "ramps": [
              {
                "feature": "torsion_flex_index",
                "x0": 4.0,
                "x1": 13.0,
                "weight": 0.45
              },
              {
                "feature": "hardpoints",
                "x0": 2.0,
                "x1": 6.0,
                "weight": 0.18
              }
            ],
            "flags": [],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.06,
            "flutter_model": 0.7,
            "flight:speed_envelope": 0.82,
            "flight:weapons_stores": 0.6
          },
          "flight_incident": {
            "encounter_weight": 0.35,
            "crash_prob_given_encounter": 0.38
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "max_mach_sl": 0.92
            }
          },
          "placard": {
            "name": "Strict Vne Dive Speed Restriction",
            "metric_multipliers": {
              "max_mach_sl": 0.86,
              "max_mach_alt": 0.92
            },
            "residual_hazard_factor": 0.25
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.52,
            "accident_rate_per_1000fh": 0.26,
            "grounding_days": 60,
            "rep_penalty": 11.5
          },
          "fixes": [
            {
              "id": "wing_skin_spar_beefup",
              "name": "Thickened Milled Wing Skins & Leading-Edge Mass Balance",
              "available_year": 1945,
              "required_tech": null,
              "base_cost_1950_usd": 175000.0,
              "retrofit_kit_1950_usd": 8200.0,
              "fix_days": 55,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "mass": 0.028,
                "cost_unit": 0.022
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "empennage_t_tail_flutter",
          "name": "Empennage & T-Tail Aeroelastic Flutter",
          "family": "flutter",
          "category": "aeroelasticity",
          "base_severity": 4,
          "known_from_year": 1947,
          "unknown_symptom_label": "Violent tail section oscillation and fin failure",
          "historical_examples": [
            "F-89 Scorpion",
            "F-104A Starfighter",
            "F-101 Voodoo"
          ],
          "max_prob": 0.78,
          "novelty_features": [
            "t_tail",
            "thin_wing",
            "supersonic_level"
          ],
          "trigger": {
            "base": 0.04,
            "gates": [
              {
                "feature": "q_dive_kpa",
                "min": 48.0,
                "full": 90.0
              }
            ],
            "ramps": [
              {
                "feature": "max_mach_nom",
                "x0": 0.88,
                "x1": 1.6,
                "weight": 0.35
              }
            ],
            "flags": [
              {
                "feature": "is_t_tail",
                "add": 0.28
              }
            ],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.05,
            "flutter_model": 0.68,
            "flight:speed_envelope": 0.8
          },
          "flight_incident": {
            "encounter_weight": 0.3,
            "crash_prob_given_encounter": 0.3
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "max_mach_sl": 0.94
            }
          },
          "placard": {
            "name": "Empennage Dynamic Pressure Limit",
            "metric_multipliers": {
              "max_mach_sl": 0.89,
              "max_mach_alt": 0.93
            },
            "residual_hazard_factor": 0.22
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.45,
            "accident_rate_per_1000fh": 0.22,
            "grounding_days": 50,
            "rep_penalty": 9.0
          },
          "fixes": [
            {
              "id": "tail_spar_mass_balance",
              "name": "Fin Spar Stiffening & Irreversible Stabilator Mass Balance",
              "available_year": 1945,
              "required_tech": null,
              "base_cost_1950_usd": 115000.0,
              "retrofit_kit_1950_usd": 5200.0,
              "fix_days": 38,
              "residual_factor": 0.09,
              "driver_log_deltas": {
                "mass": 0.016,
                "cost_unit": 0.012
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "panel_transonic_flutter",
          "name": "Supersonic Aerodynamic Skin Panel Flutter",
          "family": "flutter",
          "category": "aeroelasticity",
          "base_severity": 3,
          "known_from_year": 1953,
          "unknown_symptom_label": "High-Mach skin panel acoustic fatigue and buckling",
          "historical_examples": [
            "F-100D",
            "F-105B",
            "B-58 Hustler"
          ],
          "max_prob": 0.75,
          "novelty_features": [
            "supersonic_level",
            "mach2_regime"
          ],
          "trigger": {
            "base": 0.04,
            "gates": [
              {
                "feature": "max_mach_nom",
                "min": 1.15,
                "full": 1.75
              }
            ],
            "ramps": [
              {
                "feature": "q_dive_kpa",
                "x0": 60.0,
                "x1": 110.0,
                "weight": 0.45
              }
            ],
            "flags": [],
            "multipliers": [
              {
                "feature": "has_honeycomb",
                "mul": 0.35
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.04,
            "supersonic_tunnel": 0.4,
            "flutter_model": 0.5,
            "flight:speed_envelope": 0.76
          },
          "flight_incident": {
            "encounter_weight": 0.2,
            "crash_prob_given_encounter": 0.1
          },
          "truth_effects": {
            "driver_log_deltas": {
              "maint": 0.12
            },
            "metric_multipliers": {}
          },
          "placard": {
            "name": "Supersonic Low-Level Dash Time Limit",
            "metric_multipliers": {
              "max_mach_sl": 0.93
            },
            "residual_hazard_factor": 0.25
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.42,
            "accident_rate_per_1000fh": 0.09,
            "grounding_days": 20,
            "rep_penalty": 5.0
          },
          "fixes": [
            {
              "id": "skin_doublers_honeycomb",
              "name": "Internal Frame Doublers & Bonded Skin Stiffeners",
              "available_year": 1950,
              "required_tech": null,
              "base_cost_1950_usd": 85000.0,
              "retrofit_kit_1950_usd": 3600.0,
              "fix_days": 30,
              "residual_factor": 0.1,
              "driver_log_deltas": {
                "mass": 0.012,
                "maint": -0.08
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "unrecoverable_flat_spin",
          "name": "Irrecoverable Flat Spin Mode",
          "family": "spin",
          "category": "stability_control",
          "base_severity": 5,
          "known_from_year": 1945,
          "unknown_symptom_label": "Locked flat spin with zero rudder recovery authority",
          "historical_examples": [
            "F7U Cutlass",
            "XF-92A",
            "F-100A",
            "F-104A"
          ],
          "max_prob": 0.8,
          "novelty_features": [
            "delta_wing",
            "high_sweep",
            "t_tail"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [
              {
                "feature": "sweep_deg",
                "min": 20.0,
                "full": 38.0
              }
            ],
            "ramps": [
              {
                "feature": "fuselage_to_span_ratio",
                "x0": 1.1,
                "x1": 2.0,
                "weight": 0.35
              },
              {
                "feature": "vv_deficit",
                "x0": -0.01,
                "x1": 0.04,
                "weight": 0.3
              }
            ],
            "flags": [
              {
                "feature": "is_t_tail",
                "add": 0.14
              }
            ],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.05,
            "spin_tunnel": 0.72,
            "flight:high_aoa_spin": 0.86,
            "flight:maneuver": 0.4
          },
          "flight_incident": {
            "encounter_weight": 0.36,
            "crash_prob_given_encounter": 0.36
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "instantaneous_turn_dps_m08_4572m": 0.9
            }
          },
          "placard": {
            "name": "Intentional Spin Prohibited / AoA Placard",
            "metric_multipliers": {
              "instantaneous_turn_dps_m08_4572m": 0.84,
              "sustained_turn_dps_m08_4572m": 0.9
            },
            "residual_hazard_factor": 0.28
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.48,
            "accident_rate_per_1000fh": 0.25,
            "grounding_days": 45,
            "rep_penalty": 9.5
          },
          "fixes": [
            {
              "id": "ventral_strakes_unshielded_rudder",
              "name": "Aft Fuselage Anti-Spin Strakes & Extended Rudder Chord",
              "available_year": 1945,
              "required_tech": null,
              "base_cost_1950_usd": 92000.0,
              "retrofit_kit_1950_usd": 4100.0,
              "fix_days": 34,
              "residual_factor": 0.12,
              "driver_log_deltas": {
                "cd0": 0.011,
                "mass": 0.009
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "swept_wing_dutch_roll",
          "name": "Lightly Damped High-Altitude Dutch Roll",
          "family": "spin",
          "category": "stability_control",
          "base_severity": 2,
          "known_from_year": 1948,
          "unknown_symptom_label": "Nuisance coupled yaw-roll oscillation ruining gun/rocket tracking",
          "historical_examples": [
            "F-86A",
            "B-47",
            "F-89"
          ],
          "max_prob": 0.85,
          "novelty_features": [
            "swept_wing",
            "high_sweep"
          ],
          "trigger": {
            "base": 0.08,
            "gates": [
              {
                "feature": "sweep_deg",
                "min": 22.0,
                "full": 35.0
              }
            ],
            "ramps": [
              {
                "feature": "vv_deficit",
                "x0": -0.02,
                "x1": 0.03,
                "weight": 0.38
              },
              {
                "feature": "service_ceiling_nom_m",
                "x0": 12000.0,
                "x1": 16000.0,
                "weight": 0.25
              }
            ],
            "flags": [],
            "multipliers": [
              {
                "feature": "has_sas",
                "mul": 0.22
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.12,
            "low_speed_tunnel": 0.38,
            "flight:altitude_envelope": 0.78,
            "flight:weapons_stores": 0.7
          },
          "flight_incident": {
            "encounter_weight": 0.15,
            "crash_prob_given_encounter": 0.03
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "sustained_turn_dps_m08_4572m": 0.94
            }
          },
          "placard": {
            "name": "High-Altitude Autopilot / Rudder Coordination Restriction",
            "metric_multipliers": {
              "service_ceiling_m": 0.94
            },
            "residual_hazard_factor": 0.25
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.45,
            "accident_rate_per_1000fh": 0.04,
            "grounding_days": 0,
            "rep_penalty": 3.5
          },
          "fixes": [
            {
              "id": "single_axis_yaw_damper",
              "name": "Install Rate-Gyro Automatic Rudder Yaw Damper",
              "available_year": 1949,
              "required_tech": "systems.stability_augmentation",
              "base_cost_1950_usd": 52000.0,
              "retrofit_kit_1950_usd": 2100.0,
              "fix_days": 22,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "mass": 0.004,
                "maint": 0.02
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "high_aoa_adverse_yaw",
          "name": "High-Alpha Aileron Adverse Yaw Departure",
          "family": "spin",
          "category": "stability_control",
          "base_severity": 3,
          "known_from_year": 1948,
          "unknown_symptom_label": "Violent nose-slice opposite to roll input at high angle of attack",
          "historical_examples": [
            "F-100A/C",
            "F-102A",
            "F4H-1"
          ],
          "max_prob": 0.8,
          "novelty_features": [
            "high_sweep",
            "delta_wing"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [
              {
                "feature": "sweep_deg",
                "min": 28.0,
                "full": 42.0
              }
            ],
            "ramps": [
              {
                "feature": "shortal_maggin_excess",
                "x0": -0.5,
                "x1": 1.2,
                "weight": 0.42
              }
            ],
            "flags": [
              {
                "feature": "is_delta",
                "add": 0.16
              }
            ],
            "multipliers": [
              {
                "feature": "has_sas",
                "mul": 0.5
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.06,
            "low_speed_tunnel": 0.35,
            "spin_tunnel": 0.45,
            "flight:maneuver": 0.72,
            "flight:high_aoa_spin": 0.8
          },
          "flight_incident": {
            "encounter_weight": 0.26,
            "crash_prob_given_encounter": 0.15
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "instantaneous_turn_dps_m08_4572m": 0.88
            }
          },
          "placard": {
            "name": "Rudder-Roll Only Above 12° AoA Placard",
            "metric_multipliers": {
              "instantaneous_turn_dps_m08_4572m": 0.82
            },
            "residual_hazard_factor": 0.24
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.42,
            "accident_rate_per_1000fh": 0.14,
            "grounding_days": 25,
            "rep_penalty": 5.5
          },
          "fixes": [
            {
              "id": "aileron_rudder_interconnect",
              "name": "Install Mechanical/Hydraulic Aileron-Rudder Interconnect (ARI)",
              "available_year": 1950,
              "required_tech": null,
              "base_cost_1950_usd": 65000.0,
              "retrofit_kit_1950_usd": 2600.0,
              "fix_days": 26,
              "residual_factor": 0.12,
              "driver_log_deltas": {
                "mass": 0.005,
                "maint": 0.02
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "tip_stall_wing_drop",
          "name": "Asymmetric Low-Speed Tip Stall & Wing Drop",
          "family": "spin",
          "category": "aerodynamics",
          "base_severity": 3,
          "known_from_year": 1946,
          "unknown_symptom_label": "Sudden uncommanded 60° bank roll-off on landing approach",
          "historical_examples": [
            "FJ-2 Fury",
            "F-86F '6-3' hard wing",
            "F9F-6 Cougar"
          ],
          "max_prob": 0.82,
          "novelty_features": [
            "swept_wing",
            "thin_wing"
          ],
          "trigger": {
            "base": 0.06,
            "gates": [
              {
                "feature": "sweep_deg",
                "min": 18.0,
                "full": 34.0
              }
            ],
            "ramps": [
              {
                "feature": "taper_deficit",
                "x0": 0.0,
                "x1": 0.3,
                "weight": 0.35
              },
              {
                "feature": "shortal_maggin_excess",
                "x0": -0.6,
                "x1": 1.0,
                "weight": 0.28
              }
            ],
            "flags": [],
            "multipliers": [
              {
                "feature": "has_le_slats",
                "mul": 0.35
              },
              {
                "feature": "has_wing_fences",
                "mul": 0.55
              },
              {
                "feature": "has_le_flaps",
                "mul": 0.5
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.1,
            "low_speed_tunnel": 0.6,
            "flight:low_speed": 0.85,
            "flight:high_aoa_spin": 0.72
          },
          "flight_incident": {
            "encounter_weight": 0.25,
            "crash_prob_given_encounter": 0.12
          },
          "truth_effects": {
            "driver_log_deltas": {
              "clmax": -0.08
            },
            "metric_multipliers": {
              "landing_distance_m": 1.12
            }
          },
          "placard": {
            "name": "+15 Knot Approach Speed Margin Placard",
            "metric_multipliers": {
              "landing_distance_m": 1.22,
              "stall_speed_mps": 1.08
            },
            "residual_hazard_factor": 0.22
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.5,
            "accident_rate_per_1000fh": 0.12,
            "grounding_days": 0,
            "rep_penalty": 5.0
          },
          "fixes": [
            {
              "id": "wing_fences",
              "name": "Install Boundary-Layer Wing Fences",
              "available_year": 1948,
              "required_tech": null,
              "base_cost_1950_usd": 45000.0,
              "retrofit_kit_1950_usd": 1800.0,
              "fix_days": 21,
              "residual_factor": 0.18,
              "driver_log_deltas": {
                "cd0": 0.015,
                "mass": 0.004
              },
              "metric_multipliers": {}
            },
            {
              "id": "auto_le_slats",
              "name": "Retrofit Automatic Leading-Edge Slats",
              "available_year": 1947,
              "required_tech": "aero.le_slats",
              "base_cost_1950_usd": 140000.0,
              "retrofit_kit_1950_usd": 6500.0,
              "fix_days": 50,
              "residual_factor": 0.06,
              "driver_log_deltas": {
                "cd0": 0.012,
                "clmax": 0.08,
                "mass": 0.018
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "delta_high_sink_approach",
          "name": "Backside-of-Power-Curve High-Sink Approach Instability",
          "family": "spin",
          "category": "aerodynamics",
          "base_severity": 3,
          "known_from_year": 1951,
          "unknown_symptom_label": "Dangerous induced-drag sink rate on final approach",
          "historical_examples": [
            "F4D-1 Skyray",
            "F7U Cutlass",
            "F-102A",
            "F-104A"
          ],
          "max_prob": 0.8,
          "novelty_features": [
            "delta_wing",
            "thin_wing"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [
              {
                "feature": "wing_loading_kgm2",
                "min": 210.0,
                "full": 380.0
              }
            ],
            "ramps": [
              {
                "feature": "low_ar_excess",
                "x0": 0.0,
                "x1": 1.8,
                "weight": 0.45
              },
              {
                "feature": "wing_loading_kgm2",
                "x0": 260.0,
                "x1": 480.0,
                "weight": 0.25
              }
            ],
            "flags": [
              {
                "feature": "is_delta",
                "add": 0.18
              }
            ],
            "multipliers": [
              {
                "feature": "has_blown_flaps",
                "mul": 0.4
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.12,
            "low_speed_tunnel": 0.52,
            "flight:low_speed": 0.88
          },
          "flight_incident": {
            "encounter_weight": 0.26,
            "crash_prob_given_encounter": 0.14
          },
          "truth_effects": {
            "driver_log_deltas": {
              "kind": 0.06
            },
            "metric_multipliers": {
              "landing_distance_m": 1.18,
              "takeoff_distance_m": 1.1
            }
          },
          "placard": {
            "name": "High-Power Flat Approach & Minimum Runway Length Placard",
            "metric_multipliers": {
              "landing_distance_m": 1.28
            },
            "residual_hazard_factor": 0.25
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.48,
            "accident_rate_per_1000fh": 0.14,
            "grounding_days": 0,
            "rep_penalty": 5.5
          },
          "fixes": [
            {
              "id": "braking_parachute_le_droop",
              "name": "Install Ribbon Drag Chute & Leading-Edge Droop Camber",
              "available_year": 1950,
              "required_tech": null,
              "base_cost_1950_usd": 68000.0,
              "retrofit_kit_1950_usd": 2900.0,
              "fix_days": 28,
              "residual_factor": 0.14,
              "driver_log_deltas": {
                "mass": 0.008,
                "clmax": 0.05
              },
              "metric_multipliers": {
                "landing_distance_m": 0.88
              }
            },
            {
              "id": "blc_blown_flap_system",
              "name": "Install Compressor-Bleed Boundary-Layer Control (BLC) Flaps",
              "available_year": 1955,
              "required_tech": "aero.blown_flaps",
              "base_cost_1950_usd": 155000.0,
              "retrofit_kit_1950_usd": 7000.0,
              "fix_days": 46,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "clmax": 0.14,
                "mass": 0.014,
                "maint": 0.04
              },
              "metric_multipliers": {
                "landing_distance_m": 0.84
              }
            }
          ]
        },
        {
          "id": "area_rule_drag_pinch",
          "name": "Transonic Area-Rule Wave-Drag Wall (YF-102 Syndrome)",
          "family": "inlet",
          "category": "aerodynamics",
          "base_severity": 4,
          "known_from_year": 1952,
          "unknown_symptom_label": "Severe unexpected transonic drag rise preventing supersonic flight",
          "historical_examples": [
            "Convair YF-102 (stuck at M0.98)",
            "Grumman F11F-1",
            "Chance Vought F8U"
          ],
          "max_prob": 0.88,
          "novelty_features": [
            "supersonic_level",
            "delta_wing",
            "transonic_target"
          ],
          "trigger": {
            "base": 0.08,
            "gates": [
              {
                "feature": "max_mach_nom",
                "min": 0.96,
                "full": 1.22
              }
            ],
            "ramps": [
              {
                "feature": "wave_drag_ratio",
                "x0": 1.55,
                "x1": 2.45,
                "weight": 0.55
              },
              {
                "feature": "mach_dd_excess",
                "x0": 0.02,
                "x1": 0.25,
                "weight": 0.22
              }
            ],
            "flags": [],
            "multipliers": [
              {
                "feature": "is_area_ruled",
                "mul": 0.18
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.04,
            "transonic_bump": 0.35,
            "rocket_model": 0.72,
            "transonic_slotted": 0.85,
            "supersonic_tunnel": 0.45,
            "flight:speed_envelope": 0.95
          },
          "flight_incident": {
            "encounter_weight": 0.15,
            "crash_prob_given_encounter": 0.02
          },
          "truth_effects": {
            "driver_log_deltas": {
              "cdw": 0.22
            },
            "metric_multipliers": {
              "max_mach_alt": 0.88,
              "ps_mps_m09_4572m_1g": 0.82
            }
          },
          "placard": {
            "name": "Subsonic Operational Envelope Acceptance",
            "metric_multipliers": {
              "max_mach_alt": 0.86
            },
            "residual_hazard_factor": 0.3
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.85,
            "accident_rate_per_1000fh": 0.02,
            "grounding_days": 30,
            "rep_penalty": 10.0
          },
          "fixes": [
            {
              "id": "wasp_waist_area_rule_redesign",
              "name": "Whitcomb 'Coke-Bottle' Wasp-Waist Fuselage Redesign & Tail Fairings",
              "available_year": 1953,
              "required_tech": "aero.area_rule",
              "base_cost_1950_usd": 280000.0,
              "retrofit_kit_1950_usd": 18000.0,
              "fix_days": 85,
              "residual_factor": 0.05,
              "driver_log_deltas": {
                "cdw": -0.18,
                "mass": 0.015
              },
              "metric_multipliers": {}
            },
            {
              "id": "local_fairing_area_cleanup",
              "name": "Wing-Root Glove & Aft Kuchemann Anti-Shock Carrots",
              "available_year": 1951,
              "required_tech": null,
              "base_cost_1950_usd": 110000.0,
              "retrofit_kit_1950_usd": 5200.0,
              "fix_days": 40,
              "residual_factor": 0.3,
              "driver_log_deltas": {
                "cdw": -0.06,
                "mass": 0.008
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "supersonic_intake_buzz",
          "name": "Supersonic Shock-Disgorging Inlet Buzz (Ferri Instability)",
          "family": "inlet",
          "category": "propulsion",
          "base_severity": 3,
          "known_from_year": 1953,
          "unknown_symptom_label": "Violent supersonic inlet shock oscillation and thrust loss",
          "historical_examples": [
            "F-100A/C",
            "F-104A",
            "F-105B"
          ],
          "max_prob": 0.82,
          "novelty_features": [
            "supersonic_level",
            "mach2_regime",
            "variable_intake"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [
              {
                "feature": "max_mach_nom",
                "min": 1.3,
                "full": 1.85
              }
            ],
            "ramps": [
              {
                "feature": "max_mach_nom",
                "x0": 1.35,
                "x1": 2.15,
                "weight": 0.55
              }
            ],
            "flags": [],
            "multipliers": [
              {
                "feature": "is_variable_intake",
                "mul": 0.38
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.06,
            "supersonic_tunnel": 0.74,
            "engine_altitude_cell": 0.55,
            "flight:speed_envelope": 0.86
          },
          "flight_incident": {
            "encounter_weight": 0.25,
            "crash_prob_given_encounter": 0.1
          },
          "truth_effects": {
            "driver_log_deltas": {
              "thrust": -0.07,
              "cdw": 0.05
            },
            "metric_multipliers": {
              "max_mach_alt": 0.94
            }
          },
          "placard": {
            "name": "Supersonic Inlet Mach Cap (M 1.45)",
            "metric_multipliers": {
              "max_mach_alt": 0.9
            },
            "residual_hazard_factor": 0.22
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.45,
            "accident_rate_per_1000fh": 0.09,
            "grounding_days": 20,
            "rep_penalty": 5.5
          },
          "fixes": [
            {
              "id": "inlet_bypass_bleed_doors",
              "name": "Install Automatic Subsonic-Duct Spill & Boundary-Layer Bleed Doors",
              "available_year": 1953,
              "required_tech": null,
              "base_cost_1950_usd": 95000.0,
              "retrofit_kit_1950_usd": 4400.0,
              "fix_days": 35,
              "residual_factor": 0.12,
              "driver_log_deltas": {
                "mass": 0.009,
                "maint": 0.03
              },
              "metric_multipliers": {}
            },
            {
              "id": "translating_shock_cone",
              "name": "Convert to Variable Translating Shock Cone / Ramp Inlet",
              "available_year": 1955,
              "required_tech": "aero.inlet_variable",
              "base_cost_1950_usd": 195000.0,
              "retrofit_kit_1950_usd": 9500.0,
              "fix_days": 60,
              "residual_factor": 0.05,
              "driver_log_deltas": {
                "thrust": 0.04,
                "mass": 0.018,
                "maint": 0.05
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "inlet_distortion_recoverable",
          "name": "High-Alpha Cheek/Root Inlet Boundary-Layer Ingestion",
          "family": "inlet",
          "category": "propulsion",
          "base_severity": 3,
          "known_from_year": 1950,
          "unknown_symptom_label": "Asymmetric duct flow separation and thrust rumble in turns",
          "historical_examples": [
            "F-101A Voodoo",
            "F11F Tiger",
            "F-102A"
          ],
          "max_prob": 0.78,
          "novelty_features": [
            "swept_wing",
            "supersonic_level"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [
              {
                "feature": "non_nose_intake",
                "min": 0.5,
                "full": 1.0
              }
            ],
            "ramps": [
              {
                "feature": "max_mach_nom",
                "x0": 0.85,
                "x1": 1.6,
                "weight": 0.35
              },
              {
                "feature": "fuselage_fineness",
                "x0": 7.0,
                "x1": 12.0,
                "weight": 0.25
              }
            ],
            "flags": [],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.08,
            "low_speed_tunnel": 0.4,
            "transonic_slotted": 0.55,
            "engine_altitude_cell": 0.48,
            "flight:maneuver": 0.8
          },
          "flight_incident": {
            "encounter_weight": 0.22,
            "crash_prob_given_encounter": 0.08
          },
          "truth_effects": {
            "driver_log_deltas": {
              "thrust": -0.05,
              "tsfc": 0.03
            },
            "metric_multipliers": {}
          },
          "placard": {
            "name": "High-AoA Throttle Movement Restriction",
            "metric_multipliers": {
              "sustained_turn_dps_m08_4572m": 0.92
            },
            "residual_hazard_factor": 0.25
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.42,
            "accident_rate_per_1000fh": 0.08,
            "grounding_days": 0,
            "rep_penalty": 4.5
          },
          "fixes": [
            {
              "id": "splitter_plate_diverter",
              "name": "Enlarged Boundary-Layer Splitter Plate & Lip Camber",
              "available_year": 1948,
              "required_tech": null,
              "base_cost_1950_usd": 62000.0,
              "retrofit_kit_1950_usd": 2400.0,
              "fix_days": 25,
              "residual_factor": 0.12,
              "driver_log_deltas": {
                "cd0": 0.006,
                "mass": 0.005
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "compressor_surge_stall",
          "name": "High-OPR Axial Compressor Surge & Rotating Stall",
          "family": "engine_stall",
          "category": "propulsion",
          "base_severity": 4,
          "known_from_year": 1947,
          "unknown_symptom_label": "Explosive compressor backfire and turbine over-temperature on throttle slam",
          "historical_examples": [
            "Allison J35",
            "Wright J65 (F-84F)",
            "Allison J71 (F3H-2)"
          ],
          "max_prob": 0.82,
          "novelty_features": [
            "transonic_target",
            "supersonic_level"
          ],
          "trigger": {
            "base": 0.06,
            "gates": [],
            "ramps": [
              {
                "feature": "stall_margin_deficit",
                "x0": 0.0,
                "x1": 0.14,
                "weight": 0.55
              },
              {
                "feature": "engine_immaturity",
                "x0": 0.1,
                "x1": 0.8,
                "weight": 0.25
              }
            ],
            "flags": [
              {
                "feature": "non_nose_intake",
                "add": 0.1
              }
            ],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.08,
            "engine_altitude_cell": 0.72,
            "flight:altitude_envelope": 0.82,
            "flight:maneuver": 0.7
          },
          "flight_incident": {
            "encounter_weight": 0.3,
            "crash_prob_given_encounter": 0.18
          },
          "truth_effects": {
            "driver_log_deltas": {
              "thrust": -0.05,
              "maint": 0.12
            },
            "metric_multipliers": {}
          },
          "placard": {
            "name": "Slow Throttle Advancement & Altitude RPM Restriction",
            "metric_multipliers": {
              "service_ceiling_m": 0.94,
              "sustained_turn_dps_m08_4572m": 0.93
            },
            "residual_hazard_factor": 0.25
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.55,
            "accident_rate_per_1000fh": 0.16,
            "grounding_days": 40,
            "rep_penalty": 8.0
          },
          "fixes": [
            {
              "id": "interstage_bleed_fuel_schedule",
              "name": "Automatic Interstage Compressor Bleed Valves & Hydromechanical Fuel Limiter",
              "available_year": 1948,
              "required_tech": null,
              "base_cost_1950_usd": 110000.0,
              "retrofit_kit_1950_usd": 4800.0,
              "fix_days": 38,
              "residual_factor": 0.12,
              "driver_log_deltas": {
                "tsfc": 0.015,
                "mass": 0.006
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "gun_gas_ingestion_surge",
          "name": "Cannon Muzzle-Gas Ingestion Compressor Stall (GunVal)",
          "family": "engine_stall",
          "category": "propulsion",
          "base_severity": 4,
          "known_from_year": 1952,
          "unknown_symptom_label": "Immediate engine flameout upon firing nose armament at altitude",
          "historical_examples": [
            "F-86F-2 GunVal (T-160 20mm)",
            "F-101A",
            "F11F Tiger",
            "F-86H"
          ],
          "max_prob": 0.85,
          "novelty_features": [
            "transonic_target",
            "supersonic_level"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [
              {
                "feature": "has_guns",
                "min": 0.5,
                "full": 1.0
              }
            ],
            "ramps": [
              {
                "feature": "gun_caliber_mm",
                "x0": 12.7,
                "x1": 25.0,
                "weight": 0.35
              },
              {
                "feature": "stall_margin_deficit",
                "x0": 0.0,
                "x1": 0.12,
                "weight": 0.25
              }
            ],
            "flags": [
              {
                "feature": "guns_near_intake",
                "add": 0.32
              }
            ],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.04,
            "engine_altitude_cell": 0.25,
            "flight:weapons_stores": 0.9
          },
          "flight_incident": {
            "encounter_weight": 0.28,
            "crash_prob_given_encounter": 0.14
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {}
          },
          "placard": {
            "name": "Prohibit Gun Firing Above 30,000 ft / Salvo Limit",
            "metric_multipliers": {
              "service_ceiling_m": 0.92
            },
            "residual_hazard_factor": 0.22
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.5,
            "accident_rate_per_1000fh": 0.14,
            "grounding_days": 30,
            "rep_penalty": 7.0
          },
          "fixes": [
            {
              "id": "gun_purge_blast_deflectors",
              "name": "Install Muzzle Gas Deflector Louvers, Gun Bay Purge & Continuous Igniter",
              "available_year": 1951,
              "required_tech": null,
              "base_cost_1950_usd": 68000.0,
              "retrofit_kit_1950_usd": 2800.0,
              "fix_days": 26,
              "residual_factor": 0.1,
              "driver_log_deltas": {
                "cd0": 0.008,
                "mass": 0.006
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "high_altitude_flameout",
          "name": "Stratospheric Combustor Blowout & Relight Failure",
          "family": "engine_stall",
          "category": "propulsion",
          "base_severity": 3,
          "known_from_year": 1948,
          "unknown_symptom_label": "Combustor flameout above 42,000 ft with dead-stick descent",
          "historical_examples": [
            "GE J47",
            "Wright J65",
            "Early P&W J57"
          ],
          "max_prob": 0.8,
          "novelty_features": [
            "transonic_target",
            "supersonic_level"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [
              {
                "feature": "service_ceiling_nom_m",
                "min": 12000.0,
                "full": 15000.0
              }
            ],
            "ramps": [
              {
                "feature": "flameout_ceiling_deficit_m",
                "x0": -500.0,
                "x1": 2500.0,
                "weight": 0.5
              },
              {
                "feature": "engine_immaturity",
                "x0": 0.1,
                "x1": 0.8,
                "weight": 0.22
              }
            ],
            "flags": [],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.1,
            "engine_altitude_cell": 0.82,
            "flight:altitude_envelope": 0.86
          },
          "flight_incident": {
            "encounter_weight": 0.25,
            "crash_prob_given_encounter": 0.12
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "service_ceiling_m": 0.91
            }
          },
          "placard": {
            "name": "40,000 ft Operational Altitude Ceiling Placard",
            "metric_multipliers": {
              "service_ceiling_m": 0.86
            },
            "residual_hazard_factor": 0.2
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.45,
            "accident_rate_per_1000fh": 0.12,
            "grounding_days": 20,
            "rep_penalty": 5.5
          },
          "fixes": [
            {
              "id": "high_energy_capacitor_igniter",
              "name": "High-Energy Capacitor Discharge Igniter & Annular Crossover Tubes",
              "available_year": 1949,
              "required_tech": null,
              "base_cost_1950_usd": 72000.0,
              "retrofit_kit_1950_usd": 3100.0,
              "fix_days": 28,
              "residual_factor": 0.1,
              "driver_log_deltas": {
                "mass": 0.004,
                "maint": 0.02
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "afterburner_lightoff_instability",
          "name": "Afterburner Light-Off Failure & Screech Liner Burnthrough",
          "family": "engine_stall",
          "category": "propulsion",
          "base_severity": 3,
          "known_from_year": 1949,
          "unknown_symptom_label": "Hard afterburner light-off explosion and eyelid nozzle jamming",
          "historical_examples": [
            "F-94B Starfire",
            "F7U Cutlass (J46)",
            "F-100A (J57-P-7)"
          ],
          "max_prob": 0.82,
          "novelty_features": [
            "afterburner",
            "supersonic_level"
          ],
          "trigger": {
            "base": 0.08,
            "gates": [
              {
                "feature": "has_afterburner",
                "min": 0.5,
                "full": 1.0
              }
            ],
            "ramps": [
              {
                "feature": "ab_immaturity",
                "x0": 0.05,
                "x1": 0.75,
                "weight": 0.58
              }
            ],
            "flags": [],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.1,
            "engine_altitude_cell": 0.78,
            "flight:altitude_envelope": 0.8,
            "flight:speed_envelope": 0.7
          },
          "flight_incident": {
            "encounter_weight": 0.25,
            "crash_prob_given_encounter": 0.1
          },
          "truth_effects": {
            "driver_log_deltas": {
              "thrust": -0.05,
              "tsfc": 0.05,
              "maint": 0.15
            },
            "metric_multipliers": {}
          },
          "placard": {
            "name": "Restrict Afterburner Light-Off Below 35,000 ft",
            "metric_multipliers": {
              "max_mach_alt": 0.92,
              "climb_rate_sl_mps": 0.9
            },
            "residual_hazard_factor": 0.22
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.48,
            "accident_rate_per_1000fh": 0.1,
            "grounding_days": 20,
            "rep_penalty": 5.0
          },
          "fixes": [
            {
              "id": "hot_streak_ab_igniter",
              "name": "Install 'Hot-Streak' Turbine-Torch Igniter & Corrugated Screech Liner",
              "available_year": 1951,
              "required_tech": null,
              "base_cost_1950_usd": 82000.0,
              "retrofit_kit_1950_usd": 3600.0,
              "fix_days": 30,
              "residual_factor": 0.12,
              "driver_log_deltas": {
                "mass": 0.006,
                "maint": -0.08
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "prototype_engine_teething",
          "name": "Immature Powerplant Turbine Creep & Bearing Distress (J40 Syndrome)",
          "family": "engine_stall",
          "category": "propulsion",
          "base_severity": 4,
          "known_from_year": 1945,
          "unknown_symptom_label": "Severe premature turbine blade cracking and oil-seal failure",
          "historical_examples": [
            "Westinghouse J40 (F3H-1 Demon)",
            "Wright J65 early blocks",
            "J71"
          ],
          "max_prob": 0.85,
          "novelty_features": [
            "afterburner",
            "supersonic_level"
          ],
          "trigger": {
            "base": 0.04,
            "gates": [
              {
                "feature": "engine_immaturity",
                "min": 0.25,
                "full": 0.65
              }
            ],
            "ramps": [
              {
                "feature": "engine_immaturity",
                "x0": 0.25,
                "x1": 0.85,
                "weight": 0.65
              }
            ],
            "flags": [],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.12,
            "engine_altitude_cell": 0.75,
            "flight:altitude_envelope": 0.78,
            "flight:weapons_stores": 0.68
          },
          "flight_incident": {
            "encounter_weight": 0.32,
            "crash_prob_given_encounter": 0.2
          },
          "truth_effects": {
            "driver_log_deltas": {
              "thrust": -0.06,
              "maint": 0.25
            },
            "metric_multipliers": {}
          },
          "placard": {
            "name": "92% Military Thrust Derating & 50-Hour Engine Teardown",
            "metric_multipliers": {
              "max_mach_sl": 0.94,
              "climb_rate_sl_mps": 0.88,
              "maint_mh_per_fh": 1.3
            },
            "residual_hazard_factor": 0.25
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.65,
            "accident_rate_per_1000fh": 0.2,
            "grounding_days": 55,
            "rep_penalty": 10.5
          },
          "fixes": [
            {
              "id": "engine_cip_durability_rework",
              "name": "150-Hour Model Qualification & Turbine Hot-Section Redesign (CIP)",
              "available_year": 1945,
              "required_tech": null,
              "base_cost_1950_usd": 195000.0,
              "retrofit_kit_1950_usd": 9200.0,
              "fix_days": 60,
              "residual_factor": 0.1,
              "driver_log_deltas": {
                "mass": 0.012,
                "maint": -0.15
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "wing_root_fatigue_cracking",
          "name": "Main Wing Carry-Through Spar Fatigue & Under-Strength",
          "family": "structural_fatigue",
          "category": "structures",
          "base_severity": 4,
          "known_from_year": 1948,
          "unknown_symptom_label": "Premature wing root spar cap cracking under high-g maneuvering",
          "historical_examples": [
            "F-84B/C Thunderjet",
            "F-86A",
            "F3H Demon"
          ],
          "max_prob": 0.78,
          "novelty_features": [
            "thin_wing",
            "swept_wing",
            "high_sweep"
          ],
          "trigger": {
            "base": 0.04,
            "gates": [
              {
                "feature": "design_load_factor_g",
                "min": 6.5,
                "full": 8.0
              }
            ],
            "ramps": [
              {
                "feature": "torsion_flex_index",
                "x0": 3.0,
                "x1": 11.0,
                "weight": 0.42
              },
              {
                "feature": "wing_loading_kgm2",
                "x0": 240.0,
                "x1": 460.0,
                "weight": 0.22
              }
            ],
            "flags": [],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.06,
            "static_structural": 0.82,
            "flight:maneuver": 0.7
          },
          "flight_incident": {
            "encounter_weight": 0.25,
            "crash_prob_given_encounter": 0.28
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "max_load_factor_g": 0.84
            }
          },
          "placard": {
            "name": "5.0g Flight Manual G-Limit Placard",
            "metric_multipliers": {
              "max_load_factor_g": 0.75,
              "instantaneous_turn_dps_m08_4572m": 0.82
            },
            "residual_hazard_factor": 0.2
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.48,
            "accident_rate_per_1000fh": 0.22,
            "grounding_days": 55,
            "rep_penalty": 9.5
          },
          "fixes": [
            {
              "id": "forged_spar_cap_straps",
              "name": "Install Milled 7075/Steel Spar Cap Doublers & Carry-Through Forging",
              "available_year": 1945,
              "required_tech": null,
              "base_cost_1950_usd": 145000.0,
              "retrofit_kit_1950_usd": 6800.0,
              "fix_days": 45,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "mass": 0.026,
                "cost_unit": 0.015
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "landing_gear_shimmy_collapse",
          "name": "Main/Nose Landing Gear Shimmy & Thin-Wing Retraction Binding",
          "family": "structural_fatigue",
          "category": "structures",
          "base_severity": 3,
          "known_from_year": 1945,
          "unknown_symptom_label": "High-speed touchdown strut shimmy and gear door failure",
          "historical_examples": [
            "F7U Cutlass nose strut",
            "F-104A",
            "F-100C"
          ],
          "max_prob": 0.78,
          "novelty_features": [
            "thin_wing"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [],
            "ramps": [
              {
                "feature": "thin_wing_excess",
                "x0": 0.0,
                "x1": 0.05,
                "weight": 0.38
              },
              {
                "feature": "wing_loading_kgm2",
                "x0": 250.0,
                "x1": 480.0,
                "weight": 0.25
              }
            ],
            "flags": [
              {
                "feature": "carrier_capable",
                "add": 0.18
              }
            ],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.08,
            "static_structural": 0.65,
            "mockup_review": 0.4,
            "flight:low_speed": 0.8
          },
          "flight_incident": {
            "encounter_weight": 0.24,
            "crash_prob_given_encounter": 0.1
          },
          "truth_effects": {
            "driver_log_deltas": {
              "maint": 0.08
            },
            "metric_multipliers": {}
          },
          "placard": {
            "name": "Reduced Gross Landing Weight & Crosswind Limit",
            "metric_multipliers": {
              "landing_distance_m": 1.12
            },
            "residual_hazard_factor": 0.25
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.45,
            "accident_rate_per_1000fh": 0.1,
            "grounding_days": 15,
            "rep_penalty": 4.5
          },
          "fixes": [
            {
              "id": "heavy_duty_oleo_shimmy_damper",
              "name": "Forged Steel Oleo Strut, Hydraulic Shimmy Damper & Fuselage Stowage",
              "available_year": 1945,
              "required_tech": null,
              "base_cost_1950_usd": 65000.0,
              "retrofit_kit_1950_usd": 2800.0,
              "fix_days": 25,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "mass": 0.014,
                "cost_unit": 0.01
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "aft_fuselage_ab_overheating",
          "name": "Afterburner Tailpipe Structure Overheating & Bay Fire Hazard",
          "family": "structural_fatigue",
          "category": "structures",
          "base_severity": 3,
          "known_from_year": 1951,
          "unknown_symptom_label": "Aft fuselage aluminum frame annealing and fire warning above M 1.1",
          "historical_examples": [
            "F-100A/C",
            "F-101A",
            "F-102A"
          ],
          "max_prob": 0.8,
          "novelty_features": [
            "afterburner",
            "titanium_structure"
          ],
          "trigger": {
            "base": 0.06,
            "gates": [
              {
                "feature": "has_afterburner",
                "min": 0.5,
                "full": 1.0
              }
            ],
            "ramps": [
              {
                "feature": "ti_deficit",
                "x0": 0.0,
                "x1": 0.12,
                "weight": 0.48
              }
            ],
            "flags": [],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.08,
            "engine_altitude_cell": 0.5,
            "flight:speed_envelope": 0.76,
            "flight:altitude_envelope": 0.65
          },
          "flight_incident": {
            "encounter_weight": 0.22,
            "crash_prob_given_encounter": 0.14
          },
          "truth_effects": {
            "driver_log_deltas": {
              "maint": 0.1
            },
            "metric_multipliers": {}
          },
          "placard": {
            "name": "5-Minute Maximum Continuous Afterburner Time Limit",
            "metric_multipliers": {
              "max_mach_alt": 0.95,
              "combat_radius_m": 0.94
            },
            "residual_hazard_factor": 0.25
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.42,
            "accident_rate_per_1000fh": 0.12,
            "grounding_days": 25,
            "rep_penalty": 5.5
          },
          "fixes": [
            {
              "id": "titanium_aft_heat_shield",
              "name": "Install Titanium Aft Fuselage Shroud & Ram Cooling Ejector",
              "available_year": 1951,
              "required_tech": "struct.material.titanium_available",
              "base_cost_1950_usd": 88000.0,
              "retrofit_kit_1950_usd": 4200.0,
              "fix_days": 30,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "mass": 0.006,
                "cost_unit": 0.018
              },
              "metric_multipliers": {}
            },
            {
              "id": "stainless_steel_blast_blanket",
              "name": "Stainless-Steel Thermal Blanket & Bay Cooling Scoop",
              "available_year": 1945,
              "required_tech": null,
              "base_cost_1950_usd": 55000.0,
              "retrofit_kit_1950_usd": 2400.0,
              "fix_days": 22,
              "residual_factor": 0.16,
              "driver_log_deltas": {
                "mass": 0.015,
                "cd0": 0.006
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "stores_separation_strike",
          "name": "Transonic External Stores Pitch-Up & Tailplane Strike on Jettison",
          "family": "structural_fatigue",
          "category": "aerodynamics",
          "base_severity": 2,
          "known_from_year": 1948,
          "unknown_symptom_label": "Jettisoned drop tanks/bombs tumbling into wing and horizontal tail",
          "historical_examples": [
            "F-84E",
            "F-100C",
            "F-104C"
          ],
          "max_prob": 0.78,
          "novelty_features": [
            "transonic_target",
            "swept_wing"
          ],
          "trigger": {
            "base": 0.04,
            "gates": [
              {
                "feature": "hardpoints",
                "min": 2.0,
                "full": 4.0
              }
            ],
            "ramps": [
              {
                "feature": "max_mach_nom",
                "x0": 0.82,
                "x1": 1.35,
                "weight": 0.35
              },
              {
                "feature": "hardpoints",
                "x0": 2.0,
                "x1": 6.0,
                "weight": 0.25
              }
            ],
            "flags": [],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.06,
            "low_speed_tunnel": 0.35,
            "transonic_slotted": 0.55,
            "flight:weapons_stores": 0.88
          },
          "flight_incident": {
            "encounter_weight": 0.2,
            "crash_prob_given_encounter": 0.1
          },
          "truth_effects": {
            "driver_log_deltas": {
              "cd0": 0.03
            },
            "metric_multipliers": {}
          },
          "placard": {
            "name": "Subsonic Level-Flight Stores Release Limit (300 kt)",
            "metric_multipliers": {
              "combat_radius_m": 0.93
            },
            "residual_hazard_factor": 0.2
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.38,
            "accident_rate_per_1000fh": 0.08,
            "grounding_days": 0,
            "rep_penalty": 3.5
          },
          "fixes": [
            {
              "id": "cartridge_pneumatic_ejector_racks",
              "name": "Install Pyrotechnic Cartridge Forced-Ejection Pylon Racks & Tank Fins",
              "available_year": 1948,
              "required_tech": null,
              "base_cost_1950_usd": 48000.0,
              "retrofit_kit_1950_usd": 1900.0,
              "fix_days": 20,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "mass": 0.005,
                "cd0": 0.004
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "hydraulic_single_point_failure",
          "name": "Irreversible Flight Control Total Hydraulic Loss",
          "family": "systems",
          "category": "systems",
          "base_severity": 4,
          "known_from_year": 1948,
          "unknown_symptom_label": "Complete loss of flight control authority following single hydraulic leak",
          "historical_examples": [
            "F-86E",
            "F-100A",
            "F8U-1"
          ],
          "max_prob": 0.78,
          "novelty_features": [
            "transonic_target",
            "supersonic_level"
          ],
          "trigger": {
            "base": 0.08,
            "gates": [
              {
                "feature": "has_powered_controls",
                "min": 0.5,
                "full": 1.0
              }
            ],
            "ramps": [
              {
                "feature": "max_mach_nom",
                "x0": 0.85,
                "x1": 1.5,
                "weight": 0.42
              }
            ],
            "flags": [],
            "multipliers": [
              {
                "feature": "has_dual_hydraulics",
                "mul": 0.2
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.14,
            "mockup_review": 0.55,
            "flight:maneuver": 0.72,
            "flight:speed_envelope": 0.65
          },
          "flight_incident": {
            "encounter_weight": 0.24,
            "crash_prob_given_encounter": 0.26
          },
          "truth_effects": {
            "driver_log_deltas": {
              "maint": 0.08
            },
            "metric_multipliers": {}
          },
          "placard": {
            "name": "Mandatory Pre-Flight Hydraulic Pressure Check & Chase Escort",
            "metric_multipliers": {
              "maint_mh_per_fh": 1.15
            },
            "residual_hazard_factor": 0.4
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.48,
            "accident_rate_per_1000fh": 0.2,
            "grounding_days": 40,
            "rep_penalty": 8.5
          },
          "fixes": [
            {
              "id": "dual_tandem_hydraulics_rat",
              "name": "Dual Independent Hydraulic Loops & Drop-Out Ram Air Turbine (RAT)",
              "available_year": 1948,
              "required_tech": null,
              "base_cost_1950_usd": 98000.0,
              "retrofit_kit_1950_usd": 4500.0,
              "fix_days": 34,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "mass": 0.012,
                "cost_unit": 0.012
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "fuel_cg_shift_venting",
          "name": "Multi-Tank Fuel Sequencing CG Shift & Negative-G Venting",
          "family": "systems",
          "category": "systems",
          "base_severity": 2,
          "known_from_year": 1947,
          "unknown_symptom_label": "Aft CG migration during fuel burn and overboard fuel siphon in climbs",
          "historical_examples": [
            "F-84E",
            "F-100C",
            "F-101A"
          ],
          "max_prob": 0.75,
          "novelty_features": [
            "swept_wing",
            "thin_wing"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [],
            "ramps": [
              {
                "feature": "fuel_fraction",
                "x0": 0.24,
                "x1": 0.42,
                "weight": 0.42
              },
              {
                "feature": "thin_wing_excess",
                "x0": 0.0,
                "x1": 0.05,
                "weight": 0.22
              }
            ],
            "flags": [],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.1,
            "mockup_review": 0.38,
            "flight:altitude_envelope": 0.68,
            "flight:maneuver": 0.7
          },
          "flight_incident": {
            "encounter_weight": 0.18,
            "crash_prob_given_encounter": 0.06
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "combat_radius_m": 0.91,
              "ferry_range_m": 0.91
            }
          },
          "placard": {
            "name": "Manual Tank Selector Schedule & Unusable Reserve Increase",
            "metric_multipliers": {
              "combat_radius_m": 0.88,
              "ferry_range_m": 0.88
            },
            "residual_hazard_factor": 0.2
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.4,
            "accident_rate_per_1000fh": 0.06,
            "grounding_days": 0,
            "rep_penalty": 3.5
          },
          "fixes": [
            {
              "id": "auto_fuel_cg_proportioner",
              "name": "Automatic Float-Valve CG Fuel Proportioner & Pressurized Vent Traps",
              "available_year": 1947,
              "required_tech": null,
              "base_cost_1950_usd": 52000.0,
              "retrofit_kit_1950_usd": 2100.0,
              "fix_days": 22,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "mass": 0.005,
                "maint": 0.015
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "radar_fcs_immaturity",
          "name": "Vacuum-Tube Radar Fire-Control Microphonics & Lock Failure",
          "family": "systems",
          "category": "systems",
          "base_severity": 3,
          "known_from_year": 1949,
          "unknown_symptom_label": "Chronic radar scope clutter, tube failure, and erratic lead computing",
          "historical_examples": [
            "F-86D (E-4 FCS)",
            "F-89D Scorpion",
            "F-102A (MG-10)"
          ],
          "max_prob": 0.85,
          "novelty_features": [
            "radar_fcs"
          ],
          "trigger": {
            "base": 0.06,
            "gates": [
              {
                "feature": "has_radar",
                "min": 0.5,
                "full": 1.0
              }
            ],
            "ramps": [
              {
                "feature": "avionics_level",
                "x0": 1.5,
                "x1": 4.5,
                "weight": 0.55
              }
            ],
            "flags": [],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.12,
            "mockup_review": 0.3,
            "flight:weapons_stores": 0.84,
            "flight:altitude_envelope": 0.45
          },
          "flight_incident": {
            "encounter_weight": 0.12,
            "crash_prob_given_encounter": 0.01
          },
          "truth_effects": {
            "driver_log_deltas": {
              "maint": 0.24,
              "cost_unit": 0.08
            },
            "metric_multipliers": {}
          },
          "placard": {
            "name": "Optical Backup Sight Mode / Degraded Radar Readiness",
            "metric_multipliers": {
              "maint_mh_per_fh": 1.2
            },
            "residual_hazard_factor": 0.3
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.6,
            "accident_rate_per_1000fh": 0.02,
            "grounding_days": 15,
            "rep_penalty": 6.5
          },
          "fixes": [
            {
              "id": "fcs_environmental_isolation_rack",
              "name": "Vibration-Isolated Pressurized Avionics Bay & Ruggedized Tubes",
              "available_year": 1950,
              "required_tech": null,
              "base_cost_1950_usd": 115000.0,
              "retrofit_kit_1950_usd": 5400.0,
              "fix_days": 38,
              "residual_factor": 0.12,
              "driver_log_deltas": {
                "mass": 0.008,
                "maint": -0.16
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "ejection_envelope_deficiency",
          "name": "High-Speed / Low-Altitude Bailout & Fin-Clearance Hazard",
          "family": "systems",
          "category": "ergonomics",
          "base_severity": 3,
          "known_from_year": 1946,
          "unknown_symptom_label": "Lethal tail-strike or windblast hazard during emergency bailout",
          "historical_examples": [
            "P-80A (no seat)",
            "F-104A (downward C-2 seat)",
            "F7U Cutlass"
          ],
          "max_prob": 0.82,
          "novelty_features": [
            "t_tail",
            "mach2_regime"
          ],
          "trigger": {
            "base": 0.08,
            "gates": [
              {
                "feature": "max_mach_nom",
                "min": 0.75,
                "full": 0.95
              }
            ],
            "ramps": [
              {
                "feature": "max_mach_nom",
                "x0": 0.85,
                "x1": 1.8,
                "weight": 0.38
              }
            ],
            "flags": [
              {
                "feature": "is_t_tail",
                "add": 0.2
              }
            ],
            "multipliers": [
              {
                "feature": "has_ejection_seat",
                "mul": 0.35
              }
            ]
          },
          "detect_prob_by_source": {
            "sim": 0.2,
            "mockup_review": 0.78,
            "flight:low_speed": 0.45
          },
          "flight_incident": {
            "encounter_weight": 0.1,
            "crash_prob_given_encounter": 0.01
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {}
          },
          "placard": {
            "name": "Minimum 1,500 ft AGL Bailout Altitude Advisory",
            "metric_multipliers": {},
            "residual_hazard_factor": 0.45
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.35,
            "accident_rate_per_1000fh": 0.05,
            "grounding_days": 15,
            "rep_penalty": 6.0
          },
          "fixes": [
            {
              "id": "upward_ballistic_rocket_seat",
              "name": "Install Upward High-Impulse Catapult / Rocket Ejection Seat",
              "available_year": 1947,
              "required_tech": "systems.ejection_seat",
              "base_cost_1950_usd": 58000.0,
              "retrofit_kit_1950_usd": 2600.0,
              "fix_days": 24,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "mass": 0.006
              },
              "metric_multipliers": {}
            }
          ]
        },
        {
          "id": "carrier_hook_visibility_deficiency",
          "name": "Over-Nose Approach Blindness & Arrestor Hook Bounce",
          "family": "manufacturing",
          "category": "ergonomics",
          "base_severity": 3,
          "known_from_year": 1946,
          "unknown_symptom_label": "Pilot loses sight of runway/LSO on high-alpha approach; hook skip",
          "historical_examples": [
            "F7U-1 Cutlass",
            "F4D-1 Skyray",
            "FJ-2 Fury"
          ],
          "max_prob": 0.82,
          "novelty_features": [
            "delta_wing",
            "high_sweep"
          ],
          "trigger": {
            "base": 0.05,
            "gates": [],
            "ramps": [
              {
                "feature": "low_ar_excess",
                "x0": 0.0,
                "x1": 1.6,
                "weight": 0.32
              },
              {
                "feature": "fuselage_fineness",
                "x0": 7.5,
                "x1": 11.5,
                "weight": 0.22
              }
            ],
            "flags": [
              {
                "feature": "carrier_capable",
                "add": 0.25
              }
            ],
            "multipliers": []
          },
          "detect_prob_by_source": {
            "sim": 0.14,
            "mockup_review": 0.8,
            "flight:low_speed": 0.88
          },
          "flight_incident": {
            "encounter_weight": 0.24,
            "crash_prob_given_encounter": 0.12
          },
          "truth_effects": {
            "driver_log_deltas": {},
            "metric_multipliers": {
              "landing_distance_m": 1.1
            },
            "carrier_unsuitable_reason": "Excessive over-nose blind angle and arrestor hook skip on deck recovery"
          },
          "placard": {
            "name": "Day-VFR / Shore-Based Field Operation Restriction",
            "metric_multipliers": {
              "landing_distance_m": 1.15
            },
            "residual_hazard_factor": 0.25
          },
          "service_hazard": {
            "manifest_rate_per_1000fh": 0.5,
            "accident_rate_per_1000fh": 0.14,
            "grounding_days": 25,
            "rep_penalty": 7.0
          },
          "fixes": [
            {
              "id": "raised_seat_hook_damper",
              "name": "Raise Cockpit Sill/Canopy Line & Install Long-Stroke Hydraulic Hook Damper",
              "available_year": 1946,
              "required_tech": null,
              "base_cost_1950_usd": 72000.0,
              "retrofit_kit_1950_usd": 3200.0,
              "fix_days": 28,
              "residual_factor": 0.08,
              "driver_log_deltas": {
                "cd0": 0.008,
                "mass": 0.007
              },
              "metric_multipliers": {}
            }
          ]
        }
      ]
    },
    "sources": {
      "providers": {
        "own": {
          "name": "Company-Owned Facility",
          "quality_mult": 1.05,
          "queue_base_days": 0,
          "queue_jitter_days": 0,
          "hours_per_day": 16.0,
          "hourly_cost_1950_usd": {
            "low_speed_tunnel": 350.0,
            "transonic_slotted": 750.0,
            "supersonic_tunnel": 1200.0,
            "spin_tunnel": 250.0,
            "flutter_model": 500.0,
            "engine_altitude_cell": 850.0,
            "mockup_review": 200.0,
            "static_structural": 400.0
          }
        },
        "naca": {
          "name": "NACA National Laboratories (Langley / Ames / Lewis / Wallops)",
          "quality_mult": 1.0,
          "queue_base_days": 75,
          "queue_jitter_days": 30,
          "military_priority_queue_mult": 0.5,
          "hours_per_day": 8.0,
          "hourly_cost_1950_usd": {
            "low_speed_tunnel": 150.0,
            "transonic_bump": 220.0,
            "rocket_model": 450.0,
            "transonic_slotted": 250.0,
            "supersonic_tunnel": 320.0,
            "spin_tunnel": 140.0,
            "flutter_model": 240.0,
            "engine_altitude_cell": 280.0
          }
        },
        "aedc": {
          "name": "USAF Arnold Engineering Development Center (Tullahoma)",
          "available_from_date": "1956-01-01",
          "quality_mult": 0.88,
          "queue_base_days": 30,
          "queue_jitter_days": 15,
          "military_priority_queue_mult": 0.5,
          "hours_per_day": 12.0,
          "hourly_cost_1950_usd": {
            "transonic_slotted": 1350.0,
            "supersonic_tunnel": 1650.0,
            "flutter_model": 1200.0,
            "engine_altitude_cell": 1450.0
          }
        }
      },
      "depth_presets": {
        "brief": {
          "hours_mult": 0.5,
          "label": "Brief Survey (0.5x hours)"
        },
        "standard": {
          "hours_mult": 1.0,
          "label": "Standard Campaign (1.0x hours)"
        },
        "comprehensive": {
          "hours_mult": 2.0,
          "label": "Comprehensive Campaign (2.0x hours)"
        }
      },
      "campaigns": {
        "low_speed_tunnel": {
          "id": "low_speed_tunnel",
          "name": "Low-Speed Subsonic Wind Tunnel (M ≤ 0.4)",
          "available_year": 1945,
          "required_tech": null,
          "min_own_tunnel_level": 1,
          "allowed_providers": [
            "own",
            "naca"
          ],
          "model_cost_1950_usd": 35000.0,
          "model_fab_days": 30,
          "ref_hours": 80.0,
          "mach_max_covered": 0.45,
          "chokes_in_transonic": true,
          "driver_precision": {
            "clmax": {
              "sigma_ref": 0.024,
              "sigma_floor": 0.014
            },
            "kind": {
              "sigma_ref": 0.026,
              "sigma_floor": 0.015
            },
            "cd0": {
              "sigma_ref": 0.032,
              "sigma_floor": 0.018
            }
          }
        },
        "transonic_bump": {
          "id": "transonic_bump",
          "name": "NACA Wing-Flow / Transonic Bump Technique",
          "available_year": 1946,
          "required_tech": null,
          "min_own_tunnel_level": 99,
          "allowed_providers": [
            "naca"
          ],
          "model_cost_1950_usd": 45000.0,
          "model_fab_days": 35,
          "ref_hours": 60.0,
          "mach_max_covered": 1.12,
          "chokes_in_transonic": false,
          "driver_precision": {
            "cdw": {
              "sigma_ref": 0.065,
              "sigma_floor": 0.042
            },
            "cd0": {
              "sigma_ref": 0.045,
              "sigma_floor": 0.028
            }
          }
        },
        "rocket_model": {
          "id": "rocket_model",
          "name": "Rocket-Boosted Free-Flight Drop Models (NACA Wallops)",
          "available_year": 1945,
          "required_tech": "testing.rocket_model_testing",
          "min_own_tunnel_level": 99,
          "allowed_providers": [
            "naca"
          ],
          "model_cost_1950_usd": 75000.0,
          "model_fab_days": 45,
          "ref_hours": 40.0,
          "mach_max_covered": 1.6,
          "chokes_in_transonic": false,
          "driver_precision": {
            "cdw": {
              "sigma_ref": 0.038,
              "sigma_floor": 0.022
            },
            "cd0": {
              "sigma_ref": 0.035,
              "sigma_floor": 0.02
            }
          }
        },
        "transonic_slotted": {
          "id": "transonic_slotted",
          "name": "Slotted-Throat Transonic Wind Tunnel (M 0.7–1.3)",
          "available_year": 1950,
          "required_tech": "testing.transonic_tunnel",
          "min_own_tunnel_level": 2,
          "allowed_providers": [
            "own",
            "naca",
            "aedc"
          ],
          "model_cost_1950_usd": 65000.0,
          "model_fab_days": 45,
          "ref_hours": 100.0,
          "mach_max_covered": 1.3,
          "chokes_in_transonic": false,
          "driver_precision": {
            "cdw": {
              "sigma_ref": 0.025,
              "sigma_floor": 0.012
            },
            "cd0": {
              "sigma_ref": 0.024,
              "sigma_floor": 0.012
            },
            "kind": {
              "sigma_ref": 0.024,
              "sigma_floor": 0.013
            },
            "clmax": {
              "sigma_ref": 0.028,
              "sigma_floor": 0.015
            }
          }
        },
        "supersonic_tunnel": {
          "id": "supersonic_tunnel",
          "name": "Continuous Supersonic Wind Tunnel (M 1.2–2.5)",
          "available_year": 1945,
          "required_tech": "testing.supersonic_tunnel",
          "min_own_tunnel_level": 3,
          "allowed_providers": [
            "own",
            "naca",
            "aedc"
          ],
          "model_cost_1950_usd": 80000.0,
          "model_fab_days": 50,
          "ref_hours": 100.0,
          "mach_max_covered": 2.5,
          "chokes_in_transonic": true,
          "driver_precision": {
            "cdw": {
              "sigma_ref": 0.028,
              "sigma_floor": 0.014
            },
            "cd0": {
              "sigma_ref": 0.028,
              "sigma_floor": 0.015
            },
            "thrust": {
              "sigma_ref": 0.032,
              "sigma_floor": 0.018
            }
          }
        },
        "spin_tunnel": {
          "id": "spin_tunnel",
          "name": "20-ft Vertical Free-Spin Wind Tunnel",
          "available_year": 1945,
          "required_tech": null,
          "min_own_tunnel_level": 2,
          "allowed_providers": [
            "own",
            "naca"
          ],
          "model_cost_1950_usd": 20000.0,
          "model_fab_days": 25,
          "ref_hours": 40.0,
          "mach_max_covered": 0.3,
          "chokes_in_transonic": false,
          "driver_precision": {
            "clmax": {
              "sigma_ref": 0.04,
              "sigma_floor": 0.025
            }
          }
        },
        "flutter_model": {
          "id": "flutter_model",
          "name": "Dynamic Aeroelastic Flutter Scale Model",
          "available_year": 1947,
          "required_tech": null,
          "min_own_tunnel_level": 2,
          "allowed_providers": [
            "own",
            "naca",
            "aedc"
          ],
          "model_cost_1950_usd": 55000.0,
          "model_fab_days": 40,
          "ref_hours": 60.0,
          "mach_max_covered": 1.25,
          "chokes_in_transonic": false,
          "driver_precision": {
            "mass": {
              "sigma_ref": 0.035,
              "sigma_floor": 0.02
            }
          }
        },
        "engine_altitude_cell": {
          "id": "engine_altitude_cell",
          "name": "Propulsion Altitude & Inlet Test Cell",
          "available_year": 1945,
          "required_tech": null,
          "min_own_tunnel_level": 2,
          "allowed_providers": [
            "own",
            "naca",
            "aedc"
          ],
          "model_cost_1950_usd": 30000.0,
          "model_fab_days": 20,
          "ref_hours": 80.0,
          "mach_max_covered": 2.2,
          "chokes_in_transonic": false,
          "driver_precision": {
            "thrust": {
              "sigma_ref": 0.018,
              "sigma_floor": 0.009
            },
            "tsfc": {
              "sigma_ref": 0.016,
              "sigma_floor": 0.008
            },
            "maint": {
              "sigma_ref": 0.055,
              "sigma_floor": 0.03
            }
          }
        },
        "mockup_review": {
          "id": "mockup_review",
          "name": "Full-Scale Wood & Metal Engineering Mock-up Board",
          "available_year": 1945,
          "required_tech": null,
          "min_own_tunnel_level": 0,
          "allowed_providers": [
            "own"
          ],
          "model_cost_1950_usd": 40000.0,
          "model_fab_days": 30,
          "ref_hours": 24.0,
          "mach_max_covered": 0.0,
          "chokes_in_transonic": false,
          "driver_precision": {
            "mass": {
              "sigma_ref": 0.028,
              "sigma_floor": 0.016
            },
            "maint": {
              "sigma_ref": 0.05,
              "sigma_floor": 0.028
            },
            "cost_unit": {
              "sigma_ref": 0.055,
              "sigma_floor": 0.03
            }
          }
        },
        "static_structural": {
          "id": "static_structural",
          "name": "Static Ultimate-Load Structural Torture Rig",
          "available_year": 1945,
          "required_tech": null,
          "min_own_tunnel_level": 0,
          "allowed_providers": [
            "own"
          ],
          "model_cost_1950_usd": 110000.0,
          "model_fab_days": 60,
          "ref_hours": 40.0,
          "mach_max_covered": 0.0,
          "chokes_in_transonic": false,
          "driver_precision": {
            "mass": {
              "sigma_ref": 0.015,
              "sigma_floor": 0.008
            },
            "cost_unit": {
              "sigma_ref": 0.045,
              "sigma_floor": 0.025
            }
          }
        }
      },
      "prototype_rollout_precision": {
        "mass": 0.005,
        "cost_dev": 0.015,
        "cost_unit": 0.03
      }
    },
    "flight_items": {
      "depth_presets": {
        "light": {
          "sortie_mult": 0.5,
          "label": "Light / Cursory (0.5x sorties)"
        },
        "standard": {
          "sortie_mult": 1.0,
          "label": "Standard Syllabus (1.0x sorties)"
        },
        "thorough": {
          "sortie_mult": 1.6,
          "label": "Exhaustive Envelope Expansion (1.6x sorties)"
        }
      },
      "syllabus_items": [
        {
          "id": "low_speed",
          "name": "Low-Speed, Stall, Take-off & Landing (incl. Carrier Suitability)",
          "order": 1,
          "standard_sorties": 22,
          "days_per_sortie": 2.2,
          "cost_per_sortie_1950_usd": 8500.0,
          "base_crash_prob_per_sortie": 0.0008,
          "bailout_survival_mult": 1.0,
          "driver_precision": {
            "clmax": 0.01,
            "kind": 0.014,
            "cd0": 0.018
          }
        },
        {
          "id": "speed_envelope",
          "name": "High-Speed & Mach Dive Envelope Expansion",
          "order": 2,
          "standard_sorties": 30,
          "days_per_sortie": 2.8,
          "cost_per_sortie_1950_usd": 12000.0,
          "base_crash_prob_per_sortie": 0.0022,
          "bailout_survival_mult": 0.82,
          "driver_precision": {
            "cdw": 0.008,
            "cd0": 0.009,
            "thrust": 0.014
          }
        },
        {
          "id": "altitude_envelope",
          "name": "High-Altitude Climb, Relight & Service Ceiling",
          "order": 3,
          "standard_sorties": 20,
          "days_per_sortie": 2.5,
          "cost_per_sortie_1950_usd": 10000.0,
          "base_crash_prob_per_sortie": 0.0012,
          "bailout_survival_mult": 0.95,
          "driver_precision": {
            "thrust": 0.009,
            "tsfc": 0.009,
            "cd0": 0.016
          }
        },
        {
          "id": "maneuver",
          "name": "High-G Turn, Structural Load Factor & Energy Agility",
          "order": 4,
          "standard_sorties": 26,
          "days_per_sortie": 2.6,
          "cost_per_sortie_1950_usd": 11000.0,
          "base_crash_prob_per_sortie": 0.0018,
          "bailout_survival_mult": 0.88,
          "driver_precision": {
            "kind": 0.009,
            "clmax": 0.011,
            "mass": 0.008
          }
        },
        {
          "id": "high_aoa_spin",
          "name": "High-Alpha Stall Departure & Intentional Spin Recovery",
          "order": 5,
          "standard_sorties": 18,
          "days_per_sortie": 3.0,
          "cost_per_sortie_1950_usd": 11500.0,
          "base_crash_prob_per_sortie": 0.0032,
          "bailout_survival_mult": 0.72,
          "driver_precision": {
            "clmax": 0.008,
            "kind": 0.015
          }
        },
        {
          "id": "weapons_stores",
          "name": "Armament Firing, Stores Jettison & Avionics/FCS Shakedown",
          "order": 6,
          "standard_sorties": 24,
          "days_per_sortie": 2.5,
          "cost_per_sortie_1950_usd": 13000.0,
          "base_crash_prob_per_sortie": 0.001,
          "bailout_survival_mult": 0.96,
          "driver_precision": {
            "maint": 0.022,
            "cost_unit": 0.02,
            "cd0": 0.016,
            "tsfc": 0.014
          }
        }
      ]
    },
    "pilot_names": {
      "ranks": [
        "Capt.",
        "Maj.",
        "Lt. Col.",
        "Lt. Cmdr.",
        "Cmdr.",
        "Mr."
      ],
      "first_names": [
        "Richard 'Dick'",
        "Robert 'Bob'",
        "William 'Bill'",
        "Charles 'Chuck'",
        "George 'Wheaties'",
        "Frank 'Pete'",
        "Howard 'Tick'",
        "almers 'Slick'",
        "Joseph 'Joe'",
        "Albert 'Al'",
        "Marion 'Carl'",
        "Russell 'Russ'",
        "Teston 'Tex'",
        "Donald 'Don'",
        "Jack",
        "Glenn"
      ],
      "last_names": [
        "Thorne",
        "Caldwell",
        "Vance",
        "Mercer",
        "Halloway",
        "Bridger",
        "Keller",
        "Rawlings",
        "Stoddard",
        "armstrong",
        "Halvorsen",
        "McAllister",
        "Lindstrom",
        "Gallagher",
        "carver",
        "Bannister"
      ],
      "traits": {
        "engineer_pilot": {
          "name": "Aeronautical Engineer-Pilot",
          "description": "Holds an aeronautical engineering degree; +22% flaw detection, 15% tighter telemetry scatter.",
          "crash_mult": 1.0,
          "detect_mult": 1.22,
          "data_sigma_mult": 0.85,
          "salary_mult": 1.2
        },
        "cautious": {
          "name": "Methodical & Cautious",
          "description": "Approaches envelope boundaries incrementally; -20% crash hazard.",
          "crash_mult": 0.8,
          "detect_mult": 0.96,
          "data_sigma_mult": 1.0,
          "salary_mult": 1.0
        },
        "daring": {
          "name": "Envelope Pusher",
          "description": "Pushes deep into buffet and dive limits; +10% flaw detection, +20% crash risk.",
          "crash_mult": 1.2,
          "detect_mult": 1.1,
          "data_sigma_mult": 1.02,
          "salary_mult": 1.05
        },
        "carrier_qualified": {
          "name": "Naval Carrier Test Pilot",
          "description": "Patuxent River carrier suitability specialist; +25% detection on low-speed/carrier flaws.",
          "crash_mult": 0.92,
          "detect_mult": 1.08,
          "data_sigma_mult": 0.95,
          "salary_mult": 1.1
        }
      },
      "starter_roster_1945": [
        {
          "id": "pilot_starter_1",
          "name": "Maj. Richard 'Dick' Thorne",
          "age": 30,
          "hired_year": 1945,
          "skill": 80.0,
          "experience": 65.0,
          "traits": [
            "engineer_pilot",
            "cautious"
          ],
          "salary_annual_usd": 14500.0,
          "status": "active",
          "injured_until_day": 0,
          "assigned_prototype_idx": 0,
          "flights_flown": 0
        },
        {
          "id": "pilot_starter_2",
          "name": "Capt. Robert 'Bob' Vance",
          "age": 27,
          "hired_year": 1945,
          "skill": 72.0,
          "experience": 50.0,
          "traits": [
            "daring"
          ],
          "salary_annual_usd": 11500.0,
          "status": "active",
          "injured_until_day": 0,
          "assigned_prototype_idx": 1,
          "flights_flown": 0
        }
      ]
    }
  },
  "names": {
    "companies_and_people": {
      "schema_version": "1.0",
      "locale": "en-US",
      "description": "Display strings for all historical US airframers, engine makers, custom startup presets, and chief designers (1945-1960). Also includes optional fictionalized legal-safe fallback names per 00_conventions D4.",
      "strings": {
        "company.north_american.name": "North American Aviation",
        "company.north_american.short": "North American",
        "company.lockheed.name": "Lockheed Aircraft Corporation",
        "company.lockheed.short": "Lockheed",
        "company.republic.name": "Republic Aviation Corporation",
        "company.republic.short": "Republic",
        "company.convair.name": "Consolidated Vultee Aircraft (Convair)",
        "company.convair.short": "Convair",
        "company.mcdonnell.name": "McDonnell Aircraft Corporation",
        "company.mcdonnell.short": "McDonnell",
        "company.grumman.name": "Grumman Aircraft Engineering Corporation",
        "company.grumman.short": "Grumman",
        "company.douglas.name": "Douglas Aircraft Company",
        "company.douglas.short": "Douglas",
        "company.vought.name": "Chance Vought Aircraft",
        "company.vought.short": "Vought",
        "company.northrop.name": "Northrop Aircraft, Inc.",
        "company.northrop.short": "Northrop",
        "company.bell.name": "Bell Aircraft Corporation",
        "company.bell.short": "Bell",
        "company.curtiss_wright.name": "Curtiss-Wright Corporation (Airplane Div.)",
        "company.curtiss_wright.short": "Curtiss-Wright",
        "company.martin.name": "Glenn L. Martin Company",
        "company.martin.short": "Martin",
        "company.boeing.name": "Boeing Airplane Company",
        "company.boeing.short": "Boeing",
        "company.general_electric.name": "General Electric Aircraft Gas Turbine Division",
        "company.general_electric.short": "General Electric",
        "company.pratt_whitney.name": "Pratt & Whitney Aircraft",
        "company.pratt_whitney.short": "Pratt & Whitney",
        "company.allison.name": "Allison Division, General Motors",
        "company.allison.short": "Allison",
        "company.westinghouse.name": "Westinghouse Aviation Gas Turbine Division",
        "company.westinghouse.short": "Westinghouse",
        "company.wright.name": "Wright Aeronautical Corporation",
        "company.wright.short": "Wright",
        "preset.skunk_works_spinoff.name": "Experimental Skunk-Team Spinoff",
        "preset.skunk_works_spinoff.desc": "A lean California rapid-prototyping syndicate led by veteran high-speed aerodynamicists with private desert flight-test access.",
        "preset.wartime_subcontractor.name": "Midwest Wartime Subcontractor",
        "preset.wartime_subcontractor.desc": "A massive Wichita/Midwest B-29 assembly contractor with huge factory floor space and cash reserves, pivoting to original jet fighter design.",
        "preset.naca_alumni_syndicate.name": "Langley Aerodynamics Syndicate",
        "preset.naca_alumni_syndicate.desc": "Founded by former NACA compressible-flow researchers with an advanced wind tunnel, elite aerodynamicists, and tight capital.",
        "preset.industrialist_venture.name": "Pacific Industrialist Aviation Venture",
        "preset.industrialist_venture.desc": "Backed by a wealthy Hollywood/defense industrialist with strong avionics/electronics labs and political connections.",
        "designer.edgar_schmued.name": "Edgar Schmued",
        "designer.edgar_schmued.title": "Chief Designer (NAA)",
        "designer.harrison_storms.name": "Harrison \"Stormy\" Storms",
        "designer.harrison_storms.title": "Chief Engineer (NAA)",
        "designer.kelly_johnson.name": "Clarence \"Kelly\" Johnson",
        "designer.kelly_johnson.title": "Chief Research Engineer (ADP)",
        "designer.willis_hawkins.name": "Willis M. Hawkins",
        "designer.willis_hawkins.title": "Chief Preliminary Design Engineer",
        "designer.alexander_kartveli.name": "Alexander Kartveli",
        "designer.alexander_kartveli.title": "VP & Chief Engineer",
        "designer.frank_davis.name": "Frank W. Davis",
        "designer.frank_davis.title": "Chief Engineer (Convair San Diego)",
        "designer.ralph_shick.name": "Ralph H. Shick",
        "designer.ralph_shick.title": "Chief Aerodynamicist",
        "designer.kendall_perkins.name": "Kendall Perkins",
        "designer.kendall_perkins.title": "VP of Engineering",
        "designer.herman_barkey.name": "Herman D. Barkey",
        "designer.herman_barkey.title": "Chief Project Engineer",
        "designer.william_schwendler.name": "William T. \"Bill\" Schwendler",
        "designer.william_schwendler.title": "VP & Chief Engineer",
        "designer.richard_hutton.name": "Richard Hutton",
        "designer.richard_hutton.title": "Chief Development Engineer",
        "designer.ed_heinemann.name": "Edward H. \"Ed\" Heinemann",
        "designer.ed_heinemann.title": "Chief Engineer (El Segundo)",
        "designer.john_russell_clark.name": "John Russell \"Russ\" Clark",
        "designer.john_russell_clark.title": "Chief Project Engineer",
        "designer.rex_beisel.name": "Rex B. Beisel",
        "designer.rex_beisel.title": "General Manager & Chief Designer",
        "designer.jack_northrop.name": "John K. \"Jack\" Northrop",
        "designer.jack_northrop.title": "President & Chief Designer",
        "designer.welko_gasich.name": "Welko E. Gasich",
        "designer.welko_gasich.title": "Chief of Preliminary Design",
        "designer.robert_woods.name": "Robert J. Woods",
        "designer.robert_woods.title": "Chief Design Engineer",
        "designer.donovan_berlin.name": "Donovan R. Berlin",
        "designer.donovan_berlin.title": "VP of Engineering",
        "designer.george_trimble.name": "George S. Trimble Jr.",
        "designer.george_trimble.title": "Chief Aerodynamicist & VP Advanced Design",
        "designer.george_schairer.name": "George S. Schairer",
        "designer.george_schairer.title": "Chief Aerodynamicist",
        "designer.gerhard_neumann.name": "Gerhard Neumann",
        "designer.gerhard_neumann.title": "Jet Engine Department Manager",
        "designer.luke_hobbs.name": "Leonard S. \"Luke\" Hobbs",
        "designer.luke_hobbs.title": "VP of Engineering",
        "designer.ronald_hazen.name": "Ronald M. Hazen",
        "designer.ronald_hazen.title": "Director of Engineering",
        "designer.reinout_kroon.name": "Reinout P. Kroon",
        "designer.reinout_kroon.title": "Manager of Engineering (AGTD)",
        "designer.william_lundquist.name": "William G. Lundquist",
        "designer.william_lundquist.title": "VP of Engineering",
        "designer.custom_aero_visionary.name": "Dr. Vance Sterling",
        "designer.custom_aero_visionary.title": "Chief Aerodynamicist",
        "designer.custom_production_master.name": "Arthur K. Vance",
        "designer.custom_production_master.title": "VP of Manufacturing & Structures",
        "designer.custom_transonic_theorist.name": "Dr. Eleanor Whitmore",
        "designer.custom_transonic_theorist.title": "Director of Compressible Flow Research",
        "designer.custom_systems_integrator.name": "Howard J. Mercer",
        "designer.custom_systems_integrator.title": "Chief Weapon Systems Engineer"
      },
      "fictional_fallback_overrides": {
        "company.north_american.name": "Pacific American Aviation",
        "company.north_american.short": "Pacific American",
        "company.lockheed.name": "Burbank Aero Corporation",
        "company.lockheed.short": "Burbank Aero",
        "company.republic.name": "Farmingdale Republic Aviation",
        "company.republic.short": "Farmingdale",
        "company.convair.name": "San Diego Consolidated Aircraft",
        "company.convair.short": "San Diego Consolidated",
        "company.mcdonnell.name": "St. Louis Aerospace Corporation",
        "company.mcdonnell.short": "St. Louis Aero",
        "company.grumman.name": "Bethpage Iron Works Aviation",
        "company.grumman.short": "Bethpage",
        "company.douglas.name": "El Segundo Aircraft Company",
        "company.douglas.short": "El Segundo",
        "company.vought.name": "Corsair Naval Aircraft",
        "company.vought.short": "Corsair Naval",
        "company.northrop.name": "Hawthorne All-Wing Aircraft",
        "company.northrop.short": "Hawthorne",
        "company.bell.name": "Niagara Frontier Aircraft",
        "company.bell.short": "Niagara",
        "company.curtiss_wright.name": "Keystone-Wright Corporation",
        "company.curtiss_wright.short": "Keystone-Wright",
        "company.martin.name": "Chesapeake Aviation Company",
        "company.martin.short": "Chesapeake",
        "company.boeing.name": "Puget Sound Airplane Company",
        "company.boeing.short": "Puget Sound"
      }
    },
    "tech_and_components": {
      "schema_version": "1.0",
      "locale": "en-US",
      "description": "Display names for all 82 tech tree nodes and 28 ordnance/avionics components (1945-1960).",
      "strings": {
        "tech.aero_1945_compressible_subsonic.name": "Compressible Subsonic Aerodynamics & Laminar Airfoils",
        "tech.aero_1945_swept_wing_theory.name": "35° Swept-Wing Theory (Busemann / R.T. Jones)",
        "tech.aero_1946_auto_le_slats.name": "Automatic Leading-Edge Slats",
        "tech.aero_1947_thin_airfoils_10pct.name": "9–10% Transonic Airfoil Sections (NACA 64A/65A)",
        "tech.aero_1948_all_moving_tail.name": "All-Moving Horizontal Stabilizer (\"Flying Tail\")",
        "tech.aero_1948_tailless_delta_basics.name": "60° Tailless Delta Planform Aerodynamics",
        "tech.aero_1949_subsonic_duct_splitters.name": "Boundary-Layer Diverters & Duct Splitter Plates",
        "tech.aero_1950_high_sweep_45deg.name": "45° High-Sweep Thin Supersonic Wings (6% t/c)",
        "tech.aero_1951_le_droop_krueger_flaps.name": "Cambered Leading-Edge Droop & Krueger Flaps",
        "tech.aero_1951_variable_sweep_exp.name": "Experimental Variable-Sweep Wing Mechanisms (X-5 / XF10F)",
        "tech.aero_1952_whitcomb_area_rule.name": "Whitcomb Transonic Area Rule (\"Wasp Waist\")",
        "tech.aero_1953_supersonic_spike_inlet.name": "Fixed Oblique-Shock Cone & Half-Cone Inlets",
        "tech.aero_1953_razor_thin_wing_3pct.name": "Razor-Thin Biconvex Supersonic Wings (3.4% t/c)",
        "tech.aero_1954_vortex_generators_excrescence.name": "Vortex Generators, Wing Fences & Excrescence Cleanup",
        "tech.aero_1955_conical_camber.name": "Conical-Camber Delta Leading Edges",
        "tech.aero_1955_blc_blown_flaps.name": "Boundary-Layer Control (BLC) Blown Flaps",
        "tech.aero_1955_variable_geometry_inlet.name": "Variable-Geometry Multi-Shock Ramps & Translating Cones",
        "tech.aero_1956_supersonic_area_rule.name": "Supersonic Mach-Cone Area Rule",
        "tech.struct_1945_stressed_skin_7075.name": "7075-T6 Aluminum Stressed-Skin Construction",
        "tech.struct_1946_thick_skin_box_spar.name": "Thick-Plate Multi-Spar Torsion-Box Wings",
        "tech.struct_1948_jet_carrier_suitability.name": "Jet Carrier Suitability & High-Sink-Rate Structure",
        "tech.struct_1951_titanium_metallurgy_1.name": "Early Titanium Hot-Section Metallurgy (Kroll Process)",
        "tech.struct_1952_integrally_stiffened_skins.name": "Machined Integrally Stiffened Wing Skins",
        "tech.struct_1954_bonded_honeycomb.name": "Adhesive-Bonded Honeycomb Sandwich Panels",
        "tech.struct_1955_fatigue_failsafe_design.name": "Fail-Safe Redundant Structure & Fatigue Spectrum Design",
        "tech.struct_1956_ti_6al_4v_structural.name": "Ti-6Al-4V Structural Airframe Forgings & Skins",
        "tech.struct_1958_ph_stainless_brazed_thermal.name": "Brazed PH Stainless Steel & High-Titanium Thermal Structure",
        "tech.prop_1945_centrifugal_turbojet.name": "Centrifugal-Flow Turbojet (Whittle / I-40 Class)",
        "tech.prop_1945_early_axial_compressor.name": "Early Single-Spool Axial-Flow Turbojet (TG-180 / 19XB)",
        "tech.prop_1947_nimonic_superalloys_1.name": "Wrought Nickel-Cobalt Hot-Section Superalloys (Inconel X / S-816)",
        "tech.prop_1948_afterburner_1.name": "Early Tailpipe Afterburner & Eyelid Nozzle",
        "tech.prop_1949_multi_stage_axial_refinement.name": "12-Stage Axial Compressors with Interstage Bleed (OPR 7)",
        "tech.prop_1950_component_altitude_test_cells.name": "Refrigerated High-Altitude Engine Test Cells",
        "tech.prop_1952_twin_spool_compressor.name": "Two-Spool Split-Compressor Architecture (J57 Class)",
        "tech.prop_1953_modulated_afterburner.name": "Modulated Afterburner & Variable Iris Nozzle",
        "tech.prop_1954_waspaloy_vacuum_superalloys.name": "Vacuum-Melted Waspaloy Blades & Titanium Rotors",
        "tech.prop_1954_variable_stator_compressor.name": "Variable-Stator High-OPR Single-Spool Compressor (J79 Class)",
        "tech.prop_1956_high_massflow_cores.name": "Transonic Rotor Blading & High-Airflow Cores (J75 Class)",
        "tech.prop_1958_cooled_turbine_blades.name": "Air-Cooled High-Pressure Turbine Vanes & Blades",
        "tech.prop_1959_low_bypass_turbofan.name": "Low-Bypass Turbofan Architecture (TF33 / TF30 Class)",
        "tech.av_1945_vhf_gyro_sight_scr720.name": "VHF Radio, Lead-Computing Gyro Sight & WWII AI Radar",
        "tech.sys_1946_hydraulic_boost_controls.name": "3,000-psi Irreversible Hydraulic Flight Controls",
        "tech.sys_1946_ejection_seat.name": "Ballistic Pilot Ejection Seat",
        "tech.av_1946_xband_navy_ai_radar.name": "Compact X-Band Single-Seat Night-Fighter Radar (AN/APS-19)",
        "tech.av_1948_radar_ranging_gunsight.name": "Automatic Radar-Ranging Computing Gunsight (A-1CM / APG-30)",
        "tech.sys_1949_stability_augmentation_sas.name": "Rate-Gyro Stability Augmentation System (Yaw/Pitch Dampers)",
        "tech.av_1949_all_weather_fcs_e1.name": "All-Weather Search & Lock-On Fire Control (E-1 / APG-33 / APS-21)",
        "tech.sys_1950_inflight_refueling.name": "In-Flight Refueling Probe & Boom Receptacle",
        "tech.av_1951_lead_collision_fcs_e4.name": "Lead-Collision Automatic Rocket Fire Control (E-4 / E-9 / APG-37)",
        "tech.av_1954_subminiature_tubes_pcb.name": "Subminiature Tubes & Etched Printed-Circuit Modules",
        "tech.av_1955_awcs_mg10_apq50.name": "Missile-Capable Automatic Weapon Control (MG-10 / APQ-50)",
        "tech.av_1956_sage_gci_datalink.name": "SAGE Ground-Controlled Intercept Time-Division Datalink",
        "tech.av_1957_solid_state_transistor_avionics.name": "Solid-State Silicon Transistor & Magnetic-Core Avionics",
        "tech.av_1958_irst_sensor.name": "Passive Infrared Search and Track (IRST) Sensor",
        "tech.av_1958_integrated_digital_awcs_ma1_apq72.name": "Integrated Airborne Digital Fire Control & CW Radar (MA-1 / APQ-72)",
        "tech.arm_1945_ww2_guns_and_hvar.name": "WWII Standard .50-Cal / 20mm Guns & 5-Inch HVAR Rockets",
        "tech.arm_1947_m3_high_rof_50cal.name": "High-Speed Boosted .50-Cal Machine Gun (Browning AN/M3)",
        "tech.arm_1949_ffar_m24_interceptor_ordnance.name": "2.75-Inch Mighty Mouse FFAR & Electric 20mm Interceptor Cannon",
        "tech.arm_1952_revolver_and_navy_20mm_cannons.name": "High-Velocity 20mm Revolver & Naval Cannons (M39 / Mk 12)",
        "tech.arm_1952_labs_tactical_nuclear_delivery.name": "LABS Toss-Bombing Computer & Tactical Nuclear Store Delivery",
        "tech.arm_1953_internal_weapons_bay.name": "Supersonic Internal Missile & Rocket Trapeze Bay",
        "tech.arm_1954_beam_riding_sparrow1.name": "Radar Beam-Riding Air-to-Air Missile (AIM-7A Sparrow I)",
        "tech.arm_1955_sarh_homing_gen1_falcon.name": "Gen-1 Semi-Active Radar Homing Missile (GAR-1 / AIM-4A Falcon)",
        "tech.arm_1955_ir_homing_gen1.name": "Gen-1 Infrared Homing Missiles (AIM-9B Sidewinder / AIM-4C)",
        "tech.arm_1956_m61_vulcan_rotary_cannon.name": "20mm 6-Barrel Rotary Gatling Cannon (M61 Vulcan)",
        "tech.arm_1957_nuclear_air_to_air_rockets.name": "Unguided Nuclear Air-to-Air Rocket (MB-1 / AIR-2A Genie)",
        "tech.arm_1958_sarh_gen2_sparrow3_nuclear_falcon.name": "Gen-2 All-Weather CW SARH & Nuclear Falcon Missiles (AIM-7C / AIM-26A)",
        "tech.mfg_1945_ww2_mass_production_line.name": "Wartime Moving Assembly Line & Master Lofting (80% Curve)",
        "tech.mfg_1947_flush_riveting_aerodynamic_smoothing.name": "Coin-Dimpled Flush Riveting & Aerodynamic Skin Smoothing",
        "tech.mfg_1949_optical_tooling_jigs.name": "Optical Alignment Tooling & Precision Swept-Wing Jigs",
        "tech.mfg_1950_heavy_forging_presses.name": "35,000/50,000-Ton Closed-Die Heavy Forging Presses",
        "tech.mfg_1953_statistical_quality_control.name": "Ultrasonic/X-Ray NDI & Statistical Quality Control (MIL-Q-5923)",
        "tech.mfg_1954_titanium_forming_chem_mill.name": "Chemical Milling (\"Chem-Mill\") & Inert-Gas Titanium Forming",
        "tech.mfg_1956_nc_machining.name": "Punched-Tape Numerically Controlled (NC) 3-Axis Skin Milling",
        "tech.test_1945_sub_and_supersonic_blowdown_tunnels.name": "Subsonic Wind Tunnels & Small Supersonic Blowdown Nozzles",
        "tech.test_1946_wallops_rocket_models.name": "Rocket-Boosted Free-Flight Transonic Models (Wallops PARD)",
        "tech.test_1948_fm_telemetry_oscillographs.name": "Multi-Channel Strain Oscillographs & FM/FM Flight Telemetry",
        "tech.test_1950_slotted_transonic_tunnel.name": "Slotted-Throat Transonic Wind Tunnel (NACA Langley)",
        "tech.test_1952_flutter_aeroelastic_analog.name": "Dynamic Aeroelastic Models & Analog Flutter Computers",
        "tech.test_1953_ibm_701_digital_computing.name": "High-Speed Digital Scientific Computing (IBM 701 / 704)",
        "tech.test_1955_inertia_coupling_6dof_sim.name": "5-DOF / 6-DOF Roll-Inertia Coupling Flight Simulators",
        "tech.test_1957_high_speed_flight_station_datcom.name": "USAF/NACA DATCOM Compendium & Propulsion Wind Tunnels",
        "comp.gun.an_m2_50": "12.7mm (.50 cal) Browning AN/M2 Machine Gun",
        "comp.gun.m3_50": "12.7mm (.50 cal) Browning AN/M3 High-ROF Machine Gun",
        "comp.gun.an_m3_20mm": "20mm Hispano-Suiza AN/M3 Cannon",
        "comp.gun.m24_20mm": "20mm M24A1 Electric-Primed Cannon",
        "comp.gun.m39_20mm": "20mm Pontiac M39 Revolver Cannon",
        "comp.gun.mk12_20mm": "20mm Colt Mk 12 Naval Cannon",
        "comp.gun.m61_20mm": "20mm GE M61A1 Vulcan 6-Barrel Rotary Cannon",
        "comp.rocket.hvar_5in": "5-inch HVAR \"Holy Moses\" Rocket Pack",
        "comp.rocket.ffar_2_75in": "2.75-inch Mk 4 \"Mighty Mouse\" FFAR Rocket Pack",
        "comp.missile.aim7a_sparrow1": "AAM-N-2 (AIM-7A) Sparrow I Beam-Riding Missile",
        "comp.missile.aim4a_falcon": "GAR-1 (AIM-4A) Falcon SARH Missile",
        "comp.missile.aim4c_falcon": "GAR-2A (AIM-4C) Falcon IR Missile",
        "comp.missile.aim9b_sidewinder": "AAM-N-7 / GAR-8 (AIM-9B) Sidewinder IR Missile",
        "comp.missile.air2a_genie": "MB-1 (AIR-2A) Genie Nuclear Air-to-Air Rocket",
        "comp.missile.aim7c_sparrow3": "AAM-N-6 (AIM-7C) Sparrow III SARH Missile",
        "comp.missile.aim26a_nuclear_falcon": "GAR-11 (AIM-26A) Nuclear Falcon SARH Missile",
        "comp.radar.scr720": "Western Electric SCR-720 AI Search Radar",
        "comp.radar.apg5": "AN/APG-5 Gun-Ranging Radar",
        "comp.radar.aps19": "Sperry AN/APS-19 X-Band Search & Gun-Aiming Radar",
        "comp.radar.apg30": "GE AN/APG-30 Radar Rangefinder (with A-1CM Sight)",
        "comp.radar.apg33": "Hughes AN/APG-33 Radar (E-1 Fire Control System)",
        "comp.radar.aps21": "Westinghouse AN/APS-21 All-Weather AI Radar (APQ-35)",
        "comp.radar.apg37": "Hughes AN/APG-37 Radar (E-4/E-5/E-6 Lead-Collision FCS)",
        "comp.radar.apg40": "Hughes AN/APG-40 Radar (E-9 Fire Control System)",
        "comp.radar.mg10": "Hughes MG-10 / MG-13 Automatic Weapon Control System",
        "comp.radar.apq50": "Westinghouse AN/APQ-50 All-Weather Fighter Radar",
        "comp.radar.ma1": "Hughes MA-1 Digital Integrated Weapon Control System",
        "comp.radar.apq72": "Westinghouse AN/APQ-72 Long-Range Fleet Defense Radar"
      }
    }
  }
};
