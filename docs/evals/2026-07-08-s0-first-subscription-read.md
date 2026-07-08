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

First real measurement, run on a Claude Code subscription via the claude-cli backend (not the API). Directional read at --runs 1 (23 valid blind judgments); the official scorecard will want --runs 3 or the pinned --backend api. Hard-gate note: 3 of the 4 no_invented_numbers flags were on the WITHOUT-skill baseline (the model fabricates figures more often without Voicestead); the single with-skill flag was case 16, where the model recalled 1940 for Churchill's wartime speeches — accurate world knowledge, flagged by design because it is not in the input. The slightly negative pass-rate delta is driven by soft checks (length/burstiness), not fabrication. Cost figure below is the claude CLI's notional API-equivalent, covered by the subscription, not dollars billed.
