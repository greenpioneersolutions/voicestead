#!/usr/bin/env python3
"""Package a skill directory into a ``<name>.skill`` archive.

A ``.skill`` file is a zip of the skill folder. The archive contains the skill
directory at its root (e.g. ``voicestead/SKILL.md``, ``voicestead/references/...``),
so a user can upload it in claude.ai -> Customize -> Skills, or attach it to a
GitHub Release. Only ``skills/<name>/`` is included -- the ``tests/`` harness and
CI never ship.

Usage::

    python -m scripts.package_skill voicestead
    python scripts/package_skill.py voicestead --out dist/voicestead.skill

Run from the repository root.
"""
import argparse
import fnmatch
import os
import sys
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKIP_DIRS = {"__pycache__", ".git", "node_modules"}
_SKIP_FILES = {".DS_Store"}
# Personal-by-design files that live at the skill root and must never ship in the
# archive (see .gitignore). Only the *.example.md templates are meant to travel;
# these globs deliberately do NOT match "voice-profile.example.md". A user may keep
# a real profile locally -- we exclude it silently-but-noisily (a notice per file),
# never refuse, so packaging always succeeds.
_SKIP_ROOT_GLOBS = ("voice-profile.md", "voice-profile-*.md", "influences.md")


def package(name, out=None):
    """Zip ``skills/<name>/`` into ``<name>.skill`` and return the output path."""
    skill_dir = os.path.join(REPO, "skills", name)
    if not os.path.isdir(skill_dir):
        print(f"skill not found: {skill_dir}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(os.path.join(skill_dir, "SKILL.md")):
        print(f"missing SKILL.md in {skill_dir}", file=sys.stderr)
        sys.exit(1)

    out = out or os.path.join(REPO, f"{name}.skill")
    out_dir = os.path.dirname(os.path.abspath(out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(skill_dir):
            dirs[:] = sorted(d for d in dirs if d not in _SKIP_DIRS)
            for f in sorted(files):
                if f in _SKIP_FILES:
                    continue
                # Personal profiles live at the skill root; exclude them and say so.
                if root == skill_dir and any(fnmatch.fnmatch(f, g) for g in _SKIP_ROOT_GLOBS):
                    print(f"  excluding personal file (never ships): {f}")
                    continue
                full = os.path.join(root, f)
                arcname = os.path.join(name, os.path.relpath(full, skill_dir))
                z.write(full, arcname)
                count += 1

    print(f"wrote {out} ({count} files)")
    return out


def main():
    ap = argparse.ArgumentParser(description="Package skills/<name>/ into <name>.skill")
    ap.add_argument("name", nargs="?", default="voicestead", help="skill name under skills/")
    ap.add_argument("--out", default=None, help="output path (default: <name>.skill at repo root)")
    args = ap.parse_args()
    package(args.name, args.out)


if __name__ == "__main__":
    main()
