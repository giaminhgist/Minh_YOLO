# Paper Write: Section-by-Section LaTeX Generation

When this resource is used: when a paper plan (or an equivalent outline) exists and the user wants the actual LaTeX manuscript drafted — "write paper", "draft LaTeX", "开始写", "写论文" — or when an existing draft needs a section rewritten under the claim-calibration rules below.

## Context: $ARGUMENTS

Arguments: `[venue-or-section] [— style-ref: <source>]`.

## Constants

- **REVIEWER_MODEL** — a model from a *different family* than the executor, reached through whatever cross-model reviewer backend the session has configured (e.g. a Codex/OpenAI MCP server). Target reasoning effort: high (`xhigh` when the backend exposes it).
  - **Backend absent → `REVIEW_UNAVAILABLE`.** Run the same review prompt as a labeled self-review (fresh context), record `REVIEW_UNAVAILABLE` next to the feedback in the output, and never present it as independent review. Apply the same severity triage (CRITICAL/MAJOR/MINOR) either way.
- **TARGET_VENUE = `ICLR`** — Default venue. Supported: `ICLR`, `NeurIPS`, `ICML`, `CVPR` (also ICCV/ECCV), `ACL` (also EMNLP/NAACL), `AAAI`, `ACM` (ACM MM, SIGIR, KDD, CHI, etc.), `IEEE_JOURNAL` (IEEE Transactions / Letters, e.g. T-PAMI, JSAC, TWC, TCOM, TSP, TIP), `IEEE_CONF` (IEEE conferences, e.g. ICC, GLOBECOM, INFOCOM, ICASSP). Determines style file and formatting.
- **ANONYMOUS = true** — If true, use anonymous author block. Set `false` for camera-ready. Note: most IEEE venues do NOT use anonymous submission — set `false` for IEEE.
- **MAX_PAGES = 9** — Main body page limit. For ML conferences: counts from first page to end of Conclusion section, references and appendix NOT counted. **For IEEE venues: references ARE counted toward the page limit.** Typical limits: IEEE journal = no strict limit (but 12-14 pages typical for Transactions, 4-5 for Letters), IEEE conference = 5-8 pages including references. The live CFP overrides these defaults — verify before finalizing.
- **DBLP_BIBTEX = true** — Fetch real BibTeX from DBLP/CrossRef instead of model-generated entries. Eliminates hallucinated citations. Zero install required. Set `false` to use legacy behavior (search + `[VERIFY]` markers).

## Inputs

1. **PAPER_PLAN.md** — outline with claims-evidence matrix, section plan, figure plan (from the `paper-plan` resource)
2. **NARRATIVE_REPORT.md** — the research narrative (primary source of content)
3. **Generated figures** — PDF/PNG files in `figures/` (from the `paper-figure` resource, `${CLAUDE_PLUGIN_ROOT}/resources/figures/paper-figure/SKILL.md`)
4. **LaTeX includes** — `figures/latex_includes.tex` (from the `paper-figure` resource)
5. **Bibliography** — existing `.bib` file, or will create one

If no PAPER_PLAN.md exists, ask the user to plan the paper first or provide a brief outline.

## Writing-Reference Overlay

Use the bundled references only when they improve writing quality; they are support material, not extra workflow phases.

- Read `references/writing-principles.md` before drafting the Abstract, Introduction, Related Work, or when prose feels generic.
- Read `references/venue-checklists.md` during the final write-up and submission-readiness pass.
- Read `references/citation-discipline.md` only when the built-in DBLP/CrossRef workflow is insufficient.

## Optional: Style reference (`— style-ref: <source>`, opt-in)

Lets the user steer **structural** style (section ordering, theorem density, sentence cadence, figure density, bibliography style) toward a reference paper. **Default OFF — when the user does not pass `— style-ref`, do nothing differently.**

Only when `— style-ref: <source>` appears in the arguments, build the style profile FIRST, before drafting. Accepted sources: local TeX dir / file, local PDF, arXiv id (`2501.12345` or `arxiv:2501.12345`), http(s) URL. The full resolution procedure, cache layout (`style-ref/<source-slug>/style_profile.md` + `source_manifest.json`), and failure policy live in `${CLAUDE_PLUGIN_ROOT}/resources/writing/paper-plan/SKILL.md` § "Optional: Style reference" — including the two hard failure modes: unresolved source or failed fetch → **abort the draft**; missing PDF extractor → warn and continue without style guidance. Overleaf URLs and project IDs are rejected here (no Overleaf sync is bundled): export the project locally and pass that path.

**Strict rules:**

