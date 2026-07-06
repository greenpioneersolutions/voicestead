# Trigger checklist

The skill has to fire on the right prompts and stay quiet on the wrong ones. Nothing
automated tests that yet — it needs a key (see the last section) — so this is the manual
pass. Run it after any edit to the `description` field in `SKILL.md`, because that field
is the only thing Claude Code sees when it decides whether to load Voicestead.

Twelve prompts, pinned. Paste each into a fresh session with the skill installed and note
whether Voicestead engages. Don't reword them: the point is that the description survives
these exact phrasings, several of which never say "write."

## Should fire (10)

1. **does this sound okay?** — _[paste a short email]_
2. _ok so the vendor's API docs were wrong, we found out tuesday, migration slips two weeks, i need to tell my boss but not sound like i'm panicking_ — a raw brain-dump, no verb like "write"
3. **help me tell my boss the launch slipped**
4. **make this less robotic:** _[paste a paragraph of stiff AI prose]_
5. how do I phrase this to a customer without sounding defensive?
6. can you make this warmer? _[paste a curt message]_
7. i need to tell a vendor we're not renewing — 3 years, good relationship, budget cuts
8. reword this so it sounds like me: _[paste two sentences]_
9. this doc started in my voice but by the last section it reads like a press release — pull it back — long-session voice drift, no verb like "write"
10. the register went formal somewhere in the middle of this handbook doc. fix the sections that drifted, not the whole thing

## Must NOT fire (2)

11. **write a bash script that rotates the nginx logs nightly** — pure coding task
12. **parse this CSV and sum the third column, then show the top 10 rows** — pure data task

## Results

| # | prompt | fired? | correct? | notes |
|---|--------|--------|----------|-------|
| 1 | does this sound okay? | | | |
| 2 | vendor/migration brain-dump | | | |
| 3 | tell my boss the launch slipped | | | |
| 4 | make this less robotic | | | |
| 5 | phrase this to a customer | | | |
| 6 | make this warmer | | | |
| 7 | tell a vendor we're not renewing | | | |
| 8 | reword so it sounds like me | | | |
| 9 | last-section press-release drift | | | |
| 10 | mid-document register creep | | | |
| 11 | bash log-rotation script | | | should stay quiet |
| 12 | parse CSV, sum a column | | | should stay quiet |

## The gate

Ship only when **at least 10 of the 12 land correctly AND there are zero false fires** —
both must-NOT prompts (11 and 12) stay quiet. The two halves aren't equal. A false fire on
a coding or data task breaks that user's session, so the 0-false-fires half is
non-negotiable; the 10+/12 half then tolerates at most two soft misses among the ten
positives.

- A positive missed? The description is too narrow. Widen the phrasing it covers — the
  brain-dump and "does this sound okay?" cases are the usual casualties.
- A negative fired? The description is too greedy. Tighten the "do not trigger on pure
  coding, config, or data tasks" clause.

## Later: the judge tier (needs a key)

Once an `ANTHROPIC_API_KEY` is available, turn this page into a regression. For each
prompt, show a model only Voicestead's frontmatter description plus two decoy skill
descriptions, and ask which it would invoke — reply `{"skill": name|null}`. Gate: every
positive picks voicestead, both negatives return `null`. Roughly a dozen calls, pennies. Run
it in the eval workflow and on any PR that touches the SKILL.md description — hash the
description and re-run when it changes. It approximates Claude Code's real dispatcher
rather than being it, but it turns a description edit from a launch-day surprise into a
red check.
