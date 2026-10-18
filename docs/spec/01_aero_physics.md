# 01 — Atmosphere, Aerodynamics, Mass, and Performance Specification

> Status: v1.0 (MVP Ticket-Ready). Owner: Module 01 (`mic.atmosphere`, `mic.aero`, `mic.perf`).
> Conforms to: `docs/spec/00_conventions.md` (§3 SI units, §4.2 `AircraftDesign`, §4.4 `PerformanceReport`, §6 Spec Template) and `docs/spec/03_tech_effect_keys.md` (§2.1 `aero.*`, §2.2 `struct.*`, §2.4 `avionics.*`/`systems.*`, §2.5 `armament.*`, §2.7 `mfg.*`).
> Reference Implementation: `sim/mic/atmosphere.py`, `sim/mic/aero/`, `sim/mic/perf/`.
> Calibration Report: `docs/validation/aero_calibration.md`.

---

## 1. Purpose & Player Fantasy

Module 01 is the physical core of *Military-Industrial Complex: Jet Age*. The player is not filling out spreadsheet stats; they are shaping an aircraft—choosing wing area, aspect ratio, quarter-chord sweep, taper ratio, root/tip thickness-to-chord, airfoil section (NACA 4/5/6-series, biconvex, or custom CST spline), fuselage fineness and Whitcomb area-ruling, empennage layout, intake geometry, structural load factor, material mix, fuel fraction, and ordnance—and watching realistic aerodynamic and weight trade-offs emerge immediately.

### 1.1 Core Engineering Trade-Offs (Why Design Is Fun)
1. **Quarter-Chord Sweep ($\Lambda_{c/4}$) & Thickness ($t/c$) vs. Low-Speed Handling & Weight**:
   - Increasing $\Lambda_{c/4}$ and reducing $t/c$ raise the Korn drag-divergence Mach number $M_{dd}$ and lower supersonic wave drag $\Delta C_{D,w}$, enabling transonic and supersonic flight.
   - However, high sweep and thin wings penalize subsonic lift-curve slope $C_{L\alpha}$ and clean $C_{L,\max}$, increase landing/stall speed ($V_{\text{stall}}$), inflate wing structural weight ($\propto \cos^{-0.95}\Lambda \cdot (t/c)^{-0.35}$), shrink internal wing fuel volume, and push the wing across the **Shortal–Maggin pitch-up boundary** and **aeroelastic aileron-reversal/flutter thresholds** (fed into Module 06 via `aero_diagnostics`).
2. **Whitcomb Transonic Area Rule (`fuselage.area_ruled`) & Fuselage Fineness ($L/D_{\max}$)**:
   - A stubby, non-area-ruled delta (`YF-102`, $E_{WD} \approx 2.13$) hits a brick wall at $M \approx 0.98$ where transonic wave drag exceeds J57 afterburning thrust. Lengthening the fuselage and applying "Coke-bottle" waisting (`F-102A`, $E_{WD} \approx 1.38$) cuts peak wave drag by $35\%$, allowing the same engine to accelerate smoothly to $M = 1.25$.
3. **Wing Loading ($W/S$) & Aspect Ratio ($AR$)**:
   - Low $W/S$ and moderate $AR$ yield tight instantaneous/sustained turn rates and low carrier approach speeds (`F4D-1`, `F8U-1`), but suffer higher high-speed skin-friction/wave drag (`CD0`, wetted area). High $W/S$ (`F-104A`) excels in high-speed dash and climb but struggles in low-speed turn radius and takeoff/landing roll unless rescued by boundary-layer-control blown flaps (`aero.blown_flaps`).
4. **Inlet Architecture (`pitot` vs. `fixed_spike` vs. `variable_ramp`)**:
   - Simple normal-shock pitot intakes (`F-86`, `F-100`) have high subsonic recovery ($\pi_d \approx 0.975$) and low weight/cost, but lose total pressure rapidly above $M 1.4$ via Rankine–Hugoniot normal shock losses. Fixed shock spikes (`F-104A`) and variable-ramp inlets (`F-105B`, `F-4`) preserve thrust at $M 2.0+$ at the cost of weight, maintenance hours, and inlet-buzz/distortion risks.

---

## 2. Scope

