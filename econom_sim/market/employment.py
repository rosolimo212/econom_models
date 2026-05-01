"""Workers at factories: assignment and wages from factory capital."""

from __future__ import annotations

from econom_sim.config import Config
from econom_sim.domain import Citizen, Factory
from econom_sim.rng import Rng


def assign_workers(citizens: list[Citizen], factories: list[Factory], rng: Rng) -> None:
    if not factories:
        return
    ids = list(range(len(factories)))
    for c in citizens:
        c.employer_id = rng.choice(ids)


def pay_wages(
    citizens: list[Citizen],
    factories: list[Factory],
    cfg: Config,
    rng: Rng,
) -> None:
    """Pay workers from employer capital based on last period revenue."""
    if not cfg.features.employment or cfg.salary.model != "employment":
        return
    share = cfg.salary.wage_share_of_revenue
    # group by factory
    by_emp: dict[int, list[Citizen]] = {}
    for c in citizens:
        eid = c.employer_id
        if eid is None:
            continue
        by_emp.setdefault(eid, []).append(c)

    for fid, workers in by_emp.items():
        if fid < 0 or fid >= len(factories):
            continue
        f = factories[fid]
        if not workers:
            continue
        pool = max(0.0, float(f.last_revenue) * share)
        if pool <= 0 or not f.is_solvent():
            continue
        per = pool / len(workers)
        per = min(per, max(0.0, f.capital * 0.99))  # avoid zeroing accidentally
        total = 0.0
        for w in workers:
            pay = min(per, f.capital - total) if f.capital > total else 0.0
            w.money = round(w.money + pay, 2)
            total += pay
        f.capital = round(f.capital - total, 2)


def layoff_from_bankrupt(
    citizens: list[Citizen],
    factories: list[Factory],
    cfg: Config,
    _rng: Rng,
) -> None:
    if not cfg.features.employment or not cfg.features.bankrupt_layoffs:
        return
    bankrupt_ids = {f.id for f in factories if not f.is_solvent()}
    for c in citizens:
        if c.employer_id is not None and c.employer_id in bankrupt_ids:
            c.employer_id = None
            c.money = round(c.money + cfg.salary.unemployment_benefit, 2)


def reassign_unemployed(
    citizens: list[Citizen],
    factories: list[Factory],
    cfg: Config,
    rng: Rng,
) -> None:
    if not cfg.features.employment or cfg.salary.model != "employment":
        return
    solvent = [f.id for f in factories if f.is_solvent()]
    if not solvent:
        return
    for c in citizens:
        if c.employer_id is None:
            c.employer_id = rng.choice(solvent)
