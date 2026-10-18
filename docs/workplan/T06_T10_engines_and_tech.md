# Workplan Tickets T06–T10 — Propulsion, Technology Tree & Historical Content

> **Status**: v1.0 (Ticket-Level Implementation Plan for `MIC.Core` & `MIC.Core.Tests`)
> **Owner Assemblies**: `src/MIC.Core/` (`MIC.Core.Engine`, `MIC.Core.Tech`, `MIC.Core.Content`)
> **Authoritative Specs**: `docs/spec/02_engines.md` §§4–8, `docs/spec/03_tech_effect_keys.md` §§1–3, `docs/spec/03_tech_tree.md` §§4–8, `docs/spec/10_content.md` §§4–5
> **Golden Vectors**: `sim/golden/engine_cycle_sls.json`, `sim/golden/engine_deck_queries.json`, `sim/golden/engine_rnd_and_diagnostics.json`, `sim/golden/tech_context_start_1945.json`, `sim/golden/tech_aggregation_and_required.json`, `sim/golden/tech_research_and_maturity.json`

---

## Ticket T06 — Brayton 1D Thermodynamic Cycle Solver & Off-Design Operating Deck

- **Depends On**: `T02`, `T03`
- **Spec References**: `docs/spec/02_engines.md` §4.1 (`EngineDesignInput`), §4.2 (`EngineSpec`), §5.1–5.4 (Two-Gamma On-Design & Choked-Turbine Off-Design Brayton Cycle, Inlet Total-Pressure Recovery $\pi_d$), §5.5 (Throttle Mapping & 15×14×6 Deck Table Interpolation); Python oracle `sim/mic/engine/cycle.py` and `sim/mic/engine/deck.py`.
- **Golden Test Vector Files & Tolerances**:
  - `sim/golden/engine_cycle_sls.json`: **relative tolerance `1e-6`** on `sls_dry_thrust_N`, `sls_ab_thrust_N`, `sls_dry_tsfc`, `sls_ab_tsfc` across all 12 historical 1945–1960 engines (`j33_a_35` through `rd_9b`).
  - `sim/golden/engine_deck_queries.json`: **relative tolerance `1e-6`** across all 48 off-design $(M_0, h, \text{throttle}, \text{ab})$ deck queries and 24 inlet pressure recovery vectors (`bellmouth`, `mil_e_5007d`, `pitot`, `fixed_spike`, `variable_ramp`, plus duct losses `nose`, `chin`, `cheek`, `wing_root`).

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Engine/EngineDesignInput.cs
namespace MIC.Core.Engine;

public sealed record EngineDesignInput(
    string EngineId, string Name, string CompressorType, int Spools,
    bool VariableStators, bool HasAfterburner, string NozzleType,
    double MassFlowKgps, double Opr, double TitK, double AbTempK = 0.0,
    double BypassRatio = 0.0, bool CooledTurbine = false,
    double EtaCPoly = 0.84, double EtaTPoly = 0.86,
    double BleedFraction = 0.0, double SpecificWeightFactor = 1.0,
    double MtbfFactor = 1.0, double CumulativeTestHours = 1000.0,
    double ThrustCalFactorDry = 1.0, double ThrustCalFactorAb = 1.0,
    double TsfcCalFactorDry = 1.0, double TsfcCalFactorAb = 1.0,
    double MassCalFactor = 1.0, double DiameterCalFactor = 1.0, double LengthCalFactor = 1.0
);

// File: src/MIC.Core/Engine/InletRecoveryModel.cs
namespace MIC.Core.Engine;

public static class InletRecoveryModel
{
    public static double ComputeTotalPressureRecovery(
        double mach, string inletMode = "mil_e_5007d", string ductLocation = "nose",
        string compressorType = "axial");
}

// File: src/MIC.Core/Engine/BraytonCycleSolver.cs
namespace MIC.Core.Engine;

