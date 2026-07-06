#!/usr/bin/env python3
"""Fail-safe for launch: find leftover REPLACE_ME_* placeholders before the repo goes public.

Pre-launch, real values (the GitHub owner, the Studio MCP URLs) are not decided yet, so
placeholders are expected. This runs in REPORT mode by default (exit 0, lists what it finds).
At S6 / launch, once the real URLs land, flip CI to ``--strict`` so any leftover placeholder
fails the build -- that turns the S6 URL sweep into a mechanical find-and-replace with a net.

  python scripts/check_placeholders.py            # report (exit 0)
  python scripts/check_placeholders.py --strict   # gate (exit 1 if any placeholder remains)
"""
import argparse
import os
import re
import subprocess
import sys

SENTINEL = re.compile(r"REPLACE_ME[A-Z_]*")
# Directories/files that legitimately reference the sentinel or aren't shipped.
SKIP = ("/.git/", "/node_modules/", "/tests/golden/results/", "/docs/plans/")
SELF = "scripts/check_placeholders.py"


def candidate_files():
    try:
        out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout
        files = [f for f in out.splitlines() if f]
        if files:
            return files
    except Exception:
        pass
    # not a git repo yet -- walk the tree
    files = []
    for root, _, fs in os.walk("."):
        for f in fs:
            files.append(os.path.relpath(os.path.join(root, f), "."))
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="exit 1 if any placeholder is found")
    args = ap.parse_args()

    hits = []
    for f in candidate_files():
        norm = "/" + f.replace(os.sep, "/")
        if f == SELF or any(s in norm for s in SKIP):
            continue
        try:
            with open(f, encoding="utf-8", errors="ignore") as fh:
                for i, line in enumerate(fh, 1):
                    for m in SENTINEL.finditer(line):
                        hits.append((f, i, m.group(0)))
        except (IsADirectoryError, OSError):
            continue

    if hits:
        print(f"{len(hits)} placeholder(s) found:")
        for f, i, tok in hits:
            print(f"  {f}:{i}: {tok}")
    else:
        print("no placeholders -- clean.")
    sys.exit(1 if (hits and args.strict) else 0)


if __name__ == "__main__":
    main()
