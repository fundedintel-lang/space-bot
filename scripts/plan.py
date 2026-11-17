#!/usr/bin/env python3
"""Track loop rounds so the agent cannot loop forever without reporting.

    python3 scripts/plan.py new  --project projects/pendulum
    python3 scripts/plan.py round --project projects/pendulum --role checker --verdict FAIL --note "D2 residual 1e-3"
    python3 scripts/plan.py status --project projects/pendulum

State lives in <project>/.loop.json. Exceeding the budget makes `round`
exit 1, which is the signal to stop and report to the user (SKILL.md 4).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROLES = ("planner", "builder", "checker", "master", "judge", "clerk")
VERDICTS = ("PASS", "FAIL", "BLOCKED", "INFO")
DEFAULT_BUDGET = 6


def state_path(project: Path) -> Path:
    return project / ".loop.json"


def load(project: Path) -> dict:
    path = state_path(project)
    if not path.is_file():
        return {"project": project.name, "budget": DEFAULT_BUDGET, "rounds": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save(project: Path, state: dict) -> None:
    state_path(project).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def fix_rounds(state: dict) -> int:
    return sum(1 for r in state["rounds"] if r["role"] == "checker" and r["verdict"] == "FAIL")


def cmd_new(args) -> int:
    project = Path(args.project).resolve()
    project.mkdir(parents=True, exist_ok=True)
    state = {"project": project.name, "budget": args.budget, "rounds": []}
    save(project, state)
    print(f"loop started for {project.name} (budget: {args.budget} fix rounds)")
    return 0


def cmd_round(args) -> int:
    project = Path(args.project).resolve()
    state = load(project)
    state.setdefault("budget", DEFAULT_BUDGET)
    state.setdefault("rounds", [])
    if args.budget:
        state["budget"] = args.budget
    state["rounds"].append(
        {
            "n": len(state["rounds"]) + 1,
            "role": args.role,
            "verdict": args.verdict,
            "note": args.note or "",
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )
    save(project, state)
    used = fix_rounds(state)
    print(f"logged {args.role}/{args.verdict} (round {len(state['rounds'])}); fix rounds used: {used}/{state['budget']}")
    if used >= state["budget"]:
        print("BUDGET EXHAUSTED: stop looping and report the honest state to the user.", file=sys.stderr)
        return 1
    return 0


def cmd_status(args) -> int:
    project = Path(args.project).resolve()
    state = load(project)
    used = fix_rounds(state)
    budget = state.get("budget", DEFAULT_BUDGET)
    print(f"project: {state.get('project', project.name)}")
    print(f"rounds logged: {len(state['rounds'])}")
    print(f"fix rounds: {used}/{budget}")
    if state["rounds"]:
        last = state["rounds"][-1]
        print(f"last: {last['role']} -> {last['verdict']} ({last['note'] or 'no note'})")
    if used >= budget:
        print("status: BUDGET EXHAUSTED - report to the user, do not continue silently")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="start loop bookkeeping for a project")
    p_new.add_argument("--project", required=True)
    p_new.add_argument("--budget", type=int, default=DEFAULT_BUDGET)
    p_new.set_defaults(func=cmd_new)

    p_round = sub.add_parser("round", help="log one role round")
    p_round.add_argument("--project", required=True)
    p_round.add_argument("--role", required=True, choices=ROLES)
    p_round.add_argument("--verdict", required=True, choices=VERDICTS)
    p_round.add_argument("--note", default="")
    p_round.add_argument("--budget", type=int, default=None)
    p_round.set_defaults(func=cmd_round)

    p_status = sub.add_parser("status", help="show loop state")
    p_status.add_argument("--project", required=True)
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args(argv)
    if not Path(args.project).is_dir():
        print(f"error: no such project dir: {args.project}", file=sys.stderr)
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
