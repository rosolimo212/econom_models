"""Deterministic RNG facade (single Random instance per simulation)."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class Rng:
    seed: int
    _r: random.Random | None = None

    def __post_init__(self) -> None:
        self._r = random.Random(self.seed)

    def fork(self, salt: str) -> random.Random:
        """Child stream for isolated subsystems (same seed + salt)."""
        r = random.Random()
        r.seed((self.seed, salt), version=2)
        return r

    def gammavariate(self, alpha: float, beta: float) -> float:
        assert self._r is not None
        return self._r.gammavariate(alpha, beta)

    def normalvariate(self, mu: float, sigma: float) -> float:
        assert self._r is not None
        return self._r.normalvariate(mu, sigma)

    def randint(self, a: int, b: int) -> int:
        assert self._r is not None
        return self._r.randint(a, b)

    def random(self) -> float:
        assert self._r is not None
        return self._r.random()

    def choice(self, seq: list):
        assert self._r is not None
        return self._r.choice(seq)

    def shuffle(self, x: list) -> None:
        assert self._r is not None
        self._r.shuffle(x)
