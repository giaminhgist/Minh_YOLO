---
name: c01-fix-failing-test
description: "C01: run entry routes a simple failing test to a fix within scope, no research pipeline"
runs: 1
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---
Start by invoking the minh-agent:run skill. In this directory there is a Python
module stats.py and its unit test test_stats.py. Running
`python3 -m unittest test_stats -v` fails. Fix the bug, keep the change minimal,
and report the root cause plus the test output before and after the fix.
Do not start any research pipeline, do not plan ablations — just fix the bug.
