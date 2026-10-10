# FigureSpec: Deterministic JSON → SVG Figure Generation

When this resource is used: when the user wants architecture diagrams, workflow/pipeline figures, audit cascades, or system topology as editable vector graphics — "架构图", "workflow 图", "pipeline 图", "确定性矢量图", "figure spec", "draw architecture", or any structured diagram where node positions and connections matter. Preferred over AI illustration for formal architecture/workflow figures.

## Context: $ARGUMENTS

Arguments: `[description-of-diagram]`.

Generate publication-quality **architecture diagrams**, **workflow pipelines**, **audit cascades**, and **system topology** figures as editable SVG vector graphics using a deterministic JSON → SVG renderer.

## When to Use This Resource

**Use `figure-spec`** for:

- System architecture diagrams (layered, hub-and-spoke, multi-plane)
- Workflow / pipeline figures
- Audit cascade / flow-control diagrams
- Any structured diagram where node positions, connections, and groupings are semantically important
- Figures that need to be edited/tweaked later (SVG is plain text)
- Figures where determinism matters (same spec → same SVG)

**Do NOT use for:**

- Data plots (bar/line/scatter) — use the `paper-figure` resource
- Natural/qualitative illustrations — out of scope (no illustration resource is bundled)
- Quick state-machine / flowchart — no lighter diagram resource is bundled; a simple flowchart is usually faster hand-written in TikZ

## Core Properties

- **Deterministic**: identical FigureSpec JSON always produces identical SVG output (for a fixed renderer version + fonts)
- **Editable**: SVG output is plain-text, can be post-edited by hand or programmatically
- **Validated**: renderer enforces schema, rejects malformed specs with clear error messages
- **Shape-aware**: edge clipping works correctly for rect/rounded/circle/ellipse/diamond
- **CJK support**: multi-line labels with proper Chinese character width estimation
- **No external API**: runs fully local, no network, no API keys

## Tool Location

The renderer is bundled with this resource at:

```
${CLAUDE_PLUGIN_ROOT}/resources/figures/figure-spec/scripts/figure_renderer.py
```

Python 3 standard library only — no installation, no network. Resolve it once per session:

```bash
FIGURE_RENDERER="${CLAUDE_PLUGIN_ROOT}/resources/figures/figure-spec/scripts/figure_renderer.py"
```

If `$CLAUDE_PLUGIN_ROOT` is somehow unset, locate the plugin root before falling back to nothing — do **not** silently continue without the renderer: a figure spec that cannot be rendered cannot be delivered as a figure.

```bash
if [ ! -f "$FIGURE_RENDERER" ]; then
  echo "ERROR: figure_renderer.py not found at $FIGURE_RENDERER." >&2
  echo "       figure-spec cannot produce SVG output. Report this instead of hand-writing an 'SVG'." >&2
  exit 1
fi
```

Invoke:

```bash
python3 "$FIGURE_RENDERER" render <spec.json> --output <out.svg>
python3 "$FIGURE_RENDERER" validate <spec.json>
python3 "$FIGURE_RENDERER" schema
```

The optional `--preview` flag converts the SVG to PNG via the local `rsvg-convert` (or `cairosvg`); absent both, the renderer warns and the SVG remains the deliverable. That conversion is a local convenience only — never a network call.

## Workflow

### Step 1: Understand the Diagram Goal

From `$ARGUMENTS` (description or path to `PAPER_PLAN.md` / `NARRATIVE_REPORT.md`), identify:

- **Purpose**: architecture, workflow, pipeline, audit cascade, topology?
- **Main entities**: what are the boxes?
- **Relationships**: how do they connect? (uses, produces, calls, verifies, chains)
- **Grouping**: do entities cluster into named regions?
- **Hierarchy vs network**: stacked layers, left-to-right flow, or central hub?

### Step 2: Draft the FigureSpec JSON

Canvas sizing guide:

- Single-column figure: ~500×350 px
- Two-column (full-width): ~900×500 px
- Tall topology: ~700×700 px

Start from a template based on the diagram type:

**Architecture (stacked rows)**:

```json
{
  "canvas": {"width": 900, "height": 520},
  "nodes": [
    {"id": "layer1_label", "label": "Layer 1", "x": 450, "y": 60},
    {"id": "node_a", "label": "A", "x": 180, "y": 120},
    {"id": "node_b", "label": "B", "x": 350, "y": 120}
  ],
  "edges": [],
  "groups": [
    {"label": "Layer 1", "node_ids": ["node_a", "node_b"], "fill": "#F0F9FF", "stroke": "#BAE6FD"}
  ]
}
```

**Workflow (left-to-right chain)**:

```json
{
  "canvas": {"width": 900, "height": 300},
  "nodes": [
    {"id": "step1", "label": "Step 1", "x": 100, "y": 150, "shape": "rounded"},
    {"id": "step2", "label": "Step 2", "x": 280, "y": 150, "shape": "rounded"}
  ],
  "edges": [
    {"from": "step1", "to": "step2", "label": "produces"}
  ]
}
```

**Decision diamond**:

```json
{"id": "check", "label": "Passes?", "shape": "diamond", "x": 450, "y": 200}
```

Save the spec in `figures/specs/` next to the output so the figure is reproducible.

### Step 3: Render and Validate

