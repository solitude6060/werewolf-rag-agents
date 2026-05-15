# v1919 v1826a Boundary Regression

Date: 2026-05-15

## Summary

- Scenarios checked: `8`
- Failures: `0`
- Records unchanged: `yes`
- Records count before/after: `1` / `1`

## Boundary matrix

| Label | Score | Expected top3 | Actual top3 | Expected status | Actual status | Write status | Pass |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| top3_strictly_above_threshold | `0.52381` | yes | yes | `non_concrete_ok` | `non_concrete_ok` | `dry_run_only` | yes |
| equal_threshold_is_not_complete | `0.52380` | no | no | `concrete_ok:queue#2:v1826b` | `concrete_ok:queue#2:v1826b` | `dry_run_only` | yes |
| positive_lower_bound_inclusive | `0.47200` | no | no | `concrete_ok:queue#2:v1826b` | `concrete_ok:queue#2:v1826b` | `dry_run_only` | yes |
| just_below_positive_to_neutral_diag | `0.47199` | no | no | `concrete_ok:contingency#1:v1825c` | `concrete_ok:contingency#1:v1825c` | `dry_run_only` | yes |
| neutral_diag_lower_bound_inclusive | `0.47050` | no | no | `concrete_ok:contingency#1:v1825c` | `concrete_ok:contingency#1:v1825c` | `dry_run_only` | yes |
| just_below_neutral_to_mild_regression | `0.47049` | no | no | `concrete_ok:contingency#2:v1825a` | `concrete_ok:contingency#2:v1825a` | `dry_run_only` | yes |
| mild_regression_lower_bound_inclusive | `0.46500` | no | no | `concrete_ok:contingency#2:v1825a` | `concrete_ok:contingency#2:v1825a` | `dry_run_only` | yes |
| just_below_mild_to_severe_fallback | `0.46499` | no | no | `concrete_ok:contingency#3:v1827a` | `concrete_ok:contingency#3:v1827a` | `dry_run_only` | yes |

## Decision

Exact current-upload boundaries are covered. A score equal to `0.52380` is not a completion; only a strictly greater score stops the goal route.

## Completion boundary

This regression is local routing evidence only. The active goal is complete only after a real private score greater than `0.52380` is recorded and the records-backed gate reports completion.
