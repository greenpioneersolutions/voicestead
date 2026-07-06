#!/usr/bin/env python3
"""Dogfood gate: the skill's own always-loaded prose must pass the skill's own bar.

A writing skill whose SKILL.md or README reads like slop is dead on arrival. This runs the
high-confidence-tell and formula-structure checks against the house-voice files, after
stripping frontmatter, fenced code, and blockquotes (quoted "before" examples are
intentional slop). Two files are excluded by design: references/tells.md (a catalog OF
tells) and examples/before-after.md (intentional before/after slop).

  python tests/checks/dogfood.py     # exits nonzero if the skill violates its own rules

Dual purpose: a regression test for the checks, and public proof the repo eats its own dog food.
"""
import argparse
import glob
import os
import re
import sys

import text_metrics as tm

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO = os.path.dirname(os.path.dirname(HERE))

_EXCLUDE = {"tells.md", "before-after.md"}


def collect_files(repo):
    skill = os.path.join(repo, "skills", "voicestead")
    return (
        [os.path.join(skill, "SKILL.md")]
        + [f for f in glob.glob(os.path.join(skill, "references", "*.md")) if os.path.basename(f) not in _EXCLUDE]
        + [f for f in glob.glob(os.path.join(skill, "examples", "*.md")) if os.path.basename(f) not in _EXCLUDE]
        + [os.path.join(repo, "README.md"), os.path.join(repo, "CONTRIBUTING.md")]
        + glob.glob(os.path.join(repo, "docs", "*.md"))
    )


# The tells that are almost never justified in real prose, and the canned formula structures.
CHECKS = ["no_high_conf_tells", "formula_structures"]


def strip(text):
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)           # YAML frontmatter
    text = re.sub(r"```.*?```", "", text, flags=re.S)                  # fenced code blocks
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith(">"))  # blockquotes
    return text


def main():
    ap = argparse.ArgumentParser(description="Dogfood the skill's own prose against its bar.")
    ap.add_argument("--root", default=DEFAULT_REPO,
                    help="repo root to dogfood (default: this repo). Lets tests point at a temp copy.")
    args = ap.parse_args()
    repo = os.path.abspath(args.root)

    failures = 0
    for path in sorted(collect_files(repo)):
        if not os.path.isfile(path):
            continue
        results = tm.run(strip(open(path).read()), CHECKS)
        bad = [r for r in results if not r["passed"]]
        rel = os.path.relpath(path, repo)
        if bad:
            for r in bad:
                print(f"  [FAIL] {rel}: {r['id']}: {r['detail']}")
                failures += 1
        else:
            print(f"  [ok]   {rel}")
    print(f"\n{'DOGFOOD FAILED' if failures else 'dogfood clean — the skill passes its own bar'}: {failures} issue(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
