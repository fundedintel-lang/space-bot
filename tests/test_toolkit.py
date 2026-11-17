"""Tests for the toolkit itself. A verifier nobody verifies is a rumour."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(*args, cwd=None):
    return subprocess.run(
        [sys.executable, *args], capture_output=True, text=True, cwd=cwd or ROOT
    )


class VerifyTest(unittest.TestCase):
    def _project(self, toml_body: str) -> Path:
        tmp = Path(tempfile.mkdtemp())
        (tmp / "verify.toml").write_text(toml_body, encoding="utf-8")
        return tmp

    def test_passing_check_exits_zero(self):
        project = self._project('[[check]]\nname = "ok"\ncmd = "true"\n')
        proc = run(str(SCRIPTS / "verify.py"), "--project", str(project))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("verdict: PASS", proc.stdout)
        self.assertTrue((project / "VERIFY.md").is_file())

    def test_failing_required_check_exits_one(self):
        project = self._project('[[check]]\nname = "bad"\ncmd = "exit 3"\n')
        proc = run(str(SCRIPTS / "verify.py"), "--project", str(project))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("FAIL", (project / "VERIFY.md").read_text())

    def test_optional_failure_does_not_block(self):
        project = self._project(
            '[[check]]\nname = "soft"\ncmd = "exit 1"\nrequired = false\n'
        )
        proc = run(str(SCRIPTS / "verify.py"), "--project", str(project))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("verdict: PASS", proc.stdout)

    def test_expect_stdout_is_enforced(self):
        project = self._project(
            '[[check]]\nname = "quiet"\ncmd = "true"\nexpect_stdout = "hello"\n'
        )
        proc = run(str(SCRIPTS / "verify.py"), "--project", str(project))
        self.assertEqual(proc.returncode, 1)

    def test_timeout_fails_closed(self):
        project = self._project(
            '[[check]]\nname = "slow"\ncmd = "sleep 5"\ntimeout = 1\n'
        )
        proc = run(str(SCRIPTS / "verify.py"), "--project", str(project))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("timeout", proc.stdout)

    def test_missing_config_is_config_error(self):
        proc = run(str(SCRIPTS / "verify.py"), "--project", "/tmp/definitely-not-here")
        self.assertEqual(proc.returncode, 2)

    def test_env_points_at_repo_root(self):
        project = self._project(
            '[[check]]\nname = "env"\ncmd = "test -f $SPACE_ROOT/README.md"\n'
        )
        proc = run(str(SCRIPTS / "verify.py"), "--project", str(project))
        self.assertEqual(proc.returncode, 0, proc.stdout)


class PlanTest(unittest.TestCase):
    def setUp(self):
        self.project = Path(tempfile.mkdtemp())

    def test_budget_exhaustion_exits_one(self):
        run(str(SCRIPTS / "plan.py"), "new", "--project", str(self.project),
            "--budget", "1")
        proc = run(str(SCRIPTS / "plan.py"), "round", "--project",
                   str(self.project), "--role", "checker", "--verdict", "FAIL")
        self.assertEqual(proc.returncode, 1)
        state = json.loads((self.project / ".loop.json").read_text())
        self.assertEqual(len(state["rounds"]), 1)

    def test_pass_rounds_do_not_consume_budget(self):
        run(str(SCRIPTS / "plan.py"), "new", "--project", str(self.project),
            "--budget", "2")
        for _ in range(3):
            proc = run(str(SCRIPTS / "plan.py"), "round", "--project",
                       str(self.project), "--role", "checker", "--verdict", "PASS")
            self.assertEqual(proc.returncode, 0)

    def test_status_reports_last_round(self):
        run(str(SCRIPTS / "plan.py"), "new", "--project", str(self.project))
        run(str(SCRIPTS / "plan.py"), "round", "--project", str(self.project),
            "--role", "judge", "--verdict", "PASS", "--note", "all rows covered")
        proc = run(str(SCRIPTS / "plan.py"), "status", "--project", str(self.project))
        self.assertIn("all rows covered", proc.stdout)


class TopicsAndSanityTest(unittest.TestCase):
    def test_topics_unknown_domain_errors(self):
        proc = run(str(SCRIPTS / "topics.py"), "--domains", "nope")
        self.assertEqual(proc.returncode, 2)

    def test_topics_markdown_has_rows(self):
        proc = run(str(SCRIPTS / "topics.py"), "--domains", "mechanics")
        self.assertIn("| mechanics |", proc.stdout)

    def test_sanity_demo_catches_mismatch(self):
        proc = run(str(SCRIPTS / "sanity.py"), "--demo")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("negative control caught it", proc.stdout)


class ScaffoldTest(unittest.TestCase):
    def test_scaffold_is_idempotent_and_keeps_user_edits(self):
        root = Path(tempfile.mkdtemp())
        run(str(SCRIPTS / "scaffold.py"), "--name", "Demo Proj", "--root", str(root))
        project = root / "demo-proj"
        (project / "PLAN.md").write_text("# my real plan\n", encoding="utf-8")
        run(str(SCRIPTS / "scaffold.py"), "--name", "Demo Proj", "--root", str(root))
        self.assertEqual((project / "PLAN.md").read_text(), "# my real plan\n")
        self.assertTrue((project / "verify.toml").is_file())

    def test_new_project_verifies_green(self):
        root = Path(tempfile.mkdtemp())
        run(str(SCRIPTS / "scaffold.py"), "--name", "green", "--root", str(root))
        proc = run(str(SCRIPTS / "verify.py"), "--project", str(root / "green"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
