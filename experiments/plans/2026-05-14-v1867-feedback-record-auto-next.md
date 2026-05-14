# v1867 Feedback Record Auto-Next Plan

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Goal

Extend the final-attempt runbook so it can read the latest real score-feedback record and automatically validate the next recommended CSV.  This avoids manually transcribing a `recommended_next` path after each Kaggle score.

## Problem

v1866 prints the default first upload and can preview a router result for an entered score.  After a real score is recorded with `v1836_score_feedback_router.py --confirm-real-score`, the next upload path is stored in `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv`.  Without automation, the user must copy that path manually into the next upload workflow.

## Scope

- Add `--from-records` to `experiments/scripts/v1866_final_attempt_runbook.py`.
- Add `--records` to allow testing with a temporary records file.
- If the latest record's `recommended_next` is a real package CSV path, find the manifest row by `output_path` and validate it.
- If the latest record says STOP or manual review, print that state and exit without pretending a next upload exists.
- Keep default behavior unchanged when no record is requested.

## Validation

- `python3 -m py_compile experiments/scripts/v1866_final_attempt_runbook.py`
- Default runbook still validates order 1.
- Temporary records file with a next path resolves to order 2 and validates.
- Temporary records file with STOP returns a stop state.
- No real `v1836_score_feedback_records.csv` is written by validation.
- Rerun document scans.

## Completion boundary

This improves execution reliability only.  The active goal still requires a real private score greater than `0.50671`.
