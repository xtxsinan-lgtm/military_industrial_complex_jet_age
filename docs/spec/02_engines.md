# 02 — Engine Cycle Model, Deck Generator, Reliability, and Propulsion R&D

> Status: v1.0 (reference oracle implemented in `sim/mic/engine/`, calibrated to $\le 7.34\%$ max error across 12 historical 1945–1960 engines).
> Owner: module 02 (`mic.engine`).
> Dependencies: `00_conventions.md` (§3, §4.3), `03_tech_effect_keys.md` (§2.1 inlet/bleed keys, §2.3 `engine.*` keys).

---

## 1. Purpose & Player Fantasy

In the first fifteen years of the Jet Age (1945–1960), **the engine made or broke the fighter**. North American's F-86F dominated MiG Alley when paired with the mature General Electric J47, while the Republic F-84F suffered years of delays over the Wright J65, and the US Navy's entire early-1950s carrier air wing (F3H-1N Demon, F4D Skyray, XF10F Jaguar, A3D Skywarrior) was crippled by the catastrophic failure of the Westinghouse J40 ($> \$200\text{M}$ lost, four pilots killed, 21 airframes grounded as maintenance trainers). Conversely, Pratt & Whitney's bold bet on the twin-spool J57 and General Electric's variable-stator J79 unlocked the Mach 2 Century Series.

Module 02 turns propulsion into a high-stakes strategic and engineering subsystem with four core trade-offs:

1. **Architecture Trade-Off (Centrifugal vs. Axial Fixed-Stator vs. Twin-Spool vs. Variable-Stator)**:
   - **Centrifugal turbojets** (Allison J33, Klimov VK-1) are light, short, cheap, rugged, resistant to compressor stall, and tolerant of bifurcated cheek/wing-root intakes—but they have a large frontal diameter ($\sim 1.28\text{ m}$), an aerodynamic pressure-ratio ceiling ($\text{OPR} \le 5.0$), and high specific fuel consumption ($\text{SFC} \approx 1.07\text{–}1.15\text{ lb/(lbf}\cdot\text{h)}$).
   - **Single-spool fixed-stator axial turbojets** (Allison J35, GE J47, Wright J65, Allison J71, Tumansky RD-9B) have a slender frontal profile ($\sim 0.80\text{–}1.00\text{ m}$) and lower TSFC, but fixed compressor blade angles lose surge margin rapidly above $\text{OPR} \approx 7.0\text{–}8.0$.
   - **Twin-spool axial turbojets** (P&W J57, J75) split compression across independent LP and HP spools to reach $\text{OPR} = 11.5\text{–}13.0$ with excellent subsonic TSFC ($\sim 0.78\text{ lb/(lbf}\cdot\text{h)}$) and wide stall margin, at the price of $+15\%$ mass, $+25\%$ unit cost, and high mechanical complexity.
   - **Variable-stator (VSV) single-spool axial turbojets** (GE J79) schedule inlet guide vanes and stator rows to achieve twin-spool pressure ratios ($\text{OPR} = 12.5+$) on a single lightweight shaft ($-14\%$ mass vs. fixed-stator equivalent), excelling at Mach 2.0 interceptors.
2. **Cycle Parameter Sizing ($\dot{m}_0$, $\text{OPR}$, $T_{t4}$, $T_{t7}$)**:
   - Raising Turbine Inlet Temperature ($T_{t4}$) boosts specific thrust (shrinking diameter and mass per Newton of thrust) but worsens dry TSFC at moderate OPR and severely degrades hot-section blade life (MTBF) unless `engine.cooled_turbine_blades` is unlocked.
   - Adding an **afterburner** ($T_{t7}$) boosts Sea-Level Static thrust by $25\%\text{–}58\%$ and nearly doubles supersonic thrust at Mach 2.0, but adds $+24\%$ mass, $+1.45\text{–}1.85\text{ m}$ length, $+32\%$ cost, and triples fuel flow when lit.
3. **Procurement Strategy (Catalog vs. Custom Commission vs. In-House Engine Division)**:
   - **Catalog engines** cost $\$0$ upfront R&D and have zero schedule risk and high service maturity (Duane MTBF growth already accumulated), but carry an $18\%$ vendor price markup and force the airframe to wrap around existing dimensions and thrust levels.
   - **Custom commissioned R&D** contracts an external propulsion specialist (Pratt & Whitney, General Electric, Allison, Curtiss-Wright) to develop a bespoke engine tailored to the player's airframe; the player pays $60\%$ of the R&D cost and receives an 18-month exclusivity window.
   - **In-house engine division** requires a $\$35\text{M}$ capital investment and $\$250\text{k/month}$ standing overhead plus $100\%$ of project R&D costs, but eliminates vendor markup on own aircraft and allows the player to **sell or license engines to third-party airframers** for profit and royalties.
4. **Ambition vs. Lead-Time & Failure Risk**:
   - Engine R&D takes **4 to 6 years** for a clean-sheet design—longer than an airframe—forcing players to anticipate future RFPs or use **derivative/uprate projects** ($\sim 32\%$ cost, $\sim 42\%$ duration) to bridge capability gaps. Pushing $\text{OPR}$, $T_{t4}$, and $\dot{m}_0$ simultaneously to the bleeding edge of immature technology risks a J40/J67-style qualification crisis.

---

## 2. Scope

