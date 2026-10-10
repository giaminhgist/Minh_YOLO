#!/bin/bash
set -euo pipefail
cat > results_incomplete.json <<'MDEOF'
{
  "experiment": "vit-b16 pretraining",
  "seeds": [1, 2, 3],
  "results": {
    "seed1": {"val_acc": 0.812, "epochs_run": 90},
    "seed2": {"val_acc": 0.804, "epochs_run": 90},
    "seed3": {"val_acc": "PENDING", "epochs_run": null}
  },
  "baseline": {"val_acc": 0.775},
  "notes": "seed3 still training"
}
MDEOF
