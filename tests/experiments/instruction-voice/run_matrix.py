#!/usr/bin/env python3
"""Instruction-voice experiment runner. See PROTOCOL.md.

  python run_matrix.py --dry-run            # print the full prompt matrix, no API
  python run_matrix.py --smoke --runs 2     # 6 variants x 2 tasks
  python run_matrix.py --runs 3             # full 16 x 4
Optional: --no-skill-arm  (adds a B0-without-skill arm for H4, aggregated as "B0-noskill")
Requires ANTHROPIC_API_KEY unless --dry-run; VOICESTEAD_MOCK=1 runs the whole matrix keylessly.
Rows are flushed to <out>/rows.partial.jsonl as they complete, so a crash loses nothing.
"""
import argparse, json, os, random, re, statistics, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(TESTS, "checks"))
sys.path.insert(0, os.path.join(TESTS, "judge"))
sys.path.insert(0, TESTS)
import text_metrics as tm

INSULTS = ["screw", "garbage", "idiot", "stupid", "dumb", "crap", "useless", "or else"]
SMOKE_VARIANTS = ["B0", "T2", "V2", "M1", "M2", "S1"]
SMOKE_TASKS = ["slip-email", "sre-pitch"]


def corrupt(text, targets):
    for good, bad in targets.items():
        text = text.replace(good, bad)
    return text


def task_block(t, kind="full"):
    facts, cons = t["facts"], t["constraints"]
    if kind == "facts":
        return facts
    if kind == "constraints":
        return "\n".join(f"- {c}" for c in cons)
    return facts + "\n\nConstraints:\n" + "\n".join(f"- {c}" for c in cons)


def build_prompt(variant, t):
    tpl = variant["template"]
    if "{task_corrupted}" in tpl:
        return tpl.replace("{task_corrupted}", corrupt(task_block(t), t["typo_targets"]))
    if "{task_facts_only}" in tpl and "{task_constraints_only}" in tpl:
        return tpl.replace("{task_facts_only}", task_block(t, "facts")).replace("{task_constraints_only}", task_block(t, "constraints"))
    if "{task_facts_only}" in tpl:
        return tpl.replace("{task_facts_only}", task_block(t, "facts"))
    return tpl.replace("{task}", task_block(t))


