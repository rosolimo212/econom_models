import unittest

from econom_sim.config import config_from_dict
from econom_sim.domain import Citizen, Product
from econom_sim.market import consumer as consumer_mod
from econom_sim.rng import Rng


class TestConsumer(unittest.TestCase):
    def test_rationality_one_picks_best_quality_then_price(self) -> None:
        cfg = config_from_dict(
            {
                "seed": 0,
                "periods": 1,
                "agents": {"citizens": 1, "factories": 1},
                "salary": {"model": "gamma", "gamma": {"shape": 3, "scale": 10}},
                "factory_init": {
                    "capital": {"dist": "normal", "mean": 100, "std": 1},
                    "max_quality": {"dist": "uniform_int", "min": 5, "max": 5},
                    "cost": {"dist": "uniform_int", "min": 5, "max": 5},
                },
                "consumer": {
                    "rationality": 1.0,
                    "noise": {"price_std": 0.0, "quality_std": 0.0},
                    "selection_min_quality": 0,
                    "selection_max_price": 10000,
                },
                "modernisation": {
                    "capital_addon": {"mean": -1, "std": 0},
                    "cost_addon": {"mean": 0, "std": 0},
                    "quality_addon": {"mean": 0, "std": 0},
                },
                "pricing": {"markup": 1.0},
                "features": {"employment": False, "bankrupt_layoffs": False},
            }
        )
        rng = Rng(0)
        cit = Citizen(id=0, money=100.0)
        products = [
            Product(id=0, quality=10.0, price=50.0),
            Product(id=1, quality=12.0, price=60.0),
            Product(id=2, quality=12.0, price=55.0),
        ]
        chosen = consumer_mod.consume(cit, products, cfg, rng)
        self.assertEqual(chosen.id, 2)

    def test_rationality_zero_only_affordable(self) -> None:
        cfg = config_from_dict(
            {
                "seed": 42,
                "periods": 1,
                "agents": {"citizens": 1, "factories": 1},
                "salary": {"model": "gamma", "gamma": {"shape": 3, "scale": 10}},
                "factory_init": {
                    "capital": {"dist": "normal", "mean": 100, "std": 1},
                    "max_quality": {"dist": "uniform_int", "min": 5, "max": 5},
                    "cost": {"dist": "uniform_int", "min": 5, "max": 5},
                },
                "consumer": {"rationality": 0.0, "noise": {"price_std": 0, "quality_std": 0}},
                "modernisation": {
                    "capital_addon": {"mean": -1, "std": 0},
                    "cost_addon": {"mean": 0, "std": 0},
                    "quality_addon": {"mean": 0, "std": 0},
                },
                "pricing": {"markup": 1.0},
                "features": {"employment": False, "bankrupt_layoffs": False},
            }
        )
        cit = Citizen(id=0, money=70.0)
        products = [
            Product(id=0, quality=1.0, price=30.0),
            Product(id=1, quality=99.0, price=200.0),
        ]
        counts = {0: 0, 1: 0}
        for i in range(200):
            rng2 = Rng(42 + i)
            ch = consumer_mod.consume(cit, products, cfg, rng2)
            counts[ch.id] += 1
        self.assertEqual(counts[1], 0)
        self.assertEqual(counts[0], 200)


if __name__ == "__main__":
    unittest.main()
