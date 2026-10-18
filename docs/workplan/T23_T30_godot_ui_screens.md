# Workplan Tickets T23–T30 — Godot 4 UI Shell, Screens 0–8 & 2D Engineering Canvases

> **Status**: v1.0 (Ticket-Level Implementation Plan for `MIC.Game` & Headless Presenter Verification)
> **Owner Assembly**: `src/MIC.Game/` (`MIC.Game.Core`, `MIC.Game.UI`, `MIC.Game.Canvases`, `MIC.Game.Screens`)
> **Authoritative Spec**: `docs/spec/08_ui_ux.md` §§1–5 ("1950s Blueprint & Brass" Theme, Read-Only `IReadOnlyWorldState` Binding, 26 `SimCommand` Dispatches)
> **Locked Decisions Enforced**: **D1** (Pure `MIC.Core` + Godot `MIC.Game`), **D4** (Localization via `sim/data/names/*.json`), **D6** (Two-Stage Fly-Off UI), **D7** (Full Tech Tree Visibility & Era Fog-of-War Banner), **D8** (Post-1960 Sandbox Continuation), **D9** (Fictional Pilots & Named Engine Vendors), **D10** (Pre-Bid Rumors & Post-Award Debrief Modal)

---

## Ticket T23 — Godot 4 Project Shell, `Units` Helper, `EstimateBadgeControl`, `TopBarHUD` & `RightEventFeed`

- **Depends On**: `T20`, `T22`
- **Spec References**: `docs/spec/08_ui_ux.md` §1.2 (`SimCommand`, `IScreenPresenter`, `CampaignSessionNode`), §1.3 (`Units` Static Helper — 25 SI-to-US Conversions), §1.4 (`EstimateBadge.tscn` & `EstimateWhiskerCanvas`), §2.2 (`Palette.cs` & `blueprint_brass_theme.tres`), §§3.1–3.3 (`MainShell.tscn`, `TopBarHUD.tscn`, `LeftNavDock`, `RightEventFeed.tscn`, `HistoricalEventModal.tscn`, `AutoPauseModal.tscn`).
- **Golden / Unit Test Verification**: `tests/MIC.Core.Tests/T23_UnitsAndPresenterContractTests.cs` — **relative tolerance `1e-6`** across all 25 SI-to-US conversions and formatted strings in `08_ui_ux.md` §1.3.1.

### 1. Exact C# File Paths, Scene Paths & Type/Method Signatures

- **Godot Scenes**: `res://ui/shell/MainShell.tscn`, `res://ui/shell/TopBarHUD.tscn`, `res://ui/widgets/EstimateBadge.tscn`, `res://ui/modals/HistoricalEventModal.tscn`, `res://ui/modals/AutoPauseModal.tscn`.

