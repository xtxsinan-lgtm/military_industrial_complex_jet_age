# 04 — Company Economy, Cost Model, Workforce, Production, Contracts, and Finance

> **Status**: v1.0 (authoritative specification for Module 04)
> **Owner**: Module 04 (`mic.econ`)
> **Python Reference Oracle**: [`sim/mic/econ/`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/econ/__init__.py)
> **Tunables**: [`sim/data/tuning/econ.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/tuning/econ.json)
> **Data Files**: [`sim/data/economy/inflation_usd.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/economy/inflation_usd.json), [`sim/data/economy/contract_types.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/economy/contract_types.json), [`sim/data/economy/company_start_profiles.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/economy/company_start_profiles.json), [`sim/data/economy/historical_aircraft_costs.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/data/economy/historical_aircraft_costs.json)

---

## 1. Purpose & Player Fantasy

In *Military-Industrial Complex: Jet Age*, the player is **not** an omnipotent air force commander—the player is the Chief Executive and Chief Engineer of a private American combat aircraft manufacturer navigating the turbulent postwar transition (1945–1949 "Valley of Death"), the 1950–1953 Korean War mobilization boom, and the high-stakes supersonic Century Series era (1953–1960).

Aerodynamic brilliance alone does not keep a defense prime alive. Every technical choice in the design studio translates into engineering hours, tooling jigs, exotic titanium machining, shop-floor learning curves, working-capital strain, and contract risk:
- **The Staffing Dilemma**: Retaining a veteran 400-person engineering team between contract awards burns cash every month, yet laying them off triggers severance payouts, crushes morale, and destroys institutional capability just before the next RFP drops (as befell Curtiss-Wright and Brewster).
- **The Contract Risk Trade-Off**: Cost-Plus-Fixed-Fee (`CPFF`) contracts protect the firm during high-risk R&D and prototype flight testing, but cap profit fee at 7–10%. Fixed-Price-Incentive-Firm (`FPIF`) and Firm-Fixed-Price (`FFP`) production contracts reward manufacturing learning-curve mastery, but require the company to finance 25% of Work-in-Process (WIP) inventory out of pocket (75% progress payment rate) and expose the balance sheet to ruinous overruns or late-delivery liquidated damages.
- **The Production Break & Tooling Gamble**: Investing heavily in high-rate hard tooling (`tooling_rate_cap_per_month`) and leasing Government-Owned, Contractor-Operated (`GOCO`) plants allows rapid delivery, but pausing a line without paying to retain the shop-floor crew causes **Anderlohr learning-curve decay** (forgetting), spiking unit costs when follow-on lots arrive.
- **The Iron Triangle**: Large workforce footprints generate **Political Capital** in Congressional districts, which—combined with lobbying—unlocks Government-Furnished Equipment (`GFE`) bailment for private-venture prototypes, Regulation V defense loan guarantees (`V-Loans`), and GOCO plant leases.

---

## 2. Scope (MVP 1945–1960 In / Out)

### 2.1 In Scope for MVP (US 1945–1960)
- **Modified DAPCA-IV / RAND R-1693 Cost Model** (`estimate_costs`): Parametric Cost Estimating Relationships (CERs) for recurring unit flyaway cost (airframe labor, QC, raw materials, GFE engines, avionics, armament), non-recurring development cost (engineering, development support, tooling setup, soft-tooled prototypes, contractor flight-test support), and maintenance man-hours per flight hour (`maint_mh_per_fh`) in **nominal then-year US dollars** (with constant-1950 USD conversion).
- **Wright Cumulative-Average Learning Curve & Anderlohr Production Breaks**: Lot-by-lot airframe cost reduction ($S = 0.80$ baseline, modified by `mfg.learning_curve_rate`) and learning loss across production gaps.
- **US Military Contract Types & Accounting**: `CPFF`, `FPIF` (with target cost, target profit, 80/20 share ratio, and 125% ceiling price), `FFP`, and undefinitized `LETTER` contracts; 75% progress payments and delivery liquidations; ASPR Section XV allowable indirect overhead and IR&D/B&P cost recovery (up to 3.5% of active government direct cost base); and the **Renegotiation Act of 1951** excess-profit clawback above 12% defense return on sales.
- **Engineering Workforce by Discipline**: `aero`, `structures`, `propulsion`, and `systems` FTE pools; hiring rate limits tied to macro labor-market tightness (`inflation_usd.json`); salary multiplier vs. industry benchmark; voluntary attrition; layoff severance and morale shocks; **Brooks's Law** team-scale diminishing returns and onboarding dilution; and total-variation discipline-mix mismatch penalties.
- **Facilities, GFE, and GOCO Plants**: Owned factory floor (`m²`), leased GOCO plants (Fort Worth, Marietta, Palmdale, Columbus), wind tunnel tiers (`0..4`), and GFE engine/radar bailment.
- **Corporate Finance & Solvency**: Credit rating (`AAA` to `D`), revolving credit lines, Defense Production Act Regulation V loans (`V-Loans`, 1950–1958), 5-year corporate bonds, baseline non-fighter subcontracting/commercial revenue buffer (`none`, `subcontracting`, `civil_diversified`), spares & modification kit sustainment revenue, and a 3-month liquidity grace period leading to **Chapter XI reorganization** or forced acquisition.

### 2.2 Out of Scope for MVP (Deferred to Later Phases)
- Equity stock issuance, dividends, and hostile public stock-market takeovers.
- Risky commercial airliner development programs (e.g., Convair 880/990 gamble)—commercial business is represented as an abstract capacity-absorbing buffer tier in MVP.
- Multi-currency exchange rates and foreign offset/licensed co-production accounting (Phase 2 Export module).

---

## 3. Player-Facing Flow

1. **Monthly Financial Dashboard & Budget Allocation (1st of Month)**:
   - Every calendar day (`tick = 1 day`), active engineering projects advance (`step_company_day`). On the **1st of each month**, `step_company_month` executes the comprehensive settlement and updates the Monthly P&L and Cash Flow Statement.
   - The player inspects **Cash**, **Available Credit (Revolver + V-Loan)**, **Credit Rating**, **Monthly Burn / Net Cash Flow**, **Overhead Recovery Ratio**, and **Political Capital**.
2. **Workforce & Project Staffing**:
   - The player sets target headcount per discipline (`aero`, `structures`, `propulsion`, `systems`) and company-wide **Salary Multiplier** ($0.85\times\text{ to }1.30\times$ industry benchmark).
   - The player allocates engineers across active R&D projects, prototype builds, and IR&D tasks. The UI displays real-time **Discipline Balance Efficiency** and **Brooks's Law Team Scale Efficiency** so the player sees why dumping 600 newly hired engineers onto a late project yields diminishing returns.
3. **Contract Negotiation & Bidding (with Module 05)**:
   - When submitting an RFP proposal, `estimate_costs` displays the projected RDT&E cost (`CPFF`) and unit flyaway cost curve across quantities $Q \in [100, 1000]$ (`FPIF` or `FFP`).
   - For private-venture prototypes without a government R&D contract, the player may spend **8 Political Capital** (`request_gfe_bailment`) to borrow GFE engines and radars rather than purchasing them in cash.
4. **Production Line & Facility Management**:
   - Upon winning a production contract, a `ProductionLine` opens. The player sets `target_rate_per_month`, invests in rate tooling (`tooling_rate_cap_per_month`), and allocates factory floor space (`factory_floor_m2` + leased `goco_floor_m2`).
   - If a line runs out of orders before a follow-on lot is awarded, the player chooses whether to toggle **Retain Shop Workforce** (paying 65% idle shop wages to preserve learning-curve position) or allow the line to go cold (incurring Anderlohr learning setback).
5. **Liquidity Crisis & Insolvency**:
   - If `cash_usd` drops below zero after exhausting automatic revolving credit and V-Loan borrowing limits, a **Liquidity Crisis Warning** triggers. If cash remains negative for **3 consecutive months** (`insolvency_grace_months = 3`), the player must either execute a one-time **Chapter XI Reorganization** (35% debt haircut + emergency bridge loan, at the cost of $-20$ Reputation across all services and $-20\%$ engineering attrition) or suffer a **Forced Merger / Takeover** (campaign loss).

---

## 4. Data Schemas

### 4.1 `CompanyState` (Conforming to `00_conventions.md` §4.6)

Implemented in [`sim/mic/econ/company.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/econ/company.py). All monetary values are nominal **then-year US dollars** (`float64`).

