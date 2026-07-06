"""Unit + subprocess tests for scripts/voice_profile_draft.py — guard the cold-start.

The stylometer's promise is 'computed, never guessed', so these tests pin the math to
hand-countable fixtures and prove the canaries: two very different authors must yield
different profiles, the same input twice must yield identical bytes, and fewer than
2 samples must exit 1 with a clear message.

  python3 -m pytest tests/checks/test_voice_profile_draft.py -q

No API key, no network. Runs on Python 3.9 and 3.12.
"""
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(REPO, "scripts", "voice_profile_draft.py")

sys.path.insert(0, os.path.join(REPO, "scripts"))
import voice_profile_draft as vpd  # noqa: E402


# --------------------------------------------------------------------------- fixtures
# Two deliberately opposite authors. TERSE: lowercase, contractions, em-dashes,
# fragments, questions. FORMAL: long sentences, semicolons, hedges, no contractions.
# The splitter treats a newline as a sentence boundary, so FORMAL paragraphs are
# single long lines on purpose.

TERSE_1 = """hey — quick one. ci's flaky again, don't panic.

pushing the deploy to monday. that's the safe call. sound ok?

short version: we're fine. nothing's on fire."""

TERSE_2 = """can't make standup — dentist. notes are in the doc.

one ask: don't merge the auth branch yet. it's not ready.
flag me when the tests go green?"""

FORMAL_1 = (
    "The quarterly review process has, in my opinion, drifted a long way from its original purpose; "
    "what began as a lightweight ritual now consumes the better part of a week. "
    "It seems reasonable to ask whether the benefit justifies the cost.\n\n"
    "Perhaps the strongest argument for reform is the calendar itself. "
    "Each cycle demands preparation from every team lead; each presentation requires slides, "
    "rehearsal, and follow-up documentation."
)

FORMAL_2 = (
    "I would suggest, somewhat tentatively, that we consolidate the two reporting streams; "
    "the redundancy between them is probably the largest single source of wasted effort. "
    "It is possible that a merged format could preserve the visibility that executives want "
    "while returning several days to the engineering calendar."
)

# Tiny fixtures whose numbers a reviewer can count on their fingers.
PIN_1 = "One two three. Four five six seven eight."
PIN_2 = "Nine ten? Eleven twelve thirteen fourteen."


# --------------------------------------------------------------------------- pin values

def test_pin_sentence_distribution_exact():
    m = vpd.analyze([PIN_1, PIN_2])
    sl = m["sentence_len"]
    assert m["samples"] == 2
    assert m["words"] == 14
    assert sl["count"] == 4
    assert sl["mean"] == 3.5
    assert sl["min"] == 2 and sl["max"] == 5
    assert sl["sd"] == pytest.approx(1.118, abs=1e-3)
    assert m["question_pct"] == 25.0


def test_pin_paragraph_rhythm():
    m = vpd.analyze(["One two. Three four.\n\nFive six.", "Seven eight."])
    pg = m["paragraphs"]
    assert pg["count"] == 3
    assert pg["mean_sentences"] == pytest.approx(4 / 3)
    assert pg["single_pct"] == pytest.approx(2 / 3 * 100)
    assert pg["max_sentences"] == 2


def test_pin_contraction_rate_exact():
    m = vpd.analyze(["don't stop now.", "it's fine. do not panic."])
    c = m["contractions"]
    assert c["count"] == 2                                # don't, it's
    assert c["expanded"] == 1                             # do not
    assert c["per_100"] == pytest.approx(25.0)            # 2 of 8 words
    assert c["preference_pct"] == pytest.approx(2 / 3 * 100)


def test_pin_punctuation_density():
    m = vpd.analyze(["wait — one; two (three) — four.", "plain words here with five."])
    p = m["punct"]
    # 10 words; 2 em-dashes, 1 semicolon, 1 opening parenthesis
    assert p["em_dash_per_1000"] == pytest.approx(200.0)
    assert p["semicolon_per_1000"] == pytest.approx(100.0)
    assert p["paren_per_1000"] == pytest.approx(100.0)


def test_pin_hedges_counted():
    m = vpd.analyze(["Maybe we ship it. Probably fine, I think.",
                     "Perhaps we wait. It seems risky."])
    assert m["hedges"]["count"] == 5      # maybe, probably, i think, perhaps, it seems
    assert "maybe" in dict(m["hedges"]["top"])


def test_pin_opener_repeats_reported():
    m = vpd.analyze(["We ship. We test. We wait.", "We iterate. Then we rest."])
    assert dict(m["openers"]["repeated"]).get("we") == 4
    assert m["openers"]["total"] == 5


def test_pin_favorites_exclude_stopwords():
    m = vpd.analyze(["The deploy failed. The deploy stalled. The deploy works.",
                     "Deploy again tomorrow."])
    favs = dict(m["favorites"])
    assert favs.get("deploy") == 4
    assert "the" not in favs


def test_pin_sample_line_is_nearest_mean_sentence():
    sample = ("Tiny. This middle sentence runs six words. "
              "This one is a much longer sentence overall.")
    m = vpd.analyze([sample, "Filler words here."])
    # lengths 1, 6, 8 -> mean 5.0 -> the six-word sentence is nearest
    assert m["sample_lines"][0] == "This middle sentence runs six words."
    assert m["sample_lines"][1] == "Filler words here."


# --------------------------------------------------------------------------- canaries

def test_canary_two_authors_yield_different_metrics():
    terse = vpd.analyze([TERSE_1, TERSE_2])
    formal = vpd.analyze([FORMAL_1, FORMAL_2])
    assert terse["contractions"]["per_100"] > formal["contractions"]["per_100"]
    assert formal["sentence_len"]["mean"] > terse["sentence_len"]["mean"]
    assert formal["punct"]["semicolon_per_1000"] > terse["punct"]["semicolon_per_1000"]
    assert terse["question_pct"] > formal["question_pct"]
    assert formal["hedges"]["per_1000"] > terse["hedges"]["per_1000"]


