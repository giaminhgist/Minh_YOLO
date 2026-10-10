# Paper Claim Audit: Zero-Context Evidence Verification

> **Do not wrap this resource in `/loop`, `/schedule`, or any wall-clock scheduler.** It is
> verdict-bearing — it judges paper-to-evidence fidelity with a deliberately
> zero-context fresh reviewer. Re-firing that verdict on a timer adds no new
> signal (it changes only when the *paper or results* change). What you schedule
> is the *external wait that precedes it* — draft ready → then audit **once**.

When this resource is used: before submission, or whenever a paper draft's numbers must be checked against raw result files by a reviewer who did not write them — "check paper claims", "verify numbers", "论文数字核对", "审查论文数据".

## Context: $ARGUMENTS

Arguments: `[paper-directory]`.

## Why This Exists

The executor writes experiments AND writes the paper. It "knows" what the results should be. This creates confirmation bias:

- Rounding 84.7% up to 85.3%
- Reporting best seed instead of average
- Citing metrics from a different experiment config
- Claiming "improves by 15%" when the delta is actually 12.8%

A **fresh reviewer with zero prior context** catches these because it has no expectations — it just compares paper text vs raw files.

## How This Differs From Other Audit Resources

| Resource | Question it answers |
|-------|-------------------|
| experiment-integrity audit | Is the experiment code honest? (fake GT, normalization fraud) |
| `result-to-claim` | Does the data scientifically support this claim? |
| **`paper-claim-audit`** | **Does the paper report the data truthfully and precisely?** |

## Core Principle

**Zero-context, fresh reviewer.** The auditor receives ONLY:

- Paper `.tex` files (the claims)
- Raw result files (the evidence)

It does NOT receive:

- ❌ EXPERIMENT_LOG.md
- ❌ EXPERIMENT_TRACKER.md
- ❌ AUTO_REVIEW.md
- ❌ NARRATIVE_REPORT.md
- ❌ Any executor summary or interpretation
- ❌ Any prior audit results
- ❌ Any conversation history

This is **stricter than ordinary reviewer independence** — it is zero-context evidence audit.

## Reviewer Backend (read before Step 2)

- **Preferred**: a *cross-model* reviewer — a model from a different family than the executor — reached through the session's configured reviewer backend (e.g. a Codex/OpenAI MCP server), fresh thread/session per run, reasoning effort as high as the backend exposes (target `ultra`/`xhigh`).
- **Backend absent → `REVIEW_UNAVAILABLE`.** You may still run the audit protocol below as a *labeled self-review* in a fresh context (a new subagent that is told to read only the listed paths and to ignore summaries), but the report MUST state that the reviewer was not independent and the JSON verdict must be `REVIEW_UNAVAILABLE` with a `review_unavailable: true` flag. Never present a same-model self-review as a cross-model audit; never invent a reviewer score.
- **Fresh context every run.** Use a new thread/session; never continue a previous reviewer conversation. Zero context is the whole point — a reviewer with prior context stops being an independent check.

## Workflow

### Step 1: Collect Files (Executor — Claude)

Locate paper and result files WITHOUT reading or interpreting them.

**Paper files** (claims) — paths shown relative to the shell's working
directory so you can find them with `ls`; when writing them into
`audited_input_hashes`, use paths relative to the paper dir (no `paper/`
prefix) per the "Submission Artifact Emission" section below:

```
paper/main.tex                # → hash key: main.tex
paper/sections/*.tex          # → hash key: sections/*.tex
paper/tables/*.tex (if separate)   # → hash key: tables/*.tex
```

**Result files** (evidence):

```
results/*.json, results/*.jsonl, results/*.csv, results/*.tsv
outputs/*.json, outputs/*.csv
wandb-summary.json (if exists)
**/metrics.json, **/eval_results.json
**/config.yaml, **/args.json (experiment configs)
```

**Exclude** (no summaries, no interpretations):

```
EXPERIMENT_LOG.md, EXPERIMENT_TRACKER.md, AUTO_REVIEW*.md
NARRATIVE_REPORT.md, PAPER_PLAN.md, findings.md
Any .md file that is an executor-written summary
```

### Step 2: Fresh Reviewer Audit (NEW thread, no reply)

Send the reviewer the file paths and the protocol below. **Every run is a fresh context.**