```csharp
// File: src/MIC.Game/Core/SimCommandAndPresenter.cs
namespace MIC.Game.Core;
using System.Collections.Generic;
using Godot;
using MIC.Core.Actions;
using MIC.Core.Campaign;

public sealed record SimCommand(
    string ActionType, string ActorCompanyId, IReadOnlyDictionary<string, object?> Params
)
{
    public PlayerAction ToPlayerAction() => new(ActionType, ActorCompanyId, Params);
}

public interface IScreenPresenter
{
    void BindView(Control rootControl);
    void RefreshFromState(IReadOnlyWorldState state);
    bool CanNavigateAway();
}

// File: src/MIC.Game/Core/CampaignSessionNode.cs
namespace MIC.Game.Core;
using Godot;
using MIC.Core.Actions;
using MIC.Core.Campaign;

public sealed partial class CampaignSessionNode : Node
{
    public static CampaignSessionNode Instance { get; private set; } = default!;

    [Signal] public delegate void StateChangedEventHandler(int currentDay, string lastCommandType);
    [Signal] public delegate void NotificationEmittedEventHandler(string notificationId, string category, bool autoPaused);

    public IReadOnlyWorldState State => _runner.World;
    public int CurrentSpeedIndex { get; private set; } // 0=Pause, 1..5=Speeds, 6=SmartSpeed

    public void StartNewCampaign(CampaignConfig config);
    public ActionResult SubmitCommand(SimCommand command);
    public override void _Process(double delta);
}

// File: src/MIC.Game/UI/Units.cs (Also compiled into MIC.Core.Tests via <Compile Include> for headless xUnit verification)
namespace MIC.Game.UI;

public static class Units
{
    public const double MPerFt = 0.3048;
    public const double KgPerLb = 0.45359237;
    public const double NPerLbf = 4.4482216152605;
    public const double MpsPerKt = 0.514444;
    public const double MPerNmi = 1852.0;
    public const double SqMPerSqFt = MPerFt * MPerFt;
    public const double FpmPerMps = 60.0 / MPerFt;
    public const double LbPerSqFtPerKgM2 = SqMPerSqFt / KgPerLb;
    public const double PsfPerPa = SqMPerSqFt / NPerLbf;
    public const double SfcUsPerSi = 3600.0 * NPerLbf / KgPerLb;

    public static (double DisplayValue, string UnitSuffix, string FormatSpec) ConvertMetric(string metricOrUnitKey, double siValue);
    public static string FormatUsd(double usd, bool compact = true, bool showSign = false);
    public static string FormatMetric(string metricOrUnitKey, double siValue, bool includeUnit = true);
}

// File: src/MIC.Game/UI/EstimateBadgeControl.cs
namespace MIC.Game.UI;
using Godot;
using MIC.Core.Contracts;

public sealed partial class EstimateBadgeControl : HBoxContainer
{
    public void BindEstimate(string metricKey, Estimate estimate, double? rfpThresholdSi = null);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T23)
1. **Exact `Units.cs` Implementation**: Copy the exact switch-expression and constants from `08_ui_ux.md` §1.3.2 (`src/MIC.Game/UI/Units.cs`).
2. **`EstimateBadgeControl` & `EstimateWhiskerCanvas._Draw()`**: Render the source badge (`SIM` `#5DA9E9`, `TUNNEL` `#E09F3E`, `GROUND` `#B388EB`, `FLIGHT` `#3BCEAC`, `SERVICE` `#A3E635`, `RUMOR` `#94ADC7`), point estimate, $\pm 1\sigma$ label, $84 \times 18\text{ px}$ whisker bar ($R_{\max} = 0.25$), and optional `#F4B942` dashed RFP threshold tick (`08_ui_ux.md` §1.4.4).
3. **`MainShell.tscn`, `TopBarHUD.tscn`, `LeftNavDock` & `RightEventFeed.tscn`**:
   - Wire hotkeys `Space` (Pause), `Key1`–`Key5` (`1x`–`5x`), `Tab` (`Smart Speed`), and `F1`–`F7` workspace switching (`08_ui_ux.md` §§3.1–3.2).
   - Wire `PendingChoicesContainer` to open `HistoricalEventModal.tscn` and dispatch `core.choose_event_option`, and `NotificationListVBox` to jump to the target workspace or dispatch `core.dismiss_notification`.

---

## Ticket T24 — Screen 0 (`NewCampaignScreen`) & Screen 1 (`ExecutiveDashboardScreen`)

- **Depends On**: `T23`
- **Spec References**: `docs/spec/08_ui_ux.md` §4.0 (`NewCampaignScreen.tscn` — Contractor selection, Chief Designer card, Seed input, Locked Decision **D6** Procurement toggle, **D7** Hindsight toggle, **D4** Fictional Names toggle), §4.1 (`ExecutiveDashboardScreen.tscn` & `CashRunwayChartCanvas.cs`).
- **Verification**: Headless presenter & chart vertex tests in `T24_SetupAndDashboardPresenterTests.cs`.

### 1. Exact C# File Paths, Scene Paths & Type/Method Signatures

- **Godot Scenes**: `res://ui/screens/NewCampaignScreen.tscn`, `res://ui/screens/ExecutiveDashboardScreen.tscn`.

