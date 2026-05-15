# v1925 Active Handoff Threshold Guard Regression

## Summary

- Scenarios: `3`
- Failures: `0`

## Matrix

| Label | Exit code | Expected exit | Text found | Pass |
| --- | ---: | --- | --- | --- |
| stale_file_rejected | `1` | `nonzero` | yes | yes |
| live_file_accepted | `0` | `zero` | yes | yes |
| real_active_paths_accepted | `0` | `zero` | yes | yes |

## Completion boundary

This regression only validates the stale-threshold guard. The active goal is complete only after a real private score greater than `0.52380` is recorded.
