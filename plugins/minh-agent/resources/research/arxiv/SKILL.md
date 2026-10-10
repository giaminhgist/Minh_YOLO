# arXiv Paper Search & Download

When this resource is used: loaded by minh-agent `research`/`read` flows (and by `${CLAUDE_PLUGIN_ROOT}/resources/research/research-lit/SKILL.md` as its arXiv source) when the user asks to search arXiv, fetch a paper by ID, download a PDF, or save papers to the local paper library.

Search topic or arXiv paper ID: the user's query.

## Constants

- **PAPER_DIR** — Local directory to save downloaded PDFs. Default: `papers/` in the current project directory.
- **MAX_RESULTS = 10** — Default number of search results.
- **Runtime** — All fetching below is plain stdlib Python 3 (`urllib`, `xml.etree`), so no helper installation, virtualenv, or third-party package is required. If `python3` is unavailable, report that plainly instead of guessing paper metadata from memory.

> Overrides (state them alongside the query):
> - `"attention mechanism" - max: 20` — return up to 20 results
> - `"2301.07041" - download` — download a specific paper by ID
> - `"query" - dir: literature/` — save PDFs to a custom directory
> - `"query" - download: all` — download all result PDFs

## Workflow

### Step 1: Parse Arguments

Parse the request for directives:

- **Query or ID**: main search term or a bare arXiv ID such as `2301.07041` or `cs/0601001`
- **`- max: N`**: override MAX_RESULTS (e.g., `- max: 20`)
- **`- dir: PATH`**: override PAPER_DIR (e.g., `- dir: literature/`)
- **`- download`**: download the first result's PDF after listing
- **`- download: all`**: download PDFs for all results

If the argument matches an arXiv ID pattern (`YYMM.NNNNN` or `category/NNNNNNN`, optionally with a `vN` suffix), skip the search and go directly to Step 3.

### Step 2: Search arXiv

Search the arXiv API with stdlib Python. Send a descriptive User-Agent (the default `Python-urllib/x.y` agent is rate-limited more aggressively); set `MINH_AGENT_CONTACT` in the environment to append a contact address to the polite pool:

```bash
python3 - <<'PYEOF'
import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2005/Atom"
contact = os.environ.get("MINH_AGENT_CONTACT", "").strip()
ua = "minh-agent-arxiv/1.0" + (f" (mailto:{contact})" if contact else "")
query = urllib.parse.quote("QUERY")
url = (f"https://export.arxiv.org/api/query"
       f"?search_query={query}&start=0&max_results=MAX_RESULTS"
       f"&sortBy=relevance&sortOrder=descending")
req = urllib.request.Request(url, headers={"User-Agent": ua})
with urllib.request.urlopen(req, timeout=30) as r:
    root = ET.fromstring(r.read())
papers = []
for entry in root.findall(f"{{{NS}}}entry"):
    aid = entry.findtext(f"{{{NS}}}id", "").split("/abs/")[-1].split("v")[0]
    title = (entry.findtext(f"{{{NS}}}title", "") or "").strip().replace("\n", " ")
    abstract = (entry.findtext(f"{{{NS}}}summary", "") or "").strip().replace("\n", " ")
    authors = [a.findtext(f"{{{NS}}}name", "") for a in entry.findall(f"{{{NS}}}author")]
    published = entry.findtext(f"{{{NS}}}published", "")[:10]
    updated = entry.findtext(f"{{{NS}}}updated", "")[:10]
    cats = [c.get("term", "") for c in entry.findall(f"{{{NS}}}category")]
    papers.append({
        "id": aid,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "published": published,
        "updated": updated,
        "categories": cats,
        "pdf_url": f"https://arxiv.org/pdf/{aid}.pdf",
        "abs_url": f"https://arxiv.org/abs/{aid}",
    })
print(json.dumps(papers, ensure_ascii=False, indent=2))
PYEOF
```

Failure handling: retry once after ~5 seconds on HTTP 429, 408, or a plain-text `Rate exceeded.` body; on repeated failure or a network error, report it clearly (see Key Rules for the fallback suggestion). Do not invent results.

Present results as a table:

```text
| # | arXiv ID   | Title               | Authors        | Date       | Category |
|---|------------|---------------------|----------------|------------|----------|
| 1 | 2301.07041 | Attention Is All... | Vaswani et al. | 2017-06-12 | cs.LG    |
```

### Step 3: Fetch Details for a Specific ID

When a single paper ID is requested (either directly or from Step 2), query the API by `id_list` instead of searching:

