# Requesting Code Review

> **When this resource is used:** loaded by the `/minh-agent:review` entry, and by
> `/minh-agent:code` at the final-review stage. Adapted from superpowers
> (see registry/components.json).

## Overview

Dispatch a code reviewer subagent to catch issues before they cascade. The reviewer gets precisely crafted context for evaluation — never your session's history.

**Core principle:** Review early, review often.

## When to Request Review

**Mandatory:**
- After completing major feature
- Before merge to main
- At the end of a plan execution (whole-branch review)

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

## How to Request

**1. Get git SHAs:**
```bash
BASE_SHA=$(git merge-base origin/main HEAD 2>/dev/null || git rev-parse HEAD~1)
HEAD_SHA=$(git rev-parse HEAD)
```

**2. Dispatch code reviewer subagent:**

Dispatch a fresh subagent (the plugin's `reviewer` agent, or a
`general-purpose` subagent), filling the template at [code-reviewer.md](code-reviewer.md).

**Placeholders:**
- `{DESCRIPTION}` - Brief summary of what you built
- `{PLAN_OR_REQUIREMENTS}` - What it should do
- `{BASE_SHA}` - Starting commit
- `{HEAD_SHA}` - Ending commit

**3. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if reviewer is wrong (with reasoning)

## Review Independence Labels

State which kind of review was performed in your report — never inflate it:

- **Fresh-context subagent review** — a separate agent context evaluated the diff.
- **Self-review (labeled)** — the same model/context reviewed its own work. Weaker
  than a fresh reviewer; the user decides whether it suffices.
- **Cross-model review** — only claimable when a genuinely different model backend
  was actually invoked and returned findings. If no cross-model backend is configured,
  report `REVIEW_UNAVAILABLE` for cross-model review and fall back to one of the two
  above with the label intact. Never fabricate an independent review.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll just review the diff myself instead of dispatching a reviewer" | You're the coordinator — reviewing the diff inline burns the context window you need to keep driving the work. Dispatch a reviewer subagent: the diff and the evaluation live in its context, and only the findings come back to you. |
| "The reviewer needs my whole session history to understand the change" | Hand it precisely crafted context, never your session's history. That keeps the reviewer on the work product, not your thought process. |

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

See template at: [code-reviewer.md](code-reviewer.md)

<!-- Source: https://github.com/obra/superpowers.git @ 8ca22dba9a94f28898bbce59f2537ff4d87c747d, path skills/requesting-code-review/SKILL.md (MIT). See registry/components.json. -->