| Field | Type | Units / Range | Default (`medium_prime`) | Description |
|---|---|---|---|---|
| `id` | `str` | identifier | `"player_co"` | Unique company identifier. |
| `name` | `str` | display string | `"Player Aviation Corp."` | Display name (loaded from data). |
| `is_player` | `bool` | bool | `True` | `True` for player manufacturer, `False` for AI competitor. |
| `cash_usd` | `float` | then-year USD | `16000000.0` | Liquid cash on hand. |
| `debt_usd` | `float` | then-year USD ($\ge 0$) | `0.0` | Total outstanding interest-bearing debt. |
| `reputation` | `dict[str, float]` | `0.0 .. 100.0` | `{"USAF": 60.0, "USN": 60.0, "export": 45.0}` | Service and export reputation scores. |
| `political_capital` | `float` | `0.0 .. 100.0` | `35.0` | Iron-triangle political leverage score. |
| `engineers` | `dict[str, float]` | FTE ($\ge 0$) | `{"aero": 115, "structures": 145, "propulsion": 45, "systems": 75}` | Active engineering staff by discipline. |
| `facilities` | `dict[str, Any]` | mixed | `{"wind_tunnel_level": 2, "factory_floor_m2": 65000.0, "goco_floor_m2": 0.0, "test_site": True, "nc_machining_installed": False}` | Company facilities and plant capacity. |
| `projects` | `list[EngineeringProjectTask]` | list | `[]` | Active and completed engineering tasks. |
| `aircraft_in_production` | `list[ProductionLine]` | list | `[]` | Active and completed aircraft production lines. |
| `tech_unlocked` | `list[str]` | list of `tech_id` | `[]` | Unlocked technology node IDs (synced with Module 03). |
| `contracts` | `list[DefenseContract]` | list | `[]` | Active and completed defense procurement contracts. |
| `credit_rating` | `str` | `"AAA".."D"` | `"A"` | Current corporate credit rating. |
| `commercial_buffer_level` | `str` | enum | `"subcontracting"` | `"none" \| "subcontracting" \| "civil_diversified"`. |
| `salary_multiplier` | `float` | `0.80 .. 1.50` | `1.0` | Pay multiplier vs. industry benchmark salary. |
| `morale` | `float` | `0.70 .. 1.15` | `1.0` | Workforce morale multiplier on productivity. |
| `recent_hire_fraction` | `float` | `0.0 .. 1.0` | `0.0` | Fraction of workforce within 6-month onboarding window. |
| `lobbying_monthly_spend_usd` | `float` | then-year USD/mo | `0.0` | Monthly active Washington lobbying expenditure. |
| `irad_monthly_spend_usd` | `float` | then-year USD/mo | `0.0` | Monthly discretionary IR&D / B&P overhead spend. |
| `active_delivered_fleet` | `int` | aircraft count | `450` | Operational fleet generating spares/support revenue. |
| `consecutive_insolvent_months` | `int` | months ($\ge 0$) | `0` | Consecutive months with negative cash after credit draw. |
| `chapter_xi_used` | `bool` | bool | `False` | Whether one-time Chapter XI reorganization has been used. |
| `is_bankrupt_or_acquired` | `bool` | bool | `False` | Terminal insolvency state. |

