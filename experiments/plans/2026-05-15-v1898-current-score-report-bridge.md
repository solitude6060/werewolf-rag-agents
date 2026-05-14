# v1898 Current Score Report Bridge Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Provide a one-command post-score path for the staged upload: accept the real Kaggle private score as `--score`, inject it into the current `SCORE_REPORT.txt` template, and route through the v1895 saved-report bridge.

## Risk

The v1897 handoff puts a ready-to-edit score report beside the upload file, but editing the placeholder manually can still introduce mistakes during the deadline window.

## Scope

- Add `experiments/scripts/v1898_current_score_report_bridge.py`.
- Read `experiments/final_submission_package/current_upload/SCORE_REPORT.txt` by default.
- Validate decimal score range before filling the report.
- Run `experiments/scripts/v1895_score_report_command_center.py` with the filled report.
- Keep default mode as dry-run and pass `--confirm-real-score` only when explicitly requested.
- Update current-upload README/metadata with the no-edit command.
- Add a regression covering valid continue, valid top-3, invalid score, missing placeholder, and no official-record mutation.

## Non-goals

- Do not upload to Kaggle.
- Do not record scores unless `--confirm-real-score` is explicitly passed.
- Do not mark the active score goal complete without a recorded real score greater than `0.50671`.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1898_current_score_report_bridge.py experiments/scripts/v1898_current_score_report_bridge_regression.py`
- `python3 experiments/scripts/v1898_current_score_report_bridge_regression.py`
- `python3 experiments/scripts/v1870_stage_current_upload.py`
- `python3 experiments/scripts/v1888_final_upload_preflight.py`
- Official score-record file remains absent after dry-run validation.

## Stop condition

A user can run one command with the real score, receive v1895/v1872 routing output, and still avoid score-record mutation unless confirmation is explicit.
