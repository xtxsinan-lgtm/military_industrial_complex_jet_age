"""Tests for the 1945-1960 Integrated Campaign Simulator (`mic.campaign.integrated`) and 4 Bot Archetypes (`mic.campaign.bots`)."""

from __future__ import annotations

from mic.campaign.bots import (
    BalancedPrimeBot,
    ConservativeGoldPlaterBot,
    SpeedDemonSkipTestBot,
    TechPioneerBot,
    create_all_bots,
    get_bot_by_id,
)
from mic.campaign.integrated import IntegratedCampaignSim, run_integrated_campaign


def test_bot_archetypes_instantiation_and_pilots() -> None:
    bots = create_all_bots()
    assert len(bots) == 4
    expected_ids = {
        "balanced_prime",
        "speed_demon_skip_test",
        "conservative_gold_plater",
        "tech_pioneer",
    }
    assert {b.bot_id for b in bots} == expected_ids

    for b in bots:
        assert get_bot_by_id(b.bot_id).name == b.name
        assert get_bot_by_id(b.name).bot_id == b.bot_id
        pilots = b.get_test_pilots()
        assert len(pilots) >= 2
        for p in pilots:
            assert p.skill > 0.0
            assert p.salary_annual_usd > 0.0


def test_integrated_campaign_determinism_and_locked_decision_d6() -> None:
    r1 = run_integrated_campaign(seed=101, bot_id="balanced_prime", force_flyoff=True)
    r2 = run_integrated_campaign(seed=101, bot_id="balanced_prime", force_flyoff=True)

    assert r1.programs_total == 16
    assert r1.bids_submitted == 16
    assert r1.contracts_won == r2.contracts_won
    assert r1.ending_net_worth_1950_usd == r2.ending_net_worth_1950_usd
    assert r1.final_score == r2.final_score
    assert r1.grade_letter == r2.grade_letter
    assert all(po.acquisition_style == "flyoff" for po in r1.program_outcomes)

    r_hist = run_integrated_campaign(seed=101, bot_id="balanced_prime", force_flyoff=False)
    styles = {po.acquisition_style for po in r_hist.program_outcomes}
    assert "flyoff" in styles
    assert len(styles) >= 2


def test_four_bot_behavioral_differentiation() -> None:
    seed = 202
    r_bal = run_integrated_campaign(seed=seed, bot=BalancedPrimeBot(), force_flyoff=True)
    r_rush = run_integrated_campaign(seed=seed, bot=SpeedDemonSkipTestBot(), force_flyoff=True)
    r_gold = run_integrated_campaign(seed=seed, bot=ConservativeGoldPlaterBot(), force_flyoff=True)
    r_tech = run_integrated_campaign(seed=seed, bot=TechPioneerBot(), force_flyoff=True)

    # 1. TechPioneerBot invests most heavily in active R&D and bids selectively
    assert r_tech.active_techs_unlocked > r_bal.active_techs_unlocked
    assert r_bal.active_techs_unlocked > r_gold.active_techs_unlocked
    assert r_gold.active_techs_unlocked > r_rush.active_techs_unlocked
    assert r_tech.bids_submitted < 16
    assert r_bal.bids_submitted == 16

    # 2. SpeedDemonSkipTestBot skips all wind-tunnel campaigns and never fixes flaws
    assert r_rush.decisions_by_category["wind_tunnel_booking"] == 0
    assert r_rush.flaws_fixed == 0

    # 3. ConservativeGoldPlaterBot runs the most thorough wind-tunnel programme and bids highest price
    assert (
        r_gold.decisions_by_category["wind_tunnel_booking"]
        > r_bal.decisions_by_category["wind_tunnel_booking"]
    )
    assert r_gold.program_outcomes[0].unit_price_bid_usd > r_bal.program_outcomes[0].unit_price_bid_usd

    # 4. Player decision pacing audit is populated across 1945-1960
    assert 6.0 <= r_bal.avg_decisions_per_year <= 18.0
    assert sum(r_bal.decisions_by_year.values()) == sum(r_bal.decisions_by_category.values())
    assert r_bal.grade_letter in ("A+", "A", "B", "C", "D", "F")
