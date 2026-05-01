"""Initial and per-period salary logic."""

from __future__ import annotations

from econom_sim.config import Config, SalaryConfig
from econom_sim.domain import Citizen
from econom_sim.rng import Rng


def initial_money(cfg: SalaryConfig, rng: Rng) -> float:
    if cfg.model == "gamma":
        g = cfg.gamma
        return round(rng.gammavariate(g.shape, g.scale), 2)
    if cfg.model == "normal":
        n = cfg.normal
        return round(rng.normalvariate(n.mean, n.std), 2)
    if cfg.model == "communist":
        c = cfg.communist
        return float(rng.randint(c.low, c.high))
    # employment: starting money 0 or benefit; first wage at period 0 handled in employment
    if cfg.model == "employment":
        return round(cfg.unemployment_benefit, 2)
    raise ValueError(f"Unknown salary model: {cfg.model}")


def spawn_citizen(citizen_id: int, cfg: Config, rng: Rng) -> Citizen:
    money = initial_money(cfg.salary, rng)
    return Citizen(id=citizen_id, money=money, employer_id=None)
