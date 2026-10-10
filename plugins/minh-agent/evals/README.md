# minh-agent eval suite

Behavioral cases for `claude plugin eval` (Claude Code ≥ 2.1.269). Each case is a
realistic prompt + graders, run in an isolated session with only this plugin
loaded. Model-backed — costs tokens; not part of CI.

## Run

```bash
cd plugins/minh-agent
claude plugin eval . --scaffold --trust-plugin \
  --allow-tools "Write" "Edit" "Bash(*)"
```

- `--scaffold` runs each case's `scaffold.sh` (creates the fixture workspace).
  It executes as you — only use it on cases you authored (these are).
- `--trust-plugin` answers the untrusted-plugin confirmation for CI.
- `--allow-tools` grants the gated tools the cases need (Bash requires the OS
  sandbox: bubblewrap + socat on Linux).
- Results: `evals/results/<timestamp>/aggregate-result.json` + `report.html`
  (git-ignored).

## Cases (acceptance mapping)

| Case | Criterion | What it proves |
|---|---|---|
| c01-fix-failing-test | C01 | `run` routes a failing test to a minimal, verified fix — no research pipeline |
| c01b-natural-discovery | observation | natural-language request (no skill named); outcome judged, routing noted |
| c04-debug | C04 | reproduce → root cause → fix → regression evidence |
| c05-review | C05 | planted-bug review with locations/severity; review-only, no fixes |
| c07-read-missing | C07 | readable doc analyzed; missing doc stated, not faked |
| c08-experiment-design | C08 | design-only protocol: metric, controls, seeds, anti-claim, budget |
| c10-write-incomplete | C10 | evidence-gated drafting; missing data marked, not invented |
| c11-figure-csv | C11 | reproducible plot script from CSV; honest when the backend is absent |
| c12-resume | C12 | stale checkpoint detected, re-verified, correct continuation |
| c13-doctor | C13 | installable vs runtime-ready; missing tools → degradation, no installs |
| c15-cross-model-review | C15 | no second backend → honest unavailable/self-review label |
| c16-injection-doc | C16 | embedded instructions treated as data, never executed |

Each case has `prompt.md` (frontmatter: name, description, runs, max_turns,
allowed_tools; body: the prompt) and `graders/*.md` (llm rubrics and tool_used
guards). Scaffolds embed their fixtures inline — no external fixture files.

## Notes

- `runs: 1` per case keeps cost bounded; raise per-case if you need variance
  statistics.
- Graders judge the final response and tool-call trace; artifact-heavy checks
  (real files written) are additionally verified by the directed-run protocol in
  `docs/IMPLEMENTATION_REPORT.md` §7.4.
