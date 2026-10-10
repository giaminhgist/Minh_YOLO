# Citation Audit

> **Do not wrap this resource in `/loop`, `/schedule`, or any wall-clock scheduler.** It is
> verdict-bearing — it judges bibliographic correctness. Re-running that verdict
> on a timer adds no new signal (it changes only when the *bibliography*
> changes). What you schedule is the *external wait that precedes it* —
> bibliography finalized → then audit **once**.

When this resource is used: before submission, when the LaTeX draft and `.bib` are complete — "check citations", "citation audit", "verify references", "引用核对", "审查引用" — to catch hallucinated authors, wrong years, fabricated venues, version mismatches, and wrong-context citations.

## Context: $ARGUMENTS

Arguments: `[paper-directory-or-bib-file] [--uncited] [— soft-only] [--apply]`.

Verify every `\cite{...}` in a paper against three independent layers:

1. **Existence** — the cited paper actually exists at the claimed arXiv ID / DOI / venue.
2. **Metadata correctness** — author names, year, venue, and title match canonical sources (DBLP, arXiv, ACL Anthology, OpenReview, etc.).
3. **Context appropriateness** — the cited paper actually supports the claim it is being used to support in the manuscript.

This resource is one layer of the plugin's evidence-and-claim integrity stack, complementing result-to-claim (science verdict) and paper-claim-audit (numerical claims). Together they form a bottom-up chain from raw evaluation outputs to manuscript bibliography.

## When to Use This Resource

**Run before submission.** The right gating point is:

- After the draft and bib file exist
- After `paper-claim-audit` has verified numerical claims
- Before the final PDF build for submission

**Do not** run this on a half-written draft — most of the work is in cross-checking each `\cite` against context, which is wasted on placeholder text.

## What This Resource Catches

The dangerous citation problems are **not** wildly fake citations — those are easy to spot. The dangerous ones are:

- **Wrong-context citations**: real paper, but the cited claim is not what that paper actually establishes (e.g., citing Self-Refine to support "self-feedback produces correlated errors" — Self-Refine actually argues the opposite).
- **Author hallucinations**: anonymous-author placeholders that slipped through, missing co-authors, wrong order.
- **Title drift**: arXiv v1 vs v3 with different titles silently merged.
- **Venue confusion**: arXiv preprint cited but the official venue is now CVPR/ICML/NeurIPS — using the wrong record.
- **Year mismatch**: arXiv 2023 preprint with 2024 conference acceptance, year reported inconsistently.
- **Phantom DOIs**: DOI looks real but does not resolve.
- **Self-citation drift**: your own prior work cited with year off by one.

## Constants

- **Reviewer backend** — a *cross-model* reviewer (different family from the executor) with web access, reached through the session's configured backend (e.g. a Codex/OpenAI MCP server), reasoning effort as high as the backend exposes (target `xhigh`).
  - **Backend absent → `REVIEW_UNAVAILABLE`.** A same-model fresh-context reviewer may still perform the three layers using the session's own web tools, but the report and JSON must be labeled non-independent and carry the `REVIEW_UNAVAILABLE` verdict. Never fake independent review.
- **CONTEXT_POLICY = `fresh`** — Each audit run uses a new reviewer thread/session. Never continue a prior reviewer conversation.
- **WEB_SEARCH = required** — The reviewer must perform real web/DBLP/arXiv lookups, not pattern-match from memory.
- **OUTPUT = `CITATION_AUDIT.md`** — Human-readable per-entry verdict report.
- **STATE = `CITATION_AUDIT.json`** — Machine-readable verdict ledger consumable by downstream tools.
- **SOFT_ONLY = `false`** — When true (set via `— soft-only` / `— soft_only` flag), the audit runs all three layers normally but **forbids any `.bib` file mutation**. Findings that would otherwise mutate the bib (FIX / REPLACE / REMOVE) are translated into per-occurrence sentence-rewrite proposals against the citing `*.tex` files. Used when the user has a hard "freeze the bib" constraint.
- **AUTO_APPLY = `false`** — When true, FIX-level (metadata-only) changes may be applied without prompting. REPLACE and REMOVE always require human approval.

## Workflow

