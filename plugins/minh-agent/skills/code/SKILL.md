---
name: code
description: "Use when the user asks to implement a feature, refactor, or fix whose scope is concrete — with or without an approved plan. Test-driven implementation, surgical changes, verification before completion. Never expands scope beyond the request."
---

# minh-agent:code — implementation

**Contract:** change code to satisfy a concrete request, verify it, report what changed and
what remains unverified. No scope expansion, no unrelated refactoring.

## 1. Load the workflow

- With an approved plan + inline execution chosen: follow
  `${CLAUDE_PLUGIN_ROOT}/resources/coding/executing-plans/SKILL.md` — task loop, ledger/rulings in
  the run state, completion contract, one whole-branch review at the end.
- Without a plan (bounded task, user said "just do it"): implement directly, under the TDD rules.

## 2. TDD rules (both paths)

Read `${CLAUDE_PLUGIN_ROOT}/resources/coding/test-driven-development/SKILL.md` and follow it:

- Write the failing test first, watch it fail for the right reason, implement the minimal
  change, watch it pass, run the project's whole suite.
- Bug fixes get a regression test that reproduces the bug — the fix is only "done" when that
  test goes RED→GREEN.
- Exceptions (throwaway prototypes, generated code, config) need the user's OK.

## 3. Surgical changes

- Minimum code that solves the problem; every changed line traces to the request.
- Follow the surrounding code's style, naming, and patterns.
- Never bundle "while I'm here" improvements. If you spot a separate issue, report it — don't fix it.

## 4. When a step fails

Stop the fix loop; switch to
`${CLAUDE_PLUGIN_ROOT}/resources/debugging/systematic-debugging/SKILL.md`: root cause before
fixes, one hypothesis at a time, ≤ 3 failed fixes before questioning the architecture.

## 5. Verification and report

Read `${CLAUDE_PLUGIN_ROOT}/resources/verification/verification-before-completion/SKILL.md`
before claiming anything. Then report:

1. What changed (files, why) and the test evidence (command + real output).
2. What was verified vs. what was not (untested paths, skipped suites, environment limits).
3. Rulings you made if executing a plan (deviations, why, cost if wrong).
4. Deferred minors.

No "done" without fresh evidence. No push/merge unless the user asked in this session.
