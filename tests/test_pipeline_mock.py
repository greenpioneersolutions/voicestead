"""End-to-end pipeline tests under VOICESTEAD_MOCK=1 - no API key, no anthropic import.

Runs the real orchestrator (tests/run_eval.py) as a subprocess on three representative
cases from tests/cases.json:
  - id 3: baseline_compare (with/without arms, pairwise judging, tier-2 must_pass on a
          rubric dimension: restraint)
  - id 6: metamorphic (length_delta_max vs source)
  - id 4: must_pass on a SOFT deterministic check (not_a_rewrite)

Every subprocess runs with a PYTHONPATH shim in which `import anthropic` raises, so any
accidental anthropic import in mock mode fails the test - that is the contract.

Failure injection uses the mock knobs documented in run_skill.py / judge/judge.py
(VOICESTEAD_MOCK_REVIEW_REWRITE, VOICESTEAD_MOCK_BLOAT, VOICESTEAD_MOCK_PAIR,
VOICESTEAD_MOCK_MALFORMED, VOICESTEAD_MOCK_LOW_SCORES).
"""
import importlib
import json
import os
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_EVAL = os.path.join(REPO, "tests", "run_eval.py")
CASES = os.path.join(REPO, "tests", "cases.json")
THREE_IDS = "3,6,4"


def _env(tmp_path, **extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith("VOICESTEAD_MOCK")}
    env["VOICESTEAD_MOCK"] = "1"
    shim = tmp_path / "shim"
    shim.mkdir(exist_ok=True)
    (shim / "anthropic.py").write_text(
        "raise ImportError('anthropic must not be imported when VOICESTEAD_MOCK=1')\n")
    env["PYTHONPATH"] = str(shim) + os.pathsep + env.get("PYTHONPATH", "")
    env.update(extra)
    return env


