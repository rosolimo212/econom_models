import unittest

from econom_sim.config import config_from_dict
from econom_sim.engine import init_state, run_period
from econom_sim.events import EventBus
from econom_sim.ui.telegram_bot import MessengerStub


class TestMessengerStub(unittest.TestCase):
    def test_stub_records_events(self) -> None:
        bus = EventBus()
        stub = MessengerStub(bus=bus)
        stub.attach()
        cfg = config_from_dict(
            {
                "seed": 1,
                "periods": 1,
                "agents": {"citizens": 3, "factories": 1},
                "salary": {"model": "gamma", "gamma": {"shape": 3, "scale": 10}},
                "factory_init": {
                    "capital": {"dist": "normal", "mean": 200, "std": 10},
                    "max_quality": {"dist": "uniform_int", "min": 5, "max": 10},
                    "cost": {"dist": "uniform_int", "min": 2, "max": 5},
                },
                "consumer": {"rationality": 1.0, "noise": {"price_std": 0, "quality_std": 0}},
                "modernisation": {
                    "capital_addon": {"mean": -5, "std": 1},
                    "cost_addon": {"mean": 0, "std": 0.5},
                    "quality_addon": {"mean": 0, "std": 0.5},
                },
                "pricing": {"markup": 1.0},
                "features": {"employment": False, "bankrupt_layoffs": False},
            }
        )
        st = init_state(cfg, bus=bus)
        run_period(st)
        topics = [t for t, _ in stub.messages]
        self.assertIn("period_start", topics)
        self.assertIn("snapshot", topics)


if __name__ == "__main__":
    unittest.main()
