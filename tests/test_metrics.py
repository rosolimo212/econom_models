import unittest

from econom_sim.metrics import gini


class TestGini(unittest.TestCase):
    def test_gini_equal_values(self) -> None:
        self.assertEqual(gini([10.0, 10.0, 10.0]), 0.0)

    def test_gini_max_inequality_three(self) -> None:
        g = gini([0.0, 0.0, 100.0])
        self.assertTrue(0.6 < g < 0.68)


if __name__ == "__main__":
    unittest.main()
