# 03 — Technology Tree, Research Mechanics, and NACA Diffusion (1945–1960 Detailed; 1960–2030 Outline)

> Status: v1.0. Owner: Module 03.
> Companion spec: [`docs/spec/03_tech_effect_keys.md`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/03_tech_effect_keys.md) (canonical effect key registry).
> Reference oracle: [`sim/mic/tech/`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/tech/__init__.py).
> Data files: [`sim/data/tech/effect_keys.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/tech/effect_keys.json), [`sim/data/tech/tech_nodes_1945_1960.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/tech/tech_nodes_1945_1960.json), [`sim/data/tech/components_guns.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/tech/components_guns.json), [`sim/data/tech/components_rockets.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/tech/components_rockets.json), [`sim/data/tech/components_missiles.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/tech/components_missiles.json), [`sim/data/tech/components_radars.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/tech/components_radars.json), [`sim/data/tuning/tech.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/tuning/tech.json).

---

## 1. Purpose & Player Fantasy

In *Military-Industrial Complex: Jet Age*, the player is the chief executive and technical director of an aircraft manufacturer navigating the most explosive 15-year technological revolution in aviation history (1945–1960). In January 1945, the state of the art is a 500-mph straight-wing jet with a centrifugal compressor, manual flight controls, .50-caliber machine guns, and wind tunnels that choke at Mach 0.85. By 1960, industry leaders are building Mach 2.2+ delta-wing and twin-engine interceptors with variable-geometry inlets, titanium/honeycomb structures, afterburning twin-spool or variable-stator turbojets, pulse/CW radars coupled to SAGE digital datalinks, and semi-active radar homing missiles.

Module 03 turns this historical progression into **strategic R&D resource-allocation and risk-management trade-offs**:

1. **Pioneering (IRAD) vs. Following NACA Diffusion**: Should your firm spend scarce internal R&D (IRAD) cash and top aerodynamicists in 1946 to pioneer 35° swept wings and all-moving tails ahead of competitors, or wait 2–3 years for NACA Langley/Ames Technical Notes to diffuse the knowledge across the US industry at a fraction of the cost?
2. **Internal R&D (IRAD) vs. Government-Funded R&D Contracts**: Bidding on or accepting USAF/USN/NACA research contracts covers 80% of direct lab costs and grants a +15% speed bonus via Wright Field / BuAer test data, but is only available on government-priority nodes (`govt_contract_eligible: true`). Proprietary manufacturing and structural techniques must be self-funded via IRAD.
3. **Unlocking vs. Maturing ("Paper Tech vs. Proven Hardware")**: Unlocking a technology node immediately grants **100% of its physical effect** (e.g., unlocking Whitcomb Area Rule immediately permits `fuselage.area_ruled = true` with 0.60 wave-drag efficiency), keeping physics deterministic. However, a newly unlocked technology starts at low **maturity** ($m \approx 0.35$). Low maturity inflates performance estimation uncertainty ($\sigma$), hidden flaw incidence in Module 06, unit production cost premiums in Module 04, and technical risk penalties in Module 05 bid evaluations. The only way to push maturity above the passive bench-work ceiling ($0.65$) toward $1.0$ is **learning-by-doing**: running wind-tunnel campaigns, flying prototypes, diagnosing flaws, and producing aircraft in volume.
4. **Preventing Hindsight Exploitation**: A non-linear ahead-of-time penalty prevents a player with 21st-century hindsight from rushing 1956 Mach 2 technologies in 1947, while still allowing a specialized company (e.g., Convair on delta wings, North American on swept wings, Pratt & Whitney on twin-spool compressors) to lead history by 1–1.5 years if they concentrate engineers and accept low initial maturity.

---

## 2. Scope

### 2.1 MVP In-Scope (USA, 1945-01-01 to 1960-12-31)
- **82 historical technology nodes** across 7 branches (`aero`, `structures`, `propulsion`, `avionics`, `armament`, `manufacturing`, `testing`), mapped to the 4 engineering staff disciplines in `CompanyState.engineers` (`aero`, `structures`, `propulsion`, `systems`).
- **87 canonical effect keys** (`sim/data/tech/effect_keys.json` & `docs/spec/03_tech_effect_keys.md`), aggregated daily per company into an immutable `TechContext`.
- **Component unlock catalogs** (`components_guns.json`, `components_rockets.json`, `components_missiles.json`, `components_radars.json`) with historical mass, drag area, dimensions, reliability, cost, and combat capability ratings.
- **Daily research simulation**: Brooks's Law diminishing returns per project, ahead-of-time penalty, behind-time catch-up bonus, IRAD vs. government contract funding splits, NACA diffusion (both active report speed bonus and passive knowledge drip), and chief-designer branch speed modifiers.
- **Two-regime maturity model**: passive bench refinement up to `passive_maturity_cap` ($0.65$), plus asymptotic learning-by-doing gains from simulation runs, wind-tunnel campaigns, prototype first flights, flight-test sorties, flaw fixes, and production batches.
- **Minimal-sufficient `required_techs(design, ctx)` resolution**: determines which unlocked technologies a specific `AircraftDesign` actually relies upon, without penalizing a conservative design just because the company has also unlocked bleeding-edge experimental nodes.

### 2.2 Post-MVP Out-of-Scope (System-Level Outline in §5.8)
- Tech nodes for **1961–2030** (Eras II–V: variable-sweep operational fighters, pulse-Doppler look-down/shoot-down, fly-by-wire, relaxed static stability, composites, high-BPR/afterburning turbofans, stealth shaping/RAM, AESA, thrust vectoring, 6th-gen CCA loyal wingmen). The `TechContext` key architecture is already forward-compatible.
- Non-US national tech trees and licensing/espionage mechanics (Soviet TsAGI diffusion, British Rolls-Royce Nene licensing, French export-oriented R&D).

---

## 3. Player-Facing Flow

1. **Viewing the Tech Tree**:
   - The player opens the **R&D / Tech Tree Screen** (specified in Module 08), organized into 7 horizontal branch lanes across a 1945–1960 timeline grid.
   - Each node displays:
     - Display name and historical milestone description (from `sim/data/names/tech_names.json`).
     - Status badge: `Unlocked (Maturity XX%)`, `In Progress (YY% — ETA N days)`, `Available`, or `Locked (Prereqs missing)`.
     - Discipline icon (`aero`, `structures`, `propulsion`, `systems`), base engineer-day cost (`cost_eng_days`), and direct laboratory cost (`cost_usd`).
     - Ahead-of-time / behind-time speed modifier at the current date (e.g., `Ahead of Time (-48% speed)` in amber, or `NACA TN Published (+35% speed)` in green).
     - Exact gameplay effects translated via `effect_keys.json` (e.g., `Max Wing Sweep: 10° → 35°`, `Unlocks Radar: AN/APG-30`).
2. **Assigning Engineers & Choosing Funding Mode**:
   - When starting or adjusting an available node, the player assigns $N$ engineers from the corresponding discipline pool (`CompanyState.engineers[discipline]`).
   - The UI plots the **Brooks's Law efficiency curve**: assigning up to 15 engineers gives 1:1 linear speed; assigning 16–40 engineers yields diminishing marginal returns ($N_{\text{eff}} = 15 + (N - 15)^{0.65}$); assigning more than 40 effective engineer-equivalents is capped.
   - If `govt_contract_eligible == true` and the company meets minimum service reputation, the player may toggle between **Internal R&D (IRAD)** (100% company-funded, no government strings) and **Government R&D Contract** (company pays only 20% of direct USD cost, +15% research speed from government lab data).
3. **NACA Diffusion & Industry Catch-Up**:
   - Two years (`naca_diffusion_lag_years = 2.0`) after a node's `historical_year`, if `naca_diffusion == true`, NACA declassifies its Research Memoranda into industry-wide Technical Notes:
     - Active research on that node gains a `1.35x` speed multiplier (`naca_report_speed_multiplier`).
     - Even with 0 engineers assigned, once prerequisites are unlocked, the node receives a passive NACA knowledge drip (`0.12%/day` of total progress), automatically unlocking after ~2.3 years so no US manufacturer stays permanently stuck in 1945.
4. **Unlock & Maturation**:
   - Upon reaching 100% progress (`progress_eng_days >= cost_eng_days`), the node unlocks at `initial_maturity` (typically `0.30`–`0.45`).
   - Its capabilities are immediately selectable in the Aircraft Design Editor (Module 01/08) or Engine Project Editor (Module 02).
   - A tooltip warns the player: *"Maturity 35% (Experimental): Using this technology in a bid or prototype carries elevated performance uncertainty and flaw risk until matured through wind-tunnel testing, flight testing, and production."*

---

## 4. Data Schemas

### 4.1 `sim/data/tech/effect_keys.json`
Machine-readable mirror of `docs/spec/03_tech_effect_keys.md`.
```json
{
  "key": "aero.wing_sweep_max_deg",
  "type": "float",
  "unit": "deg",
  "agg": "max",
  "null_value": 0.0,
  "start_1945": 10.0,
  "category": "aero",
  "meaning": "Max quarter-chord sweep the design editor allows. 10 deg = incidental sweep from taper on straight wings.",
  "consumers": ["01", "08"],
  "deprecated": false
}
```

### 4.2 `sim/data/tech/tech_nodes_1945_1960.json`
| Field | Type | Units / Range | Description |
|---|---|---|---|
| `id` | `str` | snake_case | Unique identifier (`<branch>_<year>_<slug>`). |
| `name_key` | `str` | – | Localization key in `sim/data/names/tech_names.json`. |
| `branch` | `str` | enum | `"aero" \| "structures" \| "propulsion" \| "avionics" \| "armament" \| "manufacturing" \| "testing"`. |
| `discipline` | `str` | enum | Engineer pool used: `"aero" \| "structures" \| "propulsion" \| "systems"`. |
| `historical_year` | `float` | `[1944.0, 1960.5]` | Fractional year when first achieved in US aviation history. |
| `historical_date` | `str` | `YYYY-MM-DD` | Calendar date corresponding to `historical_year`. |
| `granted_at_start` | `bool` | – | `true` for the 7 baseline WWII nodes unlocked on 1945-01-01. |
| `initial_maturity` | `float` | `(0.0, 1.0]` | Maturity upon unlock (`0.85–0.90` for WWII baselines; `0.25–0.50` for new nodes). |
| `prereqs` | `list[str]` | node IDs | Prerequisite node IDs (must form a strict DAG). |
| `cost_eng_days` | `int` | `[500, 4000]` | Base engineer-days required to complete research at 1.0x multiplier. |
| `cost_usd` | `float` | USD (1950 nominal) | Total direct laboratory/material/rig USD cost over the project. |
| `naca_diffusion` | `bool` | – | Whether NACA diffuses this node via Technical Notes after `naca_diffusion_lag_years`. |
| `govt_contract_eligible` | `bool` | – | Whether USAF/USN/NACA cost-shared research contracts can fund this node. |
| `effects` | `dict` | `{effect_key: val}` | Effect key values provided when unlocked. |
| `historical_note` | `str` | – | Archival reference (NACA report, X-plane, engine, or fighter program). |

### 4.3 Component Catalogs (`sim/data/tech/components_*.json`)
- **Guns (`components_guns.json`)**: `id`, `unlock_key`, `name_key`, `historical_designation`, `caliber_mm`, `gun_mass_kg`, `feed_and_mount_mass_kg`, `round_mass_kg`, `std_rounds_per_gun`, `installed_mass_with_std_ammo_kg`, `rate_of_fire_rpm`, `muzzle_velocity_mps`, `burst_mass_kgps`, `wvr_lethality_score`, `reliability_mtbf_rounds`, `unit_cost_usd`, `historical_year`, `granted_at_start`.
- **Rockets (`components_rockets.json`)**: `id`, `unlock_key`, `name_key`, `historical_designation`, `diameter_m`, `length_m`, `single_round_mass_kg`, `salvo_pack_count`, `pack_installed_mass_kg`, `drag_area_m2`, `burnout_velocity_mps`, `effective_range_m`, `role`, `cas_score`, `interceptor_salvo_score`, `unit_cost_usd`, `historical_year`, `granted_at_start`.
- **Missiles (`components_missiles.json`)**: `id`, `unlock_key`, `name_key`, `historical_designation`, `guidance_type` (`"beam_rider" | "sarh" | "ir" | "unguided_nuclear" | "sarh_nuclear"`), `generation`, `mass_kg`, `pylon_mass_kg`, `installed_mass_per_round_kg`, `length_m`, `diameter_m`, `drag_area_m2`, `max_mach`, `min_range_m`, `max_effective_range_m`, `all_aspect`, `all_weather`, `base_pk`, `bvr_capability_score`, `wvr_capability_score`, `requires_internal_bay`, `unit_cost_usd`, `historical_year`, `granted_at_start`.
- **Radars (`components_radars.json`)**: `id`, `unlock_key`, `name_key`, `historical_designation`, `category` (`"ai_search" | "gun_ranging" | "ai_fcs" | "awcs"`), `band`, `mass_kg`, `dish_diameter_m`, `min_nose_diameter_m`, `power_kw`, `detection_range_bomber_m`, `detection_range_fighter_m`, `supports_lead_collision`, `supports_sarh_cw`, `supports_beam_rider`, `supports_sage_datalink`, `mtbf_h`, `bvr_sensor_score`, `unit_cost_usd`, `historical_year`, `granted_at_start`.

---

## 5. Algorithms

All formulas are implemented in [`sim/mic/tech/context.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/tech/context.py) and [`sim/mic/tech/research.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/tech/research.py).

### 5.1 Calendar Year Conversion
Given `date_day` (integer days since `1945-01-01`):
$$t_{\text{yr}} = 1945.0 + \frac{\text{date\_day}}{365.25}$$

### 5.2 Brooks's Law Effective Engineers (`effective_engineers`)
When $N \in \mathbb{Z}_{\ge 0}$ engineers are assigned to a single research project, communication overhead reduces marginal productivity above $N_{\text{thresh}} = 15$ (`diminishing_returns_threshold_eng`) with exponent $\alpha = 0.65$ (`diminishing_returns_exponent`), capped at $N_{\text{max}} = 40.0$ (`max_effective_engineers_per_project`):
$$N_{\text{eff}}(N) = \begin{cases} 0.0 & \text{if } N \le 0 \\ N & \text{if } 0 < N \le N_{\text{thresh}} \\ \min\!\left(N_{\text{max}},\, N_{\text{thresh}} + (N - N_{\text{thresh}})^\alpha\right) & \text{if } N > N_{\text{thresh}} \end{cases}$$

### 5.3 Ahead-of-Time Penalty & Behind-Time Catch-Up (`ahead_of_time_multiplier`)
For a tech node with `historical_year` $Y_{\text{hist}}$ at current fractional year $t_{\text{yr}}$:
- Define free lead window $\Delta_{\text{free}} = 0.5\text{ yr}$ (`aot_free_lead_years`).
- Define early excess $\Delta_{\text{early}} = (Y_{\text{hist}} - \Delta_{\text{free}}) - t_{\text{yr}}$.
- Define late excess $\Delta_{\text{late}} = t_{\text{yr}} - Y_{\text{hist}}$.

$$M_{\text{time}}(t_{\text{yr}}, Y_{\text{hist}}) = \begin{cases} \max\!\left(M_{\text{aot,min}},\, \dfrac{1.0}{1.0 + k_{\text{aot}} \cdot (\Delta_{\text{early}})^{p_{\text{aot}}}}\right) & \text{if } \Delta_{\text{early}} > 0 \\ \min\!\left(M_{\text{catchup,max}},\, 1.0 + k_{\text{catchup}} \cdot \Delta_{\text{late}}\right) & \text{if } \Delta_{\text{late}} > 0 \\ 1.0 & \text{otherwise} \end{cases}$$
where default tunables are $k_{\text{aot}} = 0.55$, $p_{\text{aot}} = 1.6$, $M_{\text{aot,min}} = 0.12$, $k_{\text{catchup}} = 0.20$, $M_{\text{catchup,max}} = 1.75$.

### 5.4 Daily Active Progress, Funding Mode, and NACA Diffusion (`step_company_tech_day`)
For an active research project on node $i$ with discipline $d = \text{node.discipline}$ and branch $b = \text{node.branch}$:
1. **Funding multiplier & cost share**:
   - If `funding_mode == "irad"`: $M_{\text{fund}} = 1.0$, $S_{\text{comp}} = 1.0$ (`irad_company_cost_share`).
   - If `funding_mode == "govt_contract"` (requires `node.govt_contract_eligible == True`): $M_{\text{fund}} = 1.15$ (`govt_contract_speed_multiplier`), $S_{\text{comp}} = 0.20$ (`govt_contract_company_cost_share`).
2. **NACA Technical Note report bonus**:
   $$M_{\text{naca}} = \begin{cases} 1.35 & \text{if } \text{node.naca\_diffusion} \land t_{\text{yr}} \ge Y_{\text{hist}} + \Delta_{\text{naca}} \\ 1.0 & \text{otherwise} \end{cases}$$
   where $\Delta_{\text{naca}} = 2.0\text{ yr}$ (`naca_diffusion_lag_years`).
3. **Discipline & Chief Designer modifiers**:
   - $M_{\text{disc}} = \text{ctx.get}(\texttt{"research.speed\_factor."} + d)$ (increased by digital computers, slotted tunnels, etc.).
   - $M_{\text{designer}} = \max(0.5,\, 1.0 + \beta_{\text{designer}, b})$, where $\beta_{\text{designer}, b}$ is the company chief designer's branch speed bonus from Module 10.
4. **Active daily progress & USD spend**:
   $$\Delta P_{\text{active}} = \min\!\Big(C_{\text{eng}} - P_{\text{cur}},\, \eta_{\text{eng}} \cdot N_{\text{eff}} \cdot M_{\text{time}} \cdot M_{\text{fund}} \cdot M_{\text{naca}} \cdot M_{\text{disc}} \cdot M_{\text{designer}} \cdot f_{\text{throttle}}\Big)$$
   $$\Delta \text{USD}_{\text{comp}} = \frac{\Delta P_{\text{active}}}{C_{\text{eng}}} \cdot C_{\text{usd}} \cdot S_{\text{comp}}, \qquad \Delta \text{USD}_{\text{govt}} = \frac{\Delta P_{\text{active}}}{C_{\text{eng}}} \cdot C_{\text{usd}} \cdot (1.0 - S_{\text{comp}})$$
5. **Passive NACA Diffusion Drip**:
   For every unresearched node $j$ with `naca_diffusion == True`, all `prereqs` unlocked at the start of the day, and $t_{\text{yr}} \ge Y_{\text{hist}, j} + \Delta_{\text{naca}}$:
   $$\Delta P_{\text{naca}, j} = \min\!\big(C_{\text{eng}, j} - P_{\text{cur}, j},\, r_{\text{drip}} \cdot C_{\text{eng}, j}\big)$$
   where $r_{\text{drip}} = 0.0012\text{ day}^{-1}$ (`naca_passive_drip_frac_per_day`), costing $0$ direct USD.

### 5.5 Maturity Growth: Passive Bench Refinement & Learning-by-Doing
1. **On Unlock**: Node $i$ enters `unlocked_maturity` at $m_i = \text{node.initial\_maturity}$.
2. **Daily Passive Refinement**: Each day, for every unlocked tech $i$ with $m_i < m_{\text{passive,cap}}$ ($0.65$):
   $$m_i \leftarrow \min\!\big(m_{\text{passive,cap}},\, m_i + r_{\text{passive}}\big)$$
   with $r_{\text{passive}} = 0.00025\text{ day}^{-1}$ ($\approx +0.091/\text{yr}$).
3. **Learning-by-Doing Events (`apply_learning_by_doing`)**:
   Whenever a design or engine relying on tech set $T_{\text{used}}$ completes an engineering or production milestone $e \in \{\texttt{sim\_run}, \texttt{tunnel\_campaign}, \texttt{first\_flight}, \texttt{flight\_test\_sortie}, \texttt{flaw\_fixed}, \texttt{production\_10\_units}\}$ with scale $s$:
   $$\forall i \in T_{\text{used}}:\quad m_i \leftarrow \min\!\big(1.0,\, m_i + \gamma_e \cdot s \cdot (1.0 - m_i)\big)$$
   Because the increment scales with $(1 - m_i)$, maturity approaches $1.0$ smoothly and asymptotically.

### 5.6 Minimal-Sufficient `required_techs(design, ctx)`
Given a design's feature dictionary (extracted from `AircraftDesign` via `extract_design_features`), for each requested feature key $k$ with value $v$:
- If `agg == "or"` and $v \equiv \text{True}$ (while `null_value` is `False`): requires `ctx.provider[k]` (the highest-maturity unlocked provider of $k$).
- If `agg == "max"` and $v > \text{null\_value} + \epsilon$:
  - If $v > \text{ctx.get}(k) + \epsilon$, raise `ValueError("TECH_CAP:" + k)`.
  - Among all unlocked nodes $i \in \text{ctx.unlocked}$ whose effect satisfies $E_{i,k} \ge v - \epsilon$, select the node minimizing $(E_{i,k}, -m_i, \text{id}_i)$.
- If `agg == "min"` and $v < \text{null\_value} - \epsilon$:
  - If $v < \text{ctx.get}(k) - \epsilon$, raise `ValueError("TECH_CAP:" + k)`.
  - Among all unlocked nodes $i \in \text{ctx.unlocked}$ whose effect satisfies $E_{i,k} \le v + \epsilon$, select the node minimizing $(-E_{i,k}, -m_i, \text{id}_i)$.

This guarantees that an F-86E design with a 35° swept wing only depends on `aero_1945_swept_wing_theory` (35° cap) even if the company has just unlocked experimental 60° delta wings (`aero_1948_tailless_delta_basics`).

### 5.7 Complete 1945–1960 Technology Node Summary (82 Nodes)
- **Aerodynamics (`aero`, 18 nodes)**: `aero_1945_compressible_subsonic` (start), `aero_1945_swept_wing_theory` (35°), `aero_1946_auto_le_slats`, `aero_1947_thin_airfoils_10pct` (9% t/c), `aero_1948_all_moving_tail`, `aero_1948_tailless_delta_basics` (60° delta), `aero_1949_subsonic_duct_splitters`, `aero_1950_high_sweep_45deg` (45° / 6% t/c), `aero_1951_le_droop_krueger_flaps`, `aero_1951_variable_sweep_exp` (X-5/XF10F), `aero_1952_whitcomb_area_rule` (0.60 eff), `aero_1953_supersonic_spike_inlet`, `aero_1953_razor_thin_wing_3pct` (3.4% t/c), `aero_1954_vortex_generators_excrescence`, `aero_1955_conical_camber`, `aero_1955_blc_blown_flaps`, `aero_1955_variable_geometry_inlet`, `aero_1956_supersonic_area_rule` (0.80 eff).
- **Structures & Materials (`structures`, 9 nodes)**: `struct_1945_stressed_skin_7075` (start), `struct_1946_thick_skin_box_spar`, `struct_1948_jet_carrier_suitability`, `struct_1951_titanium_metallurgy_1` (12% Ti, 445 K), `struct_1952_integrally_stiffened_skins`, `struct_1954_bonded_honeycomb`, `struct_1955_fatigue_failsafe_design`, `struct_1956_ti_6al_4v_structural` (30% Ti, 495 K), `struct_1958_ph_stainless_brazed_thermal` (50% Ti, 65% steel, 585 K).
- **Propulsion (`propulsion`, 13 nodes)**: `prop_1945_centrifugal_turbojet` (start), `prop_1945_early_axial_compressor` (start, maturity 0.55), `prop_1947_nimonic_superalloys_1` (1135 K), `prop_1948_afterburner_1` (1750 K), `prop_1949_multi_stage_axial_refinement` (OPR 7.0), `prop_1950_component_altitude_test_cells`, `prop_1952_twin_spool_compressor` (J57 class, OPR 12.5), `prop_1953_modulated_afterburner` (1950 K), `prop_1954_waspaloy_vacuum_superalloys` (1200 K), `prop_1954_variable_stator_compressor` (J79 class, OPR 13.5), `prop_1956_high_massflow_cores` (J75 class, 125 kg/s), `prop_1958_cooled_turbine_blades` (1340 K), `prop_1959_low_bypass_turbofan` (BPR 1.4, OPR 16.0).
- **Avionics & Flight Controls (`avionics`, 15 nodes)**: `av_1945_vhf_gyro_sight_scr720` (start), `sys_1946_hydraulic_boost_controls`, `sys_1946_ejection_seat`, `av_1946_xband_navy_ai_radar` (APS-19), `av_1948_radar_ranging_gunsight` (APG-30), `sys_1949_stability_augmentation_sas`, `av_1949_all_weather_fcs_e1` (APG-33, APS-21), `sys_1950_inflight_refueling`, `av_1951_lead_collision_fcs_e4` (APG-37, APG-40), `av_1954_subminiature_tubes_pcb`, `av_1955_awcs_mg10_apq50`, `av_1956_sage_gci_datalink`, `av_1957_solid_state_transistor_avionics`, `av_1958_irst_sensor`, `av_1958_integrated_digital_awcs_ma1_apq72`.
- **Armament (`armament`, 12 nodes)**: `arm_1945_ww2_guns_and_hvar` (start), `arm_1947_m3_high_rof_50cal`, `arm_1949_ffar_m24_interceptor_ordnance`, `arm_1952_revolver_and_navy_20mm_cannons` (M39, Mk 12), `arm_1952_labs_tactical_nuclear_delivery`, `arm_1953_internal_weapons_bay`, `arm_1954_beam_riding_sparrow1` (AIM-7A), `arm_1955_sarh_homing_gen1_falcon` (AIM-4A), `arm_1955_ir_homing_gen1` (AIM-9B, AIM-4C), `arm_1956_m61_vulcan_rotary_cannon` (M61), `arm_1957_nuclear_air_to_air_rockets` (AIR-2A Genie), `arm_1958_sarh_gen2_sparrow3_nuclear_falcon` (AIM-7C, AIM-26A).
- **Manufacturing (`manufacturing`, 7 nodes)**: `mfg_1945_ww2_mass_production_line` (start), `mfg_1947_flush_riveting_aerodynamic_smoothing`, `mfg_1949_optical_tooling_jigs`, `mfg_1950_heavy_forging_presses`, `mfg_1953_statistical_quality_control`, `mfg_1954_titanium_forming_chem_mill`, `mfg_1956_nc_machining`.
- **Testing & Simulation (`testing`, 8 nodes)**: `test_1945_sub_and_supersonic_blowdown_tunnels` (start), `test_1946_wallops_rocket_models`, `test_1948_fm_telemetry_oscillographs`, `test_1950_slotted_transonic_tunnel`, `test_1952_flutter_aeroelastic_analog`, `test_1953_ibm_701_digital_computing`, `test_1955_inertia_coupling_6dof_sim`, `test_1957_high_speed_flight_station_datcom`.

### 5.8 System-Design Outline for Later Eras (1961–2030)
To ensure the 1945–1960 schema scales to 2030 without refactoring:
- **Era II (1961–1975: Vietnam & Energy-Maneuverability)**: Afterburning turbofans (`TF30`, `F100`), operational variable-sweep (`F-111`, `F-14`), leading-edge root extensions (`aero.lerx`), pulse-Doppler look-down/shoot-down radars (`AWG-9`, `APG-63`), all-aspect cooled IR missiles (`AIM-9L`, `armament.missile_ir_gen = 3`), active BVR (`AIM-54`).
- **Era III (1976–1990: Digital Teens & Early Stealth)**: Quad-redundant digital fly-by-wire (`systems.fbw_digital`), relaxed static stability (`aero.relaxed_static_stability`), carbon-fiber composites (`struct.material.composite_max_fraction`), faceted low-observable shaping (`stealth.rcs_frontal_factor`), AMRAAM (`AIM-120A`).
- **Era IV (1991–2015: 5th Generation)**: Continuous-curvature stealth + durable RAM, supercruise cycle optimization, 2D/3D thrust vectoring (`engine.thrust_vectoring`), AESA radars (`APG-77`, `APG-81`), sensor fusion, helmet-mounted off-boresight cueing (`AIM-9X`).
- **Era V (2016–2030: 6th Generation & CCA)**: Adaptive three-stream variable-cycle engines (`engine.adaptive_cycle`), cooperative autonomous loyal wingmen (`systems.cca_control`), directed-energy/hypersonic interceptors.

---

## 6. Tunables Table

All values reside in [`sim/data/tuning/tech.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/tuning/tech.json).

