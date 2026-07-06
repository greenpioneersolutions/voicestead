# Using Voicestead

Voicestead is a writing skill for Claude that turns rough thoughts into finished prose — one that sounds like you and refuses to invent a fact. This guide walks you through installing it, the three-minute setup that makes it yours, and how it behaves day to day.

The README is the front door. This is the manual you keep open while you work.

---

## Install

Three doors. Pick the one that matches how you use Claude, and copy the commands exactly.

**Door 1 — Claude Code plugin.** The cleanest option, and you get updates when the version bumps.

```
/plugin marketplace add greenpioneersolutions/voicestead
/plugin install voicestead@voicestead
```

Run both lines in your Claude Code session. That's the whole install.

**Door 2 — Copy the folder.** Also Claude Code, no marketplace involved. Run this from the repo root:

```bash
cp -r skills/voicestead ~/.claude/skills/
```

**Door 3 — Upload to claude.ai.** For Projects and the desktop app. Build the package first:

```bash
python3 -m scripts.package_skill voicestead
```

That produces `voicestead.skill`. In claude.ai, go to Customize → Skills and upload it there.

Same skill behind every door. Only the delivery changes.

---

## First run

You don't invoke Voicestead by name. It wakes up when you say something writing-shaped and stays quiet otherwise. Try any of these:

- "Help me tell my boss the launch is slipping to next Friday."
- "Make this sound less robotic." (then paste your draft)
- "Does this email sound okay?"
- "Rewrite this so it's tighter."

A pasted brain-dump works too. You don't have to say the word "write." If another human is going to read the words, the skill leans in; on pure coding or config tasks with no prose, it stays out of the way.

### The three-minute voice setup

The first time you write with the skill and it has no profile for you, it offers a short setup. It sounds like this:

> Want to do a 3-minute voice setup? Paste 2–3 things you've actually written — an email you liked, a post, a message. I'll build a profile so everything I draft sounds like you.

Here's the setup start to finish.

**1. You paste real samples.** Two or three pieces you actually wrote and liked. Range helps — a quick Slack message, a longer email, a post. The rawer and more real, the better; polished corporate copy teaches it the wrong voice.

**2. It reads you back to you.** From your samples it pulls a few things and shows them in one block before saving anything:

- **Sounds like** — two or three adjectives, each with evidence. Not "friendly" but "direct but warm — you soften the ask with 'no rush' but never soften the ask itself."
- **Signature moves** — the patterns that keep recurring. Opens lowercase on a dash. Fragments on purpose. Closes by handing back control.
- **Never says** — the words a model would reach for that you never do. "Circle back," "per my last," exclamation stacks.
- **Sample lines** — three to five verbatim lines that are unmistakably you. This is the calibration set every future draft gets checked against.

**3. You correct it, then say yes.** This is the part that matters most. Your one correction — "I'd never say 'reach out'" — is worth more than everything the skill inferred on its own. Fix what's off, then confirm, and it saves.

If you skip the setup, it doesn't nag. It asks once, and if you keep working it infers your voice from how you write to it in the chat, and asks for one real line only when the stakes are high.

Here's roughly what a finished profile looks like, so you know what you're confirming:

```markdown
Sounds like: direct, dry, warm underneath. Says the hard thing first, then makes
it easy to take. Never performs seniority — talks to reports like peers.

Signature moves:
- Opens lowercase, often on a dash — "hey — quick one"
- Fragments on purpose. "Short notice, I know."
- Closes by handing back control: "your call," "no rush."

Never says: "circle back," "per my last," "just wanted to," exclamation stacks.

Sample lines:
1. "hey — pushing the deploy to Monday. ci's flaky, not the code."
2. "Short version: we can hit the date or keep the scope. Not both."
```

---

## The four modes

The skill picks a mode from what you're asking for. You don't name them; knowing they exist just helps you ask well.

**Draft** — you have raw material and want a finished piece. You give the brain-dump or the bullets; it shapes them, delivers the draft, then names its moves in a line or two. It never praises its own work.
> "Here are my notes from the incident — turn them into a postmortem summary for the team."

**Improve** — you wrote something and want it better. It guards your voice hard, rewrites, and tells you what it changed. The rewrite is mostly cleaning, not rebuilding.
> "Tighten this paragraph without making it sound like a robot wrote it."

