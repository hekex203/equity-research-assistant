import unittest
from src.metrics import calculate_metrics

class MetricsTests(unittest.TestCase):
    def test_known_drawdown_and_return(self):
        result = calculate_metrics([100, 120, 90, 108])
        self.assertAlmostEqual(result['total_return'], .08)
        self.assertAlmostEqual(result['max_drawdown'], -.25)
        self.assertGreater(result['annualized_volatility'], 0)

    def test_constant_price(self):
        result = calculate_metrics([100, 100, 100])
        self.assertEqual(result['annualized_volatility'], 0)
        self.assertIsNone(result['sharpe_ratio'])

    def test_invalid_prices(self):
        for values in ([100], [100, 0, 101], [100, float('inf'), 101]):
            with self.assertRaises(ValueError):
                calculate_metrics(values)

if __name__ == '__main__':
    unittest.main()
