# Grant Proposal: From Research Ideas to Fundable Application

When this resource is used: when the user wants to turn a validated research direction into a funding application — "write grant", "grant proposal", "申請書", "科研費", "基金申请", "写基金", "NSF proposal" — including KAKENHI, NSF, NSFC, ERC, DFG, SNSF, ARC, NWO, and generic formats. A grant is not a paper; this resource argues future work.

## Context: $ARGUMENTS

Arguments: `[research-direction — grant-type] [— style-ref: <source>]`, optionally with sub-type, output format, language, and review-round overrides.

## Overview

This resource turns validated research ideas into a structured, reviewer-ready grant proposal through five gated phases:

```
Phase 1 landscape + gap → Phase 2 aims/structure → Phase 3 draft sections → Phase 4 panel review → Phase 5 revise + output → GRANT_PROPOSAL.md
   (survey + funded-project scan)  (aims + matrix + timeline)   (prose + figures)     (external panelist)      (apply fixes)          (done!)
```

**This is a parallel branch, not part of a linear idea→experiment→paper pipeline.** After ideas are validated, the user can either implement and publish, or write the funding application first and implement after funding.

Grant proposals argue for **future work** (feasibility + potential), not completed work (results + claims). This resource handles the unique requirements of grant writing: narrative arc design, reviewer-facing structure, budget justification, timeline planning, and agency-specific formatting.

## Constants

- **GRANT_TYPE = `KAKENHI`** — Default grant type. Supported: `KAKENHI`, `NSF`, `NSFC`, `ERC`, `DFG`, `SNSF`, `ARC`, `NWO`, `GENERIC`. Override via argument (e.g. `— NSF`).
- **GRANT_SUBTYPE = `auto`** — Sub-type within the agency. Examples: KAKENHI `Start-up`/`Wakate`/`Kiban-B`; NSFC `Youth`/`Excellent-Youth`/`Distinguished`/`Overseas`/`Key`; NSF `CAREER`/`CRII`/`Standard`. Auto-detected from the argument or defaults to the most common sub-type.
- **Reviewer backend** — a *cross-model* reviewer (different model family from the executor), reached through the session's configured backend (e.g. a Codex/OpenAI MCP server), reasoning effort as high as the backend exposes (target `xhigh`). **Absent → skip external review, record `REVIEW_UNAVAILABLE`, and say so in `GRANT_REVIEW.md`.** A same-model review may still run, but must be labeled non-independent; the proposal remains usable without external review.
- **OUTPUT_FORMAT = `markdown`** — Supported: `markdown`, `latex`.
- **MAX_REVIEW_ROUNDS = 2** — Maximum external review-revise cycles before finalizing.
- **OUTPUT_DIR = `grant-proposal/`** — Directory for generated proposal files.
- **LANGUAGE = `auto`** — Output language. Auto-detected from grant type: KAKENHI→Japanese, NSF→English, NSFC→Chinese, ERC→English, DFG→English (or German), SNSF→English, ARC→English, NWO→English. Override explicitly if needed.
- **AUTO_PROCEED = false** — At each checkpoint, **always wait for explicit user confirmation** before proceeding. Grant proposals require PI-specific judgment at every stage. Set `true` only if the user explicitly requests fully autonomous mode.

> These are defaults. Override by telling the resource, e.g. "topic — NSF CAREER, latex output" or "topic — NSFC Youth, language: English".

## Optional: Style reference (`— style-ref: <source>`, opt-in)

Lets the PI steer the proposal's **structural** layout (section order tendency, paragraph length, figure density, citation style) toward a successful past proposal or paper. **Default OFF — when the user does not pass `— style-ref`, do nothing differently.**

Only when `— style-ref: <source>` appears in the arguments, build the profile FIRST, before drafting. The resolution procedure, accepted sources (local TeX dir/file, local PDF, arXiv id, http(s) URL), the deterministic `style-ref/<source-slug>/` cache, and the failure policy live in `${CLAUDE_PLUGIN_ROOT}/resources/writing/paper-plan/SKILL.md` § "Optional: Style reference". Overleaf URLs/IDs are rejected (no Overleaf sync is bundled) — clone locally first. An unresolvable source or a failed fetch **aborts the proposal**; a missing PDF extractor only warns and continues without style guidance.