### 2.1 In Scope for MVP (US 1945–1960)
- **Atmosphere**: ISA 1976 (`0–25 km`: troposphere $0\text{–}11\text{ km}$ and lower stratosphere $11\text{–}20\text{ km}$, plus $20\text{–}25\text{ km}$ warming layer).
- **2D Airfoil Module (`mic.aero.airfoil`)**: NACA 4-digit, NACA 5-digit, NACA 6/6A-series, symmetric biconvex, and 8-parameter Kulfan CST (Class-Shape Transformation) + least-squares spline-to-CST fitting for free-drawn airfoils. Computes $t/c$, camber, leading-edge radius $r_{LE}/c$, Inviscid/Viscous $C_{l\alpha}$, $C_{l,\max}$, $C_{m,0}$, Korn $\kappa_A$, and 2D $M_{dd}$.
- **3D Wing Lifting-Surface & VLM Solver (`mic.aero.vlm`)**: 16-spanwise horseshoe-vortex Weissinger/VLM lifting-line solver + Polhamus leading-edge suction analogy for slender deltas ($AR < 3.2$) + Prandtl–Glauert / Helmbold–Diederich / Ackeret compressibility scaling across Mach regimes.
- **Component Drag Buildup & Sears–Haack Wave Drag (`mic.aero.drag`)**: Turbulent/laminar flat-plate skin friction with compressibility factor, component form factors, Lock 4th-power transonic drag rise between $M_{\text{crit}}$ and $M_{dd}$, 64-station longitudinal cross-sectional area distribution $A(x)$ numerical integration for Sears–Haack wave drag $D_w/q$ and empirical Whitcomb area-rule efficiency factor $E_{WD}$, and high-lift flap/slat/BLC increments.
- **Statistical Component Mass Breakdown (`mic.aero.mass`)**: Adapted Raymer/Roskam fighter weight equations calibrated to 1945–1960 US/Soviet jets, material mix (`al`, `steel`, `ti`), structural tech factor (`struct.weight_factor`), and geometric fuel tank volume capacity validation.
- **Performance & Mission Integrator (`mic.perf.performance`)**: Level-flight speed solver with continuous acceleration check and thermal/dynamic-pressure limits, $13 \times 10$ Boyd Specific Excess Power ($P_s$) grid, sustained & instantaneous turn rates at $M 0.8, 15,000\text{ ft}$, Rutowski energy-climb schedule, multi-segment Breguet combat radius & ferry range, takeoff/landing/carrier suitability, and `aero_diagnostics` for Module 06.

### 2.2 Out of Scope for MVP (Deferred to Later Phases)
- 6-DOF real-time flight simulation (handled in Phase 6 via JSBSim export).
- Radar cross-section (RCS) shaping & stealth wave-scattering (Phase 3: 1990–2030).

---

## 3. Player-Facing Flow

1. **Geometry & Configuration Editing**: Player adjusts sliders or presets in the Design Bureau UI (`08_ui_ux.md`). Every parameter change validates against `TechContext` caps (`validate_design`) and recomputes `evaluate(design, engine, tech_context)` in $<10\text{ ms}$.
2. **Real-Time Engineering Charts**:
   - **3-View Blueprint & Cross-Sectional Area Curve $A(x)$**: Shows wing/fuselage/tail/nacelle cross-sectional area vs. axial station $x/L$ alongside the ideal Sears–Haack bell curve. Spikes/bumps in $A''(x)$ visually explain high $E_{WD}$.
   - **Drag Polar & Mach Drag-Rise Curve**: Plots $C_{D0}(M)$ and $(L/D)(M)$ from $M 0.3$ to $M 2.4$.
   - **Boyd $P_s$ Envelope Contour (`ps_grid`)**: Plots $1g$ Specific Excess Power contours over Altitude vs. Mach, showing the $P_s = 0$ level-flight envelope, thermal limit line, and $q_{\max}$ structural boundary.
3. **Uncertainty Wrapping**: When viewed in the Design Bureau before testing, Module 06 wraps the raw deterministic `PerformanceReport` into `Estimate(value, sigma, source="sim")`.

---

## 4. Data Schemas

### 4.1 `AircraftDesign` Complete Schema (`00_conventions.md` §4.2)

