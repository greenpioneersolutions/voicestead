# Connect Voicestead Memory

This is the **canonical** connection guide. The in-skill guide at
`skills/voicestead/references/connect.md` mirrors it — change one, change both.

Voicestead works entirely locally without this. Connecting turns on **Voicestead Memory** so your
voice and the lines that worked follow you across sessions and devices. It's a manual, one-time step
you do yourself — a skill is only instructions, so it can't add the connector or make an account for
you.

Pick your client.

## claude.ai and the mobile app

1. Open **Settings → Connectors** and choose **Add a custom connector**.
2. For the server URL, enter `https://mcp.voicestead.ai/mcp`.
3. A browser tab opens — sign in with the **magic link** (no password).
4. Approve access when asked.
5. **Turn the connector on for _this_ chat.** Adding it in settings is not enough — a connector
   added to your account still has to be enabled in the conversation you're writing in. This is the
   single most common reason memory looks connected but does nothing.

> 📷 *Screenshot: the "Add a custom connector" dialog with `https://mcp.voicestead.ai/mcp` in the URL field.*

> 📷 *Screenshot: the in-chat connector toggle, switched on for the current conversation.*

Then ask your Claude to check the connection.

## Claude Desktop and Cowork

Same custom-connector mechanism as claude.ai, but the settings live in the app itself:
**Settings → Connectors** in the desktop window, not a browser.

1. **Settings → Connectors → Add a custom connector**, URL `https://mcp.voicestead.ai/mcp`.
2. Sign in with the magic link and approve access.
3. Make sure the connector is **enabled for the conversation you're in** — the same step people miss
   on the web.

> 📷 *Screenshot: the desktop Settings → Connectors window.*

Then ask your Claude to check the connection.

## Claude Code

Run:

    claude mcp add --transport http voicestead https://mcp.voicestead.ai/mcp

That registers the remote connector. The first call hands off to your browser to sign in with the
magic link and approve access. If the browser doesn't open on its own, run `/mcp`, pick the
Voicestead Memory connector, and finish signing in there.

Then ask your Claude to check the connection.

## If something's off

Connected but it doesn't remember you, or can't read or save? Two things fix almost everything: make
sure the connector is **enabled for the current chat**, and **approve every permission** when you
sign in. The full list is in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