| Name | Default | Range | Effect | Rationale |
|---|---|---|---|---|
| `eng_efficiency_per_day` | `1.0` | `[0.25, 4.0]` | Base engineer-days of progress per effective engineer per day | 10 engineers complete an 1,800 eng-day node in ~180 days at 1.0x |
| `max_effective_engineers_per_project` | `40.0` | `[10, 100]` | Hard cap on effective engineer-equivalents per node | Brooks's Law prevents infinite manpower stacking |
| `diminishing_returns_threshold_eng` | `15.0` | `[5, 40]` | Team size before diminishing returns apply | 10–15 person research groups operate at 100% efficiency |
| `diminishing_returns_exponent` | `0.65` | `[0.4, 1.0]` | Power-law exponent above threshold | Encourages spreading engineers across 2–4 concurrent nodes |
| `aot_free_lead_years` | `0.5` | `[0.0, 2.0]` | Years before `historical_year` with no ahead-of-time penalty | Permits 6-month historical lead without artificial friction |
| `aot_rate_per_year` | `0.55` | `[0.1, 2.0]` | Penalty coefficient per year ahead of free-lead window | Prevents rushing late-1950s tech in the late 1940s |
| `aot_exponent` | `1.6` | `[1.0, 3.0]` | Non-linear exponent on ahead-of-time excess years | Gentle for 1 yr early (0.72x), steep for 3+ yrs early (0.31x) |
| `aot_min_speed_multiplier` | `0.12` | `[0.05, 0.5]` | Minimum speed multiplier floor | Prevents numerical stall |
| `catchup_rate_per_year` | `0.20` | `[0.0, 0.5]` | Linear speed bonus per year after `historical_year` | Trade press & engineer mobility accelerate late adopters |
| `catchup_max_speed_multiplier` | `1.75` | `[1.0, 3.0]` | Cap on behind-time catch-up multiplier | Reached 3.75 years after historical date |
| `irad_company_cost_share` | `1.0` | `[0.5, 1.0]` | Company fraction of direct research USD in IRAD mode | IRAD is 100% self-funded |
| `govt_contract_company_cost_share` | `0.20` | `[0.0, 0.5]` | Company fraction of direct research USD under govt contract | Government reimburses 80% of direct lab/rig expenses |
| `govt_contract_speed_multiplier` | `1.15` | `[1.0, 1.5]` | Speed multiplier for government-contracted research | Access to Wright Field / BuAer test facilities |
| `naca_diffusion_lag_years` | `2.0` | `[0.5, 5.0]` | Years after `historical_year` before NACA TN diffusion starts | Models declassification of NACA RM reports into NACA TNs |
| `naca_report_speed_multiplier` | `1.35` | `[1.0, 2.0]` | Active research speed multiplier once NACA TN is published | Published wind-tunnel curves cut internal trial-and-error |
| `naca_passive_drip_frac_per_day` | `0.0012` | `[0.0, 0.005]` | Passive daily progress fraction once NACA diffusion is active | Unresearched NACA nodes auto-complete in ~2.3 years |
| `default_unlock_maturity` | `0.35` | `[0.1, 0.7]` | Fallback unlock maturity if not specified on node | Lab proof-of-concept still needs flight & production maturation |
| `passive_maturity_rate_per_day` | `0.00025` | `[0.0, 0.001]` | Daily passive maturity increase up to `passive_maturity_cap` | ~9%/year from bench refinement |
| `passive_maturity_cap` | `0.65` | `[0.4, 0.85]` | Ceiling on passive maturity without hardware testing | Flight testing and production are required to reach >0.65 |
| `maturity_gain_sim_run` | `0.02` | `[0.005, 0.05]` | Asymptotic maturity gain factor on simulation analysis | Small analytical familiarity gain |
| `maturity_gain_tunnel_campaign` | `0.08` | `[0.02, 0.20]` | Asymptotic maturity gain factor on wind-tunnel campaign | Major aerodynamic/structural validation step |
| `maturity_gain_first_flight` | `0.12` | `[0.05, 0.25]` | Asymptotic maturity gain factor on prototype first flight | Biggest single hardware integration milestone |
| `maturity_gain_flight_test_sortie` | `0.015` | `[0.005, 0.05]` | Asymptotic maturity gain factor per flight-test sortie | Incremental envelope expansion learning |
| `maturity_gain_flaw_fixed` | `0.10` | `[0.03, 0.25]` | Asymptotic maturity gain factor when fixing a `HiddenFlaw` | Solving a flaw permanently advances company know-how |
| `maturity_gain_production_10_units` | `0.04` | `[0.01, 0.10]` | Asymptotic maturity gain factor per 10 aircraft delivered | Series manufacturing & squadron service feedback |

