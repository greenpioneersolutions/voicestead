#!/usr/bin/env python3
"""Backend seam: one place that turns a single-turn prompt into text.

Two real backends plus the mock override, resolved with the precedence
CLI flag > VOICESTEAD_BACKEND env > default "claude-cli":

- "claude-cli" (default) shells out to the installed ``claude`` binary in print
  mode, so the harness runs on a Claude Code subscription with no API key. The
  prompt travels over STDIN (never argv - quoting and ARG_MAX), the output comes
  back as one JSON envelope (``--output-format json``), all tools are disabled
  (``--tools ""``), and with no tools a print-mode run is a single turn by
  construction (the installed CLI, 2.1.195, has no turn-limit flag). ``--bare``
  is deliberately NOT used: it disables subscription auth, the point of this path.
- "api" is the Anthropic SDK path and needs ANTHROPIC_API_KEY. The anthropic
  package is imported lazily, only when this backend actually generates, so the
  default backend works without it installed.
- VOICESTEAD_MOCK=1 trumps everything: resolve_backend() returns "mock", and the
  mock-aware callers (run_skill.py, judge/judge.py) answer from their own canned
  seams without ever reaching complete().

Fail-loud contract, the same philosophy as the stop_reason guard this module
absorbed from run_skill.py: a missing binary, a nonzero exit, an error envelope,
unparseable output, an empty result, or a truncated/refused generation RAISES
RuntimeError - a bad generation must never be graded.

Token and cost figures are captured per call, only when the backend reports them
(the CLI envelope carries usage and total_cost_usd; the SDK reports tokens and
never dollars). run_eval.py snapshots the totals into benchmark.json for the run
ledger (scripts/log_eval_run.py). Nothing here estimates a number.
"""
import json
import os
import shutil
import subprocess

DEFAULT_BACKEND = "claude-cli"
BACKENDS = ("claude-cli", "api")

_CLI_TIMEOUT = 600  # seconds per generation; a hung CLI must fail the run, not stall it

_USAGE = {"calls": 0, "input_tokens": 0, "output_tokens": 0,
          "total_cost_usd": 0.0, "cost_reported": False}


def resolve_backend(cli_choice=None):
    """CLI flag > VOICESTEAD_BACKEND env > default. VOICESTEAD_MOCK=1 trumps all."""
    if os.environ.get("VOICESTEAD_MOCK", "") not in ("", "0"):
        return "mock"
    choice = cli_choice or os.environ.get("VOICESTEAD_BACKEND") or DEFAULT_BACKEND
    if choice not in BACKENDS:
        raise ValueError("unknown backend %r (valid: %s; or set VOICESTEAD_MOCK=1)"
                         % (choice, ", ".join(BACKENDS)))
    return choice


def usage_snapshot():
    """Totals across every complete() call in this process, for benchmark metadata."""
    return dict(_USAGE)


def reset_usage():
    _USAGE.update(calls=0, input_tokens=0, output_tokens=0,
                  total_cost_usd=0.0, cost_reported=False)


def _record_usage(usage, cost):
    """Accumulate ONLY what the backend reported. cost stays 0/unreported otherwise."""
    _USAGE["calls"] += 1
    if isinstance(usage, dict):
        for field in ("input_tokens", "output_tokens"):
            v = usage.get(field)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                _USAGE[field] += int(v)
    if isinstance(cost, (int, float)) and not isinstance(cost, bool):
        _USAGE["total_cost_usd"] = round(_USAGE["total_cost_usd"] + cost, 6)
        _USAGE["cost_reported"] = True


def complete(prompt, model, system=None, max_tokens=4000, temperature=None, backend=None):
    """One single-turn completion, routed by backend. Returns the text or raises.

    ``max_tokens``/``temperature`` apply to the api backend; the CLI manages its
    own output budget (truncation still raises via the envelope's stop_reason)
    and cannot set temperature, so a non-None temperature there is an error,
    never a silent ignore.
    """
    backend = backend or resolve_backend()
    if backend == "api":
        return _api_complete(prompt, model, system, max_tokens, temperature)
    if backend == "claude-cli":
        return _cli_complete(prompt, model, system, temperature)
    raise RuntimeError("backend %r cannot generate here (mock-aware callers answer from "
                       "their own seams and must not reach llm_backend.complete)" % backend)


