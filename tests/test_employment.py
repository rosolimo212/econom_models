import unittest

from econom_sim.config import config_from_dict
from econom_sim.engine import init_state, run_period


class TestEmployment(unittest.TestCase):
    def test_workers_assigned_when_employment_on(self) -> None:
        cfg = config_from_dict(
            {
                "seed": 3,
                "periods": 3,
                "agents": {"citizens": 12, "factories": 3},
                "salary": {
                    "model": "employment",
                    "wage_share_of_revenue": 0.2,
                    "unemployment_benefit": 1.0,
                },
                "factory_init": {
                    "capital": {"dist": "normal", "mean": 500, "std": 20},
                    "max_quality": {"dist": "uniform_int", "min": 8, "max": 18},
                    "cost": {"dist": "uniform_int", "min": 2, "max": 8},
                },
                "consumer": {"rationality": 1.0, "noise": {"price_std": 0, "quality_std": 0}},
                "modernisation": {
                    "capital_addon": {"mean": -15, "std": 5},
                    "cost_addon": {"mean": 0, "std": 1},
                    "quality_addon": {"mean": 0, "std": 1},
                },
                "pricing": {"markup": 1.0},
                "features": {"employment": True, "bankrupt_layoffs": True},
            }
        )
        st = init_state(cfg)
        self.assertTrue(all(c.employer_id is not None for c in st.citizens))
        run_period(st)
        self.assertGreaterEqual(len({c.employer_id for c in st.citizens}), 1)


if __name__ == "__main__":
    unittest.main()
