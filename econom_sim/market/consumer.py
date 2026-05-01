"""Consumer choice: rational (smith) + optional irrationality."""

from __future__ import annotations

from econom_sim.config import Config
from econom_sim.domain import Citizen, Product
from econom_sim.rng import Rng


def _rational_choice(
    citizen: Citizen,
    products: list[Product],
    min_qv: int,
    max_price: float,
) -> Product:
    """Exact smith.py logic (best quality among affordable, then cheapest)."""
    fun_result = Product(id=-1)
    available: list[Product] = []
    for pr in products:
        if citizen.money >= pr.price:
            available.append(pr)

    best_price = max_price
    best_qv = float(min_qv)
    for pr in available:
        if pr.quality >= best_qv:
            best_qv = pr.quality

    product_qv_lst = [pr for pr in available if pr.quality == best_qv]
    for pr in product_qv_lst:
        if pr.price <= best_price:
            best_price = pr.price

    for pr in product_qv_lst:
        if pr.price == best_price:
            return pr
    return fun_result


def _perceived(
    pr: Product,
    cfg: Config,
    rng: Rng,
) -> tuple[float, float]:
    n = cfg.consumer.noise
    p_noise = rng.normalvariate(0.0, n.price_std) if n.price_std > 0 else 0.0
    q_noise = rng.normalvariate(0.0, n.quality_std) if n.quality_std > 0 else 0.0
    perceived_price = pr.price * (1.0 + p_noise)
    perceived_quality = pr.quality + q_noise
    return perceived_price, perceived_quality


def consume(
    citizen: Citizen,
    products: list[Product],
    cfg: Config,
    rng: Rng,
) -> Product:
    rat = cfg.consumer.rationality
    if rat < 1.0 and rng.random() > rat:
        affordable = [pr for pr in products if citizen.money >= pr.price]
        if not affordable:
            return Product(id=-1)
        return rng.choice(affordable)

    if cfg.consumer.noise.price_std > 0 or cfg.consumer.noise.quality_std > 0:
        best: Product | None = None
        best_pq = -1e18
        best_pp = 1e18
        for pr in products:
            if citizen.money < pr.price:
                continue
            pp, pq = _perceived(pr, cfg, rng)
            if pq > best_pq or (pq == best_pq and pp < best_pp):
                best_pq = pq
                best_pp = pp
                best = pr
        if best is not None and best.id >= 0:
            return best

    return _rational_choice(
        citizen,
        products,
        cfg.consumer.selection_min_quality,
        cfg.consumer.selection_max_price,
    )
