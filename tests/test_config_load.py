import unittest
from pathlib import Path

from econom_sim.config import load_config


class TestYamlLoad(unittest.TestCase):
    def test_load_base_yaml(self) -> None:
        p = Path(__file__).resolve().parents[1] / "configs" / "base.yaml"
        cfg = load_config(p)
        self.assertEqual(cfg.seed, 42)
        self.assertFalse(cfg.features.employment)


if __name__ == "__main__":
    unittest.main()