- Use `style_profile.md` as **structural** guidance only. Match section count, section-ordering tendency, theorem-environment density, caption-length distribution, sentence cadence, math display ratio, citation style.
- **Never copy prose, claims, examples, or terminology** from anything reachable through the cache. The profile is intentionally aggregate; if you need substance, use the user's own outline.
- **Never pass `— style-ref` (or the cache contents) to reviewer / auditor sub-agents.** Reviewer independence requires that reviewers see only the artifact and the user's prompt, not the author's stylistic context.

### `<!-- DATA_NEEDED -->` markers (when `GAP_REPORT.md` exists)

If paper planning ran with `— style-ref:` it will have emitted `GAP_REPORT.md` alongside `PAPER_PLAN.md`. This file lists structural slots (ablation tables, scaling experiments, failure-case analyses, …) the exemplar implies but the user has **no evidence to fill**.

When `GAP_REPORT.md` is present and a section slot is classified as `status: missing`:

1. **Do not fabricate numerical results, figure references, or qualitative claims** to fill that slot.
2. Emit an HTML-comment placeholder at the exact location the missing content would go:

   ```latex
   <!-- DATA_NEEDED: GAP_S5_ABLATION — ablation table comparing X across the 3 axes implied by exemplar -->
   ```

3. Slot ID and one-line description come straight from `GAP_REPORT.md`. **Never invent Slot IDs.** Never reword the description to be more confident than the report.
4. The marker is intentionally an HTML comment so it is invisible in the rendered PDF but **searchable via `grep -r "DATA_NEEDED" sections/`** for human triage.
5. For `status: partial`, write what the user has and emit `<!-- DATA_NEEDED: <Slot ID> — <what specifically is short> -->` at the gap point in the same paragraph (do not split the section).

**Carve-out from "no placeholder" rule.** The default no-placeholder discipline (no "see supplementary", no "TBD") still applies for everything **except** GAP_REPORT-listed missing slots. The marker is the principled way to surface genuine evidence deficits without compromising claim integrity.

## Templates

### Venue-Specific Setup

This resource bundles **conference wrapper templates** in `templates/` (select based on TARGET_VENUE):

**ICLR:**
```latex
\documentclass{article}
\usepackage{iclr2026_conference,times}
% \iclrfinalcopy  % Uncomment for camera-ready
```

**NeurIPS:**
```latex
\documentclass{article}
\usepackage[preprint]{neurips_2025}
% \usepackage[final]{neurips_2025}  % Camera-ready
```

**ICML:**
```latex
\documentclass[accepted]{icml2025}
% Use [accepted] for camera-ready
```

**IEEE Journal** (Transactions, Letters):
```latex
\documentclass[journal]{IEEEtran}
\usepackage{cite}  % IEEE uses \cite{}, NOT natbib
% Author block uses \author{Name~\IEEEmembership{Member,~IEEE}}
```

**IEEE Conference** (ICC, GLOBECOM, INFOCOM, ICASSP, etc.):
```latex
\documentclass[conference]{IEEEtran}
\usepackage{cite}  % IEEE uses \cite{}, NOT natbib
% Author block uses \IEEEauthorblockN / \IEEEauthorblockA
```

**Bundled vs. not bundled — read this before Step 1:**

| File | Status |
|------|--------|
| `templates/iclr2026.tex`, `neurips2025.tex`, `icml2025.tex`, `ieee_journal.tex`, `ieee_conference.tex`, `math_commands.tex` | **bundled** — copy into `paper/` and edit |
| Venue style files (`iclr2026_conference.sty`, `neurips_2025.sty`, `icml2025.sty`, …) | **NOT bundled** — download from the venue's official call-for-papers / author kit. Verify against the current year's CFP; the bundled wrapper names the expected file. |
| `IEEEtran.cls` + `IEEEtran.bst` | **NOT bundled** (third-party IEEE class, LPPL) — obtain from TeX Live/CTAN (`ieeetran` package) or the venue author kit. `\bibliographystyle{IEEEtran}` requires the `.bst` to be installed. |

If a required class/style file is missing, stop and tell the user which file to fetch; do not substitute a different class silently.

### Project Structure

Generate this file structure:

```
paper/
├── main.tex                    # master file (includes sections)
├── iclr2026_conference.sty     # or neurips_2025.sty / icml2025.sty / IEEEtran.cls + IEEEtran.bst
├── math_commands.tex           # shared math macros
├── references.bib              # bibliography (filtered — only cited entries)
├── sections/
│   ├── 0_abstract.tex
│   ├── 1_introduction.tex
│   ├── 2_related_work.tex
│   ├── 3_method.tex            # or preliminaries, setup, etc.
│   ├── 4_experiments.tex
│   ├── 5_conclusion.tex
│   └── A_appendix.tex          # proof details, extra experiments
└── figures/                    # symlink or copy from project figures/
```