### 2.1 In Scope for MVP (USA, 1945–1960)
- **Thermodynamic cycle solver (`sim/mic/engine/cycle.py`)**: Two-gamma ($\gamma_c, \gamma_t, \gamma_{ab}$) on-design and choked-turbine off-design solver supporting centrifugal, axial fixed-stator, axial VSV, twin-spool, low-bypass mixed turbofan (for late-1950s transition), dry/afterburning operation, turbine cooling bleed, and blown-flap airframe bleed.
- **Inlet total-pressure recovery schedules**: Bellmouth uninstalled test-stand rating, MIL-E-5007D reference, normal-shock pitot, fixed conical spike (`aero.inlet_spike`), variable ramp/spike (`aero.inlet_variable`), and duct location losses (`nose`, `chin`, `cheek`, `wing_root`).
- **Deck generator & interpolator (`sim/mic/engine/deck.py`)**: Precomputes 2D/3D Mach $\times$ Altitude $\times$ Throttle tables (dry and AB) and exposes contract §4.3 (`thrust_N`, `tsfc`, `fuel_flow_kgps`, static fields).
- **Physical sizing, cost, and Duane reliability growth (`sim/mic/engine/sizing.py`)**: Predicts dry mass, max diameter, length, unit cost, initial and mature MTBF (MIL-HDBK-189 Duane growth), and maintenance man-hours per flight hour (`maint_mh_per_fh`).
- **Engine diagnostics (`sim/mic/engine/diagnostics.py`)**: Computes `compressor_surge_margin`, `high_alt_flameout_risk`, `ab_lightoff_reliability`, `intake_compatibility`, `thermal_margin_K`, and Module 06 flaw incidence multipliers.
- **Engine R&D & catalog (`sim/mic/engine/rnd.py`, `catalog.py`)**: Tech-cap validation against all 19 `engine.*` keys in `03_tech_effect_keys.md`, ambition metric $A$, cost/duration/sigma equations, stochastic outcome resolver, derivative projects, engineer priority allocation, third-party sales, and 12 calibrated historical engines (`sim/data/engines_hist/*.json`).

### 2.2 Out of Scope for MVP (System-Design Hooks Only for Later Eras)
- High-bypass separate-exhaust turbofans ($\text{BPR} > 1.5$, post-1968), variable-cycle engines (post-2015), and 2D/3D thrust-vectoring nozzles.
- Detailed transient spool-up time integration (represented via static `compressor_surge_margin` for Module 06 flight testing).
- Water-alcohol injection tankage tracking in `AircraftDesign` (published wet ratings are documented in historical reference metadata; dry/AB decks cover standard combat performance).

---

## 3. Player-Facing Flow

1. **Propulsion Selection in Aircraft Editor (or Standalone Engine Bureau Screen)**:
   - The player chooses between:
     - **Browse Catalog**: Inspect available historical/unlocked engines (`J33-A-35`, `J35-A-29`, `J47-GE-27`, `J65-W-3`, `J57-P-21`, etc.) with known static thrust, TSFC, mass, diameter, length, unit price, and current service MTBF.
     - **Launch New Engine R&D Project**: Open the Parametric Cycle Designer.
     - **Launch Derivative / Uprate Project**: Select an existing qualified engine as `parent_engine` and modify airflow ($\pm 22\%$), OPR, TIT, or add an afterburner.
2. **Parametric Cycle Designer**:
   - Player selects **Architecture**: Compressor type (`centrifugal` or `axial`), spool count (`1` or `2`), `variable_stators` (`bool`), `has_afterburner` (`bool`), `nozzle_type` (`convergent` or `convergent_divergent`), and `cooled_turbine` (`bool`). Unavailable options are greyed out with tooltip `Requires tech: <tech_id>`.
   - Player adjusts four primary sliders clamped to current `TechContext` caps (`03_tech_effect_keys.md` §2.3):
     - **Core Mass Flow $\dot{m}_0$** $[\text{kg/s}]$ (displayed in $\text{lb/s}$ and $\text{kg/s}$, capped by `engine.mass_flow_max_kgps`).
     - **Overall Pressure Ratio $\text{OPR}$** (capped by `engine.opr_max`, or `engine.opr_max_single_spool_fixed` for 1-spool fixed-stator axial, or $5.0$ for centrifugal).
     - **Turbine Inlet Temperature $T_{t4}$** $[\text{K}]$ (displayed in ${}^\circ\text{F} / \text{K}$, capped by `engine.tit_max_K`).
     - **Afterburner Exit Temperature $T_{t7}$** $[\text{K}]$ (if AB enabled, capped by `engine.afterburner_temp_max_K`).
   - As sliders move, the UI updates in real time (<1 ms):
     - **Predicted SLS Performance**: Dry thrust, AB thrust, dry TSFC, AB TSFC, thrust-to-weight ratio.
     - **Predicted Altitude/Mach Envelope**: Thrust and TSFC at $M=0.85, 35\text{k ft}$ and $M=1.6\text{–}2.0, 40\text{k ft}$.
     - **Predicted Envelope Dimensions & Mass**: Dry mass, max diameter, total length, estimated flyaway cost, initial MTBF, and `engine_diagnostics` warnings (e.g., *"Warning: Fixed-stator axial at OPR 7.8 has low surge margin (0.118) — high risk of compressor stall in flight test"*).
     - **R&D Ambition & Risk Meter**: Displays Ambition $A$, estimated total R&D cost and player share, expected duration in months/days, 10th–90th percentile thrust/TSFC outcome bands, and Severe Qualification Crisis probability.
3. **Project Execution & Priority Allocation**:
   - Active engine projects progress daily based on propulsion engineer allocation (`allocate_rnd_priorities`) and monthly cash draw.
4. **Qualification & Outcome Resolution**:
   - Upon reaching 100% progress, `resolve_rnd_outcome` rolls the realized engine specs using the campaign RNG (`00_conventions.md` §3).
   - If a severe qualification flaw occurs (e.g., J40-style compressor surge or turbine blade creep), the player receives an engineering incident report and must choose between accepting the de-rated engine immediately or funding a rectification derivative.

---

## 4. Data Schemas

### 4.1 `EngineDesignInput` (Parametric Cycle & Sizing Input)

