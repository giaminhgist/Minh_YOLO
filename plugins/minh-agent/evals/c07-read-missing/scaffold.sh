#!/bin/bash
set -euo pipefail
cat > local_paper.md <<'MDEOF'
# On Weight Decay in Small MLPs

**Abstract.** We study whether weight decay improves generalization of a
two-layer MLP trained on MNIST. We train with weight decay 1e-4 and 1e-2 and
argue that decay mainly reduces overfitting of the top layer.

**Method.** Two-layer MLP (784-256-10), Adam, batch size 128, 20 epochs,
3 seeds. Weight decay applied to all weights.

**Results.** Mean test accuracy over 3 seeds: 97.1% (decay 1e-4), 97.6%
(decay 1e-2), 96.8% (no decay). The paper reports no confidence intervals.

**Discussion.** The authors claim decay "significantly improves"
generalization, but report no statistical test and the absolute differences
are under one point.
MDEOF
