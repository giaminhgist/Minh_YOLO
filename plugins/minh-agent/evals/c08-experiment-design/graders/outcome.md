---
type: llm
weight: 2
---
PASS if the response contains a design-only protocol with: (1) ONE pre-registered primary metric, (2) ≥3 fixed seeds (DEFAULT_SEEDS=3) reported as mean±std, (3) a baseline (no-dropout ResNet-18) under the same protocol/splits/seeds, (4) an anti-claim experiment designed to rule out the mechanism, (5) budget + stop conditions consistent with 12h/8-GPU, (6) no training/execution performed.
FAIL if the response runs anything, omits controls or the budget, or proposes a single favorable seed as the result.
