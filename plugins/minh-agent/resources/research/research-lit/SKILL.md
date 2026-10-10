# Research Literature Review

When this resource is used: loaded by the minh-agent `research` entry (and by any minh-agent workflow that needs a literature landscape) when the user asks for "find papers", "related work", "literature review", "what does this paper say", or otherwise needs multi-source paper search and synthesis.

Research topic: the user's topic, paper list, or URL.

## Constants

- **PAPER_LIBRARY** — Local directory containing the user's paper collection (PDFs). Check these paths in order:
  1. `papers/` in the current project directory
  2. `literature/` in the current project directory
  3. Custom path specified by the user in the project instructions under `## Paper Library`
- **MAX_LOCAL_PAPERS = 20** — Maximum number of local PDFs to scan (read first 3 pages each). If more are found, prioritize by filename relevance to the topic.
- **SOURCES = `all`** — Which literature sources to search. Options: `zotero`, `obsidian`, `local`, `web`, `arxiv`, `semantic-scholar`, `openalex`, `deepxiv`, `exa`, `gemini`, `all`. Full source table and selection rules: see `## Data Sources` below.
- **ARXIV_DOWNLOAD = false** — When `true`, download top 3-5 most relevant arXiv PDFs to PAPER_LIBRARY after search. When `false` (default), only fetch metadata (title, abstract, authors) via the arXiv API — no files are downloaded.
- **ARXIV_MAX_DOWNLOAD = 5** — Maximum number of PDFs to download when `ARXIV_DOWNLOAD = true`.

> Overrides (state them alongside the topic, in the same request):
> - `paper library: ~/my_papers/` — custom local PDF path
> - `sources: zotero, local` — only search Zotero + local PDFs
> - `sources: web` — only search the web (skip all local)
> - `sources: web, semantic-scholar` — also search Semantic Scholar for published venue papers (IEEE, ACM, etc.)
> - `sources: all, openalex` — default sources plus OpenAlex
> - `sources: all, deepxiv` — default sources plus DeepXiv (if the user has its CLI)
> - `arxiv download: true` — download top relevant arXiv PDFs
> - `arxiv download: true, max download: 10` — download up to 10 PDFs

## Data Sources

This resource checks multiple sources **in priority order**. All are optional — if a source is not configured or not requested, skip it silently.

### Source Selection

Priority order matters when sources overlap: the earlier (more personal/curated) sources win for user context, while structured API sources win for metadata authority according to the per-source de-duplication rules stated with each search below.

Parse the request for a `sources:` directive:
- **If `sources:` is specified**: Only search the listed sources (comma-separated). Valid values: `zotero`, `obsidian`, `local`, `web`, `arxiv`, `semantic-scholar`, `openalex`, `deepxiv`, `exa`, `gemini`, `all`.
- **If not specified**: Default to `all` — search every available source in priority order (`semantic-scholar`, `openalex`, `deepxiv`, `exa`, and `gemini` are **excluded** from `all`; they must be explicitly listed).

`all` covers the default-on tier (zotero, obsidian, local, web/arxiv) — it does **not** include the opt-in fetchers (semantic-scholar, openalex, deepxiv, exa, gemini). To enable those, add them explicitly (e.g. `sources: all, semantic-scholar, openalex`).

Examples:
```
"diffusion models"                                → all (default, no S2/OpenAlex)
"diffusion models" — sources: all                 → all (default, no S2/OpenAlex)
"diffusion models" — sources: zotero              → Zotero only
"diffusion models" — sources: zotero, web         → Zotero + web
"diffusion models" — sources: local               → local PDFs only
"topic" — sources: obsidian, local, web           → skip Zotero
"topic" — sources: web, semantic-scholar          → web + Semantic Scholar API (IEEE/ACM venue papers)
"topic" — sources: openalex                       → OpenAlex only (open citation graph + institutions)
"topic" — sources: semantic-scholar, openalex     → Semantic Scholar + OpenAlex (complementary metadata)
"topic" — sources: exa                            → Exa only (requires user-provided API key)
"topic" — sources: all, exa                       → default sources + Exa web search
"topic" — sources: gemini                         → Gemini only (requires user-provided MCP/CLI)
"topic" — sources: all, gemini                    → default sources + Gemini discovery
"topic" — sources: gemini, semantic-scholar       → Gemini + S2 (broad discovery + venue metadata)
"topic" — sources: deepxiv                        → DeepXiv only (requires user-provided CLI)
"topic" — sources: all, deepxiv                   → default sources + DeepXiv
"topic" — sources: all, semantic-scholar          → all + S2 API
```

