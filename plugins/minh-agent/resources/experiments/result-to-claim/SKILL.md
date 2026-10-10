# Result-to-Claim Gate

> **Do not wrap this resource in `/loop`, `/schedule`, or any wall-clock scheduler.** It is
> verdict-bearing — it judges whether results support a claim. Re-running that verdict on a
> timer adds no new signal (the verdict changes only when the *results* change, not when the
> clock ticks). What you actually want to schedule is the *external wait that precedes it*:
> experiments finish -> then run this gate **once**. External cadence can drive work; it can
> never acquit it.

When this resource is used: after a set of experiments finishes (main results, not just sanity checks), before claims are committed to a paper or a review response, or when results are ambiguous and need an objective judgment.

Experiments produce numbers; this gate decides what those numbers *mean*. Collect the results, get a reviewer judgment if a reviewer backend is available, then route on the verdict.

## Context: $ARGUMENTS

## When to Use

- After a set of experiments completes (main results, not just sanity checks)
- Before committing to claims in a paper or review response
- When results are ambiguous and you need an assessment that the executor did not write

## Workflow

### Step 1: Collect Results

Gather experiment data from whatever sources are available in the project:

1. **W&B** (if configured): `wandb.Api().run("<entity>/<project>/<run_id>").history()` — metrics, training curves, comparisons
2. **EXPERIMENT_LOG.md**: full results table with baselines and verdicts
3. **EXPERIMENT_TRACKER.md**: check which experiments are DONE vs still running
4. **Log files**: `ssh server "tail -100 /path/to/training.log"` if no other source
5. **`docs/research_contract.md`** (legacy fallback: `idea-stage/docs/research_contract.md`): intended claims and experiment design

Assemble the key information:

- What experiments were run (method, dataset, config, seeds)
- Main metrics and baseline comparisons (deltas, with the split each was computed on)
- The intended claim these experiments were designed to test
- Any known confounds or caveats

### Step 1.5: Deterministic Evidence Pre-check (before any reviewer call)

For every claim that cites a specific number + a source file, verify the evidence
*exists* mechanically — no model call — to catch **hallucinated evidence** before the
judgment runs (see `references/evidence-precheck.md`).

**1. Build the claims list.** From the cited numbers and their result files, write
`[{"id", "value", "source"}, ...]` to `.minh-agent/claims.json` (`source` is the result
file/glob relative to the project root; `value` is the cited number or string).

**2. Run the pre-check — this is a real step, not a suggestion.** Execute the block below
(**Policy B**: warn-and-skip — nothing here may abort the audit). The helper ships with this
resource at `scripts/evidence_check.py` (relative to the directory containing this SKILL.md):

```bash
# Policy B = warn-and-skip: nothing here may abort the audit. cd is non-fatal, the
# helper run is explicitly non-blocking, no pipefail-fragile pipe.
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" 2>/dev/null || true
EVIDENCE_CHECK="<RESOURCE_DIR>/scripts/evidence_check.py"   # ships with this resource
[ -f "$EVIDENCE_CHECK" ] || EVIDENCE_CHECK="tools/evidence_check.py"  # project-vendored copy
[ -f "$EVIDENCE_CHECK" ] || EVIDENCE_CHECK=""

mkdir -p .minh-agent
if [ -n "$EVIDENCE_CHECK" ]; then
    # NB: evidence_check exits 1 when it FINDS hallucinated evidence (value_not_found /
    # path_missing) — that is the useful signal, NOT a failure. So judge success by
    # whether valid JSON was produced, never by exit code. `|| true` keeps set -e calm.
    python3 "$EVIDENCE_CHECK" . --batch .minh-agent/claims.json > .minh-agent/evidence_precheck.json 2>.minh-agent/evidence_precheck.err || true
    if [ -s .minh-agent/evidence_precheck.json ] && python3 -c "import json;json.load(open('.minh-agent/evidence_precheck.json'))" 2>/dev/null; then
        cat .minh-agent/evidence_precheck.json
    else
        echo "WARN: evidence_check produced no valid output (see .minh-agent/evidence_precheck.err);" >&2
        echo "      pre-check skipped (Policy B); the judgment still runs." >&2
    fi
else
    echo "WARN: evidence_check.py not found next to this resource or at tools/evidence_check.py." >&2
    echo "      Pre-check skipped (Policy B); the judgment still runs. Fix: copy the helper" >&2
    echo "      from this resource's scripts/ directory into the project, or cite paths correctly." >&2
fi
```

