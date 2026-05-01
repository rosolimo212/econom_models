import unittest

from econom_sim.config import config_from_dict
from econom_sim.domain import Citizen, Product
from econom_sim.market import consumer as consumer_mod
from econom_sim.rng import Rng


class TestIrrationality(unittest.TestCase):
    def test_noise_can_change_ranking(self) -> None:
        cfg = config_from_dict(
            {
                "seed": 5,
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
                    "noise": {"price_std": 0.0, "quality_std": 5.0},
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
        cit = Citizen(id=0, money=100.0)
        products = [
            Product(id=0, quality=10.0, price=40.0),
            Product(id=1, quality=11.0, price=41.0),
        ]
        picks = set()
        for s in range(50):
            ch = consumer_mod.consume(cit, products, cfg, Rng(1000 + s))
            picks.add(ch.id)
        self.assertGreater(len(picks), 1)


if __name__ == "__main__":
    unittest.main()
