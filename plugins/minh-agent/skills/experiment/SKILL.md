---
name: experiment
description: "Use when the user wants to design an experiment, plan ablations, run a small local experiment, or analyze results. Design is the default; execution only when asked and with clear budget. Real runs only — config, seeds, and results are saved, never invented."
---

# minh-agent:experiment — design, run, analyze

**Contract:** design by default; run only when the user asks and the budget is explicit.
Every number in any output traces to a real saved result. No GPU auto-spend, no paid compute
without explicit user approval.

## 1. Design (default)

Read `${CLAUDE_PLUGIN_ROOT}/resources/experiments/experiment-plan/SKILL.md`
(+ `ablation-planner/SKILL.md` when ablations are in scope) and produce:

- Protocol: hypothesis, metrics (ONE primary, pre-registered; secondaries labeled),
  data splits, controls, and the anti-claim experiment designed to rule out your mechanism.
- Seeds: DEFAULT_SEEDS ≥ 3 fixed BEFORE seeing results; report mean ± std across seeds.
- Ablations: each states `what_it_tests` and `expected_if_component_matters`; no-op ablations
  are forbidden; include the "unnecessary ablations" list and a GPU-hour estimate.
- Budget + stop conditions (2× estimated runtime without completion → flag and move on).
- Statistical plan: Welch over Student's, Wilson CI for proportions, n<30 needs
  justification, effect sizes + CIs, multiplicity/peeking flagged.

Design only → stop after the protocol. Do not run anything.

## 2. Run (only on explicit request)

Read `${CLAUDE_PLUGIN_ROOT}/resources/experiments/run-experiment/SKILL.md`:

- **Cost gate first:** the user approved the run and its budget (rented compute = explicit
  approval; nothing is auto-provisioned). Without approval: stop and report the plan.
- Record config, versions, environment, seeds, data splits WITH the results.
- Save raw outputs to files; never overwrite a previous run's outputs; log every run
  (`EXPERIMENT_LOG.md` or the project's tracker) — negative and failed runs are findings too.
- Stop conditions are real: max budget, 2× runtime, failed sanity stage → stop with status.

## 3. Analyze

Read `${CLAUDE_PLUGIN_ROOT}/resources/experiments/analyze-results/SKILL.md`
(+ `result-to-claim/SKILL.md` before any claim enters prose):

- Report mean ± std across seeds; never a single favorable seed as the result;
  never post-hoc seed selection.
- Separate exploratory from confirmatory analysis and label each.
- Claim strength never exceeds evidence strength; each number traces to a result file.
- Cross-model review of results: only with a real second backend; otherwise
  `REVIEW_UNAVAILABLE` + labeled self-review.

## 4. Output contract

1. What was designed / run / analyzed, with the evidence paths (result files, logs).
2. Config + environment + seeds (runs only).
3. Results with statistics discipline (§1), negative results included.
4. Limits: what the data do NOT support. No generalization beyond the data.
