# v1902 Upload Alias Guard Regression

Date: 2026-05-15

## Summary

- Scenarios checked: `4`
- Failures: `0`

## Matrix

| Label | Exit code | Expected exit | Text found | Pass |
| --- | ---: | --- | --- | --- |
| valid_alias_passes | `0` | `zero` | yes | yes |
| sha_mismatch_rejected | `1` | `nonzero` | yes | yes |
| missing_alias_rejected | `1` | `nonzero` | yes | yes |
| unsafe_lookalike_reported | `0` | `zero` | yes | yes |

## Decision

The guard accepts identical upload aliases, rejects missing or byte-different aliases, and reports unsafe submission.csv lookalikes without blocking the valid current upload.

## Completion boundary

This regression validates local wrong-file prevention only. The active goal is complete only after a real private score greater than `0.52380` is recorded.
