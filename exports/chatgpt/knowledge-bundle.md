# Voicestead reference library (combined)

Every Voicestead reference in one file, so you can upload a single knowledge document instead of ten. If your platform retrieves better over separate files, upload the individual files in `knowledge/` instead.

---

# capture.md

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

---

# coaching.md

# Coaching & Mentoring — Writing That Grows People

Load this when the writing involves developing a person: replying to someone you lead or mentor, prepping a 1:1, giving feedback meant to grow (not just correct), a career conversation, responding to "what should I do?", or when the user is writing to their own mentor and needs to ask well. Also load it when the user is thinking through their own problem — the questions work on yourself.

## The stance: tame the advice monster

The reflex when someone brings you a problem is to solve it. Resist. Stay curious a little longer; rush to advice a little more slowly. Every problem you solve for someone teaches them to bring you the next one — that's how leaders become bottlenecks and people stop growing. The behavior change is simple to say and hard to do: a little more asking, a little less telling.

Two roles, know which you're in:
- **Mentor** — you've been where they want to go. You share the map: what you did, what it cost, what you'd do differently. Experience, offered honestly, never forced.
- **Coach** — you help them draw their own map. Questions, not answers. They own the conclusion, so they own the action.

Most real conversations blend both. Default to coach; earn the right to mentor by asking first. And the quiet win: you don't need the title of "mentor" for either — one genuinely good question in an ordinary message does the job.

## The seven questions (Bungay Stanier)

The proven core. Use one at a time — never stack them into an interrogation.

1. **Kickstart:** "What's on your mind?" — opens the real conversation without steering it.
2. **AWE:** "And what else?" — the first answer is never the only one, and rarely the best. Ask it two or three times.
3. **Focus:** "What's the real challenge here *for you*?" — cuts from the surface problem to the actual one. The "for you" matters; you can only coach the person in front of you.
4. **Foundation:** "What do you want?" — surprisingly rarely asked, surprisingly clarifying.
5. **Lazy:** "How can I help?" — forces a direct, clear request instead of you guessing (and over-helping).
6. **Strategic:** "If you're saying yes to this, what are you saying no to?" — makes the trade-off visible.
7. **Learning:** "What was most useful for you?" — asked at the end; people learn when they recall, not when they're told.

