# 05 — Military Procurement, Bidding, and Historical Program Database

> Status: v1.0 | Owner: Module 05 (`mic.procurement`)
> Conforms to: `docs/spec/00_conventions.md` v1.0, `docs/spec/03_tech_effect_keys.md` v1.0
> Tunables: `sim/data/tuning/procurement.json`
> Historical Data: `sim/data/programs/*.json`

---

## 1. Purpose & Player Fantasy

In *Military-Industrial Complex: Jet Age*, the player is **strictly a chief executive and chief designer of a private US aircraft manufacturer**—not an Air Force general or national leader. Procurement is the high-stakes arena where aerodynamics, engineering uncertainty, corporate finance, and Washington politics collide.

### 1.1 The Core Player Fantasy
You sit across the table from Wright Field (USAF Air Materiel Command) or the Navy Bureau of Aeronautics (BuAer). A new Request for Proposals (RFP)—such as the 1950 **WS-201A "1954 Interceptor"** or the 1952 **OS-130 Supersonic Carrier Day Fighter**—has just landed on your desk. You know what your wind tunnel and slide-rule calculators *say* your design can do (`Estimate = 1.32 ± 0.08 Mach`), and you know North American, Lockheed, Convair, and Vought are sharpening their pencils.

Every bid forces five intertwined, non-trivial trade-offs:

1. **The Promise Gamble (Honesty vs. Audacity):**
   - Your engineers estimate your delta-wing interceptor will reach `Mach 1.22 ± 0.09`. The RFP objective is `Mach 1.40`. Do you bid conservatively at `1.22` (high credibility, low technical risk penalty, but mediocre performance score) or promise `1.38` to beat Convair and Republic on paper?
   - Evaluators are **not gullible**. They apply a **skepticism & credibility discount** (§5.2) that haircuts unsubstantiated promises based on your company's reputation, delivery track record, estimate uncertainty $\sigma$, and technological novelty. Over-promising still buys partial points on paper—especially if you are a high-credibility incumbent—but if you win and your prototype falls short in flight test or at Initial Operational Capability (IOC), you face **liquidated damages, reputation loss, show-cause cancellation reviews, or losing the fly-off** (§5.6–5.7).
2. **Test Before Bidding vs. Rush to Proposal:**
   - Investing time and money in wind-tunnel tests (Module 06) before `proposal_due` shrinks $\sigma$, which directly reduces the evaluator's skepticism haircut and technical risk penalty. Waiting too long leaves no time to iterate geometry before the deadline.
3. **Price & Schedule Realism ("Buy-In" vs. Profitability):**
   - Under Cost-Plus-Fixed-Fee (CPFF) development and Fixed-Price-Incentive-Firm (FPIF) production contracts, bidding an aggressively low unit flyaway price or early first-flight date improves cost and schedule scores—up to a **should-cost / schedule-realism floor** where evaluators distrust lowball bids. If you lowball production price to win, cost overruns on FPIF lots come out of your own margin (30% contractor share up to the 120% price ceiling, 100% above ceiling) and spike annual program cancellation risk.
4. **Beating Incumbent Bias & The Iron Triangle:**
   - The military often favors companies that built its last successful fighter in that role (`incumbent_bias`), hold key congressional districts (`congressional_interest`), or desperately need work to keep an assembly line warm (`industrial_base_bonus`). As an underdog, you can overcome political headwinds only through superior substantiated performance, lower risk, aggressive pricing, or spending hard-earned `political_capital` on lobbying—or by funding a **private-venture prototype** to force your way into a fly-off (§5.5.4) or pitching an **unsolicited proposal** (§5.11) like Kelly Johnson's Model L-246 (F-104) or Northrop's N-156 (F-5/T-38).
5. **Doctrinal Whiplash & Long-Term Survival:**
   - Even after winning a contract, multi-year production is broken into annual fiscal lots. A sudden engine failure (e.g., Westinghouse J40 on F3H Demon), an aerodynamic surprise (YF-102 transonic drag crisis, F-100 inertia coupling), a budget crunch (post-Korea "New Look" 1953 cuts), or a strategic shift (1957 Sputnik / ICBM shift killing the F-108 Rapier) can slash lot quantities or cancel the program outright (§5.8).

---

## 2. Scope (MVP In / Out)

| Feature | MVP (USA 1945-01-01 → 1960-12-31) | Post-MVP (1961–2030 & Other Nations) |
|---|---|---|
| **Customers** | `USAF` (USAAF before 1947-09-18, unified key `USAF`), `USN` (BuAer, includes USMC carrier/night fighters) | Foreign export ministries (Module 11+), NATO consortia, Soviet MAP/VVS OKB state taskings |
| **Historical Programs** | **16 historical US fighter programs (1945–1960)** in `sim/data/programs/*.json`, with **8 flagged `mvp_core: true`** (§4.8) | 1961–2030 programs (TFX/F-111, F-X/F-15, LWF/F-16, VFAX/F-18, ATF/F-22, JSF/F-35) |
| **Acquisition Styles** | `flyoff` (prototype downselect → flight evaluation → production award), `paper_award` (Cook-Craigie / Weapon System direct award from paper proposals), `sole_source` (directed/unsolicited award) | Total Package Procurement (McNamara 1960s), Milestone A/B/C DSARC gates |
| **Evaluation Dimensions** | Performance (threshold gates + objective utility), Cost (unit + dev with realism floor), Schedule (credibility-adjusted slip), Technical Risk (novelty + overclaim + $\sigma$), Politics (incumbent, Congress, lobbying, industrial base, cross-service rivalry) | Life-cycle O&S cost modeling, multinational workshare politics |
| **Alt-History & Dynamic RFPs** | Adaptive thresholds when player beats history; follow-on redirection (e.g. F-106 goes to WS-201A winner); stopgap suppression; cancelled-program re-issue; procedural RFP generator driven by fleet age + Soviet threat milestones + capability gaps | Dynamic doctrine evolution from live war outcomes |
| **Unsolicited Proposals** | Supported in MVP: player pitches an existing design or prototype outside an active RFP; can win sole-source award or trigger an open GOR competition | Export-oriented private ventures (Mirage/F-5 export market pitches) |

---

## 3. Player-Facing Flow

```mermaid
flowchart TD
    A["1. RFP Issued (or Advisory Preview 6 mo early)"] --> B["2. Player Designs / Tests Aircraft (Modules 01, 02, 06)"]
    B --> C["3. Proposal Preparation & Bid Submission (before proposal_due)"]
    C --> D["4. Source Selection Board Evaluation (Paper Phase)"]
    D -->|acquisition_style = paper_award / sole_source| H["7. Production Contract Award (FPIF Lots + CPFF Dev)"]
    D -->|acquisition_style = flyoff: Top K selected| E["5. Prototype Build & Flight Testing (CPFF Prototype Contract)"]
    D -->|Missed cut by <= PRIVATE_ENTRY_MARGIN| E2["5b. Optional Company-Funded Prototype Entry"]
    E --> F["6. Fly-Off Evaluation (at first_flight_due / evaluation window)"]
    E2 --> F
    F -->|Winner (or Dual Award)| H
    F -->|All fail gates: Waiver roll or Cancel| X["Program Cancelled → Capability Gap"]
    H --> I["8. IOC Promise Audit & Annual Lot Reviews (July 1)"]
    I -->|Pass & Continued| J["Deliveries, Cash Flow, Reputation & Follow-On Variants"]
    I -->|Severe Overrun / Shortfall / Obsolescence| X
```

### 3.1 Step-by-Step Player Experience & Failure Modes

1. **Draft Requirement Preview & Formal RFP Issue:**
   - Six months before `issue_date` (for scheduled historical programs), intelligence/liaison rumours alert the player to the upcoming role and rough speed/altitude targets.
   - On `issue_date`, the formal `Requirement` opens. The player sees:
     - **Customer & Role:** e.g., `USAF` — `interceptor` (WS-201A "1954 Interceptor").
     - **Deadlines:** `proposal_due`, `first_flight_due`, `ioc_due`.
     - **Criteria Table:** Every `threshold` (mandatory gate), `objective` (threshold + target objective with weight), and `weighted` criterion, plus required equipment gates (e.g. search radar, minimum crew, carrier suitability, internal weapons bay).
     - **Budget & Quantities:** `dev_usd`, `unit_price_ceiling_usd`, `quantity_planned`, and acquisition style (`flyoff` vs `paper_award`).
     - **Category Weights:** How the board weights Performance, Cost, Schedule, and Technical Risk (`eval_weights.proposal` and `eval_weights.flyoff`).
     - **Political Landscape:** Visible indicators of which rival firms hold incumbent advantage or congressional pull.
