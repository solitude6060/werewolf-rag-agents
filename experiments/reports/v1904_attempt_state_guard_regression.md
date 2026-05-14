# v1904 Attempt State Guard Regression

Date: 2026-05-15

## Summary

- Scenarios checked: `5`
- Failures: `0`

## Matrix

| Label | Exit code | Expected exit | Text found | Pass |
| --- | ---: | --- | --- | --- |
| no_records_first_upload_passes | `0` | `zero` | yes | yes |
| latest_recommended_match_passes | `0` | `zero` | yes | yes |
| latest_recommended_mismatch_rejected | `1` | `nonzero` | yes | yes |
| stop_record_rejected | `1` | `nonzero` | yes | yes |
| budget_exhausted_rejected | `1` | `nonzero` | yes | yes |

## Decision

The guard accepts the first upload or a staged latest recommendation, and rejects mismatched, stopped, or exhausted attempt states.

## Completion boundary

This regression validates local attempt-state readiness only. The active goal is complete only after a real private score greater than `0.50671` is recorded.
