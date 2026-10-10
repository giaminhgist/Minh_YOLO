---
name: c04-debug
description: "C04: debug entry reproduces, finds root cause, fixes, proves regression gone"
runs: 1
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---
Invoke the minh-agent:debug skill. The unit tests in test_stats.py fail for the
module stats.py in this directory. Reproduce the failure, find the root cause
with evidence, fix it, and prove the regression is handled (show the test
output before and after).
