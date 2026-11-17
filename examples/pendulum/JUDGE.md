# Judge — pendulum

| DoD | planned | built | checked | evidence |
|-----|---------|-------|---------|----------|
| D1 period(1 m) = 2.006409 s | yes | yes | yes | tests/test_pendulum.py::ClosedFormTest::test_one_metre_on_earth |
| D2 sqrt(L) scaling | yes | yes | yes | tests/test_pendulum.py::ClosedFormTest::test_scales_as_sqrt_length |
| D3 dimension is time | yes | yes | yes | tests/test_pendulum.py::DimensionalTest::test_period_is_time |
| D4 series vs integration < 1e-6 | yes | yes (fix round 1) | yes | tests/test_pendulum.py::LimitTest::test_series_agrees_with_numerical_integration |
| D5 limits | yes | yes | yes | tests/test_pendulum.py::LimitTest (2 tests) |
| D6 ValueError on L <= 0 | yes | yes | yes | tests/test_pendulum.py::GuardTest |
| D7 negative control catches bad formula | yes | yes | yes | tests/test_pendulum.py::NegativeControlTest |
| D8 verify.py exits 0 | yes | yes | yes | VERIFY.md |

## Verdict: PASS

Every row has planned=yes, built=yes, checked=yes and a non-empty evidence
pointer. Nothing was silently dropped.

## Ranking of remaining (non-blocking) work
1. Higher-order amplitude series or a fully numerical API near 90 degrees.
2. Add damping term (needs a modelled drag coefficient, i.e. new assumption).
3. Web-sourced comparison against a measured pendulum dataset (would strengthen
   validation beyond self-consistency).
