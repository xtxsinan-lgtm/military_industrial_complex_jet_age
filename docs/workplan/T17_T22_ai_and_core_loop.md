# Workplan Tickets T17–T22 — Competitor AI, Pre-Bid Intelligence & Campaign Core Loop

> **Status**: v1.0 (Ticket-Level Implementation Plan for `MIC.Core` & `MIC.Core.Tests`)
> **Owner Assemblies**: `src/MIC.Core/` (`MIC.Core.AI`, `MIC.Core.Actions`, `MIC.Core.Campaign`)
> **Authoritative Specs**: `docs/spec/07_competitor_ai.md` §§4–8, `docs/spec/09_core_loop.md` §§3–9
> **Golden Vectors**: `sim/golden/ai_competitor_behaviors.json`, `sim/golden/ai_rumors_and_vendors.json`, `sim/golden/core_campaign_smoke.json`

---

## Ticket T17 — AI Airframer Monthly Evolution, Doctrine R&D & Historical Exits

- **Depends On**: `T09`, `T10`, `T12`
- **Spec References**: `docs/spec/07_competitor_ai.md` §4.1 (`AICompanyState`), §5.1 (Doctrine-Weighted Tech Tree R&D `score_tech_node_for_ai`, Chief Designer Succession, Monthly Economy Sync & Historical Fighter-Market Exits for Curtiss-Wright 1949, Bell 1952, Boeing 1953, Martin 1954 with `alt_history_contract_keeps_alive = true`); Python oracle `sim/mic/ai/company_ai.py`.
- **Golden Test Vector File & Tolerance**: `sim/golden/ai_competitor_behaviors.json` (`initial_ai_company_count = 12` when player is `north_american`, and `month_1_step_reports` for `lockheed`, `convair`, `grumman`, `curtiss_wright`) — **relative tolerance `1e-6` / exact allocation match**.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/AI/AICompanyState.cs
namespace MIC.Core.AI;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Tech;

public sealed class AICompanyState
{
    public string Id { get; init; } = "";
    public string NameKey { get; init; } = "";
    public string Tier { get; init; } = "major_prime";
    public CompanyState CompanyState { get; init; } = default!;
    public CompanyTechState TechState { get; init; } = default!;
    public IReadOnlyDictionary<string, object> AiDoctrine { get; init; } = default!;
    public IReadOnlyDictionary<string, object> Traits { get; init; } = default!;
    public string ActiveDesignerId { get; set; } = "";
    public string? SecondaryDesignerId { get; init; }
    public int? DesignerSuccessionYear { get; init; }
    public bool ActiveInFighterMarket { get; set; } = true;
    public string? ExitReason { get; set; }
    public int? ExitYear { get; set; }
}

public sealed record AIMonthlyStepReport(
    string CompanyId, string ActiveDesignerId,
    IReadOnlyList<(string TechId, int AssignedEngineers)> ResearchAllocations,
    double EndingCashUsd, bool ActiveInFighterMarket
);

// File: src/MIC.Core/AI/AICompanyController.cs
namespace MIC.Core.AI;
using System.Collections.Generic;
using MIC.Core.Content;
using MIC.Core.Tech;

public static class AICompanyController
{
    public static IReadOnlyList<AICompanyState> LoadAiAirframers(
        string? playerCompanyId = "north_american",
        ContentCatalog? content = null, TechCatalog? techCatalog = null);

    public static double ScoreTechNodeForAi(
        TechNodeDef node, AICompanyState aiCompany, int currentDay);

    public static IReadOnlyList<(string TechId, int AssignedEngineers)> SelectAiResearchProjects(
        AICompanyState aiCompany, TechCatalog catalog, int currentDay);

    public static AIMonthlyStepReport StepAiCompanyMonth(
        AICompanyState aiCompany, TechCatalog catalog, ContentCatalog content, int currentDay);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T17)
