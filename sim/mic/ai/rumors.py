"""Pre-Bid Competitor Intelligence & Trade-Press Rumors (`sim/mic/ai/rumors.py`).

Implements Locked Decision D10 (Module 07):
- Before `proposal_due`, generates trade-press rumors (`CompetitorRumor` dicts) for AI rivals
  preparing bids on an active `Requirement` (`ProgramSpec` or RFP dict).
- Supports 3 intelligence inquiry tiers (`inquiry_level` in `{0, 1, 2}`):
  * Level 0: Standard Trade Press (*Aviation Week* / *Aero Digest* column) — free, wide error bars
    (`11%` Mach, `18%` combat radius, `20%` unit price), occasional false leads or missed stealth bids.
  * Level 1: Washington Liaison Inquiry (`$25k` + `2 PC`) — tighter error bars (`6.5%` Mach, `11%`
    radius, `12%` price) and configuration/powerplant hints.
  * Level 2: Deep Technical Intelligence (`$85k` + `6 PC`) — high-precision pre-bid estimates
    (`4.0%` Mach, `7%` radius, `8%` price) and zero participation false positives/negatives.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from ..procurement.models import Estimate, ProgramSpec, ProposalBid
from ..testing.hashing import keyed_normal, keyed_u01
from .bidding_ai import AICompetitorEntry
from .tuning import get_company_signature, load_ai_tuning


class CompetitorRumor(dict):
    """Dictionary representing a pre-bid competitor rumor (D10) with attribute access."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def to_dict(self) -> Dict[str, Any]:
        return dict(self)


def get_inquiry_cost(
    inquiry_level: int = 0,
    tuning: Optional[Dict[str, Any]] = None,
) -> Dict[str, float]:
    """Return `{"cost_usd": float, "political_capital": float}` for `inquiry_level` (0, 1, or 2)."""
    lvl = max(0, min(2, int(inquiry_level)))
    t = (tuning if tuning is not None else load_ai_tuning())["rumors"]
    return {
        "inquiry_level": lvl,
        "cost_usd": float(t["inquiry_costs_usd"][str(lvl)]),
        "political_capital": float(t["inquiry_pc_costs"][str(lvl)]),
    }


def _draw_normal(rng: Any, seed_tag: str, idx: int, metric: str) -> float:
    if rng is not None and hasattr(rng, "normal") and callable(rng.normal):
        return float(rng.normal(0.0, 1.0))
    return float(keyed_normal(19450101, "rumor_norm", seed_tag, idx, metric))


def _draw_u01(rng: Any, seed_tag: str, idx: int, metric: str) -> float:
    if rng is not None and hasattr(rng, "uniform") and callable(rng.uniform):
        return float(rng.uniform(0.0, 1.0))
    if rng is not None and hasattr(rng, "next_float01") and callable(rng.next_float01):
        return float(rng.next_float01())
    return float(keyed_u01(19450101, "rumor_u01", seed_tag, idx, metric))


