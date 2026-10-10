# Paper Plan: From Review Conclusions to Paper Outline

When this resource is used: when a research narrative and experiment results already exist and the user wants a paper plan before drafting — "paper outline", "plan the paper", "论文规划", "写大纲" — or when a later `paper-write` pass needs a frozen, section-by-section outline to draft against.

## Context: $ARGUMENTS

Arguments: `[topic-or-narrative-doc] [— style-ref: <source>]`, optionally `— venue: <VENUE>` and a page-budget override.

## Constants

- **REVIEWER_MODEL** — a model from a *different family* than the executor, reached through whatever cross-model reviewer backend the session has configured (e.g. a Codex/OpenAI MCP server). Target reasoning effort: high (`xhigh` when the backend exposes it).
  - **Backend absent → `REVIEW_UNAVAILABLE`.** Run the review as a labeled self-review inside a fresh context, and write in `PAPER_PLAN.md` that the review was NOT independent (same model family). Never present a self-review as cross-model review. Never invent a reviewer score.
- **TARGET_VENUE = `ICLR`** — Default venue. User can override (e.g. `— venue: NeurIPS`). Supported: `ICLR`, `NeurIPS`, `ICML`, `CVPR`, `ACL`, `AAAI`, `ACM`, `IEEE_JOURNAL` (IEEE Transactions / Letters), `IEEE_CONF` (IEEE conferences).
- **MAX_PAGES** — Page limit. For ML conferences: main body to Conclusion end (excluding references, appendix). ICLR=9, NeurIPS=9, ICML=8, AAAI=7 technical-content pages plus references unless the current AAAI CFP says otherwise. **For IEEE venues: references ARE included in page count.** IEEE journal Transactions ≈ 12-14 pages total, Letters ≈ 4-5 pages total; IEEE conference ≈ 5-8 pages total (including references).
- **Venue templates are not bundled with this resource** and the current CFP overrides any number above; verify page limits and required sections against the live venue call-for-papers before freezing the outline.

## Inputs

The resource expects one or more of these in the project directory:

1. **NARRATIVE_REPORT.md** or **STORY.md** — research narrative with claims and evidence
2. **review-stage/AUTO_REVIEW.md** — review-loop conclusions *(fall back to `./AUTO_REVIEW.md` if not found)*
3. **Experiment results** — JSON files in `figures/`, screen logs, tables
4. **idea-stage/IDEA_REPORT.md** — if a prior idea-discovery run produced one *(fall back to `./IDEA_REPORT.md`)*
5. **Compact files** (if available): `idea-stage/IDEA_CANDIDATES.md`, `findings.md`, `EXPERIMENT_LOG.md` — preferred over full files when present, saves context window

If none exist, ask the user to describe the paper's contribution in 3-5 sentences.

## Writing-Reference Overlay

The bundled references improve story and outline quality; they are support material, not extra workflow phases.

- Read `references/writing-principles.md` when framing the one-sentence contribution, Abstract, Introduction, Related Work, or hero figure.
- Read `references/venue-checklists.md` before freezing the outline for a specific venue.
- Load these only when needed; do not paste their full contents into the working draft.

## Optional: Style reference (`— style-ref: <source>`, opt-in)

Lets the user steer the **structural** layout of the outline (section ordering, subsection density, theorem-environment density, figure budget, citation style) toward a reference paper. **Default OFF — when the user does not pass `— style-ref`, do nothing differently.**

Only when `— style-ref: <source>` appears in the arguments, build the style profile FIRST, before drafting the outline:

1. **Resolve the source.** Accepted: local TeX directory, local `.tex` file, local PDF, arXiv id (`2501.12345` or `arxiv:2501.12345`), or an http(s) URL.
   - Overleaf URLs and project IDs are **rejected** (no Overleaf sync is bundled here). Tell the user to download/clone the project locally and pass that path.
   - PDF text extraction needs a local extractor (`pdftotext` or equivalent). If no extractor is available, **warn** (`style-ref skipped — missing optional dependency`) and continue without style guidance; this is a warning, not an error.
   - If the named local path does not exist, or an arXiv/URL fetch fails, **abort the outline** with a clear error. Do NOT silently fall back to un-styled planning: the user explicitly asked for a reference.