**Section files are FLEXIBLE**: If the paper plan has 6-8 sections, create corresponding files (e.g., `4_theory.tex`, `5_experiments.tex`, `6_analysis.tex`, `7_conclusion.tex`).

## Workflow

### Step 0: Backup and Clean

If `paper/` already exists, back up to `paper-backup-{timestamp}/` before overwriting. Never silently destroy existing work.

**CRITICAL: Clean stale files.** When changing section structure (e.g., 5 sections → 7 sections), delete section files that are no longer referenced by `main.tex`. Stale files (e.g., old `5_conclusion.tex` left behind when conclusion moved to `7_conclusion.tex`) cause confusion and waste space.

### Step 1: Initialize Project

1. Create `paper/` directory
2. Copy the venue wrapper from `templates/` — the wrapper already includes:
   - All standard packages (amsmath, hyperref, cleveref, booktabs, etc.)
   - Theorem environments with `\crefname{assumption}` fix
   - Anonymous author block
3. Generate `math_commands.tex` with paper-specific notation
4. Create section files matching PAPER_PLAN structure

**Author block (anonymous mode):**
```latex
\author{Anonymous Authors}
```

### Step 2: Generate math_commands.tex

Create shared math macros based on the paper's notation:

```latex
% math_commands.tex — shared notation
\newcommand{\R}{\mathbb{R}}
\newcommand{\E}{\mathbb{E}}
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\argmax}{arg\,max}
% Add paper-specific notation here
```

### Step 3: Write Each Section

Process sections in order. For each section:

1. **Read the plan** — what claims, evidence, citations belong here
2. **Read NARRATIVE_REPORT.md** — extract relevant content, findings, and quantitative results
3. **Draft content** — write complete LaTeX (no fabricated placeholders). **Exception:** if `GAP_REPORT.md` exists and the section has slots with `status: missing`, emit `<!-- DATA_NEEDED: <Slot ID> — <description> -->` at those points instead of inventing data — see the DATA_NEEDED markers subsection above.
4. **Insert figures/tables** — use snippets from `figures/latex_includes.tex` (produced by the `paper-figure` resource). If a planned figure has no file yet, insert the `\includegraphics` line and flag it as `[FIGURE MISSING: <path>]` rather than drawing a replacement.
5. **Add citations** — for ML conferences (ICLR/NeurIPS/ICML/CVPR/ACL/AAAI): use `\citep{}` / `\citet{}` (natbib). **For IEEE venues**: use `\cite{}` (numeric style via `cite` package). Never mix natbib and cite commands.

Before drafting the front matter, re-read the one-sentence contribution from `PAPER_PLAN.md`. The Abstract and Introduction should make that takeaway obvious before the reader reaches the full method.

#### Section-Specific Guidelines

**§0 Abstract:**
- Use the 5-part flow from `references/writing-principles.md`: what, why hard, how, evidence, strongest result
- Must be self-contained (understandable without reading the paper)
- Start with the paper's specific contribution, not generic field-level background
- Include one concrete quantitative result
- 150-250 words (check venue limit)
- No citations, no undefined acronyms
- No `\begin{abstract}` — that's in main.tex

**§1 Introduction:**
- Open with a compelling hook (1-2 sentences, problem motivation)
- State the gap clearly ("However, ...")
- Give a brief approach overview before the reader gets lost in details
- List 2-4 specific, falsifiable contributions as a numbered or bulleted list
- Preview the strongest result early instead of saving it for the experiments section
- End with a brief roadmap ("The rest of this paper is organized as...")
- Include the main result figure if space allows
- Target: 1-1.5 pages
- Methods should begin by page 2-3 at the latest

**§2 Related Work:**
- **MINIMUM 1 full page** (3-4 substantive paragraphs). Short related work sections are a common reviewer complaint.
- Organize by category using `\paragraph{Category Name.}`
- Organize methodologically, by assumption class, or by research question; do not write paper-by-paper mini-summaries
- Each category: 1 paragraph summarizing the line of work + 1-2 sentences positioning this paper
- Do NOT just list papers — synthesize and compare
- End each paragraph with how this paper relates/differs

**§3 Method / Preliminaries / Setup:**
- Define notation early (reference math_commands.tex)
- Use `\begin{definition}`, `\begin{theorem}` environments for formal statements
- For theory papers: include proof sketches of key results in main body, full proofs in appendix
- For theory papers: include a **comparison table** of prior bounds vs. this paper
- Include algorithm pseudocode if applicable (`algorithm2e` or `algorithmic`)
- Target: 1.5-2 pages