The output is `{"results": [{id, value, source, status, ...}], "summary": {status: n}}`
with `status` in `{verified, value_not_found, path_missing, unparseable}`.

**3. Act on the statuses.** Any claim returned `value_not_found` or `path_missing` is
**hallucinated evidence** — mark it `claim_supported: no` with
`integrity_status: evidence_not_found` immediately; do NOT spend a reviewer call defending a
number that isn't in the data. `unparseable` claims (no usable value/source) go to the
judgment normally.

**4. Carry the per-claim status into Step 2.** Feed a small
`evidence pre-check: <id> -> verified | value_not_found | path_missing | unparseable`
table (from `.minh-agent/evidence_precheck.json`) into the Step-2 review prompt so the
reviewer knows which claims have real evidence to read. If the pre-check was skipped (helper
missing), say so in that slot rather than omitting it.

`verified` here means only that the cited evidence **exists** — whether it **supports** the
claim is still the reviewer's call in Step 2 (a deterministic gate DRIVES, it does not
ACQUIT).

### Step 2: Reviewer Judgment

Send the collected results to a cross-model reviewer for evaluation. Include ONLY claims
that passed the Step 1.5 pre-check — claims already terminally rejected
(`evidence_not_found`) keep their deterministic verdict and are NOT re-litigated here.

**Reviewer backend gate (honest by construction):**

- **If a cross-model reviewer backend is configured in this session** (a reviewer tool/MCP
  server running a different model family): it judges, and it reads the artifacts itself —
  pass file paths plus the task below, never a pre-digested summary of the results, and never
  the executor's interpretation (an executor that pre-frames the numbers has replaced the
  reviewer with itself). Use the strongest reasoning effort the backend supports; a lower
  effort is a different (weaker) judgment and must be recorded as such.
- **If no such backend is available** (the normal case): the verdict is
  **`REVIEW_UNAVAILABLE`**. Write `CLAIMS_FROM_RESULTS.md` containing ONLY the first line
  `verdict: REVIEW_UNAVAILABLE`, record the same in findings.md, and STOP the claim path.
  The executor never substitutes its own claim judgment — a loop can drive, never acquit.
- **Labeled self-review is allowed only as a clearly non-independent annex.** If the user
  explicitly asks for the executor's own reading, present it as
  `SELF_REVIEW (non-independent — not a verdict)`: it may not be written into
  `CLAIMS_FROM_RESULTS.md` as a claim_supported value, may not unblock ablation planning or
  paper claims, and must never be described as a review.

Downstream steps (knowledge-base edges, ablation planning, paper claims) must not consume a
run without a real reviewer verdict or an explicit, user-accepted `REVIEW_UNAVAILABLE`.
Exception: the deterministic evidence pre-check (Step 1.5) may still terminally mark a claim
`claim_supported: no` for hallucinated evidence — a deterministic rejection needs no
reviewer; only supportive or ambiguous outcomes require one.

Prompt content for the reviewer (when one exists):

```
RESULT-TO-CLAIM EVALUATION

I need you to judge whether experimental results support the intended claim.

Intended claim: [the claim these experiments test]

Experiments run:
[list experiments with method, dataset, metrics]

Results:
[paste key numbers, comparison deltas, significance — or file paths for you to read]

Evidence pre-check (deterministic, from Step 1.5):
[per-claim: <id> -> verified | value_not_found | path_missing.
 A value_not_found/path_missing means the cited number is NOT in its result
 file — treat that claim as having no evidence; do not defend it. `verified`
 means the number exists in the file — YOU still judge whether it supports
 the claim.]

Baselines:
[baseline numbers and sources — reproduced or from paper]

Known caveats:
[any confounding factors, limited datasets, missing comparisons]

Please evaluate:
1. claim_supported: yes | partial | no
2. what_results_support: what the data actually shows
3. what_results_dont_support: where the data falls short of the claim
4. missing_evidence: specific evidence gaps
5. suggested_claim_revision: if the claim should be strengthened, weakened, or reframed
6. next_experiments_needed: specific experiments to fill gaps (if any)
7. confidence: high | medium | low

Be honest. Do not inflate claims beyond what the data supports.
A single positive result on one dataset does not support a general claim.
```

### Step 3: Parse and Normalize

Extract structured fields from the reviewer response:

```markdown
- claim_supported: yes | partial | no
- what_results_support: "..."
- what_results_dont_support: "..."
- missing_evidence: "..."
- suggested_claim_revision: "..."
- next_experiments_needed: "..."
- confidence: high | medium | low
```

