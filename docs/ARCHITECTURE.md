# ARCHITECTURE — minh-agent

minh-agent is one Claude Code plugin distributed through one marketplace
(`minh-yolo`). No agent runtime of its own, no daemon, no background runner:
workflows are finite in-session sequences coordinated by instructions and a
small state manager.

## Three layers

1. **Entry skills (native, by Minh)** — `plugins/minh-agent/skills/<name>/SKILL.md`,
   the 12 public gates (`run`, `plan`, `code`, `debug`, `review`, `research`,
   `read`, `experiment`, `write`, `figure`, `resume`, `doctor`). Each declares
   its trigger, input contract, resources to load, output contract, and
   missing-tool behavior. Namespaced `/minh-agent:<name>`.
2. **Curated workflows (upstream, provenance-tracked)** —
   `plugins/minh-agent/resources/<capability>/<component>/`, selected and
   adapted from five pinned upstreams. Every file is a component in
   `registry/components.json` (source path, revision, license, mode, hash,
   local changes). Resources are read on demand — never preloaded.
3. **Coordination layer (native)** — `registry/capabilities.json` (entry →
   workflow → resources/tools/outputs), `scripts/state.py` (per-project
   checkpoints), `scripts/doctor.py` + `scripts/validate_registry.py`
   (health and integrity gates), `agents/reviewer.md` (fresh-context reviewer).

## Modes

- **STANDALONE (default):** one requested task to a reasonable completion.
  "Read this paper" never escalates into review → experiment → paper.
- **WORKFLOW (explicit request only):** recorded before starting — goal, step
  list, budget, stop conditions — via `state.py init --mode workflow`. Stop
  conditions: goal reached, limits exhausted, real blocker, user says stop.
  Default budget suggestion: ≤ 2 revision rounds per step, no parallel agents
  unless asked, no external spend. A workflow is a finite in-session sequence.

## State and resume

- State lives in `<project>/.minh-agent/` — always inside the project
  (confinement by construction), created only when a task has continuation
  value or the user initializes it.
- `state.json` (schema_version, run_id, goal, mode, plugin version, workspace
  commit, constraints, steps, artifacts with hashes, blockers, next action) +
  `HANDOFF.md` (human-readable mirror). Atomic writes (`os.replace`), corrupt
  JSON and schema-mismatch handling, a pid-checked run lock.
- `/minh-agent:resume` reconciles the checkpoint with git and file hashes;
  stale artifacts force re-verification of the steps that depended on them.
  Two projects never share a run.

## Review independence (honest labels)

- Fresh-context subagent review (plugin's `reviewer` agent) — the default for
  review gates.
- Self-review — labeled as such, always weaker.
- Cross-model review — claimed only when a genuinely different backend ran and
  returned findings; otherwise `REVIEW_UNAVAILABLE`. Never fabricated.

## Hooks, agents, runtime constraints

- **No hooks in v1** (acceptance B07 = NOT_APPLICABLE). A future hook needs a
  smoke test proving it fires.
- One agent: `reviewer` (fresh-context review gate). No multi-agent fan-out by
  default.
- Scripts: Python ≥ 3.9 stdlib-only, no network, no installs, no paid calls,
  robust to spaces/Unicode paths. `${CLAUDE_PLUGIN_ROOT}`-relative resources;
  nothing reads the maintainer cache or upstream checkouts.
- Optional tools are declared per capability (`doctor` reports): git, pdftotext,
  pdflatex, matplotlib, curl/network.

## Registry (internal convention, not magic)

`registry/` is read by the entry skills and the validator scripts. Claude Code
does not treat it as a router on its own; a JSON file cannot constrain model
behavior by itself — the entries and the scripts do that. The validator enforces
the allowlist (exactly five upstreams, full SHAs), component provenance/hashes,
and capability→resource mapping.

## Distribution

- Marketplace manifest: `.claude-plugin/marketplace.json` (repo root) — one
  plugin entry, source `./plugins/minh-agent`.
- Plugin manifest: `plugins/minh-agent/.claude-plugin/plugin.json`.
- Install: `claude plugin marketplace add giaminhgist/Minh_YOLO` +
  `claude plugin install minh-agent@minh-yolo --scope user`. Local try-out:
  `claude --plugin-dir ./plugins/minh-agent`. Isolated test installs use
  `CLAUDE_CONFIG_DIR`.
- Version bump: `plugin.json` only; keep marketplace/plugin versions consistent
  (see docs/MAINTAINING_UPSTREAMS.md).