public readonly record struct CyclePointResult(
    double NetThrustN, double FuelFlowKgps, double TsfcKgPerNs,
    double CorrectedMassFlowKgps, double EffectiveOpr, double Tt3K, double Tt4K, double Tt5K, double Tt7K, double Npr
);

public static class BraytonCycleSolver
{
    public static CyclePointResult SolveFullPowerPoint(
        EngineDesignInput spec, double mach, double altM, bool ab = false,
        string inletMode = "mil_e_5007d", string ductLocation = "nose");

    public static CyclePointResult SolvePartPowerPoint(
        EngineDesignInput spec, double mach, double altM, double throttle, bool ab = false,
        string inletMode = "mil_e_5007d", string ductLocation = "nose");
}

// File: src/MIC.Core/Engine/EngineDeck.cs
namespace MIC.Core.Engine;
using MIC.Core.Contracts;

public sealed class EngineDeck : IEngineSpec
{
    public static readonly double[] MachGrid = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5];
    public static readonly double[] AltMGrid = [0, 1500, 3000, 4572, 6000, 7620, 9144, 10668, 12192, 13716, 15240, 18288, 21336, 25000];
    public static readonly double[] DryThrottleGrid = [0.1, 0.25, 0.5, 0.75, 0.9, 1.0];
    public static readonly double[] AbThrottleGrid = [0.0, 0.25, 0.5, 0.75, 1.0];

    public EngineDesignInput DesignInput { get; }
    public string EngineId { get; }
    public string Name { get; }
    public double MassKg { get; }
    public double DiameterM { get; }
    public double LengthM { get; }
    public double UnitCost { get; }
    public double MtbfH { get; }
    public double MaintMhPerFh { get; }
    public bool HasAfterburner { get; }

    public static EngineDeck Build(
        EngineDesignInput input, string inletMode = "mil_e_5007d", string ductLocation = "nose");

    public double ThrustN(double mach, double altM, double throttle = 1.0, bool ab = false);
    public double Tsfc(double mach, double altM, double throttle = 1.0, bool ab = false);
    public double FuelFlowKgps(double mach, double altM, double throttle = 1.0, bool ab = false);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T06)
1. **Two-Gamma Brayton Cycle (`BraytonCycleSolver`)**: Use the exact thermodynamic constants from `sim/mic/engine/cycle.py` ($\gamma_c = 1.40, \gamma_t = 1.33, \gamma_{ab} = 1.30, L_{\text{HV}} = 43.1\times 10^6\text{ J/kg}$). Implement the choked-turbine off-designcompressor operating line ($\pi_c(M_0, h)$ bounded by `off_design_max_opr_overshoot = 1.06`) and convergent vs. convergent-divergent nozzle expansion.
2. **Part-Throttle Bisection & Precomputed 3D Tables (`EngineDeck`)**:
   - Dry thrust is linear in throttle: $F_{\text{dry}}(M_0, h, \text{thr}) = \text{thr} \cdot F_{\text{dry,max}}(M_0, h)$. For $\text{thr} \ge 0.10$, solve $T_{t4}$ via 36-step bisection and apply the parasitic factor $1 + 0.06 (1 - \text{thr})^2 / \max(0.15, \text{thr})$. Below $\text{thr} = 0.10$, clamp TSFC denominator to $\max(0.05 F_{\text{dry,max}}, F, 1.0\text{ N})$ (`02_engines.md` §7.1).
   - When `ab == true` on an engine with `HasAfterburner == false`, safely fall back to `ab = false`.
3. **Verification (`tests/MIC.Core.Tests/T06_EngineCycleAndDeckTests.cs`)**: Verify all 12 SLS cases in `engine_cycle_sls.json` and all 72 deck/inlet queries in `engine_deck_queries.json` within `rel_tol = 1e-6`.

---

## Ticket T07 — Engine Sizing, Duane MTBF, `EngineDiagnostics` & In-House/Custom R&D

