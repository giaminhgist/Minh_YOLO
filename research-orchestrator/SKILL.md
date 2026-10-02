---
name: research-orchestrator
description: Task classifier, skill router, and workflow orchestrator for AI/DL/CV/biomedical research. Routes every research task to the correct upstream skill (see SKILL_INDEX.md), controls execution mode (Standalone by default vs Loop/Workflow on explicit request), and enforces context, tool, and verification discipline. Read SKILL_INDEX.md before routing any task.
---

# Research Orchestrator

This orchestrator does NOT copy upstream skills. It classifies requests, routes to the right upstream skill via `SKILL_INDEX.md` (same directory), and controls how the work runs. Upstream repos live under `~/.claude/upstream/` and are immutable — read them, never edit them; update via `git pull` + sync script (see `INSTALL.md` in this directory).

## 1. Task classifier

Classify the user's request FIRST, before doing anything else:

1. Is this a **research task** (idea / literature / novelty / experiment / analysis / paper / grant / figure)? → route via §2 and the index.
2. Is this a **coding task** (implement / review / optimize / debug)? → route via §2; use research coding skills, not generic ones, when the code is part of experiments.
3. Is this a **meta task** (prompt / context / token / tool optimization, filtering, verification of my own work)? → apply §5–§7 and the cross-cutting skills.
4. Is this **ambiguous**? → ask ONE focused clarifying question (use AskUserQuestion) before routing. Do not silently pick an interpretation.

Classification determines the mode (§3) and the minimum skill set (§4).

## 2. Skill router

Routing rules (mandatory, in order):

1. **Look up the task category in `SKILL_INDEX.md` Part 1.** Read the matched skill's SKILL.md before executing it — never route by name alone.
2. **Priority order**: `domain-specific` > `research-specific` > `specialized coding/research` > `generic`.
   - Example: training NaN/divergence → `~/.claude/skills/aris-training-check/SKILL.md` (ML-domain) before `sp-systematic-debugging` (generic).
   - Example: figure for a paper → `ns-nature-figure` (domain: Nature-standard) over a generic plotting path.
3. **One PRIMARY per capability cluster** (see SKILL_INDEX Part 2). Do not load multiple overlapping skills "just in case". Add a SECONDARY only when the PRIMARY is unavailable; add COMPLEMENTARY only when it adds clearly distinct value.
4. **FALLBACK and SPECIAL-CASE skills** are never default-routed; state the reason when routing to them.
5. **Upstream skill prerequisites**: many ARIS skills embed cross-model review (Codex MCP, floor `xhigh`). If the reviewer backend is missing, degrade per the upstream skill's own policy (usually `REVIEW_UNAVAILABLE`) — never fake cross-model independence, never run a verdict-bearing skill on a timer/`/loop`/CronCreate wrapper.
6. **Unavailable upstream skill**: say so and pick the next-best route from the index; never improvise a weaker copy silently.

## 3. Mode controller

### 3.1 STANDALONE MODE — DEFAULT

A specific request executes THAT task and only the minimum supporting skills needed to do and verify it. Mandatory rules:

- Execute only the requested task.
- Do NOT automatically invoke upstream or downstream workflow stages.
- Supporting optimization skills (context, token, tool selection) must never expand the task's scope.

| Request | Run | Do NOT run |
|---|---|---|
| "Debug this code" | systematic-debugging → root cause → fix → verification | idea discovery, novelty, experiment planning, paper writing |
| "Check novelty of this idea" | novelty-check only | experiment plan, code, paper |
| "Write code for this model" | code plan (only if complex) → code writing → code review / verification | literature search, novelty check, research proposal |
| "Analyze these results" | analyze-results (+ statistical-analyst if formal tests needed) | full paper pipeline |
| "Review this paper" | pre-submission-reviewer / review-paper | new experiments, rewriting |
| "Make Figure 2" | nature-figure (or paper-figure for ML plots) | paper rewrite, novelty check |

### 3.2 LOOP / WORKFLOW MODE — only on explicit request

Activate ONLY when the user explicitly asks, e.g.: "run the full research loop", "full workflow", "develop this idea into a study", "continue the research pipeline", "develop this into a paper", "run end-to-end research workflow".

Research loop (stage-by-stage, evidence-gated):

Idea Discovery → Idea Proposal/Refinement → Literature Review → Novelty Check → Hypothesis Definition → Experiment Plan → Code Plan → Code Writing → Code Review → Experiment Execution → Result Analysis → Debug/Refine → Re-run → Ablation/Robustness → Statistical Analysis → Paper Writing → Figure Creation → Citation Check → Reviewer Simulation → Revision → Final Verification

- Each stage loads its skills progressively (§4), not all at once.
- A stage is complete only when its evidence artifacts exist (§7).
- **Return edges are allowed and required when evidence demands them**: Experiment ↔ Debugging ↔ Code Optimization ↔ Experiment Refinement. A negative result that invalidates the hypothesis returns to Idea Refinement; a reviewer concern about missing ablations returns to Experiment Plan. Never paper over a failed stage to "move forward".

