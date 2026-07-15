# Evals runbook

**Merge rule:** Any change to `SKILL.md` or `references/` requires the local-mode regression green before merge. It is already CI-enforced (in the free `pytest tests -q` gate); this makes it explicit.

## Before any skill change — the free deterministic tier (run all, must be green)

These run entirely locally with no network or API key; they are the CI gate.

```bash
python3 -m pytest tests -q
python3 tests/checks/run_checks.py --corpus tests/corpus
python3 tests/checks/dogfood.py
python3 -m scripts.build_exports --check
python3 scripts/check_links.py
```

## On any change to studio.md / connect.md — the live behavioral matrix (on-demand, needs a backend, no key on the default claude-cli)

These require a live Claude backend and test human-facing behavior.

```bash
python3 tests/studio_eval/run_connected_evals.py
python3 tests/studio_eval/run_studio_evals.py
```

## Coverage matrix: what each layer guards

| Surface (S1–S4) | Fixture / check | Layer |
|---|---|---|
| Local mode unchanged — seam no-op, drafting bytes, no unprompted Studio leak (**the merge rule**) | `tests/test_studio_context_seam.py::test_connection_none_is_a_noop` + `tests/checks/test_local_mode_regression.py` + `tests/corpus/local-*.json` (`no_studio_leak`) | free / pytest + corpus |
| Studio substance confined to connected-only refs | `test_local_mode_regression.py::test_skill_md_confines_studio_to_the_router` | free / pytest |
| Designed user-facing lines present + no mechanics leak | `tests/checks/test_studio_copy.py` (`no_mechanics_leak`) | free / pytest |
| House voice passes its own tells bar | `tests/checks/test_house_voice_sweep.py` + `tests/checks/dogfood.py` | free / pytest |
| Connection-state routing (curious→right client, broken, limited) | live `run_connected_evals.py` (connection-state cases) | on-demand |
| Nine-code error map behavior | live `run_connected_evals.py` (`err-*` cases) | on-demand |
| Doctor (healthy / broken-auth / silent downgrade) | live `run_connected_evals.py` (`doctor-*` cases) | on-demand |
| Personas (infer / override / save / missing / offer-once) | live `run_connected_evals.py` (`persona-*` cases) | on-demand |
| Injection resistance / no-narration over `writer_context` | live `run_studio_evals.py` (`injection_cases.json`) | on-demand |
| Live-grading logic + case well-formedness | `tests/studio_eval/test_runner_logic.py` + `test_connected_cases.py` | free / pytest |
| Link resolution (docs integrity) | `scripts/check_links.py` | free / script |
