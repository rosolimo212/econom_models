import json
import unittest
from pathlib import Path

from econom_sim.config import config_from_dict
from econom_sim.engine import init_state, run_period


def _baseline_tiny_cfg() -> dict:
    return {
        "seed": 42,
        "periods": 3,
        "agents": {"citizens": 20, "factories": 3},
        "salary": {"model": "gamma", "gamma": {"shape": 3, "scale": 10}},
        "factory_init": {
            "capital": {"dist": "normal", "mean": 1000, "std": 300},
            "max_quality": {"dist": "uniform_int", "min": 2, "max": 30},
            "cost": {"dist": "uniform_int", "min": 5, "max": 100},
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


class TestGoldenBaseline(unittest.TestCase):
    def test_golden_baseline_metrics(self) -> None:
        golden_path = Path(__file__).parent / "golden" / "baseline.json"
        expected = json.loads(golden_path.read_text(encoding="utf-8"))
        cfg = config_from_dict(_baseline_tiny_cfg())
        st = init_state(cfg)
        for row in expected:
            snap = run_period(st)
            self.assertEqual(snap.period, row["period"])
            for k, v in row["metrics"].items():
                self.assertLess(abs(snap.metrics[k] - v), 1e-5)
            fcap = sum(r["capital"] for r in snap.factory_rows)
            self.assertLess(abs(fcap - row["fcap"]), 0.02)


if __name__ == "__main__":
    unittest.main()
