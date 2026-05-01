import unittest

from econom_sim.config import config_from_dict
from econom_sim.engine import init_state, run_period


def _cfg(employment: bool, layoffs: bool) -> dict:
    return {
        "seed": 1,
        "periods": 2,
        "agents": {"citizens": 8, "factories": 2},
        "salary": {"model": "gamma", "gamma": {"shape": 3, "scale": 10}},
        "factory_init": {
            "capital": {"dist": "normal", "mean": 400, "std": 50},
            "max_quality": {"dist": "uniform_int", "min": 10, "max": 20},
            "cost": {"dist": "uniform_int", "min": 5, "max": 15},
        },
        "consumer": {
            "rationality": 1.0,
            "noise": {"price_std": 0.0, "quality_std": 0.0},
        },
        "modernisation": {
            "capital_addon": {"mean": -20, "std": 5},
            "cost_addon": {"mean": 0, "std": 1},
            "quality_addon": {"mean": 0, "std": 1},
        },
        "pricing": {"markup": 1.0},
        "features": {"employment": employment, "bankrupt_layoffs": layoffs},
    }


class TestFeaturesOff(unittest.TestCase):
    def test_snapshot_shape_stable_when_toggling_features(self) -> None:
        for emp, lay in [(False, False), (False, True), (True, False)]:
            cfg = config_from_dict(_cfg(emp, lay))
            st = init_state(cfg)
            snap = run_period(st)
            self.assertTrue({"gini_factory_capital", "sales_count"}.issubset(snap.metrics))
            self.assertTrue(all("capital" in r for r in snap.factory_rows))


if __name__ == "__main__":
    unittest.main()
