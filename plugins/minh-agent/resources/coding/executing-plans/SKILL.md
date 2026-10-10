# Executing Plans

> **When this resource is used:** loaded by the `/minh-agent:code` entry when the user approved an
> implementation plan and chose inline execution. Adapted from superpowers; the per-plan workspace
> and ledger scripts are replaced by minh-agent's native state manager
> (`${CLAUDE_PLUGIN_ROOT}/scripts/state.py`). See registry/components.json.

## Overview

Execute the plan yourself, task by task, in this session: no implementer
subagent per task, no reviewer per task. One fresh-context review of the
whole branch at the end.

**Why inline:** Reviewer-per-task development pays for a fresh implementer
and a fresh reviewer on every task, each re-reading the codebase from zero.
Inline execution pays for one context (yours) plus one reviewer at the end.
What it gives up is a fresh context per task and a second pair of eyes per
task. This workflow keeps what those two things bought, by other means: the
brief is the spec, the ledger is the run state, TDD is the per-task gate, and
the final reviewer is the second pair of eyes.

**Core principle:** The plan already did the thinking. Execute it exactly,
prove each step with a test you watched fail and then pass, and leave a
record that survives your own forgetting.

**Narration:** between tool calls, narrate at most one short line — the
ledger and the tool results carry the record.

**Continuous execution:** Do not pause to check in with the user
between tasks. They chose inline execution to spend less, not to answer
"should I continue?" after every task. Execute all tasks from the plan
without stopping.

**Rulings, not stalls.** Conflicts, ambiguities, plan defects — decide them.
The spec is the binding authority, the plan is its argument, and your
judgment settles what neither answers. Record every decision in the run state
(`state.py update --set-json`) as
`Ruling: <what you decided> — <why> — <what it costs if wrong>`, and keep
going. Deviating from the plan without a recorded ruling is a decision made
in secret.

Four things stop you, and only these: an irreversible or destructive
operation; a security-sensitive action; a side effect outside the project
that norms say you ask about first (a merge, a push to a shared branch, a
publish); and a plan so broken that every path forward is a guess. For
those, stop and ask.

## Setup

- If the plan spans many tasks, initialize a run checkpoint first:
  `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/state.py init <project-dir> --mode workflow --goal "<plan file + goal>"`
  and keep it updated per task. The run state is the ledger; compaction
  cannot erase it.
- Read the plan once, note its context and Global Constraints, and create a
  todo per task. If the plan names a Spec, read that too: the spec is the
  authority the plan argues from, and conflicts inside the plan resolve
  against it. A plan with no reachable spec gets a ledger note saying so —
  rulings made without one are provisional.
- Load `${CLAUDE_PLUGIN_ROOT}/resources/coding/test-driven-development/SKILL.md` now,
  before Task 1. It governs every step of every task below; a plan whose
  steps already say "write the failing test first" does not exempt you
  from reading it.
- Before Task 1, scan the plan for conflicts between tasks. The plan's
  Interfaces blocks tell you where to look: for every task that consumes
  what an earlier task produces, one ledger row — the two tasks, what one
  produces against what the other consumes, and what you found. Tasks that
  share nothing get no row; a plan whose tasks share nothing gets the single
  line `Pre-flight: no shared interfaces`. Rule on each conflict a row
  surfaces with the spec as the binding authority, record the ruling beside
  its row, and start Task 1.

## The Task Loop

Everything you print, and every tool result, stays resident in your
context for the rest of the session. Redirect long test output to a file
and read its tail; read a task's section of the plan, not the whole plan.

### 1. Take the task

- Read the task's section of the plan — including tasks you remember from
  setup: what you remember is a summary, the plan has the exact values,
  signatures, and test cases.
- Mark the task's todo in_progress.

### 2. Work the steps

The plan's steps are already in RED-GREEN order; follow them in that
order under the TDD rules loaded at setup. A test
step's code is written first and run first. Watching it fail is a step,
not a formality — a test that passes before the implementation exists is
a finding about the test.

Every step that runs a command has an `Expected:` line. Run the command,
read its output, and compare. Three outcomes:

- **Matches.** Next step.
- **The code is wrong.** Use `${CLAUDE_PLUGIN_ROOT}/resources/debugging/systematic-debugging/SKILL.md`.
  Find the cause; never patch the symptom to make the step's output match.
- **The plan is wrong** — a step contradicts the spec, an interface from an
  earlier task doesn't match what this task consumes, a command that
  cannot work. Rule on the smallest change that satisfies the spec, record
  it in the run state as `Task <N>: Ruling: <finding> — <what you decided and why>`,
  and continue. The ruling is carried, not remembered: later tasks that touch
  the same interface read it from the run state.

Commit as the plan's commit steps say.

### 3. The completion contract

Before a task's completion line, all of the following are true, with evidence
in this session — not inferred from the diff looking right:

- Every test the task names exists and ran in this task, and you read
  the output.
- The final test run for the task passed, and the command and result are
  recorded in the run state.
- Every `Expected:` line in the task was compared against real output.
- Every deviation from the plan has a `Ruling:` line in the run state.