### Step 1: Discover bib file and section files

Locate:

- `references.bib` (or `paper.bib` / similar) under the paper directory
- All `*.tex` files containing `\cite{...}` calls (typically `sections/`)

If multiple bib files exist, audit each separately.

### Step 2: Extract all (cite-key, context) pairs

For each `\cite{key1,key2,...}` invocation in the paper:

- Record the cite key
- Record the file + line number
- Record the surrounding sentence (≥ 1 full sentence around the cite, for context check)

Output a flat list of `(key, file, line, surrounding_sentence)` tuples.

Also build the inverse: for each bib entry, the list of all places it is cited.

Define two protocol sets used throughout the rest of the workflow: `cited_keys` is the set of unique cite keys appearing in any `\cite{...}` invocation across the audited `*.tex` files (de-duplicated), and `bib_keys` is the set of keys parsed from the audited bib file(s). `cited_keys` drives Step 3 (audit only cited entries); `bib_keys \ cited_keys` is the uncited residual surfaced by the `--uncited` opt-in.

If the user passed `--uncited`, also compute the set difference `bib_keys \ cited_keys` here and stash it for Steps 5 and the JSON aggregation; see "Uncited Entry Detection (opt-in)" below. The set-diff is a string operation only and does not consume reviewer budget.

Save the extracted contexts to `<paper-dir>/.minh-agent/citation-audit/contexts.txt` so the reviewer can read it directly. Use the paper-dir-relative path `.minh-agent/citation-audit/contexts.txt` when recording the file in `audited_input_hashes`; do not stage under `/tmp` or other transient locations that a verifier cannot rehash later.

### Step 3: Send each entry to a fresh reviewer

For each **cited** bib entry — i.e., each key in `cited_keys` with at least one extracted citation context — invoke the reviewer in a fresh thread/session per entry, or batch with explicit per-entry isolation. Do **not** send entries in `bib_keys \ cited_keys` to the reviewer; those are detect-only and surface only when `--uncited` is explicitly enabled (see "Uncited Entry Detection" below).

```
You are auditing a bibliographic entry. Use web/DBLP/arXiv search.

## Bib entry
@article{key2024example,
  author = {...}, title = {...}, journal = {...}, year = {...}, ...
}

## Where this entry is cited in the paper
[paste extracted contexts]

For this entry, verify:
1. EXISTENCE: does this paper exist at the claimed arXiv ID / DOI / venue?
   Output: YES / NO / UNCERTAIN, with the verifying URL.
2. METADATA: are author names, year, venue, title correct?
   For each, output: correct / wrong: should be ... / typo: ...
3. CONTEXT: for each use, does the cited paper actually support the surrounding claim?
   Output per-use: SUPPORTS / WEAK / WRONG, with one-sentence reasoning.

VERDICT: KEEP / FIX / REPLACE / REMOVE
- KEEP: entry is clean, all uses are appropriate
- FIX: metadata needs correction; uses are appropriate
- REPLACE: cite is wrong-context, find a different paper that actually supports the claim
- REMOVE: entry is hallucinated or unsupportable

Be honest. If you cannot verify online, say UNCERTAIN; do not guess.
```

Save the response to `.minh-agent/traces/citation-audit/<date>_run<NN>/<key>.md` per the review-tracing rule below.

### Step 4: Aggregate verdicts

Build `CITATION_AUDIT.json` following the schema in "Submission Artifact Emission" below (single authoritative schema for this file). Per-entry ledger data goes under `details.per_entry`, not under a top-level `entries` field. The top-level `verdict` is a single overall value (PASS / WARN / FAIL / NOT_APPLICABLE / BLOCKED / ERROR / REVIEW_UNAVAILABLE) derived from per-entry verdicts per the decision table in "Submission Artifact Emission"; the top-level `summary` is a one-line human-readable string.

Concretely, `details` carries the per-entry ledger:

