"""Execution of sales at factories."""

from __future__ import annotations

from econom_sim.config import Config
from econom_sim.domain import Citizen, Factory, Product


def factory_trade(factory: Factory) -> None:
    """smith.py trade(): subtract cost, then if still solvent count sale and add price."""
    factory.capital = factory.capital - factory.cost
    if factory.is_solvent():
        factory.pur = factory.pur + 1
        factory.capital = factory.capital + factory.price
        factory.period_revenue = round(factory.period_revenue + factory.price, 2)


def apply_trade(
    good: Product,
    citizen_index: int,
    citizens: list[Citizen],
    factories: list[Factory],
    cfg: Config,
) -> None:
    if good.id < 0:
        return
    factory = factories[good.id]
    factory_trade(factory)
    if cfg.features.employment and cfg.salary.model == "employment":
        c = citizens[citizen_index]
        c.money = round(c.money - good.price, 2)
