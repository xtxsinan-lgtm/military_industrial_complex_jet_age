"""TechContext aggregation, cap checking, and required_techs derivation (Module 03)."""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union

from .catalog import EffectKeySpec, TechCatalog, load_catalog


@dataclass(frozen=True)
class TechContext:
    """Immutable daily tech state snapshot for a single company (03a §1)."""

    date_day: int
    company_id: str
    values: Dict[str, Union[bool, float, int]]
    provider: Dict[str, Optional[str]]
    maturity: Dict[str, float]
    tech_maturity: Dict[str, float]
    unlocked: List[str]

    def get(self, key: str) -> Union[bool, float, int]:
        """Return aggregated value for key; raises KeyError on unknown key."""
        if key not in self.values:
            raise KeyError(f"Unknown tech effect key: {key}")
        return self.values[key]

    def maturity_of(self, key: str) -> float:
        """Return maturity in [0, 1] of the binding provider for key (1.0 if provider is None)."""
        if key not in self.maturity:
            raise KeyError(f"Unknown tech effect key: {key}")
        return self.maturity[key]

    def allows(self, key: str, design_value: Any = True, eps: float = 1e-6) -> bool:
        """Check whether design_value is permitted under key's aggregated limit."""
        if key not in self.values:
            raise KeyError(f"Unknown tech effect key: {key}")
        cat = load_catalog()
        spec = cat.get_key_spec(key)
        bound = self.values[key]
        if spec.agg == "or":
            return bool(bound) is True
        if spec.agg == "max":
            return float(design_value) <= float(bound) + eps
        if spec.agg == "min":
            return float(design_value) >= float(bound) - eps
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date_day": self.date_day,
            "company_id": self.company_id,
            "values": dict(self.values),
            "provider": dict(self.provider),
            "maturity": dict(self.maturity),
            "tech_maturity": dict(self.tech_maturity),
            "unlocked": list(self.unlocked),
        }


def _cast_val(val: Any, value_type: str) -> Union[bool, float, int]:
    if value_type == "bool":
        return bool(val)
    if value_type == "int":
        return int(round(float(val)))
    return float(val)


def build_tech_context(
    company_id: str,
    date_day: int,
    unlocked_maturity: Union[Mapping[str, float], Iterable[str]],
    catalog: Optional[TechCatalog] = None,
) -> TechContext:
    """Aggregate unlocked techs and their maturities into a canonical TechContext."""
    cat = catalog if catalog is not None else load_catalog()

    if isinstance(unlocked_maturity, Mapping):
        tech_mat: Dict[str, float] = {
            str(tid): max(0.0, min(1.0, float(m)))
            for tid, m in sorted(unlocked_maturity.items())
        }
    else:
        tech_mat = {
            str(tid): cat.get_node(str(tid)).initial_maturity
            for tid in sorted(set(unlocked_maturity))
        }

    for tid in tech_mat:
        if tid not in cat.nodes:
            raise KeyError(f"Unknown unlocked tech_id: {tid}")

    unlocked_sorted = sorted(tech_mat.keys())

    values: Dict[str, Union[bool, float, int]] = {}
    provider: Dict[str, Optional[str]] = {}
    maturity: Dict[str, float] = {}

    for key, spec in cat.keys.items():
        contributors: List[Tuple[str, Any, float]] = []
        for tid in unlocked_sorted:
            node = cat.nodes[tid]
            if key in node.effects:
                contributors.append((tid, node.effects[key], tech_mat[tid]))

        null_v = _cast_val(spec.null_value, spec.value_type)

        if not contributors:
            values[key] = null_v
            provider[key] = None
            maturity[key] = 1.0
            continue

        if spec.agg == "or":
            true_contribs = [(tid, val, mat) for (tid, val, mat) in contributors if bool(val)]
            if not true_contribs:
                values[key] = False
                provider[key] = None
                maturity[key] = 1.0
            else:
                # Highest maturity, then tech_id sort
                true_contribs.sort(key=lambda item: (-item[2], item[0]))
                best_tid, _, best_mat = true_contribs[0]
                values[key] = True
                provider[key] = best_tid
                maturity[key] = best_mat

        elif spec.agg == "max":
            best_val = float(null_v)
            best_tid: Optional[str] = None
            best_mat = 1.0
            for tid, val, mat in contributors:
                fval = float(val)
                if fval > best_val + 1e-12:
                    best_val = fval
                    best_tid = tid
                    best_mat = mat
                elif abs(fval - best_val) <= 1e-12 and best_tid is not None:
                    if (mat > best_mat + 1e-12) or (abs(mat - best_mat) <= 1e-12 and tid < best_tid):
                        best_tid = tid
                        best_mat = mat
                elif abs(fval - best_val) <= 1e-12 and best_tid is None and fval >= float(null_v) - 1e-12:
                    best_tid = tid
                    best_mat = mat
            values[key] = _cast_val(best_val, spec.value_type)
            provider[key] = best_tid
            maturity[key] = best_mat if best_tid is not None else 1.0

        elif spec.agg == "min":
            best_val = float(null_v)
            best_tid = None
            best_mat = 1.0
            for tid, val, mat in contributors:
                fval = float(val)
                if fval < best_val - 1e-12:
                    best_val = fval
                    best_tid = tid
                    best_mat = mat
                elif abs(fval - best_val) <= 1e-12 and best_tid is not None:
                    if (mat > best_mat + 1e-12) or (abs(mat - best_mat) <= 1e-12 and tid < best_tid):
                        best_tid = tid
                        best_mat = mat
                elif abs(fval - best_val) <= 1e-12 and best_tid is None and fval <= float(null_v) + 1e-12:
                    best_tid = tid
                    best_mat = mat
            values[key] = _cast_val(best_val, spec.value_type)
            provider[key] = best_tid
            maturity[key] = best_mat if best_tid is not None else 1.0

        elif spec.agg == "mul":
            prod = float(null_v)
            for _, val, _ in contributors:
                prod *= float(val)
            # Lowest maturity among contributors, tie-broken by tech_id sort
            contributors.sort(key=lambda item: (item[2], item[0]))
            worst_tid, _, worst_mat = contributors[0]
            values[key] = _cast_val(prod, spec.value_type)
            provider[key] = worst_tid
            maturity[key] = worst_mat

        elif spec.agg == "add":
            total = float(null_v)
            for _, val, _ in contributors:
                total += float(val)
            contributors.sort(key=lambda item: (item[2], item[0]))
            worst_tid, _, worst_mat = contributors[0]
            values[key] = _cast_val(total, spec.value_type)
            provider[key] = worst_tid
            maturity[key] = worst_mat

        else:
            raise ValueError(f"Unsupported aggregation mode {spec.agg} for key {key}")

    return TechContext(
        date_day=int(date_day),
        company_id=str(company_id),
        values=values,
        provider=provider,
        maturity=maturity,
        tech_maturity=tech_mat,
        unlocked=unlocked_sorted,
    )


