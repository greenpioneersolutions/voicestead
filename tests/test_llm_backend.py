"""Unit + routing tests for tests/llm_backend.py — the backend seam.

The claude binary is ALWAYS faked here: each test writes a `claude` PATH shim (a
small Python script) into a temp dir and prepends that dir to PATH, so nothing can
reach the real CLI (subscription burn, nondeterminism) or the real API (the api
backend is tested against a fake client object; the end-to-end subprocess tests run
with a PYTHONPATH shim in which `import anthropic` raises).

Layout:
  - resolve_backend precedence and validation
  - claude-cli backend: flag contract, stdin transport, failure mapping, usage capture
  - api backend: temperature omission, stop_reason/empty guards, token capture,
    missing-package message
  - routing: run_skill.run and judge through the seam (in-process, shimmed PATH)
  - end-to-end: run_eval as a subprocess against the fake CLI, green and no-binary paths
"""
import json
import os
import stat
import subprocess
import sys

import pytest

TESTS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(TESTS)
if TESTS not in sys.path:
    sys.path.insert(0, TESTS)
import llm_backend


@pytest.fixture(autouse=True)
def _clean_slate(monkeypatch):
    monkeypatch.delenv("VOICESTEAD_MOCK", raising=False)
    monkeypatch.delenv("VOICESTEAD_BACKEND", raising=False)
    llm_backend.reset_usage()
    yield
    llm_backend.reset_usage()


# ---------------------------------------------------------------- the PATH shim

_SHIM_TEMPLATE = """#!/usr/bin/env python3
import json, os, sys
record = {"argv": sys.argv[1:], "stdin": sys.stdin.read()}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "call.json"), "w") as f:
    json.dump(record, f)
%(body)s
"""

_OK_BODY = """
env = {"type": "result", "subtype": "success", "is_error": False,
       "result": "the generated text", "stop_reason": "end_turn", "num_turns": 1,
       "total_cost_usd": 0.01, "usage": {"input_tokens": 100, "output_tokens": 20}}
print(json.dumps(env))
"""


def _install_shim(tmp_path, monkeypatch, body=_OK_BODY):
    """Write a fake `claude` executable into tmp and prepend its dir to PATH.
    Returns the dir; the shim records argv+stdin to <dir>/call.json before replying."""
    bin_dir = tmp_path / "fakebin"
    bin_dir.mkdir(exist_ok=True)
    shim = bin_dir / "claude"
    shim.write_text(_SHIM_TEMPLATE % {"body": body})
    shim.chmod(shim.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ.get("PATH", ""))
    return bin_dir


def _call(bin_dir):
    with open(os.path.join(str(bin_dir), "call.json")) as f:
        return json.load(f)


# ---------------------------------------------------------------- resolve_backend


def test_resolve_backend_default_env_flag_precedence(monkeypatch):
    assert llm_backend.resolve_backend() == "claude-cli"          # the default
    monkeypatch.setenv("VOICESTEAD_BACKEND", "api")
    assert llm_backend.resolve_backend() == "api"                 # env beats default
    assert llm_backend.resolve_backend("claude-cli") == "claude-cli"  # flag beats env
    monkeypatch.setenv("VOICESTEAD_MOCK", "1")
    assert llm_backend.resolve_backend("api") == "mock"           # mock trumps everything


def test_resolve_backend_rejects_unknown(monkeypatch):
    with pytest.raises(ValueError, match="unknown backend"):
        llm_backend.resolve_backend("gpt")
    monkeypatch.setenv("VOICESTEAD_BACKEND", "typo-cli")
    with pytest.raises(ValueError, match="typo-cli"):
        llm_backend.resolve_backend()


def test_complete_refuses_to_generate_in_mock_mode(monkeypatch):
    # NEGATIVE-PATH CANARY: mock callers answer from their own seams; if a code path
    # ever routes a mock run into the seam, it must blow up, not call anything.
    monkeypatch.setenv("VOICESTEAD_MOCK", "1")
    with pytest.raises(RuntimeError, match="mock"):
        llm_backend.complete("hi", model="m")


# ---------------------------------------------------------------- claude-cli backend


