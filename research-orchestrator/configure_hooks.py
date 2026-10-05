#!/usr/bin/env python3
"""Trim ~/.claude/hooks.json (awesome-claude-code-toolkit installer) to the safe subset.

Default action: write the 9 safe hooks — secret-scanner (Write/Edit), suggest-compact,
session-start, context-loader, session-end, learning-log, pre-compact, notification-log.
The full 25-hook set is backed up to ~/.claude/hooks.json.bak-toolkit-full on first run
(never overwritten). Idempotent — safe to re-run.

Usage:
  python3 configure_hooks.py          # trim to the safe subset
  python3 configure_hooks.py --full   # restore the full installer set from the backup
"""
import json
import os
import sys

HOME = os.path.expanduser("~")
HOOKS = os.path.join(HOME, ".claude/hooks.json")
BACKUP = os.path.join(HOME, ".claude/hooks.json.bak-toolkit-full")

SAFE_HOOKS = [
    {"type": "PreToolUse", "matcher": "Write",
     "description": "Scan for leaked secrets before writing files",
     "command": "node hooks/scripts/secret-scanner.js"},
    {"type": "PreToolUse", "matcher": "Edit",
     "description": "Scan for leaked secrets before editing files",
     "command": "node hooks/scripts/secret-scanner.js"},
    {"type": "PostToolUse", "matcher": "Bash",
     "description": "Track edit count and suggest compaction at intervals",
     "command": "node hooks/scripts/suggest-compact.js"},
    {"type": "SessionStart",
     "description": "Load previous context and detect package manager",
     "command": "node hooks/scripts/session-start.js"},
    {"type": "SessionStart",
     "description": "Load project context including git state, config files, and pending todos",
     "command": "node hooks/scripts/context-loader.js"},
    {"type": "SessionEnd",
     "description": "Save current context state for next session",
     "command": "node hooks/scripts/session-end.js"},
    {"type": "SessionEnd",
     "description": "Save session learnings and recent commits to daily log",
     "command": "node hooks/scripts/learning-log.js"},
    {"type": "PreCompact",
     "description": "Save important context before compaction",
     "command": "node hooks/scripts/pre-compact.js"},
    {"type": "Notification",
     "description": "Log notifications for later review",
     "command": "node hooks/scripts/notification-log.js"},
]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    full = "--full" in sys.argv
    if full:
        if not os.path.exists(BACKUP):
            print(f"FAIL — backup not found: {BACKUP}")
            return 1
        with open(BACKUP, encoding="utf-8") as f:
            content = f.read()
        json.loads(content)  # validate
        with open(HOOKS, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"restored full hook set from {BACKUP} ({len(json.loads(content)['hooks'])} hooks)")
        return 0

    target = json.dumps({"hooks": SAFE_HOOKS}, indent=2, ensure_ascii=False) + "\n"

    if os.path.exists(HOOKS):
        with open(HOOKS, encoding="utf-8") as f:
            current = f.read()
        if current == target:
            print(f"hooks.json already the safe subset ({len(SAFE_HOOKS)} hooks) — no change")
            return 0
        if not os.path.exists(BACKUP):
            with open(BACKUP, "w", encoding="utf-8") as f:
                f.write(current)
            print(f"backed up current hooks.json → {BACKUP}")
    else:
        print("WARN — ~/.claude/hooks.json not found; writing safe subset anyway")

    with open(HOOKS, "w", encoding="utf-8") as f:
        f.write(target)
    print(f"hooks.json trimmed to {len(SAFE_HOOKS)} safe hooks"
          + (f" (full set at {BACKUP})" if os.path.exists(BACKUP) else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
