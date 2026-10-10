#!/bin/bash
set -euo pipefail
ORIG_HASH=$(printf '%s' '{"model": "mlp", "val_acc": 0.72, "epochs": 50}' | python3 -c "import hashlib,sys;print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())")
mkdir -p .minh-agent
cat > .minh-agent/state.json <<STATE
{
  "schema_version": 1,
  "run_id": "c0ffeec0ffee",
  "created_at": "2026-10-10T10:00:00Z",
  "updated_at": "2026-10-10T11:00:00Z",
  "goal": "train mlp and report val_acc",
  "mode": "workflow",
  "plugin_version": "0.1.0",
  "workspace_commit": null,
  "constraints": {"max_revision_rounds": 2},
  "current_step": "analyze",
  "completed_steps": [
    {"step": "train", "at": "2026-10-10T10:50:00Z", "evidence": "results.json written"}
  ],
  "artifacts": [{"path": "results.json", "sha256": "$ORIG_HASH", "at": "2026-10-10T10:50:00Z"}],
  "blockers": [],
  "next_action": "analyze results and report val_acc"
}
STATE
# results.json was modified AFTER the checkpoint (external edit)
printf '%s' '{"model": "mlp", "val_acc": 0.79, "epochs": 75}' > results.json
