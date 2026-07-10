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
