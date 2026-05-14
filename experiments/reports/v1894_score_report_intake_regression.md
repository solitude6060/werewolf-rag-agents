# v1894 Score Report Intake Regression

Date: 2026-05-15

## Summary

- Scenarios checked: `6`
- Failures: `0`

## Matrix

| Label | Exit code | Expected exit | Text found | Pass |
| --- | ---: | --- | --- | --- |
| valid_top3_report | `0` | `zero` | yes | yes |
| valid_continue_report | `0` | `zero` | yes | yes |
| reject_wrong_sha | `1` | `nonzero` | yes | yes |
| reject_missing_real_private_flag | `1` | `nonzero` | yes | yes |
| reject_percentage_like_score | `1` | `nonzero` | yes | yes |
| reject_wrong_upload_path | `1` | `nonzero` | yes | yes |

## Decision

The intake validator accepts valid top-3/continue reports and rejects wrong SHA, missing real-private flag, percentage-like score, and wrong upload path before command-center routing.

## Completion boundary

This regression validates score-report intake only. The active goal is complete only after a real private score greater than `0.50671` is recorded.