# ---------- api backend (Anthropic SDK; lazy import so claude-cli needs no package) ----------

_CLIENT = None


def _get_client():
    global _CLIENT
    if _CLIENT is None:
        try:
            from anthropic import Anthropic
        except ImportError:
            raise RuntimeError(
                "the api backend needs the anthropic package: pip install anthropic "
                "(or use the default claude-cli backend, or set VOICESTEAD_MOCK=1)")
        _CLIENT = Anthropic()  # reads ANTHROPIC_API_KEY
    return _CLIENT


def _finalize(msg):
    """Reject truncated/refused/empty generations instead of returning them for grading."""
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    stop = getattr(msg, "stop_reason", None)
    if stop not in ("end_turn", "stop_sequence"):
        raise RuntimeError(
            "generation failed: stop_reason=%r (max_tokens means the output was truncated - "
            "raise max_tokens; refusal means the model declined). This output must not be graded."
            % stop)
    if not text.strip():
        raise RuntimeError("generation failed: the model returned an empty text body; nothing to grade")
    return text


def _api_complete(prompt, model, system, max_tokens, temperature):
    kwargs = {"model": model, "max_tokens": max_tokens,
              "messages": [{"role": "user", "content": prompt}]}
    if temperature is not None:
        kwargs["temperature"] = temperature
    if system:
        kwargs["system"] = system
    msg = _get_client().messages.create(**kwargs)
    text = _finalize(msg)
    u = getattr(msg, "usage", None)
    _record_usage({"input_tokens": getattr(u, "input_tokens", None),
                   "output_tokens": getattr(u, "output_tokens", None)} if u is not None else None,
                  None)  # the SDK reports tokens, never dollars - no cost is recorded here
    return text


# ---------- claude-cli backend (print mode on the installed binary) ----------

def _cli_complete(prompt, model, system, temperature):
    if temperature is not None:
        raise RuntimeError("the claude-cli backend cannot set temperature; use --backend api")
    binary = shutil.which("claude")
    if not binary:
        raise RuntimeError(
            "claude CLI not found on PATH. Install Claude Code "
            "(https://claude.com/claude-code) or run with --backend api.")
    cmd = [binary, "-p", "--output-format", "json", "--tools", "",
           "--no-session-persistence", "--model", model]
    if system:
        cmd += ["--system-prompt", system]
    try:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                              timeout=_CLI_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise RuntimeError("claude CLI timed out after %ds; nothing to grade" % _CLI_TIMEOUT)
    if proc.returncode != 0:
        raise RuntimeError("claude CLI exited %d: %s"
                           % (proc.returncode, (proc.stderr or proc.stdout).strip()[:500]))
    try:
        envelope = json.loads(proc.stdout)
    except ValueError:
        raise RuntimeError("claude CLI returned unparseable JSON: %r" % proc.stdout[:200])
    if not isinstance(envelope, dict):
        raise RuntimeError("claude CLI returned a non-object envelope: %r" % proc.stdout[:200])
    if envelope.get("is_error") or envelope.get("subtype") != "success":
        raise RuntimeError("claude CLI reported an error envelope (subtype=%r): %s"
                           % (envelope.get("subtype"), str(envelope.get("result"))[:500]))
    stop = envelope.get("stop_reason")
    if stop is not None and stop not in ("end_turn", "stop_sequence"):
        raise RuntimeError(
            "generation failed: stop_reason=%r - a truncated or refused output "
            "must not be graded" % stop)
    result = envelope.get("result")
    if not isinstance(result, str) or not result.strip():
        raise RuntimeError("claude CLI returned an empty result; nothing to grade")
    _record_usage(envelope.get("usage"), envelope.get("total_cost_usd"))
    return result
