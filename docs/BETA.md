# Voicestead Studio — Beta

Studio is a connector that gives the skill a memory. Right now Voicestead reads your voice profile and influences from plain files each run. Studio keeps those, plus your drafts and your verdicts, across sessions — so the skill remembers your voice and the writers who shaped you without you re-pasting them, and it can learn from what you approved last time.

**A note on names.** *Studio* is the product — the private memory, taste, and receipts layer. *Voicestead Memory* is the capability you turn on to use it: the connector your Claude signs into. When the skill offers to "turn on Voicestead Memory," that's the front door to Studio.

Concretely, it adds:

- **Persistent voice memory** across sessions, so your profile and influences carry over instead of living in files you have to attach.
- **A record of your drafts and verdicts** — what you wrote, what you approved, what you rejected — so the skill can weigh your past calls when it drafts the next thing.
- **Import** of writing you already have, so the skill starts from your real work instead of a cold start.

## Status: beta is open

The beta is **open and free**. Studio runs as a hosted connector — an MCP server at **`mcp.voicestead.ai`** that your Claude connects to over MCP, with magic-link sign-in at `app.voicestead.ai`. The skill side is built too: the free skill already knows how to turn on Voicestead Memory and drive it — loading your profile, retrieving the right past lines, logging what you approve, keeping receipts — the moment the connector is present.

The standalone skill works fully today, with or without Studio. Studio is an enhancement, never a dependency. Every mode — draft, improve, extract, review — runs the same on its own, and a session with no connector behaves exactly as it does now. If Studio never loaded for you, you'd lose the cross-session memory and nothing else.

## How to connect

Connecting is a one-time, **manual** step you do in Claude's connector settings. The skill can't create your account or add the connector for you — it's only instructions — but it *will* walk you through the exact steps for your client and check the connection once it's in. Ask it how to connect and it hands you the right guide; you're never left waiting on it.

1. In Claude's **connector settings**, add `mcp.voicestead.ai`.
2. A browser tab opens at `app.voicestead.ai` — sign in with a **magic link** (no password).
3. Approve access ("Allow Claude to access your Voicestead Memory").
4. The Memory tools light up in your session — about two minutes, no config.

Per-client steps (claude.ai, Desktop, Claude Code) and the one thing people miss — turning the connector on for the *current chat* — are in [CONNECT.md](../CONNECT.md). Stuck? [TROUBLESHOOTING.md](../TROUBLESHOOTING.md).

Prefer to follow along or flag a problem? [Watch the repo](https://github.com/greenpioneersolutions/voicestead) for release news, or [open an issue](https://github.com/greenpioneersolutions/voicestead/issues) with how you'd use it and anything that got in your way.

## What it will not change

Your voice profile and your influences stay yours. Studio persists them for you; it doesn't pool them, share them, or train anything shared on them. They're personal by design — that's the point of a voice, and it doesn't change when the storage does.
