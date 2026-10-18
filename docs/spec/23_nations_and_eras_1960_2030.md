# Module 23: Playable Nations & Post-1960 Era Expansions (1960–2030)

> **Design Pillar:** A simulation of the military-industrial complex that only works for the 1950s United States is an anecdote; one whose core architecture parameterizes across **capitalist Pentagon fly-offs, French state-backed export champions, Soviet OKB/GAZ command economies, European multi-nation workshare consortiums, and latecomer industrial catch-up ladders**—and scales from **Mach 2 variable-sweep interceptors to 6th-generation loyal wingmen**—is a grand-strategy engineering engine.

---

## 1. Architectural Philosophy: Parameterization Without Forking

Every playable nation and post-1960 technological era operates on the **exact same core simulation loop** defined in Modules 01–09 (`AircraftDesign` $\rightarrow$ `PerformanceReport` $\rightarrow$ `ManufacturingPlan` $\rightarrow$ `ProcurementCompetition` $\rightarrow$ `ActiveConflict` $\rightarrow$ `QuarterlyLedger`). Rather than writing separate hard-coded games for the USSR, France, or the 21st century, Module 23 introduces a top-level **`NationProfile`** institutional configuration and era-gated **`TechParadigm`** extensions that re-parameterize finance, factory ownership, procurement scoring, and aerodynamic/avionics physics.

```rust
pub enum InstitutionalArchetype {
    UsMarketPentagon,         // Competitive fly-offs, private capital, Congressional districts
    FrNationalChampion,       // STAe prototype subsidies, small domestic buys, export-survival doctrine
    SuOkbPlanned,             // Politburo directives, TsAGI aero gates, OKB design vs GAZ state factories
    EuroWorkshareConsortium,  // Multi-nation Juste Retour workshare vs order-share friction
    CatchupLicenseToPrime,    // 4-rung industrial ladder: CKD kits -> License -> Derivative -> Indigenous Prime
}

pub struct NationProfile {
    pub nation_id: String,                    // "USA", "FRA", "SUN", "GBR", "SWE", "CHN", "IND", "JPN"
    pub archetype: InstitutionalArchetype,
    pub domestic_procurement_scale: f64,      // Multiplier on domestic RFP peacetime quantities (USA = 1.0, FRA = 0.28)
    pub state_prototype_subsidy_share: f64,   // Share of NRE covered by state grants even outside formal Dem/Val
    pub bankruptcy_regime: BankruptcyRegime,  // Chapter11Market | NationalizationThreat | OkbPurgeAndReassignment
    pub engine_supply_doctrine: EngineSupplyDoctrine, // CompetitiveVendor | StateMonopoly("SNECMA") | AssignedEngineOkb
    pub tsagi_central_gate: bool,             // True for USSR: enforces strict aerodynamic conformity before prototype build
}
```

---

## 2. Part A: The Playable National Institutional Archetypes

### 2.1 Archetype 1: United States (`UsMarketPentagon`)
The baseline architecture defined in Modules 04, 05, and 07:
* **Capital & Ownership:** Privately owned corporations funded by retained earnings, commercial credit lines, corporate bonds, and progress payments (`Module 05`).
* **Service Rivalry:** Distinct `USAF` and `USN` customer trees with divergent doctrinal weights (USAF prioritizing Mach/altitude/range and strategic nuclear delivery; USN prioritizing carrier recovery $V_{\text{app}}$, spot factor, twin-engine safety, and salt-fog corrosion resistance).
* **Congressional Iron Triangle:** Subcontracting across key states (`CA`, `TX`, `WA`, `MO`, `CT`, `GA`, `NY`, `OH`) builds `political_clout_score` (`Module 04 §3.5`), shielding programs from Nunn-McCurdy cancellation breaches at the cost of geographic shipping overhead (`+4%` to `+9%` unit cost).

### 2.2 Archetype 2: France & The National Champion Model (`FrNationalChampion`)
Modeled on **Avions Marcel Dassault**, **Sud-Aviation / Aérospatiale**, **Breguet**, and state engine house **SNECMA** (`Atar 101` $\rightarrow$ `Atar 9C/9K50` $\rightarrow$ `M53` $\rightarrow$ `M88`):
* **The `STAé` (`Service Technique Aéronautique`) Incremental Prototype Doctrine:** French state technical directors favor evolutionary, low-risk aerodynamic families (`Ouragan` $\rightarrow$ `Mystère II/IV` $\rightarrow$ `Super Mystère` $\rightarrow$ `Mirage III` $\rightarrow$ `Mirage F1` $\rightarrow$ `Mirage 2000` $\rightarrow$ `Rafale`). Sharing $>60\%$ structural or aerodynamic family lineage with a proven predecessor grants a **`+25%` `STAé` NRE subsidy** and cuts prototype build time by `20%`.
* **Small Domestic Buy / Export Imperative:** Because `Armée de l'Air` and `Aéronavale` domestic orders are $\sim 25\text{--}35\%$ the size of USAF/USN buys ($80\text{--}200$ airframes vs $600\text{--}1,500$), domestic production alone rarely amortizes tooling down Wright's learning curve (`Module 06`). Survival **requires capturing 40–65% export share**.
* **Modular "Mirage" Export Engineering:** French National Champion firms unlock the **`ModularExportBus`** design trait (`+3%` empty structural weight, `+5%` base NRE), which reduces customer-variant integration cost (`Atar` engine swaps, Israeli/South African/Swiss avionics bricks, cannon packs vs rocket packs) by **`-65%`** (`Module 22 §4.2`).
* **Political Autonomy Dividend:** As captured in `Module 22 §2`, France's `ExportControlPosture::CommercialPragmatic` (`political_strings_index = 0.20`) gives French designs a structural advantage whenever Washington imposes embargoes or human-rights conditions on Latin American, Middle Eastern, or South Asian buyers.