**Strict rules:**

- Use `style_profile.md` to align paragraph-length tendency, figure budget, and citation density. Grant-type-mandated section order (KAKENHI 研究目的 → 研究計画・方法 → 準備状況, NSF Intellectual Merit → Broader Impacts, etc.) **always takes precedence** — the agency template wins, the style ref only refines secondary structure.
- **Never copy proposal prose, claims, vision statements, or budget items** from anything reachable through the cache. The reference might be someone else's funded proposal; reproducing language risks plagiarism.
- **Never pass `— style-ref` (or the cache contents) to the reviewer** when it scores the draft — the proposal must be judged on its own merits.

## Grant Type Specifications

### KAKENHI (Japan — JSPS)

| Field | Detail |
|-------|--------|
| **Sections** | 研究目的 (Research Objective), 研究計画・方法 (Plan & Methods), 準備状況 (Preparation Status), 人権の保護 (Ethics, if applicable) |
| **Sub-types** | 基盤研究 A/B/C (Kiban), 若手研究 (Wakate), 研究活動スタート支援 (Start-up), 国際共同研究 (International), 学術変革領域 (Transformative), 挑戦的研究 (Challenging), DC1/DC2 (doctoral) |
| **Language** | Japanese (English technical terms acceptable) |
| **Review criteria** | 学術的重要性 (academic significance), 独創性 (originality), 研究計画の妥当性 (plan feasibility), 研究遂行能力 (PI capability) |
| **Cultural norms** | Explicit yearly milestones (Year 1 / Year 2), budget justification integrated into plan, emphasize 社会的意義 (societal significance), concrete expected outputs (papers, datasets), reference the KAKEN database for related funded projects |

### NSF (US)

| Field | Detail |
|-------|--------|
| **Sections** | Project Summary (1p), Project Description (15p max), References Cited, Biographical Sketch, Budget Justification, Data Management Plan |
| **Sub-types** | Standard Grant, CAREER (early career), CRII (research initiation), RAPID, EAGER |
| **Language** | English |
| **Review criteria** | Intellectual Merit, Broader Impacts |
| **Cultural norms** | Aim-based structure (Aim 1/2/3), preliminary data strongly expected, broader impacts must be concrete and specific (not generic "benefit society"), Results from Prior Support section |

### NSFC (China — 国家自然科学基金)

| Field | Detail |
|-------|--------|
| **Sections** | 立项依据 (Rationale & Significance), 研究内容 (Content), 研究目标 (Objectives), 研究方案 (Plan & Methods), 可行性分析 (Feasibility), 创新性 (Innovation Points), 预期成果 (Expected Outcomes), 研究基础 (PI Foundation & Track Record) |
| **Sub-types** | 面上项目 (General Program) — emphasis on scientific problem and research accumulation; 青年基金 (Young Scientists Fund) — age ≤35, emphasis on independence and growth potential; 优秀青年基金/优青 (Excellent Young Scientists) — age ≤38, emphasis on outstanding achievements; 杰出青年基金/杰青 (Distinguished Young Scientists) — age ≤45, emphasis on international-leading level; 海外优青 (Overseas Excellent Young Scientists) — emphasis on overseas experience and return contribution plan; 重点项目 (Key Program) — emphasis on systematic in-depth research |
| **Language** | Chinese |
| **Review criteria** | 科学意义 (scientific significance), 创新性 (innovation), 可行性 (feasibility), 研究队伍 (team qualification) |
| **Cultural norms** | Heavy emphasis on 国际前沿 (international frontier) positioning, detailed feasibility analysis, explicit citation of the applicant's prior publications, 研究基础 section is critical for demonstrating PI capability |

### ERC (EU — European Research Council)

| Field | Detail |
|-------|--------|
| **Sections** | Extended Synopsis (5p), Scientific Proposal Part B2 (15p) |
| **Sub-types** | Starting Grant (2-7 years post-PhD), Consolidator Grant (7-12 years), Advanced Grant (established leaders) |
| **Language** | English |
| **Review criteria** | Ground-breaking nature, Methodology, PI track record |
| **Cultural norms** | Emphasis on "high-risk/high-gain", methodology table with WP/deliverables/milestones, Gantt chart expected, strong PI narrative |

