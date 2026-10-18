# 03a — Tech Effect Keys (canonical namespace)

> Status: v1.0 (STABLE — keys will not be renamed; new keys may be added; values of tech nodes may be re-tuned).
> Owner: module 03 (tech tree). Consumers: 01 aero/perf, 02 engines, 04 economy, 05 procurement, 06 testing, 07 AI, 08 UI.
> Companion: `docs/spec/03_tech_tree.md` (nodes, research model). Data: `sim/data/tech/effect_keys.json` (machine-readable copy of this table — **the JSON is authoritative if the two ever differ**). Python: `mic.tech.context`.

## 1. What a consumer gets: `TechContext`

Module 03 aggregates the effects of every tech a company has unlocked into one immutable object per company per day (recomputed only when the unlocked set or a maturity changes).

```python
TechContext {
  date_day: int                    # days since 1945-01-01 (00 §3)
  company_id: str
  values:   {effect_key: bool|float|int}   # ALWAYS contains EVERY key in this document (missing => bug)
  provider: {effect_key: tech_id|None}     # tech that sets the binding value (None => key is at its null value)
  maturity: {effect_key: float in [0,1]}   # maturity of the binding provider (1.0 if provider is None)
  tech_maturity: {tech_id: float in [0,1]} # all unlocked techs
  unlocked: sorted list[tech_id]
}
```
API (Python reference; C# mirrors names in PascalCase):
- `ctx.get(key)` → value (raises `KeyError` on unknown key — never silently default).
- `ctx.maturity_of(key)` → float.
- `ctx.allows(key, design_value)` → bool. For `max` keys: `design_value <= value`; `min` keys: `design_value >= value`; `or` keys: `value is True` (design_value ignored).

### 1.1 Aggregation rules (per key, column `agg`)

| agg | Type | Aggregated value | `provider` | `maturity` |
|---|---|---|---|---|
| `or` | bool | True if any unlocked tech sets it True, else `null` (False) | first tech (by tech id sort) among the providers with highest maturity | that tech's maturity |
| `max` | float/int | max(null, all tech values) | tech giving the max (ties: highest maturity, then id sort) | that tech's maturity |
| `min` | float | min(null, all tech values) | tech giving the min (same tie rule) | that tech's maturity |
| `mul` | float | null × Π(tech values) | the tech with the lowest maturity among contributors | min maturity among contributors |
| `add` | float | null + Σ(tech values) | same as `mul` | same as `mul` |

`null` = identity value when **no** tech provides the key. `start` = value for a standard US company on 1945-01-01 after the "baseline" techs (`granted_at_start: true` in `sim/data/tech/*.json`) are applied. Consumers must read values from `TechContext`, never hard-code `start`; `start` is listed for convenience and is golden-tested (`sim/golden/tech_context_start_1945.json`).

### 1.2 Important semantics

1. **Effects are full-strength on unlock.** Maturity does NOT scale effect values. Maturity affects *uncertainty and risk* (module 06 reads `maturity`), *production cost premium* (04 reads), and *bid evaluation risk* (05 reads). Rationale: keeps physics deterministic and predictable for the player; risk lives in 06.
2. **Caps are hard.** The design editor (08) clamps inputs to `max`/`min` keys; module 01 `validate(design, ctx)` rejects designs that violate them with error code `TECH_CAP:<key>`.
3. **`unlock.<component_type>.<component_id>` keys** are bools generated from the component catalogs `sim/data/tech/components_*.json` (owned by 03; stats of each radar/gun/missile/rocket there). Every catalog entry automatically has an `or` key with `null=False`. Module 01 reads mass/drag of the component from the catalog; 05 reads capability.
4. **Which tech does a design rely on?** `mic.tech.required_techs(design_features, ctx)` returns, for each capped feature the design actually uses beyond the `null` value, the provider tech id (see 03_tech_tree §5.6). This fills `AircraftDesign.techs_used[]`; 06 uses those techs' maturities for sigma/flaw rolls.
5. Units follow 00 §3: SI internally, `_deg` suffix = degrees in data.

## 2. Key table

Columns: `key | type | unit | agg | null | start (1945-01-01) | meaning | consumer(s)`.

### 2.1 Aerodynamics (`aero.*`)

| key | type | unit | agg | null | start | meaning | consumer |
|---|---|---|---|---|---|---|---|
| `aero.wing_sweep_max_deg` | float | deg (quarter-chord) | max | 0 | 10 | Max quarter-chord sweep the design editor allows. 10° = incidental sweep from taper on "straight" wings. | 01, 08 |
| `aero.thin_wing_tc_min` | float | ratio | min | 0.15 | 0.12 | Thinnest allowed mean thickness/chord (structural + manufacturing know-how). | 01, 08 |
| `aero.aspect_ratio_min` | float | – | min | 3.0 | 3.0 | Lowest aspect ratio allowed (low-AR wings need high-alpha knowledge). | 01, 08 |
| `aero.delta_wing` | bool | – | or | False | False | Delta / tailless-delta planforms allowed (planform type `delta`). | 01, 08 |
| `aero.variable_sweep` | bool | – | or | False | False | Variable-sweep wing allowed (MVP: experimental, very heavy). | 01, 08 |
| `aero.area_rule` | bool | – | or | False | False | `fuselage.area_ruled = true` permitted; 01 applies area-rule wave-drag reduction. | 01 |
| `aero.wave_drag_area_rule_eff` | float | ratio | max | 0.0 | 0.0 | Fraction of theoretical wave-drag reduction achieved by area ruling (0 = none). Whitcomb basic 0.6; supersonic area rule 0.8. | 01 |
| `aero.conical_camber` | bool | – | or | False | False | Conical camber on delta LE (reduces drag-due-to-lift ~ per 01). | 01 |
| `aero.le_slats` | bool | – | or | False | False | Automatic leading-edge slats as a wing device. | 01 |
| `aero.le_flaps` | bool | – | or | False | False | Leading-edge (droop/Krueger) flaps as a wing device. | 01 |
| `aero.blown_flaps` | bool | – | or | False | False | Boundary-layer-control blown flaps (needs engine bleed). | 01, 02 |
| `aero.fowler_flaps` | bool | – | or | False | True | Fowler flaps device. | 01 |
| `aero.all_moving_tail` | bool | – | or | False | False | All-flying horizontal tail; required for controllability above M≈0.95 (06 flaw `transonic_control_loss` otherwise). | 01, 06 |
| `aero.t_tail` | bool | – | or | False | True | T-tail permitted (06 deep-stall/pitch-up risk handled there). | 01, 06 |
| `aero.inlet_spike` | bool | – | or | False | False | Fixed supersonic cone/half-cone inlet (pressure recovery above M1.4). | 01, 02 |
| `aero.inlet_variable` | bool | – | or | False | False | Variable-geometry inlet (ramps/translating spike). | 01, 02 |
| `aero.inlet_pressure_recovery_bonus` | float | ratio (additive to π_d) | add | 0.0 | 0.0 | Additive bonus to inlet total-pressure recovery from duct design know-how (boundary-layer splitters, bleed). | 01, 02 |
| `aero.drag_skin_factor` | float | multiplier on CD0 friction part | mul | 1.0 | 1.0 | Aero refinement of excrescences (separate from `mfg.surface_finish_factor`). | 01 |

### 2.2 Structures & materials (`struct.*`)

| key | type | unit | agg | null | start | meaning | consumer |
|---|---|---|---|---|---|---|---|
| `struct.weight_factor` | float | multiplier on structural mass | mul | 1.0 | 1.0 | Structural efficiency (alloys, integral machining, honeycomb, analysis methods). | 01 |
| `struct.material.al7075_available` | bool | – | or | False | True | 7075-T6 aluminium usable (higher strength; baseline in 1945). | 01 |
| `struct.material.titanium_available` | bool | – | or | False | False | Titanium may appear in `structure.material_mix.ti`. | 01, 04 |
| `struct.material.ti_max_fraction` | float | mass fraction of structure | max | 0.0 | 0.0 | Max allowed `material_mix.ti`. | 01, 08 |
| `struct.material.steel_max_fraction` | float | mass fraction | max | 0.25 | 0.25 | Max allowed `material_mix.steel` (high-strength steel for hot/strong parts). | 01, 08 |
| `struct.max_skin_temp_K` | float | K | max | 395 | 410 | Max sustained skin/recovery temperature of the primary structure. 01 converts to a thermal Mach limit (Al ≈ M2.1 in stratosphere). Value raised by Ti/steel fractions per 01 formula; this key is the material-system cap. | 01 |
| `struct.honeycomb` | bool | – | or | False | False | Bonded honeycomb sandwich panels (weight factor applied via its tech's `struct.weight_factor`). | 01, 04 |
| `struct.design_load_max_g` | float | g | max | 7.33 | 8.0 | Max design limit load factor allowed in `structure.design_load_factor_g`. | 01, 08 |
| `struct.carrier_weight_factor` | float | multiplier on carrier-suitability mass penalty | mul | 1.0 | 1.0 | Navalisation know-how (folding wings, arrestor structure). | 01 |

### 2.3 Propulsion (`engine.*`) — frontier for module 02

| key | type | unit | agg | null | start | meaning | consumer |
|---|---|---|---|---|---|---|---|
| `engine.centrifugal_compressor` | bool | – | or | False | True | Centrifugal-compressor turbojets designable. | 02 |
| `engine.axial_compressor` | bool | – | or | False | True | Axial-compressor turbojets designable (immature at start). | 02 |
| `engine.twin_spool` | bool | – | or | False | False | Two-spool compressors (J57-class). | 02 |
| `engine.variable_stators` | bool | – | or | False | False | Variable stator vanes (J79-class single spool, high OPR). | 02 |
| `engine.afterburner` | bool | – | or | False | False | Afterburner + variable nozzle allowed. | 02, 01 |
| `engine.afterburner_temp_max_K` | float | K | max | 0 | 0 | Max afterburner exit total temperature (0 = no AB). | 02 |
| `engine.low_bypass_turbofan` | bool | – | or | False | False | Low-bypass (mixed) turbofans designable. | 02 |
| `engine.bypass_ratio_max` | float | – | max | 0.0 | 0.0 | Max bypass ratio. | 02 |
| `engine.tit_max_K` | float | K | max | 1050 | 1090 | Max turbine inlet total temperature. | 02 |
| `engine.cooled_turbine_blades` | bool | – | or | False | False | Air-cooled HP turbine blades (02 applies cooling-bleed penalty). | 02 |
| `engine.opr_max` | float | – | max | 4.0 | 5.0 | Max overall pressure ratio, ANY architecture (02 further limits single-spool fixed-stator designs by `engine.opr_max_single_spool_fixed`). | 02 |
| `engine.opr_max_single_spool_fixed` | float | – | max | 4.0 | 5.0 | Max OPR for single-spool, fixed-stator axial compressors. | 02 |
| `engine.eta_compressor_poly` | float | – | max | 0.80 | 0.83 | Best attainable compressor polytropic efficiency. | 02 |
| `engine.eta_turbine_poly` | float | – | max | 0.83 | 0.86 | Best attainable turbine polytropic efficiency. | 02 |
| `engine.mass_flow_max_kgps` | float | kg/s | max | 30 | 40 | Largest core airflow (engine size) the industry can build. | 02 |
| `engine.specific_weight_factor` | float | multiplier on engine mass | mul | 1.0 | 1.0 | Engine structural/material efficiency. | 02 |
| `engine.mtbf_factor` | float | multiplier on MTBF | mul | 1.0 | 1.0 | Reliability know-how (>1 better). | 02, 04 |
| `engine.dev_cost_factor` | float | multiplier on engine R&D cost | mul | 1.0 | 1.0 | Engine development methods (component rigs, altitude test cells). | 02 |
| `engine.dev_risk_factor` | float | multiplier on engine R&D shortfall sigma | mul | 1.0 | 1.0 | Same; lowers risk of missing thrust/TSFC targets. | 02 |

### 2.4 Avionics & systems (`avionics.*`, `systems.*`)

| key | type | unit | agg | null | start | meaning | consumer |
|---|---|---|---|---|---|---|---|
| `avionics.radar_search` | bool | – | or | False | True | Airborne-intercept search radar may be installed (requires a radar component unlock too). | 01, 05 |
| `avionics.radar_mass_factor` | float | multiplier on radar/FCS mass | mul | 1.0 | 1.0 | Miniaturisation (transistors, printed circuits). | 01 |
| `avionics.radar_range_factor` | float | multiplier on catalogue detection range | mul | 1.0 | 1.0 | Generic signal-processing improvements applied to all radars. | 05, (war later) |
| `avionics.reliability_factor` | float | multiplier on avionics MTBF | mul | 1.0 | 1.0 | >1 better. | 04, 06 |
| `avionics.lead_collision_fcs` | bool | – | or | False | False | Lead-collision (rocket) fire control allowed (E-4/E-5 class). | 05 |
| `avionics.datalink_ground` | bool | – | or | False | False | Ground-controlled-intercept datalink (SAGE-compatible). | 05 |
| `avionics.irst` | bool | – | or | False | False | Infra-red search & track sensor allowed. | 05 |
| `avionics.level_max` | int | 0..5 | max | 0 | 1 | Max `systems.avionics_level` in `AircraftDesign` (0 basic VFR, 1 radio nav+gyro sight, 2 radar ranging, 3 AI radar+lead-pursuit, 4 lead-collision+autopilot, 5 integrated automatic FCS). | 01, 05 |
| `systems.powered_controls` | bool | – | or | False | False | Hydraulic irreversible flight controls. Without: 06 raises `control_heaviness` and `aileron_reversal` risk above M0.85. | 06, 01 |
| `systems.stability_augmentation` | bool | – | or | False | False | Yaw/pitch dampers. Without: 06 raises `inertia_coupling` & `dutch_roll` risk. | 06 |
| `systems.ejection_seat` | bool | – | or | False | False | Ejection seat installable (05 criterion from ~1947; 06 pilot survival). | 05, 06 |
| `systems.inflight_refuel` | bool | – | or | False | False | Probe/receptacle for air refuelling. 01 adds mass; 05 may require. | 01, 05 |
| `systems.pressurized_cockpit` | bool | – | or | False | True | Pressurised cockpit. | 01, 05 |

### 2.5 Armament (`armament.*`, `unlock.*`)

| key | type | unit | agg | null | start | meaning | consumer |
|---|---|---|---|---|---|---|---|
| `armament.internal_bay` | bool | – | or | False | False | Internal missile/rocket bay allowed. | 01, 05 |
| `armament.hardpoints_max` | int | count | max | 2 | 6 | Max `armament.hardpoints`. | 01, 08 |
| `armament.missile_ir_gen` | int | generation 0..5 | max | 0 | 0 | Best IR-guided AAM generation available (1 = AIM-9B/GAR-2 class). | 05, (war) |
| `armament.missile_sarh_gen` | int | generation 0..5 | max | 0 | 0 | Best semi-active radar AAM generation (1 = GAR-1/AIM-4 class, 2 = Sparrow III). | 05, (war) |
| `armament.missile_beamrider` | bool | – | or | False | False | Beam-riding AAM (Sparrow I). | 05 |
| `armament.nuclear_aam` | bool | – | or | False | False | Unguided nuclear air-to-air rocket (Genie). | 05 |
| `armament.nuclear_delivery` | bool | – | or | False | False | Fighter-bomber nuclear store delivery (LABS toss). | 05 |
| `unlock.gun.<id>` | bool | – | or | False | see catalog | Gun component available. MVP ids: `an_m2_50`, `m3_50`, `an_m3_20mm`(Hispano, Navy), `m24_20mm`, `m39_20mm`, `mk12_20mm`, `m61_20mm`. | 01, 05 |
| `unlock.rocket.<id>` | bool | – | or | False | see catalog | `hvar_5in`, `ffar_2_75in`. | 01, 05 |
| `unlock.missile.<id>` | bool | – | or | False | – | `aim4a_falcon`, `aim4c_falcon`, `aim9b_sidewinder`, `aim7a_sparrow1`, `aim7c_sparrow3`, `air2a_genie`, `aim26a_nuclear_falcon`. | 01, 05 |
| `unlock.radar.<id>` | bool | – | or | False | see catalog | `scr720`, `apg5`, `aps19`, `apg30`, `apg33`, `apg37`, `apg40`, `aps21`, `apq50`, `mg10`, `ma1`, `apq72`. | 01, 05 |

Start set of component unlocks: `an_m2_50`, `an_m3_20mm`, `hvar_5in`, `scr720`, `apg5`.

### 2.6 Testing infrastructure & knowledge (`testing.*`) — consumed by 06

| key | type | unit | agg | null | start | meaning | consumer |
|---|---|---|---|---|---|---|---|
| `testing.transonic_tunnel` | bool | – | or | False | False | Slotted-throat transonic tunnel testing available (own tunnel per 04 `wind_tunnel_level` OR NACA access). Without it tunnel results in M0.85–1.2 band are NOT available (06 reports "choked"). | 06 |
| `testing.supersonic_tunnel` | bool | – | or | False | True | Supersonic tunnel testing (M>1.2) available. | 06 |
| `testing.rocket_model_testing` | bool | – | or | False | False | Rocket-boosted free-flight models (NACA Wallops style): expensive transonic data before slotted tunnels. | 06 |
| `testing.sim_sigma_factor` | float | multiplier on "sim" source sigma | mul | 1.0 | 1.0 | Better analytic methods / computers shrink design-estimate sigma (<1 better). | 06 |
| `testing.tunnel_sigma_factor` | float | multiplier on "tunnel" source sigma | mul | 1.0 | 1.0 | Tunnel correction methods & instrumentation (<1 better). | 06 |
| `testing.flight_sigma_factor` | float | multiplier on "flight" source sigma | mul | 1.0 | 1.0 | Flight-test instrumentation/telemetry (<1 better). | 06 |
| `testing.sim_time_factor` | float | multiplier on sim turnaround days | mul | 1.0 | 1.0 | Digital computers (<1 faster). | 06 |
| `testing.flight_test_time_factor` | float | multiplier on flight-test calendar days | mul | 1.0 | 1.0 | Telemetry, chase/instrumentation practice. | 06 |
| `testing.flaw_detect_factor` | float | multiplier on all detect_prob_by_source | mul | 1.0 | 1.0 | >1 better; result clamped to ≤0.99 by 06. | 06 |
| `testing.flaw_incidence.<family>` | float | multiplier on base probability that a flaw of that family is generated | mul | 1.0 | 1.0 | Knowledge that prevents the flaw at design time (<1 better). Families (06 must map its flaw types onto these): `flutter`, `aileron_reversal`, `transonic_control_loss`, `pitch_up`, `inertia_coupling`, `spin`, `inlet`, `engine_stall`, `structural_fatigue`, `systems`, `manufacturing`. | 06 |

### 2.7 Manufacturing (`mfg.*`) — consumed by 04 (and 01 for drag)

| key | type | unit | agg | null | start | meaning | consumer |
|---|---|---|---|---|---|---|---|
| `mfg.labor_hours_factor` | float | multiplier on production labour hours/unit | mul | 1.0 | 1.0 | Tooling, power tools, NC machining. | 04 |
| `mfg.learning_curve_rate` | float | Wright learning-curve rate (labour per unit ×rate per doubling) | min | 0.85 | 0.80 | Lower = faster learning. | 04 |
| `mfg.tooling_cost_factor` | float | multiplier on tooling cost | mul | 1.0 | 1.0 | | 04 |
| `mfg.material_cost_factor` | float | multiplier on raw material cost | mul | 1.0 | 1.0 | | 04 |
| `mfg.titanium_cost_factor` | float | multiplier on titanium $/kg vs. its first-availability price | mul | 1.0 | 1.0 | Ti sponge/forming maturity. | 04 |
| `mfg.surface_finish_factor` | float | multiplier on skin-friction drag | mul | 1.0 | 1.0 | Flush riveting, bonded/integral skins (<1 better). | 01 |
| `mfg.quality_defect_factor` | float | multiplier on production-defect flaw incidence | mul | 1.0 | 1.0 | QC/statistical process control (<1 better). | 06, 04 |
| `mfg.nc_machining` | bool | – | or | False | False | Numerically controlled machining (enables integral-skin techs; 04 capex). | 04 |

### 2.8 Research meta (`research.*`) — consumed by 03 itself

| key | type | unit | agg | null | start | meaning | consumer |
|---|---|---|---|---|---|---|---|
| `research.speed_factor.aero` | float | multiplier on research progress rate in discipline | mul | 1.0 | 1.0 | e.g. digital computers speed aero/structures research. | 03 |
| `research.speed_factor.structures` | float | ″ | mul | 1.0 | 1.0 | | 03 |
| `research.speed_factor.propulsion` | float | ″ | mul | 1.0 | 1.0 | | 03 |
| `research.speed_factor.systems` | float | ″ | mul | 1.0 | 1.0 | | 03 |

## 3. Rules for adding keys
1. Only module 03 adds keys (other modules: change request in your spec §11).
2. New key = new row here + entry in `effect_keys.json` + golden update. Never reuse or rename a key; deprecate with `"deprecated": true` and keep it in the context.
3. Every key MUST have at least one consumer listed.
