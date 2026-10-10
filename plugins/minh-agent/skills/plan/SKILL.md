---
name: plan
description: "Use when the user asks for a plan, design, or spec before any code is written — a multi-step change, a new feature, or an architecture decision. Produces a reviewable plan with verification criteria. Does NOT modify code."
---

# minh-agent:plan — design and implementation planning

**Contract:** a `/minh-agent:plan` request produces a plan or design — it never changes code.
A one-line fix does not belong here; route it to `/minh-agent:code`.

## Classify the request (say it out loud)

Read `${CLAUDE_PLUGIN_ROOT}/resources/planning/brainstorming/SKILL.md` and classify:

- **Spike** — feasibility question ("can we…"). Output: an answer, not kept code.
- **Bounded** — small change to code that already exists. Present a short in-chat design,
  get approval, then stop — implementation goes through `/minh-agent:code` afterwards.
- **Architectural** — new subsystem or restructuring. Full path: questions → approaches →
  sectioned design → written spec (`docs/specs/…`) → user review → implementation plan.

The HARD-GATE applies: no implementation action of any kind before the user approves the
artifact for the stage you are at. When in doubt between two paths, take the heavier one.

## Writing the implementation plan

When the design is approved, write the plan following
`${CLAUDE_PLUGIN_ROOT}/resources/planning/writing-plans/SKILL.md`:

- Save to `docs/plans/YYYY-MM-DD-<feature>.md` with the standard header (Goal, Architecture,
  Tech Stack, Spec path, Global Constraints, Review Focus).
- Tasks sized so each has its own test cycle and reviewer gate; steps are one action with a
  checkable result; every verification step carries the exact command and its expected output.
- Self-review before presenting: spec coverage, step scan, type consistency, Review Focus,
  proportion (a plan is decisions, not a transcript of the code).

## Output contract

1. The plan file path + the classification you used.
2. The plan itself, with per-task verification commands.
3. What the plan does NOT cover, and which decisions remain for the user.
4. A stop: no code was changed. State the next step (review the plan, choose execution method).

## Verification of your own work

- Re-read the plan against the user's constraints: every requirement maps to a task with a check.
- If the user only asked to plan, nothing else happens. Do not pre-implement "just to validate".