def _run_eval(out_dir, env, ids=THREE_IDS, runs="1", *extra_args):
    cmd = [sys.executable, RUN_EVAL, "--cases", CASES, "--runs", runs,
           "--ids", ids, "--out", str(out_dir)] + list(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def _bench(out_dir):
    with open(os.path.join(str(out_dir), "benchmark.json")) as f:
        return json.load(f)


def _recs(bench):
    return {r["eval_id"]: r for r in bench["runs"]}


# ---------------------------------------------------------------- full green run


def test_full_mock_run_end_to_end(tmp_path):
    out = tmp_path / "res"
    p = _run_eval(out, _env(tmp_path), runs="2")
    assert p.returncode == 0, "stdout:\n%s\nstderr:\n%s" % (p.stdout, p.stderr)
    assert "release gate: PASS" in p.stdout

    b = _bench(out)
    # benchmark.json structure
    md = b["metadata"]
    assert md["skill_name"] == "voicestead"
    assert md["runs_per_configuration"] == 2
    assert md["mock"] is True
    assert sorted(md["evals_run"]) == [3, 4, 6]
    recs = _recs(b)
    assert set(recs) == {3, 4, 6}
    for r in recs.values():
        assert "error" not in r
        assert len(r["with_skill_tier1"]) == 2
        assert r["hard_fails"] == []
        assert r["tier2_must_pass_failures"] == []
        assert r["judge"] and all(j["median_scores"] for j in r["judge"])
        assert r["judge_failed_samples"] == 0

    # baseline case 3: without-skill outputs are Tier-1 checked, delta reported,
    # every generated pair compared, non-discriminating checks flagged
    c3 = recs[3]
    assert len(c3["without_skill_tier1"]) == 2
    assert c3["tier1_pass_rate_without"]["mean"] is not None
    assert c3["pass_rate_delta"] is not None and c3["pass_rate_delta"] > 0
    assert isinstance(c3["non_discriminating_checks"], list)
    pw = c3["pairwise"]
    assert pw["n_pairs"] == 2  # all N runs pairwise-compared, not just run 1
    assert pw["wins"] + pw["losses"] + pw["ties"] == pw["valid"] == 2
    assert pw["invalid"] == 0 and pw["failed"] == 0
    assert pw["win_rate"] == 1.0  # mock judge votes against the sloppy baseline

    # non-baseline cases carry no fabricated comparison
    assert recs[4]["pairwise"] is None and recs[6]["pairwise"] is None
    assert recs[4]["without_skill_tier1"] == []

    # metamorphic case 6: property evaluated and recorded
    meta = recs[6]["with_skill_tier1"][0]["metamorphic"]
    assert meta["property"] == "length_delta_max" and meta["passed"] is True

    # rubric_dimensions actually select what is scored (case 4 declares clarity+restraint)
    assert set(recs[4]["judge"][0]["median_scores"]) == {"clarity", "restraint"}

    # the judge's critique-the-test output is kept and persisted
    assert any(recs[i]["judge_critiques"] for i in (3, 4, 6))

    # overall win-rate: ties in the denominator, invalid/failed explicitly reported
    wr = b["overall"]["win_rate"]
    for key in ("wins", "losses", "ties", "invalid", "failed", "n_valid", "rate"):
        assert key in wr
    assert wr["rate"] == 1.0

    # incremental persistence: per-case partials exist and the aggregation matches them
    for cid in (3, 4, 6):
        pp = os.path.join(str(out), "partial", "case-%02d.json" % cid)
        assert os.path.exists(pp)
        with open(pp) as f:
            assert json.load(f)["eval_id"] == cid
    assert os.path.exists(os.path.join(str(out), "scorecard.md"))


def test_resume_reads_partials_instead_of_regenerating(tmp_path):
    out = tmp_path / "res"
    assert _run_eval(out, _env(tmp_path), ids="3", runs="1").returncode == 0
    # rerun with --resume under a forced-loss judge: if aggregation reads the saved
    # partial (a win) the gate passes; if it regenerated, the loss would fail --gate
    p = _run_eval(out, _env(tmp_path, VOICESTEAD_MOCK_PAIR="loss"), "3", "1", "--resume", "--gate")
    assert p.returncode == 0, p.stdout + p.stderr
    assert "skipping (--resume)" in p.stdout
    assert _bench(out)["overall"]["win_rate"]["rate"] == 1.0


# ---------------------------------------------------------------- gates fail loudly


def test_must_pass_soft_check_violation_gates(tmp_path):
    """Case 4's only stated gate is not_a_rewrite (severity soft). A mock output that
    rewrites the post must fail the release gate - must_pass promotes it to hard."""
    out = tmp_path / "res"
    p = _run_eval(out, _env(tmp_path, VOICESTEAD_MOCK_REVIEW_REWRITE="1"), ids="4")
    assert p.returncode != 0
    b = _bench(out)
    rec = _recs(b)[4]
    assert "not_a_rewrite" in rec["hard_fails"]
    assert b["overall"]["cases_with_hard_failures"] == 1
    assert "release gate: FAIL" in p.stdout


def test_metamorphic_length_violation_gates(tmp_path):
    out = tmp_path / "res"
    p = _run_eval(out, _env(tmp_path, VOICESTEAD_MOCK_BLOAT="1"), ids="6")
    assert p.returncode != 0
    rec = _recs(_bench(out))[6]
    assert "length_delta_max" in rec["hard_fails"]
    assert rec["with_skill_tier1"][0]["metamorphic"]["passed"] is False


def test_rubric_dim_must_pass_enforced_at_tier2(tmp_path):
    """Case 3 declares must_pass: [restraint] - a rubric dimension. Median < 4 must gate."""
    out = tmp_path / "res"
    p = _run_eval(out, _env(tmp_path, VOICESTEAD_MOCK_LOW_SCORES="1"), ids="3")
    assert p.returncode != 0
    rec = _recs(_bench(out))[3]
    assert rec["tier2_must_pass_failures"] == ["restraint"]
    assert "must_pass rubric dimension" in p.stdout


def test_gate_flag_fails_on_losing_win_rate(tmp_path):
    env = _env(tmp_path, VOICESTEAD_MOCK_PAIR="loss")
    # without --gate: a losing win rate is reported but does not gate
    p0 = _run_eval(tmp_path / "res0", env, ids="3")
    assert p0.returncode == 0
    assert _bench(tmp_path / "res0")["overall"]["win_rate"]["rate"] == 0.0
    # with --gate: nonzero exit
    p1 = _run_eval(tmp_path / "res1", env, "3", "1", "--gate")
    assert p1.returncode != 0
    assert "below the 0.7 bar" in p1.stdout


def test_ties_count_in_denominator(tmp_path):
    out = tmp_path / "res"
    p = _run_eval(out, _env(tmp_path, VOICESTEAD_MOCK_PAIR="tie"), ids="3")
    assert p.returncode == 0, p.stdout + p.stderr
    pw = _recs(_bench(out))[3]["pairwise"]
    assert pw["ties"] == 1 and pw["wins"] == 0 and pw["losses"] == 0
    assert pw["win_rate"] == 0.0  # a tie is not a win: it stays in the denominator
    assert pw["pairs"][0]["detail"][0]["winner_original"] == "tie"  # even when order was swapped


def test_invalid_verdict_reported_never_a_loss(tmp_path):
    out = tmp_path / "res"
    p = _run_eval(out, _env(tmp_path, VOICESTEAD_MOCK_PAIR="invalid"), ids="3")
    assert p.returncode == 0, p.stdout + p.stderr
    pw = _recs(_bench(out))[3]["pairwise"]
    assert pw["invalid"] == 1
    assert pw["losses"] == 0 and pw["wins"] == 0 and pw["ties"] == 0
    assert pw["win_rate"] is None  # no valid judgments - not a silent 0% or 100%


def test_malformed_judge_json_is_recorded_failed_run_not_crash(tmp_path):
    out = tmp_path / "res"
    p = _run_eval(out, _env(tmp_path, VOICESTEAD_MOCK_MALFORMED="score"), ids="4")
    assert p.returncode == 0, p.stdout + p.stderr  # case 4 has no rubric-dim must_pass
    rec = _recs(_bench(out))[4]
    assert "error" not in rec  # the run completed
    assert rec["judge_failed_samples"] == 1
    assert rec["judge"][0]["failed"] == 1
    assert rec["judge"][0]["median_scores"] is None
    assert "error" in rec["judge"][0]["samples"][0]


def test_tier1_only_exits_with_clear_error(tmp_path):
    out = tmp_path / "res"
    p = _run_eval(out, _env(tmp_path), THREE_IDS, "1", "--tier1-only")
    assert p.returncode != 0
    assert "run_checks.py" in p.stderr
    assert not os.path.exists(os.path.join(str(out), "benchmark.json"))


# ---------------------------------------------------------------- run_skill unit guards


def _import_run_skill(monkeypatch):
    monkeypatch.setenv("VOICESTEAD_MOCK", "1")
    tests_dir = os.path.join(REPO, "tests")
    if tests_dir not in sys.path:
        sys.path.insert(0, tests_dir)
    return importlib.import_module("run_skill")


class _FakeBlock(object):
    type = "text"

    def __init__(self, text):
        self.text = text


class _FakeMsg(object):
    def __init__(self, text="hello world", stop_reason="end_turn"):
        self.content = [_FakeBlock(text)]
        self.stop_reason = stop_reason


class _FakeClient(object):
    def __init__(self, msg, captured):
        self._msg = msg
        self._captured = captured
        self.messages = self

    def create(self, **kwargs):
        self._captured.update(kwargs)
        return self._msg


def test_run_skill_omits_temperature_unless_set(monkeypatch):
    rs = _import_run_skill(monkeypatch)
    captured = {}
    monkeypatch.setattr(rs, "MOCK", False)
    monkeypatch.setattr(rs, "_get_client", lambda: _FakeClient(_FakeMsg(), captured))
    assert rs.run("hi", with_skill=False) == "hello world"
    assert "temperature" not in captured
    captured.clear()
    rs.run("hi", with_skill=False, temperature=0.7)
    assert captured["temperature"] == 0.7


def test_run_skill_rejects_truncated_and_empty_outputs(monkeypatch):
    rs = _import_run_skill(monkeypatch)
    monkeypatch.setattr(rs, "MOCK", False)
    monkeypatch.setattr(rs, "_get_client",
                        lambda: _FakeClient(_FakeMsg(stop_reason="max_tokens"), {}))
    with pytest.raises(RuntimeError, match="max_tokens"):
        rs.run("hi", with_skill=False)
    monkeypatch.setattr(rs, "_get_client",
                        lambda: _FakeClient(_FakeMsg(stop_reason="refusal"), {}))
    with pytest.raises(RuntimeError, match="refusal"):
        rs.run("hi", with_skill=False)
    monkeypatch.setattr(rs, "_get_client", lambda: _FakeClient(_FakeMsg(text="   "), {}))
    with pytest.raises(RuntimeError, match="empty"):
        rs.run("hi", with_skill=False)
