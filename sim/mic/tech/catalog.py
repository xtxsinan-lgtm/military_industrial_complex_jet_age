"""Catalog loader and schema validator for Module 03 (Tech Tree)."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def date_str_to_day(date_str: str) -> int:
    """Convert YYYY-MM-DD to days since 1945-01-01 (using 365-day/month or exact calendar)."""
    from datetime import date

    parts = [int(p) for p in date_str.split("-")]
    d = date(parts[0], parts[1], parts[2])
    epoch = date(1945, 1, 1)
    return (d - epoch).days


def day_to_year(date_day: int) -> float:
    """Convert days since 1945-01-01 to fractional calendar year."""
    return 1945.0 + (float(date_day) / 365.25)


@dataclass(frozen=True)
class EffectKeySpec:
    key: str
    value_type: str  # "bool" | "float" | "int"
    unit: str
    agg: str  # "or" | "max" | "min" | "mul" | "add"
    null_value: Any
    start_1945: Any
    category: str
    meaning: str
    consumers: Tuple[str, ...]
    deprecated: bool = False


@dataclass(frozen=True)
class TechNode:
    id: str
    name_key: str
    branch: str
    discipline: str
    historical_year: float
    historical_date: str
    granted_at_start: bool
    initial_maturity: float
    prereqs: Tuple[str, ...]
    cost_eng_days: int
    cost_usd: float
    naca_diffusion: bool
    govt_contract_eligible: bool
    effects: Dict[str, Any]
    historical_note: str


class TechCatalog:
    """Immutable loaded tech tree, effect keys, component catalogs, and tunables."""

    def __init__(
        self,
        keys: Dict[str, EffectKeySpec],
        nodes: Dict[str, TechNode],
        components: Dict[str, Dict[str, Dict[str, Any]]],
        tunables: Dict[str, float],
    ) -> None:
        self.keys = keys
        self.nodes = nodes
        self.components = components
        self.tunables = tunables
        self._validate()

    def _validate(self) -> None:
        for node_id, node in self.nodes.items():
            for p in node.prereqs:
                if p not in self.nodes:
                    raise ValueError(f"Tech node {node_id} references unknown prereq {p}")
            for eff_key in node.effects:
                if eff_key not in self.keys:
                    raise ValueError(f"Tech node {node_id} sets unknown effect key {eff_key}")

        # Verify DAG acyclicity via topological sort / DFS
        visited: Dict[str, int] = {}

        def dfs(nid: str) -> None:
            state = visited.get(nid, 0)
            if state == 1:
                raise ValueError(f"Cycle detected in tech tree involving {nid}")
            if state == 2:
                return
            visited[nid] = 1
            for p in self.nodes[nid].prereqs:
                dfs(p)
            visited[nid] = 2

        for nid in self.nodes:
            dfs(nid)

        # Verify every component unlock_key is in self.keys
        for comp_type, comp_map in self.components.items():
            for comp_id, comp_data in comp_map.items():
                expected_key = f"unlock.{comp_type}.{comp_id}"
                if comp_data.get("unlock_key") != expected_key:
                    raise ValueError(
                        f"Component {comp_type}.{comp_id} unlock_key mismatch: {comp_data.get('unlock_key')}"
                    )
                if expected_key not in self.keys:
                    raise ValueError(f"Component unlock key {expected_key} missing from effect_keys.json")

    def get_key_spec(self, key: str) -> EffectKeySpec:
        if key not in self.keys:
            raise KeyError(f"Unknown tech effect key: {key}")
        return self.keys[key]

    def get_node(self, tech_id: str) -> TechNode:
        if tech_id not in self.nodes:
            raise KeyError(f"Unknown tech node id: {tech_id}")
        return self.nodes[tech_id]

    def get_component(self, comp_type: str, comp_id: str) -> Dict[str, Any]:
        if comp_type not in self.components or comp_id not in self.components[comp_type]:
            raise KeyError(f"Unknown component {comp_type}.{comp_id}")
        return self.components[comp_type][comp_id]

    def baseline_unlocked_maturity(self) -> Dict[str, float]:
        """Return {tech_id: initial_maturity} for all nodes with granted_at_start=True."""
        return {
            nid: node.initial_maturity
            for nid, node in sorted(self.nodes.items())
            if node.granted_at_start
        }


_DEFAULT_CATALOG: Optional[TechCatalog] = None


def load_catalog(data_dir: Optional[Path] = None) -> TechCatalog:
    """Load TechCatalog from sim/data/tech and sim/data/tuning/tech.json."""
    global _DEFAULT_CATALOG
    if data_dir is None and _DEFAULT_CATALOG is not None:
        return _DEFAULT_CATALOG

    base = Path(data_dir) if data_dir is not None else DEFAULT_DATA_DIR
    tech_dir = base / "tech"

    with open(tech_dir / "effect_keys.json", "r", encoding="utf-8") as f:
        raw_keys = json.load(f)["keys"]
    keys: Dict[str, EffectKeySpec] = {}
    for rk in raw_keys:
        spec = EffectKeySpec(
            key=rk["key"],
            value_type=rk["type"],
            unit=rk["unit"],
            agg=rk["agg"],
            null_value=rk["null_value"],
            start_1945=rk["start_1945"],
            category=rk["category"],
            meaning=rk["meaning"],
            consumers=tuple(rk["consumers"]),
            deprecated=bool(rk.get("deprecated", False)),
        )
        keys[spec.key] = spec

    with open(tech_dir / "tech_nodes_1945_1960.json", "r", encoding="utf-8") as f:
        raw_nodes = json.load(f)["nodes"]
    nodes: Dict[str, TechNode] = {}
    for rn in raw_nodes:
        node = TechNode(
            id=rn["id"],
            name_key=rn["name_key"],
            branch=rn["branch"],
            discipline=rn["discipline"],
            historical_year=float(rn["historical_year"]),
            historical_date=rn["historical_date"],
            granted_at_start=bool(rn["granted_at_start"]),
            initial_maturity=float(rn["initial_maturity"]),
            prereqs=tuple(rn["prereqs"]),
            cost_eng_days=int(rn["cost_eng_days"]),
            cost_usd=float(rn["cost_usd"]),
            naca_diffusion=bool(rn["naca_diffusion"]),
            govt_contract_eligible=bool(rn["govt_contract_eligible"]),
            effects=dict(rn["effects"]),
            historical_note=rn.get("historical_note", ""),
        )
        nodes[node.id] = node

    comp_files = {
        "gun": "components_guns.json",
        "rocket": "components_rockets.json",
        "missile": "components_missiles.json",
        "radar": "components_radars.json",
    }
    components: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for ctype, fname in comp_files.items():
        with open(tech_dir / fname, "r", encoding="utf-8") as f:
            raw_comps = json.load(f)["components"]
        components[ctype] = {c["id"]: c for c in raw_comps}

    tuning_path = base / "tuning" / "tech.json"
    with open(tuning_path, "r", encoding="utf-8") as f:
        tunables = {k: float(v) for k, v in json.load(f)["tunables"].items()}

    cat = TechCatalog(keys=keys, nodes=nodes, components=components, tunables=tunables)
    if data_dir is None:
        _DEFAULT_CATALOG = cat
    return cat
