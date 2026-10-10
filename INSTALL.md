# INSTALL — minh-agent (plugin `minh-agent` @ marketplace `minh-yolo`)

One plugin, one install. Nothing else is required: no upstream clones, no extra
marketplaces, no `~/.claude/skills` provisioning, no global CLAUDE.md overwrite.

## Requirements

- **Claude Code ≥ 2.1.269** (tested on 2.1.296). Older versions lack
  `claude plugin eval` and the current plugin-manifest behavior.
- **Python ≥ 3.9** for the bundled scripts (standard library only).
- Optional per capability — `/minh-agent:doctor` reports what's missing:
  `git` (required by code/debug/review/resume), `pdftotext` (PDF reading),
  `pdflatex` (paper compilation), `matplotlib` (figure rendering),
  `curl` + network (live literature search).

Verified on Linux (2026-10-10, Claude Code 2.1.296, Python 3.12). macOS/Windows
are expected to work for the structure/scripts (stdlib-only, path-robust) but
have **not been executed in this session** — treat as unverified there.

## Install from GitHub (after the refactor release is published)

```bash
claude plugin marketplace add giaminhgist/Minh_YOLO
claude plugin install minh-agent@minh-yolo --scope user
```

Or in one step on Claude Code ≥ 2.1.275:

```
/plugin install minh-agent --marketplace giaminhgist/Minh_YOLO
```

> These two commands require the marketplace to exist on GitHub at
> `giaminhgist/Minh_YOLO` (this repo). Until the maintainer publishes it, use the
> local checkout instructions below.

## Install from a local checkout (works today)

```bash
git clone https://github.com/giaminhgist/Minh_YOLO.git
claude plugin marketplace add ./Minh_YOLO
claude plugin install minh-agent@minh-yolo --scope user
```

`--scope user` makes the plugin available across your projects on this machine.
Account data, API keys, project state, and machine config are never synced by the
plugin — only the plugin files travel.

## Try without installing (one session)

```bash
cd /path/to/Minh_YOLO
claude --plugin-dir ./plugins/minh-agent
```

## Verify

```bash
claude plugin list            # minh-agent … ✔ enabled
/minh-agent:doctor            # installable vs runtime-ready, per-capability tools
python3 plugins/minh-agent/scripts/validate_registry.py   # 5 upstreams · 76 components · 12 entries
```

`doctor` distinguishes "files are all there" (installable) from "required tools
are present" (runtime-ready). Missing optional tools degrade only the listed
capabilities; the plugin never installs anything for you.

## Test the install in isolation first (recommended)

```bash
export CLAUDE_CONFIG_DIR=/tmp/claude-test-config
claude plugin marketplace add giaminhgist/Minh_YOLO   # or a local path
claude plugin install minh-agent@minh-yolo --scope user
claude -p "/minh-agent:doctor"
unset CLAUDE_CONFIG_DIR
```

`CLAUDE_CONFIG_DIR` relocates ALL Claude Code configuration — your real
`~/.claude` is untouched.

## Update / uninstall / rollback

```bash
claude plugin update minh-agent        # newest release of the marketplace entry
claude plugin uninstall minh-agent     # removes the installed plugin
```

- Update a **marketplace entry**: the maintainer edits
  `.claude-plugin/marketplace.json` / bumps `plugin.json` version and releases.
  On your side, refresh the marketplace and update the plugin.
- Rollback: `claude plugin update` tracks the previous version; you can reinstall
  a known-good release by pinning the repo ref
  (`claude plugin marketplace add giaminhgist/Minh_YOLO@<ref>`).
- No configuration is written by the plugin itself: uninstalling removes only
  the plugin files. Project checkpoints (`.minh-agent/`) are per-project and
  yours to keep or delete.

## What install does NOT do

- Does not clone or fetch upstream skill repositories (runtime never downloads
  skill code; everything ships in the plugin).
- Does not write `~/.claude/CLAUDE.md`, `~/.claude/hooks.json`, or agents.
- Does not install Python/Node packages, models, or call paid APIs.
- Does not enable hooks (v1 ships none — see `docs/ARCHITECTURE.md`).

## Coming from the old 12-upstream installer?

The old kit (12 repos, global CLAUDE.md, 20-plugin verify gate) is superseded by
this plugin. See [docs/MIGRATION.md](docs/MIGRATION.md) for a safe migration
path — the old installation is never touched automatically.
