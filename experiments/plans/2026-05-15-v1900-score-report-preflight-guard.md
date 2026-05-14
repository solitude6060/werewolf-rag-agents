# v1900 Score Report Preflight Guard Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Make the final upload preflight verify that `current_upload/SCORE_REPORT.txt` matches the exact staged upload CSV, metadata, row count, SHA, candidate, group, and order.

## Risk

The staged CSV can be refreshed independently from score-report handoff files. If the score report is stale, the post-score command could record feedback for the wrong candidate context.

## Scope

- Add `experiments/scripts/v1900_current_upload_score_report_guard.py`.
- Validate `current_upload/SCORE_REPORT.txt` against `submission.csv` and `metadata.json`.
- Require the score placeholder before upload so a prior real score is not accidentally reused.
- Add regression coverage for valid template, wrong SHA, filled score, and wrong candidate.
- Wire the guard into `experiments/scripts/v1888_final_upload_preflight.py`.
- Update generated preflight report instructions to prefer the v1898 no-edit score bridge.

## Non-goals

- Do not upload to Kaggle.
- Do not record any score.
- Do not mark the active goal complete without a real recorded score greater than `0.50671`.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1900_current_upload_score_report_guard.py experiments/scripts/v1900_current_upload_score_report_guard_regression.py experiments/scripts/v1888_final_upload_preflight.py`
- `python3 experiments/scripts/v1900_current_upload_score_report_guard_regression.py`
- `python3 experiments/scripts/v1900_current_upload_score_report_guard.py`
- `python3 experiments/scripts/v1888_final_upload_preflight.py`
- Score-record file remains absent.

## Stop condition

The upload preflight fails if the score-report template is stale or already filled, and passes only when the score report matches the staged upload context.
