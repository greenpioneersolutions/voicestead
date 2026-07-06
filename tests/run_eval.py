#!/usr/bin/env python3
"""Orchestrator: the with/without benchmark.

For each case, generate N outputs WITH the skill and (if baseline_compare) N WITHOUT.
Both arms go through Tier 1 (deterministic checks), so the report carries the
with/without pass-rate delta and flags checks that pass in both configurations
(non-discriminating). Every generated with/without pair is compared blind at Tier 2,
and each with-skill output is rubric-scored on the case's declared rubric_dimensions,
with any loaded voice-profile/influences fixture shown to the judge. Emits
benchmark.json (Anthropic schema) + a human-readable scorecard.md.

Gates (always enforced):
- Tier-1 hard checks, plus any failing deterministic check named in the case's
  must_pass list (promoted to hard regardless of registry severity).
- Declared metamorphic properties: length_delta_max (output vs source) and
  output_to_input_ratio_max (output vs prompt).
- Rubric dimensions named in must_pass: median judge score must be >= 4.
- A case that errors mid-run.
`--gate` additionally fails the run when the pooled blind win rate lands below
`--min-win-rate` (default 0.70, ties in the denominator) or cannot be computed —
the weekly CI job passes `--gate`.

Robustness: each case's record is flushed to <out>/partial/case-NN.json the moment it
completes, and the final benchmark is assembled by reading those files back, so a crash
late in a paid run loses nothing (`--resume` skips cases that already have a record).
Malformed judge output is retried once, then recorded as a failed run - never a crash.

Requires ANTHROPIC_API_KEY, or VOICESTEAD_MOCK=1 for a keyless end-to-end rehearsal.
For keyless deterministic checks against the committed corpus use tests/checks/run_checks.py.

  python tests/run_eval.py --cases tests/cases.json --runs 3 --out tests/results [--ids 1,2,5] [--gate]
"""
import argparse, json, os, statistics, sys
from datetime import datetime, timezone

TESTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TESTS, "checks"))
sys.path.insert(0, os.path.join(TESTS, "judge"))
import text_metrics as tm

REPO = os.path.dirname(TESTS)
SKILL_DIR = os.path.join(REPO, "skills", "voicestead")
RUBRIC_DIMS = ("voice", "clarity", "persuasion", "human_rhythm", "restraint", "truth")
VOICE_FIXTURE_HINTS = ("voice-profile", "influences")


def _mean_std(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"mean": None, "stddev": None}
    return {"mean": round(statistics.mean(xs), 3),
            "stddev": round(statistics.pstdev(xs), 3) if len(xs) > 1 else 0.0}


def _load_text(load):
    """Concatenated text of every file a case loads (paths are skill-relative)."""
    parts = []
    for rel in (load or []):
        path = os.path.join(SKILL_DIR, rel)
        if os.path.exists(path):
            parts.append(open(path).read())
    return "\n".join(parts)


def _voice_text(load):
    """Only the personal-fixture files (voice profile / influences) - the material the
    judge must see to grade voice for cases that load them."""
    fixtures = [rel for rel in (load or [])
                if any(h in os.path.basename(rel) for h in VOICE_FIXTURE_HINTS)]
    return _load_text(fixtures)


def tier1(output, case, prompt, loaded_text=""):
    """Tier-1 gate for one output.

    `source` handed to the checks = the case's source plus the text of every loaded
    file, so figures that come from loaded context are licensed, not 'invented'.
    Failing deterministic checks named in must_pass are promoted to hard failures;
    the case's declared metamorphic property is enforced here too."""
    source = "\n".join(x for x in (case.get("source", ""), loaded_text) if x)
    results = tm.run(output, case.get("deterministic_checks", []), prompt=prompt, source=source)
    hard_fail = [r["id"] for r in results if r["severity"] == "hard" and not r["passed"]]
    must = case.get("must_pass", [])
    for r in results:
        if r["id"] in must and not r["passed"] and r["id"] not in hard_fail:
            hard_fail.append(r["id"])

    meta = case.get("metamorphic")
    meta_rec = None
    if meta:
        prop, val = meta["property"], meta["value"]
        ow = tm.word_count(output)
        if prop == "output_to_input_ratio_max":
            pw = tm.word_count(prompt)
            failed = ow > val * pw
            detail = "output %dw vs prompt %dw (max ratio %s)" % (ow, pw, val)
        elif prop == "length_delta_max" and case.get("source"):
            sw = tm.word_count(case["source"])
            failed = abs(ow - sw) > val * sw
            detail = "output %dw vs source %dw (max delta %s)" % (ow, sw, val)
        elif prop == "per_section_tell_rise_max":
            # session-drift guard: per-section tell density must not rise. The first
            # section is the baseline; any later section may not exceed it by more
            # than `value` tell-words per 200 words. Single-section outputs pass.
            secs = tm.split_sections(output)
            rates = [tm.check_tell_flags((h + "\n" + b) if h else b)["metric"]
                     for h, b in secs]
            failed = len(rates) > 1 and any(r > rates[0] + val for r in rates[1:])
            detail = ("per-section tell rates %s; first section %s is the baseline "
                      "(max rise %s)" % (rates, rates[0], val))
        else:
            failed, detail = True, "unknown or unevaluable metamorphic property %r" % prop
        meta_rec = {"property": prop, "value": val, "passed": not failed, "detail": detail}
        if failed and prop not in hard_fail:
            hard_fail.append(prop)

    # a must_pass id that names nothing this case runs would otherwise be a silent dead gate
    known = {r["id"] for r in results} | set(RUBRIC_DIMS)
    if meta:
        known.add(meta["property"])
    for mp in must:
        if mp not in known:
            tag = "%s (must_pass id matches no check or rubric dimension)" % mp
            if tag not in hard_fail:
                hard_fail.append(tag)

    passed = sum(1 for r in results if r["passed"])
    return {"results": results, "metamorphic": meta_rec, "hard_fail": hard_fail,
            "pass_rate": round(passed / len(results), 3) if results else 1.0}


