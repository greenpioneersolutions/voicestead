# The Launch Play — Voicestead

This is the working play, not a pitch: what ships, what gates it, and where we are right now. The repo is not step one. The eval is step one.

This is our own launch checklist, kept public on purpose — if you're reading it on launch day, that's the transparency working.

Voicestead is a writing skill for Claude plus a three-tier eval harness. The repo root is the plugin root. Current version is `0.9.0` (pre-launch); the launch target is `v1.0.0`, cut after the S0 eval clears and the S8 regression sweep is green. It ships under **Green Pioneer Solutions** (`github.com/greenpioneersolutions`), which holds the IP. Domain: `voicestead.ai` (purchased, site not yet live).

## The three laws

Every skill that broke out had the same three things. Not better prose about itself — these three:

1. **Instantly demoable.** You see the output and want it. A before/after that lands in ten seconds, before anyone reads a word of docs.
2. **Zero-friction install.** One command, or one upload. Every extra step halves the number of people who finish.
3. **Borrowed trust.** They launched through a channel that already trusted them — a following, an official listing, a newsletter. Quality gets you in the door; distribution is what actually happened.

The receipts corollary: a launch without receipts is a launch on vibes. Voicestead's receipt is the eval scorecard — a blind win rate on real writing, published the day it's measured. Few writing skills in this space bring one. That is the asset. Guard it: a skill built to refuse invented facts cannot publish an invented number about itself.

## The gate: S0

Nothing ships before this. Not the landing page, not a post, not the release.

Run the eval on real writing — five real pieces, each generated with the skill and without it, judged blind and order-randomized (`tests/run_eval.py`, method in `tests/TESTING.md`). Iterate on the skill until the blind win rate is a number you would stand behind in public. The target is **≥70%, with zero hard-gate failures** (no invented facts, no high-confidence tells) and zero previously-shipping golden cases regressed.

S0 needs one thing it doesn't have yet: an `ANTHROPIC_API_KEY`. The writer's five real pieces are already committed in `tests/golden/raw/`. Until the key exists, the scorecard stays marked **pending** — in the README, on the site, everywhere. Don't fill the table with a guess to unblock a downstream task. The pending marker is honest; a fabricated figure is the one thing this skill exists to stop.

One human check rides alongside the number: a real stranger sets up a voice profile, runs one real piece, and answers "does this sound like me, and does it respect the craft?" A judge can approximate "sounds human." It can't confirm "sounds like this person." That verdict, plus the five pieces, freezes into the golden set (S3) that anchors every future version.

## Packaging: the three doors

There is no single app store. The official path is plugins and plugin marketplaces, alongside plain skill repos people copy from, awesome lists, and third-party directories. So Voicestead packages for all three doors at once. This is largely **done** — `claude plugin validate` passes; what's still pending is a live door-1 install once the repo is public.

- **Door 1 — Claude Code plugin.** `.claude-plugin/plugin.json` in the repo root with explicit semver, the skill under `skills/voicestead/`, and `.claude-plugin/marketplace.json` at the root listing the plugin. Install is `/plugin marketplace add greenpioneersolutions/voicestead` then `/plugin install voicestead@voicestead`. Users get updates only when the version bumps.
- **Door 2 — Copy the folder.** `cp -r skills/voicestead ~/.claude/skills/` for the Claude Code crowd who skip the marketplace. The skill stays readable at a stable path.
- **Door 3 — `.skill` upload.** `python3 -m scripts.package_skill voicestead` builds `voicestead.skill`, attached to every GitHub Release. claude.ai and desktop users upload it under Customize → Skills; Team and Enterprise owners can provision it org-wide.

The dev harness under `tests/` and the workflows under `.github/` are never packaged — `package_skill` zips only `skills/voicestead/`. The README already carries the winner's anatomy: value prop, the slop-to-human before/after up top, install one-liners for all three doors, the scorecard (pending), FAQ, contribution invite.

## Where we are

The build spine from gate to launch to forever. This session shipped everything that didn't need an API key or live Studio URLs. What's left is gated on exactly those inputs.

| Phase | What it is | Status | What it needs next |
|---|---|---|---|
| **S0** | Eval gate (with/without, blind) | scaffolded | `ANTHROPIC_API_KEY`, then a run |
| **S1** | Trigger tuning | partial | S0 clear |
| **S2** | Onboarding hardened | partial | S0 clear |
| **S3** | Golden set + regression freeze | scaffolded | S0's real verdicts to freeze |
| **S4** | Distribution (three doors) | validate-green | live door-1 install (needs public repo) |
| **S5** | Studio integration | plan-only | Studio P7 green (in development, not shipped) |
| **S6** | Connector wiring + URL sweep | plan-only | real staging/prod Studio URLs, live `voicestead.ai` |
| **S7** | Instruction-voice experiment | scaffolded | S0 (research only) |
| **S8** | Full regression sweep | plan-only | S3 + S5; runs before any launch piece merges |
| **S9** | Landing page (`voicestead.ai`) | plan-only | S0 numbers, S6 URLs |
| **S10** | Launch content | plan-only | S8 green, S0 numbers |
| **S11** | Submissions & listings | plan-only | S8 green, public repo, S10 copy |
| **S12** | Post-launch care | plan-only | S11 (then recurring forever) |