def test_cli_flag_contract_and_stdin_transport(tmp_path, monkeypatch):
    bin_dir = _install_shim(tmp_path, monkeypatch)
    out = llm_backend.complete("write me a note", model="claude-sonnet-5",
                               system="SYSTEM RULES", backend="claude-cli")
    assert out == "the generated text"
    call = _call(bin_dir)
    argv = call["argv"]
    assert call["stdin"] == "write me a note"        # prompt over STDIN...
    assert "write me a note" not in " ".join(argv)   # ...never argv
    assert "-p" in argv
    assert argv[argv.index("--output-format") + 1] == "json"
    assert argv[argv.index("--tools") + 1] == ""     # all tools disabled = single turn
    assert argv[argv.index("--model") + 1] == "claude-sonnet-5"
    assert argv[argv.index("--system-prompt") + 1] == "SYSTEM RULES"
    assert "--no-session-persistence" in argv


def test_cli_omits_system_prompt_flag_when_none(tmp_path, monkeypatch):
    bin_dir = _install_shim(tmp_path, monkeypatch)
    llm_backend.complete("hi", model="m", backend="claude-cli")
    assert "--system-prompt" not in _call(bin_dir)["argv"]


def test_cli_nonzero_exit_raises(tmp_path, monkeypatch):
    _install_shim(tmp_path, monkeypatch, body="""
print("boom: not logged in", file=sys.stderr)
sys.exit(3)
""")
    with pytest.raises(RuntimeError, match="exited 3.*not logged in"):
        llm_backend.complete("hi", model="m", backend="claude-cli")


def test_cli_error_envelope_raises(tmp_path, monkeypatch):
    _install_shim(tmp_path, monkeypatch, body="""
env = {"type": "result", "subtype": "error_during_execution", "is_error": True,
       "result": "something broke"}
print(json.dumps(env))
""")
    with pytest.raises(RuntimeError, match="error envelope.*error_during_execution"):
        llm_backend.complete("hi", model="m", backend="claude-cli")


def test_cli_empty_result_raises(tmp_path, monkeypatch):
    _install_shim(tmp_path, monkeypatch, body="""
env = {"type": "result", "subtype": "success", "is_error": False,
       "result": "   ", "stop_reason": "end_turn"}
print(json.dumps(env))
""")
    with pytest.raises(RuntimeError, match="empty result"):
        llm_backend.complete("hi", model="m", backend="claude-cli")


def test_cli_truncation_raises_never_graded(tmp_path, monkeypatch):
    # NEGATIVE-PATH CANARY: a truncated generation must never come back as text.
    _install_shim(tmp_path, monkeypatch, body="""
env = {"type": "result", "subtype": "success", "is_error": False,
       "result": "half a sente", "stop_reason": "max_tokens"}
print(json.dumps(env))
""")
    with pytest.raises(RuntimeError, match="max_tokens"):
        llm_backend.complete("hi", model="m", backend="claude-cli")


def test_cli_unparseable_output_raises(tmp_path, monkeypatch):
    _install_shim(tmp_path, monkeypatch, body="""
print("I am prose, not a JSON envelope")
""")
    with pytest.raises(RuntimeError, match="unparseable"):
        llm_backend.complete("hi", model="m", backend="claude-cli")


def test_cli_missing_binary_names_both_ways_out(tmp_path, monkeypatch):
    empty = tmp_path / "emptybin"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))  # no claude anywhere on PATH
    with pytest.raises(RuntimeError) as exc:
        llm_backend.complete("hi", model="m", backend="claude-cli")
    msg = str(exc.value)
    assert "Install Claude Code" in msg and "--backend api" in msg


def test_cli_rejects_temperature_instead_of_ignoring(tmp_path, monkeypatch):
    bin_dir = _install_shim(tmp_path, monkeypatch)
    with pytest.raises(RuntimeError, match="temperature"):
        llm_backend.complete("hi", model="m", temperature=0.7, backend="claude-cli")
    assert not os.path.exists(os.path.join(str(bin_dir), "call.json"))  # never invoked


def test_cli_usage_and_cost_accumulate_across_calls(tmp_path, monkeypatch):
    _install_shim(tmp_path, monkeypatch)
    llm_backend.complete("one", model="m", backend="claude-cli")
    llm_backend.complete("two", model="m", backend="claude-cli")
    u = llm_backend.usage_snapshot()
    assert u["calls"] == 2
    assert u["input_tokens"] == 200 and u["output_tokens"] == 40
    assert u["total_cost_usd"] == pytest.approx(0.02) and u["cost_reported"] is True


