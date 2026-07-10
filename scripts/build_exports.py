#!/usr/bin/env python3
"""Generate per-platform export bundles from the canonical Voicestead skill.

skills/voicestead/SKILL.md + references/ are the single source of truth. Flat
surfaces that can't run a Claude Skill natively -- ChatGPT Custom GPTs, Gemini
Gems, and AGENTS.md-reading tools -- get paste-ready bundles under exports/,
assembled from one hand-authored distillation (exports/core.md) plus the skill's
reference files.

exports/core.md is the ONLY hand-maintained derivative. It opens with a seal
comment recording the SHA-256 of the SKILL.md it was distilled from; CI fails if
SKILL.md changes without core.md being re-condensed and re-sealed.

Usage:
    python -m scripts.build_exports            # regenerate the derived files
    python -m scripts.build_exports --check     # verify committed exports (CI)
    python -m scripts.build_exports --reseal     # stamp core.md with SKILL.md's hash

Run from the repository root.
"""
import argparse
import hashlib
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(REPO, "skills", "voicestead", "SKILL.md")
REFERENCES_DIR = os.path.join(REPO, "skills", "voicestead", "references")
EXPORTS = os.path.join(REPO, "exports")
CORE = os.path.join(EXPORTS, "core.md")

CHATGPT_CHAR_LIMIT = 8000
GEMINI_KNOWLEDGE_LIMIT = 10
RAW_BASE = "https://github.com/greenpioneersolutions/voicestead/blob/main"

SEAL_RE = re.compile(
    r"<!--\s*distilled-from:\s*skills/voicestead/SKILL\.md\s+sha256=([0-9a-f]{64})\s*-->"
)


def skill_hash():
    """SHA-256 of SKILL.md bytes, as 64 lowercase hex chars."""
    with open(SKILL_MD, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def read_core():
    with open(CORE, encoding="utf-8") as fh:
        return fh.read()


def parse_seal(core_text):
    """Return the hash recorded in core.md's seal comment, or None."""
    m = SEAL_RE.search(core_text)
    return m.group(1) if m else None


def strip_seal(core_text):
    """core.md without its seal comment line -- the text users actually paste."""
    return SEAL_RE.sub("", core_text, count=1).lstrip("\n")


def reseal(core_text, digest):
    """Return core_text with its seal set to *digest* (prepend one if absent)."""
    seal = "<!-- distilled-from: skills/voicestead/SKILL.md sha256=%s -->" % digest
    if SEAL_RE.search(core_text):
        return SEAL_RE.sub(seal, core_text, count=1)
    return seal + "\n" + core_text


def reference_files():
    """Sorted [(name, abspath)] for every references/*.md."""
    return [
        (f, os.path.join(REFERENCES_DIR, f))
        for f in sorted(os.listdir(REFERENCES_DIR))
        if f.endswith(".md")
    ]


def _read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def build_derived():
    """Return {path relative to exports/: text} for every GENERATED file.

    Static docs (SETUP.md, README.md, conversation-starters.txt, core.md) are
    authored by hand and intentionally excluded here.
    """
    instructions = strip_seal(read_core())
    refs = reference_files()
    derived = {}

    # ChatGPT
    derived["chatgpt/instructions.txt"] = instructions
    for name, path in refs:
        derived["chatgpt/knowledge/%s" % name] = _read_text(path)

    return derived


def validate(derived):
    """Return a list of hard-limit violations (empty when clean)."""
    errors = []
    instr = derived.get("chatgpt/instructions.txt", "")
    if len(instr) > CHATGPT_CHAR_LIMIT:
        errors.append(
            "chatgpt/instructions.txt is %d chars, over the %d limit — tighten core.md"
            % (len(instr), CHATGPT_CHAR_LIMIT)
        )
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate exports/ from the canonical skill")
    ap.add_argument("--check", action="store_true", help="verify committed exports are fresh")
    ap.add_argument("--reseal", action="store_true", help="stamp core.md with SKILL.md's current hash")
    args = ap.parse_args(argv)

    if args.reseal:
        sealed = reseal(read_core(), skill_hash())
        with open(CORE, "w", encoding="utf-8") as fh:
            fh.write(sealed)
        print("resealed core.md -> %s" % skill_hash())
        return 0

    print("build_exports: scaffold only (builders wired in Task 6)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
