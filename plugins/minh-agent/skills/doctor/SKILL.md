---
name: doctor
description: "Use when the user asks about the minh-agent plugin's health: is it installed correctly, are its resources intact, which tools are present or missing, which capabilities still work. Reports the difference between 'installable' and 'runtime-ready'. Never installs or spends anything."
---

# minh-agent:doctor — plugin health check

**Contract:** report the plugin's real status — structure, sources, tools, runnability —
with the installable vs. runtime-ready distinction. Never claim "fully working" from file
counts alone; never installs packages or calls paid services.

## 1. Run the checks

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/doctor.py --json` (add `--project <dir>` to also
verify that project's `.minh-agent` state). Read the JSON report.

## 2. Interpret for the user

- **installable** — manifest, 12 entries, registry (5 locked upstreams, components with
  matching hashes, capability→resource mapping), scripts parse. If this fails, the plugin is
  broken and needs repair/update — say which check failed and what the error says.
- **runtime-ready** — all REQUIRED tools present (python3, git). Missing required tools are
  errors with the concrete install hint from the report.
- **Optional tools** (pdftotext, pdflatex, matplotlib, curl) — each maps to a capability:
  - missing `pdftotext` → PDF reading degrades (text/HTML reading still works)
  - missing `pdflatex` → paper drafting works, compilation doesn't
  - missing `matplotlib` → figure scripts can't run locally
  - missing `curl`/network → live literature search blocked; local-document work unaffected
- **Registry size**: report the component count and upstream count from the JSON. Bloat is a
  signal to the maintainer, not a user-facing feature list.

## 3. Never

- Never run `pip install`, `npm install`, `claude plugin install`, or any paid API from this
  entry. Report what's missing and how to install it — the user decides.
- Never call a plugin "working" because all files exist. "Files present" ≠ "tested working":
  say which evidence exists (checks passed) and which doesn't.

## 4. Output contract

1. Verdicts: installable (yes/no + failures), runtime-ready (yes/degraded + which tools).
2. Registry summary: entries, components, upstreams, any hash/provenance mismatches.
3. Capability degradation list (optional tools missing → which entries are affected).
4. The exact command to re-run later, and what to install to lift each degradation.
