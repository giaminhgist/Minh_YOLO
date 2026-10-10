#!/usr/bin/env python3
"""CLI probe: run an external command and report exit code / stderr / stdout
with a hard timeout. Success == exit code 0. Never counts emoji or output
patterns as success (B03 discipline).

Usage: python3 tests/cli_probe.py [--timeout SECONDS] -- CMD [ARGS...]

Exit code: 0 when the probed command exits 0, 1 otherwise (failure or timeout).
"""
import argparse
import subprocess
import sys

MAX_OUTPUT = 4000  # chars of each stream to echo back


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    if not args.cmd or args.cmd[0] == "--":
        args.cmd = args.cmd[1:]
    if not args.cmd:
        print("FAIL — no command given", file=sys.stderr)
        return 1

    try:
        proc = subprocess.run(args.cmd, capture_output=True, text=True, timeout=args.timeout)
    except FileNotFoundError:
        print(f"RESULT not_found cmd={args.cmd[0]}")
        print("stderr: command binary not found")
        return 1
    except subprocess.TimeoutExpired as ex:
        print(f"RESULT timeout cmd={args.cmd[0]} after={args.timeout}s")
        if ex.stdout:
            print(f"stdout: {ex.stdout[:MAX_OUTPUT]}")
        if ex.stderr:
            print(f"stderr: {ex.stderr[:MAX_OUTPUT]}")
        return 1

    print(f"RESULT exit={proc.returncode} cmd={args.cmd[0]}")
    print(f"stdout: {proc.stdout[:MAX_OUTPUT]}")
    print(f"stderr: {proc.stderr[:MAX_OUTPUT]}")
    return 0 if proc.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