| Field | Type | Unit | Range / Allowed | Default | Description |
|---|---|---|---|---|---|
| `engine_id` | `str` | – | snake_case identifier | required | Unique engine ID (e.g. `"j57_p_21"`). |
| `name` | `str` | – | display string | required | Display name (stored in data files per D4). |
| `compressor_type` | `str` | – | `"centrifugal"`, `"axial"` | `"axial"` | Primary compressor architecture. |
| `spools` | `int` | count | `1`, `2` | `1` | Number of concentric compressor/turbine shafts. |
| `variable_stators` | `bool` | – | `true`, `false` | `false` | Variable stator vanes (`engine.variable_stators`). |
| `has_afterburner` | `bool` | – | `true`, `false` | `false` | Afterburner and variable-area nozzle installed. |
| `nozzle_type` | `str` | – | `"convergent"`, `"convergent_divergent"` | `"convergent"` | Exhaust nozzle expansion geometry. |
| `mass_flow_kgps` | `float` | $\text{kg/s}$ | $[5.0, 250.0]$ | `42.0` | Design-point SLS physical core airflow $\dot{m}_{0,R}$. |
| `opr` | `float` | ratio | $[2.0, 25.0]$ | `5.35` | Design-point SLS overall pressure ratio $\pi_{c,R}$. |
| `tit_K` | `float` | $\text{K}$ | $[900.0, 1800.0]$ | `1117.0` | Design-point SLS turbine inlet temperature $T_{t4,R}$. |
| `ab_temp_K` | `float` | $\text{K}$ | $0.0$ or $[1350.0, 2200.0]$ | `0.0` | Max afterburner total temperature $T_{t7,\text{max}}$. |
| `bypass_ratio` | `float` | ratio | $[0.0, 1.5]$ | `0.0` | Bypass ratio $\alpha_{\text{bpr}}$ ($0.0$ for pure turbojet). |
| `cooled_turbine` | `bool` | – | `true`, `false` | `false` | Air-cooled HP turbine blades (`engine.cooled_turbine_blades`). |
| `eta_c_poly` | `float` | ratio | $[0.70, 0.92]$ | `0.84` | Compressor polytropic efficiency $e_c$. |
| `eta_t_poly` | `float` | ratio | $[0.75, 0.93]$ | `0.86` | Turbine polytropic efficiency $e_t$. |
| `bleed_fraction` | `float` | ratio | $[0.0, 0.15]$ | `0.0` | External airframe bleed fraction $\varepsilon_{\text{bleed}}$ ($0.04$ if blown flaps). |
| `specific_weight_factor` | `float` | mult | $[0.45, 1.50]$ | `1.0` | Structural/material weight multiplier (`engine.specific_weight_factor`). |
| `mtbf_factor` | `float` | mult | $[0.30, 3.00]$ | `1.0` | Baseline reliability multiplier (`engine.mtbf_factor`). |
| `cumulative_test_hours` | `float` | $\text{h}$ | $[0.0, 10^6]$ | `1000.0` | Cumulative test/service EFH for Duane MTBF growth. |

### 4.2 `EngineSpec` Contract (`00_conventions.md` §4.3)

```python
class EngineSpec:
    engine_id: str
    name: str
    mass_kg: float             # Dry equipped mass [kg]
    diameter_m: float          # Maximum installation envelope diameter [m]
    length_m: float            # Total length including tailpipe/nozzle [m]
    unit_cost: float           # Manufacturing flyaway unit cost [then-year USD]
    mtbf_h: float              # Current instantaneous Mean Time Between Failures [h]
    maint_mh_per_fh: float     # Maintenance man-hours per flight hour [MMH/FH]
    has_afterburner: bool

    def thrust_N(self, mach: float, alt_m: float, throttle: float = 1.0, ab: bool = False) -> float: ...
    def tsfc(self, mach: float, alt_m: float, throttle: float = 1.0, ab: bool = False) -> float: ...
    def fuel_flow_kgps(self, mach: float, alt_m: float, throttle: float = 1.0, ab: bool = False) -> float: ...
```

### 4.3 `engine_diagnostics` Schema (Consumed by Module 06)

```json
{
  "engine_id": "j57_p_21",
  "compressor_surge_margin": 0.232,
  "high_alt_flameout_risk": 0.05,
  "ab_lightoff_reliability": 0.87,
  "intake_compatibility": 1.0,
  "thermal_margin_K": -9.0,
  "flaw_incidence_multipliers": {
    "engine_stall": 0.7069,
    "inlet": 1.0
  }
}
```

### 4.4 Historical Engine JSON Schema (`sim/data/engines_hist/*.json`)

Example (`sim/data/engines_hist/j57_p_21.json`):
```json
{
  "engine_id": "j57_p_21",
  "name": "Pratt & Whitney J57-P-21",
  "manufacturer": "Pratt & Whitney",
  "country": "USA",
  "first_run_year": 1950,
  "service_entry_year": 1955,
  "applications": ["North American F-100C/D Super Sabre"],
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
    "sls_dry_tsfc_kg_per_Ns": 2.22355e-5,
    "sls_ab_tsfc_kg_per_Ns": 5.80672e-5,
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
}
```

---

## 5. Algorithms & Exact Formulas

### 5.1 Thermodynamic Constants (Two-Gamma Model, Mattingly 2002 Ch. 4)
- Cold section (stations $0 \to 3$): $\gamma_c = 1.40$, $c_{pc} = 1004.5\text{ J/(kg}\cdot\text{K)}$, $R_c = \frac{\gamma_c - 1}{\gamma_c} c_{pc} = 287.0\text{ J/(kg}\cdot\text{K)}$.
- Hot turbine section (stations $4 \to 5$, and dry $9$): $\gamma_t = 1.33$, $c_{pt} = 1156.0\text{ J/(kg}\cdot\text{K)}$, $R_t = \frac{\gamma_t - 1}{\gamma_t} c_{pt} = 286.827\text{ J/(kg}\cdot\text{K)}$.
- Mean combustor specific heat ($3 \to 4$): $c_{pb} = \frac{1}{2}(c_{pc} + c_{pt}) = 1080.25\text{ J/(kg}\cdot\text{K)}$.
- Afterburning section (stations $7 \to 9$ when AB lit): $\gamma_{ab} = 1.30$, $c_{p,ab} = 1243.0\text{ J/(kg}\cdot\text{K)}$, $R_{ab} = \frac{\gamma_{ab} - 1}{\gamma_{ab}} c_{p,ab} = 286.846\text{ J/(kg}\cdot\text{K)}$.
- Fuel lower heating value (JP-4): $h_{PR} = 42.8 \times 10^6\text{ J/kg}$.
- Standard Sea-Level reference: $T_{\text{std}} = 288.15\text{ K}$, $P_{\text{std}} = 101325.0\text{ Pa}$.