### Step 3.5: Check Experiment Integrity (if an audit exists)

**Skip this step if `EXPERIMENT_AUDIT.json` does not exist.** (The integrity audit itself is
produced by a separate integrity pass, not by this resource; if none was run, integrity is
`unavailable`.)

```
if EXPERIMENT_AUDIT.json exists:
    read integrity_status from file
    attach to verdict output:
        integrity_status: pass | warn | fail

    if integrity_status == "fail":
        append to verdict: "[INTEGRITY CONCERN] — audit found issues, see EXPERIMENT_AUDIT.md"
        downgrade confidence to "low" regardless of the judgment

    if integrity_status == "warn":
        append to verdict: "[INTEGRITY: WARN] — audit flagged potential issues"
else:
    integrity_status = "unavailable"
    verdict is labeled "provisional — no integrity audit run"
    (this does NOT block anything — the pipeline continues normally)
```

See `references/experiment-integrity.md` for the full integrity protocol (fake ground truth,
score normalization fraud, phantom results, insufficient scope — and the rule that the model
writing experiment code never judges experiment integrity).

### Step 4: Route Based on Verdict

#### `no` — Claim not supported

1. Record a postmortem in findings.md (Research Findings section):
   - What was tested, what failed, hypotheses for why
   - Constraints for future attempts (what NOT to try again)
2. Update the project's pipeline status (CLAUDE.md, if it tracks one)
3. Decide whether to pivot to the next idea candidate or try an alternative approach

#### `partial` — Claim partially supported

1. Update the working claim to reflect what IS supported
2. Record the gap in findings.md
3. Design and run supplementary experiments to fill evidence gaps
4. Re-run this gate after the supplementary experiments complete
5. **Multiple rounds of `partial` on the same claim** -> record the analysis in findings.md,
   and consider whether to narrow the claim scope or switch ideas

#### `yes` — Claim supported

1. Record the confirmed claim in the project notes
2. If ablation studies are incomplete -> run `experiments/ablation-planner`
3. If all evidence is in -> ready for paper writing

### Step 5: Update the Project Knowledge Base (if one exists)

**Skip this step entirely if the project keeps no knowledge base / research wiki.**

If the project does keep one (e.g. `research-wiki/` or a notes system with idea and claim pages):

- Attach the experiment to the active idea: record `<exp_id>`, verdict, confidence, date, hardware, duration, key metrics, and one line of reasoning
- Link the experiment to the claims it supports or invalidates (as edges/notes), with the decisive metric as evidence
- **Never** rewrite a claim's proof status (`verified` / `refuted` / `unproven`): that axis belongs to whichever resource or process births claims; this gate only attaches experiment evidence
- Update the idea's outcome field (positive | mixed | negative) on raw markdown — no helper script is bundled, and no script needs to run for this step
- If three or more ideas have been tested since the last ideation pass, say so: the knowledge base now knows what does not work

## Rules

- **The reviewer is the judge, not the executor.** The executor collects evidence and routes; a reviewer evaluates. This prevents post-hoc rationalization. If no reviewer backend exists, the verdict is `REVIEW_UNAVAILABLE` — never a self-issued `yes`.
- Do not inflate claims beyond what the data supports. If the verdict is "partial", do not round up to "yes".
- A single positive result on one dataset does not support a general claim. Be honest about scope.
- If `confidence` is low, treat the judgment as inconclusive and add experiments rather than committing to a claim.
- **Fail closed if the reviewer is unavailable.** Write `CLAIMS_FROM_RESULTS.md` with `verdict: REVIEW_UNAVAILABLE` as its first line, record the same in findings.md, and stop. Downstream consumers (ablation planner, paper claims, knowledge-base edges) must not consume a run without a verdict or without the user accepting the labeled unavailability.
- Always record the verdict and reasoning in findings.md, regardless of outcome — including negative and unavailable outcomes.

## Review Tracing

If a reviewer backend actually ran, save a trace for each call (Policy C — forensic; never
silently skip): write `.minh-agent/traces/result-to-claim/<date>_run<NN>/` containing the
prompt sent, the raw response, and the parsed verdict. If no reviewer backend ran, write the
same directory with a single `SKIPPED.md` stating `REVIEW_UNAVAILABLE` and why — the absence
of a review is itself part of the record and must not be indistinguishable from an unlogged
review.

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/result-to-claim/SKILL.md (MIT). See registry/components.json. -->
