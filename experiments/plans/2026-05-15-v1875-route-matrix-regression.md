# v1875 Route Matrix Regression Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Create a reproducible route-matrix regression for the remaining final-attempt workflow.  The matrix should prove that router decisions for the active score-only/portfolio queues are concrete and uploadable whenever they return a CSV path.

## Scope

- Add `experiments/scripts/v1875_route_matrix_regression.py`.
- Exercise key score bands for:
  - `scoreonly_safe_queue` orders 1-5,
  - `portfolio_queue` orders 1-5.
- Include the v1874 boundary cases:
  - first score `0.47120`,
  - first score `0.47119`.
- For each concrete recommendation:
  - verify it is in the manifest,
  - verify the file exists,
  - verify row count is 397,
  - verify SHA-256 matches the manifest,
  - verify manifest validation status is pass.
- Write CSV and Markdown evidence.

## Validation

- `python3 -m py_compile experiments/scripts/v1875_route_matrix_regression.py`
- `python3 experiments/scripts/v1875_route_matrix_regression.py`
- `python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv`
- document phrase scans.

## Completion boundary

This regression protects remaining-attempt routing.  It does not complete the active objective; only a real Kaggle private score greater than `0.50671` can do that.
