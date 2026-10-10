# Minh_YOLO — the `minh-agent` plugin for Claude Code

A single Claude Code plugin that ships curated research + coding workflows for
AI/ML/DL/CV/biomedical researchers. One install; no upstream skill repositories
to clone, no marketplaces to stack, nothing downloaded at runtime.

- **Plugin:** `minh-agent` · **Marketplace:** `minh-yolo` (this repository)
- **12 entry skills** with direct slash namespaces: `/minh-agent:run`,
  `/minh-agent:plan`, `/minh-agent:code`, `/minh-agent:debug`, `/minh-agent:review`,
  `/minh-agent:research`, `/minh-agent:read`, `/minh-agent:experiment`,
  `/minh-agent:write`, `/minh-agent:figure`, `/minh-agent:resume`,
  `/minh-agent:doctor`
- **STANDALONE is the default.** Each entry does exactly the requested task.
  Multi-step workflows run only when explicitly requested, with recorded state,
  budget, and stop conditions (see `/minh-agent:run`).
- **Provenance-tracked content.** Workflows are selected and adapted from exactly
  five pinned upstream skill repositories (ARIS, superpowers, Orchestra-Research,
  claude-skills, Context Engineering — see `THIRD_PARTY_NOTICES.md` and
  `plugins/minh-agent/registry/`). Every component records source, revision,
  license, and local changes. Runtime never fetches skill code.

## Install

```bash
claude plugin marketplace add giaminhgist/Minh_YOLO
claude plugin install minh-agent@minh-yolo --scope user
```

One line on Claude Code ≥ 2.1.275:

```
/plugin install minh-agent --marketplace giaminhgist/Minh_YOLO
```

Try it without installing (this session only):

```bash
claude --plugin-dir ./plugins/minh-agent
```

Then `/minh-agent:doctor` to check your environment. Full instructions (local
install, update, uninstall, rollback, requirements) in [INSTALL.md](INSTALL.md).

## What each entry does

| Entry | Use for | Output |
|---|---|---|
| `run` | anything unclassified; workflow orchestration when explicitly asked | one primary workflow, executed and verified |
| `plan` | design/spec/implementation plan before code | reviewable plan with per-task verification; no code changed |
| `code` | implement a feature/refactor/fix | code + test evidence; surgical scope |
| `debug` | bug/error/test failure | root cause + fix + regression proof |
| `review` | review a diff/PR/branch | severity-ranked findings with location + evidence; never fixes |
| `research` | literature questions, novelty, ideas | sourced synthesis; fact/inference/gap separated |
| `read` | deep reading of a supplied document | claims/evidence/limits of what was actually read |
| `experiment` | design (default) or run/analyze experiments | protocol with controls/budget; real saved results when run |
| `write` | papers, grants, technical docs from evidence | evidence-gated draft; missing parts marked, never invented |
| `figure` | scientific figures from your data | figure + reproducible script + statistics legend |
| `resume` | continue a previous run | checkpoint reconciled with workspace; stale parts re-verified |
| `doctor` | plugin health | installable vs runtime-ready verdicts |

## Requirements

- Claude Code ≥ 2.1.269 (plugin manifest, `claude plugin` commands; tested on
  2.1.296). Python ≥ 3.9 for the bundled scripts (stdlib only).
- Optional tools per capability (declared, never auto-installed): `git`
  (required for code/debug/review/resume), `pdftotext` (PDF reading),
  `pdflatex` (paper compilation), `matplotlib` (figure rendering),
  network + `curl` (live literature search). `/minh-agent:doctor` tells you
  exactly which capability degrades when one is missing.

## Repo layout

```
.claude-plugin/marketplace.json      marketplace "minh-yolo" (one plugin)
plugins/minh-agent/                  the plugin
  skills/<entry>/SKILL.md            12 entry skills
  resources/<capability>/            curated workflows (provenance-tracked)
  registry/                          upstreams.lock.json · components.json · capabilities.json
  scripts/                           state.py · doctor.py · validate_registry.py
  agents/reviewer.md                 fresh-context reviewer
  evals/                             behavior eval suite for `claude plugin eval`
  licenses/ · THIRD_PARTY_NOTICES.md
scripts/                             maintainer tools (fetch, merge, rehash, package)
tests/                               unit tests (stdlib unittest)
docs/                                architecture, migration, maintaining, report
```

Developers: see [CLAUDE.md](CLAUDE.md). Previously installed the old multi-upstream
kit? See [docs/MIGRATION.md](docs/MIGRATION.md).
