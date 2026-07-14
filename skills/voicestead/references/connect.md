# Connecting Voicestead Memory — the per-client guide

Load this when the user asks about memory, remembering, Studio, connecting, syncing across
devices, or why you don't know their voice — and when a call to a present Studio tool fails and the
fix is to reconnect. It carries the connect steps for each client and the one-line reconnect fixes
the error states point to. Connecting is a manual, one-time step the user does themselves: a skill
is only instructions — it can't add a connector or make an account. Frame it as turning on a
capability, never as a login to a paid backend. Never narrate tool mechanics.

## Which client is this?

The steps differ by client. If you already know which one the user is in, go straight to that
section. If you can't tell, ask one question — **"Are you in the Claude app, or Claude Code?"** —
and give only the matching guide. Don't print all three.

## Claude.ai and the mobile app

1. Open **Settings → Connectors** and choose **add a custom connector**.
2. For the server URL, enter **`https://mcp.voicestead.ai/mcp`**.
3. A browser tab opens — **sign in with the magic link** (no password).
4. Approve access when asked.
5. **The step people miss: turn the connector on for _this_ chat.** Adding it in settings is not
   enough — a connector added account-wide still has to be enabled for the current conversation.
   This is the single most common reason memory looks connected but does nothing. Open the current
   chat's connector control and switch Voicestead Memory on.

Then ask me to check the connection.

## Claude Desktop and Cowork

Same custom-connector mechanism as claude.ai, but the directory lives in the app itself:
**Settings → Connectors** in the desktop window (not a browser). Add the custom connector with the
URL **`https://mcp.voicestead.ai/mcp`**, sign in with the magic link, and approve access. As above,
make sure the connector is enabled for the conversation you're in — that's the step people miss.

Then ask me to check the connection.

## Claude Code

Run:

    claude mcp add --transport http voicestead https://mcp.voicestead.ai/mcp

That registers the remote connector. The first call hands off to your browser to sign in with the
magic link and approve access; if the browser doesn't open on its own, run `/mcp`, pick the
Voicestead Memory connector, and complete the sign-in there.

Then ask me to check the connection.

## The one-line reconnect fixes

When a connection that was working starts failing, the fix is usually one of these. Give the user
the line for their client, then finish their writing locally either way — never stall the draft on
the connection.

- **Needs a re-sign-in** (the session lapsed): reconnect using the steps above for your client — it
  re-runs the magic-link sign-in.
- **Missing a permission** (a capability wasn't approved): reconnect and, at the approval step,
  grant the permission that was skipped.
