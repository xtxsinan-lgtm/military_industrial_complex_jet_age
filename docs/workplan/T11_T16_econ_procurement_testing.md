# Workplan Tickets T11–T16 — Corporate Economy, Pentagon Procurement & Bayesian Testing

> **Status**: v1.0 (Ticket-Level Implementation Plan for `MIC.Core` & `MIC.Core.Tests`)
> **Owner Assemblies**: `src/MIC.Core/` (`MIC.Core.Econ`, `MIC.Core.Procurement`, `MIC.Core.Testing`)
> **Authoritative Specs**: `docs/spec/04_economy.md` §§4–8, `docs/spec/05_procurement.md` §§4–8, `docs/spec/06_testing_uncertainty.md` §§4–8
> **Golden Vectors**: `econ_cost_historical.json`, `econ_contracts_and_settlement.json`, `procurement_scoring_vectors.json`, `procurement_lifecycle_vectors.json`, `procurement_dynamic_vectors.json`, `testing_hashing_vectors.json`, `testing_truth_and_flaws.json`, `testing_bayesian_progression.json`, `testing_flight_programme_run.json`

---

## Ticket T11 — DAPCA-Style RDT&E / Flyaway Cost Estimator & Wright's Law Learning Curve

- **Depends On**: `T02`, `T08`
- **Spec References**: `docs/spec/04_economy.md` §5.1–5.2 (Modified DAPCA-IV / RAND R-1693 Cost Model, Complexity $C_{\text{total}}$, Material Mix $C_{\text{mat}}$, Tech Immaturity $M_{\text{imm}}$, Wright 1936 Cumulative-Average Learning Curve, Recurring Unit Flyaway Cost, Non-Recurring RDT&E Cost), §5.4 (Anderlohr 1969 Production Break Setback); Python oracle `sim/mic/econ/cost.py` and `sim/mic/econ/production.py`.
- **Golden Test Vector Files & Tolerances**:
  - `sim/golden/econ_cost_historical.json`: **relative tolerance `1e-6`** across all 13 benchmark cases (`f80c_shooting_star` through `f106a_delta_dart` + `f104a_with_tech_context_and_immaturity`).
  - `sim/golden/econ_contracts_and_settlement.json`: `wright_factors` (`cum_avg_q100_s080`, `cum_avg_q500_s080`, `lot_101_to_150_s080_no_break`, `lot_101_to_150_s080_with_30_setback`) within **`rel_tol = 1e-6`**.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Econ/WrightLearningCurve.cs
namespace MIC.Core.Econ;

public static class WrightLearningCurve
{
    public static double CumulativeAverageFactor(int quantity, double learningSlope = 0.80);
    public static double UnitFactor(int unitNumber, double learningSlope = 0.80, double breakSetbackUnits = 0.0);
    public static double LotAverageFactor(int startUnit, int endUnit, double learningSlope = 0.80, double breakSetbackUnits = 0.0);
    public static double StepAnderlohrBreakSetback(
        double currentSetbackUnits, int cumulativeUnitsBuilt, bool isLineIdle, bool retainWorkforce);
}

// File: src/MIC.Core/Econ/CostEstimator.cs
namespace MIC.Core.Econ;
using MIC.Core.Contracts;
using MIC.Core.Tech;

public sealed record CostEstimateReport(
    int Year, int Quantity, int Prototypes, double AirframeMassKg, double AirframeMassLb,
    double MaxMach, double LearningCurveRate, double WrightLaborFactor, double WrightMaterialFactor,
    double ComplexityFactor, double MaterialMixFactor, double ImmaturityPenaltyDev, double ImmaturityPenaltyMfg,
    double AeroCostIndex, double CpiIndex, double EngineeringHours, double ToolingHours,
    double T1MfgLaborHours, double AvgMfgLaborHours, double AvgQcHours,
    double T1AirframeCostUsd, double AirframeUnitCostUsd, double EngineUnitCostUsd,
    double AvionicsUnitCostUsd, double ArmamentUnitCostUsd, double UnitFlyawayCostUsd,
    double UnitFlyawayCost1950Usd, double DevEngineeringCostUsd, double DevSupportCostUsd,
    double DevToolingCostUsd, double PrototypesCostUsd, double FlightTestSupportCostUsd,
    double DevCostUsdEstimate, double DevCost1950Usd, double MaintMhPerFh
);

public static class CostEstimator
{
    public static double GetAeroCostIndex1950(int year);
    public static double GetCpiDeflator1950(int year);

    public static CostEstimateReport EstimateCosts(
        AircraftDesign design, double emptyMassKg, IEngineSpec engine,
        int quantity = 250, int year = 1950, int prototypes = 2,
        double? maxMachOverride = null, ITechContext? techContext = null);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T11)