```bash
python3 - <<'PYEOF'
import os, urllib.request, urllib.parse, xml.etree.ElementTree as ET
NS = "http://www.w3.org/2005/Atom"
contact = os.environ.get("MINH_AGENT_CONTACT", "").strip()
ua = "minh-agent-arxiv/1.0" + (f" (mailto:{contact})" if contact else "")
url = ("https://export.arxiv.org/api/query?" +
       urllib.parse.urlencode({"id_list": "ARXIV_ID", "max_results": 1}))
req = urllib.request.Request(url, headers={"User-Agent": ua})
with urllib.request.urlopen(req, timeout=30) as r:
    root = ET.fromstring(r.read())
entry = root.find(f"{{{NS}}}entry")
if entry is None:
    print("NOT FOUND: ARXIV_ID")
else:
    print((entry.findtext(f"{{{NS}}}title", "") or "").strip())
    print([a.findtext(f"{{{NS}}}name", "") for a in entry.findall(f"{{{NS}}}author")])
    print([c.get("term", "") for c in entry.findall(f"{{{NS}}}category")])
    print((entry.findtext(f"{{{NS}}}summary", "") or "").strip())
    print(entry.findtext(f"{{{NS}}}published", "")[:10])
PYEOF
```

Display: title, all authors, categories, full abstract, published date, PDF URL, abstract URL.

### Step 4: Download PDFs

When download is requested, for each paper ID to download:

```bash
mkdir -p PAPER_DIR && python3 - <<'PYEOF'
import os, pathlib, sys, time, urllib.error, urllib.request
arxiv_id = "ARXIV_ID"
out_dir = pathlib.Path("PAPER_DIR")
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / f"{arxiv_id.replace('/', '_')}.pdf"
if out.exists():
    print(f"Already exists: {out}")
    sys.exit(0)
contact = os.environ.get("MINH_AGENT_CONTACT", "").strip()
ua = "minh-agent-arxiv/1.0" + (f" (mailto:{contact})" if contact else "")
req = urllib.request.Request(f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                             headers={"User-Agent": ua})
for attempt in (1, 2, 3):
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        break
    except urllib.error.HTTPError as e:
        if e.code == 429 and attempt < 3:
            time.sleep(5 * attempt)
            continue
        raise
    except (urllib.error.URLError, TimeoutError, OSError):
        if attempt < 3:
            time.sleep(2 * attempt)
            continue
        raise
else:
    sys.exit("Download failed after 3 attempts")
if len(data) < 10240 or b"%PDF-" not in data[:1024]:
    sys.exit(f"Rejected: {len(data)} bytes and/or missing PDF header - likely an error page")
out.write_bytes(data)
time.sleep(1.0)  # rate limiting between downloads
print(f"Downloaded: {out} ({len(data) // 1024} KB)")
PYEOF
```

After each download:

- Confirm file size > 10 KB and a PDF header (reject smaller/HTML files and warn the user)
- Keep a 1-second delay between consecutive downloads to avoid rate limiting; retry once after 5 seconds on HTTP 429
- Never overwrite an existing PDF at the same path — skip it and report "already exists"
- Report: `Downloaded: papers/2301.07041.pdf (842 KB)`

### Step 5: Summarize

For each paper (downloaded or fetched by API):

```markdown
## [Title]

- **arXiv**: [ID] - [abs_url]
- **Authors**: [full author list]
- **Date**: [published]
- **Categories**: [cs.LG, cs.AI, ...]
- **Abstract**: [full abstract]
- **Key contributions** (extracted from abstract):
  - [contribution 1]
  - [contribution 2]
  - [contribution 3]
- **Local PDF**: papers/[ID].pdf (if downloaded)
```

### Step 6: Project Wiki Hand-Off (optional, if the project provides one)

**Skip silently (no action, no error) unless the project both contains a `research-wiki/` directory and provides its own wiki ingest tool.** No wiki helper ships with minh-agent. When both are present, ingest every paper returned by this invocation through that tool (arXiv ID form when available, otherwise the manual metadata form). Do not hand-write wiki pages; if ingest fails or the tool is absent, report the results as usual and log the gap.

### Step 7: Final Output

Summarize what was done:

- `Found N papers for "query"`
- `Downloaded: papers/2301.07041.pdf (842 KB)` (for each download)
- `Wiki-ingested N papers` (only if a project wiki tool was present and used)
- Any warnings (rate limit hit, file too small, already exists)

Suggest follow-up resources:

```text
${CLAUDE_PLUGIN_ROOT}/resources/research/research-lit/SKILL.md   - multi-source review: Zotero + Obsidian + local PDFs + web
${CLAUDE_PLUGIN_ROOT}/resources/ideas/novelty-check/SKILL.md     - verify an idea is novel against these papers
```

## Key Rules

- Always show the arXiv ID prominently — users need it for citations and reproducibility
- Verify downloaded PDFs: file must be > 10 KB and carry a `%PDF-` header; warn and discard if not
- Rate limit: wait 1 second between consecutive PDF downloads; retry once after 5 seconds on HTTP 429
- Never overwrite an existing PDF at the same path — skip it and report "already exists"
- Handle both arXiv ID formats: new (`2301.07041`) and old (`cs/0601001`)
- PAPER_DIR is created automatically if it does not exist
- If the arXiv API is unreachable, report the error clearly and suggest the web-search path of the bundled research-lit resource as a fallback
- Never fabricate metadata: every field shown must come from the API response or the downloaded PDF

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/arxiv/SKILL.md (MIT). See registry/components.json. -->
