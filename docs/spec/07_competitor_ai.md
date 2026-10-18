# 07 — Competitor AI, Pre-Bid Intelligence Rumors, and Named Engine Vendors

> Status: v1.0 (Reference Implementation Verified). Owner: Module 07 (`sim/mic/ai/`).
> Conforms to: [`00_conventions.md`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/00_conventions.md) v1.2 (Locked Decisions D1–D10).

---

## 1. Purpose & Player Fantasy

In *Military-Industrial Complex: Jet Age*, the player does not bid against faceless random number generators. They compete against **12 named historical US airframers**—Lockheed (*Kelly Johnson*), North American (*Edgar Schmued / Harrison Storms*), Republic (*Alexander Kartveli*), Convair (*Frank Davis*), McDonnell (*Kendall Perkins*), Grumman (*Leroy Grumman / Dick Hutton*), Douglas (*Ed Heinemann*), Vought (*Rex Beisel / John Russell Clark*), Northrop (*Jack Northrop / Welko Gasich*), Bell (*Robert Woods*), Curtiss-Wright (*Don Berlin*), Martin, and Boeing—and **5 named US jet engine manufacturers** (Pratt & Whitney, General Electric, Allison, Westinghouse, and Curtiss-Wright).

### Core Player Decisions & Trade-Offs
1. **Reading Rival Doctrine & Signatures**: Knowing that Convair favors tailless supersonic deltas while Grumman and McDonnell specialize in rugged carrier aircraft lets an observant player anticipate which RFPs will have fierce competition and where a niche performance advantage (e.g., combat radius vs. raw Mach) can win.
2. **Pre-Bid Intelligence Investment (Locked Decision D10)**: Before `proposal_due`, the player sees free trade-press rumors (*Aviation Week* / *Aero Digest*) with wide error bars (`±11%` Mach, `±18%` combat radius, `±20%` unit price). Spending cash and Political Capital (`PC`) on **Level 1 Washington Liaison Inquiries** (`$25,000 + 2 PC`) or **Level 2 Deep Technical Intelligence** (`$85,000 + 6 PC`) tightens rival uncertainty bands (`sigma`) and uncovers stealth entries before the player locks their own bid price and performance promises.
3. **Surviving the Two-Stage Hardware Fly-Off (Locked Decision D6)**: Rival finalists build physical prototypes (`run_prototype_rollout`), run wind-tunnel and flight-test campaigns (`run_flight_test_programme`), and must decide whether to spend time fixing hidden transonic/supersonic flaws or rush to fly-off with operational placards.
4. **Selecting Named Engine Vendors (Locked Decision D9)**: When commissioning a custom turbojet, the player chooses between **Pratt & Whitney** (dual-spool low SFC & `1.25x` MTBF durability at premium cost), **General Electric** (variable-stator high-Mach afterburner thrust & fast supersonic schedule), **Allison** (GM mass-production `0.90x` unit cost), **Westinghouse** (ultra-lightweight compact axial layout with `1.45x` schedule/shortfall risk, echoing the historical J40 crisis), and **Curtiss-Wright** (`42%–48%` R&D discount on licensed derivatives like the J65 Sapphire).

---

## 2. Scope

### 2.1 MVP In-Scope (USA, 1945-01-01 → 1960-12-31)
- **13 US Airframers**: 12 active AI rivals when the player selects a historical airframer, or all 13 when the player founds a custom startup (`load_ai_airframers`).
- **29 Historical Chief Designers**: Automatic historical succession (`_update_chief_designer_succession`) updating research branch bonuses and design modifiers (`cd0_refinement_factor`, `prototype_build_time_factor`, `structural_mass_factor`).
- **Doctrine-Weighted Tech Tree R&D**: Deterministic scoring (`score_tech_node_for_ai`) and engineer allocation (`select_ai_research_projects`) across Module 03 (`CompanyTechState`).
- **Synchronized Economy & Dynamic/Historical Market Exit**: Monthly corporate financial settlement via Module 04 (`step_company_month`); historical prime-fighter exit rules for Curtiss-Wright (1949), Bell (1952), Boeing (1953), and Martin (1954) with alt-history override (`alt_history_contract_keeps_alive = true`).
- **Parametric Aircraft Design Synthesis & Local Search**: `generate_ai_design_for_rfp` producing `TechContext`-compliant `AircraftDesign` dicts evaluated by Module 01 (`mic.perf.evaluate`).
- **RFP Bidding & Two-Stage Fly-Off Progression (D6)**: `prepare_all_ai_entries_for_rfp` and `step_all_ai_flyoff_finalists` integrated with Module 05 (`ProposalBid`, `BidderContext`) and Module 06 (`LineageTestState`).
- **Pre-Bid Trade-Press Rumors (D10)**: `generate_pre_bid_rumors(rfp, ai_entries, inquiry_level, rng)` with 3 intelligence tiers (`0, 1, 2`).
- **Named US Engine Vendors (D9)**: `get_available_catalog_engines`, `quote_custom_engine`, and `compare_vendor_quotes`.