```json
"details": {
  "total_entries": 29,
  "counts": { "KEEP": 11, "FIX": 14, "REPLACE": 3, "REMOVE": 1 },
  "per_entry": [
    {
      "key": "lu2024aiscientist",
      "verdict": "KEEP",
      "axis_failures": [],
      "uses": [
        {"file": "sections/1.intro.tex", "line": 11, "verdict": "SUPPORTS"},
        {"file": "sections/6.related.tex", "line": 8, "verdict": "SUPPORTS"}
      ]
    },
    {
      "key": "madaan2023selfrefine",
      "verdict": "FIX",
      "axis_failures": ["CONTEXT"],
      "uses": [
        {"file": "sections/2.overview.tex", "line": 42, "verdict": "WRONG",
         "note": "Self-Refine demonstrates iterative improvement, not correlated errors"},
        {"file": "sections/6.related.tex", "line": 13, "verdict": "SUPPORTS"}
      ]
    }
  ]
}
```

### Step 5: Generate human-readable report

Write `CITATION_AUDIT.md`:

```markdown
# Citation Audit Report

**Date**: 2026-04-19
**Bib file(s)**: references.bib
**Total entries**: 29

## Summary
| Verdict | Count |
|---------|-------|
| KEEP    | 11   |
| FIX     | 14   |
| REPLACE | 3    |
| REMOVE  | 1    |

## Priority Fixes (CRITICAL — apply before submission)

### REMOVE: anon2025placeholder
- Author listed as "Anonymous" — canonical record exists with real authors and full title
- Title is incomplete
- ACTION: Replace key with the canonical citekey, update authors and title

### REPLACE-CONTEXT: example2023priorwork in sections/2.overview.tex:42
- Cited to support a specific technical claim
- The cited paper actually demonstrates a different (related but distinct) phenomenon
- ACTION: Rewrite the sentence; cite the prior work for what it actually establishes

[... continues for each entry ...]

## All-Clean Entries (no action needed)

[list of KEEP keys]
```

When `--uncited` is set, append the following section after "All-Clean Entries":

```markdown
## Uncited Entries (opt-in)

The following bib entries are present in the audited bib file(s) but are not referenced by any `\cite{...}` in the paper body:

- `author2010example` — suggestion: prune (uncited; no local evidence of intent)
- `someone2015othercite` — suggestion: prune (uncited; no local evidence of intent)
- `third2024todo` — suggestion: check (a `% TODO: cite third2024todo` comment was found in `sections/3.related.tex`)

This section is detect-only; it does not change the top-level verdict.
```

### Step 6: Apply fixes (interactive)

For each FIX/REPLACE/REMOVE verdict, prompt the user:

```
Fix [key]?
  Change: <description of change>
  Files affected: references.bib + sections/X.tex:Y
[Apply / Skip / Defer]
```

If `AUTO_APPLY = true`, apply all FIX-level changes (metadata corrections only). REPLACE and REMOVE always require human approval — they involve content changes.

### Step 7: Recompile and verify

```bash
latexmk -C && latexmk -pdf -interaction=nonstopmode main.tex
```

Confirm:

- No new `Citation undefined` warnings
- No `Reference undefined` warnings
- Page count unchanged or only minimally affected by metadata fixes

If no TeX toolchain is available, run the static checks instead (`grep` for undefined cite keys against the bib; confirm every edited key still appears in the body) and report that the compile step was skipped.

## Uncited Entry Detection (opt-in)

**Default**: disabled. Existing users see no behavior change — only `\cite{...}` keys are audited, and bib entries with no `\cite` reference in the manuscript are silently ignored.

**Opt-in**: pass `--uncited` on invocation. The audit then performs a set-diff after Step 2 and reports bib entries that appear in any audited bib file(s) but are not cited anywhere in the paper. Detect-only — uncited entries are **not** sent to the reviewer, so there is no extra reviewer/web-lookup cost.

### Why opt-in

This resource's headline output is the three-axis audit on cited entries. Surfacing uncited bib entries by default would (a) change long-form output for every existing run, and (b) noise up the verdict for users who intentionally maintain a superset bib file (e.g., shared lab bib, in-progress section reorder where the cite has been removed but the entry intentionally retained). The flag preserves zero behavior change for existing callers.

### Effect when enabled

When `--uncited` is set:

