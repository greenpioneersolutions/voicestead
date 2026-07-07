#!/usr/bin/env python3
"""Tier-2 LLM-as-judge. Absolute scoring and blind pairwise comparison.

Judge calls route through tests/llm_backend.py: the default backend (claude-cli) runs
on a Claude Code subscription with no API key; `--backend api` (or
VOICESTEAD_BACKEND=api) uses the Anthropic SDK and needs ANTHROPIC_API_KEY. Model via
--model or $JUDGE_MODEL (default: a strong, current model). Use a judge from a
DIFFERENT model family than the one under test to reduce self-preference bias. Set
VOICESTEAD_MOCK=1 for a keyless run: deterministic canned (but valid) verdicts and
scores, and no backend is ever invoked.

Parsing is strict, and failure is contained instead of fatal:
- a malformed response (bad JSON, truncation) is retried once, then recorded as a
  `failed` run — never an uncaught exception, never a silent zero;
- a pairwise verdict that is not exactly "A"/"B"/"tie" is retried once, then counted
  as `invalid` — explicitly reported, never scored as a loss;
- pairwise `win_rate` counts ties in the denominator; `decisive_win_rate` excludes them.

  python tests/judge/judge.py --output out.txt --prompt prompt.txt [--voice sample.txt] [--rubric r.md] --runs 3
  python tests/judge/judge.py --compare with_skill.txt without_skill.txt --prompt prompt.txt --runs 3

Mock knobs (test-only, all require VOICESTEAD_MOCK=1):
  VOICESTEAD_MOCK_PAIR=win|loss|tie|invalid   pairwise behavior (default: vote for the clean side)
  VOICESTEAD_MOCK_MALFORMED=score|pair|all    return unparseable text for that call type
  VOICESTEAD_MOCK_LOW_SCORES=1                absolute scores 2-3 instead of 4-5
"""
import argparse, hashlib, json, os, random, re, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
if TESTS not in sys.path:
    sys.path.insert(0, TESTS)  # llm_backend lives one level up, in tests/
import llm_backend

MOCK = os.environ.get("VOICESTEAD_MOCK", "") not in ("", "0")

MODEL = os.environ.get("JUDGE_MODEL", "claude-opus-4-8")

# ---------- mock seam (VOICESTEAD_MOCK=1): canned verdicts/scores, zero network ----------

# run_skill's mock no-skill baseline always carries this phrase, so the mock judge can
# recognize the baseline side regardless of A/B order randomization.
_SLOP_MARKER = "I hope this message finds you well"

_ABS_DIMS = ["voice", "clarity", "persuasion", "human_rhythm", "restraint", "truth"]
_MATRIX_DIMS = ["task_quality", "instruction_adherence", "tone_fidelity",
                "register_contamination", "human_rhythm"]


def _mock_judge_text(user):
    malform = os.environ.get("VOICESTEAD_MOCK_MALFORMED", "")
    if '"winner"' in user:  # pairwise prompt
        if malform in ("pair", "all"):
            return 'the judge rambles instead of JSON {"winner": "A"'
        mode = os.environ.get("VOICESTEAD_MOCK_PAIR", "win")
        if mode == "tie":
            return '{"winner": "tie", "why": "mock tie"}'
        if mode == "invalid":
            return '{"winner": "C", "why": "mock invalid verdict"}'
        a = user.split("\n## A\n", 1)[1].split("\n## B\n", 1)[0]
        b = user.split("\n## B\n", 1)[1]
        a_slop, b_slop = _SLOP_MARKER in a, _SLOP_MARKER in b
        if a_slop == b_slop:
            winner = "tie"
        elif mode == "loss":
            winner = "A" if a_slop else "B"  # vote FOR the sloppy baseline side
        else:
            winner = "B" if a_slop else "A"  # vote for the clean side
        return json.dumps({"winner": winner, "why": "mock: picked the cleaner text"})
    if malform in ("score", "all"):
        return "no json here, just vibes"
    graded = user.split("## The writing to grade\n", 1)[-1]
    h = int(hashlib.sha256(graded.encode("utf-8")).hexdigest()[:8], 16)
    low = os.environ.get("VOICESTEAD_MOCK_LOW_SCORES", "") not in ("", "0")
    base = 2 if low else 4
    dims = _MATRIX_DIMS if "task_quality" in user else _ABS_DIMS
    scores = {d: {"score": min(5, base + ((h >> i) & 1)), "why": "mock"} for i, d in enumerate(dims)}
    return json.dumps({"scores": scores, "would_send": not low, "sounds_ai": low,
                       "eval_critique": "mock critique: a wrong output could also pass the vaguest assertion"})