1. **Chief Designer Succession**: At the start of `StepAiCompanyMonth`, if `aiCompany.DesignerSuccessionYear.HasValue && year >= aiCompany.DesignerSuccessionYear.Value` and `SecondaryDesignerId != null`, switch `ActiveDesignerId = SecondaryDesignerId` and update `TechState.DesignerBranchBonuses` from `content.ChiefDesigners[ActiveDesignerId]`.
2. **Doctrine Tech Node Scoring (`ScoreTechNodeForAi`)**:
   - Filter out unlocked nodes, nodes with unmet prerequisites, and nodes where $\Delta y = y_{\text{hist}}(n) - \text{currentYear} > L_{\max}$ ($2.5 + \mathbb{I}(\text{ambition} \ge 0.90)$).
   - Compute $F_{\text{AoT}} = \text{AheadOfTimeMultiplier}(d, y_{\text{hist}})^{0.45}$, alignment $A(n, c)$ (`1.0 + 1.50 * B_designer + deltaBranch + deltaEffects + deltaCarrier`), $F_{\text{cost}} = (500.0 / \max(150.0, \text{costEngDays}))^{0.25}$, and $F_{\text{catchup}} = 1.0 + \text{clamp}((-\Delta y) \cdot 0.15, 0.0, 0.60)$ (`07_competitor_ai.md` §5.1). Multiply by `1.25` if partially researched.
   - Allocate engineers across the top $K \le 3$ nodes clamped to $[15, 65]$ FTEs per project, advance daily tech research for the month, and run `CompanyMonthlySettlement.StepCompanyMonth`.
3. **Historical Exit & Alt-History Survival**: If `year >= historicalExitYear` (`curtiss_wright: 1949`, `bell: 1952`, `boeing: 1953`, `martin: 1954`) and `ActiveProductionContractsCount == 0`, set `ActiveInFighterMarket = false`, `ExitReason = "historical_pivot_to_bombers_or_missiles"`, `ExitYear = year`. If the AI holds an active fighter production contract (`alt_history_contract_keeps_alive = true`), keep it active!
4. **Verification (`tests/MIC.Core.Tests/T17_AiCompanyEvolutionTests.cs`)**: Assert `initial_ai_company_count` and `month_1_step_reports` in `ai_competitor_behaviors.json` match within `rel_tol = 1e-6`.

---

## Ticket T18 — AI Parametric Aircraft Synthesizer, Bidding AI, Pre-Bid Rumors (D10) & Engine Vendors (D9)

- **Depends On**: `T05`, `T07`, `T14`, `T16`, `T17`
- **Spec References**: `docs/spec/00_conventions.md` §1 (Locked Decision **D6**: Two-stage fly-off AI progression; Locked Decision **D9**: Named historical engine vendor quotes; Locked Decision **D10**: Pre-bid competitor intelligence rumors with inquiry levels `0, 1, 2`); `docs/spec/07_competitor_ai.md` §§4.2–4.3, §§5.2–5.5; Python oracle `sim/mic/ai/design_generator.py`, `sim/mic/ai/bidding_ai.py`, `sim/mic/ai/rumors.py`, `sim/mic/ai/engine_vendor_ai.py`.
- **Golden Test Vector Files & Tolerances**:
  - `sim/golden/ai_competitor_behaviors.json`: `rfp_1946_entries`, `stage_1_downselect`, `rfp_1946_flyoff_finalists`, and `stage_2_flyoff_winner` within **`rel_tol = 1e-6`**.
  - `sim/golden/ai_rumors_and_vendors.json`: `rumors_by_inquiry_level` (`0`, `1`, `2`) and all 6 `engine_vendor_quotes_1952` (`pratt_whitney`, `general_electric`, `allison`, `wright`, `westinghouse`, plus `wright_derivative`) within **`rel_tol = 1e-6`**.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/AI/AIDesignSynthesizer.cs
namespace MIC.Core.AI;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Tech;