```csharp
// File: src/MIC.Game/Screens/NewCampaignPresenter.cs
namespace MIC.Game.Screens;
using Godot;
using MIC.Core.Campaign;
using MIC.Core.Content;

public sealed record CampaignConfig(
    string PlayerCompanyId, ulong Seed, string DifficultyId = "normal",
    bool StrictCookCraigie = false, // D6: false = Always Two-Stage Fly-Off
    bool FlawHindsight = false,     // D7: false = Standard Era Fog-of-War
    bool UseFictionalNames = false, // D4: false = Authentic Historical Names
    CustomStartupConfig? CustomStartup = null
);

public sealed partial class NewCampaignPresenter : Control
{
    public void SelectContractor(string companyId, ContentCatalog content);
    public CampaignConfig BuildCampaignConfigFromUi();
    public void OnLaunchCampaignPressed();
}

// File: src/MIC.Game/Screens/ExecutiveDashboardPresenter.cs
namespace MIC.Game.Screens;
using System.Collections.Generic;
using Godot;
using MIC.Core.Campaign;
using MIC.Game.Core;

public sealed partial class ExecutiveDashboardPresenter : MarginContainer, IScreenPresenter
{
    public void BindView(Control rootControl);
    public void RefreshFromState(IReadOnlyWorldState state);
    public bool CanNavigateAway() => true;
}

// File: src/MIC.Game/Canvases/CashRunwayChartCanvas.cs
namespace MIC.Game.Canvases;
using System.Collections.Generic;
using Godot;

public sealed partial class CashRunwayChartCanvas : Control
{
    public void SetCashSeries(IReadOnlyList<double> trailing12MoCashUsd, IReadOnlyList<double> forward12MoProjectedUsd);
    public override void _Draw();
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T24)
1. **Screen 0 (`NewCampaignScreen.tscn`)**: Populate `ContractorItemList` from `ContentCatalog.Airframers` (plus Custom Startup option). Default `RadioTwoStageDefault.ButtonPressed = true` (D6), `RadioStandardFogDefault.ButtonPressed = true` (D7), and `ChkUseFictionalNamesD4.ButtonPressed = false` (D4).
2. **Screen 1 (`ExecutiveDashboardScreen.tscn`)**: Render the 4 quadrant cards (`CardLiquidityRunway`, `CardMacroBudget`, `CardActivePrograms`, `CardActionItems`) and bind `[Jump]` buttons on bottleneck alerts to switch `MainShell` to Screen 4, Screen 5, or Screen 7.

---

## Ticket T25 — Screen 2 (Part A): `DesignBureauScreen` Parametric Controls & Live Preview

- **Depends On**: `T23`
- **Spec References**: `docs/spec/08_ui_ux.md` §1.2.1 (Transient `DraftDesignBuffer` & `<2ms` Stateless Preview Evaluation), §4.2 (`DesignBureauScreen.tscn` Node Hierarchy, Tech-Cap Slider Clamping, `EstimateBadgeList`, Stability & Latent Regime Risk Drawer, `design.create`, `design.modify`, `design.freeze_and_build_prototypes`, `design.create_variant`).
- **Verification**: Headless draft-buffer preview & command dispatch tests in `T25_DesignBureauPresenterTests.cs`.

### 1. Exact C# File Paths, Scene Paths & Type/Method Signatures

- **Godot Scene**: `res://ui/screens/DesignBureauScreen.tscn` (exact node tree in `08_ui_ux.md` §4.2.2).