class _MockBlock(object):
    type = "text"

    def __init__(self, text):
        self.text = text


class _MockMsg(object):
    def __init__(self, text):
        self.content = [_MockBlock(text)]
        self.stop_reason = "end_turn"


class _MockMessages(object):
    def create(self, **kwargs):
        return _MockMsg(_mock_judge_text(kwargs["messages"][0]["content"]))


class _MockClient(object):
    def __init__(self):
        self.messages = _MockMessages()


# ---------- client + strict parsing ----------

_CLIENT = None


def _client():
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = _MockClient()  # only the mock path uses this; real calls go via llm_backend
    return _CLIENT


def _extract_json(text):
    """First JSON object in the text. raw_decode tolerates trailing prose and braces
    inside string values, which the old hand-rolled brace counter did not."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    start = text.find("{")
    if start == -1:
        raise ValueError("no JSON object in judge response")
    obj, _ = json.JSONDecoder().raw_decode(text, start)
    return obj


def _judge_call(user, model, max_tokens, backend=None):
    """One judge call, strictly parsed. Retries once on any failure (malformed JSON,
    truncation, backend error), then returns (None, error) — the caller records a failed
    run and keeps going. Returns (obj, None) on success."""
    attempt_user = user
    last_err = None
    for _ in range(2):
        try:
            if MOCK:
                msg = _client().messages.create(model=model, max_tokens=max_tokens,
                                                messages=[{"role": "user", "content": attempt_user}])
                text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
            else:
                text = llm_backend.complete(attempt_user, model=model,
                                            max_tokens=max_tokens, backend=backend)
            return _extract_json(text), None
        except Exception as e:  # noqa: BLE001 — a judge failure must be a recorded run, not a crash
            last_err = "%s: %s" % (type(e).__name__, e)
            attempt_user = user + "\n\nReturn ONLY the JSON object - no prose, no code fences."
    return None, last_err


# ---------- scoring ----------

def score_absolute(output, prompt, voice="", runs=3, rubric_path=None, dims=None, model=None,
                   backend=None):
    """Absolute rubric scoring, `runs` samples. `voice` (the loaded profile/influences text)
    is shown to the judge when provided. `dims` restricts scoring and aggregation to those
    rubric dimensions (the case's rubric_dimensions). A sample that stays malformed after
    one retry is recorded as {"error": ...} and counted in `failed` — never a silent zero."""
    model = model or MODEL
    rubric = open(rubric_path or os.path.join(HERE, "rubric.md")).read()
    voice_block = "\n\n## Writer's voice sample (match this)\n%s\n" % voice if voice else ""
    dims_block = ("\nScore ONLY these dimensions and omit the rest: %s.\n" % ", ".join(dims)) if dims else ""
    user = ("%s\n\n---\n## Task the writer was given\n%s%s%s\n\n"
            "## The writing to grade\n%s\n\nReturn only the JSON." % (rubric, prompt, voice_block, dims_block, output))
    samples = []
    failed = 0
    for _ in range(runs):
        obj, err = _judge_call(user, model, 1024, backend=backend)
        if obj is None:
            failed += 1
            samples.append({"error": err})
            continue
        try:
            scores = obj["scores"]
            want = list(dims) if dims else list(scores.keys())
            if not want:
                raise ValueError("empty scores object")
            clean = {}
            for d in want:
                s = int(scores[d]["score"])
                if not 1 <= s <= 5:
                    raise ValueError("score out of range for %s: %s" % (d, s))
                clean[d] = s
            obj["_clean_scores"] = clean
            samples.append(obj)
        except (KeyError, TypeError, ValueError) as e:
            failed += 1
            samples.append({"error": "invalid score JSON: %s: %s" % (type(e).__name__, e), "raw": obj})
    valid = [s for s in samples if "_clean_scores" in s]
    agg = None
    mean_overall = None
    if valid:
        all_dims = list(dims) if dims else sorted({d for s in valid for d in s["_clean_scores"]})
        agg = {d: statistics.median([s["_clean_scores"][d] for s in valid if d in s["_clean_scores"]])
               for d in all_dims}
        mean_overall = round(statistics.mean(agg.values()), 2) if agg else None
    return {"model": model, "runs": runs, "failed": failed,
            "median_scores": agg, "mean_overall": mean_overall,
            "would_send_rate": round(sum(1 for s in valid if s.get("would_send")) / len(valid), 2) if valid else None,
            "sounds_ai_rate": round(sum(1 for s in valid if s.get("sounds_ai")) / len(valid), 2) if valid else None,
            "critiques": [s.get("eval_critique", "") for s in valid if s.get("eval_critique")],
            "samples": samples}


def compare_pairwise(a_text, b_text, prompt, runs=3, voice="", seed=None, model=None,
                     backend=None):
    """Blind A/B. Order is randomized per judgment (seeded, so runs reproduce) to cancel
    position bias; results are reported for the FIRST argument (by convention, with-skill).

    win_rate = wins / (wins + losses + ties) — ties count in the denominator and are
    reported separately. Verdicts other than exactly "A"/"B"/"tie" are retried once and
    then counted as `invalid` (reported, never a loss); responses that stay malformed
    after a retry are counted as `failed`."""
    model = model or MODEL
    rng = random.Random(seed)
    wins = losses = ties = invalid = failed = 0
    detail = []
    voice_block = "\n\n## Writer's voice sample (the better text matches this)\n%s\n" % voice if voice else ""
    for _ in range(runs):
        swap = rng.random() < 0.5
        left, right = (b_text, a_text) if swap else (a_text, b_text)
        user = ("You are a discerning editor. For the task below, two candidate texts follow, "
                "labeled A and B. Pick the one you would actually send. Judge voice, clarity, "
                "persuasion, human rhythm, restraint, and truthfulness. Do not reward length.\n\n"
                "## Task\n%s%s\n\n## A\n%s\n\n## B\n%s\n\n"
                'Return only JSON: {"winner":"A"|"B"|"tie","why":"one sentence"}'
                % (prompt, voice_block, left, right))
        obj, err = _judge_call(user, model, 400, backend=backend)
        if obj is None:
            failed += 1
            detail.append({"failed": err, "order_swapped": swap})
            continue
        winner = obj.get("winner")
        if winner not in ("A", "B", "tie"):
            # parseable JSON but an invalid verdict: one stricter retry, then report as invalid
            obj2, _err2 = _judge_call(
                user + '\n\nThe "winner" value MUST be exactly "A", "B", or "tie".', model, 400,
                backend=backend)
            winner = obj2.get("winner") if isinstance(obj2, dict) else None
            if winner not in ("A", "B", "tie"):
                invalid += 1
                detail.append({"invalid_verdict": repr(obj.get("winner")), "order_swapped": swap})
                continue
            obj = obj2
        first_is_a = not swap
        if winner == "tie":
            ties += 1
            original = "tie"
        else:
            a_won = (winner == "A") == first_is_a
            original = "a" if a_won else "b"
            if a_won:
                wins += 1
            else:
                losses += 1
        detail.append({"winner_original": original, "why": obj.get("why", ""), "order_swapped": swap})
    valid = wins + losses + ties
    return {"model": model, "runs": runs, "wins": wins, "losses": losses, "ties": ties,
            "invalid": invalid, "failed": failed, "valid": valid,
            "win_rate": round(wins / valid, 3) if valid else None,
            "decisive_win_rate": round(wins / (wins + losses), 3) if (wins + losses) else None,
            "detail": detail}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--voice", default="")
    ap.add_argument("--rubric", default=None, help="path to an alternate rubric (default: judge/rubric.md)")
    ap.add_argument("--compare", nargs=2, metavar=("A", "B"))
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--backend", default=None, choices=llm_backend.BACKENDS,
                    help="claude-cli (default; runs on your Claude Code subscription) or "
                         "api (Anthropic SDK, needs ANTHROPIC_API_KEY)")
    args = ap.parse_args()
    prompt = open(args.prompt).read() if os.path.exists(args.prompt) else args.prompt

    if args.compare:
        a = open(args.compare[0]).read()
        b = open(args.compare[1]).read()
        print(json.dumps(compare_pairwise(a, b, prompt, runs=args.runs, model=args.model,
                                          backend=args.backend), indent=2))
    else:
        if not args.output:
            ap.error("provide --output or --compare")
        out = open(args.output).read()
        voice = open(args.voice).read() if args.voice and os.path.exists(args.voice) else args.voice
        print(json.dumps(score_absolute(out, prompt, voice=voice, runs=args.runs,
                                        rubric_path=args.rubric, model=args.model,
                                        backend=args.backend), indent=2))


if __name__ == "__main__":
    main()
