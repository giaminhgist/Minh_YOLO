#!/usr/bin/env python3
"""Maintainer tool: fetch the five pinned upstreams into a local cache and verify them.

Usage:
  python3 scripts/fetch_upstreams.py              # fetch + verify + refresh lock metadata
  python3 scripts/fetch_upstreams.py --report     # only report cache state, no network
  python3 scripts/fetch_upstreams.py --revision aris=<full-sha>   # override one pinned revision

Exit code: 0 = all revisions verified, 1 = any failure.

The cache lives at $MINH_UPSTREAM_CACHE or <repo>/.cache/upstreams and is NOT shipped
in the plugin. End users never run this. Stdlib only (Python >= 3.9).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK_PATH = os.path.join(REPO_ROOT, "plugins", "minh-agent", "registry", "upstreams.lock.json")
DEFAULT_CACHE = os.path.join(REPO_ROOT, ".cache", "upstreams")
GIT_TIMEOUT = 600

LICENSE_HINTS = [
    ("Apache License", "Apache-2.0"),
    ("MIT License", "MIT"),
    ("MIT", "MIT"),
    ("GNU GENERAL PUBLIC LICENSE", "GPL"),
    ("GNU AFFERO GENERAL PUBLIC LICENSE", "AGPL"),
    ("BSD", "BSD"),
    ("Creative Commons", "CC"),
    ("CC BY-NC-SA", "CC BY-NC-SA"),
    ("Mozilla Public License", "MPL"),
]


def run(cmd, cwd=None):
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=GIT_TIMEOUT)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def detect_license(tree_dir):
    """Return (license_name_or_None, license_file_or_None) from the repo root."""
    candidates = []
    for f in sorted(os.listdir(tree_dir)):
        if f.upper().startswith("LICENSE") or f.upper().startswith("COPYING"):
            candidates.append(f)
    for f in candidates:
        path = os.path.join(tree_dir, f)
        if os.path.isfile(path):
            try:
                text = open(path, encoding="utf-8", errors="replace").read(4096)
            except OSError:
                continue
            for hint, name in LICENSE_HINTS:
                if hint.lower() in text.lower():
                    return name, f
            return "other (see file)", f
    return None, None


def ensure_fetched(upstream, cache_dir, revision_override):
    name = upstream["id"]
    url = upstream["repository"]
    revision = revision_override or upstream["revision"]
    dest = os.path.join(cache_dir, name)

    if not os.path.isdir(os.path.join(dest, ".git")):
        os.makedirs(dest, exist_ok=True)
        rc, out, err = run(["git", "init", "-q", dest])
        if rc != 0:
            return f"{name}: git init failed: {err}"
        rc, out, err = run(["git", "-C", dest, "remote", "add", "origin", url])
        if rc != 0:
            return f"{name}: git remote add failed: {err}"

    rc, out, err = run(["git", "-C", dest, "fetch", "--depth", "1", "origin", revision])
    if rc != 0:
        return f"{name}: fetch of {revision} failed: {err or out}"
    rc, out, err = run(["git", "-C", dest, "checkout", "-q", "--detach", "FETCH_HEAD"])
    if rc != 0:
        return f"{name}: checkout failed: {err or out}"
    rc, head, err = run(["git", "-C", dest, "rev-parse", "HEAD"])
    if rc != 0 or head != revision:
        return f"{name}: HEAD {head!r} != pinned {revision}"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help="no network: only report current cache state")
    ap.add_argument("--revision", action="append", default=[],
                    help="override pinned revision: --revision <id>=<full-sha> (repeatable)")
    ap.add_argument("--cache", default=None, help=f"cache dir (default $MINH_UPSTREAM_CACHE or {DEFAULT_CACHE})")
    args = ap.parse_args()

    overrides = {}
    for item in args.revision:
        if "=" not in item:
            print(f"FAIL — bad --revision {item!r} (want id=sha)")
            return 1
        k, v = item.split("=", 1)
        overrides[k] = v

    lock = json.load(open(LOCK_PATH, encoding="utf-8"))
    cache_dir = args.cache or os.environ.get("MINH_UPSTREAM_CACHE") or DEFAULT_CACHE
    cache_dir = os.path.abspath(cache_dir)

    errors = []
    for u in lock["upstreams"]:
        u_id = u["id"]
        if args.report:
            dest = os.path.join(cache_dir, u_id)
            if os.path.isdir(os.path.join(dest, ".git")):
                rc, head, err = run(["git", "-C", dest, "rev-parse", "HEAD"])
                status = f"HEAD={head}" if rc == 0 else f"git error: {err}"
            else:
                status = "not fetched"
            print(f"[..] {u_id}: {status}")
            continue
        err = ensure_fetched(u, cache_dir, overrides.get(u_id))
        if err:
            errors.append(err)
            continue
        if u_id in overrides:
            u["revision"] = overrides[u_id]
        license_name, license_file = detect_license(os.path.join(cache_dir, u_id))
        u["license"] = license_name
        u["license_file"] = license_file
        u["verified_at"] = time.strftime("%Y-%m-%d")
        print(f"[ok] {u_id} @ {u['revision'][:12]} license={license_name} ({license_file})")

    if not args.report and not errors:
        with open(LOCK_PATH, "w", encoding="utf-8") as f:
            json.dump(lock, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"[ok] lock metadata refreshed: {LOCK_PATH}")

    if errors:
        print("FAIL —")
        for e in errors:
            print(f"  - {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
