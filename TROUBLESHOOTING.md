# Troubleshooting

Voicestead works locally with no setup. These are the things that trip people up once they turn on
**Voicestead Memory**. Connection steps for every client are in [CONNECT.md](CONNECT.md).

## "It says I need a connector / it doesn't remember me"

**Cause:** the connector isn't added — or, far more often, it's added to your account but **not
enabled for this chat**.

**Fix:**
1. Open the current conversation's connector control and switch **Voicestead Memory** on.
2. If it isn't in the list, add it first — see [CONNECT.md](CONNECT.md).
3. Ask your Claude to check the connection.

## "It was working, now it isn't"

**Cause:** the session expired.

**Fix:**
1. Reconnect through the same connector entry — it re-runs the magic-link sign-in.
2. Ask your Claude to check the connection.

## "It connected but can't read or save"

**Cause:** a permission wasn't approved when you signed in.

**Fix:**
1. Reconnect via [CONNECT.md](CONNECT.md).
2. At the approval step, approve **all** the permissions it asks for.

## "The skill isn't triggering at all"

**Cause:** the skill isn't installed or enabled in this client.

**Fix:**
1. Reinstall it with the Install step for your client in the [README](README.md).
2. Confirm it's enabled, then start a new message.

## "My line didn't get saved"

**Cause:** it was probably **held for your review** — the safety screen working, not a failure.

**Fix:**
1. Open `app.voicestead.ai` and keep or discard the held line.

## Still stuck?

Open an issue: https://github.com/greenpioneersolutions/voicestead/issues