def _extract_entry_truth(
    entry: Any,
    rfp_info: Mapping[str, Any],
) -> Tuple[str, str, str, float, float, float, str, str]:
    """Extract `(company_id, company_name, design_name, mach, radius_m, price_usd, config_hint, eng_hint)`."""
    if isinstance(entry, AICompetitorEntry):
        cid = entry.company_id
        cname = entry.company_name
        dname = entry.design_name
        mach = float(entry.true_performance.get("max_mach_alt", entry.nominal_report.max_mach_alt))
        rad = float(entry.true_performance.get("combat_radius_m", entry.nominal_report.combat_radius_m))
        price = float(entry.bid.unit_price_bid_usd)
        pf = str(entry.design.get("wing", {}).get("planform_type", "swept"))
        ecount = int(entry.design.get("propulsion", {}).get("count", 1))
        eid = str(entry.design.get("propulsion", {}).get("engine_id", "J47-GE-27"))
        ab = bool(entry.design.get("propulsion", {}).get("afterburner", False))
    elif isinstance(entry, ProposalBid):
        cid = entry.company_id
        cname = entry.company_id.replace("_", " ").title()
        dname = entry.design_name
        mach = float(entry.estimates.get("max_mach_alt", Estimate(1.15)).value if "max_mach_alt" in entry.estimates else entry.promised.get("max_mach_alt", 1.15))
        rad = float(entry.estimates.get("combat_radius_m", Estimate(650000.0)).value if "combat_radius_m" in entry.estimates else entry.promised.get("combat_radius_m", 650000.0))
        price = float(entry.unit_price_bid_usd)
        sig = get_company_signature(cid)
        pf = "delta" if float(sig.get("delta_bias", 0.0)) >= 0.7 else "swept"
        ecount = int(entry.equipment.engines)
        eid = "turbojet"
        ab = mach >= 1.05
    elif isinstance(entry, Mapping):
        cid = str(entry.get("company_id", entry.get("id", "lockheed")))
        cname = str(entry.get("company_name", cid.replace("_", " ").title()))
        dname = str(entry.get("design_name", entry.get("name", f"{cid.upper()} Proposal")))
        perf = entry.get("true_performance", entry.get("performance_summary", entry.get("anchor_performance", entry)))
        mach = float(perf.get("max_mach_alt", entry.get("max_mach_alt", rfp_info["target_mach"])))
        rad = float(perf.get("combat_radius_m", entry.get("combat_radius_m", rfp_info["target_radius_m"])))
        price = float(entry.get("unit_price_bid_usd", perf.get("unit_flyaway_cost_usd", rfp_info["ceiling_usd"] * 0.92)))
        sig = get_company_signature(cid)
        pf = str(entry.get("wing", {}).get("planform_type", "delta" if float(sig.get("delta_bias", 0.0)) >= 0.7 else "swept"))
        ecount = int(entry.get("propulsion", {}).get("count", 2 if float(sig.get("twin_engine_bias", 0.2)) >= 0.7 else 1))
        eid = str(entry.get("propulsion", {}).get("engine_id", "axial turbojet"))
        ab = bool(entry.get("propulsion", {}).get("afterburner", mach >= 1.05))
    else:
        raise TypeError(f"Unsupported AI entry type for rumor generation: {type(entry)}")

    config_hint = f"{pf}-wing {'twin-jet' if ecount >= 2 else 'single-jet'}"
    eng_hint = f"{eid} ({'afterburning' if ab else 'dry'})"
    return cid, cname, dname, mach, rad, price, config_hint, eng_hint