```csharp
// File: src/MIC.Game/Screens/DesignBureauPresenter.cs
namespace MIC.Game.Screens;
using Godot;
using MIC.Core.Campaign;
using MIC.Core.Contracts;
using MIC.Core.Perf;
using MIC.Core.Tech;
using MIC.Core.Testing;
using MIC.Game.Core;

public sealed partial class DesignBureauPresenter : HBoxContainer, IScreenPresenter
{
    public AircraftDesign DraftBuffer { get; private set; } = default!;
    public FullEvaluationBundle LatestPreviewBundle { get; private set; } = default!;
    public EstimateReport LatestEstimateReport { get; private set; } = default!;
    public bool HasUnsavedDraftChanges { get; private set; }

    public void BindView(Control rootControl);
    public void RefreshFromState(IReadOnlyWorldState state);
    public bool CanNavigateAway();

    public void ClampControlsToTechContext(ITechContext techContext);
    public void OnAnyGeometryParameterChanged(AircraftDesign updatedDraft);
    public SimCommand BuildSaveModifyCommand();
    public SimCommand BuildFreezeAndBuildPrototypesCommand(int prototypeCount = 2);
    public SimCommand BuildCreateVariantCommand(string newVariantName);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T25)
1. **Strictly Non-Mutating `DraftBuffer` (`OnAnyGeometryParameterChanged`)**:
   - Slider drags modify only `DraftBuffer` (converting US display slider values to SI via `Units.SqFtToM2`, `Units.FtToM`, `Units.LbToKg`).
   - Call `PerformanceEvaluator.EvaluateFull(DraftBuffer, selectedEngine, playerTechContext)` and `CostEstimator.EstimateCosts(...)` in $< 2\text{ ms}$, wrap metrics in `Estimate` objects (`source = "sim"` while unfrozen, or from `LineageTestState` if frozen/tested), and update the 10 `EstimateBadgeControl` rows in `RightPerformanceInspector`.
2. **Tech-Cap Clamping (`ClampControlsToTechContext`)**:
   - Read `techContext.GetDouble("aero.wing_sweep_max_deg")`, `techContext.GetDouble("aero.thin_wing_tc_min")`, `techContext.GetDouble("struct.design_load_max_g")`, `techContext.GetDouble("struct.material.ti_max_fraction")`, `techContext.GetBool("aero.area_rule")`, `techContext.GetBool("aero.all_moving_tail")`, `techContext.GetBool("aero.t_tail")`, `techContext.GetBool("aero.inlet_spike")`, and `techContext.GetBool("aero.inlet_variable")`.
   - Clamp slider min/max bounds and disable locked checkboxes with tooltip `"Requires Tech: <localized_tech_name>"`.
3. **Command Dispatch**:
   - `[New Design]` $\to$ `design.create`; `[Save Changes]` $\to$ `design.modify` (disabled with `ERR_DESIGN_FROZEN` tooltip if `DraftBuffer.IsFrozen`); `[Create Variant]` $\to$ `design.clone` / `design.create_variant`; `[Freeze & Build (2)]` $\to$ `design.freeze` + `test.build_prototype`.

---

## Ticket T26 — Screen 2 (Part B): Interactive 2D Vector Engineering Canvases

- **Depends On**: `T25`
- **Spec References**: `docs/spec/08_ui_ux.md` §4.3.1 (`Blueprint3ViewCanvas.cs` — Top/Front/Side Orthographic Quadrants + CG/AC & Static Margin Bar), §4.3.2 (`AirfoilSectionCanvas.cs` — $(x/c, z/c)$ Section + $C_p(x/c)$ vs. $C_{p,\text{crit}}$ Shock Pocket), §4.3.3 (`AreaRuleCanvas.cs` — 64-Station $A(x)$ Component Stack vs. Ideal Sears–Haack Spindle $A_{\text{SH}}(x)$ & $|d^2A/dx^2|$ Hotspots), §4.3.4 (`PsContourCanvas.cs` — $C_{D0}(M)$ Drag Rise, $C_D(C_L)$ Polars, and Boyd $P_s(M, h)$ Iso-Contours).
- **Verification**: Pure-math geometry vertex & contour extraction unit tests in `tests/MIC.Core.Tests/T26_EngineeringCanvasGeometryTests.cs` (**relative tolerance `1e-5`**).

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Game/Canvases/EngineeringPlotCanvas.cs
namespace MIC.Game.Canvases;
using Godot;

public abstract partial class EngineeringPlotCanvas : Control
{
    protected void DrawBlueprintGrid(Rect2 rect, float minorStepPx = 20f, float majorStepPx = 100f);
    protected Vector2 DataToPixel(Rect2 plotRect, double x, double y, double xMin, double xMax, double yMin, double yMax);
}

// File: src/MIC.Game/Canvases/Blueprint3ViewCanvas.cs
namespace MIC.Game.Canvases;
using Godot;
using MIC.Core.Aero;
using MIC.Core.Contracts;
using MIC.Core.Perf;

public sealed partial class Blueprint3ViewCanvas : EngineeringPlotCanvas
{
    public static (Vector2[] FuselageTop, Vector2[] WingRight, Vector2[] HtRight, Vector2[] SideProfile) ComputeOrthographicPolylines(
        AircraftDesign design, DerivedAircraftGeometry geom);

    public void UpdateDesign(AircraftDesign design, FullEvaluationBundle evalBundle);
    public override void _Draw();
}

// File: src/MIC.Game/Canvases/AirfoilSectionCanvas.cs
namespace MIC.Game.Canvases;
using Godot;
using MIC.Core.Aero;

public sealed partial class AirfoilSectionCanvas : EngineeringPlotCanvas
{
    public void UpdateAirfoil(AirfoilMetrics airfoil, double previewMach = 0.82, double previewCl = 0.35);
    public override void _Draw();
}

// File: src/MIC.Game/Canvases/AreaRuleCanvas.cs
namespace MIC.Game.Canvases;
using Godot;
using MIC.Core.Aero;

public sealed partial class AreaRuleCanvas : EngineeringPlotCanvas
{
    public static double ComputeIdealSearsHaackArea(double xOverL, double aMaxM2); // aMax * Math.Pow(4.0 * xOverL * (1.0 - xOverL), 1.5)
    public static bool[] IdentifyCurvatureHotspots(WaveDragSummary summary, double thresholdRatio = 1.25);

    public void UpdateWaveDrag(WaveDragSummary summary, bool isAreaRuled);
    public override void _Draw();
}

// File: src/MIC.Game/Canvases/PsContourCanvas.cs
namespace MIC.Game.Canvases;
using Godot;
using MIC.Core.Contracts;
using MIC.Core.Perf;

public sealed partial class PsContourCanvas : EngineeringPlotCanvas
{
    public enum PlotSubMode { DragPolarAndMachRise, BoydPsContour }
    public PlotSubMode CurrentSubMode { get; set; } = PlotSubMode.BoydPsContour;

    public void UpdatePerformance(FullEvaluationBundle bundle);
    public override void _Draw();
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T26)
1. **Tab A (`Blueprint3ViewCanvas`)**:
   - Auto-scale `pxPerMeter` to fit $\max(\text{SpanM}, \text{LengthM})$ inside the Top/Front/Side quadrants.
   - When `design.Fuselage.AreaRuled == true`, indent the fuselage top/side waist radius by `22%` across the wing root chord stations (`08_ui_ux.md` §4.3.1) so toggling `[x] Whitcomb Area-Ruled Waist` visually pinches the "Coke-bottle" fuselage in real time.
   - Draw $\oplus$ CG (`#E09F3E`), $\triangle$ subsonic AC (`#5DA9E9`), $\triangle$ supersonic AC (`#B388EB`), and the LR Static Margin `% MAC` bar.