- `CITATION_AUDIT.md` gains a `## Uncited Entries (opt-in)` section listing the keys with a one-line suggestion each: `prune` (entry is dead weight; recommend deleting) or `check` (entry might be intentional; flag for user review). Default suggestion is `prune`; only emit `check` when there is concrete local evidence (e.g., a TODO comment in a `.tex` file mentioning the key, or a recently removed `\cite` visible in `git diff`). Do not infer intent from the bib key string alone.
- `CITATION_AUDIT.json` `details` gains an `uncited_entries` array; see "Submission Artifact Emission" below for the schema.
- The top-level `verdict` is **unchanged**: uncited entries do not upgrade or downgrade the PASS / WARN / FAIL classification. The `reason_code` and `summary` are likewise unchanged in shape; only the `details.uncited_entries` field appears.
- Verifier gates and downstream consumers MUST NOT treat the presence of `uncited_entries` as a blocking signal.

### When opt-in is appropriate

- Pre-submission cleanup (drop dead bib entries before sharing a camera-ready ZIP).
- Shared lab bib file where the paper uses a subset and the user wants to confirm what is in scope.
- Recurring audits where the user has previously seen the uncited count and wants to track whether it changed.

### Fallback when bib enumeration fails

If `--uncited` is enabled but full bib-key enumeration fails (e.g., malformed bib syntax that the parser cannot recover), the cited-entry audit must still proceed if at all possible. In that case:

- Do **not** alter the top-level `verdict`, `reason_code`, or `summary`.
- Emit `details.uncited_entries` as an empty array `[]`.
- Add `details.uncited_entries_status: "unavailable"` plus a one-line note explaining why (e.g., `"bib parser could not enumerate keys; cited-entry audit completed normally"`).
- Verifier gates and downstream consumers MUST treat `unavailable` the same as the field being absent: not blocking.

If the bib file cannot be read well enough to audit even the cited entries, fall back to the existing `BLOCKED` / `bib_unreadable` path defined in the verdict decision table; this is the same behavior as the no-flag default.

## Key Rules

- **Fresh reviewer thread per audit run** — never reuse prior review context
- **Web access required** — the reviewer must do real lookups, not memory pattern-match
- **Wrong-context > metadata** — a real paper used to support a wrong claim is more dangerous than a typo in an author name
- **REPLACE/REMOVE require human approval** — never auto-modify content claims
- **Always emit, never block** — this resource always writes `CITATION_AUDIT.json` with a verdict; the decision to block finalization belongs to the caller. A `REVIEW_UNAVAILABLE` verdict means the check was not independent — it is not a pass.
- **Run once per submission** — the audit is wall-clock expensive (web lookups for each entry); not for every save
- **Uncited detection is opt-in only** — never auto-enable; never block on uncited entries; callers that do not pass `--uncited` must observe identical output
- **Under `--soft-only`, this resource emits text-rewrite proposals only; bib files are never mutated regardless of finding severity.** The audit semantics (existence + metadata + context) and the per-entry KEEP/FIX/REPLACE/REMOVE ledger are preserved verbatim; only the action layer is translated to per-occurrence sentence rewrites in the citing `*.tex` files. Refuse any downstream-proposed bib edit while `--soft-only` is set.

## Comparison with Other Integrity Resources

| Resource | What it audits | What it catches |
|-------|---------------|-----------------|
| experiment integrity | Evaluation code | Fake ground truth, self-normalized scores, phantom results |
| `result-to-claim` | Result-to-claim mapping | Claims unsupported by evidence |
| `paper-claim-audit` | Numerical claims in manuscript | Number inflation, best-seed cherry-pick, config mismatch |
| `citation-audit` | Bibliographic entries | Hallucinated refs, wrong-context citations, metadata errors |

Together: code → result → numerical claim → cited claim. Each layer uses review with no executor in the validator path.

## Known Limitations

- **DBLP coverage gap**: very recent papers (< 2 weeks) may not yet be in DBLP. The reviewer should fall back to arXiv.
- **Pre-print vs published**: when both exist, the reviewer should prefer the published venue (ICML 2024 over arXiv 2401.xxxxx) but flag both.
- **Anthology vs OpenReview**: NeurIPS/ICLR papers have OpenReview entries before official proceedings; both are valid sources.
- **Multi-author truncation**: bib entries with 6+ authors using `and others` are conventional and not flagged unless the truncation hides a co-author the user explicitly cares about.