**§4 Experiments:**
- Start with experimental setup (datasets, baselines, metrics, implementation details)
- Main results table/figure first
- Then ablations and analysis
- Every claim from the introduction must have supporting evidence here
- For each major experiment, make explicit what claim it supports and what the reader should notice
- Target: 2.5-3 pages

**§5 Conclusion:**
- Summarize contributions (NOT copy-paste from intro — rephrase)
- Limitations (2-4 material, specific limits — dataset scale, compute regime, assumption X; real ones only, never invented to fill a count. This section is the ONLY home for generic caveats)
- Future work (1-2 concrete directions)
- Ethics statement and reproducibility statement (if venue requires)
- Target: 0.5 pages

**Appendix:**
- Proof details (full proofs of main-body theorems)
- Additional experiments, ablations
- Implementation details, hyperparameter tables
- Additional visualizations

### Step 3.5: Theory Paper Consistency Pass (theory papers only)

Run this pass after drafting all sections and before building the bibliography.

**Trigger heuristic:** treat the paper as theory-heavy if `PAPER_PLAN.md` labels it as theory/analysis, or if the drafted sections contain 5 or more formal result environments (`\begin{theorem}`, `\begin{lemma}`, `\begin{proposition}`, `\begin{corollary}`).

**Proof source search:** search the workspace for any standalone full-proof source file whose name or contents indicate a canonical proof version (`proof`, `appendix`, `full`, `complete`, `supplement`, `supplementary`). If such a file exists, prompt the user exactly:

`Inline full proofs from {file}? [Y/n]`

Default to `Y`.

If the user accepts:
- import the full theorem/lemma statement plus proof block into the appendix source (`A_appendix.tex` or the appendix file named by the plan)
- use the main-body theorem statement as the canonical public statement; the appendix copy must match it unless the main-body statement is being revised in the same pass
- do **not** leave placeholders such as "see supplementary proof document" or "proof omitted for brevity"
- preserve theorem labels, equation labels, and proof structure exactly
- keep the main body proof sketches short, but never let the appendix be a sketch-only placeholder when a full proof source exists

If no standalone full-proof source exists:
- use proof sketches only when they are actually written as proof sketches, not placeholders
- do not fabricate an external proof document reference

**Restatement audit:**
- Compare every theorem/lemma/proposition statement that is restated in the appendix against the main-body version
- Do not diff proof bodies; only audit statements, hypotheses, case splits, quantifiers, domains, notation, variable names, and terminology for defined objects
- Treat `stationary` vs `terminal`, changed assumption names, or missing case splits as mismatches unless explicitly documented
- If the appendix needs different wording, add an explicit notation bridge instead of silently renaming concepts
- Resolve all mismatches before Step 4

**Empirical motivation:** in a real theory-paper run, the default behavior generated `"see supplementary proof document"` placeholders in the appendix. The author had to manually pull hundreds of lines of full proofs from a standalone proofs file (e.g. `proof_full.tex`). Without this pass, theory papers ship with sketch-only appendices that fail at theory venues.

### Step 4: Build Bibliography

**CRITICAL: Only include entries that are actually cited in the paper.**

1. Scan all citation references in the drafted sections (`\citep{}`/`\citet{}` for ML conferences, `\cite{}` for IEEE venues)
2. Build a citation key list
3. For each citation key:
   - Check existing `.bib` files in the project/narrative docs
   - If not found and **DBLP_BIBTEX = true**, use the verified fetch chain below
   - If not found and **DBLP_BIBTEX = false**, search arXiv/DBLP for correct BibTeX
   - **NEVER fabricate BibTeX entries** — mark unknown ones with a `[VERIFY]` comment
4. Write `references.bib` containing ONLY cited entries (no bloat)

#### Verified BibTeX Fetch (when DBLP_BIBTEX = true)

Three-step fallback chain — zero install, zero auth, all real BibTeX:

**Step A: DBLP (best quality — full venue, pages, editors)**
```bash
# 1. Search by title + first author
curl -s "https://dblp.org/search/publ/api?q=TITLE+AUTHOR&format=json&h=3"
# 2. Extract DBLP key from result (e.g., conf/nips/VaswaniSPUJGKP17)
# 3. Fetch real BibTeX
curl -s "https://dblp.org/rec/{key}.bib"
```

**Step B: CrossRef DOI (fallback — works for arXiv preprints)**
```bash
# If paper has a DOI or arXiv ID (arXiv DOI = 10.48550/arXiv.{id})
curl -sLH "Accept: application/x-bibtex" "https://doi.org/{doi}"
```

**Step C: Mark `[VERIFY]` (last resort)**
If both DBLP and CrossRef return nothing, mark the entry with `% [VERIFY]` comment. Do NOT fabricate.

