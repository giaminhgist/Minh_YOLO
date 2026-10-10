---
name: research
description: "Use when the user asks a research question needing literature — find sources, synthesize with traceability, check novelty, or develop an idea. Real sources only, facts separated from inference, no fabricated citations. Does NOT run experiments or write papers by default."
---

# minh-agent:research — literature and synthesis

**Contract:** a sourced synthesis of the literature for the user's question — with every
important conclusion traceable to a real, accessible source. Facts, inferences, and gaps are
labeled separately. This entry does NOT by default propose ideas, run experiments, or write
papers; those happen only when the user asks.

## 1. Load the workflow

Read `${CLAUDE_PLUGIN_ROOT}/resources/research/research-lit/SKILL.md` and follow its
retrieval → verification → synthesis → anti-hallucination flow. The bundled source connectors
are:
- `${CLAUDE_PLUGIN_ROOT}/resources/research/arxiv/SKILL.md`
- `${CLAUDE_PLUGIN_ROOT}/resources/research/semantic-scholar/SKILL.md`
- OpenAlex (documented free REST API) and arXiv API as native fallbacks.

## 2. Source discipline (non-negotiable)

- Prefer deterministic keyless sources: arXiv, Semantic Scholar, PubMed E-utilities, OpenAlex,
  Crossref. API-key services only when the user has them configured.
- Every hit is verified against the source before it enters the synthesis — never trust a
  search result's title/abstract blindly, never cite from memory.
- Citations: fetch and verify (DBLP → CrossRef → `[VERIFY]`). BibTeX is generated from fetched
  records, never from memory.
- Network blocked or a source unreachable? Report the blocker and deliver the local-document
  branch honestly — do not fabricate sources to fill the gap.

## 3. Output contract

1. The question as understood, and the scope/time-box used (30-minute tool-exploration cap
   per episode; then report and ask).
2. Synthesis with each important conclusion carrying its source (with URL/ID and the
   supporting quote or record). Distinguish: **fact from source** / **reasoned inference** /
   **gap (no source found)**.
3. Confidence labels per conclusion — no fake numerical precision.
4. Blockers: unreachable sources, paywalled papers, search limits.
5. If the user asked about novelty: additionally read
   `${CLAUDE_PLUGIN_ROOT}/resources/ideas/novelty-check/SKILL.md` — multiple query formulations
   (≥3 per core claim), multiple sources; "not found" does not prove novelty, and an ABANDON
   verdict must name the colliding paper.
6. If the user asked for ideas: `${CLAUDE_PLUGIN_ROOT}/resources/ideas/idea-creator/SKILL.md`
   (+ `research-refine`). Cross-model verdict gates report `REVIEW_UNAVAILABLE` honestly when
   no second backend exists.

## 4. Boundaries

- "Research this" ≠ "run experiments on it" and ≠ "write a paper about it" (STANDALONE mode).
  Only when the user explicitly asks do you hand off to `experiment` or `write`.
