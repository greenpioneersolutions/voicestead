# Architecture

How Voicestead is built, and why it's built this way. Read this if you want to understand the design or contribute.

Voicestead is two pieces in one repository: a writing skill for Claude, and the eval harness that keeps the skill honest. The skill ships to users; the harness never does. Almost every design choice below follows from one bet about how a writing skill earns its keep — so start there.

## The design bet: lean core, progressive disclosure

A skill loads into the model's context every time it triggers. That cost is real and it recurs on every message. So the core question isn't "what could we teach the model about writing" — it's "what must load every time, versus what can wait until the job actually needs it."

Voicestead answers with progressive disclosure. Only `SKILL.md` — the core, kept under about 100 lines — is always in context. Everything else lives in `references/` and loads on demand: the persuasion module when the user is pitching, the tells catalog on a humanizing pass, the capture playbook only in Extract mode. A routine two-line note pays for the core and nothing more. A high-stakes proposal pulls in one or two references and pays for those too, but only then.

That structure is the spine of the whole design, not an optimization bolted on at the end. It lets the skill hold real depth — ten reference files, a persuasion canon, a coaching arc, a documentation framework — without making every trivial request carry that weight. The core's own economy rule makes the discipline explicit: load at most the one or two references the job needs, never all of them, and match effort to stakes.

The bet behind the bet: a general-purpose writing skill can't win by being big. What makes writing good — voice, judgment, the specific point — is exactly what can't be pre-packaged and handed to everyone. So Voicestead stays lean and generic at the core, and becomes *yours* through a voice profile and your own eval results. Lean-and-personal over big-and-generic.

## Skill anatomy

`SKILL.md` is the whole always-loaded surface. It does five things, in order.

### The four modes

Every request resolves to one of four jobs, picked at Step 0, because drafting, improving, and reviewing are genuinely different work and collapsing them causes specific failures.

- **Draft** — the user gave raw material (a brain-dump, bullets, "help me tell my boss X") and wants a finished piece. Shape it, deliver it, name the moves in a line or two. Never praise your own draft.
- **Improve** — the user gave their own draft and wants it better. Preserve their voice ruthlessly, then name the moves.
- **Extract** — the knowledge is in their head, not on the page: a runbook, a process, a handoff. Interview first, one question at a time; structure second; draft last.
- **Review** — they want feedback, not a rewrite. Lead with the most specific thing that works, then the sharp questions, then fixes in priority order. Don't rewrite unless asked.

The split exists to prevent two concrete bugs. A single combined mode invites sycophancy — the model drafting *and* grading its own output tends to praise it. And it produces wrong Review behavior, rewriting when the user only wanted to be told what to fix.

### The three mental models

Under the modes sit three ideas that shape every piece:

1. **Name the one job — and the one reader.** Who reads this, what should they think or feel or do, and what single idea must land? If that won't fit in one sentence, the thinking isn't finished. This carries the curse-of-knowledge check: list what the reader doesn't know that the draft silently assumes.
2. **Point first, then why it matters.** Attention is highest at the top and leaks from there. Lead with the answer, the ask, or the news.
3. **Say it to one person.** Write the way you'd say it out loud to one smart person across a table. Plain words are clearer, and they're also more honest — fancy words fool the writer into thinking they've said more than they have.

### The priority-ordered quality bar

Five rules, ranked, so that when two collide the higher one wins and small rules can't crowd out big ones: **true > specific > clear > human-rhythm > clean.** Truth is first on purpose — never invent a fact, quote, number, or source; a missing figure becomes a flagged placeholder. Above all five sits one restraint rule: *if it's already good, say so and stop.* That rule is the guard against checkbox editing, which is its own kind of slop.

### The countable self-check

