#!/usr/bin/env python3
"""Maintainer tool: merge component fragments into the shipped components.json.

Usage:
  python3 scripts/build_registry.py [--fragments DIR] [--check]

Each fragment file (JSON with a "components" list, as produced by the curation
step) is merged into plugins/minh-agent/registry/components.json. Duplicate
component_ids are an error. With --check, only verify that components.json is
consistent with the plugin tree (same checks as the shipped validator).
"""
import argparse
import hashlib
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(REPO_ROOT, "plugins", "minh-agent", "registry", "components.json")
DEFAULT_FRAGMENTS = os.environ.get("MINH_FRAGMENTS_DIR", "/tmp/minh-components")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fragments", default=DEFAULT_FRAGMENTS, help="fragment dir to merge")
    ap.add_argument("--check", action="store_true", help="only verify existing components.json")
    args = ap.parse_args()

    if args.check:
        if not os.path.exists(TARGET):
            print(f"FAIL — {TARGET} missing")
            return 1
        data = json.load(open(TARGET, encoding="utf-8"))
        errors = 0
        for c in data["components"]:
            p = os.path.join(REPO_ROOT, "plugins", "minh-agent", c["local_path"])
            if not os.path.isfile(p):
                print(f"FAIL — missing: {c['component_id']} → {c['local_path']}")
                errors += 1
            elif sha256(p) != c["sha256"]:
                print(f"FAIL — hash mismatch: {c['component_id']} → {c['local_path']}")
                errors += 1
        print("PASS — components.json matches the tree." if not errors else f"FAIL — {errors} problem(s)")
        return 1 if errors else 0

    frag_files = sorted(f for f in os.listdir(args.fragments) if f.endswith(".json"))
    if not frag_files:
        print(f"FAIL — no fragment files in {args.fragments}")
        return 1
    merged = {}
    for fname in frag_files:
        data = json.load(open(os.path.join(args.fragments, fname), encoding="utf-8"))
        for c in data.get("components", []):
            cid = c["component_id"]
            if cid in merged:
                print(f"FAIL — duplicate component_id {cid!r} ({fname})")
                return 1
            merged[cid] = c
    out = {
        "schema_version": 1,
        "note": "Provenance of every component shipped by minh-agent. origin_kind: native or upstream. Upstream components carry source_path/revision/mode and a sha256 of the shipped local file; native components leave upstream fields null. Regenerate hashes with scripts/rehash_components.py after edits.",
        "components": [merged[k] for k in sorted(merged)],
    }
    with open(TARGET, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"[ok] merged {len(merged)} components from {len(frag_files)} fragment(s) → {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
