# Report — pendulum (worked example)

## What was asked
Produce a correct pendulum period calculation and prove it is correct, in the
spirit of "build until the goal is met exactly".

## What was built
- `src/pendulum.py` — small-angle period, large-amplitude series, and a
  deliberately wrong draft used as a negative control.
- `src/scipy_free_integrator.py` — exact period by Simpson integration of the
  energy integral (no third-party libraries).
- `tests/test_pendulum.py` — 8 tests: dimensional, closed form, scaling, limits,
  independent cross-check, guards, negative control.
- `verify.toml` — 3 required machine gates.
- `PLAN.md`, `CHECK_REPORT.md`, `JUDGE.md`, `VERIFY.md` — the paper trail the
  loop runs on.

## How it was verified
```
python3 scripts/verify.py --project examples/pendulum
```
Result: PASS, 3/3 required checks. 8/8 unit tests. One real bug (missing
sqrt(2) in the change of variables) was found by the cross-check and fixed in
fix round 1 — the tolerance was not weakened.

## Known limits
- Ideal pendulum only: point mass, rigid massless rod, uniform g, no air
  resistance or pivot friction.
- Series with 6 terms degrades near 90 degrees; the numerical path is the
  accurate one there.
- This is a **simulation/calculation**, not a physical measurement.
