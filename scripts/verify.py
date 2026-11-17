#!/usr/bin/env python3
"""Run every gate in a project's verify.toml and write VERIFY.md.

    python3 scripts/verify.py --project projects/pendulum
    python3 scripts/verify.py --project projects/pendulum --list

Exit code 0 = every required check passed (the only legal end of the loop).
Exit code 1 = at least one required check failed.
Exit code 2 = config problem (missing file, bad TOML, no checks).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path

MAX_OUTPUT_LINES = 25
REPO_ROOT = Path(__file__).resolve().parent.parent


def run_check(check: dict, cwd: Path) -> dict:
    name = check.get("name") or check.get("cmd", "<unnamed>")
    cmd = check.get("cmd")
    required = bool(check.get("required", True))
    timeout = int(check.get("timeout", 600))
    expect_stdout = check.get("expect_stdout")

    if not cmd:
        return {"name": name, "ok": False, "required": required,
                "reason": "plugin error: missing 'cmd'", "output": "", "seconds": 0.0}

    # Checks run from the project dir; $SPACE_ROOT and $SPACE_PROJECT let them
    # reach the toolkit and their own files without hardcoded paths.
    env = os.environ.copy()
    env["SPACE_ROOT"] = str(REPO_ROOT)
    env["SPACE_PROJECT"] = str(cwd)

    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True,
            timeout=timeout, env=env,
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        ok = proc.returncode == 0
        reason = f"exit {proc.returncode}"
    except subprocess.TimeoutExpired:
        output = ""
        ok = False
        reason = f"timeout after {timeout}s"
    except OSError as exc:
        output = str(exc)
        ok = False
        reason = f"could not run: {exc}"

    if ok and expect_stdout and expect_stdout not in output:
        ok = False
        reason = f"exit 0 but stdout missing {expect_stdout!r}"

    return {
        "name": name,
        "ok": ok,
        "required": required,
        "reason": reason,
        "output": output,
        "seconds": round(time.monotonic() - started, 2),
        "cmd": cmd,
    }


def trim(text: str, lines: int = MAX_OUTPUT_LINES) -> str:
    rows = [r for r in text.splitlines() if r.strip()]
    if len(rows) <= lines:
        return "\n".join(rows)
    head = rows[: lines - 3]
    tail = rows[-2:]
    return "\n".join(head + [f"... ({len(rows) - lines} lines trimmed) ..."] + tail)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="project directory")
    parser.add_argument("--config", default=None, help="path to verify.toml")
    parser.add_argument("--list", action="store_true", help="list checks and exit")
    parser.add_argument("--no-write", action="store_true", help="do not write VERIFY.md")
    args = parser.parse_args(argv)

    project = Path(args.project).resolve()
    config_path = Path(args.config) if args.config else project / "verify.toml"
    if not config_path.is_file():
        print(f"error: no verify config at {config_path}", file=sys.stderr)
        return 2
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        print(f"error: bad TOML in {config_path}: {exc}", file=sys.stderr)
        return 2

    checks = config.get("check") or []
    if isinstance(checks, dict):
        checks = [checks]
    if not checks:
        print(f"error: {config_path} defines no [[check]] blocks", file=sys.stderr)
        return 2

    if args.list:
        for check in checks:
            print(f"- {check.get('name', '?')}: {check.get('cmd', '?')}")
        return 0

    print(f"verify: {project.name}  ({config_path})")
    results = []
    for check in checks:
        result = run_check(check, project)
        results.append(result)
        flag = "PASS" if result["ok"] else "FAIL"
        print(f"  [{flag}] {result['name']} ({result['seconds']}s) - {result['reason']}")
        if not result["ok"]:
            for line in trim(result.get("output", "")).splitlines():
                print(f"         {line}")

    failed_required = [r for r in results if r["required"] and not r["ok"]]
    verdict = "PASS" if not failed_required else "FAIL"

    if not args.no_write:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
        rows = ["# Machine verification", "", f"- run: {stamp}", f"- verdict: **{verdict}**", ""]
        rows += ["| check | required | result | time | note |", "|---|---|---|---|---|"]
        for r in results:
            rows.append(
                f"| {r['name']} | {'yes' if r['required'] else 'no'} | "
                f"{'PASS' if r['ok'] else 'FAIL'} | {r['seconds']}s | {r['reason']} |"
            )
        if failed_required:
            rows += ["", "## Failure output"]
            for r in failed_required:
                rows += ["", f"### {r['name']}", "```", trim(r.get("output", "")), "```"]
        (project / "VERIFY.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

    print(f"verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