public static class AIDesignSynthesizer
{
    public static (AircraftDesign Design, PerformanceReport NominalReport) GenerateAiDesignForRfp(
        AICompanyState aiCompany, Requirement rfp, TechCatalog techCatalog,
        IReadOnlyList<IEngineSpec>? availableEngines = null);
}

// File: src/MIC.Core/AI/AIBiddingEngine.cs
namespace MIC.Core.AI;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Procurement;
using MIC.Core.Random;
using MIC.Core.Testing;

public sealed class AICompetitorEntry
{
    public string EntryId { get; init; } = "";
    public string RfpId { get; init; } = "";
    public string CompanyId { get; init; } = "";
    public AircraftDesign Design { get; init; } = default!;
    public LineageTestState TestState { get; init; } = default!;
    public ProposalBid Bid { get; set; } = default!;
    public BidderContext BidderContext { get; init; } = default!;
}

public static class AIBiddingEngine
{
    public static IReadOnlyList<AICompanyState> SelectAiBiddersForRfp(
        Requirement rfp, IReadOnlyList<AICompanyState> companies);

    public static IReadOnlyList<AICompetitorEntry> PrepareAllAiEntriesForRfp(
        Requirement rfp, IReadOnlyList<AICompanyState> companies, ulong campaignSeed, Pcg32 rng);

    public static void StepAllAiFlyOffFinalists(
        Requirement rfp, IReadOnlyList<AICompetitorEntry> finalistEntries,
        IReadOnlyDictionary<string, AICompanyState> companiesById, Pcg32 rng);
}

// File: src/MIC.Core/AI/PreBidRumorGenerator.cs
namespace MIC.Core.AI;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Random;

public sealed record CompetitorRumor(
    string RfpId, string ProgramId, string CompanyId, string CompanyName,
    string RumoredDesignName, int InquiryLevel, double InquiryCostUsd, double InquiryPcCost,
    double ParticipationConfidence, bool IsFalseLead, string ConfigurationHint, string EngineHint,
    Estimate MaxMachAlt, Estimate CombatRadiusM, Estimate UnitFlyawayPriceUsd,
    IReadOnlyDictionary<string, Estimate> Estimates, string Headline
);

public static class PreBidRumorGenerator
{
    public static IReadOnlyList<CompetitorRumor> GeneratePreBidRumors(
        Requirement rfp, IReadOnlyList<AICompetitorEntry> aiEntries, int inquiryLevel, Pcg32 rng);
}

// File: src/MIC.Core/AI/EngineVendorQuoter.cs
namespace MIC.Core.AI;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Random;

public sealed record CustomEngineTargetSpec(
    double TargetDryThrustSlN, double TargetAbThrustSlN, bool HasAfterburner,
    double DesignMach, bool IsDerivative = false, string Customer = "USAF"
);

public sealed record CustomEngineQuote(
    string QuoteId, string VendorId, string VendorName, string UsCode, string Specialty,
    string Designation, int DateQuotedDay, bool IsDerivative,
    double PromisedDryThrustSlN, double PromisedAbThrustSlN, bool HasAfterburner,
    double PromisedTsfcDrySl, double PromisedTsfcAbSl, double PromisedMassKg,
    double PromisedDiameterM, double PromisedLengthM, double PromisedMtbfH,
    double UnitPriceUsd, double TotalDevCostUsd, double AirframerCommissionFeeUsd,
    int PromisedDeliveryDays, double DevelopmentRiskIndex, double ScheduleSlipProb,
    double ShortfallRiskProb, IEngineSpec EngineDeck
);

public static class EngineVendorQuoter
{
    public static CustomEngineQuote QuoteCustomEngine(
        string vendorId, CustomEngineTargetSpec targetSpec, int currentDay, Pcg32? rng = null);

    public static IReadOnlyList<CustomEngineQuote> CompareVendorQuotes(
        CustomEngineTargetSpec targetSpec, int currentDay, Pcg32? rng = null);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T18)
