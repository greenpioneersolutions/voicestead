# Voicestead exports — paste-ready bundles for other platforms

Voicestead is a Claude Skill. These folders let it run elsewhere. Each bundle is generated from the one canonical skill (`../skills/voicestead/`), so it stays in sync — see `../docs/ARCHITECTURE.md`.

| Platform | Folder | Install |
|---|---|---|
| **ChatGPT** (Custom GPT or Project) | [`chatgpt/`](chatgpt/SETUP.md) | Paste `instructions.txt`, upload the single `knowledge-bundle.md` |
| **Gemini** (Gem) | [`gemini/`](gemini/SETUP.md) | Paste `instructions.txt`, upload the single `knowledge-bundle.md` |
| **AGENTS.md tools** (Codex, Copilot, Cursor, Zed, Amp) | [`agents/`](agents/SETUP.md) | One `curl` into your repo root |
| **Skill-native tools** (Cursor, Codex, Copilot, Gemini CLI, Windsurf) | — | Copy `../skills/voicestead/` into `.agents/skills/` |
| **Claude Code / claude.ai** | — | See the [main README](../README.md) (plugin, folder copy, or `.skill`) |

**One-click on ChatGPT/Gemini** (click a link, nothing to paste) needs a hosted GPT/Gem published once from a Voicestead account — see [`../docs/PUBLISHING.md`](../docs/PUBLISHING.md). Each `knowledge-bundle.md` is the ten references in one file; the split `knowledge/` folder is still there if your platform retrieves better over separate documents.

## What each surface keeps

| Capability | Claude (native) | Skill-native tools | ChatGPT / Gemini | AGENTS.md |
|---|---|---|---|---|
| On-demand reference loading | ✅ | ✅ | ⚠️ retrieval (RAG) | ❌ (repo links) |
| Voice-profile persistence | ✅ file | ✅ file | ⚠️ paste into instructions | ⚠️ in the file |
| One-click / copy install | ✅ plugin | copy folder | paste + upload | copy one file |
| Script execution | ✅ | ✅ | ❌ | ❌ |

`⚠️` = works with a caveat; see `../docs/PLATFORMS.md` for the honest limits.

## Regenerating

The derived files (`*/instructions.txt`, `*/knowledge/`, `agents/AGENTS.md`) are built by `../scripts/build_exports.py`. Don't hand-edit them. After changing the skill, re-condense `core.md`, then:

```bash
python -m scripts.build_exports --reseal   # after editing SKILL.md and re-condensing core.md
python -m scripts.build_exports            # rebuild the bundles
```
