"""Data models and contracts for Module 05 (Procurement).

Conforms to 00_conventions.md section 4 and docs/spec/05_procurement.md section 4.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Estimate:
    """Performance estimate carrying uncertainty (00_conventions.md §4.1)."""

    value: float
    sigma: float = 0.0
    source: str = "sim"  # "sim" | "tunnel" | "flight" | "service"
    unit: str = "float"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Estimate":
        return cls(
            value=float(d["value"]),
            sigma=float(d.get("sigma", 0.0)),
            source=str(d.get("source", "sim")),
            unit=str(d.get("unit", "float")),
        )


@dataclass
class CriterionSpec:
    """Single requirement criterion (threshold, objective, or weighted)."""

    key: str
    kind: str  # "threshold" | "objective" | "weighted"
    op: str  # ">=" | "<="
    value: float
    weight: float = 0.0
    objective_value: Optional[float] = None
    unit: str = "float"
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CriterionSpec":
        obj_val = d.get("objective_value")
        return cls(
            key=str(d["key"]),
            kind=str(d["kind"]),
            op=str(d["op"]),
            value=float(d["value"]),
            weight=float(d.get("weight", 0.0)),
            objective_value=float(obj_val) if obj_val is not None else None,
            unit=str(d.get("unit", "float")),
            description=str(d.get("description", "")),
        )


@dataclass
class EquipmentRequirement:
    """Mandatory configuration/equipment gates on a Requirement."""

    carrier_capable: bool = False
    radar_required: bool = False
    min_crew: int = 1
    min_engines: int = 1
    internal_bay_required: bool = False
    min_guns_20mm: int = 0
    missile_capability: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> "EquipmentRequirement":
        if not d:
            return cls()
        return cls(
            carrier_capable=bool(d.get("carrier_capable", False)),
            radar_required=bool(d.get("radar_required", False)),
            min_crew=int(d.get("min_crew", 1)),
            min_engines=int(d.get("min_engines", 1)),
            internal_bay_required=bool(d.get("internal_bay_required", False)),
            min_guns_20mm=int(d.get("min_guns_20mm", 0)),
            missile_capability=[str(x) for x in d.get("missile_capability", [])],
        )


@dataclass
class EquipmentProfile:
    """Equipment and configuration flags present on a submitted aircraft design."""

    carrier_capable: bool = False
    radar_installed: bool = False
    crew: int = 1
    engines: int = 1
    internal_bay: bool = False
    guns_20mm: int = 0
    missile_capability: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> "EquipmentProfile":
        if not d:
            return cls()
        return cls(
            carrier_capable=bool(d.get("carrier_capable", False)),
            radar_installed=bool(d.get("radar_installed", False)),
            crew=int(d.get("crew", 1)),
            engines=int(d.get("engines", 1)),
            internal_bay=bool(d.get("internal_bay", False)),
            guns_20mm=int(d.get("guns_20mm", 0)),
            missile_capability=[str(x) for x in d.get("missile_capability", [])],
        )


@dataclass
class NoveltyProfile:
    """Technological novelty profile of a submitted aircraft bid."""

    unproven_tech_count: int = 0
    unflown_engine: bool = False
    unconventional_config: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> "NoveltyProfile":
        if not d:
            return cls()
        return cls(
            unproven_tech_count=int(d.get("unproven_tech_count", 0)),
            unflown_engine=bool(d.get("unflown_engine", False)),
            unconventional_config=bool(d.get("unconventional_config", False)),
        )


@dataclass
class BudgetSpec:
    """Program budget and planned production quantity."""

    dev_usd: float
    unit_price_ceiling_usd: float
    quantity_planned: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "BudgetSpec":
        return cls(
            dev_usd=float(d["dev_usd"]),
            unit_price_ceiling_usd=float(d["unit_price_ceiling_usd"]),
            quantity_planned=int(d["quantity_planned"]),
        )


@dataclass
class AcquisitionSpec:
    """Acquisition structure and evaluation mechanics for a program."""

    style: str = "paper_award"  # "flyoff" | "paper_award" | "sole_source"
    downselect_count: int = 2
    prototype_quantity_per_winner: int = 2
    allow_dual_award: bool = False
    production_lots: int = 4
    urgency: float = 0.50

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> "AcquisitionSpec":
        if not d:
            return cls()
        return cls(
            style=str(d.get("style", "paper_award")),
            downselect_count=int(d.get("downselect_count", 2)),
            prototype_quantity_per_winner=int(d.get("prototype_quantity_per_winner", 2)),
            allow_dual_award=bool(d.get("allow_dual_award", False)),
            production_lots=int(d.get("production_lots", 4)),
            urgency=float(d.get("urgency", 0.50)),
        )


@dataclass
class PoliticsSpec:
    """Political landscape and incumbent biases for a Requirement."""

    incumbent_bias: Dict[str, float] = field(default_factory=dict)
    congressional_interest: float = 0.30
    industrial_base_need: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> "PoliticsSpec":
        if not d:
            return cls()
        return cls(
            incumbent_bias={
                str(k): float(v) for k, v in d.get("incumbent_bias", {}).items()
            },
            congressional_interest=float(d.get("congressional_interest", 0.30)),
            industrial_base_need={
                str(k): float(v) for k, v in d.get("industrial_base_need", {}).items()
            },
        )


@dataclass
class HistoricalEntrant:
    """Published/reconstructed historical competitor specification for replay and AI."""

    company_id: str
    design_name: str
    is_historical_winner: bool
    built_prototype: bool
    first_flight_date: Optional[str]
    unit_price_bid_usd: float
    dev_cost_bid_usd: float
    novelty: NoveltyProfile
    equipment: EquipmentProfile
    reputation_at_bid: float
    track_record_at_bid: float
    district_weight: float
    cross_service_derivative: bool
    anchor_performance: Dict[str, float]
    promised_overrides: Dict[str, float] = field(default_factory=dict)
    flyoff_flaws_unfixed_severity: int = 0
    published_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "HistoricalEntrant":
        return cls(
            company_id=str(d["company_id"]),
            design_name=str(d["design_name"]),
            is_historical_winner=bool(d.get("is_historical_winner", False)),
            built_prototype=bool(d.get("built_prototype", False)),
            first_flight_date=d.get("first_flight_date"),
            unit_price_bid_usd=float(d["unit_price_bid_usd"]),
            dev_cost_bid_usd=float(d["dev_cost_bid_usd"]),
            novelty=NoveltyProfile.from_dict(d.get("novelty")),
            equipment=EquipmentProfile.from_dict(d.get("equipment")),
            reputation_at_bid=float(d.get("reputation_at_bid", 60.0)),
            track_record_at_bid=float(d.get("track_record_at_bid", 0.50)),
            district_weight=float(d.get("district_weight", 0.35)),
            cross_service_derivative=bool(d.get("cross_service_derivative", False)),
            anchor_performance={
                str(k): float(v) for k, v in d.get("anchor_performance", {}).items()
            },
            promised_overrides={
                str(k): float(v) for k, v in d.get("promised_overrides", {}).items()
            },
            flyoff_flaws_unfixed_severity=int(d.get("flyoff_flaws_unfixed_severity", 0)),
            published_notes=str(d.get("published_notes", "")),
        )


@dataclass
class HistoricalMeta:
    """Historical outcome and entrants for a Requirement (00_conventions.md §4.5)."""

    winner_company_id: str
    winner_design_name: str
    award_date: str
    outcome: str  # "produced" | "cancelled_after_flyoff" | "cancelled_in_dev"
    production_delivered: int
    notes: str
    citations: List[str] = field(default_factory=list)
    competitors: List[HistoricalEntrant] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "HistoricalMeta":
        return cls(
            winner_company_id=str(d["winner_company_id"]),
            winner_design_name=str(d["winner_design_name"]),
            award_date=str(d.get("award_date", "1950-01-01")),
            outcome=str(d.get("outcome", "produced")),
            production_delivered=int(d.get("production_delivered", 0)),
            notes=str(d.get("notes", "")),
            citations=[str(x) for x in d.get("citations", [])],
            competitors=[
                HistoricalEntrant.from_dict(c) for c in d.get("competitors", [])
            ],
        )


@dataclass
class AltHistorySpec:
    """Alt-history adaptation linkage for a historical program."""

    predecessor_program_id: Optional[str] = None
    follow_on_program_id: Optional[str] = None
    suppress_if_role_satisfied: bool = False
    historical_cancellation_shock: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Optional[Dict[str, Any]]) -> "AltHistorySpec":
        if not d:
            return cls()
        return cls(
            predecessor_program_id=d.get("predecessor_program_id"),
            follow_on_program_id=d.get("follow_on_program_id"),
            suppress_if_role_satisfied=bool(d.get("suppress_if_role_satisfied", False)),
            historical_cancellation_shock=float(
                d.get("historical_cancellation_shock", 0.0)
            ),
        )


@dataclass
class ProgramSpec:
    """Complete procurement program / Requirement specification (00_conventions.md §4.5)."""

    id: str
    program_name: str
    customer: str  # "USAF" | "USN"
    role: str
    issue_date: str
    proposal_due: str
    first_flight_due: str
    ioc_due: str
    criteria: List[CriterionSpec]
    budget: BudgetSpec
    politics: PoliticsSpec
    historical: HistoricalMeta
    name_key: str = ""
    mvp_core: bool = False
    equipment: EquipmentRequirement = field(default_factory=EquipmentRequirement)
    acquisition: AcquisitionSpec = field(default_factory=AcquisitionSpec)
    eval_weights: Dict[str, Dict[str, float]] = field(
        default_factory=lambda: {
            "proposal": {"perf": 0.45, "cost": 0.20, "sched": 0.15, "risk": 0.20},
            "flyoff": {"perf": 0.60, "cost": 0.15, "sched": 0.10, "risk": 0.15},
        }
    )
    alt_history: AltHistorySpec = field(default_factory=AltHistorySpec)
    schema_version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "name_key": self.name_key or f"program.{self.id}.name",
            "program_name": self.program_name,
            "customer": self.customer,
            "role": self.role,
            "mvp_core": self.mvp_core,
            "issue_date": self.issue_date,
            "proposal_due": self.proposal_due,
            "first_flight_due": self.first_flight_due,
            "ioc_due": self.ioc_due,
            "equipment": self.equipment.to_dict(),
            "criteria": [c.to_dict() for c in self.criteria],
            "budget": self.budget.to_dict(),
            "acquisition": self.acquisition.to_dict(),
            "eval_weights": self.eval_weights,
            "politics": self.politics.to_dict(),
            "historical": self.historical.to_dict(),
            "alt_history": self.alt_history.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ProgramSpec":
        default_weights = {
            "proposal": {"perf": 0.45, "cost": 0.20, "sched": 0.15, "risk": 0.20},
            "flyoff": {"perf": 0.60, "cost": 0.15, "sched": 0.10, "risk": 0.15},
        }
        ew = d.get("eval_weights", default_weights)
        return cls(
            schema_version=int(d.get("schema_version", 1)),
            id=str(d["id"]),
            name_key=str(d.get("name_key", f"program.{d['id']}.name")),
            program_name=str(d["program_name"]),
            customer=str(d["customer"]),
            role=str(d.get("role", "day_fighter")),
            mvp_core=bool(d.get("mvp_core", False)),
            issue_date=str(d["issue_date"]),
            proposal_due=str(d["proposal_due"]),
            first_flight_due=str(d["first_flight_due"]),
            ioc_due=str(d["ioc_due"]),
            equipment=EquipmentRequirement.from_dict(d.get("equipment")),
            criteria=[CriterionSpec.from_dict(c) for c in d["criteria"]],
            budget=BudgetSpec.from_dict(d["budget"]),
            acquisition=AcquisitionSpec.from_dict(d.get("acquisition")),
            eval_weights={
                str(phase): {str(k): float(v) for k, v in weights.items()}
                for phase, weights in ew.items()
            },
            politics=PoliticsSpec.from_dict(d.get("politics")),
            historical=HistoricalMeta.from_dict(d["historical"]),
            alt_history=AltHistorySpec.from_dict(d.get("alt_history")),
        )


@dataclass
class BidderContext:
    """Snapshot of a bidding company's reputation, track record, and industrial standing."""

    company_id: str
    reputation_service: float = 50.0
    track_record: float = 0.50
    district_weight: float = 0.35
    active_contracts_same_role: int = 0
    active_contracts_same_customer: int = 0
    idle_factory_fraction: float = 0.30

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "BidderContext":
        return cls(
            company_id=str(d["company_id"]),
            reputation_service=float(d.get("reputation_service", 50.0)),
            track_record=float(d.get("track_record", 0.50)),
            district_weight=float(d.get("district_weight", 0.35)),
            active_contracts_same_role=int(d.get("active_contracts_same_role", 0)),
            active_contracts_same_customer=int(
                d.get("active_contracts_same_customer", 0)
            ),
            idle_factory_fraction=float(d.get("idle_factory_fraction", 0.30)),
        )