```bash
# Validate first
python3 "$FIGURE_RENDERER" validate figures/specs/fig_arch.json

# Render to SVG
python3 "$FIGURE_RENDERER" render figures/specs/fig_arch.json --output figures/fig_arch.svg

# Convert to PDF for LaTeX inclusion (requires local rsvg-convert)
rsvg-convert -f pdf figures/fig_arch.svg -o figures/fig_arch.pdf
```

If validation fails, inspect the error (missing field, duplicate ID, overlap warning, invalid hex color) and fix the JSON. If `rsvg-convert` is not installed, deliver the SVG and say the PDF conversion needs a local SVG→PDF tool — do not rasterize silently.

### Step 4: Visual Review

Open the SVG/PDF and check:

- **No overlaps**: nodes don't collide with each other or group boundaries
- **Readability**: font sizes are consistent, labels aren't clipped
- **Edge clarity**: arrows hit nodes at clean angles, labels near edges are legible
- **Group alignment**: background rectangles frame their members cleanly
- **Color distinction**: categories are visually distinct in both color and grayscale

If issues found, edit the JSON spec (never the generated SVG) and re-render.

### Step 5: Iterate with Cross-Model Review (Optional, for High-Stakes Figures)

For paper architecture figures, invoke cross-model review when a reviewer backend is available:

```
Review this SVG figure for a technical paper (architecture / workflow diagram).

Spec file: /path/to/spec.json
Rendered: /path/to/fig.svg

Evaluate:
1. Clarity (C): can a reader understand the system from this figure alone?
2. Readability (R): font sizes, label placement, visual hierarchy
3. Semantic accuracy (S): do relationships match the described system?

Score each axis 1-10 and list specific issues to fix.
```

When the backend is available, iterate until all three axes ≥ 7/10. This is a single review-and-fix pass per round on a specific figure — not something to schedule or loop in the background.

> ⚠️ **Reviewer-backend fallback**: if no cross-model reviewer backend is available, skip the external review and record `REVIEW_UNAVAILABLE`. You may still run the same three-axis rubric as a **labeled, non-independent self-review** (self-check the rendered SVG against C/R/S and fix what it finds), and the figure is delivered normally. Never present a same-model self-score as an independent review, and never invent reviewer scores.

## Schema Quick Reference

Run `python3 "$FIGURE_RENDERER" schema` for the authoritative schema.

### Nodes

| Field | Required | Default | Notes |
|-------|----------|---------|-------|
| `id` | ✓ | — | Unique |
| `label` | ✓ | — | `\n` for multi-line |
| `x`, `y` | ✓ | — | Center coordinates |
| `width`, `height` | | 120, 50 | |
| `shape` | | `rounded` | `rect` / `rounded` / `circle` / `ellipse` / `diamond` |
| `fill`, `stroke` | | auto from palette | `#RRGGBB` |
| `text_color` | | `#333333` | |
| `font_size` | | 14 | Override style default |

### Edges

| Field | Default | Notes |
|-------|---------|-------|
| `from`, `to` | required | Same = self-loop |
| `label` | — | Short edge label |
| `style` | `solid` | `solid` / `dashed` / `dotted` |
| `color` | `#555555` | |
| `curve` | `false` | Curved path |

### Groups

Rectangular background regions framing a set of nodes:

```json
{"label": "Layer Name", "node_ids": ["a", "b", "c"], "fill": "#EFF6FF", "stroke": "#BFDBFE"}
```

## Design Patterns

### Pattern 1: Layered Architecture

Stack rows of related nodes, each row is a group, add inter-layer arrows with semantic labels (`uses↓`, `produces↑`, `checks↓`).

### Pattern 2: Hub-and-Spoke

Central node (e.g., Executor), peripheral nodes (skills, tools), solid arrows for primary relations, dashed for feedback.

### Pattern 3: Pipeline with Feedback

Left-to-right main flow, feedback arrows curve below with `curve: true`.

### Pattern 4: Audit Cascade

Three-stage horizontal cascade with inputs feeding in from top, outputs exiting right, each stage in its own group.

## Anti-Patterns

- **Don't use groups as hierarchy**: groups frame peer nodes, not containment
- **Don't nest groups**: renderer draws them as background rectangles; nested groups look like Russian dolls
- **Don't cross-draw long diagonals**: if an arrow crosses 3+ rows, rethink the layout
- **Don't mix font sizes for same role**: keep one size per node category

## Output Contract

- SVG file in `figures/` (vector, editable, hand-tweakable)
- Source FigureSpec JSON saved in `figures/specs/` for reproducibility
- PDF version via `rsvg-convert` for LaTeX inclusion (local tool required)

## Integration with Other Resources

- **`paper-figure`** (`${CLAUDE_PLUGIN_ROOT}/resources/figures/paper-figure/SKILL.md`): handles data plots; they complement each other (data + architecture = complete figure set)
- **`paper-write`**: when the paper plan marks an architecture figure `[MANUAL]`, route it here if the diagram is structured (blocks + arrows); freeform art stays manual
- Out of scope: AI illustration (no such resource bundled), Mermaid-style lightweight flowcharts (hand-write in TikZ or spec them here)

## Review Tracing

After each cross-model reviewer call, save a trace under `.minh-agent/traces/figure-spec/<date>_run<NN>/` containing the exact prompt sent, the raw response, and the resolved reviewer model and reasoning effort. Never silently skip the trace; if a trace cannot be written, say so in the report instead of pretending it exists. A trace never contains credentials or API keys.

<!-- Source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git @ 26b95cfa0d8747078e9e43b42e20952709e561b8, path skills/figure-spec/SKILL.md (MIT). See registry/components.json. -->