def test_canary_analyze_is_deterministic():
    assert vpd.analyze([TERSE_1, TERSE_2]) == vpd.analyze([TERSE_1, TERSE_2])


def test_sample_lines_are_verbatim():
    m = vpd.analyze([TERSE_1, TERSE_2])
    combined = TERSE_1 + "\n" + TERSE_2
    assert len(m["sample_lines"]) == 2
    for line in m["sample_lines"]:
        assert line in combined


# --------------------------------------------------------------------------- render

def test_render_mirrors_example_profile_sections():
    out = vpd.render(vpd.analyze([TERSE_1, TERSE_2]))
    for section in ["Sounds like:", "Signature moves", "Never says:",
                    "Registers (if voice shifts by medium):", "Sample lines"]:
        assert section in out, "missing section: %s" % section


def test_render_reports_computed_numbers():
    out = vpd.render(vpd.analyze([PIN_1, PIN_2]))
    assert out.startswith("# Voice Profile")
    assert "measured from 2 samples, 14 words" in out
    assert "3.5" in out               # mean sentence length, hand-counted
    assert "range 2–5" in out         # min-max, hand-counted
    assert "25%" in out               # question rate, hand-counted


def test_canary_render_is_deterministic():
    a = vpd.render(vpd.analyze([TERSE_1, TERSE_2]))
    b = vpd.render(vpd.analyze([TERSE_1, TERSE_2]))
    assert a == b


def test_canary_two_authors_yield_different_profiles():
    terse = vpd.render(vpd.analyze([TERSE_1, TERSE_2]))
    formal = vpd.render(vpd.analyze([FORMAL_1, FORMAL_2]))
    assert terse != formal


def test_render_leaves_judgment_calls_open():
    # The script must never invent adjectives or a never-says list.
    out = vpd.render(vpd.analyze([TERSE_1, TERSE_2]))
    assert "the interview fills this in" in out
    assert "never what you avoid" in out


# --------------------------------------------------------------------------- CLI
# Subprocess tests in the test_scripts.py style: run the real script, assert on
# exit codes and streams. The script never writes anywhere unless --out says so,
# so running it against the real repo is safe.

def _run(*args, stdin_text=None, cwd=None):
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        input=stdin_text, cwd=cwd or REPO, capture_output=True, text=True,
    )


def _write_samples(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text(TERSE_1, encoding="utf-8")
    b.write_text(TERSE_2, encoding="utf-8")
    return str(a), str(b)


def test_cli_smoke_two_files(tmp_path):
    a, b = _write_samples(tmp_path)
    r = _run(a, b)
    assert r.returncode == 0, r.stderr + r.stdout
    assert r.stdout.startswith("# Voice Profile")
    assert "Sample lines" in r.stdout


def test_cli_canary_same_input_twice_identical(tmp_path):
    a, b = _write_samples(tmp_path)
    r1 = _run(a, b)
    r2 = _run(a, b)
    assert r1.returncode == 0 and r2.returncode == 0
    assert r1.stdout == r2.stdout


def test_cli_stdin_dash_is_one_sample(tmp_path):
    a, b = _write_samples(tmp_path)
    r = _run("-", b, stdin_text=TERSE_1)
    assert r.returncode == 0, r.stderr + r.stdout
    # stdin + file must equal file + file with the same contents
    assert r.stdout == _run(a, b).stdout


def test_cli_canary_one_sample_exits1(tmp_path):
    a, _ = _write_samples(tmp_path)
    r = _run(a)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "at least 2 samples" in r.stderr


def test_cli_canary_no_samples_exits1():
    r = _run()
    assert r.returncode == 1
    assert "at least 2 samples" in r.stderr


def test_cli_missing_file_exits1(tmp_path):
    a, _ = _write_samples(tmp_path)
    r = _run(a, str(tmp_path / "nope.txt"))
    assert r.returncode == 1
    assert "no such file" in r.stderr


def test_cli_four_samples_accepted_with_notice(tmp_path):
    a, b = _write_samples(tmp_path)
    c = tmp_path / "c.txt"
    d = tmp_path / "d.txt"
    c.write_text(FORMAL_1, encoding="utf-8")
    d.write_text(FORMAL_2, encoding="utf-8")
    r = _run(a, b, str(c), str(d))
    assert r.returncode == 0, r.stderr
    assert "2-3 is typical" in r.stderr


def test_cli_out_writes_file_matching_stdout(tmp_path):
    a, b = _write_samples(tmp_path)
    out = tmp_path / "sub" / "draft.md"
    r = _run(a, b, "--out", str(out))
    assert r.returncode == 0, r.stderr
    assert out.read_text(encoding="utf-8") == _run(a, b).stdout


def test_cli_refuses_out_into_skills_tree(tmp_path):
    a, b = _write_samples(tmp_path)
    target = os.path.join(REPO, "skills", "voicestead", "tmp-canary-vpd.md")
    r = _run(a, b, "--out", target)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "personal-by-design" in r.stderr
    assert not os.path.exists(target)


def test_cli_refuses_relative_out_into_skills_tree(tmp_path):
    a, b = _write_samples(tmp_path)
    r = _run(a, b, "--out", os.path.join("skills", "voicestead", "tmp-canary-vpd2.md"),
             cwd=REPO)
    assert r.returncode == 1, r.stdout + r.stderr
    assert not os.path.exists(os.path.join(REPO, "skills", "voicestead", "tmp-canary-vpd2.md"))


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