### 5.2 Freestream & Inlet Total-Pressure Recovery ($0 \to 2$)
At altitude $h$ and Mach $M_0$, let $(T_0, P_0, a_0)$ be the ISA 1976 state (`00_conventions.md` §3).
$$\tau_r = 1 + \frac{\gamma_c - 1}{2} M_0^2, \quad \pi_r = \tau_r^{\frac{\gamma_c}{\gamma_c - 1}}, \quad T_{t2} = T_0 \tau_r, \quad P_{t2} = P_0 \pi_r \pi_d(M_0)$$
where $\pi_d(M_0) = \pi_{d,\text{sub}} \cdot \eta_r(M_0) \cdot \pi_{\text{plenum}}$:
- $\pi_{\text{plenum}} = 0.968$ if `compressor_type == "centrifugal"` (double-sided radial plenum loss), else $1.0$.
- For uninstalled test-stand rating (`uninstalled_bellmouth=True` at $M_0 = 0$): $\pi_{d,\text{sub}} = 1.0, \eta_r = 1.0$.
- For installed operation: $\pi_{d,\text{sub}} = \min\left(0.995,\; \pi_{d,\text{loc}} + \Delta\pi_{d,\text{tech}}\right)$ where $\Delta\pi_{d,\text{tech}}$ is `aero.inlet_pressure_recovery_bonus` and $\pi_{d,\text{loc}} \in \{0.975\text{ (nose)}, 0.968\text{ (chin)}, 0.962\text{ (cheek)}, 0.955\text{ (wing\_root)}, 0.985\text{ (mil\_spec)}\}$.
- Supersonic shock recovery $\eta_r(M_0)$ for $M_0 > 1$ ($\eta_r = 1.0$ for $M_0 \le 1$):
  - **Variable geometry (`aero.inlet_variable` or `mil_spec`, MIL-E-5007D)**:
    $$\eta_{r,\text{var}}(M_0) = \max\left(0.20,\; 1 - 0.075 (M_0 - 1)^{1.35}\right)$$
  - **Fixed conical spike (`aero.inlet_spike`)**: oblique + reduced normal shock at effective Mach $M_{\text{eff}} = 1 + 0.52 (M_0 - 1)$:
    $$\eta_{r,\text{spike}}(M_0) = 0.99 \, \eta_{r,\text{norm}}(M_{\text{eff}})$$
  - **Pitot / normal shock**:
    $$\eta_{r,\text{norm}}(M) = \left[\frac{(\gamma_c + 1) M^2}{(\gamma_c - 1) M^2 + 2}\right]^{\frac{\gamma_c}{\gamma_c - 1}} \left[\frac{\gamma_c + 1}{2 \gamma_c M^2 - (\gamma_c - 1)}\right]^{\frac{1}{\gamma_c - 1}}$$

### 5.3 On-Design Cycle Solution ($M_0 = 0, h = 0$)
1. **Compressor ($2 \to 3$)**:
   - Single-spool (`spools == 1`): $\pi_{cL,R} = \pi_{c,R} = \text{OPR}$, $\pi_{cH,R} = 1$.
   - Twin-spool (`spools == 2`): $\pi_{cL,R} = \pi_{c,R}^{s_{LP}}$, $\pi_{cH,R} = \pi_{c,R}^{1 - s_{LP}}$ with $s_{LP} = 0.45$.
   - Temperature ratios via polytropic efficiency $e_c$:
     $$\tau_{cL,R} = \pi_{cL,R}^{\frac{\gamma_c - 1}{\gamma_c e_c}}, \quad \tau_{cH,R} = \pi_{cH,R}^{\frac{\gamma_c - 1}{\gamma_c e_c}}, \quad \tau_{c,R} = \tau_{cL,R} \tau_{cH,R}, \quad T_{t3,R} = T_{t2,R} \tau_{c,R}$$
2. **Bleed & Combustor ($3 \to 4$)**:
   - Turbine cooling bleed fraction: $\varepsilon_{\text{cool}} = 0.025 + 0.00015 \max(0, T_{t4,R} - 1150)$ if `cooled_turbine` else $0.0$.
   - Core fraction entering burner: $\beta_{\text{core}} = 1 - \varepsilon_{\text{cool}} - \varepsilon_{\text{bleed}}$.
   - Burner fuel-air ratio (sensible enthalpy referenced to $T_{\text{std}}$):
     $$f_{\text{core},R} = \frac{c_{pb}(T_{t4,R} - T_{t3,R})}{\eta_b h_{PR} - c_{pt}(T_{t4,R} - T_{\text{std}})}, \quad f_R = \beta_{\text{core}} f_{\text{core},R}$$
   - Effective mixed turbine entry temperature after cooling-air re-injection:
     $$m_{\text{turb},R} = 1 - \varepsilon_{\text{bleed}} + f_R, \quad T_{t4,\text{eff},R} = \frac{\beta_{\text{core}}(1 + f_{\text{core},R}) T_{t4,R} + \varepsilon_{\text{cool}}(c_{pc}/c_{pt}) T_{t3,R}}{m_{\text{turb},R}}$$
3. **Turbine Work Balance ($4 \to 5$)**:
   - With bypass ratio $\alpha_{\text{bpr}} \ge 0$ and fan temperature ratio $\tau_{f,R} = \tau_{cL,R}$ (if $\alpha_{\text{bpr}} > 0$ else $1$):
     $$1 - \tau_{t,R} = \frac{c_{pc} T_{t2,R}\left[(\tau_{c,R} - 1) + \alpha_{\text{bpr}}(\tau_{f,R} - 1)\right]}{\eta_m m_{\text{turb},R} c_{pt} T_{t4,\text{eff},R}}, \quad \pi_{t,R} = \tau_{t,R}^{\frac{\gamma_t}{(\gamma_t - 1) e_t}}$$
   - For twin-spool engines, HP and LP turbine temperature ratios $\tau_{tH,R}, \tau_{tL,R}$ are solved sequentially across HP and LP shafts with $\tau_{t,R} = \tau_{tH,R} \tau_{tL,R}$.

### 5.4 Off-Design Cycle Model & Governor Limits (Mattingly Ch. 8)
Under choked turbine nozzle guide vanes and choked exhaust nozzle, $\tau_t = \tau_{t,R}$ and $\pi_t = \pi_{t,R}$ remain invariant across off-design operation:
1. **Maximum Available $T_{t4,\text{avail}}(M_0, h)$**:
   - Bounded by both the turbine material limit $T_{t4,R}$ and the cold-air mechanical/aerodynamic spool limit $\pi_c \le \kappa_{\text{opr}} \pi_{c,R}$ ($\kappa_{\text{opr}} = 1.06$):
     $$\tau_{c,\text{max}} = (\kappa_{\text{opr}} \pi_{c,R})^{\frac{\gamma_c - 1}{\gamma_c e_c}}, \quad T_{t4,\text{spool}} = T_{t4,R} \frac{T_{t2}}{T_{\text{std}}} \frac{\tau_{c,\text{max}} - 1}{\tau_{c,R} - 1}$$
     $$T_{t4,\text{avail}}(M_0, h) = \min\left(T_{t4,R},\; T_{t4,\text{spool}}\right)$$
