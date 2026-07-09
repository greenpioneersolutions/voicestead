# Eval run — 2026-07-08 — s0-first-subscription-read

- **Date:** 2026-07-08
- **Backend:** claude-cli
- **Generator model:** claude-sonnet-5
- **Judge model:** claude-opus-4-8
- **Cases:** 32
- **Runs per configuration:** 1
- **Blind win rate:** 0.783 (18W/0T/5L of 23 valid)
- **Cases with hard-gate failures:** 3
- **Judge samples failed:** 0
- **Tokens:** 264110 in / 164665 out (110 calls)
- **Cost (USD):** 10.166824
- **Git commit:** 1705453
- **Command:** `tests/run_eval.py --cases tests/cases.json --runs 1 --out tests/results/s0-full --backend claude-cli`

> **Overall blind win rate vs no-skill: 0.783 (18W/0T/5L of 23 valid; 0 invalid, 0 failed)** | hard-gate failures: 3/32 | tier-2 must-pass failures: 0 | errored cases: 0

## Notes

First real measurement, run on a Claude Code subscription via the claude-cli backend (not the API). Directional read at `--runs 1` (23 valid blind judgments per pair); a robust official number wants `--runs 3` or the pinned `--backend api`.

**Hard-gate breakdown.** The skill's own drafts hit a hard gate in 3 of 32 cases, all in the rewrite/extract modes:

- **Case 6 (Improve)** — asked to edit a 16-word standup note, the draft came back 29 words, past the 10% length bound (`length_delta_max`). Improve over-expands short inputs.
- **Case 16 (Extract)** — the draft recalled "1940" for Churchill's wartime speeches: accurate, but not in the input, so `no_invented_numbers` flagged it by design (the gate licenses from the input, never from model memory).
- **Case 24 (Improve)** — a "make this sound human" rewrite left false-agency and zombie-noun constructions that the case marks `must_pass`; the de-slop didn't fully land.

Separately, the **without-skill baseline** invented numbers it was never given in cases 2, 11, and 27 — evidence the skill *reduces* fabrication, tracked apart from the skill's own count above.

These are single-generation results; `--runs 3` averages out temperature variance (case 1 tripped the number gate in a smoke run but passed clean here). The cost figure above is the claude CLI's notional API-equivalent, covered by the subscription, not dollars billed.
