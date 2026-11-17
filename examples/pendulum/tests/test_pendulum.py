import math
import unittest

from examples.pendulum.src.pendulum import (
    G,
    period,
    period_exact_series,
    period_wrong,
)


class DimensionalTest(unittest.TestCase):
    def test_period_is_time(self):
        from sanity import check_dimensions, dims, si_base
        self.assertEqual(si_base(dims(T=1)), "T")
        # T = 2*pi*sqrt(L/g): L has L, g has L T^-2, ratio has T^2 -> T
        check_dimensions(dims(T=1), dims(T=1), "pendulum period")


class ClosedFormTest(unittest.TestCase):
    def test_one_metre_on_earth(self):
        # Known value: T for L=1 m, g=9.80665 -> 2.006409...
        self.assertAlmostEqual(period(1.0), 2.0064093, places=6)

    def test_scales_as_sqrt_length(self):
        self.assertAlmostEqual(period(4.0) / period(1.0), 2.0, places=12)


class LimitTest(unittest.TestCase):
    def test_zero_amplitude_matches_small_angle(self):
        self.assertAlmostEqual(
            period_exact_series(1.0, amplitude_rad=0.0, terms=6), period(1.0), places=12
        )

    def test_large_amplitude_is_slower(self):
        self.assertGreater(period_exact_series(1.0, math.radians(60)), period(1.0))

    def test_series_agrees_with_numerical_integration(self):
        # Independent path: integrate dt = sqrt(2L/g)/sqrt(cos t - cos t0)
        from scipy_free_integrator import integrate_period

        theta0 = math.radians(30)
        numeric = integrate_period(1.0, theta0, G, steps=4000)
        series = period_exact_series(1.0, theta0, terms=6)
        self.assertLess(abs(numeric - series) / series, 1e-6)


class NegativeControlTest(unittest.TestCase):
    def test_wrong_formula_must_fail(self):
        """If this fails, the suite is not actually catching bugs."""
        with self.assertRaises(AssertionError):
            self.assertAlmostEqual(period_wrong(1.0), period(1.0), places=3)


class GuardTest(unittest.TestCase):
    def test_non_positive_length_rejected(self):
        with self.assertRaises(ValueError):
            period(0.0)


if __name__ == "__main__":
    unittest.main()
