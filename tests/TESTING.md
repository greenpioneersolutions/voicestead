# Testing Voicestead

How we know the skill actually improves writing — and how to prove it on every change, automatically.

Voicestead is hard to test for two reasons a normal test suite never faces: its output is **non-deterministic** (same prompt, different text each run) and "good" is **subjective and multi-dimensional** (voice, clarity, persuasion, rhythm, no-slop). You cannot diff prose against one correct answer. So we don't. We use three layers, each catching a different class of failure, at a different cost and reliability.

## The three tiers

| Tier | Method | Catches | Cost | Deterministic? | Runs where |
|---|---|---|---|---|---|
| 1 | Code checks | Structural + mechanical slop (buried point, uniform rhythm, triads, tell-words, invented numbers/quotes/citations/URLs, length) | ~free, instant | Yes | Every push/PR |
| 2 | LLM-as-judge | Subjective quality — voice, clarity, persuasive strength, "sounds human," restraint | API $, minutes | No (average N runs) | On demand / schedule |
| 3 | Human review | The final call — *does it sound like me?* — and calibration of tiers 1–2 | Your time | No | Before trusting a version |

The rule of thumb: **push a rule down a tier whenever you can.** Anything a regex or a counter can verify shouldn't burn an API call or your attention. Anything a judge can score reliably shouldn't wait on you. You are the scarcest, most valuable grader — spend you last.

---

## Tier 1 — Deterministic checks (`tests/checks/`)

These are the backbone of automation: fast, free, repeatable, and perfect for catching regressions ("did my edit reintroduce slop?"). They run in CI with no API key. Each check returns a verdict plus a **severity**:

- **hard** — a gate. Failing means the output is unacceptable regardless of anything else. These map to the skill's non-negotiables.
- **soft** — a signal. It feeds the score and flags the output for the judge/human, but a single soft flag isn't a failure (context can justify it).

What's mechanically verifiable, and how:

- **`no_invented_numbers`** *(hard — the Truth rule)*. Extracts every number, %, and $ figure from the output and checks each appears in the prompt/context. A figure in the output that isn't in the input is a candidate fabrication. Placeholders like `[X]` pass. This is the single most important automated guard — a writing skill that invents statistics is dangerous, and this catches it cheaply.
- **`no_invented_quotes`** *(hard — the Truth rule, for quotations)*. Any quoted span of five or more words in the output must appear — whitespace/case-normalized — in the prompt or source. Shorter spans are scare quotes or quoted terms and stay exempt. Paraphrased fabrication carries no quote marks for a matcher to catch; the judge's truth dimension owns it.
- **`no_invented_citations`** *(hard — the Truth rule, for citations)*. Citation-shaped claims — `Author (Year)`, bracketed refs like `[1]`, DOIs, `according to <Name>`, `a <year> study` — must be licensed by the prompt or source. The shape families are narrow on purpose; shapeless authority ("studies show") is judge territory.
- **`no_invented_urls`** *(hard — the Truth rule, for links)*. Every URL in the output must appear in the prompt or source. String-level only; nothing is ever fetched. A real link the user never supplied still fails: licensing comes from the input, not the model's memory.
- **`no_high_conf_tells`** *(hard)*. Scans for the handful of phrases that are almost never justified: "in today's rapidly evolving," "it's worth noting," "at the end of the day," "that being said," etc. High precision, low false-positive.
- **`tell_flags`** *(soft)*. Scans a curated word-list mirroring the categories in `references/tells.md` (sync enforced by a unit test) — delve, leverage, robust, seamless… Reported as flags with context, **not** an auto-fail — because "robust test coverage" is correct and only a judge/human can tell. The count feeds the score and hands candidates to Tier 2 to adjudicate. (A static list can spot the word; it can't judge the context. Respect that boundary or you'll punish good writing.)
- **`burstiness_ok`** *(soft)*. Computes the coefficient of variation of sentence lengths (stddev ÷ mean words-per-sentence). Human prose typically lands above ~0.5; metronomic AI prose falls below ~0.4. Also flags 3+ consecutive sentences within ±2 words of each other. This is the earlier "rule of three / vary the rhythm" insight, now a number.
- **`triads_ok`** *(soft)*. Counts "A, B, and C" / "A, B, or C" constructions, normalized per 200 words. More than ~1 per 200 words is the pattern readers feel without naming.
- **`no_throatclear_open`** *(soft)*. Checks the first sentence doesn't open with a runway phrase ("I just wanted to," "In this response," "I hope this finds you").
- **`max_words` / `has_subject`** *(structural, per-format)*. Length caps and format requirements from `references/formats.md`.