### DFG (Germany — Deutsche Forschungsgemeinschaft)

| Field | Detail |
|-------|--------|
| **Sections** | State of the Art, Objectives, Work Programme, Bibliography, CV |
| **Language** | English or German |
| **Review criteria** | Scientific quality, Originality, Feasibility, PI qualification |

### SNSF (Switzerland — Swiss National Science Foundation)

| Field | Detail |
|-------|--------|
| **Sections** | Summary, Research Plan, Timetable, Budget |
| **Language** | English |
| **Review criteria** | Scientific relevance, Originality, Feasibility, Track record |

### ARC (Australia — Australian Research Council)

| Field | Detail |
|-------|--------|
| **Sections** | Project Description, Feasibility, Benefit, Budget |
| **Language** | English |
| **Review criteria** | Research quality, Feasibility, Benefit to Australia |

### NWO (Netherlands — Dutch Research Council)

| Field | Detail |
|-------|--------|
| **Sections** | Summary, Proposed Research, Knowledge Utilisation |
| **Language** | English |
| **Review criteria** | Scientific quality, Innovative character, Knowledge utilisation |

### GENERIC

For any grant not listed above. The user provides section names, page limits, and review criteria via the argument:

```
grant proposal "topic — GENERIC, sections: Background|Methods|Impact, language: English"
```

The live agency call-for-proposals always overrides the tables above — verify section list, page limits, and review criteria against the current call before drafting.

## State Persistence (Compact Recovery)

Grant proposal drafting is a long task that may trigger context compaction. Persist state to `grant-proposal/GRANT_STATE.json` after each phase:

```json
{
  "phase": 2,
  "grant_type": "KAKENHI",
  "grant_subtype": "Start-up",
  "language": "Japanese",
  "reviewer_thread_id": "019cfcf4-...",
  "gap_statement": "...",
  "aims_count": 3,
  "status": "in_progress",
  "timestamp": "2026-03-18T15:00:00"
}
```

**Write this file at the end of every phase.** On invocation, check for this file:

- If absent or `status: "completed"` → fresh start
- If `status: "in_progress"` and within 24h → **resume** from the saved phase (read `GRANT_PROPOSAL.md` and `GRANT_REVIEW.md` to restore context)
- If older than 24h → fresh start (stale state)

On completion, set `"status": "completed"`.

## Workflow

### Phase 0: Input Parsing & Context Gathering

Parse the arguments to extract:

1. **Research direction/idea** — may reference existing files or be a freeform description
2. **Grant type** — detect from keywords (e.g. "科研費"→KAKENHI, "NSF"→NSF, "国自然"→NSFC, "基金"→NSFC)
3. **Grant sub-type** — detect from keywords (e.g. "Start-up", "若手", "青年", "CAREER", "优青", "海外优青")
4. **Overrides** — output format, language, review rounds

Then gather context from the project directory:

1. Read `idea-stage/IDEA_REPORT.md` if it exists; fall back to `./IDEA_REPORT.md`
2. Read `refine-logs/FINAL_PROPOSAL.md` if it exists
3. Read `refine-logs/EXPERIMENT_PLAN.md` if it exists
4. Read `review-stage/AUTO_REVIEW.md` if it exists (prior review feedback is gold for grants); fall back to `./AUTO_REVIEW.md`
5. Read `NARRATIVE_REPORT.md` or `STORY.md` if they exist
6. Read any existing literature notes or survey documents
7. Scan for the user's publication list (e.g. `publications.md`, `cv.md`, `bio.md`, `CV.pdf`)
8. Check for `grant-proposal/GRANT_STATE.json` (resume from a prior interrupted run)

If insufficient context exists:

- No research idea at all → ask the user for the direction before doing anything else
- No literature survey → run the Phase 1 survey inline
- No publication list → leave the PI qualification section with `[TODO: Add publications]` placeholders
- Has `review-stage/AUTO_REVIEW.md` → extract reviewer feedback and use it to strengthen the feasibility narrative