#### JSON Example (`CompanyState`)
```json
{
  "id": "north_american",
  "name": "North American Aviation",
  "is_player": true,
  "cash_usd": 16000000.0,
  "debt_usd": 0.0,
  "reputation": {"USAF": 60.0, "USN": 60.0, "export": 45.0},
  "political_capital": 35.0,
  "engineers": {"aero": 115.0, "structures": 145.0, "propulsion": 45.0, "systems": 75.0},
  "facilities": {
    "wind_tunnel_level": 2,
    "factory_floor_m2": 65000.0,
    "goco_floor_m2": 0.0,
    "test_site": true,
    "nc_machining_installed": false
  },
  "projects": [],
  "aircraft_in_production": [],
  "tech_unlocked": [],
  "contracts": [],
  "credit_rating": "A",
  "commercial_buffer_level": "subcontracting",
  "salary_multiplier": 1.0,
  "morale": 1.0
}
```

### 4.2 `CostEstimate` (Output of `estimate_costs`)
Implemented in [`sim/mic/econ/cost.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/econ/cost.py). Supports both attribute (`est.unit_flyaway_cost_usd`) and dictionary (`est["unit_flyaway_cost_usd"]`) access:
- **Summary Contract Keys (`00_conventions.md` §4.4)**: `unit_flyaway_cost_usd`, `dev_cost_usd_estimate`, `maint_mh_per_fh`.
- **Recurring Breakdown (then-year USD)**: `t1_airframe_cost_usd`, `airframe_unit_cost_usd`, `engine_unit_cost_usd`, `avionics_unit_cost_usd`, `armament_unit_cost_usd`, `gfe_unit_cost_usd`.
- **Non-Recurring RDT&E Breakdown (then-year USD)**: `engineering_cost_usd`, `dev_support_cost_usd`, `tooling_cost_usd`, `prototype_unit_cost_usd`, `prototypes_total_cost_usd`, `flight_test_cost_usd`.
- **Labor Hours & Multipliers**: `engineering_hours`, `tooling_hours`, `t1_mfg_labor_hours`, `avg_mfg_labor_hours`, `avg_qc_hours`, `learning_curve_rate`, `wright_labor_factor`, `wright_material_factor`, `complexity_factor`, `material_mix_factor`, `immaturity_penalty_dev`, `immaturity_penalty_mfg`.
- **Constant-1950 USD Display Fields (`00_conventions.md` §3)**: `constant_1950_unit_flyaway_usd`, `constant_1950_dev_cost_usd`, `cpi_index`, `aero_cost_index`.

### 4.3 `DefenseContract`, `ProductionLine`, and `EngineeringProjectTask`
- **`DefenseContract`** ([`sim/mic/econ/contracts.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/econ/contracts.py)): `contract_id`, `program_id`, `customer` (`USAF|USN|export`), `contract_type` (`CPFF|FPIF|FFP|LETTER`), `phase` (`rdte|production`), `target_cost_usd`, `target_profit_or_fee_usd`, `ceiling_price_usd`, `govt_share_ratio`, `unit_price_usd`, `quantity`, `gfe_provided`, `incurred_cost_usd`, `reimbursed_or_progress_paid_usd`, `delivery_payments_received_usd`, `fee_paid_usd`, `units_delivered`, `undefinitized_months_elapsed`, `completed`.
- **`ProductionLine`** ([`sim/mic/econ/production.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/econ/production.py)): `line_id`, `design_id`, `contract_id`, `airframe_mass_lb`, `t1_airframe_cost_usd`, `gfe_unit_cost_usd`, `learning_curve_rate`, `target_rate_per_month`, `current_rate_per_month`, `tooling_rate_cap_per_month`, `total_quantity_ordered`, `cumulative_units_built`, `fractional_unit_wip`, `idle_months`, `break_setback_units`, `retain_workforce`, `months_elapsed`, `scheduled_months`, `months_late`, `completed`.
- **`EngineeringProjectTask`** ([`sim/mic/econ/workforce.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/econ/workforce.py)): `project_id`, `name`, `kind`, `total_hours_required`, `hours_completed`, `allocated_engineers`, `required_shares`, `contract_id`, `is_irad_or_bp`, `completed`.

