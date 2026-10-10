---
name: c05-review
description: "C05: review entry finds planted bugs with location and evidence, does not fix"
runs: 1
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite]
---
Invoke the minh-agent:review skill. Review the latest commit (HEAD~1..HEAD) of
this git repository. The commit message is "refactor discount logic". Report
findings with severity and location. This is a review-only request: do NOT fix
anything.