### 2.2 Out of Scope for MVP
- Foreign airframers (MiG, Sukhoi, Hawker, Dassault, Avro Canada) as active USAF/USN prime bidders (deferred to Phase 2+ NATO/export modules).
- Hostile corporate M&A takeovers initiated by AI companies against the player.

---

## 3. Player-Facing Flow

1. **Monthly World Tick (`step_ai_company_month`)**: On the 1st of each month, every active AI airframer updates its Chief Designer, allocates engineers to up to 3 tech tree nodes matching its doctrine, advances daily research and NACA diffusion, upgrades wind tunnels when cash and era thresholds permit, and settles payroll/contracts. If an AI rival goes insolvent or hits its historical fighter-market exit year without an active fighter production contract, a trade-press news item announces its pivot to bombers/missiles or subcontracting.
2. **RFP Issuance & AI Bidder Selection (`select_ai_bidders_for_rfp`)**: When an RFP opens (`issue_date`), 3 to 6 AI airframers with matching service affinity (`USAF` vs. `USN`), sufficient engineering capacity, and appropriate technology enter the competition and begin synthesizing designs (`generate_ai_design_for_rfp`) and running pre-bid wind-tunnel tests.
3. **Pre-Bid Intelligence Window (D10, `generate_pre_bid_rumors`)**: Anytime between `issue_date` and `proposal_due`, the player opens the **Intelligence & Trade Press** tab on the RFP screen:
   - **Level 0 (Free — *Aviation Week* Rumor Mill)**: Shows approximate rival Mach, combat radius, and unit price with wide `±1σ` error bars (`source="rumor"`), plus a `15%` chance a stealth bidder is omitted.
   - **Level 1 (`$25,000 + 2 PC` — Washington Liaison Inquiry)**: Narrows `sigma` by ~40% and reveals each rival's airframe configuration (`delta-wing single-jet`, `swept-wing twin-jet`) and engine class.
   - **Level 2 (`$85,000 + 6 PC` — Deep Technical Intelligence)**: Narrows `sigma` to `4%` Mach / `7%` radius / `8%` price and guarantees 100% bidder discovery.
4. **Proposal Downselect & Two-Stage Fly-Off (D6, `step_all_ai_flyoff_finalists`)**: At `proposal_due`, AI entrants submit `ProposalBid`s. Downselected AI finalists build 2 prototypes (`run_prototype_rollout`) and fly the 6-item Module 06 flight-test syllabus (`run_flight_test_programme`), resolving discovered flaws via engineering fixes or flight-manual placards before final `evaluate_flyoff`.
5. **Custom Engine Commission Quotes (D9, `quote_custom_engine`)**: In the Propulsion Bureau, the player specifies desired dry/afterburning thrust, Mach regime, and whether the engine is a derivative, then compares side-by-side binding quotes from P&W, GE, Allison, Westinghouse, and Curtiss-Wright.

---

## 4. Data Schemas

### 4.1 `AICompanyState` (`sim/mic/ai/company_ai.py`)
Wraps Module 04 [`CompanyState`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/econ/company.py) and Module 03 [`CompanyTechState`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/tech/research.py):

