"""Generator for Module 09 golden test vectors (`sim/golden/core_*.json`).

Owned by Module 09 (`docs/spec/09_core_loop.md`).
Run via: `PYTHONPATH=sim .venv/bin/python -m mic.campaign.golden_gen`
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from mic.calendar import (
     add_months,
    day_to_iso,
    day_to_ymd,
    fiscal_quarter,
    fiscal_year,
    fiscal_year_bounds,
    get_tick_schedule,
    is_leap_year,
    iso_to_day,
    weekday_name,
    ymd_to_day,
)
from mic.campaign.macro import MacroEnvironment
from mic.campaign.runner import Campaign, HeuristicBotPolicy, NullPolicy, run_campaign
from mic.rng import PCG32, RngStreamRegistry, fnv1a_64, mtth_prob, u64_to_hex


def generate_rng_golden() -> Dict[str, Any]:
    # 1. Canonical O'Neill PCG32 demo seed (initstate=42, initseq=54)
    rng_42_54 = PCG32(42, 54)
    u32_seq = [rng_42_54.next_u32() for _ in range(10)]
    post_u32_state = rng_42_54.to_dict()

    # 2. Uniform float64, u64, bounded, randint, bernoulli, Box-Muller normal
    rng_ops = PCG32(123456789, 987654321)
    u64_seq = [u64_to_hex(rng_ops.next_u64()) for _ in range(4)]
    float_seq = [rng_ops.next_float() for _ in range(6)]
    bounded_seq = [rng_ops.next_bounded(b) for b in (6, 10, 52, 100, 1000, 65536)]
    normal_seq = [rng_ops.normal(0.0, 1.0) for _ in range(6)]
    weighted_items = ["alpha", "beta", "gamma", "delta"]
    weighted_weights = [0.1, 0.2, 0.5, 0.2]
    weighted_picks = [rng_ops.weighted_choice(weighted_items, weighted_weights) for _ in range(10)]
    deck = [0, 1, 2, 3, 4, 5, 6, 7]
    rng_ops.shuffle(deck)

    # 3. FNV-1a 64-bit stream hash vectors
    stream_names = [
        "core.events.mtth",
        "core.events.choice",
        "proc.eval",
        "ai.bidding",
        "testing.flight/dsn_001",
        "econ.market",
    ]
    fnv_vectors = {name: u64_to_hex(fnv1a_64(name)) for name in stream_names}

    # 4. Named stream registry vectors (master_seed = 19450101)
    reg = RngStreamRegistry(19450101)
    stream_draws = {
        name: [reg.stream(name).next_u32() for _ in range(4)]
        for name in ("proc.eval", "core.events.mtth", "ai.bidding")
    }

    # 5. MTTH probability vectors
    mtth_cases = [
        {"mtth_days": 30.0, "dt_days": 30, "prob": mtth_prob(30.0, 30)},
        {"mtth_days": 360.0, "dt_days": 30, "prob": mtth_prob(360.0, 30)},
        {"mtth_days": 720.0, "dt_days": 31, "prob": mtth_prob(720.0, 31)},
        {"mtth_days": 540.0, "dt_days": 28, "prob": mtth_prob(540.0, 28)},
    ]

    return {
        "module": "09_core_loop",
        "suite": "core_rng_pcg32",
        "tolerance_float_rel": 1e-15,
        "pcg32_canonical_seed_42_54": {
            "initstate": 42,
            "initseq": 54,
            "first_10_u32": u32_seq,
            "state_after_10_u32": post_u32_state,
        },
        "rng_operations_seed_123456789_987654321": {
            "initstate": 123456789,
            "initseq": 987654321,
            "u64_hex_4": u64_seq,
            "float_6": float_seq,
            "bounded_6_10_52_100_1000_65536": bounded_seq,
            "box_muller_normal_6": normal_seq,
            "weighted_choice_10": weighted_picks,
            "shuffled_deck_8": deck,
            "final_state": rng_ops.to_dict(),
        },
        "fnv1a_64_vectors": fnv_vectors,
        "stream_registry_master_19450101": stream_draws,
        "mtth_prob_vectors": mtth_cases,
    }


def generate_calendar_golden() -> Dict[str, Any]:
    sample_dates = [
        "1945-01-01",
        "1945-05-08",
        "1945-06-30",
        "1945-07-01",
        "1945-08-15",
        "1947-09-18",
        "1947-10-14",
        "1948-02-28",
        "1948-02-29",
        "1948-03-01",
        "1950-06-25",
        "1950-06-30",
        "1950-07-01",
        "1952-02-29",
        "1953-07-27",
        "1956-02-29",
        "1957-10-04",
        "1960-02-29",
        "1960-06-30",
        "1960-07-01",
        "1960-12-31",
    ]
    date_vectors: List[Dict[str, Any]] = []
    for iso in sample_dates:
        d = iso_to_day(iso)
        y, m, dom = day_to_ymd(d)
        sched = get_tick_schedule(d)
        date_vectors.append(
            {
                "iso": iso,
                "day": d,
                "year": y,
                "month": m,
                "day_of_month": dom,
                "weekday": sched.weekday,
                "weekday_name": weekday_name(d),
                "calendar_quarter": sched.calendar_quarter,
                "fiscal_year": fiscal_year(d),
                "fiscal_quarter": fiscal_quarter(d),
                "is_month_start": sched.is_month_start,
                "is_month_end": sched.is_month_end,
                "is_quarter_start": sched.is_quarter_start,
                "is_year_start": sched.is_year_start,
                "is_fiscal_year_start": sched.is_fiscal_year_start,
                "days_in_current_month": sched.days_in_current_month,
                "days_in_prev_month": sched.days_in_prev_month,
            }
        )

    fy_bounds_vectors = {}
    for fy in range(1945, 1962):
        s_day, e_day = fiscal_year_bounds(fy)
        fy_bounds_vectors[str(fy)] = {
            "start_day": s_day,
            "start_iso": day_to_iso(s_day),
            "end_day": e_day,
            "end_iso": day_to_iso(e_day),
            "length_days": e_day - s_day + 1,
        }

    leap_years = {str(y): is_leap_year(y) for y in (1900, 1944, 1945, 1948, 1950, 1952, 1956, 1960, 2000)}

    add_month_cases = [
        {"base_iso": "1945-01-31", "months": 1, "result_iso": day_to_iso(add_months(iso_to_day("1945-01-31"), 1))},
        {"base_iso": "1948-01-31", "months": 1, "result_iso": day_to_iso(add_months(iso_to_day("1948-01-31"), 1))},
        {"base_iso": "1945-07-01", "months": 12, "result_iso": day_to_iso(add_months(iso_to_day("1945-07-01"), 12))},
    ]

    return {
        "module": "09_core_loop",
        "suite": "core_calendar",
        "date_vectors": date_vectors,
        "fiscal_year_bounds": fy_bounds_vectors,
        "leap_years": leap_years,
        "add_months_vectors": add_month_cases,
    }


def generate_campaign_smoke_golden() -> Dict[str, Any]:
    # 1. Two-year smoke run (1945-01-01 to 1946-12-31) with HeuristicBotPolicy
    res_2y = run_campaign(
        seed=42,
        player_policy=HeuristicBotPolicy(),
        start="1945-01-01",
        end="1946-12-31",
        difficulty="normal",
        company_id="mcdonnell",
    )

    # 2. Full 16-year MVP campaign run (1945-01-01 to 1960-12-31) with HeuristicBotPolicy
    res_full = run_campaign(
        seed=1945,
        player_policy=HeuristicBotPolicy(),
        start="1945-01-01",
        end="1960-12-31",
        difficulty="normal",
        company_id="north_american",
    )

    # 3. Save/load mid-run determinism check (run 1945-01-01..1945-12-31, save/load at 1945-07-01)
    cmp_direct = Campaign.new_game(seed=777, start="1945-01-01", end="1945-12-31")
    pol_a = HeuristicBotPolicy()
    while not cmp_direct.world.ended:
        cmp_direct.step_day(pol_a)

    cmp_split = Campaign.new_game(seed=777, start="1945-01-01", end="1945-12-31")
    pol_b = HeuristicBotPolicy()
    mid_day = iso_to_day("1945-07-01")
    while cmp_split.world.day < mid_day and not cmp_split.world.ended:
        cmp_split.step_day(pol_b)
    env_mid = cmp_split.to_envelope()
    cmp_restored = Campaign.from_envelope(env_mid)
    while not cmp_restored.world.ended:
        cmp_restored.step_day(pol_b)

    assert cmp_direct.state_hash() == cmp_restored.state_hash()

    # 4. Macro budget lookup vectors
    macro = MacroEnvironment()
    budget_vectors = {}
    for fy in (1945, 1947, 1950, 1953, 1958, 1960, 1961):
        b = macro.budget_for_fy(fy)
        budget_vectors[str(fy)] = {
            "dod_total_usd": b.dod_total_usd,
            "aircraft_procurement_total_usd": b.aircraft_procurement_total_usd,
            "aircraft_procurement_usaf_usd": b.aircraft_procurement_usaf_usd,
            "aircraft_procurement_usn_usd": b.aircraft_procurement_usn_usd,
            "aviation_rd_usd": b.aviation_rd_usd,
            "deflator_1950": b.deflator_1950,
        }

    return {
        "module": "09_core_loop",
        "suite": "core_campaign_smoke",
        "note": "Stub-era campaign smoke test vectors; regenerate when domain modules 01..07 replace stubs.",
        "smoke_2y_seed_42": {
            "seed": res_2y.seed,
            "start_day": res_2y.start_day,
            "end_day": res_2y.end_day,
            "days_simulated": res_2y.days_simulated,
            "outcome": res_2y.outcome,
            "state_hash": res_2y.state_hash,
            "events_fired_count": res_2y.events_fired_count,
            "player_score": res_2y.player_score.to_dict(),
        },
        "full_mvp_1945_1960_seed_1945": {
            "seed": res_full.seed,
            "start_day": res_full.start_day,
            "end_day": res_full.end_day,
            "days_simulated": res_full.days_simulated,
            "outcome": res_full.outcome,
            "state_hash": res_full.state_hash,
            "events_fired_count": res_full.events_fired_count,
            "player_score": res_full.player_score.to_dict(),
        },
        "save_load_split_1945_seed_777": {
            "mid_day": mid_day,
            "final_state_hash": cmp_direct.state_hash(),
        },
        "macro_budget_sample": budget_vectors,
    }


def write_all_goldens(golden_dir: Path) -> None:
    golden_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "core_rng_pcg32.json": generate_rng_golden(),
        "core_calendar.json": generate_calendar_golden(),
        "core_campaign_smoke.json": generate_campaign_smoke_golden(),
    }
    for fname, payload in files.items():
        out = golden_dir / fname
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2] / "golden"
    write_all_goldens(root)
