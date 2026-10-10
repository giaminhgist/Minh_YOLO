#!/bin/bash
set -euo pipefail
cat > plot_data.csv <<'MDEOF'
model,dataset,accuracy,ci_low,ci_high
baseline,cifar10,0.71,0.69,0.73
ours,cifar10,0.83,0.81,0.85
baseline,imagenet100,0.64,0.62,0.66
ours,imagenet100,0.74,0.72,0.76
MDEOF
