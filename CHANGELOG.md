# Changelog

All notable changes to Voicestead are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Versions v5 through v9 predate semver — they were the skill's internal revisions, promoted here from the eval guide's change log. Plugin packaging began at 0.9.0.

## [0.9.0] — Unreleased

The pre-launch packaging release: the skill got a real home, a real installer, and a real regression net. No behavior claims are published yet — the blind win-rate scorecard is **pending S0** (the real-writing eval hasn't been run this cycle; no invented number goes here).

### Added
- **Plugin packaging.** `.claude-plugin/plugin.json` and `marketplace.json`, so `/plugin marketplace add` + `/plugin install` works as a one-command door. `claude plugin validate` passes.
- **`evals.json` mirror.** The harness cases now mirror into `skills/voicestead/evals/evals.json` so the native skill-eval loop can run them as isolated subagents, alongside the deeper harness.
- **Golden scaffolding.** `tests/golden/` structure for capturing real prompts with human verdicts — the regression anchor and judge-calibration set.
- **Placeholder guard.** `scripts/check_placeholders.py` sweeps for the unresolved owner token so nothing half-filled ships; wired into CI.
- **S2 onboarding cases 17–19** covering offer-once behavior, voice-profile-loaded drafts, and influence-informed drafts.
- **Hardening cases 20–25** covering instructions-vs-material, genre exemption, never-send-hot,
  review-quotes-strength, zombie-noun thaw, and three-questions-max.
- **CI / test automation.** A `check` job on every push (repo-structure guard, Tier-1 corpus, a **dogfood** self-test that holds the skill's own prose to its own bar, `pytest` unit tests for the checks, and a `.skill` build artifact); a `golden` dispatch job that runs the S0 with/without benchmark on the 5 real fixtures; `release.yml` (a `v*` tag → validated GitHub Release with `voicestead.skill` attached); and `pr-eval.yml` (a sticky check-summary comment on PRs).

### Changed
- **Restructured to the plugin layout.** The skill moved under `skills/voicestead/`; the dev harness stays at `tests/` and never ships. Packaging zips only the skill.
- **S1 description tuning.** Sharpened the skill's trigger description so it fires on real "make this sound like me" prompts without over-firing.
- **S2 onboarding hardening.** Onboarding is now offered once and never nags; storage of personal files is described honestly on both surfaces (Claude Code writes local profile/influence files the skill rereads; claude.ai users add them to Project knowledge — no claim of magic persistence). Regression-guarded by the new `no_onboarding_pitch` check (a soft signal) and the `onboarding-nag` corpus fixture (case 17).
- **Docs.** Consolidated the throwaway per-phase plan docs into four durable docs — `docs/ARCHITECTURE.md`, `docs/USING.md`, `docs/LAUNCH.md`, `docs/BETA.md`. Removed `PLAYBOOK.md` (folded into `LAUNCH.md`) and the internal `PROMPTS.md`.

### Toward 1.0.0
**v1.0.0 is the launch target**, and it is gated — plainly — on two things: **S0**, the real-writing eval producing a win-rate scorecard worth publishing (target ≥70%, zero hard-gate failures), and **S8**, a full regression pass with no previously-shipping golden case broken. Until both are green, this stays 0.9.0.

## [v9] — 2026-07
### Added
- Renamed the skill to **Voicestead**.
- **Influence system** — `inspiration.md` introduces the influence interview, the study-an-influence pipeline, and the `influences.md` storage standard. Cases 15–16.

## [v8] — 2026-07
### Added
- **Research integration** — `science.md` as the evidence base.
- Persuasion moves in `persuasion.md`: the narrative move, values reframing, the emotion dial.
- Influence craft in `influence.md`: the misread-tone law plus a hostile-reading test, a receptiveness recipe, and warmth-vs-firmness guidance.
- Case 14.
### Changed
- Refined the hedging rule after a failed-replication finding — the one negative result the project deliberately kept.

## [v7]
### Added
- **Extract mode** and `capture.md` (Diátaxis, interview-first docs).
- `coaching.md` (The Coaching Habit / GROW).
- An Economy section with honest token-cost findings.
- Cases 11–13.

## [v6]
### Added
- `influence.md` grounded in Sinek, Carnegie, Voss, and Goleman.
- Test cases 9–10.

## [v5]
### Added
- The full repository structure — modes, the curse-of-knowledge treatment, persuasion, voice capture, formats, and evals.
### Note
- Still untested against real writing at this point; that step (S0) was, and remains, the gate.
