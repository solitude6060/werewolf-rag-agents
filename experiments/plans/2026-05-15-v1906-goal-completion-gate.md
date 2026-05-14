# v1906 Goal Completion Gate Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Add a strict records-based completion gate for the active leaderboard objective, so the goal can be marked complete only when an official local score record proves a real private score greater than `0.50671`.

## Risk

The project now has many green readiness checks. Those checks are proxies and must not be confused with the actual objective. After the user reports a score, the operator needs a single local command that says whether `update_goal` is allowed.

## Scope

- Add `experiments/scripts/v1906_goal_completion_gate.py`.
- Read `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv` by default.
- Validate score values, `top3_hit` consistency, and record count/budget.
- Output `GOAL_COMPLETE=yes` only when at least one valid recorded score is strictly greater than `0.50671`.
- Add regression coverage for no records, below-threshold records, above-threshold records, inconsistent flags, invalid scores, and budget overflow.
- Update current-upload README/metadata to run the gate after a confirmed score record.

## Non-goals

- Do not upload to Kaggle.
- Do not write score records.
- Do not call `update_goal`; this script only reports whether it is allowed.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1906_goal_completion_gate.py experiments/scripts/v1906_goal_completion_gate_regression.py experiments/scripts/v1870_stage_current_upload.py`
- `python3 experiments/scripts/v1906_goal_completion_gate_regression.py`
- `python3 experiments/scripts/v1906_goal_completion_gate.py`
- `python3 experiments/scripts/v1870_stage_current_upload.py`
- `python3 experiments/scripts/v1888_final_upload_preflight.py`

## Stop condition

The gate returns `GOAL_COMPLETE=no` for the current no-record state, returns `yes` for a consistent top-3 record in regression, rejects inconsistent records, and the active goal remains open until real records satisfy the gate.