```
You are a paper-to-evidence auditor. You have ZERO prior context about
this research. You will receive only paper source files and raw result
files. Your job is to verify that every number in the paper exactly
matches the raw evidence.

Paper files to read:
[list .tex file paths]

Result files to read:
[list .json/.csv/.yaml file paths]

## Audit Protocol

### A. Extract Every Quantitative Claim
For each number, percentage, comparison, or scope statement in the paper:
- Location (section, table, caption, or inline text)
- Exact claim text
- The number or comparison being made

### B. Trace Each Claim to Evidence
For each extracted claim, find the supporting raw data:
- Which result file contains this number?
- What is the EXACT value in that file?
- Match status: exact_match / rounding_ok / mismatch

### C. Check These Specific Failure Modes

1. **Number inflation**: Paper says 85.3%, raw file says 84.7%
   Rule: only standard rounding to displayed precision is allowed

2. **Best-seed cherry-pick**: Paper says "achieves 90.2%" but
   that's the best of 5 seeds; mean is 87.1%
   Rule: check if paper specifies "average" / "best" / "median"

3. **Config mismatch**: Paper compares Method A vs Baseline B,
   but they used different hyperparameters / datasets / splits
   Rule: verify config files show same settings for compared methods

4. **Aggregation mismatch**: Paper says "average over 5 seeds"
   but result files show only 3 runs
   Rule: count actual runs vs claimed count

5. **Delta error**: Paper says "improves by 15%" but
   actual delta is (85.3 - 73.1) / 73.1 = 16.7%
   Rule: verify arithmetic of all relative improvements

6. **Caption-table mismatch**: Figure caption describes
   something different from what the figure/table actually shows
   Rule: cross-check every caption against its content

7. **Scope overclaim**: Paper says "consistently outperforms"
   but only tested on 2 datasets
   Rule: check if language matches actual evaluation scope

## Output Format (per claim)
For each claim, report:
- claim_id: sequential number
- location: section/table/figure
- paper_text: exact quote from paper
- paper_value: the number claimed
- evidence_file: which raw file
- evidence_value: the actual number
- status: exact_match | rounding_ok | ambiguous_mapping |
          missing_evidence | config_mismatch | aggregation_mismatch |
          number_mismatch | scope_overclaim | unsupported_claim
- details: explanation if not exact_match

Overall verdict: PASS | WARN | FAIL
```

Save the reviewer prompt and raw response as a trace (see "Review Tracing").

### Step 3: Write Report (Executor — Claude)

Parse the reviewer's response and write `PAPER_CLAIM_AUDIT.md`:

```markdown
# Paper Claim Audit Report

**Date**: [today]
**Auditor**: [resolved reviewer model + effort, or "self-review (REVIEW_UNAVAILABLE — not independent)"]
**Paper**: [paper title from tex]

## Overall Verdict: [PASS | WARN | FAIL | REVIEW_UNAVAILABLE]

## Claims Verified: [N total]
- exact_match: [count]
- rounding_ok: [count]
- ambiguous_mapping: [count]
- missing_evidence: [count]
- mismatch: [count]

## Issues Found

### [FAIL/WARN] Claim #N: [description]
- **Location**: Section X / Table Y / Figure Z
- **Paper says**: "..."
- **Evidence shows**: ...
- **Status**: [status]
- **Fix**: [specific correction needed]

## All Claims (detailed)

| # | Location | Paper Value | Evidence Value | Status |
|---|----------|-------------|---------------|--------|
| 1 | Table 2 | 85.3% | 85.28% | rounding_ok |
| 2 | Abstract | "15% improvement" | 12.8% | number_mismatch |
| ... |
```

Also write `PAPER_CLAIM_AUDIT.json` for machine consumption.

### Step 4: Print Summary

```
📋 Paper Claim Audit Complete

  Claims verified: 24
  exact_match:     18
  rounding_ok:      3
  ambiguous:         1
  ⚠️ mismatch:      2

  Overall: ⚠️ WARN

  See PAPER_CLAIM_AUDIT.md for details.
```

## When to Run

1. **After the draft is written** — first check before any improvement round
2. **After any improvement round that changed numbers** — recheck
3. **Before submission** — final verification

## Integration with Other Resources

### Consumed by an improvement loop

```
if PAPER_CLAIM_AUDIT.json exists:
    read mismatched claims
    fix them as priority items in the improvement round
```

### Advisory, Never Blocking

- `PASS` → continue normally
- `WARN` → print warning, continue, flag draft as "check numbers before submission"
- `FAIL` → print alert, continue, but do NOT mark as submission-ready
- `REVIEW_UNAVAILABLE` → continue, but the claims have NOT been independently checked; say so in the final report

## HTML view (optional, non-blocking)

An HTML rendering of the audit is a convenience for human readers and is **out of scope here** — no renderer is bundled. The Markdown and JSON verdict files are the canonical outputs. If the user wants an HTML view, convert `PAPER_CLAIM_AUDIT.md` with whatever local markdown/HTML tool is available; a rendering failure never blocks or alters the audit verdict.

## Key Rules

