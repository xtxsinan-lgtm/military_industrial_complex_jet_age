# Validation #5 — "Dumb Agent Test" (`flash_lite` Clean-Room Ticket Execution)

> **Date**: 2026-10-18  
> **Subagent Model Tested**: `flash_lite` (lowest-tier lightweight model)  
> **Target Ticket**: `T01` (`Fnv1a64`, `Pcg32`, `RngStreamRegistry`, `SimDate`, `TickSchedule`, `GameCalendar` in [T01_T05_foundation_and_aero.md](../workplan/T01_T05_foundation_and_aero.md))  
> **Golden Vectors Verified**: `sim/golden/core_rng_pcg32.json`, `sim/golden/core_calendar.json`

---

## 1. Test Protocol (Clean-Room Isolation)

To verify that our specifications (`docs/spec/*.md`) and workplan tickets (`docs/workplan/*.md`) are detailed enough that **even the lowest-end AI model (`flash_lite`) can implement them with zero clarification questions and zero access to the Python reference code**:

1. We invoked a subagent with `Model="flash_lite"`.
2. **Strict Clean-Room Rule**: The `flash_lite` subagent was strictly forbidden from reading `sim/mic/rng.py` or `sim/mic/calendar.py`. It was allowed to read **only**:
   - `docs/workplan/T01_T05_foundation_and_aero.md` (Ticket `T01`)
   - `docs/spec/09_core_loop.md` (§2 Deterministic RNG & §4.1 Calendar)
   - `sim/golden/core_rng_pcg32.json` and `sim/golden/core_calendar.json`
3. The `flash_lite` subagent was tasked with writing:
   - The full C# implementation (`T01_Foundation.cs`) conforming to Ticket `T01`'s namespace, class, record, and method signatures.
   - A standalone clean-room verifier (`verify_t01_cleanroom.py`) implementing the exact mathematical formulas from the spec/ticket and asserting 100% match against the golden vector JSON files.

---

## 2. Quantitative Results

| Subsystem | Test Cases in Golden JSON | Clean-Room `flash_lite` Match Rate | Max Error / Tolerance | Clarification Questions Asked |
| :--- | :---: | :---: | :---: | :---: |
| **`Fnv1a64` Stream Name Hashing** | 8 named streams | **8 / 8 (100%)** | Bit-exact (`0 ulp`) | `0` |
| **`Pcg32` Canonical O'Neill Sequence** | 10 `uint32` draws | **10 / 10 (100%)** | Bit-exact (`0 ulp`) | `0` |
| **`Pcg32` Operations (`u64`, `float`, `bounded`, `uniform`, `randint`, `bernoulli`, `normal`, `choice`, `weighted_choice`, `mtth_prob`)** | All operation vectors | **100% Pass** | Integer bit-exact; float `< 1e-15` | `0` |
| **`RngStreamRegistry` Stream Isolation & Hex Serialization** | Multi-stream state DTOs | **100% Pass** | Bit-exact (`0x` 16-hex) | `0` |
| **`GameCalendar` & `SimDate` (`1945-01-01` to `1961-12-31`)** | Leap years, month/quarter/FY rollovers, `AddMonths` | **100% Pass** | Exact integer match | `0` |

---

## 3. Audit Feedback & Ticket Refinement Applied

The `flash_lite` subagent reported **only one minor observation** across the entire Ticket `T01` specification:
- **Observation**: While `ShuffleInPlace<T>(IList<T> items)` had an exact method signature in `T01`, its inline comment did not repeat the backward Fisher-Yates index loop (`for (int i = items.Count - 1; i > 0; i--) swap(i, (int)NextBounded((uint)(i + 1)))`) from `09_core_loop.md` §2.2.
- **Resolution**: Immediately added the explicit inline backward Fisher-Yates loop comment to `T01_T05_foundation_and_aero.md` line 58.

**Conclusion**: Validation #5 (**Dumb Agent Test**) is **PASSED**.
