# Validation #3 — Full Integrated Campaign & 4-Bot Monte-Carlo Balance Report

- **Campaign Horizon**: 1945-08-15 to 1960-12-31 (16 Historical RFPs, 5,618 simulated days)
- **Default Mode (Locked Decision D6)**: `force_flyoff=True` (200 campaigns = 50 seeds × 4 bot archetypes)
- **Historical Acquisition Style Comparison**: `force_flyoff=False` (200 campaigns)
- **Total Campaigns Executed**: 400 deterministic 1945–1960 campaigns in `317.74s`

---

## 1. Executive Summary & Dominant Strategy Check

| Bot Archetype | Bids / 16 | Downselects | Contracts Won (Mean ± SD) | Win Rate (of Bids) | Aircraft Built | Ending Net Worth (1950 USD) | Chapter XI / Bankruptcy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **BalancedPrimeBot** | 16.0 | 6.32 | **3.40 ± 1.40** (P10=2, P90=5) | 21.2% (21.2% all) | 1537 | **\$43.44M** (\$13.0M–\$74.8M) | 2.0% / 2.0% |
| **TechPioneerBot** | 13.0 | 5.90 | **3.24 ± 0.97** (P10=2, P90=4) | 24.9% (20.2% all) | 1995 | **\$68.53M** (\$43.1M–\$98.6M) | 2.0% / 0.0% |
| **ConservativeGoldPlaterBot** | 13.1 | 1.86 | **0.50 ± 0.64** (P10=0, P90=1) | 3.1% (3.1% all) | 160 | **\$-0.91M** (\$-9.7M–\$21.6M) | 68.0% / 58.0% |
| **SpeedDemonSkipTestBot** | 15.6 | 5.00 | **0.76 ± 0.84** (P10=0, P90=2) | 4.8% (4.8% all) | 441 | **\$10.75M** (\$-4.5M–\$35.9M) | 48.0% / 48.0% |

### Key Balance Findings
1. **No Single Trivial Exploit Dominates**:
   - **Reckless rushing (`SpeedDemonSkipTestBot`)** suffers high prototype crash rates during flight test, unfixed hidden flaw penalties at fly-off, missed schedule promises, and severe squadron service groundings/retrofits when it does win a contract.
   - **Over-testing & gold-plating (`ConservativeGoldPlaterBot`)** achieves near-zero prototype crashes and zero service groundings with strong customer reputation, but its +25% price margin and conservative performance envelope reduce its RFP win rate.
   - **Balanced prime strategy (`BalancedPrimeBot`)** and **selective R&D leadership (`TechPioneerBot`)** both achieve viable, competitive paths to Tier A/A+ Prime Contractor status via distinct strategic trade-offs (broad portfolio volume vs. high-Mach technological superiority).

---

## 2. Flight Test Safety, Hidden Flaws, Service Groundings & Reputation (`force_flyoff=True`)

| Bot Archetype | Proto Crashes | Pilots Lost | Flaws Detected | Flaws Fixed | Service Grounding Events | Service Grounding Days | Squadron Accidents | Retrofit Cost (USD) | Ending Rep (USAF / USN) | Track Record |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **BalancedPrimeBot** | 1.22 | 0.34 | 8.1 | 7.2 | 0.10 | 2.8 d | 6.04 | \$0.07M | 47.0 / 54.7 | 0.77 |
| **TechPioneerBot** | 0.88 | 0.24 | 9.5 | 8.7 | 0.08 | 2.4 d | 7.98 | \$0.03M | 34.5 / 59.5 | 0.73 |
| **ConservativeGoldPlaterBot** | 0.24 | 0.08 | 9.2 | 9.2 | 0.00 | 0.0 d | 0.60 | \$0.00M | 45.9 / 48.3 | 0.61 |
| **SpeedDemonSkipTestBot** | 2.58 | 1.18 | 7.5 | 0.0 | 0.20 | 7.3 d | 1.02 | \$0.33M | 37.3 / 50.5 | 0.58 |

---