---

## 7. Edge Cases & Failure Modes

1. **Missing Keys or Unknown Keys**: `TechContext.values` is verified at build time to contain all 87 keys from `effect_keys.json`. Calling `ctx.get(unknown_key)` raises `KeyError` immediately—never silently returns `None` or `0`.
2. **Mid-Project Engineer Reassignment or Cash Crunch**: If the player reduces `assigned_engineers` to `0` or `budget_throttle` to `0.0` (e.g., during a cash crisis in Module 04), `progress_eng_days` is preserved in `state.partial_progress[tech_id]` without decay.
3. **Overshooting Node Progress on Final Day**: `compute_daily_active_progress` clamps `actual_progress = min(remaining, raw_progress)` so the company is never billed more than 100% of `node.cost_usd`.
4. **Multiple Unlocks Providing the Same Capability at Different Maturities**:
   - Suppose a company has unlocked 35° sweep (`aero_1945_swept_wing_theory`, maturity `0.85`) and later unlocks 60° delta sweep (`aero_1948_tailless_delta_basics`, maturity `0.30`).
   - `ctx.get("aero.wing_sweep_max_deg")` increases to `60.0` (so the editor allows up to 60°), and `ctx.maturity_of("aero.wing_sweep_max_deg")` reports `0.30` (the maturity of the 60° provider).
   - However, when evaluating a 35° swept-wing design via `required_techs(design, ctx)`, the minimal-sufficient resolver selects `aero_1945_swept_wing_theory` (maturity `0.85`), ensuring that unlocking experimental delta wings **never degrades** the reliability or uncertainty of existing 35° swept-wing designs!