2. **Tab B (`AirfoilSectionCanvas`)**:
   - Upper half plots `AirfoilMetrics.XCoords` vs. `YUpper`/`YLower` in `#E8F1F5`. Lower half plots Prandtl–Glauert / Karman–Tsien $C_p(x/c)$ against $C_{p,\text{crit}}(M_\infty)$ and shades supersonic shock pockets in translucent `#E09F3E`.
3. **Tab C (`AreaRuleCanvas`)**:
   - Plot the 64-station `WaveDragSummary` component area stacks ($A_{\text{fus}}, A_{\text{wing}}, A_{\text{tail}}$), the ideal Sears–Haack curve $A_{\text{SH}}(x) = A_{\max}[4(x/L)(1-x/L)]^{3/2}$ (dashed `#5DA9E9`), the actual total $A(x)$ (solid `#E8F1F5`), and shade stations where $|d^2A/dx^2|$ exceeds the Sears–Haack baseline by $> 25\%$ in `#D94A38` Red.
4. **Tab D (`PsContourCanvas`)**:
   - In `DragPolarAndMachRise` mode, plot $C_{D0}(M)$ (`M = 0.2..2.2`) with vertical markers at $M_{\text{crit}}$ and $M_{dd}$, plus $C_D(C_L)$ polars at $M \in \{0.6, 0.9, 1.2, 1.8\}$.
   - In `BoydPsContour` mode, render filled marching-squares iso-contours of `PsGrid` at `0`, `+5,000`, `+15,000`, and `+30,000 ft/min` (`Units.MpsToFpm`), highlighting the bold $P_s = 0$ level-flight envelope, low-speed stall boundary, and $q_{\max}$ thermal/structural limit line.

---

## Ticket T27 — Screen 3 (`PropulsionScreen` + D9 Vendor Modal) & Screen 4 (`TestCenterScreen` + D7/D9)

- **Depends On**: `T23`
- **Spec References**: `docs/spec/08_ui_ux.md` §4.4 (`PropulsionScreen.tscn`, `CustomEngineModal.tscn` with 5 Named US Vendors per Locked Decision **D9**, `EngineCurveCanvas.cs`, `engine.start_project`, `engine.set_engineers`, `engine.cancel_project`, `procurement.request_gfe_bailment`), §4.5 (`TestCenterScreen.tscn`, 10-Driver Bayesian Shrinkage Bars, `UnchartedRegimeBanner` per Locked Decision **D7**, Fictional Test Pilot Dropdown from `pilot_names.json` per **D9**, `test.run_wind_tunnel`, `test.build_prototype`, `test.schedule_flight_test`, `test.fix_flaw`).
- **Verification**: Headless presenter & command payload tests in `T27_PropulsionAndTestCenterPresenterTests.cs`.

### 1. Exact C# File Paths, Scene Paths & Type/Method Signatures

- **Godot Scenes**: `res://ui/screens/PropulsionScreen.tscn`, `res://ui/modals/CustomEngineModal.tscn`, `res://ui/screens/TestCenterScreen.tscn`.

