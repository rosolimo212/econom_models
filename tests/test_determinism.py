import json
import unittest

from econom_sim.config import config_from_dict
from econom_sim.engine import init_state, run_period
from econom_sim.io.snapshot import snapshot_to_dict


def _tiny_cfg() -> dict:
    return {
        "seed": 123,
        "periods": 5,
        "agents": {"citizens": 15, "factories": 4},
        "salary": {"model": "gamma", "gamma": {"shape": 3, "scale": 10}},
        "factory_init": {
            "capital": {"dist": "normal", "mean": 800, "std": 100},
            "max_quality": {"dist": "uniform_int", "min": 5, "max": 25},
            "cost": {"dist": "uniform_int", "min": 5, "max": 40},
        },
        "consumer": {
            "rationality": 1.0,
            "noise": {"price_std": 0.0, "quality_std": 0.0},
            "selection_min_quality": 0,
            "selection_max_price": 10000,
        },
        "modernisation": {
            "capital_addon": {"mean": -100, "std": 50},
            "cost_addon": {"mean": 0, "std": 5},
            "quality_addon": {"mean": 0, "std": 3},
        },
        "pricing": {"markup": 1.0},
        "features": {"employment": False, "bankrupt_layoffs": False},
    }


class TestDeterminism(unittest.TestCase):
    def test_same_seed_identical_snapshots(self) -> None:
        cfg_d = _tiny_cfg()

        def run_all() -> list:
            st = init_state(config_from_dict(cfg_d))
            return [snapshot_to_dict(run_period(st)) for _ in range(5)]

        a = run_all()
        b = run_all()
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