For a longer or more structured conversation, GROW gives the arc: **G**oal (what do you want?), **R**eality (what's actually happening?), **O**ptions (what could you do?), **W**ill (what will you do, by when?). The seven questions slot into it naturally.

## The rules that keep it honest

- **No advice with a question mark attached.** "Have you tried X?" is telling, disguised. If you're going to advise, advise openly ("here's what I did in that spot"); if you're asking, ask something you don't know the answer to.
- **One question per message.** A written list of five questions reads as a quiz, not care. Pick the one that matters most right now.
- **Genuinely open beats leading.** A leading question steers to your answer; an open one hands them the pen. "What options do you see?" not "Don't you think you should…?"
- **Acknowledge before you ask.** A question that lands after real acknowledgment ("That's a genuinely hard spot — three good options and only one yes") feels like partnership. The same question cold feels like deflection.
- **Silence is allowed.** In writing, that means: ask the question and *stop*. Don't answer it yourself in the next paragraph.
- **Follow-ups are the highest-value questions.** Research on question-asking finds follow-up questions — built on what they just said — do the most to make people feel heard and liked. "You said the real blocker is the review queue — what's keeping it long?" beats a new question from your list.

## How this shows up in Voicestead's modes

- **Drafting a reply to someone they develop** (a report, a mentee, a struggling peer): resist solving it in the message. Acknowledge specifically, offer what only the writer can offer (context, air cover, one piece of hard-won experience if it's earned), then end on the one question that moves them forward — usually Focus or Foundation.
- **Prepping a 1:1 or career conversation:** give them a spine, not a script — an opener, the two or three questions that fit this person and moment, and the trap to avoid (their advice monster's favorite move).
- **Feedback meant to grow:** pair the specific observation with a forward question. "The demo ran long and the decision slipped — what would you cut next time?" beats a paragraph of prescriptions.
- **Writing up to their own mentor:** help them ask a mentor-worthy question — specific situation, the decision they face, what they've already tried, and the one thing they want the mentor's experience on. "Can I pick your brain?" wastes a mentor; a sharp question honors one.
- **Self-coaching** (journaling, a decision doc, thinking out loud): run them through the seven on the page. The questions work solo.

The tell that this file should fire: the user's real goal is the *person's growth*, not just the message's outcome. When the goal is purely persuasion or information, use `persuasion.md` / `influence.md` instead — and when it's both, lead with influence, close with one good question.

---

# craft-notes.md

# Craft Notes & Sources

For the human, and for Claude when the user asks *why* a rule exists. The skill runs without this file.

## The lineage

- **Steven Pinker, *The Sense of Style*** — "classic style": the writer directs the reader's gaze at something in the world; writer and reader are equals; good writing makes the reader feel smart. The **curse of knowledge** — failing to imagine what the reader doesn't know — as the single best explanation of why good people write bad prose. Zombie nouns. Compulsive hedging (trust readers to fill in the caveats). Grammar as the *least* important part of good writing.
- **Smart Brevity (Axios — VandeHei, Allen, Schwartz)** — the commercially proven workplace-comms system: strong short lead (one memorable sentence), "why it matters" immediately after, then optional depth ("go deeper") so nobody is forced to read everything. Their updates run ~40% shorter with nothing essential lost. Creed: "Brevity is confidence. Length is fear."
- **George Orwell, "Politics and the English Language"** — cut every word that can be cut; never a long word where a short one works; clichés are ready-made phrases that think your thoughts for you.
- **Ernest Hemingway** — the iceberg: omit what you know and the reader still feels it; never omit what you don't know — that just leaves hollow places.
- **James Baldwin** — the goal is a sentence "clean as a bone"; first drafts are overwritten and the rewrite is mostly taking things out.
- **Joan Didion, "Why I Write"** — arrangement is meaning: shifting a sentence's structure alters what it says as surely as moving a camera changes the shot. End on the strong word.
- **Paul Graham, "Write Like You Talk"** — read it aloud and fix everything that isn't conversation; plain words are honest, fancy ones fool the writer; informal spoken language puts you ahead of 95% of writers.
- **Margaret Atwood** — every written piece is a score for a speaking voice; reading aloud disallows cheating.
- **Kazuo Ishiguro** — restraint: understatement carries more weight than melodrama; never heighten emotion for effect.
- **The persuasion canon (Ogilvy, Schwartz, direct-response)** — the "so what?" chain (descended from conversion copy's So-What test); benefits over features; specifics over claims; the situation→stakes→answer→proof→ask shape as a de-marketed descendant of PAS/PASTOR; meet the reader at their level of awareness.
- **Simon Sinek, *Start With Why*** — the golden circle (why → how → what); people are moved by purpose, not features; inspiration over manipulation. Feeds influence.md's purpose-first opening.
- **Dale Carnegie, *How to Win Friends and Influence People*** — people are creatures of emotion and ego; don't criticize, begin friendly, frame asks in the other's interest, let conclusions be theirs, give sincere and specific appreciation. Feeds influence.md's goodwill section and the Review-mode lead-with-a-strength rule.
- **Chris Voss, *Never Split the Difference*** — tactical empathy; label the emotion, run the accusation audit, aim for "that's right" over "you're right," prefer calibrated how/what questions. Feeds influence.md's tactical-empathy section for asks and hard messages.
- **Daniel Goleman, *Emotional Intelligence*** — self-awareness, self-regulation, empathy, relationship management; manage your own state before the reader's, and treat every message as a deposit or withdrawal on the relationship. Feeds influence.md's EI section and the never-send-hot rule.
- **Michael Bungay Stanier, *The Coaching Habit*** — tame the advice monster: stay curious longer, ask more, tell less; the seven essential questions (What's on your mind? / And what else? / What's the real challenge here for you? / What do you want? / How can I help? / What are you saying no to? / What was most useful?); no advice with a question mark attached. With the GROW arc (Goal, Reality, Options, Will), feeds coaching.md.
- **Daniele Procida, Diátaxis** — the documentation framework used by Django, Canonical, and Cloudflare: four doc types (tutorial, how-to, reference, explanation) for four reader needs, and the #1 rule that mixing types in one page serves no one. Feeds capture.md's doc-type picker.

## Why "burstiness" is in the skill

The rhythm rules map to what AI-detection research calls **burstiness** — variance in sentence length and structure. Human writing swings; model writing is metronomic, and studies find that variance is the single clearest measurable difference between the two. The companion metric, **perplexity**, is word-level predictability: humans pick surprising words for reasons of memory, humor, and context; models pick the statistically likely one. The skill's goal isn't beating detectors — varied rhythm and chosen words are simply what human writing is. Caveat, encoded in the guardrails: technical and legal genres are *supposed* to be uniform; low burstiness there is correct.

The rule-of-three callout is the project owner's own observed catch, independently confirmed by detection research: AI reflexively groups items in threes, sentence after sentence, and readers feel the pattern before they can name it.

## Design decisions

- **Lean core + on-demand references, not a monolith.** Progressive disclosure keeps the always-loaded cost low while allowing depth. The core stays under ~100 lines; depth loads only when the job calls for it.
- **Categories, not kill-lists.** Static banned-word lists age, cause false positives, and invite synonym-swapping, which changes nothing at the rhythm level where detection actually happens. The durable test is contextual: would this writer say this word, here, out loud?
- **Moderation, not prohibition.** Em-dashes, adverbs, and passive voice are tools; overuse is the tell. Blanket bans trade one robotic style for another.
- **Modes.** Drafting, improving, and reviewing are different jobs. Collapsing them created sycophancy risk (praising one's own draft) and wrong review behavior.
- **A priority order** (true > specific > clear > rhythmic > clean) so small rules can't crowd out big ones.
- **The skill's own voice is a design choice, not an accident.** Research on prompt sensitivity says tone barely moves task quality on frontier models (politeness studies flip direction between papers), while mechanical corruption reliably hurts — typos measurably degrade even frontier models, and our own YAML-colon bug proved mechanics can hard-fail at the parse layer. So this skill's prose is standardized: second-person imperative, informative not persuasive, plain register, mechanically impeccable. Two reasons beyond robustness: the skill's prose doubles as a few-shot style exemplar for outputs, and a plain instruction voice keeps the *voice profile* as the only style signal — persuasive or ornate instruction prose risks leaking into drafts. Contributors should match this register.
- **Economy over ceremony (and honest numbers).** The 2026 wave of "token-saving" skills is mostly one idea — tell the model to be terse — plus real architecture: keep the always-loaded file small and load depth on demand. Marketed savings claims run high; the one repo that measured honestly found far smaller output reductions, and noted the instruction file itself costs input tokens on every message. The durable wins Voicestead adopts: progressive disclosure (already core), load-only-what-the-job-needs, effort matched to stakes, and no output ceremony. Generic "be smarter" incantations are left out; rules should target actual failure modes, not vibes.
- **The restraint rule** ("if it's already good, say so and stop") as the guard against checkbox editing — which is its own kind of slop.
- **Influences as moves, not fingerprints.** The influence system (inspiration.md) stores who shaped the writer and distills each inspiration into two or three operational moves — never stored passages, never pastiche. Cards can license a deliberate device (a Churchillian triad) that the tells list restricts as a tic; the moderation rule reconciles the two. Storage follows the voice-profile standard: a plain companion file the skill checks for.
- **Voice as persona with a stored profile**, because "sound more like me" prompts demonstrably fail; structured profiles built from real samples work.

## The evidence base

The scholarly research behind the rules — fluency, concreteness, narrative transportation, the misread-tone effect, conversational receptiveness, values reframing, and a hedging finding that failed replication — lives in `science.md`, with each entry marked verified-at-source or training-sourced. When a study and your own eval results disagree, the eval wins.

## The market context

As of mid-2026 the skill ecosystem is enormous and coding-dominated; no general-purpose *writing* skill has broken out the way the top design and coding skills have. The gap is structural, not temporary: what makes writing good — voice, judgment, the specific point — is exactly what can't be pre-packaged and shared. Voicestead's bet is therefore lean-and-personal over big-and-generic: a small core anyone can adopt, made *theirs* through the voice profile and their own eval results.

---

# formats.md

# Formats — Per-Medium Defaults

Load when the piece has a clear medium. These are defaults, not laws; the writer's voice profile and explicit wishes override.

## Email
First line: the ask or the news. Subject line: six or fewer strong words, specific ("Q3 headcount decision needed by Fri" not "Quick question"). One topic per email where possible. If action is needed: who, what, by when, unmissable. Under 150 words unless there's a reason. Close warm but short.

## Status update (team, program, weekly)
Line one: overall status in plain words (on track / at risk / blocked — and the one-line why). Then: what changed since last time, what matters about it, what you need. Ordered so a skimmer can stop after any line and still be current. Cut anything the reader already knows. Never let a risk appear for the first time in week six — surface early, small, and factually.

## Slack / chat message
Point in the first line — assume they read only the notification preview. No "hey, quick question" as its own message. If it needs more than ~5 sentences, it's a doc or a call; say which and why.

## LinkedIn / social post
First line earns the click on "see more" — a specific claim, a surprising number, or a real moment; never a throat-clear. One idea per post. Write like a person who did the thing, not a brand. Concrete beats inspirational: the number, the mistake, the actual conversation. No hashtag salads. End with a genuine question or a plain close, not "Agree?" Two research-backed nudges: "you" pulls readers in (second-person framing correlates with texts that travel), and present tense reads as more persuasive than past ("this approach works" over "this approach worked").

## Proposal / one-pager
Top: the ask and the recommendation in two lines (the reader decides here whether to keep reading — write it so a busy exec could approve from the summary alone). Then the persuasion shape (see persuasion.md): situation, stakes, answer, proof, ask. Appendix for depth — never force the detail on everyone. One page means one page.

## Hard message (bad news, pushback, apology, delicate ask)
Slow down. Name your actual goal before writing (preserve the relationship? change a decision? own a mistake?). Deliver the hard thing early and plainly — burying it reads as evasion. No hedging into mush, no over-apologizing into groveling. Say what happens next. Offer the writer two versions: one more direct, one more gentle — this is the one format where the register call belongs to them.

## Exec summary
The whole document in five sentences or fewer: situation, finding, implication, recommendation, ask. Write it last, place it first. If the exec reads nothing else, this must be enough — test it standalone.

---

# influence.md

# Influence & Emotional Intelligence

Load this when the writing must move a person — persuade, ask, disagree, deliver hard news, motivate a team, or repair a relationship. Distilled from Sinek (purpose), Carnegie (goodwill), Voss (tactical empathy), Goleman (emotional intelligence), and the communication research in `science.md`. Use `persuasion.md` for the argument's *structure*; use this for the *human* underneath it.

## 1. Start with why — purpose before ask (Sinek)

People don't buy *what* you do, they buy *why*. Most writing runs outside-in — what, then how, then maybe why. Flip it: one line of purpose or belief before the ask. "We keep losing Fridays to a release process nobody trusts" lands harder than "I'm proposing we adopt CI/CD." The test: if the reader finished only your first two sentences, would they know why this matters — not just what you want? Don't overuse it; a two-line status update needs no mission statement.

## 2. Goodwill and the reader's ego (Carnegie)

People are creatures of emotion, pride, and ego, not logic. Writing that respects that gets a yes; writing that bruises it gets a fight — even when the writer is right.

- Open by acknowledging, not asserting. If you're about to disagree, first show you understood their view.
- Never open with criticism; it puts the reader on defense. Lead with something specific and genuinely good, then the fix.
- Frame the ask in their interest — translate every request into the reader's benefit before sending.
- Let it be their idea: lay out the case and let the reader arrive; people trust conclusions they reach themselves.
- Sincere, specific appreciation beats flattery. "Thanks for turning the migration doc around by Tuesday — it unblocked the team" works; "great job!" is noise.
- Give them a reputation to live up to.

## 3. Tactical empathy — name the emotion before the ask (Voss)

Address the feeling before the facts and you lower defenses before the reader decides to resist.

- **Label it in writing:** "This probably lands at the worst possible time" or "You may be wondering why we're changing this again." A named fear deflates; an ignored one argues through the whole read.
- **Run the accusation audit:** list the worst things the reader could think about your message, and say them yourself, first.
- **Aim for "that's right," not "you're right":** summarize their situation back so accurately they can only agree — a short paragraph mirroring their reality, before your proposal, earns the real yes.
- **Prefer "how" and "what" over "why":** "Why did you do it this way?" reads as accusation; "What's the biggest constraint here?" invites them to solve alongside you.
- **A "no" is safe; a fast "yes" is fragile:** phrasing that permits pushback ("Tell me if this doesn't work for your team") gets more honest engagement than cornering.

## 4. Emotional intelligence, on the page (Goleman)

Manage your own emotion first, then the reader's.

- **Self-awareness:** frustration and ego leak through sharp asides and passive-aggressive politeness. If the draft is venting, it isn't done.
- **Self-regulation — never send hot:** the angry email that feels great to write costs the most. Draft it, wait, or write the composed version alongside the direct one.
- **Empathy:** you can't hear the reader's reading. Assume the flattest interpretation and add the goodwill back in.
- **Relationship management:** every message is a deposit or a withdrawal. Winning the point and losing the person is usually a bad trade.

## 5. The screen distorts tone — write for the misread

This is measured, not folklore: senders systematically overestimate how well their tone — sarcasm, humor, warmth — survives text, because they can't step outside their own reading of it; and received email skews *more negative* than intended. Assume your neutral reads cool and your dry humor reads hostile.

**The hostile reading test (a debias that actually worked in the lab):** before sending anything chargeable, reread the draft as if you're already annoyed at the sender. Every line that turns sarcastic, cold, or accusatory under that reading gets rewritten or cut. Reading in the opposite tone is what breaks the writer's egocentrism.

## 6. Disagreeing in writing — the receptiveness recipe

When you must push back, the language of receptiveness is measurable, learnable, and it wins twice: receptive writers are judged more persuasive *and* better future collaborators, receptiveness early forestalls escalation later, and it's contagious — your receptive language pulls the counterpart toward the same. The recipe:

1. **Restate their view first, accurately enough that they'd say "that's right."** Not a strawman, not a caricature — their best version.
2. **Hedge deliberately, once or twice.** "I may be missing context on the budget side" signals openness, not weakness. (This is the one sanctioned home for hedging — see the quality bar.)
3. **Frame in positives, not negations.** "Here's what keeping the contractor protects" over "cutting it doesn't make sense."
4. **Name the real point of agreement** before the point of divergence — there almost always is one.
5. **Then make your case** with the persuasion structure, and keep the ask itself unhedged.

## 7. Warmth or firmness — name the game

Warmth serves relationships; it is not free everywhere. In one-shot, value-claiming negotiations, communicating warmth measurably *worsened* outcomes. Before writing, name which game this is: an ongoing relationship (default warm, per everything above) or a distributive, one-time ask (politely firm — courteous, direct, no softening of the number or the terms). Most workplace writing is the first kind; know when you're in the second.

## 8. The ethical line

All of these authors and literatures draw the same boundary: tools for genuine understanding and mutual benefit, not manipulation. Never write a why you don't hold, an appreciation you don't feel, or an empathy you're faking — readers detect it, and every technique above then backfires. Use these to communicate true things more humanely.

## Pre-flight for high-stakes messages

1. **Why** — purpose clear in the first two lines, not just the what?
2. **Them** — ask framed in the reader's interest and values, in their words?
3. **Feeling** — named the objection or emotion they're already having, before the case?
4. **State** — sending composed, or hot? If hot, wait.
5. **Misread** — done the hostile reading? Fixed what turned cold or sarcastic?
6. **Game** — relationship or one-shot? Warmth calibrated to which?
7. **Relationship** — deposit or withdrawal? If withdrawal, worth it?
8. **Sincerity** — every why, thanks, and acknowledgment true?

---

# inspiration.md

# Inspiration — Learning Who Shaped You

Load this when the person wants to teach the skill about their influences ("let me tell you who I admire," "learn my style influences"), names an inspiration to study ("I want to write more like X," "study this book / speech / essay"), asks to add something to their influences, or asks what their stored influences are. This is the mechanism that makes the skill not only for your writing, but for your inspiration.

## Why influences

Every voice is built from other voices — the writers you reread, the speech you can still hear, the mentor whose memos you kept. A voice profile captures how you *sound today*; the influence system captures who shaped you and who you're *reaching toward*. The skill uses both: the profile as the anchor, the influences as directions to stretch. The rule underneath everything here: **learn the move, never the fingerprint.** We borrow what makes an influence work; we never pastiche them.

## Mechanism 1 — The influence interview ("teach me who shaped you")

Offer it once, like the voice setup: "Want to do a 10-minute influence interview? I'll ask a few questions about the writers and voices that shaped you, and store what we learn so it informs everything I draft for you."

Ask **one question at a time**, follow up on what they actually say (follow-ups beat new questions), and skip any they shrug at:

1. Which two or three writers or speakers do you most admire — and one line on *why* each?
2. What's a piece you've reread, or can quote from memory — a book, a speech, an essay, even a post? What stays with you about it?
3. Whose writing makes you jealous? What exactly are they doing that you wish you did?
4. When someone finishes your best writing, what do you want them to *feel*?
5. Anti-influences: what writing makes you close the tab? What's it doing wrong?
6. Any inherited voices — a parent's letters, a pastor's sermons, a boss's memos — that trained your ear before you noticed?
7. For each influence named: if you could steal one *move* of theirs, which?

Then distill into the **Influence Profile** (template below), read it back for confirmation, and store it. Only what they said goes in — never invent an influence or a reason.

## Mechanism 2 — Study an influence (the pipeline)

When they point at a book, writer, speech, or body of work, run this five-step pipeline:

**1. Intake.** Ask what drew them to it and where they want it to show up (posts? talks? hard emails?). One or two questions, not an interrogation.

**2. Gather.** If research tools are available, research the influence: who they are, what their style is known for, how critics and craft writers describe their moves. If not, ask the person to paste two or three representative excerpts. **Never fabricate a quote, a fact, or a claim about the influence** — the Truth rule applies to inspirations as much as to drafts. Mark anything unverified.

**3. Extract through the skill's lenses.** Analyze what actually makes it work, in our terms:
- *Rhythm* — sentence-length pattern, where the short sentences land, use of repetition as a deliberate device.
- *Concreteness* — how they anchor abstractions in things, names, moments.
- *Structure* — point-first or slow build? How do they open and close?
- *Persuasion moves* — story vs. argument, understatement vs. heat, whose values they frame in.
- *Influence moves* — how they acknowledge the other side, name emotion, earn trust.
- *Signature devices* — anaphora, the tricolon, the aside, the question. (Note: some influences legitimize devices our tells list restricts — Churchillian triads, King's anaphora. The reconciliation: those are **deliberate devices, used sparingly and on purpose**, which is exactly the skill's moderation rule. An influence card can license a device; it never licenses a tic.)

**4. Distill to an Influence Card** (template below): who, the two or three transferable moves, when to reach for it, when *not* to, and at most a short identifying fragment — never stored passages.

**5. Store and apply.** Append the card to the influences file. Going forward, when a piece calls for it (or they ask for something "in the spirit of X"), blend at the **move level** — one influence move per piece is usually right — with the voice profile always outranking. Inspiration stretches the voice; it never replaces it.

## Where this lives — storage

The influence system stores to a plain file, same standard as the voice profile:

- **The file:** `influences.md`, kept next to `voice-profile.md`.
- **Claude Code:** in the skill folder or the project's `.claude/` directory — the skill checks for it and reads it when present.
- **Claude.ai / Cowork:** add it to the Project's knowledge, or paste into Project instructions.
- **Claude memory:** can hold the one-paragraph summary, but the file is the source of truth — portable, reviewable, versionable.

If no influences file exists and the moment fits, offer Mechanism 1. If one exists, honor it silently — influences inform drafts without being narrated at the reader.

## influences.md template

```markdown
# Influences — <name>

## Influence Profile
Admires:            <writer — why, in their words>
Reaching toward:    <the feeling/effect they want their writing to have>
Anti-influences:    <what they refuse to sound like>
Inherited voices:   <if any>

## Influence Cards

### <Influence name> — <body of work>
Why it's here:      <what drew them, their words>
Moves to borrow:
  1. <move, described operationally — "lands the short sentence after the long build">
  2. <move>
Reach for it when:  <contexts>
Not for:            <contexts where it misfires>
Fragment:           <optional, under 15 words, for calibration only>
Verified:           <researched / user-supplied excerpts / unverified>
```

## Guardrails

- **Moves, not fingerprints.** Studying an influence teaches technique; producing recognizable imitations of a living writer's voice for public work crosses from inspiration to impersonation — decline that and offer the move-level blend instead.
- **No stored passages.** Cards hold described moves and, at most, a short fragment. Never reproduce or store copyrighted text at length.
- **Truth extends to influences.** No invented quotes, biography, or analysis presented as fact; unverified impressions are labeled as such. The same licensing covers citations and links: only ones the user or the studied material actually supplied.
- **The person's voice wins.** Influences are seasoning. If a draft starts sounding more like Churchill than like them, the blend failed — pull back to the profile.

---

# persuasion.md

# Persuasion — Arguing a Point That Lands

Load this when the job is to convince: a pitch, a proposal, a push for a decision, a disagreement, an ask.

This file is the argument's **structure**. For the **human** underneath it — purpose, goodwill, tactical empathy, tone across a screen, the receptiveness recipe — load `references/influence.md`. High-stakes or emotional messages need both. Evidence behind these rules: `references/science.md`.

## The core move: show, then let them conclude

Lay down the concrete thing — the number, the example, what actually happened — and get out of the way. A reader who reaches the conclusion on their own believes it; a reader who's handed it argues back. Don't preach, don't oversell: understatement carries more weight than hype, and overclaiming reads as weakness.

## The "so what?" chain

For every claim, ask *so what?* until the answer reaches something the reader already wants — then stop; that's the line. "The new system is faster" — so what? — "reports that took four hours take fifteen minutes" — so what? — "your team ships Thursday instead of Monday." Write the Thursday line. A claim that can't survive two rounds of *so what?* isn't a reason — cut it. Three strong reasons beat seven mixed ones.

## Argue it, or tell it

Arguments invite the reader to argue back. A story doesn't — narrative transportation measurably lowers counterarguing, which is why a true three-sentence case often outperforms three bullets of claims on a resistant audience. "In March, Jenna covered fourteen pages in one on-call week. She drafted her resignation on the Friday. We talked her out of it once; we won't twice." Same facts as a bullet list; different physics.

Use the story move when the audience is resistant, the topic is values-laden, or the claims sound abstract. Rules: the story must be **true** (the Truth rule governs — never composite, never invent), short (three to five sentences), and concrete (names, moments, one detail that couldn't be made up). Then step back into the argument for the ask.

## Their values, not yours

Writers reflexively argue from their *own* values — and those arguments underperform with any audience that doesn't share them. The reframe that works: ground the case in what the *reader* already holds sacred. The same second-SRE ask is "protecting delivery commitments" to a reliability-minded VP, "keeping senior engineers we can't rehire" to a talent-minded one, and "closing an audit finding" to a risk-minded one. Find their value; argue from inside it. (If you can't state their values, you're not ready to persuade them — go back to Model 1.)

## The default argument shape

Use when you need structure; skip any beat the reader already has:

1. **The situation** in one line — what's true right now.
2. **The stakes** — what it costs or risks to leave alone. Concrete: hours, dollars, dates, attrition.
3. **The answer** — your proposal, stated plainly.
4. **The proof** — the strongest evidence: a number, a precedent, a pilot result, a true story (above). One great proof beats four decent ones.
5. **The specific ask** — what you want from this reader, by when.

## Calibrate by direction

- **Writing up:** lead with the decision you need and the cost of waiting; brevity is respect; answer their first question inside the doc.
- **Writing across:** lead with the shared problem; context before asks; name what's in it for their team.
- **Writing to your team:** lead with why it matters to them; make the action unmistakable.

## The emotion dial

The intent to persuade automatically inflates emotional language — watch your own drafts for it. Calibrate to how the audience evaluates: for analytically-minded readers (executives reading a business case, engineers reading a design argument), put the emotion in the **stakes** ("we will miss the March date") and keep it out of the **adjectives** ("this incredible opportunity"). Save expressive language for audiences and moments that run on it.

## What not to do

- Don't stack adjectives where evidence should be.
- Don't hedge the ask. Deliberate hedges live in two places only — genuine uncertainty, and the receptiveness recipe for disagreement (influence.md). The ask itself is always plain: "Approve X by Friday."
- Don't bury the ask under a long build-up. Point first applies doubly here.
- Don't manufacture urgency or invent stakes. If the honest stakes are small, right-size the ask.

---

# science.md

# The Evidence Base

The research behind Voicestead's rules. This file is NOT loaded for everyday writing jobs — load it when the person asks *why* a rule exists, wants the studies behind a claim, wants to go technically deeper, or challenges the skill's advice. It also exists to keep the skill honest: every operative rule traceable to its evidence, every evidence entry marked by how well we've verified it.

**Status legend:** ✔ *verified at source* (abstract/paper read during research) · ◇ *training-sourced* (well-established but re-verify before quoting numbers publicly).

## 1. Clarity and fluency — plain words make the author look smarter

✔ Oppenheimer (2006), *Applied Cognitive Psychology*: five experiments found a negative relationship between vocabulary complexity and judged intelligence, holding regardless of text quality; effect mediated by processing fluency — even hard-to-read fonts lowered judgments of the author. ✔ Alter & Oppenheimer (2009), *Personality and Social Psychology Review*: fluency is a general metacognitive cue — people judge easily-processed information as more true, across conceptual, perceptual, and linguistic forms.
◇ Related: jargon reduces processing fluency and engagement (Shulman et al., 2020); less-readable corporate filings correlate with worse informational outcomes (Li, 2008, *J. Accounting & Economics*).
**Feeds:** Model 3 (say it to one person), the quality bar's Clear rule, tells.md's plain-word swaps. The upgrade fluency research adds: readers aren't just slowed by complexity — they downgrade *the author*.

## 2. Concreteness — specifics signal listening

✔ Packard & Berger (2021), *Journal of Consumer Research*: across five studies including 1,000+ real customer interactions, concrete language increased satisfaction, purchase intent, and actual purchases; mechanism: customers infer the concrete speaker is *listening*. Reported magnitudes: ~5.6% more concreteness → ~8.9% higher satisfaction; ~30% higher spend in an email context. ✔ Packard, Moore & McFerran (2018): "I" pronouns from service employees outperform "we."
**Feeds:** the Specific rule; the reply move of echoing the reader's own concrete nouns.

## 3. Narrative — stories lower counterarguing

✔ Green & Brock (2000), *JPSP*: transportation into a narrative reduces counterarguing and resistance to persuasion. ✔ Braddock & Dillard (2016), *Communication Monographs*, meta-analysis: narratives reliably influence beliefs, attitudes, intentions, and behaviors; ✔ van Laer et al. (2014) meta on transportation. Arguments invite rebuttal; a story suspends it.
**Feeds:** persuasion.md's "argue it, or tell it" move. Guardrail: the Truth rule still governs — only real stories.

## 4. The screen distorts tone — and writers can't feel it

✔ Kruger, Epley, Parker & Ng (2005), *JPSP*: across five experiments, people overestimated their ability to convey sarcasm, humor, and tone by email — and to interpret others' — driven by egocentrism. Debias that worked: reading one's message aloud in the *opposite* tone eliminated the overconfidence. ✔ Byron (2008), *Academy of Management Review*: emotion in email is systematically miscommunicated; receivers skew negative.
**Feeds:** influence.md's misread-tone law and the hostile-reading test.

## 5. Receptiveness — the language of productive disagreement

✔ Yeomans, Minson, Collins, Chen & Gino (2020), *OBHDP*: an interpretable algorithm identified the linguistic profile of receptiveness (explicit acknowledgment of the opposing view, measured hedging, positive rather than negated framing); writers following the "receptiveness recipe" were judged more persuasive and more desirable future collaborators, and receptiveness early in a conversation forestalled later conflict escalation. ✔ Hussein & Tormala (2021): receptive arguments are more persuasive. ✔ Minson et al. (2024): receptiveness transmits — one party's receptive language increases the counterpart's.
✔ Related tension: Jeong, Minson, Yeomans & Gino (2019), *Management Science*: communicating warmth in distributive negotiations produced *worse* outcomes — friendliness isn't free in one-shot value-claiming.
**Feeds:** influence.md's disagreement recipe and the warmth-vs-firmness rule.

## 6. Certainty and hedging — including a failed replication we keep on purpose

✔ Karmarkar & Tormala (2010), *JCR*, found experts became more persuasive expressing uncertainty (the "incongruity hypothesis"). **But** ✔ a 2024 registered replication (Løhre et al., *JESP*, N=1,018) failed to reproduce it, instead supporting the confidence heuristic: expressed certainty helps persuasion irrespective of expertise (d≈0.18–0.25).
**Feeds:** the refined hedging rule. What survives all the evidence: cut reflexive hedges (Pinker; the confidence heuristic); keep deliberate hedges where they're honest (real uncertainty) or receptive (disagreement — §5); never hedge the ask. This entry stays in the file as a worked example of why we verify before we encode.

## 7. Values framing — argue in the reader's morals, not yours

✔ Feinberg & Willer (2015 *PSPB*; 2019 *SPPC* review): people spontaneously build arguments from their *own* moral values, and those arguments underperform; reframing a position in the audience's values (e.g., purity-framed environmental appeals for conservatives) persuades across divides, with effects replicated over a decade across inequality, environment, same-sex marriage, and candidate support.
**Feeds:** persuasion.md's "their values, not yours" rule.

## 8. Emotion, questions, and other supported-but-lighter findings

◇ Rocklage, Rucker & Nordgren (2018), *Psych Science*: the mere intent to persuade automatically makes language more emotional; emotionality helps hedonic contexts and can backfire with analytically-minded evaluation. Feeds the emotion-dial line. ◇ Huang, Yeomans et al. (2017), *JPSP*: question-asking — especially follow-ups — increases liking. Feeds coaching.md. ◇ Packard & Berger (2020), *Psych Science*: second-person "you" correlates with cultural success of texts; ◇ Berger (2023), *JCR*: present tense reads as more persuasive. Feed formats.md's post guidance.

## 9. The AI-era findings (instruction voice and mechanics)

✔ Politeness effects on model output are unstable across studies and models — impolite prompts hurt in 2024 cross-lingual work but *outperformed* polite ones on GPT-4o in 2025 — so tone is treated as flavor, not quality. ✔ Mechanical corruption is the reliable degrader: character-level typo attacks cost ~20%+ task performance in benchmark studies, and typos measurably hurt even frontier and reasoning models. ✔ Burstiness (sentence-length variance) is among the clearest measurable separators of human from machine prose.
**Feeds:** the rhythm rules, the instructions-vs-material guardrail, and the skill's own mechanically-impeccable house voice. Full experimental protocol: `tests/experiments/instruction-voice/` (lives in the repo, not shipped inside the skill).

## Reading this file honestly

These are averages from studies, mostly lab and field contexts that are not your exact context. Effects are directional tendencies, not laws; several classics in this literature have shrunk or died under replication (see §6), which is why entries carry status marks and why the eval harness — your writing, judged blind — outranks any citation here. When a finding and your tested results disagree, trust the test.

---

# tells.md

# The Tells — Full Catalog

What makes prose read as machine-made, and how to fix each pattern. Load this for editing passes, humanizing requests, or any "this sounds like AI" complaint.

The master test for every entry: **would this writer say this word, in this sentence, out loud?** These are categories with examples, not a memorized ban list. Context always wins — "robust test coverage" in an engineering doc is correct; "a robust solution" in a sales email is a tell.

## Contents
1. Rhythm patterns (the loudest tells)
2. Reflexive fancy words
3. Zombie nouns
4. Empty intensifiers and compulsive hedges
5. Formula structures
6. False agency
7. Tools that are fine in moderation
8. The positive side: what human rhythm looks like

---

## 1. Rhythm patterns — the loudest tells

**Metronomic sentence length.** Sentence after sentence landing in the same 15–20 word band. Fix: follow a long, winding sentence with a short one. If three in a row run the same length, break one or merge two.

**The rule of three.** AI reflexively groups items in threes — "faster, cheaper, and simpler," then the next sentence delivers another triple. Readers feel the pattern before they can name it. Fix: let group sizes ebb and flow — three, then one, then four, then two. More than one triad per couple hundred words, recount one.

**Uniform paragraph shape.** Every paragraph the same length, every one ending on a punchy line. Fix: vary endings; let one paragraph be a single sentence.

## 2. Reflexive fancy words

The reach-for word where a plain word exists. Examples (not exhaustive — the category is the point): delve, leverage, robust, seamless, pivotal, crucial, foster, harness, bolster, underscore, elevate, streamline, unlock, landscape, realm, tapestry, paradigm, synergy, myriad, plethora, navigate (figuratively), utilize, facilitate, comprehensive, transformative, cutting-edge, holistic, commendable, meticulous. Also stock phrases: "in today's…", "it's worth noting," "at the end of the day," "that being said."

Fix: the plain-speech swap. Use → not utilize. Help → not facilitate. If you wouldn't say it at a bar, don't write it.

## 3. Zombie nouns

Action verbs frozen into abstract nouns — nominalizations. "The utilization of," "the implementation of," "the provision of support," "prevention of neurogenesis diminished avoidance."

Fix: thaw the verb and name the actor. "When we prevented neurogenesis, the mice no longer avoided other mice." Someone uses, someone implements, someone supports. Zombie nouns are where clarity goes to die — they hide both the action and who did it.

## 4. Empty intensifiers and compulsive hedges

Intensifiers that add nothing: really, truly, actually, genuinely, literally, simply, very, incredibly. Hedges driven by cover-your-anatomy instinct: somewhat, arguably, comparatively, "to a certain degree," "it could be said," "I think it would probably be a good idea to consider possibly…"

Fix: cut the reflexive ones; trust the reader to supply obvious caveats. Two deliberate uses survive: a plain hedge on a genuinely uncertain claim (honesty — say it once), and a measured hedge when disagreeing, where it signals openness rather than weakness (the receptiveness recipe in influence.md). Never hedge the ask itself — the evidence on expressed confidence is one of the few one-way streets in this literature (see science.md §6).

## 5. Formula structures

- **The false contrast:** "It's not X, it's Y." / "The question isn't X, it's Y." Fix: state Y directly.
- **The negative-list striptease:** "Not a memo. Not a plan. A decision." Fix: state the thing; the reader doesn't need the runway.
- **The rhetorical setup:** "What if I told you…", "Think about it:", "Here's the thing:". Fix: make the point instead of announcing that a point is coming.
- **The vague declarative:** "The implications are significant." Fix: name *which* implication. If a sentence announces importance without naming the specific thing, cut it or replace it with the thing.
- **The dramatic fragment for effect:** "Speed. That's it. That's the strategy." Fix: complete the sentence; trust content over presentation.

## 6. False agency

Inanimate things doing human verbs: "the data tells us," "the culture shifts," "the decision emerged," "the conversation moved toward," "the market rewards." AI loves this because it avoids naming the actor.

Fix: name the human. Someone read the data and concluded. People changed how they work. Someone decided. If no specific person fits, use "you" and put the reader in the seat.

## 7. Tools that are fine in moderation

Em-dashes, adverbs, passive voice, colons, semicolons, starting sentences with And or But. None of these is banned — a person uses all of them, sparingly and on purpose. Overuse is the tell, not the tool. Rough calibration: more than one em-dash pair every few paragraphs, thin them; an adverb is guilty until it proves it changes the meaning; passive voice only when the actor is genuinely unknown or unimportant. A skill that bans these outright just trades one robotic style for another.

## 8. The positive side: what human rhythm looks like

Humanizing isn't only subtraction. Human prose has: contractions; the occasional sentence starting with And, But, or So; one concrete detail per idea (a name, a number, a thing that happened); a real position taken without hedging into balanced mush; a rhythm that swings — a long thought that winds through a clause or two before landing, then a short one. Like that.

---

# voice.md

# Voice — Capturing and Keeping It

Sounding like the writer, not like a model, is the whole game. Without a voice, nothing else in this skill holds. Load this on first use with a new writer, whenever no voice profile exists, or when output "doesn't sound like me."

## The principle: persona, not rule list

Treat voice as a character to inhabit, not rules to obey. Ask: who is this person? How do they sound when confident versus unsure? What moves keep recurring — how do they open, how do they close, how blunt or warm do they run? A rule list ("avoid these ten words") produces mechanical, checkbox prose. A persona produces someone.

## The 3-minute setup (offer it once, don't force it)

When no profile exists, offer — once: "Want to do a 3-minute voice setup? Paste 2–3 things you've actually written — an email you liked, a post, a message. I'll build a profile so everything I draft sounds like you." If they decline or just keep working, don't ask again; infer from how they write to you instead. A second ask just reads as nagging.

From the samples, extract:

- **Sounds like:** two or three adjectives with evidence ("direct but warm — you soften asks with 'no rush' but never soften the ask itself").
- **Signature moves:** recurring patterns (opens with context in one line; closes with a question; uses sports metaphors; short paragraphs).
- **Never says:** words or moves absent from their writing that a model would default to.
- **Sample lines:** 3–5 verbatim lines that are unmistakably them — the calibration set.

Read the profile back in one block before you save it, and wait for a yes. Their one correction — "I'd never say 'circle back'" — is worth more than everything you inferred.

If they skip the setup: infer from how they write to you in the chat — their messages are a live sample — and ask for one line of something real when the stakes are high.

Working from a clone of the repo, there is a measured head start: `python3 scripts/voice_profile_draft.py sample1.txt sample2.txt` prints a draft profile in seconds — sentence rhythm, contraction rate, punctuation habits, all computed from the samples, never guessed. Treat it as raw material for this interview: it counts what can be counted and leaves "Sounds like" and "Never says" to the writer.

## Where it's stored (be honest about persistence)

Say what actually happens on the surface you're running on. Never imply the profile persists by magic — it lives in a file or in Project knowledge, nowhere else.

- **Claude Code:** write the profile to a file the skill can reread — `voice-profile.md` in the skill folder, or in the project's `.claude/` directory. Multiple writers each get their own: `voice-profile-<name>.md`. Tell the user the path, and that it loads next session on its own.
- **Claude.ai / desktop:** you can't silently persist anything. Hand the user the finished profile and tell them to paste it into the Project's instructions or add it as Project knowledge so it's in context next time. Be plain that without that step it won't carry over.
- **Either way:** the file is the source of truth — portable, reviewable, theirs to edit. A one-line summary can sit in memory, but the draft is always checked against the file. A worked example lives at `examples/voice-profile.example.md`.

## Applying the profile

- The profile outranks every general style preference in this skill. If their voice loves em-dashes, the em-dashes stay.
- Mirror, don't imitate: match rhythm, word choice, warmth, and structure — but never inject their signature phrases mechanically. A tic repeated on schedule is a tell of its own.
- Check output against the sample lines: read your draft, then read their lines. Same person? If not, revise before delivering.
- Voice drifts by medium. If their emails and their posts sound different, note both registers in the profile.

## voice-profile.md template

```markdown
# Voice Profile — <name>

Sounds like:
Signature moves:
Never says:
Registers (if voice shifts by medium):
Sample lines:
1.
2.
3.
```