**Why this matters:** model-generated BibTeX frequently hallucinates venue names, page numbers, or even co-authors. DBLP and CrossRef return publisher-verified metadata. Upstream research resources may mention papers from model memory — this fetch chain is the gate that prevents hallucinated citations from entering the final `.bib`.

If the DBLP/CrossRef flow is not enough, load `references/citation-discipline.md` for stricter fallback rules before adding placeholders.

**Automated bib cleaning** — use this stdlib-only Python pattern to extract only cited entries:

```python
import re, pathlib
# 1. Grep all \citep{...}, \citet{...}, \cite{...} from every .tex file (handle multi-cite a,b,c)
# 2. Extract unique keys
# 3. Parse the .bib file with a regex over entry headers (@type{key,) — no third-party parser
# 4. Keep only entries whose key is in the cited set; write the filtered bib
```

This prevents bib bloat (e.g., 948 lines → 215 lines in testing).

**Enforced Bib Hygiene Validation** — run immediately after the filtered `references.bib` is written. Offline reconciliation is stdlib-only (no `pip install`, no third-party BibTeX parser):

```python
import re, pathlib, sys

ROOT = pathlib.Path("paper")
tex_paths = [ROOT / "main.tex", *sorted((ROOT / "sections").glob("*.tex"))]
tex = "\n".join(p.read_text(errors="ignore") for p in tex_paths if p.exists())

cited = set()
for m in re.finditer(r'\\cite[a-zA-Z]*\{([^}]*)\}', tex):
    cited.update(k.strip() for k in m.group(1).split(',') if k.strip())

bib_text = (ROOT / "references.bib").read_text(errors="ignore")
bib_keys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)\s*,', bib_text))

dead = sorted(bib_keys - cited)          # in bib, never cited → delete
missing = sorted(cited - bib_keys)       # cited, no bib entry → must be fetched or [VERIFY]

if dead:
    print("DEAD ENTRIES:")
    for key in dead:
        print("  ", key)
if missing:
    print("MISSING ENTRIES (cited but absent from references.bib):")
    for key in missing:
        print("  ", key)
if not dead and not missing:
    print("OK: cited keys and bib entries agree")
```

Then verify metadata against the two publisher sources — one lookup per cited entry, using the fetch tool or `curl`:

1. Query DBLP by title (+ first author) and compare **year**, **venue/booktitle**, and the **first two authors** against the entry. Normalize by lowercasing and collapsing non-alphanumerics before comparing.
2. If DBLP misses and the entry has a `doi` field, fetch `https://doi.org/{doi}` with `Accept: application/x-bibtex` and compare the same three fields.
3. Print `VERIFY {key}: no DBLP/CrossRef hit` or `MISMATCH {key} ({source}): <fields>` for every entry that fails.

Decision rules:

- `DEAD ENTRIES` printed → remove those keys from `references.bib` before continuing.
- `MISSING ENTRIES` printed → run the verified fetch chain (Step A/B) for each key; only placeholders marked `% [VERIFY]` may remain.
- `VERIFY` or `MISMATCH` printed → do not invent metadata:
  - prefer DBLP when it returns a clear hit
  - if DBLP misses and a DOI is available, fall back to CrossRef
  - if both disagree or still cannot verify, keep the entry only with a `% [VERIFY]` marker
  - uncited entries must be deleted, not left behind as dead bibliography bloat

**Citation reachability rule:** an entry is dead if its key does not appear in any `\cite...{}` command in `paper/main.tex` or any `paper/sections/*.tex` file.

**Empirical motivation:** in a real submission run, several dead bib entries sat in `references.bib` for many improvement rounds, and at least one entry had a key/year mismatch. Neither was flagged by the existing automated cleaning.

**Citation verification rules** (verified-metadata discipline; stricter protocol in `references/citation-discipline.md`):
1. Every BibTeX entry must have: author, title, year, venue/journal
2. Prefer published venue versions over arXiv preprints (if published)
3. Use consistent key format: `{firstauthor}{year}{keyword}` (e.g., `ho2020denoising`)
4. Double-check year and venue for every entry
5. Remove duplicate entries (same paper with different keys)

### Step 5: Scientific Writing Quality Pass (5 audit passes)

After drafting all sections, run five sequential audit passes. Based on Sainani's "Writing in the Sciences" methodology: every word must earn its place.

**Pass 1: Clutter Extraction** — Strip sentences to cleanest components.

| Cluttered phrase | Replace with |
|------------------|--------------|
| Due to the fact that | Because |
| In order to | To |
| A number of | Several |
| It is worth noting that | (delete — just state the point) |
| It is important to note that | (delete) |
| At the present time | Now |
| On the basis of | Based on |
| In light of the fact that | Because |
| Have an effect on | Affect |
| Give rise to | Cause |

