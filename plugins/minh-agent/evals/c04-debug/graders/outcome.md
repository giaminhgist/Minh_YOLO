---
type: llm
weight: 2
---
PASS if the response: (1) reproduces the failure with real test output, (2) identifies the root cause with evidence (the off-by-one denominator in stats.py), (3) applies a single minimal fix, (4) shows the tests passing afterward.
FAIL if the response proposes fixes without reproduction, fixes the symptom/test, or reports success without fresh test output.