```csharp
// File: src/MIC.Game/Screens/PropulsionPresenter.cs
namespace MIC.Game.Screens;
using System.Collections.Generic;
using Godot;
using MIC.Core.AI;
using MIC.Core.Campaign;
using MIC.Core.Engine;
using MIC.Game.Core;

public sealed partial class PropulsionPresenter : HBoxContainer, IScreenPresenter
{
    public void BindView(Control rootControl);
    public void RefreshFromState(IReadOnlyWorldState state);
    public bool CanNavigateAway() => true;

    public IReadOnlyList<CustomEngineQuote> PreviewVendorQuotes(CustomEngineTargetSpec targetSpec, int currentDay);
    public SimCommand BuildStartEngineProjectCommand(EngineDesignInput spec, string vendorId, int engineersAssigned, string? baseEngineId = null);
    public SimCommand BuildSetEngineersCommand(string projectId, int engineersAssigned);
    public SimCommand BuildCancelProjectCommand(string projectId);
}

// File: src/MIC.Game/Screens/TestCenterPresenter.cs
namespace MIC.Game.Screens;
using System.Collections.Generic;
using Godot;
using MIC.Core.Campaign;
using MIC.Core.Testing;
using MIC.Game.Core;

public sealed partial class TestCenterPresenter : HBoxContainer, IScreenPresenter
{
    public void BindView(Control rootControl);
    public void RefreshFromState(IReadOnlyWorldState state);
    public bool CanNavigateAway() => true;

    public static bool ShouldShowUnchartedRegimeBanner(EstimateReport report, bool flawHindsight); // D7: report.HasUnchartedHighSpeedRegimeRisk && !flawHindsight
    public SimCommand BuildRunWindTunnelCommand(string designId, string facility, string regime);
    public SimCommand BuildBuildPrototypeCommand(string designId, int quantity);
    public SimCommand BuildScheduleFlightTestCommand(string designId, IReadOnlyList<string> syllabus, string thoroughness, string assignedPilotId);
    public SimCommand BuildFixFlawCommand(string designId, string flawId);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T27)
1. **Screen 3 & `CustomEngineModal.tscn` (Locked Decision D9)**:
   - Render radio buttons for all 5 historical US engine vendors (`Pratt & Whitney`, `General Electric`, `Allison`, `Curtiss-Wright`, `Westinghouse`) loaded from `sim/data/companies/engine_makers_us_1945_1960.json`, displaying side-by-side `EngineVendorQuoter.CompareVendorQuotes` thrust, SFC, MTBF, R&D cost share (`60%`), and schedule risk.
   - Plot dry and afterburning thrust $F_n(M, h)$ and TSFC curves at `SL`, `15,000 ft`, and `36,089 ft` on `EngineCurveCanvas.cs`.
2. **Screen 4 (`TestCenterScreen.tscn` — Locked Decisions D7 & D9)**:
   - Left column renders prior vs. posterior $\pm 1\sigma$ bars for the 10 log-space physical drivers (`cd0`, `cdw`, `kind`, `clmax`, `mass`, `thrust`, `tsfc`, `cost_unit`, `cost_dev`, `maint`) and highlights `TRANSONIC CHOKING (M 0.85–1.20)` in `#E09F3E` Amber if a pre-slotted tunnel choked.
   - Center column populates `OptionTestPilotSelect` strictly from `CampaignsAndFlightRunner.LoadFictionalPilotPool()` (`sim/data/testing/pilot_names.json`, **D9**) and maps the 4 UI syllabus phases onto the 6 canonical flight-test items (`low_speed`, `speed_envelope`, `altitude_envelope`, `maneuver`, `high_aoa_spin`, `weapons_stores`).
   - Right column displays `UnchartedRegimeBanner` (`"UNCHARTED HIGH-SPEED REGIME RISKS"`) when `state.FlawHindsight == false` (**D7**) and renders discovered `ActiveFlawState` cards with `[Ground & Apply Fix]`, `[Apply Operational Placard]`, and `[Accept Risk]` actions.

---

## Ticket T28 — Screen 5: `ProcurementScreen`, Pre-Bid Rumors (D10), Fly-Off Tracker (D6) & Debrief Modal (D10)

- **Depends On**: `T23`
- **Spec References**: `docs/spec/08_ui_ux.md` §4.6 (`ProcurementScreen.tscn`, `FlyOffTrackerCard` per Locked Decision **D6**, `RivalIntelCard` Pre-Bid Rumors with Inquiry Tiers `0..2` per **D10**, `SourceSelectionDebriefModal.tscn` per **D10**, `proc.submit_proposal`, `proc.withdraw_proposal`, `proc.lobby_program`).
- **Verification**: Headless presenter & debrief binding tests in `T28_ProcurementPresenterTests.cs`.

### 1. Exact C# File Paths, Scene Paths & Type/Method Signatures

- **Godot Scenes**: `res://ui/screens/ProcurementScreen.tscn`, `res://ui/modals/SourceSelectionDebriefModal.tscn`.

