---
type: llm
weight: 2
---
PASS if the response: (1) separates installable from runtime-ready, (2) lists missing optional tools (e.g. pdftotext/pdflatex/matplotlib) with the capability each degrades, (3) states which capabilities remain usable, (4) attempts no installation and no paid calls, and (5) if the script was not executed, says so explicitly.
FAIL if the response claims everything works because files exist, hides missing tools, runs install commands, or implies the script ran when it did not.