## Review Tracing

After each reviewer call, save the trace under
`.minh-agent/traces/citation-audit/<date>_run<NN>/` — one file per audited key
plus a run index carrying the exact prompts, the raw responses, the resolved
reviewer model and effort, and the file set the reviewer received. Policy:
forensic — never silently skip. If a trace cannot be written, say so in the
report rather than implying the evidence exists. `.minh-agent/` is project-local
working state and should be git-ignored.

## Output Contract

- `CITATION_AUDIT.md` (human-readable report) at paper root
- `CITATION_AUDIT.json` (machine-readable ledger; schema below) at paper root
- `.minh-agent/traces/citation-audit/<date>_runNN/` (per-entry review traces)
- Optional: applied fixes to `references.bib` + `sections/*.tex` (with the `--apply` path of Step 6)
- Optional: `details.uncited_entries` field in JSON + `## Uncited Entries (opt-in)` MD section (with `--uncited` flag; field absent and section omitted when the flag is unset)
- Optional: an HTML view of the report — **out of scope here**, no renderer is bundled and a render failure never affects the verdict; the JSON + MD ledger are the canonical outputs

## Optional: Soft-Only Mode (— soft-only)

**Default**: disabled. The audit emits the standard `KEEP / FIX / REPLACE / REMOVE` per-entry verdicts and a downstream caller (or the `--apply` path of Step 6) is free to mutate the bib.

**Opt-in**: pass `— soft-only` (also accepts `— soft_only`) on invocation. This mode is designed for callers operating under a **hard "freeze the bib" constraint**: if a citation is wrong-context, soften the surrounding sentence; do **not** change, add, or remove the cite itself.

### What soft-only changes

The audit semantics are **unchanged**: existence + metadata + context-appropriateness checks all run, the reviewer is still invoked once per cited entry, and the per-entry KEEP/FIX/REPLACE/REMOVE verdicts are still computed and emitted exactly as in default mode. Only the **action layer** changes — soft-only translates each base verdict into a text-rewrite proposal instead of a bib mutation.

### Verdict translation table

| Base verdict | Soft-only translation | Notes |
|---|---|---|
| `KEEP` | `keep_unchanged` | No action. Cite + sentence are both fine. |
| `FIX` (metadata wrong) | `keep_metadata_drift_acknowledged` | Bib stays as-is. Flag for human review at submission time. Append note: "metadata drift detected but not fixed under --soft-only". |
| `REPLACE` (wrong-context cite) | `soften_citing_sentence` | Per-occurrence sentence-rewrite proposal. For each `\cite{X}` in the body, locate the surrounding sentence and propose a softened version that does not claim what `X` actually establishes. |
| `REMOVE` (cite refers to nonexistent paper — i.e., hallucinated citation) | `drop_cite_in_body_only` | The bib entry is left untouched (per the `--soft-only` invariant), but **the inline `\cite{X}` references in the body MUST be removed and the surrounding sentence rewritten** so it no longer relies on a nonexistent paper. Two sub-strategies the rewriter may use: (a) drop the inline `\cite{X}` entirely and rephrase the sentence to remove the load-bearing claim, OR (b) re-attribute to a different in-bib source that genuinely supports the claim. **Never** leave a `\cite{X}` to a hallucinated paper in the body — that is a worse failure mode than removing the cite, because reviewers will check the reference and find nothing. The bib entry itself stays (it is harmless once not cited; uncited-detection at submission time will surface it for cleanup outside this audit). |

### Augmented JSON schema (under `--soft-only`)

When the flag is set, the standard top-level fields (`audit_skill`, `verdict`, `reason_code`, `summary`, etc.) and the existing `details.per_entry` ledger are emitted exactly as in default mode. In addition:

- A top-level `soft_only_mode: true` boolean is added.
- `details` gains a `soft_only_actions` array — one entry per audited bib key, in the same order as `details.per_entry`.