2. **Bid Authoring Screen (Module 08 UI backed by Module 05 preview API):**
   - The player selects an `AircraftDesign` (or active prototype) and sets:
     - **Promised performance values** $P_i$ for each criterion (defaults to the player's current `Estimate.value`; slider allows promising higher or lower, displaying live **Confidence %** = $\Phi\left(\frac{s_i(\mu_i - P_i)}{\sigma_i}\right)$ and live **Overclaim Risk warning**).
     - **Bid unit flyaway price** (`unit_price_bid_usd`) and **Bid development cost** (`dev_cost_bid_usd`).
     - **Promised first-flight date** (`promised_first_flight_day`) and **IOC date** (`promised_ioc_day`).
     - **Lobbying allocation:** Optional `political_capital_spent` ($\ge 0$).
3. **Paper Source Selection & Downselect (`proposal_due`):**
   - All player and AI competitor bids are evaluated (§5.2–5.5).
   - **What can go wrong:**
     - *Gate Disqualification:* Promising a value that violates a `threshold` criterion, missing required equipment (e.g., single-seat on a two-seat mandated fleet interceptor), or bidding $> 1.30 \times \text{unit\_price\_ceiling\_usd}$ marks the bid **Non-Responsive (Disqualified)**.
     - *Skepticism Discount:* A newcomer with high $\sigma$ (no wind-tunnel tests) and 4 unproven technologies who promises Mach 2.2 sees their credited speed discounted heavily and their Technical Risk score crater.
   - **Outcome:**
     - In `paper_award` programs (e.g., F-102, F-104, F8U), the highest-scoring responsive bid above `MIN_AWARD_SCORE` wins the development + initial production contract directly.
     - In `flyoff` programs (e.g., 1946 Penetration Fighter XF-88/XF-90/YF-93, 1945 All-Weather Fighter XF-87/XF-89, 1958 USN FAD F4H-1/XF8U-3), the top $K$ (`downselect_count`, typically 2 or 3) bidders receive CPFF prototype contracts.
     - **Company-Funded Prototype Option:** If the player missed the top $K$ by at most `PRIVATE_ENTRY_MARGIN` (8.0 points) and was responsive, they may elect within 14 days to self-fund a prototype and enter the fly-off at their own expense.
4. **Fly-Off Evaluation (`flyoff_date`):**
   - Prototypes are evaluated using **measured flight-test performance** (`source = "flight"`, tight $\sigma$) plus any **unfixed discovered flaws** from Module 06 and a **broken-promise penalty** where measured performance fell short of paper promises (§5.6).
   - **What can go wrong:**
     - *Prototype not flown by deadline:* Disqualified (unless all entrants are unflown, triggering a deadline extension).
     - *Measured performance misses threshold by $> 3\%$ (`FLYOFF_GATE_TOL`):* Fails the fly-off gate (e.g., YF-102 failing to break Mach 1.0 before area-rule fix). If *all* finalists fail a gate, the board rolls for a **Waiver** (accepting the "least unsatisfactory" aircraft at a reputation penalty, as in the 1948 F-89 evaluation) or cancels the program (as in the August 1950 Penetration Fighter cancellation).
5. **Contract Execution, Promise Audits & Annual Lot Reviews:**
   - At First Flight and IOC, promised numbers are audited against actuals (§5.7). Shortfalls beyond `PROMISE_TOL` (2%) trigger **FPIF liquidated damages** (up to 15% unit price reduction), **reputation penalties**, **track-record decay**, and—if a hard threshold is missed by $> 3\%$ at IOC—a **Show-Cause Review** that requires an engineering fix project (e.g., Whitcomb area-rule fuselage redesign on YF-102A, tail enlargement on F-100) or risks contract termination.
   - Every **July 1** (start of US fiscal year), active programs undergo an **Annual Lot Review** (§5.8) that computes `p_cancel` and the next lot's `qty_multiplier`.
6. **Evaluation Debrief Report:**
   - After every paper selection or fly-off, the player receives a structured **Source Selection Debrief** listing every entrant's score breakdown (`Perf`, `Cost`, `Sched`, `Risk`, `Politics`, `Total`), compliance flags, and a plain-language narrative explaining *why* the winner won and *why* each loser fell short.

---

## 4. Data Schemas

All schemas use SI units internally (`m`, `kg`, `s`, `mps`, `dps`, `usd`, `mach`, `days since 1945-01-01`). In static JSON files (`sim/data/programs/*.json`), dates are stored as ISO strings `"YYYY-MM-DD"` alongside integer day helpers, and historical human-readable notes record original imperial specifications for traceability.

### 4.1 `Requirement` & `ProgramSpec` Schema (`sim/data/programs/<id>.json`)

Conforms to and extends `00_conventions.md` §4.5. All top-level keys of `Requirement` (`id`, `program_name`, `customer`, `issue_date`, `proposal_due`, `first_flight_due`, `ioc_due`, `criteria`, `budget`, `politics`, `historical`) are preserved verbatim.

```json
{
  "schema_version": 1,
  "id": "usn_os130_1952",
  "name_key": "program.usn_os130_1952.name",
  "program_name": "OS-130 Carrier Supersonic Day Fighter",
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
    "missile_capability": ["ir"]
  },
  "criteria": [
    {
      "key": "max_mach_alt",
      "kind": "objective",
      "op": ">=",
      "value": 1.20,
      "objective_value": 1.55,
      "weight": 0.30,
      "unit": "mach",
      "description": "Level flight supersonic speed at 10,668 m (35,000 ft)"
    },
    {
      "key": "climb_rate_sl_mps",
      "kind": "objective",
      "op": ">=",
      "value": 101.6,
      "objective_value": 135.0,
      "weight": 0.25,
      "unit": "mps",
      "description": "Sea-level initial rate of climb (20,000–26,500 ft/min)"
    },
    {
      "key": "service_ceiling_m",
      "kind": "objective",
      "op": ">=",
      "value": 15240.0,
      "objective_value": 16764.0,
      "weight": 0.15,
      "unit": "m",
      "description": "Service ceiling (50,000–55,000 ft)"
    },
    {
      "key": "combat_radius_m",
      "kind": "objective",
      "op": ">=",
      "value": 555600.0,
      "objective_value": 740800.0,
      "weight": 0.15,
      "unit": "m",
      "description": "Combat radius on internal fuel (300–400 nmi)"
    },
    {
      "key": "stall_speed_mps",
      "kind": "objective",
      "op": "<=",
      "value": 54.0,
      "objective_value": 48.9,
      "weight": 0.15,
      "unit": "mps",
      "description": "Carrier approach/stall speed (<= 105 kt threshold, 95 kt objective)"
    },
    {
      "key": "carrier_suitability",
      "kind": "threshold",
      "op": ">=",
      "value": 1.0,
      "weight": 0.0,
      "unit": "bool",
      "description": "Must satisfy Essex/Forrestal carrier suitability & deck spot factor"
    }
  ],
  "budget": {
    "dev_usd": 32000000.0,
    "unit_price_ceiling_usd": 950000.0,
    "quantity_planned": 550
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
    "proposal": { "perf": 0.45, "cost": 0.20, "sched": 0.15, "risk": 0.20 },
    "flyoff":   { "perf": 0.60, "cost": 0.15, "sched": 0.10, "risk": 0.15 }
  },
  "politics": {
    "incumbent_bias": {
      "grumman": 0.35,
      "douglas": 0.30,
      "mcdonnell": 0.25,
      "vought": 0.20,
      "north_american": 0.15
    },
    "congressional_interest": 0.40,
    "industrial_base_need": {
      "vought": 0.65,
      "grumman": 0.20,
      "douglas": -0.20
    }
  },
  "historical": {
    "winner_company_id": "vought",
    "winner_design_name": "V-383 (XF8U-1 Crusader)",
    "award_date": "1953-05-29",
    "outcome": "produced",
    "production_delivered": 1261,
    "notes": "Eight companies submitted proposals. Vought V-383 won on its two-position variable-incidence wing and Mach 1.35–1.50 performance with J57.",
    "citations": [
      "https://en.wikipedia.org/wiki/Vought_F-8_Crusader",
      "https://thanlont.blogspot.com/2017/10/the-first-supersonic-us-navy-fighter.html"
    ],
    "competitors": []
  },
  "alt_history": {
    "predecessor_program_id": null,
    "follow_on_program_id": "usn_fad_1955",
    "suppress_if_role_satisfied": false,
    "historical_cancellation_shock": 0.0
  }
}
```

### 4.2 `CriterionSpec` Fields

| Field | Type | Range / Allowed | Default | Description |
|---|---|---|---|---|
| `key` | `str` | Any `PerformanceReport` key (`00` §4.4) | required | Metric evaluated by this criterion |
| `kind` | `str` | `"threshold"`, `"objective"`, `"weighted"` | required | `"threshold"`: hard pass/fail gate only (`weight = 0`). `"objective"`: both hard gate at `value` and utility scored toward `objective_value`. `"weighted"`: soft utility scored around `value` without hard disqualification gate. |
| `op` | `str` | `">="`, `"<="` | required | Direction of improvement (`">="` more is better; `"<="` less is better, e.g., `stall_speed_mps`, `time_to_alt_10668m_s`, `takeoff_distance_m`, `maint_mh_per_fh`) |
| `value` | `float` | Finite float (SI) | required | Threshold value $T_i$ (or reference value for `"weighted"`) |
| `objective_value` | `float\|None` | Finite float (SI) | `None` | Target objective $O_i$. If omitted on an `"objective"` or `"weighted"` criterion, defaults to $T_i \cdot (1 + s_i \cdot \text{DEFAULT\_SPAN\_FRAC})$ where $s_i = +1$ for `">="` and $-1$ for `"<="`. |
| `weight` | `float` | $[0.0, 1.0]$ | `0.0` | Relative importance among scored criteria ($\sum w_i = 1.0$ across `"objective"` and `"weighted"` criteria). |
| `unit` | `str` | `"mach"`, `"m"`, `"mps"`, `"dps"`, `"s"`, `"kg"`, `"usd"`, `"bool"` | `"float"` | Unit identifier for UI conversion and reporting |

### 4.3 `HistoricalEntrant` Schema (inside `historical.competitors[]`)

Every historical program includes the winner and major losing entrants with their published/reconstructed specifications so the replay validator (`sim/mic/procurement/replay.py`) and AI competitor generator (`sim/mic/procurement/ai_competitor.py`) operate deterministically from data:

```json
{
  "company_id": "vought",
  "design_name": "Vought V-383 (XF8U-1 Crusader)",
  "is_historical_winner": true,
  "built_prototype": true,
  "first_flight_date": "1955-03-25",
  "unit_price_bid_usd": 780000.0,
  "dev_cost_bid_usd": 28000000.0,
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
    "missile_capability": ["ir"]
  },
  "reputation_at_bid": 68.0,
  "track_record_at_bid": 0.48,
  "district_weight": 0.45,
  "cross_service_derivative": false,
  "promised_overrides": {},
  "anchor_performance": {
    "max_mach_alt": 1.45,
    "climb_rate_sl_mps": 127.0,
    "service_ceiling_m": 15697.0,
    "combat_radius_m": 722280.0,
    "stall_speed_mps": 50.4,
    "carrier_suitability": 1.0
  },
  "flyoff_flaws_unfixed_severity": 0
}
```

### 4.4 `ProposalBid` Schema (Input to Evaluation)

```python
ProposalBid {
  bid_id: str                                # unique id, e.g. "usn_os130_1952__vought"
  program_id: str
  company_id: str
  design_name: str
  is_player: bool
  submitted_day: int                         # days since 1945-01-01
  estimates: dict[str, Estimate]             # substantiated data package from Module 01/06
  promised: dict[str, float]                 # binding performance promises per criterion key
  unit_price_bid_usd: float                  # proposed average unit flyaway price
  unit_cost_estimate_usd: float              # should-cost estimate from Module 01/04
  dev_cost_bid_usd: float                    # proposed RDT&E cost
  dev_cost_estimate_usd: float               # estimated RDT&E cost from Module 01/04
  promised_first_flight_day: int             # promised first flight calendar day
  promised_ioc_day: int                      # promised IOC calendar day
  novelty: NoveltyProfile                    # {unproven_tech_count: int, unflown_engine: bool, unconventional_config: bool}
  equipment: EquipmentProfile                # {carrier_capable, radar_installed, crew, engines, internal_bay, guns_20mm, missile_capability}
  political_capital_spent: float             # >= 0.0
  cross_service_derivative: bool             # True if navalized USAF design or land-based USN design
  is_originator: bool                        # True if this company originated the requirement via unsolicited proposal
  measured_performance: dict[str, Estimate]  # populated for fly-off evaluation (empty at paper stage)
  actual_first_flight_day: int | None        # populated if prototype has flown
  unfixed_flaw_severity_sum: int             # sum of severities (1..5) of unfixed discovered HiddenFlaws
}
```

### 4.5 `BidderContext` Schema (Company Standing Snapshot)

```python
BidderContext {
  company_id: str
  reputation_service: float      # [0, 100] reputation with customer (USAF or USN) from Module 04
  track_record: float            # [0, 1] EMA of promise-delivery accuracy maintained by Module 05 (default 0.5)
  district_weight: float         # [0, 1] Congressional delegation weight of company's plants
  active_contracts_same_role: int
  active_contracts_same_customer: int
  idle_factory_fraction: float   # [0, 1] fraction of factory floor currently idle
}
```

### 4.6 `BidScoreBreakdown` & `EvaluationReport` Schema

```python
CriterionEvalDetail {
  key: str
  kind: str
  promised: float
  substantiated_mu: float
  substantiated_sigma: float
  credible_value: float
  overclaim_q: float
  gate_passed: bool
  utility: float
  weight: float
  weighted_utility: float
}

BidScoreBreakdown {
  bid_id: str
  company_id: str
  design_name: str
  phase: str                     # "proposal" | "flyoff"
  responsive: bool               # True if all hard gates (thresholds, equipment, price ceiling) passed
  disqualify_reasons: list[str]
  credibility: float             # C in [0.05, 0.95]
  novelty_index: float           # N >= 0
  perf_score: float              # [0, 125]
  cost_score: float              # [0, 100]
  sched_score: float             # [0, 110]
  risk_index: float              # [0, 1]
  risk_score: float              # [0, 100] = 100 * (1 - risk_index)
  tech_score: float              # weighted sum of perf, cost, sched, risk_score
  politics_bonus: float          # [-15, +15]
  promise_penalty: float         # >= 0 (fly-off only)
  flaw_penalty: float            # >= 0 (fly-off only)
  eval_noise: float              # N(0, EVAL_NOISE_SD)
  total_score: float             # final ranking score
  criteria_details: list[CriterionEvalDetail]
}
```

### 4.7 `ContractState` Schema

```python
ProductionLot {
  lot_number: int                # 1..L
  fiscal_year: int               # e.g. 1954
  quantity_planned: int
  quantity_awarded: int
  unit_target_price_usd: float
  unit_ceiling_price_usd: float  # FPIF_CEILING * unit_target_price_usd
  gov_share: float               # FPIF_GOV_SHARE (0.70)
  liquidated_damage_frac: float  # [0, LD_CAP]
  status: str                    # "planned" | "active" | "completed" | "cancelled"
}

ContractState {
  contract_id: str
  program_id: str
  customer: str
  role: str
  company_id: str
  design_name: str
  contract_kind: str             # "prototype_cpff" | "production_fpif"
  award_day: int
  dev_target_cost_usd: float
  dev_fixed_fee_usd: float       # DEV_FEE_FRAC * dev_target_cost_usd
  dev_cost_incurred_usd: float
  promised_performance: dict[str, float]
  promised_first_flight_day: int
  promised_ioc_day: int
  lots: list[ProductionLot]
  status: str                    # "active" | "show_cause" | "completed" | "cancelled"
  cancellation_reason: str | None
}
```

### 4.8 Historical Program Roster (`sim/data/programs/*.json`)

All 16 programs (9 USAF + 7 USN) span 1945–1960, with 8 marked `mvp_core: true`:

| # | Program ID | Customer | Issue Date | Program Name | Historical Winner | Acquisition Style | `mvp_core` |
|---|---|---|---|---|---|---|---|
| 1 | `usaf_aw_int_1945` | USAF | 1945-08-28 | 1945 All-Weather Fighter (MX-785) | Northrop XP-89 Scorpion (vs Curtiss XF-87, Douglas XF3D, Convair XP-92) | `flyoff` | **true** |
| 2 | `usn_night_1945` | USN | 1945-10-15 | 1945 Carrier Night / All-Weather Fighter | Douglas XF3D-1 Skyknight (vs Grumman G-75, Curtiss Naval XP-87) | `paper_award` | **true** |
| 3 | `usaf_pen_fighter_1946` | USAF | 1946-02-15 | 1946 Penetration Fighter & 1950 Edwards Fly-Off | McDonnell XF-88A Voodoo (vs Lockheed XF-90A, North American YF-93A; cancelled Aug 1950) | `flyoff` | **true** |
| 4 | `usn_os105_1946` | USN | 1946-01-15 | OS-105 Carrier Swept-Wing Day Fighter | Vought XF7U-1 Cutlass (vs North American NA-140, Douglas D-558-II study) | `paper_award` | false |
| 5 | `usn_short_int_1947` | USN | 1947-06-01 | 1947 Carrier Point-Defense Interceptor | Douglas XF4D-1 Skyray (vs Grumman/Vought studies) | `paper_award` | false |
| 6 | `usn_gp_fighter_1949` | USN | 1949-01-15 | 1949 Carrier General-Purpose All-Weather Fighter | McDonnell XF3H-1 Demon (vs Grumman, Douglas, North American) | `paper_award` | false |
| 7 | `usaf_ws201a_1950` | USAF | 1950-06-18 | WS-201A "1954 Interceptor" (Project MX-1554) | Convair YF-102 / F-102A Delta Dagger (vs Republic AP-57/XF-103, Lockheed L-205, NAA NA-177) | `paper_award` | **true** |
| 8 | `usaf_sabre45_1951` | USAF | 1951-01-15 | Sabre 45 Supersonic Day Fighter (GOR 1951) | North American YF-100A Super Sabre (unsolicited / sole-source origin) | `sole_source` | false |
| 9 | `usaf_gor101_1951` | USAF | 1951-02-06 | GOR 101 Long-Range Strategic Fighter Escort (WS-105A) | McDonnell F-101A Voodoo (vs Lockheed F-90D, NAA F-93B, Northrop F-89E, Republic AP-51) | `paper_award` | false |
| 10 | `usaf_ws306a_1952` | USAF | 1952-04-15 | WS-306A Supersonic Tactical Nuclear Strike Fighter | Republic YF-105A / F-105B Thunderchief (AP-63 unsolicited / sole-source) | `sole_source` | false |
| 11 | `usn_os130_1952` | USN | 1952-09-15 | OS-130 Carrier Supersonic Day Fighter | Vought XF8U-1 Crusader (vs Grumman G-98, Douglas M-656, Lockheed L-242, NAA NA-208, McDonnell M-91) | `paper_award` | **true** |
| 12 | `usaf_ws303a_1952` | USAF | 1952-12-12 | WS-303A Lightweight Air-Superiority Day Fighter | Lockheed XF-104 Starfighter (vs Northrop N-102 Fang, Republic AP-55, NAA NA-212) | `paper_award` | **true** |
| 13 | `usn_f11f_1953` | USN | 1953-03-01 | BuAer Lightweight Transonic Carrier Day Fighter | Grumman XF9F-9 / F11F-1 Tiger (unsolicited Design 98) | `sole_source` | false |
| 14 | `usn_fad_1955` | USN | 1955-05-26 | Carrier Fleet Air Defense All-Weather Interceptor & 1958 Fly-Off | McDonnell XF4H-1 Phantom II (vs Vought XF8U-3 Crusader III in 1958 fly-off) | `flyoff` | **true** |
| 15 | `usaf_ws202a_1955` | USAF | 1955-10-06 | GOR 114 / WS-202A Long-Range Interceptor (LRI-X) | North American XF-108 Rapier (vs Lockheed CL-325, Northrop N-167; cancelled Sep 1959) | `paper_award` | **true** |
| 16 | `usaf_gor127_n156_1956` | USAF | 1956-06-01 | Northrop N-156 Private Venture / GOR 127 & MAP Light Fighter | Northrop YT-38 Talon / N-156F (F-5A Freedom Fighter) (vs NAA NA-241, Lockheed CL-419) | `paper_award` | false |

Auxiliary data files in `sim/data/programs/`:
- `sim/data/programs/threats_1945_1960.json` — Soviet threat intelligence milestones & doctrinal shocks (Tu-4, RDS-1 A-bomb, MiG-15, RDS-6s H-bomb, M-4 Bison, Tu-95 Bear, MiG-19, Sputnik-1 / R-7 ICBM).
- `sim/data/programs/budget_index_1945_1960.json` — US defense aircraft procurement budget multiplier by fiscal year (post-WWII demobilization, Korean War surge, Eisenhower "New Look", late-1950s missile shift).

---

## 5. Algorithms & Mathematical Specification

Every constant in `UPPER_SNAKE` below is loaded from `sim/data/tuning/procurement.json` (§6).

### 5.1 Sign Normalization & Criterion Helpers

For any criterion $i$ with operator $\text{op}_i \in \{\text{">="}, \text{"<="}\}$:
$$s_i = \begin{cases} +1 & \text{if } \text{op}_i = \text{">="} \\ -1 & \text{if } \text{op}_i = \text{"<="} \end{cases}$$

If $O_i$ (`objective_value`) is `None` or equal to $T_i$ (`value`), the effective objective is:
$$O_i = T_i \cdot \left(1 + s_i \cdot \text{DEFAULT\_SPAN\_FRAC}\right)$$
And the positive criterion span is:
$$\Delta_i = \max\left(\left|O_i - T_i\right|,\; 10^{-6} \cdot \max(|T_i|, 1.0)\right)$$

### 5.2 Bidder Credibility, Novelty, and Skepticism Discount

#### 5.2.1 Bidder Credibility $C \in [\text{CRED\_MIN}, \text{CRED\_MAX}]$
Given customer reputation $R_{\text{svc}} \in [0, 100]$ and historical promise track record $\tau \in [0, 1]$ (default $\text{TRACK\_DEFAULT} = 0.5$):
$$C = \text{clamp}\!\left(\text{CRED\_BASE} + \text{CRED\_W\_REP} \cdot \frac{R_{\text{svc}}}{100} + \text{CRED\_W\_TRACK} \cdot \tau,\;\; \text{CRED\_MIN},\;\; \text{CRED\_MAX}\right)$$
*(Example: at baseline $R_{\text{svc}} = 50, \tau = 0.5$, $C = 0.20 + 0.50(0.5) + 0.30(0.5) = 0.60$.)*

#### 5.2.2 Novelty Index $N \ge 0$
From the bid's `NoveltyProfile` ($n_{\text{tech}}$ = number of required techs not yet proven in service, $I_{\text{eng}} \in \{0,1\}$ = unflown engine indicator, $I_{\text{cfg}} \in \{0,1\}$ = unconventional aerodynamic configuration such as tailless delta / variable sweep before prior company flight):
$$N_{\text{raw}} = \text{NOV\_PER\_TECH} \cdot n_{\text{tech}} + \text{NOV\_ENGINE\_UNFLOWN} \cdot I_{\text{eng}} + \text{NOV\_UNCONVENTIONAL} \cdot I_{\text{cfg}}$$
In the **paper proposal phase**, $N = N_{\text{raw}}$. In the **fly-off phase** (once hardware has flown), $N = \text{FLYOFF\_NOV\_FACTOR} \cdot N_{\text{raw}}$.

#### 5.2.3 Substantiated Estimate Haircut & Credible Value $\hat{V}_i$
For each quantitative criterion $i$, the bidder submits a substantiated estimate $(\mu_i, \sigma_i)$ from Module 01/06 and a binding promise $P_i$.
1. **Conservative Substantiated Baseline $E_{\text{adj}, i}$:**
   Evaluators discount the mean estimate $\mu_i$ in proportion to its uncertainty $\sigma_i$, the bidder's lack of credibility $(1 - C)$, and novelty $N$:
   $$k_{\text{skep}} = \text{SKEPTIC\_K} \cdot (1 - C) \cdot \left(\text{SKEPTIC\_NOV\_BASE} + N\right)$$
   $$E_{\text{adj}, i} = \mu_i - s_i \cdot k_{\text{skep}} \cdot \sigma_i$$
2. **Overclaim Ratio $q_i \ge 0$ (in $\sigma$ units):**
   $$\sigma_{\text{eff}, i} = \max\left(\sigma_i,\; 0.01 \cdot \max(|\mu_i|, 1.0)\right)$$
   $$q_i = \max\!\left(0.0,\; \frac{s_i \cdot (P_i - \mu_i)}{\sigma_{\text{eff}, i}}\right)$$
3. **Credible Value $\hat{V}_i$:**
   - In the **paper proposal phase**:
     - If $s_i \cdot (P_i - E_{\text{adj}, i}) \le 0$ (the bidder promised at or more conservatively than $E_{\text{adj}, i}$):
       $$\hat{V}_i = P_i$$
     - If $s_i \cdot (P_i - E_{\text{adj}, i}) > 0$ (the bidder promised above the conservative substantiated baseline):
       $$\lambda_{\text{oc}} = \text{OC\_MIN} + (\text{OC\_MAX} - \text{OC\_MIN}) \cdot C$$
       $$\hat{V}_i = E_{\text{adj}, i} + \lambda_{\text{oc}} \cdot (P_i - E_{\text{adj}, i})$$
   - In the **fly-off phase**:
     Promises no longer inflate performance credit. Given measured flight-test estimate $(\mu_{\text{flt}, i}, \sigma_{\text{flt}, i})$:
     $$\hat{V}_i = \mu_{\text{flt}, i} - s_i \cdot k_{\text{skep}} \cdot \sigma_{\text{flt}, i}$$
   - For boolean criteria (`unit == "bool"`, e.g. `carrier_suitability`): $\hat{V}_i = \mu_i \in \{0.0, 1.0\}$ directly (cannot be faked by promise).

### 5.3 Gate Compliance & Criterion Utility $u_i$

#### 5.3.1 Hard Gate Check (`responsive`)
For every criterion with `kind` $\in \{\text{"threshold"}, \text{"objective"}\}$:
- **Paper proposal phase:** The **promised value** $P_i$ must satisfy the threshold $T_i$:
  $$s_i \cdot (P_i - T_i) \ge -10^{-9}$$
- **Fly-off phase:** The **measured value** $\mu_{\text{flt}, i}$ must satisfy $T_i$ within tolerance $\text{FLYOFF\_GATE\_TOL} = 0.03$:
  $$s_i \cdot (\mu_{\text{flt}, i} - T_i) \ge -\text{FLYOFF\_GATE\_TOL} \cdot |T_i|$$
- **Equipment Gates:** `Bid.equipment` must satisfy all requirements in `ProgramSpec.equipment` (`carrier_capable`, `radar_required`, `min_crew`, `min_engines`, `internal_bay_required`, `min_guns_20mm`, `missile_capability` subset).
- **Price Ceiling Gate:** $\text{unit\_price\_bid\_usd} \le \text{PRICE\_ZERO\_RATIO} \cdot \text{unit\_price\_ceiling\_usd}$ ($1.30 \times$ ceiling).

If any hard gate fails, `responsive = False` and the reason is appended to `disqualify_reasons`.

#### 5.3.2 Criterion Utility $u_i(\hat{V}_i) \in [\text{U\_MIN}, \text{U\_MAX}]$
Let normalized progress from threshold $T_i$ to objective $O_i$ be:
$$m_i = \frac{s_i \cdot (\hat{V}_i - T_i)}{\Delta_i}$$
Piecewise linear utility with diminishing returns above objective and steeper penalty below threshold:
$$u_i = \begin{cases}
\min\!\left(\text{U\_MAX},\; 1.0 + \text{U\_OVER\_SLOPE} \cdot (m_i - 1.0)\right) & \text{if } m_i \ge 1.0 \\[4pt]
\text{U\_AT\_THRESHOLD} + (1.0 - \text{U\_AT\_THRESHOLD}) \cdot m_i & \text{if } 0.0 \le m_i < 1.0 \\[4pt]
\max\!\left(\text{U\_MIN},\; \text{U\_AT\_THRESHOLD} + \text{U\_BELOW\_SLOPE} \cdot m_i\right) & \text{if } m_i < 0.0
\end{cases}$$
With default tunables ($\text{U\_AT\_THRESHOLD} = 0.30$, $\text{U\_OVER\_SLOPE} = 0.35$, $\text{U\_MAX} = 1.25$, $\text{U\_BELOW\_SLOPE} = 1.30$, $\text{U\_MIN} = -1.0$):
- Meeting $T_i$ exactly ($m_i = 0$) earns $u_i = 0.30$ (30 points on a 100-point scale).
- Meeting $O_i$ ($m_i = 1$) earns $u_i = 1.00$ (100 points).
- Exceeding $O_i$ can earn up to $1.25$ (125 points max).
- If a discounted $\hat{V}_i$ falls slightly below $T_i$ ($m_i < 0$), $u_i$ drops smoothly below $0.30$ down to $-1.0$.

#### 5.3.3 Aggregate Performance Score $S_{\text{perf}} \in [0, 125]$
Across all criteria with $w_i > 0$:
$$W = \sum_{i: w_i > 0} w_i, \qquad S_{\text{perf}} = \text{clamp}\!\left(100.0 \cdot \frac{\sum_{i: w_i > 0} w_i \cdot u_i}{W},\; 0.0,\; 100.0 \cdot \text{U\_MAX}\right)$$
(If $W = 0$, $S_{\text{perf}} = 100.0$ if all gates pass else $0.0$.)

### 5.4 Cost, Schedule, Technical Risk, and Politics Sub-Scores

#### 5.4.1 Cost Score $S_{\text{cost}} \in [0, 100]$ (with Should-Cost Realism Floor)
Government cost analysts compare `unit_price_bid_usd` ($B_{\text{unit}}$) against the independent should-cost estimate `unit_cost_estimate_usd` ($E_{\text{unit}}$). Bidding below $(1 - \text{PRICE\_REALISM\_TOL}) \cdot E_{\text{unit}}$ is recognized as an unrealistic "buy-in" and receives no extra price credit below that floor:
$$\hat{B}_{\text{unit}} = \max\!\left(B_{\text{unit}},\; (1.0 - \text{PRICE\_REALISM\_TOL}) \cdot E_{\text{unit}}\right)$$
$$\rho_{\text{unit}} = \frac{\hat{B}_{\text{unit}}}{\text{unit\_price\_ceiling\_usd}}$$
$$S_{\text{unit}} = 100.0 \cdot \text{clamp}\!\left(\frac{\text{PRICE\_ZERO\_RATIO} - \rho_{\text{unit}}}{\text{PRICE\_ZERO\_RATIO} - \text{PRICE\_FULL\_RATIO}},\; 0.0,\; 1.0\right)$$
Similarly, for development cost against `budget.dev_usd` ($B_{\text{dev,ceil}}$):
$$\hat{B}_{\text{dev}} = \max\!\left(B_{\text{dev}},\; (1.0 - \text{PRICE\_REALISM\_TOL}) \cdot E_{\text{dev}}\right), \qquad \rho_{\text{dev}} = \frac{\hat{B}_{\text{dev}}}{B_{\text{dev,ceil}}}$$
$$S_{\text{dev}} = 100.0 \cdot \text{clamp}\!\left(\frac{\text{PRICE\_ZERO\_RATIO} - \rho_{\text{dev}}}{\text{PRICE\_ZERO\_RATIO} - \text{PRICE\_FULL\_RATIO}},\; 0.0,\; 1.0\right)$$
$$S_{\text{cost}} = \text{COST\_W\_UNIT} \cdot S_{\text{unit}} + \text{COST\_W\_DEV} \cdot S_{\text{dev}}$$

#### 5.4.2 Schedule Score $S_{\text{sched}} \in [0, \text{SCHED\_MAX}]$
1. **Paper Proposal Phase:**
   From submission date $t_{\text{sub}}$, expected minimum realistic development time to first flight is:
   $$D_{\text{exp}} = \text{DEV\_DAYS\_BASE} \cdot \left(\text{DEV\_DAYS\_NOV\_BASE} + \text{DEV\_DAYS\_NOV\_K} \cdot N\right)$$
   $$t_{\text{ff,floor}} = t_{\text{sub}} + \text{SCHED\_REALISM} \cdot D_{\text{exp}}$$
   $$D_{\text{slip}} = \text{SLIP\_DAYS\_PER\_NOV} \cdot N \cdot (1.0 - C)$$
   $$\hat{t}_{\text{ff}} = \max\left(t_{\text{ff,promised}},\; t_{\text{ff,floor}}\right) + D_{\text{slip}}$$
2. **Fly-Off Phase:**
   $$\hat{t}_{\text{ff}} = t_{\text{ff,actual}}$$
3. **Months Late vs. `first_flight_due` ($t_{\text{ff,due}}$):**
   $$M_{\text{late}} = \frac{\hat{t}_{\text{ff}} - t_{\text{ff,due}}}{\text{DAYS\_PER\_MONTH}}$$
   $$S_{\text{sched}} = \text{clamp}\!\left(100.0 - \text{SCHED\_PTS\_PER\_MONTH} \cdot M_{\text{late}},\; 0.0,\; \text{SCHED\_MAX}\right)$$
   *(At $\text{SCHED\_PTS\_PER\_MONTH} = 4.1667$, being on time scores $100$, 24 months late scores $0$, and delivering $\ge 2.4$ months early caps at $\text{SCHED\_MAX} = 110$.)*

#### 5.4.3 Technical Risk Index $R_{\text{tech}} \in [0, 1]$ and Score $S_{\text{risk}} \in [0, 100]$
1. **Weighted Overclaim Index $\bar{q} \in [0, 1]$:**
   Across criteria (giving `"threshold"` criteria a small weight $\text{GATE\_RISK\_WEIGHT} = 0.10$ if $w_i = 0$):
   $$\tilde{w}_i = \max(w_i, \text{GATE\_RISK\_WEIGHT}), \qquad \bar{q} = \text{clamp}\!\left(\frac{\sum_i \tilde{w}_i \cdot (q_i / \text{RISK\_Q\_NORM})}{\sum_i \tilde{w}_i},\; 0.0,\; 1.0\right)$$
2. **Relative Uncertainty Index $\bar{\sigma}_{\text{rel}} \in [0, 1]$:**
   $$\bar{\sigma}_{\text{rel}} = \text{clamp}\!\left(\frac{\sum_i \tilde{w}_i \cdot \min\!\left(1.0,\; \frac{\sigma_i}{0.10 \cdot \max(|\mu_i|, 1.0)}\right)}{\sum_i \tilde{w}_i},\; 0.0,\; 1.0\right)$$
3. **Composite Technical Risk:**
   $$R_{\text{nov}} = \text{clamp}(N, 0.0, 1.0)$$
   $$R_{\text{tech}} = \text{clamp}\!\left(\text{RISK\_W\_NOV} \cdot R_{\text{nov}} + \text{RISK\_W\_OVER} \cdot \bar{q} + \text{RISK\_W\_SIG} \cdot \bar{\sigma}_{\text{rel}} + \text{RISK\_W\_CRED} \cdot (1.0 - C),\; 0.0,\; 1.0\right)$$
   $$S_{\text{risk}} = 100.0 \cdot (1.0 - R_{\text{tech}})$$

#### 5.4.4 Weighted Technical Score $S_{\text{tech}}$
Using phase weights $(W_{\text{perf}}, W_{\text{cost}}, W_{\text{sched}}, W_{\text{risk}})$ from `ProgramSpec.eval_weights[phase]`:
$$S_{\text{tech}} = W_{\text{perf}} \cdot S_{\text{perf}} + W_{\text{cost}} \cdot S_{\text{cost}} + W_{\text{sched}} \cdot S_{\text{sched}} + W_{\text{risk}} \cdot S_{\text{risk}}$$

#### 5.4.5 Politics & Iron Triangle Bonus $\Delta_{\text{pol}} \in [-\text{POL\_CAP}, +\text{POL\_CAP}]$
1. **Incumbent Bias $I_{\text{inc}} \in [-1, 1]$:**
   - In **historical replay mode** (or when static bias is explicitly provided on `Requirement.politics.incumbent_bias[company_id]`): uses the table value $I_{\text{static}}$.
   - In **dynamic campaign mode**, incumbent bias is computed live from company state (`compute_dynamic_incumbent_bias`):
     $$I_{\text{dyn}} = \text{clamp}\!\left(\text{INC\_SAME\_ROLE} \cdot \mathbb{I}(\text{active\_same\_role} > 0) + \text{INC\_SAME\_CUSTOMER} \cdot \mathbb{I}(\text{active\_same\_customer} > 0) + \text{INC\_REP\_K} \cdot \frac{R_{\text{svc}} - 50}{50} + \text{ORIGINATOR\_BIAS} \cdot \mathbb{I}(\text{is\_originator}),\; -0.50,\; 1.00\right)$$
2. **Congressional District Pull:**
   $$\Delta_{\text{cong}} = \text{CONG\_PTS} \cdot \text{congressional\_interest} \cdot (\text{district\_weight} - 0.35)$$
3. **Lobbying Spend (Diminishing Returns):**
   $$\Delta_{\text{lobby}} = \text{LOBBY\_MAX\_PTS} \cdot \left(1.0 - \exp\!\left(-\frac{\text{political\_capital\_spent}}{\text{LOBBY\_SCALE\_PC}}\right)\right)$$
4. **Industrial Base Preservation Bonus:**
   If `politics.industrial_base_need[company_id]` is specified, uses $b_{\text{ib}} \in [-1, 1]$; otherwise $b_{\text{ib}} = \text{idle\_factory\_fraction} - 0.30$:
   $$\Delta_{\text{ib}} = \text{IB\_PTS} \cdot b_{\text{ib}}$$
5. **Cross-Service Rivalry Penalty:**
   The US Navy BuAer historically resisted adopting USAF-originated airframes (and vice versa prior to McNamara's 1962 F-4/TFX directives):
   $$\Delta_{\text{rival}} = -\text{RIVAL\_PTS} \cdot \mathbb{I}(\text{cross\_service\_derivative})$$
6. **Total Political Adjustment:**
   $$\Delta_{\text{pol}} = \text{clamp}\!\left(\text{INC\_PTS} \cdot I_{\text{inc}} + \Delta_{\text{cong}} + \Delta_{\text{lobby}} + \Delta_{\text{ib}} + \Delta_{\text{rival}},\; -\text{POL\_CAP},\; +\text{POL\_CAP}\right)$$
   *(Capped at $\pm 15.0$ points so politics acts as a decisive tie-breaker among competitive designs, never rescuing a broken airplane.)*

### 5.5 Total Score, Evaluation Noise, and Downselect Rules

#### 5.5.1 Paper Proposal Total Score
For each bid (sorted ascending by `bid_id` before drawing noise for deterministic RNG ordering):
$$\varepsilon \sim \mathcal{N}(0, \text{EVAL\_NOISE\_SD}^2)$$
$$S_{\text{total}} = S_{\text{tech}} + \Delta_{\text{pol}} + \varepsilon$$
*(When `deterministic=True` in replay validation and golden tests, $\varepsilon = 0$.)*

#### 5.5.2 Downselect & Paper Award Decision
Let $\mathcal{B}_{\text{resp}}$ be all bids with `responsive == True` and $S_{\text{total}} \ge \text{MIN\_AWARD\_SCORE}$ ($35.0$), sorted descending by $S_{\text{total}}$ (ties broken by higher $S_{\text{perf}}$, then lower `bid_id`):
- If $\mathcal{B}_{\text{resp}}$ is empty:
  - No award is made (`outcome = "no_responsive_bid"`). The requirement is queued in the capability-gap pool for re-issue (§5.9).
- If `acquisition.style == "sole_source"` or `"paper_award"`:
  - The top bid $b_{(1)}$ wins the development and production contract (`winners = [b_{(1)}]`).
- If `acquisition.style == "flyoff"`:
  - The top $K = \min(\text{downselect\_count}, |\mathcal{B}_{\text{resp}}|)$ bids receive CPFF prototype contracts (`finalists = [b_{(1)}, \dots, b_{(K)}]`).
  - Any responsive non-selected bid $b_j$ ($j > K$) with $S_{\text{total}}(b_{(K)}) - S_{\text{total}}(b_j) \le \text{PRIVATE\_ENTRY\_MARGIN}$ ($8.0$) is flagged `eligible_for_private_prototype = True`.

### 5.6 Fly-Off Evaluation & Waiver Logic

At the conclusion of prototype flight testing, every finalist (plus any company-funded private entrant that has completed first flight) is evaluated with `phase = "flyoff"`:

1. **Broken-Promise Penalty $P_{\text{prom}} \ge 0$:**
   For each criterion $i$, let relative shortfall vs. the paper promise $P_i$ be:
   $$\delta_{\text{prom}, i} = \max\!\left(0.0,\; \frac{s_i \cdot (P_i - \mu_{\text{flt}, i})}{\max(|P_i|, 1.0)}\right)$$
   $$P_{\text{prom}} = \text{PROMISE\_PTS\_PER\_PCT} \cdot 100.0 \cdot \frac{\sum_i \tilde{w}_i \cdot \delta_{\text{prom}, i}}{\sum_i \tilde{w}_i}$$
2. **Unfixed Hidden Flaw Penalty $P_{\text{flaw}} \ge 0$:**
   Given the sum of severities $\Sigma_{\text{sev}}$ of discovered but unfixed flaws on the prototype (Module 06):
   $$P_{\text{flaw}} = \text{FLAW\_PTS\_PER\_SEVERITY} \cdot \Sigma_{\text{sev}}$$
3. **Fly-Off Total Score:**
   $$S_{\text{total,flyoff}} = S_{\text{tech,flyoff}} + \Delta_{\text{pol}} - P_{\text{prom}} - P_{\text{flaw}} + \varepsilon$$
4. **Winner Selection, Dual Award, and All-Fail Waiver:**
   - **Case A (At least one responsive finalist with $S_{\text{total,flyoff}} \ge \text{MIN\_AWARD\_SCORE}$):**
     - Top finalist $b_{(1)}$ wins primary production contract.
     - If `acquisition.allow_dual_award == True`, $|\mathcal{B}_{\text{resp}}| \ge 2$, and $S_{\text{total,flyoff}}(b_{(1)}) - S_{\text{total,flyoff}}(b_{(2)}) \le \text{DUAL\_MARGIN}$ ($5.0$), a **Dual Production Award** splits `quantity_planned` as $\text{DUAL\_SPLIT\_WINNER} = 65\%$ to $b_{(1)}$ and $35\%$ to $b_{(2)}$.
   - **Case B (All finalists failed at least one fly-off threshold gate):**
     - If `historical_cancellation_shock >= 0.80` (e.g., 1950 Penetration Fighter where SAC doctrine shifted simultaneously), the program is cancelled immediately after naming the technical fly-off winner.
     - Otherwise, the board rolls for a **Threshold Waiver** ("best of a poor lot", modeling the Oct 1948 Northrop F-89 evaluation):
       $$p_{\text{waiver}} = \text{clamp}\!\left(\text{WAIVER\_P\_BASE} + \text{WAIVER\_P\_URGENCY} \cdot \text{urgency} - \text{historical\_cancellation\_shock},\; 0.0,\; 0.95\right)$$
       If a uniform draw $u < p_{\text{waiver}}$, the highest-scoring finalist wins under a waiver, suffering an immediate $-\text{WAIVER\_REP\_PENALTY}$ ($-5.0$) reputation hit and a mandatory redesign milestone. Otherwise, the program is cancelled and queued for re-issue.
### 5.7 Milestone Promise Audit, Liquidated Damages, and Track Record Update

At First Flight and at Initial Operational Capability (IOC), the contractor's delivered performance $\mu_{\text{act}, i}$ and actual milestone date $t_{\text{act}}$ are audited against promised $P_i$ and $t_{\text{prom}}$:

1. **Weighted Net Shortfall & Liquidated Damages on FPIF Production Lots:**
   Let weighted percentage shortfall beyond tolerance $\text{PROMISE\_TOL} = 0.02$ be:
   $$\delta_{\text{net}, i} = \max\!\left(0.0,\; \frac{s_i \cdot (P_i - \mu_{\text{act}, i})}{\max(|P_i|, 1.0)} - \text{PROMISE\_TOL}\right), \qquad \bar{\delta}_{\text{short}} = \frac{\sum_i \tilde{w}_i \cdot \delta_{\text{net}, i}}{\sum_i \tilde{w}_i}$$
   $$f_{\text{LD}} = \text{clamp}\!\left(\text{LD\_RATE} \cdot \bar{\delta}_{\text{short}},\; 0.0,\; \text{LD\_CAP}\right)$$
   Each active or future production lot has its target unit price reduced by factor $(1 - f_{\text{LD}})$ (up to $\text{LD\_CAP} = 15\%$).
2. **Reputation Delta $\Delta R_{\text{svc}}$:**
   - **Performance component:**
     If $\bar{\delta}_{\text{short}} > 0$:
     $$\Delta R_{\text{perf}} = \max\!\left(\text{REP\_SHORTFALL\_FLOOR},\; -\text{REP\_PER\_PCT} \cdot (100.0 \cdot \bar{\delta}_{\text{short}})\right)$$
     Else if every criterion exceeded $P_i$ by at least $\text{PROMISE\_TOL}$:
     $$\Delta R_{\text{perf}} = +\text{REP\_BONUS\_EXCEED}$$
     Else $\Delta R_{\text{perf}} = 0.0$.
   - **Schedule component:**
     Let months late beyond grace period $\text{REP\_LATE\_GRACE\_MONTHS} = 3.0$ be:
     $$M_{\text{over}} = \max\!\left(0.0,\; \frac{t_{\text{act}} - t_{\text{prom}}}{\text{DAYS\_PER\_MONTH}} - \text{REP\_LATE\_GRACE\_MONTHS}\right)$$
     $$\Delta R_{\text{sched}} = \max\!\left(\text{REP\_LATE\_FLOOR},\; -\text{REP\_PER\_LATE\_MONTH} \cdot M_{\text{over}}\right)$$
   - Total reputation change: $\Delta R_{\text{svc}} = \Delta R_{\text{perf}} + \Delta R_{\text{sched}}$.
3. **Track Record EMA Update $\tau_{\text{new}}$:**
   $$r_{\text{deliv}} = \text{clamp}\!\left(1.0 - \text{TRACK\_K} \cdot \bar{\delta}_{\text{short}},\; 0.0,\; 1.0\right)$$
   $$\tau_{\text{new}} = (1.0 - \text{TRACK\_ALPHA}) \cdot \tau_{\text{old}} + \text{TRACK\_ALPHA} \cdot r_{\text{deliv}}$$
4. **Show-Cause Threshold Review (Area-Rule / Inertia-Coupling Redesign Trigger):**
   If any `threshold` or `objective` criterion misses $T_i$ by more than $\text{SHOW\_CAUSE\_GATE\_TOL} = 3\%$ at First Flight or IOC (e.g., Convair YF-102 achieving only Mach 0.98 against a Mach 1.15 threshold):
   - Contract status enters `"show_cause"`. Production lot release is frozen until a redesign/fix project (Module 06) cures the shortfall.
   - If uncured within 180 days, a cancellation roll with probability $\text{SHOW\_CAUSE\_P\_CANCEL} = 0.50$ terminates the contract.

### 5.8 Contract Structures (CPFF / FPIF), Annual Lot Review & Cancellation Model

#### 5.8.1 Contract Cost-Sharing Formulas (Interface with Module 04)
- **Development / Prototype Contract (`prototype_cpff`):**
  - Target cost: $C_{\text{target}} = B_{\text{dev}}$.
  - Fixed fee: $F_{\text{fixed}} = \text{DEV\_FEE\_FRAC} \cdot C_{\text{target}}$ ($7\%$).
  - Government reimburses actual RDT&E costs up to $1.25 \cdot C_{\text{target}}$ plus $F_{\text{fixed}}$; overruns beyond $C_{\text{target}}$ feed into the annual cancellation review below.
- **Production Lot Contract (`production_fpif`):**
  - Given target unit cost $C_{\text{T}}$, target unit price $P_{\text{T}} = B_{\text{unit}} \cdot (1 - f_{\text{LD}})$, ceiling price $P_{\text{ceil}} = \text{FPIF\_CEILING} \cdot B_{\text{unit}}$ ($120\%$), and actual unit cost $C_{\text{A}}$:
  $$P_{\text{final}} = \min\!\left(P_{\text{ceil}},\; P_{\text{T}} + (1.0 - \text{FPIF\_GOV\_SHARE}) \cdot (C_{\text{A}} - C_{\text{T}})\right)$$
  The government pays $70\%$ ($\text{FPIF\_GOV\_SHARE}$) of cost overruns up to the $120\%$ price ceiling; above $P_{\text{ceil}}$, the contractor absorbs $100\%$ of additional cost.

#### 5.8.2 Annual Fiscal Lot Review (Every July 1)
For each active contract with remaining planned lots, let:
- $r_{\text{overrun}} = \max\!\left(0.0,\; \frac{C_{\text{incurred}} - C_{\text{expected}}}{\max(C_{\text{expected}}, 1.0)} - \text{CANCEL\_OVERRUN\_TOL}\right)$
- $Y_{\text{slip}} = \max\!\left(0.0,\; \frac{t_{\text{current\_est}} - t_{\text{promised}}}{365.25}\right)$ (schedule slip in years)
- $\bar{\delta}_{\text{short}} =$ current weighted performance shortfall fraction
- $B_{\text{idx}} \in [0.4, 1.6] =$ current fiscal year budget index (`budget_index_1945_1960.json`, baseline $1.0$)
- $\Omega_{\text{obs}} \in [0, 2] =$ doctrinal obsolescence index (e.g., $+1.20$ for high-altitude Mach 3 interceptors after the 1957 Sputnik / ICBM shift, or $+1.0$ if a newer aircraft in the same role has entered service with $> 25\%$ higher performance)
- $d_{\text{cong}} = \text{congressional\_interest} \cdot \text{district\_weight} \in [0, 1]$
- $L_{\text{norm}} = \min(1.0, \text{political\_capital\_spent} / 20.0)$

The annual cancellation probability is:
$$p_{\text{cancel}} = \text{clamp}\!\Big(\text{CANCEL\_BASE} + \text{CANCEL\_OVERRUN\_K} \cdot r_{\text{overrun}} + \text{CANCEL\_SLIP\_K} \cdot Y_{\text{slip}} + \text{CANCEL\_SHORTFALL\_K} \cdot \bar{\delta}_{\text{short}} + \text{CANCEL\_BUDGET\_K} \cdot \max(0.0, 1.0 - B_{\text{idx}}) + \text{CANCEL\_OBSOLETE\_K} \cdot \Omega_{\text{obs}} - \text{CANCEL\_CONGRESS\_K} \cdot d_{\text{cong}} - \text{CANCEL\_LOBBY\_K} \cdot L_{\text{norm}},\;\; 0.0,\;\; \text{CANCEL\_MAX}\Big)$$

If the contract survives ($u \ge p_{\text{cancel}}$), the next lot's awarded quantity is scaled by:
$$m_{\text{qty}} = \text{clamp}\!\left(1.0 + \text{QTY\_PERF\_K} \cdot \left(\frac{S_{\text{perf}}}{100.0} - \text{QTY\_PERF\_REF}\right) - \text{QTY\_OVERRUN\_K} \cdot r_{\text{overrun}} + \text{QTY\_BUDGET\_K} \cdot (B_{\text{idx}} - 1.0),\;\; \text{QTY\_MULT\_MIN},\;\; \text{QTY\_MULT\_MAX}\right)$$
$$Q_{\text{lot,awarded}} = \max\!\left(1,\; \text{round}(Q_{\text{lot,planned}} \cdot m_{\text{qty}})\right)$$

### 5.9 Alt-History Adaptation Rules

When player actions diverge from historical outcomes, the historical program schedule adapts via four deterministic rules (`sim/mic/procurement/dynamic_rfp.py`):

1. **Adaptive Requirement Escalation (`adapt_program_to_world`):**
   When a historical program is about to be issued on `issue_date`, for each `"more is better"` (`">="`) speed/climb/ceiling/radius criterion $i$, let $V_{\text{world}, i}$ be the best measured performance already achieved in flight by any US aircraft in that role. If $\text{ADAPT\_FRAC} \cdot V_{\text{world}, i} > T_i$ ($\text{ADAPT\_FRAC} = 0.90$), then:
   $$T_i^{\text{new}} = \text{ADAPT\_FRAC} \cdot V_{\text{world}, i}, \qquad O_i^{\text{new}} = O_i \cdot \frac{T_i^{\text{new}}}{T_i}$$
   *(Prevents the player from coasting on an early breakthrough against obsolete historical thresholds.)*
2. **Stopgap Suppression:**
   If a program has `alt_history.suppress_if_role_satisfied == True` (e.g., interim stopgaps or redundant secondary day fighters like `usn_f11f_1953`), and the customer already awarded a production contract in the same role within the past $\text{SUPPRESS\_YEARS} = 3.0$ years whose delivered performance meets at least $95\%$ of all thresholds of the stopgap program, the stopgap program is suppressed (`status = "suppressed"`).
3. **Follow-On Redirection:**
   If a program specifies `alt_history.predecessor_program_id` (e.g., WS-201B / F-106 Delta Dart following WS-201A / F-102, or GOR 101 F-101 Voodoo following the 1946 Penetration Fighter fly-off), the follow-on's `incumbent_bias` and sole-source/directed recipient are redirected to whichever company actually won the predecessor in the current campaign. If the predecessor was cancelled with no winner, the follow-on converts to an open `paper_award` competition.
4. **Cancelled Program Re-Issue:**
   Whenever a program fails to produce an operational aircraft (all bids non-responsive, or cancelled in fly-off/development without doctrinal obsolescence), a `CapabilityGapRecord` is created and re-issued after $\text{REISSUE\_DELAY\_MONTHS} = 18$ months ($\text{REISSUE\_DELAY\_URGENT\_MONTHS} = 12$ if `urgency >= 0.75`) with thresholds updated to the current technological frontier.

### 5.10 Procedural / Dynamic RFP Generator

In addition to the 16 historical programs, a monthly check (`evaluate_monthly_rfp_trigger`) runs on the 1st of each month for each `(customer, role)` pair across the 5 standard roles (`day_fighter`, `interceptor`, `fighter_bomber`, `escort_fighter`, `carrier_day_fighter`, `carrier_interceptor`):

1. **Demand Pressure Signals:**
   - **Fleet Age Pressure $D_{\text{age}} \in [0, 1]$:**
     Given years $Y_{\text{age}}$ since the customer's current frontline aircraft in that role first entered service:
     $$D_{\text{age}} = \text{clamp}\!\left(\frac{Y_{\text{age}} - \text{REPLACE\_YEARS}}{\text{AGE\_RAMP\_YEARS}},\; 0.0,\; 1.0\right)$$
   - **Soviet Threat Gap $D_{\text{threat}} \in [0, 1]$:**
     From `threats_1945_1960.json`, let $M_{\text{threat}}$ be the active Soviet threat Mach (bomber Mach $\times 1.25$ for interceptors; fighter Mach for day fighters) and $M_{\text{fleet}}$ be the customer's best fielded Mach in that role:
     $$D_{\text{threat}} = \text{clamp}\!\left(\frac{M_{\text{threat}} - M_{\text{fleet}}}{\text{THREAT\_GAP\_NORM}} + \Delta_{\text{shock}},\; 0.0,\; 1.0\right)$$
   - **Unmet Capability Gap $D_{\text{gap}} \in \{0, 1\}$:** $1.0$ if a prior program in this role failed/cancelled without replacement and its reissue delay has elapsed, else $0.0$.
2. **Composite Demand Score & Trigger Gate:**
   $$D_{\text{total}} = \text{W\_AGE} \cdot D_{\text{age}} + \text{W\_THREAT} \cdot D_{\text{threat}} + \text{W\_GAP} \cdot D_{\text{gap}}$$
   A procedural RFP is issued if:
   - $D_{\text{total}} \ge \text{ISSUE\_THRESHOLD}$ ($0.60$),
   - No historical program for `(customer, role)` is scheduled within $\text{HIST\_LOOKAHEAD\_MONTHS} = 18$ months,
   - At least $\text{MIN\_GAP\_MONTHS} = 12$ months have elapsed since the last RFP in `(customer, role)`, and
   - Active open programs for `customer` $< \text{round}(\text{MAX\_OPEN\_BASE} \cdot B_{\text{idx}})$.
3. **Procedural Target Synthesis (`generate_procedural_requirement`):**
   - Interpolates the technological frontier curve $F_k(y)$ at calendar year $y \in [1945, 1960]$ for each role criterion $k$.
   - Sets threshold $T_k = F_k(y) \cdot (1 + s_k \cdot 0.05 \cdot \min(D_{\text{total}}, \text{AMB\_CAP}))$ and objective $O_k = T_k \cdot (1 + s_k \cdot \text{DEFAULT\_SPAN\_FRAC})$.
   - Sets unit price ceiling from reference cost growth curve:
     $$C_{\text{ref}}(y) = \text{COST\_REF\_C0\_USD} \cdot \exp\!\left(\text{COST\_REF\_GROWTH} \cdot (y - 1945.0)\right)$$
     $$\text{unit\_price\_ceiling\_usd} = \text{CEILING\_MARGIN} \cdot C_{\text{ref}}(y) \cdot m_{\text{role\_cost}}$$
     $$\text{dev\_usd} = \text{DEV\_MULT} \cdot \text{unit\_price\_ceiling\_usd}$$

### 5.11 Unsolicited Proposals (Private Venture Pitch)

Modeled on Lockheed's CL-246 (F-104), North American's Sabre 45 (F-100), Republic's AP-63 (F-105), and Northrop's N-156 (T-38/F-5):

1. **Eligibility & Pitch Cost:**
   - The player may pitch a design or flown prototype to `customer` for `role` if not on cooldown ($\text{U\_COOLDOWN\_DAYS} = 365$ days per `(customer, role)`).
   - Submitting costs $\text{U\_PITCH\_COST\_FRAC} \cdot C_{\text{ref}}(y)$ ($0.5\%$ of reference dev cost) and takes $\text{U\_REVIEW\_DELAY\_DAYS} = 90$ days for Air Staff / BuAer review.
2. **Evaluation Against Virtual Requirement:**
   - The bid is scored against the procedural requirement for `(customer, role, y)` using §5.2–5.5, yielding $S_{\text{total}}$ (with an added $+5.0$ bonus if the player has already flown a private prototype).
3. **Acceptance Probability:**
   $$p_{\text{accept}} = \sigma_{\text{logistic}}\!\left(\frac{S_{\text{total}} - \text{U\_MID}}{\text{U\_SCALE}}\right) \cdot \text{clamp}\!\left(\text{U\_NEED\_BASE} + D_{\text{total}},\; 0.20,\; 1.00\right) \cdot \text{clamp}(B_{\text{idx}}, 0.5, 1.3) \cdot f_{\text{open}}$$
   where $\sigma_{\text{logistic}}(x) = \frac{1}{1 + e^{-x}}$, and $f_{\text{open}} = \text{U\_OPEN\_PROGRAM\_FACTOR}$ ($0.30$) if an RFP is already open in that role else $1.0$.
4. **Sole-Source vs. Open GOR Competition Roll:**
   - If accepted ($u_1 < p_{\text{accept}}$), the customer decides between awarding a **Direct Sole-Source Contract** (like the F-100 and F-105) or issuing an **Open Competitive GOR** tailored around the player's concept (like the F-104 WS-303A competition):
     $$p_{\text{sole}} = \text{clamp}\!\left(\text{U\_SOLE\_BASE} + \text{U\_SOLE\_K} \cdot (C - 0.50) + 0.20 \cdot \mathbb{I}(\text{prototype\_flown}),\; 0.15,\; 0.90\right)$$
   - If $u_2 < p_{\text{sole}}$: immediate sole-source contract award for $\text{round}(\text{U\_QTY\_FRAC} \cdot Q_{\text{role\_std}})$ aircraft.
   - Else: an open `paper_award` RFP is issued with objectives set to $\text{U\_COPY\_OBJ\_FRAC} = 0.95$ of the player's promised performance and `is_originator = True` ($+\text{ORIGINATOR\_BIAS} = +0.30$ incumbent bias for the player).

### 5.12 AI Competitor Proposal Generator (`sim/mic/procurement/ai_competitor.py`)

Generates realistic rival bids for both historical and procedural RFPs:

1. **Historical Entrants (`generate_historical_entrant_bid`):**
   - Reads the entrant's `anchor_performance` $A_i$ from `sim/data/programs/<id>.json`.
   - Applies company engineering quality modifier $Q_{\text{AI}} \in [\text{AI\_MIN\_QUALITY}, 1.30]$ (default $1.0$ in historical calibration replay):
     - True performance: $V_{\text{true}, i} = A_i \cdot \left(1 + s_i \cdot \text{AI\_SKILL\_SPAN} \cdot (Q_{\text{AI}} - 1.0) + \varepsilon_{\text{true}}\right)$ where $\varepsilon_{\text{true}} \sim \mathcal{N}(0, \text{AI\_TRUE\_SD}^2)$.
     - Substantiated paper estimate: $\mu_i = V_{\text{true}, i} \cdot (1 + \varepsilon_{\text{est}})$ with $\sigma_i = \text{AI\_PAPER\_SIGMA\_REL} \cdot |\mu_i|$.
     - Paper promise: if `promised_overrides[key]` is present (e.g., Convair's Mach 1.25 promise on YF-102 before the area-rule drag crisis), uses that override; otherwise $P_i = \max_{s_i}\!\left(T_i,\; \mu_i + s_i \cdot z_{\text{prom}} \cdot \sigma_i\right)$ where $z_{\text{prom}} = \text{AI\_PROMISE\_Z\_DEFAULT} = 0.5$.
     - Fly-off measured estimate (if `built_prototype` is true): $\mu_{\text{flt}, i} = V_{\text{true}, i}$ with $\sigma_{\text{flt}, i} = \text{FLIGHT\_SIGMA\_REL} \cdot |\mu_{\text{flt}, i}|$.
2. **Dynamic AI Entrants (`generate_dynamic_ai_bids`):**
   - For procedural RFPs (or when historical entrants have exited the industry, such as Curtiss-Wright after 1948), active AI companies with matching role competence generate bids scaled off the requirement thresholds $T_i$ and objectives $O_i$ using their company skill $Q_{\text{AI}}$ and aggression trait.

---

## 6. Tunables Table (`sim/data/tuning/procurement.json`)

All 84 balance parameters live in `sim/data/tuning/procurement.json`:

| Name | Default | Range | Effect | Rationale |
|---|---|---|---|---|
| `CRED_BASE` | `0.20` | `[0.0, 0.4]` | Base credibility floor before reputation/track record | Even a new firm gets some baseline consideration |
| `CRED_W_REP` | `0.50` | `[0.2, 0.7]` | Weight of service reputation in credibility $C$ | Service relationship is the strongest credibility driver |
| `CRED_W_TRACK` | `0.30` | `[0.1, 0.5]` | Weight of historical promise delivery EMA $\tau$ | Rewards consistent truth-in-bidding across programs |
| `CRED_MIN` / `CRED_MAX` | `0.05` / `0.95` | `[0.01, 0.99]` | Clamp bounds on credibility $C$ | Prevents complete immunity or total zeroing |
| `TRACK_DEFAULT` | `0.50` | `[0.3, 0.7]` | Initial track record $\tau$ for companies with no deliveries | Neutral starting prior |
| `NOV_PER_TECH` | `0.20` | `[0.05, 0.40]` | Novelty index added per unproven technology | Stacks risk when combining multiple bleeding-edge techs |
| `NOV_ENGINE_UNFLOWN` | `0.25` | `[0.10, 0.50]` | Novelty penalty for pairing airframe with unflown engine | Reflects historical J40/J67 engine-airframe fiascos |
| `NOV_UNCONVENTIONAL` | `0.15` | `[0.05, 0.35]` | Novelty penalty for tailless/delta/variable-sweep layout | Reflects BuAer/USAF caution on XF7U-1 and XF-92A/F-102 |
| `SKEPTIC_K` | `1.00` | `[0.3, 2.0]` | Multiplier on estimate uncertainty haircut $k_{\text{skep}}$ | Scales how strongly $\sigma$ reduces substantiated baseline |
| `SKEPTIC_NOV_BASE` | `0.50` | `[0.2, 1.0]` | Base offset in $(1-C)(\text{SKEPTIC\_NOV\_BASE} + N)$ | Ensures high-$\sigma$ bids face haircut even at $N=0$ |
| `OC_MIN` / `OC_MAX` | `0.15` / `0.60` | `[0.0, 0.8]` | Min/max overclaim credit fraction $\lambda_{\text{oc}}$ | Trusted incumbents get up to 60% paper credit on stretch claims; newcomers get ~15–25% |
| `DEFAULT_SPAN_FRAC` | `0.20` | `[0.10, 0.40]` | Default $(O_i - T_i)/T_i$ when `objective_value` omitted | 20% performance headroom between threshold and objective |
| `U_AT_THRESHOLD` | `0.30` | `[0.10, 0.50]` | Utility $u_i$ when $\hat{V}_i = T_i$ | Barely meeting threshold scores 30/100, leaving 70 pts for reaching objective |
| `U_OVER_SLOPE` | `0.35` | `[0.10, 0.60]` | Utility slope above objective $O_i$ | Diminishing returns above objective |
| `U_MAX` / `U_MIN` | `1.25` / `-1.0` | `[1.0, 1.5]` / `[-2.0, 0.0]` | Utility upper and lower clamps | Caps single-criterion runaway at 125 pts |
| `U_BELOW_SLOPE` | `1.30` | `[0.5, 2.5]` | Utility penalty slope when $\hat{V}_i < T_i$ | Steep drop when discounted value falls below threshold |
| `PRICE_FULL_RATIO` | `0.70` | `[0.50, 0.90]` | Bid-to-ceiling ratio earning 100 cost points | Bidding $\le 70\%$ of ceiling gets full cost score |
| `PRICE_ZERO_RATIO` | `1.30` | `[1.10, 1.50]` | Bid-to-ceiling ratio earning 0 cost points & gate limit | Bids $> 130\%$ of ceiling are non-responsive |
| `PRICE_REALISM_TOL` | `0.10` | `[0.0, 0.25]` | Max discount below should-cost estimate credited | Prevents $1 unit price lowball exploits |
| `COST_W_UNIT` / `COST_W_DEV` | `0.70` / `0.30` | `[0.0, 1.0]` | Weights of unit flyaway price vs RDT&E cost in $S_{\text{cost}}$ | Unit price dominates large production runs |
| `SLIP_DAYS_PER_NOV` | `540.0` | `[180, 900]` | Expected schedule slip days per unit of $N \cdot (1-C)$ | High-novelty low-credibility bids face ~6–18 mo slip adjustment |
| `DEV_DAYS_BASE` | `900.0` | `[600, 1200]` | Baseline days from proposal to first flight (~2.5 yr) | Calibrated to 1945–1960 US fighter development timelines |
| `DEV_DAYS_NOV_BASE` / `K` | `0.70` / `0.60` | `[0.4, 1.0]` | Novelty scaling on minimum realistic development time | Prevents promising 6-month clean-sheet Mach 2 fighters |
| `SCHED_REALISM` | `0.75` | `[0.5, 1.0]` | Realism floor fraction on expected development days | Evaluators clamp implausibly early first-flight promises |
| `SCHED_PTS_PER_MONTH` | `4.1667` | `[2.0, 8.0]` | Schedule points lost per month late vs `first_flight_due` | 24 months late zeroes schedule score ($100 / 24 = 4.1667$) |
| `SCHED_MAX` | `110.0` | `[100, 120]` | Maximum schedule score for early delivery | Up to +10 pt bonus for credible early delivery (e.g., F-94, F-100) |
| `RISK_W_NOV` / `OVER` / `SIG` / `CRED` | `0.35 / 0.25 / 0.20 / 0.20` | sum to `1.0` | Component weights in technical risk $R_{\text{tech}}$ | Balances novelty, overclaiming, $\sigma$, and company standing |
| `RISK_Q_NORM` | `2.0` | `[1.0, 4.0]` | Overclaim $\sigma$-units corresponding to $100\%$ overclaim risk | Promising $+2\sigma$ above estimate saturates overclaim risk |
| `INC_PTS` / `CONG_PTS` | `10.0` / `10.0` | `[0.0, 20.0]` | Max points from incumbent bias and congressional pull | Meaningful tie-breaker ($\sim 5–10$ pts) without overriding a 15-pt technical lead |
| `LOBBY_MAX_PTS` / `SCALE_PC` | `6.0` / `20.0` | `[0, 12]` / `[5, 50]` | Asymptote and scale of lobbying points vs political capital | Diminishing returns prevent buying every competition |
| `IB_PTS` / `RIVAL_PTS` | `4.0` / `5.0` | `[0, 10]` | Industrial-base preservation bonus & cross-service penalty | Models Knaack p. 175 (F-104) & BuAer resistance to USAF airframes |
| `POL_CAP` | `15.0` | `[5.0, 25.0]` | Absolute cap on total political bonus $\pm\Delta_{\text{pol}}$ | Guarantees physics/engineering remains primary |
| `EVAL_NOISE_SD` | `1.5` | `[0.0, 4.0]` | Standard deviation of source selection board noise | Small subjective variance in close contests |
| `MIN_AWARD_SCORE` | `35.0` | `[20.0, 60.0]` | Minimum total score required to win an award | Prevents terrible bids from winning by default |
| `PRIVATE_ENTRY_MARGIN` | `8.0` | `[0.0, 15.0]` | Max point deficit behind last finalist to allow private prototype | Lets near-miss bidders self-fund into the fly-off |
| `FLYOFF_GATE_TOL` | `0.03` | `[0.0, 0.10]` | Relative tolerance on threshold gates in fly-off ($3\%$) | Prevents disqualifying a prototype for a 1% instrument variance |
| `PROMISE_PTS_PER_PCT` | `1.0` | `[0.2, 3.0]` | Fly-off score penalty per 1% weighted promise shortfall | Punishes paper sandbaggers when prototypes fly |
| `FLAW_PTS_PER_SEVERITY` | `3.0` | `[1.0, 6.0]` | Fly-off score penalty per severity point of unfixed flaws | Links Module 06 flight-test flaw discovery to fly-off outcome |
| `DUAL_MARGIN` / `SPLIT_WINNER` | `5.0` / `0.65` | `[1, 10]` / `[0.5, 0.8]` | Margin for dual production award and winner share | Models split buys when two finalists finish neck-and-neck |
| `WAIVER_P_BASE` / `URGENCY` | `0.60` / `0.30` | `[0, 1]` | Probability of granting a waiver when all finalists miss a gate | Models Oct 1948 F-89 "best of a poor lot" award |
| `PROMISE_TOL` / `LD_RATE` / `LD_CAP` | `0.02 / 2.0 / 0.15` | — | IOC promise audit tolerance (2%), liquidated damages slope & 15% cap | Standard FPIF contract price adjustment for shortfall |
| `CANCEL_BASE` .. `CANCEL_MAX` | see JSON | — | Annual July 1 lot cancellation probability coefficients | Calibrated to XF-87, XF-103, F5D, F-108 cancellations |
| `ADAPT_FRAC` | `0.90` | `[0.80, 1.00]` | World-record adaptation fraction for historical RFP thresholds | Escalates requirements when player outpaces history by $>11\%$ |

---

## 7. Edge Cases & Failure Modes

1. **Zero or Near-Zero $\sigma_i$ (Div-by-Zero Protection):**
   - If a player or test passes $\sigma_i = 0$, $\sigma_{\text{eff}, i} = \max(\sigma_i, 0.01 \cdot \max(|\mu_i|, 1.0))$ ensures $q_i$ is always finite and smooth.
2. **Lowball / $0.01 Price Exploit ("Buy-In" Exploit):**
   - Blocked in two places: (a) $\hat{B}_{\text{unit}} = \max(B_{\text{unit}}, (1 - \text{PRICE\_REALISM\_TOL}) \cdot E_{\text{unit}})$ caps cost score credit at $90\%$ of the independent should-cost estimate, and (b) FPIF production ceiling is anchored to $1.20 \times B_{\text{unit}}$, so bidding far below actual cost guarantees $100\%$ contractor-paid losses on every aircraft produced.
3. **Impossible Schedule Promise Exploit:**
   - Bidding `promised_first_flight_day = submitted_day + 30` is clamped by the schedule realism floor $t_{\text{ff,floor}} = t_{\text{sub}} + \text{SCHED\_REALISM} \cdot D_{\text{exp}}$, so unrealistic dates give zero extra schedule points while guaranteeing massive late-delivery reputation penalties at First Flight.
4. **Over-Promising on Paper to Win `paper_award` Competitions:**
   - Countered by three mechanisms: (a) low credibility $C$ limits overclaim credit $\lambda_{\text{oc}}$ to $0.15–0.35$, (b) $q_i$ drives up Technical Risk $R_{\text{tech}}$ (costing up to $25 \times W_{\text{risk}}$ points immediately), and (c) at First Flight and IOC, `audit_milestone_promises` inflicts liquidated damages up to $15\%$ of revenue, up to $-20$ reputation loss, permanent decay of $\tau$ (crippling future bids), and a `show_cause` freeze if thresholds are missed.
5. **All Entrants Disqualified / No Bids Submitted:**
   - Handled gracefully: `evaluate_proposals` returns `outcome = "no_responsive_bid"`, `winners = []`, and registers a `CapabilityGapRecord` so the military re-issues a revised RFP 12–18 months later.
6. **All Fly-Off Finalists Fail a Threshold Gate:**
   - Handled explicitly via the Waiver / Cancellation roll (§5.6 Case B), accurately reproducing both the 1948 All-Weather Fighter outcome (F-89 awarded under waiver despite all prototypes missing requirements) and the 1950 Penetration Fighter outcome (program cancelled after naming XF-88 winner).

---

## 8. Golden Test Vectors

Generated deterministically by `sim/mic/procurement/golden_gen.py` and verified by `sim/tests/test_procurement.py` (relative tolerance `1e-6`):

1. `sim/golden/procurement_scoring_vectors.json`
   - **Vector 1 (`honest_vs_overclaim_newcomer`):** Identical aircraft design ($\mu = 1.25$ Mach, $\sigma = 0.08$) submitted by a low-credibility newcomer ($R=35, \tau=0.40$) vs. an honest incumbent ($R=80, \tau=0.80$), testing `credible_value`, `overclaim_q`, `risk_score`, and `total_score`.
   - **Vector 2 (`lowball_price_and_schedule_realism`):** Verifies should-cost floor clamping on a $50\%$ lowball bid and schedule realism clamping on a 180-day promised first flight.
   - **Vector 3 (`non_responsive_disqualification`):** Verifies hard gate rejection on threshold miss, missing radar/crew equipment, and $>1.30\times$ price ceiling.
2. `sim/golden/procurement_lifecycle_vectors.json`
   - **Vector 1 (`flyoff_usn_fad_1955_f4h_vs_f8u3`):** Full two-stage paper downselect + 1958 fly-off between McDonnell XF4H-1 Phantom II and Vought XF8U-3 Crusader III, verifying equipment gates, fly-off measured scoring, and winner selection.
   - **Vector 2 (`flyoff_waiver_and_promise_audit`):** All-fail fly-off waiver roll, IOC promise shortfall audit on YF-102 pre-area-rule (Mach 0.98 actual vs Mach 1.25 promised), liquidated damages, track record update, and `show_cause` trigger.
   - **Vector 3 (`annual_lot_review_and_f108_cancellation`):** Annual July 1 lot review under normal conditions vs. post-Sputnik obsolescence shock ($\Omega_{\text{obs}} = 1.4$) on `usaf_ws202a_1955` (F-108 Rapier).
3. `sim/golden/procurement_dynamic_vectors.json`
   - **Vector 1 (`alt_history_adaptation_and_redirection`):** Adaptive threshold escalation when player flies a Mach 1.60 fighter before 1952, stopgap suppression of `usn_f11f_1953`, and follow-on redirection.
   - **Vector 2 (`procedural_rfp_and_unsolicited_pitch`):** Monthly demand trigger after MiG-15 threat shock, procedural RFP synthesis, and unsolicited proposal evaluation (CL-246 / N-156 style).

---

## 9. Interactions with Other Modules

| Module | Direction | Contract / Data Exchanged |
|---|---|---|
| **01 Aero & Performance** (`mic.aero`, `mic.perf`) | `01 → 05` | Provides `PerformanceReport` keys (`max_mach_alt`, `climb_rate_sl_mps`, `service_ceiling_m`, `combat_radius_m`, `stall_speed_mps`, `carrier_suitability`, `unit_flyaway_cost_usd`, `dev_cost_usd_estimate`, etc.) and `AircraftDesign` configuration flags. |
| **02 Engines** (`mic.engine`) | `02 → 05` | Provides `unflown_engine` status for `NoveltyProfile` and engine availability for AI competitor proposals. |
| **03 Tech Tree** (`mic.tech`) | `03 → 05` | Provides `TechContext` (`03_tech_effect_keys.md`) to validate equipment unlocks (`avionics.radar_search`, `armament.internal_bay`, `armament.missile_ir_gen`, `armament.missile_sarh_gen`) and count `unproven_tech_count`. |
| **04 Economy** (`mic.econ`) | `04 ↔ 05` | `04 → 05`: `CompanyState` (`reputation`, `political_capital`, `factory_floor_m2`). `05 → 04`: `ContractState` CPFF development reimbursements + fixed fee, FPIF production lot revenues/cost-sharing, liquidated damages, and reputation deltas. |
| **06 Testing & Uncertainty** (`mic.testing`) | `06 → 05` | Provides `Estimate(value, sigma, source)` for paper proposals (`sim`/`tunnel`) and fly-offs (`flight`), plus discovered unfixed `HiddenFlaw` severities and `show_cause` fix project completion. |
| **07 Competitor AI** (`mic.ai`) | `07 ↔ 05` | `05` provides `ai_competitor.py` baseline historical/dynamic bid generator and emits `HistoricalLossEvent` when the player takes a contract from its historical winner. |
| **08 UI / UX** (`08_ui_ux.md`) | `05 → 08` | Provides `preview_bid_evaluation()` for live bid-screen confidence/risk preview and `generate_debrief_report()` for post-award Source Selection Board debriefs. |
| **09 Core Loop** (`mic.campaign`) | `09 ↔ 05` | Calls `05` on RFP issue dates, `proposal_due`, `flyoff_date`, `ioc_due`, monthly dynamic RFP checks (1st of month), and annual lot reviews (July 1) passing a deterministic `RandomSource`. |
| **10 Historical Content** (`10_content.md`) | `10 → 05` | Canonical company IDs (`north_american`, `lockheed`, `mcdonnell`, `republic`, `convair`, `northrop`, `curtiss_wright`, `grumman`, `douglas`, `vought`, `bell`) and localized display strings (`name_key`). |

---

## 10. Validation Results Summary

Full report generated by `sim/mic/procurement/replay.py` at [`docs/validation/procurement_replay.md`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/procurement_replay.md):

- **Historical Winner Match Rate (All 16 Programs, 1945–1960):** **16 / 16 (100.0%)** when replayed with historical entrant specifications and documented political context; **16 / 16 (100.0%)** on pure technical merit alone ($\Delta_{\text{pol}} = 0$).
- **MVP Core Programs Match Rate (8 MVP Programs):** **8 / 8 (100.0%)**, including multi-stage fly-offs (`usaf_aw_int_1945` Northrop F-89 over Curtiss XF-87, `usaf_pen_fighter_1946` McDonnell XF-88A over Lockheed XF-90A and NAA YF-93A, and `usn_fad_1955` McDonnell XF4H-1 Phantom II over Vought XF8U-3 Crusader III).
- **Incumbent Bias Sensitivity Analysis:** A newcomer with zero political capital and baseline reputation ($R=50$, $I_{\text{inc}}=0$) facing an entrenched incumbent ($R=80$, $I_{\text{inc}}=0.50$, $\Delta_{\text{pol}} \approx +6.0$ pts) overcomes the political disadvantage by achieving an average **+7.7% performance margin** across weighted criteria (or a **+5.5% performance margin combined with a -12% unit price advantage and wind-tunnel-substantiated $\sigma$**).

---

## 11. Open Questions & Cross-Module Change Requests

### 11.1 Open Questions for User (Taste Decisions Only)
1. **Cook-Craigie (`paper_award`) vs. Fly-Off Toggle in Sandbox/Campaign Settings:** Historically, most 1950–1955 USAF Century Series contracts (F-100, F-101, F-102, F-104, F-105) were awarded directly from paper proposals under the Cook-Craigie Plan without a competitive prototype fly-off, whereas 1945–1950 programs (XF-88/90/93, XF-87/89) and key USN contests (F4H vs XF8U-3) held dramatic hardware fly-offs. Should the default campaign strictly follow each program's historical `acquisition.style`, or offer a campaign option *"Always Require Prototype Fly-Offs"* for players who love head-to-head flight competitions on every program?
2. **Visibility of AI Competitor Promises Before `proposal_due`:** Should industrial espionage / trade-press leaks show rough ranges of rival companies' rumoured speed/price targets before bid submission, or should competitor numbers remain completely hidden until the Source Selection Debrief?

### 11.2 Cross-Module Change Requests (for `00_conventions.md` reconciliation)
1. **[CR-05-01] Additive fields on `Requirement` (`00` §4.5):** Preserve all existing top-level keys (`id`, `program_name`, `customer`, `issue_date`, `proposal_due`, `first_flight_due`, `ioc_due`, `criteria`, `budget`, `politics`, `historical`) and formally standardize the additive optional fields `role`, `mvp_core`, `name_key`, `equipment` (for non-`PerformanceReport` hard gates: `carrier_capable`, `radar_required`, `min_crew`, `min_engines`, `internal_bay_required`, `min_guns_20mm`, `missile_capability`), `acquisition`, `eval_weights`, and `alt_history`, plus `objective_value` on criterion items.
2. **[CR-05-02] Reputation Scale in `CompanyState` (`00` §4.6 / Module 04):** Module 05 normalizes `CompanyState.reputation[customer]` assuming a `[0.0, 100.0]` scale with neutral baseline `50.0`. Module 04 should confirm this range (or expose a helper `reputation_0_100(customer)`).
3. **[CR-05-03] Program Display Names in `data/names/` (Module 10):** Per D4 (`00` §1), every program file in `sim/data/programs/*.json` includes a `name_key` (`program.<id>.name`) alongside `program_name` so Module 10 can populate `sim/data/names/programs.json` for localization/rename patches.
