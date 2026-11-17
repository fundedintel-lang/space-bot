#!/usr/bin/env python3
"""A small, honest physics/maths sanity kit for Checker scripts.

    python3 scripts/sanity.py --demo

Import it from your project tests:

    from sanity import dims, si_base, check_dimensions, close

Rules of thumb this encodes:
  * a formula's SI base dimensions must match on both sides
  * a residual is only as good as its tolerance; state the tolerance
  * limits and conservation laws catch more bugs than long derivations

Accuracy is the caller's responsibility: this module refuses to guess.
"""
from __future__ import annotations

import argparse
import sys
from fractions import Fraction

# SI base dimension vector order: (mass, length, time, current, temperature,
# amount, luminous intensity)
BASE = ("M", "L", "T", "I", "TH", "N", "J")


def dims(**kwargs: int) -> tuple[Fraction, ...]:
    """Build a dimension vector, e.g. dims(L=1, T=-1) is a velocity."""
    unknown = set(kwargs) - set(BASE)
    if unknown:
        raise ValueError(f"unknown base dimension(s): {sorted(unknown)}; use {BASE}")
    return tuple(Fraction(kwargs.get(k, 0)) for k in BASE)


def si_base(vector: tuple[Fraction, ...]) -> str:
    parts = [f"{name}^{d}" if d != 1 else name for name, d in zip(BASE, vector) if d != 0]
    return " ".join(parts) if parts else "dimensionless"


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def mul(a, n) -> tuple[Fraction, ...]:
    return tuple(x * Fraction(n) for x in a)


def check_dimensions(lhs, rhs, what: str = "") -> None:
    """Raise AssertionError if the two dimension vectors differ."""
    if tuple(lhs) != tuple(rhs):
        label = f"{what}: " if what else ""
        raise AssertionError(
            f"{label}dimension mismatch: {si_base(tuple(lhs))} != {si_base(tuple(rhs))}"
        )


def close(actual: float, expected: float, rel: float = 1e-9, what: str = "") -> None:
    """Raise AssertionError if not relatively close. rel is a stated tolerance."""
    if expected == 0:
        ok = abs(actual) <= rel
        err = abs(actual)
    else:
        err = abs(actual - expected) / abs(expected)
        ok = err <= rel
    if not ok:
        label = f"{what}: " if what else ""
        raise AssertionError(f"{label}relative error {err:.3e} exceeds tolerance {rel:.1e}")


def demo() -> int:
    """Show the kit working on the pendulum period T = 2*pi*sqrt(L/g)."""
    g = dims(L=1, T=-2)          # acceleration
    length = dims(L=1)
    check_dimensions(sub(length, g), dims(T=2), "period under the square root")
    print("pendulum: sqrt(L/g) has dimensions", si_base(dims(T=1)))

    force = dims(M=1, L=1, T=-2)
    check_dimensions(sub(force, mul(dims(M=1, L=1, T=-2), 1)), dims(), "F = m*a")
    print("Newton: F = m*a is dimensionally consistent")

    # A deliberately wrong formula must fail, or the kit is useless.
    try:
        check_dimensions(dims(M=1, L=1, T=-1), force, "wrong momentum check")
    except AssertionError as exc:
        print("negative control caught it:", exc)
    else:
        print("ERROR: dimensional check did not catch a mismatch", file=sys.stderr)
        return 1

    close(9.81, 9.81, rel=1e-12, what="g")
    print("sanity kit: OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="run the self-test demonstration")
    parser.parse_args(argv)
    return demo()


if __name__ == "__main__":
    sys.exit(main())