- **Depends On**: `T06`, `T08`, `T10`
- **Spec References**: `docs/spec/02_engines.md` §4.3 (`engine_diagnostics`), §5.6 (Mass, Dimensions, Cost & MIL-HDBK-189 Duane Reliability Growth), §5.7 (Engine R&D Ambition $A$, Cost/Duration/Crisis Equations, Third-Party Sales); Python oracle `sim/mic/engine/sizing.py`, `sim/mic/engine/diagnostics.py`, `sim/mic/engine/rnd.py`, `sim/mic/engine/catalog.py`.
- **Golden Test Vector Files & Tolerances**:
  - `sim/golden/engine_cycle_sls.json`: `mass_kg`, `diameter_m`, `length_m`, `unit_cost`, `mtbf_h`, `maint_mh_per_fh` within **`rel_tol = 1e-6`**.
  - `sim/golden/engine_deck_queries.json`: 5 Duane reliability growth vectors within **`rel_tol = 1e-6`**.
  - `sim/golden/engine_rnd_and_diagnostics.json`: `rnd_estimate`, `diagnostics_j57`, and `third_party_sale_j57_100` within **`rel_tol = 1e-6`**.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Engine/EngineSizingModel.cs
namespace MIC.Core.Engine;

public readonly record struct EnginePhysicalMetrics(
    double MassKg, double DiameterM, double LengthM,
    double UnitCostUsd, double Mtbf0H, double MtbfCurrentH, double MaintMhPerFh
);

public static class EngineSizingModel
{
    public static EnginePhysicalMetrics ComputeSizingAndReliability(EngineDesignInput input);
    public static double ComputeDuaneMtbf(double mtbf0H, double cumulativeTestHours, double duaneAlpha = 0.42);
}

// File: src/MIC.Core/Engine/EngineDiagnosticsCalculator.cs
namespace MIC.Core.Engine;
using System.Collections.Generic;

public sealed record EngineDiagnosticsReport(
    string EngineId, double CompressorSurgeMargin, double HighAltFlameoutRisk,
    double AbLightoffReliability, double IntakeCompatibility, double ThermalMarginK,
    IReadOnlyDictionary<string, double> FlawIncidenceMultipliers
);

public static class EngineDiagnosticsCalculator
{
    public static EngineDiagnosticsReport ComputeDiagnostics(
        EngineDesignInput input, double designMaxMach = 1.2, double designCeilingM = 15000.0,
        string intakeLocation = "nose", string intakeCompression = "pitot", double titTechMaxK = 1135.0);
}

// File: src/MIC.Core/Engine/EngineRndEngine.cs
namespace MIC.Core.Engine;
using System.Collections.Generic;
using MIC.Core.Random;
using MIC.Core.Tech;

public sealed record EngineRndEstimate(
    string ProcurementMode, double Ambition, double TotalDevCostUsd, double PlayerCostShareUsd,
    int ExpectedDurationDays, double ThrustSigmaRel, double TsfcSigmaRel,
    double MassSigmaRel, double ScheduleSigmaRel, double CatastrophicFlawProb
);

public sealed record ThirdPartySaleQuote(double GrossRevenueUsd, double NetProfitUsd, double RoyaltyUsd);

public static class EngineRndEngine
{
    public static IReadOnlyList<string> ValidateEngineAgainstTech(EngineDesignInput input, ITechContext techContext);
    public static double ComputeAmbition(EngineDesignInput input, ITechContext techContext);
    public static EngineRndEstimate EstimateRndProject(
        EngineDesignInput input, ITechContext techContext,
        string procurementMode = "custom_commission", string? parentEngineId = null, double riskFactor = 1.0);
    public static EngineDesignInput ResolveRndOutcome(
        EngineDesignInput targetInput, EngineRndEstimate estimate, Pcg32 rng, out bool hadQualificationCrisis);
    public static ThirdPartySaleQuote EvaluateThirdPartySale(EnginePhysicalMetrics metrics, int quantity);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T07)
