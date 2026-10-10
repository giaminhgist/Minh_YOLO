"""Shared registry validation for minh-agent (stdlib only, Python >= 3.9).

Loads and checks the three registry files (upstreams.lock.json, components.json,
capabilities.json) plus their cross-references against the plugin tree. Used by
validate_registry.py (strict CI validator) and doctor.py (runtime health check).

A "finding" is a dict: {level: "error"|"warn", check: str, message: str}.
"""
import hashlib
import json
import os
import re

PLUGIN_ROOT = os.environ.get("MINH_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_DIR = os.path.join(PLUGIN_ROOT, "registry")
LOCK_PATH = os.path.join(REGISTRY_DIR, "upstreams.lock.json")
COMPONENTS_PATH = os.path.join(REGISTRY_DIR, "components.json")
CAPABILITIES_PATH = os.path.join(REGISTRY_DIR, "capabilities.json")

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_ORIGIN_KINDS = ("native", "upstream")
ALLOWED_MODES = ("verbatim", "adapted", "reference")

EXPECTED_ENTRIES = [
    "run", "plan", "code", "debug", "review", "research", "read",
    "experiment", "write", "figure", "resume", "doctor",
]


def _load(path, findings, what):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        findings.append({"level": "error", "check": "registry",
                         "message": f"{what} missing: {os.path.relpath(path, PLUGIN_ROOT)}"})
    except json.JSONDecodeError as ex:
        findings.append({"level": "error", "check": "registry",
                         "message": f"{what} invalid JSON: {ex}"})
    return None


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(p):
    return os.path.relpath(p, PLUGIN_ROOT).replace(os.sep, "/")


def check_lock(lock=None):
    """Return (lock_dict_or_None, findings). Five upstreams, full SHAs, licenses set."""
    findings = []
    lock = lock if lock is not None else _load(LOCK_PATH, findings, "upstreams.lock.json")
    if lock is None:
        return None, findings
    ups = lock.get("upstreams")
    if not isinstance(ups, list) or len(ups) != 5:
        findings.append({"level": "error", "check": "lock",
                         "message": f"expected exactly 5 upstreams, found {len(ups) if isinstance(ups, list) else 'n/a'}"})
        return lock, findings
    seen = set()
    for u in ups:
        uid = u.get("id")
        if not uid:
            findings.append({"level": "error", "check": "lock", "message": "upstream entry without id"})
            continue
        if uid in seen:
            findings.append({"level": "error", "check": "lock", "message": f"duplicate upstream id {uid!r}"})
        seen.add(uid)
        rev = u.get("revision") or ""
        if not SHA_RE.match(rev):
            findings.append({"level": "error", "check": "lock",
                             "message": f"{uid}: revision is not a full 40-hex commit SHA: {rev!r}"})
        if not str(u.get("repository", "")).startswith("https://"):
            findings.append({"level": "error", "check": "lock",
                             "message": f"{uid}: repository URL missing or not https: {u.get('repository')!r}"})
        if not u.get("license"):
            findings.append({"level": "warn", "check": "lock",
                             "message": f"{uid}: license not yet verified (run scripts/fetch_upstreams.py)"})
    return lock, findings


def check_components(lock, components=None):
    """Return (components_list_or_None, findings). Provenance, paths, hashes, dependencies."""
    findings = []
    comps = components if components is not None else _load(COMPONENTS_PATH, findings, "components.json")
    if comps is None:
        return None, findings
    comps = comps.get("components", comps)
    if not isinstance(comps, list) or not comps:
        findings.append({"level": "error", "check": "components", "message": "components.json must contain a non-empty 'components' list"})
        return comps, findings
    upstream_ids = {u["id"] for u in lock.get("upstreams", [])} if lock else set()
    known_paths = set()
    for c in comps:
        cid = c.get("component_id")
        if not cid:
            findings.append({"level": "error", "check": "components", "message": "component without component_id"})
            continue
        if cid in known_paths:
            findings.append({"level": "error", "check": "components", "message": f"duplicate component_id {cid!r}"})
        known_paths.add(cid)
        origin = c.get("origin_kind")
        if origin not in ALLOWED_ORIGIN_KINDS:
            findings.append({"level": "error", "check": "components",
                             "message": f"{cid}: origin_kind must be one of {ALLOWED_ORIGIN_KINDS}, got {origin!r}"})
            continue
        local = c.get("local_path")
        if not local:
            findings.append({"level": "error", "check": "components", "message": f"{cid}: missing local_path"})
            continue
        lp = os.path.join(PLUGIN_ROOT, local)
        if not os.path.isfile(lp):
            findings.append({"level": "error", "check": "components",
                             "message": f"{cid}: local file missing: {local}"})
            continue
        if not c.get("sha256"):
            findings.append({"level": "error", "check": "components", "message": f"{cid}: missing sha256"})
        elif _sha256(lp) != c["sha256"]:
            findings.append({"level": "error", "check": "components",
                             "message": f"{cid}: sha256 mismatch for {local} (content changed without registry update)"})
        if origin == "upstream":
            uid = c.get("upstream_id")
            if uid not in upstream_ids:
                findings.append({"level": "error", "check": "components",
                                 "message": f"{cid}: upstream_id {uid!r} not in upstreams.lock.json (allowlist violation)"})
            elif c.get("revision") != (lock["upstreams"][[u["id"] for u in lock["upstreams"]].index(uid)]["revision"] if uid in upstream_ids else None):
                findings.append({"level": "error", "check": "components",
                                 "message": f"{cid}: revision does not match locked revision for {uid}"})
            if not c.get("source_path"):
                findings.append({"level": "error", "check": "components",
                                 "message": f"{cid}: upstream component missing source_path"})
            if c.get("mode") not in ALLOWED_MODES:
                findings.append({"level": "error", "check": "components",
                                 "message": f"{cid}: mode must be one of {ALLOWED_MODES}, got {c.get('mode')!r}"})
            if not c.get("local_changes"):
                findings.append({"level": "warn", "check": "components",
                                 "message": f"{cid}: adapted upstream component should record local_changes"})
        else:  # native
            for field in ("upstream_id", "source_path", "revision", "mode"):
                if c.get(field) is not None:
                    findings.append({"level": "error", "check": "components",
                                     "message": f"{cid}: native component must leave {field} null, got {c.get(field)!r}"})
        deps = c.get("dependencies") or []
        for d in deps:
            dp = os.path.join(PLUGIN_ROOT, d)
            if not os.path.exists(dp):
                findings.append({"level": "error", "check": "components",
                                 "message": f"{cid}: dependency missing: {d}"})
    return comps, findings


def check_capabilities(comps=None):
    """Return (caps_dict_or_None, findings). Every entry maps to real resources."""
    findings = []
    caps = _load(CAPABILITIES_PATH, findings, "capabilities.json")
    if caps is None:
        return None, findings
    entries = caps.get("entries")
    if not isinstance(entries, list) or not entries:
        findings.append({"level": "error", "check": "capabilities", "message": "capabilities.json must contain a non-empty 'entries' list"})
        return caps, findings
    comp_paths = {c.get("local_path") for c in (comps or [])}
    entry_names = []
    for e in entries:
        name = e.get("entry")
        entry_names.append(name)
        if not name:
            findings.append({"level": "error", "check": "capabilities", "message": "entry without name"})
            continue
        skill = os.path.join(PLUGIN_ROOT, "skills", name, "SKILL.md")
        if not os.path.isfile(skill):
            findings.append({"level": "error", "check": "capabilities",
                             "message": f"entry {name}: skills/{name}/SKILL.md missing"})
        if not e.get("primary_workflow"):
            findings.append({"level": "error", "check": "capabilities",
                             "message": f"entry {name}: missing primary_workflow"})
        for r in e.get("resources") or []:
            rp = os.path.join(PLUGIN_ROOT, r)
            if not os.path.exists(rp):
                findings.append({"level": "error", "check": "capabilities",
                                 "message": f"entry {name}: resource missing: {r}"})
            elif r in comp_paths and not os.path.isdir(rp):
                findings.append({"level": "error", "check": "capabilities",
                                 "message": f"entry {name}: resource {r} is a file component; resources must be directories or referenced files"})
    for expected in EXPECTED_ENTRIES:
        if expected not in entry_names:
            findings.append({"level": "error", "check": "capabilities",
                             "message": f"entry {expected} (required by contract) not present in capabilities.json"})
    return caps, findings


def check_skill_frontmatter():
    """Return findings for the 12 entry skills' frontmatter."""
    findings = []
    fm_re = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
    for name in EXPECTED_ENTRIES:
        path = os.path.join(PLUGIN_ROOT, "skills", name, "SKILL.md")
        if not os.path.isfile(path):
            continue  # reported by check_capabilities
        text = open(path, encoding="utf-8").read()
        m = fm_re.match(text)
        if not m:
            findings.append({"level": "error", "check": "skills",
                             "message": f"skills/{name}/SKILL.md: missing YAML frontmatter"})
            continue
        fm = m.group(1)
        if f"name: {name}" not in fm:
            findings.append({"level": "error", "check": "skills",
                             "message": f"skills/{name}/SKILL.md: frontmatter name must be {name!r}"})
        if not re.search(r"^description: .{10,}", fm, re.MULTILINE):
            findings.append({"level": "error", "check": "skills",
                             "message": f"skills/{name}/SKILL.md: frontmatter description missing or too short"})
    return findings


def full_check():
    """Run every registry check; return (lock, comps, caps, findings)."""
    findings = []
    lock, lock_f = check_lock()
    findings += lock_f
    comps, comp_f = check_components(lock)
    findings += comp_f
    caps, cap_f = check_capabilities(comps)
    findings += cap_f
    findings += check_skill_frontmatter()
    return lock, comps, caps, findings


if __name__ == "__main__":
    _, _, _, findings = full_check()
    errors = [f for f in findings if f["level"] == "error"]
    warns = [f for f in findings if f["level"] == "warn"]
    for f in warns:
        print(f"WARN — [{f['check']}] {f['message']}")
    if errors:
        print(f"FAIL — {len(errors)} error(s):")
        for f in errors:
            print(f"  - [{f['check']}] {f['message']}")
        raise SystemExit(1)
    print("PASS — registry consistent.")