**Fallbacks and degraded behavior (all sources).** Every optional source has a defined failure path, and none of them may abort the run: MCP servers that are not configured are skipped silently; a requested bash/API source that fails after being invoked emits one WARN line and drops out of the contributing list; the local-PDF scan that finds nothing emits the explicit `WARN: local contributed nothing` above (never a silent skip); `verify_pending` is a retryable state, not a rejection. The only hard stop is the aggregate-empty error below, which fires after all requested sources have been tried.

### Source Table

| Priority | Source | ID | How to detect | What it provides |
|----------|--------|----|---------------|-----------------|
| 1 | **Zotero** (via MCP) | `zotero` | Try calling any `mcp__zotero__*` tool — if unavailable, skip | Collections, tags, annotations, PDF highlights, BibTeX, semantic search |
| 2 | **Obsidian** (via MCP) | `obsidian` | Try calling any `mcp__obsidian-vault__*` tool — if unavailable, skip | Research notes, paper summaries, tagged references, wikilinks |
| 3 | **Local PDFs** | `local` | `Glob: papers/**/*.pdf, literature/**/*.pdf` | Raw PDF content (first 3 pages) |
| 4 | **Web search + arXiv API** | `web` (alias `arxiv`) | WebSearch is always available; the arXiv API tier needs `python3` + network only | arXiv preprints (structured metadata via the native arXiv API, see the bundled arXiv resource), plus Google Scholar/venue pages via WebSearch |
| 5 | **Semantic Scholar API** | `semantic-scholar` | The project has `python3` + network (no key required; an optional `SEMANTIC_SCHOLAR_API_KEY` lifts rate limits). Procedure: `${CLAUDE_PLUGIN_ROOT}/resources/research/semantic-scholar/SKILL.md` | Published venue papers (IEEE, ACM, Springer) with structured metadata: citation counts, venue info, TLDR. **Only runs when explicitly requested** via `sources: semantic-scholar` |
| 6 | **OpenAlex API** | `openalex` | `python3` + network (or `curl`); fully open API, no key required | Open citation graph with institutional affiliations, funding data, and comprehensive metadata across 250M+ works. **Only runs when explicitly requested** via `sources: openalex` |
| 7 | **DeepXiv CLI** | `deepxiv` | Only if the user has installed the external `deepxiv` CLI (`command -v deepxiv`) — user-provided, never auto-installed | Progressive paper retrieval: search, brief, head, section, trending. **Only runs when explicitly requested** via `sources: deepxiv` |
| 8 | **Exa Search** | `exa` | Only if `EXA_API_KEY` is set in the environment (user-provided key; `exa-py` SDK optional) | AI-powered broad web search with content extraction covering blogs, docs, news, and papers beyond arXiv/S2. **Only runs when explicitly requested** via `sources: exa` |
| 9 | **Gemini** (MCP / CLI) | `gemini` | Only if `mcp__gemini-cli__ask-gemini` is available, or the `gemini` CLI is installed — user-provided | AI-powered broad literature discovery — decomposes topics into sub-problems, aliases, and variants. **Only runs when explicitly requested** via `sources: gemini` |

> **Graceful degradation**: If no MCP servers are configured, the resource works exactly as before (local PDFs + web search + native arXiv API). Zotero, Obsidian, DeepXiv, Exa, and Gemini are pure additions; never fail because one of them is missing.

## Workflow

### Step 0a: Search Zotero Library (if available)

**Skip this step entirely if Zotero MCP is not configured.**

Try calling a Zotero MCP tool (e.g., search). If it succeeds:

1. **Search by topic**: Use the Zotero search tool to find papers matching the research topic
2. **Read collections**: Check if the user has a relevant collection/folder for this topic
3. **Extract annotations**: For highly relevant papers, pull PDF highlights and notes — these represent what the user found important
4. **Export BibTeX**: Get citation data for relevant papers (useful for later paper writing)
5. **Compile results**: For each relevant Zotero entry, extract:
   - Title, authors, year, venue
   - User's annotations/highlights (if any)
   - Tags the user assigned
   - Which collection it belongs to