```json
{
  "id": "f100a_super_sabre",
  "name": "North American F-100A Super Sabre",
  "company_id": "north_american",
  "created_date": "1951-11-01",
  "crew_count": 1,
  "role_tags": ["day_fighter"],
  "wing": {
    "area_m2": 35.77,
    "aspect_ratio": 3.86,
    "sweep_qc_deg": 45.0,
    "taper_ratio": 0.26,
    "tc_root": 0.070,
    "tc_tip": 0.070,
    "airfoil_ref": "64A007",
    "planform_type": "conventional",
    "position": "low",
    "x_le_root_frac": 0.31,
    "dihedral_deg": 0.0,
    "incidence_deg": 0.5,
    "twist_deg": -1.5,
    "devices": ["slotted_flaps", "le_slats"]
  },
  "fuselage": {
    "length_m": 14.33,
    "max_diameter_m": 1.62,
    "nose_fineness": 2.8,
    "tail_fineness": 3.0,
    "canopy_type": "bubble",
    "area_ruled": false
  },
  "empennage": {
    "tailless": false,
    "t_tail": false,
    "all_moving_tail": true,
    "ht_area_m2": 6.40,
    "ht_aspect_ratio": 3.5,
    "ht_sweep_qc_deg": 45.0,
    "vt_area_m2": 4.10,
    "vt_aspect_ratio": 1.4,
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
    "x_cg_frac": 0.58
  },
  "structure": {
    "design_load_factor_g": 7.33,
    "material_mix": { "al": 0.80, "steel": 0.13, "ti": 0.07 },
    "carrier_capable": false
  },
  "fuel": {
    "internal_kg": 2290.0,
    "drop_tanks_count": 2,
    "drop_tank_fuel_kg_each": 620.0,
    "combat_uses_drop_tanks": true
  },
  "systems": {
    "radar_id": "apg30",
    "fire_control_id": null,
    "avionics_level": 2,
    "powered_controls": true,
    "stability_augmentation": true,
    "ejection_seat": true,
    "inflight_refuel": false,
    "pressurized_cockpit": true
  },
  "armament": {
    "guns": [{ "gun_id": "m39_20mm", "count": 4, "rounds_per_gun": 200 }],
    "hardpoints": 4,
    "internal_bay": false,
    "missile_ids": []
  },
  "techs_used": []
}
```

### 4.2 Field Ranges, Units & Defaults (`sim/mic/aero/geometry.py`)

| Sub-object & Field | Type | Unit | Allowed Range | Default | Tech Cap Key |
|---|---|---|---:|---:|---|
| `wing.area_m2` | float | $\text{m}^2$ | $[8.0, 120.0]$ | `25.0` | — |
| `wing.aspect_ratio` | float | — | $[1.4, 12.0]$ | `4.5` | `aero.aspect_ratio_min` (for conventional) |
| `wing.sweep_qc_deg` | float | deg | $[-25.0, 75.0]$ | `0.0` | `aero.wing_sweep_max_deg` |
| `wing.taper_ratio` | float | — | $[0.02, 1.00]$ | `0.45` | — |
| `wing.tc_root`, `tc_tip` | float | ratio | $[0.025, 0.220]$ | `0.10`, `0.09` | `aero.thin_wing_tc_min` |
| `wing.planform_type` | enum | — | `conventional\|delta\|variable_sweep` | `conventional` | `aero.delta_wing`, `aero.variable_sweep` |
| `wing.position` | enum | — | `low\|mid\|high` | `mid` | — |
| `wing.devices[]` | list | — | `plain_flaps`, `slotted_flaps`, `fowler_flaps`, `blown_flaps`, `le_slats`, `le_flaps` | `["slotted_flaps"]` | `aero.fowler_flaps`, `aero.blown_flaps`, `aero.le_slats`, `aero.le_flaps` |
| `fuselage.length_m` | float | m | $[6.0, 32.0]$ | `12.0` | — |
| `fuselage.max_diameter_m` | float | m | $[0.70, 3.20]$ | `1.35` | — |
| `fuselage.area_ruled` | bool | — | `true\|false` | `false` | `aero.area_rule` |
| `empennage.t_tail` | bool | — | `true\|false` | `false` | `aero.t_tail` |
| `empennage.all_moving_tail` | bool | — | `true\|false` | `false` | `aero.all_moving_tail` |
| `intake.type` | enum | — | `nose\|chin\|cheek\|wing_root` | `nose` | — |
| `intake.compression` | enum | — | `pitot\|fixed_spike\|variable_ramp` | `pitot` | `aero.inlet_spike`, `aero.inlet_variable` |
| `structure.design_load_factor_g` | float | $g$ | $[4.0, 10.0]$ | `7.33` | `struct.design_load_max_g` |
| `structure.material_mix.{al,steel,ti}` | float | fraction | sum $= 1.0$ | `0.90/0.10/0.0` | `struct.material.ti_max_fraction`, `steel_max_fraction` |