5. **Floating-Point Boundary Tolerance**: `allows()` and `required_techs()` apply `float_cap_epsilon = 1e-6` so a design specifying `tc_ratio = 0.06` against a `0.06` minimum cap is never rejected due to IEEE-754 representation (`0.059999999999999998`).

---

## 8. Golden Test Vectors

Generated by [`sim/mic/tech/`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/tech/__init__.py) and verified by [`sim/tests/test_tech.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/tests/test_tech.py) (all tolerances `rel_tol = 1e-6`):

1. [`sim/golden/tech_context_start_1945.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/golden/tech_context_start_1945.json): Canonical 1945-01-01 `TechContext` snapshot for a standard US company with the 7 `granted_at_start: true` nodes unlocked. Every key matches the `start` column of `docs/spec/03_tech_effect_keys.md`.
2. [`sim/golden/tech_aggregation_and_required.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/golden/tech_aggregation_and_required.json): Multi-node aggregation (`or`, `max`, `min`, `mul`, `add`), provider/maturity tie-breaking, and `required_techs()` vectors for a 1950 F-86E Sabre configuration and a 1958 F-106A Delta Dart configuration.
3. [`sim/golden/tech_research_and_maturity.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/golden/tech_research_and_maturity.json): Exact vectors for `ahead_of_time_multiplier` across 1945–1955, `effective_engineers` across 0–100 engineers, a complete daily trajectory of `aero_1945_swept_wing_theory` under government contract funding, and post-unlock learning-by-doing maturity jumps.

