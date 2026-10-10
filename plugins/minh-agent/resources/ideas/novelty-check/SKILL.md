# Novelty Check

When this resource is used: loaded by minh-agent idea-stage workflows (and directly through the `research` entry) when the user asks "is this novel", "has anyone done this", "查新", "novelty check", or wants a proposed method verified against recent literature before implementation.

Check whether a proposed method/idea has already been done in the literature: the user's method or idea description.

## Constants

- **REVIEWER_MODEL** — the cross-model reviewer used for the independent verdict. It must be a **non-Claude** model reachable through a backend the user has actually configured (e.g. a Codex-style MCP endpoint at xhigh reasoning, or an equivalent OpenAI/Google/DeepSeek/Qwen endpoint). The executor is Claude, so a review pasted into any Claude product cannot acquit (same-family review). If no such backend is available, see Phase C fallback — never fake independence.

## Instructions

Given a method description, systematically verify its novelty:

### Phase A: Extract Key Claims
1. Read the user's method description
2. Identify 3-5 core technical claims that carry the claimed delta:
   - What is the method?
   - What problem does it solve?
   - What is the mechanism?
   - What makes it different from obvious baselines?

### Phase B: Multi-Source Literature Search
For EACH core claim, search using ALL available sources:

1. **Web Search** (via `WebSearch`):
   - Search arXiv, Google Scholar, Semantic Scholar
   - Use specific technical terms from the claim
   - Try at least 3 different query formulations per claim
   - Include year filters for the recent 2 years
2. **Native API searches** when available: the arXiv API and Semantic Scholar Graph API procedures in `${CLAUDE_PLUGIN_ROOT}/resources/research/arxiv/SKILL.md` and `${CLAUDE_PLUGIN_ROOT}/resources/research/semantic-scholar/SKILL.md` (stdlib Python, no key required).
3. **Known paper databases**: Check against the current top-venue proceedings (ICLR/NeurIPS/ICML) and recent arXiv preprints from the last 6 months — the field moves fast.
4. **Read abstracts**: For each potentially overlapping paper, fetch its abstract and related-work section.

### Phase C: Cross-Model Verification

**Backend availability gate (honest check, no faking).**

1. Probe whether a non-Claude reviewer backend is actually available (e.g. a Codex-style MCP tool responds). 
2. **If available**: send the review with xhigh reasoning to that backend. When the method description plus the Phase-B paper list is more than a short note, avoid pasting it inline; write a dossier file such as `NOVELTY_DOSSIER.md` (or a project-local equivalent) containing the method description, core claims, candidate papers, the exact questions below, and the NOVELTY VERDICT LIMITS block verbatim — then send only the file path.
3. **If not available**: output `REVIEW_UNAVAILABLE` in the report, state plainly that the novelty verdict was produced by a single model (Claude, self-review) plus deterministic checks, and continue with that explicitly-labeled self-review. Do not describe it as independent or cross-model, and do not skip the search work.

Questions for the reviewer (or the labeled self-review): "Is this method novel? What is the closest prior work? What is the delta?"

### The verdict limits

Copy this block **verbatim** into the reviewer's briefing; the report in Phase D is judged under it too.

```
=== NOVELTY VERDICT LIMITS (these bound how you judge, never how widely you search) ===
Search exhaustively; judge calibrated. Two failures waste months equally:
passing an idea a published paper already contains, and killing a viable idea
because the territory has neighbors.
1. Proximity is information, not a verdict. Someone working nearby goes in the
   report; it is not by itself a reason to reject.
2. ABANDON has exactly one qualification: a specific published paper already
   contains this result — name that paper. No named paper, no ABANDON.
3. Crowded-but-deltaed is PROCEED: state the delta in one sentence a reviewer
   could verify. Thin or contested delta is PROCEED WITH CAUTION — say what
   would make it carry, not why it should die. CAUTION is not a safe middle:
   if you cannot name the specific thing that makes the delta thin, the
   verdict is PROCEED.
4. Concurrent or competing work is not a veto. That is a race — report it and
   let the user decide whether to run it.
5. A direct attack on a central problem is legitimate novelty when nobody has
   executed it well. "This area is hot" does not mean "this area is taken."
6. This check is an early gate, never the last one — more triage, pilots, or
   external review still stand between any idea and a paper, whatever order
   this run uses. A wrongly passed idea dies cheaply at one of them; a wrongly
   killed idea is never seen again. When torn between two verdicts, choose the
   more permissive one.
Say plainly when an idea clears the check. Do not manufacture overlap.
```

### Phase D: Novelty Report
Output a structured report:

```markdown
## Novelty Check Report

### Proposed Method
[1-2 sentence description]

### Review Status
[Cross-model review via <backend/model> | REVIEW_UNAVAILABLE — single-model
(Claude) self-review with deterministic paper verification only]

### Core Claims
1. [Claim 1] — Closest: [paper] — What stays unknown or different: [delta]
2. [Claim 2] — Closest: [paper] — What stays unknown or different: [delta]
...

### Closest Prior Work
| Paper | Year | Venue | Overlap | Key Difference | Status |
|-------|------|-------|---------|----------------|--------|
| ...   | ...  | ...   | ...     | ...            | ✅ verified / ⚠️ UNVERIFIED |

### Overall Novelty Assessment
- Score: X/10 (anchor: 5/10 = has clear neighbors but a defensible delta worth
  a pilot; reserve 1-3 for results a named published paper already contains)
- Recommendation: PROCEED / PROCEED WITH CAUTION / ABANDON (per the verdict
  limits: crowded-but-deltaed ground is PROCEED; ABANDON must name the paper)
- Key differentiator: [what makes this unique, if anything]
- Risk: [what a reviewer would cite as prior work]

### Suggested Positioning
[State the delta honestly in one sentence a reviewer could verify]
```

### Important Rules
- Two failures waste months equally: a false novelty claim, and a viable idea abandoned because the territory has neighbors. Be brutally honest in both directions — and when an idea clears the check, say so plainly.
- Novelty can live in the combination or the finding even when every individual claim rates LOW — judge the idea, not each claim in isolation. Known parts arranged to reveal something unknown are novel.
- "Applying X to Y" earns novelty by what the application reveals — a non-obvious interaction, failure mode, or insight. Judge the revelation, not the template.
- Check both the method AND the experimental setting for novelty
- If the method is not novel but the FINDING would be, say so explicitly
- Always check the most recent 6 months of arXiv — the field moves fast
- **Anti-hallucination for Closest Prior Work.** Every paper in the prior-work table must pass pre-search verification using the 3-layer procedure (arXiv batch → CrossRef DOI → Semantic Scholar fuzzy title) documented in `${CLAUDE_PLUGIN_ROOT}/resources/research/research-lit/SKILL.md` (Step 1.5). If the procedure cannot run (no python3, no network), tag the entries `[UNVERIFIED]` and surface the uncertainty rather than dropping them. Never fabricate arXiv IDs, DOIs, or titles from memory.

## Review Tracing

After each reviewer call, save a trace: the full prompt (or bundle path) and the full raw response verbatim to a project-local traces directory (e.g. `novelty-check-traces/<date>_run<NN>/`) — forensic record, never silently skipped. If the reviewer backend was unavailable, record the unavailability and the labeled self-review instead.

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/novelty-check/SKILL.md (MIT). See registry/components.json. -->
