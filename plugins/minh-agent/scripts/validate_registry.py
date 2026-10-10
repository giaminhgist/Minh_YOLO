#!/usr/bin/env python3
"""Strict minh-agent registry validator (stdlib only, Python >= 3.9).

Validates the three registry files and the 12 entry skills against each other
and against the plugin tree. This is the gate for A01/A03/A04/A05-style checks:
five pinned upstreams, full commit SHAs, component provenance + hashes +
dependencies, capability→resource mapping, skill frontmatter.

Usage:
  python3 validate_registry.py          # human-readable report
  python3 validate_registry.py --json   # machine-readable findings list

Exit codes: 0 = no errors (warnings allowed) · 1 = errors found · 2 = registry files missing/corrupt.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import minh_registry  # noqa: E402


def main():
    want_json = "--json" in sys.argv
    lock, comps, caps, findings = minh_registry.full_check()
    errors = [f for f in findings if f["level"] == "error"]
    warns = [f for f in findings if f["level"] == "warn"]

    if want_json:
        print(json.dumps({"errors": errors, "warnings": warns}, indent=2, ensure_ascii=False))
    else:
        for w in warns:
            print(f"WARN — [{w['check']}] {w['message']}")
        if errors:
            print(f"FAIL — {len(errors)} error(s):")
            for f in errors:
                print(f"  - [{f['check']}] {f['message']}")
            return 1
        print("PASS — registry consistent: "
              f"{len((lock or {}).get('upstreams') or [])} upstreams, "
              f"{len(comps or [])} components, "
              f"{len((caps or {}).get('entries') or [])} capability entries.")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
