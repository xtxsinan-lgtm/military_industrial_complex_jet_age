# Workplan Tickets T01–T05 — Foundation Spine & Aerodynamics/Performance Engine

> **Status**: v1.0 (Ticket-Level Implementation Plan for `MIC.Core` & `MIC.Core.Tests`)
> **Owner Assemblies**: `src/MIC.Core/` (`MIC.Core.Random`, `MIC.Core.Calendar`, `MIC.Core.Contracts`, `MIC.Core.Data`, `MIC.Core.Aero`, `MIC.Core.Perf`)
> **Authoritative Specs**: `docs/spec/00_conventions.md` §§3–4, `docs/spec/09_core_loop.md` §§4.1–4.2 & 5.1–5.2, `docs/spec/01_aero_physics.md` §§4–8
> **Golden Vectors**: `sim/golden/core_rng_pcg32.json`, `sim/golden/core_calendar.json`, `sim/golden/aero_atmosphere_and_airfoil.json`, `sim/golden/perf_historical_reports.json`

---

## Ticket T01 — Deterministic `Pcg32`, `Fnv1a64`, `RngStreamRegistry`, `SimDate` & `GameCalendar`

- **Depends On**: None (Wave A Root Ticket)
- **Spec References**: `docs/spec/09_core_loop.md` §4.1 (`TickSchedule`), §4.2 (RNG Hex Serialization), §5.1 (PCG32 & FNV-1a 64), §5.2 (Proleptic Gregorian & Pre-1976 US Fiscal Year), §8.1–8.2; Python oracle `sim/mic/rng.py` and `sim/mic/calendar.py`.
- **Golden Test Vector Files & Tolerances**:
  - `sim/golden/core_rng_pcg32.json`: Integer & hex string equality **exact (`tol = 0`)**; floating-point operations (`next_float`, `normal`, `mtth_prob`) **relative tolerance `1e-15`**.
  - `sim/golden/core_calendar.json`: **100% exact equality** across all 21 milestone dates (`1945-01-01` to `1960-12-31`, leap days, FY boundaries) and all 17 fiscal year `[start_day, end_day]` spans (`FY1945`–`FY1961`).

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Random/Fnv1a64.cs
namespace MIC.Core.Random;

public static class Fnv1a64
{
    public const ulong OffsetBasis = 0xCBF29CE484222325UL;
    public const ulong Prime = 0x00000100000001B3UL;

    public static ulong HashStreamName(string streamName);
    public static string ToHex(ulong value);      // Returns $"0x{value:x16}"
    public static ulong FromHex(string hexValue); // Parses "0x..." or 16-char hex
}

// File: src/MIC.Core/Random/Pcg32.cs
namespace MIC.Core.Random;
using System.Collections.Generic;

public sealed class Pcg32
{
    public const ulong Multiplier = 6364136223846793005UL;
    public ulong State { get; private set; }
    public ulong Inc { get; private set; }

    public Pcg32(ulong initState = 0x853C49E6748FEA9BUL, ulong initSeq = 0xDA3E39CB94B95BDBUL);
    public static Pcg32 FromRawState(ulong state, ulong inc);
    public void Seed(ulong initState, ulong initSeq);

    public uint NextU32();
    public ulong NextU64();                       // hi = NextU32(), lo = NextU32() -> (hi << 32) | lo
    public double NextFloat();                    // (NextU64() >> 11) * (1.0 / (1UL << 53))
    public uint NextBounded(uint bound);          // Lemire/O'Neill threshold = (0UL - bound) % bound
    public double Uniform(double low, double high);
    public int RandInt(int lowInclusive, int highInclusive);
    public bool Bernoulli(double p);
    public double Normal(double mu = 0.0, double sigma = 1.0); // Stateless Box-Muller cosine branch (4 NextU32 steps)
    public T Choice<T>(IReadOnlyList<T> items);
    public T WeightedChoice<T>(IReadOnlyList<T> items, IReadOnlyList<double> weights);
    public void ShuffleInPlace<T>(IList<T> items); // Backward Fisher-Yates: for (int i = items.Count - 1; i > 0; i--) swap(i, (int)NextBounded((uint)(i + 1)))
    public static double MtthProb(double mtthDays, double dtDays); // 1.0 - Math.Pow(2.0, -dtDays / mtthDays)
    public Pcg32StateDto ToDto();
    public static Pcg32 FromDto(Pcg32StateDto dto);
}

