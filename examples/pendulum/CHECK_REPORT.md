# Check report — pendulum

## Verdict: PASS (after 1 fix round)

## Round 1 (FAIL)
- F1: D4 failed. `test_series_agrees_with_numerical_integration` gave relative
  error 0.2929 (expected < 1e-6).
  - Proof: `python3 -m unittest ...` -> "AssertionError: 0.29289321542159213
    not less than 1e-06".
  - Diagnosis: the substitution sin(phi) = sin(theta/2)/sin(theta0/2) turns the
    integral into sqrt(2) * int dphi/sqrt(1 - s0^2 sin^2 phi); the sqrt(2) was
    missing in `scipy_free_integrator.py`.
  - Severity: blocking (it would have shipped a 30% wrong large-amplitude
    period).
  - Fix: multiplied by sqrt(2). The tolerance was NOT relaxed.

## Round 2 (PASS)
Ran `python3 scripts/verify.py --project examples/pendulum` -> all 3 required
checks PASS. 8 unit tests OK.

## Dimensional check
- [L]/[L T^-2] = T^2, square root -> T. Matches D3.
- Encoded in `scripts/sanity.py` (`check_dimensions`) and run by the test suite.

## Physics sanity
- Zero-amplitude limit reduces to the small-angle formula (D5). PASS.
- Monotonic increase with amplitude, consistent with the elliptic integral
  being > K(0) (D5). PASS.
- Energy conservation is built into the exact integral (no time-stepping
  drift). PASS.
- Order of magnitude: T ~ 2 s for L ~ 1 m on Earth. PASS.

## Independent recompute
- Series (perturbative) vs Simpson integration of the energy integral
  (non-perturbative) agree to < 1e-6 at 30 degrees. Two genuinely different
  derivations.

## Warnings (not blocking)
- Series with 6 terms is inaccurate near 90 degrees; it is not claimed to be
  exact. Numerical path is the accurate one.
- Model ignores air drag and pivot friction; it is a textbook idealisation.

## Sources
- Standard-gravity value: BIPM/CGPM definition (g_n = 9.80665 m/s^2).
- Pendulum period series: standard elliptic-integral expansion; verified
  numerically here rather than cited line-by-line.
