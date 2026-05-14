# v1908 Final Goal Status Console Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Provide a single read-only command that combines the records-based completion gate and upload preflight into one operator-facing status: mark complete, upload current, or blocked.

## Risk

The workflow now has strong separate gates, but a deadline operator can still misread which one is decisive. A single status command reduces confusion between readiness (`READY_TO_MANUAL_UPLOAD=yes`) and completion (`GOAL_COMPLETE=yes`).

## Scope

- Add `experiments/scripts/v1908_final_goal_status.py`.
- Run `v1906_goal_completion_gate.py` and `v1888_final_upload_preflight.py` with temporary outputs.
- Output one action:
  - `MARK_GOAL_COMPLETE` if the records-based gate says complete.
  - `UPLOAD_CURRENT` if goal is not complete but final preflight is ready.
  - `BLOCKED` otherwise.
- Add regression coverage for completion, upload-ready, and blocked preflight cases without mutating official records.

## Non-goals

- Do not upload to Kaggle.
- Do not write score records.
- Do not call `update_goal`; this command only tells whether it is allowed.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1908_final_goal_status.py experiments/scripts/v1908_final_goal_status_regression.py`
- `python3 experiments/scripts/v1908_final_goal_status_regression.py`
- `python3 experiments/scripts/v1908_final_goal_status.py`
- Score records remain absent in the current no-score state.

## Stop condition

The status console returns `ACTION=UPLOAD_CURRENT` for the current no-record ready state, returns `MARK_GOAL_COMPLETE` in regression for a consistent top-3 record, and returns `BLOCKED` when preflight is not ready.
