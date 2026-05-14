# v1872 Post-Score Command Center Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Add one safe command for the moment after a real Kaggle private score appears.  It should:

- preview the router decision,
- optionally record the score only when explicitly confirmed as real,
- show the remaining attempt budget,
- refresh `current_upload/submission.csv` from score records when a concrete next file exists,
- regenerate the final attempt cockpit card.

## Why

The deadline-day workflow now has reliable components, but after a score appears it still requires several manual commands in the right order.  This wrapper reduces missed steps while preserving the existing safety gate: no real record is written unless the user passes an explicit confirmation flag.

## Scope

- Add `experiments/scripts/v1872_post_score_command_center.py`.
- Default mode is dry-run only.
- Default upload context is read from `experiments/final_submission_package/current_upload/metadata.json`, so the score is routed against the fixed file that was actually staged for upload.
- `--group` and `--order` remain available for explicit override; both must be passed together.
- Require `--confirm-real-score` for any call that writes score-feedback records.
- Do not upload anything.
- Do not stage another upload if the router recommends a stop/manual state.

## Validation

- `python3 -m py_compile experiments/scripts/v1872_post_score_command_center.py`
- Dry-run with score `0.48000`.
- Dry-run with score `0.50672`.
- Confirm that the real score-feedback records file is still absent after dry-runs.
- Run staged CSV validator and document phrase scans.

## Completion boundary

This command center only improves the post-score workflow.  It cannot complete the active objective unless it records a real Kaggle private score greater than `0.50671`, and that has not happened yet.
