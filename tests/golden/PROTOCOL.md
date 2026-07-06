# S0 Protocol — the with/without gate

The one number that earns the skill its place: on the same real prompts, does Claude-**with**-Voicestead beat Claude-**without**, judged blind? Run this before trusting the skill and before every release.

## Path A — automated (needs `ANTHROPIC_API_KEY`)

```bash
pip install -r tests/requirements.txt
export ANTHROPIC_API_KEY=sk-...
# generate with/without pairs for the golden prompts, grade Tiers 1–2, emit scorecard
python tests/run_eval.py --cases tests/golden/cases.golden.json --runs 3 --out tests/golden/results
```

Then do the human pass: open each with/without pair (labels hidden), mark `ship`/`don't ship` and `me`/`not me`. Those labels are the ground truth; the judge only approximates them.

## Path B — manual two-session (no key)

For each piece in `raw/`:

1. **Without.** Fresh session, no skill installed. Paste the raw prompt. Save the output as `results/NN-without.txt`.
2. **With.** Fresh session, skill installed. Same prompt, same raw material. Save as `results/NN-with.txt`.
3. **Blind pair.** Strip the labels (or have someone who knows your voice do it). Ask the one question: *which would you actually send?*
4. **Score both** on the rubric below and record which won.

Assemble the results into `results/scorecard.md` (copy `results/scorecard.template.md`).

## The rubric (score each output 1–5)

- **Voice** — sounds like the writer, not a model. The killer criterion; a brilliant draft in the wrong voice fails.
- **Point** — the ask/news/claim in the first sentence; "why it matters" clear to *this* reader.
- **Truth** — zero invented specifics; every detail the writer supplied survived.
- **Rhythm** — read 6 consecutive sentences: do lengths vary? Triads more than one per ~200 words?
- **Tells** — sweep `references/tells.md` categories: reflexive fancy words, zombie nouns, formula structures, false agency.
- **Restraint** — edited what needed editing, left alone what didn't.

## The gate (what S0 must clear before anything ships)

- Blind win rate you'd publish — target **≥ 70%**, consistently (not always, consistently).
- **Zero** hard-gate failures (invented numbers, high-confidence tells).
- A recorded `ship / don't ship` **and** `me / not me` verdict per piece.

Failing three-worst analysis: list every hard-gate failure and rubric miss, propose the minimal skill edits to fix the worst three, and report before editing. The eval is the compass; installs are the echo.
