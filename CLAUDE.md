# CLAUDE.md — Minh_YOLO (contributor guide)

This repository distributes **minh-agent**, a single Claude Code plugin with
curated research + coding workflows. This file guides work ON the repo — it is a
project instruction file, NOT a global config: the installer never copies it to
`~/.claude/CLAUDE.md`.

## Layout

```
.claude-plugin/marketplace.json   marketplace "minh-yolo" — exactly one plugin entry
plugins/minh-agent/               the shippable plugin (runtime must be self-contained here)
  skills/  resources/  registry/  scripts/  agents/  evals/  licenses/
scripts/                          maintainer tools (fetch_upstreams, build_registry,
                                  rehash_components, package)
tests/                            stdlib unittest suites
docs/                             ARCHITECTURE, MIGRATION, MAINTAINING_UPSTREAMS, IMPLEMENTATION_REPORT
.cache/upstreams/                 maintainer-only upstream checkouts (git-ignored, never shipped)
```

## Invariants (do not break these)

1. **Exactly five direct upstreams** — `registry/upstreams.lock.json` holds the
   allowlist with full commit SHAs. Adding a sixth source, or a runtime fetch of
   skill code, is a design violation. Runtime dependencies on the maintainer
   cache, `~/.claude`, or versioned cache paths are bugs
   (`validate_registry.py` + `grep` scans enforce this).
2. **Provenance rule** — every shipped file derived from an upstream is a
   component in `registry/components.json` (origin_kind, source_path, revision,
   license, mode verbatim/adapted, local_changes, sha256). After editing any
   registered file: `python3 scripts/rehash_components.py` then
   `python3 plugins/minh-agent/scripts/validate_registry.py`.
3. **12 entry skills** — `skills/<name>/SKILL.md` with frontmatter
   `name: <name>` + description. The namespace is `/minh-agent:<name>`.
   New capabilities go through `registry/capabilities.json` too.
4. **STANDALONE default** — entries never auto-expand scope; workflows only on
   explicit request with recorded budget/stop conditions (state.py).
5. **No hooks in v1** — any future hook needs a smoke test proving it fires.

## Development loop

```bash
python3 -m unittest discover -s tests -v                      # unit tests (no model calls)
python3 plugins/minh-agent/scripts/validate_registry.py       # registry/structure gate
python3 plugins/minh-agent/scripts/doctor.py                  # installable vs runtime-ready
claude plugin validate . --strict && claude plugin validate ./plugins/minh-agent --strict
claude --plugin-dir ./plugins/minh-agent                      # try it in a session
claude plugin eval . --scaffold --trust-plugin \
  --allow-tools "Write" "Edit" "Bash(*)"                     # behavior evals (model-backed, costs tokens)
```

Test installs against the real `~/.claude`: never. Use
`CLAUDE_CONFIG_DIR=/tmp/<scratch> claude plugin marketplace add <path>` instead.

## Updating an upstream component

See `docs/MAINTAINING_UPSTREAMS.md`. Short form: fetch the new revision
(`scripts/fetch_upstreams.py --revision <id>=<sha>`), diff against the current
pin, adapt deliberately, update provenance + local_changes, rehash, revalidate,
run the affected evals, bump `plugin.json` version, and only then release.

## Conventions

- Scripts: Python ≥ 3.9, stdlib only, no network at runtime, never install
  packages, never call paid APIs. Paths must survive spaces/Unicode.
- Evidence discipline: no claim of "works" without the fresh output that proves
  it; test output is shown, not asserted. Never fabricate results, citations,
  SHAs, or license info.
- Keep a visible task checklist for multi-step work.
- Don't push/merge/publish without authorization in the session.
