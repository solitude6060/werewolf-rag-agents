# v1919 v1826a Boundary Regression Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Add a direct regression for the current upload route (`queue#1`, `v1826a`) at exact score boundaries, so a returned score equal to a threshold is handled correctly and not mistaken for a top-3 completion.

## Current boundary contract

For the current `v1826a` upload:

- `score > 0.52380` => stop/top-3 candidate.
- `0.47200 <= score <= 0.52380` => route to `queue#2:v1826b`.
- `0.47050 <= score < 0.47200` => route to `contingency#1:v1825c`.
- `0.46500 <= score < 0.47050` => route to `contingency#2:v1825a`.
- `score < 0.46500` => route to `contingency#3:v1827a`.

## Constraints

- Use dry-run only; do not confirm or record synthetic scores.
- Do not stage a new upload.
- Verify official score-record SHA/count does not change.
- Treat `0.52380` as not complete because completion is strictly greater than the threshold.

## Method

1. Add `experiments/scripts/v1919_v1826a_boundary_regression.py`.
2. Execute `v1872_post_score_command_center.py --group queue --order 1 --score <boundary>` for exact boundary values.
3. Parse `top3_hit`, `recommended_next`, `NEXT_PATH_STATUS`, and `WRITE_STATUS`.
4. Assert expected route/status for each boundary.
5. Record CSV/MD evidence.

## Verification standard

- `python3 -m py_compile experiments/scripts/v1919_v1826a_boundary_regression.py`
- `python3 experiments/scripts/v1919_v1826a_boundary_regression.py`
- Expected: `SCENARIOS=8`, `FAILURES=0`, `RECORDS_UNCHANGED=yes`.
- Current upload validator still passes.

## Outputs

- `experiments/scripts/v1919_v1826a_boundary_regression.py`
- `experiments/reports/v1919_v1826a_boundary_regression.csv`
- `experiments/reports/v1919_v1826a_boundary_regression.md`

## Stop condition

Stop when exact current-upload score boundaries are covered by regression and no score records were mutated.
