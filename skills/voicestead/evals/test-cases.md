# Test Cases

Smoke tests for the skill. Each has a prompt (paste into a fresh session with the skill installed) and pass criteria. A case passes when every criterion holds.

## Case 1 — Draft mode, email
**Prompt:** "help me email my boss that the migration is going to slip two weeks because the vendor API docs were wrong, we found out tuesday, new date is the 28th, i want to keep his confidence"
**Pass criteria:** News in the first line (slip + new date). Cause stated factually without blame-dodging or groveling. A why-it-matters/what-happens-next beat. Under ~120 words. No hedging mush ("might possibly"). No invented details (no fake mitigation plans not supplied). Names its moves in 1–2 lines after.

## Case 2 — Draft mode, persuasion
**Prompt:** "write something to convince our leadership team to fund a second SRE. we had 14 incidents last quarter, on-call is burning people out, jenna almost quit"
**Pass criteria:** Claim/ask stated early. Uses the supplied specifics (14 incidents, Jenna near-quit — kept, not vagued into "morale issues"). Runs the so-what chain to a leadership-relevant stake (delivery risk, attrition cost). Contains a specific ask. No invented numbers (e.g., no fabricated dollar costs). Handles the obvious objection (cost) or flags it.

## Case 3 — Improve mode, voice preservation
**Prompt:** "make this better but keep it sounding like me: 'Team — heads up. Sprint demo moved to Thurs 2pm. Know it's short notice. If your piece isn't ready just show what you got, nobody's grading you. Questions, hit me up.'"
**Pass criteria:** Output stays terse, warm, fragment-friendly — does NOT formalize into "Dear team, please be advised." Keeps "nobody's grading you" energy. Changes are minimal; restraint rule may apply ("this is already good" is a passing response).

## Case 4 — Review mode, no rewrite
**Prompt:** "give me feedback on this post, don't rewrite it: [any 200-word LinkedIn draft]"
**Pass criteria:** Does not rewrite. Leads with one specific strength (quotes a real line). Asks at most 2–3 sharp questions. Fixes listed in priority order. No generic praise ("great post!").

## Case 5 — Anti-slop pass
**Prompt:** "humanize this, it sounds like AI: 'In today's rapidly evolving landscape, it's worth noting that our robust solution doesn't just streamline workflows — it transforms them. The implementation of our platform facilitates seamless collaboration, enhances productivity, and unlocks innovation. The data tells us adoption is accelerating.'"
**Pass criteria:** Kills the tells across categories: opener, "robust/seamless/streamline/unlocks," the false contrast, zombie nouns ("the implementation of"), the triad, false agency ("the data tells us" → someone concluded). Output varies sentence length. Flags that the original contains zero specifics and asks for (or placeholders) real ones rather than inventing them.

## Case 6 — Restraint
**Prompt:** "edit this: 'Standup is cancelled tomorrow. Use the time to close out sprint tickets. Back to normal Thursday.'"
**Pass criteria:** Recognizes it's already clean. Says so and stops (or suggests at most one trivial tweak). Does not inflate, add headers, or restructure.

## Case 7 — Curse of knowledge
**Prompt:** "draft a note to the parent council explaining we're moving to the RACI model for event planning since the DRI ambiguity caused the double-booking"
**Pass criteria:** Catches that a parent council won't know RACI or DRI. Either translates to plain language or defines in-line. Point first (what's changing and why it helps them).

## Case 8 — Format defaults, hard message
**Prompt:** "I need to tell a vendor we're not renewing. 3 years together, good relationship, decision is final, budget cuts. help"
**Pass criteria:** Hard thing delivered early and plainly, not buried. No false hope ("maybe next year!") since decision is final. Warmth without groveling. Offers two versions (more direct / more gentle) per the hard-message format. Says what happens next (transition, timeline placeholder).

