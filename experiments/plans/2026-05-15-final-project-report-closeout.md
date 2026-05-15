# Final Project and Report Closeout Plan

## Goal

Prepare the final homework project package and report after all five final leaderboard attempts are exhausted.

## Current scoring facts

- Attempts used: `5/5`.
- Final failed attempt: `v1846e = 0.46698`.
- Best verified private score: `v1840c = 0.49349`.
- Updated operational target `>0.50000`: not achieved.
- Original top-three target `>0.52380`: not achieved.

## Packaging decision

The final coursework package should default to the best verified candidate, not the failed last attempt.

- Final packaged candidate: `v1840c`.
- Last failed experiment retained in the report: `v1846e`.
- `submission.csv`, `checkpoints/final_current_private.csv`, and the one-command `make_final.py --output submission.csv` path must reproduce the same best-candidate bytes.

## Required updates

1. Record the last real private score in the score-feedback ledger.
2. Restage the package default to best known `v1840c`.
3. Update `hw2_D13922024/README.md` to state final best candidate and exhausted-attempt context.
4. Update `hw2_D13922024/hw2_report.md` with final score trajectory, method summary, and failure analysis.
5. Preserve all final-attempt history and failed last-shot evidence under `experiments/`.
6. Run package reproduction, validator, report/document scan, and sensitive-wording scan.

## Validation standard

- `python3 hw2_D13922024/make_final.py --output /tmp/<file>.csv` produces the same SHA as `hw2_D13922024/submission.csv`.
- `python3 hw2_D13922024/assert/validate_submission.py hw2_D13922024/submission.csv` returns `OK: 397 predictions validated`.
- Score ledger has `5` records and best score `0.49349`.
- No tracked report/package file contains risky authorship wording or powered-by-agent phrasing.
- `git status --short -uno` is clean after commit.

## Stop condition

Stop after the final project/report package is committed and the user is given:

- final package path,
- final best candidate and score,
- validation commands and results,
- known failed target status.
