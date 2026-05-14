# v1904 Attempt State Preflight Guard Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Make the final upload preflight valid for all remaining attempts, not only the first upload with no score records.

## Risk

The current preflight has a first-upload check that expects no score-feedback records. After the first real score is recorded and the next candidate is staged, the same preflight should validate that `current_upload` matches the latest `recommended_next` instead of failing only because records exist.

## Scope

- Add `experiments/scripts/v1904_attempt_state_guard.py`.
- Accept no-records state for the first upload.
- When score records exist, require the latest `recommended_next` to be a concrete CSV and require current upload metadata/SHA/rows to match that manifest row.
- Reject STOP/non-concrete recommendations and exhausted attempt budget as upload-not-ready states.
- Add regression coverage for no-records, matched latest recommendation, mismatched latest recommendation, STOP, and budget exhausted.
- Replace the v1888 first-upload-only records check with the new adaptive guard.

## Non-goals

- Do not upload to Kaggle.
- Do not write score records.
- Do not stage files.
- Do not mark the active goal complete without a real recorded score greater than `0.50671`.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1904_attempt_state_guard.py experiments/scripts/v1904_attempt_state_guard_regression.py experiments/scripts/v1888_final_upload_preflight.py`
- `python3 experiments/scripts/v1904_attempt_state_guard_regression.py`
- `python3 experiments/scripts/v1904_attempt_state_guard.py`
- `python3 experiments/scripts/v1888_final_upload_preflight.py`

## Stop condition

The final preflight can pass for the current no-record first upload and has regression evidence that it will pass only when later attempts are staged to the latest concrete router recommendation.
