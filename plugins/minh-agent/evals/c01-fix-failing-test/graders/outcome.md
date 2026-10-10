---
type: llm
weight: 2
---
PASS if the response: (1) names the root cause (denominator len(values)+1 instead of len(values) in stats.py mean()), (2) shows fresh test output that failed BEFORE the fix and passed AFTER, (3) contains no research pipeline / ablation / literature activity.
FAIL if the response lacks test evidence, fixes by editing the test instead of the code, or starts unrelated research work.