Shipped this session: the plugin restructure (skill under `skills/voicestead/`, manifests at root, harness isolated under `tests/`); S4 packaging validated across all three doors; S2 onboarding with honest both-surface storage and three new cases; the S1 description sharpened; S0/S3 golden scaffolding awaiting real inputs; the `scripts/check_placeholders.py` guard (owner resolved to `greenpioneersolutions`; the placeholder sweep is clean; Studio URLs will be added (and sentinel-guarded) at S6); the S7 dry-run; one Track-A influence card (target: ten for launch); and CI — a free `check` job on every push, plus `golden` (the S0 benchmark), `release.yml`, and `pr-eval.yml`.

Five rules hold the spine together. **S0 gates all** — the blind win-rate gate comes first, everything waits on it. **S5 never before Studio P7** — a session with no connector must stay byte-identical to pre-S5. **S6 waits for real URLs** — no invented Studio MCP URLs; `voicestead.ai` is usable in copy but not live. **S8 before launch** — the full suite (all cases, golden, corpus) green with the changelog written, before any launch asset merges. **S12 is forever** — every accepted bug becomes an eval case before the fix; every major model release re-runs the sweep and reports drift.

Studio, for the record, is a future connector that adds persistent voice memory across sessions — tools like `get_writer_context`, `log_draft`, `score_draft`, `import_pieces`. It is in development. Not shipped, beta not open. Nothing in the launch depends on it, and no copy claims a ship date.

## The channel sequence

Borrowed trust, inner ring outward. Win one channel, then widen — don't spray day one. Every launch asset is written *with* Voicestead and says so; dogfooding is the demo. The story is just what happened: a writing skill built from 16 scholarly papers, eight master writers studied for their moves, and one replication that failed, which we kept on purpose.

1. **LinkedIn — the beachhead.** Engineering leaders who already follow the AI-adoption content. The launch post opens on that story, shows the before/after, closes with the one-line install and the landing URL, and ends with the disclosure that Voicestead wrote it.
2. **X thread.** The before/after plus the failed-replication story, tagged to the writing-tools and Claude communities.
3. **Show HN.** Title: "Show HN: Voicestead — a research-backed writing skill for Claude (with a public eval harness)." Lead with receipts and honest limits in the same breath — both are true, so say both.
4. **r/ClaudeAI and the newsletters.** Pitch The Rundown, Ben's Bites, TLDR AI with the before/after and the one-command install. One newsletter feature can outperform a month of posting.

First 72 hours, founder mode: answer every issue and comment fast, ship a small point release from real feedback within the week, and pin a "known limitations" issue. Being there, and being straight with people, counts for more in those first days than any launch post.

## Submissions & listings

An evidence checklist — every row carries a link or a dated status, no blank cells. Being indexable is most of the job: standard layout, clear description, topics set, and the crawlers find you.

- [ ] Confirm the placeholder sweep is green (`scripts/check_placeholders.py`) — owner resolved to `greenpioneersolutions`; the Studio MCP URLs land at S6.
- [ ] Bump `plugin.json` to `1.0.0` (from S8) and confirm `claude plugin validate` passes.
- [ ] Build the release asset: `python3 -m scripts.package_skill voicestead` → `voicestead.skill`.
- [ ] Tag `v1.0.0`, cut a GitHub Release with `voicestead.skill` attached, paste the CHANGELOG entry and the scorecard link into the notes.
- [ ] Flip the repo public.
- [ ] Set GitHub topics: `claude-skill`, `claude-code-plugin`, `agent-skills`, `writing`. Match the repo description to the skill description.
- [ ] Submit to Anthropic's plugin portal (`claude.ai/settings/plugins/submit`). Record the date and pending status; direct-install via the repo URL works while it's under review.
- [ ] PR to `travisvn/awesome-claude-skills` (fork, add to the right section, submit). Record the PR link.
- [ ] Submit to the `awesomeclaude.ai` directory. Record link and date.
- [ ] Verify the auto-indexers pick it up once public — `claudemarketplaces.com`, `claudeskills.info`, `skillsmp.com` discover public `SKILL.md` repos. Record the URL or "awaiting crawl" with a date.
- [ ] Submit / confirm listing on `agentskills.io`, the open Agent Skills standard the skill already follows — it widens the funnel beyond Claude to Codex, Cursor, and others.

## Post-launch care

The loop that keeps the skill honest after launch, and it runs forever.

Every accepted bug becomes an eval case *before* the fix. Write the failing case in `tests/cases.json` (mirror it to `skills/voicestead/evals/evals.json`), watch it fail, then fix the skill, then watch it pass. No fix lands without its case — the suite only grows in ways a failing case justifies.

On every major model release, re-run the full sweep and the golden set, then file a dated drift report under `docs/drift/`: what moved, which golden pieces changed verdict, which skill rules the new data challenges. Propose fixes only with evidence. Skills drift as models change, so this is not optional.

Community contributions merge only on the safe surfaces — eval cases, tell-list updates, format packs. Voice profiles and influence files stay personal by design and never enter the shared repo. Validate each case PR for format, scorecard delta, and slop before merging.

Keep the receipts current: refresh the published scorecard monthly and after any model-release re-run. Ship small, semver-bumped releases from real feedback — the update channel is a retention channel. Keep the "known limitations" issue accurate, and add real user feedback to the README as it arrives.

## What not to do

Don't launch before S0 — an untested writing skill dies on its first public counterexample. Don't post the repo bare with "check it out"; no demo, no one-line install, and no receipts means no adoption. Don't chase every channel at once — win LinkedIn, then widen. And don't optimize for the directories' metrics over the writing itself. The eval is the compass. Installs are the echo.
