---
name: c11-figure-csv
description: "C11: figure entry produces a reproducible script from CSV; honest if the plotting backend is missing"
runs: 1
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---
Invoke the minh-agent:figure skill. Create a publication-quality bar chart
comparing baseline vs ours accuracy on the two datasets in plot_data.csv, with
95% CI error bars. Write the plotting script and (if the backend is available)
the figure into this directory. Report the figure contract and the statistics
legend.