---

## 5. Algorithms & Exact Formulas

### 5.1 Inflation & Aerospace Cost Escalation ([`sim/mic/econ/inflation.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/econ/inflation.py))
`sim/data/economy/inflation_usd.json` tabulates two indices anchored at **Base Year 1950 = 1.0000**:
1. **`cpi_index_1950(year)` ($I_{\text{CPI}}(y)$)**: US Bureau of Labor Statistics CPI-U (`1982–84 = 100`, where $1950 = 24.1 \implies I_{\text{CPI}}(1950) = 1.0000$). Used by UI helper `to_constant_1950_usd(then_year_usd, year)` for constant-1950-dollar displays (`00_conventions.md` §3).
2. **`aero_cost_index_1950(year)` ($I_{\text{aero}}(y)$)**: Aerospace industry composite cost index ($65\%$ BLS SIC 372 Aircraft & Parts production/engineering labor index $+ 35\%$ BLS industrial metals/components wholesale price index, $1950 = 1.0000$). Because real aerospace wages grew faster than headline CPI during the 1950s ($I_{\text{CPI}}(1960) = 1.2282$ vs. $I_{\text{aero}}(1960) = 1.6500$), all 1950 base-year CER outputs are multiplied by $I_{\text{aero}}(y)$ to yield **nominal then-year USD**.

### 5.2 Modified DAPCA-IV / RAND R-1693 Cost Model ([`sim/mic/econ/cost.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/econ/cost.py))
Adapted from **Raymer (2018, Ch. 18)** and **RAND R-1693-PA&E (Large, Campbell, Cates 1976)**:

1. **Normalized Airframe Weight & Speed**:
   $$W_a = \frac{\max(400.0,\; m_{\text{empty,kg}} - N_{\text{eng}} m_{\text{eng,kg}})}{0.45359237}\;\text{[lb]}, \qquad \tilde{W} = \frac{W_a}{10,000\text{ lb}}$$
   $$V_{\text{kt}} = 573.57 \cdot M_{\max}\;\text{[kt]}, \qquad \tilde{V} = \frac{V_{\text{kt}}}{500\text{ kt}}$$