2. **Off-Design Compressor Operating Point & Choked Mass Flow Scaling**:
   - For any combustor temperature $T_{t4}$:
     $$\tau_c = 1 + (\tau_{c,R} - 1) \frac{T_{t4,\text{eff}} / T_{t2}}{T_{t4,\text{eff},R} / T_{\text{std}}}, \quad \pi_c = \tau_c^{\frac{\gamma_c e_c}{\gamma_c - 1}}$$
   - From conservation of mass at the choked HP turbine throat ($A_4^*$ constant):
     $$\dot{m}_0 = \dot{m}_{0,R} \, \delta_0 \left(\frac{\pi_d}{\pi_{d,R}}\right) \left(\frac{\pi_c}{\pi_{c,R}}\right) \sqrt{\frac{T_{t4,\text{eff},R}}{T_{t4,\text{eff}}}} \left(\frac{1 - \varepsilon_{\text{bleed}} + f_R}{1 - \varepsilon_{\text{bleed}} + f}\right)$$
3. **Afterburner & Exhaust Nozzle ($5 \to 7 \to 9$)**:
   - When `ab == True` and `has_afterburner == True`:
     $$f_{\text{ab}} = m_{\text{turb}} \frac{c_{p,ab}(T_{t7} - T_{t5})}{\eta_{ab} h_{PR} - c_{p,ab}(T_{t7} - T_{\text{std}})}, \quad P_{t9} = P_{t5} \pi_{\text{ab,wet}} \pi_{n,\text{dry}}$$
   - When `ab == False`: $f_{\text{ab}} = 0, T_{t7} = T_{t5}, P_{t9} = P_{t5} \pi_{\text{ab,dry}} \pi_{n,\text{dry}}$ (where $\pi_{\text{ab,dry}} = 0.972$ if an unlit afterburner flameholder duct is present, else $1.0$).
   - Let $\text{NPR} = P_{t9} / P_0$ and $\pi_{\text{crit}} = \left(\frac{\gamma_9 + 1}{2}\right)^{\frac{\gamma_9}{\gamma_9 - 1}}$:
     - **Convergent nozzle (`"convergent"`)**:
       - If $\text{NPR} \le \pi_{\text{crit}}$ (unchoked): $M_9 = \sqrt{\frac{2}{\gamma_9 - 1}\left(\text{NPR}^{\frac{\gamma_9 - 1}{\gamma_9}} - 1\right)}$, $T_9 = \frac{T_{t7}}{1 + \frac{\gamma_9 - 1}{2} M_9^2}$, $V_{9,\text{eff}} = C_v M_9 \sqrt{\gamma_9 R_9 T_9}$.
       - If $\text{NPR} > \pi_{\text{crit}}$ (choked at $M_9 = 1$): $T_9 = \frac{2}{\gamma_9 + 1} T_{t7}$, $V_9 = \sqrt{\gamma_9 R_9 T_9}$, and including the pressure-thrust area term $(P_9 - P_0)A_9 / \dot{m}_9$:
         $$V_{9,\text{eff}} = C_v V_9 \left[1 + \frac{1}{\gamma_9}\left(1 - \frac{\pi_{\text{crit}}}{\text{NPR}}\right)\right]$$
     - **Convergent-divergent nozzle (`"convergent_divergent"`)**: expands up to $\text{NPR}_{\text{max}} = 12.5$:
       $$V_{9,\text{eff}} = C_v \sqrt{2 c_{p9} T_{t7} \left[1 - \left(\frac{1}{\min(\text{NPR}, \text{NPR}_{\text{max}})}\right)^{\frac{\gamma_9 - 1}{\gamma_9}}\right]}$$
   - **Net Thrust and TSFC**:
     $$F = \dot{m}_0 \left[(1 - \varepsilon_{\text{bleed}} + f + f_{\text{ab}}) V_{9,\text{eff}} - (1 + \alpha_{\text{bpr}}) V_0 + \alpha_{\text{bpr}} V_{19,\text{eff}}\right]$$
     $$\dot{m}_f = \dot{m}_0 (f + f_{\text{ab}}), \quad \text{TSFC} = \frac{\dot{m}_f}{F}$$

### 5.5 Throttle Mapping & Deck Table Interpolation (`sim/mic/engine/deck.py`)
- **Dry Mode (`ab=False`, $\text{throttle} \in [0, 1]$)**:
  - Thrust is strictly linear in throttle so Module 01 can invert $\text{throttle} = D / F_{\text{dry,max}}(M_0, h)$ analytically without iteration:
    $$F_{\text{dry}}(M_0, h, \text{throttle}) = \text{throttle} \cdot F_{\text{dry,max}}(M_0, h)$$
  - For $\text{throttle} \ge 0.10$, $T_{t4}$ is solved via 36-step fixed bisection so that cycle net thrust equals $\text{throttle} \cdot F_{\text{dry,max}}$, with a low-power accessory/parasitic loss factor $1 + 0.06 \frac{(1 - \text{throttle})^2}{\max(0.15, \text{throttle})}$, producing the realistic subsonic cruise TSFC bucket at $75\%\text{–}90\%$ throttle.
  - For $\text{throttle} < 0.10$, fuel flow interpolates linearly to $\dot{m}_{f,\text{idle}} = 0.14 \, \dot{m}_{f,\text{mil}}$, and $\text{TSFC}$ divides by $\max(0.05 F_{\text{dry,max}}, \text{throttle} \cdot F_{\text{dry,max}}, 1\text{ N})$ to remain finite at $\text{throttle} = 0$.
- **Afterburning Mode (`ab=True`, $\text{throttle} \in [0, 1]$)**:
  - Thrust interpolates linearly from Military thrust at $\text{throttle} = 0$ to Max AB thrust at $\text{throttle} = 1$:
    $$F_{\text{ab}}(M_0, h, \text{throttle}) = F_{\text{dry,max}}(M_0, h) + \text{throttle} \cdot \left(F_{\text{ab,max}}(M_0, h) - F_{\text{dry,max}}(M_0, h)\right)$$
  - $T_{t7}$ is solved via 32-step bisection to match $F_{\text{ab}}(M_0, h, \text{throttle})$.
