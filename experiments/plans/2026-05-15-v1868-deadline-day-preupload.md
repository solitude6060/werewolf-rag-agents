# v1868 Deadline-Day Pre-Upload Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Run a final deadline-day pre-upload audit for the current recommended Kaggle CSV before any remaining attempt is used.

## Inputs

- Current recommended upload queue: `scoreonly_safe_queue`.
- Runbook: `experiments/scripts/v1866_final_attempt_runbook.py`.
- Final package manifest: `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv`.
- Score-feedback records: `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv` if present.

## Validation

- Run the v1866 runbook with live validator.
- Confirm no real score-feedback record already exists.
- Confirm manifest still has all generated private CSVs with validator pass status and 397 rows.
- Confirm the first upload path and hash.
- Rerun submission-facing document scan after writing this audit.

## Completion boundary

This audit can confirm readiness to upload, but it cannot complete the active goal.  The goal is complete only after a real Kaggle private score greater than `0.50671` is reported and recorded.