1. **Wright Continuous Approximation (`WrightLearningCurve`)**:
   - Clamp `quantity >= 1`. When `quantity == 1`, `CumulativeAverageFactor` returns `1.0` (`04_economy.md` §7.4).
   - For `quantity > 1`, let $b = \ln(S) / \ln(2.0)$ and return $\frac{(Q + 0.5)^{1+b} - 0.5^{1+b}}{(1 + b) Q}$.
2. **Airframe Complexity & Material Multipliers (`CostEstimator`)**:
   - Clamp `airframeMassKg = Math.Max(400.0, emptyMassKg - design.Propulsion.Count * engine.MassKg)`.
   - Normalize `al + steel + ti` by their sum. Implement exact $C_{\text{mach}}, C_{tc}, C_{\text{sweep}}, C_{\text{feat}}, C_{\text{mat}}, M_{\text{imm,dev}}, M_{\text{imm,mfg}}$ formulas from `04_economy.md` §5.2 (`sim/mic/econ/cost.py`).
3. **Verification (`tests/MIC.Core.Tests/T11_EconCostHistoricalTests.cs`)**: Assert all 13 vectors in `econ_cost_historical.json` and `wright_factors` in `econ_contracts_and_settlement.json` match within `rel_tol = 1e-6`.

---

## Ticket T12 — Contract Types (`CPFF`, `FPIF`, `FFP`), Monthly Settlement, Workforce & Insolvency