2. **Aerodynamic, Structural, and Feature Complexity Multiplier ($C_{\text{total}}$)**:
   $$C_{\text{mach}} = 1 + 0.05 \cdot \max(0,\; M_{\max} - 0.85)^{1.30}$$
   $$C_{tc} = \left[1 + 7.0 \cdot \max(0,\; 0.11 - (t/c)) + 420.0 \cdot \max(0,\; 0.055 - (t/c))^2\right] \cdot \begin{cases} 0.92 & \text{if } \texttt{mfg.nc\_machining} \land (t/c) < 0.08 \\ 1.0 & \text{otherwise} \end{cases}$$
   $$C_{\text{sweep}} = 1 + 0.0071 \cdot \max(0,\; \Lambda_{\text{deg}} - 10^\circ)$$
   $$C_{\text{feat}} = 1 + 0.14\mathbb{I}_{\text{carrier}} + 0.04\mathbb{I}_{\text{area\_rule}} + 0.06\mathbb{I}_{\text{int\_bay}} + 0.05\mathbb{I}_{\text{var\_inlet}} + 0.04\mathbb{I}_{\text{delta}} + 0.22\mathbb{I}_{\text{var\_sweep}} + 0.18\mathbb{I}_{\text{av}\ge 4} + 0.20\mathbb{I}_{N_{\text{eng}}\ge 2} + 0.12\mathbb{I}_{\text{AB}}$$
   $$C_{\text{total}} = C_{\text{mach}} \cdot C_{tc} \cdot C_{\text{sweep}} \cdot C_{\text{feat}}$$

3. **Material Mix & Tech Immaturity Multipliers**:
   $$C_{\text{mat}} = \left(1.0 f_{\text{Al}} + 1.6 f_{\text{steel}} + 4.5 f_{\text{Ti}} \cdot \texttt{mfg.titanium\_cost\_factor}\right) \cdot (1.05 \text{ if } \texttt{struct.honeycomb} \text{ else } 1.0)$$
   For a design using unlocked technologies $T_{\text{used}}$ with mean immaturity $\bar{u} = \frac{1}{|T_{\text{used}}|}\sum_{t \in T_{\text{used}}}(1 - \text{maturity}(t))$:
   $$M_{\text{imm,dev}} = 1 + 0.35\bar{u}, \qquad M_{\text{imm,mfg}} = 1 + 0.20\bar{u}$$

4. **Wright (1936) Cumulative-Average Learning Curve**:
   Given learning slope $S \in (0, 1]$ (`mfg.learning_curve_rate`, default $S_{\text{lab}} = 0.80$, $S_{\text{mat}} = 0.90$), the exponent is $b = \log_2(S)$. Across $Q$ units, the cumulative-average factor is:
   $$F_{\text{avg}}(Q, S) = \frac{(Q + 0.5)^{1+b} - 0.5^{1+b}}{(1 + b) Q}$$

5. **Recurring Unit Airframe & Flyaway Cost (Then-Year USD)**:
   $$H_{\text{mfg},T_1} = 70,713 \cdot \tilde{W}^{0.7003} \cdot \tilde{V}^{0.6086} \cdot C_{\text{total}} \cdot \texttt{mfg.labor\_hours\_factor} \cdot M_{\text{imm,mfg}}$$
   $$\bar{H}_{\text{mfg}}(Q) = H_{\text{mfg},T_1} \cdot F_{\text{avg}}(Q, S_{\text{lab}}), \qquad \bar{H}_{\text{QC}}(Q) = 0.13 \cdot \texttt{mfg.quality\_defect\_factor} \cdot \bar{H}_{\text{mfg}}(Q)$$
   $$C_{\text{mat},T_1,1950} = 0.22 \cdot \left(\frac{H_{\text{mfg},T_1}}{\texttt{mfg.labor\_hours\_factor}}\right) \cdot 5.40 \cdot C_{\text{mat}} \cdot \texttt{mfg.material\_cost\_factor}$$
   $$\bar{C}_{\text{airframe},1950}(Q) = 5.40\,\bar{H}_{\text{mfg}}(Q) + 5.80\,\bar{H}_{\text{QC}}(Q) + C_{\text{mat},T_1,1950} \cdot F_{\text{avg}}(Q, 0.90)$$
   $$\text{AirframeUnitCost}_{\text{USD}} = I_{\text{aero}}(y) \cdot \bar{C}_{\text{airframe},1950}(Q)$$
   Adding GFE/CFE engines ($N_{\text{eng}} \cdot C_{\text{eng,USD}}$), avionics tier cost $I_{\text{aero}}(y) C_{\text{av},1950}(\text{level})$, and armament $I_{\text{aero}}(y) C_{\text{arm},1950}$ yields `unit_flyaway_cost_usd`.