> Zotero annotations are gold — they show what the user personally highlighted as important, which is far more valuable than generic summaries.

### Step 0b: Search Obsidian Vault (if available)

**Skip this step entirely if Obsidian MCP is not configured.**

Try calling an Obsidian MCP tool (e.g., search). If it succeeds:

1. **Search vault**: Search for notes related to the research topic
2. **Check tags**: Look for notes tagged with relevant topics (e.g., `#diffusion-models`, `#paper-review`)
3. **Read research notes**: For relevant notes, extract the user's own summaries and insights
4. **Follow links**: If notes link to other relevant notes (wikilinks), follow them for additional context
5. **Compile results**: For each relevant note:
   - Note title and path
   - User's summary/insights
   - Links to other notes (research graph)
   - Any frontmatter metadata (paper URL, status, rating)

> Obsidian notes represent the user's **processed understanding** — more valuable than raw paper content for understanding their perspective.

### Step 0c: Scan Local Paper Library

Before searching online, check if the user already has relevant papers locally:

1. **Locate library**: Check PAPER_LIBRARY paths for PDF files
   ```
   Glob: papers/**/*.pdf, literature/**/*.pdf
   ```

2. **De-duplicate against Zotero**: If Step 0a found papers, skip any local PDFs already covered by Zotero results (match by filename or title).

3. **Filter by relevance**: Match filenames and first-page content against the research topic. Skip clearly unrelated papers.

4. **Summarize relevant papers**: For each relevant local PDF (up to MAX_LOCAL_PAPERS):
   - Read first 3 pages (title, abstract, intro)
   - Extract: title, authors, year, core contribution, relevance to topic
   - Flag papers that are directly related vs tangentially related

5. **Build local knowledge base**: Compile summaries into a "papers you already have" section. This becomes the starting point — external search fills the gaps.