1. **Sizing & Duane Growth (`EngineSizingModel`)**: Implement the exact equations in `02_engines.md` §5.6 (`sim/mic/engine/sizing.py`), applying `MassCalFactor`, `DiameterCalFactor`, and `LengthCalFactor` from `sim/data/engines_hist/*.json` when building historical catalog decks.
2. **Engine Diagnostics (`EngineDiagnosticsCalculator`)**: Compute `CompressorSurgeMargin`, `HighAltFlameoutRisk`, `AbLightoffReliability`, `IntakeCompatibility`, `ThermalMarginK`, and `FlawIncidenceMultipliers["engine_stall"]` and `["inlet"]` exactly matching `sim/mic/engine/diagnostics.py`.
3. **Engine R&D (`EngineRndEngine`)**: Implement `ComputeAmbition`, `EstimateRndProject` (with `0.32x` cost and `0.42x` duration discounts when `parentEngineId != null`, and `0.60x` player share for `"custom_commission"`), and `EvaluateThirdPartySale` (`1.18x` price, `12%` royalty).
4. **Verification (`tests/MIC.Core.Tests/T07_EngineSizingAndRndTests.cs`)**: Assert `engine_rnd_and_diagnostics.json` and the sizing columns of `engine_cycle_sls.json` match within `rel_tol = 1e-6`.

---

## Ticket T08 — 87 Canonical Tech Effect Keys, `TechCatalog` DAG & `TechContext` Aggregator

- **Depends On**: `T02`
- **Spec References**: `docs/spec/03_tech_effect_keys.md` §§1–3 (87 Canonical Keys & Aggregation Rules `or`, `max`, `min`, `mul`, `add`), `docs/spec/03_tech_tree.md` §4.1–4.3 (Data Schemas), §5.6 (Minimal-Sufficient `required_techs(design, ctx)`), §7 (Edge Cases); Python oracle `sim/mic/tech/context.py`.
- **Golden Test Vector Files & Tolerances**:
  - `sim/golden/tech_context_start_1945.json`: **100% match (`rel_tol = 1e-6`)** across all 87 effect keys on `1945-01-01`.
  - `sim/golden/tech_aggregation_and_required.json`: **100% match (`rel_tol = 1e-6` / exact string match)** for multi-node aggregation, provider/maturity tie-breaking, and `RequiredTechs` resolution on `f86e_sabre_1950` and `f106a_delta_dart_1958`.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Tech/TechEffectKeyDef.cs
namespace MIC.Core.Tech;
using System.Collections.Generic;

public sealed record TechEffectKeyDef(
    string Key, string Type, string Unit, string Agg, // "or" | "max" | "min" | "mul" | "add"
    object NullValue, object Start1945, string Category,
    string Meaning, IReadOnlyList<string> Consumers, bool Deprecated
);

public sealed record TechNodeDef(
    string Id, string NameKey, string Branch, string Discipline,
    double HistoricalYear, string HistoricalDate, bool GrantedAtStart,
    double InitialMaturity, IReadOnlyList<string> Prereqs,
    int CostEngDays, double CostUsd, bool NacaDiffusion,
    bool GovtContractEligible, IReadOnlyDictionary<string, object> Effects, string HistoricalNote
);

// File: src/MIC.Core/Tech/TechCatalog.cs
namespace MIC.Core.Tech;
using System.Collections.Generic;

public sealed class TechCatalog
{
    public IReadOnlyDictionary<string, TechEffectKeyDef> EffectKeys { get; } // 87 keys
    public IReadOnlyDictionary<string, TechNodeDef> Nodes { get; }           // 82 nodes

    public static TechCatalog LoadDefault();
    public void ValidateDagAndCoverage(); // Throws InvalidOperationException on cycle or missing key
}