Whether the *point* leads and whether the *voice* matches are deliberately **not** here — a heuristic can't judge them honestly. They live in Tier 2.

Run them:
```bash
python3 tests/checks/run_checks.py --output path/to/output.txt --prompt path/to/prompt.txt --checks no_invented_numbers,burstiness_ok,triads_ok
```

---

## Tier 2 — LLM-as-judge (`tests/judge/`)

For the subjective dimensions, a second Claude call scores the output against an anchored rubric (`tests/judge/rubric.md`). This is the dominant industry technique for grading open-ended output, and it works — *if* you respect its failure modes.

**Design choices we make, and why:**

- **Anchored 1–5 scales, not "rate this."** Each dimension (voice, clarity, persuasion, human-rhythm, restraint, truth) has a written description of what a 1 and a 5 look like. Vague rubrics produce vague, drifting scores.
- **Structured JSON out** (score + one-line rationale per dimension), so results aggregate and diff. Parsed strictly: a malformed response is retried once, then recorded as a failed run — never a crash, never a silent zero. A pairwise verdict that isn't exactly `A`/`B`/`tie` is retried once, then reported as `invalid` — never counted as a loss.
- **Pairwise > absolute.** LLM judges are far more reliable at "is A or B better?" than at "is this a 4 or a 5?" Our headline metric is a *with-skill vs without-skill* comparison, not an absolute grade. Every generated with/without pair is compared blind; we report the pooled win rate.
- **Self-consistency.** Variance comes from the N generations per configuration; each output is scored once by default, and `--judge-runs 3` adds per-output median-of-3 scoring when you want the extra signal. The spread across runs is itself a signal — a good skill produces *consistently* good output.
- **The judge also critiques the test** (borrowed from Anthropic's grader spec): it flags assertions that a wrong output could also pass, and outcomes no check covers. Critiques are persisted per case as `judge_critiques` in `benchmark.json` and surfaced in their own scorecard section, so a weak assertion gets fixed instead of forgotten.

**Judge biases we actively mitigate:**

- **Position bias** — judges favor whichever output is shown first. A/B order is randomized per judgment, seeded per pair, so runs reproduce.
- **Verbosity bias** — judges favor longer answers. The rubric explicitly rewards concision and the `max_words` check counterweights it.
- **Self-preference** — a model tends to prefer text from its own family. Use a judge from a different model line than the one being tested where possible, and always calibrate against human labels (Tier 3).
- **Goodhart** — *do not optimize the skill to please the judge.* The judge is a proxy for a good reader, not the target. When judge scores and human judgment diverge, the human wins and the rubric gets fixed.

Run it:
```bash
export ANTHROPIC_API_KEY=sk-...
python3 tests/judge/judge.py --output out.txt --prompt prompt.txt --rubric tests/judge/rubric.md   # absolute
python3 tests/judge/judge.py --compare a.txt b.txt --prompt prompt.txt                              # pairwise
```

---

## Tier 3 — Human review (the part no automation replaces)

One question stays yours forever: **does it sound like you?** A judge can approximate "sounds human"; it cannot confirm it sounds like *you*. So the workflow keeps a human-in-the-loop ritual and, crucially, **turns your judgments into data**:

1. Run the suite; it emits `results/scorecard.md` and a side-by-side of with/without outputs.
2. You skim, and for each pair mark *ship / don't ship* and (for voice) *me / not me*.
3. Those labels are appended to `tests/golden/` — a growing set of real prompts with your verdicts.

The golden set does double duty. It's a **regression anchor** (re-run it after any change; a version that starts failing previously-shipping cases regressed). And it **calibrates the judge**: feed a few labeled examples into the judge prompt as few-shot anchors so its scores track *your* taste, not a generic one. This is how you bootstrap a personalized evaluator over time — the more you review, the less you have to.

---

## The headline: the with/without benchmark (`tests/run_eval.py`)

The one number that proves the skill earns its place: **on the same prompts, does Claude-with-Voicestead beat Claude-without?** The orchestrator runs every case N times in both configurations, puts *both* arms through the Tier-1 checks, rubric-scores the with-skill outputs on each case's declared `rubric_dimensions` (showing the judge any loaded voice-profile/influences fixture), compares **every** generated with/without pair blind, and reports (in `benchmark.json`, Anthropic's schema, plus a readable `scorecard.md`):

