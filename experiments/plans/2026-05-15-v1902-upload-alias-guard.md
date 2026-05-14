# v1902 Upload Alias Guard Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Ensure every likely manually selected upload CSV alias is byte-identical to the canonical current upload, so choosing the packaged hand-in CSV or final checkpoint cannot accidentally upload a different candidate.

## Risk

The browser upload dialog is manual. Even with a canonical path, it is easy to select `hw2_D13922024/submission.csv` or the final checkpoint instead of `experiments/final_submission_package/current_upload/submission.csv`. Those aliases must remain identical to avoid a wrong-file attempt.

## Scope

- Add `experiments/scripts/v1902_upload_alias_guard.py`.
- Compare canonical upload against:
  - `hw2_D13922024/submission.csv`
  - `hw2_D13922024/checkpoints/final_v1856g_private.csv`
- Check existence, row count, and SHA-256 equality.
- Add regression for valid aliases, SHA mismatch, and missing alias.
- Wire the guard into `experiments/scripts/v1888_final_upload_preflight.py`.

## Non-goals

- Do not upload to Kaggle.
- Do not alter candidate CSV content.
- Do not mark the active goal complete without a real recorded score greater than `0.50671`.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1902_upload_alias_guard.py experiments/scripts/v1902_upload_alias_guard_regression.py experiments/scripts/v1888_final_upload_preflight.py`
- `python3 experiments/scripts/v1902_upload_alias_guard_regression.py`
- `python3 experiments/scripts/v1902_upload_alias_guard.py`
- `python3 experiments/scripts/v1888_final_upload_preflight.py`

## Stop condition

The final preflight reports alias guard ready, and any manual upload path among the canonical/current/package/final-checkpoint CSVs resolves to the same bytes and 397-row submission.