---

## 9. Interactions

| Module | Direction | Contract / API | Description |
|---|---|---|---|
| **01 Aero & Perf** | `03 → 01` | `TechContext`, `components_*.json`, `required_techs()` | 01 reads `aero.*`, `struct.*`, `mfg.surface_finish_factor`, component masses/drag areas, and validates design geometry against caps. |
| **02 Engines** | `03 → 02` | `TechContext` (`engine.*`) | 02 reads compressor/turbine efficiency ceilings, `tit_max_K`, `opr_max`, `afterburner`, `twin_spool`, `variable_stators`, `low_bypass_turbofan`. |
| **04 Economy** | `03 ↔ 04` | `CompanyState.engineers`, `DailyTechStepResult.company_cost_usd`, `mfg.*` | 04 supplies available engineer headcount & deducts daily research USD; reads `mfg.*` multipliers and tech maturities for production cost curves. |
| **05 Procurement** | `03 → 05` | `TechContext`, `components_*.json`, `required_techs()` | 05 checks RFP equipment requirements (e.g., ejection seat, radar, all-weather FCS, missiles) and penalizes bid technical risk based on `tech_maturity` of `design.techs_used`. |
| **06 Testing & Flaws** | `03 ↔ 06` | `TechContext` (`testing.*`), `apply_learning_by_doing()` | 06 scales estimation `sigma`, flaw incidence, and flaw detection probabilities by `testing.*` and `tech_maturity`; calls `apply_learning_by_doing()` after tunnel/flight tests and flaw fixes. |
| **07 Competitor AI** | `03 → 07` | `CompanyTechState` | AI companies allocate engineers to tech nodes matching their historical specialties and upcoming RFP targets. |
| **10 Content** | `10 → 03` | `companies/*.json`, `names/tech_names.json` | 10 defines starting company tech maturities, chief designer branch bonuses (`designer_branch_bonuses`), and display strings. |