public sealed record Pcg32StateDto(string State, string Inc);

// File: src/MIC.Core/Random/RngStreamRegistry.cs
namespace MIC.Core.Random;
using System.Collections.Generic;

public sealed class RngStreamRegistry
{
    public ulong MasterSeed { get; }
    public RngStreamRegistry(ulong masterSeed);
    public Pcg32 Stream(string name); // Lazy-init: initState = MasterSeed ^ Fnv1a64(name), initSeq = Fnv1a64(name)
    public RngRegistryDto ToDto();    // Serializes streams sorted by Ordinal key
    public static RngStreamRegistry FromDto(RngRegistryDto dto);
}

public sealed record RngRegistryDto(string MasterSeed, IReadOnlyDictionary<string, Pcg32StateDto> Streams);

// File: src/MIC.Core/Calendar/GameCalendar.cs
namespace MIC.Core.Calendar;

public readonly record struct SimDate(int Year, int Month, int DayOfMonth)
{
    public int ToDayIndex() => GameCalendar.YmdToDay(Year, Month, DayOfMonth);
    public static SimDate FromDayIndex(int dayIndex) => GameCalendar.DayToYmd(dayIndex);
    public override string ToString() => $"{Year:D4}-{Month:D2}-{DayOfMonth:D2}";
}

public sealed record TickSchedule(
    int Day, int Year, int Month, int DayOfMonth, string Iso, int Weekday,
    int CalendarQuarter, int FiscalYear, int FiscalQuarter,
    bool IsMonthStart, bool IsMonthEnd, bool IsQuarterStart,
    bool IsFiscalQuarterStart, bool IsYearStart, bool IsFiscalYearStart,
    int DaysInCurrentMonth, int DaysInPrevMonth
);

public static class GameCalendar
{
    public const int CivilOffset19450101 = 710337;
    public const int CampaignStartDay = 0;    // 1945-01-01
    public const int CampaignEndDay = 5843;   // 1960-12-31

    public static bool IsLeapYear(int year);
    public static int DaysInMonth(int year, int month);
    public static int YmdToDay(int year, int month, int day);
    public static SimDate DayToYmd(int dayIndex);
    public static string DayToIso(int dayIndex);
    public static int IsoToDay(string isoDate);
    public static int Weekday(int dayIndex); // Monday = 0 .. Sunday = 6
    public static (int FiscalYear, int FiscalQuarter) GetFiscalYearAndQuarter(int year, int month);
    public static (int StartDay, int EndDay) FiscalYearBounds(int fiscalYear);
    public static int AddMonths(int dayIndex, int months);
    public static TickSchedule GetTickSchedule(int dayIndex);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T01)
1. **Unchecked 64-Bit Arithmetic**: Wrap all `Pcg32` and `Fnv1a64` integer transitions in `unchecked { ... }`. In `NextU32()`, compute `uint xorshifted = (uint)(((oldstate >> 18) ^ oldstate) >> 27); int rot = (int)(oldstate >> 59); return (xorshifted >> rot) | (xorshifted << ((-rot) & 31));`.
2. **Stateless Box-Muller `Normal()`**: Draw `double u1 = Math.Max(NextFloat(), 1.1102230246251565e-16); double u2 = NextFloat(); double z0 = Math.Sqrt(-2.0 * Math.Log(u1)) * Math.Cos(2.0 * Math.PI * u2); return mu + sigma * z0;`. Never cache the `Math.Sin` branch.
3. **Howard Hinnant Civil Date Algorithm**: Implement `DaysFromCivil(y, m, d) - 710337` and `CivilFromDays(dayIndex + 710337)` using integer division rounding toward $-\infty$ for negative eras.
4. **Verification (`tests/MIC.Core.Tests/T01_RngAndCalendarTests.cs`)**: Load `sim/golden/core_rng_pcg32.json` and `sim/golden/core_calendar.json` and assert 100% match across all vectors.

---

## Ticket T02 — Shared Data Contracts (`00_conventions.md` §4) & JSON Data Infrastructure

