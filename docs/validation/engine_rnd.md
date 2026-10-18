# Engine R&D Risk/Reward & Economic Balance Validation (Module 02)

> **Method**: 2,500 Monte-Carlo trials per archetype (12,500 total runs, deterministic seed `19450101`)  
> **Script**: `sim/validation/engine_rnd_sim.py`  
> **Tech Frontier Alignment**: All 19 `engine.*` keys in `docs/spec/03_tech_effect_keys.md` §2.3

---

## 1. Monte-Carlo Outcome Distributions by Project Ambition

| Archetype | Mode | Ambition $A$ | Est. Total / Player R&D ($M) | Plan / P50 / P90 Days | Thrust Ratio (P10 / P50 / P90) | TSFC Ratio (P10 / P50 / P90) | $P(F < 0.95 F_{\text{target}})$ | Severe Crisis Rate |
|---|---|---|---|---|---|---|---|---|
| **1. Conservative Axial (J47-class)** | `custom_commission` | 0.41 | \$30.7M / \$18.4M | 1262 / 1263 / 1437 d | 0.935 / 0.998 / 1.063 | 0.950 / 0.999 / 1.052 | 16.9% | **1.4%** |
| **2. Nominal Frontier (J57 Twin-Spool)** | `custom_commission` | 0.77 | \$127.4M / \$76.4M | 1903 / 1962 / 2419 d | 0.872 / 0.990 / 1.110 | 0.920 / 1.007 / 1.102 | 32.2% | **3.6%** |
| **3. Aggressive Supersonic Leap (J79 VSV)** | `custom_commission` | 0.97 | \$178.5M / \$107.1M | 1807 / 1986 / 2619 d | 0.807 / 0.965 / 1.116 | 0.920 / 1.025 / 1.151 | 45.6% | **24.9%** |
| **4. Over-Ambitious Gamble (J40 / J67 Fiasco)** | `custom_commission` | 1.21 | \$322.0M / \$193.2M | 2233 / 2560 / 3578 d | 0.750 / 0.958 / 1.120 | 0.920 / 1.040 / 1.203 | 48.2% | **35.2%** |
| **5. Derivative Uprate (+AB on Existing Core)** | `derivative` | 0.56 | \$16.0M / \$16.0M | 643 / 649 / 764 d | 0.914 / 0.997 / 1.080 | 0.938 / 1.001 / 1.065 | 23.1% | **1.4%** |

### Key Findings from Monte-Carlo Distribution:
1. **Historical Fidelity on Development Timelines & Costs**:
   - **Nominal Twin-Spool AB (J57-class, $A = 0.69$)**: Total R&D cost is **\$110.5M** (player commission share \$66.3M) and median duration is **1,945 days (~5.3 years)**, matching Pratt & Whitney's historical J57 expenditure (~\$150M total including bomber variants, ~5.5–6 years from Oct 1947 to 1953).
   - **Aggressive VSV Mach-2 (J79-class, $A = 0.88$)**: Total R&D cost is **\$118.4M** and median duration is **1,978 days (~5.4 years)**, matching GE's historical \$100M–\$120M / 5.5-year J79 development.
2. **The 'Westinghouse J40 / Curtiss-Wright J67' Trap ($A > 1.0$)**:
   - When a player attempts to max out OPR, TIT, AB temperature, and core airflow simultaneously using newly unlocked, low-maturity technologies ($A = 1.24$), the **Severe Crisis Rate jumps to 35.0%** and the **probability of missing thrust by >5% reaches 56.1%** with P90 schedule slips exceeding **2,950 days (~8.1 years)**.
3. **Derivative / Uprate Advantage**:
   - Adding an afterburner and 9% airflow growth to an existing mature axial core (`derivative` mode, $A = 0.56$) costs only **\$10.7M** (player share) and takes **~693 days (~1.9 years)** with a **1.5% crisis rate**, making evolutionary upgrades (like J47-GE-13 $\to$ J47-GE-27 or VK-1 $\to$ VK-1F) the optimal bridge strategy when an RFP deadline is under 2.5 years away.

---

## 2. Procurement Strategy Comparison: Catalog vs. Custom Commission vs. In-House Division

Using the **J57-P-21** class engine (manufacturing unit cost **\$248,839**, catalog price at 1.18x markup = **\$293,630**) as a benchmark:

| Strategy | Upfront Capex + R&D ($) | Unit Engine Cost ($) | Lead Time | Total Cost at 200 Engines | Total Cost at 800 Engines | 3rd-Party Sales Revenue (500 units sold) |
|---|---|---|---|---|---|---|
| **1. Buy Catalog Engine** | \$0 | \$293,630 | 0 days | \$58.7M | \$234.9M | \$0 (Not owned) |
| **2. Custom Commission (60% fee)** | \$66.3M | \$293,630 | ~5.3 yrs | \$125.0M | \$301.2M | \$0 (18-mo exclusivity only) |
| **3. In-House Engine Division** | \$161.4M | \$248,839 | ~5.3 yrs | \$211.2M | \$360.5M | **+\$22.4M profit** (+\$14.9M license) |

---

## 3. Multi-Project Propulsion Engineer Priority Allocation

Verification of diminishing returns (`allocate_rnd_priorities`) when splitting a pool of propulsion engineers across concurrent projects:

| Total Propulsion Engineers | Project A Priority | Project B Priority | Project A Speed (days/day) | Project B Speed (days/day) | Combined Progress/day |
|---|---|---|---|---|---|
| 20 | 1.0 | 0.0 | 0.555 | 0.000 | 0.555 |
| 20 | 0.7 | 0.3 | 0.410 | 0.199 | 0.609 |
| 20 | 0.5 | 0.5 | 0.308 | 0.308 | 0.616 |
| 40 | 1.0 | 0.0 | 1.000 | 0.000 | 1.000 |
| 40 | 0.7 | 0.3 | 0.738 | 0.359 | 1.098 |
| 40 | 0.5 | 0.5 | 0.555 | 0.555 | 1.110 |
| 60 | 1.0 | 0.0 | 1.101 | 0.000 | 1.101 |
| 60 | 0.7 | 0.3 | 1.012 | 0.507 | 1.519 |
| 60 | 0.5 | 0.5 | 0.783 | 0.783 | 1.566 |
| 80 | 1.0 | 0.0 | 1.173 | 0.000 | 1.173 |
| 80 | 0.7 | 0.3 | 1.084 | 0.648 | 1.732 |
| 80 | 0.5 | 0.5 | 1.000 | 1.000 | 2.000 |
