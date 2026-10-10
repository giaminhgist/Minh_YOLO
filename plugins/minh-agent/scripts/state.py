#!/usr/bin/env python3
"""minh-agent project state manager (stdlib only, Python >= 3.9).

State always lives INSIDE the project at <project>/.minh-agent/ — there is no way
to write outside the project. Writes are atomic (tmp file + os.replace). A lock
file prevents two concurrent runs from sharing a checkpoint.

Usage:
  python3 state.py init <project> [--goal GOAL] [--mode standalone|workflow]
                       [--constraints-json JSON] [--force]
  python3 state.py show <project> [--json]
  python3 state.py update <project> --set-json JSON_OBJECT
  python3 state.py complete-step <project> STEP [--evidence TEXT]
  python3 state.py add-blocker <project> TEXT
  python3 state.py verify <project>
  python3 state.py lock <project> [--force]
  python3 state.py unlock <project>

Exit codes: 0 ok · 1 usage/state error · 2 corrupt state · 3 lock held ·
4 schema not supported · 5 verification failed.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_VERSION = 1
STATE_DIR_NAME = ".minh-agent"
LOCK_NAME = ".lock"
STATE_NAME = "state.json"
HANDOFF_NAME = "HANDOFF.md"


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def plugin_version():
    try:
        with open(os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            return json.load(f).get("version")
    except Exception:
        return None


def git_head(project):
    try:
        proc = subprocess.run(["git", "-C", project, "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=10)
        return proc.stdout.strip() if proc.returncode == 0 else None
    except Exception:
        return None


def resolve_state_dir(project):
    """Confinement: state can only live inside the given project directory."""
    project = os.path.abspath(project)
    if not os.path.isdir(project):
        raise SystemExit(f"state.py: not a directory: {project}")
    return project, os.path.join(project, STATE_DIR_NAME)


def load_state(state_dir, strict=True):
    path = os.path.join(state_dir, STATE_NAME)
    if not os.path.exists(path):
        if strict:
            raise SystemExit(f"state.py: no state at {path} (run `state.py init` first)")
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as ex:
        print(f"FAIL — corrupt state JSON at {path}: {ex}", file=sys.stderr)
        raise SystemExit(2)
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        print(f"FAIL — unsupported schema_version in {path} "
              f"(found {data.get('schema_version') if isinstance(data, dict) else 'n/a'}, "
              f"supported {SCHEMA_VERSION})", file=sys.stderr)
        raise SystemExit(4)
    return data


def atomic_write_json(state_dir, data):
    os.makedirs(state_dir, exist_ok=True)
    path = os.path.join(state_dir, STATE_NAME)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def write_handoff(state_dir, data):
    """Human-readable handoff mirroring the JSON state."""
    lines = [
        "# minh-agent run handoff",
        "",
        f"- run_id: {data['run_id']}",
        f"- goal: {data.get('goal') or '(unset)'}",
        f"- mode: {data.get('mode')}",
        f"- created: {data['created_at']} · updated: {data['updated_at']}",
        f"- workspace commit at start: {data.get('workspace_commit') or '(not a git repo)'}",
        f"- constraints: {json.dumps(data.get('constraints') or {}, ensure_ascii=False)}",
        f"- current step: {data.get('current_step') or '(none)'}",
        "",
        "## Completed steps",
    ]
    for s in data.get("completed_steps") or []:
        ev = f" — evidence: {s['evidence']}" if s.get("evidence") else ""
        lines.append(f"- [x] {s['step']} ({s['at']}){ev}")
    lines += ["", "## Blockers"]
    if data.get("blockers"):
        for b in data["blockers"]:
            lines.append(f"- [!] {b['blocker']} ({b['at']})")
    else:
        lines.append("(none)")
    lines += ["", "## Next action", f"- {data.get('next_action') or '(unset)'}", ""]
    with open(os.path.join(state_dir, HANDOFF_NAME), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_init(args):
    project, state_dir = resolve_state_dir(args.project)
    if os.path.exists(os.path.join(state_dir, STATE_NAME)) and not args.force:
        print(f"FAIL — state already exists at {state_dir} (use --force to start a new run)")
        return 1
    data = {
        "schema_version": SCHEMA_VERSION,
        "run_id": uuid.uuid4().hex[:12],
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "goal": args.goal or "",
        "mode": args.mode or "standalone",
        "plugin_version": plugin_version(),
        "workspace_commit": git_head(project),
        "constraints": {},
        "current_step": "",
        "completed_steps": [],
        "artifacts": [],
        "blockers": [],
        "next_action": "",
        "notes": [],
    }
    if args.constraints_json:
        try:
            data["constraints"] = json.loads(args.constraints_json)
        except json.JSONDecodeError as ex:
            print(f"FAIL — invalid --constraints-json: {ex}")
            return 1
    atomic_write_json(state_dir, data)
    write_handoff(state_dir, data)
    print(f"[ok] state initialized at {state_dir} (run {data['run_id']}, mode {data['mode']})")
    return 0


def cmd_show(args):
    project, state_dir = resolve_state_dir(args.project)
    data = load_state(state_dir)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"run_id:     {data['run_id']}")
        print(f"goal:       {data['goal'] or '(unset)'}")
        print(f"mode:       {data['mode']}")
        print(f"updated:    {data['updated_at']}")
        print(f"current:    {data.get('current_step') or '(none)'}")
        print(f"completed:  {len(data.get('completed_steps') or [])} step(s)")
        for s in data.get("completed_steps") or []:
            print(f"  - [x] {s['step']}")
        for b in data.get("blockers") or []:
            print(f"  - [!] {b['blocker']}")
        print(f"next:       {data.get('next_action') or '(unset)'}")
    return 0


def cmd_update(args):
    project, state_dir = resolve_state_dir(args.project)
    data = load_state(state_dir)
    try:
        patch = json.loads(args.set_json)
    except json.JSONDecodeError as ex:
        print(f"FAIL — invalid --set-json: {ex}")
        return 1
    if not isinstance(patch, dict):
        print("FAIL — --set-json must be a JSON object")
        return 1
    data.update(patch)
    data["updated_at"] = now_iso()
    atomic_write_json(state_dir, data)
    write_handoff(state_dir, data)
    print(f"[ok] state updated ({', '.join(sorted(patch))})")
    return 0


def cmd_complete_step(args):
    project, state_dir = resolve_state_dir(args.project)
    data = load_state(state_dir)
    data.setdefault("completed_steps", []).append({
        "step": args.step, "at": now_iso(), "evidence": args.evidence or "",
    })
    data["current_step"] = ""
    data["updated_at"] = now_iso()
    atomic_write_json(state_dir, data)
    write_handoff(state_dir, data)
    print(f"[ok] step completed: {args.step}")
    return 0


def cmd_add_blocker(args):
    project, state_dir = resolve_state_dir(args.project)
    data = load_state(state_dir)
    data.setdefault("blockers", []).append({"blocker": args.text, "at": now_iso()})
    data["updated_at"] = now_iso()
    atomic_write_json(state_dir, data)
    write_handoff(state_dir, data)
    print(f"[ok] blocker recorded: {args.text}")
    return 0


def cmd_verify(args):
    project, state_dir = resolve_state_dir(args.project)
    data = load_state(state_dir)
    errors = []
    head = git_head(project)
    if data.get("workspace_commit") and head and data["workspace_commit"] != head:
        errors.append(f"workspace moved since state was saved: "
                      f"{data['workspace_commit'][:8]} → {head[:8]} (re-verify affected steps)")
    for a in data.get("artifacts") or []:
        p = os.path.join(project, a["path"])
        if not os.path.exists(p):
            errors.append(f"artifact missing: {a['path']}")
        elif a.get("sha256") and sha256(p) != a["sha256"]:
            errors.append(f"artifact changed since checkpoint: {a['path']}")
    if errors:
        print("FAIL — state verification found issues:")
        for e in errors:
            print(f"  - {e}")
        return 5
    print("PASS — state consistent with workspace.")
    return 0


def cmd_lock(args):
    project, state_dir = resolve_state_dir(args.project)
    os.makedirs(state_dir, exist_ok=True)
    path = os.path.join(state_dir, LOCK_NAME)
    me = f"pid={os.getpid()} at={now_iso()}"
    if os.path.exists(path):
        holder = open(path, encoding="utf-8").read().strip()
        m = re.search(r"pid=(\d+)", holder)
        if not args.force and m:
            try:
                os.kill(int(m.group(1)), 0)
                print(f"FAIL — lock held by {holder} (use --force only if you know the holder is gone)")
                return 3
            except OSError:
                print(f"[..] stale lock from dead process ({holder}); taking over")
                os.remove(path)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, me.encode())
        os.close(fd)
    except FileExistsError:
        print(f"FAIL — lock exists at {path}")
        return 3
    print(f"[ok] locked {state_dir}")
    return 0


def cmd_unlock(args):
    project, state_dir = resolve_state_dir(args.project)
    path = os.path.join(state_dir, LOCK_NAME)
    if os.path.exists(path):
        os.remove(path)
        print("[ok] unlocked")
    else:
        print("[..] no lock present")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="create state for a project")
    p.add_argument("project")
    p.add_argument("--goal")
    p.add_argument("--mode", choices=["standalone", "workflow"], default="standalone")
    p.add_argument("--constraints-json", help="e.g. '{\"max_revision_rounds\": 2, \"budget\": \"...\"}'")
    p.add_argument("--force", action="store_true", help="start a new run even if state exists")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("show", help="print state")
    p.add_argument("project")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("update", help="merge a JSON object into state")
    p.add_argument("project")
    p.add_argument("--set-json", required=True)
    p.set_defaults(fn=cmd_update)

    p = sub.add_parser("complete-step", help="record a completed step")
    p.add_argument("project")
    p.add_argument("step")
    p.add_argument("--evidence")
    p.set_defaults(fn=cmd_complete_step)

    p = sub.add_parser("add-blocker", help="record a blocker")
    p.add_argument("project")
    p.add_argument("text")
    p.set_defaults(fn=cmd_add_blocker)

    p = sub.add_parser("verify", help="verify state against the current workspace")
    p.add_argument("project")
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("lock", help="take the run lock (refuses if held)")
    p.add_argument("project")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_lock)

    p = sub.add_parser("unlock", help="release the run lock")
    p.add_argument("project")
    p.set_defaults(fn=cmd_unlock)

    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