```json
{
  "audit_skill": "citation-audit",
  "verdict": "...",
  "soft_only_mode": true,
  "details": {
    "soft_only_actions": [
      {
        "citekey": "smith2023example",
        "base_verdict": "REPLACE",
        "soft_action": "soften_citing_sentence",
        "occurrences": [
          {
            "file": "sections/3.method.tex",
            "line": 142,
            "current_sentence": "Smith et al. [2023] proves a generic result that...",
            "proposed_rewrite": "Smith et al. [2023] discusses a related setting; while not directly applicable, the framing motivates...",
            "rationale": "Original sentence claims smith2023 'proves' a result, but smith2023 actually only conjectures it. Softened to 'discusses ... motivates' to remove the unsupported claim."
          }
        ]
      }
    ]
  }
}
```

`soft_action` is one of `keep_unchanged | keep_metadata_drift_acknowledged | soften_citing_sentence | drop_cite_in_body_only`. For `keep_unchanged` and `keep_metadata_drift_acknowledged`, `occurrences` MAY be omitted or emitted as `[]`. For `soften_citing_sentence` and `drop_cite_in_body_only`, `occurrences` MUST list one object per `\cite{X}` site in the body that triggered the verdict.

For `drop_cite_in_body_only`, the `proposed_rewrite` field shows the sentence with the inline `\cite{X}` removed (or replaced by a `\cite{Y}` to an alternate in-bib source). The `bib_entry_action` field is fixed to `"leave_as_is_per_soft_only"` — the bib record itself is never modified by the audit.

### Augmented human-readable report

`CITATION_AUDIT.md` gains a new section `## Soft-Only Rewrites (— soft-only mode)` listing each occurrence with the proposed sentence rewrite for human approval. Example:

```markdown
## Soft-Only Rewrites (— soft-only mode)

The bib file is frozen. The following sentence rewrites are proposed in lieu of bib edits.

### `smith2023example` — base verdict REPLACE → `soften_citing_sentence`

- **File**: `sections/3.method.tex:142`
- **Current**: "Smith et al. [2023] proves a generic result that..."
- **Proposed**: "Smith et al. [2023] discusses a related setting; while not directly applicable, the framing motivates..."
- **Rationale**: Original sentence claims smith2023 "proves" a result, but smith2023 actually only conjectures it. Softened to "discusses ... motivates" to remove the unsupported claim.
```

The existing per-entry verdict table in the Summary block is **kept** but FIX/REPLACE/REMOVE rows are annotated with a `🔒 bib frozen by --soft-only` badge so downstream readers see immediately why the bib was not mutated.

### Hard guarantees under `--soft-only`

- **No `.bib` file mutations under any circumstance.** Step 6 ("Apply fixes (interactive)") is bypassed for the bib file; only `*.tex` rewrite proposals are produced (and still require human approval before any text edit).
- If a downstream caller — or any wrapper — proposes a bib edit while `--soft-only` is set, **refuse it**: emit a one-line refusal in the trace and continue to the next finding.
- The top-level `verdict` decision table is **unchanged**: a wrong-context cite still produces `FAIL` with `reason_code: wrong_context`. Soft-only does not silence the finding; it only constrains the action layer.
- `--soft-only` composes with `--uncited`: both flags can be set together. Uncited entries remain detect-only and are not subject to soft-only translation (there is no citing sentence to soften).

## Submission Artifact Emission

This resource **always** writes `paper/CITATION_AUDIT.json`, regardless of
caller or detector outcome. A paper with no `.bib` file or no `\cite{...}`
usage emits verdict `NOT_APPLICABLE`; silent skip is forbidden. Downstream
gates rely on this artifact existing at a predictable path.

```json
{
  "audit_skill":      "citation-audit",
  "verdict":          "PASS | WARN | FAIL | NOT_APPLICABLE | BLOCKED | ERROR | REVIEW_UNAVAILABLE",
  "review_unavailable": false,
  "reason_code":      "all_entries_keep | metadata_drift | wrong_context | hallucinated | reviewer_backend_absent | ...",
  "summary":          "One-line human-readable verdict summary.",
  "audited_input_hashes": {
    "references.bib":             "sha256:...",
    "main.tex":                   "sha256:...",
    "sections/3.related.tex":     "sha256:..."
  },
  "trace_path":       ".minh-agent/traces/citation-audit/<date>_run<NN>/",
  "thread_id":        "<reviewer session/thread id, or null for self-review>",
  "reviewer_model":   "<resolved — the model that actually ran>",
  "reviewer_reasoning": "<resolved — the effort that actually ran>",
  "generated_at":     "<UTC ISO-8601>",
  "details": {
    "total_entries":  <int>,                 // count of audited cited entries (= |cited_keys|), NOT the bib-file size
    "per_entry":      [ { "key": "madaan2023selfrefine",
                          "verdict": "KEEP | FIX | REPLACE | REMOVE",
                          "axis_failures": [ "CONTEXT" | "METADATA" | "EXISTENCE" ],
                          "note": "..." }, ... ]
  }
}
```

