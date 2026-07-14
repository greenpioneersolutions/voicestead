<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="brand/voicestead-lockup-reversed.svg">
    <img src="brand/voicestead-lockup.svg" alt="Voicestead" width="380">
  </picture>
</p>

<p align="center"><strong>A writing skill that keeps your voice.</strong></p>

<p align="center">Voicestead teaches the <a href="https://claude.com/claude-code">Claude</a> you already use to do the mechanical work — structure, tightening, cutting the tells that mark prose as machine-made — and leaves you the thinking and the voice. It works entirely locally; connect memory later if you want it.</p>

<p align="center"><em>Free · open source (MIT) · no account · works with your Claude subscription</em></p>

---

## What it is

A small writing skill for Claude. Paste in a rough draft or a brain-dump and get back something you'd actually send — in your voice, not a model's. It runs on your own Claude: no account, no server, nothing to sign up for. If you ever want your voice to follow you across devices, you can turn on memory later — but you never have to.

One thing it will not do is invent facts. When a draft has no real number or quote to stand on, it says so and asks you for one instead of making it up.

**Before**

> In today's rapidly evolving landscape, our robust solution doesn't just streamline workflows — it transforms them, unlocking innovation and driving engagement at scale.

**After**

> More teams are moving to the platform, and the ones that do say it's easier to work together.
>
> *(The original names nothing real — no number, no example. I won't invent one for you. Give me a win that actually happened and this goes from fine to sharp.)*

A paragraph of throat-clearing became one plain sentence. Notice what it did *not* do: fill the empty space with a made-up statistic. The empty space was the problem, so it said so.

## Install

One step for your client. Pick one.

**Claude Code**

```
/plugin marketplace add greenpioneersolutions/voicestead
/plugin install voicestead@voicestead
```

**claude.ai (skill upload)** — build the skill file, then upload it under **Customize → Skills**:

```
python3 -m scripts.package_skill voicestead   # → voicestead.skill
```

**Claude Desktop** — same `voicestead.skill` as above, uploaded under **Customize → Skills** in the desktop app.

On ChatGPT, Gemini, or a coding tool (Codex, Cursor, Copilot)? Each has a paste-ready bundle — see [other platforms](#other-platforms).

## Try it

Install it, then paste one of these into a fresh chat:

- **Turn a mess into an email.** *"Help me tell my team the launch slips to Friday. Here's the mess: QA found a login bug, the fix needs another two days, and I don't want to sound panicked."*
- **Make it sound less AI.** Paste something stiff and say *"make this sound less AI — keep my meaning, lose the polish."*
- **Draft a hard message.** *"Help me push back on my manager's deadline without sounding difficult."*

None of these need setup. To make it sound like *you* specifically, give it two or three real samples of your writing and ask for a voice profile — about three minutes, and every draft after that edits toward you.

## Turn on memory (optional)

The skill sounds like you today from the voice file you give it. **Voicestead Memory** does the remembering for you: your voice profile and the lines that worked persist across sessions and devices, so you never paste them again. It stores only lines you've approved, your own Claude still does all the writing on your own subscription, and you can see and delete everything — including any line held for review — at `app.voicestead.ai`. The skill works exactly the same without it.

Steps for every client are in **[CONNECT.md](CONNECT.md)** — a one-time setup you do in your Claude's connector settings.

## Privacy

Your voice profile is a plain file — on your machine in Claude Code, or in your own Project on claude.ai. It never leaves your control, and it's yours to read, edit, or delete.

Turn on memory and what it stores stays private to you: approved lines only, kept in your own space, never pooled with anyone else's and never used to train a shared model, deletable for real. Contributions to this project stay on the shared surfaces — eval cases, tell-lists, format packs — never personal voice files. More detail: [CONNECT.md](CONNECT.md) and [docs/BETA.md](docs/BETA.md).

---

## Does it work?

Fair question for anything that claims to improve your writing. Voicestead answers with a test harness, not adjectives — three tiers, each catching a different failure at a different cost: free deterministic checks on every push (including a hard gate that fails any draft with a number that wasn't in the input), an LLM judge for the subjective dimensions, and you for the one question a machine can't answer — *does it sound like me?* Method: [tests/TESTING.md](tests/TESTING.md); every run is logged in [docs/evals/](docs/evals/README.md).

### Scorecard

| Metric | Target | Result |
|---|---|---|
| Blind win rate vs. no skill | ≥ 70% | **78.3%** — directional* |
| Hard-gate failures (skill's own drafts) | 0 | **3 of 32*** |
| Previously-shipping golden cases regressed | 0 | *golden set not in this run* |

*First read, 2026-07-08 — all 32 cases at `--runs 1` on a Claude Code subscription. Directional, not the averaged official number; a pinned `--backend api` run comes next. The three hard-gate misses are honest — an over-expanded edit, an accurate-but-unsourced date, an incomplete de-slop — with the full breakdown in [docs/evals/](docs/evals/). No number goes in this table until it's measured blind; a writing skill that invents its own results is the exact thing this one exists to stop.*

## Make it yours

What makes it *yours* is two files you build once. Paste a few real samples and the skill learns your defaults — sentence length, punctuation habits, whether you open with a lowercase "hey" — and edits toward you from then on. Run the influence interview and it studies the writers who shaped you for their moves, not their fingerprints. In Claude Code these are plain files (`voice-profile.md`, `influences.md`) the skill rereads each run; on claude.ai you add them to your Project knowledge. No magic persistence — just files you can inspect, edit, or delete.

## Other platforms

The same skill runs on ChatGPT (Custom GPT), Gemini (Gem), AGENTS.md tools, and skill-native coding tools — each with a paste-ready bundle and its own setup notes in [exports/](exports/README.md). What each surface keeps and gives up is in [docs/PLATFORMS.md](docs/PLATFORMS.md).

## Contributing

Add a case to `tests/cases.json`, run the suite, and include the scorecard delta in your PR — details in [CONTRIBUTING.md](CONTRIBUTING.md).

## Documentation

- [Using Voicestead](docs/USING.md) — install, first run, the voice setup, the modes, storage.
- [Connect memory](CONNECT.md) · [Troubleshooting](TROUBLESHOOTING.md)
- [Platforms](docs/PLATFORMS.md) — what each surface keeps and loses.
- [Architecture](docs/ARCHITECTURE.md) — how the skill and its eval harness are built.
- [Beta access](docs/BETA.md) — what Voicestead Studio adds.
- [The launch play](docs/LAUNCH.md) — the plan and where the project stands.

## The story behind it

Voicestead is built from 16 scholarly papers on what makes prose land, eight master writers studied for their moves, and one replication that failed — which we kept on purpose. A skill whose whole job is to refuse invented facts has no business hiding the study that didn't hold up. The sourcing lives in [craft-notes.md](skills/voicestead/references/craft-notes.md) and [science.md](skills/voicestead/references/science.md).

## For developers

The repository root is the plugin — skill, harness, and manifests side by side.

```
skills/voicestead/    the skill — the only thing packaged into voicestead.skill
tests/                the three-tier eval harness (dev-only, never shipped)
.claude-plugin/       plugin.json + marketplace.json
scripts/              package_skill.py, build_exports.py, check_links.py
exports/              paste-ready bundles for ChatGPT, Gemini, AGENTS.md (generated + committed)
docs/                 ARCHITECTURE, USING, LAUNCH, BETA, PLATFORMS
```

```bash
# fast, free structural checks (no API key)
pip3 install -r tests/requirements.txt
python3 tests/checks/run_checks.py --corpus tests/corpus

# full evaluation (default backend: your installed claude CLI, on a Claude Code subscription)
python3 tests/run_eval.py --cases tests/cases.json --runs 3 --out tests/results
```

`tests/` and `.github/` are never loaded by Claude at runtime. `python3 -m scripts.package_skill voicestead` zips only `skills/voicestead/`.

## License

MIT — see [LICENSE](LICENSE). Site: [voicestead.ai](https://voicestead.ai) *(coming soon)*.