| Field | Type | Units / Range | Description |
|---|---|---|---|
| `id` | `str` | snake_case | Canonical company ID (e.g. `"lockheed"`, `"convair"`). |
| `name` / `name_key` | `str` | localization key | Display name key from `airframers_us_1945_1960.json`. |
| `tier` | `str` | enum | `"major_prime"`, `"mid_prime"`, `"specialist"`, `"legacy_giant"`. |
| `company_state` | `CompanyState` | Module 04 | Synchronized cash, debt, reputation (`0..100`), engineers, facilities, contracts. |
| `tech_state` | `CompanyTechState` | Module 03 | Unlocked tech maturities (`0..1`), active R&D projects, NACA diffusion state. |
| `ai_doctrine` | `Dict[str, Any]` | `0.0..1.0` | `preferred_customers`, `speed_vs_maneuver_bias`, `aerodynamic_ambition`, `risk_tolerance`, `bid_aggression`. |
| `traits` | `Dict[str, Any]` | mixed | Merged `company_signatures[id]` + `ai_doctrine` (`delta_bias`, `sweep_bias_deg`, `tc_bias`, `twin_engine_bias`, etc.). |
| `active_designer_id` | `str` | ID | Currently active Chief Designer ID (`chief_designers_us_1945_1960.json`). |
| `active_in_fighter_market` | `bool` | bool | `True` while competing for prime fighter RFPs; `False` after exit. |
| `exit_reason` / `exit_year` | `Optional[str/int]` | year | `"insolvency"` or `"historical_pivot_to_bombers_or_missiles"`. |

### 4.2 `CompetitorRumor` (Locked Decision D10, `sim/mic/ai/rumors.py`)
Each rumor is a dictionary (`CompetitorRumor(dict)`) containing `Estimate` objects with `source="rumor"`:
```json
{
  "rfp_id": "usaf_pen_fighter_1946",
  "company_id": "republic",
  "company_name": "company.republic.name",
  "rumored_design_name": "Republic AP-100",
  "inquiry_level": 1,
  "inquiry_cost_usd": 25000.0,
  "inquiry_pc_cost": 2.0,
  "participation_confidence": 0.86,
  "is_false_lead": false,
  "configuration_hint": "swept-wing twin-jet",
  "engine_hint": "J35-A-29 (dry)",
  "max_mach_alt": { "value": 0.903, "sigma": 0.0598, "source": "rumor", "unit": "mach" },
  "combat_radius_m": { "value": 1502410.5, "sigma": 159842.1, "source": "rumor", "unit": "m" },
  "unit_flyaway_price_usd": { "value": 512400.0, "sigma": 58900.0, "source": "rumor", "unit": "usd" },
  "headline": "Trade press reports company.republic.name is readying the Republic AP-100..."
}
```

### 4.3 `CustomEngineQuote` (Locked Decision D9, `sim/mic/ai/engine_vendor_ai.py`)
Returned by `quote_custom_engine(vendor_id, target_spec, date, rng)`:
- `quote_id`, `vendor_id`, `vendor_name`, `us_code` (`"P"`, `"GE"`, `"A"`, `"WE"`, `"W"`), `specialty`, `designation` (e.g. `"XJ73-GE-1"`), `date_quoted`, `is_derivative` (`bool`).
- Promised performance & physical envelope: `promised_dry_thrust_sl_N`, `promised_ab_thrust_sl_N`, `has_afterburner`, `promised_tsfc_dry_sl` [kg/(N·s)], `promised_tsfc_ab_sl` [kg/(N·s)], `promised_mass_kg`, `promised_diameter_m`, `promised_length_m`, `promised_mtbf_h`.
- Financial & schedule terms: `unit_price_usd`, `total_dev_cost_usd`, `airframer_commission_fee_usd`, `promised_delivery_days`, `development_risk_index` (`0..1`), `schedule_slip_prob`, `shortfall_risk_prob`, and callable `engine_deck: StubEngineDeck`.


---

## 5. Algorithms & Mathematical Formulations

### 5.1 Doctrine-Weighted Tech Tree R&D (`score_tech_node_for_ai`, `step_ai_company_month`)

For an AI company $c$ at date $d$ (`current_year` $= 1945 + d / 365.25$), each unlockable `TechNode` $n$ in `TechCatalog` is scored deterministically:

