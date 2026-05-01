"""Aggregate metrics from period state."""

from __future__ import annotations

from econom_sim.domain import Citizen, Factory


def gini(values: list[float]) -> float:
    """Gini coefficient; 0 if empty or all zero."""
    arr = sorted(float(x) for x in values if x == x)
    n = len(arr)
    if n == 0:
        return 0.0
    s = sum(arr)
    if s == 0:
        return 0.0
    cum = 0.0
    weighted = 0.0
    for i, v in enumerate(arr, start=1):
        cum += v
        weighted += cum
    return (n + 1) / n - 2 * weighted / (s * n)


def compute_metrics(
    citizens: list[Citizen],
    factories: list[Factory],
    purchases: list[tuple[int, int, float, float]],
) -> dict:
    """
    purchases: list of (citizen_id, factory_id_or_-1, price, quality)
    """
    capitals = [f.capital for f in factories]
    moneys = [c.money for c in citizens]
    sold = [p for p in purchases if p[1] >= 0]
    prices = [p[2] for p in sold]
    qualities = [p[3] for p in sold]
    bankrupt = sum(1 for f in factories if not f.is_solvent())
    employed = sum(1 for c in citizens if c.employer_id is not None)
    return {
        "gini_factory_capital": round(gini(capitals), 6),
        "gini_citizen_money": round(gini(moneys), 6),
        "mean_price": round(sum(prices) / len(prices), 6) if prices else 0.0,
        "mean_quality": round(sum(qualities) / len(qualities), 6) if qualities else 0.0,
        "sales_count": len(sold),
        "bankrupt_factories": bankrupt,
        "employed_citizens": employed,
        "total_citizen_money": round(sum(moneys), 2),
        "total_factory_capital": round(sum(capitals), 2),
    }