def extract_design_features(design_or_features: Mapping[str, Any]) -> Dict[str, Any]:
    """Convert either an AircraftDesign dict (00 §4.2) or a flat {effect_key: value} dict into {effect_key: value}."""
    # If all keys already look like effect keys (contain a dot and are in catalog), copy directly
    cat = load_catalog()
    if all(k in cat.keys for k in design_or_features.keys()) and len(design_or_features) > 0:
        return dict(design_or_features)

    features: Dict[str, Any] = {}
    wing = design_or_features.get("wing") or {}
    if "sweep_deg" in wing:
        features["aero.wing_sweep_max_deg"] = float(wing["sweep_deg"])
    elif "sweep_qc_deg" in wing:
        features["aero.wing_sweep_max_deg"] = float(wing["sweep_qc_deg"])
    if "tc_ratio" in wing:
        features["aero.thin_wing_tc_min"] = float(wing["tc_ratio"])
    elif "t_over_c" in wing:
        features["aero.thin_wing_tc_min"] = float(wing["t_over_c"])
    if "aspect_ratio" in wing:
        features["aero.aspect_ratio_min"] = float(wing["aspect_ratio"])
    if wing.get("planform") == "delta" or wing.get("delta_wing"):
        features["aero.delta_wing"] = True
    if wing.get("variable_sweep"):
        features["aero.variable_sweep"] = True
    if wing.get("conical_camber"):
        features["aero.conical_camber"] = True
    devices = set(wing.get("devices") or [])
    if "le_slats" in devices:
        features["aero.le_slats"] = True
    if "le_flaps" in devices:
        features["aero.le_flaps"] = True
    if "blown_flaps" in devices:
        features["aero.blown_flaps"] = True
    if "fowler_flaps" in devices:
        features["aero.fowler_flaps"] = True

    fuselage = design_or_features.get("fuselage") or {}
    if fuselage.get("area_ruled"):
        features["aero.area_rule"] = True

    emp = design_or_features.get("empennage") or {}
    if emp.get("all_moving_tail"):
        features["aero.all_moving_tail"] = True
    if emp.get("t_tail"):
        features["aero.t_tail"] = True

    intake = design_or_features.get("intake") or {}
    if intake.get("spike") or intake.get("type") == "shock_cone":
        features["aero.inlet_spike"] = True
    if intake.get("variable"):
        features["aero.inlet_variable"] = True

    prop = design_or_features.get("propulsion") or {}
    if prop.get("afterburner"):
        features["aero.afterburner_used"] = False  # handled below
        features["engine.afterburner"] = True

    struct = design_or_features.get("structure") or {}
    if "design_load_factor_g" in struct:
        features["struct.design_load_max_g"] = float(struct["design_load_factor_g"])
    mat_mix = struct.get("material_mix") or {}
    ti_frac = float(mat_mix.get("ti", 0.0))
    if ti_frac > 0.0:
        features["struct.material.titanium_available"] = True
        features["struct.material.ti_max_fraction"] = ti_frac
    steel_frac = float(mat_mix.get("steel", 0.0))
    if steel_frac > 0.0:
        features["struct.material.steel_max_fraction"] = steel_frac
    if struct.get("honeycomb"):
        features["struct.honeycomb"] = True

    systems = design_or_features.get("systems") or {}
    if "avionics_level" in systems:
        features["avionics.level_max"] = int(systems["avionics_level"])
    radar_id = systems.get("radar_id")
    if radar_id:
        features["avionics.radar_search"] = True
        features[f"unlock.radar.{radar_id}"] = True
    if systems.get("lead_collision_fcs"):
        features["avionics.lead_collision_fcs"] = True
    if systems.get("datalink_ground"):
        features["avionics.datalink_ground"] = True
    if systems.get("irst"):
        features["avionics.irst"] = True
    if systems.get("powered_controls"):
        features["systems.powered_controls"] = True
    if systems.get("stability_augmentation"):
        features["systems.stability_augmentation"] = True
    if systems.get("ejection_seat"):
        features["systems.ejection_seat"] = True
    if systems.get("inflight_refuel"):
        features["systems.inflight_refuel"] = True
    if systems.get("pressurized_cockpit"):
        features["systems.pressurized_cockpit"] = True

    arm = design_or_features.get("armament") or {}
    if "hardpoints" in arm:
        features["armament.hardpoints_max"] = int(arm["hardpoints"])
    if arm.get("internal_bay"):
        features["armament.internal_bay"] = True
    for g in arm.get("guns") or []:
        gid = g["id"] if isinstance(g, Mapping) else str(g)
        features[f"unlock.gun.{gid}"] = True
    for r in arm.get("rocket_ids") or []:
        features[f"unlock.rocket.{r}"] = True
    for m in arm.get("missile_ids") or []:
        features[f"unlock.missile.{m}"] = True

    # Also allow explicit effect keys at top level of design_or_features
    for k, v in design_or_features.items():
        if k in cat.keys:
            features[k] = v

    features.pop("aero.afterburner_used", None)
    return features