```csharp
// File: src/MIC.Game/Screens/ProcurementPresenter.cs
namespace MIC.Game.Screens;
using System.Collections.Generic;
using Godot;
using MIC.Core.AI;
using MIC.Core.Campaign;
using MIC.Core.Procurement;
using MIC.Game.Core;

public sealed partial class ProcurementPresenter : HBoxContainer, IScreenPresenter
{
    public void BindView(Control rootControl);
    public void RefreshFromState(IReadOnlyWorldState state);
    public bool CanNavigateAway() => true;

    public BidEvaluationResult PreviewPlayerBid(string requirementId, string designId, double bidUnitPriceUsd, IReadOnlyDictionary<string, double>? promisedOverrides = null);
    public SimCommand BuildSubmitProposalCommand(string requirementId, string designId, double bidUnitPriceUsd, IReadOnlyDictionary<string, double>? promisedPerformance = null);
    public SimCommand BuildWithdrawProposalCommand(string requirementId);
    public SimCommand BuildLobbyProgramCommand(string requirementId, double politicalCapitalSpent);
}

// File: src/MIC.Game/Screens/SourceSelectionDebriefModalPresenter.cs
namespace MIC.Game.Screens;
using Godot;
using MIC.Core.Procurement;

public sealed partial class SourceSelectionDebriefModalPresenter : PanelContainer
{
    public void BindOutcomeReport(SelectionOutcomeReport report);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T28)
1. **Live Bid Preview & Confidence % (`PreviewPlayerBid`)**: As the player adjusts `SpinBidPriceUsd` or promised performance sliders, call `ProposalEvaluator.ScoreSingleBid` to display live Credibility $C$, Overclaim Risk $q_i$, and estimated composite score before clicking `[Submit Bid]`.
2. **Pre-Bid Competitor Intelligence Panel (D10)**: Render `CompetitorRumor` cards using `EstimateBadgeControl` (`source = "rumor"`). Clicking `[Gather Deep Intel]` upgrades inquiry level `0 -> 1 -> 2`, narrowing rival error bars (`sigma`).
3. **Two-Stage Fly-Off Tracker (D6) & Post-Award Debrief Modal (D10)**: Display Stage 2 prototype sortie progress for downselected finalists in `FlyOffTrackerCard`, and display the full comparative table (`PerfScore`, `CostScore`, `SchedScore`, `RiskScore`, `PoliticsBonus`, `TotalScore` + `DebriefNarrativeSummary`) in `SourceSelectionDebriefModal.tscn`.

---

## Ticket T29 — Screen 6 (`TechTreeScreen` D7) & Screen 7 (`CompanyManagementScreen`)

- **Depends On**: `T23`
- **Spec References**: `docs/spec/08_ui_ux.md` §4.7 (`TechTreeScreen.tscn` & `TechDagCanvas.cs` — all 82 nodes visible from Day 1 per Locked Decision **D7**, `tech.set_allocation`, `tech.cancel_research`), §4.8 (`CompanyManagementScreen.tscn` & `WrightsLawChartCanvas.cs` — 4 Sub-Tabs: Finance & P&L, Factory & Wright's Law, Engineering Workforce, Facilities & Politics, `econ.*` commands).
- **Verification**: Headless presenter & DAG layout tests in `T29_TechTreeAndCompanyPresenterTests.cs`.

### 1. Exact C# File Paths, Scene Paths & Type/Method Signatures

- **Godot Scenes**: `res://ui/screens/TechTreeScreen.tscn`, `res://ui/screens/CompanyManagementScreen.tscn`.

