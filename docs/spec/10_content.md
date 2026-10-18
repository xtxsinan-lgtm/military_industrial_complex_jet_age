# 10 — Historical Content: Companies, Chief Designers, Display Strings, and Designation Rules (1945–1960)

> Status: v1.0. Owner: Module 10.
> Data files: [`sim/data/companies/airframers_us_1945_1960.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/companies/airframers_us_1945_1960.json), [`sim/data/companies/engine_makers_us_1945_1960.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/companies/engine_makers_us_1945_1960.json), [`sim/data/companies/startup_presets.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/companies/startup_presets.json), [`sim/data/companies/chief_designers_us_1945_1960.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/companies/chief_designers_us_1945_1960.json), [`sim/data/names/companies_and_people.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/names/companies_and_people.json), [`sim/data/names/tech_and_components.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/names/tech_and_components.json), [`sim/data/names/designation_rules_us_pre1962.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/names/designation_rules_us_pre1962.json).

---

## 1. Purpose & Player Fantasy

In January 1945, the American aviation industry stands at a precipice. Wartime production contracts for tens of thousands of piston fighters and bombers are being cancelled overnight, while the jet revolution renders every existing production line obsolete. Some wartime titans (Curtiss-Wright, Bell) will fail to transition to series jet fighter production; scrappy newcomers (McDonnell) and focused engineering houses (North American, Lockheed, Douglas El Segundo, Convair, Grumman, Republic, Vought, Northrop) will define the Jet Age.

Module 10 provides the **historical soul, asymmetric starting conditions, engineering leadership personalities, and authentic US military nomenclature** for the 1945–1960 campaign:

1. **Asymmetric Historical Starting Positions**: Playing **North American** or **Lockheed** gives the player strong cash reserves, a private high-speed wind tunnel (`wind_tunnel_level: 2`), desert test-site access, and deep USAAF trust (`reputation.USAF >= 0.90`). Playing **McDonnell** in 1945 means starting with a modest St. Louis plant (`115,000 m²`), `$14M` cash, and no transonic tunnel—forcing smart bets on US Navy twin-engine carrier jets (`FH-1`, `F2H`). Playing **Grumman** ("The Iron Works") grants `0.95` USN BuAer reputation and early carrier-suitability know-how, but low USAF clout.
2. **Custom Startup Presets**: Players who want to write their own history can found a custom 1945 aircraft manufacturer using one of four balanced archetypes: *Experimental Skunk-Team Spinoff*, *Midwest Wartime Subcontractor*, *Langley Aerodynamics Syndicate*, or *Pacific Industrialist Aviation Venture*.
3. **Chief Designers with Modest, Authentic Engineering Traits**: Real historical engineering leaders—Edgar Schmued, Kelly Johnson, Ed Heinemann, Alexander Kartveli, Frank Davis, Kendall Perkins, Bill Schwendler, Russ Clark, Jack Northrop, Robert Woods, George Schairer, Gerhard Neumann, and Luke Hobbs—provide realistic, bounded (`±3%` to `±15%`) modifiers to branch research speed, prototype build time, aerodynamic drag cleanup, and structural weight discipline.
4. **Data-Driven Display Names & Pre-1962 US Military Designation Generator**: Per Locked Decision D4 (`00_conventions.md` §1), zero display strings are hard-coded in code. Every company, person, tech node, and component resolves through `sim/data/names/*.json` (including a one-flag `fictional_fallback_overrides` map for legal/trademark safety). When a prototype is ordered or enters production, the designation engine automatically assigns authentic pre-1962 USAAF/USAF (`XP-86` → `F-86A`, `YF-100A` → `F-100A`) or US Navy BuAer (`XFH-1` → `FH-1`, `XF2H-1` → `F2H-2N`, `XF8U-1` → `F8U-1`) designations and company-authentic popular names (*Sabre*, *Starfighter*, *Thunderchief*, *Phantom II*, *Skyray*, *Crusader*).

---

## 2. Scope

### 2.1 MVP In-Scope (USA, 1945–1960)
- **13 historical US fighter/strike airframers**: North American, Lockheed, Republic, Convair, McDonnell, Grumman, Douglas, Chance Vought, Northrop, Bell, Curtiss-Wright, Martin, Boeing.
- **5 historical US jet engine manufacturers**: General Electric, Pratt & Whitney, Allison, Westinghouse, Wright Aeronautical.
- **4 custom player startup presets** for founding a new company on 1945-01-01.
- **29 chief designers** (25 historical airframe/engine leaders + 4 startup archetypes) with bounded, data-driven research and design modifiers.
- **Complete display string tables** (`companies_and_people.json`, `tech_and_components.json`) + legal-safe fictionalized company fallback names.
- **Pre-1962 US military designation rules** (`designation_rules_us_pre1962.json`):
  - USAAF `P-` to USAF `F-` transition on **1948-06-11** (`XP-`/`YP-`/`P-` before June 11, 1948; `XF-`/`YF-`/`F-` on and after June 11, 1948).
  - US Navy BuAer `<Status><Type><ModelNumber><ManufacturerLetter>-<Variant><SubMod>` system (`FH-1`, `F2H-2`, `F9F-6`, `F4D-1`, `F8U-1`, `F4H-1`).
  - US joint turbojet/turbofan numbering (`J` + even numbers for USN BuAer, `J` + odd numbers for USAAF/USAF, plus `-<MfgCode>-<Dash>`).

### 2.2 Out-of-Scope for MVP
- Post-1962 Tri-Service McNamara designation reset (`F-4B`, `F-8E`, `F-111A`, instituted September 18, 1962).
- Foreign manufacturers (Mikoyan-Gurevich, Sukhoi, Lavochkin, Yakovlev, Hawker, English Electric, Dassault, Saab) — reserved for Post-MVP expansions.

---

## 3. Player-Facing Flow

1. **Campaign New-Game Selection Screen**:
   - The player selects either a **Historical Prime Contractor** (11 playable by default; Martin and Boeing optional/AI-focused) or **Found Custom Manufacturer** (choosing one of the 4 startup presets, custom company name, USN manufacturer letter, and headquarters city).
   - The selection card displays 1945-01-01 starting cash, factory floor area (`m²`), wind tunnel level (`0` = none/NACA-dependent, `1` = subsonic tunnel, `2` = high-speed compressible tunnel), engineering staff breakdown (`aero`, `structures`, `propulsion`, `systems`), USAF/USN/export reputation bars, and active Chief Designer profile.
2. **Chief Designer Management & Succession**:
   - Each company has an active Chief Designer whose `research_branch_bonuses` feed directly into `CompanyTechState.designer_branch_bonuses` (Module 03) and whose `design_modifiers` apply to prototype construction speed and baseline structural/drag refinement.
   - When a historical succession date arrives (e.g., Harrison Storms succeeding Edgar Schmued at North American in 1957, or Welko Gasich / Edgar Schmued leading Northrop's N-156/F-5 team from 1953), an event notification transitions the active Chief Designer to `secondary_designer_id`.
3. **Automatic Military Designation Assignment**:
   - **Internal Company Model Number**: When the player creates a draft `AircraftDesign` in the Design Editor before military contract award, it receives a company-internal project code (e.g., `NA-140`, `L-193`, `Convair Model 8-24`, `Douglas Model 640`).
   - **Prototype Contract Award (`X` / `Y` Prefix)**:
     - If awarded a USAAF/USAF prototype contract before `1948-06-11`, it is designated `XP-<seq>` (e.g., `XP-86`). On `1948-06-11`, all active `P-` designations automatically convert to `F-` (`XF-86`, `F-86A`).
     - If awarded a USAF prototype/service-test contract on or after `1948-06-11`, it receives `XF-<seq>` or `YF-<seq>A` (e.g., `YF-100A`, `XF-104`).
     - If awarded a US Navy BuAer prototype contract, it receives `XF<n><MfgLetter>-1` (omitting `<n>` when $n=1$, e.g., `XFH-1`, `XF2H-1`, `XF9F-1`, `XF8U-1`) and increments that company's Navy fighter model counter.
   - **Series Production & Popular Nickname**:
     - Upon winning a production contract, the `X`/`Y` prefix is dropped (`F-86A`, `F2H-1`, `F-106A`), and the player may accept the default company-themed nickname from `company_nickname_pools` (e.g., *Sabre*, *Banshee*, *Delta Dart*) or type a custom name.

---

## 4. Data Schemas

### 4.1 `sim/data/companies/airframers_us_1945_1960.json`
Conforms to `CompanyState` in `00_conventions.md` §4.6 plus historical metadata and AI doctrine weights:
```json
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
  "reputation": { "USAF": 0.92, "USN": 0.55, "export": 0.80 },
  "political_capital": 0.85,
  "engineers": { "aero": 65, "structures": 70, "propulsion": 20, "systems": 45 },
  "facilities": { "wind_tunnel_level": 2, "factory_floor_m2": 260000.0, "test_site": true },
  "chief_designer_id": "designer_edgar_schmued",
  "secondary_designer_id": "designer_harrison_storms",
  "starting_tech_overrides": {
    "aero_1945_compressible_subsonic": 0.95,
    "struct_1945_stressed_skin_7075": 0.94,
    "mfg_1945_ww2_mass_production_line": 0.95
  },
  "ai_doctrine": {
    "preferred_customers": ["USAF", "USN"],
    "speed_vs_maneuver_bias": 0.35,
    "production_scalability_focus": 0.90,
    "aerodynamic_ambition": 0.85,
    "risk_tolerance": 0.65
  }
}
```

### 4.2 Summary of the 13 US Airframers (1945-01-01 Starting State)

| ID | Company | USN Code | Cash ($M) | Engineers (A/S/P/Sys) | Tunnel Lvl | Floor ($\text{m}^2$) | Rep (USAF / USN) | Chief Designer(s) |
|---|---|---|---|---|---|---|---|---|
| `north_american` | North American Aviation | `J` | $38.0M | 65 / 70 / 20 / 45 (200) | 2 | 260,000 | 0.92 / 0.55 | E. Schmued / H. Storms |
| `lockheed` | Lockheed Aircraft Corp. | `V` | $34.0M | 62 / 58 / 18 / 42 (180) | 2 | 220,000 | 0.90 / 0.50 | C. "Kelly" Johnson / W. Hawkins |
| `republic` | Republic Aviation Corp. | `P` | $24.0M | 45 / 58 / 22 / 38 (163) | 1 | 175,000 | 0.86 / 0.25 | Alexander Kartveli |
| `convair` | Consolidated Vultee (Convair) | `Y` | $36.0M | 60 / 62 / 18 / 55 (195) | 2 | 250,000 | 0.84 / 0.52 | F. Davis / R. Shick |
| `mcdonnell` | McDonnell Aircraft Corp. | `H` | $14.0M | 42 / 46 / 16 / 36 (140) | 1 | 115,000 | 0.62 / 0.78 | K. Perkins / H. Barkey |
| `grumman` | Grumman Aircraft Eng. | `F` | $28.0M | 46 / 56 / 15 / 38 (155) | 1 | 180,000 | 0.35 / 0.95 | W. Schwendler / R. Hutton |
| `douglas` | Douglas Aircraft (El Segundo) | `D` | $42.0M | 60 / 64 / 18 / 44 (186) | 2 | 270,000 | 0.72 / 0.90 | Ed Heinemann |
| `vought` | Chance Vought Aircraft | `U` | $19.0M | 42 / 44 / 14 / 32 (132) | 1 | 135,000 | 0.30 / 0.84 | J.R. Clark / R. Beisel |
| `northrop` | Northrop Aircraft, Inc. | `N` | $17.0M | 46 / 40 / 14 / 38 (138) | 1 | 125,000 | 0.76 / 0.30 | J. Northrop / W. Gasich |
| `bell` | Bell Aircraft Corp. | `L` | $15.0M | 44 / 36 / 18 / 28 (126) | 1 | 110,000 | 0.70 / 0.42 | Robert J. Woods |
| `curtiss_wright` | Curtiss-Wright (Airplane Div.) | `C` | $32.0M | 34 / 42 / 20 / 28 (124) | 1 | 195,000 | 0.65 / 0.62 | Donovan R. Berlin |
| `martin` | Glenn L. Martin Co. | `M` | $26.0M | 38 / 48 / 16 / 36 (138) | 1 | 165,000 | 0.74 / 0.76 | George S. Trimble |
| `boeing` | Boeing Airplane Co. | `B` | $45.0M | 68 / 72 / 22 / 48 (210) | 2 | 290,000 | 0.95 / 0.40 | George S. Schairer |

### 4.3 Summary of the 5 US Jet Engine Manufacturers (`engine_makers_us_1945_1960.json`)

| ID | Company | US Code | Cash ($M) | Propulsion Eng. | Test Cell Lvl | Chief Designer | 1945 Centrifugal / Axial Mat. |
|---|---|---|---|---|---|---|---|
| `general_electric` | General Electric (AGTD) | `GE` | $40.0M | 120 | 2 | Gerhard Neumann | `0.92` / `0.70` |
| `pratt_whitney` | Pratt & Whitney Aircraft | `P` | $48.0M | 135 | 3 | Leonard "Luke" Hobbs | `0.65` / `0.45` |
| `allison` | Allison Div. (GM) | `A` | $35.0M | 95 | 2 | Ronald M. Hazen | `0.88` / `0.65` |
| `westinghouse` | Westinghouse (AGTD) | `WE` | $25.0M | 75 | 1 | Reinout P. Kroon | `0.60` / `0.75` |
| `wright` | Wright Aeronautical | `W` | $28.0M | 70 | 1 | William G. Lundquist | `0.65` / `0.50` |

### 4.4 Chief Designer Schema (`chief_designers_us_1945_1960.json`)
- `research_branch_bonuses`: `{branch: float in [-0.15, +0.15]}` — additive bonus applied to `1.0` in Module 03 `compute_daily_active_progress()`.
- `design_modifiers`:
  - `cd0_refinement_factor` $\in [0.95, 1.02]$: small multiplier on airframe parasite drag representing detail aerodynamic cleanliness (e.g., Kelly Johnson `0.96`, Jack Northrop `0.96`, Edgar Schmued `0.97`).
  - `prototype_build_time_factor` $\in [0.85, 1.05]$: multiplier on prototype shop fabrication days (e.g., Kelly Johnson `0.85`, Ed Heinemann `0.88`).
  - `structural_mass_factor` $\in [0.92, 1.03]$: multiplier on empty structural mass representing weight-control discipline (e.g., Ed Heinemann `0.92`, Alexander Kartveli `0.96`).

---

## 5. Algorithms

### 5.1 Pre-1962 USAF Fighter Designation Generator
Given `customer == "USAF"`, `order_date_day: int`, `stage: "prototype" | "service_test" | "production"`, `seq_num: int`, and `series_index: int` ($0 \to \text{"A"}, 1 \to \text{"B"}, \dots$):
1. Determine type letter:
   $$\text{type\_letter} = \begin{cases} \text{"P"} & \text{if } \text{order\_date\_day} < \text{date\_str\_to\_day}(\texttt{"1948-06-11"}) \\ \text{"F"} & \text{otherwise} \end{cases}$$
2. Determine status prefix:
   - `"prototype"` $\to \text{"X"}$ (omits series letter: e.g., `XP-86`, `XF-104`).
   - `"service_test"` $\to \text{"Y"}$ (includes series letter: e.g., `YF-100A`, `YF-102A`).
   - `"production"` $\to \text{""}$ (includes series letter: e.g., `P-80A`, `F-86A`, `F-106A`).
3. On calendar date `1948-06-11` (`date_day == 1257`), all existing active `P-`, `XP-`, `YP-` designations replace `"P"` with `"F"`.

### 5.2 Pre-1962 US Navy BuAer Fighter Designation Generator
Given `customer == "USN"`, `company_code: str` (e.g. `"H"` for McDonnell, `"F"` for Grumman, `"D"` for Douglas, `"U"` for Vought, `"J"` for North American), `model_num: int` (1-indexed per manufacturer), `variant_num: int` ($1, 2, \dots$), `stage: "prototype" | "development_test" | "production"`, and optional `sub_mod: "" | "N" | "P" | "M"`:
1. Determine status prefix: `"X"` for prototype, `"Y"` for development test, `""` for production.
2. Format model number: if `model_num == 1`, `model_str = ""` (per BuAer rule: McDonnell's first fighter is `FH-1`, North American's first is `FJ-1`); if `model_num >= 2`, `model_str = str(model_num)` (`F2H-1`, `F9F-2`, `F4D-1`, `F8U-1`).
3. Concatenate:
   $$\text{designation} = \texttt{f"\{status\_prefix\}F\{model\_str\}\{company\_code\}-\{variant\_num\}\{sub\_mod\}"}$$

### 5.3 Display String Resolution & Legal-Safe Rename Toggle
Given `name_key: str` and `use_fictional_names: bool = False`:
1. If `use_fictional_names` is `True` and `name_key in fictional_fallback_overrides`, return `fictional_fallback_overrides[name_key]`.
2. Else look up `name_key` in `strings` across `sim/data/names/*.json`; raise `KeyError` if missing.

---

## 6. Tunables Table

All numeric modifiers in Module 10 are bounded in data files (`chief_designers_us_1945_1960.json` and `airframers_us_1945_1960.json`):

| Parameter | Bound / Range | Effect | Rationale |
|---|---|---|---|
| `research_branch_bonuses[branch]` | `[-0.15, +0.15]` | Additive research speed modifier in Module 03 | Gives historical flavor (+15% aero for Kelly Johnson, +15% propulsion for Neumann/Hobbs) without breaking tech pacing |
| `design_modifiers.cd0_refinement_factor` | `[0.95, 1.02]` | Multiplier on baseline parasite drag $C_{D0}$ | Reflects aerodynamic detail cleanliness (3–4% difference) |
| `design_modifiers.prototype_build_time_factor` | `[0.85, 1.05]` | Multiplier on prototype shop build days | Models Skunk Works / El Segundo rapid prototyping |
| `design_modifiers.structural_mass_factor` | `[0.92, 1.03]` | Multiplier on airframe structural mass | Models Heinemann's famous weight-saving discipline vs. heavy conventional designs |

---

## 7. Edge Cases & Failure Modes

1. **Missing Localization Key**: Verified by automated test (`sim/tests/test_tech.py::test_content_and_names_integrity`) that every `name_key`, `short_name_key`, `title_key`, and `desc_key` across all Module 03 and Module 10 JSON files exists in `sim/data/names/*.json`.
2. **USN Model Number Collision (Skipping Unlucky 13)**: Historically Grumman skipped `F13F` (`F9F` $\to$ `F10F` $\to$ `F11F` $\to$ `F12F`). If a company's USN fighter model counter reaches `13`, increment to `14`.
3. **Custom Company USN Letter Collision**: Custom presets use reserved USN letters (`X`, `W`, `A`, `K`) that do not collide with the 13 active jet fighter airframers (`B, C, D, F, H, J, L, M, N, P, U, V, Y`).

---

## 8. Golden Test Vectors

Verified in [`sim/tests/test_tech.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/tests/test_tech.py):
- Every company's `starting_tech_overrides` keys are valid tech IDs in `tech_nodes_1945_1960.json` with maturities in `(0, 1]`.
- Every `chief_designer_id` and `secondary_designer_id` resolves in `chief_designers_us_1945_1960.json`.
- Every `name_key` across all Module 03 and Module 10 files resolves in `sim/data/names/*.json`.

---

## 9. Interactions

| Module | Direction | Contract / API | Description |
|---|---|---|---|
| **01 Aero & Perf** | `10 → 01` | `chief_designers.design_modifiers` | Optional small multipliers on structural mass and $C_{D0}$ refinement. |
| **02 Engines** | `10 → 02` | `engine_makers_us_1945_1960.json` | Provides starting state and propulsion tech maturities for the 5 US engine makers. |
| **03 Tech Tree** | `10 → 03` | `starting_tech_overrides`, `research_branch_bonuses` | Initializes company-specific 1945 tech maturities and chief designer research bonuses. |
| **04 Economy** | `10 → 04` | `airframers_us_1945_1960.json`, `startup_presets.json` | Initializes `CompanyState` (`cash_usd`, `debt_usd`, `engineers`, `facilities`, `reputation`, `political_capital`). |
| **05 Procurement** | `10 → 05` | `designation_rules_us_pre1962.json` | Assigns official `XP-`/`XF-`/`YF-`/`F-` and USN `XF`/`F` designations on contract award. |
| **07 Competitor AI** | `10 → 07` | `ai_doctrine` | Guides AI competitor bidding preferences, speed vs. maneuver bias, and risk tolerance. |
| **08 UI/UX** | `10 → 08` | `sim/data/names/*.json` | Resolves all user-facing display strings and legal-safe fallback names. |

---

## 10. Validation Results

- **100% Referential Integrity**: All 13 airframers, 5 engine makers, 4 startup presets, 29 chief designers, 82 tech nodes, and 28 components have verified cross-references and display strings (`sim/tests/test_tech.py`).
- **Historical Roster Coverage**: Every US prime contractor that built or flew a jet fighter/interceptor prototype between 1945 and 1960 is represented with historically grounded plant size, engineering staff, wind tunnel capability, and service reputation.

---

## 11. Open Questions & Cross-Module Change Requests

### 11.1 Open Questions (User Taste Only)
1. **Default Company Naming Mode**: Locked Decision D4 specifies real names by default with all strings in `data/names/*.json`. We have included both the authentic historical names (`strings`) and a complete set of trademark-safe fictionalized names (`fictional_fallback_overrides`, e.g., *Burbank Aero Corporation*, *Pacific American Aviation*, *Bethpage Iron Works*) in `companies_and_people.json`. Should the game settings menu expose a user-visible toggle ("Historical Names / Fictionalized Names") out of the box?
2. **Poaching Chief Designers**: Should chief designers remain historically loyal to their companies (with scripted historical moves such as Edgar Schmued moving from North American to Northrop in 1952), or should players be able to spend cash/political capital to poach a rival's secondary designer?

### 11.2 Cross-Module Change Requests
- None.
