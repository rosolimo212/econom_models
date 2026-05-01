"""Factory modernisation (smith.py logic)."""

from __future__ import annotations

import numpy as np

from econom_sim.config import Config
from econom_sim.domain import Factory
from econom_sim.rng import Rng


def get_modern_params(cfg: Config, rng: Rng) -> tuple[float, float, float]:
    m = cfg.modernisation
    capital_addon = round(rng.normalvariate(m.capital_addon.mean, m.capital_addon.std), 2)
    if capital_addon > 0:
        capital_addon = -10.0
    cost_addon = round(rng.normalvariate(m.cost_addon.mean, m.cost_addon.std), 2)
    qv_addon = round(rng.normalvariate(m.quality_addon.mean, m.quality_addon.std), 0)
    return qv_addon, cost_addon, capital_addon


def modernise_process(
    factory: Factory,
    qv_addon: float,
    cost_addon: float,
    capital_addon: float,
) -> None:
    if factory.capital + capital_addon > 0:
        if factory.max_quality + qv_addon > 0:
            factory.max_quality = float(np.round(factory.max_quality + qv_addon, 0))
        if factory.cost + cost_addon > 0:
            factory.cost = float(np.round(factory.cost + cost_addon, 2))
        factory.capital = float(np.round(factory.capital + capital_addon, 2))


def modernise(factory: Factory, cfg: Config, rng: Rng) -> None:
    qv_addon, cost_addon, capital_addon = get_modern_params(cfg, rng)
    if len(factory.pur_history) > 1:
        if factory.pur_history[-1] == 0 and factory.pur_history[-2] > 0:
            factory.max_quality = factory.quality_history[-2]
            factory.cost = factory.cost_history[-2]
        else:
            modernise_process(factory, qv_addon, cost_addon, capital_addon)
    else:
        modernise_process(factory, qv_addon, cost_addon, capital_addon)
