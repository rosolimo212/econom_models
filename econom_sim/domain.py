"""Core domain types."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Product:
    id: int = -1
    quality: float = -100.0
    price: float = -10000.0


@dataclass
class Citizen:
    id: int
    money: float
    employer_id: int | None = None  # factory id when employment feature on


@dataclass
class Factory:
    id: int
    max_quality: float
    cost: float
    capital: float
    pur: int = 0
    price: float = 0.0
    capital_history: list[float] = field(default_factory=list)
    cost_history: list[float] = field(default_factory=list)
    quality_history: list[float] = field(default_factory=list)
    pur_history: list[int] = field(default_factory=list)
    price_history: list[float] = field(default_factory=list)
    last_revenue: float = 0.0  # previous full period gross sales (for wages)
    period_revenue: float = 0.0  # accumulates during current period trades

    def is_solvent(self) -> bool:
        return self.capital > 0