def generate_pre_bid_rumors(
    rfp: Union[ProgramSpec, Mapping[str, Any]],
    ai_entries: Sequence[Any],
    inquiry_level: int = 0,
    rng: Any = None,
    tuning: Optional[Dict[str, Any]] = None,
) -> List[CompetitorRumor]:
    """Generate pre-bid `CompetitorRumor` dicts for `ai_entries` on `rfp` (Locked Decision D10).

    Each returned `CompetitorRumor` contains `Estimate` dicts (`source="rumor"`) for:
    - `max_mach_alt` (`unit="mach"`)
    - `combat_radius_m` (`unit="m"`)
    - `unit_flyaway_price_usd` (`unit="usd"`)
    """
    t_all = tuning if tuning is not None else load_ai_tuning()
    t_rum = t_all["rumors"]
    lvl = max(0, min(2, int(inquiry_level)))
    lvl_key = str(lvl)

    sig_mults = t_rum["sigma_multipliers_by_level"][lvl_key]
    part_cfg = t_rum["participation_noise_by_level"][lvl_key]
    cost_info = get_inquiry_cost(lvl, tuning=t_all)

    if isinstance(rfp, ProgramSpec):
        rfp_id = rfp.id
        prog_name = rfp.program_name
        ceil_usd = float(rfp.budget.unit_price_ceiling_usd)
    else:
        rfp_id = str(rfp.get("id", "rfp_custom"))
        prog_name = str(rfp.get("program_name", rfp_id))
        ceil_usd = float(rfp.get("budget", {}).get("unit_price_ceiling_usd", 850000.0))

    rfp_info = {"id": rfp_id, "target_mach": 1.25, "target_radius_m": 650000.0, "ceiling_usd": ceil_usd}
    rumors: List[CompetitorRumor] = []

    for idx, entry in enumerate(ai_entries):
        cid, cname, dname, true_mach, true_rad, true_price, cfg_hint, eng_hint = _extract_entry_truth(entry, rfp_info)
        seed_tag = f"{rfp_id}__{cid}__L{lvl}"

        # Check false-negative participation noise (stealth Skunk Works / unannounced bid at level 0)
        u_fn = _draw_u01(rng, seed_tag, idx, "fn")
        if len(ai_entries) > 2 and idx == len(ai_entries) - 1 and u_fn < float(part_cfg["false_negative_prob"]):
            continue

        sig_mach = max(0.015, float(sig_mults["mach_rel"]) * abs(true_mach))
        sig_rad = max(15000.0, float(sig_mults["radius_rel"]) * abs(true_rad))
        sig_price = max(10000.0, float(sig_mults["price_rel"]) * abs(true_price))

        z_mach = max(-2.2, min(2.2, _draw_normal(rng, seed_tag, idx, "mach")))
        z_rad = max(-2.2, min(2.2, _draw_normal(rng, seed_tag, idx, "rad")))
        z_price = max(-2.2, min(2.2, _draw_normal(rng, seed_tag, idx, "price")))

        est_mach = round(max(0.55, min(2.65, true_mach + z_mach * sig_mach)), 3)
        est_rad = round(max(120000.0, true_rad + z_rad * sig_rad), 1)
        est_price = round(max(80000.0, true_price + z_price * sig_price), 2)

        mach_est_dict = Estimate(value=est_mach, sigma=round(sig_mach, 4), source="rumor", unit="mach").to_dict()
        rad_est_dict = Estimate(value=est_rad, sigma=round(sig_rad, 1), source="rumor", unit="m").to_dict()
        price_est_dict = Estimate(value=est_price, sigma=round(sig_price, 2), source="rumor", unit="usd").to_dict()

        conf = round(max(0.50, min(0.99, float(part_cfg["base_confidence"]) - 0.02 * idx)), 2)
        headline = (
            f"Trade press reports {cname} is readying the {dname} ({cfg_hint}, {eng_hint}) "
            f"for {prog_name}: est. Mach {est_mach:.2f} ± {sig_mach:.2f}, "
            f"unit price ~${est_price:,.0f}."
        )

        rumors.append(
            CompetitorRumor(
                rfp_id=rfp_id,
                program_id=rfp_id,
                company_id=cid,
                company_name=cname,
                rumored_design_name=dname if lvl >= 1 else f"{cname} Entry",
                inquiry_level=lvl,
                inquiry_cost_usd=cost_info["cost_usd"],
                inquiry_pc_cost=cost_info["political_capital"],
                participation_confidence=conf,
                is_false_lead=False,
                configuration_hint=cfg_hint if lvl >= 1 else f"{cfg_hint.split()[0]} layout",
                engine_hint=eng_hint if lvl >= 1 else "classified turbojet",
                max_mach_alt=mach_est_dict,
                combat_radius_m=rad_est_dict,
                unit_flyaway_price_usd=price_est_dict,
                estimates={
                    "max_mach_alt": mach_est_dict,
                    "combat_radius_m": rad_est_dict,
                    "unit_flyaway_price_usd": price_est_dict,
                    "unit_price_bid_usd": price_est_dict,
                },
                headline=headline,
            )
        )

    return rumors