2. **Extract aggregate structure only** — a compact markdown profile (≤ ~200 lines): ordered section list, per-section approximate length distribution, figure/table counts, theorem-environment density, caption-length and sentence-length statistics, citation-style hints. For remote sources use the session's web-fetch tool; do not download or run helper scripts from the source.
3. **Write a deterministic cache** at `style-ref/<source-slug>/` containing `style_profile.md` plus `source_manifest.json` (original source input, resolved type, resolved path/URL, fetch time, sha256 of the extracted text, profile version). Same source → same directory. The cache is an input to planning only; never mutate it mid-run.

**Strict rules:**

- Use `style_profile.md` as **structural** guidance only when proposing the outline's section list, subsection counts, theorem density, figure budget.
- **Never copy prose, claims, examples, section names verbatim, or terminology** from anything reachable through the cache. The user's narrative is the only source of substance.
- **Never pass `— style-ref` (or the cache contents) to reviewer / auditor sub-agents.** Reviewer independence requires that reviewers see only the artifact and the user's prompt — not the author's stylistic context.

### Gap Report (`GAP_REPORT.md`, auto-emitted when style-ref is on)

When `— style-ref:` succeeded AND any of `figures/`, `results/`, `data/`, `tables/`, `sec/`, `NARRATIVE_REPORT.md`, `CLAIMS_FROM_RESULTS.md` exists in the project, **also** emit a gap report before drafting the outline. It maps the exemplar's section topology + density requirements (from `style_profile.md`) against the user's actual assets, surfacing structural slots where the user has **no evidence to fill**. It is the contract by which `paper-write` decides when to emit `<!-- DATA_NEEDED -->` markers instead of fabricating content.

Procedure:

1. Read `style_profile.md` for the exemplar's section list + per-section feature counts (figures, theorems, tables, citations, sentences per section).
2. Inventory user assets: `figures/*` filenames, `results/*` evidence files, `sec/*.tex` existing prose, `NARRATIVE_REPORT.md`, `CLAIMS_FROM_RESULTS.md`, `references.bib` for citation density.
3. For each section slot the exemplar implies (ablation table, scaling experiment, failure-case analysis, proof block, …), classify as `covered` / `partial` / `missing`.
4. Emit `<output-dir>/GAP_REPORT.md`:

```markdown
# GAP_REPORT — exemplar vs user assets

- **Exemplar source:** <source identifier (file path, arXiv ID, URL)>
- **Generated:** <UTC ISO-8601>
- **Style profile:** <relative path to style_profile.md>

## Section topology gaps

| Exemplar slot | Exemplar feature | User evidence | Status | Slot ID |
|---|---|---|---|---|
| §5 Experiments | ablation table (3 axes × 4 levels) | `results/` has no ablation file | missing | `GAP_S5_ABLATION` |
| §5.3 Scaling | log-N scaling curve | `figures/scaling.pdf` not found | missing | `GAP_S5_SCALING` |
| §6 Discussion | failure-case analysis | not present in `NARRATIVE_REPORT.md` | missing | `GAP_S6_FAILURE` |
| §2 Related | citation density ≥ 60 | `references.bib` has 35 entries | partial | `GAP_S2_CITES` |

## Coverage summary

- covered: N
- partial: M
- missing: K

## Used by

- `paper-write` reads this file and emits `<!-- DATA_NEEDED: <Slot ID> — <one-line description> -->` placeholders for `missing` slots instead of fabricating content.
- `paper-claim-audit` can use Slot IDs to flag claims that cite sections with `missing` evidence.
```

Slot ID format: `GAP_<SECTION>_<FEATURE>`, all-caps, stable across regenerations unless user assets change.

**Rules** (hard):

- **Do not** infer, fill, or hallucinate evidence to "close" gaps. Missing is missing.
- **Do not** propose specific experiment commands to fill gaps — surfacing deficits is this resource's job; experiment planning belongs to the experiment-planning resource.
- **Do not** include exemplar prose / claim text / author names / quantitative figures from the exemplar.
- If `style_profile.md` extraction failed or the user has no project assets, skip the Gap Report (no error; just do not emit the file).
- The gap report is **also subject to reviewer isolation** — never passed to reviewer / auditor sub-agents (same rule as `style_profile.md`).