- **Deck Grid & Interpolation**:
  - `mach_grid`: $[0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5]$ (15 points)
  - `alt_m_grid`: $[0, 1500, 3000, 4572, 6000, 7620, 9144, 10668, 12192, 13716, 15240, 18288, 21336, 25000]\text{ m}$ (14 points)
  - `dry_throttle_grid`: $[0.1, 0.25, 0.5, 0.75, 0.9, 1.0]$ (6 points); `ab_throttle_grid`: $[0.0, 0.25, 0.5, 0.75, 1.0]$ (5 points)
  - Queries use clamped bilinear interpolation on $(M_0, h)$ for $F_{\text{dry,max}}$ and $F_{\text{ab,max}}$, and trilinear interpolation on $(M_0, h, \text{throttle})$ for $\text{TSFC}$.

### 5.6 Mass, Dimensions, Cost, and Duane Reliability Growth (`sim/mic/engine/sizing.py`)
1. **Maximum Diameter $D$ $[\text{m}]$**:
   $$D = f_{\text{diam}} \times \begin{cases} 0.885 + 0.059 \sqrt{\dot{m}_0} & \text{centrifugal} \\ 0.625 + 0.043 \sqrt{\dot{m}_0} & \text{axial} \end{cases}$$
2. **Length $L$ $[\text{m}]$**:
   $$L = f_{\text{len}} \times \begin{cases} 1.82 + 0.132 \sqrt{\dot{m}_0} + 1.30\,\mathbb{I}_{\text{AB}} & \text{centrifugal} \\ \left(1.42 + 0.225 \sqrt{\dot{m}_0} + 0.42 \ln(\text{OPR})\right) (0.88)^{\mathbb{I}_{\text{VSV}}} + \left(1.45 + 0.085 \sqrt{\dot{m}_0}\right)\mathbb{I}_{\text{AB}} & \text{axial} \end{cases}$$
3. **Dry Equipped Mass $m_{\text{eng}}$ $[\text{kg}]$**:
   Let $\tilde{m} = 42.0 (\dot{m}_0 / 42.0)^{0.92}$.
   $$m_{\text{eng}} = f_{\text{wt}} \cdot (1.24)^{\mathbb{I}_{\text{AB}}} (1 + 0.18 \alpha_{\text{bpr}}) \times \begin{cases} 19.3\,\tilde{m}\,(\text{OPR}/4.4)^{0.08} & \text{centrifugal} \\ 20.8\,\tilde{m}\,(\text{OPR}/5.0)^{0.18} (1.15)^{\mathbb{I}_{2\text{sp}}} (0.86)^{\mathbb{I}_{\text{VSV}}} & \text{axial} \end{cases}$$
4. **Baseline MTBF & Duane (1964) / MIL-HDBK-189 Reliability Growth**:
   $$\text{MTBF}_0 = \text{MTBF}_{\text{base}} \cdot \max\left(0.35, 1 - 0.035\max(0, \text{OPR} - 5)\right) \cdot \max\left(0.35, 1 - 0.18\max\left(0, \frac{T_{t4} - 1100}{100}\right)\right) (0.82)^{\mathbb{I}_{\text{AB}}} (0.90)^{\mathbb{I}_{2\text{sp}}} f_{\text{mtbf}}$$
   where $\text{MTBF}_{\text{base}} = 180\text{ h}$ (centrifugal) or $110\text{ h}$ (axial). As cumulative operational/test engine flight hours $T$ accumulate:
   $$\text{MTBF}(T) = \text{MTBF}_0 \cdot \min\left(6.0,\; \left(1 + \frac{T}{1000\text{ h}}\right)^{\alpha_{\text{Duane}}}\right), \quad \alpha_{\text{Duane}} = 0.42$$
5. **Maintenance Man-Hours per Flight Hour (`maint_mh_per_fh`) & Unit Cost**:
   $$\text{MMH/FH} = \frac{\text{MMH}_{\text{base}} + 0.18\max(0, \text{OPR} - 5)\,\mathbb{I}_{\text{axial}} + 1.6\,\mathbb{I}_{\text{AB}} + 0.8\,\mathbb{I}_{2\text{sp}}}{\sqrt{\max(0.5, f_{\text{mtbf}})}}$$
   $$\text{Cost}_{\text{unit}} = \left(\$14,000 + \$1,150\,\dot{m}_0\right)\left(\frac{\text{OPR}}{5.0}\right)^{0.48} (0.62)^{\mathbb{I}_{\text{cent}}} (1.32)^{\mathbb{I}_{\text{AB}}} (1.25)^{\mathbb{I}_{2\text{sp}}} (1.12)^{\mathbb{I}_{\text{VSV}}}$$

### 5.7 Engine R&D Gameplay Mechanics (`sim/mic/engine/rnd.py`)
1. **Ambition Metric $A \in [0.05, 1.50]$**:
   Normalized frontier utilization ratios against `TechContext` caps ($\text{TIT}_{\max}, \text{OPR}_{\max}, \dot{m}_{\max}, T_{t7,\max}$):
   $$u_{\text{TIT}} = \frac{\max(0, T_{t4} - 980)}{\max(50, \text{TIT}_{\max} - 980)}, \quad u_{\text{OPR}} = \frac{\max(0, \text{OPR} - 3.5)}{\max(1, \text{OPR}_{\max} - 3.5)}, \quad u_{\dot{m}} = \frac{\max(0, \dot{m}_0 - 20)}{\max(10, \dot{m}_{\max} - 20)}$$
   $$A = \sqrt{\sum_i w_i u_i^2} + \sum_{k \in \text{arch}} c_k \left(1 - \text{maturity}(k)\right)$$
   where $(w_{\text{TIT}}, w_{\text{OPR}}, w_{\dot{m}}) = (0.35, 0.35, 0.30)$ (dry) or $(0.28, 0.28, 0.24, 0.20)$ with $u_{\text{AB}}$ (wet), and architecture immaturity weights $c_k$ are $0.15$ (`twin_spool`, `variable_stators`), $0.12$ (`afterburner`), and $0.10$ (`axial_compressor`).
