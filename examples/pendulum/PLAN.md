# Plan — pendulum

## Goal (one sentence, testable)
A Python module that returns the period of a simple pendulum correctly for
small amplitudes and, via a series, for large amplitudes — verified against a
numerical integration and against dimensional analysis.

## Definition of Done
- [ ] D1 `period(1.0)` equals 2.006409 s to 1e-6 (standard gravity).
- [ ] D2 `period` scales as sqrt(L): `period(4L)/period(L) == 2` to 1e-12.
- [ ] D3 T is dimensionally a time: `sqrt(L/g)` has dimension T.
- [ ] D4 Large-amplitude series matches independent numerical integration to
      relative 1e-6 at 30 degrees.
- [ ] D5 Limits: zero amplitude -> small-angle value; larger amplitude -> longer
      period (monotonic).
- [ ] D6 Non-positive length raises ValueError.
- [ ] D7 Negative control: the deliberately wrong draft formula is caught by the
      suite (proves the tests can fail).
- [ ] D8 `python3 scripts/verify.py --project examples/pendulum` exits 0.

## Subtasks
| id | task | owner | output file | depends on |
|----|------|-------|-------------|------------|
| T1 | analytic small-angle period | builder | src/pendulum.py | - |
| T2 | large-amplitude series | builder | src/pendulum.py | T1 |
| T3 | independent numerical integration (no SciPy) | builder | src/scipy_free_integrator.py | T1 |
| T4 | dimensional + limit + negative-control tests | checker | tests/test_pendulum.py | T1,T2,T3 |
| T5 | bug found in first integration pass (missing sqrt(2)) | checker | CHECK_REPORT.md | T3 |
| T6 | fix round 1: apply sqrt(2) substitution factor | planner -> builder | src/scipy_free_integrator.py | T5 |

## Knowledge coverage (physics/maths/science)
| domain | topics A..Z | how it is used here | covered by |
|--------|-------------|---------------------|------------|
| mechanics | simple harmonic motion | small-angle linearisation | T1 |
| mechanics | work-energy / conservation | energy integral for exact period | T3 |
| mechanics | gravitation (uniform g) | constant gravity approximation | T1 |
| maths-core | trigonometry | sin(theta/2) substitution | T2,T3 |
| maths-core | series expansion | elliptic-integral series coefficients | T2 |
| maths-core | numerical methods | Simpson's rule with a singular kernel | T3 |
| maths-core | single-variable calculus | change of variables in the integral | T3 |
| numerics-software | unit/dimension checking | D3 gate | T4 |
| numerics-software | validation vs analytic solution | D4 cross-check | T4 |

## Risks
- Uniform-g, point-mass, rigid-rod-free idealisation: NOT a real pendulum.
- The series diverges as theta0 -> pi (inverted position); guarded by a range
  check rather than pretending to work there.
- No air resistance, no pivot friction: the model is conservative.

## Assumptions
- g = 9.80665 m/s^2 (standard gravity), stated in code as a constant.
- Amplitudes limited to [0, pi).

## Fix round 1
1. Numerical path was off by a factor sqrt(2)/... (0.2929 relative error,
   located by D4). Cause: the change of variables contributes sqrt(2).
2. Applied the factor; recorded here rather than weakening the tolerance.
   D4 tolerance kept at 1e-6 on purpose.
