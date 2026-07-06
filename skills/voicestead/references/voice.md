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
