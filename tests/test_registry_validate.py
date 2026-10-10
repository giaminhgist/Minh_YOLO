"""Unit tests for the registry validator (B01, A01, A03, A05): it must detect
extra sources, missing revisions, broken files/hashes/dependencies, and bad
skill frontmatter. Fixtures are broken copies of the real plugin in temp dirs,
selected via MINH_PLUGIN_ROOT.

Run: python3 -m unittest tests.test_registry_validate -v   (from the repo root)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO_ROOT, "plugins", "minh-agent")
VALIDATOR = os.path.join(PLUGIN, "scripts", "validate_registry.py")


def run_validator(plugin_root):
    env = dict(os.environ)
    env["MINH_PLUGIN_ROOT"] = plugin_root
    return subprocess.run([sys.executable, VALIDATOR, "--json"], capture_output=True,
                          text=True, timeout=60, env=env)


def copy_plugin(dest):
    shutil.copytree(PLUGIN, dest, ignore=shutil.ignore_patterns("__pycache__"))


class RegistryValidatorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="minh-reg-test-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _fresh(self):
        dest = os.path.join(self.tmp, "p")
        copy_plugin(dest)
        return dest

    def _run_and_fail_with(self, dest, needle, has_components=True):
        if has_components:
            # validator needs components.json present for non-lock errors
            pass
        r = run_validator(dest)
        self.assertEqual(r.returncode, 1, r.stdout)
        data = json.loads(r.stdout)
        all_msgs = [e["message"] for e in data["errors"]] + [w["message"] for w in data["warnings"]]
        self.assertTrue(any(needle in m for m in all_msgs),
                        f"expected an error containing {needle!r}, got: {all_msgs}")
        return data

    def test_valid_plugin_passes(self):
        dest = self._fresh()
        r = run_validator(dest)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_extra_upstream_detected(self):
        dest = self._fresh()
        lock_path = os.path.join(dest, "registry", "upstreams.lock.json")
        lock = json.load(open(lock_path, encoding="utf-8"))
        lock["upstreams"].append(dict(lock["upstreams"][0], id="sixth"))
        json.dump(lock, open(lock_path, "w", encoding="utf-8"))
        self._run_and_fail_with(dest, "exactly 5 upstreams")

    def test_missing_revision_detected(self):
        dest = self._fresh()
        lock_path = os.path.join(dest, "registry", "upstreams.lock.json")
        lock = json.load(open(lock_path, encoding="utf-8"))
        lock["upstreams"][0]["revision"] = "short"
        json.dump(lock, open(lock_path, "w", encoding="utf-8"))
        self._run_and_fail_with(dest, "full 40-hex commit SHA")

    def test_hash_mismatch_detected(self):
        dest = self._fresh()
        comp_path = os.path.join(dest, "registry", "components.json")
        comps = json.load(open(comp_path, encoding="utf-8"))
        target = comps["components"][0]
        target["sha256"] = "0" * 64
        json.dump(comps, open(comp_path, "w", encoding="utf-8"))
        self._run_and_fail_with(dest, "sha256 mismatch")

    def test_missing_dependency_detected(self):
        dest = self._fresh()
        comp_path = os.path.join(dest, "registry", "components.json")
        comps = json.load(open(comp_path, encoding="utf-8"))
        comps["components"][0]["dependencies"] = ["resources/does-not-exist.md"]
        json.dump(comps, open(comp_path, "w", encoding="utf-8"))
        self._run_and_fail_with(dest, "dependency missing")

    def test_allowlist_violation_detected(self):
        dest = self._fresh()
        comp_path = os.path.join(dest, "registry", "components.json")
        comps = json.load(open(comp_path, encoding="utf-8"))
        comps["components"][0]["upstream_id"] = "removed-upstream"
        json.dump(comps, open(comp_path, "w", encoding="utf-8"))
        self._run_and_fail_with(dest, "allowlist violation")

    def test_bad_skill_frontmatter_detected(self):
        dest = self._fresh()
        skill = os.path.join(dest, "skills", "run", "SKILL.md")
        text = open(skill, encoding="utf-8").read()
        text = text.replace("name: run", "name: wrong-name", 1)
        open(skill, "w", encoding="utf-8").write(text)
        self._run_and_fail_with(dest, "frontmatter name must be")

    def test_missing_resource_in_capabilities_detected(self):
        dest = self._fresh()
        caps_path = os.path.join(dest, "registry", "capabilities.json")
        caps = json.load(open(caps_path, encoding="utf-8"))
        caps["entries"][0]["resources"] = ["resources/does-not-exist/"]
        json.dump(caps, open(caps_path, "w", encoding="utf-8"))
        self._run_and_fail_with(dest, "resource missing")


if __name__ == "__main__":
    unittest.main()
