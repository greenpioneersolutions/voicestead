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

| Surface | Fixture/Check | Layer |
|---------|---------------|-------|
| `connection=None` no-op | `test_wellformed` + `test_connected_cases` | pytest / free tier |
| error handling (broken/limited/errors) | `test_connected_cases` | pytest / free tier |
| persona inference & override | `run_connected_evals.py` | live matrix / on-demand |
| voice profile creation | `run_connected_evals.py` | live matrix / on-demand |
| memory connectivity health | `test_connected_cases` + `run_studio_evals.py` | both tiers |
| link resolution (docs integrity) | `check_links.py` | pytest / free tier |