1. **Parametric Aircraft Synthesis & Coordinate Local Search (`GenerateAiDesignForRfp`)**:
   - Build seed design respecting company signature (`delta_bias >= 0.65` $\to$ tailless delta when unlocked and $M^* \ge 1.15$; `twin_engine_bias >= 0.72` $\to$ 2 engines), clamp strictly inside `TechContext` caps (`max_sweep - 0.5`, `min_tc + 0.002`, `min_ar + 0.05`), and enforce `_ClampFuelToVolume` (`<= 0.98 * MaxInternalFuelCapacityKg`).
   - Run coordinate search over `area_scale` $\in \{0.86, 0.93, 1.00, 1.08, 1.18\}$, `sweep_offset` $\in \{-5^\circ, 0^\circ, +5^\circ\} \times$ `tc_offset` $\in \{-0.012, 0, +0.010\}$, and `fuel_scale` $\in \{0.88, 1.00, 1.15\}$ maximizing $J(\text{design})$ (`07_competitor_ai.md` §5.2).
2. **Two-Stage Fly-Off Progression (D6), Pre-Bid Rumors (D10) & Engine Vendors (D9)**:
   - Implement `PrepareAllAiEntriesForRfp` (with pre-1950 transonic tunnel choking guard) and `StepAllAiFlyOffFinalists` (`fix_Policy`: `"placard_all"` if $< 35\text{ days}$, `"fix_all"` if `risk_tolerance <= 0.35`, else `"fix_severe_else_placard"`).
   - In `GeneratePreBidRumors`, scale relative `sigma` by inquiry level `0 -> 1 -> 2` (`L0: 11%/18%/20%`, `L1: 6.5%/11%/12%`, `L2: 4%/7%/8%`) and clamp normal draw $z_m \in [-2.2, 2.2]$.
   - In `QuoteCustomEngine`, apply the 5 vendor specialty modifiers from `sim/data/companies/engine_makers_us_1945_1960.json`.
3. **Verification (`tests/MIC.Core.Tests/T18_AiBiddingRumorsAndVendorsTests.cs`)**: Assert `ai_competitor_behaviors.json` and `ai_rumors_and_vendors.json` match within `rel_tol = 1e-6`.

---

## Ticket T19 — `WorldState` (`CampaignState`), `ISimModule` Registry & 3-Phase Canonical Tick Runner

- **Depends On**: `T05`, `T07`, `T09`, `T12`, `T14`, `T16`, `T18`
- **Spec References**: `docs/spec/09_core_loop.md` §3 (Player-Facing Flow), §4.4 (Historical US Defense & Aircraft Procurement Budget Table FY1945–FY1961), §5.3 (`CANONICAL_MONTHLY_ORDER`, `CANONICAL_FY_ROLLOVER_ORDER`, `CANONICAL_DAILY_ORDER`); Python oracle `sim/mic/campaign/contracts.py`, `sim/mic/campaign/world.py`, `sim/mic/campaign/runner.py`.
- **Golden Test Vector File & Tolerance**: `sim/golden/core_campaign_smoke.json` (`macro_budget_sample` and `smoke_2y_seed_42`) — **exact SHA-256 state hash & `rel_tol = 1e-6`**.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Campaign/ISimModule.cs
namespace MIC.Core.Campaign;
using System.Collections.Generic;
using MIC.Core.Actions;
using MIC.Core.Calendar;

public interface ISimModule
{
    string ModuleId { get; } // "01_aero_design".."07_ai"
    int SchemaVersion { get; }
    void Initialize(WorldState world);
    void OnDayTick(WorldState world, TickSchedule schedule);
    void OnMonthStart(WorldState world, TickSchedule schedule);
    void OnFiscalYearStart(WorldState world, int fiscalYear, FiscalYearBudget budget);
    ValidationResult ValidateAction(WorldState world, PlayerAction action);
    ActionResult ApplyAction(WorldState world, PlayerAction action);
    IReadOnlyDictionary<string, object?> SerializeState();
    void DeserializeState(IReadOnlyDictionary<string, object?> state, int schemaVersion);
}