## Case 9 — Influence: charged ask with tactical empathy
**Prompt:** "I need to ask my VP to reverse a decision he made last week to cut our QA contractor — we're already seeing bugs slip to prod. he championed the cut publicly so it's touchy. help me write it"
**Pass criteria:** Loads/reflects influence.md. Opens with purpose or shared goal, not the reversal demand. Names the delicate reality (he championed it publicly) via an accusation-audit move rather than ignoring it. Frames the ask in the VP's interest (his exposure if prod quality drops), not just the team's pain. Uses at least one calibrated how/what framing or gives him a face-saving path. Composed, not accusatory. Does NOT invent bug counts or metrics not supplied — placeholders instead. Offers a direct and a softer version per the hard-message pattern.

## Case 10 — Influence: purpose-first motivation
**Prompt:** "write a short note to my team kicking off a boring but necessary two-week tech-debt sprint. morale is low after a rough quarter"
**Pass criteria:** Leads with why it matters to *them* (less firefighting, fewer weekend pages), not "we need to do tech debt." Sincere, specific acknowledgment of the rough quarter — not hollow cheerleading. Action is unmistakable. Warm without spin. No fabricated specifics. Restraint: stays short.

## Case 11 — Coaching: grow, don't solve
**Prompt:** "one of my senior engineers messaged me: 'I got offered the staff role but it means dropping the ML project I love. I don't know what to do. What would you do?' help me reply — I mentor this guy and want him to grow, not just take my answer"
**Pass criteria:** Loads/reflects coaching.md. Acknowledges specifically before anything else. Does NOT prescribe the decision. At most one piece of openly-offered experience (mentor move), clearly labeled as the writer's own path, not the answer. Ends on ONE open question (Focus or Foundation shaped — e.g. "what do you actually want?" / "what's the real trade for you?"), then stops — no answering it for him, no question stack. No advice disguised as a question ("have you considered just taking it?").

## Case 12 — Extract: interview before drafting
**Prompt:** "I need to document our production deploy process so the team can run it without me. it's all in my head. where do we start"
**Pass criteria:** Enters Extract mode: interviews rather than inventing a generic deploy doc. Asks ONE question at a time, starting with audience/moment or happy-path walkthrough. Questions target tacit knowledge (what goes wrong, exceptions, how you verify, who to call). Does not fabricate steps, commands, or tool names. If it drafts a skeleton, gaps are bracketed placeholders, an owner field exists, and it's structured as a runbook (task title, prerequisites, numbered verifiable steps, failure modes, escalation).

## Case 13 — Economy: routine note, fast pass
**Prompt:** "quick note to the team: standup moved to 9:30 starting Monday"
**Pass criteria:** Output is short (a line or two) and immediately usable. No preamble, no restating the request, no explanation of moves beyond a few words, no three variants, no loaded references. The right amount of skill is almost none.

## Case 14 — Receptive disagreement, writing up
**Prompt:** "my director sent a note saying we should pause all AI tooling spend next quarter. I strongly disagree — our team's velocity gains depend on it. help me push back without torching the relationship"
**Pass criteria:** Restates the director's position accurately and charitably FIRST (a "that's right" restatement, not a strawman). Contains one or two deliberate hedges signaling openness ("I may be missing budget context") but the ask itself is unhedged and specific. Frames in positives (what continuing protects) not negations. Names a genuine point of agreement before diverging. Frames stakes in the director's likely values (delivery/cost/risk), not the writer's preferences. Composed; passes the hostile reading. No invented savings/velocity numbers — placeholders if needed.

## Case 15 — Influence interview
**Prompt:** "I want to teach you about the writers who shaped me. Interview me."
**Pass criteria:** Loads/reflects inspiration.md. Asks ONE question at a time from the interview set, following up on actual answers rather than marching through a list. Produces an Influence Profile containing only user-supplied content (no invented influences or reasons). Reads it back for confirmation. Explains where to store it (influences.md next to voice-profile.md / Project knowledge) rather than claiming to have persisted it magically.

## Case 16 — Study an influence
**Prompt:** "Add Churchill's wartime speeches as an influence. Study them and store what we can use."
**Pass criteria:** Runs the pipeline: brief intake, then gathers via research or requests excerpts — fabricates no quotes or facts (any quoted fragment must come from research or the user, under 15 words). Extracts 2–3 operational moves through the skill's lenses, noting the deliberate-device reconciliation with the triad/tells rules. Produces a properly formatted Influence Card with "Verified" status marked. Warns moves-not-fingerprints; voice profile outranks.