- **Depends On**: `T01`
- **Spec References**: `docs/spec/00_conventions.md` §§4.1–4.7; `docs/spec/01_aero_physics.md` §4.1; `docs/spec/02_engines.md` §4.2; `docs/spec/04_economy.md` §4.1; `docs/spec/05_procurement.md` §4.1; `docs/spec/06_testing_uncertainty.md` §4.1.
- **Golden Test Vector Files**: Round-trip deserialization & validation of `sim/data/aircraft_hist/*.json`, `sim/data/engines_hist/*.json`, `sim/data/programs/*.json`, `sim/data/economy/*.json`, and `sim/data/tuning/*.json`.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Data/SimDataLocator.cs
namespace MIC.Core.Data;
using System.Text.Json;

public static class SimDataLocator
{
    public static string ResolveDataPath(string relativePathUnderSimData);
    public static string ResolveGoldenPath(string goldenFileName);
    public static T LoadJson<T>(string fullPath);
    public static JsonSerializerOptions DefaultOptions { get; } // SnakeCaseLower, ReadCommentHandling.Skip, NumberHandling.Strict
}

// File: src/MIC.Core/Contracts/Estimate.cs
namespace MIC.Core.Contracts;

public sealed record Estimate(
    double Value,
    double Sigma,
    string Source, // "sim" | "tunnel" | "ground" | "flight" | "service" | "rumor"
    string Unit
);

// File: src/MIC.Core/Contracts/AircraftDesign.cs
namespace MIC.Core.Contracts;
using System.Collections.Generic;

public sealed record WingGeometry(
    double AreaM2, double AspectRatio, double SweepQcDeg, double TaperRatio,
    double TcRoot, double TcTip, string AirfoilRef, string PlanformType,
    string Position, double XLeRootFrac, double DihedralDeg, double IncidenceDeg,
    double TwistDeg, IReadOnlyList<string> Devices
);

public sealed record FuselageGeometry(
    double LengthM, double MaxDiameterM, double NoseFineness, double TailFineness,
    string CanopyType, bool AreaRuled
);

public sealed record EmpennageGeometry(
    bool Tailless, bool TTail, bool AllMovingTail,
    double HtAreaM2, double HtAspectRatio, double HtSweepQcDeg,
    double VtAreaM2, double VtAspectRatio, double VtSweepQcDeg
);

public sealed record IntakeSpec(string Type, string Compression, bool Variable, bool Spike);
public sealed record PropulsionInstallSpec(string EngineId, int Count, bool Afterburner, double XCgFrac = 0.58);
public sealed record MaterialMix(double Al, double Steel, double Ti);
public sealed record StructureSpec(double DesignLoadFactorG, MaterialMix MaterialMix, bool CarrierCapable);
public sealed record FuelSpec(double InternalKg, int DropTanksCount = 0, double DropTankFuelKgEach = 0.0, bool CombatUsesDropTanks = false);
public sealed record SystemsSpec(
    string? RadarId, string? FireControlId, int AvionicsLevel,
    bool PoweredControls = true, bool StabilityAugmentation = false,
    bool EjectionSeat = true, bool InflightRefuel = false, bool PressurizedCockpit = true
);
public sealed record GunLoadoutItem(string GunId, int Count, int RoundsPerGun);
public sealed record ArmamentSpec(IReadOnlyList<GunLoadoutItem> Guns, int Hardpoints, bool InternalBay, IReadOnlyList<string> MissileIds);

public sealed record AircraftDesign(
    string Id, string Name, string CompanyId, string CreatedDate, int CrewCount,
    IReadOnlyList<string> RoleTags, WingGeometry Wing, FuselageGeometry Fuselage,
    EmpennageGeometry Empennage, IntakeSpec Intake, PropulsionInstallSpec Propulsion,
    StructureSpec Structure, FuelSpec Fuel, SystemsSpec Systems, ArmamentSpec Armament,
    IReadOnlyList<string> TechsUsed, bool IsFrozen = false
);

// File: src/MIC.Core/Contracts/EngineSpec.cs
namespace MIC.Core.Contracts;

public interface IEngineSpec
{
    string EngineId { get; }
    string Name { get; }
    double MassKg { get; }
    double DiameterM { get; }
    double LengthM { get; }
    double UnitCost { get; }
    double MtbfH { get; }
    double MaintMhPerFh { get; }
    bool HasAfterburner { get; }