`${CLAUDE_PLUGIN_ROOT}/resources/verification/verification-before-completion/SKILL.md` governs
the claim. If any item is missing, the task is not complete: finish it.

### 4. Complete the task

Record the completion in the run state with the test command and its result
(`state.py complete-step <project-dir> "<task name>" --evidence "<test command>"`),
mark the todo complete, and take the next task.

## Final Review

After the last task, build the review package: the full diff from the branch
base (`git diff <merge-base>..HEAD` plus changed file paths), the plan and
spec paths, the plan's Review Focus section verbatim if it has one, and the
run state's `Ruling:` lines so the reviewer can weigh the calls you made.

**With a subagent tool:** dispatch the plugin's `reviewer` agent (or a fresh
subagent using `${CLAUDE_PLUGIN_ROOT}/resources/reviewing/requesting-code-review/code-reviewer.md`)
on the most capable available model — the whole-branch review is a judgment task. Specify the model
explicitly; an omitted model inherits the session's, which may not be the
most capable. This is the one fresh context the whole run buys. Do not
skip it, and do not replace it with your own read of the diff.

**Without a subagent tool:** read code-reviewer.md and perform that review
yourself against the package, as a separate pass after the last task.
Record `Final review: self-review (no subagent tool)` in the run state,
and say so in your final message: a self-review by the author is
weaker than a fresh reviewer, and the user decides whether that
is enough before merge.

Sort the findings before you act on any of them. The reviewer's severity
labels are advice; the gate is yours. Its "Declined to judge" list is
yours too: every line there is a ruling you make and record, exactly like
a plan conflict — `Final: Ruling: <behavior the reviewer set aside> —
<what a reasonable person using this software gets, and why that stands
or why it is now a finding> — <cost if wrong>`. Re-grade first, by effect: the
spec is a vision document, and a finding's grade is what a reasonable
person using this software gets if it ships, not whether the spec names
the input that triggers it. Then:

- **Critical and Important** enter the fix pass.
- **Minor** goes to the run state as `Final: minor (deferred): <one-liner>`
  and to your final message under "Deferred minors". Minors never enter
  the fix pass, and never become rulings.

Fix the Critical and Important findings yourself — you are the
implementer here — in ONE pass. Each fix is verified by TDD, not by a
second reviewer: write the test that reproduces the finding, watch it
fail, make it pass, then run the whole suite. Record each in the run state as
`Final: fixed <finding> — <test name> RED→GREEN, suite <N>/<N>`. A fix
without a test that failed first is not verified; a suite that is not
green after the pass means the pass is not over. Do not dispatch a
re-review: it would re-read a diff whose covering tests already answer
"addressed" and whose suite run already answers "broke nothing".

A finding you decide not to fix is a ruling — `Final: Ruling: <finding> —
<why the code stands> — <cost if wrong>` — and reaches the user
in the rulings list. There is no second fix pass.

## Finish

Collect every `Ruling:` line from the run state into your final message under
"Rulings I made", in the order you made them, each with what it costs if wrong,
and every `minor (deferred)` line under "Deferred minors". Both lists are
exhaustive. Your final message is the only place the decisions you took on
the user's behalf — and the findings you chose not to act on — reach them.

When the final review is clean and its fixes are committed, mark the run
complete (`state.py complete-step` for the final review step). The git
history and the run state are the record now.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I remember what Task N says" | You remember a summary. The plan has the exact values. Read it. |
| "The plan's code is right, skip watching the test fail" | A test you never saw fail proves nothing. It is one step. Run it. |
| "I'll run the full suite at the end instead of per step" | Per-step runs are how you learn which step broke it. The end-of-task run is the contract, not a substitute. |
| "The plan is wrong here, I'll just do the right thing" | Do the right thing and record the ruling. Unrecorded deviation is a decision made in secret. |
| "I'll write the state lines after a few tasks" | Compaction does not wait for a convenient moment. One line per task, in the same message as the commit. |
| "Let me check in before the next task" | They chose inline to spend less. Progress prompts spend their time instead. Only the four stops stop you. |
| "I read my own diff carefully; the final reviewer is redundant" | Same author, same blind spots. The reviewer is the only fresh context this run buys. |
| "Tests should pass, the change was trivial" | "Should" is not evidence. The contract requires the command and its output. |
| "Subagents are slow and expensive, I'll skip the final review too" | Inline already removed the per-task reviewers. One review of the whole branch is the floor, not the ceiling. |
| "The reviewer said Minor, so it's Minor" | The label graded the spec's silence. Grade what the person gets. Re-grade, then gate. |
| "The fix is obvious, no need for a failing test first" | The failing test is the only proof the finding was real and is now gone. Without it you have a diff and a hope. |
| "I'll fix the minors too while I'm in there" | Every minor you fix is a test, a fix, and a suite run the user did not ask for. Record them; the user decides. |

<!-- Source: https://github.com/obra/superpowers.git @ 8ca22dba9a94f28898bbce59f2537ff4d87c747d, path skills/executing-plans/SKILL.md (MIT). See registry/components.json. -->