def _non_discriminating(t1_with, t1_without):
    """Check ids that passed in every run of BOTH arms - they prove nothing about the skill."""
    if not t1_with or not t1_without:
        return []

    def all_pass(runs, cid):
        vals = [r["passed"] for t in runs for r in t["results"] if r["id"] == cid]
        return bool(vals) and all(vals)

    ids = sorted({r["id"] for t in t1_with for r in t["results"]})
    return [cid for cid in ids if all_pass(t1_with, cid) and all_pass(t1_without, cid)]


def _tier2_must_pass_failures(case, judge_runs):
    """Rubric dimensions named in must_pass are enforced at Tier 2: median score >= 4.
    A dimension with no valid judge scores cannot be verified, which is a failure, not a pass."""
    fails = []
    for d in [m for m in case.get("must_pass", []) if m in RUBRIC_DIMS]:
        vals = [j["median_scores"][d] for j in judge_runs
                if j.get("median_scores") and d in j["median_scores"]]
        if not vals:
            fails.append("%s (no valid judge scores)" % d)
        elif statistics.median(vals) < 4:
            fails.append(d)
    return fails


def _pool_pairs(pairs):
    """Pool the per-pair blind comparisons into one case-level tally.
    win_rate keeps ties in the denominator; invalid/failed are reported, never losses."""
    tot = {k: sum(p[k] for p in pairs) for k in ("wins", "losses", "ties", "invalid", "failed")}
    valid = tot["wins"] + tot["losses"] + tot["ties"]
    tot.update({"valid": valid, "n_pairs": len(pairs),
                "win_rate": round(tot["wins"] / valid, 3) if valid else None,
                "decisive_win_rate": round(tot["wins"] / (tot["wins"] + tot["losses"]), 3)
                                     if (tot["wins"] + tot["losses"]) else None,
                "pairs": pairs})
    return tot


def _evaluate_case(case, args, run_skill, judge):
    prompt = case["prompt"]
    load = case.get("load", [])
    loaded_text = _load_text(load)
    voice = _voice_text(load)

    with_outs, without_outs = [], []
    for _ in range(args.runs):
        with_outs.append(run_skill.run(prompt, with_skill=True, load=load))
        if case.get("baseline_compare"):
            without_outs.append(run_skill.run(prompt, with_skill=False))

    # Tier 1 on BOTH arms - the without arm is what makes the pass-rate delta meaningful
    t1 = [tier1(o, case, prompt, loaded_text) for o in with_outs]
    t1_wo = [tier1(o, case, prompt, loaded_text) for o in without_outs]
    rate_w = _mean_std([t["pass_rate"] for t in t1])
    rate_wo = _mean_std([t["pass_rate"] for t in t1_wo])
    delta = (round(rate_w["mean"] - rate_wo["mean"], 3)
             if rate_w["mean"] is not None and rate_wo["mean"] is not None else None)

    # Tier 2: rubric scoring restricted to the case's declared dimensions, with any
    # loaded voice/influences fixture shown to the judge
    dims = case.get("rubric_dimensions") or None
    j = [judge.score_absolute(o, prompt, voice=voice, runs=args.judge_runs, dims=dims)
         for o in with_outs]

    # blind pairwise on EVERY generated pair, seeded per pair for reproducible ordering
    pairs = []
    if case.get("baseline_compare"):
        for k, (w, wo) in enumerate(zip(with_outs, without_outs)):
            pairs.append(judge.compare_pairwise(w, wo, prompt, runs=args.pair_judgments,
                                                voice=voice, seed=case["id"] * 1000 + k))

    return {"eval_id": case["id"], "mode": case.get("mode"), "type": case.get("type"),
            "with_skill_tier1": t1,
            "tier1_pass_rate": rate_w,
            "without_skill_tier1": t1_wo,
            "tier1_pass_rate_without": rate_wo,
            "pass_rate_delta": delta,
            "non_discriminating_checks": _non_discriminating(t1, t1_wo),
            "hard_fails": sorted({h for t in t1 for h in t["hard_fail"]}),
            "tier2_must_pass_failures": _tier2_must_pass_failures(case, j),
            "judge": j,
            "judge_failed_samples": sum(run.get("failed", 0) for run in j),
            "judge_critiques": [c for run in j for c in run.get("critiques", [])],
            "pairwise": _pool_pairs(pairs) if pairs else None}