### Optional: `details.uncited_entries` (only when `--uncited` is set)

```json
"details": {
  ...
  "uncited_entries": [
    {"key": "<bibkey>", "suggestion": "prune" | "check", "note": "..."}
  ],
  "uncited_entries_status": "ok" | "unavailable"
}
```

Field semantics:

- Both fields are **omitted entirely** when the flag is not set. The default schema does not include either key.
- When the flag is set and the set-diff completes normally, `uncited_entries_status` is `"ok"` and `uncited_entries` lists the detected keys (possibly empty if every bib entry is cited).
- When the flag is set but bib-key enumeration fails (per "Fallback when bib enumeration fails" above), `uncited_entries_status` is `"unavailable"` and `uncited_entries` is `[]`. Downstream consumers MUST treat `"unavailable"` identically to the field being absent: not blocking.
- Downstream consumers MUST treat absence of either field as the only valid default state and MUST NOT raise on missing.
- `suggestion` is advisory only; no gate blocks on it.

### `audited_input_hashes` scope

Hash the **declared input set** actually passed to this audit: the `.bib`
file, `main.tex`, and every `sections/*.tex` file that supplied citation
contexts. Do NOT hash extracted contexts from `/tmp` or other transient
paths — if you need to stage extracted contexts, materialize them under
`paper/.minh-agent/` so a verifier can rehash reproducibly. Do NOT hash
repo-wide unions or the reviewer's self-reported opened subset.

**Path convention**: keys are **paths relative to the paper directory** (no
`paper/` prefix — the verifier already resolves relative to the paper dir;
prefixing produces `paper/paper/...` and false-fails as STALE). Use **absolute
paths** for any file outside the paper dir.

### Verdict decision table

| Input state                                                    | Verdict              | `reason_code` example |
|----------------------------------------------------------------|----------------------|-----------------------|
| No `.bib` file or no `\cite{...}` usage                        | `NOT_APPLICABLE`     | `no_citations`        |
| `.bib` file referenced but unreadable / missing                | `BLOCKED`            | `bib_unreadable`      |
| Every entry KEEP, all three axes green                         | `PASS`               | `all_entries_keep`    |
| Only FIX verdicts (metadata drift, no context errors)          | `WARN`               | `metadata_drift`      |
| Any REPLACE or REMOVE (wrong-context or hallucinated entry)    | `FAIL`               | `wrong_context`       |
| Web lookups timed out / reviewer invocation failed             | `ERROR`              | `reviewer_error`      |
| No cross-model reviewer backend available                      | `REVIEW_UNAVAILABLE` | `reviewer_backend_absent` |

The `--uncited` flag does **not** appear in this table: uncited entries are advisory only and never alter the top-level verdict or reason_code. They surface exclusively through `details.uncited_entries` and the optional MD section.

### Thread independence

Every invocation uses a fresh reviewer thread/session. Never continue a prior
reviewer conversation. Do not accept prior audit outputs (proof audits,
PAPER_CLAIM_AUDIT, EXPERIMENT_LOG) as input — the fresh thread is what preserves
reviewer independence.

This resource never blocks by itself; the caller decides whether the verdict
blocks finalization.

## See Also

- `paper-claim-audit` — sibling resource for numerical claim verification
- `result-to-claim` — claim verdict assignment from results
- `references/citation-discipline.md` — full citation-hygiene protocol
- Out of scope here: HTML report rendering, Overleaf sync, automated improvement loops

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/citation-audit/SKILL.md (MIT). See registry/components.json. -->
