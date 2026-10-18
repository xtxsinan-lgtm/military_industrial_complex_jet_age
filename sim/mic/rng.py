"""Bit-exact deterministic RNG (PCG32 / PCG-XSH-RR) and named stream registry.

Owned by Module 09 (`docs/spec/09_core_loop.md`).
Designed so Python 3.9+ and C# (`MIC.Core`) produce identical sequences bit-for-bit.
"""

from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple, TypeVar

T = TypeVar("T")

MASK64: int = 0xFFFFFFFFFFFFFFFF
MASK32: int = 0xFFFFFFFF

PCG32_MULT: int = 6364136223846793005  # 0x5851F42D4C957F2D
PCG32_DEFAULT_STATE: int = 0x853C49E6748FEA9B
PCG32_DEFAULT_SEQ: int = 0xDA3E39CB94B95BDB

FNV1A_64_OFFSET_BASIS: int = 0xCBF29CE484222325
FNV1A_64_PRIME: int = 0x00000100000001B3

# Exact IEEE-754 binary64 constants
INV_2_POW_53: float = 1.0 / 9007199254740992.0  # 2**-53
MIN_POSITIVE_U53: float = 1.1102230246251565e-16  # 2**-53 (floor for Box-Muller log)
TWO_PI: float = 6.283185307179586  # 2.0 * math.pi


def fnv1a_64(text: str) -> int:
    """Compute canonical 64-bit FNV-1a hash of a UTF-8 string."""
    h = FNV1A_64_OFFSET_BASIS
    for byte in text.encode("utf-8"):
        h ^= byte
        h = (h * FNV1A_64_PRIME) & MASK64
    return h


def u64_to_hex(val: int) -> str:
    """Format an unsigned 64-bit integer as a 16-char lowercase hex string with 0x prefix."""
    return f"0x{(int(val) & MASK64):016x}"


def hex_to_u64(text: str) -> int:
    """Parse a hex string (with or without 0x prefix) or integer into uint64."""
    if isinstance(text, int):
        return text & MASK64
    s = str(text).strip().lower()
    if s.startswith("0x"):
        return int(s, 16) & MASK64
    return int(s, 10) & MASK64


