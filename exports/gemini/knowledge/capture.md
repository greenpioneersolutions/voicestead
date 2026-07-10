# Capture — Getting Knowledge Out of Your Head

Load this for Extract mode: documentation, process write-ups, runbooks, onboarding guides, handoffs, "how we do X here," or any time the knowledge lives in the user's head and the goal is a document that works when they're not in the room. The defining test for everything in this file: **could someone competent do this at 2am, alone, without calling you?**

## Why this is its own mode

Drafting assumes the material is already on the page or in the prompt. Capture doesn't — the hardest part is extraction, and the expert is the worst-placed person to do it alone, because the curse of knowledge hides exactly the steps that matter ("everyone knows you restart the service after"— no, they don't). So the workflow inverts: **interview first, structure second, draft last.**

## Step 1 — Interview (pull it out)

Act as the intelligent novice. Ask one question at a time, in roughly this arc:

1. **Frame:** "Who will use this doc, and in what moment?" (Mid-task? Learning? Looking something up? This decides the doc type below.)
2. **Happy path:** "Walk me through it start to finish, as if I'm doing it live." Capture exact commands, names, links, owners — not "update the config" but *which file, which line, who approves*.
3. **The tacit layer — where the real knowledge hides:**
   - "What usually goes wrong, and how do you know?"
   - "When would you NOT do this / what's the exception?"
   - "What do you check before you trust it worked?"
   - "What would a smart new person get wrong here?"
   - "Who do you call when it breaks, and what do you tell them?"
4. **Boundaries:** "Where does this process start and stop? What's someone else's job?"
5. **And what else?** — ask it until they say "that's actually everything."
6. **Exact names:** confirm spellings of every system, tool, and person mentioned — the 2am reader searches by exact string, and a name you guessed at is a dead end.

A brain-dump counts as answers: if they paste a messy mind-map of thoughts, mine it against this list and ask only for the gaps.

## Step 2 — Pick the doc type (Diátaxis, translated)

Four kinds of doc answer four different needs; the number-one documentation mistake is mixing them in one page. Pick before structuring:

- **How-to / runbook** — for someone *at work, mid-task*: numbered steps, exact commands, no theory. (Most workplace process docs are this.)
- **Reference** — for looking facts up: tables, settings, owners, links. Structured like the thing it describes; no narrative.
- **Explanation / decision doc** — for understanding *why it's this way*: context, trade-offs, the options rejected. This is the doc that stops the next person from "fixing" a deliberate choice.
- **Tutorial / onboarding** — for a learner's first time through: a guided, guaranteed-success walkthrough of one concrete example. Minimal explanation inline; link out for depth.

If the user's material wants to be two of these, make two short docs and link them — a runbook with a "Why it works this way" paragraph linked at the bottom beats a hybrid that serves neither reader.

## Step 3 — Structure and draft

Default skeleton for a how-to/runbook (adapt, don't worship):

1. **Title as a task** ("Deploy a hotfix to production," not "Deployment").
2. **One-line purpose + when to use this** (and when *not* to).
3. **Before you start** — access, prerequisites, the state things should be in.
4. **Steps** — numbered, one action each, exact names/commands/owners, expected result after each ("you should see…" is what makes it followable alone).
5. **If it goes wrong** — the failure modes from the interview, each with its check and fix.
6. **Escalation** — who to contact, with what information.
7. **Owner + last-verified date** — an unowned doc is already rotting.

Style rules on top of Voicestead's quality bar: here, uniform and plain *wins* — this is the genre where the rhythm rules stand down (per the guardrails). Write steps as imperatives. Never bury an action in a paragraph. Specifics outrank elegance: the doc is a tool, not prose.

## Step 4 — The survivability pass

Before delivering, audit as the 2am stranger:

- Every acronym and internal name defined or linked at first use.
- No step that assumes unstated knowledge ("configure it appropriately" is a hole, not a step).
- Each step verifiable — the reader can tell they did it right.
- The exceptions and failure modes made it in (if the interview surfaced them and the doc lost them, the doc failed).
- Someone is named as owner.

Then say what you did: "Structured as a runbook; flagged two gaps you may want to fill: [X], [Y]." Gaps stay visible as bracketed placeholders — never smoothed over, per the Truth rule.