- **Win rate** — % of blind pairwise comparisons the with-skill output wins, **with ties in the denominator** and reported separately (invalid verdicts and failed judgments are reported too, never counted as losses). Target: consistently ≥ 70%. Passing `--gate` makes the run exit nonzero when the pooled rate misses `--min-win-rate` (default 0.70) — the weekly CI job uses it.
- **Pass-rate delta** — mean Tier-1 pass rate, with vs without, with stddev. A check that passes in *both* configs proves nothing about the skill — those are flagged per case as `non_discriminating_checks`.
- **Variance** — spread across the N runs. Lower is better; it means the skill is reliable, not lucky.

Each case's record is flushed to `<out>/partial/` the moment it completes, and the final benchmark is assembled from those files — a crash late in a paid run loses nothing, and `--resume` skips cases that already have a record.

A skill "passes" a release when hard gates never fail — including `must_pass`: a failing deterministic check named there is promoted to a hard failure, and a rubric dimension named there must hold a median judge score ≥ 4 — win rate clears the bar, and no previously-shipping golden case regressed.

---

## Metamorphic / property tests

A few properties should hold across transformations, even without a fixed expected output:

- **Restraint** — feeding an already-clean text through Improve mode must not lengthen it beyond the declared bound. (Guards the "if it's already good, stop" rule.) *Enforced:* cases with `type: metamorphic` declare a `metamorphic` block, and the orchestrator computes `length_delta_max` (output vs source) or `output_to_input_ratio_max` (output vs prompt) as a hard gate — a violation lands in `hard_fails`.
- **Mode integrity** — Review mode output must not be a rewrite. *Enforced:* the `not_a_rewrite` check, promoted to a hard gate through `must_pass`.
- **Voice pull** — with a voice profile loaded, output should score *closer* to the sample's style than without it. *Partially covered:* the judge now sees the loaded profile when grading voice; the automated with/without style-delta comparison is still planned.
- **Truth preservation** — every specific the prompt supplied must survive to the output (subset check). *Planned:* today this is judged (the `truth` dimension), not deterministically checked. The inverse direction — nothing fabricated — is now deterministically gated for figures, quotations, citations, and URLs.

---

## Running the whole thing

```bash
pip3 install -r tests/requirements.txt
export ANTHROPIC_API_KEY=sk-...            # only needed for tiers 2–3

# fast, free, no key — structural regression check against the committed corpus
python3 tests/checks/run_checks.py --corpus tests/corpus

# the full evaluation: generate, grade, benchmark, scorecard
python3 tests/run_eval.py --cases tests/cases.json --runs 3 --out tests/results

# keyless end-to-end rehearsal of the same pipeline (mock generations + mock judge, no anthropic import)
VOICESTEAD_MOCK=1 python3 tests/run_eval.py --cases tests/cases.json --runs 2 --out /tmp/mockeval
```

