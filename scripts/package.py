#!/usr/bin/env python3
"""Maintainer tool: package the minh-agent plugin for isolated loading tests.

Usage:
  python3 scripts/package.py [--out DIR]   # writes minh-agent-<version>.zip into DIR
                                           # (default: dist/ at repo root)

The zip is a loadable plugin package (--plugin-dir and --plugin-url accept .zip).
This is for local testing only; the normal distribution path is the marketplace.
"""
import argparse
import json
import os
import sys
import zipfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_ROOT = os.path.join(REPO_ROOT, "plugins", "minh-agent")
EXCLUDE_DIRS = {"__pycache__"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "dist"))
    args = ap.parse_args()

    manifest = json.load(open(os.path.join(PLUGIN_ROOT, "plugin.json"), encoding="utf-8"))
    version = manifest["version"]
    os.makedirs(args.out, exist_ok=True)
    target = os.path.join(args.out, f"minh-agent-{version}.zip")

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PLUGIN_ROOT):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, PLUGIN_ROOT)
                zf.write(full, rel)
    size = os.path.getsize(target)
    print(f"[ok] packaged {target} ({size} bytes, {sum(1 for _ in zipfile.ZipFile(target).namelist())} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
