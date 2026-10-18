"""Deterministic counter-based hashing & 5D value noise for Module 06.

Identical 64-bit unsigned integer arithmetic in Python and C# guarantees:
1. Cross-language reproducibility within rel 1e-6.
2. Continuous 5D value noise so micro-tweaking continuous design parameters
   smoothly shifts TrueAircraft rather than rerolling luck.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence, Tuple, Union

MASK64 = 0xFFFFFFFFFFFFFFFF
FNV_OFFSET_BASIS_64 = 0xCBF29CE484222325
FNV_PRIME_64 = 0x100000001B3

KeyPart = Union[str, int]


def fnv1a_64(text: str) -> int:
    """Compute 64-bit FNV-1a hash of an ASCII/UTF-8 string."""
    h = FNV_OFFSET_BASIS_64
    for b in text.encode("utf-8"):
        h ^= b
        h = (h * FNV_PRIME_64) & MASK64
    return h


def mix64(x: int) -> int:
    """SplitMix64 finalizer bijective 64-bit mixer."""
    z = (x + 0x9E3779B97F4A7C15) & MASK64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
    return (z ^ (z >> 31)) & MASK64


def hash_keys(campaign_seed: int, *parts: KeyPart) -> int:
    """Fold an arbitrary sequence of int/str key parts into a 64-bit hash."""
    h = mix64(campaign_seed & MASK64)
    for p in parts:
        if isinstance(p, int):
            val = p & MASK64
        else:
            val = fnv1a_64(str(p))
        h = mix64(h ^ val)
    return h


def u01_from_hash(h: int) -> float:
    """Convert 64-bit hash to open interval (0, 1) using top 53 bits + 0.5 offset."""
    top53 = (h & MASK64) >> 11
    return (top53 + 0.5) / 9007199254740992.0  # 2**53


def keyed_u01(campaign_seed: int, *parts: KeyPart) -> float:
    """Deterministic uniform draw in (0, 1) for a given key tuple."""
    return u01_from_hash(hash_keys(campaign_seed, *parts))


def keyed_normal(campaign_seed: int, *parts: KeyPart) -> float:
    """Deterministic standard normal N(0, 1) draw via Box-Muller transform."""
    u1 = keyed_u01(campaign_seed, *parts, 0)
    u2 = keyed_u01(campaign_seed, *parts, 1)
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


def value_noise_5d(
    campaign_seed: int,
    company_id: str,
    driver_id: str,
    coords: Sequence[float],
) -> float:
    """Variance-normalized 5D multilinear value noise over continuous coordinates.

    Because linear interpolation between independent N(0, 1) lattice points has
    variance prod_j ((1 - alpha_j)^2 + alpha_j^2), dividing by its square root
    restores exact unit variance N(0, 1) at every continuous point x in R^5.
    """
    if len(coords) != 5:
        raise ValueError(f"Expected 5 coordinates, got {len(coords)}")

    floors = [int(math.floor(x)) for x in coords]
    alphas = [float(coords[j] - floors[j]) for j in range(5)]

    norm_sq = 1.0
    for a in alphas:
        norm_sq *= (1.0 - a) * (1.0 - a) + a * a

    base_h = hash_keys(campaign_seed, "vn5d", company_id, driver_id)
    total = 0.0
    for mask in range(32):
        w = 1.0
        h = base_h
        for j in range(5):
            bit = (mask >> j) & 1
            w *= alphas[j] if bit else (1.0 - alphas[j])
            h = mix64(h ^ ((floors[j] + bit) & MASK64))
        if w > 0.0:
            u1 = u01_from_hash(mix64(h ^ 0))
            u2 = u01_from_hash(mix64(h ^ 1))
            z_corner = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
            total += w * z_corner

    return total / math.sqrt(max(1e-12, norm_sq))


def driver_z_draw(
    campaign_seed: int,
    categorical_sig: str,
    company_id: str,
    driver_id: str,
    coords_5d: Sequence[float],
    categorical_weight: float = 0.50,
) -> float:
    """Blended standard-normal draw for driver `driver_id` (§5.1.2)."""
    rho = max(0.0, min(1.0, float(categorical_weight)))
    z_cat = keyed_normal(campaign_seed, "driver_cat", categorical_sig, driver_id)
    z_vn = value_noise_5d(campaign_seed, company_id, driver_id, coords_5d)
    return math.sqrt(rho) * z_cat + math.sqrt(1.0 - rho) * z_vn


def flaw_u01_draw(
    campaign_seed: int,
    categorical_sig: str,
    flaw_id: str,
) -> float:
    """Monotonic uniform threshold U_flaw in (0, 1) for flaw realization (§5.6.2)."""
    return keyed_u01(campaign_seed, "flaw_u01", categorical_sig, flaw_id)
