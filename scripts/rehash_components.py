#!/usr/bin/env python3
"""Maintainer tool: recompute sha256 for every component in components.json after edits.

Usage: python3 scripts/rehash_components.py [--list-changed]
"""
import hashlib
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(REPO_ROOT, "plugins", "minh-agent", "registry", "components.json")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    list_only = "--list-changed" in sys.argv
    data = json.load(open(TARGET, encoding="utf-8"))
    changed, updated = [], 0
    for c in data["components"]:
        p = os.path.join(REPO_ROOT, "plugins", "minh-agent", c["local_path"])
        if not os.path.isfile(p):
            print(f"FAIL — missing file for {c['component_id']}: {c['local_path']}")
            return 1
        new_hash = sha256(p)
        if new_hash != c.get("sha256"):
            changed.append(c["component_id"])
            c["sha256"] = new_hash
            updated += 1
    if list_only:
        for cid in changed:
            print(cid)
    else:
        with open(TARGET, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"[ok] updated {updated} hash(es); {len(data['components']) - updated} unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
