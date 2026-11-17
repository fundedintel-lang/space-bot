"""Pure-stdlib numerical integration for the pendulum period (independent path)."""
from __future__ import annotations

import math


def integrate_period(length_m: float, theta0_rad: float, g: float, steps: int = 4000) -> float:
    """Exact period via the energy integral, Simpson's rule.

    T = 4 * sqrt(L/(2g)) * int_0^theta0 dtheta / sqrt(cos theta - cos theta0)
    The integrand is singular at theta0, so substitute
    sin(phi) = sin(theta/2)/sin(theta0/2), which removes it.
    """
    if not 0 < theta0_rad < math.pi:
        raise ValueError("amplitude must be in (0, pi)")
    s0 = math.sin(theta0_rad / 2.0)
    h = (math.pi / 2.0) / steps

    def f(phi: float) -> float:
        s = s0 * math.sin(phi)
        return 1.0 / math.sqrt(max(1.0 - s * s, 1e-300))

    total = f(0.0) + f(math.pi / 2.0)
    for i in range(1, steps):
        total += (4.0 if i % 2 else 2.0) * f(i * h)

    integral = total * h / 3.0
    # With sin(phi) = sin(theta/2)/sin(theta0/2) the singular integral becomes
    #   int_0^theta0 dtheta/sqrt(cos t - cos t0) = sqrt(2) * int_0^{pi/2} dphi/sqrt(1 - s0^2 sin^2 phi)
    return 4.0 * math.sqrt(length_m / (2.0 * g)) * math.sqrt(2.0) * integral
