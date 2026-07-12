# Publishing the one-click versions (ChatGPT GPT + Gemini Gem)

Everything under [`../exports/`](../exports/README.md) is a *build-it-yourself* bundle: a reader pastes the instructions and uploads the knowledge file. That's the honest floor, and it works today.

**True one-click — where someone clicks a link and just starts typing, nothing to paste or upload — is a different thing.** ChatGPT Custom GPTs and Gemini Gems have no importable config file, so the only way to hand someone a ready-made one is to *host* it: build it once from your own account and share the link. This page is the ~5-minute how-to. You only do it once (and again when the skill changes materially).

---

## 1. ChatGPT — publish a shared Custom GPT

1. Build the GPT exactly as in [`../exports/chatgpt/SETUP.md`](../exports/chatgpt/SETUP.md) → **Option A** (instructions + the single `knowledge-bundle.md` + conversation starters).
2. **Create → Save**, then set sharing:
   - **Anyone with the link** — enough for one-click; no builder verification needed.
   - **Publish to the GPT Store** — makes it discoverable, but needs a verified builder profile (a verified name, or the `voicestead.ai` domain).
3. Copy the resulting share/store URL.

**Caveats to know before you promise one-click:**
- Users still need a ChatGPT account. Whether a *free* account can run a shared GPT (vs. needing Plus) is inconsistent across reports — test with a logged-out/free account before you advertise it.
- The knowledge is baked in at publish time. When you change the skill, rebuild the GPT (see §3).

## 2. Gemini — publish a shared Gem

1. Build the Gem as in [`../exports/gemini/SETUP.md`](../exports/gemini/SETUP.md) (instructions + the single `knowledge-bundle.md`).
2. Use the Gem's **share** control (link or email). Sharing works because the knowledge is an uploaded file (not a chat attachment).
3. Copy the share link.

**Caveats:** the recipient may get a view/copy rather than a live Gem, and may need to save their own copy — confirm the flow before advertising it.

## 3. Wire the links into the README

Once you have the two URLs, make the [main README](../README.md) install table one-click:

- In the **ChatGPT** row, change `paste 1 box · upload 1 file` to `[▶ Open in ChatGPT](<your GPT url>)`.
- In the **Gemini** row, change `paste 1 box · upload 1 file` to `[▶ Open in Gemini](<your Gem url>)`.
- Delete (or soften) the "Want true one-click …" note above the table, since it's now live.

Keep the 3-minute build sections below the table — they're the fallback for anyone who wants their own copy or can't open a shared GPT.

## 4. Keep them in sync

The hosted GPT/Gem are **snapshots**. They don't auto-update when the skill does. When `skills/voicestead/SKILL.md` changes and you regenerate exports (`python3 -m scripts.build_exports`), the hosted copies are stale until you rebuild them: re-paste the new `instructions.txt` and re-upload the new `knowledge-bundle.md`. Note the skill version you published against so you know when a refresh is due.

---

*Why not automate this?* There's no ChatGPT/Gemini API that creates a GPT or Gem from a file — building them is a manual step in each product's UI, tied to your account. The bundles remove every bit of friction that *can* be removed from a file; publishing removes the rest, and only you can do it.
