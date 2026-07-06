# Testing Voicestead — The Eval Guide

A skill you haven't tested is theory. This guide is the part most writing skills skip. Run it before trusting the skill, and re-run occasionally — skills drift as models change.

## The core method: with/without, judged blind

1. Pick 3–5 **real** pieces of your writing work — an email you need to send, a status update, a post draft, a raw brain-dump. Real stakes, real voice. Invented test prompts test nothing.
2. For each, run two fresh sessions: one **with** the skill installed, one **without** (same prompt, same raw material).
3. Compare blind if you can — paste both outputs to someone who knows your voice (or to yourself the next day, labels hidden) and ask: which would you actually send?
4. Score each pair on the rubric below. The skill earns trust when the with-skill version wins consistently — not always, consistently.

## The rubric (score each output 1–5)

- **Voice:** does it sound like the writer, or like a model? (The killer criterion. A brilliant draft in the wrong voice fails.)
- **Point:** is the ask/news/claim in the first sentence, and is "why it matters" clear to this reader?
- **Truth:** zero invented specifics; every detail the writer supplied survived.
- **Rhythm:** read 6 consecutive sentences — do lengths vary? Count triads — more than one per ~200 words?
- **Tells:** sweep against references/tells.md categories. Any reflexive fancy words, zombie nouns, formula structures, false agency?
- **Restraint:** did it edit what needed editing and leave alone what didn't?

## Using test-cases.md

`test-cases.md` holds 25 ready-made cases spanning modes, formats, and guardrails, each with a prompt and pass-criteria. Use them for a quick smoke test after any edit to the skill — they catch regressions ("did my change break Review mode?"). They complement, never replace, the real-writing eval above.

## Iterating

When a case fails, fix the skill file that owns that behavior (core SKILL.md for models/modes/self-check; the relevant reference for tells/persuasion/formats/voice), then re-run just the failed cases. Change one thing at a time. Log what you changed and why at the bottom of this file — the skill's history is part of the skill.

## Change log

- v9 (2026-07): Renamed to Voicestead. Influence system added — inspiration.md (influence interview, study-an-influence pipeline, influences.md storage standard), cases 15–16.
- v8 (2026-07): Research integration — science.md evidence base; narrative move, values reframing, emotion dial (persuasion.md); misread-tone law + hostile reading test, receptiveness recipe, warmth-vs-firmness (influence.md); hedging rule refined after a failed-replication finding; case 14. v7: Added Extract mode + capture.md (Diátaxis, interview-first docs), coaching.md (Coaching Habit/GROW), Economy section (honest token findings), cases 11–13. v6: Added influence.md (Sinek, Carnegie, Voss, Goleman) plus test cases 9–10. v5: full repository structure — modes, curse-of-knowledge, persuasion, voice capture, formats, evals. Still untested against real writing; that step is yours.

## Automated harness

The full three-tier harness lives at the repo root under `tests/` (not shipped inside the skill). See `tests/TESTING.md`. Quick commands:

- Tier 1 (free, no key): `python3 tests/checks/run_checks.py --corpus tests/corpus`
- Full eval (needs `ANTHROPIC_API_KEY`): `python3 tests/run_eval.py --cases tests/cases.json --runs 3 --out tests/results`
- CI runs Tier 1 on every push; the model-graded eval runs on manual dispatch / weekly.