6. **Non-Recurring Development (RDT&E) Cost (Then-Year USD)**:
   $$C_{\text{av,dev}} = 1 + 0.02 \cdot \max(0,\; \text{level}_{\text{av}} - 1)^{1.25}$$
   $$H_{\text{eng}} = 708,130 \cdot \tilde{W}^{0.6753} \cdot \tilde{V}^{0.9582} \cdot C_{\text{total}} \cdot C_{\text{av,dev}} \cdot M_{\text{imm,dev}}$$
   $$C_{\text{eng},1950} = 6.80 \cdot H_{\text{eng}}, \qquad C_{\text{dev\_support},1950} = 0.28 \cdot C_{\text{eng},1950}$$
   $$H_{\text{tool}} = 0.55 \cdot \left(\frac{H_{\text{eng}}}{C_{\text{av,dev}}}\right) \cdot \tilde{V}^{-0.20} \cdot \texttt{mfg.tooling\_cost\_factor}, \qquad C_{\text{tool},1950} = 6.20 \cdot H_{\text{tool}}$$
   $$C_{\text{proto\_unit},1950} = 1.35 \cdot (5.40\,H_{\text{mfg},T_1} + C_{\text{mat},T_1,1950}) + \frac{N_{\text{eng}} C_{\text{eng,USD}}}{I_{\text{aero}}(y)} + C_{\text{av},1950}$$
   $$C_{\text{ft},1950} = 0.18 \cdot C_{\text{eng},1950} \cdot N_{\text{proto}}^{0.55}$$
   $$\text{dev\_cost\_usd\_estimate} = I_{\text{aero}}(y) \cdot \left(C_{\text{eng},1950} + C_{\text{dev\_support},1950} + C_{\text{tool},1950} + N_{\text{proto}} C_{\text{proto\_unit},1950} + C_{\text{ft},1950}\right)$$

### 5.3 Workforce, Brooks's Law, and Discipline Mismatch ([`sim/mic/econ/workforce.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/econ/workforce.py))
- **Brooks's Law Efficiency** (Brooks 1975): For total project team size $N_{\text{FTE}}$ and recent-hire fraction $f_{\text{new}} \in [0, 1]$:
  $$\eta_{\text{Brooks}} = \text{clamp}\!\left(\min\!\left(1.0,\; \left(\frac{N_{\text{FTE}}}{250}\right)^{0.85 - 1}\right) \cdot (1 - 0.40 f_{\text{new}}),\; 0.25,\; 1.0\right)$$
- **Discipline Mix Efficiency**: Given allocated share vector $p_d$ vs. required share vector $q_d$ across $d \in \{\text{aero}, \text{structures}, \text{propulsion}, \text{systems}\}$:
  $$\text{TV} = \frac{1}{2}\sum_d |p_d - q_d|, \qquad \eta_{\text{mix}} = \max(0.35,\; 1 - 0.60 \cdot \text{TV})$$
- **Monthly Effective Engineering Hours**:
  $$H_{\text{eff,mo}} = 160 \cdot N_{\text{FTE}} \cdot \eta_{\text{mix}} \cdot \eta_{\text{Brooks}} \cdot \text{clamp}(\text{morale},\; 0.70,\; 1.15)$$

### 5.4 Production Lines & Anderlohr Learning Loss ([`sim/mic/econ/production.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/econ/production.py))
- **Lot Cost**: Delivering units $[n_1, n_2]$ costs $\sum_{i=n_1}^{n_2} C_{T_1} F_{\text{unit}}(i - \Delta n_{\text{break}}, S_{\text{lab}})$.
- **Anderlohr (1969) Production Break Setback**: Each idle month ($R_{\text{target}} = 0$) when `retain_workforce == False` increases $\Delta n_{\text{break}}$ by $3.5\%$ of cumulative units built (capped at $45\%$ setback).

### 5.5 Defense Contracts, Progress Payments, Overhead & Renegotiation ([`sim/mic/econ/contracts.py`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/econ/contracts.py))
- **CPFF**: Reimburses $100\%$ of allowable cost up to $1.25 C_{\text{target}}$ plus fixed fee $F_{\text{fixed}} = r_{\text{fee}} C_{\text{target}}$ ($15\%$ of fee withheld until completion).
- **FPIF**: Pays $75\%$ progress payments on incurred cost (capped at $80\%$ of target price). At completion, final contract price is:
  $$P_{\text{final}} = \min\!\left(P_{\text{ceiling}},\; C_{\text{actual}} + \Pi_{\text{target}} + (1 - s_{\text{govt}})(C_{\text{target}} - C_{\text{actual}})\right) \cdot (1 - \text{penalty}_{\text{late}})$$
- **ASPR Section XV Overhead & IR&D Recovery**: Recoverable IR&D/B&P is capped at $3.5\%$ of active government direct cost base; total allowable indirect overhead is capped at $115\%$ of direct cost base.
- **Renegotiation Act of 1951 (`year >= 1951`)**: At year-end (`month == 12`), if annual defense pre-tax return on sales exceeds $12.0\%$, the Renegotiation Board claws back $65\%$ of excess profit.