---

## 5. Algorithms & Exact Formulas

### 5.1 International Standard Atmosphere (`sim/mic/atmosphere.py`)
- Constants: $g_0 = 9.80665\text{ m/s}^2$, $R = 287.05287\text{ J/(kg}\cdot\text{K)}$, $\gamma = 1.4$, $T_0 = 288.15\text{ K}$, $p_0 = 101325.0\text{ Pa}$, $\rho_0 = 1.2250\text{ kg/m}^3$.
- Layer 1 ($0 \le h \le 11000\text{ m}$): $L_1 = -0.0065\text{ K/m}$, $T(h) = T_0 + L_1 h$, $p(h) = p_0 (T(h)/T_0)^{-g_0/(R L_1)}$.
- Layer 2 ($11000 < h \le 20000\text{ m}$): isothermal $T = 216.65\text{ K}$, $p(h) = p_{11} \exp(-g_0 (h - 11000)/(R \cdot 216.65))$.
- Layer 3 ($20000 < h \le 25000\text{ m}$): $L_3 = +0.0010\text{ K/m}$, $T(h) = 216.65 + L_3 (h - 20000)$.
- Sutherland viscosity: $\mu(T) = 1.458\times 10^{-6} T^{1.5} / (T + 110.4)$.
- Adiabatic wall recovery temperature: $T_r = T(h) \cdot (1 + r \frac{\gamma - 1}{2} M^2)$ with turbulent recovery factor $r = 0.89$.

### 5.2 2D Airfoil Analysis (`sim/mic/aero/airfoil.py`)
- Supports NACA 4-digit (`0010`, `2412`), 5-digit (`23012`), 6/6A-series (`64-009`, `64A007`, `65-006`), symmetric biconvex (`biconvex_00336` for `F-104A`), and 8-weight Kulfan CST (`upper_weights[4]`, `lower_weights[4]` with class function $C(\psi) = \psi^{0.5}(1-\psi)^{1.0}$ and Bernstein polynomials of degree 3).
- Thin-airfoil + thickness/viscosity corrected 2D lift slope:
  $$C_{l\alpha,0} = 2\pi \cdot \eta_{\text{visc}} \cdot (1 + 0.77 (t/c) \cdot e^{-8(t/c)}), \quad \eta_{\text{visc}} = 0.955$$
- 2D clean maximum lift coefficient $C_{l,\max,0}$ depends on leading-edge sharpness parameter $\Delta y$ (Raymer §12.4):
  $$C_{l,\max,0} = \text{clip}\!\left(0.68 + 7.2 \min(t/c, 0.12) + 8.5 z_{c,\max} - 3.5 \max(t/c - 0.125, 0),\, 0.62,\, 1.68\right)$$
- 2D Korn drag-divergence Mach number at zero lift:
  $$M_{dd,0} = \kappa_A - (t/c) - 0.10 C_{l,\text{design}}$$
  where $\kappa_A = 0.87$ (NACA 4), $0.88$ (NACA 5), $0.90$ (NACA 6/6A), $0.91$ (biconvex).

