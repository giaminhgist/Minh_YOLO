# Ablation Planner

When this resource is used: after main results have passed the `experiments/result-to-claim` gate with `claim_supported = yes` or `partial`, when the user explicitly asks for ablation planning, or when a reviewer identifies missing ablations. Designs the ablation set a rigorous reviewer would demand, then implements and runs it.

Systematically design ablation studies that answer the questions reviewers will ask, from a reviewer's adversarial perspective; feasibility and implementation stay with the engineer's.

Context: $ARGUMENTS

## When to Use

- Main results pass `experiments/result-to-claim` with claim_supported = yes or partial
- User explicitly requests ablation planning
- A reviewer (or the user reviewing as a reviewer) identifies missing ablations

Do not start from a claim that has no evidence yet — ablations isolate a working effect, they do not create one.

## Workflow

### Step 1: Prepare Context

Read the available project files to build the full picture:

- Method description and components (from `docs/research_contract.md`, `idea-stage/docs/research_contract.md`, or the project CLAUDE.md)
- Current experiment results (from EXPERIMENT_LOG.md, EXPERIMENT_TRACKER.md, `refine-logs/`, or the project's run outputs)
- Confirmed and intended claims (from the `experiments/result-to-claim` verdict or project notes)
- Available compute resources (from the project CLAUDE.md / server notes, if present)

### Step 2: Reviewer-Perspective Design

**Reviewer backend gate.** The ablation design is a verdict-adjacent artifact: it decides what evidence the claim still needs. Handle it honestly according to what is actually available:

- **If a cross-model reviewer backend is configured in this session** (a reviewer tool or MCP server running a different model family): it leads the design, with artifacts passed by path plus the task below. The executor must not pre-filter or pre-rank the ablation list before the reviewer sees the method and results.
- **If no such backend exists** (the normal case): design the ablations natively with the reviewer-perspective prompt below as the specification, and label the plan output `review_mode: SELF_DESIGNED (no cross-model reviewer available)`. Never present a self-designed plan as independently reviewed.

Either way, the design must answer for the given method and results: (1) isolate the contribution of each novel component, (2) answer questions reviewers will definitely ask, (3) test sensitivity to key hyperparameters, (4) compare against natural alternative design choices. Inputs to reason over (placed in the prompt when a reviewer backend exists):

```
Method: [description from project files]
Components: [list of removable/replaceable components]
Current results: [key metrics from experiments]
Claims: [what we claim and current evidence]

For each ablation, specify:
- name: what to change (e.g., "remove module X", "replace Y with Z")
- what_it_tests: the specific question this answers
- expected_if_component_matters: what we predict if the component is important
- priority: 1 (must-run) to 5 (nice-to-have)

Also provide:
- coverage_assessment: what reviewer questions these ablations answer
- unnecessary_ablations: experiments that seem useful but won't add insight
- suggested_order: run order optimized for maximum early information
- estimated_compute: total GPU-hours estimate
```

### Step 3: Parse Ablation Plan

Normalize the design into this structured format:

```markdown
## Ablation Plan

### Component Ablations (highest priority)
| # | Name | What It Tests | Expected If Matters | Priority |
|---|------|---------------|---------------------|----------|
| 1 | remove module X | contribution of X | performance drops on metric Y | 1 |
| 2 | replace X with simpler Z | value of learned vs fixed | drops, especially on dataset A | 2 |

### Hyperparameter Sensitivity
| # | Parameter | Values to Test | What It Tests | Priority |
|---|-----------|---------------|---------------|----------|
| 3 | lambda | [0.01, 0.1, 1.0] | sensitivity to regularization | 3 |

### Design Choice Comparisons
| # | Name | What It Tests | Priority |
|---|------|---------------|----------|
| 4 | joint vs separate matching | whether joint adds value | 4 |

### Coverage Assessment
[What reviewer questions these ablations answer]

### Unnecessary Ablations
[Experiments that seem useful but won't add insight — skip these]

### Run Order
[Optimized for maximum early information]

### Estimated Compute
[Total GPU-hours]

### Review Mode
[SELF_DESIGNED (no cross-model reviewer available) | cross-model reviewer: <backend id>]
```

### Step 4: Engineering Review of Feasibility

Before running anything, the executor checks:

- Compute budget: can we afford all ablations with the available GPUs and the current `max_budget` (if one is set)?
- Code changes: which ablations need code modifications vs config-only changes?
- Dependencies: which ablations can run in parallel on distinct GPUs?
- Cuts: if the budget is tight, propose removing the lowest-priority ablations and ask the owner of the design (the reviewer backend, or the user) to confirm the cut list

### Step 5: Implement and Run

1. Create configs/scripts for each ablation (config-only changes first)
2. Smoke test each ablation before the full run
3. Run in the suggested order through `experiments/run-experiment`, using descriptive names (e.g., `ablation-no-module-X`)
4. Track results in EXPERIMENT_LOG.md, with the seed list used for each cell
5. After all ablations complete -> update findings.md with the insights

## Rules

- **The design is reviewer-first, engineer-second.** The executor does not pre-filter or bias the ablation list before it is designed. If a cross-model reviewer backend led the design, the executor treats its list as the starting point and argues feasibility with it, not around it.
- Every ablation must have a clear `what_it_tests` and `expected_if_component_matters`. No "just try it" experiments.
- No-op ablations are forbidden: never design an ablation whose variant is identical to the baseline.
- Config-only ablations take priority over those needing code changes (faster, less error-prone).
- Component ablations (remove/replace) take priority over hyperparameter sweeps.
- If total compute exceeds budget, propose cuts and ask the design owner to re-prioritize — never silently drop ablations.
- Record all ablation results in EXPERIMENT_LOG.md, including negative results (component removal had no effect = an important finding, not a failed run).
- Ablation runs follow the same protocol, data splits, and seed policy as the main results; raw results are preserved.

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/ablation-planner/SKILL.md (MIT). See registry/components.json. -->
