# v1902 Upload Alias Guard Regression

Date: 2026-05-15

## Summary

- Scenarios checked: `3`
- Failures: `0`

## Matrix

| Label | Exit code | Expected exit | Text found | Pass |
| --- | ---: | --- | --- | --- |
| valid_alias_passes | `0` | `zero` | yes | yes |
| sha_mismatch_rejected | `1` | `nonzero` | yes | yes |
| missing_alias_rejected | `1` | `nonzero` | yes | yes |

## Decision

The guard accepts identical upload aliases and rejects missing or byte-different aliases.

## Completion boundary

This regression validates local wrong-file prevention only. The active goal is complete only after a real private score greater than `0.50671` is recorded.
