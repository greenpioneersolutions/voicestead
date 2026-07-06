#!/usr/bin/env python3
"""Check that relative markdown links point at files that exist.

Scans README.md, CONTRIBUTING.md, CHANGELOG.md, docs/*.md, skills/**/*.md,
and tests/**/*.md for inline links and images. External links (http/https),
mailto: links, and same-page anchors (#...) are skipped; everything else is
resolved relative to the file that contains it. Fenced code blocks and inline
code spans are ignored so example snippets never false-positive.

Exits 1 with a file:line list of broken links, 0 when everything resolves.
Offline-only on purpose — nothing here can flake in CI.

Usage::

    python scripts/check_links.py
"""
import glob
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCAN_PATTERNS = [
    "README.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "docs/*.md",
    os.path.join("skills", "**", "*.md"),
    os.path.join("tests", "**", "*.md"),
]

# [text](target) or ![alt](target), with an optional "title" after the target.
_LINK = re.compile(r"!?\[[^\]]*\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
_FENCE = re.compile(r"^\s*(```|~~~)")
_INLINE_CODE = re.compile(r"`[^`]*`")
_SKIP_SCHEMES = ("http://", "https://", "mailto:")


def markdown_files():
    seen = []
    for pattern in SCAN_PATTERNS:
        for path in sorted(glob.glob(os.path.join(REPO, pattern), recursive=True)):
            if os.path.isfile(path) and path not in seen:
                seen.append(path)
    return seen


def broken_links(path):
    """Return (lineno, raw_target) for every relative link in *path* that does not resolve."""
    broken = []
    in_fence = False
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if _FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            line = _INLINE_CODE.sub("", line)
            for match in _LINK.finditer(line):
                raw = match.group(1).strip("<>").strip()
                if raw.startswith(_SKIP_SCHEMES) or raw.startswith("#"):
                    continue
                target = raw.split("#", 1)[0]
                if not target:
                    continue
                dest = os.path.normpath(os.path.join(os.path.dirname(path), target))
                if not os.path.exists(dest):
                    broken.append((lineno, raw))
    return broken


def main():
    files = markdown_files()
    failures = []
    for path in files:
        for lineno, target in broken_links(path):
            failures.append("%s:%d: broken link -> %s" % (os.path.relpath(path, REPO), lineno, target))
    if failures:
        print("BROKEN LINKS (%d):" % len(failures))
        for f in failures:
            print("  " + f)
        return 1
    print("link check clean: %d markdown files, all relative links resolve" % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