2. **Development Cost & Duration**:
   $$C_{\text{dev}} = \$22\text{M} \left(\frac{\dot{m}_0}{45.0}\right)^{0.65} \left(1 + 2.4 A^2\right) (1.28)^{\mathbb{I}_{\text{AB}}} (1.35)^{\mathbb{I}_{2\text{sp}}} (1.20)^{\mathbb{I}_{\text{VSV}}} \cdot f_{\text{dev\_cost}}$$
   $$D_{\text{dev}} = \left(1100 + 550 A^{1.35} + 180\,\mathbb{I}_{\text{AB}} + 240\,\mathbb{I}_{2\text{sp}}\right)\text{ days}$$
   - For **Derivative Projects** (`parent_engine != None`): $C_{\text{dev}} \times 0.32$, $D_{\text{dev}} \times 0.42$.
   - **Player Cost Share**: $0\%$ for `catalog`, $60\%$ for `custom_commission`, $100\%$ for `inhouse`.
3. **Outcome Uncertainty & Severe Crisis Probability**:
   $$\sigma_F = (0.025 + 0.095 A^{1.5}) f_{\text{risk}}, \quad \sigma_{\text{TSFC}} = (0.020 + 0.075 A^{1.5}) f_{\text{risk}}, \quad \sigma_m = (0.030 + 0.080 A^{1.5}) f_{\text{risk}}$$
   $$P_{\text{crisis}}(A) = \begin{cases} 0.02 (A / 0.72) f_{\text{risk}} & A \le 0.72 \\ \min\left(0.35,\; \left[0.02 + 0.28\left(\frac{A - 0.72}{0.28}\right)^{1.6}\right] f_{\text{risk}}\right) & A > 0.72 \end{cases}$$
4. **Can Engines Be Sold to Other Airframers? (Resolution of GDD §18.2)**:
   - **Yes, if and only if developed via an In-House Engine Division (`is_inhouse_engine=True`)**. The owning company can sell physical engines at `1.18 * unit_cost` ($18\%$ gross margin) or license production for a $12\%$ royalty (`third_party_license_royalty_rate`).
   - Engines developed via **Custom Commission (`custom_commission`)** are owned by the propulsion vendor (P&W, GE, Allison, Wright); the commissioning airframer receives an **18-month exclusivity window** before the engine enters the general catalog for competitors.

---

## 6. Tunables Table (`sim/data/tuning/engine.json`)

| Key Path | Default | Range | Effect | Rationale |
|---|---|---|---|---|
| `thermo.pi_centrifugal_plenum` | `0.968` | $[0.94, 0.99]$ | Plenum total-pressure factor on centrifugal inlets | Captures $90^\circ$ plenum flow-turning loss on double-sided impellers (J33, VK-1). |
| `thermo.pi_ab_duct_dry` | `0.972` | $[0.94, 0.99]$ | Tailpipe pressure ratio with unlit AB flameholders | Accounts for dry thrust/TSFC penalty of carrying an afterburner duct. |
| `thermo.pi_ab_duct_wet` | `0.935` | $[0.88, 0.97]$ | Rayleigh + flameholder total pressure ratio when AB lit | Matches 1950s AB total pressure loss (Mattingly Table 4.4). |
| `thermo.off_design_max_opr_overshoot` | `1.06` | $[1.00, 1.15]$ | Cold-air OPR cap $\kappa_{\text{opr}}$ at altitude | Prevents unrealistic mechanical overspeed in stratosphere. |
| `sizing.mass_axial_per_kgps` | `20.8` | $[16.0, 26.0]$ | Base axial mass per $\text{kg/s}$ core airflow | Calibrated to 1945–1960 axial turbojets. |
| `sizing.mass_twin_spool_factor` | `1.15` | $[1.05, 1.30]$ | Mass multiplier for 2-spool concentric shafts/bearings | Captures J57/J75 structural mass premium over single-spool. |
| `sizing.mass_vsv_factor` | `0.86` | $[0.78, 0.95]$ | Mass multiplier for variable-stator single-spool | Captures J79 weight reduction vs. fixed-stator/twin-spool. |
| `sizing.mass_ab_multiplier` | `1.24` | $[1.15, 1.35]$ | Mass multiplier for afterburner + variable nozzle | Calibrated to VK-1 vs VK-1F and J57/J71/J79 weights. |
| `reliability_and_cost.duane_alpha_default` | `0.42` | $[0.15, 0.50]$ | Duane reliability growth exponent $\alpha$ | Matches Duane (1964) GE jet engine data ($\alpha \in [0.40, 0.50]$). |
| `rnd.base_dev_cost_usd_1950` | `22000000` | $[10\text{M}, 40\text{M}]$ | Baseline clean-sheet R&D cost ($) | Calibrated to J73 ($\$40\text{M}$), J75 ($\$70\text{M}$), J79 ($\$110\text{M}$), J57 ($\$110\text{M}\text{–}\$150\text{M}$). |
| `rnd.custom_commission_fee_multiplier` | `0.60` | $[0.40, 0.85]$ | Airframer cost share when commissioning external vendor | Reflects cost-sharing with P&W/GE/USAF on bespoke fighter engines. |
| `rnd.catastrophic_flaw_ambition_threshold` | `0.72` | $[0.55, 0.90]$ | Ambition knee where J40/J67 crisis probability accelerates | Punishes simultaneous bleeding-edge gambles while keeping moderate leaps safe. |

---

## 7. Edge Cases & Failure Modes

1. **Zero or Near-Zero Throttle (`throttle -> 0.0`)**:
   - As `throttle -> 0.0`, net thrust $F \to 0.0\text{ N}$ while idle fuel flow remains positive ($14\%$ of military fuel flow), which would cause $\text{TSFC} = \dot{m}_f / F \to \infty$. `EngineSpec.tsfc()` clamps the denominator thrust at $\max(0.05 F_{\text{dry,max}}, F, 1.0\text{ N})$ below $\text{throttle} = 0.10$ so `tsfc()` is always finite and continuous, and provides `fuel_flow_kgps()` for exact idle/descent fuel integration.
2. **Afterburner Requested on Non-Afterburning Engine (`ab=True` when `has_afterburner=False`)**:
   - Safely falls back to `ab=False` (dry thrust and dry TSFC) without raising an exception.
3. **Out-of-Bounds Flight Envelope Queries ($M_0 > 2.5$ or $h > 25,000\text{ m}$ or negative inputs)**:
   - Input `mach`, `alt_m`, and `throttle` are clamped to non-negative values; deck interpolation clamps neatly at grid boundaries.
