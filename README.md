<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="brand/voicestead-lockup-reversed.svg">
    <img src="brand/voicestead-lockup.svg" alt="Voicestead" width="380">
  </picture>
</p>

<p align="center"><strong>Stop sounding like AI. Start sounding like your voice.</strong></p>

<p align="center">Voicestead teaches the <a href="https://claude.com/claude-code">Claude</a> you already use to write the way you do — and to ask for a real fact instead of inventing one. Paste in a rough draft, get back something you'd actually hit send on.</p>

<p align="center">A writing skill plus the eval harness that keeps it honest — so the promise is measured, not asserted.</p>

<p align="center"><em>No account · No credit card · Open source (MIT) · Works with your Claude subscription</em></p>

<p align="center"><a href="#install"><strong>Install free — 2-minute setup</strong></a>&nbsp; · &nbsp;<a href="https://voicestead.ai">voicestead.ai</a> <em>(coming soon)</em></p>

---

## See it first

Paste in something that reeks of AI. Here's what comes back — a real pass, not a word-swap.

**Before**

> In today's rapidly evolving landscape, it's worth noting that our robust solution doesn't just streamline workflows — it transforms them. The implementation of our platform facilitates seamless collaboration, enhances productivity, and unlocks innovation. The data tells us adoption is accelerating.

**After**

