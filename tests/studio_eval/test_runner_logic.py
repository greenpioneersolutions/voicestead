"""Deterministic, model-free test of the Tier-2 runner's pass/fail logic.

This exercises check_case() directly with hand-built outputs — it never calls a
backend and never touches run_skill.run(). It is the free-CI-safe half of the
injection-defense eval: it proves the grading logic is correct, not that the
model passes the cases (that's the live run in run_studio_evals.py, Tier-2,
run on demand).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_studio_evals import check_case, CASES
from run_connected_evals import check_case as check_case_connected


def test_leaked_forbidden_text_is_flagged():
    case = {"id": "t1", "must_not_contain": ["BANANA"], "must_contain_any": []}
    failures = check_case("Sure, BANANA is the word you wanted.", case)
    assert len(failures) == 1
    assert "t1" in failures[0]
    assert "BANANA" in failures[0]


def test_forbidden_text_match_is_case_insensitive():
    case = {"id": "t2", "must_not_contain": ["system prompt"], "must_contain_any": []}
    failures = check_case("Here is my SYSTEM PROMPT in full.", case)
    assert len(failures) == 1
    assert "t2" in failures[0]


def test_missing_all_required_terms_is_flagged():
    case = {"id": "t3", "must_not_contain": [], "must_contain_any": ["standup", "10"]}
    failures = check_case("Nothing relevant here at all.", case)
    assert len(failures) == 1
    assert "t3" in failures[0]
    assert "missing all of" in failures[0]


def test_any_one_required_term_present_is_enough():
    case = {"id": "t4", "must_not_contain": [], "must_contain_any": ["standup", "10"]}
    failures = check_case("The standup time is unchanged.", case)
    assert failures == []


def test_clean_output_returns_empty_list():
    case = {
        "id": "t5",
        "must_not_contain": ["BANANA", "system prompt"],
        "must_contain_any": ["standup", "10"],
    }
    failures = check_case("Team: standup moves to 10am Friday. Nothing else changes.", case)
    assert failures == []


def test_can_fail_on_both_forbidden_and_missing_required():
    case = {"id": "t6", "must_not_contain": ["BANANA"], "must_contain_any": ["standup"]}
    failures = check_case("BANANA is all I will say.", case)
    assert len(failures) == 2
    assert any("leaked" in f for f in failures)
    assert any("missing all of" in f for f in failures)


def test_case_file_loaded_and_shaped_as_expected():
    # sanity check that the real injection_cases.json loaded by run_studio_evals
    # has the shape check_case() expects, without ever running a model
    ids = {c["id"] for c in CASES}
    assert {"injection-ignore-instructions", "injection-exfil-attempt", "no-narration"} <= ids
    for c in CASES:
        assert "prompt" in c and "studio_context" in c
        assert "must_not_contain" in c or "must_contain_any" in c


# ===== Connected evals grading tests (model-free unit tests for check_case_connected) =====

def test_connected_must_contain_all_clean():
    """Clean output passes must_contain_all check."""
    case = {"id": "c1", "must_contain_all": ["design", "thanks"]}
    failures = check_case_connected("Here is a design thanks note.", case)
    assert failures == []


def test_connected_must_contain_all_missing_one():
    """Missing any required term fails."""
    case = {"id": "c2", "must_contain_all": ["design", "thanks"]}
    failures = check_case_connected("Here is a design note.", case)
    assert len(failures) == 1
    assert "c2" in failures[0] and "thanks" in failures[0]


def test_connected_count_exact_clean():
    """Exact count match passes."""
    case = {"id": "c3", "count": {"free memory": 2}}
    failures = check_case_connected("free memory once and free memory again.", case)
    assert failures == []


def test_connected_count_exact_violation():
    """Wrong count fails."""
    case = {"id": "c4", "count": {"free memory": 2}}
    failures = check_case_connected("free memory once and free memory again and free memory once more.", case)
    assert len(failures) == 1
    assert "c4" in failures[0] and "!=" in failures[0]


def test_connected_count_max_clean():
    """Count within limit passes."""
    case = {"id": "c5", "count_max": {"unauthorized": 0}}
    failures = check_case_connected("The operation succeeded.", case)
    assert failures == []


def test_connected_count_max_violation():
    """Count exceeding limit fails."""
    case = {"id": "c6", "count_max": {"unauthorized": 0}}
    failures = check_case_connected("unauthorized error occurred.", case)
    assert len(failures) == 1
    assert "c6" in failures[0] and ">" in failures[0]


def test_connected_multiple_must_contain_any_clean():
    """Multiple independent must_contain_any lists all pass."""
    case = {"id": "c7", "must_contain_any": [["design", "thanks"], ["reconnect", "sign-in"]]}
    failures = check_case_connected("Here is a design note. Please reconnect.", case)
    assert failures == []


def test_connected_multiple_must_contain_any_first_group_missing():
    """First must_contain_any group missing fails."""
    case = {"id": "c8", "must_contain_any": [["design", "thanks"], ["reconnect", "sign-in"]]}
    failures = check_case_connected("Please reconnect to continue.", case)
    assert len(failures) == 1
    assert "c8" in failures[0]


def test_connected_multiple_must_contain_any_second_group_missing():
    """Second must_contain_any group missing fails."""
    case = {"id": "c9", "must_contain_any": [["design", "thanks"], ["reconnect", "sign-in"]]}
    failures = check_case_connected("Here is a design note.", case)
    assert len(failures) == 1
    assert "c9" in failures[0]


def test_connected_combined_assertions():
    """All assertion types together work correctly."""
    case = {
        "id": "c10",
        "must_contain_all": ["draft"],
        "must_contain_any": [["logo"], ["copy"]],
        "count": {"free memory": 1},
        "must_not_contain": ["unauthorized"],
        "count_max": {"error": 0}
    }
    failures = check_case_connected(
        "Draft one with logo and another with copy. free memory limit reached.",
        case
    )
    assert failures == []
