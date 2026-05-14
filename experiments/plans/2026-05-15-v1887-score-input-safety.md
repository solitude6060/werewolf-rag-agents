# v1887 Score Input Safety Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Prevent malformed post-score inputs from corrupting the final-attempt records or accidentally creating a false top-3 completion signal.

## Risk

The score router and command center accept numeric CLI input. A user could accidentally type a percentage-like value such as `47.119` instead of `0.47119`, or pass `nan`/`inf`. That would be a local input error, not a real private leaderboard result.

## Scope

- Add decimal score range validation to the post-score command center.
- Add the same validation to the underlying feedback router.
- Add a regression script that checks invalid score inputs are rejected and dry-runs do not mutate score records or staged upload files.

## Non-goals

- Do not upload to Kaggle.
- Do not write score records.
- Do not change the staged upload candidate.
- Do not infer goal completion from local command success.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1836_score_feedback_router.py experiments/scripts/v1872_post_score_command_center.py experiments/scripts/v1887_score_input_safety_regression.py`
- `python3 experiments/scripts/v1887_score_input_safety_regression.py`
- `python3 experiments/scripts/v1882_command_center_dry_run_regression.py`
- `python3 experiments/scripts/v1875_route_matrix_regression.py`

## Stop condition

The work is complete when malformed scores are rejected, valid dry-run routing remains green, score records remain absent, current upload SHA is unchanged, and the active goal remains open until a real private score above `0.50671` exists.
