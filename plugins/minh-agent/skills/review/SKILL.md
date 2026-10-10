---
name: review
description: "Use when the user asks for a code review of a diff, PR, branch, or file — or when another minh-agent workflow reaches its review gate. Produces findings with location, evidence, and severity. Does NOT fix anything unless asked."
---

# minh-agent:review — code review

**Contract:** findings with location + evidence + severity. A review-only request changes
nothing — no fixes unless the user asks.

## 1. Scope the review

- Diff/PR/branch: resolve BASE (`git merge-base origin/main HEAD` or `HEAD~1`) and HEAD.
- Files or a single change: read them in full, plus what they touch.
- State the review scope in one line before starting.

## 2. Dispatch a fresh reviewer

Read `${CLAUDE_PLUGIN_ROOT}/resources/reviewing/requesting-code-review/SKILL.md`, then dispatch
the plugin's `reviewer` agent (or a fresh general-purpose subagent) with the template at
`${CLAUDE_PLUGIN_ROOT}/resources/reviewing/requesting-code-review/code-reviewer.md`, filled in
with: DESCRIPTION, PLAN_OR_REQUIREMENTS (the user's request or the plan/spec path), BASE_SHA,
HEAD_SHA, and any Review Focus section from the plan.

The reviewer gets precisely crafted context — never your session history.

## 3. Review independence labels — report exactly which one applies

- **Fresh-context subagent review** — separate agent context evaluated the diff.
- **Self-review (labeled)** — you reviewed your own work; weaker, say so.
- **Cross-model review** — only if a genuinely different model backend was invoked and
  returned findings. No backend configured → `REVIEW_UNAVAILABLE` for cross-model; fall back
  to one of the above with the label intact. Never fabricate an independent review.

## 4. Output contract

1. Scope (base..head or files), and the independence label from §3.
2. Findings ranked by severity (Critical / Important / Minor), each with file:line, the
   failure scenario, and the evidence (code excerpt, test output).
3. An empty-findings result only when the review actually ran — and it is still a real result.
   Do not pad findings to hit a quota; do not invent them.
4. What the review did NOT cover (untested paths, areas outside the diff).
5. If the user asked only for review: stop. No fixes. If they asked review+fix, hand Critical
   and Important findings to `/minh-agent:code` discipline — TDD, one pass, suite green.