def test_cli_usage_absent_fields_stay_unreported(tmp_path, monkeypatch):
    # an envelope without usage/cost must not fabricate zeros-as-figures: the call is
    # counted, the cost stays explicitly unreported
    _install_shim(tmp_path, monkeypatch, body="""
env = {"type": "result", "subtype": "success", "is_error": False,
       "result": "text", "stop_reason": "end_turn"}
print(json.dumps(env))
""")
    llm_backend.complete("hi", model="m", backend="claude-cli")
    u = llm_backend.usage_snapshot()
    assert u["calls"] == 1 and u["input_tokens"] == 0 and u["cost_reported"] is False


# ---------------------------------------------------------------- api backend (fake client)


class _FakeBlock(object):
    type = "text"

    def __init__(self, text):
        self.text = text


class _FakeUsage(object):
    input_tokens = 100
    output_tokens = 5


class _FakeMsg(object):
    def __init__(self, text="hello world", stop_reason="end_turn", usage=None):
        self.content = [_FakeBlock(text)]
        self.stop_reason = stop_reason
        if usage is not None:
            self.usage = usage


class _FakeClient(object):
    def __init__(self, msg, captured):
        self._msg = msg
        self._captured = captured
        self.messages = self

    def create(self, **kwargs):
        self._captured.update(kwargs)
        return self._msg


def test_api_omits_temperature_and_system_unless_set(monkeypatch):
    captured = {}
    monkeypatch.setattr(llm_backend, "_get_client", lambda: _FakeClient(_FakeMsg(), captured))
    assert llm_backend.complete("hi", model="m", backend="api") == "hello world"
    assert "temperature" not in captured and "system" not in captured
    assert captured["max_tokens"] == 4000
    captured.clear()
    llm_backend.complete("hi", model="m", temperature=0.7, system="S", backend="api")
    assert captured["temperature"] == 0.7 and captured["system"] == "S"


def test_api_rejects_truncated_refused_and_empty(monkeypatch):
    monkeypatch.setattr(llm_backend, "_get_client",
                        lambda: _FakeClient(_FakeMsg(stop_reason="max_tokens"), {}))
    with pytest.raises(RuntimeError, match="max_tokens"):
        llm_backend.complete("hi", model="m", backend="api")
    monkeypatch.setattr(llm_backend, "_get_client",
                        lambda: _FakeClient(_FakeMsg(stop_reason="refusal"), {}))
    with pytest.raises(RuntimeError, match="refusal"):
        llm_backend.complete("hi", model="m", backend="api")
    monkeypatch.setattr(llm_backend, "_get_client", lambda: _FakeClient(_FakeMsg(text="   "), {}))
    with pytest.raises(RuntimeError, match="empty"):
        llm_backend.complete("hi", model="m", backend="api")


def test_api_records_tokens_but_never_invents_cost(monkeypatch):
    monkeypatch.setattr(llm_backend, "_get_client",
                        lambda: _FakeClient(_FakeMsg(usage=_FakeUsage()), {}))
    llm_backend.complete("hi", model="m", backend="api")
    u = llm_backend.usage_snapshot()
    assert u["calls"] == 1 and u["input_tokens"] == 100 and u["output_tokens"] == 5
    assert u["total_cost_usd"] == 0.0 and u["cost_reported"] is False  # the SDK reports no dollars


def test_api_missing_anthropic_package_says_how_to_fix(monkeypatch):
    monkeypatch.setattr(llm_backend, "_CLIENT", None)
    monkeypatch.setitem(sys.modules, "anthropic", None)  # forces `from anthropic import ...` to raise
    with pytest.raises(RuntimeError, match="pip install anthropic"):
        llm_backend.complete("hi", model="m", backend="api")


# ---------------------------------------------------------------- routing: run_skill + judge


def _import_run_skill(monkeypatch):
    import run_skill
    monkeypatch.setattr(run_skill, "MOCK", False)
    return run_skill


def _import_judge(monkeypatch):
    judge_dir = os.path.join(TESTS, "judge")
    if judge_dir not in sys.path:
        sys.path.insert(0, judge_dir)
    import judge
    monkeypatch.setattr(judge, "MOCK", False)
    return judge


