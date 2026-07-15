#!/usr/bin/env python3
"""Live behavioral matrix for connected mode (S1-S4). Drives the skill through the
run_skill connection seam and grades with countable substring assertions. Needs a real
backend (claude-cli default) — NOT a free per-push check; run on demand:

  python3 tests/studio_eval/run_connected_evals.py
  VOICESTEAD_BACKEND=api python3 tests/studio_eval/run_connected_evals.py

check_case() is pure and unit-tested model-free by test_runner_logic.py."""
import json, os, sys
TESTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS)
import run_skill

CASES = json.load(open(os.path.join(os.path.dirname(__file__), "connected_cases.json")))

def check_case(output, case):
    low, fails = output.lower(), []
    for bad in case.get("must_not_contain", []):
        if bad.lower() in low: fails.append(f"{case['id']}: leaked {bad!r}")
    anyreq = case.get("must_contain_any", [])
    if anyreq:
        # Support both flat list and list-of-lists (independent requirements)
        if anyreq and isinstance(anyreq[0], list):
            for inner_list in anyreq:
                if inner_list and not any(x.lower() in low for x in inner_list):
                    fails.append(f"{case['id']}: missing all of {inner_list}")
        else:
            if not any(x.lower() in low for x in anyreq):
                fails.append(f"{case['id']}: missing all of {anyreq}")
    for req in case.get("must_contain_all", []):
        if req.lower() not in low: fails.append(f"{case['id']}: missing {req!r}")
    for sub, n in case.get("count", {}).items():
        if low.count(sub.lower()) != n: fails.append(f"{case['id']}: {sub!r} x{low.count(sub.lower())} != {n}")
    for sub, n in case.get("count_max", {}).items():
        if low.count(sub.lower()) > n: fails.append(f"{case['id']}: {sub!r} x{low.count(sub.lower())} > {n}")
    return fails

def main():
    fails = []
    for c in CASES:
        out = run_skill.run(c["prompt"], with_skill=True, load=c.get("load", []),
                            connection=c.get("connection"))
        fails.extend(check_case(out, c))
    for f in fails: print("FAIL:", f)
    print(f"\n{len(CASES) - len(set(f.split(':')[0] for f in fails))}/{len(CASES)} cases clean")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