Also remove redundancies: "completely eliminate" → "eliminate", "future plans" → "plans", "unexpected surprise" → "surprise".

Remove AI-isms: delve, pivotal, landscape, tapestry, underscore, noteworthy, intriguingly.

**Pass 2: Active Voice and Verb Vitality** — Identify who did what.

- Spot passive: "to-be" verb + past participle ("was observed", "were analyzed")
- Convert: find the actor, reconstruct as Subject–Verb–Object
- Resurrect smothered verbs (nominalizations):
  - "We made an investigation" → "We investigated"
  - "Failure of the system occurs" → "The system fails"
  - "Provides a description of" → "Describes"

Passive voice IS acceptable for: established facts, methods where agent is irrelevant, or when required by venue style.

**Pass 3: Sentence Architecture** — Structure and flow. Vary paragraph shape:
if every paragraph runs problem → method → benefit → summary, the mold numbs
the reader — break it.

- Flag sentences > 40 words for splitting
- Ensure subject and verb are close together (no long parenthetical insertions between them)
- Put familiar context first, new information later
- Place the most important point near the end of the sentence
- Let each paragraph do one job
- Don't start consecutive sentences with "This" or "We"
- Check paragraph transitions — each paragraph's first sentence should connect to the previous

**Pass 4: Keyword Consistency** — The Banana Rule.

**Do not call a "banana" an "elongated yellow fruit" to avoid repetition.** If the Methods say "obese group," the Results must not switch to "heavier group." Synonym variation for technical terms forces the reader to wonder whether a new category has been introduced.

- Extract all key terms from Method section (group names, variable names, technique names, abbreviations)
- Verify exact same terms appear in Results, Discussion, Tables, Figure captions
- Flag every synonym substitution for a defined term
- Acronym austerity: flag non-standard acronyms created only for convenience; verify every acronym is defined at first use

**Pass 5: Numerical and Citation Integrity**

- Does sample size (N) in Abstract match Table 1?
- Do percentages in Results match raw numbers in Tables?
- Are significant figures consistent and appropriate?
- Do Figure graphics match Table values?
- Flag statistics cited only through secondary sources (reviews, textbooks) — recommend verifying primary source
- Do not write a "citations verified" line in prose; verification lives in the tool trace and the audit artifacts

### Step 6: Cross-Review with the Reviewer Backend

Send the complete draft to the cross-model reviewer at high reasoning effort (see Constants):

```
Review this [VENUE] paper draft (main body, excluding appendix).

Judge claim calibration in BOTH directions. Recommend narrowing only when the
current scope or modality exceeds the evidence; do not ask for extra hedges
around a supported result. Flag stacked hedges, self-defence ("we do not
claim"), instruction confessions ("we do not address X"), and generic caveats
outside Limitations as writing defects to remove. Tone fixes must never alter
facts, negation, modality, scope, comparison direction, or numbers.

Focus on:
1. Does each claim from the intro have supporting evidence?
2. Is the writing clear, concise, and free of AI-isms?
3. Any logical gaps or unclear explanations?
4. Does it fit within [MAX_PAGES] pages (to end of Conclusion)?
5. Is related work sufficiently comprehensive (≥1 page)?
6. For theory papers: are proof sketches adequate?
7. Are figures/tables clearly described and properly referenced?
8. Would a skim reader understand the contribution from the title, abstract, introduction, and Figure 1?

For each issue, specify: severity (CRITICAL/MAJOR/MINOR), location, and fix.

[paste full draft text]
```

Apply CRITICAL and MAJOR fixes. Document MINOR issues for the user. If no reviewer backend is available, run this prompt as a labeled self-review and mark the feedback block `REVIEW_UNAVAILABLE`.

### Step 7: Reverse Outline Test

After drafting all sections:

1. **Extract topic sentences** — pull the first sentence of every paragraph
2. **Read them in sequence** — they should form a coherent narrative on their own
3. **Check claim coverage** — every claim from the Claims-Evidence Matrix must appear
4. **Check evidence mapping** — every experiment/figure must support a stated claim
5. **Fix gaps** — if a topic sentence doesn't advance the story, rewrite the paragraph

### Step 8: Build the PDF (native LaTeX — no external compile service)

Build locally with the standard TeX toolchain; nothing here is delegated to another resource.

```bash
cd paper
latexmk -pdf -interaction=nonstopmode main.tex     # runs pdflatex/bibtex as many passes as needed
```

Then inspect the log for the failure classes below before reporting the build:

