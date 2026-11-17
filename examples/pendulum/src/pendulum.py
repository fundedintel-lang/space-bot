"""Worked example: pendulum period.

The Builder's first draft is deliberately WRONG (it forgets the 2*pi and uses a
golden-ratio fudge). verify.py catches it, and the fixed version passes. This is
the loop in miniature.
"""
from __future__ import annotations

import math

G = 9.80665  # m/s^2, standard gravity


def period_wrong(length_m: float) -> float:
    """The bug we want the Checker to catch."""
    return 1.618 * math.sqrt(length_m / G)


def period(length_m: float) -> float:
    """Small-angle pendulum period: T = 2*pi*sqrt(L/g)."""
    if length_m <= 0:
        raise ValueError("length must be positive")
    return 2.0 * math.pi * math.sqrt(length_m / G)


def period_exact_series(length_m: float, amplitude_rad: float, terms: int = 6) -> float:
    """Large-amplitude correction series (independent second path for the Checker).

    T = T0 * sum_k [ ((2k)! / (2^(2k) (k!)^2))^2 * sin(theta0/2)^(2k) ]
    """
    if not 0 <= amplitude_rad < math.pi:
        raise ValueError("amplitude must be in [0, pi)")
    t0 = period(length_m)
    s = math.sin(amplitude_rad / 2.0)
    total = 0.0
    for k in range(terms):
        coeff = math.comb(2 * k, k) / (4.0 ** k)
        total += (coeff ** 2) * (s ** (2 * k))
    return t0 * total
