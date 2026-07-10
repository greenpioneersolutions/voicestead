# Voicestead on Gemini (Gems)

A **Gem** is Gemini's reusable custom assistant — an instructions field plus knowledge files. This folder has both ingredients: `instructions.txt` and `knowledge/`.

## Build the Gem

1. In the Gemini app, open **Gem manager → New Gem** (Gems require an eligible Google account).
2. **Name** it `Voicestead`.
3. Open `instructions.txt` from this folder, copy all of it, and paste it into the **Instructions** field.
4. Under **Knowledge**, upload every file in the `knowledge/` folder (10 files — exactly at the Gem limit).
5. **Save.** To share, use the share control (email or link) — sharing works when the knowledge is uploaded files or Drive files.

## Make it yours

Ask for the **3-minute voice setup**, paste 2–3 things you actually wrote, and it builds a profile. Gems don't persist silently: paste the finished profile back into the **Instructions** field, or add it as an 11th knowledge file only if you first merge two of the existing references to stay within the 10-file cap.

## What's different here vs. Claude

Gemini retrieves from the uploaded knowledge files rather than loading a reference on demand. There's no script execution. See `../../docs/PLATFORMS.md` for the full per-surface limits.