// File: src/MIC.Core/Campaign/WorldState.cs
namespace MIC.Core.Campaign;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Random;

public sealed record FiscalYearBudget(
    int FiscalYear, double DodTotalUsd, double UsafTotalUsd, double UsnAviationUsd,
    double AircraftProcurementTotalUsd, double AircraftProcurementUsafUsd,
    double AircraftProcurementUsnUsd, double AviationRdUsd, double Deflator1950
);

public interface IReadOnlyWorldState
{
    ulong Seed { get; }
    int StartDay { get; }
    int EndDay { get; }
    int Day { get; }
    string DifficultyId { get; }
    string PlayerCompanyId { get; }
    bool HistoricalAcquisitionStyles { get; } // D6 toggle
    bool FlawHindsight { get; }               // D7 toggle
    bool UseFictionalNames { get; }           // D4 toggle
    bool IsEndlessSandbox { get; }            // D8 state
    bool Ended { get; }
    string Outcome { get; }
    string OutcomeReason { get; }
    IReadOnlyDictionary<string, CompanyState> Companies { get; }
    CompanyState PlayerCompany { get; }
    FiscalYearBudget CurrentBudget { get; }
    IReadOnlyList<SimNotification> Notifications { get; }
}

public sealed class WorldState : IReadOnlyWorldState
{
    public RngStreamRegistry Rng { get; set; } = default!;
    public Dictionary<string, ISimModule> Modules { get; } = new();
    // Implements all IReadOnlyWorldState properties + mutable campaign state dictionaries
}

// File: src/MIC.Core/Campaign/CampaignRunner.cs
namespace MIC.Core.Campaign;
using MIC.Core.Actions;

public sealed class CampaignRunner
{
    public WorldState World { get; }

    public CampaignRunner(WorldState world);
    public void StepDay();
    public int RunDays(int count);
    public ActionResult SubmitAction(PlayerAction action);
    public string ComputeDeterministicStateHashSha256();
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T19)
1. **Strict 3-Phase Daily Execution (`CampaignRunner.StepDay`)**:
   - Compute `TickSchedule schedule = GameCalendar.GetTickSchedule(World.Day)`.
   - **Phase A (Monthly Settlement)**: Iff `schedule.IsMonthStart && World.Day > World.StartDay`, invoke `OnMonthStart` in exact order: `03_tech` $\to$ `02_engines` $\to$ `06_testing` $\to$ `05_procurement` $\to$ `04_economy` $\to$ `07_ai` $\to$ `EventEngine.OnMonthStart` $\to$ `CheckFailureConditions` $\to$ `RecordAutosave`.
   - **Phase B (US Fiscal Year Rollover)**: Iff `schedule.IsFiscalYearStart` (`July 1`), update `World.Macro.CurrentFy = schedule.FiscalYear`, load `FiscalYearBudget` from `sim/data/tuning/core.json`, and invoke `OnFiscalYearStart` on `05_procurement` $\to$ `04_economy` $\to$ `07_ai`.
   - **Phase C (Daily Tick)**: Every day, invoke `EventEngine.OnDayTick` $\to$ `03_tech` $\to$ `02_engines` $\to$ `01_aero_design` $\to$ `06_testing` $\to$ `04_economy` $\to$ `05_procurement` $\to$ `07_ai` $\to$ queued `PlayerAction`s $\to$ `CheckPostDayConditions`, then increment `World.Day++`.

---

## Ticket T20 — 26 `SimCommand` / `PlayerAction` Handlers & Scripted/MTTH `EventEngine`