---

## 10. Validation Results

- **Schema & DAG verification**: All 82 nodes in `tech_nodes_1945_1960.json` form a verified acyclic DAG; all 87 effect keys in `effect_keys.json` are covered by at least one node; all 28 components across `components_guns.json` (7), `components_rockets.json` (2), `components_missiles.json` (7), and `components_radars.json` (12) match their `unlock.<type>.<id>` keys.
- **1945-01-01 Baseline Parity**: Zero discrepancies between `CompanyTechState.create_starting_1945().context()` and `docs/spec/03_tech_effect_keys.md` (`sim/tests/test_tech.py::test_start_1945_matches_effect_keys_spec`).
- **Historical Pacing Check**: With 15–20 engineers assigned at historical date under government contract, major milestone nodes (e.g., 35° swept wing, afterburner, Whitcomb area rule, twin-spool compressor) complete in 70–140 calendar days, matching historical NACA-to-prototype design-freeze lead times.

---

## 11. Open Questions & Cross-Module Change Requests

### 11.1 Open Questions (User Taste Only)
1. **Visibility of Future Tech Nodes**: Should the player see the entire 1945–1960 tech tree from Day 1 (with historical years and ahead-of-time penalties visible), or should nodes more than 1 tier ahead of currently unlocked prerequisites be shrouded ("fog of research") until prerequisites are met? *(Current implementation supports both; UI can filter by `prereqs` depth).*
2. **Government-Furnished Equipment (GFE) Unlocks**: Radars, guns, and missiles were historically developed by electronics/ordnance vendors (Hughes, Westinghouse, GE, Raytheon, China Lake) and supplied to airframers as GFE, whereas airframers still needed internal systems engineers to integrate them (e.g., Convair's F-102/MG-10 Weapon System 201A integration). Do you prefer keeping avionics/armament nodes researched by the airframer's `systems` engineers (current model, with 80% government contract subsidy), or having GFE components unlock automatically by calendar date while `systems` engineers only research integration levels?

### 11.2 Cross-Module Change Requests
- **None required to `00_conventions.md`**: `AircraftDesign.techs_used[]` and `CompanyState.tech_unlocked[]` match `00_conventions.md` §4.2 and §4.6. Note for Module 04/09: `CompanyState` should store `tech_maturity: {tech_id: float}` alongside (or as a map replacing) `tech_unlocked[]` so maturity persists across save/load.