4. **Windmilling / High-Mach Ram Drag Exceeding Gross Thrust**:
   - At extreme Mach and low $T_{t4}$, if $V_{9,\text{eff}} < V_0$, net thrust is clamped at $0.0\text{ N}$ and `high_alt_flameout_risk` flags the envelope limit to Module 01/06.
5. **Exploit Prevention ("Micro-Engine Swarm" & "Zero-Margin Paper Engine")**:
   - Sub-linear mass scaling ($\dot{m}^{0.92}$) and base accessory diameter ($0.625\text{ m}$) prevent players from gaming thrust-to-weight by clustering 8 tiny engines instead of 1–2 properly sized engines.
   - Pushing $\text{OPR}$ and $T_{t4}$ to 100% of newly unlocked tech caps triggers both the quadratic R&D cost multiplier ($1 + 2.4 A^2$), the $35\%$ J40/J67 crisis probability, and high Module 06 `engine_stall` flaw multipliers.

---

## 8. Golden Test Vectors

All golden vectors are generated by the Python reference oracle and verified to relative tolerance `1e-6` in `sim/tests/test_engine.py`:
- [`sim/golden/engine_cycle_sls.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/golden/engine_cycle_sls.json): On-design SLS thrust (dry/AB), TSFC (dry/AB), mass, diameter, length, unit cost, MTBF, and MMH/FH for all 12 historical engines.
- [`sim/golden/engine_deck_queries.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/golden/engine_deck_queries.json): 48 off-design $(M_0, h, \text{throttle}, \text{ab})$ deck interpolation vectors across 6 engines, 24 inlet pressure recovery vectors across 4 inlet modes, and 5 Duane reliability growth vectors.
- [`sim/golden/engine_rnd_and_diagnostics.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/golden/engine_rnd_and_diagnostics.json): R&D project estimate vector, `engine_diagnostics` vector for J57-P-21, and third-party engine sale vector.

---

## 9. Interactions with Other Modules

| Module | Direction | Contract / API | Details |
|---|---|---|---|
| **01 Aero & Performance** | `02 -> 01` | `EngineSpec` (§4.3) | Module 01 calls `engine.thrust_N(mach, alt_m, throttle, ab)` and `engine.tsfc(...)`, and reads `mass_kg, diameter_m, length_m, unit_cost, mtbf_h, maint_mh_per_fh`. |
| **01 Aero & Performance** | `01 -> 02` | `IntakeSpec`, `aero.blown_flaps` | `IntakeSpec` (`nose|cheek|chin|wing_root`, `variable`) and `aero.blown_flaps` bleed configure installed engine deck recovery and bleed. |
| **03 Tech Tree** | `03 -> 02` | `TechContext` (`03_tech_effect_keys.md` §2.3) | `validate_engine_against_tech` and `compute_ambition` consume all 19 `engine.*` keys and their maturities. |
| **04 Economy** | `02 <-> 04` | `EngineProjectState`, `unit_cost` | Module 04 deducts monthly engine R&D spending, in-house division overhead, and engine flyaway unit costs; credits third-party engine sales. |
| **06 Testing & Flaws** | `02 -> 06` | `engine_diagnostics` | `compute_diagnostics` provides `compressor_surge_margin`, `high_alt_flameout_risk`, `ab_lightoff_reliability`, `intake_compatibility`, and flaw incidence multipliers for `testing.flaw_incidence.engine_stall` and `inlet`. |

---

## 10. Validation Results

1. **Historical Engine Calibration ([`docs/validation/engine_calibration.md`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/engine_calibration.md))**:
   - Calibrated across **12 historical 1945–1960 turbojets** (`J33-A-35`, `J35-A-29`, `J47-GE-27`, `J65-W-3`, `J57-P-21`, `J71-A-2`, `J73-GE-3`, `J75-P-19W`, `J79-GE-11A`, `VK-1`, `VK-1F`, `RD-9B`).
   - **Mean Absolute Relative Error**: **$2.43\%$** across all 72 engine-metric pairs.
   - **Max Absolute Relative Error**: **$7.34\%$** (well within the $\pm 10.0\%$ target on every single metric of every engine).
   - Verified off-design altitude/Mach thrust lapse against Mattingly (2002) Eqs. 2.55a/2.55b and verified the part-power subsonic cruise TSFC bucket ($75\%\text{–}90\%$ throttle).
2. **Engine R&D Monte-Carlo Balance ([`docs/validation/engine_rnd.md`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/engine_rnd.md))**:
   - 12,500 Monte-Carlo runs across 5 project archetypes confirm realistic 1950s costs ($\$18\text{M}\text{–}\$110\text{M}$), timelines ($1.8\text{–}5.4\text{ years}$), derivative savings ($68\%$ cost reduction, $58\%$ time reduction), and a $35\%$ crisis rate for J40/J67-style over-ambitious gambles.

---

## 11. Open Questions & Cross-Module Change Requests

### 11.1 Open Questions for User (Taste Only)
1. **Vendor Exclusivity Window Duration**: When the player pays $60\%$ of R&D to commission a custom engine from an external vendor (e.g., P&W or GE), we set the player's exclusivity window to **18 months** before rival AI airframers can buy that engine from the catalog. Would you prefer a longer exclusivity window (e.g., 24–36 months) or an option to pay $80\%$ for permanent exclusivity?
2. **Named Engine Vendors in UI**: Should external engine commissions explicitly assign a historical propulsion vendor (`Pratt & Whitney`, `General Electric`, `Allison`, `Curtiss-Wright`, `Westinghouse`) with vendor-specific specialty bonuses, or keep external commissioning vendor-agnostic in the MVP?

### 11.2 Cross-Module Change Requests
- **None required for `00_conventions.md` or `03_tech_effect_keys.md`**: All 19 `engine.*` keys in `03_tech_effect_keys.md` §2.3 and the `EngineSpec` contract in `00_conventions.md` §4.3 are used verbatim without modification.
- **Note for Module 06 (`06_testing_uncertainty.md`)**: Module 02 exposes `mic.engine.compute_diagnostics(engine_spec, design_max_mach, design_ceiling_m, ...)` returning `flaw_incidence_multipliers["engine_stall"]` and `["inlet"]` ready to multiply directly into `testing.flaw_incidence.engine_stall` and `testing.flaw_incidence.inlet`.