def required_techs_by_feature(
    design_or_features: Mapping[str, Any],
    ctx: TechContext,
    catalog: Optional[TechCatalog] = None,
) -> Dict[str, str]:
    """Return {effect_key: sufficient_provider_tech_id} for every capped feature exceeding null_value.

    Raises ValueError('TECH_CAP:<key>') if a requested feature exceeds the unlocked cap in ctx.
    """
    cat = catalog if catalog is not None else load_catalog()
    eps = cat.tunables.get("float_cap_epsilon", 1e-6)
    features = extract_design_features(design_or_features)

    result: Dict[str, str] = {}
    for key, req_val in sorted(features.items()):
        spec: EffectKeySpec = cat.get_key_spec(key)
        if spec.agg == "or":
            if not bool(req_val):
                continue
            if bool(spec.null_value) is True:
                continue
            if not ctx.allows(key, True, eps=eps):
                raise ValueError(f"TECH_CAP:{key}")
            prov = ctx.provider.get(key)
            if prov is not None:
                result[key] = prov

        elif spec.agg == "max":
            f_req = float(req_val)
            f_null = float(spec.null_value)
            if f_req <= f_null + eps:
                continue
            if not ctx.allows(key, f_req, eps=eps):
                raise ValueError(f"TECH_CAP:{key}")
            # Minimal sufficient unlocked tech: smallest effects[key] >= f_req - eps
            # Ties broken by highest maturity, then tech_id sort
            candidates: List[Tuple[float, float, str]] = []
            for tid in ctx.unlocked:
                node = cat.nodes[tid]
                if key in node.effects:
                    n_val = float(node.effects[key])
                    if n_val >= f_req - eps:
                        candidates.append((n_val, -ctx.tech_maturity[tid], tid))
            if not candidates:
                raise ValueError(f"TECH_CAP:{key}")
            candidates.sort()
            result[key] = candidates[0][2]

        elif spec.agg == "min":
            f_req = float(req_val)
            f_null = float(spec.null_value)
            if f_req >= f_null - eps:
                continue
            if not ctx.allows(key, f_req, eps=eps):
                raise ValueError(f"TECH_CAP:{key}")
            # Minimal sufficient unlocked tech: largest effects[key] <= f_req + eps
            # (closest to null_value while still allowing f_req)
            candidates_min: List[Tuple[float, float, str]] = []
            for tid in ctx.unlocked:
                node = cat.nodes[tid]
                if key in node.effects:
                    n_val = float(node.effects[key])
                    if n_val <= f_req + eps:
                        candidates_min.append((-n_val, -ctx.tech_maturity[tid], tid))
            if not candidates_min:
                raise ValueError(f"TECH_CAP:{key}")
            candidates_min.sort()
            result[key] = candidates_min[0][2]

    return result


def required_techs(
    design_or_features: Mapping[str, Any],
    ctx: TechContext,
    catalog: Optional[TechCatalog] = None,
) -> List[str]:
    """Return sorted unique list of provider tech IDs relied upon by design_or_features (03a §1.2 #4)."""
    by_feat = required_techs_by_feature(design_or_features, ctx, catalog=catalog)
    return sorted(set(by_feat.values()))
