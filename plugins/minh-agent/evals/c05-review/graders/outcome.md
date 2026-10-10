---
type: llm
weight: 2
---
PASS if the response reports at least TWO of these three planted bugs, each with its location in calc.py and a severity: (1) divide() lost its zero-division guard, (2) discount() now ADDS the percentage instead of subtracting it (sign flipped), (3) total() raises KeyError when an item lacks a "price" key.
FAIL if the response invents unrelated findings, finds none of the planted bugs, or fixes the code despite the review-only instruction.
