---
name: write
description: "Use when the user asks to write or edit a paper, grant proposal, or technical document from evidence they provide. Evidence-gated drafting: no invented results, citations, or numbers; missing parts are marked, not filled. Polish preserves meaning only."
---

# minh-agent:write — papers, grants, technical writing

**Contract:** write or edit from the user's evidence, for the stated audience and venue.
Never fabricate results, citations, numbers, or experiment settings. Missing pieces are
marked as missing — never filled in to make the draft look complete.

## 1. Determine what is being written

- **Paper** → read `${CLAUDE_PLUGIN_ROOT}/resources/writing/paper-plan/SKILL.md` (structure,
  venue checklists) and `${CLAUDE_PLUGIN_ROOT}/resources/writing/paper-write/SKILL.md`
  (evidence-gated drafting).
- **ML paper** → additionally `${CLAUDE_PLUGIN_ROOT}/resources/writing/ml-paper-writing/SKILL.md`.
- **Grant proposal** → `${CLAUDE_PLUGIN_ROOT}/resources/grants/grant-proposal/SKILL.md`.
  A grant is NOT a paper: it argues future work (feasibility, impact, risk management).
  Budget amounts and PI credentials are placeholders (`[AMOUNT]`, `[PI INFO]`) — never
  fabricated. Agency structure (KAKENHI / NSF / NSFC / ERC / DFG / SNSF / ARC / NWO) and a
  risk/mitigation table are required.

## 2. Evidence discipline

- Before any claim enters prose: read
  `${CLAUDE_PLUGIN_ROOT}/resources/experiments/result-to-claim/SKILL.md` and map each claim to
  a raw result (result-to-claim). Drafting evidence hierarchy L0–L4; zero bracketed
  placeholders; concrete details the user did not provide are not written.
- Citations: fetched and verified (DBLP → CrossRef → `[VERIFY]`); never BibTeX from memory;
  never cite a paper whose support for the sentence you haven't checked.
- Write order: Results → Intro/Conclusion → Title → Discussion → Methods → Abstract.

## 3. Editing and polish

- Meaning-preserving only; prefer the small edit over the big one, and no edit over the small
  one. Sentences ≤ 30 words; hedge-ladder calibration; no overclaim vocabulary (prove,
  conclusively, unprecedented, best, superior, first — soften or remove).
- Polishing an AI-written draft moves only in the direction of the source text: never add a
  fact, name, number, date, quote, or citation that is not in the source or from the user.

## 4. Pre-submission checks (papers)

paper-claim-audit (numbers vs raw results) → citation-audit
(`${CLAUDE_PLUGIN_ROOT}/resources/writing/paper-claim-audit/SKILL.md`,
`${CLAUDE_PLUGIN_ROOT}/resources/writing/citation-audit/SKILL.md`) → reviewer simulation
(labeled: fresh-context / self-review / cross-model only if a real second backend ran —
otherwise `REVIEW_UNAVAILABLE`) → integrity self-check.

## 5. Output contract

1. The document (or the edited diff of it).
2. Which parts are backed by which evidence, and which parts are marked missing/unverified.
3. What was checked pre-submission and with what result.
4. Limits: no claim of venue compliance without verifying the current CFP/page limits.