1. **Horizon Filter**: Let $\Delta y = y_{\text{hist}}(n) - \text{current\_year}$. If $\Delta y > L_{\max}$, where $L_{\max} = \text{rnd\_year\_window\_lead} + \mathbb{I}(\text{ambition}_c \ge 0.90)$, then $S_{\text{tech}}(n, c) = -1$.
2. **Ahead-of-Time Multiplier**: Using Module 03 `ahead_of_time_multiplier` ($M_{\text{AoT}} \in (0, 1]$):
   $$F_{\text{AoT}} = \left(M_{\text{AoT}}(d, y_{\text{hist}}(n))\right)^{w_{\text{AoT}}}, \quad w_{\text{AoT}} = 0.45$$
3. **Doctrine, Signature, & Chief Designer Alignment**:
   $$A(n, c) = 1.0 + 1.50 \cdot B_{\text{designer}}(\text{branch}(n)) + \Delta A_{\text{branch}} + \Delta A_{\text{effects}} + \Delta A_{\text{carrier}}$$
   - $\Delta A_{\text{branch}}$: $+0.35 \cdot \text{ambition}_c$ if `branch == "aero"`; $+0.35 \cdot \text{mfg\_focus}_c$ if `branch == "manufacturing"`; $+0.25 \cdot (\text{ruggedness\_g\_bias}_c + 0.5)$ if `branch == "structures"`.
   - $\Delta A_{\text{effects}}$: $+0.85 \cdot \text{delta\_bias}_c - 0.20 (1 - \text{delta\_bias}_c)$ for delta-wing / conical-camber nodes; $+0.25 \cdot \text{speed\_bias}_c$ for high-Mach sweep, thin wing, area rule, shock spike/variable inlet, or afterburner nodes.
   - $\Delta A_{\text{carrier}}$: for carrier nodes, $+0.40 \times 1.3$ if `USN` is primary customer, $+0.40 \times 0.8$ if secondary, or $-0.45$ if USAF-only.
4. **Cost & Catch-Up Urgency**:
   $$F_{\text{cost}} = \left(\frac{500}{\max(150, \text{cost\_eng\_days}(n))}\right)^{0.25}, \quad F_{\text{catchup}} = 1 + \text{clamp}\big((-\Delta y) \cdot 0.15,\, 0,\, 0.60\big)$$
   $$S_{\text{tech}}(n, c) = \max\big(0.01,\, A(n, c) \cdot F_{\text{AoT}} \cdot F_{\text{cost}} \cdot F_{\text{catchup}}\big)$$
   Partially researched nodes receive a $1.25\times$ continuation multiplier. The top $K \le 3$ nodes receive engineering allocations proportional to $S_{\text{tech}}(n, c)$, clamped to $[15, 65]$ FTEs per project.

### 5.2 Parametric Aircraft Design Synthesis & Local Search (`generate_ai_design_for_rfp`)

Given `(company, rfp, unlocked_techs, available_engines)`:
1. **Target Extraction**: Reads target Mach $M^*$, target radius $R^*$, target turn rate $\dot{\psi}^*$, carrier flag, equipment gates, and price ceiling $P_{\text{ceil}}$ from `rfp.criteria`, `rfp.equipment`, and `rfp.budget`.
2. **Engine Selection**: Filters `available_engines` (or `get_available_catalog_engines(proposal_due)`) by `ctx.get("engine.afterburner")`, ranking engines that match $\mathbb{I}(M^* \ge 1.02 \land \text{AB unlocked})$ by maximum sea-level thrust. Selects `engine_count = 2` if `min_engines >= 2`, `twin_engine_bias >= 0.72` (e.g. McDonnell `0.88`, Northrop `0.82`), or single-engine thrust is insufficient for long-range/supersonic targets.
3. **Seed Synthesis (`_build_seed_design`)**:
   - **Planform**: Chooses `"delta"` (`taper = 0.08`, `tailless = true`) when `aero.delta_wing` is unlocked, $\text{delta\_bias}_c \ge 0.65$ (Convair `0.92`), and $M^* \ge 1.15$; otherwise `"swept"` (or `"straight"` for early subsonic negative-sweep bias).
   - **Sweep, Thickness, & Aspect Ratio**: Clamped strictly inside `TechContext` hard caps (`aero.wing_sweep_max_deg - 0.5`, `aero.thin_wing_tc_min + 0.002`, `aero.aspect_ratio_min + 0.05`) while applying `sweep_bias_deg`, `tc_bias`, and `aspect_ratio_bias`.
   - **Packaging & Fuel Volume Guard (`_clamp_fuel_to_volume`)**: Sets fuselage diameter $\ge 1.12 D_{\text{eng}}$ (multiplied by $1.36$ for twin engines) and clamps `fuel.internal_kg` to $\le 0.98 \cdot \text{max\_fuel\_capacity\_kg}$ (derived via Torenbeek wing-box + fuselage volume integration in Module 01).