@dataclass
class ProposalBid:
    """Bid submitted by a player or AI company for a Requirement."""

    bid_id: str
    program_id: str
    company_id: str
    design_name: str
    is_player: bool
    submitted_day: int
    estimates: Dict[str, Estimate]
    promised: Dict[str, float]
    unit_price_bid_usd: float
    unit_cost_estimate_usd: float
    dev_cost_bid_usd: float
    dev_cost_estimate_usd: float
    promised_first_flight_day: int
    promised_ioc_day: int
    novelty: NoveltyProfile = field(default_factory=NoveltyProfile)
    equipment: EquipmentProfile = field(default_factory=EquipmentProfile)
    political_capital_spent: float = 0.0
    cross_service_derivative: bool = False
    is_originator: bool = False
    measured_performance: Dict[str, Estimate] = field(default_factory=dict)
    actual_first_flight_day: Optional[int] = None
    unfixed_flaw_severity_sum: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ProposalBid":
        return cls(
            bid_id=str(d["bid_id"]),
            program_id=str(d["program_id"]),
            company_id=str(d["company_id"]),
            design_name=str(d["design_name"]),
            is_player=bool(d.get("is_player", False)),
            submitted_day=int(d["submitted_day"]),
            estimates={
                str(k): Estimate.from_dict(v) if isinstance(v, dict) else v
                for k, v in d.get("estimates", {}).items()
            },
            promised={str(k): float(v) for k, v in d.get("promised", {}).items()},
            unit_price_bid_usd=float(d["unit_price_bid_usd"]),
            unit_cost_estimate_usd=float(
                d.get("unit_cost_estimate_usd", d["unit_price_bid_usd"])
            ),
            dev_cost_bid_usd=float(d["dev_cost_bid_usd"]),
            dev_cost_estimate_usd=float(
                d.get("dev_cost_estimate_usd", d["dev_cost_bid_usd"])
            ),
            promised_first_flight_day=int(d["promised_first_flight_day"]),
            promised_ioc_day=int(d["promised_ioc_day"]),
            novelty=NoveltyProfile.from_dict(d.get("novelty")),
            equipment=EquipmentProfile.from_dict(d.get("equipment")),
            political_capital_spent=float(d.get("political_capital_spent", 0.0)),
            cross_service_derivative=bool(d.get("cross_service_derivative", False)),
            is_originator=bool(d.get("is_originator", False)),
            measured_performance={
                str(k): Estimate.from_dict(v) if isinstance(v, dict) else v
                for k, v in d.get("measured_performance", {}).items()
            },
            actual_first_flight_day=(
                int(d["actual_first_flight_day"])
                if d.get("actual_first_flight_day") is not None
                else None
            ),
            unfixed_flaw_severity_sum=int(d.get("unfixed_flaw_severity_sum", 0)),
        )


