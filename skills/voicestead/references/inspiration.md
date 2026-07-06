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
- **Truth extends to influences.** No invented quotes, biography, or analysis presented as fact; unverified impressions are labeled as such.
- **The person's voice wins.** Influences are seasoning. If a draft starts sounding more like Churchill than like them, the blend failed — pull back to the profile.
