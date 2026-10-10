# MIGRATION — from the old 12-upstream installer to the minh-agent plugin

The old Minh_YOLO was an installer kit: 12 upstream skill repositories copied or
installed into `~/.claude` (≈218 skills, 20 plugins, global CLAUDE.md, trimmed
hooks, a verify gate counting plugins and checkmarks). The new Minh_YOLO is ONE
plugin (`minh-agent`) with curated, provenance-tracked workflows. This guide
moves you to the new model safely. **Nothing here uninstalls or deletes your old
setup automatically** — you choose what to disable.

## 1. Inventory what you have today

Run these and save the output:

```bash
claude plugin list
claude plugin marketplace list
ls ~/.claude/skills 2>/dev/null          # direct-installed skills
ls ~/.claude/agents 2>/dev/null          # toolkit agents
ls ~/.claude/hooks.json 2>/dev/null      # global hooks (old kit trimmed to 9)
ls ~/.claude/CLAUDE.md 2>/dev/null       # old global instructions (old kit replaced this)
ls ~/.claude/upstream 2>/dev/null        # upstream clones (ARIS, OR, …)
ls ~/.aris 2>/dev/null                   # ARIS helper dir
ls ~/.orchestra 2>/dev/null              # OR installer dir
```

## 2. What is yours vs. what the old kit put there

| Path | Origin in the old kit | Advice |
|---|---|---|
| `~/.claude/skills/<name>/` | copied ARIS / OR symlinks / ARF / natureskills / Supervisor-Skills / toolkit skills | You may still use these for other purposes. The new plugin does not depend on them. Remove only after confirming nothing you run still uses them. |
| `~/.claude/upstream/` | 6 upstream clones | Safe to keep or archive. The new plugin never reads them. |
| `~/.claude/plugins/marketplaces/…`, `plugins/cache/…` | plugin-installed upstreams (superpowers 6.4.2, claude-skills, context-engineering, …) | If you use those plugins for non-minh work, keep them. The new plugin bundles its own copies and does not conflict. |
| `~/.claude/CLAUDE.md` | **overwritten by the old kit's Bước 3** (backed up as `CLAUDE.md.bak.<date>` if you used that runbook) | Review and restore your own content; the new kit never touches it. |
| `~/.claude/hooks.json` | toolkit installer's 25 hooks, trimmed to 9 by `configure_hooks.py` (backup `hooks.json.bak-toolkit-full`) | Review which hooks you actually want. The new plugin ships no hooks, so it needs none of these. |
| `~/.claude/agents/*.md` | 3 toolkit agents | Keep if you use them; unrelated to the new plugin. |
| `~/.claude/skills/research-orchestrator/` | old orchestrator + SKILL_INDEX + verify_install.py | Superseded. See §4. |

Do not infer ownership from file names alone — you may have used Superpowers or
ARIS directly for other purposes. Only remove what you are sure you installed
via the old kit's runbook and no longer use.

## 3. Install the new plugin in isolation first

```bash
export CLAUDE_CONFIG_DIR=/tmp/minh-test
claude plugin marketplace add giaminhgist/Minh_YOLO    # or: <path-to-checkout>
claude plugin install minh-agent@minh-yolo --scope user
claude -p "/minh-agent:doctor"
unset CLAUDE_CONFIG_DIR
```

Nothing about your real `~/.claude` changes in this test. When satisfied, repeat
without `CLAUDE_CONFIG_DIR` for the real install.

## 4. Superseded pieces of the old kit

- **`research-orchestrator/SKILL.md` + `SKILL_INDEX.md`** — routing logic moved
  into the 12 entry skills + `registry/capabilities.json`. The installed copies
  under `~/.claude/skills/research-orchestrator/` are dead weight for the new
  flow; delete when you no longer need the old routing (its rules routed to
  hardcoded `~/.claude` paths that the plugin no longer uses).
- **`verify_install.py`** (20 plugins / 218 skills / `✔` counting) — replaced by
  `/minh-agent:doctor` and `validate_registry.py`, which check real structure
  and behavior.
- **`configure_hooks.py`** — the new kit ships no hooks; if you keep the old
  hooks for other tools, manage them yourself (`--full` restores the backup).

## 5. Optional: disable overlapping pieces (only what you choose)

- Old plugins that only served the old kit (e.g. `superpowers@superpowers-marketplace`
  installed purely for SKILL_INDEX paths): `claude plugin disable <plugin>` is
  reversible — prefer disable over uninstall while you evaluate.
- Old `~/.claude/CLAUDE.md`: restore your backup or start from your own content.
  The plugin carries its instructions in its own skills; it does not need
  global instructions to work.

## 6. Rollback

The old kit's state lives in git history of this repository (commit
`716b86e` and earlier) and in your `~/.claude` backup files. To go back:
uninstall the plugin (`claude plugin uninstall minh-agent`), remove the
marketplace entry (`claude plugin marketplace remove minh-yolo`), and re-apply
the old runbook from the old checkout. The new plugin writes no global config,
so removal is complete by design.

## 7. Data that carries over

Project-level work (results, papers, experiment logs, git repos) is yours and
unchanged. If you used the old ARIS helpers (`~/.aris/repo`), those are ARIS
state — the new plugin keeps its own state per project in `.minh-agent/`
(git-ignored). Syncing checkpoints between machines remains your choice, not an
automatic plugin feature.