def det_metrics(output, t, variant_id):
    checks = ["no_high_conf_tells", "tell_flags", "burstiness_ok", "triads_ok",
              {"id": "max_words", "params": {"limit": t["max_words"]}}]
    if t.get("has_subject"):
        checks.append("has_subject")
    # truth vs the CLEAN task facts (so M2 propagation shows up as invented numbers/names)
    res = tm.run(output, checks + ["no_invented_numbers"], prompt=task_block(t))
    out = {r["id"]: r for r in res}
    low = output.lower()
    words = re.findall(r"[A-Za-z']+", output)
    return {
        "adherence_must_include": all(m.lower() in low for m in t["must_include"]),
        "checks": {k: v["passed"] for k, v in out.items()},
        "burstiness_cv": out.get("burstiness_ok", {}).get("metric"),
        "contamination_proxies": {
            "exclaim_per_100w": round(output.count("!") / max(len(words), 1) * 100, 2),
            "insult_hits": sum(low.count(w) for w in INSULTS),
            "longword_rate": round(sum(1 for w in words if len(w) >= 9) / max(len(words), 1), 3),
        },
        "corruption_propagated": any(bad.lower() in low for bad in t["typo_targets"].values()) if variant_id == "M2" else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-skill-arm", action="store_true")
    ap.add_argument("--judge-runs", type=int, default=2)
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    args = ap.parse_args()

    variants = json.load(open(os.path.join(HERE, "variants.json")))["variants"]
    tasks = json.load(open(os.path.join(HERE, "tasks.json")))["tasks"]
    if args.smoke:
        variants = [v for v in variants if v["id"] in SMOKE_VARIANTS]
        tasks = [t for t in tasks if t["id"] in SMOKE_TASKS]

    matrix = [(v, t) for v in variants for t in tasks]
    if args.dry_run:
        for v, t in matrix:
            print(f"\n===== {v['id']} x {t['id']} =====\n{build_prompt(v, t)}")
        print(f"\n--- {len(matrix)} cells x {args.runs} runs = {len(matrix)*args.runs} generations ---")
        return

    import run_skill, judge  # API needed (or VOICESTEAD_MOCK=1)
    os.makedirs(args.out, exist_ok=True)
    rubric = os.path.join(HERE, "rubric-voice.md")
    rows_path = os.path.join(args.out, "rows.partial.jsonl")
    open(rows_path, "w").close()  # incremental flush: a crash keeps every completed row
    rows = []
    for v, t in matrix:
        prompt = build_prompt(v, t)
        clean_task = task_block(t) + f"\n\nIntended reader register: {t['intended_register']}"
        for arm in (["with", "without"] if (args.no_skill_arm and v["id"] == "B0") else ["with"]):
            for i in range(args.runs):
                out = run_skill.run(prompt, with_skill=(arm == "with"))
                det = det_metrics(out, t, v["id"])
                j = judge.score_absolute(out, clean_task, runs=args.judge_runs, rubric_path=rubric)
                jm = j.get("median_scores") or {}  # a fully-failed judge run is recorded, not fatal
                row = {"variant": v["id"], "task": t["id"], "arm": arm, "run": i,
                       "det": det, "judge_median": jm, "judge_failed": j.get("failed", 0),
                       "output": out}
                rows.append(row)
                with open(rows_path, "a") as f:
                    f.write(json.dumps(row) + "\n")
                print(f"{v['id']} x {t['id']} [{arm}] run {i}: quality={jm.get('task_quality')}")

    # aggregate: per-variant means + delta vs B0
    def agg(rs, key_fn):
        vals = [key_fn(r) for r in rs if key_fn(r) is not None]
        return round(statistics.mean(vals), 2) if vals else None

    def summarize(rs):
        return {
            d: agg(rs, lambda r, d=d: r["judge_median"].get(d)) for d in
            ["task_quality", "instruction_adherence", "tone_fidelity", "register_contamination", "human_rhythm"]
        } | {"must_include_rate": agg(rs, lambda r: 1.0 if r["det"]["adherence_must_include"] else 0.0),
             "burstiness": agg(rs, lambda r: r["det"]["burstiness_cv"]),
             "insult_hits": agg(rs, lambda r: r["det"]["contamination_proxies"]["insult_hits"]),
             "longword_rate": agg(rs, lambda r: r["det"]["contamination_proxies"]["longword_rate"]),
             "corruption_propagated": agg(rs, lambda r: (1.0 if r["det"]["corruption_propagated"] else 0.0) if r["det"]["corruption_propagated"] is not None else None)}

    summary = {}
    for v in variants:
        summary[v["id"]] = summarize([r for r in rows if r["variant"] == v["id"] and r["arm"] == "with"])
    # H4: the paid-for no-skill arm gets its own summary row instead of vanishing
    without_rows = [r for r in rows if r["arm"] == "without"]
    if without_rows:
        summary["B0-noskill"] = summarize(without_rows)
    base = summary.get("B0", {})
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    report = ["# Instruction-voice results", f"_generated {ts}_", "",
              "| variant | quality | adherence | tone_fid | contam | must_incl | Δquality vs B0 |", "|---|---|---|---|---|---|---|"]
    for vid, s in summary.items():
        dq = (round(s["task_quality"] - base["task_quality"], 2)
              if s.get("task_quality") is not None and base.get("task_quality") is not None and vid != "B0" else "")
        report.append(f"| {vid} | {s.get('task_quality')} | {s.get('instruction_adherence')} | {s.get('tone_fidelity')} | {s.get('register_contamination')} | {s.get('must_include_rate')} | {dq} |")
    if "B0-noskill" in summary:
        ns = summary["B0-noskill"]
        report += ["",
                   "**H4 - B0 with skill vs without** (contamination scored 5 = cleanest): "
                   f"register_contamination {base.get('register_contamination')} vs {ns.get('register_contamination')}; "
                   f"insult_hits {base.get('insult_hits')} vs {ns.get('insult_hits')}; "
                   f"quality {base.get('task_quality')} vs {ns.get('task_quality')}; "
                   f"burstiness {base.get('burstiness')} vs {ns.get('burstiness')}."]
    json.dump({"rows": rows, "summary": summary}, open(os.path.join(args.out, "matrix.json"), "w"), indent=2)
    open(os.path.join(args.out, "report.md"), "w").write("\n".join(report))
    print(f"\nwrote {args.out}/matrix.json and report.md")


if __name__ == "__main__":
    main()
