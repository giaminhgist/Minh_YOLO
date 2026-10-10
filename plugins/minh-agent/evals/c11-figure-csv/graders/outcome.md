---
type: llm
weight: 2
---
PASS if the response: (1) writes a reproducible plotting script that reads plot_data.csv, (2) uses the real CSV values (cifar10: 0.71 vs 0.83; imagenet100: 0.64 vs 0.74) with error bars from ci_low/ci_high, (3) names a backend gate (Python/R) rather than silently picking one, (4) provides a caption/statistics legend (n, center, spread, CI, source file), AND either produces the figure file or honestly states the plotting backend (matplotlib) is not installed in this environment.
FAIL if the response invents data, plots values that don't match the CSV, or silently produces nothing without a script.