Before delivering, the skill runs an eight-step check written to be counted, not felt. Does the first sentence state the point? Scan sentence lengths — three in a row within a few words of each other means break one or merge two. Count triads. Sweep the tells by category. Check the draft against the voice profile. The checks are countable by design, because "make it sound more human" is a vibe and a vibe can't be verified — but a coefficient of variation or a triad count can.

### The references map

`SKILL.md`'s Step 1 is a routing table from job to reference. The current set:

- `persuasion.md` — the argument's structure, for pitching or pushing a decision.
- `influence.md` — the human underneath an ask, a disagreement, or bad news.
- `formats.md` — email, status update, LinkedIn post, proposal, exec summary.
- `tells.md` — the full anti-slop catalog, for editing and humanizing passes.
- `coaching.md` — replies to someone you lead or mentor; 1:1 prep; growth feedback.
- `capture.md` — Extract mode's documentation playbook.
- `inspiration.md` — the influence system.
- `voice.md` — the voice-profile setup.
- `science.md` — the evidence base, loaded only when someone asks *why*.
- `craft-notes.md` — the lineage and the design rationale.

If none clearly applies, the skill proceeds on the core alone.

## The anti-slop approach

Cutting AI tells is the most visible thing the skill does, so it's worth being precise about the method, because the obvious method is the wrong one.

**Categories, not kill-lists.** A static banned-word list ages, throws false positives, and invites synonym-swapping that changes nothing where it counts. "Robust test coverage" in an engineering doc is correct; "a robust solution" in a sales email is a tell. The same word, judged by context. So the tells catalog is organized as categories with examples — reflexive fancy words, zombie nouns, empty intensifiers, formula structures, false agency — under one durable test: *would this writer say this word, in this sentence, out loud?*

**Moderation, not prohibition.** Em-dashes, adverbs, passive voice, semicolons — these are tools a real writer uses, sparingly and on purpose. Overuse is the tell, not the tool. A blanket ban just trades one robotic style for another.

**Rhythm is the real signal.** The loudest tell isn't any word; it's the shape. Human prose swings — a long winding sentence, then a short one — while model prose is metronomic. Detection research names this variance "burstiness," and it's among the clearest measurable separators of human from machine writing. Its companion, the rule-of-three reflex — AI grouping items in threes, sentence after sentence — is a pattern readers feel before they can name it. The skill targets both directly. And it carries the honest caveat: technical and legal genres are *supposed* to be uniform, so low burstiness there is correct, not a defect.

## The voice and influence system

The core ships identical for everyone. Two optional files make it personal, and they're built once from real material.

**Voice profile.** "Sound more like me" prompts demonstrably fail; structured profiles built from real samples work. So the skill treats voice as a stored persona: paste two or three genuine samples of your writing and it learns your defaults — sentence length, punctuation habits, whether you open with a lowercase "hey" — then edits toward you rather than toward generic polish.

**Influences.** A separate mechanism captures who shaped you and who you're reaching toward. The governing rule is *learn the move, never the fingerprint.* An influence card distills a writer, book, or speech into two or three operational moves — "lands the short sentence after the long build" — never stored passages, never pastiche. This is also where the anti-slop rules and the influence rules reconcile: a card can license a deliberate device (a Churchillian triad) that the tells list otherwise restricts as a tic, because the moderation rule already says the difference between a device and a tic is whether it's used on purpose. The voice profile always outranks; influences stretch the voice, they never replace it.

**Honest storage on both surfaces.** There is no magic persistence. In Claude Code the skill writes `voice-profile.md` and `influences.md` and rereads them each run. On claude.ai you add the same two files to your Project knowledge. They're plain files you can inspect, edit, or delete, and they never leave your control — contributions to the project deliberately stay on shared surfaces (formats, eval cases, tell-lists), never personal voice files.

*(A future connector, Studio — an MCP server at `mcp.voicestead.ai` — would add persistent voice memory across sessions, with tools to log drafts, record verdicts, and score against your history. The domain is set; it's in development and not yet shipped, and the beta isn't open. For now, storage is the plain files above.)*