For an autonomous end-to-end run, `aris-research-pipeline` (W1→W1.5→W2→W3) is the canonical upstream engine; `or-autoresearch` is the alternative two-loop engine. Both require a loop-capable host and GPU/API budgets — state the cost expectation before starting.

### 3.3 GRANT branch (separate workflow — never mixed with the paper loop)

Idea → Literature/Gap → Preliminary Evidence → Research Objectives → Work Packages → Methodology → Risk/Mitigation → Budget/Resources → Impact → Grant Writing → Grant Review → Revision

- Route to `aris-grant-proposal`; add `arf-review-grant` for the review stage and `cs-grants` for NIH-oriented searches.
- **A grant is not a paper.** It argues future work (feasibility + expected impact + risk management). Budget numbers and PI credentials are placeholders — never fabricated.

### 3.4 PUBLICATION track

Results → Claim–Evidence Map → Paper Outline → Introduction/Related Work → Methodology → Experiments → Results → Discussion → Figures/Tables → Citation Verification → Reviewer Simulation → Revision → Final Integrity Check

- Drafting discipline: `ss-paper-writer` evidence rules (L0–L4) + `or-ml-paper-writing` for ML venues + `aris-paper-writing` pipeline for end-to-end.
- **Never fabricate**: results, citations, metrics, statistical claims, experiment settings. The citation workflow is always DBLP → CrossRef → [VERIFY]; never BibTeX from memory.
- Pre-submission: `aris-paper-claim-audit` → `aris-citation-audit` → `ss-pre-submission-reviewer` (or `aris-auto-review-loop` when a cross-model reviewer is configured) → `aris-integrity-forensics` for high-stakes submissions.

## 4. Progressive skill loading

Default flow: Understand request → Classify task → Search SKILL_INDEX → Select minimum sufficient skills → Read selected SKILL.md → Execute → Load additional skill only if necessary → Verify.

Active skill budget (target, not a hard cap):

- Simple task: 0–2 skills
- Normal task: 1–4 skills
- Complex research task: progressively load stage-by-stage

Never preload the full skill catalog. Never load two skills that fill the same role.

## 5. Context controller

Treat context as a limited attention budget. Classify information:

- **CRITICAL** — current objective, user constraints, important decisions, current experiment settings, current task list, relevant file paths, verified findings, active blockers. Keep in active context.
- **SUPPORTING** — useful but not required immediately. Compress to a compact note; expand only when the task touches it.
- **ARCHIVAL** — possibly useful later. Move to files (`research-wiki/`, experiment logs, `.inspection/`) and reference by path.
- **IRRELEVANT** — drop.

Compaction triggers: context > ~70–80% of the window, or when a stage finishes. Never prune anything whose loss could change scientific interpretation, code behavior, experiment reproducibility, or user intent. Never compress tool definitions. (For the full machinery, `ctx-context-fundamentals` / `ctx-context-compression` / `ctx-context-optimization`.)

For long tasks, maintain a compact state representation and re-emit it at stage boundaries:

```
Goal | Current task | Completed | Important decisions | Relevant files | Experiment config | Blockers | Next action
```

## 6. Tool controller

- Select the minimum sufficient tools for the task. No popularity-based choices ("Do not recommend a tool based on popularity alone").
- Verification claims require verification tools (fresh command output, VCS diff, test run) — a model's own assertion is not evidence.
- Research search: prefer deterministic, keyless sources first (arXiv, Semantic Scholar, PubMed E-utilities, OpenAlex, Crossref); API-key sources (Exa, Gemini, Stipple) only when configured and only with the user's awareness (Stipple uploads documents to a third party — obtain approval first).
- Research tooling time-box: 30 minutes per tool-exploration episode; then report and ask.
- Never expose secrets in commands or artifacts.

## 7. Verification controller

- **Nothing is "done" because code was written or text was drafted.** Completion requires verification appropriate to the task:
  - Code: fresh run output / tests / diff review.
  - Experiments: result files exist and parse; numbers match logs (`arf-audit-analysis` discipline: file+line+quote, CONFIRMED/SUSPECTED).
  - Claims: evidence exists in raw results (`aris-result-to-claim` before any claim enters prose).
  - Paper: compiled PDF; numbers audited (`aris-paper-claim-audit`); bibliography audited (`aris-citation-audit`).
  - Review/verdict: independent reviewer, not self-assessment ("Never adjudicate your own verification").
  - Task loop: visible checklist (§8) — no silent completion of multiple major tasks.
- Distinguish: **observation** (what the data show) vs **interpretation** (what that means) vs **hypothesis** vs **claim** (what we assert in writing). Claims must trace to experimental evidence, a figure/table, a citation, or a mathematical argument.
- Never report an error or an exhausted budget as success.

## 8. Visible task list (global requirement)

For every non-trivial multi-step task, maintain a checklist IN the conversation:

```
Tasks
- [x] completed
- [>] current
- [ ] pending
- [!] blocked
```

Create it before a large task; mark the current task `[>]`; after each major task: mark `[x]`, record the verification performed, promote the next task. Trivial tasks (rename a variable, explain a function, fix a typo, simple factual question) need no checklist.
