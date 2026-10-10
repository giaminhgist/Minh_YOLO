# Semantic Scholar Paper Search

When this resource is used: loaded by minh-agent `research`/`read` flows (and by `${CLAUDE_PLUGIN_ROOT}/resources/research/research-lit/SKILL.md` when the `semantic-scholar` source is requested) when the user asks for published venue papers, IEEE/ACM/Springer literature, citation counts, or venue metadata beyond arXiv preprints.

Search topic or paper ID: the user's query.

## Role & Positioning

This resource is the **published venue** counterpart to `${CLAUDE_PLUGIN_ROOT}/resources/research/arxiv/SKILL.md`:

| Resource | Source | Best for |
|----------|--------|----------|
| arXiv resource | arXiv API | Latest preprints, cutting-edge unrefereed work |
| This resource | Semantic Scholar Graph API | **Published** journal/conference papers (IEEE, ACM, Springer, etc.) with citation counts, venue info, TLDR |

**Do NOT duplicate arXiv's job.** If results contain an `externalIds.ArXiv` field, the paper is also on arXiv — note this but do not re-fetch it from arXiv.

## Constants

- **MAX_RESULTS = 10** — Default number of search results.
- **API** — `https://api.semanticscholar.org/graph/v1`, queried with stdlib Python 3 (`urllib`) or `curl`. No SDK or install step is required.
- **SEMANTIC_SCHOLAR_API_KEY** — optional, user-provided environment variable. When set, send it as the `x-api-key` header for much higher rate limits (free key form: https://www.semanticscholar.org/product/api#api-key-form). Without it the API is heavily rate-limited (~1 req/s, strict cooldown). Never ask for, print, or store the key.
- **DEFAULT_FIELDS** — `paperId,title,abstract,year,venue,publicationVenue,publicationTypes,publicationDate,url,openAccessPdf,authors,externalIds,citationCount,referenceCount,fieldsOfStudy,s2FieldsOfStudy,tldr`
- **DEFAULT_FILTERS** — For general research queries, apply these by default to reduce noise:
  - `fieldsOfStudy=Computer Science,Engineering`
  - `publicationTypes=JournalArticle,Conference`

> Overrides (state them alongside the query):
> - `"topic" - max: 20` — return up to 20 results
> - `"topic" - type: journal` — only journal articles
> - `"topic" - type: conference` — only conference papers
> - `"topic" - min-citations: 50` — only highly-cited papers
> - `"topic" - year: 2022-` — papers from 2022 onward
> - `"topic" - fields: all` — remove default field-of-study filter
> - `"topic" - sort: citations` — bulk search sorted by citation count
> - `"DOI:10.1109/..."` — fetch a single paper by DOI

## Workflow

### Step 1: Parse Arguments

Parse the request for directives:

- **Query or ID**: main search term, or a paper identifier:
  - DOI: `10.1109/TWC.2024.1234567`
  - Semantic Scholar ID: `f9314fd99be5f2b1b3efcfab87197d578160d553`
  - ArXiv: `ARXIV:2006.10685`
  - Corpus: `CorpusId:219792180`
- **`- max: N`**: override MAX_RESULTS
- **`- type: journal|conference|review|all`**: map to `publicationTypes`
- **`- min-citations: N`**: map to `minCitationCount`
- **`- year: RANGE`**: map to `year` (e.g. `2022-`, `2020-2024`)
- **`- fields: FIELDS`**: override `fieldsOfStudy` (use `all` to remove the filter)
- **`- sort: citations|date`**: use bulk search with `sort=citationCount:desc` or `publicationDate:desc`

If the argument matches a DOI pattern (`10.XXXX/...`), a Semantic Scholar ID (40-char hex), or a prefixed ID (`ARXIV:...`, `CorpusId:...`), skip search and go directly to Step 3.

### Step 2: Search Papers

**Standard search** (default — relevance-ranked):

```bash
python3 - <<'PYEOF'
import json, os, urllib.parse, urllib.request
params = {
    "query": "QUERY",
    "limit": 10,                      # MAX_RESULTS
    "fields": ("paperId,title,abstract,year,venue,publicationVenue,publicationTypes,"
               "publicationDate,url,openAccessPdf,authors,externalIds,citationCount,"
               "referenceCount,fieldsOfStudy,s2FieldsOfStudy,tldr"),
    "fieldsOfStudy": "Computer Science,Engineering",
    "publicationTypes": "JournalArticle,Conference",
}
headers = {"User-Agent": "minh-agent-s2/1.0", "Accept": "application/json"}
key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "").strip()
if key:
    headers["x-api-key"] = key
url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(params)
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as r:
    print(json.dumps(json.loads(r.read()), ensure_ascii=False, indent=2))
PYEOF
```

**Bulk search** (when `- sort:` is specified, or MAX_RESULTS > 100): use the endpoint `https://api.semanticscholar.org/graph/v1/paper/search/bulk` with the same parameter names, plus `sort=citationCount:desc` (or `publicationDate:desc`). For bulk calls, request the conservative field set `paperId,title,abstract,year,venue,publicationDate,url,authors,externalIds,citationCount,referenceCount,fieldsOfStudy`, and follow the returned `token` for the next page instead of guessing offsets.

**Recommended filter combos** (from upstream testing):

| Goal | Parameters |
|------|------------|
| High-quality journal papers | `publicationTypes=JournalArticle` + `minCitationCount=10` |
| CS/EE papers, recent | `fieldsOfStudy=Computer Science,Engineering` + `year=2022-` |
| Foundational / high-impact | bulk search with `sort=citationCount:desc`, `fieldsOfStudy=Computer Science` |
| Conference papers only | `publicationTypes=Conference` |

> **Note**: the `venue` parameter requires exact venue names (e.g. "IEEE Transactions on Signal Processing"), not partial matches like "IEEE". Avoid it in automated flows — prefer `publicationTypes` + `fieldsOfStudy`.

**Failure handling**: on HTTP 429 (or 500/502/503/504), wait ~1.5–3 seconds and retry up to two times; on repeated failure or a network error, report it and fall back to the remaining sources of the calling workflow. A successful call with zero results is still a successful call.

### Step 3: Fetch Details for a Specific Paper

When a single paper ID is requested, fetch `https://api.semanticscholar.org/graph/v1/paper/{PAPER_ID}?fields={DEFAULT_FIELDS}` (URL-encode the ID; send the same optional `x-api-key` header).

Where PAPER_ID can be:
- DOI: `10.1109/TSP.2021.3071210`
- ArXiv: `ARXIV:2006.10685`
- CorpusId: `CorpusId:219792180`
- S2 ID: `f9314fd99be5f2b1b3efcfab87197d578160d553`

### Step 4: De-duplicate Against arXiv

For each result, check `externalIds.ArXiv`:
- If present → paper is also on arXiv. Note this in the output but do NOT re-fetch it from the arXiv resource.
- If absent → paper is **venue-only** (e.g. IEEE without preprint). This is the unique value of this resource.

### Step 5: Present Results

Present results as a table:

```text
| # | Title | Venue | Year | Citations | Authors | Type |
|---|-------|-------|------|-----------|---------|------|
| 1 | Deep Learning Enabled... | IEEE Trans. Signal Process. | 2021 | 1364 | Xie et al. | Journal |
```

For each paper, also show:
- **DOI link**: `https://doi.org/DOI` (for IEEE/ACM papers, this is the canonical link)
- **Open Access PDF**: if `openAccessPdf.url` is non-empty, show it
- **TLDR**: if available, show the one-line summary
- **Also on arXiv**: if `externalIds.ArXiv` exists, note the arXiv ID

### Step 6: Detailed Summary

For each paper (or top 5 if many results):

```markdown
## [Title]

- **Venue**: [venue name] ([publicationVenue.type]: journal/conference)
- **Year**: [year] | **Citations**: [citationCount]
- **Authors**: [full author list]
- **DOI**: [doi link]
- **Fields**: [fieldsOfStudy]
- **TLDR**: [tldr.text if available]
- **Abstract**: [abstract]
- **Open Access**: [openAccessPdf.url or "Not available"]
- **Also on arXiv**: [ArXiv ID if exists, else "No"]
```

### Step 7: Project Wiki Hand-Off (optional, if the project provides one)

**Skip silently (no action, no error) unless the project both contains a `research-wiki/` directory and provides its own wiki ingest tool.** No wiki helper ships with minh-agent. When both are present: for results with an `externalIds.ArXiv` field, ingest by arXiv ID; for venue-only papers (common for IEEE/ACM), use the project tool's manual metadata form (title, authors, year, venue, DOI). Do not hand-write wiki pages; if ingest fails or the tool is absent, the paper list is still the deliverable.

### Step 8: Final Output

Summarize what was done:

- `Found N published papers for "query"`
- `Filters applied: [publication types, fields, year range, etc.]`
- `N papers are venue-only (not on arXiv)`
- `Wiki-ingested N papers` (only if a project wiki tool was present and used)

Suggest follow-up resources:

```text
${CLAUDE_PLUGIN_ROOT}/resources/research/arxiv/SKILL.md          - search arXiv preprints (complements this search)
${CLAUDE_PLUGIN_ROOT}/resources/research/research-lit/SKILL.md   - multi-source review: Zotero + local PDFs + arXiv + S2
${CLAUDE_PLUGIN_ROOT}/resources/ideas/novelty-check/SKILL.md     - verify novelty against literature
```

## Key Rules

- **Default to filtered search**: Always apply `fieldsOfStudy` and `publicationTypes` unless the user says `- fields: all`. Without filters, the API returns cross-discipline noise (linguistics, psychology, etc.).
- **Citation count is gold**: S2's citation data is its main advantage over arXiv. Always show `citationCount` prominently and use it to rank/prioritize results.
- **Venue metadata matters**: Show `venue` and `publicationVenue.type` (journal vs conference) — this helps users assess paper quality.
- **DOI is the canonical ID for published papers**: Always show DOI links for IEEE/ACM/Springer papers.
- **Rate limiting**: Without a key the API is heavily rate-limited (~1 req/s, strict cooldown). If HTTP 429 occurs, wait and retry. Mention the free `SEMANTIC_SCHOLAR_API_KEY` option to the user when rate limits bite.
- **TLDR may be null**: Some publishers (notably IEEE) elide the TLDR field. Fall back to showing the first sentence of the abstract.
- **openAccessPdf may be empty**: Many IEEE papers are closed access. Always provide the DOI link as fallback.
- **Never fabricate metadata**: only show fields returned by the API; if the API is unreachable, report the error and suggest the arXiv resource or the web-search path of the research-lit resource as fallback.

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/semantic-scholar/SKILL.md (MIT). See registry/components.json. -->
