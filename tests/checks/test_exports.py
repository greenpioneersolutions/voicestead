#!/usr/bin/env python3
"""Tests for scripts/build_exports.py — the multi-platform export generator.

No API key, no network. Runs on Python 3.9 and 3.12. Pure-function tests import
the module (namespace-package import with REPO on sys.path); integration tests
call the internal run() rather than shelling out.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

from scripts import build_exports as bx  # noqa: E402


def test_skill_hash_is_deterministic_64_hex():
    h1 = bx.skill_hash()
    h2 = bx.skill_hash()
    assert h1 == h2
    assert len(h1) == 64
    assert all(c in "0123456789abcdef" for c in h1)


def test_parse_seal_reads_recorded_hash():
    digest = "a" * 64
    text = "<!-- distilled-from: skills/voicestead/SKILL.md sha256=%s -->\n# Core\nbody" % digest
    assert bx.parse_seal(text) == digest


def test_parse_seal_returns_none_when_absent():
    assert bx.parse_seal("# Core\nno seal here") is None


def test_strip_seal_removes_only_the_marker_line():
    digest = "b" * 64
    text = "<!-- distilled-from: skills/voicestead/SKILL.md sha256=%s -->\n# Core\nbody" % digest
    stripped = bx.strip_seal(text)
    assert stripped == "# Core\nbody"
    assert "sha256" not in stripped


def test_reseal_roundtrip_updates_hash():
    original = "<!-- distilled-from: skills/voicestead/SKILL.md sha256=%s -->\n# Core" % ("c" * 64)
    resealed = bx.reseal(original, "d" * 64)
    assert bx.parse_seal(resealed) == "d" * 64
    assert resealed.endswith("# Core")


def test_reseal_adds_marker_when_absent():
    resealed = bx.reseal("# Core\nbody", "e" * 64)
    assert bx.parse_seal(resealed) == "e" * 64


def test_reference_files_returns_ten_sorted_md_files():
    refs = bx.reference_files()
    names = [n for n, _ in refs]
    assert names == sorted(names)
    assert len(names) == 10
    assert all(n.endswith(".md") for n in names)
    assert "tells.md" in names