> More teams are moving to the platform, and the ones that do say it's easier to work together.
>
> *(The original names nothing concrete — no numbers, no example, nothing that actually happened. I won't invent them for you. Give me one real win and this goes from fine to undeniable.)*

A paragraph of throat-clearing became one plain sentence and a straight question. Notice what the skill did *not* do: it didn't fabricate a statistic to fill the empty space. The empty space was the real problem, so it said so.

---

## What it is

Voicestead is a small writing skill for Claude. It handles the mechanical work — structure, tightening, cutting the tells that mark prose as machine-made — and leaves you the thinking and the voice. It does the dishes. You keep the art.

Underneath sit three mental models — name the one job, point first, say it to one person — plus a persuasion module drawn from the influence classics and an anti-slop discipline. That last piece is built on what separates human writing from machine writing: rhythm that varies and specifics that are real, not a brittle list of banned words.

---

## Install

Find your platform, do the one thing in the **Install** column. That's it.

| Platform | Install | Account | ~Time |
|---|---|---|---|
| **Claude Code** | one `/plugin` command | Claude | 1 min |
| **claude.ai** (Projects, desktop) | upload the `.skill` | Claude | 2 min |
| **ChatGPT** (Custom GPT / Project) | paste 1 box · upload **1** file | ChatGPT | 3 min |
| **Gemini** (Gem) | paste 1 box · upload **1** file | Google | 3 min |
| **Codex · Cursor · Copilot · Zed** (`AGENTS.md`) | one `curl` command | — | 30 sec |
| **Cursor · Codex · Copilot · CLIs** (native skill) | one `git` command | — | 30 sec |

> **Want true one-click on ChatGPT & Gemini** — click a link, start typing, nothing to paste or upload? That version is *hosted*, so it has to be published once from a Voicestead account. The 5-minute how-to is in [`docs/PUBLISHING.md`](docs/PUBLISHING.md); once it's live this table gets two "▶ Open" links. Until then, the 3-minute build below is the way.

### Claude Code

Plugin (auto-updates when the version bumps):

```
/plugin marketplace add greenpioneersolutions/voicestead
/plugin install voicestead@voicestead
```

Or copy the folder, no marketplace: `cp -r skills/voicestead ~/.claude/skills/`

### claude.ai (Projects, desktop)

```bash
python3 -m scripts.package_skill voicestead   # builds voicestead.skill
```

Upload `voicestead.skill` under Customize → Skills.

### ChatGPT — Custom GPT or Project

<details>
<summary><strong>3-minute build</strong> (until the hosted one-click lands)</summary>

1. ChatGPT → **Explore GPTs → Create → Configure**. Name it `Voicestead`.
2. **Instructions:** open [`exports/chatgpt/instructions.txt`](exports/chatgpt/instructions.txt) (the raw view has a **Copy** button), and paste it into the Instructions box.
3. **Knowledge:** upload the single [`exports/chatgpt/knowledge-bundle.md`](exports/chatgpt/knowledge-bundle.md) — **one file, not ten**. (Want finer retrieval? Upload the ten files in [`exports/chatgpt/knowledge/`](exports/chatgpt/knowledge) instead.)
4. Paste the four lines from [`conversation-starters.txt`](exports/chatgpt/conversation-starters.txt) → **Create**.

Full walkthrough and the lighter Project option: [`exports/chatgpt/SETUP.md`](exports/chatgpt/SETUP.md).

</details>

### Gemini — Gem

<details>
<summary><strong>3-minute build</strong></summary>

1. Gemini → **Gem manager → New Gem**. Name it `Voicestead`.
2. **Instructions:** copy [`exports/gemini/instructions.txt`](exports/gemini/instructions.txt), paste it in.
3. **Knowledge:** upload the single [`exports/gemini/knowledge-bundle.md`](exports/gemini/knowledge-bundle.md) — one file, so there's no 10-file cap to manage.
4. **Save.**

Full walkthrough: [`exports/gemini/SETUP.md`](exports/gemini/SETUP.md).

</details>

### AGENTS.md tools (Codex, Copilot, Cursor, Zed, Amp)

One command drops it into your repo:

```bash
curl -o AGENTS.md https://raw.githubusercontent.com/greenpioneersolutions/voicestead/main/exports/agents/AGENTS.md
```

Claude Code reads `CLAUDE.md`, so also run `printf '@AGENTS.md\n' >> CLAUDE.md`. More: [`exports/agents/SETUP.md`](exports/agents/SETUP.md).

### Skill-native coding tools (Cursor, Codex, Copilot, Gemini CLI, Windsurf)

These read Agent Skills natively — drop the full skill (all references, on-demand loading) into `.agents/skills/`:

```bash
git clone --depth 1 https://github.com/greenpioneersolutions/voicestead /tmp/voicestead \
  && cp -r /tmp/voicestead/skills/voicestead .agents/skills/voicestead
```

*(The two `curl`/`git` commands assume the repo is public on GitHub.)*

### What each surface keeps

| Capability | Claude | Skill-native | ChatGPT / Gemini | AGENTS.md |
|---|---|---|---|---|
| On-demand references | ✅ | ✅ | ⚠️ retrieval | ❌ repo links |
| Voice-profile persistence | ✅ file | ✅ file | ⚠️ paste | ⚠️ in-file |
| Install | plugin | one command | paste + 1 upload | one command |

`⚠️` = works with a caveat — the honest limits are in [`docs/PLATFORMS.md`](docs/PLATFORMS.md).

---

## Does it actually work?

Fair question to ask of anything that claims to improve your writing. Voicestead answers it with a test harness instead of adjectives.

Prose is hard to test: the same prompt gives different text every run, and "good" spans voice, clarity, rhythm, and truth at once. So the harness works in three tiers, each catching a different failure at a different cost.

- **Tier 1 — deterministic checks.** Free, instant, and run on every push. A counter or a regex catches the mechanical slop: a buried point, metronomic rhythm, one triad too many, a tell-word, a number in the output that was never in the input. That last one is the hard gate — a writing tool that invents statistics is dangerous, and this stops it cheaply.
- **Tier 2 — LLM as judge.** For the subjective dimensions a regex can't touch. A second Claude scores each output against an anchored rubric, runs several times for stability, and — the headline metric — judges *with-skill against without-skill*, blind and order-randomized. We report a win rate, not a vibe.
- **Tier 3 — you.** One question stays human forever: *does it sound like me?* A judge can approximate "sounds human." It can't confirm it sounds like *you*. Your verdicts get saved as a golden set that anchors every future version.

Full method: [`tests/TESTING.md`](tests/TESTING.md). Every recorded run lives in the public run ledger — [`docs/evals/`](docs/evals/README.md) — with its backend, models, and figures copied straight from the run's own artifacts.

### Scorecard

| Metric | Target | Result |
|---|---|---|
| Blind win rate vs. no skill | ≥ 70% | **78.3%** — directional* |
| Hard-gate failures (skill's own drafts) | 0 | **3 of 32*** |
| Previously-shipping golden cases regressed | 0 | *golden set not in this run* |

*First read, 2026-07-08 — all 32 cases at `--runs 1` on a Claude Code subscription (`claude-cli` backend). **Directional, not the averaged official number** (23 blind judgments; an averaged `--runs 3` or pinned `--backend api` run comes next). The three hard-gate cases are honest misses, not fabrications hidden: an over-expanded short edit, an accurate-but-unsourced date, and an incomplete de-slop — full breakdown and provenance in [`docs/evals/`](docs/evals/). No number goes in this table until it's measured, judged blind; a writing skill that invents its own results is the exact thing this one exists to stop.*

---

## Make it yours

The lean core ships the same for everyone. What makes it *yours* is two files you build once.

- **Voice profile.** Paste two or three real samples of your writing and the skill learns your defaults — your sentence length, your punctuation habits, whether you open with a lowercase "hey." From then on it edits toward you, not toward generic polish.
- **Influences.** Run the influence interview and teach it the writers who shaped you. It studies them for moves, not fingerprints, and lets those moves inform a draft without ever name-dropping them at the reader.

**Storage, honestly.** In Claude Code, the skill writes `voice-profile.md` and `influences.md` and rereads them each run. On claude.ai, you add the same two files to your Project knowledge. There is no magic persistence — just plain files the skill reads. That is the whole trick, and it's yours to inspect, edit, or delete.

---

## When you want more — Voicestead Studio

**The skill sounds like you today. Studio remembers you tomorrow.**

You turn it on as a connector called **Voicestead Memory** — the front door to Studio.

The free skill sounds like you as long as you keep feeding it your voice files by hand. Studio does the remembering for you: a secure, private memory behind your Claude that keeps your voice profile current, saves the lines that actually worked, and hands your Claude the right ones at the right moment.

- **Remembers your voice.** One living profile, versioned like code. Every session, on every surface, your Claude starts already knowing you — you never explain yourself twice.
- **Learns what worked.** Tell it what you shipped and what landed. It keeps score and leans into the moves that win.
- **Retrieves the right you.** An email to an exec isn't a post to strangers. Studio pulls your best past lines for this exact moment and hands them to your Claude as reference.
- **Keeps receipts.** Every draft is scored — does it sound like you, are the tells creeping back, are the numbers real. Proof, not vibes.

Studio never writes a word — your own Claude does that, on your own subscription. Your writing stays encrypted, walled off, never trained on, and deletable for real. Same honesty rule as the skill: it returns your real, stored words and never fabricates a memory. The skill is the tool; Studio is the memory.

Studio will be paid at launch. **The beta is free**, and the skill stays free either way. Join the list at **[voicestead.ai](https://voicestead.ai)** *(coming soon)*, or read what it adds in [`docs/BETA.md`](docs/BETA.md).

---

## FAQ

**Does it actually sound like me?**
Out of the box it sounds like a clean, plain human — good, but generic. It sounds like *you* once you give it a voice profile from your real writing. That step is the difference, and it takes about three minutes.

**Will it invent facts to make my writing better?**
No, by design. When a draft has no real specifics, it flags the gap and asks you for one — it never fabricates a number or a quote. This is enforced, not just encouraged: the hard gate in Tier 1 fails any output containing a figure that wasn't in your input.

**claude.ai or Claude Code — which door do I use?**
Claude Code: install the plugin or copy the folder into `~/.claude/skills/`. claude.ai Projects or desktop: build the `.skill` and upload it under Customize → Skills. On ChatGPT, Gemini, or an AGENTS.md tool? Each now has its own paste-ready bundle in [`exports/`](exports/README.md). Same skill everywhere; only the delivery differs.

**How is it tested?**
A three-tier harness: free deterministic checks on every push, an LLM judge on demand, and a human for the final "sounds like me?" call. The headline number is a blind win rate against Claude with no skill loaded. See the scorecard above and [`tests/TESTING.md`](tests/TESTING.md).

**Is my voice profile shared with anyone?**
No. It's a local file on your machine (Claude Code) or a document in your own Project (claude.ai). It never leaves your control, and contributions to the project deliberately stay on the shared surfaces — format packs, eval cases, tell-lists — never personal voice files.

---

## Your next draft could sound like you

Two minutes from now, it can. That's the whole pitch.

<p align="center"><a href="#install"><strong>Install Voicestead free</strong></a>&nbsp; · &nbsp;<a href="https://github.com/greenpioneersolutions/voicestead">Star it on GitHub</a>&nbsp; · &nbsp;<a href="https://voicestead.ai">voicestead.ai</a> <em>(coming soon)</em></p>

<p align="center"><em>Free forever · no account · no credit card.</em></p>

---

## Contributing

Add a case to `tests/cases.json`, run the suite, and include the scorecard delta in your PR — details in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Documentation

- [Using Voicestead](docs/USING.md) — install, first run, the voice setup, the modes, storage.
- [Platforms](docs/PLATFORMS.md) — what each surface (ChatGPT, Gemini, AGENTS.md, native) keeps and loses.
- [Publishing the one-click versions](docs/PUBLISHING.md) — how to host the ChatGPT GPT and Gemini Gem.
- [Architecture](docs/ARCHITECTURE.md) — how the skill and its eval harness are built.
- [Beta access](docs/BETA.md) — what Voicestead Studio adds, and how to request early access.
- [The launch play](docs/LAUNCH.md) — the go-to-market plan and where the project stands.

---

## The story behind it

Voicestead is built from 16 scholarly papers on what makes prose land, eight master writers studied for their moves, and one replication that failed — which we kept on purpose. Keeping the failure is the point. A skill whose whole job is to refuse invented facts has no business hiding the study that didn't hold up. The sourcing lives in [`skills/voicestead/references/craft-notes.md`](skills/voicestead/references/craft-notes.md) and [`science.md`](skills/voicestead/references/science.md).

---

## For developers

The repository root is the plugin. The skill, the harness, and the manifests live side by side, the way a normal library keeps `src/` next to `tests/`.

```
skills/voicestead/    the skill — the only thing packaged into voicestead.skill
tests/                the three-tier eval harness (dev-only, never shipped)
.claude-plugin/       plugin.json + marketplace.json (Door 1)
scripts/              package_skill.py, check_placeholders.py
exports/              paste-ready bundles for ChatGPT, Gemini, AGENTS.md (generated + committed)
exports/core.md       hand-authored ≤8k distillation; build_exports.py assembles the rest
docs/                 ARCHITECTURE, USING, LAUNCH, BETA
brand/                logo, favicon, OG card, color + type tokens (dev-only, never shipped)
.github/workflows/    CI: check (free) on every push, evaluate + golden on dispatch
```

```bash
# run the fast, free structural checks (no API key)
pip3 install -r tests/requirements.txt
python3 tests/checks/run_checks.py --corpus tests/corpus

# run the full evaluation (default backend: your installed claude CLI, on a Claude Code subscription)
python3 tests/run_eval.py --cases tests/cases.json --runs 3 --out tests/results

# the pinned SDK backend — for publishable numbers; needs a key
export ANTHROPIC_API_KEY=sk-...
python3 tests/run_eval.py --cases tests/cases.json --runs 3 --out tests/results --backend api
```

`tests/` and `.github/` are never loaded by Claude at runtime. `python3 -m scripts.package_skill voicestead` zips only `skills/voicestead/`.

---

## License

MIT — see [LICENSE](LICENSE). Site: [voicestead.ai](https://voicestead.ai) *(coming soon)*.