@dataclass
class CriterionEvalDetail:
    """Detailed evaluation trace of a single criterion on a bid."""

    key: str
    kind: str
    promised: float
    substantiated_mu: float
    substantiated_sigma: float
    credible_value: float
    overclaim_q: float
    gate_passed: bool
    utility: float
    weight: float
    weighted_utility: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BidScoreBreakdown:
    """Complete score breakdown for one ProposalBid in proposal or fly-off phase."""

    bid_id: str
    company_id: str
    design_name: str
    phase: str  # "proposal" | "flyoff"
    responsive: bool
    disqualify_reasons: List[str]
    credibility: float
    novelty_index: float
    perf_score: float
    cost_score: float
    sched_score: float
    risk_index: float
    risk_score: float
    tech_score: float
    politics_bonus: float
    promise_penalty: float
    flaw_penalty: float
    eval_noise: float
    total_score: float
    criteria_details: List[CriterionEvalDetail] = field(default_factory=list)
    eligible_for_private_prototype: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvaluationReport:
    """Output of a Source Selection Board evaluation (proposal downselect or fly-off)."""

    program_id: str
    program_name: str
    customer: str
    phase: str  # "proposal" | "flyoff"
    evaluation_day: int
    outcome: str  # "awarded" | "downselected" | "dual_award" | "waiver_award" | "cancelled_after_flyoff" | "no_responsive_bid"
    winner_bid_ids: List[str]
    winner_company_ids: List[str]
    finalist_bid_ids: List[str]
    private_prototype_eligible_bid_ids: List[str]
    quantity_splits: Dict[str, int]
    waiver_granted: bool
    rankings: List[BidScoreBreakdown]
    debrief_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProductionLot:
    """Single fiscal-year production lot within a ContractState."""

    lot_number: int
    fiscal_year: int
    quantity_planned: int
    quantity_awarded: int
    unit_target_price_usd: float
    unit_ceiling_price_usd: float
    gov_share: float
    liquidated_damage_frac: float = 0.0
    status: str = "planned"  # "planned" | "active" | "completed" | "cancelled"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContractState:
    """Active development or production contract awarded by Module 05."""

    contract_id: str
    program_id: str
    customer: str
    role: str
    company_id: str
    design_name: str
    contract_kind: str  # "prototype_cpff" | "production_fpif"
    award_day: int
    dev_target_cost_usd: float
    dev_fixed_fee_usd: float
    dev_cost_incurred_usd: float
    promised_performance: Dict[str, float]
    promised_first_flight_day: int
    promised_ioc_day: int
    lots: List[ProductionLot] = field(default_factory=list)
    status: str = "active"  # "active" | "show_cause" | "completed" | "cancelled"
    cancellation_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PromiseAuditReport:
    """Result of auditing promised vs delivered performance and schedule at FF or IOC."""

    contract_id: str
    milestone: str  # "first_flight" | "ioc"
    weighted_shortfall_frac: float
    liquidated_damage_frac: float
    reputation_delta_perf: float
    reputation_delta_sched: float
    reputation_delta_total: float
    old_track_record: float
    new_track_record: float
    show_cause_triggered: bool
    failed_threshold_keys: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnnualReviewReport:
    """Result of an annual July 1 fiscal lot review."""

    contract_id: str
    fiscal_year: int
    p_cancel: float
    cancelled: bool
    cancellation_reason: Optional[str]
    lot_number_reviewed: Optional[int]
    qty_multiplier: float
    quantity_awarded: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CapabilityGapRecord:
    """Unmet operational requirement queued for delayed re-issue after cancellation."""

    customer: str
    role: str
    origin_program_id: str
    created_day: int
    reissue_due_day: int
    urgency: float
    reissued: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ThreatMilestone:
    """Soviet threat intelligence event driving doctrinal pressure and dynamic RFPs."""

    id: str
    date: str
    name: str
    category: str  # "bomber" | "fighter" | "nuclear" | "missile" | "armistice"
    affected_customers: List[str]
    affected_roles: List[str]
    threat_mach: float
    threat_ceiling_m: float
    demand_shock: float
    obsolescence_shock_roles: Dict[str, float] = field(default_factory=dict)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ThreatMilestone":
        return cls(
            id=str(d["id"]),
            date=str(d["date"]),
            name=str(d["name"]),
            category=str(d["category"]),
            affected_customers=[str(x) for x in d.get("affected_customers", [])],
            affected_roles=[str(x) for x in d.get("affected_roles", [])],
            threat_mach=float(d.get("threat_mach", 0.80)),
            threat_ceiling_m=float(d.get("threat_ceiling_m", 12000.0)),
            demand_shock=float(d.get("demand_shock", 0.0)),
            obsolescence_shock_roles={
                str(k): float(v)
                for k, v in d.get("obsolescence_shock_roles", {}).items()
            },
            description=str(d.get("description", "")),
        )


@dataclass
class UnsolicitedPitchResult:
    """Result of pitching an unsolicited private-venture design to USAF or USN."""

    company_id: str
    design_name: str
    customer: str
    role: str
    pitch_day: int
    decision_day: int
    pitch_cost_usd: float
    evaluated_score: float
    p_accept: float
    accepted: bool
    p_sole_source: float
    outcome: str  # "sole_source_award" | "open_competition_issued" | "rejected"
    generated_program: Optional[ProgramSpec] = None
    awarded_contract: Optional[ContractState] = None
    cooldown_until_day: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
