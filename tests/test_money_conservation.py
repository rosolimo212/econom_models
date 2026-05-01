import unittest

from econom_sim.config import config_from_dict
from econom_sim.engine import init_state, run_period


class TestMoney(unittest.TestCase):
    def test_employment_simulation_runs(self) -> None:
        cfg = config_from_dict(
            {
                "seed": 99,
                "periods": 5,
                "agents": {"citizens": 10, "factories": 2},
                "salary": {
                    "model": "employment",
                    "wage_share_of_revenue": 0.5,
                    "unemployment_benefit": 2.0,
                },
                "factory_init": {
                    "capital": {"dist": "normal", "mean": 2000, "std": 50},
                    "max_quality": {"dist": "uniform_int", "min": 5, "max": 15},
                    "cost": {"dist": "uniform_int", "min": 1, "max": 3},
                },
                "consumer": {"rationality": 1.0, "noise": {"price_std": 0, "quality_std": 0}},
                "modernisation": {
                    "capital_addon": {"mean": -10, "std": 2},
                    "cost_addon": {"mean": 0, "std": 0.5},
                    "quality_addon": {"mean": 0, "std": 0.5},
                },
                "pricing": {"markup": 1.0},
                "features": {"employment": True, "bankrupt_layoffs": False},
            }
        )
        st = init_state(cfg)
        for _ in range(5):
            run_period(st)
        self.assertTrue(all(f.capital == f.capital for f in st.factories))


if __name__ == "__main__":
    unittest.main()