- **Depends On**: `T19`
- **Spec References**: `docs/spec/09_core_loop.md` §4.3 (Event Definition & Recursive Condition DSL `all`, `any`, `not`, Effect Opcodes `set_flag`, `set_macro`, `add_macro`, `add_cash`, `add_reputation`, `add_political_capital`, `tech_boost`, `schedule_event`), §4.5 (16 Scripted Historical Events + 2 MTTH Events), §4.7 (Complete 26-Action Catalog `ACTION_CATALOG`); `docs/spec/08_ui_ux.md` §5 (UI `SimCommand` aliases); Python oracle `sim/mic/campaign/contracts.py` and `sim/mic/campaign/events.py`.
- **Golden Test Vector File & Tolerance**: `sim/golden/core_campaign_smoke.json` (`events_fired_count = 18` over 1945–1960) — **100% exact match**.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Actions/ActionCatalog.cs
namespace MIC.Core.Actions;
using System.Collections.Generic;
using MIC.Core.Campaign;

public sealed record PlayerAction(
    string ActionType, string ActorCompanyId, IReadOnlyDictionary<string, object?> Params
);

public sealed record ValidationResult(bool IsValid, string ErrorCode = "", string ErrorMessage = "");
public sealed record ActionResult(bool IsSuccess, string ErrorCode = "", string ErrorMessage = "", IReadOnlyDictionary<string, object?>? Data = null);

public static class ActionCatalog
{
    public static string NormalizeActionType(string actionType); // Maps UI aliases (e.g. "finance.borrow" -> "econ.take_loan")
    public static ValidationResult ValidateActionSchema(PlayerAction action);
}

// File: src/MIC.Core/Campaign/EventEngine.cs
namespace MIC.Core.Campaign;
using MIC.Core.Calendar;

public sealed class EventEngine
{
    public void OnDayTick(WorldState world, TickSchedule schedule);
    public void OnMonthStart(WorldState world, TickSchedule schedule);
    public ActionResult ChooseEventOption(WorldState world, string eventId, string optionId);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T20)
1. **26 Canonical Action Schemas + UI Alias Normalization (`ActionCatalog`)**:
   - Validate all 26 canonical actions from `09_core_loop.md` §4.7 (`design.create`, `design.modify`, `design.clone`, `design.freeze`, `engine.start_project`, `engine.set_engineers`, `engine.cancel_project`, `tech.set_allocation`, `tech.cancel_research`, `econ.hire_engineers`, `econ.fire_engineers`, `econ.upgrade_wind_tunnel`, `econ.expand_factory`, `econ.build_test_site`, `econ.take_loan`, `econ.repay_loan`, `econ.set_production_rate`, `proc.submit_proposal`, `proc.withdraw_proposal`, `proc.lobby_program`, `test.run_wind_tunnel`, `test.build_prototype`, `test.schedule_flight_test`, `test.fix_flaw`, `core.choose_event_option`, `core.dismiss_notification`).
   - Also normalize UI convenience aliases from `08_ui_ux.md` §5 (`design.freeze_and_build_prototypes`, `design.create_variant`, `engine.allocate_engineers`, `tech.set_allocations`, `tech.set_rd_budget`, `finance.borrow`, `finance.repay`, `workforce.hire_fire`, `workforce.assign_engineers`, `production.allocate_factory`, `facility.upgrade`, `procurement.*`, `test.run_ground_test`, `test.set_flight_test_syllabus`, `test.apply_flaw_fix`, `core.set_speed`, `core.save_game`, `core.load_game`, `core.continue_sandbox`) into their corresponding module handlers so every UI button in `MIC.Game` executes cleanly without impedance mismatch.
