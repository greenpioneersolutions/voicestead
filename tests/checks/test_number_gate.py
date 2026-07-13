import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "skills", "voicestead", "checks"))
import number_gate as ng


def test_unsourced_number_fails():
    passed, failures = ng.gate("We grew 47% last quarter.", prompt="write about our growth")
    assert passed is False
    assert any(f["id"] == "no_invented_numbers" for f in failures)


def test_sourced_number_passes():
    passed, failures = ng.gate("We grew 47% last quarter.", prompt="we grew 47% last quarter, write it up")
    assert passed is True
    assert failures == []


def test_small_bare_integer_is_exempt():
    passed, _ = ng.gate("Here are 3 options for you.", prompt="give me some options")
    assert passed is True


def test_unsourced_quote_fails():
    passed, failures = ng.gate('She said "this is the best launch we have ever run".', prompt="write about the launch")
    assert passed is False
    assert any(f["id"] == "no_invented_quotes" for f in failures)


def test_unsourced_url_fails():
    passed, failures = ng.gate("Sign up at https://example.com/promo today.", prompt="announce the signup")
    assert passed is False
    assert any(f["id"] == "no_invented_urls" for f in failures)


def test_unsourced_citation_fails():
    passed, failures = ng.gate("As Alvarez (2021) showed, it works.", prompt="write about the method")
    assert passed is False
    assert any(f["id"] == "no_invented_citations" for f in failures)


def test_gate_checks_registry_has_four():
    assert set(ng.GATE_CHECKS) == {
        "no_invented_numbers", "no_invented_quotes",
        "no_invented_citations", "no_invented_urls",
    }

def test_curly_quoted_invented_quote_is_caught():
    # smart/typographic quotes (Word, Google Docs, iMessage, LLM output) must still trip the gate
    output = "She said “this is the best launch we have ever run” today."
    passed, failures = ng.gate(output, prompt="write about the launch")
    assert passed is False
    assert any(f["id"] == "no_invented_quotes" for f in failures)