---

## 6. Tunables Table (`sim/data/tuning/econ.json`)

| Name | Default | Range | Effect | Rationale |
|---|---:|---|---|---|
| `cer.k_mfg_t1_hours` | `70713.0` | `50000..100000` | Scales $T_1$ manufacturing labor hours | Least-squares fit to 12 historical US fighters (MAPE 7.75%). |
| `cer.exp_mfg_weight` | `0.7003` | `0.60..0.85` | Airframe weight exponent on mfg labor | RAND R-1693 / DAPCA-IV empirical range. |
| `cer.exp_mfg_speed` | `0.6086` | `0.45..0.85` | Speed exponent on mfg labor | Captures tighter tolerances at higher speed. |
| `cer.default_learning_curve_labor` | `0.80` | `0.72..0.90` | Wright labor learning slope $S_{\text{lab}}$ | Standard 80% aerospace airframe learning curve (Wright 1936). |
| `cer.k_eng_dev_hours` | `708130.0` | `400000..1100000` | Scales non-recurring engineering hours | Calibrated to RAND R-1693 RDT&E totals (MAPE 10.28%). |
| `workforce.brooks_law_ref_team_fte` | `250.0` | `100..500` | Team size threshold for Brooks's Law | Above 250 FTE, communication overhead scales as $(N/250)^{-0.15}$. |
| `workforce.discipline_mismatch_penalty_k` | `0.60` | `0.20..1.00` | Throughput penalty per unit TV mismatch | Soft Leontief constraint (20% mismatch costs 12% efficiency). |
| `production.anderlohr_break_loss_per_month` | `0.035` | `0.01..0.08` | Learning setback per cold month | Anderlohr (1969) production-break loss of learning. |
| `contracts.progress_payment_rate_fp` | `0.75` | `0.50..0.90` | Fixed-price progress payment fraction | Historical 1950s DoD standard 75% progress payment rate. |
| `contracts.irad_bp_allowable_recovery_cap_frac` | `0.035` | `0.01..0.08` | Max IR&D/B&P recovered in overhead | ASPR Section XV negotiated IR&D allowability ceiling. |
| `contracts.renegotiation_act_exempt_return_on_sales` | `0.12` | `0.08..0.18` | Pre-tax ROS exempt from clawback | Renegotiation Act of 1951 historical benchmark (~12% ROS). |
| `finance.insolvency_grace_months` | `3` | `1..6` | Months negative cash before Chapter XI | Gives player 3 months to cut burn or sell assets. |

---

## 7. Edge Cases & Failure Modes

1. **Zero or Negative Airframe Mass**: If `empty_mass_kg <= engine_count * engine_mass_kg`, `airframe_mass_kg` is clamped to `400.0 kg` so fractional exponents never see zero or negative numbers.
2. **Unnormalized Material Mix**: If `al + steel + ti != 1.0`, fractions are normalized by their sum (floored at `1e-6`).
3. **Missing `max_mach` When Called Before Performance Solver**: If Module 01 calls `estimate_costs` before solving `max_mach`, `cost.py` uses a deterministic physics proxy from `afterburner`, `inlet_variable`, `wing_sweep_deg`, and `delta_wing`.
4. **Zero-Quantity or Single-Unit Calls**: `quantity < 1` is clamped to `1`, and `wright_cumulative_average_factor(1, S)` returns `1.0` exactly.
5. **Overrun Above Contract Ceiling**: On `CPFF`, costs above `1.25 * target_cost_usd` are unallowable (absorbed $100\%$ by the contractor). On `FPIF`, once total price hits `ceiling_price_usd = 1.25 * target_cost_usd`, effective share ratio becomes $0/100$ (contractor absorbs $100\%$ of further overruns).

---

## 8. Golden Test Vectors