    double ThrustN(double mach, double altM, double throttle = 1.0, bool ab = false);
    double Tsfc(double mach, double altM, double throttle = 1.0, bool ab = false);
    double FuelFlowKgps(double mach, double altM, double throttle = 1.0, bool ab = false);
}

// File: src/MIC.Core/Contracts/PerformanceReport.cs
namespace MIC.Core.Contracts;
using System.Collections.Generic;

public sealed record PsGridData(IReadOnlyList<double> Mach, IReadOnlyList<double> AltM, IReadOnlyList<IReadOnlyList<double>> PsMps);
public sealed record CarrierSuitabilityResult(bool Suitable, IReadOnlyList<string> Reasons);

public sealed record PerformanceReport(
    double MaxMachSl, double MaxMachAlt, double AltOfMaxMachM, double ServiceCeilingM,
    double ClimbRateSlMps, double TimeToAlt10668mS,
    double SustainedTurnDpsM08_4572m, double InstantaneousTurnDpsM08_4572m,
    double PsMpsM09_4572m_1g, double CombatRadiusM, double FerryRangeM,
    double TakeoffDistanceM, double LandingDistanceM, double StallSpeedMps,
    double MaxLoadFactorG, double EmptyMassKg, double MtowKg, double InternalFuelKg,
    double PayloadKg, double ThrustToWeightCombat, double WingLoadingCombatKgm2,
    PsGridData PsGrid, double UnitFlyawayCostUsd, double DevCostUsdEstimate,
    double MaintMhPerFh, CarrierSuitabilityResult CarrierSuitability
)
{
    public double GetScalarMetric(string key);
}
```
*(In `src/MIC.Core/Contracts/Requirement.cs`, `CompanyState.cs`, and `HiddenFlaw.cs`, define the exact records matching `00_conventions.md` §§4.5–4.7 and `tests/MIC.Core.Tests/GoldenAssert.cs` with `AssertDoubleEqual(expected, actual, relTol = 1e-6, absTol = 1e-9)`.)*

---

## Ticket T03 — ISA 1976 Atmosphere & Parametric 2D Airfoil Solver

- **Depends On**: `T02`
- **Spec References**: `docs/spec/01_aero_physics.md` §5.1 (ISA 1976 Atmosphere), §5.2 (2D Airfoil Analysis — NACA 4/5/6/6A, Biconvex, 8-Parameter Kulfan CST); Python oracle `sim/mic/atmosphere.py` and `sim/mic/aero/airfoil.py`.
- **Golden Test Vector File & Tolerance**: `sim/golden/aero_atmosphere_and_airfoil.json` — **relative tolerance `1e-6`** across all 8 altitude vectors (`0 m` to `24,000 m`) and all 2D airfoil section vectors (`0010`, `2412`, `23012`, `64-009`, `64A007`, `65-006`, `biconvex_00336`, CST).

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Aero/IsaAtmosphere.cs
namespace MIC.Core.Aero;

public readonly record struct AtmosphereState(
    double AltM, double TK, double PPa, double RhoKgm3, double AMps,
    double MuPas, double NuM2ps, double Theta, double Delta, double Sigma
);

public static class IsaAtmosphere
{
    public const double G0Mps2 = 9.80665;
    public const double RAirJKgK = 287.05287;
    public const double GammaAir = 1.4;
    public const double T0SlK = 288.15;
    public const double P0SlPa = 101325.0;
    public const double Rho0SlKgm3 = P0SlPa / (RAirJKgK * T0SlK); // 1.225000018124288
    public const double H1TropopauseM = 11000.0;
    public const double H2StratoM = 20000.0;
    public const double H3MaxM = 32000.0;
    public const double LapseTropoKPerM = -0.0065;
    public const double LapseStrato2KPerM = 0.0010;
    public const double SutherlandMuRefPas = 1.716e-5;
    public const double SutherlandTRefK = 273.15;
    public const double SutherlandSK = 110.4;

    public static double TemperatureK(double altM);
    public static double PressurePa(double altM);
    public static double DensityKgm3(double altM);
    public static double SpeedOfSoundMps(double altM);
    public static double DynamicViscosityPas(double altM);
    public static double AdiabaticRecoveryTempK(double altM, double mach, double recoveryFactor = 0.89);
    public static AtmosphereState Evaluate(double altM);
}

// File: src/MIC.Core/Aero/AirfoilSolver.cs
namespace MIC.Core.Aero;
using System.Collections.Generic;

public sealed record AirfoilMetrics(
    string Spec, string Family, double TcRatio, double XTmax, double MaxCamber,
    double XMaxCamber, double RLeOverC, double AlphaZeroLiftRad, double ClAlphaRad,
    double ClMaxLowSpeed, double Cm0, double KornKappaA, double MDd0,
    IReadOnlyList<double> XCoords, IReadOnlyList<double> YUpper, IReadOnlyList<double> YLower
);

public static class AirfoilSolver
{
    public static AirfoilMetrics Analyze(string airfoilSpec, double? tcOverride = null);
    public static AirfoilMetrics AnalyzeCst(
        IReadOnlyList<double> upperWeights, IReadOnlyList<double> lowerWeights, string name = "cst_custom");
    public static (double[] UpperWeights, double[] LowerWeights) FitSplineToCst8(
        IReadOnlyList<(double X, double Y)> upperPoints, IReadOnlyList<(double X, double Y)> lowerPoints);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T03)
1. **ISA 3-Layer Pressure Equations**: Clamp `altM` to `[-500.0, 32000.0]`. For `h <= 11000`, `p = P0 * Math.Pow(T / T0, -G0 / (R * L1))`. For `11000 < h <= 20000`, `p = P1 * Math.Exp(-G0 * (h - 11000.0) / (R * T1))`. For `h > 20000`, `p = P2 * Math.Pow(T / T1, -G0 / (R * L3))`.
2. **Sutherland Dynamic Viscosity**: `mu = SutherlandMuRefPas * Math.Pow(T / SutherlandTRefK, 1.5) * ((SutherlandTRefK + SutherlandSK) / (T + SutherlandSK))`.
3. **2D Airfoil Grid & Metrics**: Discretize chord on `N = 121` cosine-spaced points `x_i = 0.5 * (1.0 - Math.Cos(Math.PI * i / 120.0))` exactly as in `sim/mic/aero/airfoil.py`. Compute `TcRatio`, `XTmax`, `MaxCamber`, `ClAlphaRad`, `ClMaxLowSpeed`, `KornKappaA`, and `MDd0` using the exact formulas in `sim/mic/aero/airfoil.py`.
4. **Verification (`tests/MIC.Core.Tests/T03_AtmosphereAndAirfoilTests.cs`)**: Assert `aero_atmosphere_and_airfoil.json` matches within `rel_tol = 1e-6`.

---

## Ticket T04 — 16-Panel Weissinger VLM, Sears–Haack Wave Drag $A(x)$ & Transonic Drag Rise

- **Depends On**: `T03`, `T08`
- **Spec References**: `docs/spec/01_aero_physics.md` §5.3 (3D Wing VLM & Compressibility), §5.4 (Component Drag Buildup, Sears–Haack 64-station $A(x)$ Wave Drag & Whitcomb Area Rule); Python oracle `sim/mic/aero/geometry.py`, `sim/mic/aero/vlm.py`, and `sim/mic/aero/drag.py`.
- **Golden Test Vector File & Tolerance**: `sim/golden/perf_historical_reports.json` (aero intermediate values & wave drag efficiency `E_WD` for `yf102_pre_area_rule` vs `f102a_delta_dagger`) — **relative tolerance `1e-6`**.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Aero/DerivedGeometry.cs
namespace MIC.Core.Aero;
using MIC.Core.Contracts;

public sealed record DerivedAircraftGeometry(
    double SpanM, double RootChordM, double TipChordM, double MacM, double YMacM,
    double XLeMacM, double SweepLeDeg, double SweepHalfDeg, double TcMean,
    double WettedAreaWingM2, double WettedAreaFuselageM2, double WettedAreaTailM2,
    double TotalWettedAreaM2, double MaxCrossSectionAreaM2
);

public static class GeometryDeriver
{
    public static DerivedAircraftGeometry Derive(AircraftDesign design, IEngineSpec? engine = null);
}

// File: src/MIC.Core/Aero/WingVlmSolver.cs
namespace MIC.Core.Aero;
using MIC.Core.Contracts;
using MIC.Core.Tech;

public sealed record WingAeroCharacteristics(
    double ClAlphaSubsonicRad, double OswaldEfficiencyInv, double DownwashDepsilonDalpha,
    double XAcSubsonicMacFrac, double XAcSupersonicMacFrac, double KpPolhamus, double KvPolhamus
);

public static class WingVlmSolver
{
    public const int SpanwisePanels = 16;

    public static WingAeroCharacteristics SolveSubsonicVlm(AircraftDesign design, DerivedAircraftGeometry geom);
    public static double ComputeClAlphaAtMach(
        AircraftDesign design, DerivedAircraftGeometry geom, WingAeroCharacteristics vlm, double mach);
    public static double ComputeClMaxAtMach(
        AircraftDesign design, DerivedAircraftGeometry geom, AirfoilMetrics airfoil,
        ITechContext techContext, double mach, bool landingConfig = false);
}

// File: src/MIC.Core/Aero/WaveDragSolver.cs
namespace MIC.Core.Aero;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Tech;

public sealed record WaveDragSummary(
    IReadOnlyList<double> XStationsM,
    IReadOnlyList<double> AreaFuselageM2,
    IReadOnlyList<double> AreaWingM2,
    IReadOnlyList<double> AreaTailM2,
    IReadOnlyList<double> AreaTotalM2,
    IReadOnlyList<double> AreaIdealSearsHaackM2,
    double AMaxM2, double DqSearsHaackM2, double EwdFactor, double CdWavePeak
);

public static class WaveDragSolver
{
    public const int AxialStations = 64;
    public static WaveDragSummary ComputeWaveDragSummary(
        AircraftDesign design, DerivedAircraftGeometry geom, IEngineSpec engine, ITechContext techContext);
}

// File: src/MIC.Core/Aero/DragBuildupSolver.cs
namespace MIC.Core.Aero;
using MIC.Core.Contracts;
using MIC.Core.Tech;

public sealed record DragPolarPoint(
    double Mach, double AltM, double Cl, double Cd0Sub, double CdWave,
    double KInduced, double CdInduced, double CdTotal, double LOverD
);

public static class DragBuildupSolver
{
    public static (double MCrit, double MDd) ComputeCriticalAndDivergenceMach(
        AircraftDesign design, DerivedAircraftGeometry geom, AirfoilMetrics airfoil, double cl);
    public static DragPolarPoint EvaluateDrag(
        AircraftDesign design, DerivedAircraftGeometry geom, AirfoilMetrics airfoil,
        WingAeroCharacteristics vlm, WaveDragSummary waveSummary,
        IEngineSpec engine, ITechContext techContext, double mach, double altM, double cl);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T04)
1. **16-Panel Weissinger Solver (`WingVlmSolver`)**: Solve the $16 \times 16$ linear system $[A]\{\Gamma\} = \{1\}$ via Gaussian elimination with partial pivoting (`double[,]`). Extract spanwise circulation, `OswaldEfficiencyInv`, `DownwashDepsilonDalpha`, and `XAcSubsonicMacFrac`.
2. **Compressibility Regimes**: Implement the exact Helmbold–Diederich swept equation for $M \le 0.95$, supersonic Ackeret + subsonic-LE cone factor for $M \ge 1.15$, and the $C^1$ cubic Hermite bridge on $0.95 < M < 1.15$ (`sim/mic/aero/vlm.py`).
3. **64-Station Sears–Haack & Area Rule (`WaveDragSolver`)**: Compute $A(x)$ across 64 uniform stations $x \in [0, L]$, evaluate the discrete second-derivative roughness integral $\int (A''(x))^2 dx$, apply the Whitcomb waisting gain (`area_rule_waisting_gain * techContext.GetDouble("aero.wave_drag_area_rule_eff")`) when `design.Fuselage.AreaRuled == true`, and compute `EwdFactor` and `CdWavePeak` (`sim/mic/aero/drag.py`).
4. **Lock 4th-Power Transonic Rise & Supersonic Decay**: Match `sim/mic/aero/drag.py` across subsonic, transonic ($M_{\text{crit}} \to M_{dd} \to 1.05$), and supersonic Mach numbers.

---

## Ticket T05 — Structural Mass Breakdown, Mission Integration & `PerformanceEvaluator.Evaluate`

- **Depends On**: `T04`, `T06`, `T11`
- **Spec References**: `docs/spec/01_aero_physics.md` §4.2 (Design Validation), §5.5 (Statistical Component Mass Breakdown), §5.6 (`aero_diagnostics` Dictionary), §6 (Tunables `sim/data/tuning/aero.json`), §7 (Edge Cases), §8 (Golden Vectors); Python oracle `sim/mic/aero/mass.py`, `sim/mic/aero/diagnostics.py`, `sim/mic/perf/performance.py`, `sim/mic/perf/mission.py`.
- **Golden Test Vector File & Tolerance**: `sim/golden/perf_historical_reports.json` — **relative tolerance `1e-6`** across all 4 benchmark aircraft (`f86f_sabre`, `yf102_pre_area_rule`, `f102a_delta_dagger`, `f104a_starfighter`) including all 26 `PerformanceReport` fields, `ps_grid` ($13 \times 10$), `mass_breakdown`, and all 39 `aero_diagnostics` keys.

### 1. Exact C# File Paths & Type/Method Signatures

```csharp
// File: src/MIC.Core/Aero/MassBreakdownSolver.cs
namespace MIC.Core.Aero;
using MIC.Core.Contracts;
using MIC.Core.Tech;

