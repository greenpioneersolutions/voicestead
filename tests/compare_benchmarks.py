#!/usr/bin/env python3
"""Diff two benchmark.json runs and fail on regression. No key, no network.

Compares a PREVIOUS run against the CURRENT one and exits non-zero when either:
  * the pooled blind win rate drops by more than --max-win-drop (default 0.10, i.e.
    10 points), or
  * a hard gate that was PASSING for a case in the previous run now fails (any
    per-case check id newly appearing in that case's hard_fails).

Everything else — win-rate gains, resolved failures, per-case movement — is printed
as a readable delta table but never fails the run.

  python tests/compare_benchmarks.py --previous prev/benchmark.json --current tests/results/benchmark.json

How the weekly job adopts this (once two runs exist)
----------------------------------------------------
The scheduled eval writes tests/results/benchmark.json each week. On its own that
file can only fail on the (already-enforced) hard gates of a single run — it cannot
see drift. To close that gap, keep the previous week's file around and diff:

  1. Before the run, restore last week's benchmark.json (from the committed
     tests/results/history/ dir, or `gh run download` of the prior 'scorecard'
     artifact) to prev/benchmark.json.
  2. Run the eval:  python tests/run_eval.py --cases tests/cases.json --gate --out tests/results
  3. Diff as the final step:
       python tests/compare_benchmarks.py --previous prev/benchmark.json \
              --current tests/results/benchmark.json
     A non-zero exit turns the scheduled workflow red so GitHub emails the owner —
     that red run is the drift alarm the single-run gate can't raise.
  4. Archive this week's benchmark.json as next week's previous.

The FIRST scheduled run has no previous file, so skip the diff until two runs exist.
"""
import argparse
import json
import sys


def _load(path):
    with open(path) as f:
        return json.load(f)


def _overall_win(bench):
    """Pooled win rate as a float in 0..1, or None if the run recorded none.
    Tolerant of a couple of shapes so an older/newer benchmark still parses."""
    overall = bench.get("overall", {}) or {}
    wr = overall.get("win_rate")
    if isinstance(wr, dict):
        for k in ("rate", "point", "mean"):
            if wr.get(k) is not None:
                return float(wr[k])
        return None
    if isinstance(wr, (int, float)):
        return float(wr)
    return None


def _case_records(bench):
    """eval_id -> {'hard': set(hard-failing check ids), 'win': float|None}."""
    out = {}
    for r in bench.get("runs", []) or []:
        cid = r.get("eval_id", r.get("id"))
        if cid is None:
            continue
        hard = set(r.get("hard_fails") or r.get("hard_fail") or [])
        p = r.get("pairwise") or {}
        win = p.get("win_rate", p.get("rate")) if isinstance(p, dict) else None
        out[cid] = {"hard": hard, "win": win}
    return out


def _fmt_win(w):
    return "n/a" if w is None else "%.0f%%" % (w * 100)


def _fmt_delta_pts(prev, cur):
    if prev is None or cur is None:
        return "  -"
    return "%+.0f" % ((cur - prev) * 100)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--previous", required=True, help="prior run's benchmark.json")
    ap.add_argument("--current", required=True, help="this run's benchmark.json")
    ap.add_argument("--max-win-drop", type=float, default=0.10,
                    help="fail if win rate falls by more than this fraction (default 0.10 = 10 points)")
    args = ap.parse_args(argv)

    prev, cur = _load(args.previous), _load(args.current)
    prev_cases, cur_cases = _case_records(prev), _case_records(cur)
    prev_win, cur_win = _overall_win(prev), _overall_win(cur)

    # --- per-case delta table ---
    rows = []
    regressed_gates = []  # (case_id, gate) that passed before and fails now
    for cid in sorted(set(prev_cases) | set(cur_cases)):
        pc = prev_cases.get(cid)
        cc = cur_cases.get(cid)
        p_win = pc["win"] if pc else None
        c_win = cc["win"] if cc else None
        p_hard = pc["hard"] if pc else set()
        c_hard = cc["hard"] if cc else set()
        new_fail = sorted(c_hard - p_hard) if pc else []   # only a regression if the case existed before
        fixed = sorted(p_hard - c_hard)
        for g in new_fail:
            regressed_gates.append((cid, g))
        note_bits = ["+%s" % g for g in new_fail] + ["-%s" % g for g in fixed]
        if cid not in prev_cases:
            note_bits.append("(new case)")
        elif cid not in cur_cases:
            note_bits.append("(dropped)")
        rows.append((str(cid), _fmt_win(p_win), _fmt_win(c_win),
                     _fmt_delta_pts(p_win, c_win), ", ".join(note_bits) or "-"))

    headers = ("case", "prev win", "cur win", "Δpts", "hard-gate change")
    widths = [max(len(h), *(len(r[i]) for r in rows)) if rows else len(h)
              for i, h in enumerate(headers)]
    line = lambda cells: "  ".join(c.ljust(widths[i]) for i, c in enumerate(cells))
    print("Benchmark delta  (previous -> current)")
    print("  previous: %s" % args.previous)
    print("  current:  %s" % args.current)
    print()
    print(line(headers))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print(line(r))
    print()
    print("Overall blind win rate: %s -> %s  (%s pts)"
          % (_fmt_win(prev_win), _fmt_win(cur_win), _fmt_delta_pts(prev_win, cur_win).strip()))

    # --- gates ---
    failures = []
    if prev_win is None:
        print("note: previous run has no pooled win rate; win-rate drop check skipped.")
    elif cur_win is None:
        failures.append("current run has no pooled win rate to compare against the previous %.0f%%"
                        % (prev_win * 100))
    elif (prev_win - cur_win) > args.max_win_drop + 1e-9:
        failures.append("win rate dropped %.0f points (%.0f%% -> %.0f%%), over the %.0f-point limit"
                        % ((prev_win - cur_win) * 100, prev_win * 100, cur_win * 100,
                           args.max_win_drop * 100))

    if regressed_gates:
        detail = ", ".join("case %s: %s" % (c, g) for c, g in regressed_gates)
        failures.append("%d previously-passing hard gate(s) now fail: %s"
                        % (len(regressed_gates), detail))

    print()
    if failures:
        print("REGRESSION - benchmark comparison FAILED:")
        for f in failures:
            print("  - " + f)
        sys.exit(1)
    print("OK - no win-rate regression beyond %.0f points and no newly-failing hard gate."
          % (args.max_win_drop * 100))
    sys.exit(0)


if __name__ == "__main__":
    main()