## How it's tested

Prose is hard to test for two reasons a normal suite never faces: the output is non-deterministic (same prompt, different text each run), and "good" is subjective and multi-dimensional (voice, clarity, persuasion, rhythm, no slop). You can't diff prose against one correct answer. So the harness doesn't try — it uses three tiers, each catching a different class of failure at a different cost.

**Tier 1 — deterministic checks** (`tests/checks/`). Free, instant, and run on every push with no API key. A counter or a regex catches mechanical slop: a buried point, metronomic rhythm (the burstiness coefficient), one triad too many, a tell-word, a length overrun. Each check carries a severity. *Hard* checks are gates that map to the skill's non-negotiables — `no_invented_numbers` is the most important one, failing any output that contains a figure absent from the input. *Soft* checks are signals that feed the score and hand candidates up to the judge; `tell_flags` is soft on purpose, because a static list can spot the word "robust" but can't tell whether the context justifies it.

**Tier 2 — LLM-as-judge** (`tests/judge/`). A second Claude scores the subjective dimensions against an anchored 1–5 rubric, structured as JSON so results aggregate. The design respects the known failure modes: the headline metric is *pairwise* (with-skill versus without-skill, blind and order-randomized) because judges are far more reliable at "is A or B better?" than at "is this a 4 or a 5?"; every judgment runs several times and takes the median; and the harness actively mitigates position, verbosity, and self-preference bias. The standing rule is Goodhart's — don't optimize the skill to please the judge; the judge is a proxy for a good reader, not the target.

**Tier 3 — human review** (`tests/golden/`). One question stays human forever: *does it sound like me?* A judge can approximate "sounds human"; it can't confirm it sounds like *you*. Your ship/don't-ship and me/not-me verdicts get appended to the golden set, which does double duty — a regression anchor for future versions, and few-shot calibration that pulls the judge toward your taste.

**The cases.** `tests/cases.json` holds 25 cases in an extension of Anthropic's evals.json shape (each adds mode, references to load, deterministic checks, rubric dimensions, hard gates, and a baseline-compare flag). Most are task cases; a few are metamorphic — they assert a property across a transformation rather than grading one output, like "feeding already-clean text through Improve must not lengthen it beyond its declared bound (10% for case 6)." The golden set adds five real fixtures in `tests/golden/raw/` — an actual persuasive email, a release update, a LinkedIn post, a hard return-to-office message, and a brain-dump.

**The headline metric** is the with/without benchmark (`tests/run_eval.py`): on the same prompts, does Claude-with-Voicestead beat Claude-without, judged blind? The target is a win rate consistently at or above 70%, with zero hard-gate failures and zero previously-shipping golden cases regressed. That scorecard is currently **pending** — it publishes the day it's run on real writing, judged blind, and not before. A writing skill that invents its own results is the exact thing this one exists to stop.

**What CI runs** (`.github/workflows/`), split by cost and determinism:

- `eval.yml` has three jobs. `check` runs on every push and PR — free, no key, seconds: the repo-structure guard, the Tier-1 checks against the committed corpus, a *dogfood* gate (the skill's own docs must pass the checks it enforces on everyone else), the check unit tests, a placeholder sweep, and a build of `voicestead.skill` as an artifact. `evaluate` runs on manual dispatch and a weekly cron, needs the `ANTHROPIC_API_KEY` secret, and runs the full generate→judge→benchmark loop. `golden` runs on dispatch — the S0 gate, the with/without benchmark on the real fixtures.
- `release.yml` fires on a `v*` tag: re-runs the free gates, fails on any leftover placeholder, builds the `.skill`, and cuts a GitHub Release.
- `pr-eval.yml` posts one sticky check-summary comment on each PR.

The pattern generalizes to any LLM skill: cheap deterministic checks guard every change, expensive model-graded evals gate releases, and a human calibrates and makes the final call.

## Repo and plugin layout

The repository root *is* the plugin root. The skill, the harness, and the manifests sit side by side, the way a normal library keeps `src/` next to `tests/`.

```
skills/voicestead/     the skill — SKILL.md, references/, evals/, examples/.
                       This, and only this, is packaged and installed.
tests/                 the three-tier harness. Dev-only; never shipped.
.claude-plugin/        plugin.json + marketplace.json (the one-command install).
scripts/               package_skill.py, check_placeholders.py.
.github/workflows/     CI.
docs/                  these docs.
```

The load-bearing rule: **`tests/` and `.github/` are never loaded by Claude at runtime.** They're development infrastructure that lives alongside the skill, not part of it. `python3 -m scripts.package_skill voicestead` zips only `skills/voicestead/` into `voicestead.skill`. That separation is what lets the harness be as heavy as it needs to be — 25 cases, a judge, a golden set, experiments — without adding a byte to what the user installs.

There are three install doors, each hitting the same skill through a different delivery:

1. **Claude Code plugin** — `/plugin marketplace add greenpioneersolutions/voicestead` then `/plugin install voicestead@voicestead`. You get version updates.
2. **Copy the folder** — `cp -r skills/voicestead ~/.claude/skills/`.
3. **Upload to claude.ai** — `python3 -m scripts.package_skill voicestead` builds the `.skill`; upload it under Customize → Skills.

The plugin manifests validate against `claude plugin validate`. The project is at version 0.10.0, pre-launch; v1.0.0 is the launch target once the S0 eval and the S8 regression pass. It's MIT-licensed, owned by Green Pioneer Solutions.

## The evidence base

The rules aren't invented. They trace to a lineage — Pinker's classic style and the curse of knowledge, Orwell on cutting every word that can be cut, Smart Brevity's short lead and "why it matters," the persuasion canon, Voss and Carnegie and Goleman underneath the influence module, Diátaxis under the documentation one. `craft-notes.md` records that lineage and the design rationale for a human reader; the skill runs fine without it.

`science.md` holds the scholarly base — clarity and fluency, concreteness, narrative transportation, the misread-tone effect, conversational receptiveness, values reframing. Two disciplines make it trustworthy rather than decorative. First, every entry is marked by verification status: ✔ verified at source, or ◇ training-sourced and re-verify before quoting numbers publicly. Second, it keeps a *failed replication* on purpose — a 2010 finding on expert hedging that a 2024 registered replication couldn't reproduce — as a worked example of why the project verifies before it encodes. For a skill whose first rule is truth, hiding the study that didn't hold up would be the tell.

And the whole edifice defers to one arbiter. These studies are averages from contexts that aren't yours; effects are directional tendencies, not laws. So when a citation and your own tested results disagree, the eval wins. The research sets the priors; your writing, judged blind, settles them.

## Multi-platform exports

The skill is the source of truth; other platforms are generated from it, never forked.

```
skills/voicestead/SKILL.md + references/   canonical
        │
exports/core.md                            hand-authored ≤8k distillation, SHA-256-sealed to SKILL.md
scripts/build_exports.py                   mechanical assembler
        │
exports/{chatgpt,gemini,agents}/           committed, paste-ready bundles
```

`core.md` is the only maintained derivative. It opens with a seal comment recording the hash of the `SKILL.md` it was condensed from; `build_exports.py --check` (run in CI) fails if `SKILL.md` changed without `core.md` being re-condensed and re-sealed (`--reseal`). Everything else under `exports/` — the two `instructions.txt`, the `knowledge/` copies, and `agents/AGENTS.md` — is regenerated and diffed against the committed tree on every push, so a stale export can't merge. The static `SETUP.md` files and `README.md` are authored by hand and covered by the link checker.

Flat surfaces lose author-controlled progressive disclosure (references become retrieval or repo links) — documented honestly in [`PLATFORMS.md`](PLATFORMS.md).