public sealed record MassBreakdown(
    double WingKg, double FuselageKg, double TailKg, double LandingGearKg,
    double PropulsionGroupKg, double FlightControlsHydraulicsKg,
    double AvionicsAndRadarKg, double ElectricalPneumaticEnvKg,
    double FurnishingsAndEjectionKg, double ArmamentFixedDryKg,
    double EmptyMassKg, double InternalFuelKg, double DropTankFuelKg,
    double PayloadKg, double CombatMassKg, double MtowKg,
    double MaxInternalFuelCapacityKg, double FuelVolumeMarginRatio
);

public static class MassBreakdownSolver
{
    public const int FixedPointIterations = 6;
    public static MassBreakdown ComputeMassBreakdown(
        AircraftDesign design, DerivedAircraftGeometry geom, IEngineSpec engine, ITechContext techContext);
}

// File: src/MIC.Core/Aero/AeroDiagnosticsCalculator.cs
namespace MIC.Core.Aero;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Tech;

public static class AeroDiagnosticsCalculator
{
    public static IReadOnlyDictionary<string, double> ComputeAeroDiagnostics(
        AircraftDesign design, DerivedAircraftGeometry geom, AirfoilMetrics airfoil,
        WingAeroCharacteristics vlm, WaveDragSummary waveSummary, MassBreakdown mass,
        IEngineSpec engine, ITechContext techContext, double maxMachAlt, double altOfMaxMachM);
}

