---
name: c08-experiment-design
description: "C08: experiment entry designs only — protocol with metrics/controls/budget, no execution"
runs: 1
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
---
Invoke the minh-agent:experiment skill. Design (ONLY design — do not run or
install anything) an experiment to test the hypothesis that adding dropout 0.1
to a ResNet-18 trained on CIFAR-10 improves generalization. Resources: one
8-GPU node, 12-hour budget. Produce the protocol: hypothesis, metrics,
controls, seeds, the anti-claim experiment, and budget/stop conditions.