```csharp
// File: src/MIC.Game/Screens/TechTreePresenter.cs
namespace MIC.Game.Screens;
using Godot;
using MIC.Core.Campaign;
using MIC.Core.Tech;
using MIC.Game.Core;

public sealed partial class TechTreePresenter : HBoxContainer, IScreenPresenter
{
    public void BindView(Control rootControl);
    public void RefreshFromState(IReadOnlyWorldState state);
    public bool CanNavigateAway() => true;

    public SimCommand BuildSetAllocationCommand(string techId, int engineersAssigned);
    public SimCommand BuildCancelResearchCommand(string techId);
}

// File: src/MIC.Game/Screens/CompanyManagementPresenter.cs
namespace MIC.Game.Screens;
using Godot;
using MIC.Core.Campaign;
using MIC.Game.Core;

public sealed partial class CompanyManagementPresenter : VBoxContainer, IScreenPresenter
{
    public void BindView(Control rootControl);
    public void RefreshFromState(IReadOnlyWorldState state);
    public bool CanNavigateAway() => true;

    public SimCommand BuildHireEngineersCommand(string discipline, int count);
    public SimCommand BuildFireEngineersCommand(string discipline, int count);
    public SimCommand BuildUpgradeWindTunnelCommand(int targetLevel);
    public SimCommand BuildExpandFactoryCommand(double additionalFloorM2);
    public SimCommand BuildBuildTestSiteCommand();
    public SimCommand BuildTakeLoanCommand(double principalUsd);
    public SimCommand BuildRepayLoanCommand(double amountUsd);
    public SimCommand BuildSetProductionRateCommand(string contractId, int unitsPerMonth);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T29)
1. **Screen 6 (`TechTreeScreen.tscn` — Locked Decision D7)**: Render all 82 nodes across the 7 horizontal branch lanes (`aero`, `structures`, `propulsion`, `avionics`, `armament`, `manufacturing`, `testing`) and 1945–1960 year columns from Day 1, drawing cubic Bezier prerequisite edges on `TechDagCanvas.cs` and displaying live `AheadOfTimeMultiplier`, `EffectiveEngineers` Brooks's Law curve, NACA diffusion badge, and current maturity $m_i \in [0, 1]$.
2. **Screen 7 (`CompanyManagementScreen.tscn` & `WrightsLawChartCanvas.cs`)**: Plot the cumulative-average and unit flyaway cost curve $C(N)$ across $N \in [1, 500]$ (highlighting any Anderlohr production break setback $\Delta n_{\text{break}}$) and wire all 8 `econ.*` commands.

---

## Ticket T30 — Screen 8 (`CampaignEpilogueModal` D8) & Full 26-Command E2E Integration

- **Depends On**: `T24`, `T26`, `T27`, `T28`, `T29`
- **Spec References**: `docs/spec/08_ui_ux.md` §4.9 (`CampaignEpilogueModal.tscn` — 1960 Executive Legacy Scorecard, Grade Tier `S`..`D`, Industry Leaderboard #1–#9, and `[Continue in Sandbox (Post-1960 Dynamic RFPs)]` button per Locked Decision **D8**), §5 (Complete 26-Command UI Dispatch Coverage Table).
- **Verification**: `tests/MIC.Core.Tests/T30_EndToEndIntegrationTests.cs` — 100% pass across all 26 `PlayerAction` / `SimCommand` types, full 1945–1960 campaign completion (`day == 5843`), epilogue leaderboard generation, and `core.continue_sandbox` continuation into `1961`–`1962`.

### 1. Exact C# File Paths, Scene Paths & Type/Method Signatures

- **Godot Scene**: `res://ui/modals/CampaignEpilogueModal.tscn`.

```csharp
// File: src/MIC.Game/Screens/CampaignEpilogueModalPresenter.cs
namespace MIC.Game.Screens;
using System.Collections.Generic;
using Godot;
using MIC.Core.Campaign;
using MIC.Game.Core;

public sealed partial class CampaignEpilogueModalPresenter : PanelContainer
{
    public void BindScorecard(IReadOnlyWorldState state, IReadOnlyList<CompanyScoreBreakdown> leaderboard);
    public SimCommand BuildContinueSandboxCommand(string playerCompanyId); // Dispatches "core.continue_sandbox" (Decision D8)
    public void ExportCampaignLedgerJson(string targetFilePath);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T30)
1. **1960 Epilogue & Sandbox Continuation (`CampaignEpilogueModalPresenter`)**:
   - When `state.Day >= 5843` (`1960-12-31`) or `state.Ended == true`, pause `CampaignSessionNode` and open `CampaignEpilogueModal.tscn` displaying `ScoringService.ComputeLeaderboardAndScores`.
   - Clicking `BtnContinueSandbox` dispatches `new SimCommand("core.continue_sandbox", state.PlayerCompanyId, new Dictionary<string, object?>())`, locks the official 1945–1960 scorecard, sets `IsEndlessSandbox = true`, closes the modal, and resumes simulation into `1961+` with dynamic procedural RFPs (**Locked Decision D8**).
2. **Full 26-Command E2E Verification (`T30_EndToEndIntegrationTests.cs`)**:
   - Execute a comprehensive automated test that constructs a `CampaignRunner`, dispatches every one of the 26 canonical `PlayerAction` commands (plus all UI aliases in `08_ui_ux.md` §5) through `ActionCatalog.ValidateActionSchema` and `CampaignRunner.SubmitAction`, steps to `day = 5843`, verifies `ScoringService.ComputeLeaderboardAndScores`, invokes `core.continue_sandbox`, and steps 365 post-1960 sandbox days with zero errors, zero warnings, and 100% golden vector parity.