Generated by the Python reference implementation and verified in `sim/tests/test_econ.py` to relative tolerance `1e-6`:
1. **[`sim/golden/econ_cost_historical.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/golden/econ_cost_historical.json)**: 13 deterministic vectors covering all 12 historical US fighters (`f80c_shooting_star` through `f106a_delta_dart`) plus `f104a_with_tech_context_and_immaturity` verifying all `mfg.*`, `struct.honeycomb`, `engine.mtbf_factor`, `avionics.reliability_factor`, and tech immaturity modifiers.
2. **[`sim/golden/econ_contracts_and_settlement.json`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/golden/econ_contracts_and_settlement.json)**: Deterministic vectors for `wright_cumulative_average_factor`, `wright_lot_average_factor` (with and without Anderlohr break setback), `CPFF` and `FPIF` multi-step contract settlements, ASPR overhead/IR&D recovery, 1953 Renegotiation Act clawback, and a 12-month full-year `CompanyState` settlement ledger.

---

## 9. Interactions with Other Modules

- **Module 01 (`mic.aero` / `mic.perf`)**: Calls `mic.econ.cost.estimate_costs(design, mass_breakdown, engine, quantity, year, company, tech_context)` to populate `unit_flyaway_cost_usd`, `dev_cost_usd_estimate`, and `maint_mh_per_fh` in `PerformanceReport` (§4.4).
- **Module 02 (`mic.engine`)**: Supplies `EngineSpec` (`mass_kg`, `unit_cost`, `maint_mh_per_fh`, `dry_thrust_N`).
- **Module 03 (`mic.tech`)**: Supplies `TechContext` with `mfg.*`, `struct.honeycomb`, `engine.mtbf_factor`, `avionics.reliability_factor`, and `tech_maturity` (`03_tech_effect_keys.md`).
- **Module 05 (`mic.procurement`)**: Reads `CompanyState.reputation`, `political_capital`, and `CostEstimate` during RFP evaluation; awards `DefenseContract` (`CPFF`, `FPIF`, `FFP`, `LETTER`) to the winning `CompanyState`.
- **Module 06 (`mic.testing`)**: Reads `CompanyState.facilities["wind_tunnel_level"]` and `test_site`; charges `HiddenFlaw.fix_cost_usd` against `CompanyState.cash_usd`.

---

## 10. Validation Results

1. **Historical Fighter Cost Calibration ([`docs/validation/econ_cost_calibration.md`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/econ_cost_calibration.md))**:
   - Calibrated against **12 historical US fighters (1945–1960)**: `F-80C`, `F-84E`, `F-86F`, `F-89D`, `F4D-1`, `F-100D`, `F-102A`, `F8U-1`, `F-101B`, `F-104A/C`, `F-105D`, `F-106A`.
   - **Unit Flyaway Cost MAPE = 7.75%** (Max Error = **19.23%** on `F-104A/C`).
   - **RDT&E Development Cost MAPE = 10.28%** (Max Error = **21.98%** on `F-100D`).
2. **Monte-Carlo Campaign Cash-Flow & Solvency ([`docs/validation/econ_cashflow.md`](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/econ_cashflow.md))**:
   - **2,400 16-year campaigns** across 4 strategies $\times$ 5 win-rate tiers confirm a clean Pareto frontier (`conservative_lean` wins at $p_{\text{win}} \le 0.20$; `balanced_prime` wins at $p_{\text{win}} = 0.33$ with `$30.9M` median net worth and `80.0%` survival; `aggressive_expander` wins at $p_{\text{win}} \ge 0.50$ with `$64.4M` median net worth at $p_{\text{win}} = 0.67$).
   - Removing the baseline subcontracting buffer (`no_commercial_buffer`) increases bankruptcy at $p_{\text{win}} = 0.33$ by **+23.3 percentage points** (`43.3%` vs. `20.0%`).

---

## 11. Open Questions & Cross-Module Change Requests

### 11.1 Open Questions for User (Taste / Design Preference Only)
1. **Chapter XI Reorganization Frequency**: Currently, a player company may survive one severe liquidity crisis per campaign via Chapter XI reorganization (`35%` debt haircut, `-20` reputation, `-20%` engineers), and a second insolvency triggers a forced merger/game-over. Would you prefer Chapter XI to be available once per decade on Normal difficulty and disabled on Hardcore difficulty?
2. **Renegotiation Board Visibility**: Should the Renegotiation Act of 1951 excess-profit clawback (`month == 12`) be settled automatically as a line item on the Year-End Financial Statement, or presented as an interactive hearing event where the player can spend Political Capital to contest the clawback?

### 11.2 Cross-Module Change Requests
- **None required on `00_conventions.md` or `03_tech_effect_keys.md`**: `CompanyState` (§4.6), `PerformanceReport` cost fields (§4.4), and all `mfg.*` / `struct.*` / `engine.*` / `avionics.*` tech keys in `03_tech_effect_keys.md` are consumed with zero schema changes.
- **Note for Module 01 (`mic.perf`)**: When calling `mic.econ.cost.estimate_costs(design, mass_breakdown, engine, quantity, year, company, tech_context, max_mach=...)`, pass the solved `max_mach = max(max_mach_sl, max_mach_alt)` keyword argument once envelope solving completes so that supersonic speed complexity uses the exact aerodynamic Mach number rather than the pre-solve proxy.
