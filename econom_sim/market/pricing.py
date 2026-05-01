"""Product pricing rules."""

from __future__ import annotations

from econom_sim.config import Config
from econom_sim.domain import Factory, Product


def produce_one(factory: Factory, cfg: Config) -> Product:
    if not factory.is_solvent():
        factory.price = -10000.0
        return Product(id=-1)
    price = factory.cost + cfg.pricing.markup
    quality = factory.max_quality
    if price > factory.cost and quality <= factory.max_quality and factory.is_solvent():
        factory.price = price
        return Product(id=factory.id, quality=quality, price=price)
    factory.price = -10000.0
    return Product(id=-1)
