"""Unit tests for minh-agent scripts/state.py, driven through its CLI.

Covers B04 (atomic write, schema, corrupt data) and B05 (project confinement,
no shared run state). Runs entirely in temp dirs; no network, no model calls.
Run: python3 -m unittest tests.test_state_cli -v   (from the repo root)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PY = os.path.join(REPO_ROOT, "plugins", "minh-agent", "scripts", "state.py")


def run_state(*args, cwd=None):
    return subprocess.run([sys.executable, STATE_PY, *args], capture_output=True,
                          text=True, timeout=30, cwd=cwd)


class StateCliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="minh-state-test-")
        self.proj = os.path.join(self.tmp, "project")
        os.makedirs(self.proj)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_init_show_complete_verify(self):
        r = run_state("init", self.proj, "--mode", "workflow", "--goal", "g",
                      "--constraints-json", '{"max_revision_rounds": 2}')
        self.assertEqual(r.returncode, 0, r.stderr)
        state = json.load(open(os.path.join(self.proj, ".minh-agent", "state.json")))
        self.assertEqual(state["schema_version"], 1)
        self.assertEqual(state["mode"], "workflow")
        self.assertEqual(state["constraints"]["max_revision_rounds"], 2)
        self.assertTrue(state["run_id"])
        # handoff written
        self.assertTrue(os.path.exists(os.path.join(self.proj, ".minh-agent", "HANDOFF.md")))

        r = run_state("complete-step", self.proj, "step a", "--evidence", "tests pass")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run_state("show", self.proj)
        self.assertEqual(r.returncode, 0)
        self.assertIn("step a", r.stdout)

        r = run_state("verify", self.proj)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_init_refuses_overwrite_without_force(self):
        run_state("init", self.proj)
        r = run_state("init", self.proj)
        self.assertEqual(r.returncode, 1)
        self.assertIn("already exists", r.stdout + r.stderr)
        r = run_state("init", self.proj, "--force")
        self.assertEqual(r.returncode, 0)

    def test_corrupt_json_exit_2(self):
        run_state("init", self.proj)
        with open(os.path.join(self.proj, ".minh-agent", "state.json"), "w") as f:
            f.write("{corrupt")
        r = run_state("show", self.proj)
        self.assertEqual(r.returncode, 2)
        self.assertIn("corrupt", r.stderr)

    def test_schema_mismatch_exit_4(self):
        run_state("init", self.proj)
        with open(os.path.join(self.proj, ".minh-agent", "state.json"), "w") as f:
            json.dump({"schema_version": 99}, f)
        r = run_state("show", self.proj)
        self.assertEqual(r.returncode, 4)

    def test_confinement_nonexistent_project(self):
        r = run_state("init", os.path.join(self.tmp, "nope"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("not a directory", r.stderr)

    def test_two_projects_do_not_share_state(self):
        proj2 = os.path.join(self.tmp, "project two")
        os.makedirs(proj2)
        run_state("init", self.proj, "--goal", "one")
        run_state("init", proj2, "--goal", "two")
        s1 = json.load(open(os.path.join(self.proj, ".minh-agent", "state.json")))
        s2 = json.load(open(os.path.join(proj2, ".minh-agent", "state.json")))
        self.assertNotEqual(s1["run_id"], s2["run_id"])
        self.assertEqual(s1["goal"], "one")
        self.assertEqual(s2["goal"], "two")
        # completing a step in one does not touch the other
        run_state("complete-step", self.proj, "only here")
        s2b = json.load(open(os.path.join(proj2, ".minh-agent", "state.json")))
        self.assertEqual(s2b["completed_steps"], [])

    def test_lock_held_and_unlock(self):
        run_state("init", self.proj)
        # a lock held by a LIVE process must be refused
        holder = subprocess.Popen(["sleep", "60"])
        try:
            with open(os.path.join(self.proj, ".minh-agent", ".lock"), "w") as f:
                f.write(f"pid={holder.pid} at=test")
            r = run_state("lock", self.proj)
            self.assertEqual(r.returncode, 3)
            self.assertIn("lock held", r.stdout + r.stderr)
        finally:
            holder.terminate()
        os.remove(os.path.join(self.proj, ".minh-agent", ".lock"))
        self.assertEqual(run_state("lock", self.proj).returncode, 0)
        self.assertEqual(run_state("unlock", self.proj).returncode, 0)
        # a stale lock (dead pid) is reclaimed, not a dead end
        with open(os.path.join(self.proj, ".minh-agent", ".lock"), "w") as f:
            f.write("pid=999999 at=dead")
        r = run_state("lock", self.proj)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("stale lock", r.stdout)

    def test_verify_detects_changed_artifact(self):
        run_state("init", self.proj)
        art = os.path.join(self.proj, "results.json")
        with open(art, "w") as f:
            json.dump({"acc": 0.5}, f)
        run_state("update", self.proj, "--set-json",
                  json.dumps({"artifacts": [{"path": "results.json",
                                             "sha256": "0" * 64}]}))
        r = run_state("verify", self.proj)
        self.assertEqual(r.returncode, 5)
        self.assertIn("changed since checkpoint", r.stdout + r.stderr)

    def test_unicode_and_space_paths(self):
        proj = os.path.join(self.tmp, "dự án có khoảng trắng")
        os.makedirs(proj)
        r = run_state("init", proj, "--goal", "kiểm tra")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run_state("show", proj)
        self.assertEqual(r.returncode, 0)
        self.assertIn("kiểm tra", r.stdout)


if __name__ == "__main__":
    unittest.main()
