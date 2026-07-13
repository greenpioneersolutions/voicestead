# Voicestead Studio — Beta

Studio is a connector that gives the skill a memory. Right now Voicestead reads your voice profile and influences from plain files each run. Studio keeps those, plus your drafts and your verdicts, across sessions — so the skill remembers your voice and the writers who shaped you without you re-pasting them, and it can learn from what you approved last time.

**A note on names.** *Studio* is the product — the private memory, taste, and receipts layer. *Voicestead Memory* is the capability you turn on to use it: the connector your Claude signs into. When the skill offers to "turn on Voicestead Memory," that's the front door to Studio.

Concretely, it adds:

- **Persistent voice memory** across sessions, so your profile and influences carry over instead of living in files you have to attach.
- **A record of your drafts and verdicts** — what you wrote, what you approved, what you rejected — so the skill can weigh your past calls when it drafts the next thing.
- **Import** of writing you already have, so the skill starts from your real work instead of a cold start.

## Status: in development

Studio is not shipped. The beta is not open yet, and there is no date to give you — announcing one before it's true would break the same rule this skill exists to enforce.

When it opens, Studio runs as a hosted connector — an MCP server at **`mcp.voicestead.ai`** that your Claude connects to over MCP. The domain is decided; the service isn't live yet, and the exact connector endpoint lands when the beta opens.

The standalone skill works fully today, with or without Studio. Studio is an enhancement, never a dependency. Every mode — draft, improve, extract, review — runs the same on its own, and a session with no connector behaves exactly as it does now. If Studio never loaded for you, you'd lose the cross-session memory and nothing else.

## How to request access

Three honest options while it's in development:

- **Watch or star [the repo](https://github.com/greenpioneersolutions/voicestead).** Release news posts there first — watching is the surest way to hear when the beta opens.
- **Open a [GitHub issue](https://github.com/greenpioneersolutions/voicestead/issues)** describing how you'd use it. Real use cases shape what ships and who gets early access. Tell us what you write, where the file-based setup gets in your way, and what you'd want Studio to remember.
- **Join the waitlist at [voicestead.ai](https://voicestead.ai)** once it's live. The site isn't up yet; when it is, the waitlist feeds the beta list directly.

## What it will not change

Your voice profile and your influences stay yours. Studio persists them for you; it doesn't pool them, share them, or train anything shared on them. They're personal by design — that's the point of a voice, and it doesn't change when the storage does.
