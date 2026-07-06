# Voicestead

**Writing that sounds like you and never invents a fact — with an eval harness built to prove it.**

A writing skill for [Claude](https://claude.com/claude-code), plus the eval harness that keeps it honest.

---

## See it first

Paste in something that reeks of AI. Here is what comes back.

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

Three doors. Pick the one that matches how you use Claude.

**Door 1 — Claude Code plugin.** One command, and you get updates when the version bumps.

```
/plugin marketplace add greenpioneersolutions/voicestead
/plugin install voicestead@voicestead
```

**Door 2 — Copy the folder.** Claude Code, no marketplace.

```bash
cp -r skills/voicestead ~/.claude/skills/
```

**Door 3 — Upload to claude.ai.** For Projects and the desktop app.

```bash
python3 -m scripts.package_skill voicestead   # builds voicestead.skill
```

Attach `voicestead.skill` to a GitHub Release, then upload it under Customize → Skills.

---

## Does it actually work?

Fair question to ask of anything that claims to improve your writing. Voicestead answers it with a test harness instead of adjectives.

Prose is hard to test: the same prompt gives different text every run, and "good" spans voice, clarity, rhythm, and truth at once. So the harness works in three tiers, each catching a different failure at a different cost.

- **Tier 1 — deterministic checks.** Free, instant, and run on every push. A counter or a regex catches the mechanical slop: a buried point, metronomic rhythm, one triad too many, a tell-word, a number in the output that was never in the input. That last one is the hard gate — a writing tool that invents statistics is dangerous, and this stops it cheaply.
- **Tier 2 — LLM as judge.** For the subjective dimensions a regex can't touch. A second Claude scores each output against an anchored rubric, runs several times for stability, and — the headline metric — judges *with-skill against without-skill*, blind and order-randomized. We report a win rate, not a vibe.
- **Tier 3 — you.** One question stays human forever: *does it sound like me?* A judge can approximate "sounds human." It can't confirm it sounds like *you*. Your verdicts get saved as a golden set that anchors every future version.

Full method: [`tests/TESTING.md`](tests/TESTING.md).

### Scorecard

| Metric | Target | Result |
|---|---|---|
| Blind win rate vs. no skill | ≥ 70% | **pending S0** |
| Hard-gate failures (invented facts, high-confidence tells) | 0 | **pending S0** |
| Previously-shipping golden cases regressed | 0 | **pending S0** |

*No number goes in this table until it's measured — on real writing, judged blind. It gets published here the day it's run. A writing skill that invents its own results is the exact thing this one exists to stop.*

---

## Make it yours

The lean core ships the same for everyone. What makes it *yours* is two files you build once.

- **Voice profile.** Paste two or three real samples of your writing and the skill learns your defaults — your sentence length, your punctuation habits, whether you open with a lowercase "hey." From then on it edits toward you, not toward generic polish.
- **Influences.** Run the influence interview and teach it the writers who shaped you. It studies them for moves, not fingerprints, and lets those moves inform a draft without ever name-dropping them at the reader.

**Storage, honestly.** In Claude Code, the skill writes `voice-profile.md` and `influences.md` and rereads them each run. On claude.ai, you add the same two files to your Project knowledge. There is no magic persistence — just plain files the skill reads. That is the whole trick, and it's yours to inspect, edit, or delete.

---

## FAQ

**Does it actually sound like me?**
Out of the box it sounds like a clean, plain human — good, but generic. It sounds like *you* once you give it a voice profile from your real writing. That step is the difference, and it takes about three minutes.

**Will it invent facts to make my writing better?**
No, by design. When a draft has no real specifics, it flags the gap and asks you for one — it never fabricates a number or a quote. This is enforced, not just encouraged: the hard gate in Tier 1 fails any output containing a figure that wasn't in your input.

**claude.ai or Claude Code — which door do I use?**
Claude Code users take Door 1 or 2. If you work in claude.ai Projects or the desktop app, take Door 3 and upload the `.skill`. Same skill either way; only the delivery differs.

**How is it tested?**
A three-tier harness: free deterministic checks on every push, an LLM judge on demand, and a human for the final "sounds like me?" call. The headline number is a blind win rate against Claude with no skill loaded. See the scorecard above and [`tests/TESTING.md`](tests/TESTING.md).

**Is my voice profile shared with anyone?**
No. It's a local file on your machine (Claude Code) or a document in your own Project (claude.ai). It never leaves your control, and contributions to the project deliberately stay on the shared surfaces — format packs, eval cases, tell-lists — never personal voice files.

---

## Contributing

Add a case to `tests/cases.json`, run the suite, and include the scorecard delta in your PR — details in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Documentation

- [Using Voicestead](docs/USING.md) — install, first run, the voice setup, the modes, storage.
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
docs/                 ARCHITECTURE, USING, LAUNCH, BETA
.github/workflows/    CI: check (free) on every push, evaluate + golden on dispatch
```

```bash
# run the fast, free structural checks (no API key)
pip3 install -r tests/requirements.txt
python3 tests/checks/run_checks.py --corpus tests/corpus

# run the full evaluation (needs a key)
export ANTHROPIC_API_KEY=sk-...
python3 tests/run_eval.py --cases tests/cases.json --runs 3 --out tests/results
```

`tests/` and `.github/` are never loaded by Claude at runtime. `python3 -m scripts.package_skill voicestead` zips only `skills/voicestead/`.

---

## License

MIT — see [LICENSE](LICENSE). Site: [voicestead.ai](https://voicestead.ai) *(coming soon)*.