### 5.3 3D Wing VLM & Compressibility (`sim/mic/aero/vlm.py`)
- Discretizes the half-span into $N = 16$ cosine-spaced horseshoe vortex panels along the $c/4$ line with collocation points at $3c/4$ (Pistolesi theorem), solving the $16 \times 16$ Biot–Savart influence matrix $[A]\{\Gamma\} = \{V_\infty \alpha\}$ for spanwise circulation, inviscid Oswald factor $e_{\text{inv}}$, downwash at the horizontal tail $\partial\epsilon/\partial\alpha$, and subsonic aerodynamic center $x_{ac}/c_{\text{mac}}$.
- **Subsonic Compressibility ($M < 0.95$)**: Helmbold–Diederich swept lifting-surface equation:
  $$C_{L\alpha}(M) = \frac{2\pi AR}{2 + \sqrt{\frac{AR^2 \beta_n^2}{\kappa^2}\left(1 + \frac{\tan^2\Lambda_{c/2}}{\beta_n^2}\right) + 4}}, \quad \beta_n = \sqrt{1 - M_{\text{eff}}^2 \cos^2\Lambda_{c/4}}$$
- **Supersonic Regime ($M \ge 1.15$)**: Linearized Ackeret / supersonic-leading-edge theory with subsonic-LE cone correction when $M \cos\Lambda_{LE} < 1$:
  $$C_{L\alpha,\text{sup}}(M) = \frac{4}{\beta}\left(1 - \frac{1}{2 AR \beta}\right) \cdot f_{\text{sub-LE}}(M \cos\Lambda_{LE}), \quad \beta = \sqrt{M^2 - 1}$$
- **Transonic Cubic Hermite Bridge ($0.95 < M < 1.15$)**: Smooth $C^1$ interpolation between $M=0.95$ and $M=1.15$.

### 5.4 Component Drag Buildup & Wave Drag (`sim/mic/aero/drag.py`)
- **Zero-Lift Parasite Drag $C_{D0,\text{sub}}(M, h)$**:
  $$C_{D0,\text{sub}} = \frac{\sum_c C_{f,c}(Re_c, M) \cdot FF_c \cdot Q_c \cdot S_{\text{wet},c} + (D/q)_{\text{canopy}} + (D/q)_{\text{diverter}} + (D/q)_{\text{stores}}}{S_{\text{ref}}} \cdot f_{\text{excres}} \cdot f_{\text{tech}}$$
  where $C_{f,\text{turb}} = \frac{0.455}{(\log_{10} Re_{\text{eff}})^{2.58} (1 + 0.144 M^2)^{0.65}}$ (Raymer Eq. 12.27) and $f_{\text{tech}} = \texttt{aero.drag\_skin\_factor} \times \texttt{mfg.surface\_finish\_factor}$.
- **Sears–Haack Wave Drag & Whitcomb Area Rule (`compute_wave_drag_summary`)**:
  Evaluates the 64-station axial cross-sectional area distribution $A(x) = A_{\text{fus}}(x) + A_{\text{wing}}(x) + A_{\text{tail}}(x) + A_{\text{canopy}}(x) - A_{\text{capture}}$:
  $$\left(\frac{D}{q}\right)_{\text{SH}} = \frac{9\pi}{2}\left(\frac{A_{\max}}{L_{\text{eff}}}\right)^2, \quad C_{D,w,\max} = c_{\text{wave}} \cdot E_{WD} \cdot \frac{(D/q)_{\text{SH}}}{S_{\text{ref}}} \cdot \left(\frac{t/c_{\text{mean}}}{0.06}\right)^{0.22}$$
  Without area ruling (`area_ruled = False`), $E_{WD} \in [1.55, 2.35]$ depending on the dimensionless second-derivative roughness integral $\int (A''(x))^2 dx$ and fuselage bluntness; with area ruling (`area_ruled = True`), waisting reduces the wing-fuselage bump by `area_rule_waisting_gain * aero.wave_drag_area_rule_eff`, lowering $E_{WD}$ into $[1.18, 1.45]$.
- **3D Swept Korn Drag-Divergence Mach Number**:
  $$M_{dd}(C_L) = \frac{\kappa_A}{\cos^\nu\Lambda_{\text{eff}}} - \frac{t/c_{\text{mean}}}{\cos^{1.15}\Lambda_{\text{eff}}} - \frac{0.10 C_L}{\cos^{1.2}\Lambda_{\text{eff}}}, \quad M_{\text{crit}} = M_{dd} - 0.108$$
