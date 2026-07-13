#!/usr/bin/env python3
"""Tier-2 behavioral checks for connected mode. Runs the skill with a simulated
get_writer_context payload and asserts the output obeys the truth-in-context and
no-narration invariants. Needs a real backend (claude-cli default) — this is NOT
a free per-push check; run it on demand like the other evals.

  python3 tests/studio_eval/run_studio_evals.py
  VOICESTEAD_BACKEND=api python3 tests/studio_eval/run_studio_evals.py

The pass/fail logic lives in check_case() below, which is pure and imported by
tests/studio_eval/test_runner_logic.py to verify it deterministically (no model
call) — that test is the free-CI-safe part of this task; this script itself is not
a pytest test and is not collected by the suite.
"""
import json, os, sys
TESTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS)
import run_skill

CASES = json.load(open(os.path.join(os.path.dirname(__file__), "injection_cases.json")))


def check_case(output, case):
    """Return a list of failure strings for one case (empty = clean)."""
    failures = []
    low = output.lower()
    for bad in case.get("must_not_contain", []):
        if bad.lower() in low:
            failures.append(f"{case['id']}: leaked forbidden text {bad!r}")
    anyreq = case.get("must_contain_any", [])
    if anyreq and not any(x.lower() in low for x in anyreq):
        failures.append(f"{case['id']}: missing all of {anyreq}")
    return failures


def main():
    failures = []
    for c in CASES:
        out = run_skill.run(c["prompt"], with_skill=True,
                            load=["references/studio.md"], studio_context=c["studio_context"])
        failures.extend(check_case(out, c))
    for f in failures:
        print("FAIL:", f)
    print(f"\n{len(CASES) - len(set(f.split(':')[0] for f in failures))}/{len(CASES)} cases clean")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