class PCG32:
    """Canonical PCG-XSH-RR (64-bit state, 32-bit output) pseudorandom number generator.

    Matches M. E. O'Neill's reference C implementation (`pcg32_srandom_r`, `pcg32_random_r`,
    `pcg32_boundedrand_r`).
    """

    __slots__ = ("state", "inc")

    def __init__(
        self,
        initstate: int = PCG32_DEFAULT_STATE,
        initseq: int = PCG32_DEFAULT_SEQ,
        *,
        _raw: bool = False,
    ) -> None:
        if _raw:
            self.state: int = int(initstate) & MASK64
            self.inc: int = int(initseq) & MASK64
            if (self.inc & 1) == 0:
                raise ValueError("PCG32 raw inc must be odd")
        else:
            self.state = 0
            self.inc = ((int(initseq) << 1) | 1) & MASK64
            self.next_u32()
            self.state = (self.state + (int(initstate) & MASK64)) & MASK64
            self.next_u32()

    @classmethod
    def from_raw_state(cls, state: int, inc: int) -> "PCG32":
        """Reconstruct a PCG32 directly from its internal (state, inc) without re-seeding."""
        return cls(state, inc, _raw=True)

    @classmethod
    def from_stream_name(cls, master_seed: int, stream_name: str) -> "PCG32":
        """Derive a deterministic PCG32 stream from a master seed and canonical stream name."""
        h = fnv1a_64(stream_name)
        initstate = (int(master_seed) ^ h) & MASK64
        initseq = h
        return cls(initstate, initseq)

    def clone(self) -> "PCG32":
        """Return an exact copy of this generator."""
        return PCG32(self.state, self.inc, _raw=True)

    def next_u32(self) -> int:
        """Generate the next 32-bit unsigned integer in [0, 2**32 - 1]."""
        oldstate = self.state
        self.state = (oldstate * PCG32_MULT + self.inc) & MASK64
        xorshifted = (((oldstate >> 18) ^ oldstate) >> 27) & MASK32
        rot = (oldstate >> 59) & 0x1F
        return ((xorshifted >> rot) | ((xorshifted << ((-rot) & 31)) & MASK32)) & MASK32

    def next_u64(self) -> int:
        """Generate a 64-bit unsigned integer from two sequential 32-bit draws (high then low)."""
        hi = self.next_u32()
        lo = self.next_u32()
        return ((hi << 32) | lo) & MASK64

    def next_float(self) -> float:
        """Generate a uniform IEEE-754 float64 in [0.0, 1.0) with 53-bit significand precision."""
        u64 = self.next_u64()
        return (u64 >> 11) * INV_2_POW_53

    def uniform(self, low: float = 0.0, high: float = 1.0) -> float:
        """Sample uniformly in [low, high)."""
        u = self.next_float()
        return float(low) + (float(high) - float(low)) * u

    def next_bounded(self, bound: int) -> int:
        """Unbiased integer in [0, bound) using Lemire/O'Neill rejection method (`pcg32_boundedrand_r`)."""
        b = int(bound)
        if b <= 0 or b > (1 << 32):
            raise ValueError(f"bound must be in [1, 2**32], got {bound}")
        threshold = ((1 << 32) - b) % b
        while True:
            r = self.next_u32()
            if r >= threshold:
                return r % b

    def randint(self, low: int, high: int) -> int:
        """Sample an unbiased integer in the half-open interval [low, high)."""
        lo = int(low)
        hi = int(high)
        if hi <= lo:
            raise ValueError(f"high ({high}) must be > low ({low})")
        return lo + self.next_bounded(hi - lo)

    def randint_inclusive(self, low: int, high: int) -> int:
        """Sample an unbiased integer in the closed interval [low, high]."""
        lo = int(low)
        hi = int(high)
        if hi < lo:
            raise ValueError(f"high ({high}) must be >= low ({low})")
        return lo + self.next_bounded(hi - lo + 1)

    def bernoulli(self, p: float) -> bool:
        """Return True with probability p in [0, 1]. Always consumes exactly one float draw."""
        u = self.next_float()
        return u < float(p)

    def normal(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Sample from N(mu, sigma^2) using stateless Box-Muller transform.

        Always consumes exactly two `next_float()` draws (four `next_u32()` draws) with
        no rejection loop and no cached spare value, guaranteeing stream synchronization
        and a 16-byte serialization state.
        """
        u1 = self.next_float()
        u2 = self.next_float()
        if u1 <= MIN_POSITIVE_U53:
            u1 = MIN_POSITIVE_U53
        r = math.sqrt(-2.0 * math.log(u1))
        theta = TWO_PI * u2
        z0 = r * math.cos(theta)
        return float(mu) + float(sigma) * z0

    def choice(self, seq: Sequence[T]) -> T:
        """Select one element uniformly from a non-empty sequence."""
        n = len(seq)
        if n == 0:
            raise ValueError("Cannot choose from an empty sequence")
        idx = self.next_bounded(n)
        return seq[idx]

    def weighted_choice(self, items: Sequence[T], weights: Sequence[float]) -> T:
        """Select one element with probability proportional to `weights`.

        Uses sequential left-to-right float64 addition for deterministic cross-language behavior.
        """
        n = len(items)
        if n == 0 or n != len(weights):
            raise ValueError("items and weights must be non-empty and of equal length")
        total = 0.0
        last_positive_idx = -1
        for i in range(n):
            w = float(weights[i])
            if math.isnan(w) or math.isinf(w) or w < 0.0:
                raise ValueError(f"Invalid weight at index {i}: {w}")
            if w > 0.0:
                total += w
                last_positive_idx = i
        if total <= 0.0 or last_positive_idx < 0:
            raise ValueError("Sum of weights must be > 0")

        target = self.next_float() * total
        acc = 0.0
        for i in range(n):
            w = float(weights[i])
            if w <= 0.0:
                continue
            acc += w
            if target < acc:
                return items[i]
        return items[last_positive_idx]

    def shuffle(self, seq: List[T]) -> None:
        """In-place Fisher-Yates shuffle."""
        for i in range(len(seq) - 1, 0, -1):
            j = self.next_bounded(i + 1)
            seq[i], seq[j] = seq[j], seq[i]

    def to_dict(self) -> Dict[str, str]:
        """Serialize internal state using hex strings to avoid JSON float53 truncation."""
        return {
            "state": u64_to_hex(self.state),
            "inc": u64_to_hex(self.inc),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "PCG32":
        """Deserialize internal state from `to_dict()` representation."""
        return cls.from_raw_state(
            hex_to_u64(data["state"]),
            hex_to_u64(data["inc"]),
        )


def mtth_prob(mtth_days: float, dt_days: int = 1) -> float:
    """Compute exact probability that an exponential event with half-life `mtth_days` fires in `dt_days`.

    Follows Paradox-style MTTH convention where `mtth_days` is the median time to happen
    (probability 0.5 of firing within `mtth_days` days):
        p = 1 - 2**(-dt_days / mtth_days) = 1 - exp(-ln(2) * dt_days / mtth_days)
    """
    if dt_days <= 0:
        return 0.0
    if mtth_days <= 0.0:
        return 1.0
    exponent = -math.log(2.0) * (float(dt_days) / float(mtth_days))
    if exponent <= -700.0:
        return 0.0
    p = -math.expm1(exponent)
    if p < 0.0:
        return 0.0
    if p > 1.0:
        return 1.0
    return p


class RngStreamRegistry:
    """Deterministic registry of named `PCG32` streams derived from a single campaign master seed.

    Because each stream's initial state depends ONLY on `(master_seed, stream_name)` via
    FNV-1a 64-bit hashing, the sequence of values produced by stream `"A"` is completely
    independent of when or whether stream `"B"` is accessed.
    """

    def __init__(self, master_seed: int) -> None:
        self.master_seed: int = int(master_seed) & MASK64
        self._streams: Dict[str, PCG32] = {}

    def stream(self, name: str) -> PCG32:
        """Return (or lazily initialize) the named `PCG32` stream."""
        if not name or not isinstance(name, str):
            raise ValueError("Stream name must be a non-empty string")
        rng = self._streams.get(name)
        if rng is None:
            rng = PCG32.from_stream_name(self.master_seed, name)
            self._streams[name] = rng
        return rng

    def stream_names(self) -> List[str]:
        """Return currently materialized stream names in canonical sorted order."""
        return sorted(self._streams.keys())

    def to_dict(self) -> Dict[str, object]:
        """Serialize master seed and all materialized streams in sorted key order."""
        return {
            "master_seed": u64_to_hex(self.master_seed),
            "streams": {k: self._streams[k].to_dict() for k in sorted(self._streams.keys())},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "RngStreamRegistry":
        """Restore a registry from serialized state."""
        master_seed = hex_to_u64(str(data["master_seed"]))
        reg = cls(master_seed)
        streams_raw = data.get("streams", {})
        if isinstance(streams_raw, dict):
            for k in sorted(streams_raw.keys()):
                reg._streams[k] = PCG32.from_dict(streams_raw[k])
        return reg
