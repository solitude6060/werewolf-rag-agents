# v1890 Confirm Score Sandbox Regression

Date: 2026-05-15

## Summary

- Scenarios checked: `5`
- Failures: `0`
- Official score records existed before: `False`
- Official score records existed after: `False`
- Official score records untouched: `True`

## Matrix

| Label | Exit code | Sandbox records | Pass |
| --- | ---: | ---: | --- |
| first_confirm_write_succeeds_in_sandbox | `0` | `1` | yes |
| duplicate_confirm_rejected_in_sandbox | `1` | `1` | yes |
| top3_confirm_writes_stop_record_in_sandbox | `0` | `1` | yes |
| post_top3_followup_confirm_rejected_in_sandbox | `1` | `1` | yes |
| sixth_confirm_rejected_in_sandbox | `1` | `5` | yes |

## Decision

The real confirmed-write path can write a first sandbox score, rejects exact duplicates, records top-3 stop state, rejects post-top-3 follow-up writes, and rejects a sixth final-attempt write without touching official records.

## Completion boundary

This sandbox verifies local score-record behavior only. The active score objective still requires a real Kaggle private score greater than `0.50671`.
