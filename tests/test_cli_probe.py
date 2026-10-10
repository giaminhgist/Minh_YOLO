"""CLI probe helper + its own tests (B03): external commands are judged by
exit code and stderr, with a hard timeout — never by counting checkmarks or
scanning for emoji in stdout.

Run: python3 -m unittest tests.test_cli_probe -v   (from the repo root)
"""
import os
import stat
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE = os.path.join(REPO_ROOT, "tests", "cli_probe.py")


class CliProbeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="minh-cli-test-")
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_fake_cli(self, name, body):
        path = os.path.join(self.tmp, name)
        with open(path, "w") as f:
            f.write("#!/bin/sh\n" + body)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        return path

    def _probe(self, *cmd, timeout=10):
        return subprocess.run([sys.executable, PROBE, "--timeout", str(timeout), "--", *cmd],
                              capture_output=True, text=True, timeout=30)

    def test_success_is_exit_code_zero(self):
        r = self._probe("true")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("exit=0", r.stdout)

    def test_failure_is_exit_code_nonzero(self):
        cli = self._write_fake_cli("fail-cli", "echo '✔ everything fine' >&1; echo 'boom' >&2; exit 3\n")
        r = self._probe(cli)
        self.assertNotEqual(r.returncode, 0)  # probe reports failure
        out = r.stdout
        self.assertIn("exit=3", out)
        self.assertIn("boom", out)          # stderr captured and surfaced
        self.assertNotIn("PASS", out.split("stdout")[0])  # ✔ alone never counts as success

    def test_timeout_kills_and_reports(self):
        cli = self._write_fake_cli("slow-cli", "sleep 30\n")
        r = self._probe(cli, timeout=2)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("timeout", (r.stdout + r.stderr).lower())

    def test_missing_binary_reports_not_runs(self):
        r = self._probe(os.path.join(self.tmp, "does-not-exist"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not found", (r.stdout + r.stderr).lower())


if __name__ == "__main__":
    unittest.main()
