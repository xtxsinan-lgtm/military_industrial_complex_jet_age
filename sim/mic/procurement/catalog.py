"""Catalog loader for historical programs, Soviet threat milestones, and budget indices."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .dates import date_to_day
from .models import ProgramSpec, ThreatMilestone

DEFAULT_PROGRAMS_DIR = Path(__file__).resolve().parents[2] / "data" / "programs"


def load_all_programs(
    directory: Optional[Path] = None, mvp_only: bool = False
) -> List[ProgramSpec]:
    """Load all historical ProgramSpec JSON files from sim/data/programs/, sorted by issue_date."""
    target_dir = directory if directory is not None else DEFAULT_PROGRAMS_DIR
    programs: List[ProgramSpec] = []
    for p in sorted(target_dir.glob("*.json")):
        if p.name in ("threats_1945_1960.json", "budget_index_1945_1960.json"):
            continue
        with open(p, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if "criteria" not in raw or "customer" not in raw:
            continue
        spec = ProgramSpec.from_dict(raw)
        if mvp_only and not spec.mvp_core:
            continue
        programs.append(spec)
    programs.sort(key=lambda s: (date_to_day(s.issue_date), s.id))
    return programs


def load_program_by_id(
    program_id: str, directory: Optional[Path] = None
) -> ProgramSpec:
    """Load a single ProgramSpec by its id."""
    target_dir = directory if directory is not None else DEFAULT_PROGRAMS_DIR
    path = target_dir / f"{program_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Program file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return ProgramSpec.from_dict(json.load(f))


def load_threat_milestones(
    directory: Optional[Path] = None,
) -> List[ThreatMilestone]:
    """Load Soviet threat milestones from sim/data/programs/threats_1945_1960.json."""
    target_dir = directory if directory is not None else DEFAULT_PROGRAMS_DIR
    path = target_dir / "threats_1945_1960.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    milestones = [ThreatMilestone.from_dict(item) for item in data["milestones"]]
    milestones.sort(key=lambda m: (date_to_day(m.date), m.id))
    return milestones


def load_budget_index_table(
    directory: Optional[Path] = None,
) -> Dict[int, float]:
    """Load fiscal year -> budget_index mapping from sim/data/programs/budget_index_1945_1960.json."""
    target_dir = directory if directory is not None else DEFAULT_PROGRAMS_DIR
    path = target_dir / "budget_index_1945_1960.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {int(k): float(v) for k, v in data["fiscal_year_budget_index"].items()}
