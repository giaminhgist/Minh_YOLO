#!/usr/bin/env python3
"""minh-agent health check (stdlib only, Python >= 3.9).

Reports two distinct verdicts:
  installable   — plugin structure + registry are intact (the plugin will load)
  runtime-ready — required runtime tools for each capability are present

Optional tools are reported per capability; a missing optional tool degrades that
capability but never fails the install. This script never installs anything, never
spends money, never touches the network.

Usage: python3 doctor.py [--json] [--project DIR]

Exit codes: 0 = installable (warnings allowed) · 1 = broken structure/registry.
"""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import minh_registry  # noqa: E402

PLUGIN_ROOT = minh_registry.PLUGIN_ROOT
PLUGIN_JSON = os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json")
EXPECTED_NAME = "minh-agent"

# capability → {tool: (required, hint)}
CAPABILITY_TOOLS = {
    "all": {
        "python3": (True, "Python >= 3.9 (install from python.org or your package manager)"),
    },
    "code": {
        "git": (True, "git (required for diffs, commits, and reviews)"),
    },
    "debug": {
        "git": (True, "git (required to check recent changes)"),
    },
    "read": {
        "pdftotext": (False, "poppler-utils (for PDF extraction; text/HTML reading works without it)"),
    },
    "write": {
        "pdflatex": (False, "TeX Live (to compile LaTeX papers; drafting works without it)"),
    },
    "figure": {
        "matplotlib": (False, "matplotlib (pip install matplotlib; only for plotting)"),
    },
    "research": {
        "curl": (False, "curl (network access for arXiv/Semantic Scholar/OpenAlex APIs)"),
    },
}

# tools that are Python modules, not binaries on PATH
PYTHON_MODULE_TOOLS = {"matplotlib"}


def which(tool):
    return shutil.which(tool)


def tool_found(tool):
    if tool in PYTHON_MODULE_TOOLS:
        proc = subprocess.run([sys.executable, "-c", f"import {tool}"],
                              capture_output=True, timeout=30)
        return proc.returncode == 0
    return which(tool) is not None


def check_plugin_json():
    findings = []
    try:
        with open(PLUGIN_JSON, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return findings, None
    except json.JSONDecodeError as ex:
        findings.append({"level": "error", "check": "manifest",
                         "message": f".claude-plugin/plugin.json invalid JSON: {ex}"})
        return findings, None
    if data.get("name") != EXPECTED_NAME:
        findings.append({"level": "error", "check": "manifest",
                         "message": f"plugin name must be {EXPECTED_NAME!r}, got {data.get('name')!r}"})
    if not data.get("version"):
        findings.append({"level": "warn", "check": "manifest", "message": "plugin.json missing version"})
    return findings, data


def check_scripts_runnable():
    findings = []
    for name in ("state.py", "doctor.py", "validate_registry.py", "minh_registry.py"):
        path = os.path.join(PLUGIN_ROOT, "scripts", name)
        if not os.path.isfile(path):
            findings.append({"level": "error", "check": "scripts", "message": f"scripts/{name} missing"})
            continue
        spec = importlib.util.spec_from_file_location(name[:-3], path)
        try:
            src = open(path, encoding="utf-8").read()
            compile(src, path, "exec")
        except SyntaxError as ex:
            findings.append({"level": "error", "check": "scripts",
                             "message": f"scripts/{name} has a syntax error: {ex}"})
    return findings


def check_tools():
    """Return (tools_report, findings). Required missing tool = error; optional = warn."""
    report = {}
    findings = []
    for capability, tools in sorted(CAPABILITY_TOOLS.items()):
        report[capability] = {}
        for tool, (required, hint) in sorted(tools.items()):
            found = tool_found(tool)
            report[capability][tool] = {"found": found, "required": required, "hint": hint}
            if not found:
                findings.append({
                    "level": "error" if required else "warn",
                    "check": "tools",
                    "message": f"{tool} not found (required for capability '{capability}'): {hint}"
                    if required else
                    f"{tool} not found (optional for capability '{capability}'): {hint}",
                })
    return report, findings


def check_state(project):
    if not project:
        return None, []
    path = os.path.join(PLUGIN_ROOT, "scripts", "state.py")
    proc = subprocess.run([sys.executable, path, "verify", project],
                          capture_output=True, text=True, timeout=30)
    return {"exit": proc.returncode, "output": proc.stdout.strip()}, []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--project", help="also verify the .minh-agent state of this project")
    args = ap.parse_args()

    findings = []
    manifest_findings, manifest = check_plugin_json()
    findings += manifest_findings
    lock, comps, caps, reg_findings = minh_registry.full_check()
    findings += reg_findings
    findings += check_scripts_runnable()
    tools_report, tool_findings = check_tools()
    findings += tool_findings
    state_report, _ = check_state(args.project)

    errors = [f for f in findings if f["level"] == "error"]
    warns = [f for f in findings if f["level"] == "warn"]
    installable = not errors
    required_missing = [f for f in errors if f["check"] == "tools"]
    runtime_ready = not required_missing and installable

    n_components = len(comps or [])
    n_upstream_components = sum(1 for c in (comps or []) if c.get("origin_kind") == "upstream")
    n_upstreams = len((lock or {}).get("upstreams") or [])

    if args.json:
        out = {
            "plugin": {"name": (manifest or {}).get("name"), "version": (manifest or {}).get("version")},
            "verdict": {"installable": installable, "runtime_ready": runtime_ready},
            "counts": {"entries": len(minh_registry.EXPECTED_ENTRIES),
                       "components": n_components,
                       "upstream_components": n_upstream_components,
                       "upstreams": n_upstreams},
            "tools": tools_report,
            "findings": findings,
            "state": state_report,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"minh-agent {((manifest or {}).get('version') or '?')} — health check")
        print(f"  entries: {len(minh_registry.EXPECTED_ENTRIES)} · components: {n_components} "
              f"({n_upstream_components} upstream) · upstreams: {n_upstreams}")
        for w in warns:
            print(f"  WARN — {w['message']}")
        if state_report:
            print(f"  state: {'PASS' if state_report[0] == 0 else 'FAIL'} — {state_report[1]}")
        if errors:
            print(f"FAIL — not installable ({len(errors)} error(s)):")
            for f in errors:
                print(f"  - {f['message']}")
            return 1
        print("  installable:  PASS — structure and registry intact")
        if runtime_ready:
            print("  runtime-ready: PASS — all required runtime tools present")
        else:
            missing = [f["message"].split(":")[0] for f in required_missing]
            print(f"  runtime-ready: DEGRADED — required tools missing: {', '.join(sorted(set(missing)))} "
                  f"(see the WARN/error lines above; the plugin still installs and non-dependent "
                  f"capabilities still work)")
        print("PASS — installable. (Optional tools missing above only degrade the listed capabilities.)")
    return 0 if installable else 1


if __name__ == "__main__":
    sys.exit(main())