// File: src/MIC.Core/Tech/ITechContext.cs
namespace MIC.Core.Tech;
using System.Collections.Generic;

public interface ITechContext
{
    IReadOnlyDictionary<string, double> UnlockedMaturity { get; }
    object GetRaw(string key);
    double GetDouble(string key);
    int GetInt(string key);
    bool GetBool(string key);
    double MaturityOf(string key);
    string? ProviderOf(string key);
    bool Allows(string key, object requestedValue, double epsilon = 1e-6);
}

// File: src/MIC.Core/Tech/TechContext.cs
namespace MIC.Core.Tech;
using System.Collections.Generic;
using MIC.Core.Contracts;

public sealed class TechContext : ITechContext
{
    public const double FloatCapEpsilon = 1e-6;
    public IReadOnlyDictionary<string, double> UnlockedMaturity { get; }

    public static TechContext Build(
        TechCatalog catalog, IReadOnlyDictionary<string, double> unlockedMaturity);

    public static TechContext CreateStarting1945(TechCatalog? catalog = null);
    public object GetRaw(string key);
    public double GetDouble(string key);
    public int GetInt(string key);
    public bool GetBool(string key);
    public double MaturityOf(string key);
    public string? ProviderOf(string key);
    public bool Allows(string key, object requestedValue, double epsilon = FloatCapEpsilon);

    public static IReadOnlyDictionary<string, object> ExtractDesignFeatures(AircraftDesign design);
    public static (IReadOnlyList<string> TechIds, IReadOnlyDictionary<string, string> ByFeature) RequiredTechs(
        IReadOnlyDictionary<string, object> designFeatures, TechContext ctx, TechCatalog catalog);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T08)
1. **87-Key Aggregation (`TechContext.Build`)**:
   - Initialize every key in `catalog.EffectKeys` to its `NullValue`.
   - Iterate over unlocked nodes in deterministic sorted order (`unlockedMaturity.Keys.OrderBy(k => k, StringComparer.Ordinal)`).
   - Apply `or` (boolean OR; provider is highest-maturity true provider), `max` (provider is node achieving maximum value; ties broken by higher maturity then lexicographically smaller `nodeId`), `min` (provider is node achieving minimum value; ties broken by higher maturity then smaller `nodeId`), `mul` (product of node multipliers; maturity is weighted average by $|\ln E_{i,k}|$), and `add` (sum of deltas).
2. **Minimal-Sufficient `RequiredTechs` (`03_tech_tree.md` §5.6)**:
   - For `agg == "max"` when `v > nullValue + 1e-6`: filter unlocked nodes with $E_{i,k} \ge v - 10^{-6}$ and pick the node minimizing `(E_{i,k}, -maturity_i, nodeId_i)`.
   - For `agg == "min"` when `v < nullValue - 1e-6`: filter unlocked nodes with $E_{i,k} \le v + 10^{-6}$ and pick the node minimizing `(-E_{i,k}, -maturity_i, nodeId_i)`.
3. **Verification (`tests/MIC.Core.Tests/T08_TechContextAndRequiredTests.cs`)**: Assert `tech_context_start_1945.json` and `tech_aggregation_and_required.json` match 100%.

---

## Ticket T09 — Daily/Monthly Tech R&D, Ahead-of-Time Penalty, Brooks's Law & NACA Diffusion

