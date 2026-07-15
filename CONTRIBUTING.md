# Contributing to Voicestead

Thanks for being here. The best contribution to a writing skill is a hard case it gets wrong — a real prompt, a clear idea of the right answer, and proof of whether the skill clears the bar.

So the contribution model is three steps: **add a case, run the suite, include the scorecard delta.** That's it. If you do those three things, your PR is easy to trust and easy to merge.

## Add a case

Cases live in two places, and a good contribution touches both.

1. **The harness case** — `tests/cases.json`. Add an object to the `evals` array. Give it the next `id`, a `mode` (`draft` / `improve` / `review` / `extract`), a `prompt` written the way a real person would type it, and an `expected_output` that describes what a passing answer does (not the exact words — prose isn't diffable). Wire the Tier-1 `deterministic_checks` that should hold, the `rubric_dimensions` a judge should score, and the `must_pass` hard gates. Set `baseline_compare: true` if the case is meant to beat a no-skill baseline. Any specific the prompt supplies must survive into the output — that's the Truth rule, and `no_invented_numbers` enforces it.

2. **The native mirror** — `skills/voicestead/evals/evals.json`. Mirror the same case into the skill's own `evals.json` so the official skill-eval loop can run it as an isolated subagent. Keep the `id`, `prompt`, and `expected_output` in sync with the harness copy; the mirror carries the fields the native runner understands. Two homes, one source of truth — if they drift, the harness copy wins.

## Run the suite

Tier 1 is **free, deterministic, and needs no API key** — run it on every change:

```bash
python3 tests/checks/run_checks.py --corpus tests/corpus
```

That's the same net CI runs on every push: structural and mechanical slop (buried point, flat rhythm, triads, tell-words, invented numbers, onboarding re-pitch). If it's red, fix it before you open the PR.

The full model-graded eval runs on your Claude Code subscription by default — the harness drives your installed `claude` binary, no key required (see [Backends](tests/TESTING.md#backends)). Those runs are iteration signals: cheap to repeat, good for tuning. The scorecard a PR cites comes from the pinned `api` backend, which **needs a key** and costs a little:

```bash
export ANTHROPIC_API_KEY=sk-...
python3 tests/run_eval.py --cases tests/cases.json --runs 3 --out tests/results --backend api
```

It generates with and without the skill, judges the pairs blind, and writes `tests/results/scorecard.md`. That scorecard is the receipt.

## What a PR must include

The **scorecard delta.** Show the numbers before your change and after — win rate, pass-rate delta, any hard-gate failures. A green Tier-1 run is the floor; if your change touches behavior a judge scores, paste the with/without scorecard so a reviewer can see the skill got better and nothing regressed. No pinned-backend number yet (no key)? Say so plainly and include the Tier-1 output, plus a subscription (`claude-cli`) scorecard if you ran one — labeled as the iteration signal it is. Honesty about what you measured beats a made-up percentage. This repo exists to stop writing tools from inventing numbers; we hold our own PRs to that too.

## What's open, and what's personal by design

Some surfaces are built for community help. Some are meant to stay one person's, forever. Knowing which is which saves everyone a round-trip.

**Open to PRs:**
- **Format packs** — new output formats and their length/shape rules in `references/formats.md`.
- **Eval cases** — new prompts that expose a weakness, per the two-file recipe above.
- **Tells-list updates** — additions to `references/tells.md`, ideally with a case showing the tell in the wild.

**Personal by design (please keep these out of PRs):**
- **Voice profiles** — a voice profile is one writer's fingerprint. The skill reads yours locally; it never belongs in the shared repo.
- **Influences** — the influence files are personal study notes. Same reasoning: the mechanism is shared, the contents are yours.

If you're not sure which bucket your idea falls in, open an issue first and ask. We'd rather talk it through than turn a good contribution away at the door.

### Before changing SKILL.md or references/

Before changing SKILL.md or references/, see [the eval runbook](skills/voicestead/evals/RUNNING.md) — the local-mode regression must be green before merge.

### Changing the skill? Refresh the exports

`skills/voicestead/SKILL.md` is the source of truth, but three flat-surface platforms ship a condensed copy. If you edit `SKILL.md`:

1. Re-condense `exports/core.md` to reflect the change (keep it ≤ 8,000 characters).
2. Re-seal and rebuild:
   ```bash
   python -m scripts.build_exports --reseal
   python -m scripts.build_exports
   ```
3. Commit the regenerated `exports/`.

CI (`python -m scripts.build_exports --check`) fails if `core.md` is stale, the ChatGPT instructions exceed 8,000 chars, Gemini exceeds 10 knowledge files, or any committed export is out of date.
