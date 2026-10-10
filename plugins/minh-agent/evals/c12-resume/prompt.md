---
name: c12-resume
description: "C12: resume detects stale state (artifact changed after checkpoint), re-verifies, continues"
runs: 1
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---
Invoke the minh-agent:resume skill. A previous minh-agent workflow left a
checkpoint in .minh-agent/ in this directory (state.json + artifacts). Continue
the run: reconcile the checkpoint with the current workspace, then continue
with the next step ("analyze results and report val_acc"). Report what you
found stale and what you re-verified.