4. **Coordinate Local Search**: Evaluates candidates via `mic.perf.evaluate(design, engine, tech_context)` across:
   - Wing area scales $s_S \in \{0.86, 0.93, 1.00, 1.08, 1.18\}$,
   - Sweep offsets $\Delta \Lambda \in \{-5^\circ, 0^\circ, +5^\circ\} \times$ thickness offsets $\Delta(t/c) \in \{-0.012, 0, +0.010\}$,
   - Internal fuel scales $s_F \in \{0.88, 1.00, 1.15\}$,
   maximizing:
   $$J(\text{design}) = -500 N_{\text{invalid}} + \sum_{i} w_i \left(100 \cdot \text{clamp}\!\left(\frac{s_i (v_i - T_i)}{\Delta_i}, -0.5, 1.35\right) - 4.5 \cdot \text{miss\_pct}_i\right) + 18 \cdot \text{clamp}\!\left(1.15 - \frac{C_{\text{unit}}}{P_{\text{ceil}}}, -1.5, 0.5\right) + 8 \cdot \mathbb{I}_{\text{sig}}$$

### 5.3 RFP Entry, Bid Formulation, & Two-Stage Fly-Off (`bidding_ai.py`, Locked Decision D6)

1. **Entry Propensity Score (`score_rfp_entry_for_ai`)**:
   $$S_{\text{entry}}(c, \text{rfp}) = 0.25 + 0.32 \cdot \alpha_{\text{cust}} + 0.35 \cdot \frac{\text{Rep}_{c, \text{cust}}}{100} + 0.25 \cdot \text{Cap}_c + 0.20 \cdot \text{Fit}_{\text{role}} + 0.45 \cdot \mathbb{I}_{\text{hist}} - 0.35 \cdot \mathbb{I}_{\text{no\_carrier}}$$
   Active companies with $S_{\text{entry}} \ge 0.52$ (bounded to $[3, 6]$ bidders) enter the RFP.
2. **Pre-Bid Testing & Promises (`prepare_ai_rfp_entry`)**:
   - Initializes Module 06 `LineageTestState` and runs `low_speed_tunnel` (plus `transonic_tunnel` if $M_{\max} \ge 0.90$ and unlocked) with `auto_fix_detected_flaws = true`.
   - Promises each criterion at $P_i = \mu_i + s_i \cdot (0.25 + 0.70 \cdot \text{risk\_tolerance}_c) \sigma_i$, snapping to threshold $T_i$ if within $14\%$.
   - Formulates bid price ratio:
     $$m_{\text{price}} = 0.94 - 0.14 (\text{bid\_aggression}_c - 0.50) + 0.04 \mathbb{I}_{\text{incumbent}} - 0.08 \mathbb{I}_{\text{no\_active\_contracts}}$$
3. **Stage 2 Fly-Off Progression (`run_ai_flyoff_progression`, D6)**:
   - Downselected AI finalists call `run_prototype_rollout(n_prototypes)` and `run_flight_test_programme`.
   - Flaw resolution policy: `"placard_all"` if $< 35$ days remain before fly-off deadline; `"fix_all"` if $\text{risk\_tolerance}_c \le 0.35$; else `"fix_severe_else_placard"` (fixes severity $\ge 3$, placards severity $\le 2$).
   - Populates `bid.measured_performance` (`source="flight"`), `bid.actual_first_flight_day`, and `bid.unfixed_flaw_severity_sum`.

### 5.4 Pre-Bid Trade-Press Rumors (`generate_pre_bid_rumors`, Locked Decision D10)

For inquiry level $L \in \{0, 1, 2\}$ and relative sigma table $\eta_m(L)$ (`mach_rel`, `radius_rel`, `price_rel`):
$$\sigma_m = \eta_m(L) \cdot |v_{\text{true}, m}|, \quad v_{\text{rumor}, m} = v_{\text{true}, m} + \text{clamp}(z_m, -2.2, 2.2) \cdot \sigma_m, \quad z_m \sim \mathcal{N}(0, 1)$$
Returned as `Estimate(value=v_rumor, sigma=sigma_m, source="rumor", unit=...)` inside each `CompetitorRumor`.