def test_run_skill_routes_through_cli_with_skill_system_prompt(tmp_path, monkeypatch):
    bin_dir = _install_shim(tmp_path, monkeypatch)
    rs = _import_run_skill(monkeypatch)
    assert rs.run("write the note", with_skill=True, backend="claude-cli") == "the generated text"
    call = _call(bin_dir)
    assert call["stdin"] == "write the note"
    argv = call["argv"]
    assert "name: voicestead" in argv[argv.index("--system-prompt") + 1]  # SKILL.md rode along


def test_run_skill_no_skill_sends_no_system_prompt(tmp_path, monkeypatch):
    bin_dir = _install_shim(tmp_path, monkeypatch)
    rs = _import_run_skill(monkeypatch)
    rs.run("hi", with_skill=False, backend="claude-cli")
    assert "--system-prompt" not in _call(bin_dir)["argv"]


_JUDGE_BODY = """
user = record["stdin"]
if '"winner"' in user:
    inner = {"winner": "A", "why": "clean"}
else:
    dims = ["voice", "clarity", "persuasion", "human_rhythm", "restraint", "truth"]
    inner = {"scores": {d: {"score": 5, "why": "x"} for d in dims},
             "would_send": True, "sounds_ai": False, "eval_critique": "fine"}
env = {"type": "result", "subtype": "success", "is_error": False,
       "result": json.dumps(inner), "stop_reason": "end_turn",
       "usage": {"input_tokens": 10, "output_tokens": 5}, "total_cost_usd": 0.001}
print(json.dumps(env))
"""


def test_judge_scores_through_cli_backend(tmp_path, monkeypatch):
    _install_shim(tmp_path, monkeypatch, body=_JUDGE_BODY)
    j = _import_judge(monkeypatch)
    res = j.score_absolute("some text", "the task", runs=1, backend="claude-cli")
    assert res["failed"] == 0
    assert res["mean_overall"] == 5.0
    assert llm_backend.usage_snapshot()["calls"] == 1


def test_judge_pairwise_through_cli_backend(tmp_path, monkeypatch):
    _install_shim(tmp_path, monkeypatch, body=_JUDGE_BODY)
    j = _import_judge(monkeypatch)
    res = j.compare_pairwise("clean text", "slop text", "the task", runs=2, seed=7,
                             backend="claude-cli")
    assert res["failed"] == 0 and res["invalid"] == 0
    assert res["wins"] + res["losses"] + res["ties"] == 2  # every judgment landed


def test_judge_cli_failure_is_a_recorded_run_not_a_crash(tmp_path, monkeypatch):
    # NEGATIVE-PATH CANARY: a dying CLI during judging must become a `failed` sample,
    # exactly like malformed API JSON always has.
    _install_shim(tmp_path, monkeypatch, body="""
sys.exit(2)
""")
    j = _import_judge(monkeypatch)
    res = j.score_absolute("some text", "the task", runs=1, backend="claude-cli")
    assert res["failed"] == 1
    assert res["median_scores"] is None
    assert "exited 2" in res["samples"][0]["error"]


# ---------------------------------------------------------------- end-to-end: run_eval subprocess

RUN_EVAL = os.path.join(REPO, "tests", "run_eval.py")
CASES = os.path.join(REPO, "tests", "cases.json")

# The e2e shim delegates to the SAME canned mock seams the keyless rehearsal uses
# (run_skill._mock_output / judge._mock_judge_text), so the full pipeline goes green
# through the claude-cli transport without a single real model call.
_E2E_BODY_TEMPLATE = """
os.environ["VOICESTEAD_MOCK"] = "1"
sys.path.insert(0, %(tests)r)
sys.path.insert(0, %(judge_dir)r)
import run_skill, judge
user = record["stdin"]
if '"winner"' in user or "## The writing to grade" in user:
    text = judge._mock_judge_text(user)
else:
    text = run_skill._mock_output(user, "--system-prompt" in sys.argv)
env = {"type": "result", "subtype": "success", "is_error": False, "result": text,
       "stop_reason": "end_turn", "usage": {"input_tokens": 11, "output_tokens": 7},
       "total_cost_usd": 0.001}
print(json.dumps(env))
"""


