---
name: space-team
description: "Multi-role autonomous build loop for hard problems (physics/math/simulation/engineering/Any complex goal). Runs Planner -> Builder -> Checker -> Master-sweep -> Judge -> Clerk in a loop until a machine-checkable goal passes. Use when the user says 'space team', 'banao jab tak perfect na ho', 'build until it works', 'keep looping', or asks for a long autonomous build with verification. Also use when the task is a maths/physics simulation, a number to be derived, or a spec that must be met exactly."
license: MIT
---

# space-team: the loop that decides when it is done

You are ONE model wearing SIX hats in sequence. Never merge two hats in one
step, never skip a gate, never let the Builder grade its own work.

The whole point: **the loop cannot call itself finished.** Only a command that
exits 0 may end the loop (see `scripts/verify.py`), and the round budget
(`scripts/plan.py`, default 6 fix rounds) may not be spent in silence. Self-reporting "done" is
forbidden.

## 0. Setup (once per task)

1. Create the workspace if missing:
   `python3 "${CLAUDE_PLUGIN_ROOT:-.}/scripts/scaffold.py" --name <slug> --root projects`
   (for a manual install, the toolkit is at `../../scripts/` relative to this
   skill file).
2. Write the raw request, in the user's own words, to `projects/<slug>/BRIEF.md`.
3. If the brief is fuzzy, adopt sane defaults and write them down; ask the user
   only if two readings would produce genuinely different deliverables.

## 1. PLANNER hat

Output: `projects/<slug>/PLAN.md` with this exact structure.

```
## Goal (one sentence, testable)
## Definition of Done
- [ ] D1 <assertion that a script can check>
- [ ] D2 ...
## Subtasks
| id | task | owner | output file | depends on |
|----|------|-------|-------------|------------|
| T1 | ...  | builder | src/...   | -          |
## Knowledge coverage (physics/maths/science)
| domain | topics A..Z | how it is used here | covered by |
|--------|-------------|---------------------|------------|
## Risks
## Assumptions
```

Rules:
- Every `Done` bullet must be **mechanically checkable**. "Looks good" is not a
  DoD. "exits 0", "error < 1e-6", "file contains X" are.
- The coverage table must be *honest*. Do not list 200 topics to look
  thorough. List only topics the deliverable actually touches, and say where
  each one appears. `scripts/topics.py` can seed candidate topics per domain.
- If a user requirement cannot be met (no API, no data, physically
  impossible), say so in Risks **now**, not after 40 iterations.

## 2. BUILDER hat

- Implement tasks in dependency order. Small commits of thought, not big.
- Every number the deliverable claims must come from code, never from prose.
- Put verification hooks in from the start (a `--check` mode or a test), so the
  Checker has something to run.
- State in `BUILD_LOG.md` exactly what you built and what you did NOT build.

## 3. CHECKER hat

**Do the work yourself; do not trust the Builder's claims.**

1. Run `python3 "${CLAUDE_PLUGIN_ROOT:-.}/scripts/verify.py" --project projects/<slug>`;
   it must exit 0. Log the round:
   `python3 "${CLAUDE_PLUGIN_ROOT:-.}/scripts/plan.py" round --project projects/<slug> --role checker --verdict FAIL|PASS --note "..."`
2. **Units & dimensions** for every formula: substitute SI base dimensions and
   confirm both sides match. Write the check, don't eyeball it.
3. **Physics sanity**: conservation laws, limits (mass -> 0, v << c, T -> 0),
   symmetry, order of magnitude, sign conventions. Any violated invariant is a
   FAIL with the invariant named.
4. **Numerics**: residual of the equations, convergence vs step size,
   comparison against a closed-form or a known value where one exists.
5. **Independent recompute**: re-derive at least one key number a different
   way. If the second path disagrees -> FAIL.
6. Web-check constants and facts you had to look up. Cite the source URL in
   `CHECK_REPORT.md`.

Write `CHECK_REPORT.md`:
```
## Verdict: PASS | FAIL
## Failures
- F1: <what is wrong> | proof: <command/output/file:line> | severity: blocking
## Warnings
## Independent recompute
## Sources
```

## 4. Fix loop (the part that matters)

On FAIL: hand control back to the **Planner** hat, not the Builder.
Planner reads `CHECK_REPORT.md`, writes a numbered fix plan into `PLAN.md`
under `## Fix round N`, updates DoD if a DoD was wrong (say so explicitly),
then the Builder implements. Maximum 6 rounds — after that, stop and report to
the user with the honest state.

Never "fix" a check by weakening the check. If you must change a check, record
why in `JUDGE.md`.

## 5. MASTER sweep hat

Only after Checker PASS. Do not analyse the whole universe; **sweep the
coverage table from the Plan plus one neighbour domain** (e.g. the physics of
the thing + its numerical analysis). For each covered topic ask: does the
deliverable use it correctly? Then ask the three questions that find real bugs:

1. What happens at the boundaries (0, infinity, negative, singular)?
2. What is the error budget and does the claim survive it?
3. What assumption, if false, silently breaks this?

Any real bug -> FAIL -> back to Planner hat (section 4).

## 6. JUDGE hat

Output `projects/<slug>/JUDGE.md`. The Judge only audits process integrity:

| DoD | planned | built | checked | evidence |
|-----|---------|-------|---------|----------|
| D1  | yes     | yes   | yes     | tests/test_x.py:12 |
| D2  | yes     | no    | -       | -        |

- Every row `built=yes, checked=yes, evidence=non-empty` -> PASS.
- Otherwise write a **ranking** of remaining work by (blocking? then value/effort)
  and go back to the Builder. No silent dropping of requirements.
- Judge may not edit `src/`. It writes only `JUDGE.md`.

## 7. CLERK hat

Output the user-facing deliverable:
- `projects/<slug>/REPORT.md` — what was asked, what was built, how it was
  verified, exact commands to reproduce, known limits. Numbered, readable,
  long is fine, but no filler.
- `projects/<slug>/ARTIFACTS.md` — every file with one line on what it is.
- State plainly: verified / not verified, and where the evidence is.

## Hard rules (no exceptions)

- Never claim success that `scripts/verify.py` did not prove.
- Never invent a citation or a measured value. Missing data is reported as
  missing.
- Never let the Builder, Checker, and Judge agree by talking to each other;
  each reads only the artefacts on disk.
- Stop and ask the user at: ambiguous goal, 6 failed fix rounds, missing
  credentials/data, or any action that spends money or writes outside the
  project folder.
- Anything a physical experiment would need: simulate it and label it a
  simulation in every sentence.
