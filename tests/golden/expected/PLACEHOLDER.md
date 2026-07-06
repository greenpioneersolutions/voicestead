# Frozen verdicts land here (after S0)

One file per raw piece — `NN-<slug>.md` — containing:

- the with-skill output that shipped,
- the human labels: `ship` / `don't ship`, and `me` / `not me`,
- rubric scores (voice, point, truth, rhythm, tells, restraint),
- one line on *why*.

These become the regression anchor (S3) and the judge's few-shot calibration set. Until S0 runs, this directory is empty by design.