- **Undefined citations** (`Citation 'x' undefined`) → the key is missing from `references.bib`, or the `.bib` was not re-run; fix the bib, re-run `latexmk`.
- **Undefined references** (`Reference 'x' undefined`) → mismatched `\label`/`\ref`; fix and rebuild.
- **`Citation ... undefined` with `\cite` vs `\citep` confusion** → natbib/cite package mismatch for the venue; fix the preamble (never mix).
- **Overfull `\hbox` warnings** → inspect; fix only if text is visibly clipped in the output PDF.
- **Page count** → read the final page number in the log and compare to MAX_PAGES under the venue's counting rule (IEEE counts references).

If no TeX distribution is available, do **not** claim the paper compiles. Run the static checks instead and say so explicitly in the final report:

- every `\input{}`/`\include{}` target exists,
- every `\cite` key has a `references.bib` entry (the Step 4 reconciliation),
- every `\ref` has a matching `\label`,
- no `TODO`/`FIXME`/`XXX` and no unchecked `[VERIFY]` markers remain.

Report either the built PDF path or the explicit "PDF not built — TeX toolchain unavailable" status with the static-check results.

### Step 9: Final Checks

Before declaring done:

- [ ] All `\ref{}` and `\label{}` match (no undefined references)
- [ ] All citation commands (`\citep{}`/`\citet{}` for ML conferences, `\cite{}` for IEEE) have corresponding BibTeX entries
- [ ] No author information in anonymous mode
- [ ] Figure/table numbering is correct
- [ ] Page count within MAX_PAGES (main body to Conclusion end)
- [ ] No TODO/FIXME/XXX markers left in the text
- [ ] No `[VERIFY]` markers left unchecked
- [ ] Abstract is self-contained (understandable without reading the paper)
- [ ] Title is specific and informative (not generic)
- [ ] Related work is ≥1 full page
- [ ] references.bib contains ONLY cited entries (no bloat)
- [ ] **No stale section files** — every .tex in `sections/` is `\input`ed by `main.tex`
- [ ] **Section files match main.tex** — file numbering and `\input` paths are consistent
- [ ] Venue-specific required sections/checklists satisfied (read `references/venue-checklists.md` if needed)
- [ ] A skim reader can recover the main claim from the title, abstract, introduction, and Figure 1/captions
- [ ] PDF built, or the static-check fallback explicitly reported

## Key Rules

=== CONFIDENT PROSE, HONEST LIMITS (never upgrades claims) ===
1. Calibrate each claim to the evidence's actual scope and modality, then state
   that calibrated claim directly. Necessary assumptions, uncertainty, and
   scope are part of the claim; stacked hedges and defensive throat-clearing
   are not.
2. If the current claim is unsupported, narrow it to a version the evidence
   supports or cut it. Do not substitute a softer-sounding synonym for fixing
   scope, modality, comparison, or aggregation.
3. Put generic caveats and broader boundary discussion in one Limitations
   section. Outside it, remove generic disclaimers such as "further research
   is needed", "may not generalize", and "should be interpreted with caution".
   Claim-defining scope, assumptions, and statistical qualifications stay
   attached to the claims they make true.
4. Aim for 2-4 material, specific limitations (dataset scale, compute regime,
   assumption X). Real ones only — never invent one to meet a count, never
   apologize generically, never repeat the same limitation through the paper.
5. Writing instructions are not manuscript content. "Do not mention X" means
   omit X, not write "we do not address/claim/discuss X". Never expose
   drafting instructions, requested omissions, reviewer feedback, or revision
   history in manuscript prose.
6. Replace self-defence ("we do not claim", "our goal is merely") with a
   positive, evidence-matched statement of what the paper does establish. If
   the defensive sentence carries a real boundary, keep that boundary in the
   claim or Limitations; do not delete truth-conditional content.
7. Tone-only edits never alter facts, negation, modality, scope, assumptions,
   comparison direction, aggregation, numbers, formulas, or citations. Genuine
   overclaims must still be narrowed; supported claims wrapped in redundant
   caution must be stated directly.
8. One causal spine: gap -> question -> insight -> consequence -> evidence ->
   implication. Every section advances it. Make the method feel inevitable:
   the gap creates a concrete question, the key insight answers it, the method
   follows from the insight, each major experiment tests a consequence of it,
   and the conclusion states exactly what the evidence establishes.
   Front-load the contribution; never narrate the drafting or revision process.
9. The paper is a launch, not a progress report. Organize the narrative
   around the work's strongest genuine advantage — a new capability, problem,
   mechanism or viewpoint, wider applicability, lower cost, a better tradeoff.
   Material that does not form an advantage stays out of the main line. If the
   results cannot carry the original story, rebuild the story around the
   strongest evidence instead of defending the original one.
