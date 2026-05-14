# v1887 Score Input Safety Regression

Date: 2026-05-15

## Summary

- Scenarios checked: `7`
- Failures: `0`
- Score feedback records existed before: `False`
- Score feedback records existed after: `False`
- Current upload SHA unchanged: `True`
- Current metadata SHA unchanged: `True`

## Matrix

| Label | Exit code | Expected exit | Text found | Pass |
| --- | ---: | --- | --- | --- |
| command_center_rejects_percentage_like_score | `1` | `nonzero` | yes | yes |
| command_center_rejects_nan_score | `1` | `nonzero` | yes | yes |
| command_center_rejects_negative_score | `1` | `nonzero` | yes | yes |
| command_center_rejects_bad_previous_score | `1` | `nonzero` | yes | yes |
| router_rejects_percentage_like_score | `1` | `nonzero` | yes | yes |
| valid_top3_dry_run_still_routes_stop | `0` | `zero` | yes | yes |
| valid_tiny_positive_dry_run_still_routes_next_csv | `0` | `zero` | yes | yes |

## Decision

Malformed score inputs are rejected before routing or recording, while valid dry-runs still route to the expected stop/next-candidate outcomes without mutating score records or staged upload files.

## Completion boundary

This safety regression does not complete the active score objective. Completion still requires a real Kaggle private score greater than `0.50671`.