## 3. R&D Progression, Campaign Score & Grade Distribution (`A+` to `F`)

| Bot Archetype | Active R&D Techs Unlocked | Total Techs Unlocked (+Start) | Mean Campaign Score (± SD) | Grade `A+` | Grade `A` | Grade `B` | Grade `C` | Grade `D` | Grade `F` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **BalancedPrimeBot** | 19.0 | 32.0 | **1631.1 ± 501.7** | 47 (94%) | 2 (4%) | 0 (0%) | 0 (0%) | 0 (0%) | 1 (2%) |
| **TechPioneerBot** | 30.0 | 42.0 | **1763.0 ± 301.9** | 50 (100%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) |
| **ConservativeGoldPlaterBot** | 14.0 | 31.0 | **400.6 ± 370.2** | 6 (12%) | 11 (22%) | 4 (8%) | 0 (0%) | 0 (0%) | 29 (58%) |
| **SpeedDemonSkipTestBot** | 12.0 | 31.0 | **514.6 ± 450.4** | 11 (22%) | 12 (24%) | 3 (6%) | 0 (0%) | 0 (0%) | 24 (48%) |

---

## 4. Acquisition Mode Comparison: Locked Decision D6 (`force_flyoff=True`) vs Historical Styles (`force_flyoff=False`)

| Bot Archetype | D6 Fly-Off Contracts Won | Historical Style Contracts Won | D6 Fly-Off Win Rate | Historical Win Rate | D6 Mean Score | Historical Mean Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **BalancedPrimeBot** | 3.40 | 3.86 | 21.2% | 24.1% | 1631.1 | 1776.6 |
| **TechPioneerBot** | 3.24 | 3.02 | 24.9% | 23.2% | 1763.0 | 1684.4 |
| **ConservativeGoldPlaterBot** | 0.50 | 0.22 | 3.1% | 1.4% | 400.6 | 249.8 |
| **SpeedDemonSkipTestBot** | 0.76 | 3.32 | 4.8% | 20.8% | 514.6 | 1480.0 |

> [!NOTE]
> Under `force_flyoff=False` (where several mid-1950s programs use `paper_2stage` award before flight test),
> `SpeedDemonSkipTestBot` wins slightly more paper awards by over-promising (`promise_z = +1.15`), though it is
> subsequently penalized at IOC milestone promise audit (`audit_milestone_promises`). Under Locked Decision D6
> (`force_flyoff=True`), hardware fly-offs expose unfixed aerodynamic/propulsion flaws before production award.

---

## 5. Player Decision Pacing Audit (1945–1960)

Target pacing window from the architecture specification: **~8–15 meaningful player decisions per year**
(R&D project allocations, RFP aircraft design configurations, wind-tunnel campaign bookings, flight-test phase
authorizations, flaw fix vs. placard trade-offs, proposal bid submissions, and facility/finance actions).

### 5.1 Decision Breakdown by Category (Mean per 1945–1960 Campaign)

| Bot Archetype | R&D Alloc | RFP Design | Wind Tunnel | Flight Test Phases | Flaw Fix / Placard | Bid Submission | Facility / Finance | Total Decisions | **Mean Decisions / Year** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **BalancedPrimeBot** | 28.0 | 16.0 | 47.9 | 25.3 | 7.9 | 16.0 | 3.9 | 144.9 | **9.42 / yr** |
| **TechPioneerBot** | 52.0 | 13.0 | 39.0 | 29.5 | 9.4 | 13.0 | 4.2 | 160.1 | **10.41 / yr** |
| **ConservativeGoldPlaterBot** | 18.0 | 13.1 | 91.6 | 11.2 | 9.2 | 13.1 | 1.2 | 157.3 | **10.23 / yr** |
| **SpeedDemonSkipTestBot** | 18.0 | 15.6 | 0.0 | 25.0 | 7.4 | 15.6 | 1.3 | 82.8 | **5.38 / yr** |

### 5.2 Annual Decision Pacing Timeline (1945–1960 Mean Decisions per Year)

