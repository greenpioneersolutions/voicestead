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

# References that ship in the skill (Claude Code, .skill upload, skill-native
# .agents/skills) but are deliberately NOT exported to the flat-blob surfaces
# (ChatGPT/Gemini/AGENTS.md). The Voicestead Memory connector is Claude/MCP-only,
# so its conductor is inert there — and excluding it keeps Gemini knowledge within
# the 10-file cap.
EXCLUDE_FROM_EXPORTS = {"studio.md"}

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
    """Sorted [(name, abspath)] for every references/*.md that exports to the
    flat-blob surfaces. Connector-only references (EXCLUDE_FROM_EXPORTS) ship in
    the skill but never here."""
    return [
        (f, os.path.join(REFERENCES_DIR, f))
        for f in sorted(os.listdir(REFERENCES_DIR))
        if f.endswith(".md") and f not in EXCLUDE_FROM_EXPORTS
    ]


def _agents_footer(refs):
    """A repo-link list of the references, for tools that can't upload knowledge."""
    lines = [
        "## Reference library (full text in the repo)",
        "",
        "This flat file is always loaded. The full references load on demand only on "
        "Skill-native tools; here, open the one a job calls for:",
        "",
    ]
    for name, _ in refs:
        lines.append("- **%s** — %s/skills/voicestead/references/%s" % (name[:-3], RAW_BASE, name))
    return "\n".join(lines) + "\n"


def _read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# A region of an exported reference wrapped in these markers is connector-only
# (Claude/MCP surfaces) and is stripped from the flat-blob exports, where the
# Voicestead Memory connector doesn't exist. Lets connector guidance live in a
# locally-loaded reference (e.g. voice.md's "Turn on Voicestead Memory" offer)
# without leaking it to ChatGPT/Gemini/AGENTS.
_EXPORT_EXCLUDE_RE = re.compile(
    r"<!--\s*export:exclude:start\s*-->.*?<!--\s*export:exclude:end\s*-->",
    re.DOTALL,
)


def _export_text(path):
    """Reference text as it should appear in the flat-blob exports: connector-only
    regions stripped, trailing whitespace normalized to a single final newline."""
    stripped = _EXPORT_EXCLUDE_RE.sub("", _read_text(path))
    return stripped.rstrip() + "\n"


def _knowledge_bundle(refs):
    """Every reference concatenated into one file.

    Uploading ten separate knowledge files is the friction on ChatGPT/Gemini;
    this is the single-file alternative, so a self-builder uploads one document
    instead of ten. (The individual files in knowledge/ stay available for
    platforms that retrieve better over separate documents.)
    """
    parts = [
        "# Voicestead reference library (combined)",
        "",
        "Every Voicestead reference in one file, so you can upload a single "
        "knowledge document instead of ten. If your platform retrieves better "
        "over separate files, upload the individual files in `knowledge/` instead.",
    ]
    for name, path in refs:
        parts += ["", "---", "", "# %s" % name, "", _export_text(path).rstrip()]
    return "\n".join(parts) + "\n"


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
        derived["chatgpt/knowledge/%s" % name] = _export_text(path)

    # Gemini
    derived["gemini/instructions.txt"] = instructions
    for name, path in refs:
        derived["gemini/knowledge/%s" % name] = _export_text(path)

    # One-file knowledge bundle — a single upload instead of ten, for
    # self-builders on either chat platform. Sits beside knowledge/, so it is
    # not counted against the Gemini 10-file cap.
    bundle = _knowledge_bundle(refs)
    derived["chatgpt/knowledge-bundle.md"] = bundle
    derived["gemini/knowledge-bundle.md"] = bundle

    # AGENTS.md — one flat file; references become repo links (no knowledge upload here)
    derived["agents/AGENTS.md"] = instructions.rstrip() + "\n\n" + _agents_footer(refs)

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
    gemini_files = [k for k in derived if k.startswith("gemini/knowledge/")]
    if len(gemini_files) > GEMINI_KNOWLEDGE_LIMIT:
        errors.append(
            "Gemini knowledge has %d files, over the %d-file Gem cap — merge references"
            % (len(gemini_files), GEMINI_KNOWLEDGE_LIMIT)
        )
    return errors


def _managed_knowledge_dirs():
    return ["chatgpt/knowledge", "gemini/knowledge"]


def write_all():
    """Write every derived file under exports/. Refuses on hard-limit violations."""
    derived = build_derived()
    errors = validate(derived)
    if errors:
        print("BUILD BLOCKED (%d):" % len(errors))
        for e in errors:
            print("  " + e)
        return 1
    for rel, content in sorted(derived.items()):
        dest = os.path.join(EXPORTS, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(content)

    # Reconcile: remove orphan knowledge files no longer produced (e.g. a
    # deleted or renamed reference) so a regenerate fully matches build_derived().
    removed = 0
    for sub in _managed_knowledge_dirs():
        d = os.path.join(EXPORTS, sub)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                rel = "%s/%s" % (sub, f)
                if rel not in derived:
                    os.remove(os.path.join(d, f))
                    removed += 1

    removed_note = ", removed %d orphan(s)" % removed if removed else ""
    if parse_seal(read_core()) != skill_hash():
        print(
            "wrote %d derived files%s. WARNING: core.md seal is stale — run --reseal"
            % (len(derived), removed_note)
        )
    else:
        print("wrote %d derived files (seal ok)%s" % (len(derived), removed_note))
    return 0


def check():
    """Verify committed derived files are fresh, within limits, and sealed. CI gate."""
    derived = build_derived()
    errors = list(validate(derived))

    if parse_seal(read_core()) != skill_hash():
        errors.append(
            "core.md seal does not match SKILL.md — re-condense core.md then run "
            "`python -m scripts.build_exports --reseal`"
        )

    for rel, content in sorted(derived.items()):
        dest = os.path.join(EXPORTS, rel)
        current = _read_text(dest) if os.path.exists(dest) else None
        if current != content:
            errors.append("stale export: exports/%s — run `python -m scripts.build_exports`" % rel)

    # Catch leftover knowledge files after a reference is deleted/renamed.
    expected = set(derived)
    for sub in _managed_knowledge_dirs():
        d = os.path.join(EXPORTS, sub)
        if os.path.isdir(d):
            for f in os.listdir(d):
                rel = "%s/%s" % (sub, f)
                if rel not in expected:
                    errors.append("orphan export: exports/%s — run `python -m scripts.build_exports`" % rel)

    if errors:
        print("EXPORTS CHECK FAILED (%d):" % len(errors))
        for e in errors:
            print("  " + e)
        return 1
    print("exports check clean: %d derived files fresh, seal ok" % len(derived))
    return 0


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

    if args.check:
        return check()
    return write_all()


if __name__ == "__main__":
    sys.exit(main())
