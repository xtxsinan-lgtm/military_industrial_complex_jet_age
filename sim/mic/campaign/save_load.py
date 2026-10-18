"""Save/load serialization, schema migration registry, and deterministic state hashing.

Owned by Module 09 (`docs/spec/09_core_loop.md`).
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Dict, Tuple, Union

CURRENT_SAVE_SCHEMA_VERSION: int = 1
CURRENT_GAME_VERSION: str = "0.1.0-mvp"

MigrationFunc = Callable[[Dict[str, Any]], Dict[str, Any]]

# Global registries for envelope-level and module-level save migrations
_ENVELOPE_MIGRATIONS: Dict[int, MigrationFunc] = {}
_MODULE_MIGRATIONS: Dict[Tuple[str, int], MigrationFunc] = {}


def register_envelope_migration(from_version: int, fn: MigrationFunc) -> None:
    """Register a migration function that upgrades a save envelope from `from_version` to `from_version + 1`."""
    _ENVELOPE_MIGRATIONS[int(from_version)] = fn


def register_module_migration(module_id: str, from_version: int, fn: MigrationFunc) -> None:
    """Register a migration function that upgrades `module_id` state from `from_version` to `from_version + 1`."""
    _MODULE_MIGRATIONS[(str(module_id), int(from_version))] = fn


def _validate_and_canonicalize_json_value(val: Any, path: str = "$") -> Any:
    """Recursively verify that no NaN/Infinity floats exist and canonicalize dict key order."""
    if val is None or isinstance(val, (bool, str, int)):
        return val
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            raise ValueError(f"Non-finite float ({val}) encountered during save serialization at {path}")
        # Avoid -0.0 differences across platforms
        if val == 0.0:
            return 0.0
        return val
    if isinstance(val, (list, tuple)):
        return [_validate_and_canonicalize_json_value(x, f"{path}[{i}]") for i, x in enumerate(val)]
    if isinstance(val, dict):
        return {
            str(k): _validate_and_canonicalize_json_value(val[k], f"{path}.{k}")
            for k in sorted(val.keys(), key=lambda x: str(x))
        }
    raise TypeError(f"Unsupported type {type(val).__name__} in save payload at {path}")


def canonical_json_dumps(payload: Dict[str, Any], *, indent: Union[int, None] = None) -> str:
    """Serialize `payload` into deterministic sorted-key JSON after checking for NaN/Inf."""
    clean = _validate_and_canonicalize_json_value(payload)
    return json.dumps(clean, sort_keys=True, indent=indent, ensure_ascii=False)


def build_save_envelope(world: Any) -> Dict[str, Any]:
    """Create a complete versioned save envelope dictionary from `world`."""
    modules_block: Dict[str, Dict[str, Any]] = {}
    for mid in sorted(world.modules.keys()):
        mod = world.modules[mid]
        modules_block[mid] = {
            "schema_version": int(getattr(mod, "schema_version", 1)),
            "state": mod.to_dict(),
        }

    envelope = {
        "save_schema_version": CURRENT_SAVE_SCHEMA_VERSION,
        "game_version": CURRENT_GAME_VERSION,
        "campaign_id": str(world.campaign_id),
        "world_state": world.to_core_dict(),
        "modules": modules_block,
    }
    return _validate_and_canonicalize_json_value(envelope)


def compute_state_hash(world: Any) -> str:
    """Return the hex SHA-256 digest of the canonical serialized state of `world`."""
    env = build_save_envelope(world)
    raw_bytes = json.dumps(env, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw_bytes).hexdigest()


def migrate_save_envelope(
    envelope: Dict[str, Any],
    target_envelope_version: int = CURRENT_SAVE_SCHEMA_VERSION,
    target_module_versions: Union[Dict[str, int], None] = None,
) -> Dict[str, Any]:
    """Step an older save envelope and its module payloads forward to current schema versions."""
    if not isinstance(envelope, dict) or "save_schema_version" not in envelope:
        raise ValueError("Invalid save envelope: missing 'save_schema_version'")

    cur_ver = int(envelope["save_schema_version"])
    if cur_ver > target_envelope_version:
        raise ValueError(
            f"Save schema version {cur_ver} is newer than supported version {target_envelope_version}"
        )

    env = json.loads(json.dumps(envelope))
    while cur_ver < target_envelope_version:
        mig = _ENVELOPE_MIGRATIONS.get(cur_ver)
        if mig is None:
            raise ValueError(f"Missing envelope migration from version {cur_ver} to {cur_ver + 1}")
        env = mig(env)
        cur_ver += 1
        env["save_schema_version"] = cur_ver

    if target_module_versions:
        mods = env.get("modules", {})
        for mid, target_mver in sorted(target_module_versions.items()):
            if mid not in mods:
                continue
            mblock = mods[mid]
            mver = int(mblock.get("schema_version", 1))
            if mver > target_mver:
                raise ValueError(
                    f"Module {mid} save version {mver} is newer than supported version {target_mver}"
                )
            mstate = mblock.get("state", {})
            while mver < target_mver:
                mmig = _MODULE_MIGRATIONS.get((mid, mver))
                if mmig is None:
                    raise ValueError(
                        f"Missing module migration for {mid} from version {mver} to {mver + 1}"
                    )
                mstate = mmig(mstate)
                mver += 1
            mblock["schema_version"] = mver
            mblock["state"] = mstate

    return env


def save_to_file(world: Any, path: Union[str, Path], *, compress: bool = False) -> Path:
    """Write `world` save envelope to `path` (plain UTF-8 JSON or gzip if `compress=True` or `.gz`)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    env = build_save_envelope(world)
    text = canonical_json_dumps(env, indent=2)
    if compress or p.suffix == ".gz":
        with gzip.open(p, "wt", encoding="utf-8") as f:
            f.write(text)
    else:
        p.write_text(text, encoding="utf-8")
    return p


def load_envelope_from_file(path: Union[str, Path]) -> Dict[str, Any]:
    """Read a save envelope from a plain JSON or `.gz` file."""
    p = Path(path)
    raw = p.read_bytes()
    if raw[:2] == b"\x1f\x8b":
        text = gzip.decompress(raw).decode("utf-8")
    else:
        text = raw.decode("utf-8")
    return json.loads(text)
