"""YAML + pydantic configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, model_validator


class AgentsConfig(BaseModel):
    citizens: int = Field(ge=1, default=2000)
    factories: int = Field(ge=1, default=50)


class GammaSalary(BaseModel):
    shape: float = 3.0
    scale: float = 10.0


class NormalSalary(BaseModel):
    mean: float = 45.0
    std: float = 10.0


class CommunistSalary(BaseModel):
    low: int = 10
    high: int = 100


class SalaryConfig(BaseModel):
    model: Literal["gamma", "normal", "communist", "employment"] = "gamma"
    gamma: GammaSalary = Field(default_factory=GammaSalary)
    normal: NormalSalary = Field(default_factory=NormalSalary)
    communist: CommunistSalary = Field(default_factory=CommunistSalary)
    # employment: wage share of previous-period revenue per worker (when feature on)
    wage_share_of_revenue: float = Field(default=0.3, ge=0.0, le=1.0)
    unemployment_benefit: float = Field(default=0.0, ge=0.0)


class NormalDist(BaseModel):
    dist: Literal["normal"] = "normal"
    mean: float
    std: float = Field(ge=0.0)


class UniformIntDist(BaseModel):
    dist: Literal["uniform_int"] = "uniform_int"
    min: int
    max: int

    @model_validator(mode="after")
    def max_ge_min(self) -> UniformIntDist:
        if self.max < self.min:
            raise ValueError("max must be >= min")
        return self


FactoryCapitalInit = NormalDist
FactoryQualityInit = UniformIntDist
FactoryCostInit = UniformIntDist


class FactoryInitConfig(BaseModel):
    capital: NormalDist = Field(
        default_factory=lambda: NormalDist(mean=1000.0, std=300.0)
    )
    max_quality: UniformIntDist = Field(
        default_factory=lambda: UniformIntDist(min=2, max=30)
    )
    cost: UniformIntDist = Field(
        default_factory=lambda: UniformIntDist(min=5, max=100)
    )


class ConsumerNoise(BaseModel):
    price_std: float = Field(default=0.0, ge=0.0)
    quality_std: float = Field(default=0.0, ge=0.0)


class ConsumerConfig(BaseModel):
    rationality: float = Field(default=1.0, ge=0.0, le=1.0)
    noise: ConsumerNoise = Field(default_factory=ConsumerNoise)
    # matches smith.py global min_qv for selection (0), not factory init range
    selection_min_quality: int = 0
    selection_max_price: float = 10000.0


class NormalAddon(BaseModel):
    mean: float
    std: float = Field(ge=0.0)


class ModernisationConfig(BaseModel):
    capital_addon: NormalAddon = Field(
        default_factory=lambda: NormalAddon(mean=-100.0, std=50.0)
    )
    cost_addon: NormalAddon = Field(
        default_factory=lambda: NormalAddon(mean=0.0, std=5.0)
    )
    quality_addon: NormalAddon = Field(
        default_factory=lambda: NormalAddon(mean=0.0, std=3.0)
    )


class PricingConfig(BaseModel):
    markup: float = Field(default=1.0, description="price = cost + markup (smith uses 1)")


class FeaturesConfig(BaseModel):
    employment: bool = False
    bankrupt_layoffs: bool = False


class Config(BaseModel):
    seed: int = 42
    periods: int = Field(default=30, ge=1)
    agents: AgentsConfig = Field(default_factory=AgentsConfig)
    salary: SalaryConfig = Field(default_factory=SalaryConfig)
    factory_init: FactoryInitConfig = Field(default_factory=FactoryInitConfig)
    consumer: ConsumerConfig = Field(default_factory=ConsumerConfig)
    modernisation: ModernisationConfig = Field(default_factory=ModernisationConfig)
    pricing: PricingConfig = Field(default_factory=PricingConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)

    model_config = {"extra": "forbid"}


def load_config(path: str | Path) -> Config:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("YAML root must be a mapping")
    return Config.model_validate(raw)


def config_from_dict(data: dict[str, Any]) -> Config:
    return Config.model_validate(data)
