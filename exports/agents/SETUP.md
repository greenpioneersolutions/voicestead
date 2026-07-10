# Voicestead as AGENTS.md

`AGENTS.md` is the cross-tool instruction file read natively by Codex, GitHub Copilot's coding agent, Cursor, Zed, Amp, and others. Drop this folder's `AGENTS.md` where your tool looks for it.

## Install

Copy `AGENTS.md` to your project root (or merge it into an existing one — the nearest `AGENTS.md` to a file wins):

```bash
cp AGENTS.md /path/to/your/project/AGENTS.md
```

Codex, Copilot coding agent, Cursor, Zed, and Amp pick it up automatically.

## Two tools need a one-line shim

- **Claude Code** reads `CLAUDE.md`, not `AGENTS.md`. Point it at this file:
  ```bash
  printf '@AGENTS.md\n' >> CLAUDE.md
  ```
- **Gemini CLI** defaults to `GEMINI.md`. Add `AGENTS.md` to its context in `.gemini/settings.json`:
  ```json
  { "context": { "fileName": ["AGENTS.md", "GEMINI.md"] } }
  ```

## Prefer the native skill instead

If your tool supports Agent Skills (Cursor, Codex, Copilot, Gemini CLI, Windsurf all do), skip AGENTS.md and drop the **whole skill folder** into `.agents/skills/` — you keep progressive disclosure and the full references instead of this flattened digest:

```bash
cp -r ../../skills/voicestead /path/to/your/project/.agents/skills/voicestead
```

## What's different here vs. Claude

AGENTS.md is one flat, always-loaded file: no on-demand reference loading (the footer links to the full references in the repo) and no script execution. See `../../docs/PLATFORMS.md`.
