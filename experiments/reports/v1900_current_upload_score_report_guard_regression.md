# v1900 Current Upload Score Report Guard Regression

Date: 2026-05-15

## Summary

- Scenarios checked: `4`
- Failures: `0`

## Matrix

| Label | Exit code | Expected exit | Text found | Pass |
| --- | ---: | --- | --- | --- |
| valid_current_report_passes | `0` | `zero` | yes | yes |
| wrong_sha_rejected | `1` | `nonzero` | yes | yes |
| filled_score_rejected_before_upload | `1` | `nonzero` | yes | yes |
| wrong_candidate_rejected | `1` | `nonzero` | yes | yes |

## Decision

The guard accepts the current score report only when it matches the staged upload and rejects stale or pre-filled report contexts.

## Completion boundary

This regression validates local handoff integrity only. The active goal is complete only after a real private score greater than `0.50671` is recorded.