- **Depends On**: `T09`, `T11`
- **Spec References**: `docs/spec/04_economy.md` §4.1 (`CompanyState`), §5.3 (Workforce Brooks's Law & Discipline Mix TV Penalty), §5.5 (Defense Contracts `CPFF`/`FPIF`/`FFP`/`LETTER`, 75% Progress Payments, ASPR Section XV Overhead & IR&D 3.5% Cap, Renegotiation Act of 1951 12% ROS Clawback, Credit Rating & 3-Month Insolvency / Chapter XI); Python oracle `sim/mic/econ/contracts.py`, `sim/mic/econ/workforce.py`, `sim/mic/econ/company.py`.
- **Golden Test Vector File & Tolerance**: `sim/golden/econ_contracts_and_settlement.json` — **relative tolerance `1e-6`** across `cpff_two_step`, `fpif_underrun_two_step`, `fpif_overrun_above_ceiling`, `aspr_overhead_and_renegotiation`, and the 12-month `company_12_month_ledger`.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Econ/ContractAccounting.cs
namespace MIC.Core.Econ;

public sealed class DefenseContract
{
    public string ContractId { get; init; } = "";
    public string ProgramId { get; init; } = "";
    public string Customer { get; init; } = "USAF";
    public string ContractType { get; set; } = "CPFF"; // "CPFF" | "FPIF" | "FFP" | "LETTER"
    public string Phase { get; init; } = "rdte";       // "rdte" | "production"
    public double TargetCostUsd { get; init; }
    public double TargetProfitOrFeeUsd { get; init; }
    public double CeilingPriceUsd { get; init; }
    public double GovtShareRatio { get; init; } = 0.80;
    public double UnitPriceUsd { get; set; }
    public int Quantity { get; set; }
    public bool GfeProvided { get; init; } = true;
    public double IncurredCostUsd { get; set; }
    public double ReimbursedOrProgressPaidUsd { get; set; }
    public double DeliveryPaymentsReceivedUsd { get; set; }
    public double FeePaidUsd { get; set; }
    public int UnitsDelivered { get; set; }
    public int UndefinitizedMonthsElapsed { get; set; }
    public string DefinitizesTo { get; init; } = "CPFF";
    public bool Completed { get; set; }
    public double TargetPriceUsd => TargetCostUsd + TargetProfitOrFeeUsd;
    public double RemainingBacklogUsd { get; }
}

public readonly record struct ContractStepSettlement(
    double CashReceivedUsd, double ProgressPaymentUsd,
    double DeliveryOrSettlementUsd, double FeeReceivedUsd, double ReputationDelta
);

public static class ContractAccounting
{
    public static ContractStepSettlement StepContractBilling(
        DefenseContract contract, double costIncurredThisPeriodUsd,
        int unitsDeliveredThisPeriod = 0, bool markCompleted = false, double latePenaltyFraction = 0.0);

    public static (double AllowableOverheadUsd, double AllowableIradUsd, double UnallowableUsd) ComputeAsprOverheadRecovery(
        double directGovtCostBaseUsd, double incurredIndirectOverheadUsd, double incurredIradBpUsd);

    public static double ComputeRenegotiationClawback1951(
        int year, double annualDefenseRevenueUsd, double annualDefensePreTaxProfitUsd);
}

// File: src/MIC.Core/Econ/WorkforceModel.cs
namespace MIC.Core.Econ;
using System.Collections.Generic;

public static class WorkforceModel
{
    public static double ComputeBrooksLawEfficiency(double totalTeamFte, double recentHireFraction);
    public static double ComputeDisciplineMixEfficiency(
        IReadOnlyDictionary<string, double> allocatedShares, IReadOnlyDictionary<string, double> requiredShares);
    public static double ComputeMonthlyEffectiveHours(
        double totalTeamFte, double recentHireFraction, double morale,
        IReadOnlyDictionary<string, double> allocatedShares, IReadOnlyDictionary<string, double> requiredShares);
}

// File: src/MIC.Core/Econ/CompanyMonthlySettlement.cs
namespace MIC.Core.Econ;
using MIC.Core.Contracts;

public sealed record MonthlyLedgerReport(
    int Year, int Month, double OpeningCashUsd, double ContractReceiptsUsd,
    double CommercialAndSparesRevenueUsd, double PayrollExpenseUsd,
    double FacilityOverheadExpenseUsd, double DirectProductionAndRdCostUsd,
    double DebtInterestExpenseUsd, double RenegotiationClawbackUsd,
    double NetCashFlowUsd, double ClosingCashUsd, double ClosingDebtUsd, string CreditRating
);

public static class CompanyMonthlySettlement
{
    public static MonthlyLedgerReport StepCompanyMonth(CompanyState company, int year, int month);
    public static void ExecuteChapterXiReorganization(CompanyState company);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T12)
1. **Contract Billing (`StepContractBilling`)**:
   - **CPFF**: Reimburse allowable cost up to `1.25 * TargetCostUsd`; pay `85%` of pro-rata fixed fee during execution and release the `15%` withheld fee on `markCompleted == true`. If final cost exceeds `1.10 * TargetCostUsd`, apply reputation delta `-2.0`.
   - **FPIF**: Pay `75%` progress payments on incurred cost (capped at `80%` of `TargetPriceUsd`). On delivery/completion, compute final price $\min(P_{\text{ceil}}, C_{\text{act}} + \Pi_{\text{target}} + (1 - s_{\text{govt}})(C_{\text{target}} - C_{\text{act}}))(1 - \text{penalty}_{\text{late}})$ and settle balance against prior progress + delivery payments.
2. **ASPR & Renegotiation Act (`ComputeAsprOverheadRecovery`, `ComputeRenegotiationClawback1951`)**: Cap IR&D recovery at `3.5%` of direct base and total indirect overhead at `115%`. In December (`month == 12`, `year >= 1951`), claw back `65%` of defense pre-tax profit exceeding `12.0%` return on sales.
3. **Verification (`tests/MIC.Core.Tests/T12_EconContractsAndSettlementTests.cs`)**: Assert `econ_contracts_and_settlement.json` matches within `rel_tol = 1e-6`.

---

## Ticket T13 — Pentagon RFP Catalog, Threshold/Objective Scoring & Credibility Multiplier

- **Depends On**: `T02`, `T08`, `T10`
- **Spec References**: `docs/spec/05_procurement.md` §4 (`Requirement`, `ProposalBid`, `BidderContext`, 16 Historical Programs in `sim/data/programs/*.json`), §§5.1–5.5 (Hard Responsiveness Gates, Credibility $C$, Novelty $N$, Skepticism Haircut & Overclaim Credit $\hat{V}_i$, Piecewise Linear Criterion Utility $u_i$, Should-Cost & Schedule Realism Floors, Technical Risk $R_{\text{tech}}$, Political Bonus $\Delta_{\text{pol}}$); Python oracle `sim/mic/procurement/models.py` and `sim/mic/procurement/scoring.py`.
- **Golden Test Vector File & Tolerance**: `sim/golden/procurement_scoring_vectors.json` — **relative tolerance `1e-6`** across `honest_incumbent`, `overclaim_newcomer`, `lowball_price_and_schedule_realism`, and `non_responsive_disqualification`.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Procurement/ProcurementModels.cs
namespace MIC.Core.Procurement;
using System.Collections.Generic;
using MIC.Core.Contracts;

public sealed record NoveltyProfile(
    int UnprovenTechCount, bool UnflownEngine, bool UnconventionalLayout
);

public sealed record BidderContext(
    string CompanyId, double Reputation0To100, double TrackRecord0To1,
    double PoliticalCapitalSpent, int ActiveProductionContractsCount,
    bool HasPriorServiceFighterInOtherBranch, bool IsOriginator = false
);

public sealed record ProposalBid(
    string BidId, string CompanyId, string DesignId, string DesignName,
    int SubmittedDay, int PromisedFirstFlightDay, int PromisedIocDay,
    double UnitPriceBidUsd, double ShouldCostUnitUsd,
    double DevCostBidUsd, double ShouldCostDevUsd,
    IReadOnlyDictionary<string, double> PromisedPerformance,
    IReadOnlyDictionary<string, Estimate> SubstantiatedEstimates,
    IReadOnlyDictionary<string, object> EquipmentProvided,
    NoveltyProfile Novelty,
    bool BuiltPrototype = false, int? ActualFirstFlightDay = null,
    IReadOnlyDictionary<string, Estimate>? MeasuredPerformance = null,
    double UnfixedFlawSeveritySum = 0.0
);

public sealed record CriterionScoreDetail(
    string Key, string Kind, double Promised, double SubstantiatedMu, double SubstantiatedSigma,
    double CredibleValue, double OverclaimQ, bool GatePassed,
    double Utility, double Weight, double WeightedUtility
);

public sealed record BidEvaluationResult(
    string BidId, string CompanyId, string DesignName, string Phase, // "proposal" | "flyoff"
    bool Responsive, IReadOnlyList<string> DisqualifyReasons,
    double Credibility, double NoveltyIndex,
    double PerfScore, double CostScore, double SchedScore,
    double RiskIndex, double RiskScore, double TechScore,
    double PoliticsBonus, double PromisePenalty, double FlawPenalty,
    double EvalNoise, double TotalScore,
    IReadOnlyList<CriterionScoreDetail> CriteriaDetails,
    bool EligibleForPrivatePrototype
);

// File: src/MIC.Core/Procurement/ProposalEvaluator.cs
namespace MIC.Core.Procurement;
using System.Collections.Generic;
using MIC.Core.Contracts;

public static class ProposalEvaluator
{
    public static double ComputeCredibility(double reputation0To100, double trackRecord0To1);
    public static double ComputeNoveltyIndex(NoveltyProfile novelty);

    public static (double CredibleValue, double OverclaimQ) ComputeCredibleValue(
        double promised, double mu, double sigma, int directionSign, double credibility, double noveltyIndex);

    public static double ComputeCriterionUtility(
        double credibleValue, double thresholdValue, double objectiveValue, int directionSign);

    public static BidEvaluationResult ScoreSingleBid(
        Requirement req, ProposalBid bid, BidderContext ctx,
        string phase = "proposal", double evalNoise = 0.0);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T13)
1. **Credibility $C$ & Novelty $N$**:
   - $C = \text{clamp}(0.20 + 0.50 \cdot (R / 100.0) + 0.30 \cdot \tau,\; 0.05,\; 0.95)$.
   - $N = 0.20 \cdot N_{\text{unproven}} + 0.25 \cdot \mathbb{I}(\text{unflown\_engine}) + 0.15 \cdot \mathbb{I}(\text{unconventional})$.
2. **Skepticism Haircut & Overclaim Credit (`ComputeCredibleValue`)**:
   - Let $s_i = +1$ for `">="` and $-1$ for `"<="`. Substantiated conservative baseline: $\mu_{\text{sub}, i} = \mu_i - s_i \cdot 1.00 \cdot (1.0 - C)(0.50 + N)\sigma_i$.
   - Overclaim $\Delta_{\text{oc}, i} = \max(0.0, s_i(P_i - \mu_i))$. Overclaim credit fraction $\lambda_{\text{oc}} = \text{clamp}\!\left(\frac{C^2}{1.0 + N},\; 0.15,\; 0.60\right)$.
   - $\hat{V}_i = \mu_{\text{sub}, i} + s_i \lambda_{\text{oc}} \Delta_{\text{oc}, i}$ (or $\min_{s_i}(P_i, \mu_{\text{sub}, i})$ if promising more conservatively than $\mu_i$).
   - Overclaim normalized sigma $q_i = \Delta_{\text{oc}, i} / \max(\sigma_i, 0.01 \max(|\mu_i|, 1.0))$.
3. **Hard Responsiveness Gates, Cost/Schedule Realism Floors & Politics**:
   - Disqualify (`Responsive = false`) if any threshold gate fails on $P_i$, any `req.Equipment` gate fails, or `UnitPriceBidUsd > 1.30 * req.Budget.UnitPriceCeilingUsd`.
   - Clamp credited bid price at should-cost floor $\hat{B}_{\text{unit}} = \max(B_{\text{unit}}, 0.90 \cdot E_{\text{unit}})$ and promised first-flight day at $t_{\text{sub}} + 0.75 \cdot D_{\text{exp}}$.
4. **Verification (`tests/MIC.Core.Tests/T13_ProcurementScoringTests.cs`)**: Assert all 4 vectors in `procurement_scoring_vectors.json` match within `rel_tol = 1e-6`.

---

## Ticket T14 — Two-Stage Hardware Fly-Off Lifecycle (D6), Debrief (D10) & Dynamic RFPs

- **Depends On**: `T12`, `T13`, `T16`
- **Spec References**: `docs/spec/00_conventions.md` §1 (Locked Decision **D6**: default all gameplay procurement programs to two-stage `flyoff` while keeping `historical_acquisition_styles` toggle for replay; Locked Decision **D10**: post-award Source Selection Debrief); `docs/spec/05_procurement.md` §§5.5.3–5.11 (Paper Downselect & Private-Venture Entry Margin `8.0 pts`, Stage 2 Fly-Off Evaluation & Waiver/Cancel Roll, IOC Promise Audit & Liquidated Damages, Annual July 1 Lot Review, Alt-History Adaptation/Suppression/Redirection, Procedural RFP Generator, Unsolicited Proposals); Python oracle `sim/mic/procurement/lifecycle.py` and `sim/mic/procurement/dynamic.py`.
- **Golden Test Vector Files & Tolerances**:
  - `sim/golden/procurement_lifecycle_vectors.json`: **relative tolerance `1e-6`** across `flyoff_usn_fad_1955_f4h_vs_f8u3`, `flyoff_waiver_and_promise_audit`, and `annual_lot_review_and_f108_cancellation`.
  - `sim/golden/procurement_dynamic_vectors.json`: **relative tolerance `1e-6`** across `alt_history_adaptation_and_redirection` and `procedural_rfp_and_unsolicited_pitch`.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Procurement/FlyOffLifecycleEngine.cs
namespace MIC.Core.Procurement;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Random;

public sealed record SelectionOutcomeReport(
    string RequirementId, string Stage, string Outcome, // "downselect"|"awarded"|"dual_award"|"waiver_award"|"cancelled"|"no_responsive_bid"
    IReadOnlyList<string> WinnerCompanyIds,
    IReadOnlyList<BidEvaluationResult> RankedEvaluations,
    IReadOnlyList<string> PrivateVentureEligibleCompanyIds,
    string DebriefNarrativeSummary
);

public sealed record PromiseAuditResult(
    double WeightedShortfallPct, double LiquidatedDamagesFraction,
    double ReputationDelta, double UpdatedTrackRecord, bool TriggerShowCauseReview
);

public sealed record AnnualLotReviewResult(
    bool Cancelled, double CancelProbability, int NextLotQuantity, double QtyMultiplier, string Reason
);

public static class FlyOffLifecycleEngine
{
    public static string EffectiveAcquisitionStyle(Requirement req, bool historicalAcquisitionStyles); // D6: returns "flyoff" when historicalAcquisitionStyles == false

    public static SelectionOutcomeReport EvaluateProposals(
        Requirement req, IReadOnlyList<(ProposalBid Bid, BidderContext Ctx)> entries,
        Pcg32? rng = null, bool historicalAcquisitionStyles = true);

    public static SelectionOutcomeReport EvaluateFlyOff(
        Requirement req, IReadOnlyList<(ProposalBid Bid, BidderContext Ctx)> finalists,
        Pcg32? rng = null, double strategicUrgency = 0.5);

    public static PromiseAuditResult AuditMilestonePromises(
        Requirement req, ProposalBid bid, IReadOnlyDictionary<string, double> actualPerformance,
        double currentTrackRecord);

    public static AnnualLotReviewResult ReviewAnnualProductionLot(
        Requirement req, double costOverrunRatio, double scheduleSlipMonths,
        double performanceShortfallPct, double obsolescenceShock, double budgetIndex, Pcg32? rng = null);
}

// File: src/MIC.Core/Procurement/DynamicRfpGenerator.cs
namespace MIC.Core.Procurement;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Random;

public static class DynamicRfpGenerator
{
    public static Requirement AdaptHistoricalRequirement(
        Requirement baseReq, IReadOnlyDictionary<string, double> worldRecordsByMetric,
        IReadOnlyDictionary<string, string> priorProgramWinners);

    public static bool ShouldSuppressStopgapProgram(Requirement req, double maxMachInServiceForCustomer);

    public static Requirement? TrySynthesizeProceduralRfp(
        string customer, string role, int currentDay, double fleetAgeYears,
        double threatDeficit, double budgetIndex, Pcg32 rng);

    public static SelectionOutcomeReport EvaluateUnsolicitedProposal(
        string customer, string role, int currentDay, ProposalBid pitchBid, BidderContext ctx,
        double fleetDemand, double budgetIndex, bool openRfpExistsInRole, Pcg32 rng);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T14)
1. **Locked Decision D6 (`EffectiveAcquisitionStyle`)**: When `historicalAcquisitionStyles == false` (default gameplay mode), override `req.Acquisition.Style` to `"flyoff"` with `downselect_count = 2` so every competition runs a two-stage hardware prototype fly-off. When `historicalAcquisitionStyles == true` (used in historical golden replay vectors), preserve `req.Acquisition.Style`.
2. **Stage 2 Fly-Off (`EvaluateFlyOff`)**: Score finalists using `bid.MeasuredPerformance` (`source = "flight"`), apply `PromisePenalty` (`1.0 pt` per `1%` weighted shortfall vs. paper promises) and `FlawPenalty` (`3.0 pts` per unfixed flaw severity point), and handle the all-fail Waiver vs. Cancellation roll (`WAIVER_P_BASE = 0.60 + 0.30 * urgency`).
3. **Source Selection Debrief (D10)**: Populate `RankedEvaluations` (`PerfScore`, `CostScore`, `SchedScore`, `RiskScore`, `PoliticsBonus`, `TotalScore`) and deterministic `DebriefNarrativeSummary`.
4. **Verification (`tests/MIC.Core.Tests/T14_ProcurementLifecycleAndDynamicTests.cs`)**: Assert `procurement_lifecycle_vectors.json` and `procurement_dynamic_vectors.json` match within `rel_tol = 1e-6`.

---

## Ticket T15 — Deterministic Truth Hashing, 5D Value Noise, Novelty & Hidden Flaw Generator

- **Depends On**: `T01`, `T02`
- **Spec References**: `docs/spec/06_testing_uncertainty.md` §4.2 (10 Log-Space Physical Drivers `cd0`, `cdw`, `kind`, `clmax`, `mass`, `thrust`, `tsfc`, `cost_unit`, `cost_dev`, `maint`), §5.1 (FNV-1a 64 + SplitMix64 Counter-Based Hashing, `keyed_u01`, `keyed_normal`, 5D Smoothstep Value Noise $2^5 = 32$ hypercube corners preventing slider-jiggle save-scumming), §5.2 (13-Feature Novelty Extraction & Prior Bias/Variance $\mu_{0,d}, \sigma_{\text{prior},d}$), §5.3 (34 Historical Hidden Flaws Catalog & Monotonic Trigger Generation); Python oracle `sim/mic/testing/hashing.py`, `sim/mic/testing/features.py`, `sim/mic/testing/truth.py`, `sim/mic/testing/flaws.py`.
- **Golden Test Vector Files & Tolerances**:
  - `sim/golden/testing_hashing_vectors.json`: **exact integer equality** on `fnv1a_64` and `mix64`; **relative tolerance `1e-6`** on `keyed_draws` and `value_noise_5d`.
  - `sim/golden/testing_truth_and_flaws.json`: **relative tolerance `1e-6`** across all 4 canonical archetypes (`straight_wing_1946`, `swept_transonic_1950`, `early_supersonic_delta_1953`, `mach2_interceptor_1957`) for `coords_5d`, all 10 `driver_priors`, `true_drivers`, and all 34 flaw trigger probabilities.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Testing/TruthHasher.cs
namespace MIC.Core.Testing;
using System;

public static class TruthHasher
{
    public static ulong Fnv1a64(string text);
    public static ulong Mix64(ulong z);
    public static double KeyedU01(ulong campaignSeed, string key);
    public static double KeyedNormal(ulong campaignSeed, string key);
    public static double ValueNoise5D(ulong campaignSeed, string driverId, ReadOnlySpan<double> coords5D);
    public static double DriverStandardNormalZ(
        ulong campaignSeed, string categoricalSig, string driverId,
        ReadOnlySpan<double> coords5D, double categoricalWeight = 0.50);
}

// File: src/MIC.Core/Testing/FeatureExtractor.cs
namespace MIC.Core.Testing;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Tech;

public sealed record DesignFeatureVector(
    string CategoricalSig,
    double[] Coords5D, // [sweep_norm, tc_norm, ar_norm, log_area_norm, tw_norm]
    IReadOnlyDictionary<string, double> NoveltyFeatures13,
    IReadOnlyDictionary<string, double> AeroDiagnostics,
    IReadOnlyDictionary<string, double> EngineDiagnostics
);

public static class FeatureExtractor
{
    public static DesignFeatureVector Extract(
        AircraftDesign design, PerformanceReport nominalReport,
        IReadOnlyDictionary<string, double>? aeroDiagnostics = null,
        IReadOnlyDictionary<string, double>? engineDiagnostics = null,
        ITechContext? techContext = null);
}

// File: src/MIC.Core/Testing/FlawGenerator.cs
namespace MIC.Core.Testing;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Tech;

public sealed record DriverPriorAndTruth(
    string DriverId, double Mu0, double SigmaPrior, double ZDraw,
    double ND, double RD, double MTech, double QD,
    double ThetaTrue, double MultiplierTrue
);

public sealed class ActiveFlawState
{
    public string FlawId { get; init; } = "";
    public int Severity { get; init; }
    public int KnownFromYear { get; init; }
    public double TriggerProb { get; init; }
    public double UDraw { get; init; }
    public bool IsPresent { get; init; }
    public bool Detected { get; set; }
    public string? DetectedBy { get; set; }
    public double ResidualFactor { get; set; } = 1.0; // 1.0 = unfixed, <1.0 after fix or placard
    public string? FixAppliedId { get; set; }
    public bool Placarded { get; set; }
}

public static class FlawGenerator
{
    public static IReadOnlyDictionary<string, DriverPriorAndTruth> GenerateDrivers(
        ulong campaignSeed, DesignFeatureVector features, int dateDay,
        IReadOnlyDictionary<string, double>? companyFeatureExperience = null,
        ITechContext? techContext = null);

    public static IReadOnlyDictionary<string, ActiveFlawState> GenerateFlaws(
        ulong campaignSeed, DesignFeatureVector features, int dateDay,
        ITechContext? techContext = null);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T15)
1. **SplitMix64 & 5D Value Noise (`TruthHasher`)**:
   - In `Mix64(ulong z)` (`unchecked`): `z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL; return z ^ (z >> 31);`.
   - In `ValueNoise5D`, compute integer grid cell $i_k = \lfloor x_k \rfloor$, fractional part $f_k = x_k - i_k$, quintic Perlin smoothstep $w_k = f_k^3(f_k(6 f_k - 15) + 10)$, and interpolate across all $32$ vertices $v \in \{0, 1\}^5$ multiplied by variance-preservation factor $\prod_{k=0}^4 (w_k^2 + (1-w_k)^2)^{-1/2}$ (`sim/mic/testing/hashing.py`).
2. **10-Driver Priors & 34-Flaw Monotonic Draw (`FlawGenerator`)**:
   - Compute novelty score $N_d$, regime factor $R_d$, tech immaturity factor $M_{\text{tech}}$, and staff quality factor $Q_d$ exactly as in `sim/mic/testing/truth.py`.
   - For each of the 34 flaws in `sim/data/testing/flaw_catalog.json`, draw $U_{\text{flaw}} = \text{KeyedU01}(\text{seed}, \text{sig}_{\text{cat}} + \text{":flaw:"} + \text{flawId})$ and trigger iff $U_{\text{flaw}} < P_{\text{trig}, f}$.
3. **Verification (`tests/MIC.Core.Tests/T15_TestingTruthAndFlawsTests.cs`)**: Assert `testing_hashing_vectors.json` and `testing_truth_and_flaws.json` match within `rel_tol = 1e-6`.

---

## Ticket T16 — Bayesian `Estimate` Shrinkage, Wind Tunnels, Flight Syllabus, Pilots (D9) & Era Fog-of-War (D7)

- **Depends On**: `T05`, `T07`, `T10`, `T15`
- **Spec References**: `docs/spec/00_conventions.md` §1 (Locked Decision **D7**: Era-unknown flaws before `known_from_year` display as generic *"Uncharted High-Speed Regime Risks"* unless `flaw_hindsight == true`; Locked Decision **D9**: Fictional period-authentic test pilot names from `sim/data/testing/pilot_names.json`); `docs/spec/06_testing_uncertainty.md` §§5.4–5.8 (Conjugate Normal-Normal Bayesian Updating with Measurement Floor $\sigma_{\text{floor}}$, Transonic Tunnel Choking Rule before `testing.transonic_tunnel`, Prototype Rollout Weighing, 6-Item / 4-Phase Flight-Test Syllabus, Per-Sortie Flaw Discovery/Crash/Ejection Survival, Squadron Service Monthly Hazard); Python oracle `sim/mic/testing/belief.py`, `sim/mic/testing/campaigns.py`, `sim/mic/testing/pilots.py`, `sim/mic/testing/service.py`.
- **Golden Test Vector Files & Tolerances**:
  - `sim/golden/testing_bayesian_progression.json`: **relative tolerance `1e-6`** across stages `0_sim` $\to$ `1_low_speed_tunnel_choked` (`choked == true`) $\to$ `2_transonic_slotted` $\to$ `3_prototype_rollout` $\to$ `4_flight_speed_envelope` $\to$ `5_service_1yr`.
  - `sim/golden/testing_flight_programme_run.json`: **relative tolerance `1e-6` / exact integer match** across `tunnel_result`, `prototype_rollout`, `flight_result` (`total_sorties_flown = 140`, `near_misses = 1`, `flaws_detected_in_flight = ["tip_stall_wing_drop"]`), `service_result`, and `final_total_testing_cost_usd`.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Testing/BayesianBeliefTracker.cs
namespace MIC.Core.Testing;
using System.Collections.Generic;
using MIC.Core.Contracts;

public sealed record WatchlistEntry(
    string FlawId, string DisplayTitleKey, string QualitativeBand, // "Low"|"Moderate"|"High"|"Severe"|"UnchartedRegime"
    double TriggerProb, bool IsEraUnknown
);

public sealed record EstimateReport(
    IReadOnlyDictionary<string, Estimate> Metrics,
    IReadOnlyList<WatchlistEntry> Watchlist,
    bool HasUnchartedHighSpeedRegimeRisk
);

public sealed class LineageTestState
{
    public string DesignId { get; }
    public PerformanceReport NominalReport { get; }
    public IReadOnlyDictionary<string, DriverPriorAndTruth> Drivers { get; }
    public IReadOnlyDictionary<string, ActiveFlawState> Flaws { get; }
    public Dictionary<string, (double MuHat, double Variance, double MinFloorVar, string BestSource)> Beliefs { get; }

    public PerformanceReport ComputeTruePerformanceReport();
    public EstimateReport ComputeEstimateReport(int currentYear, bool flawHindsight = false);
}

// File: src/MIC.Core/Testing/CampaignsAndFlightRunner.cs
namespace MIC.Core.Testing;
using System.Collections.Generic;
using MIC.Core.Random;
using MIC.Core.Tech;

public sealed record TestPilotProfile(
    string Id, string Name, string Rank, string Service, int Skill, int Experience,
    IReadOnlyList<string> Traits, string Status = "active", int RecoveryDaysRemaining = 0
);

public static class CampaignsAndFlightRunner
{
    public static IReadOnlyList<TestPilotProfile> LoadFictionalPilotPool(); // D9: sim/data/testing/pilot_names.json

    public static TunnelCampaignResult RunTunnelOrGroundCampaign(
        LineageTestState state, string campaignId, string providerId, string depth,
        int dateDay, ITechContext techContext, Pcg32 rng, bool autoFixDetectedFlaws = false);

    public static PrototypeRolloutResult RunPrototypeRollout(
        LineageTestState state, int nPrototypes, int dateDay, Pcg32 rng);

    public static FlightProgrammeResult RunFlightTestProgramme(
        LineageTestState state, IReadOnlyList<string> syllabusItems, string depth,
        int dateDay, ITechContext techContext, Pcg32 rng,
        TestPilotProfile? assignedPilot = null, string fixPolicy = "fix_all");

    public static ServiceRunResult RunServiceMonths(
        LineageTestState state, int months, int fleetSize, int startYear, Pcg32 rng);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T16)
1. **Transonic Choking Rule & Bayesian Floor (`RunTunnelOrGroundCampaign`)**:
   - If `NominalReport.MaxMachAlt >= 0.85` and `!techContext.GetBool("testing.transonic_tunnel")` during `low_speed_tunnel` or `supersonic_tunnel`, set `Choked = true`, skip updating `cdw`, and block detection of transonic flaws (`mach_tuck`, `area_rule_drag_pinch`, `transonic_buffet`, `aileron_reversal`).
   - Update driver posterior precision $\tau_{\text{post}} = \tau_{\text{prior}} + \tau_{\text{obs}}$, then apply floor $V_d \leftarrow \max(V_{\text{post}}, \sigma_{\text{floor}, d}^2)$.
2. **Locked Decision D7 (`ComputeEstimateReport`) & D9 (`LoadFictionalPilotPool`)**:
   - When `flawHindsight == false` and `currentYear < flaw.KnownFromYear`, suppress the specific flaw from `Watchlist` and set `HasUnchartedHighSpeedRegimeRisk = true` whenever any era-unknown flaw has `TriggerProb >= 0.08`.
   - Load test pilots exclusively from `sim/data/testing/pilot_names.json` (`Maj. Richard "Dick" Thorne`, etc.).
3. **Verification (`tests/MIC.Core.Tests/T16_TestingBayesianAndFlightTests.cs`)**: Assert `testing_bayesian_progression.json` and `testing_flight_programme_run.json` match within `rel_tol = 1e-6`.
