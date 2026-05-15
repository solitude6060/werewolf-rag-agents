# v1904 Attempt State Guard Regression

Date: 2026-05-15

## Summary

- Scenarios checked: `7`
- Failures: `0`

## Matrix

| Label | Exit code | Expected exit | Text found | Pass |
| --- | ---: | --- | --- | --- |
| no_records_first_upload_passes | `0` | `zero` | yes | yes |
| latest_recommended_match_passes | `0` | `zero` | yes | yes |
| latest_recommended_mismatch_rejected | `1` | `nonzero` | yes | yes |
| stop_record_rejected | `1` | `nonzero` | yes | yes |
| five_records_manual_override_with_open_budget_passes | `0` | `zero` | yes | yes |
| five_real_records_manual_override_after_non_concrete_passes | `0` | `zero` | yes | yes |
| fifteen_records_budget_exhausted_rejected | `1` | `nonzero` | yes | yes |

## Decision

The guard accepts the first upload, a staged latest recommendation, or a documented manual override after non-concrete router output while the expanded attempt budget remains open.

## Completion boundary

This regression validates local attempt-state readiness only. The active goal is complete only after a real private score greater than `0.52380` is recorded.
