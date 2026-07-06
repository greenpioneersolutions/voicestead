# Voicestead

**A lean writing skill for Claude that makes your writing land — in your voice, shaped by your influences, without the AI tells.**

Not only for your writing — for your inspiration.

It does the dishes. You keep the art.

## What it is

Voicestead turns rough thoughts into finished writing that reads as genuinely human: emails, status updates, posts, proposals, hard messages — anything another person will read. It's built on three mental models (name the one job, point first, say it to one person), a persuasion module distilled from the direct-response canon and the influence classics (Sinek, Carnegie, Voss, Goleman), and an anti-slop discipline grounded in what actually distinguishes human prose from machine prose (rhythm variance, specificity, voice) rather than brittle banned-word lists.

It's deliberately small. The skill ecosystem has thousands of coding skills and no general writing standard — because voice and judgment don't generalize. Voicestead's bet: a lean core anyone can adopt, made *yours* through a voice profile built from your real writing and evals run on your real work.

## Structure

```
voicestead/
├── SKILL.md                    # the core: modes, mental models, quality bar, self-check
├── references/
│   ├── tells.md                # full AI-tells catalog, by category, with fixes
│   ├── persuasion.md           # so-what chain, argument shape, audience calibration
│   ├── influence.md            # purpose, goodwill, tactical empathy, EI (Sinek/Carnegie/Voss/Goleman)
│   ├── formats.md              # per-medium defaults (email, update, post, proposal…)
│   ├── coaching.md             # grow-people writing: seven questions, GROW, mentor vs coach
│   ├── capture.md              # Extract mode: interview-first documentation, Diátaxis, runbooks
│   ├── voice.md                # the 3-minute voice capture flow + profile template
│   ├── inspiration.md          # the influence system: interview, study pipeline, influences.md storage
│   ├── craft-notes.md          # sources: Pinker, Smart Brevity, Orwell → Ishiguro
│   └── science.md              # the research evidence base (fluency, narrative, receptiveness…)
├── evals/
│   ├── eval-guide.md           # how to test it on YOUR writing before trusting it
│   ├── evals.json              # native eval mirror (kept in sync with tests/cases.json)
│   └── test-cases.md           # 25 smoke tests with pass criteria
└── examples/
    └── before-after.md         # worked examples across modes
```

## Install

**Claude Code:** copy the `skills/voicestead/` folder into `~/.claude/skills/` (or your project's `.claude/skills/`).

**Claude.ai / Cowork:** upload the `.skill` package, or paste `SKILL.md` into a Project's instructions (add reference files as Project knowledge).

## First run

1. Say anything writing-shaped: "help me email my boss that the launch is slipping."
2. Accept the 3-minute voice setup when offered — paste 2–3 real samples of your writing. This is the step that makes the output sound like *you*.
3. When you're ready, run the influence interview ("teach yourself who shaped my writing") — it stores an influences.md alongside your voice profile.
4. Before trusting it broadly, run `evals/eval-guide.md`: your real pieces, with and without the skill, judged blind.

## Principles (the short version)

True > specific > clear > rhythmic > clean — in that order. If it's already good, it says so and stops. Never invents a fact. Moderation, not prohibition (em-dashes and adverbs are tools; overuse is the tell). Voice is a persona, not a rule list.

Full sourcing and design rationale: `references/craft-notes.md`.

## License

MIT — see LICENSE.