10. Pick the contest the paper wins. Do not build the narrative on a metric
    where the method is not ahead; frame the comparison around the task
    definition, evaluation dimension or constraint that reflects what the
    method is for, and say explicitly which contest it wins. Unfavorable
    numbers still appear — tables stay complete. Where the evidence supports
    it, explain them as a goal difference or a deliberate tradeoff rather
    than narrating a defeat ("underperforms", "fails to surpass"); where it
    does not, state the underperformance neutrally, narrow the claim, and
    keep it in Limitations if it is material. Never elevate a local
    observation into a verdict on the whole method, and never invent a
    tradeoff to cover a weakness.
11. Every experiment has an argumentative duty: it shows the method works,
    shows the gain comes from the key mechanism, shows value in the target
    scenario, or rules out the most likely alternative explanation. An
    experiment carrying none of these is cut, shortened, moved to the
    appendix, or redesigned. The experiments section is an argument, not a
    results warehouse.
12. State the advantage yourself — under which condition it appears, why it
    appears, what it solves — rather than expecting the reviewer to find it
    in a table. Abstract and introduction open like a launch: an important
    unsolved problem, the gap in existing methods, this paper's distinct
    idea, the heaviest result. The conclusion reinforces what was solved,
    proposed and proven and why it matters; no new self-negation or widened
    limitations in the last paragraph.

- **Large file handling**: if a write fails because of file size, retry with a chunked shell write (`cat << 'EOF' > file`) rather than asking the user.
- **Do NOT generate author names, emails, or affiliations** — use anonymous block or placeholder
- **Write complete sections, not outlines** — the output should be compilable LaTeX
- **One file per section** — modular structure for easy editing
- **Every claim must cite evidence** — cross-reference the Claims-Evidence Matrix
- **Compile-ready** — the output should compile with `latexmk` without errors (modulo missing figures)
- **Calibrate, don't hedge** — match each claim to its evidence's actual scope and modality, then state it directly; generic caveats live in Limitations only (the CONFIDENT PROSE, HONEST LIMITS block above is the contract)
- **Launch, not progress report** — organize around the strongest genuine advantage, pick the contest the paper wins, give every experiment an argumentative duty; unfavorable numbers stay in the tables, explained as tradeoffs where the evidence supports that and stated neutrally where it does not — never narrated as defeats, never dressed as a tradeoff they are not (rules 9-12 above)
- **Venue style matters** — ML conferences (ICLR/NeurIPS/ICML) use `natbib` (`\citep`/`\citet`); **IEEE venues use `cite` package (`\cite{}`, numeric)**. Never mix.
- **Page limit rules differ by venue** — ML conferences: main body to Conclusion, references/appendix NOT counted. **IEEE: references ARE counted toward the page limit.**
- **Clean bib** — references.bib must only contain entries that are actually `\cite`d
- **Section count is flexible** — match PAPER_PLAN structure, don't force into 5 sections
- **Backup before overwrite** — never destroy existing `paper/` directory without backing up
- **Front-load the contribution** — do not hide the payoff until the experiments or appendix
- **Order results by argument, not by lab notebook** — present experiments in the sequence that best builds the case, never in the order they happened to run
- **Controls and ablations sit next to the claim they test** — not pooled in a distant subsection where the reader has forgotten what was at stake
- **No fabricated numbers, even mid-draft** — a number that is not in a result file, log, or the narrative report does not get written; mark the gap instead (see DATA_NEEDED)

## Writing Quality Reference

- `references/writing-principles.md` — story framing, abstract/introduction patterns, sentence-level clarity, reviewer reading order
- `references/venue-checklists.md` — ICLR/NeurIPS/ICML/IEEE submission requirements to check before declaring done
- `references/citation-discipline.md` — stricter fallback for ambiguous citations
- `${CLAUDE_PLUGIN_ROOT}/resources/figures/paper-figure/SKILL.md` — figure and table generation (data plots, LaTeX comparison tables, `latex_includes.tex`)
- Out of scope for this resource: Overleaf sync, automated improvement loops, slide/poster generation, rebuttal writing. Handle those directly or ask the user.

Keep using the reverse-outline test and anti-inflation polish from the main workflow above; the bundled references are there to improve quality without adding a new phase.

## Acknowledgements

Writing methodology adapted from [Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills) (CCF award-winning methodology). Citation verification from [claude-scholar](https://github.com/Galaxy-Dawn/claude-scholar) and [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills). This writing-guidance overlay is adapted from Orchestra Research's paper-writing materials.

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/paper-write/SKILL.md (MIT). See registry/components.json. -->