### 5.5 Named Engine Vendor Commissions (`quote_custom_engine`, Locked Decision D9)

Given vendor $v \in \{\text{P\&W}, \text{GE}, \text{Allison}, \text{Westinghouse}, \text{Wright}\}$, target dry/AB thrust $(T_{\text{dry}}^*, T_{\text{AB}}^*)$, Mach $M^*$, and date $t$:
- **Promised Thrust & SFC**: Applies vendor thrust bonuses $\beta_{\text{dry}, v}, \beta_{\text{AB}, v}$ (with $+3\%$ extra high-Mach AB bonus for GE at $M^* \ge 1.5, y \ge 1952$) and SFC multipliers $M_{\text{SFC}, v}$ to era baseline TSFC.
- **Mass & Envelope**: Specific mass scales from $0.046\text{ kg/N}$ (1945) to $0.032\text{ kg/N}$ (1960), multiplied by $1.16$ for afterburners and vendor `specific_weight_mult` ($0.90\times$ for Westinghouse).
- **Development Cost, Schedule, & Risk**: Scaled by raw ambition $A_{\text{eng}}$, 1950 aerospace inflation index $I_{1950}(y)$, vendor multipliers, and derivative discounts ($48\%$ dev cost / $42\%$ duration discount for Curtiss-Wright licensed derivatives).


---

## 6. Tunables Table (`sim/data/tuning/ai.json`)

| Key Path | Default | Range | Effect | Rationale |
|---|---|---|---|---|
| `company_ai.rnd_year_window_lead` | `2.5` | `[1.0, 5.0]` | Max years ahead of `historical_year` an AI researches | Prevents AI wasting FTEs on 10x AoT penalty nodes |
| `company_ai.rnd_aot_penalty_weight` | `0.45` | `[0.1, 1.0]` | Exponent on `ahead_of_time_multiplier` in R&D score | Balances historical pacing with ambitious AI leads |
| `company_ai.rnd_designer_bonus_scale` | `1.50` | `[0.5, 3.0]` | Multiplier on Chief Designer branch bonus | Channels Kelly Johnson / Kartveli into signature branches |
| `company_ai.rnd_max_concurrent_projects` | `3` | `[1, 5]` | Max simultaneous tech nodes researched by AI | Concentrates AI FTEs for timely unlocks |
| `company_ai.rnd_irad_cash_floor_usd` | `4000000.0` | `[1e6, 1e7]` | Cash floor below which AI pauses discretionary IR&D | Prevents AI self-bankruptcy from R&D burn |
| `company_ai.historical_exit_years` | `CW:1949, Bell:1952, Boeing:1953, Martin:1954` | `1948..1958` | Year each legacy firm exits prime fighter bidding if lacking fighter work | Matches historical post-WWII airframer consolidation |
| `company_ai.alt_history_contract_keeps_alive` | `true` | `bool` | Keeps historical-exit firms active if they won a major fighter contract | Rewards dynamic alt-history outcomes |
| `design_generator.area_scale_candidates` | `[0.86, 0.93, 1.0, 1.08, 1.18]` | `0.7..1.4` | Wing area multipliers searched during local optimization | Tunes wing loading for turn rate vs. high-speed drag |
| `design_generator.sweep_offset_candidates_deg` | `[-5.0, 0.0, 5.0]` | `-15..+15` | Quarter-chord sweep offsets searched (deg) | Balances wave drag Mach divergence vs. stall speed |
| `design_generator.tc_offset_candidates` | `[-0.012, 0.0, 0.010]` | `-0.03..+0.03` | Wing thickness-to-chord offsets searched | Trades supersonic wave drag against wing fuel volume |
| `bidding_ai.entry_threshold_score` | `0.52` | `[0.3, 0.8]` | Minimum propensity score to enter an RFP | Keeps AI participation realistic (`3..6` bidders) |
| `bidding_ai.min_bidders_per_rfp` / `max_bidders_per_rfp` | `3` / `6` | `2..8` | Hard bounds on AI entrants per RFP | Guarantees competitive fly-offs without UI clutter |
| `bidding_ai.price_markup_base` | `0.94` | `[0.80, 1.10]` | Baseline ratio of bid price to estimated cost | Reflects aggressive 1950s prime bidding |
| `bidding_ai.promise_sigma_k_base` / `risk_slope` | `0.25` / `0.70` | `0.0..1.5` | Overclaim multiplier on `sigma` as a function of `risk_tolerance` | Models conservative vs. aggressive brochure promises |
| `bidding_ai.flyoff_placard_days_remaining_threshold` | `35` | `[15, 90]` | Days remaining below which AI placards flaws instead of redesigning | Prevents AI missing fly-off evaluation deadlines |
| `rumors.inquiry_costs_usd` | `L0:0, L1:25k, L2:85k` | `$0..$250k` | Cash cost per pre-bid intelligence inquiry tier (D10) | Meaningful pre-bid intelligence sink |
| `rumors.sigma_multipliers_by_level` | `L0:11%/18%/20%, L1:6.5%/11%/12%, L2:4%/7%/8%` | `0.02..0.30` | Relative `sigma` on Mach, combat radius, and unit price | Guarantees strictly shrinking error bars across `0 -> 1 -> 2` |
| `engine_vendor_ai.base_commission_dev_cost_1950_usd` | `14000000.0` | `$5M..$40M` | Baseline 1950 USD R&D cost for a custom turbojet (D9) | Calibrated to 1950s J57/J79 development budgets |
| `engine_vendor_ai.derivative_dev_cost_discount` | `0.42` (`0.48` Wright) | `0.20..0.65` | Development cost reduction for derivative/licensed engines | Models Curtiss-Wright J65 Sapphire licensed advantage |