def _e2e_env(tmp_path, bin_dir):
    """Non-mock env: shimmed claude first on PATH, anthropic import poisoned, models unset."""
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("VOICESTEAD_") and k not in ("SKILL_MODEL", "JUDGE_MODEL")}
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    poison = tmp_path / "poison"
    poison.mkdir(exist_ok=True)
    (poison / "anthropic.py").write_text(
        "raise ImportError('anthropic must not be imported on the claude-cli backend')\n")
    env["PYTHONPATH"] = str(poison) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def test_run_eval_end_to_end_through_fake_cli(tmp_path):
    body = _E2E_BODY_TEMPLATE % {"tests": TESTS, "judge_dir": os.path.join(TESTS, "judge")}
    bin_dir = tmp_path / "fakebin"
    bin_dir.mkdir()
    shim = bin_dir / "claude"
    shim.write_text(_SHIM_TEMPLATE % {"body": body})
    shim.chmod(shim.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    out = tmp_path / "res"
    p = subprocess.run([sys.executable, RUN_EVAL, "--cases", CASES, "--runs", "1",
                        "--ids", "3,6,4", "--out", str(out)],
                       capture_output=True, text=True, env=_e2e_env(tmp_path, bin_dir))
    assert p.returncode == 0, "stdout:\n%s\nstderr:\n%s" % (p.stdout, p.stderr)
    assert "release gate: PASS" in p.stdout

    with open(os.path.join(str(out), "benchmark.json")) as f:
        b = json.load(f)
    md = b["metadata"]
    assert md["backend"] == "claude-cli" and md["mock"] is False
    assert md["skill_model"] == "claude-sonnet-5"
    assert md["judge_model"] == "claude-opus-4-8"
    assert "run_eval.py" in md["command"]
    # 3 cases x 1 run: case 3 = with + without + 1 score + 1 pairwise; cases 6 and 4 =
    # 1 generation + 1 score each -> 8 CLI calls, tokens/cost summed from the envelopes
    u = md["llm_usage"]
    assert u["calls"] == 8
    assert u["input_tokens"] == 88 and u["output_tokens"] == 56
    assert u["total_cost_usd"] == pytest.approx(0.008) and u["cost_reported"] is True


def test_run_eval_without_claude_binary_fails_loud_with_install_hint(tmp_path):
    # NEGATIVE-PATH CANARY for the default backend: no claude on PATH must produce
    # errored cases and a failing release gate, with the fix named in the record.
    empty = tmp_path / "emptybin"
    empty.mkdir()
    env = _e2e_env(tmp_path, empty)
    env["PATH"] = str(empty)  # nothing else on PATH; sys.executable is absolute
    out = tmp_path / "res"
    p = subprocess.run([sys.executable, RUN_EVAL, "--cases", CASES, "--runs", "1",
                        "--ids", "4", "--out", str(out)],
                       capture_output=True, text=True, env=env)
    assert p.returncode != 0
    with open(os.path.join(str(out), "benchmark.json")) as f:
        b = json.load(f)
    rec = b["runs"][0]
    assert "Install Claude Code" in rec["error"] and "--backend api" in rec["error"]
    assert b["overall"]["cases_with_errors"] == 1


def test_run_eval_mock_metadata_records_mock_backend(tmp_path):
    env = dict(os.environ, VOICESTEAD_MOCK="1")
    out = tmp_path / "res"
    p = subprocess.run([sys.executable, RUN_EVAL, "--cases", CASES, "--runs", "1",
                        "--ids", "4", "--out", str(out)],
                       capture_output=True, text=True, env=env)
    assert p.returncode == 0, p.stdout + p.stderr
    with open(os.path.join(str(out), "benchmark.json")) as f:
        md = json.load(f)["metadata"]
    assert md["backend"] == "mock" and md["mock"] is True
    assert md["llm_usage"]["calls"] == 0  # the seam was never touched


# ---------------------------------------------------------------- live smoke (opt-in only)


@pytest.mark.skipif(os.environ.get("VOICESTEAD_LIVE_SMOKE", "") in ("", "0"),
                    reason="live smoke is opt-in: VOICESTEAD_LIVE_SMOKE=1 runs ONE real "
                           "claude CLI call on your subscription; never runs in CI")
def test_live_smoke_one_real_cli_call():
    out = llm_backend.complete("Reply with the single word: ok", model="claude-haiku-4-5",
                               backend="claude-cli")
    assert out.strip()
    u = llm_backend.usage_snapshot()
    assert u["calls"] == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
