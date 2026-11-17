#!/usr/bin/env python3
"""Create a fresh space-team project workspace.

    python3 scripts/scaffold.py --name pendulum --root projects

Creates the artefact files the six roles read and write, plus a verify.toml
the Checker can run immediately.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEMPLATES = {
    "BRIEF.md": "# Brief\n\n<raw request, in the user's own words>\n",
    "PLAN.md": "# Plan\n\n## Goal (one sentence, testable)\n\nTBD\n\n## Definition of Done\n- [ ] D1 \n\n## Subtasks\n| id | task | owner | output file | depends on |\n|----|------|-------|-------------|------------|\n| T1 |     | builder |             | -          |\n",
    "BUILD_LOG.md": "# Build log\n\n## Built\n\n## Not built\n",
    "CHECK_REPORT.md": "# Check report\n\n## Verdict: not run\n",
    "JUDGE.md": "# Judge\n\n| DoD | planned | built | checked | evidence |\n|-----|---------|-------|---------|----------|\n",
    "REPORT.md": "# Report\n\n## What was asked\n\n## What was built\n\n## How it was verified\n\n## Known limits\n",
    "ARTIFACTS.md": "# Artifacts\n\n",
    "verify.toml": '''[project]
name = "{name}"

# The loop may only stop when every required check below exits 0.
# Add one [[check]] per thing you promise the user.

[[check]]
name = "unit tests"
cmd = "PYTHONPATH=$SPACE_ROOT/scripts python3 -m unittest discover -s tests -t . -v"
required = true
timeout = 300
''',
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise SystemExit("error: --name must contain at least one letter or digit")
    return slug


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="project name (will be slugified)")
    parser.add_argument("--root", default="projects", help="where projects live")
    parser.add_argument("--force", action="store_true", help="overwrite template files")
    args = parser.parse_args(argv)

    slug = slugify(args.name)
    project = Path(args.root) / slug
    (project / "src").mkdir(parents=True, exist_ok=True)
    (project / "tests").mkdir(parents=True, exist_ok=True)

    created, skipped = [], []
    for filename, body in TEMPLATES.items():
        target = project / filename
        if target.exists() and not args.force:
            skipped.append(filename)
            continue
        target.write_text(body.replace("{name}", slug), encoding="utf-8")
        created.append(filename)

    for pkg_dir in (project / "src", project / "tests"):
        init = pkg_dir / "__init__.py"
        if not init.exists():
            init.write_text("", encoding="utf-8")

    test_file = project / "tests" / "test_smoke.py"
    if not test_file.exists():
        test_file.write_text(
            'import unittest\n'
            '\n'
            '\n'
            'class SmokeTest(unittest.TestCase):\n'
            '    def test_workspace_is_alive(self):\n'
            '        """Replace with a real check. This exists so verify.py has work."""\n'
            '        self.assertTrue(True)\n'
            '\n'
            '\n'
            'if __name__ == "__main__":\n'
            '    unittest.main()\n',
            encoding="utf-8",
        )
        created.append("tests/test_smoke.py")

    print(f"project: {project}")
    if created:
        print("created: " + ", ".join(created))
    if skipped:
        print("kept existing: " + ", ".join(skipped))
    print("\nnext: fill BRIEF.md, then run the Planner hat (see SKILL.md section 1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