### Phase 1: Literature & Landscape Positioning

Ground the proposal in real literature, then search for competing funded projects:

**What this does:**

- Reuse existing surveys and notes if a literature survey was already run
- Otherwise run a multi-source literature search yourself (arXiv, DBLP, Semantic Scholar, local PDFs) using the session's search/fetch tools — the plugin's `research-lit` resource may be used when installed
- Search for **funded projects** in the same area via web search:
  - KAKENHI → KAKEN database (https://kaken.nii.ac.jp/)
  - NSF → NSF Award Search (https://www.nsf.gov/awardsearch/)
  - NSFC → NSFC funded projects
  - Other agencies → general web search
- Identify competing groups and their recent publications
- Verify the gap is real before building the proposal on it: use the plugin's `novelty-check` resource when installed, or do it directly — at least 3 query formulations across at least 2 sources per core claim. Remember: "not found" does not prove novelty.
- Build the **gap statement** — the single most important sentence in the proposal:

  ```
  "Despite progress in [X], [specific gap] remains unaddressed because [reason].
  This proposal addresses this by [approach], which will [expected impact]."
  ```

**🚦 Checkpoint:** Present the landscape summary and gap statement to the user:

```
📚 Literature & landscape analysis complete:
- [key findings from literature]
- [competing funded projects found]
- Gap statement: "[the gap statement]"

Does this accurately capture the positioning? Should I adjust before designing the proposal structure?
```

**⛔ STOP HERE and wait for user response.** Do NOT auto-proceed unless AUTO_PROCEED=true was explicitly set by the user.

Options for the user:

- Reply **"go"** or **"ok"** → proceed to Phase 2 with current positioning
- Reply with **adjustments** (e.g. "focus more on X", "the gap should emphasize Y") → refine and re-present
- Reply **"stop"** → end the workflow, save current progress to `grant-proposal/DRAFT_NOTES.md`

**State**: Write `GRANT_STATE.json` with `phase: 1` and the gap statement.

### Phase 2: Narrative Structure & Aims Design

Design the proposal's logical architecture before writing any prose.

#### 2.1 Define Specific Aims (2-4)

Each aim must satisfy:

- **Independently valuable** — if one aim fails, others still produce publishable results
- **Logically connected** — Aim 1 enables Aim 2, Aim 2 informs Aim 3
- **Concrete deliverables** — each aim maps to specific outputs (papers, datasets, tools, benchmarks)
- **Feasible within budget and timeline**

#### 2.2 Build Claims-Aims-Evidence Matrix

```markdown
| Aim | Key Claim | Preliminary Evidence | Proposed Validation | Risk Level | Deliverable |
|-----|-----------|---------------------|--------------------|-----------:|-------------|
| Aim 1 | [claim] | [pilot data, prior work] | [experiments] | LOW | [paper, dataset] |
| Aim 2 | [claim] | [theoretical basis] | [experiments] | MEDIUM | [paper, tool] |
```

#### 2.3 Design the Narrative Arc

Grant proposals follow a fundamentally different arc from papers:

```
Problem → Why Now → What We Propose → Why It Will Work → What We Will Deliver
         (not: Problem → Method → Results → Implications)
```

- **Problem**: What gap exists and why it matters (scientific + societal)
- **Why Now**: What recent developments make this the right time (new data, new methods, new need)
- **What We Propose**: The specific aims and approach
- **Why It Will Work**: Preliminary data, PI track record, team expertise, feasibility arguments
- **What We Will Deliver**: Concrete outputs, timeline, expected publications

#### 2.4 Timeline & Milestones

Design a year-by-year (or quarter-by-quarter) plan:

```markdown
### Year 1
- Q1-Q2: [Aim 1 tasks]
- Q3-Q4: [Aim 1 completion + Aim 2 start]
- Expected outputs: [papers, datasets]

### Year 2
- Q1-Q2: [Aim 2 completion + Aim 3]
- Q3-Q4: [Aim 3 completion + synthesis]
- Expected outputs: [papers, tools, final report]
```

#### 2.5 Include a Risk / Mitigation Table

Every aim carries a risk level; the proposal must say what happens if it fails and how the plan adapts. Use one row per risk:

```markdown
| Risk | Likelihood | Impact | Mitigation | Fallback deliverable |
|------|-----------|--------|------------|----------------------|
| [technical risk in Aim 2] | MEDIUM | [what it blocks] | [concrete step] | [what is still publishable/deliverable] |
```

The fallback column is the one reviewers read: it must show that no single aim failure destroys the project.

#### 2.6 Structural Review

Get critical feedback on the proposal structure before drafting, using the reviewer backend as a **grant review panelist** (not a paper reviewer):

```
[GRANT_TYPE] [GRANT_SUBTYPE] proposal structure:
Gap: [gap statement]
Aims: [aims list with claims-evidence matrix]
Timeline: [timeline]
Risk table: [risks + mitigations]

Evaluate aims independence, narrative arc, risk identification, timeline realism.
Identify the single biggest reviewer concern.
Provide actionable fixes ranked by severity.
```

Apply structural feedback before proceeding to drafting. If no reviewer backend is available, run the same prompt as a labeled self-review and record `REVIEW_UNAVAILABLE`.

**🚦 Checkpoint:** Present the proposal structure to the user:

```
🏗️ Proposal structure designed:
- Gap: [gap statement]
- Aim 1: [title] — Risk: LOW
- Aim 2: [title] — Risk: MEDIUM
- Aim 3: [title] — Risk: LOW
- Timeline: [summary]
- Reviewer feedback: [key points]

Proceed to section drafting? Or adjust the structure?
```

**⛔ STOP HERE. This is the most critical checkpoint — the proposal structure determines everything downstream.**

Options for the user:

- Reply **"go"** or **"ok"** → proceed to Phase 3 (section drafting)
- Reply with **structural changes** (e.g. "merge Aim 2 and 3", "add an aim about X", "reduce to 2 aims") → redesign and re-present
- Reply **"back"** → return to Phase 1 to adjust the gap/positioning
- Reply **"stop"** → save the current structure to `grant-proposal/DRAFT_NOTES.md`

**State**: Write `GRANT_STATE.json` with `phase: 2`, aims summary, and the reviewer thread id.

### Phase 3: Section Drafting

Draft each section according to the grant type template. Write **complete prose**, not outlines or placeholders.

**What this does:**

- Writes all required sections in the agency-specific language and tone
- Pulls content from the Phase 0 context files and literature notes
- Generates figures (see below)
- Leaves `[TODO]` only for PI-specific information, `[AMOUNT]` for budget figures
- Outputs `grant-proposal/GRANT_PROPOSAL.md`

#### Drafting Order (optimized for narrative coherence)

1. **Specific Aims / Research Objective** — the "abstract" of the grant. Write first, refine last.
2. **Background / Significance / State of the Art** — establish the problem and gap.
3. **Research Plan / Methods** — per aim, with feasibility arguments.
4. **Figures** — generate key diagrams (see below).
5. **Timeline & Milestones** — year-by-year deliverables.
6. **PI Qualification / Preparation Status** — track record, team, infrastructure.
7. **Budget Justification** — narrative only (leave amounts as `[AMOUNT]` placeholders).
8. **Broader Impacts / Societal Significance** — if required by the grant type.

#### Figure Generation

Grant proposals benefit greatly from clear diagrams. Generate the following (save to `grant-proposal/figures/`):

1. **全体構成図 / Overview Diagram** — the relationship between aims (Aim 1 → Aim 2 → Aim 3), shared resources (participants, stimuli, pipeline), and outputs. This is the single most important figure.
2. **実験パラダイム図 / Experimental Paradigm** — schematic of each paradigm (stimulus timing, conditions, recording setup).
3. **年次計画 / Timeline Gantt Chart** — year-by-year (or H1/H2) milestones with deliverables.

Produce these natively: SVGs or matplotlib scripts for the Gantt/paradigm figures, and the plugin's `figure-spec` resource (`${CLAUDE_PLUGIN_ROOT}/resources/figures/figure-spec/SKILL.md`) for structured block diagrams — it renders a FigureSpec JSON to deterministic, editable SVG. Vector output, colour-blind-safe palettes, no chartjunk, every number readable at print size; keep the generation script next to the figure for reproducibility.

**🚦 Figure Checkpoint:** Before generating, ask which figures the user wants:

```
🎨 The following figures would strengthen this proposal:
1. 全体構成図 / Overview — aims relationship + shared resources
2. 実験パラダイム図 / Paradigm — stimulus timing + conditions
3. 年次計画 / Gantt — timeline with milestones

Which should I generate? (e.g., "1 and 3", "all", "skip")
```

**⛔ Wait for user response.** Generate only the requested figures.

#### Grant-Specific Drafting Guidelines

**KAKENHI:**

- Write in formal Japanese academic style (である調, not です/ます調)
- Use 「」for Japanese quotations, bold for emphasis
- Structure: 研究の学術的背景 → 研究期間内に何をどこまで明らかにするか → 本研究の学術的な特色・独創性
- Include explicit 年次計画 (yearly plan) with concrete milestones
- Emphasize 社会的意義 (societal significance)
- Reference related KAKEN-funded projects to show awareness of the field

**NSF:**

- Write in clear, direct English
- Use Aim-based structure with bold headings
- Preliminary data paragraphs for each Aim (with figure references)
- Broader Impacts must be concrete: specific outreach activities, broadening participation plans
- Include Results from Prior Support (if the PI has prior NSF funding)

**NSFC:**

- Write in formal Chinese academic style
- 立项依据 must position the work at 国际前沿 (international frontier)
- 创新性 section must list numbered innovation points (创新点)
- 研究基础 must cite the PI's own publications (with IF and citations if possible)
- 可行性分析 must address: technical feasibility, team capability, time feasibility, equipment/conditions

**ERC:**

- Write a compelling "high-risk/high-gain" narrative
- Extended Synopsis must be self-contained and compelling
- Include a Work Package table with deliverables and milestones
- Gantt chart (describe in text, or generate as a figure)

#### For Each Section

1. **Pull relevant content** from the Phase 0 context files and literature notes
2. **Write complete prose** — no `[TODO]` except for PI-specific information
3. **Include figure/table placeholders** where appropriate (e.g. `[Figure 1: System architecture]`)
4. **Cite references properly** — use citation keys; build the bibliography from verified metadata only
5. **Match the agency's tone and style** — formal Japanese for KAKENHI, direct English for NSF, etc.

#### Citations in a Grant

- Never fabricate a citation. Verify via DBLP first, then CrossRef (`https://doi.org/{doi}` with `Accept: application/x-bibtex`); keep `[VERIFY]` on anything unresolved. The full protocol is in `${CLAUDE_PLUGIN_ROOT}/resources/writing/citation-audit/references/citation-discipline.md`.
- A grant cites *future* work and *feasibility* evidence: prior work of the applicant, pilot results, competing funded projects. Do not present preliminary data as completed results.

### Phase 4: External Review

Run a grant-type-specific evaluation of the complete draft with the reviewer backend acting as a review panelist. Keep the panel prompt short and point the reviewer at files it can read; if the backend cannot read files, paste the draft instead.

**Bundle/prompt contents:**

```
Review this complete [GRANT_TYPE] [GRANT_SUBTYPE] proposal draft.

Act as a [GRANT_TYPE] review panelist. Evaluate using the official criteria:

[INSERT GRANT-TYPE-SPECIFIC CRITERIA — see Grant Type Specifications above]

For each section:
1. Score 1-5 (5 = excellent)
2. Strongest aspect
3. Most critical weakness
4. Specific fix suggestion (actionable, not vague)

Overall assessment:
- Would you recommend funding? (Yes / Yes with revisions / No)
- Single most impactful change to improve funding chances?
- Any fatal flaws?

Proposal draft path (read this file yourself): <absolute path to
grant-proposal/GRANT_PROPOSAL.md>
```

**Round 2+ (after revisions):** if MAX_REVIEW_ROUNDS > 1 and revisions were applied, re-review with the same reviewer thread/session when the backend supports it, and include the change log:

```
[Round N review of revised [GRANT_TYPE] [GRANT_SUBTYPE] proposal]

Since your last review, I have applied the following changes:
1. [Change 1]: [what was done]
2. [Change 2]: [what was done]
3. [Change 3]: [what was done]

Please re-evaluate. Same format: section scores, overall assessment, remaining weaknesses.
Focus on whether the CRITICAL and MAJOR issues from Round 1 have been adequately addressed.

Revised proposal path (read this file yourself): <absolute path to
grant-proposal/GRANT_PROPOSAL.md>
```

All feedback is saved to `grant-proposal/GRANT_REVIEW.md`.

> ⚠️ **Reviewer-backend fallback**: if no cross-model reviewer backend is available, skip external review and note in `GRANT_REVIEW.md`: "External review skipped — no cross-model reviewer backend available; a labeled same-model review may be run separately." The proposal is still usable without external review, and its review status must be reported honestly rather than implied.

### Phase 5: Revision & Output

#### 5.1 Apply Reviewer Feedback

Parse reviewer feedback into severity levels:

- **CRITICAL** — fatal flaws that would lead to rejection. Fix immediately.
- **MAJOR** — significant weaknesses. Fix before submission.
- **MINOR** — suggestions for improvement. Fix if time allows.

Implement CRITICAL and MAJOR fixes. If MAX_REVIEW_ROUNDS > 1, re-submit for another round.

#### 5.2 Generate Output

**Markdown output** (default):

```
grant-proposal/
├── GRANT_PROPOSAL.md          # Complete proposal, all sections
├── GRANT_REVIEW.md            # Review history and reviewer feedback
├── GRANT_STATE.json           # State persistence file
├── figures/                   # Generated diagrams (if any)
└── references.bib             # Bibliography (if citations were used)
```

**LaTeX output** (when OUTPUT_FORMAT = latex):

```
grant-proposal/
├── main.tex                   # Master file
├── sections/
│   ├── aims.tex               # Specific Aims / Research Objective
│   ├── background.tex         # Background / Significance
│   ├── research_plan.tex      # Research Plan / Methods
│   ├── timeline.tex           # Timeline & Milestones
│   ├── pi_qualification.tex   # PI Qualification / Track Record
│   └── budget.tex             # Budget Justification (if applicable)
├── references.bib
└── figures/                   # Any generated diagrams
```

Build the LaTeX output locally with `latexmk -pdf -interaction=nonstopmode main.tex` and check for undefined citations/references. If no TeX toolchain is available, say the PDF was not built and report the static-check results instead of implying a compiled document.

#### 5.3 Final Checks

Before declaring done:

- [ ] All sections required by the grant type are present and complete
- [ ] Gap statement is clear and appears early in the proposal
- [ ] Each aim is independently valuable and logically connected
- [ ] Timeline includes concrete yearly milestones and deliverables
- [ ] Risk/mitigation table present, with a fallback deliverable per risk
- [ ] PI qualification section has content (or clear `[TODO]` placeholders)
- [ ] Budget justification uses `[AMOUNT]` placeholders (no fabricated numbers)
- [ ] Language matches the grant type (Japanese for KAKENHI, Chinese for NSFC, etc.)
- [ ] No leftover `[TODO]` markers except for PI-specific information
- [ ] References are real (no hallucinated citations; unresolved ones marked `[VERIFY]`)
- [ ] Review feedback has been addressed (CRITICAL and MAJOR items), or the review status is explicitly reported as unavailable
- [ ] Live agency call-for-proposals checked against the section list and page limits used

**🚦 Final Checkpoint:** Present the completed proposal summary:

```
📝 Grant proposal draft complete:
- Type: [GRANT_TYPE] [GRANT_SUBTYPE]
- Language: [language]
- Aims: [N] aims covering [summary]
- Timeline: [N] years
- Review: [summary, or "external review unavailable"]
- Output: grant-proposal/GRANT_PROPOSAL.md

Files saved to grant-proposal/. Please review and customize:
1. PI qualification section (add your publications and track record)
2. Budget amounts (replace [AMOUNT] placeholders)
3. Any [TODO] markers for personal information

What would you like to do next?
- "figures" → generate proposal diagrams
- "review again" → run another round of external review
- "latex" → convert to LaTeX format
- "done" → finalize
```

## Output Protocols

For every output file produced here:

- **Versioning** — write the timestamped file first (`{NAME}_{YYYYMMDD_HHmmss}.md`, seconds precision), then copy the same content to the fixed name. Downstream readers always read the fixed name. Never delete timestamped files.
- **Manifest** — maintain `MANIFEST.md` in the project root only when a run produces more than 15 artifacts; below that threshold a manifest is duplicate bookkeeping. Append one row per output (timestamp | skill | file | stage | description).
- **Language** — follow the project's language setting for commentary and boilerplate, matching the grant type (see LANGUAGE). Do not localize code, paths, names, BibTeX entries, or JSON keys. Machine-parsed markers stay English.

## Key Rules

- **Do NOT fabricate budget amounts.** Generate narrative budget justification only. Leave specific dollar/yen/yuan/euro amounts as `[AMOUNT]` placeholders for the user to fill in.
- **Do NOT fabricate PI information.** If no publication list is available, leave `[TODO: Add publications]` placeholders. Never invent papers, grants, or credentials.
- **Do NOT hallucinate citations.** Use verified metadata (DBLP → CrossRef); mark uncertain citations with `[VERIFY]`.
- **Grant ≠ paper.** A grant argues for future work (feasibility + potential). A paper argues for completed work (results + claims). Write accordingly — emphasize "what we will do" and "why it will work", not "what we found."
- **Aims must be independently valuable.** If Aim 2 fails, Aim 1 and Aim 3 should still produce publishable results.
- **Preliminary data de-risks.** Include any pilot results, existing datasets, or prior publications that demonstrate feasibility.
- **Reviewer-facing structure.** Bold key sentences. Use numbered lists for clarity. Make the reviewer's job easy.
- **Cultural norms matter.** KAKENHI expects 社会的意義; NSF expects Broader Impacts; NSFC expects 国际前沿 positioning. Missing these is a red flag for reviewers.
- **Large file handling**: if a write fails because of file size, retry with a chunked shell write (`cat << 'EOF' > file`) rather than asking the user.
- **Checkpoints are mandatory** unless AUTO_PROCEED was explicitly set — a grant proposal needs PI judgment at the gap statement and at the structure.

## Parameter Pass-Through

Parameters are passed inline with a `—` separator:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `grant type` | KAKENHI | Agency (KAKENHI/NSF/NSFC/ERC/DFG/SNSF/ARC/NWO/GENERIC) |
| `grant subtype` | auto | Sub-type (Start-up/Wakate/CAREER/Youth/etc.) |
| `output format` | markdown | `markdown` or `latex` |
| `language` | auto | Output language override |
| `max review rounds` | 2 | External review cycles |
| `sources` | all | Literature sources for the Phase 1 survey |
| `arxiv download` | false | Download arXiv PDFs during the survey |
| `reviewer model` | backend default | Reviewer model |
| `auto proceed` | false | Skip checkpoints |

## Composing with Other Resources

| Resource | Phase | Purpose |
|-----------|:-----:|---------|
| `research-lit` (if installed) | 1 | Literature survey; otherwise run the multi-source search directly |
| `novelty-check` (if installed) | 1 | Verify the gap is real; otherwise verify directly with ≥3 query formulations |
| reviewer backend | 2, 4 | Structural review + full draft panel review |
| `figure-spec` | 3 | Structured diagrams (overview, cascade) as editable SVG |
| `paper-figure` | 3 | Data plots and tables if the proposal includes preliminary results |

**Funding track (this resource's primary use case):**

```
idea discovery → refine the method → grant-proposal → [submit & get funded]
                                    → implement experiments → review loop → write the paper
```

**Publish track (skip this resource):**

```
idea discovery → implement → review loop → paper writing → submit
```

Out of scope here: rebuttal writing, slide/poster generation, automated improvement loops, Overleaf sync.

## Acknowledgements

Agency-structure guidance and the "grant is not a paper" framing follow common research-office practice across JSPS, NSF, NSFC, ERC, DFG, SNSF, ARC, and NWO calls; verify every structural detail against the live call-for-proposals.

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/grant-proposal/SKILL.md (MIT). See registry/components.json. -->
