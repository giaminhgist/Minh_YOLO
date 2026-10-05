#!/usr/bin/env python3
"""One-shot verification gate for the research-skills install (INSTALL.md, Bước 4).

Checks:
  1. Every backtick `~/.claude/...` path in SKILL_INDEX.md exists (files / symlinks).
  2. Paths ending in "/" exist as directories.
  3. No broken symlinks under ~/.claude/skills.
  4. Install artifacts: ~/.claude/CLAUDE.md, orchestrator files (SKILL.md, SKILL_INDEX.md,
     INSTALL.md, this script), ~/.aris/repo, 3 toolkit agents.
  5. ~/.claude/hooks.json is valid JSON and every hook script it references exists.
  6. Counts: >= 200 entries in ~/.claude/skills (exact count reported; expected ~218),
     exactly 20 enabled plugins via `claude plugin list`.

Exit code: 0 = PASS, 1 = FAIL.  Usage: python3 verify_install.py [--index PATH]
"""
import argparse
import json
import os
import re
import subprocess
import sys

HOME = os.path.expanduser("~")
EXPECTED_AGENTS = ["academic-researcher.md", "autoresearch-agent.md", "computer-vision-engineer.md"]
EXPECTED_PLUGINS = 20
EXPECTED_SKILLS = 218
MIN_SKILLS = 200

failures = []
warnings = []


def resolve_index(args):
    if args.index:
        return os.path.abspath(args.index)
    for p in (
        os.path.join(HOME, ".claude/skills/research-orchestrator/SKILL_INDEX.md"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "SKILL_INDEX.md"),
    ):
        if os.path.exists(p):
            return p
    return None


def check_skill_index_paths(idx):
    """Return list of missing paths referenced in SKILL_INDEX.md."""
    s = open(idx, encoding="utf-8").read()
    missing = []
    for cell in set(re.findall(r"`(~/.claude/[^`]+)`", s)):
        for p in cell.split(" · "):
            p = re.sub(r" \(.*\)$", "", p).strip()
            if "<" in p or "…" in p or " " in p:
                continue  # template / prose placeholder
            real = p.replace("~", HOME, 1)
            if p.endswith("/"):
                if not os.path.isdir(real):
                    missing.append(p)
            elif not (os.path.exists(real) or os.path.islink(real)):
                missing.append(p)
    return missing


def check_broken_symlinks():
    broken = []
    skills = os.path.join(HOME, ".claude/skills")
    if os.path.isdir(skills):
        for root, _dirs, files in os.walk(skills):
            for f in files:
                fp = os.path.join(root, f)
                if os.path.islink(fp) and not os.path.exists(fp):
                    broken.append(fp)
            for d in _dirs:
                dp = os.path.join(root, d)
                if os.path.islink(dp) and not os.path.exists(dp):
                    broken.append(dp)
    return broken


def check_hooks():
    hooks_file = os.path.join(HOME, ".claude/hooks.json")
    if not os.path.exists(hooks_file):
        warnings.append("~/.claude/hooks.json not present (toolkit hooks not installed)")
        return
    try:
        d = json.load(open(hooks_file, encoding="utf-8"))
    except Exception as ex:
        failures.append(f"~/.claude/hooks.json invalid JSON: {ex}")
        return
    for h in d.get("hooks", []):
        cmd = h.get("command", "")
        parts = cmd.split()
        if not parts:
            continue
        script = parts[-1]
        if script.startswith("hooks/"):
            fp = os.path.join(HOME, ".claude", script)
            if not os.path.exists(fp):
                failures.append(f"hook script missing: {script} (from hooks.json)")


def check_plugins():
    try:
        out = subprocess.run(
            ["claude", "plugin", "list"], capture_output=True, text=True, timeout=120
        ).stdout
    except Exception as ex:
        failures.append(f"cannot run `claude plugin list`: {ex}")
        return
    enabled = out.count("✔")
    if enabled != EXPECTED_PLUGINS:
        failures.append(f"expected {EXPECTED_PLUGINS} enabled plugins, found {enabled}")
    else:
        print(f"[ok] plugins enabled: {enabled}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", help="path to SKILL_INDEX.md (default: installed copy)")
    args = ap.parse_args()

    idx = resolve_index(args)
    if not idx:
        print("FAIL — SKILL_INDEX.md not found (pass --index or install first)")
        return 1
    print(f"[..] verifying against: {idx}")

    # 1+2. SKILL_INDEX paths
    missing = check_skill_index_paths(idx)
    if missing:
        for m in sorted(set(missing)):
            failures.append(f"path missing: {m}")
    else:
        print(f"[ok] all SKILL_INDEX paths exist (MISSING: 0)")

    # 3. broken symlinks
    broken = check_broken_symlinks()
    if broken:
        for b in broken:
            failures.append(f"broken symlink: {b}")
    else:
        print("[ok] no broken symlinks under ~/.claude/skills")

    # 4. artifacts
    orch = os.path.join(HOME, ".claude/skills/research-orchestrator")
    for f in ("SKILL.md", "SKILL_INDEX.md", "INSTALL.md", "verify_install.py", "configure_hooks.py"):
        if not os.path.exists(os.path.join(orch, f)):
            failures.append(f"missing orchestrator file: {orch}/{f}")
    for f in EXPECTED_AGENTS:
        if not os.path.exists(os.path.join(HOME, ".claude/agents", f)):
            failures.append(f"missing agent: ~/.claude/agents/{f}")
    if not os.path.exists(os.path.join(HOME, ".claude/CLAUDE.md")):
        failures.append("missing ~/.claude/CLAUDE.md")
    if not os.path.exists(os.path.join(HOME, ".aris/repo")):
        failures.append("missing ~/.aris/repo (run ARIS smart_update.sh --apply)")
    print("[ok] orchestrator + agents + ~/.claude/CLAUDE.md + ~/.aris/repo present"
          if not any("missing" in f for f in failures) else "[--] artifact check reported issues above")

    # 5. hooks
    check_hooks()

    # 6. counts
    skills_dir = os.path.join(HOME, ".claude/skills")
    n = len(os.listdir(skills_dir)) if os.path.isdir(skills_dir) else 0
    if n < MIN_SKILLS:
        failures.append(f"skills count too low: {n} (expected ~{EXPECTED_SKILLS})")
    elif n != EXPECTED_SKILLS:
        warnings.append(f"skills count {n} != expected {EXPECTED_SKILLS} (upstream may have changed)")
    print(f"[..] skills entries: {n} (expected ~{EXPECTED_SKILLS})")
    check_plugins()

    print()
    for w in warnings:
        print(f"WARN — {w}")
    if failures:
        print(f"FAIL — {len(failures)} issue(s):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS — all checks green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
