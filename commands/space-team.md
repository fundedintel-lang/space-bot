---
description: Start the space-team build loop on a goal (planner, builder, checker, judge, clerk)
argument-hint: <what you want built or proven>
---

Start the **space-team** loop for this request:

$ARGUMENTS

Follow `skills/space-team/SKILL.md` exactly, in order:

1. Scaffold the project with `scripts/scaffold.py` and write `BRIEF.md` in the
   user's own words.
2. Planner hat -> `PLAN.md` with a machine-checkable Definition of Done.
3. Builder hat -> code + tests.
4. Checker hat -> run `scripts/verify.py`, log the round with `scripts/plan.py`,
   write `CHECK_REPORT.md`.
5. On FAIL, go back to the Planner hat (never weaken a check). Respect the fix
   round budget; on exhaustion, stop and report the honest state.
6. Master sweep, then Judge (`JUDGE.md`), then Clerk (`REPORT.md`).

Do not declare success unless `scripts/verify.py` exits 0. Show the user the
final verdict plus the exact reproduce command.
