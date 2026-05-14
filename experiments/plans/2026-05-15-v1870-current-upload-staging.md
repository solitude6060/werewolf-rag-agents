# v1870 Current Upload Staging Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Stage the current recommended upload CSV into a single fixed path so the final manual Kaggle upload does not require selecting from many candidate folders.

## Problem

The final package now contains many validated candidates.  Even with the runbook, a manual file picker can still select the wrong CSV.  A fixed `current_upload/submission.csv` with metadata and checksum reduces this operational risk.

## Scope

- Add `experiments/scripts/v1870_stage_current_upload.py`.
- Default source: `scoreonly_safe_queue` order 1 from the manifest.
- Optional source: latest feedback record's concrete `recommended_next` path.
- Copy selected CSV to `experiments/final_submission_package/current_upload/submission.csv`.
- Write `metadata.json` and `README.md` with source path, candidate, group/order, SHA-256, row count, validator result, and next router command.
- Validate the staged CSV.

## Validation

- `python3 -m py_compile experiments/scripts/v1870_stage_current_upload.py`
- `python3 experiments/scripts/v1870_stage_current_upload.py`
- `python3 experiments/scripts/v1870_stage_current_upload.py --from-records --records /tmp/v1869_records_one.csv --out-dir /tmp/v1870_test_current_upload`
- `python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv`
- Confirm staged SHA-256 matches source SHA-256.
- Rerun document scans.

## Completion boundary

Staging a CSV helps prevent upload mistakes but does not complete the active goal.  Completion still requires a real Kaggle private score greater than `0.50671`.
