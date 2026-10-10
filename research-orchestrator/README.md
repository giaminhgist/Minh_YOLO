# research-orchestrator — SUPERSEDED by the minh-agent plugin

The old orchestrator of the 12-upstream install kit (SKILL.md, SKILL_INDEX.md,
verify_install.py, configure_hooks.py) has been removed from the working tree —
it lives in git history (commit `716b86e` and earlier). The new distribution is
the **minh-agent plugin**:

- Routing → `plugins/minh-agent/skills/run/SKILL.md` + `registry/capabilities.json`
- Modes (STANDALONE/WORKFLOW) → `plugins/minh-agent/skills/run/SKILL.md` + `scripts/state.py`
- Verification gate (20 plugins / 218 skills / checkmark counting) →
  `plugins/minh-agent/scripts/doctor.py` + `scripts/validate_registry.py`
- Global hook trimmer → removed; the plugin ships no hooks (v1)

Install via `claude plugin marketplace add giaminhgist/Minh_YOLO` per
[INSTALL.md](../INSTALL.md). If you installed the old kit, see
[docs/MIGRATION.md](../docs/MIGRATION.md).