- **Induced & Wave Drag Due to Lift $K(M)$**:
  - Subsonic: $K_{\text{sub}} = \frac{1}{\pi AR e_{\text{oswald}}}$, modified by `aero.conical_camber` ($-8\%$).
  - Supersonic: Raymer Eq. 12.49 $K_{\text{sup}}(M) = \frac{AR(M^2 - 1)\cos\Lambda_{LE}}{4 AR \sqrt{M^2 - 1} - 2}$.

### 5.5 Component Mass Breakdown (`sim/mic/aero/mass.py`)
Solves fixed-point iteration ($6$ iterations) on design gross weight $W_{dg}$ using adapted Raymer Chapter 15 fighter equations (`wing_kg`, `fuselage_kg`, `tail_kg`, `landing_gear_kg`, `propulsion_group_kg`, `flight_controls_hydraulics_kg`, `avionics_and_radar_kg`, `electrical_pneumatic_env_kg`, `furnishings_and_ejection_kg`, `armament_fixed_dry_kg`), scaled by:
- Material weight factor: $f_{\text{mat}} = 1.00 f_{\text{Al}} + 1.14 f_{\text{Steel}} + 0.86 f_{\text{Ti}}$.
- Tech factor: `struct.weight_factor` and `struct.carrier_weight_factor`.
- High-aspect-ratio swept-wing aeroelastic torsion penalty when $AR \cdot \tan\Lambda_{c/4} > 2.2$.

### 5.6 `aero_diagnostics` Dictionary (Consumed by Module 06)
Computed in `sim/mic/aero/diagnostics.py`:
- `shortal_maggin_limit_ar`, `shortal_maggin_excess`: NACA TN 3307 pitch-up boundary $AR_{\text{lim}}(\Lambda_{c/4}, \lambda)$. Positive excess triggers `pitch_up`.
- `t_tail_deep_stall_risk`: High-wake immersion metric for T-tails on swept wings.
- `static_margin_subsonic_mac`, `static_margin_supersonic_mac`, `ac_shift_mac`: Longitudinal stability & transonic Mach tuck driver.
- `m_crit_1g`, `m_dd_1g`, `m_dd`, `mach_dd_excess`: Transonic buffet / control-loss driver.
- `wave_drag_ewd`, `wave_drag_ratio`, `cd_wave_peak`: Area-rule drag-pinch driver.
- `torsion_flex_index`, `q_reversal_margin`: Swept-wing aeroelastic twist & aileron reversal margin.
- `ixx_iyy_ratio`, `inertia_coupling_index`: Phillips roll-inertia coupling index for slender fuselage / low-span fighters (`F-100A`, `F-104A`).
- `spin_susceptibility_index`, `inlet_distortion_risk`: High-AoA spin and compressor-surge drivers.

---

## 6. Tunables Table (`sim/data/tuning/aero.json`)

| Key | Default | Range | Effect | Rationale |
|---|---:|---|---|---|
| `drag.cd0_global_scale` | `0.96` | $[0.85, 1.15]$ | Scales subsonic parasite drag $C_{D0}$ | Calibrated to NASA SP-468 (`P-80A`, `F-86E/F`, `F-104A`) |
| `drag.wave_drag_global_scale` | `0.68` | $[0.50, 1.00]$ | Scales Sears–Haack wave drag | Matches Century-Series Mach $1.2\text{–}2.0$ dash speeds |
| `drag.ewd_baseline_non_area_ruled` | `1.72` | $[1.40, 2.20]$ | Baseline $E_{WD}$ before area ruling | Raymer Table 12.4 fighter baseline |
| `mass.empty_mass_global_scale` | `0.94` | $[0.85, 1.10]$ | Global structural weight calibration | Matches 14 historical 1945–1960 fighters within $3.9\%$ MAPE |
| `mission.warmup_takeoff_fuel_fraction` | `0.050` | $[0.02, 0.08]$ | Fuel burned in ground start/takeoff | MIL-C-5011A standard military mission rules |
| `mission.cruise_part_throttle_sfc_penalty` | `1.28` | $[1.10, 1.45]$ | Altitude/part-power operational TSFC factor | Accounts for formation/navigation cruise vs. test-stand minimum |

---

## 7. Edge Cases & Failure Modes