- **Fresh thread EVERY run.** Never continue a previous reviewer conversation. Never carry context.
- **Zero executor interpretation.** Only file paths. No summaries.
- **Only raw results.** No EXPERIMENT_LOG, no AUTO_REVIEW, no human summaries.
- **Rounding rule.** Only standard rounding to displayed precision. 84.7% → 84.7% or 85% is OK. 84.7% → 85.3% is NOT OK.
- **Cross-model when available; labeled when not.** The reviewer must be a different model family from the executor; if no such backend exists, the verdict is `REVIEW_UNAVAILABLE` and the self-review is labeled as non-independent.

## Review Tracing

After every reviewer call, save a trace under
`<paper-dir>/.minh-agent/traces/paper-claim-audit/<date>_run<NN>/` containing:
the exact reviewer prompt, the raw response, the resolved reviewer model and
reasoning effort, and the list of files the reviewer was given. Never silently
skip the trace — an untraceable audit cannot be re-checked. If a trace cannot be
written, say so in the report instead of pretending it exists.

## Submission Artifact Emission

This resource **always** writes `paper/PAPER_CLAIM_AUDIT.json`, regardless of
caller or detector outcome. A detector-negative run (paper has no numeric
claims) emits verdict `NOT_APPLICABLE`; a paper-with-numeric-claims-but-no-
raw-results run emits `BLOCKED`. Silent skip is forbidden — downstream tooling
and any external verifier rely on this artifact existing at a predictable path.

Artifact schema:

```json
{
  "audit_skill":      "paper-claim-audit",
  "verdict":          "PASS | WARN | FAIL | NOT_APPLICABLE | BLOCKED | ERROR | REVIEW_UNAVAILABLE",
  "review_unavailable": false,
  "reason_code":      "all_numbers_match | rounding_drift | missing_raw_results | reviewer_backend_absent | ...",
  "summary":          "One-line human-readable verdict summary.",
  "audited_input_hashes": {
    "main.tex":                              "sha256:...",
    "sections/5.evidence.tex":               "sha256:...",
    "/abs/path/to/results/run_2026_04_19.json": "sha256:..."
  },
  "trace_path":       ".minh-agent/traces/paper-claim-audit/<date>_run<NN>/",
  "thread_id":        "<reviewer session/thread id, or null for self-review>",
  "reviewer_model":   "<resolved — the model that actually ran>",
  "reviewer_reasoning": "<resolved — the effort that actually ran>",
  "generated_at":     "<UTC ISO-8601>",
  "details": {
    "total_claims":   <int>,
    "mismatches":     [ ... per-claim issue records ... ],
    "result_files":   [ ... raw files consulted ... ]
  }
}
```

### `audited_input_hashes` scope

Hash the **declared input set** passed into this audit invocation — i.e. the
exact `.tex` files and raw result / config files this run read — not a
repo-wide union and not the reviewer's self-reported subset. If a caller
passed only `main.tex` + a single result file, hash those two files and no
others. An external verifier (or the user) rehashes these entries; any mismatch
flags `STALE`.

**Path convention**: keys are **paths relative to the paper directory** (the
argument passed to the verifier) for in-paper files — so `main.tex`, not
`paper/main.tex` — and **absolute paths** for out-of-paper files such as
external `results/` dirs. The verifier resolves relative entries via
`os.path.join(paper_dir, key)`; prefixing with `paper/` produces
`paper/paper/main.tex` and false-fails as STALE.

### Verdict decision table

| Input state                                           | Verdict              | `reason_code` example |
|-------------------------------------------------------|----------------------|-----------------------|
| No numeric claims detected in paper                   | `NOT_APPLICABLE`     | `no_numeric_claims`   |
| Numeric claims detected, no raw result files found    | `BLOCKED`            | `no_raw_evidence`     |
| All claims reconcile to raw data                      | `PASS`               | `all_numbers_match`   |
| Minor rounding drift only, no material mismatch       | `WARN`               | `rounding_drift`      |
| Any material mismatch (wrong number, config mismatch) | `FAIL`               | `claim_mismatch`      |
| Reviewer invocation failed (network / malformed)      | `ERROR`              | `reviewer_error`      |
| No cross-model reviewer backend available             | `REVIEW_UNAVAILABLE` | `reviewer_backend_absent` |

### Thread independence

Every invocation uses a fresh reviewer session. Do not accept prior audit
outputs (proof audits, citation audits, EXPERIMENT_LOG, AUTO_REVIEW summaries)
as input to this audit — the fresh thread is what preserves reviewer
independence.

### Human-readable sibling

`paper/PAPER_CLAIM_AUDIT.md` is written alongside the JSON for readers. The
JSON is authoritative for any automated verifier; the Markdown is for humans.
The verdict does not by itself block finalization — that decision belongs to
the caller (submission-readiness level) — this resource only emits.

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/paper-claim-audit/SKILL.md (MIT). See registry/components.json. -->