| Year | BalancedPrimeBot | TechPioneerBot | ConservativeGoldPlaterBot | SpeedDemonSkipTestBot | Historical RFP Activity |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **1945** | 14.2 | 14.2 | 21.5 | 3.0 | USN Night Fighter (F3D), USAF Penetration (F-90/F-88) |
| **1946** | 24.3 | 25.9 | 35.7 | 21.5 | USN Carrier Day (F9F/F2H), USAF All-Weather (F-89/F-94) |
| **1947** | 7.1 | 10.2 | 12.4 | 2.0 | USN Swept Carrier Fighter (F7U) |
| **1948** | 6.2 | 7.4 | 3.4 | 6.2 | USAF 1954 Ultimate Interceptor (F-102) |
| **1949** | 9.1 | 10.2 | 10.3 | 3.0 | USAF Transonic Superiority (F-100), USN Escort (F3H) |
| **1950** | 9.2 | 11.5 | 9.1 | 3.0 | USAF Tactical Bomber (B-66), USN Fleet Defense (F4D) |
| **1951** | 24.2 | 33.4 | 24.4 | 26.4 | USAF Long-Range Escort / Strike (F-101) |
| **1952** | 16.5 | 18.7 | 21.8 | 7.5 | USAF Supersonic Tactical Strike (F-105), USAF Mach 2 Day (F-104) |
| **1953** | 16.9 | 15.6 | 6.2 | 4.4 | USN Supersonic Carrier Day (F8U), USN Lightweight (F11F) |
| **1954** | 1.6 | 1.5 | 0.1 | 0.3 | USN All-Weather Fleet Defense Missileer (F4H Phantom II) |
| **1955** | 9.6 | 10.6 | 8.1 | 2.9 | Prototype Fly-Offs & Century-Series Production Ramp |
| **1956** | 5.1 | 0.0 | 4.0 | 1.7 | USAF Lightweight Ally / Export Fighter (N-156 / F-5) |
| **1957** | 1.0 | 1.0 | 0.4 | 0.9 | Mach 2 Flight Testing & Fleet IOC |
| **1958** | 0.0 | 0.0 | 0.0 | 0.0 | Production Line Rate Optimization & Service Retrofits |
| **1959** | 0.0 | 0.0 | 0.0 | 0.0 | Late-Decade Fleet Sustainment & Advanced R&D |
| **1960** | 0.0 | 0.0 | 0.0 | 0.0 | Campaign Endgame & Final Fleet Deliveries |

---

## 6. Per-Program Contract Win Rate Matrix across All 16 Historical RFPs (`force_flyoff=True`)

| Program ID | BalancedPrimeBot | TechPioneerBot | ConservativeGoldPlaterBot | SpeedDemonSkipTestBot |
| :--- | :---: | :---: | :---: | :---: |
| `usaf_aw_int_1945` | 36% | 38% | 10% | 10% |
| `usn_night_1945` | 82% | 0% | 34% | 12% |
| `usn_os105_1946` | 0% | 0% | 0% | 0% |
| `usaf_pen_fighter_1946` | 0% | 0% | 0% | 0% |
| `usn_short_int_1947` | 0% | 0% | 0% | 0% |
| `usn_gp_fighter_1949` | 0% | 0% | 0% | 0% |
| `usaf_ws201a_1950` | 42% | 64% | 0% | 12% |
| `usaf_sabre45_1951` | 60% | 92% | 0% | 22% |
| `usaf_gor101_1951` | 34% | 76% | 6% | 20% |
| `usaf_ws306a_1952` | 0% | 0% | 0% | 0% |
| `usn_os130_1952` | 10% | 38% | 0% | 0% |
| `usaf_ws303a_1952` | 0% | 16% | 0% | 0% |
| `usn_f11f_1953` | 76% | 0% | 0% | 0% |
| `usn_fad_1955` | 0% | 0% | 0% | 0% |
| `usaf_ws202a_1955` | 0% | 0% | 0% | 0% |
| `usaf_gor127_n156_1956` | 0% | 0% | 0% | 0% |
