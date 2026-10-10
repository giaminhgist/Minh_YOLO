# MAINTAINING UPSTREAMS — provenance, selective updates, rollback

minh-agent ships curated content from exactly five upstream skill repositories.
This file is the maintainer playbook for keeping them correct over time.

## The five sources (allowlist)

Locked in `plugins/minh-agent/registry/upstreams.lock.json` with full commit
SHAs. IDs: `aris`, `superpowers`, `orchestra`, `claude_skills`,
`context_engineering`. Adding any other skill source — via the installer, the
marketplace, a runtime fetch, or a hidden dependency — is a design violation.

## Directory and tooling

- Maintainer cache: `.cache/upstreams/<id>/` (git-ignored). Fetch with
  `python3 scripts/fetch_upstreams.py` — verifies each pinned SHA against
  GitHub and refreshes license metadata in the lock. Use
  `--revision <id>=<full-sha>` to test a new revision without touching the lock
  until you're sure.
- Curation: adapt selected files into `plugins/minh-agent/resources/<capability>/<component>/`
  following the rules in §3, record each file as a component fragment, and merge
  with `python3 scripts/build_registry.py --fragments <dir>`.
- After ANY edit to a registered file: `python3 scripts/rehash_components.py`,
  then `python3 plugins/minh-agent/scripts/validate_registry.py` and
  `python3 plugins/minh-agent/scripts/doctor.py`.

## Component rules (enforced by the validator)

1. Every shipped file derived from an upstream is a component with:
   `component_id`, `capability`, `origin_kind` (`upstream`|`native`),
   `upstream_id`, `source_path`, `revision`, `license`, `local_path`,
   `sha256`, `mode` (`verbatim`|`adapted`|`reference`), `dependencies`,
   `local_changes`. Native components leave upstream fields `null`.
2. Adapted files keep: decision gates, error conditions, thresholds,
   verification criteria. Remove: upstream install/marketplace machinery,
   hardcoded paths (`~/.claude`, `.aris`, versioned cache paths), references to
   unbundled skills (rewrite as native instructions or mark out of scope).
   Record what changed in `local_changes` — "optimized" is not a note.
3. Every file the adapted text tells the model to read or run must be bundled
   (and registered). A reference to an unbundled skill is a broken dependency.
4. Provenance line as the LAST line of each file:
   `<!-- Source: <repo-url> @ <full-sha>, path <path> (MIT). See registry/components.json. -->`
   (adapted files) — verbatim copies get the same line appended.
5. License: keep the upstream LICENSE verbatim in `licenses/<id>-LICENSE.txt`.
   Check for third-party content inside upstream files (LaTeX classes under
   LPPL, Apache-2.0 patterns) — do not ship LPPL class files; record other
   third-party material in `local_changes` and `THIRD_PARTY_NOTICES.md`.
6. Runtime independence: the installed plugin never touches the maintainer
   cache or network for skill code. Scan before release:
   `grep -rnE '\.cache/upstreams|MINH_UPSTREAM_CACHE|~/.claude|\.aris' plugins/minh-agent/`
   (registry JSON metadata excepted).

## Updating one source (one at a time)

1. `python3 scripts/fetch_upstreams.py --revision <id>=<new-sha>` — inspect the
   diff between the new tree and the pinned one:
   `git -C .cache/upstreams/<id> diff <old-sha> FETCH_HEAD --stat`.
2. Decide per affected component: keep pinned (no change), update verbatim
   (copy new content, keep provenance), or re-adapt (deliberate changes, new
   `local_changes` note). Never blanket-sync; never auto-update at runtime.
3. Update the lock (`revision`, `verified_at`), rebuild components hashes,
   revalidate, run the unit tests and the evals that exercise the affected
   entries.
4. Bump `plugins/minh-agent/.claude-plugin/plugin.json` `version`
   (semver: patch for fixes, minor for content updates that change behavior).
   Keep marketplace entry and plugin.json versions consistent
   (`claude plugin validate . --strict` warns on drift).
5. Release: commit + tag. Tag with `claude plugin tag` so installers can pin
   a known-good release.

## Rollback

- Users: `claude plugin update minh-agent` tracks the previous version;
  pinning via `giaminhgist/Minh_YOLO@<ref>` restores an older release.
- Maintainer: revert the lock + components + resources to the last good commit;
  the git history IS the release history — keep it clean and tagged.

## Refresh vs update

- **Marketplace refresh** (your side): re-fetch the marketplace manifest to see
  new versions (`claude plugin marketplace` commands). Does not change the
  installed plugin.
- **Plugin update**: `claude plugin update minh-agent` applies the new version
  (restart required). These are two distinct operations; document both.

## Release checklist

- [ ] `python3 -m unittest discover -s tests -v` green
- [ ] `python3 plugins/minh-agent/scripts/validate_registry.py` PASS
- [ ] `python3 plugins/minh-agent/scripts/doctor.py` installable
- [ ] `claude plugin validate . --strict` + `claude plugin validate ./plugins/minh-agent --strict` PASS
- [ ] forbidden-path scan clean
- [ ] affected evals re-run (`claude plugin eval . --scaffold --trust-plugin --allow-tools "Write" "Edit" "Bash(*)"`)
- [ ] version bumped; marketplace/plugin versions consistent
- [ ] push/publish authorized in the session