---

## 7. Edge Cases & Failure Modes

1. **Strict `TechContext` Cap & Packaging Enforcement**: `generate_ai_design_for_rfp` clamps wing sweep (`<= max_sweep - 0.5`), thickness (`>= min_tc + 0.002`), aspect ratio (`>= min_ar + 0.05`), load factor, titanium fraction, avionics level, and weapon unlocks to the company's `TechContext`, and invokes `_clamp_fuel_to_volume` after every coordinate perturbation so `validate_design` never fails with `TECH_CAP:*` or `PACKAGING:*`.
2. **Transonic Tunnel Choking Guard**: Before `testing.transonic_tunnel` (slotted-throat tunnel, 1950) is unlocked, `prepare_ai_rfp_entry` only runs `low_speed_tunnel` so AI rivals experience the same transonic wave-drag uncertainty (`cdw` prior variance) as the player.
3. **Minimum Bidder Guarantee Under Market Consolidation**: Even if several airframers exit the fighter market by the late 1950s, `select_ai_bidders_for_rfp` falls back to the top `min_bidders_per_rfp` (`3`) remaining active airframers so every RFP remains contested.
4. **Module 01 `ps_grid` Shape Normalization**: `PerformanceReport.to_dict()` outputs `ps_grid` as `{"mach": [...], "alt_m": [...], "ps_mps": [[...]]}`, whereas Module 06 `compute_true_performance_report` scales a 2D array; `prepare_ai_rfp_entry` normalizes `nom_dict["ps_grid"]` to its 2D `ps_mps` matrix before initializing `LineageTestState`.
5. **Calendar Engine Registration**: `build_deck_from_calendar_entry` registers every off-the-shelf calendar engine (`J33-A-9` through `J75-P-5`) into `HISTORICAL_ENGINES` so `mic.perf.evaluate(design)` resolves any AI-selected `engine_id` without requiring an explicit deck object.

---

## 8. Golden Test Vectors

All golden vectors are generated deterministically by the Python reference oracle and verified to relative tolerance `1e-6` in [`sim/tests/test_ai.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/tests/test_ai.py):

1. [`sim/golden/ai_competitor_behaviors.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/golden/ai_competitor_behaviors.json):
   - Initial non-player AI company count (`12` when player is `north_american`).
   - Month 1 (`1945-01`) `step_ai_company_month` reports (`active_designer_id`, `research_allocations`, `ending_cash_usd`) for `lockheed`, `convair`, `grumman`, and `curtiss_wright`.
   - Full `usaf_pen_fighter_1946` AI entries (`rfp_1946_entries`), Stage 1 proposal downselect finalists (`usaf_pen_fighter_1946__republic`, `usaf_pen_fighter_1946__boeing`, `usaf_pen_fighter_1946__northrop`), Stage 2 `flyoff` progression results (`rfp_1946_flyoff_finalists`), and fly-off winner (`republic`).