- **Depends On**: `T01`, `T08`
- **Spec References**: `docs/spec/03_tech_tree.md` §§5.1–5.5 (Calendar Year Conversion, Brooks's Law $N_{\text{eff}}$, Ahead-of-Time / Behind-Time Multiplier, NACA Diffusion & Passive Drip, Two-Regime Maturity Growth), §6 (Tunables `sim/data/tuning/tech.json`); Python oracle `sim/mic/tech/research.py`.
- **Golden Test Vector File & Tolerance**: `sim/golden/tech_research_and_maturity.json` — **relative tolerance `1e-6`** across all 6 `aot_vectors`, 7 `brooks_vectors`, and the complete `swept_wing_project_trajectory` (`days_to_unlock = 86`, `total_company_usd = 28000.0`, `total_govt_usd = 112000.0`, maturity jumps).

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Tech/CompanyTechState.cs
namespace MIC.Core.Tech;
using System.Collections.Generic;

public sealed class ActiveTechProject
{
    public string TechId { get; init; } = "";
    public int AssignedEngineers { get; set; }
    public string FundingMode { get; set; } = "irad"; // "irad" | "govt_contract"
    public double ProgressEngDays { get; set; }
    public double SpentCompanyUsd { get; set; }
    public double SpentGovtUsd { get; set; }
}

public sealed class CompanyTechState
{
    public string CompanyId { get; }
    public Dictionary<string, double> UnlockedMaturity { get; }
    public Dictionary<string, ActiveTechProject> ActiveProjects { get; }
    public Dictionary<string, double> PartialProgressEngDays { get; }
    public Dictionary<string, double> DesignerBranchBonuses { get; }

    public static CompanyTechState CreateStarting1945(
        string companyId, TechCatalog? catalog = null,
        IReadOnlyDictionary<string, double>? maturityOverrides = null,
        IReadOnlyDictionary<string, double>? designerBranchBonuses = null);

    public TechContext BuildContext(TechCatalog? catalog = null);
}

// File: src/MIC.Core/Tech/TechResearchEngine.cs
namespace MIC.Core.Tech;
using System.Collections.Generic;

public sealed record DailyTechStepResult(
    IReadOnlyList<string> NewlyUnlockedTechIds,
    double TotalCompanyCostUsd,
    double TotalGovtCostUsd
);

public static class TechResearchEngine
{
    public static double DateDayToYear(int dateDay) => 1945.0 + (dateDay / 365.25);
    public static double EffectiveEngineers(int assignedEngineers);
    public static double AheadOfTimeMultiplier(int dateDay, double historicalYear);
    public static bool IsNacaDiffused(TechNodeDef node, int dateDay);

    public static DailyTechStepResult StepCompanyTechDay(
        CompanyTechState state, TechCatalog catalog, int dateDay,
        double budgetThrottle = 1.0, double globalNacaBonus = 0.0);

    public static void ApplyLearningByDoing(
        CompanyTechState state, IEnumerable<string> techsUsed,
        string milestoneEvent, double scale = 1.0); // "sim_run"|"tunnel_campaign"|"first_flight"|"flight_test_sortie"|"flaw_fixed"|"production_10_units"
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T09)
1. **Brooks's Law Effective Engineers (`EffectiveEngineers`)**: For $N \le 0 \to 0.0$; for $0 < N \le 15 \to N$; for $N > 15 \to \min(40.0, 15.0 + \text{Math.Pow}(N - 15.0, 0.65))$.
2. **Ahead-of-Time / Behind-Time Multiplier (`AheadOfTimeMultiplier`)**:
   - Let $t_{\text{yr}} = 1945.0 + \text{dateDay} / 365.25$ and $\Delta y = y_{\text{hist}} - t_{\text{yr}}$.
   - If $\Delta y > 0.5$ (`aot_free_lead_years`): return $\max\!\left(0.12,\; \frac{1.0}{1.0 + 0.55 \cdot (\Delta y - 0.5)^{1.6}}\right)$.
   - If $\Delta y < 0.0$: return $\min(1.75, 1.0 + 0.20 \cdot (-\Delta y))$. Else return `1.0`.
3. **Daily Progress, Funding Mode & NACA Diffusion (`StepCompanyTechDay`)**:
   - Under `"govt_contract"`, speed multiplier is `1.15` and company cost share is `0.20` (`govt_contract_company_cost_share`); under `"irad"`, speed multiplier is `1.0` and company share is `1.0`.
   - When `node.NacaDiffusion && t_yr >= node.HistoricalYear + 2.0`: active research receives `1.35x` speed (`naca_report_speed_multiplier`), and any unresearched node whose prerequisites are unlocked receives passive progress `0.0012 * node.CostEngDays` per day (`naca_passive_drip_frac_per_day`) at zero company USD cost.
   - Clamp final-day progress to `remaining = node.CostEngDays - progress` so direct USD billing never exceeds `node.CostUsd` (`03_tech_tree.md` §7.3).
   - Apply daily passive bench maturity growth $+0.00025/\text{day}$ up to `passive_maturity_cap = 0.65`.
4. **Verification (`tests/MIC.Core.Tests/T09_TechResearchAndMaturityTests.cs`)**: Assert `tech_research_and_maturity.json` matches within `rel_tol = 1e-6`.

---

## Ticket T10 — Historical Content Loader & Pre-1962 USAF/USN Designation Generator

- **Depends On**: `T02`
- **Spec References**: `docs/spec/00_conventions.md` §1 (Locked Decision D4 — zero hard-coded display names, all strings in `sim/data/names/*.json`; Decision D9 — fictional test pilot names in `sim/data/testing/pilot_names.json` & 5 named US engine vendors in `sim/data/companies/engine_makers_us_1945_1960.json`); `docs/spec/10_content.md` §§4.1–4.4 (13 Airframers, 5 Engine Makers, 4 Startup Presets, 29 Chief Designers), §§5.1–5.3 (Pre-1962 USAF `P-` $\to$ `F-` on `1948-06-11`, USN BuAer `XF<n><Code>-<Var>`, Legal-Safe Fictional Fallback Overrides).
- **Golden Test Vector Files & Tolerances**:
  - `sim/data/companies/airframers_us_1945_1960.json`, `engine_makers_us_1945_1960.json`, `startup_presets.json`, `chief_designers_us_1945_1960.json`
  - `sim/data/names/companies_and_people.json`, `tech_and_components.json`, `designation_rules_us_pre1962.json`, `sim/data/testing/pilot_names.json`
  - **100% exact string & referential integrity match**.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Content/ContentSchemas.cs
namespace MIC.Core.Content;
using System.Collections.Generic;

public sealed record DesignerModifiers(
    double Cd0RefinementFactor,
    double PrototypeBuildTimeFactor,
    double StructuralMassFactor
);

public sealed record ChiefDesignerDef(
    string Id, string NameKey, string CompanyId, int ActiveFromYear, int ActiveUntilYear,
    IReadOnlyDictionary<string, double> ResearchBranchBonuses,
    DesignerModifiers DesignModifiers, string HistoricalNote
);

public sealed record AirframerProfileDef(
    string Id, string NameKey, string ShortNameKey, string HqLocation,
    string CompanyCodeUsn, bool PlayableDefault, string Tier,
    double CashUsd, double DebtUsd, IReadOnlyDictionary<string, double> Reputation,
    double PoliticalCapital, IReadOnlyDictionary<string, int> Engineers,
    IReadOnlyDictionary<string, object> Facilities,
    string ChiefDesignerId, string? SecondaryDesignerId, int? SuccessionYear,
    IReadOnlyDictionary<string, double> StartingTechOverrides,
    IReadOnlyDictionary<string, object> AiDoctrine
);

public sealed record EngineMakerProfileDef(
    string Id, string NameKey, string ShortNameKey, string UsCode,
    double CashUsd, int PropulsionEngineers, int TestCellLevel,
    string ChiefDesignerId, string Specialty,
    IReadOnlyDictionary<string, double> VendorModifiers
);

// File: src/MIC.Core/Content/LocalizationCatalog.cs
namespace MIC.Core.Content;
using System.Collections.Generic;

public sealed class LocalizationCatalog
{
    public bool UseFictionalNames { get; set; }
    public IReadOnlyDictionary<string, string> Strings { get; }
    public IReadOnlyDictionary<string, string> FictionalFallbackOverrides { get; }

    public static LocalizationCatalog LoadDefault(bool useFictionalNames = false);
    public string Resolve(string nameKey); // Throws KeyNotFoundException if missing
}

// File: src/MIC.Core/Content/ContentCatalog.cs
namespace MIC.Core.Content;
using System.Collections.Generic;

public sealed class ContentCatalog
{
    public IReadOnlyDictionary<string, AirframerProfileDef> Airframers { get; }       // 13 US airframers
    public IReadOnlyDictionary<string, EngineMakerProfileDef> EngineMakers { get; }   // 5 US engine makers
    public IReadOnlyDictionary<string, ChiefDesignerDef> ChiefDesigners { get; }      // 29 chief designers
    public LocalizationCatalog Localization { get; }

    public static ContentCatalog LoadDefault(bool useFictionalNames = false);
    public void ValidateReferentialIntegrity(MIC.Core.Tech.TechCatalog techCatalog);
}

// File: src/MIC.Core/Content/DesignationGenerator.cs
namespace MIC.Core.Content;
using System.Collections.Generic;

public sealed class DesignationGenerator
{
    public const int UsafPToFTransitionDay = 1257; // 1948-06-11

    public int NextUsafFighterSeq { get; set; } = 85;
    public Dictionary<string, int> UsnModelCounterByCompanyCode { get; } = new();

    public static string GenerateUsafDesignation(
        int orderDateDay, string stage, int seqNum, int seriesIndex = 0); // stage: "prototype"|"service_test"|"production"

    public static string UpgradeUsafPursuitToFighterOn19480611(string currentDesignation);

    public static string GenerateUsnDesignation(
        string companyCodeUsn, int modelNum, int variantNum,
        string stage = "production", string subMod = ""); // Skips modelNum == 13 -> 14

    public int AllocateNextUsnModelNumber(string companyCodeUsn);
    public static string GenerateJointEngineDesignation(
        string customer, int number, string vendorUsCode, int dashNum, bool isExperimental = false);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T10)
1. **Pre-1962 USAF `P-` to `F-` Rule (`DesignationGenerator.GenerateUsafDesignation`)**:
   - Before `1948-06-11` (`orderDateDay < 1257`), type letter is `"P"`; on or after `1257`, type letter is `"F"`.
   - Status prefix: `"prototype"` $\to$ `"X"` (omits series letter: `XP-86`, `XF-104`); `"service_test"` $\to$ `"Y"` + series letter (`YF-100A`); `"production"` $\to$ `""` + series letter (`P-80A`, `F-86A`).
   - On `dayIndex == 1257`, `UpgradeUsafPursuitToFighterOn19480611` converts `"XP-86"` $\to$ `"XF-86"` and `"P-80A"` $\to$ `"F-80A"`.
2. **Pre-1962 USN BuAer Rule (`GenerateUsnDesignation`)**:
   - Omit `<modelNum>` when `modelNum == 1` (`"XFH-1"`, `"FH-1"`, `"FJ-1"`). For `modelNum >= 2`, include integer (`"XF2H-1"`, `"F9F-2"`, `"F4D-1"`, `"F8U-1"`).
   - In `AllocateNextUsnModelNumber`, if the next incremented counter equals `13`, automatically increment to `14` (`10_content.md` §7.2).
3. **Referential Integrity & D4 Verification (`tests/MIC.Core.Tests/T10_ContentAndDesignationTests.cs`)**:
   - Verify all 13 airframers, 5 engine vendors, 29 chief designers, 82 tech nodes, and 28 components resolve every `name_key`, `short_name_key`, `chief_designer_id`, and `starting_tech_overrides` entry without error, both with `useFictionalNames: false` and `useFictionalNames: true`.