## Workflow

### Step 1: Extract Claims and Evidence

**First check for `CLAIMS_FROM_RESULTS.md`** (produced by the plugin's result-to-claim resource). If its first line is `verdict: REVIEW_UNAVAILABLE`, treat the file as ABSENT for claim extraction (fall through to the narrative documents below) and then: if the user asked for submission-grade work, **STOP** — the claims were never adjudicated; rerun result-to-claim first. Otherwise continue but tag every claim `[unadjudicated]` in the claims matrix. If it exists and carries a real verdict, use it as the starting point: it contains validated claims already mapped to experiment evidence. Merge with any additional claims from the narrative documents below.

If `CLAIMS_FROM_RESULTS.md` does not exist, extract claims from scratch:

Read all available narrative documents and extract:

1. **Core claims** (3-5 main contributions)
2. **One-sentence contribution** (the single sentence that best states what the paper contributes)
3. **Evidence** for each claim (which experiments, which metrics, which figures)
4. **Known weaknesses** (from reviewer feedback)
5. **Suggested framing** (from review conclusions)

Build a **Claims-Evidence Matrix**:

```markdown
| Claim | Evidence | Status | Section |
|-------|----------|--------|---------|
| [claim 1] | [exp A, metric B] | Supported | §3.2 |
| [claim 2] | [exp C] | Partially supported | §4.1 |
```

### Step 2: Determine Paper Type and Structure

Based on TARGET_VENUE and paper content, classify and select structure.

Before committing to a structure, apply the narrative principle from `references/writing-principles.md`:

- The paper should tell one coherent technical story.
- By the end of the Introduction, the outline should make the **What**, **Why**, and **So What** explicit.
- Front-load the most important material: title, abstract, introduction, and hero figure. Reviewers often form a judgment before reading the full method.

**IMPORTANT**: The section count is FLEXIBLE (5-8 sections). Choose what fits the content best. The templates below are starting points, not rigid constraints.

**Empirical/Diagnostic paper:**
```
1. Introduction (1.5 pages)
2. Related Work (1 page)
3. Method / Setup (1.5 pages)
4. Experiments (3 pages)
5. Analysis / Discussion (1 page)
6. Conclusion (0.5 pages)
```

**Theory + Experiments paper:**
```
1. Introduction (1.5 pages)
2. Related Work (1 page)
3. Preliminaries & Modeling (1.5 pages)
4. Experiments (1.5 pages)
5. Theory Part A (1.5 pages)
6. Theory Part B (1.5 pages)
7. Conclusion (0.5 pages)
— Total: 9 pages
```
Theory papers often need 7 sections (splitting theory into estimation + optimization, or setup + analysis). The total page budget MUST sum to MAX_PAGES.

Theory papers should:
- Include **proof sketch** locations (not just theorem statements)
- Plan a **comparison table** of prior theoretical bounds vs. this paper's bounds
- Identify which proofs go in appendix vs. main body

**Method paper:**
```
1. Introduction (1.5 pages)
2. Related Work (1 page)
3. Method (2 pages)
4. Experiments (2.5 pages)
5. Ablation / Analysis (1 page)
6. Conclusion (0.5 pages)
```

### Step 3: Section-by-Section Planning

For each section, specify:

```markdown
### §0 Abstract
- **What we achieve**: [the paper's specific contribution, not field-level background]
- **Why it matters / is hard**: [why this problem is important and non-trivial]
- **How we do it**: [approach in one sentence]
- **Evidence**: [what supports the claim]
- **Most remarkable result**: [strongest quantitative or theoretical result]
- **Estimated length**: 150-250 words
- **Self-contained check**: can a reader understand this without the paper?

### §1 Introduction
- **Opening hook**: [1-2 sentences that motivate the problem]
- **Gap / challenge**: [what's missing in prior work, and why prior work is insufficient]
- **One-sentence contribution**: [the main takeaway of the paper]
- **Approach overview**: [what we do differently]
- **Key questions**: [the research questions this paper answers]
- **Contributions**: [2-4 numbered bullets, specific and falsifiable, matching Claims-Evidence Matrix]
- **Results preview**: [the strongest result or comparison to surface early]
- **Hero figure**: [describe what Figure 1 should show — MUST include clear comparison if applicable]
- **Estimated length**: 1.5 pages
- **Key citations**: [3-5 papers to cite here]
- **Front-loading check**: [would a skim reader know the main claim before reaching the method?]

### §2 Related Work
- **Subtopics**: [2-4 categories of related work]
- **Positioning**: [how this paper differs from each category]
- **Minimum length**: 1 full page (at least 3-4 paragraphs with substantive synthesis)
- **Organization rule**: organize by methodological family / assumption / question, not paper-by-paper
- **Must NOT be just a list** — synthesize, compare, and position

### §3 Method / Setup / Preliminaries
- **Notation**: [key symbols and their meanings]
- **Problem formulation**: [formal setup]
- **Method description**: [algorithm, model, or experimental design]
- **Formal statements**: [theorems, propositions if applicable]
- **Proof sketch locations**: [which key steps appear here vs. appendix]
- **Estimated length**: 1.5-2 pages

### §4 Experiments / Main Results
- **Figures planned**:
  - Fig 1: [description, type: bar/line/table/architecture, WHAT COMPARISON it shows]
  - Fig 2: [description]
  - Table 1: [what it shows, which methods/baselines compared]
- **Data source**: [which JSON files / experiment results]

### §5 Conclusion
- **Restatement**: [contributions rephrased, not copy-pasted from intro]
- **Limitations**: [honest assessment — reviewers value this]
- **Future work**: [1-2 concrete directions]
- **Estimated length**: 0.5 pages
```

### Step 4: Figure Plan

List every figure and table:

```markdown
## Figure Plan

| ID | Type | Description | Data Source | Priority |
|----|------|-------------|-------------|----------|
| Fig 1 | Hero/Architecture | System overview + comparison | manual | HIGH |
| Fig 2 | Line plot | Training curves comparison | figures/exp_A.json | HIGH |
| Fig 3 | Bar chart | Ablation results | figures/ablation.json | MEDIUM |
| Table 1 | Comparison table | Main results vs. baselines | figures/main_results.json | HIGH |
| Table 2 | Theory comparison | Prior bounds vs. ours | manual | HIGH (theory papers) |
```

**CRITICAL for Figure 1 / Hero Figure**: Describe in detail what the figure should contain, including:
- Which methods are being compared
- What the visual difference should demonstrate
- Caption draft that clearly states the comparison
- Why the figure helps a skim reader understand the paper before reading the full method

### Step 5: Citation Scaffolding

For each section, list required citations:

```markdown
## Citation Plan
- §1 Intro: [paper1], [paper2], [paper3] (problem motivation)
- §2 Related: [paper4]-[paper10] (categorized by subtopic)
- §3 Method: [paper11] (baseline), [paper12] (technique we build on)
```

**Citation rules** (verified-metadata discipline; full protocol in `${CLAUDE_PLUGIN_ROOT}/resources/writing/citation-audit/references/citation-discipline.md` when this scaffolding is not enough):
1. NEVER generate BibTeX from memory — verify via DBLP first, then CrossRef, or an existing project `.bib`
2. Every citation must be verified: correct authors, year, venue
3. Flag any citation you're unsure about with `[VERIFY]` — never invent a plausible-looking entry
4. Prefer published versions over arXiv preprints when available
5. A planned citation whose claim has not been checked against the actual paper is a *plan*, not evidence — it must not be written as if the paper already supports the statement

### Step 6: Cross-Review with the Reviewer Backend

Send the complete outline to the cross-model reviewer at high reasoning effort (see Constants; score targets are the same either way):

```
Review this paper outline for a [VENUE] submission.
[full outline including Claims-Evidence Matrix]

Score 1-10 on:
1. Logical flow — does the story build naturally?
2. Claim-evidence alignment — every claim backed?
3. Missing experiments or analysis
4. Positioning relative to prior work
5. Page budget feasibility (MAX_PAGES = main body to Conclusion end, excluding refs/appendix)
6. Front-matter strength — are the abstract, introduction, and hero figure plan strong enough for skim-reading reviewers?

For each weakness, suggest the MINIMUM fix.
Be specific and actionable — "add X" not "consider more experiments".
```

Apply feedback before finalizing. If the backend is unavailable, run the same prompt as a labeled self-review and record `REVIEW_UNAVAILABLE` in the output next to the feedback block.

### Step 7: Output

Save the final outline to `PAPER_PLAN.md` in the project root:

```markdown
# Paper Plan

**Title**: [working title]
**One-sentence contribution**: [single-sentence statement of the paper's core takeaway]
**Venue**: [target venue]
**Type**: [empirical/theory/method]
**Date**: [today]
**Page budget**: [MAX_PAGES] pages (main body to Conclusion end, excluding references & appendix)
**Section count**: [N] (must match the number of section files that will be created)

## Claims-Evidence Matrix
[from Step 1]

## Structure
[from Step 2-3, section by section]

## Figure Plan
[from Step 4, with detailed hero figure description]

## Citation Plan
[from Step 5]

## Reviewer Feedback
[from Step 6, summarized; labeled self-review if the backend was unavailable]

## Next Steps
- [ ] generate all figures (paper-figure resource)
- [ ] draft LaTeX sections (paper-write resource)
- [ ] build the PDF (latexmk)
```

## Output Protocols

For every output file produced here:

- **Versioning** — write the timestamped file first (`{NAME}_{YYYYMMDD_HHmmss}.md`, seconds precision, `_2`/`_3` on sub-second collisions), then copy the same content to the fixed name (`PAPER_PLAN.md`). Downstream readers always read the fixed name. Never delete timestamped files; they are the permanent history.
- **Manifest** — maintain `MANIFEST.md` in the project root only when a run produces more than 15 artifacts; below that threshold a manifest is duplicate bookkeeping. Append one row per output (timestamp | skill | file | stage | description).
- **Language** — follow the project's language setting (check `CLAUDE.md`, then the user's most recent message; default English). Do not localize code, paths, BibTeX entries, venue names, JSON keys, or machine-parsed markers. LaTeX for venue submission is always English.

