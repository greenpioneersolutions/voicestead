# The Golden Set — regression anchor + judge calibration

Real pieces of the writer's own work, with the verdicts they earned in S0. Two jobs (see [`../TESTING.md`](../TESTING.md), Tier 3):

1. **Regression anchor.** Re-run after any skill change; a version that starts failing a previously-shipping case has regressed.
2. **Judge calibration.** A few labeled examples become few-shot anchors so the judge's scores track *this writer's* taste, not a generic one.

## Layout

- `raw/` — the source pieces. 3–5 real writing tasks (an email you need to send, a status update, a post draft, a brain-dump). Real stakes, real voice — invented prompts prove nothing. Name them `01-<slug>.txt` … `05-<slug>.txt`. These are *inputs*; the eval generates the with-skill and without-skill versions from them.
- `expected/` — the frozen verdicts from S0: for each piece, the with-skill output that shipped, the human labels (`ship`/`don't ship`, `me`/`not me`), and the rubric scores. One `NN-<slug>.md` per piece.
- `results/` — scorecards from runs (git-ignored except the template).

## Making the verdicts (S0)

See [`PROTOCOL.md`](PROTOCOL.md). With an `ANTHROPIC_API_KEY`, `tests/run_eval.py` generates the with/without pairs and grades them through Tiers 1–2; without a key, run the manual two-session protocol and record verdicts by hand. Either way the human makes the final `me / not me` call — no machine gets that one.

## The freeze (S3)

Once S0's verdicts exist, copy them into `expected/` and wire the golden run into CI (deterministic tier every push; golden on dispatch). The gate that proves the anchor works: a *deliberately-degraded* skill edit must fail the golden run.

> **Status:** the 5 real pieces are in `raw/`. Awaiting an `ANTHROPIC_API_KEY` to run the with/without benchmark and record verdicts into `expected/`. This is the S0 gate that everything else waits on.
