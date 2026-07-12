# Voicestead on ChatGPT

Two ways to run Voicestead in ChatGPT. A **Custom GPT** is shareable and reusable; a **Project** is a lighter, personal option. Both use the same two ingredients from this folder: `instructions.txt` (the skill) and `knowledge/` (the references it consults).

## Option A — Custom GPT (shareable)

1. In ChatGPT, open **Explore GPTs → Create** (or **My GPTs → Create a GPT**).
2. Go to the **Configure** tab.
3. **Name** it `Voicestead` and add a short description (e.g. "Writing that sounds like you and never invents a fact").
4. Open `instructions.txt` from this folder, copy all of it, and paste it into the **Instructions** box. (It is kept under ChatGPT's ~8,000-character limit on purpose.)
5. Under **Knowledge**, upload the single `knowledge-bundle.md` — **one file** with every reference in it. (Prefer finer retrieval? Upload the ten separate files in `knowledge/` instead. Either works; don't upload both.)
6. Paste the four lines from `conversation-starters.txt` into **Conversation starters**.
7. Under **Capabilities**, leave **Web Search** on if you want it to study a public writer; the rest are optional.
8. **Create → Save.** Choose **Only me**, **Anyone with the link**, or **Publish to the GPT Store**.

## Option B — Project (personal)

1. In the ChatGPT sidebar, click **+ → New project**.
2. Open **Instructions** and paste the contents of `instructions.txt`.
3. **Add files** and upload `knowledge-bundle.md` (one file), or the ten files in `knowledge/`.
4. Start a chat inside the project — the instructions and files apply to every chat in it.

## Make it yours

Voicestead sounds generic until it has your voice. Ask it for the **3-minute voice setup**, paste 2–3 things you actually wrote, and it builds a profile. On ChatGPT there's no silent persistence: paste the finished profile back into the **Instructions** box (Custom GPT) or add it as a project file (Project) so it carries over.

## What's different here vs. Claude

ChatGPT retrieves from the uploaded knowledge files instead of loading a reference on demand, so the match is fuzzier than on Claude. There's no script execution. See `../../docs/PLATFORMS.md` for the full list of per-surface limits.
