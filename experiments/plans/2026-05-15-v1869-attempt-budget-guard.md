# v1869 Attempt Budget Guard Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Add a small local guard that reads score-feedback records and reports how many of the final five attempts have been used, how many remain, the best real score recorded so far, whether the top-3 target has been hit, and the next safe action.

## Why

The active objective is explicitly constrained by a small number of remaining Kaggle attempts.  The existing router and runbook pick the next file, but they do not summarize the attempt budget or stop condition across all recorded attempts.

## Scope

- Add `experiments/scripts/v1869_attempt_budget_guard.py`.
- Default record source: `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv`.
- Support `--records` for temporary validation files.
- Support `--max-attempts`, default `5`.
- Report:
  - attempts used,
  - attempts remaining,
  - best recorded score,
  - whether any score is `>0.50671`,
  - latest recommended next path or stop/manual state.
- Follow-up after v1870: also print the staging command so `current_upload/submission.csv` is refreshed before each later manual upload.

## Validation

- `python3 -m py_compile experiments/scripts/v1869_attempt_budget_guard.py`
- No-records case.
- One-record next-file case.
- Top-3 hit case.
- Five-record exhausted case.
- Rerun document scans.

## Completion boundary

This guard can detect a top-3 score if it is present in records, but it cannot complete the active goal unless the record is based on a real Kaggle private score.  The current validation uses temporary records only.