## How CI works

See `.github/workflows/`. Split by cost and determinism.

**`eval.yml`**

1. **`check`** — every **push and PR**. Free, no key, seconds. Runs the repo-structure guard (`validate_repo.py`: cases↔evals in sync, manifests valid, frontmatter + description length, load-fixtures present), the Tier-1 deterministic checks against `tests/corpus/`, the **dogfood** gate (`dogfood.py`: the skill's own SKILL.md/README/references must pass the checks the skill enforces on everyone else), the check unit tests (`pytest`), the placeholder sweep, and it builds `voicestead.skill` and uploads it as an artifact. A change that reintroduces slop, breaks structure, or desyncs the evals fails the build.
2. **`evaluate`** — **manual dispatch + weekly cron**. Uses the `ANTHROPIC_API_KEY` secret; runs the full generate→judge→benchmark loop on the full case suite (currently 25 cases) and uploads `scorecard.md`. Gate releases on this, not on every commit.
3. **`golden`** — **manual dispatch**. The S0 gate: the with/without benchmark on the writer's real pieces (`tests/golden/cases.golden.json`), uploaded as `golden-scorecard`. Needs the key.

**`release.yml`** — on a `v*` tag: re-runs the free gates, fails on any leftover placeholder (`--strict`), builds `voicestead.skill`, and cuts a GitHub Release with it attached.

**`pr-eval.yml`** — on every PR: posts one sticky comment with the check summary and the "include your scorecard delta" reminder. Fork PRs run with a read-only token, so the comment is same-repo only.

This is the general pattern for testing any LLM skill: **cheap deterministic checks guard every change; expensive model-graded evals gate releases; humans calibrate and make the final call.**

## Where this lives

A **GitHub repository**, laid out so the installable skill stays clean:

```
skills/voicestead/     ← the skill. This — and only this — is packaged to voicestead.skill and installed.
.claude-plugin/        ← plugin + marketplace manifests (Door 1: one-command install).
tests/                 ← the harness. Dev-only; never shipped to users.
.github/workflows/     ← CI.
README.md              ← repo/dev readme.
```

`tests/` and `.github/` are never loaded by Claude at runtime — they're development infrastructure that lives alongside the skill, exactly like a normal library repo keeps its `src/` and its `tests/` side by side. `python3 -m scripts.package_skill voicestead` zips only `skills/voicestead/`.

## Repo tooling (`scripts/`)

Standalone argparse + stdlib helpers, run from the repo root. None needs a key or the network.

| Script | What it does | Exits 1 when |
|---|---|---|
| `scripts/package_skill.py` | Zips `skills/voicestead/` into `voicestead.skill`; personal profile files never ship | the skill dir or its SKILL.md is missing |
| `scripts/check_links.py` | Resolves every relative markdown link | any link is broken |
| `scripts/check_placeholders.py` | Sweeps for leftover pre-launch sentinel tokens | `--strict` finds one |
| `scripts/voice_profile_draft.py` | Measures 2–3 writing samples into a draft voice profile on stdout; deterministic, every number computed | fewer than 2 samples, or `--out` points into `skills/` |

## Honest limits

- The judge is a good proxy for a thoughtful reader, not a substitute for one. Treat its scores as evidence, not verdicts.
- Deterministic checks catch *form*, never *substance*. They can confirm the point is short; they can't confirm it's the *right* point.
- Voice is unfalsifiable by machine. Budget human review for it, forever.
- Optimizing to any metric corrupts it. Re-audit the rubric and checks whenever scores climb but the writing doesn't feel better.

## Experiments

`tests/experiments/` holds one-off research studies that use the same harness. Current: `instruction-voice/` — a pre-registered matrix testing how instruction tone, register, person, and mechanical quality affect output quality and voice contamination (see its PROTOCOL.md; start with `--dry-run`, then `--smoke`).