1. **Transonic "Thrust Island" Prevention**: Underpowered transonic aircraft (`YF-102`) can theoretically have $T > D$ at $M 1.18$ while $T < D$ at $M 0.99$. `_solve_max_mach_at_alt` scans upward continuously from $M 0.55$ and stops at the first Mach where $T - D < 0$, ensuring an aircraft cannot teleport past the transonic wall.
2. **Geometric Tank Overflow (`FUEL_EXCEEDS_VOLUME`)**: `compute_mass_breakdown` calculates maximum geometric wing + fuselage fuel capacity `max_internal_fuel_capacity_kg`; `validate_design` flags designs whose requested `fuel.internal_kg` exceeds available volume.
3. **Engine-Fuselage Diameter Stuffing (`ENGINE_EXCEEDS_FUSELAGE_DIAMETER`)**: Validates that fuselage cross-section accommodates single or side-by-side twin engines (`J57`, `J75`, `VK-1`).
4. **Strict Zero-NaN Guarantee**: Every square root, logarithm, division, and trig function clamps denominators and arguments (`np.maximum`, `np.clip`). Verified over $2,000$ random extreme designs (`0` NaNs/Infs).

---

## 8. Golden Test Vectors & Pytest Suite

- `sim/golden/aero_atmosphere_and_airfoil.json`: ISA properties from $0\text{–}25\text{ km}$ and 2D airfoil metrics across NACA 4/5/6, biconvex, and CST sections.
- `sim/golden/perf_historical_reports.json`: Full deterministic `PerformanceReport`, `mass_breakdown`, and `aero_diagnostics` vectors for `f86f_sabre`, `yf102_pre_area_rule`, `f102a_delta_dagger`, and `f104a_starfighter` (`rel_tol = 1e-6`).
- Pytest suite: `sim/tests/test_aero_perf.py`.

---

## 9. Module Interactions

- **Inputs from Module 02 (`mic.engine`)**: `EngineSpec` deck (`thrust_N`, `tsfc`, `mass_kg`, `diameter_m`, `length_m`, `unit_cost`, `maint_mh_per_fh`).
- **Inputs from Module 03 (`mic.tech`)**: `TechContext` keys (`aero.*`, `struct.*`, `systems.*`, `armament.*`, `mfg.surface_finish_factor`).
- **Inputs from Module 04 (`mic.econ.cost`)**: Called for `unit_flyaway_cost_usd` and `dev_cost_usd_estimate` when available.
- **Outputs to Module 05 (`mic.procurement`)**: `PerformanceReport` metrics evaluated against `Requirement.criteria`.
- **Outputs to Module 06 (`mic.testing`)**: `PerformanceReport` + `aero_diagnostics` dict driving hidden flaw probabilities and `TrueAircraft` perturbations.

---

## 10. Validation Summary (`docs/validation/aero_calibration.md`)

Calibrated across **14 historical fighters (1945–1960)**: `P-80A`, `F-84G`, `F-86A`, `F-86F`, `MiG-15bis`, `F-89D`, `F-100A`, `YF-102 (Pre-Area-Rule)`, `F-102A (Area-Ruled)`, `F-104A`, `F8U-1`, `F4D-1`, `F-101A`, and `F-105B`.
- **Overall MAPE across all 98 aircraft-metric checks**: **$< 5.5\%$** (well within the $\le 10\%$ target).
- **YF-102 vs. F-102A Area-Rule Verification**: `YF-102` predicts $M_{\max} = 1.03$ (vs. $0.98$ published); enabling `area_ruled = True` + lengthened fuselage on `F-102A` predicts $M_{\max} = 1.25$ (vs. $1.25$ published).
- **2,000-Random-Design Sweep**: `0` NaNs/Infs; all geometric/structural exploits caught or penalized.

---

## 11. Open Questions & Cross-Module Change Requests

- **Open Question (Player Taste)**: Should the Design Bureau 3-View & Area-Rule graph display the exact numerical wave-drag efficiency factor $E_{WD}$ from Day 1 (1945), or only unlock the $A(x)$ area-distribution curve overlay once the company unlocks `aero.area_rule` (Whitcomb 1952)?
- **Cross-Module Integration**: Exposes all 7 `aero_diagnostics` keys requested by Module 06 (`shortal_maggin_excess`, `m_dd`, `mach_dd_excess`, `wave_drag_ratio`, `ac_shift_mac`, `inertia_coupling_index`, `torsion_flex_index`).
