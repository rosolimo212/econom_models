"""Simulation engine: state + one period + full run generator."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from econom_sim.config import Config
from econom_sim.domain import Citizen, Factory, Product
from econom_sim.events import EventBus
from econom_sim.market import consumer as consumer_mod
from econom_sim.market import employment as emp_mod
from econom_sim.market import modernise as mod_mod
from econom_sim.market import pricing as price_mod
from econom_sim.market import salary as salary_mod
from econom_sim.market import trade as trade_mod
from econom_sim.metrics import compute_metrics
from econom_sim.rng import Rng


@dataclass
class PeriodSnapshot:
    period: int
    citizen_rows: list[dict[str, Any]]
    factory_rows: list[dict[str, Any]]
    metrics: dict[str, Any]


@dataclass
class SimulationState:
    cfg: Config
    rng: Rng
    citizens: list[Citizen]
    factories: list[Factory]
    current_period: int = 0
    bus: EventBus = field(default_factory=EventBus)


def _spawn_factory_legacy_triple(fid: int, cfg: Config, rng: Rng) -> Factory:
    """Match smith.py factory.__init__ (three independent set_params calls)."""
    fi = cfg.factory_init

    def triple() -> tuple[int, float, float]:
        mq = rng.randint(fi.max_quality.min, fi.max_quality.max)
        co = float(rng.randint(fi.cost.min, fi.cost.max))
        cap = round(rng.normalvariate(fi.capital.mean, fi.capital.std), 2)
        return mq, co, cap

    t1, t2, t3 = triple(), triple(), triple()
    max_quality = float(t1[0])
    cost = t2[1]
    capital = t3[2]
    return Factory(id=fid, max_quality=max_quality, cost=cost, capital=capital)


def init_state(cfg: Config, bus: EventBus | None = None) -> SimulationState:
    rng = Rng(cfg.seed)
    citizens = [
        salary_mod.spawn_citizen(i, cfg, rng) for i in range(cfg.agents.citizens)
    ]
    factories = [
        _spawn_factory_legacy_triple(i, cfg, rng) for i in range(cfg.agents.factories)
    ]
    if cfg.features.employment and cfg.salary.model == "employment":
        emp_mod.assign_workers(citizens, factories, rng)
    return SimulationState(
        cfg=cfg,
        rng=rng,
        citizens=citizens,
        factories=factories,
        current_period=0,
        bus=bus or EventBus(),
    )


def _produce_all(factories: list[Factory], cfg: Config) -> list[Product]:
    products: list[Product] = []
    for f in factories:
        if f.is_solvent():
            products.append(price_mod.produce_one(f, cfg))
        else:
            f.price = -10000.0
            products.append(Product(id=-1))
    return products


def _citizen_snapshot_pre_trade(
    state: SimulationState,
    goods: list[Product],
    period: int,
) -> tuple[list[dict[str, Any]], list[tuple[int, int, float, float]]]:
    """smith: cit_df uses money before trade."""
    citizen_rows: list[dict[str, Any]] = []
    purchases: list[tuple[int, int, float, float]] = []
    for i, good in enumerate(goods):
        c = state.citizens[i]
        citizen_rows.append(
            {
                "id": good.id,
                "quality": good.quality,
                "price": good.price,
                "citizen_id": c.id,
                "money": c.money,
                "period": period,
                "employer_id": c.employer_id,
            }
        )
        purchases.append((c.id, good.id, good.price, good.quality))
    return citizen_rows, purchases


def _factory_snapshot_post_trade(state: SimulationState, period: int) -> list[dict[str, Any]]:
    """smith: fact_df after global_trade, before hist."""
    factory_rows: list[dict[str, Any]] = []
    for f in state.factories:
        factory_rows.append(
            {
                "id": f.id,
                "max_quality": f.max_quality,
                "cost": f.cost,
                "capital": f.capital,
                "pur": f.pur,
                "price": f.price,
                "period": period,
                "last_revenue": f.last_revenue,
            }
        )
    return factory_rows


def _hist_and_reset(f: Factory) -> None:
    f.capital_history.append(f.capital)
    f.cost_history.append(f.cost)
    f.quality_history.append(f.max_quality)
    f.pur_history.append(f.pur)
    f.price_history.append(f.price)


def _to_null(f: Factory) -> None:
    f.price = 0.0
    f.pur = 0


def _roll_revenue(factories: list[Factory]) -> None:
    for f in factories:
        f.last_revenue = f.period_revenue
        f.period_revenue = 0.0


def run_period(state: SimulationState) -> PeriodSnapshot:
    """Advance one market period; mutates state."""
    cfg = state.cfg
    period = state.current_period
    state.bus.publish("period_start", period)

    emp_mod.layoff_from_bankrupt(state.citizens, state.factories, cfg, state.rng)
    emp_mod.reassign_unemployed(state.citizens, state.factories, cfg, state.rng)
    emp_mod.pay_wages(state.citizens, state.factories, cfg, state.rng)

    products = _produce_all(state.factories, cfg)
    goods: list[Product] = []
    for i, cit in enumerate(state.citizens):
        goods.append(consumer_mod.consume(cit, products, cfg, state.rng))

    citizen_rows, purchases = _citizen_snapshot_pre_trade(state, goods, period)

    for i, good in enumerate(goods):
        trade_mod.apply_trade(good, i, state.citizens, state.factories, cfg)

    factory_rows = _factory_snapshot_post_trade(state, period)
    metrics = compute_metrics(state.citizens, state.factories, purchases)
    snap = PeriodSnapshot(
        period=period,
        citizen_rows=citizen_rows,
        factory_rows=factory_rows,
        metrics=metrics,
    )
    state.bus.publish("snapshot", snap)

    for f in state.factories:
        _hist_and_reset(f)
        _to_null(f)
        mod_mod.modernise(f, cfg, state.rng)

    _roll_revenue(state.factories)
    state.current_period = period + 1
    state.bus.publish("period_end", period)
    return snap


def run(state: SimulationState) -> Iterator[PeriodSnapshot]:
    """Yield one snapshot per configured period (after trades, before modernise in metrics timing — snapshot matches pre-hist factory state)."""
    for _ in range(state.cfg.periods):
        yield run_period(state)


def run_from_config(cfg: Config, bus: EventBus | None = None) -> Iterator[PeriodSnapshot]:
    st = init_state(cfg, bus)
    yield from run(st)