## Key Rules

- **Do NOT generate author information** — leave the author block as placeholder or anonymous
- **Be honest about evidence gaps** — mark claims as "needs experiment" rather than overclaiming
- **Page budget is hard** — if content exceeds MAX_PAGES, suggest what to move to appendix
- **MAX_PAGES counting differs by venue** — ML conferences: main body to Conclusion end, references/appendix NOT counted; AAAI main track is typically 7 technical-content pages plus references. **IEEE venues: references ARE counted toward the page limit.**
- **Venue-specific norms** — ML conferences (ICLR/NeurIPS/ICML) use `natbib` (`\citep`/`\citet`); **IEEE venues use `cite` package (`\cite{}`, numeric style)**
- **Claims-Evidence Matrix is the backbone** — every claim must map to evidence, every experiment must support a claim
- **Front-load the story** — the outline should make the contribution clear in the title, abstract, introduction, and hero figure before the reader reaches the full method
- **Figures need detailed descriptions** — especially the hero figure, which must clearly specify comparisons and visual expectations
- **Section count is flexible** — 5-8 sections depending on paper type. Don't force content into a rigid 5-section template.
- **Large file handling**: if a write fails because of file size, retry with a chunked shell write (`cat << 'EOF' > file`) rather than asking the user.

## Acknowledgements

Outline methodology inspired by [Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills) (claim-evidence mapping), [claude-scholar](https://github.com/Galaxy-Dawn/claude-scholar) (citation verification), and [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) (claim verification protocol). The writing-framing overlay is adapted from Orchestra Research's paper-writing guidance. The opt-in style-reference / gap-report concept originated in upstream ARIS issue #217 (@zhangpelf).

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/paper-plan/SKILL.md (MIT). See registry/components.json. -->
