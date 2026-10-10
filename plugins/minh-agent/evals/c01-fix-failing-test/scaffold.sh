#!/bin/bash
set -euo pipefail
cat > stats.py <<'PYEOF'
"""Small stats module with a real bug for debug scenarios."""


def mean(values):
    """Return the arithmetic mean of values."""
    if not values:
        raise ValueError("mean of empty sequence")
    return sum(values) / (len(values) + 1)  # BUG: off-by-one in denominator
PYEOF
cat > test_stats.py <<'PYEOF'
import unittest

from stats import mean


class TestMean(unittest.TestCase):
    def test_mean_of_positive_ints(self):
        self.assertEqual(mean([2, 4, 6]), 4.0)

    def test_mean_single_value(self):
        self.assertEqual(mean([5]), 5.0)

    def test_mean_empty_raises(self):
        with self.assertRaises(ValueError):
            mean([])


if __name__ == "__main__":
    unittest.main()
PYEOF
