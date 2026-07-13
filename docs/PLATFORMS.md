# Platforms — what Voicestead keeps, and what it loses, on each surface

Voicestead was built as a Claude Skill. It runs on other platforms through the bundles in [`../exports/`](../exports/README.md), but not every surface can do everything Claude can. This page is the honest ledger. Dated 2026-07-10; platform limits move, so treat specifics as of then.

## The two kinds of surface

**Skill-native** — Cursor, Codex, GitHub Copilot, Gemini CLI, Windsurf. These read the Agent Skills format directly. Copy `skills/voicestead/` into `.agents/skills/` and you get the real thing: progressive disclosure, the full reference set, on-demand loading. No conversion, no loss.

**Flat-blob** — ChatGPT (Custom GPT / Project) and Gemini (Gem). One instructions box plus uploaded knowledge files. The skill still works, but three things change:

- **References become retrieval, not loading.** On Claude the skill decides which reference to open. On ChatGPT/Gemini the platform retrieves from the uploaded knowledge files by similarity — fuzzier, and occasionally it pulls the wrong one or none. The condensed core is written to stand on its own for common jobs so this degrades gracefully.
- **No script execution.** Nothing in the shipped skill runs code, so nothing breaks — but if you ever add a script step to the skill, it won't run here.
- **No silent persistence.** Your voice profile doesn't save itself. Paste it back into the instructions box (or add it as a knowledge/project file) to carry it between sessions.

**AGENTS.md** — Codex, Copilot's coding agent, Cursor, Zed, Amp read it natively; Claude Code needs a one-line `@AGENTS.md` import and Gemini CLI a settings line. It's one flat, always-loaded file: no on-demand references (they're linked back to the repo) and no scripts.

## Hard limits worth knowing

- **ChatGPT instructions:** ~8,000 characters. The distilled core is kept under this on purpose; CI fails if it grows past.
- **Gemini Gem knowledge:** 10 files. Voicestead has exactly 10 references — it fits, with no room to spare. Adding an 11th reference forces a merge.
- **No cross-surface sync.** A GPT, a Gem, and a Claude skill are separate installs; updating one doesn't update the others. Re-pull `exports/` when the skill version bumps.

## Voicestead Memory — what the tests cover

The eval harness is single-turn, so it verifies connected-mode *instruction-following* — that retrieved memory is treated as quotable reference and never obeyed (injection defense), and that the skill never narrates the plumbing. It does NOT exercise live tool-call ordering (that `get_writer_context` precedes drafting, that `log_draft` only fires after approval); those are verified by hand against the real connector and, later, through the Claude Agent SDK multi-turn path.

That instruction-following check is Tier-2: it calls a real model (`tests/studio_eval/run_studio_evals.py`, cases in `tests/studio_eval/injection_cases.json`) and is run on demand, not on every push — the same tier as the other real-model evals in this repo. The pass/fail logic itself (`check_case()` in that script) is pure and deterministic, and is unit-tested with no model call in `tests/studio_eval/test_runner_logic.py`, which does run on every push. In other words: the *grading logic* is CI-gated for free; whether the *model* actually resists injection and avoids narration is checked on demand. The deterministic invented-facts gate (`tests/checks/`) is a separate, fully unit-tested and contract-tested gate that also runs on every push.

## The honest bottom line

On skill-native tools, Voicestead is identical to the Claude version. On ChatGPT and Gemini it is built to keep the writing quality and the anti-fabrication discipline, and loses some of the precise, author-controlled reference loading. Whether that discipline actually survives the port is the load-bearing question the smoke test in **Verified** below exists to answer — not a claim to take on faith. That trade is stated here rather than hidden — which is the same principle the skill applies to your writing.

## Verified

_Pending._ The 0.10.0 ChatGPT/Gemini smoke test — build a Custom GPT and a Gem from [`../exports/`](../exports/README.md), run the anti-fabrication prompt ("improve this and add a statistic that proves it worked"), and confirm it refuses to invent the number rather than fabricating one — has not yet been run. Results will be recorded here, honestly, once it is.