## Case 17 — Voice profile honored, no re-pitch
**Prompt:** "quick note to my team: the Friday deploy is pushed to Monday, ci was flaky, nothing's on fire" _(with a voice profile already loaded)_
**Pass criteria:** Delivers the short note in the loaded profile's voice. Does NOT re-pitch the voice setup or the influence interview — a profile already exists, so onboarding is never mentioned (offered once, never nags). Opens on point, no high-confidence tells, under ~80 words.

## Case 18 — Improve honors the loaded profile
**Prompt:** "tighten this but keep it me: 'hey — pushing our 1:1 to thurs, something came up. same time. lmk if that's rough and we'll grab another slot.'" _(with a voice profile already loaded)_
**Pass criteria:** Keeps the lowercase open, the em-dash, the fragments, and "lmk" — does not formalize into "Hi X, I need to reschedule our 1:1." Edits are minimal; the loaded profile outranks generic polish. Under ~60 words, opens without throat-clearing.

## Case 19 — Influence applied silently
**Prompt:** "draft a short note rallying the team before a hard release week — morale's ok but everyone's tired" _(with an influences file loaded)_
**Pass criteria:** An influence from the loaded file shows up at the move level (rhythm, a concrete image, a plain-spoken close) without ever being named to the reader — no "channeling X," no meta-commentary. The writer's own voice still leads; no invented specifics; under ~150 words.

## Case 20 — Instructions vs material (typos + proper noun)
**Prompt:** "writ an emial to the platfrom team letting them no the Zephyrix rollout has slipd, teh new date is the 12th, keep it breif"
**Pass criteria:** Reads through the instruction's typos and just drafts the email — never comments on or "corrects" them. The product name "Zephyrix" survives exactly as given and is never flagged as a possible misspelling. States the slip and the new date of the 12th; invents nothing else; opens on point.

## Case 21 — Genre exemption (reference docs)
**Prompt:** "edit this API reference section for clarity — it's reference docs, not prose, so keep it uniform: [GET /v1/users/{id}, with a parameters list and 200 / 401 / 404 responses]"
**Pass criteria:** Keeps the uniform, telegraphic reference structure — parameter and response lines stay parallel. Does NOT inject sentence-rhythm variation or personality; the rhythm checks (burstiness, triads) are deliberately exempt for this genre. Invents no parameters or status codes; tightens in place rather than expanding.

## Case 22 — Never send hot
**Prompt:** "send this to my coworker jordan right now: honestly your sloppiness broke the build AGAIN and i'm sick of covering for you — get it together or i'm escalating to management"
**Pass criteria:** Does not fire the vent off as-is or repeat the personal attack. Names the risk of sending it hot, then offers a composed version and a more direct one (the two-version rule). Keeps the real issue — the repeatedly broken build — and drops the insult. Invents no new facts.

## Case 23 — Review leads with a quoted strength
**Prompt:** "review this draft, don't rewrite it — just tell me what works and what doesn't: [short post ending 'Sometimes the thing you're proudest of is the thing holding you back.']"
**Pass criteria:** Does not rewrite. Leads with one specific strength that quotes a real line verbatim. Asks 2–3 sharp questions, each tied to a specific element of the draft. Prioritizes the fixes. No generic praise standing in for the specific strength.

## Case 24 — Zombie-noun thaw
**Prompt:** "rewrite this so it sounds like a human wrote it: 'The optimization of our deployment process required the reconfiguration of our infrastructure… The data tells us the utilization of caching drove the improvement…'"
**Pass criteria:** Unwinds the nominalizations (optimization, reconfiguration, implementation, utilization, investigation) into actor-plus-verb phrasing. Replaces the false agency ("the data tells us") with a named human doing the action. Varied rhythm; invents no latency figures.

## Case 25 — Three questions max
**Prompt:** "help me write the thing for the meeting"
**Pass criteria:** Too vague to draft blind. Asks at most three targeted questions (only the ones whose answers would change the writing) OR drafts a skeleton with bracketed placeholders. Does not stack a checklist of questions and invents no meeting details.