**Extract** — the thing you want written lives in your head, not on the page. A process, a runbook, a handoff. Here it interviews you first, one question at a time, structures second, and drafts last.
> "Help me document how we do our release process — I've never written it down."

**Review** — you want feedback, not a rewrite. It leads with the most specific thing that's working (a real line you wrote, not generic praise), then the sharp questions, then fixes in priority order. It won't rewrite unless you ask.
> "Read this cover letter and tell me what's weak — don't rewrite it."

Across all four, it infers what it can and asks only what it can't, at most three questions, and only when the answer would actually change the writing.

---

## Making it yours

Out of the box, Voicestead writes like a clean, plain human. Good, but generic. Two files close the gap between "sounds human" and "sounds like you," and you build them once.

### The voice profile

This is the setup above — the anchor. It captures how you sound today: your sentence lengths, your punctuation habits, whether you open with a lowercase "hey." Once it exists, the skill edits toward you instead of toward generic polish. Your profile outranks every general style rule in the skill. If your voice loves em-dashes, the em-dashes stay.

### Influences

The voice profile is who you are now. Influences are who shaped you and who you're reaching toward. Teach them two ways.

**Teach it who shaped you.** Ask for the influence interview and it walks you through a handful of questions — the writers you most admire and why, a piece you can quote from memory, whose writing makes you jealous, what you want a reader to feel when they finish. It stores only what you actually say. It never invents an influence.

**Have it study a writer.** Point at a book, a speech, an essay, or an author, and it studies them — either by researching if it has the tools, or by asking you to paste a few representative passages. Then it pulls out what makes them work: their rhythm, how they anchor abstractions in real things, how they open and close.

The rule under all of it: **moves, not fingerprints.** It borrows the technique that makes a writer land — the way they drop a short sentence after a long build — and it never produces recognizable imitations of them or name-drops them at your reader. Influences season the voice; they never replace it. If a draft starts sounding more like Hemingway than like you, the blend failed and it pulls back to your profile.

---

## Where your files live

No magic persistence. Your profile and influences are plain files the skill rereads each run — yours to open, edit, or delete. Where they sit depends on your surface.

**Claude Code.** The skill writes `voice-profile.md` and `influences.md` to a place it can reread — the skill folder, or your project's `.claude/` directory. It tells you the path, and the file loads on its own next session. Working with a team? Each writer gets their own `voice-profile-<name>.md`.

**claude.ai and desktop.** Nothing persists silently here. The skill hands you the finished profile and you paste it into your Project's instructions or add it as Project knowledge, so it's in context next time. Skip that step and it won't carry over — the skill will tell you so plainly rather than pretend.

Either way, the file is the source of truth. Portable, reviewable, and it never leaves your control.

---

## Limits

Worth knowing before you lean on it.

It can't confirm it sounds like *you* — only you can. A profile gets it close, but that last call is one no tool makes for you.

It won't fill empty space with invented specifics. Hand it a draft with no real numbers, names, or moments and it flags the gap and asks you for one detail rather than fabricating it. That can feel like it's doing less than a tool that happily makes things up. That restraint is the point.

It matches effort to stakes. A routine two-line note gets a fast pass, not full ceremony. The deep self-check is for writing that matters.

---

## FAQ

**Does it actually sound like me?**
Out of the box, no — it sounds like a clean, plain human, which is good but generic. It sounds like you once you give it a voice profile from your real writing. That step is the whole difference, and it takes about three minutes.

**Will it invent facts to make my writing better?**
No, by design. When a draft has no real specifics, it flags the gap and asks you for one. It never fabricates a number or a quote. This is enforced, not just hoped for — the test harness fails any output containing a figure that wasn't in your input.

**Is my voice profile shared with anyone?**
No. It's a local file on your machine in Claude Code, or a document inside your own Project on claude.ai. It stays in your control. Contributions to the project deliberately live on shared surfaces only — format packs, test cases, tell-lists — never personal voice files.

---

## More

- Curious whether it works? The project answers that with a test harness rather than adjectives — see [`tests/TESTING.md`](../tests/TESTING.md). The public scorecard reports a blind win rate against Claude with no skill loaded; the target is at least 70%, and no number goes in the table until it's measured on real writing.
- The skill's own rules and reasoning live under [`skills/voicestead/references/`](../skills/voicestead/references/).