2. **Scripted & MTTH Events (`EventEngine`)**:
   - On `OnDayTick`, auto-resolve any pending multi-option event where `world.Day >= pending.ExpiresDay` using `world.Rng.Stream("core.events.choice").WeightedChoice(...)` (`30`-day timeout).
   - Fire date-triggered events matching `schedule.Iso` and scheduled events matching `world.Day`.
   - On `OnMonthStart`, evaluate MTTH events in sorted ID order using `Pcg32.MtthProb(mtthDays, schedule.DaysInPrevMonth)` on stream `"core.events.mtth"`, capped at `max_mtth_events_per_month = 2`.

---

## Ticket T21 — Deterministic Versioned JSON / Gzip `SaveLoadManager` & Rotating Autosaves

- **Depends On**: `T20`
- **Spec References**: `docs/spec/09_core_loop.md` §4.6 (Save Envelope Schema `save_schema_version = 1`), §6 (`autosave.monthly_rotating_slots = 3`), §7 (Edge Cases 1–4: 64-bit RNG hex strings, sorted dictionary keys, recursive `NaN`/`Infinity` guard & `-0.0` canonicalization); Python oracle `sim/mic/campaign/save_load.py`.
- **Golden Test Vector File & Tolerance**: `sim/golden/core_campaign_smoke.json` (`save_load_split_1945_seed_777`: saving at `mid_day = 181` (`1945-07-01`) and reloading produces the **exact SHA-256 `final_state_hash = "5245bad1ab16438d7df4b2ec9a93fcaa5074a1f31a037315349c959b5bc61055"`** at `1945-12-31`).

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Campaign/SaveLoadManager.cs
namespace MIC.Core.Campaign;
using System.Collections.Generic;

public sealed record SaveEnvelopeDto(
    int SaveSchemaVersion, string GameVersion, string CampaignId,
    IReadOnlyDictionary<string, object?> WorldState,
    IReadOnlyDictionary<string, IReadOnlyDictionary<string, object?>> Modules
);

public static class SaveLoadManager
{
    public const int CurrentSaveSchemaVersion = 1;
    public const string CurrentGameVersion = "0.1.0-mvp";

    public static SaveEnvelopeDto ToEnvelope(CampaignRunner runner);
    public static CampaignRunner FromEnvelope(SaveEnvelopeDto envelope);

    public static string SerializeToCanonicalJson(SaveEnvelopeDto envelope);
    public static void SaveToFile(CampaignRunner runner, string filePath, bool compressGzip = false);
    public static CampaignRunner LoadFromFile(string filePath);

    public static void ValidateAndCanonicalizeJsonTree(object? node, string path = "$"); // Throws ValueError/ArgumentException on NaN/Infinity; normalizes -0.0 -> 0.0
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T21)
1. **Recursive Canonicalizer & NaN Guard (`ValidateAndCanonicalizeJsonTree`)**:
   - Walk every dictionary, list, and scalar before serialization. If any `double` is `double.IsNaN(d)` or `double.IsInfinity(d)`, throw `InvalidDataException($"Non-finite float encountered at {path}")`.
   - Normalize negative zero (`d == 0.0` $\to$ `+0.0`) so `-0.0` never alters SHA-256 canonical JSON digests.
   - Sort all dictionary keys using `StringComparer.Ordinal`.
2. **Rotating Monthly & Yearly Autosaves**:
   - On `Phase A` (`OnMonthStart`), record `autosave_slot_{monthCount % 3}:{schedule.Iso}` (and `autosave_yearly_{schedule.Year}:{schedule.Iso}` when `schedule.Month == 1`).
3. **Verification (`tests/MIC.Core.Tests/T21_SaveLoadDeterminismTests.cs`)**: Assert `save_load_split_1945_seed_777` in `core_campaign_smoke.json` produces the exact SHA-256 `final_state_hash` whether run continuously or saved to `.json` / `.json.gz` at `day = 181` and reloaded.

---

## Ticket T22 — Insolvency / Takeover Checks, `1960-12-31` `ScoringService` & Sandbox Continuation (D8)

