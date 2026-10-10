---
name: resume
description: "Use when the user wants to continue a previous run or task in a project (workflow, experiment, plan execution). Reads the .minh-agent checkpoint, compares it with the current workspace, re-verifies affected steps, and continues from the first unfinished step without repeating completed work."
---

# minh-agent:resume — continue from a checkpoint

**Contract:** read the real checkpoint, reconcile it with the current workspace, continue
from the first unfinished step. Never redo completed steps blindly; never treat a stale
checkpoint as current truth.

## 1. Read the checkpoint

- Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/state.py show <project-dir>` (and read
  `<project-dir>/.minh-agent/HANDOFF.md` for the human-readable record).
- If no checkpoint exists: say so and ask which task the user means — do not invent state.

## 2. Reconcile with the workspace (stale-state check)

- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/state.py verify <project-dir>` — flags artifacts that
  are missing or changed since the checkpoint, and workspace commit drift.
- Compare with git: `git status`, `git log`, `git diff` since the recorded commit.
- Files changed after the checkpoint → **re-verify the steps that depended on them** before
  continuing. Do not redo a step that had external side effects just because context was lost.

## 3. Continue correctly

- Resume at the first step not marked complete; do not re-run completed steps.
- Re-check tools and permissions for the remaining steps (they may have changed).
- If the checkpoint's constraints (budget, revision rounds) still apply, honor them;
  if the user changes them, record the change in the state.

## 4. Output contract

1. What the checkpoint says was done (with its evidence paths) — and what you re-verified.
2. What changed since the checkpoint and which steps were re-verified as a result.
3. The step you are continuing from, and the result of this session's work.
4. Unverified or stale parts stated explicitly — a summary must not turn hypotheses into facts.

Checkpoints are per-project (`<project>/.minh-agent/`). Two projects never share a run;
syncing checkpoints between machines is the user's own choice, not automatic.
