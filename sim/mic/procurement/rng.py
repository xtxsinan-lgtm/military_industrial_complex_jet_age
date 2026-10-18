"""Deterministic random number stream wrapper for Module 05 (Procurement).

Designed for exact cross-language reproducibility between Python and C#:
- Can wrap a numpy.random.Generator, a list/iterable of fixed uniform floats in (0, 1)
  (used in golden test vectors), or a deterministic zero-noise mode.
- Normal draws use an explicit Box-Muller transform consuming two uniform draws u1, u2
  per call (no cached spare value) so call sequences are stateless and trivial to mirror in C#.
"""
from __future__ import annotations

import math
from typing import Iterable, Iterator, List, Optional, Union
import numpy as np


class RandomSource:
    """Minimal uniform + normal random source with deterministic Box-Muller transform."""

    def __init__(
        self,
        source: Optional[Union[np.random.Generator, Iterable[float], int]] = None,
        deterministic: bool = False,
    ) -> None:
        self.deterministic = deterministic
        self._iter: Optional[Iterator[float]] = None
        self._rng: Optional[np.random.Generator] = None
        self._consumed: List[float] = []

        if deterministic:
            return
        if source is None:
            self._rng = np.random.default_rng(19450101)
        elif isinstance(source, (int, np.integer)):
            self._rng = np.random.default_rng(int(source))
        elif isinstance(source, np.random.Generator):
            self._rng = source
        else:
            self._iter = iter(source)

    @property
    def consumed_uniforms(self) -> List[float]:
        """Return list of raw uniform(0, 1) draws consumed so far (for golden vector recording)."""
        return list(self._consumed)

    def uniform(self) -> float:
        """Draw a single uniform float in (0, 1)."""
        if self.deterministic:
            return 0.5
        if self._iter is not None:
            try:
                u = float(next(self._iter))
            except StopIteration as exc:
                raise RuntimeError("RandomSource exhausted fixed uniform sequence") from exc
        else:
            assert self._rng is not None
            u = float(self._rng.random())
        # Clamp away from exact 0.0 or 1.0 for Box-Muller log safety
        u = min(max(u, 1e-12), 1.0 - 1e-12)
        self._consumed.append(u)
        return u

    def normal(self, mean: float = 0.0, sd: float = 1.0) -> float:
        """Draw a normal variate N(mean, sd^2) via stateless Box-Muller using 2 uniform draws."""
        if self.deterministic or sd <= 0.0:
            return float(mean)
        u1 = self.uniform()
        u2 = self.uniform()
        z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return float(mean + sd * z)