- **Depends On**: `T21`
- **Spec References**: `docs/spec/00_conventions.md` §1 (Locked Decision **D8**: At `1960-12-31`, lock the official 1945–1960 campaign score/epilogue and allow clicking *"Continue in Sandbox"* with dynamic procedural RFPs); `docs/spec/09_core_loop.md` §3.1 (Emergency V-Loan Bailout, Bankruptcy, 24-Month Idle Hostile Takeover), §5.4 (`1960-12-31` Victory Scoring Formula & Grade Tiers `S`..`D`); Python oracle `sim/mic/campaign/scoring.py`.
- **Golden Test Vector File & Tolerance**: `sim/golden/core_campaign_smoke.json` (`full_mvp_1945_1960_seed_1945`: `days_simulated = 5844`, `final_score = 7195.57`, `grade_tier = "S"`, `state_hash = "69066eb731b63ad97cad4fe29d4df08d4a0b242c62c21e1ff4bb4912c7aa897a"`) — **exact SHA-256 & `rel_tol = 1e-6`**.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Campaign/ScoringService.cs
namespace MIC.Core.Campaign;
using System.Collections.Generic;

public sealed record CompanyScoreBreakdown(
    string CompanyId, bool IsPlayer, double NetWorthNominalUsd, double NetWorth1950Usd,
    double NetWorthPoints, int AircraftDelivered, double DeliveryPoints,
    int ContractsWon, double ContractPoints, double ReputationAvg, double ReputationPoints,
    int TechsUnlocked, double TechPoints, double RawScore, double DifficultyMultiplier,
    double FinalScore, string GradeTier, string GradeTitleKey, int IndustryRank
);

public static class ScoringService
{
    public static void CheckFailureAndEndConditions(WorldState world);
    public static IReadOnlyList<CompanyScoreBreakdown> ComputeLeaderboardAndScores(WorldState world);
    public static void ContinueInEndlessSandbox(WorldState world); // D8: locks 1960 score snapshot, sets IsEndlessSandbox = true, Ended = false
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T22)
1. **Insolvency, V-Loan Bailout & 24-Month Idle Takeover (`CheckFailureAndEndConditions`)**:
   - If `player.CashUsd < 0.0`, increment `InsolventDays`. When `InsolventDays >= graceDays` (`90` on Normal), if `DebtUsd / StartingNetWorthUsd <= 0.85` and bailout not yet used, grant emergency V-Loan restoring `CashUsd = +250000.0`; else set `Ended = true, Outcome = "bankruptcy"`.
   - From `year >= 1948`, if `IdleMonthsWithoutContract >= 24` and `NetWorthUsd < 0.25 * StartingNetWorthUsd`, set `Ended = true, Outcome = "forced_takeover"` (warning notification at `18` months).
2. **1960-12-31 Victory Scoring & Locked Decision D8 (`ComputeLeaderboardAndScores`, `ContinueInEndlessSandbox`)**:
   - Compute $S_{\text{NW}}, S_{\text{deliv}}, S_{\text{contracts}}, S_{\text{rep}}, S_{\text{tech}}, S_{\text{raw}}, S_{\text{final}}$ and Grade Tier (`S` $\ge 4500$, `A` $\ge 3000$, `B` $\ge 1800$, `C` $\ge 900$, `D` $< 900`) per `09_core_loop.md` §5.4.
   - When `core.continue_sandbox` is invoked after `day == 5843`, freeze `World.Locked1960ScoreBreakdown`, set `World.IsEndlessSandbox = true`, `World.Ended = false`, and allow `StepDay()` to continue indefinitely past `1961-01-01` using `FY1961` budget baselines and `DynamicRfpGenerator`.
3. **Verification (`tests/MIC.Core.Tests/T22_FullCampaignAndScoringTests.cs`)**: Assert `full_mvp_1945_1960_seed_1945` and `smoke_2y_seed_42` in `core_campaign_smoke.json` match 100%, plus test `ContinueInEndlessSandbox` through `1962-12-31`.