// File: src/MIC.Core/Aero/DesignValidator.cs
namespace MIC.Core.Aero;
using System.Collections.Generic;
using MIC.Core.Contracts;
using MIC.Core.Tech;

public sealed record DesignValidationReport(
    bool IsValid,
    IReadOnlyList<string> Errors,   // e.g. "TECH_CAP:aero.wing_sweep_max_deg", "PACKAGING:FUEL_EXCEEDS_VOLUME"
    IReadOnlyList<string> Warnings
);

public static class DesignValidator
{
    public static DesignValidationReport ValidateDesign(
        AircraftDesign design, DerivedAircraftGeometry geom, MassBreakdown mass,
        IEngineSpec engine, ITechContext techContext);
}

// File: src/MIC.Core/Perf/PerformanceEvaluator.cs
namespace MIC.Core.Perf;
using System.Collections.Generic;
using MIC.Core.Aero;
using MIC.Core.Contracts;
using MIC.Core.Tech;

public sealed record FullEvaluationBundle(
    PerformanceReport Report,
    MassBreakdown MassBreakdown,
    WaveDragSummary WaveDragSummary,
    DesignValidationReport Validation,
    IReadOnlyDictionary<string, double> AeroDiagnostics
);

public static class PerformanceEvaluator
{
    public static readonly double[] PsMachGrid = [0.3, 0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2];
    public static readonly double[] PsAltMGrid = [0.0, 2000.0, 4000.0, 6000.0, 8000.0, 10000.0, 12000.0, 14000.0, 16000.0, 18000.0];

