#!/usr/bin/env python3
"""Run Tier-1 deterministic checks. No API key, no network.

Three modes:
  # single output
  python tests/checks/run_checks.py --output out.txt --prompt prompt.txt \
         --checks no_invented_numbers,burstiness_ok,triads_ok

  # regression corpus: every *.json manifest in tests/corpus/ pairs an output file
  # with the checks it must pass. Exits non-zero if any HARD check or expected soft
  # result fails — this is what CI runs on every push.
  python tests/checks/run_checks.py --corpus tests/corpus

  # per-section drift scan: split the output on markdown H2 ('## ') boundaries
  # (fence-aware) and run the same checks against each section, tagging every
  # result line with the section index and heading.
  python tests/checks/run_checks.py --output out.md --per-section --checks tell_flags

Exit codes: --output mode exits 1 on any hard failure (soft flags never gate) and 2 on
an unknown check id. --per-section keeps both rules and adds the drift signature: a
check that passes on the whole document but fails inside at least one section also
exits 1 — early clean sections must not dilute late slop. A document with no H2
headings is graded as one section, identical to a plain --output run.
"""
import argparse, glob, json, os, sys
import text_metrics as tm


def _grade(output, checks, prompt="", source=""):
    results = tm.run(output, checks, prompt=prompt, source=source)
    hard_fail = [r for r in results if r["severity"] == "hard" and not r["passed"]]
    soft_fail = [r for r in results if r["severity"] == "soft" and not r["passed"]]
    return results, hard_fail, soft_fail


def _print(results):
    for r in results:
        icon = "PASS" if r["passed"] else ("FAIL" if r["severity"] == "hard" else "warn")
        metric = f" [{r['metric']}]" if r.get("metric") is not None else ""
        print(f"  [{icon}] {r['id']}{metric}: {r['detail']}")


def _print_section(results, idx, n, heading):
    tag = f' "{heading}"' if heading else ""
    for r in results:
        icon = "PASS" if r["passed"] else ("FAIL" if r["severity"] == "hard" else "warn")
        metric = f" [{r['metric']}]" if r.get("metric") is not None else ""
        print(f"  [{icon}] {r['id']} [section {idx}/{n}{tag}]{metric}: {r['detail']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output"); ap.add_argument("--prompt", default="")
    ap.add_argument("--source", default="")
    ap.add_argument("--checks", default="no_invented_numbers,no_high_conf_tells,tell_flags,formula_structures,burstiness_ok,triads_ok,no_throatclear_open,zombie_nouns,false_agency")
    ap.add_argument("--corpus")
    ap.add_argument("--per-section", action="store_true",
                    help="split --output on markdown H2 boundaries and run the checks "
                         "per section (drift scan; see module docstring for exit codes)")
    args = ap.parse_args()
    if args.per_section and args.corpus:
        ap.error("--per-section applies to --output mode, not --corpus")

    if args.corpus:
        manifests = sorted(glob.glob(os.path.join(args.corpus, "*.json")))
        if not manifests:
            print(f"no manifests in {args.corpus}"); sys.exit(1)
        total_hard = 0; total_expect_miss = 0; bad_manifests = 0
        for mpath in manifests:
            man = json.load(open(mpath))
            base = os.path.dirname(mpath)
            output = open(os.path.join(base, man["output_file"])).read()
            prompt = man.get("prompt", "")
            source = man.get("source", "")
            try:
                results, hard_fail, soft_fail = _grade(output, man["checks"], prompt, source)
            except ValueError as e:
                # an unknown check id in a manifest is a broken gate, not a green one
                print(f"\n=== {man.get('name', os.path.basename(mpath))} [FAIL] ===")
                print(f"  !! FAILURE: {e}")
                bad_manifests += 1
                continue
            # A fixture is a regression test of the CHECKS. Success = every declared
            # expectation matches, and no HARD check fails unless the fixture expects it to
            # (intentionally-bad fixtures declare expect:{check:false}).
            expect = man.get("expect", {})  # {check_id: bool}
            miss = [cid for cid, want in expect.items()
                    if next((r["passed"] for r in results if r["id"] == cid), None) != want]
            unexpected_hard = [r["id"] for r in hard_fail if expect.get(r["id"], True) is not False]
            status = "OK" if not unexpected_hard and not miss else "FAIL"
            print(f"\n=== {man.get('name', os.path.basename(mpath))} [{status}] ===")
            _print(results)
            if miss:
                print(f"  !! expectation mismatch on: {miss}")
            total_hard += len(unexpected_hard); total_expect_miss += len(miss)
        print(f"\n---\nunexpected HARD failures: {total_hard} | expectation mismatches: {total_expect_miss}"
              f" | broken manifests: {bad_manifests}")
        sys.exit(0 if (total_hard == 0 and total_expect_miss == 0 and bad_manifests == 0) else 1)

    if not args.output:
        ap.error("provide --output or --corpus")
    output = open(args.output).read()
    prompt = open(args.prompt).read() if args.prompt and os.path.exists(args.prompt) else args.prompt
    source = open(args.source).read() if args.source and os.path.exists(args.source) else args.source
    checks = [c.strip() for c in args.checks.split(",") if c.strip()]
    if args.per_section:
        try:
            whole_results, _, _ = _grade(output, checks, prompt, source)
        except ValueError as e:
            print(f"FAILURE: {e}")
            sys.exit(2)
        whole_pass = {r["id"]: r["passed"] for r in whole_results}
        sections = tm.split_sections(output)
        n = len(sections)
        total_hard = total_soft = 0
        drift = []
        for idx, (heading, body) in enumerate(sections, 1):
            text = f"{heading}\n{body}" if heading else body
            results, hard_fail, soft_fail = _grade(text, checks, prompt, source)
            _print_section(results, idx, n, heading)
            total_hard += len(hard_fail)
            total_soft += len(soft_fail)
            for r in results:
                # the drift signature: clean overall, dirty in one section
                if not r["passed"] and whole_pass.get(r["id"], False):
                    drift.append({"check": r["id"], "section": idx, "heading": heading})
        print(json.dumps({"sections": n, "hard_failures": total_hard,
                          "soft_flags": total_soft, "drift": drift}))
        sys.exit(0 if (total_hard == 0 and not drift) else 1)
    try:
        results, hard_fail, soft_fail = _grade(output, checks, prompt, source)
    except ValueError as e:
        print(f"FAILURE: {e}")
        sys.exit(2)
    _print(results)
    print(json.dumps({"hard_failures": len(hard_fail), "soft_flags": len(soft_fail)}))
    sys.exit(0 if not hard_fail else 1)


if __name__ == "__main__":
    main()