2. [`sim/golden/ai_rumors_and_vendors.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/golden/ai_rumors_and_vendors.json):
   - Pre-bid `CompetitorRumor` vectors across `inquiry_level` `0`, `1`, and `2` on `usaf_pen_fighter_1946`.
   - 1952 clean-sheet supersonic afterburning turbojet quotes (`44 kN` dry / `66 kN` AB, Mach `1.8`) across all 5 US engine vendors (`pratt_whitney`, `general_electric`, `allison`, `wright`, `westinghouse`), plus Curtiss-Wright's licensed derivative quote (`is_derivative = true`).

---

## 9. Cross-Module Interactions

- **Inputs from Module 01 (`mic.aero`, `mic.perf`)**: `evaluate(design, engine, tech_context) -> PerformanceReport`, `validate_design`, `derive_aircraft_geometry`, `StubEngineDeck`.
- **Inputs from Module 03 (`mic.tech`)**: `TechCatalog`, `TechNode`, `TechContext`, `CompanyTechState`, `ahead_of_time_multiplier`, `step_company_tech_day`, `required_techs`.
- **Inputs from Module 04 (`mic.econ`)**: `CompanyState`, `step_company_month`, `aero_cost_index_1950`.
- **Inputs/Outputs with Module 05 (`mic.procurement`)**: Reads `ProgramSpec` / `CriterionSpec`; produces `ProposalBid` and `BidderContext` for `evaluate_proposals` and `evaluate_flyoff`.
- **Inputs/Outputs with Module 06 (`mic.testing`)**: Initializes `LineageTestState`, runs `run_tunnel_or_ground_campaign`, `run_prototype_rollout`, `run_flight_test_programme`, `compute_estimate_report`, and `compute_true_performance_report`.
- **Inputs from Module 10 (`sim/data/companies/`)**: Reads `airframers_us_1945_1960.json`, `chief_designers_us_1945_1960.json`, and `engine_makers_us_1945_1960.json`.

---

## 10. Validation Results

Verified via `.venv/bin/python -m pytest sim/tests/test_ai.py`:
- **7 / 7 test suites passing (`100%`)**:
  - `test_load_ai_airframers_and_doctrine_rnd`: 13 total / 12 non-player airframers loaded; Grumman scores carrier tech higher than Convair; monthly R&D allocations deterministic.
  - `test_historical_exit_and_alt_history_contract_survival`: Curtiss-Wright exits in 1949 when without fighter contracts, and survives when holding a major production contract.
  - `test_design_generator_validity_and_company_signatures`: 0 validation errors on all generated AI designs; Convair synthesizes a tailless delta (`planform_type == "delta"`), McDonnell synthesizes a twin-engine layout (`count == 2`).
  - `test_bidding_ai_and_two_stage_flyoff_progression`: Full two-stage `flyoff` lifecycle (D6) from proposal downselect to prototype rollout and flight test.
  - `test_pre_bid_rumors_inquiry_levels`: `sigma` strictly decreases across `L0 > L1 > L2` for Mach, combat radius, and unit price (D10).
  - `test_engine_vendor_quotes_and_specialties`: P&W lowest dry SFC & highest MTBF, GE highest supersonic AB thrust & throttle ratio, Allison lowest unit price, Westinghouse lightest weight & highest risk, Curtiss-Wright `< 0.60x` derivative R&D cost (D9).
  - `test_golden_vectors_reproduction`: 100% bit/float match (`rel=1e-6`) against `sim/golden/ai_competitor_behaviors.json` and `sim/golden/ai_rumors_and_vendors.json`.

---

## 11. Open Questions & Cross-Module Change Requests

- **None for MVP**: All Module 07 contracts (`AICompanyState`, `AICompetitorEntry`, `CompetitorRumor`, `CustomEngineQuote`) conform strictly to `00_conventions.md` v1.2 without requiring schema changes in other modules.
