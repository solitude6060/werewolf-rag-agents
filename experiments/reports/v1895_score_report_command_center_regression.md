# v1895 Score Report Command Center Regression

Date: 2026-05-15

## Summary

- Scenarios checked: `4`
- Failures: `0`
- Official records unchanged: `True`

## Matrix

| Label | Exit code | Expected exit | Text found | Pass |
| --- | ---: | --- | --- | --- |
| valid_continue_report_dry_runs_next_csv | `0` | `zero` | yes | yes |
| valid_top3_report_dry_runs_stop | `0` | `zero` | yes | yes |
| invalid_wrong_sha_stops_before_command_center | `1` | `nonzero` | yes | yes |
| invalid_real_flag_stops_before_command_center | `1` | `nonzero` | yes | yes |

## Decision

The bridge routes valid SCORE_REPORT files through the command-center dry-run and rejects invalid reports before routing, without mutating official score records.

## Completion boundary

This regression validates the dry-run bridge only. The active goal is complete only after a real private score greater than `0.50671` is recorded.
