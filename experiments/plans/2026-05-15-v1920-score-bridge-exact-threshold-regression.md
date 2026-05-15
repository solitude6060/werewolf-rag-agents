# v1920 Score Bridge Exact Threshold Regression Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Extend the score-report bridge regressions so the exact current top-3 cutoff `0.52380` is tested at the v1895/v1898 handoff layer, not only at the lower router layer.

## Boundary contract

- `0.52380` is equal to the live cutoff and must continue routing; it is **not** completion.
- `0.52381` is strictly greater and may become a top-3 completion candidate after real-score confirmation.

## Constraints

- Dry-run only; do not confirm synthetic scores.
- Official score records must remain byte-identical.
- Current upload must remain `v1826a` / `queue#1`.

## Method

1. Add an exact-threshold dry-run case to `v1898_current_score_report_bridge_regression.py`.
2. Add an exact-threshold dry-run case to `v1895_score_report_command_center_regression.py`.
3. Rerun both regressions and verify records are unchanged.
4. Keep v1919 router-boundary regression as the lower-level route proof.

## Verification standard

- `python3 -m py_compile experiments/scripts/v1898_current_score_report_bridge_regression.py experiments/scripts/v1895_score_report_command_center_regression.py`
- `python3 experiments/scripts/v1898_current_score_report_bridge_regression.py` -> `SCENARIOS=5`, `FAILURES=0`, `OFFICIAL_RECORDS_UNCHANGED=yes`.
- `python3 experiments/scripts/v1895_score_report_command_center_regression.py` -> `SCENARIOS=5`, `FAILURES=0`, `OFFICIAL_RECORDS_UNCHANGED=yes`.
- Current upload validator still passes.

## Outputs

- Updated `experiments/scripts/v1898_current_score_report_bridge_regression.py`
- Updated `experiments/scripts/v1895_score_report_command_center_regression.py`
- Updated `experiments/reports/v1898_current_score_report_bridge_regression.*`
- Updated `experiments/reports/v1895_score_report_command_center_regression.*`

## Stop condition

Stop when both score-report bridge regressions prove exact-threshold equality continues routing and records remain unchanged.
