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


def test_core_exists_and_is_sealed_to_current_skill():
    core = bx.read_core()
    assert bx.parse_seal(core) == bx.skill_hash(), (
        "core.md seal is stale — re-condense core.md then run "
        "`python -m scripts.build_exports --reseal`"
    )


def test_core_body_within_chatgpt_char_budget():
    body = bx.strip_seal(bx.read_core())
    assert len(body) <= bx.CHATGPT_CHAR_LIMIT, "core.md body is %d chars (limit %d)" % (
        len(body), bx.CHATGPT_CHAR_LIMIT
    )


def test_core_names_every_reference():
    body = bx.strip_seal(bx.read_core())
    assert "Reference library" in body
    for name, _ in bx.reference_files():
        assert name in body, "core.md never mentions reference %s" % name


def test_build_derived_includes_chatgpt_instructions_and_knowledge():
    derived = bx.build_derived()
    assert "chatgpt/instructions.txt" in derived
    for name, _ in bx.reference_files():
        assert "chatgpt/knowledge/%s" % name in derived


def test_chatgpt_instructions_equal_core_body_within_limit():
    derived = bx.build_derived()
    instr = derived["chatgpt/instructions.txt"]
    assert instr == bx.strip_seal(bx.read_core())
    assert len(instr) <= bx.CHATGPT_CHAR_LIMIT


def test_chatgpt_knowledge_files_match_source_references():
    derived = bx.build_derived()
    for name, path in bx.reference_files():
        assert derived["chatgpt/knowledge/%s" % name] == open(path, encoding="utf-8").read()


def test_validate_flags_oversize_instructions():
    errors = bx.validate({"chatgpt/instructions.txt": "x" * (bx.CHATGPT_CHAR_LIMIT + 1)})
    assert any("8000" in e or "limit" in e for e in errors)


def test_validate_clean_on_real_build():
    assert bx.validate(bx.build_derived()) == []


def test_build_derived_includes_gemini_instructions_and_knowledge():
    derived = bx.build_derived()
    assert "gemini/instructions.txt" in derived
    for name, _ in bx.reference_files():
        assert "gemini/knowledge/%s" % name in derived


def test_gemini_knowledge_within_ten_file_cap():
    derived = bx.build_derived()
    gemini_knowledge = [k for k in derived if k.startswith("gemini/knowledge/")]
    assert len(gemini_knowledge) <= bx.GEMINI_KNOWLEDGE_LIMIT


def test_validate_flags_too_many_gemini_files():
    fake = {"gemini/knowledge/r%02d.md" % i: "x" for i in range(bx.GEMINI_KNOWLEDGE_LIMIT + 1)}
    fake["chatgpt/instructions.txt"] = "ok"
    errors = bx.validate(fake)
    assert any("Gemini" in e or "10" in e for e in errors)
