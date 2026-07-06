# Instruction-Voice Experiment — Protocol

**Question:** How does the *voice* of an instruction (person, rhetorical mode, politeness, vocabulary register, mechanical quality) affect Voicestead's output quality — and which dimensions actually matter?

**Origin:** A peer's informal Copilot test found nearly all voice variants produced "different flavors of good"; only bad grammar + misspellings reliably degraded output. We treat this as a hypothesis to stress-test, not a conclusion.

## Pre-registered predictions (falsifiable, written before running)

- **H1 (mechanical, refined):** Mechanical errors on *content-critical tokens* (names, numbers, key nouns) degrade adherence and truth measurably; errors on *function words* degrade little on a frontier model. The peer's binary "bad grammar hurts" is predicted to split into these two very different effects.
- **H2 (register contamination):** Tone/register variants will NOT much change task quality — but WILL shift the *output's* register (contamination). For code this is invisible; for prose it's the whole game. Predicted largest for rude and brutish variants.
- **H3 (the untested dimensions dominate):** Specificity and structure variants will produce larger quality/adherence deltas than any voice variant. The peer found voice doesn't matter partly because he never varied the things that do.
- **H4 (skill as buffer):** With Voicestead loaded, contamination is smaller than without (the skill explicitly pins output voice to the reader/profile), measurable via the optional no-skill arm.

## Design

One-factor-at-a-time around a fixed baseline, plus two interaction cells and a second wave for the dimensions the peer skipped. Full factorial (108+ cells) is deliberately rejected as unrunnable.

- **Baseline B0:** second person, informative, neutral-polite, plain-idiomatic, mechanically correct.
- **Wave 1 (replicates the peer):** person (first, third), rhetorical mode (persuasive), politeness (super-polite, rude), vocabulary (high, brutish), mechanical (M1 function-word typos/bad grammar; M2 content-word corruption — the refinement).
- **Wave 2 (what he didn't test):** S1 vague (constraints stripped), S2 scaffolded (delimited sections, explicit format), E1 one-shot example, N1 all constraints phrased negatively.
- **Interactions:** X1 rude×brutish, X2 persuasive×high-vocab.

**Constant-content rule:** every variant carries the *identical* facts and constraints; only the wrapper voice changes. (Register manipulations in the wild accidentally change specificity and length — the main confound in informal tests. S1 is the only variant allowed to drop constraints, because measuring that drop is its purpose.)

## Tasks (4, from cases.json, spanning modes/genres)

Slip email (inform, format-constrained) · SRE pitch (persuade) · humanize-the-slop (improve) · team kickoff note (influence). Each defines: facts, hard constraints (must-include strings, word cap, subject-line requirement), content-typo targets for M2, and the intended reader register for tone judging.

## Metrics

**Deterministic (per output):** constraint adherence (must_include, max_words, has_subject), truth (no_invented_numbers vs. the clean task facts — M2's key metric: does the model *propagate* the corrupted name/number, silently fix it, or flag it?), rhythm (burstiness, triads), tells, plus contamination proxies: exclamation density, insult-lexicon hits (rude leak), long-word rate (high-vocab leak).

**Judge (rubric-voice.md, median of runs):** task_quality, instruction_adherence, tone_fidelity (does the output's tone serve the *stated reader*?), register_contamination (did the instruction's voice leak?), human_rhythm.

## Size and cost

Full: 16 variants × 4 tasks × 3 runs = 192 generations + ~2 judge calls each ≈ 550–600 API calls. Smoke (`--smoke`): 6 variants (B0, T2, V2, M1, M2, S1) × 2 tasks = 12 cells (× 3 runs by default = 36 generations; add `--runs 2` for a faster 24). Run smoke first; only scale if the smoke deltas look real.

## Analysis

Per variant: mean ± sd per metric, delta vs. B0, rank by |delta|. With n=3 per cell only large effects are detectable — report effect direction + magnitude, no p-value theater. The decision rule: a dimension "matters" if its worst level shifts a primary metric (adherence, truth, tone_fidelity) by ≥1 rubric point or flips a hard deterministic check across a majority of tasks.

## Threats to validity (known, accepted)

Single judge model (position bias mitigated by design; self-preference unmitigated — use a different family than the generator when possible). Small n. Template-authored variants (one author's idea of "rude"). Claude-specific results won't transfer to Copilot and vice versa — that's partly the point.