def _partial_path(out, cid):
    return os.path.join(out, "partial", "case-%02d.json" % int(cid))


def _write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--out", default="tests/results")
    ap.add_argument("--ids", default="")
    ap.add_argument("--judge-runs", type=int, default=1,
                    help="judge samples per generated output (median-of-N; default 1)")
    ap.add_argument("--pair-judgments", type=int, default=1,
                    help="blind judgments per with/without pair (every pair is compared)")
    ap.add_argument("--gate", action="store_true",
                    help="exit nonzero when the pooled blind win rate is below --min-win-rate "
                         "or cannot be computed")
    ap.add_argument("--min-win-rate", type=float, default=0.70)
    ap.add_argument("--resume", action="store_true",
                    help="skip cases that already have a record in <out>/partial/")
    ap.add_argument("--tier1-only", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if args.tier1_only:
        ap.error("--tier1-only cannot run: this orchestrator grades outputs it generates, so "
                 "there is nothing to check without generation. For keyless deterministic checks "
                 "against the committed corpus run: python tests/checks/run_checks.py --corpus "
                 "tests/corpus. For a keyless end-to-end rehearsal of THIS pipeline, set "
                 "VOICESTEAD_MOCK=1.")

    data = json.load(open(args.cases))
    cases = data["evals"]
    if args.ids:
        want = {int(x) for x in args.ids.split(",")}
        cases = [c for c in cases if c["id"] in want]
    if not cases:
        ap.error("no cases matched --ids %r; refusing to write an empty green benchmark" % args.ids)

    # A case may carry its prompt inline ("prompt") or point at a file ("prompt_file",
    # repo-relative) - the golden set keeps the writer's real pieces as plain .txt files.
    for c in cases:
        if "prompt" not in c and c.get("prompt_file"):
            c["prompt"] = open(os.path.join(REPO, c["prompt_file"])).read().strip()

    import run_skill, judge  # mock-aware: keyless when VOICESTEAD_MOCK=1

    os.makedirs(os.path.join(args.out, "partial"), exist_ok=True)
    for case in cases:
        ppath = _partial_path(args.out, case["id"])
        if args.resume and os.path.exists(ppath):
            print("case %s: partial record exists, skipping (--resume)" % case["id"])
            continue
        try:
            rec = _evaluate_case(case, args, run_skill, judge)
        except Exception as e:  # a failed case is a recorded result, not a lost run
            rec = {"eval_id": case["id"], "mode": case.get("mode"), "type": case.get("type"),
                   "error": "%s: %s" % (type(e).__name__, e)}
        _write_json(ppath, rec)
        print("case %s: %s" % (case["id"],
                               rec.get("error") or ("hard_fails=" + (",".join(rec["hard_fails"]) or "none"))))

    # final aggregation reads the partial records back - the same files a crashed or
    # resumed run leaves behind
    runs_out = [json.load(open(_partial_path(args.out, case["id"]))) for case in cases]

    hard_cases = sum(1 for r in runs_out if r.get("hard_fails"))
    t2_cases = sum(1 for r in runs_out if r.get("tier2_must_pass_failures"))
    err_cases = sum(1 for r in runs_out if r.get("error"))
    pw = [r["pairwise"] for r in runs_out if r.get("pairwise")]
    tot = {k: sum(p.get(k, 0) for p in pw) for k in ("wins", "losses", "ties", "invalid", "failed")}
    n_valid = tot["wins"] + tot["losses"] + tot["ties"]
    win = {"wins": tot["wins"], "losses": tot["losses"], "ties": tot["ties"],
           "invalid": tot["invalid"], "failed": tot["failed"], "n_valid": n_valid,
           "rate": round(tot["wins"] / n_valid, 3) if n_valid else None,
           "decisive_rate": round(tot["wins"] / (tot["wins"] + tot["losses"]), 3)
                            if (tot["wins"] + tot["losses"]) else None}
    overall = {"win_rate": win,
               "pass_rate_delta_mean": _mean_std([r.get("pass_rate_delta") for r in runs_out])["mean"],
               "cases_with_hard_failures": hard_cases,
               "cases_with_tier2_must_pass_failures": t2_cases,
               "cases_with_errors": err_cases,
               "judge_failed_samples": sum(r.get("judge_failed_samples", 0) for r in runs_out),
               "cases": len(cases)}

    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    sc = ["# Voicestead scorecard", "_generated %s_" % ts, ""]
    wr_str = ("%s (%dW/%dT/%dL of %d valid; %d invalid, %d failed)"
              % (win["rate"], win["wins"], win["ties"], win["losses"], win["n_valid"],
                 win["invalid"], win["failed"])) if win["rate"] is not None else "n/a"
    sc.append("**Overall blind win rate vs no-skill: %s** | hard-gate failures: %d/%d | "
              "tier-2 must-pass failures: %d | errored cases: %d"
              % (wr_str, hard_cases, len(cases), t2_cases, err_cases))
    sc.append("")
    for r in runs_out:
        sc.append("## Case %s (%s, %s)" % (r["eval_id"], r.get("mode"), r.get("type")))
        if r.get("error"):
            sc.append("- **ERRORED:** %s" % r["error"])
            sc.append("")
            continue
        rw, rwo = r["tier1_pass_rate"], r["tier1_pass_rate_without"]
        line = "- Tier1 pass-rate with skill: **%s** (±%s)" % (rw["mean"], rw["stddev"])
        if rwo["mean"] is not None:
            line += " | without: %s | delta: %s" % (rwo["mean"], r["pass_rate_delta"])
        sc.append(line)
        hf = r["hard_fails"]
        sc.append("- Hard-gate failures: %s" % ("**" + ", ".join(hf) + "**" if hf else "none"))
        if r["tier2_must_pass_failures"]:
            sc.append("- Tier-2 must-pass failures (median < 4): **%s**"
                      % ", ".join(r["tier2_must_pass_failures"]))
        med = [j["median_scores"] for j in (r.get("judge") or []) if j.get("median_scores")]
        if med:
            dims = sorted({d for m in med for d in m})
            avg = {d: round(statistics.mean([m[d] for m in med if d in m]), 1) for d in dims}
            sc.append("- Judge medians: %s" % avg)
        if r.get("judge_failed_samples"):
            sc.append("- Judge samples failed (malformed after retry): %d" % r["judge_failed_samples"])
        p = r.get("pairwise")
        if p:
            sc.append("- Blind win rate vs no-skill: **%s** (%dW/%dT/%dL, %d invalid, %d failed, "
                      "over %d pair(s))" % (p["win_rate"], p["wins"], p["ties"], p["losses"],
                                            p["invalid"], p["failed"], p["n_pairs"]))
        if r.get("non_discriminating_checks"):
            sc.append("- Non-discriminating checks (passed in both configs): %s"
                      % ", ".join(r["non_discriminating_checks"]))
        sc.append("")
    crits = [(r["eval_id"], c) for r in runs_out for c in (r.get("judge_critiques") or [])]
    if crits:
        sc.append("## Judge critiques of the test")
        seen = set()
        for cid, c in crits:
            if (cid, c) in seen:
                continue
            seen.add((cid, c))
            sc.append("- Case %s: %s" % (cid, c))
        sc.append("")

    benchmark = {"metadata": {"skill_name": data.get("skill_name", "voicestead"),
                              "timestamp": ts,
                              "runs_per_configuration": args.runs,
                              "judge_runs_per_output": args.judge_runs,
                              "pair_judgments_per_pair": args.pair_judgments,
                              "mock": os.environ.get("VOICESTEAD_MOCK", "") not in ("", "0"),
                              "evals_run": [c["id"] for c in cases]},
                 "runs": runs_out, "overall": overall}
    _write_json(os.path.join(args.out, "benchmark.json"), benchmark)
    with open(os.path.join(args.out, "scorecard.md"), "w") as f:
        f.write("\n".join(sc))
    print("wrote %s/benchmark.json and scorecard.md" % args.out)
    print(json.dumps(overall, indent=2))

    # release gate
    failures = []
    if hard_cases:
        failures.append("%d case(s) with hard-gate failures" % hard_cases)
    if t2_cases:
        failures.append("%d case(s) failing a must_pass rubric dimension (median < 4)" % t2_cases)
    if err_cases:
        failures.append("%d case(s) errored" % err_cases)
    if args.gate:
        if win["rate"] is None:
            failures.append("--gate set but no valid pairwise judgments to gate on")
        elif win["rate"] < args.min_win_rate:
            failures.append("win rate %s below the %s bar (--gate)" % (win["rate"], args.min_win_rate))
    print("release gate: " + ("FAIL - " + "; ".join(failures) if failures else "PASS"))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