---

### 2.3 Archetype 3: USSR & The OKB / GAZ Command Economy (`SuOkbPlanned`)
Modeled on **OKB-155 (Mikoyan-Gurevich)**, **OKB-51 (Sukhoi)**, **OKB-115 (Yakovlev)**, **OKB-301 (Lavochkin)**, **OKB-156 (Tupolev)**, and engine bureaus **Klimov, Tumansky, Lyulka, and Soloviev**:

#### 2.3.1 Separation of Design Bureau (`OKB`) and State Serial Factories (`GAZ`)
Unlike American primes that own both engineering offices and final assembly plants, a Soviet player leads an **Experimental Design Bureau (`OKB`)** with its own prototype shop, while mass production takes place in gigantic **State Aviation Factories (`GAZ` — *Gosudarstvenny Aviatsionny Zavod*)**, such as **GAZ-21 (Gorky)**, **GAZ-30 (Moscow Znamya Truda)**, **GAZ-153 (Novosibirsk)**, or **GAZ-126 (Komsomolsk-on-Amur)**:
1. **No Commercial Bankruptcy — Instead, `Politburo Favor` & `GAZ` Factory Allocation:** An OKB cannot go bankrupt in dollars/rubles. Instead, the primary strategic currency is **Politburo & MAP (*Ministerstvo Aviatsionnoy Promyshlennosti*) Authority (`0–100`)** and **Assigned `GAZ` Floor-Space Quotas**.
2. **Winning vs. Losing the `GAZ` Struggle:** If your prototype (`Ye-152` or `T-4`) fails acceptance trials or loses to a rival OKB (`MiG-21`), MAP strips your assigned `GAZ` factories and hands them to the rival OKB to mass-produce *their* aircraft. An OKB whose `Politburo_Authority` drops below `15` suffers a **Leadership Reorganization** (chief designer demoted/replaced, engineering teams reassigned—as happened to Lavochkin after shifting to SAMs or Sukhoi's temporary dissolution in 1949–1953).

```
   +-----------------------------------------------------------------------+
   |     COUNCIL OF MINISTERS / VPK (Military-Industrial Commission)       |
   |  Issues Spec Directive (e.g., Frontline Fighter / PVO Interceptor)    |
   +-----------------------------------+-----------------------------------+
                                       |
                   +-------------------+-------------------+
                   v                                       v
   +-------------------------------+       +-------------------------------+
   |    TsAGI (Central Aero-       |       |   MAP Engine OKB Assignment   |
   |    Hydrodynamic Institute)    |       |  (Tumansky / Lyulka / Klimov) |
   |  Mandatory Wind-Tunnel Gate   |       |  State-Allocated Powerplant   |
   +---------------+---------------+       +---------------+---------------+
                   |                                       |
                   +-------------------+-------------------+
                                       v
   +-----------------------------------------------------------------------+
   |         RIVAL EXPERIMENTAL DESIGN BUREAUS (OKB-155 vs OKB-51)         |
   |      Build Ye-series / T-series Prototypes -> NII VVS State Trials    |
   +-----------------------------------+-----------------------------------+
                                       |
                        Winner Awarded GAZ Allocation
                                       v
   +-----------------------------------------------------------------------+
   |        STATE SERIAL FACTORIES (GAZ-21 Gorky / GAZ-153 Novosibirsk)    |
   |   Five-Year Plan Quota Output -> VVS / PVO Regiments & Warsaw Pact    |
   +-----------------------------------------------------------------------+
```

#### 2.3.2 The `TsAGI` Aerodynamic Conformity Gate
Every Soviet design must pass review by **TsAGI** (*Tsentralny Aerogidrodinamichesky Institut*) before prototype metal is cut:
* **TsAGI Recommended Planforms:** Each era, TsAGI publishes blessed aerodynamic configurations (e.g., 1956 tailed $55^\circ$ delta + swept sisters `TsAGI S-1/T-1` shared by `MiG-21` and `Su-7/Su-9`; 1966 variable-sweep vs lift-jet; 1977 integrated wing-body `TsAGI` LERX layout for `MiG-29`/`Su-27`).
* **Conformity vs. Heresy:** Adopting a TsAGI-blessed configuration grants **`-30%` wind-tunnel drag uncertainty** and **`+10` MAP institutional approval**. Rejecting TsAGI's recommendation (as Pavel Sukhoi or Alexander Kartveli-style mavericks sometimes did) imposes a **`+15` Politburo political risk penalty** if the prototype misses its guaranteed speed/turn numbers, but yields **`+25` Prestige & Lenin Prize / Hero of Socialist Labor** rewards if `NII VVS` State Trials prove the heretical design superior!

#### 2.3.3 Soviet Operational Doctrine Constraints (`VVS Frontal Aviation` vs `PVO Strany`)
Soviet requirements enforce distinctive physical trade-offs directly inside `PerformanceReport`:
* **Unpaved / Rough-Field Strip Mandate (`VVS`):** Landing gear stroke, low-pressure tire footprint, and intake FOD doors (such as the `MiG-29` dorsal auxiliary louvers) are scored heavily (`rough_field_index >= 0.75`).
* **Automated GCI Intercept (`PVO Strany`):** Vast Siberian/Arctic borders require integration with `Vozdukh-1` / `Lazur` ground-controlled intercept datalinks, heavy long-range missiles (`K-8`, `K-23`, `K-33`), and high supersonic dash ceiling over dogfight agility.

---

### 2.4 Archetype 4: Latecomer Industrial Catch-Up (`CatchupLicenseToPrime`) & European Consortiums (`EuroWorkshareConsortium`)

#### 2.4.1 The 4-Rung Industrial Catch-Up Ladder (Sweden, Japan, China, India)
Nations entering the jet age without an established prime-contractor ecosystem progress up a rigorous **4-Rung Localization Ladder**:

| Rung | Industrial Stage | Historical Examples | Engineering & Manufacturing Mechanics | Unlock Condition for Next Rung |
| :--- | :--- | :--- | :--- | :--- |
| **Rung 1** | **CKD/SKD Kit Assembly** | Early `JASDF F-86F` (Mitsubishi), `HAL Vampire`, `PLAAF MiG-17` | Assemble imported Complete Knock-Down (`CKD`) kits. Zero aerodynamic NRE; builds airframe labor pool & QA tooling (`mfg_experience +1.5/yr`). | Assemble $\ge 100$ kit aircraft with `< 5%` rework rate. |
| **Rung 2** | **Licensed Production & Subsystem Localization** | `Shenyang J-6`, `HAL Gnat / MiG-21FL`, `F-104J` | Manufacture airframe and licensed engine (`RD-9B`/`Orpheus`/`J79-IHI-11`) from domestic alloys. Domestic metallurgy penalty starts at `+6%` structural weight and decays to `0%` over 16 quarters. | Achieve $\ge 75\%$ domestic value-added content across airframe + avionics. |
| **Rung 3** | **Reverse-Engineered / Modified Derivative** | `Nanchang Q-5` (side-intake `J-6`), `Shenyang J-7E/G` (double-delta), `Shenyang J-8`, `Atlas Cheetah`, `IAI Kfir` | Re-engineer nose/intakes, wing planform (`double-delta`), or re-engine an existing baseline airframe (`Module 06 §6` Derivative Airframe rules). Costs `35%` of clean-sheet NRE. | Successfully pass military qualification with a derivative changing $\ge 2$ major morphological subsystems. |
| **Rung 4** | **Indigenous Clean-Sheet Prime** | `Saab 35 Draken / 37 Viggen`, `Mitsubishi F-1 / F-2`, `HAL HF-24 Marut / Tejas`, `Chengdu J-10 / J-20` | Full clean-sheet `AircraftDesign` authority. **The Jet Engine Bottleneck:** Even at Rung 4, indigenous high-temperature hot-section metallurgy (`TurbineInletTemp_K`) lags superpower engines by `1–2` tiers unless heavy sustained R&D is invested or foreign engines (`RM12`, `AL-31FN`, `F404`) are imported! | Complete indigenous hot-section engine qualification to achieve 100% strategic autonomy. |

#### 2.4.2 Multi-Nation European Consortiums (`EuroWorkshareConsortium`)
Modeled on **SEPECAT (`Jaguar`)**, **Panavia (`Tornado`)**, and **Eurofighter (`Typhoon`)**:
* ***Juste Retour* (Fair Return) Workshare Equation:** When $M$ nations form a consortium with national order shares $s_1, s_2, \dots, s_M$ ($\sum s_i = 1$), each partner demands factory and subsystem workshare $w_i \approx s_i$.
* **Consortium Integration Overhead & Order-Cut Friction:**
  $$\text{NRE}_{\text{consortium}} = \text{NRE}_{\text{single}} \cdot \sqrt{M}, \qquad \text{Friction}_i = \max\left(0,\; w_i - s_i(t)\right) \cdot 150$$
  If a partner nation cuts its domestic order share $s_i(t)$ mid-program while refusing to surrender its factory workshare $w_i$, consortium political friction spikes, delaying milestone gates by `1–3 quarters` unless the player renegotiates subsystem allocation or secures third-party export orders to absorb the slack.

---

## 3. Part B: Era II (1960–1975) — Mach 2+, Variable Geometry & Missile Doctrines

Era II transitions from the pure high-altitude interceptors of the late 1950s to multi-mission weapon systems shaped by SAM proliferation (`SA-2 Guideline` / `SA-6 Gainful`), low-altitude terrain-following penetration (`F-111`, `Su-24`, `Tornado`), and the hard combat lessons of Vietnam and the Middle East (`F-4 Phantom II`, `MiG-21bis`, `Mirage III`, `F-14A Tomcat`).

### 3.1 Variable-Sweep Wing (`VG`) Kinematics, Weight & Drag Physics
To reconcile low-speed carrier/short-field landing ($V_{\text{app}}$) and long subsonic loiter with Mach 2.2+ high-altitude dash and Mach 1.2 sea-level penetration, Era II unlocks `WingPlanform::VariableSweep`:

```rust
pub struct VariableSweepParameters {
    pub sweep_min_deg: f64,           // e.g., 16.0 deg (F-111) or 20.0 deg (F-14)
    pub sweep_max_deg: f64,           // e.g., 72.5 deg (F-111) or 68.0 deg (F-14)
    pub pivot_spanwise_fraction: f64, // Outboard pivot (Su-17: 0.42) vs root carry-through box (F-14/MiG-23: 0.18)
    pub control_mode: VgScheduleMode, // Manual3Position (MiG-23) | MachScheduledAuto (F-14 CADC)
}
```

* **Aerodynamic Envelope Expansion:** At each flight regime $m \in \{\text{Takeoff/Landing}, \text{Subsonic Cruise}, \text{Transonic Turn}, \text{Supersonic Dash}\}$, the solver evaluates `PerformanceReport` at the optimal sweep angle $\Lambda^*(M) \in [\Lambda_{\min}, \Lambda_{\max}]$:
  * **Low-Speed / Loiter ($\Lambda = \Lambda_{\min}$):** Effective aspect ratio $AR_{\text{eff}} = AR_{\text{unswept}}$, maximizing subsonic Oswald efficiency $e_0$ (`+28%` ferry/loiter range) and $C_{L,\max}$ (`-18 kt` approach speed).
  * **Supersonic Dash ($\Lambda = \Lambda_{\max}$):** Effective aspect ratio drops by $\cos^2(\Lambda_{\max} - \Lambda_{\min})$ and Mach-cone wave drag $C_{D,\text{wave}}(M)$ (`Module 02 §3.2`) is evaluated at $\Lambda_{\max}$, slashing supersonic wave drag by **`35%–50%`**.
* **Structural & Maintenance Penalties:**
  $$\Delta W_{\text{VG\_pivot}} = W_{\text{wing\_base}} \cdot \left(0.18 + 0.10 \cdot (1.0 - f_{\text{pivot}})\right)$$
  Outboard pivots (`Su-17/22`, $f_{\text{pivot}} \approx 0.42$) halve the titanium carry-through box weight penalty (`+11%` wing weight) compared to root pivots (`F-111`/`MiG-23`, `+16%` to `+19%` wing weight), at the cost of smaller aspect-ratio modulation. In addition, the wing-sweep screwjacks and pivot bearings add **`+3.5 MMH/FH`** and aerodynamic center shift $\Delta x_{\text{AC}}(\Lambda)$ that can induce high-speed pitch-up tuck unless mitigated by glove vanes or an automated Air Data Computer (`CADC`).

### 3.2 Early Afterburning Turbofans & Inlet-Engine Distortion Coupling
Era II introduces the first generation of **afterburning low-bypass turbofans** (`Pratt & Whitney TF30`, `Rolls-Royce Spey`, `Tumansky R-29`, `SNECMA TF106`):
* **Specific Fuel Consumption (`SFC`) vs Thrust Growth:** Early turbofans (`bypass_ratio = 0.30..0.90`) reduce dry subsonic cruise `SFC` from `0.90–1.05 lb/(lbf·hr)` (turbojets) down to **`0.62–0.75 lb/(lbf·hr)`**, extending combat radius by `35%–55%`.
* **High-AoA Compressor Stall Susceptibility (`TF30` Syndrome):** Early mixed-flow afterburning turbofans suffer severe fan-core pressure interaction when the aircraft pulls high Angle of Attack ($\alpha > 15^\circ$) or rapid yaw during a dogfight while lighting afterburner zones:
  $$P_{\text{stall}}(\alpha, M) = \text{clamp}\left(\frac{\text{Distortion}_{\text{inlet}}(\alpha, M) - \text{SurgeMargin}_{\text{fan}}(\text{BPR})}{0.25},\; 0.0,\; 1.0\right)$$
  Pairing an early high-bypass turbofan (`TF30`) with a high-agility airframe (`F-14A`) or a poorly baffled fuselage side intake (`F-111A` Triple Plow I) causes catastrophic compressor stalls in `Module 03` Flight Testing and `Module 21` Dogfight Sorties until the player invests in inlet boundary-layer splitter plates or upgrades to a high-surge-margin 4th-gen turbofan (`F110`).

### 3.3 Pulse-Doppler Look-Down/Shoot-Down Radars, RWR & ECM Pods
* **Ground Clutter Rejection (`Look-Down/Shoot-Down`):** Early 1950s pulse radars (`APQ-72`, `RP-21 Sapfir`) are blinded by ground return whenever the target flies below the horizon ($\text{LookDownClutterRatio} = 0.0$). Era II unlocks **Pulse-Doppler (`PD`) Signal Processing** (`AWG-9`, `AWG-10`, `Cyrano IV`, `Sapfir-23`), enabling detection and `SARH` missile illumination of low-flying penetrators against clutter (`clutter_rejection_db = 25..55 dB`).
* **Electronic Warfare (`RWR` + Jamming Pods):** Combat against Soviet SAM networks (`Module 21 §2.3`) drives the mandatory integration of **Radar Warning Receivers (`ALR-45`, `SPO-10 Sirena-3`)**, chaff/flare dispensers (`ALE-29/39`), and external noise/deception jamming pods (`ALQ-71/87/101/119`), which trade hardpoint payload and parasitic drag (`+8 to +18 counts`) for a **`-35%` to `-60%` reduction in SAM/BVR $P_k$**.

### 3.4 McNamara Joint-Service Commonality RFPs (`TFX` Syndrome)
In `UsMarketPentagon` (and `EuroWorkshareConsortium`), the Secretary of Defense periodically issues **Forced Joint-Service RFPs** (modeled on Robert McNamara's `TFX / F-111` mandate):
* **The Commonality Constraint:** The player must submit a single baseline `AircraftDesign` (sharing $\ge 70\%$ structural airframe commonality) simultaneously evaluated against both **USAF Tactical Strike** (side-by-side seating, long internal fuel range, Mach 2.5 dash) and **USN Fleet Air Defense** (carrier arrestor hook, nose dish diameter $\ge 36\text{ in}$, loiter weight $< 55,000\text{ lb}$).
* **The Divergence Trap:** Compromising a single airframe to satisfy two orthogonal service doctrines compounds structural weight growth (`Module 02` mass-growth factor $\approx 2.6\times$), easily triggering USN cancellation (`F-111B`) unless the player either lobbies Congress (`political_clout_score >= 70`) to split the RFP into dedicated single-service programs (`F-14` / `F-15`) or unlocks Era III lightweight composites and high-T/W engines.

---

## 4. Part C: Era III (1975–1990) — Energy-Maneuverability & 4th-Gen Digital FBW

Spurred by John Boyd's **Energy-Maneuverability ($E\text{-}M$) Theory** (`Specific Excess Power` $P_s = \frac{(T - D)V}{W}$) and the rise of the "Teen Series" (`F-14`, `F-15`, `F-16`, `F/A-18`) Alongside the `Mirage 2000`, `JA 37 Viggen`, `MiG-29`, and `Su-27`, Era III revolutionizes subsonic/transonic agility, cockpit ergonomics (`HOTAS`), and engine thrust-to-weight ratios.

### 4.1 Relaxed Static Stability (`RSS`) & Fly-By-Wire (`FBW`) Physics
In Eras I and II, aircraft must be **statically stable** ($\text{StaticMargin} = \frac{x_{\text{NP}} - x_{\text{CG}}}{\bar{c}} \ge +0.05$): to pitch the nose up in a high-$g$ turn, the horizontal tail must generate **downforce** ($L_{\text{tail}} < 0$), which forces the main wing to carry *both* the aircraft's weight $n \cdot W$ *and* the tail downforce, multiplying induced trim drag!

```
  CONVENTIONAL STATICALLY STABLE (Era I-II)       RELAXED STATIC STABILITY + FBW (Era III+)
        CG ahead of Aerodynamic Center                  CG near/behind Aerodynamic Center
              L_wing = n*W + |L_tail|                         L_wing = n*W - L_tail
                     ^                                               ^        ^
                     |      L_tail < 0 (Downforce)                   |        | L_tail > 0 (Trim Lift!)
        ======[CG]===[AC]========+===                   ======[AC]==[CG]======+===
                                 v
      High Trim Drag + Lower Sustained Turn           Negative Trim Drag + +18% Sustained Turn!
```

* **Unlocking Negative Subsonic Static Margin (`F-16`, `Mirage 2000`, `Su-27`, `JAS 39 Gripen`):**
  When the player equips an **Analog Quad-Redundant (`F-16A`)** or **Digital Fly-By-Wire (`F/A-18`, `Mirage 2000`)** flight control system (`FlightControlType::FlyByWireAnalog` / `FlyByWireDigital`), `AircraftDesign` permits a negative subsonic static margin ($\text{StaticMargin}_{M < 0.9} \in [-0.10, +0.02]$):
  1. **Trim Lift Bonus:** In maneuvering flight, the horizontal tail or canard generates **positive upload** ($L_{\text{tail}} > 0$), reducing main-wing lift burden and cutting transonic/high-$g$ trim drag by **`15%–25%`**:
     $$C_{D,\text{trim}}(\text{SM}) = C_{D,\text{trim},0} \cdot \max\left(0.15,\; 1.0 + 6.5 \cdot \text{SM}\right)$$
  2. **Leading-Edge Root Extensions (`LERX`) & Close-Coupled Canards:** Combining `FBW` with `LERX` (`F-16`, `F/A-18`, `MiG-29`, `Su-27`) or unstable close-coupled canards (`Viggen`/`Gripen`/`Rafale`/`Typhoon`/`J-10`) generates stable vortex lift up to $\alpha = 26^\circ\text{--}32^\circ$, boosting instantaneous turn rate by **`+3.5 to +5.0 deg/s`** without departure spin risk.
  3. **Software Failure Mode in Flight Test (`Module 03`):** Early `FBW` control laws introduce **PIO (Pilot-Induced Oscillation) & Control Law Phase Lag** risk during Phase 1 Flight Testing, requiring dedicated digital iron-bird rig hours to debug before fleet release.

### 4.2 High-T/W Modular Turbofans (`F100`/`F110`/`AL-31F`/`RD-33`/`M88`) & FADEC
* **The `8:1` Thrust-to-Weight Milestone:** Core hot-section cooling (directionally solidified & single-crystal turbine blades) raises `TurbineInletTemp_K` to `1,650–1,800 K`, doubling engine thrust-to-weight ratio from `4.5:1` (`J79`) to **`7.5:1–8.5:1`** (`F100-PW-100/220`, `F110-GE-100`, `AL-31F`), allowing aircraft gross thrust-to-weight $(T/W)_{\text{combat}} > 1.05$ (vertical acceleration!).
* **The "Great Engine War" (`F100` vs `F110`) & Modular Maintenance:** Early high-performance turbofans pushed to maximum temperature suffer rapid hot-section Thermal Fatigue (`TBO_hours` dropping to `250 hr`). Unlocking **Full Authority Digital Engine Control (`FADEC`)** eliminates throttle-transience stalls and boosts `engine_reliability` by **`+18%`**, while **Modular Engine Architecture** allows squadron mechanics to swap fan/core/turbine modules on the flight line (`MMH/FH -2.8`).

### 4.3 All-Aspect IR Missiles, Look-Down BVR & Composite Structures
* **All-Aspect Cooled IR Seekers (`AIM-9L/M`, `R-73 / AA-11 Archer`, `Magic 2`):** Indium-antimonide cooled seekers expand IR missile engagement from a narrow $\pm 30^\circ$ rear-tail cone to **`360°` all-aspect frontal engagements** (`seeker_fov_bonus = 2.4x`), while Soviet helmet-mounted cueing (`Shchel-3UM` + `R-73`) dominates within-visual-range (`WVR`) high-off-boresight (`HOBS`) snapshots (`Module 21 §2.2`).
* **Monopulse SARH & Early Active Radar BVR (`AIM-7M`, `R-27R/ER`, `Skyflash`, `AIM-54C`):** Inverse-monopulse seekers resist Era II noise jammers, making BVR first-look/first-shot lethal against non-stealth targets.
* **Carbon-Fiber Composite Skins (`AV-8B`, `F/A-18`, `Mirage 2000`):** Introducing 10%–28% carbon-epoxy composite wet wings and tail skins reduces structural weight by **`7%–12%`** and eliminates metal fatigue cracks, at the cost of autoclave tooling capex (`+$25M` per facility line).

---

## 5. Part D: Era IV (1990–2010) — Stealth, "The Last Supper" M&A & 5th-Gen Dominance

The collapse of the Soviet Union and Operation Desert Storm (1991) usher in two simultaneous earthquakes: the **5th-Generation Stealth/Supercruise/AESA Revolution** (`F-117`, `B-2`, `YF-22/YF-23` $\rightarrow$ `F-22A`, `JSF X-32/X-35` $\rightarrow$ `F-35`, `Su-47/T-50`, `J-20`) and the **Post-Cold War Defense Consolidation ("The Last Supper", 1993)**.

### 5.1 3-Aspect Radar Cross Section (`RCS`) Physics & The Internal Bay Mandate
In Eras I–III, aircraft radar cross section ($\sigma$, measured in $\text{m}^2$ or $\text{dBsm} = 10\log_{10}(\sigma/\text{m}^2)$) is a rough function of physical wetted area ($+3\text{ to }+15\text{ dBsm}$). In Era IV, the aerodynamic solver computes a **3-Aspect `RCS` Vector** (`rcs_frontal_dbsm`, `rcs_beam_dbsm`, `rcs_rear_dbsm`):

$$\text{RCS}_{\text{aspect (dBsm)}} = 10 \log_{10}\!\left(\sigma_{\text{planform\_edges}} + \sigma_{\text{cavity\_intake}} + \sigma_{\text{fuselage\_chine}} + \sigma_{\text{external\_stores}} + \sigma_{\text{nozzle}}\right) - \Delta\text{RAM}_{\text{dB}}$$

| Morphological Design Choice | Frontal RCS Impact ($\Delta\text{dBsm}$) | Beam / Rear RCS Impact | Aerodynamic, Weight & Maintenance Trade-Off |
| :--- | :--- | :--- | :--- |
| **Planform Edge Alignment & Serrated Doors** | `-12 dBsm` | `-8 dBsm` (beam spike narrowed) | Restricts wing/tail sweep to parallel angles (e.g., $\pm 42^\circ$ on `F-22`), imposing `-4%` subsonic $L/D$. |
| **Canted Twin Tails + Chined Forebody** | `-6 dBsm` | `-10 dBsm` (eliminates $90^\circ$ corner reflector) | Generates strong forebody vortex lift at high $\alpha$; `+3%` fuselage structural weight. |
| **Serpentine S-Duct Intake / Radar Blocker** | **`-15 dBsm`** (hides compressor face!) | `-3 dBsm` | `-2.5%` intake pressure recovery at Mach 1.8+; `+4%` internal volume consumption. |
| **Internal Weapons Bay (`InternalLoBay`)** | **`-18 dBsm`** vs external pylons | **`-14 dBsm`** | Adds `+650 to +1,100 lb` bay door/bulkhead weight and `+18%` fuselage cross-section $A_{\max}$ (raising transonic wave drag unless area-ruled!). Carrying even **one** external pylon ("Beast Mode") immediately resets frontal RCS to `>= +1.5 dBsm`! |
| **2D Pitch-Vectoring / Serrated Low-IR Nozzle** | `-2 dBsm` | **`-12 dBsm` rear RCS** & **`-55%` IR signature** | `+280 lb` per nozzle (`F119` vs axisymmetric `F135`); `-1.5%` gross nozzle thrust coefficient. |
| **Radar Absorbent Material (`RAM`) Coating** | `-6 to -10 dBsm` | `-6 to -10 dBsm` | Early Era IV RAM (`F-117`/`B-2`/`F-22`) adds **`+6.5 to +11.0 MMH/FH`** and degrades in heavy rain/salt fog until late-2000s baked-in fiber-mat skins (`F-35`). |

* **The Radar Range Fourth-Root Law in `Module 21` Combat:**
  Because radar detection range scales with the **fourth root of target RCS** ($R_{\text{detect}} \propto \sigma^{1/4}$), reducing frontal RCS from $+5\text{ dBsm}$ ($\approx 3.16\text{ m}^2$, `F-15C`) to $-30\text{ dBsm}$ ($0.001\text{ m}^2$, `F-22A`) slashes enemy radar detection range by **`82%`** ($0.000316^{1/4} \approx 0.133$), guaranteeing first-look, first-shot BVR lethality (`Module 21 §2.1`).

### 5.2 Supercruise, 2D/3D Thrust Vectoring & AESA Sensor Fusion
* **Supercruise Evaluation (`supercruise_mach`):** `PerformanceReport` computes maximum sustained dry (non-afterburning) supersonic Mach at $35,000\text{--}45,000\text{ ft}$ where $T_{\text{mil}}(M, h) \ge D_{\text{clean\_internal}}(M, h)$. Achieving `supercruise_mach >= 1.5` (`F-22A` with `F119-PW-100` low-bypass `BPR 0.30` turbofans) triples supersonic combat radius compared to afterburning dash (which burns fuel at $\text{SFC}_{\text{AB}} \approx 1.95\text{ lb/(lbf}\cdot\text{hr)}$) and denies enemy SAMs time to complete engagement loops.
* **2D/3D Thrust Vectoring (`TVC`):** Equipping `NozzleType::Vectoring2D` (`F-22`) or `Vectoring3D` (`Su-30MKI`, `Su-35S`, `F-15 ACTIVE`) deflects engine thrust $\pm 15^\circ\text{--}20^\circ$, unlocking **Post-Stall Maneuverability (`Herbst / Pugachev Cobra / Kulbit`)** up to $\alpha = 60^\circ$ (`+28%` WVR dogfight snapshot score) and providing pitch trim authority at Mach 1.6+ without elevator deflection drag.
* **AESA Radars, IRST & Cooperative Datalinks (`Link-16` / `MADL`):** **Active Electronically Scanned Array (`AESA`)** radars (`APG-77`, `APG-81`, `RBE2-AA`, `Irbis-E`) use $1,000\text{--}2,000$ solid-state Transmit/Receive (`T/R`) modules to hop frequencies 1,000 times per second (**Low Probability of Intercept / `LPI`** — engaging targets without triggering Era III RWRs!), achieve `2,000+ hr` MTBF, and fuse tracks across friendly aircraft via `Link-16` / `MADL`.

### 5.3 Post-Cold War "Last Supper" Defense Consolidation & M&A (1991–2000)
When the Cold War ends (or a superpower tension drop event triggers), domestic procurement budgets contract by **`-45%`**, and active RFPs shrink from 2–3 new fighter starts per decade to **1 existential winner-take-all mega-program per decade (`ATF`, `JSF`)**:
* **The M&A Consolidation Window (`Module 05` Extension):** Cash-rich primes can acquire distressed or exiting aerospace divisions (**General Dynamics Fort Worth**, **Grumman**, **Northrop**, **McDonnell Douglas**, **Rockwell**, **Vought**, **British Aerospace**):
  1. **Absorbing Capabilities & IP:** Acquiring a rival transfers their accumulated `TechTree` nodes (e.g., Lockheed acquiring GD's Fort Worth `F-16` production line; Northrop acquiring Grumman's carrier/electronics heritage; Boeing merging with McDonnell Douglas).
  2. **Overhead Rationalization vs Debt Leverage:** Consolidating two engineering workforces cuts combined fixed facility overhead by **`-30%`**, but taking on acquisition debt just before losing a binary mega-RFP (`JSF`) risks corporate default unless sustained by legacy upgrade/SLEP modification contracts (`F-16V`, `F-15EX`).

---

## 6. Part E: Era V (2010–2030) — UCAVs, Loyal Wingmen & 6th-Gen Adaptive Systems

Era V extends the simulation into modern and near-future air combat (`XQ-58A Valkyrie`, `MQ-28 Ghost Bat`, `GJ-11 Sharp Sword`, `B-21 Raider`, `NGAD`, `GCAP`, `FCAS/SCAF`), where manned-unmanned teaming (`MUM-T`), directed-energy defense, and adaptive propulsion redefine the airframe.

### 6.1 Unmanned Combat Aerial Vehicles (`UCAV`) & `crew = 0` Physics
Setting `AircraftDesign.crew = 0` and equipping an **Autonomous AI Mission Core (`AutonomyTier::DatalinkRemotelyPiloted` or `AutonomyTier::OnboardTacticalAI`)** fundamentally alters `Module 02` airframe physics:
* **Cockpit, Canopy & Life-Support Elimination:** Removes ejection seat, canopy bow, armored tub, environmental control/OBOGS, and instrument displays—saving **`1,400–2,200 lb` of fixed mass** and reducing forward fuselage cross-sectional area $A_{\max}$ by **`18%`**, unlocking tailless flying-wing planforms (`Planform::TaillessFlyingWing`) with all-aspect broadband stealth (`rcs_frontal_dbsm <= -38 dBsm`, `rcs_beam_dbsm <= -28 dBsm`).
* **Breaking the Human $9g$ Physiological Limit:** Without a human pilot subject to G-LOC, an autonomous airframe can be stressed to **`n_max = 12.0g..15.0g`**, enabling kinematics that physically out-turn incoming missiles.
* **Electronic Warfare Spoofing & Cyber-Link Vulnerability:** Early datalinked UCAVs (`DatalinkRemotelyPiloted`) suffer catastrophic mission abort if enemy EA pods jam their satellite/line-of-sight command link (`jamming_abort_prob`). Overcoming this requires investing in **`OnboardTacticalAI`**, which carries a steep software NRE cost and triggers **Autonomous ROE Political Scrutiny** in `Module 04` Congressional hearings if a software glitch causes friendly-fire during `Module 03` operational evaluation!

### 6.2 Collaborative Combat Aircraft (`CCA` / "Loyal Wingman") Doctrine
Era V RFPs introduce **System-of-Systems Procurement**: a manned 5th/6th-Gen command fighter ("Quarterback") controls `2–4` **Attritable Collaborative Combat Aircraft (`CCA`)** priced at **`15%–25%`** of a manned fighter's flyaway cost (`$15M–$30M` in FY2025 dollars):
* **Attritable Design Philosophy:** Designed for a `1,500-hour` airframe life (vs `8,000 hr` for manned fighters) using automated composite tape-laying and digital-twin manufacturing (`Module 06`), CCAs act as forward sensor nodes, electronic decoys, or flying missile magazines in `Module 21` combat sorties, absorbing front-line SAM attrition so manned command aircraft survive at `99%+` rates.

### 6.3 Variable-Cycle Adaptive 3-Stream Engines (`VCE` — `XA100` / `XA101`)
Era V propulsion culminates in the **Adaptive Variable-Cycle Engine (`EngineCycle::AdaptiveThreeStream`)**:
* **The Third Bypass Stream:** By dynamically modulating fan bypass doors between a **High-Thrust Mode** (`BPR = 0.25` for Mach 2+ supercruise and maximum combat $P_s$) and a **High-Efficiency Cruise Mode** (`BPR = 0.85` for subsonic loiter), a single engine achieves **`+25%` subsonic range (`-20%` cruise SFC)**, **`+10%` supersonic thrust**, and **`2.0x` thermal heat-sink capacity** (using the outer third air stream to cool high-kilowatt AESA/EW/Directed-Energy lasers without ram-air drag scoops!).

---

## 7. Zero-Breakage Schema Forward-Compatibility Proof (1945–2030)

All institutional archetypes and Era II–V technologies slot into the existing Modules 01–09 schemas via **clean optional/defaulted extensions**, requiring **zero breaking changes** to the Era I (1945–1960) baseline structs:

| Core Struct (Module) | Era I Baseline Fields (Unchanged) | Additive Era II–V / Multi-Nation Fields (Defaulted in Era I) |
| :--- | :--- | :--- |
| **`CompanyState`** (`Mod 01/05`) | `cash`, `facilities`, `engineering_teams`, `reputation` | `nation_profile: NationProfile`, `politburo_authority: Option<f64>`, `assigned_gaz_plants: Vec<GazFactoryId>`, `catchup_rung: u8` (`default = 4`) |
| **`AircraftDesign`** (`Mod 02`) | `wing`, `fuselage`, `empennage`, `engines`, `avionics`, `weapons`, `crew` (`1..2`) | `vg_params: Option<VariableSweepParameters>`, `flight_control: FlightControlType` (`Mechanical`), `static_margin_subsonic: f64` (`+0.06`), `stealth_features: StealthConfig` (`None`), `internal_weapons_bay: bool` (`false`), `autonomy_tier: Option<AutonomyTier>` (`crew = 0` enabled in Era V) |
| **`EngineSpec`** (`Mod 02`) | `thrust_dry`, `thrust_ab`, `sfc_dry`, `sfc_ab`, `weight`, `diameter`, `reliability` | `cycle_type: EngineCycle` (`Turbojet` \| `AfterburningTurbofan` \| `AdaptiveThreeStream`), `bypass_ratio: f64` (`0.0`), `fadec_equipped: bool` (`false`), `nozzle_vectoring: NozzleType` (`Fixed`), `thermal_sink_kw: f64` |
| **`PerformanceReport`** (`Mod 02`) | `max_mach`, `combat_radius_nm`, `sustained_turn_deg_s`, `climb_rate_fpm`, `unit_cost` | `supercruise_mach: f64` (`< 1.0` in Era I–III), `rcs_frontal_dbsm: f64`, `rcs_beam_dbsm: f64`, `rcs_rear_dbsm: f64`, `ir_signature_index: f64`, `look_down_shoot_down_capable: bool`, `lpi_sensor_fusion_score: f64` |