> If the user has a comprehensive local collection, the external search can be more targeted (focus on what's missing).
>
> **If all three PAPER_LIBRARY paths miss, say so before moving on** — do not skip silently. A user whose PDFs live in a reference manager (Zotero, Mendeley, ...) otherwise assumes `sources: all` covered them. Emit:
>
> `WARN: local contributed nothing — no PDFs found in papers/, literature/, or a configured paper library. To include yours, add a "## Paper Library" heading to the project instructions followed by the directory path.`
>
> Then continue to Step 1.

### Step 1: Search (external)

- Use WebSearch to find recent papers on the topic
- Check arXiv, Semantic Scholar, Google Scholar
- Focus on papers from last 2 years unless studying foundational work
- **De-duplicate**: Skip papers already found in Zotero, Obsidian, or local library

**Source-contribution tracking (aggregate gate).** The executor (you, the LLM) maintains an in-context list of contributing sources, because each fetch command runs in its own shell and state does not survive between commands. A source contributes iff:

- helper-free bash/command sources (arXiv API, Semantic Scholar, OpenAlex, Exa): the fetch command was actually invoked and exited 0 — an exit-0 call that returned an empty result list still counts as "ran"; downstream relevance ranking decides what the user sees;
- non-command sources: `zotero` / `obsidian` iff the step returned non-empty hits; `local` iff at least one relevant local PDF was found; `web` (WebSearch) iff it was requested (no `sources:` filter, or the list contains `web` or `all`) and actually invoked; `gemini` iff it returned at least one paper.

Sources that were not requested via `sources:` do not count. At the end of Step 1 (before "Optional PDF download"), if zero sources contributed, surface the aggregate-empty error below and stop.

**arXiv API search** (runs when `sources:` is unset or contains `web`, `arxiv`, or `all`; no download by default):

The full arXiv procedure (search, ID lookup, download, rate-limit and retry rules) lives in the bundled arXiv resource: `${CLAUDE_PLUGIN_ROOT}/resources/research/arxiv/SKILL.md`. Follow it; the essential search call is:

```bash
python3 - <<'PY'   # stdlib-only; exits 1 on failure so the aggregate can continue
import json, urllib.parse, urllib.request, xml.etree.ElementTree as ET
NS = "http://www.w3.org/2005/Atom"
params = urllib.parse.urlencode({
 "search_query": "QUERY", "start": 0, "max_results": 10,
 "sortBy": "relevance", "sortOrder": "descending"})
req = urllib.request.Request("https://export.arxiv.org/api/query?" + params,
                          headers={"User-Agent": "minh-agent-arxiv/1.0"})
with urllib.request.urlopen(req, timeout=30) as r:
 root = ET.fromstring(r.read())
papers = []
for e in root.findall(f"{{{NS}}}entry"):
 aid = e.findtext(f"{{{NS}}}id", "").split("/abs/")[-1].split("v")[0]
 papers.append({
     "id": aid,
     "title": (e.findtext(f"{{{NS}}}title", "") or "").strip(),
     "abstract": (e.findtext(f"{{{NS}}}summary", "") or "").strip(),
     "authors": [a.findtext(f"{{{NS}}}name", "") for a in e.findall(f"{{{NS}}}author")],
     "published": (e.findtext(f"{{{NS}}}published", "") or "")[:10],
     "categories": [c.get("term", "") for c in e.findall(f"{{{NS}}}category")],
 })
print(json.dumps(papers, ensure_ascii=False, indent=2))
PY
```

If the call fails (network error, HTTP non-200, python3 missing), emit one WARN line (`WARN: arXiv API call failed; continuing with remaining sources.`) and continue — never abort the whole aggregate. The arXiv API returns structured metadata (title, abstract, full author list, categories, dates) — richer than WebSearch snippets. Merge these results with WebSearch findings and de-duplicate.

**Why use the arXiv API in the web tier?** WebSearch surfaces pages about papers; the API returns the papers themselves with exact titles, IDs, and dates, which is what the verification step and later citation work need. WebSearch remains the discovery tool; the API is the metadata authority.

**Semantic Scholar API search** (only when `semantic-scholar` is in sources):

Follow the bundled procedure in `${CLAUDE_PLUGIN_ROOT}/resources/research/semantic-scholar/SKILL.md` for the default query. The default filters for a general research query are:

```
python3 - <<'PY'
import json, urllib.parse, urllib.request
q = urllib.parse.urlencode({
    "query": "QUERY", "limit": 10,
    "fields": "paperId,title,abstract,year,venue,publicationVenue,publicationTypes,"
              "publicationDate,url,openAccessPdf,authors,externalIds,citationCount,tldr",
    "fieldsOfStudy": "Computer Science,Engineering",
    "publicationTypes": "JournalArticle,Conference"})
req = urllib.request.Request("https://api.semanticscholar.org/graph/v1/paper/search?" + q,
                             headers={"User-Agent": "minh-agent-s2/1.0"})
with urllib.request.urlopen(req, timeout=30) as r:
    print(json.dumps(json.loads(r.read()), ensure_ascii=False, indent=2))
PY
```

If the call fails (or python3 is missing), skip silently — the aggregate continues with the remaining resolved sources. If HTTP 429 occurs, wait and retry once after a few seconds.

**Why use Semantic Scholar?** Many IEEE/ACM journal papers are NOT on arXiv. S2 fills the gap for published venue-only papers with citation counts and venue metadata.

**De-duplication between arXiv and S2**: Match by arXiv ID (S2 returns `externalIds.ArXiv`):
- If a paper appears in both: check S2's `venue`/`publicationVenue` — if it has been published in a journal/conference (e.g. IEEE TWC, JSAC), use S2's metadata (venue, citationCount, DOI) as the authoritative version, since the published version supersedes the preprint. Keep the arXiv PDF link for download.
- If the S2 match has no venue (still just a preprint indexed by S2): keep the arXiv version as-is.
- S2 results without `externalIds.ArXiv` are **venue-only papers** not on arXiv — these are the unique value of this source.

**OpenAlex search** (only when `openalex` is in sources):

OpenAlex is a fully open API (no key required). Query it natively with `curl` or `python3`:

```bash
# Optional polite pool: add "&mailto=<contact>" when the user provides a contact address.
curl -sf -G "https://api.openalex.org/works" \
  --data-urlencode "search=QUERY" \
  --data-urlencode "per-page=10" \
  --data-urlencode "filter=publication_year:2022-,type:article" \
  --data-urlencode "sort=relevance_score:desc"
```

If `curl` returns non-zero (network unavailable, HTTP error), emit one WARN line and continue with the remaining sources. When `python3` is available, prefer a small urllib call with the same parameters so the JSON can be parsed directly.

> **Preflight**: skip the OpenAlex source silently (or with one WARN line) when neither `curl` nor `python3` is available, so a default run never dumps a runtime stack trace on a machine without these tools.

**Why use OpenAlex?** Open citation graph (no API key required), institutional affiliations, funding data (NSF, NIH), comprehensive topic/keyword metadata, and coverage across all disciplines (not just CS).

**De-duplication against arXiv, S2, and others**:
- Match by DOI first (OpenAlex has DOI for most works), then arXiv ID, then normalized title
- If OpenAlex and S2 both have the same paper: prefer S2 for citation counts and CS/AI venue metadata; use OpenAlex for institutional affiliations and funding data (unique value); merge both into a richer record
- If OpenAlex and arXiv overlap, prefer arXiv's PDF link and metadata, but keep OpenAlex's citation/institution data

**DeepXiv search** (only when `deepxiv` is in sources):

DeepXiv is an optional, user-provided CLI. It is useful when a broad search should be followed by staged reading rather than immediate full-paper loading — this reduces unnecessary context while still surfacing structure, TLDRs, and the most relevant sections.

1. **Availability check**: require `command -v deepxiv`. If it fails, emit one WARN line and skip the source; never install or authenticate on the user's behalf.
2. **Search**: run the CLI's search for the query (about 10 results) and treat a successful invocation as a contribution to the aggregate, even if the result list is empty.
3. **Deepen only the most relevant papers** (sub-calls do not change the aggregate count). For each top paper, progress through staged reading — brief, then head (abstract/intro), then specific sections (e.g. "Experiments"). Wrap each sub-call so one failure only skips that deepen step:
   `WARN: deepxiv <step> failed; skipping deepen step.`
4. **De-duplication against arXiv and Semantic Scholar**: match by arXiv ID first, DOI second, normalized title third. If DeepXiv and arXiv refer to the same preprint, keep one canonical paper row and record `deepxiv` as an additional source. If DeepXiv overlaps with S2 on a published paper, prefer S2 venue/citation metadata in the final table, but keep DeepXiv-derived section notes when they add value.

**Exa search** (only when `exa` is in sources):

Exa is an optional, user-provided API service. It fills a gap between academic databases (arXiv, S2) and generic WebSearch by returning richer content with each result (blogs, documentation, news, company pages).

1. **Availability check**: require `EXA_API_KEY` in the environment. If unset, emit `WARN: EXA_API_KEY not set; skipping Exa.` and continue. Never ask for, print, or store keys.
2. **Search**: call `https://api.exa.ai/search` with the topic; optionally restrict one call to research papers and run a second broader call. Treat at least one successful invocation as a contribution.
3. **De-duplication against arXiv, S2, and DeepXiv**: match by URL first, then normalized title. If Exa returns an arXiv paper already found upstream, prefer the structured metadata from those sources; Exa results from non-academic domains are its unique value.

**Gemini search** (only when `gemini` is in sources):

Gemini is an optional, user-provided discovery backend. **Priority 1 — Gemini MCP** (preferred): if `mcp__gemini-cli__ask-gemini` is available, call it with the scout prompt. **Priority 2 — Gemini CLI**: if MCP is unavailable but the `gemini` CLI exists, use `gemini -p "..."` via Bash (timeout: 120s). If both are unavailable, skip gracefully and continue with the remaining requested sources.

The scout prompt must: decompose the topic into sub-problems, aliases, neighboring tasks, and benchmark/setting variants; prefer genuinely relevant papers over keyword-adjacent ones; include top venues, journals, surveys, recent preprints, and papers with code; focus on 2022 onward unless older foundational work is necessary; and return for EACH paper: exact title, full author list, year, venue (or "arXiv preprint"), arXiv ID or "N/A", DOI or "N/A", code URL or "No code", and a one-sentence core-contribution summary — at least 15 papers.

De-duplication against the other sources: match by arXiv ID first, DOI second, normalized title third. If Gemini returns a paper already found by S2, prefer S2's citation count and venue metadata; if already found by arXiv, prefer arXiv's structured metadata. **Do not use Gemini-reported citation counts** — they may be inaccurate; use Semantic Scholar for authoritative citation data. Gemini's unique value is discovering papers that keyword-based indexes did not surface.

**Aggregate finalization**:

If the contributing-source list (built per "Source-contribution tracking" above) has zero entries, surface:

> **ERROR**: aggregate empty — every requested source either was unavailable, not invoked, failed, or (for MCP / local PDF / Gemini sources) returned no usable result. (Note: WebSearch contributes when requested and invoked, even if the result set is empty.) The multi-source aggregate cannot proceed. Suggest the user retry with a wider `sources:` list (e.g. `web, local`) or check network/python3 availability.

Then stop before Step 1.5. Otherwise log the contributing-source list to the user (e.g. "Sources contributed: arxiv, semantic_scholar, web") and proceed.

**Optional PDF download** (only when `ARXIV_DOWNLOAD = true`):

After all sources are searched and papers are ranked by relevance, follow the download procedure in `${CLAUDE_PLUGIN_ROOT}/resources/research/arxiv/SKILL.md`:

- Only download papers ranked in the top ARXIV_MAX_DOWNLOAD (and never more than ARXIV_MAX_DOWNLOAD) by relevance
- Skip papers already in the local library — never overwrite an existing PDF
- 1-second delay between downloads (rate limiting)
- Verify each PDF > 10 KB and has a PDF header; delete and warn on failures

### Step 1.5: Verify Candidate Papers (anti-hallucination, mandatory)

Before analysis, run pre-search verification on **all** candidate papers collected from Steps 0a-1 to filter out LLM-fabricated arXiv IDs / DOIs / titles. This is the deterministic admission gate for the analyzed set. It is a process, not a model verdict — so it carries no cross-model-family requirement.

1. Emit candidates as JSON in the project scratch directory:
```bash
mkdir -p .minh-agent/verify-papers
cat > .minh-agent/verify-papers/candidate_papers.json <<'JSON'
[
  {"id": "p1", "arxiv_id": "2307.03172", "doi": null, "title": "Lost in the Middle"},
  {"id": "p2", "arxiv_id": null, "doi": "10.1145/...", "title": "..."},
  {"id": "p3", "arxiv_id": null, "doi": null, "title": "Some Paper Title"}
]
JSON
```
Never fabricate a DOI or arXiv ID from memory. If a field is unknown, leave it `null` — the verification falls through to title search.

2. Run the 3-layer verification with stdlib-only Python. Layer 1 checks arXiv-ID existence in one batched `id_list` call; layer 2 checks that the DOI resolves at CrossRef (HTTP 200 = exists, 404 = not found, transient codes defer to `verify_pending`); layer 3 searches Semantic Scholar by normalized title and accepts a hit only at >= 0.6 token overlap. Keep a throttle of about 1 request/second for the Semantic Scholar layer and set a descriptive User-Agent (`MINH_AGENT_CONTACT` in the environment may carry a contact address for the polite pools of arXiv and CrossRef):
```bash
python3 - <<'PY'
import json, os, re, time, unicodedata, urllib.error, urllib.parse, urllib.request

contact = os.environ.get("MINH_AGENT_CONTACT", "").strip()
UA = "minh-agent-verify/1.0" + (f" (mailto:{contact})" if contact else "")
ARXIV = "https://export.arxiv.org/api/query"
CROSSREF = "https://api.crossref.org/works/"
S2 = "https://api.semanticscholar.org/graph/v1/paper/search"

def get(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return -1, None

def norm_doi(d): return (d or "").strip().lower().replace("https://doi.org/", "").replace("doi.org/", "")
def norm_title(t):
    t = unicodedata.normalize("NFKC", t or "").lower()
    return re.sub(r"[^a-z0-9 ]+", " ", t)
def similar(a, b):
    sa, sb = set(norm_title(a).split()), set(norm_title(b).split())
    return len(sa & sb) / max(1, min(len(sa), len(sb)))

cands = json.load(open(".minh-agent/verify-papers/candidate_papers.json"))
# Layer 1: arXiv batch id lookup (transient failure -> verify_pending, not a rejection)
ids = [c["arxiv_id"] for c in cands if c.get("arxiv_id")]
arxiv_ok, arxiv_transient = {}, False
if ids:
    url = f"{ARXIV}?id_list={','.join(ids)}&max_results={len(ids)}"
    status, body = get(url, headers={"User-Agent": UA}, timeout=30)
    if status == 200 and body:
        for i in ids:
            base = i.rsplit("v", 1)[0]
            arxiv_ok[base] = f"http://arxiv.org/abs/{base}" in body
    elif status in (406, 408, 429, -1) or status >= 500:
        arxiv_transient = True
# Layers 2 + 3 (fall through only while still unverified)
out = []
for c in cands:
    status_, method = "unverified", None
    if c.get("arxiv_id"):
        base = c["arxiv_id"].rsplit("v", 1)[0]
        if arxiv_ok.get(base):
            status_, method = "verified", "arxiv"
        elif arxiv_transient:
            status_ = "verify_pending"
    elif c.get("doi"):
        s, _ = get(CROSSREF + urllib.parse.quote(norm_doi(c["doi"])), timeout=15)
        if s == 200: status_, method = "verified", "crossref"
        elif s in (406, 408, 429, -1) or s >= 500: status_ = "verify_pending"
    if status_ == "unverified" and c.get("title"):
        q = urllib.parse.urlencode({"query": c["title"], "limit": 3, "fields": "title,year,externalIds"})
        time.sleep(1.0)
        s, body = get(f"{S2}?{q}", timeout=15)
        if s == 200 and body:
            for hit in json.loads(body).get("data", []):
                if similar(c["title"], hit.get("title", "")) >= 0.6:
                    status_, method = "verified", "s2"
                    break
        elif s in (429, -1) or s >= 500: status_ = "verify_pending"
    if status_ == "unverified" and not (c.get("arxiv_id") or c.get("doi") or c.get("title")):
        status_ = "error"
    out.append({**{k: c.get(k) for k in ("id", "arxiv_id", "doi", "title")},
                "status": status_, "method": method})
json.dump({"verdict": "WARN" if any(p["status"] != "verified" for p in out) else "PASS",
           "papers": out},
          open(".minh-agent/verify-papers/verified_papers.json", "w"), indent=2)
PY
```

3. **Degraded-output fallback (never silently drop candidates).** If the verification cannot run at all (python3 missing, or the whole network layer is down so every layer fails), and if python3 itself is unavailable you cannot emit the fallback file — then report `BLOCKED: verification unavailable; python3 required` and stop rather than proceeding on unverified data by hand. Otherwise, when the script above cannot complete, emit a degraded `verified_papers.json` tagging every candidate `status: "unverified", method: "none"` with `reason_code: "verify_unavailable"`, so downstream analysis proceeds with audit-visible degradation.

4. Read the verdict + per-paper status from `.minh-agent/verify-papers/verified_papers.json`; surface warnings to the user.

**Mandatory output rules**:

- Tag every paper in the analyzed list with its status: `✅ verified (via arxiv|crossref|s2)` or `⚠️ UNVERIFIED (reason)` or `… verify_pending`.
- **Never silently drop unverified papers** — keep them in the output with the `[UNVERIFIED]` marker so the user can audit the search quality.
- **Retention rule**: every candidate emitted in `candidate_papers.json` is carried into Step 2 and into the output table; verification changes only the status label, never the row count. The single exception is malformed input with no identifier and no title, which is retained as `❌ ERROR` so the user can see the emission bug.
- If the verification run reports `WARN` with a high hallucination rate (an implausible share of candidates failing every layer), surface that warning verbatim and recommend re-running with narrower queries.
- For papers tagged `verify_pending`, do not promote them to `verified` — show the pending state to the user and retry on the next session.

Optional: set `MINH_AGENT_CONTACT=you@institution.edu` in the environment to lift CrossRef rate limits to the polite pool.

### Step 2: Analyze Each Paper

> **Fan-out (tier-aware).** Per-paper extraction is pure breadth — each paper is independent — so it parallelizes cleanly. **Tier 1** (workflow/subagent tooling available): spawn one subagent per paper (or per small batch) to extract the fields below. **Tier 2** (Agent tool, no workflow): the same per-paper subagents via the Agent tool. **Tier 3**: iterate sequentially. Per-shard output schema: `{shard_id: "<paper-or-batch id>", entries: [{dedup_key: "<canonical arXiv-id / DOI / title-hash, already assigned upstream in Step 1.5>", problem, method, results, relevance, source, verification_status}]}`.
>
> The "jury" here is **not a model** — it is the **deterministic** Step-1.5 verification gate (3-layer arXiv / CrossRef / Semantic Scholar cross-check). Because the acceptance gate is a deterministic verifier, not a model verdict, the cross-model-family rule is automatically satisfied (a process is not a model family), so this is the near-zero-risk corner of the fan-out design space. The per-paper work is **extraction, not adjudication**: shards report what each paper says and its verification status verbatim; they do **not** decide which papers "count" (Step 1.5 already did, mechanically) and they do **not** drop a paper for any status other than `verified`. Synthesis (Step 3) is interpretive aggregation over an already-admitted set — not an accept/reject verdict on whether a paper counts.

For **every** paper in `.minh-agent/verify-papers/verified_papers.json` (verified, unverified, `verify_pending`, and `error` alike), extract:
- **Problem**: What gap does it address?
- **Method**: Core technical contribution (1-2 sentences)
- **Results**: Key numbers/claims
- **Relevance**: How does it relate to our work?
- **Source**: Where we found it (Zotero/Obsidian/local/web) — helps the user know what they already have vs what's new
- **Verification status** (one of):
  - `✅ verified (via arxiv|crossref|s2)`
  - `⚠️ UNVERIFIED (verification unavailable: helper unresolved or invocation failed)`
  - `⚠️ UNVERIFIED (searched: not found in any source)`
  - `… VERIFY_PENDING (transient API failure — retry next session)`
  - `❌ ERROR (malformed input: no arxiv, no DOI, no title)`

  Show the status in the analyzed table — never silently drop a paper because its status is anything other than `verified`.

### Step 3: Synthesize
- Group papers by approach/theme
- Identify consensus vs disagreements in the field
- Find gaps that our work could fill
- If Obsidian notes exist, incorporate the user's own insights into the synthesis

### Step 4: Output
Present as a structured literature table:

```
| Paper | Venue | Method | Key Result | Relevance to Us | Source | Status |
|-------|-------|--------|------------|-----------------|--------|--------|
```

Plus a narrative summary of the landscape (3-5 paragraphs).

If Zotero BibTeX was exported, include a `references.bib` snippet for direct use in paper writing.

### Step 5: Save (if requested)
- Save paper PDFs to `literature/` or `papers/`
- Update related work notes in project memory
- If Obsidian is available, optionally create a literature review note in the vault

> **Composed mode** — if invoked with `composed: <canonical-report-path>` (a calling minh-agent workflow passes this), do **not** write a standalone landscape `.md`. Return the structured table + narrative summary for the orchestrator to fold into its canonical report as a "Literature Landscape" section; the report links any saved PDFs/`references.bib`, it does not get a duplicate landscape file. The optional wiki hand-off (Step 6) still runs in composed mode — the wiki is a separate persistent store, not a duplicate of the report. **Default (no `composed:` directive): behave exactly as above — standalone, write files as documented.** Never infer composed mode from a report file merely existing on disk.

### Step 6: Project Wiki Hand-Off (optional, if the project provides one)

**Skip silently (no action, no error) unless the project both contains a `research-wiki/` directory and provides its own wiki ingest tool.** This resource does not ship a wiki helper; the wiki store is an optional project-side capability.

When both are present: hand the top 8-12 relevant papers to the project's ingest tool with their arXiv IDs (or, for non-arXiv sources such as Semantic Scholar-only or IEEE/ACM journal papers, the manual metadata form: title, authors, year, venue, DOI). Let the tool handle slug generation, dedup, page rendering, and index rebuilds — do not hand-write wiki pages. If ingest fails or the tool is absent, log the gap and continue; the literature output is the deliverable.

## Key Rules
- Always include paper citations (authors, year, venue)
- Distinguish between peer-reviewed and preprints
- Be honest about limitations of each paper
- Note if a paper directly competes with or supports our approach
- **Never fail because an MCP server, CLI, or API key is not configured** — always fall back gracefully to the next data source
- Zotero/Obsidian tools may have different names depending on how the user configured the MCP server (e.g., `mcp__zotero__search` or `mcp__zotero-mcp__search_items`). Try the most common patterns and adapt.
- Never fabricate an arXiv ID, DOI, or title from memory; the Step-1.5 gate exists precisely to catch this
- Optional sources (DeepXiv, Exa, Gemini) are user-provided backends: detect them honestly, skip with a WARN when absent, and never install, authenticate, or spend money on them on your own.
- Report the contributing-source list with the results — the user should see which sources actually ran, not just which were requested.

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/research-lit/SKILL.md (MIT). See registry/components.json. -->