    public static PerformanceReport Evaluate(
        AircraftDesign design, IEngineSpec? engine = null, ITechContext? techContext = null);

    public static FullEvaluationBundle EvaluateFull(
        AircraftDesign design, IEngineSpec? engine = null, ITechContext? techContext = null);
}
```

### 2. Step-by-Step Implementation Checklist & Acceptance Criteria (T05)
1. **6-Step Fixed-Point Mass Iteration (`MassBreakdownSolver`)**:
   - Initialize `wDgKg` from empty weight proxy + internal fuel + payload (`sim/mic/aero/mass.py`).
   - Run 6 iterations computing Raymer Ch. 15 fighter component masses (`WingKg`, `FuselageKg`, `TailKg`, `LandingGearKg`, `PropulsionGroupKg`, `FlightControlsHydraulicsKg`, `AvionicsAndRadarKg`, `ElectricalPneumaticEnvKg`, `FurnishingsAndEjectionKg`, `ArmamentFixedDryKg`).
   - Apply material mix multiplier `1.00 * Al + 1.14 * Steel + 0.86 * Ti`, `struct.weight_factor`, `struct.carrier_weight_factor`, and high-AR swept-wing torsion penalty when `AR * tan(SweepQc) > 2.2`.
   - Compute geometric wing-box + fuselage fuel volume capacity `MaxInternalFuelCapacityKg` and `CombatMassKg = EmptyMassKg + 0.50 * InternalFuelKg + PayloadKg`.
2. **Continuous Level-Flight Speed Solver (`_SolveMaxMachAtAlt`)**:
   - Scan upward continuously from `M = 0.55` in `0.02` Mach steps and refine the root where `T_installed(M, h) - D(M, h, n=1) == 0` via 28-step bisection, stopping at the **first** crossing where `T - D < 0` so underpowered transonic designs (`yf102_pre_area_rule`) cannot jump across the transonic drag wall (`01_aero_physics.md` §7.1).
   - Enforce dynamic pressure limit $q_{\max}$ and skin adiabatic recovery temperature limit `struct.max_skin_temp_K`.
3. **Boyd $P_s$ Grid ($13 \times 10$), Turn Rates & Rutowski Climb**:
   - Evaluate $P_s = V (T - D) / W_{\text{combat}}$ across `PsAltMGrid` (10 rows) $\times$ `PsMachGrid` (13 columns), clamping floor to `-250.0 m/s` and rounding grid cells to 2 decimal places (`Math.Round(val, 2)`) if matching serialized `ps_grid.ps_mps` in `perf_historical_reports.json`.
   - Compute `SustainedTurnDpsM08_4572m` and `InstantaneousTurnDpsM08_4572m` at $M = 0.8, h = 4572\text{ m}$ (`15,000 ft`).
   - Integrate `ServiceCeilingM` ($P_s = 0.508\text{ m/s} = 100\text{ ft/min}$) and `TimeToAlt10668mS` (`35,000 ft`).
4. **Multi-Segment Breguet Mission Integrator (`CombatRadiusM`, `FerryRangeM`)**:
   - Implement MIL-C-5011A fuel fractions (5% warmup/takeoff, climb to best cruise altitude, subsonic cruise out/back at optimal $(M/c_T)(L/D)$ with `mission.cruise_part_throttle_sfc_penalty = 1.28`, combat fuel allowance, and 20-minute loiter reserve).
5. **Takeoff, Landing & Carrier Suitability**:
   - Compute `StallSpeedMps`, `TakeoffDistanceM`, `LandingDistanceM`, and `CarrierSuitabilityResult` (`Suitable` bool + failure reason codes when `carrier_capable == false`, approach speed exceeds arrestor limit, or catapult wind-over-deck limit is exceeded).
6. **Verification (`tests/MIC.Core.Tests/T05_PerformanceHistoricalTests.cs`)**:
   - Load `sim/golden/perf_historical_reports.json` and assert every scalar metric, `ps_grid` cell, `mass_breakdown` component, and `aero_diagnostics` entry for `f86f_sabre`, `yf102_pre_area_rule`, `f102a_delta_dagger`, and `f104a_starfighter` matches within `rel_tol = 1e-6`.
   - Run a 500-random-design fuzz test seeded with `Pcg32(1945)` asserting `0` `NaN`/`Infinity` values across all outputs.
