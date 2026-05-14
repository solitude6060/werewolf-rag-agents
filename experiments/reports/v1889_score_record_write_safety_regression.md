# v1889 Score Record Write Safety Regression

Date: 2026-05-15

## Summary

- Scenarios checked: `6`
- Failures: `0`
- Real score-record files touched: `no`

## Matrix

| Label | Expected allowed | Actual allowed | Pass |
| --- | --- | --- | --- |
| empty_ledger_allows_first_record | yes | yes | yes |
| four_records_allows_fifth_record | yes | yes | yes |
| five_records_rejects_sixth_record | no | no | yes |
| existing_top3_hit_rejects_followup_record | no | no | yes |
| exact_duplicate_rejected | no | no | yes |
| same_candidate_different_score_allowed | yes | yes | yes |

## Decision

The score-record append guard rejects duplicate exact records, a sixth final-attempt record, and any follow-up write after a recorded top-3 hit while preserving valid first/fifth-record writes.

## Completion boundary

This regression protects the attempt ledger, but it does not complete the active score objective. Completion still requires a real Kaggle private score greater than `0.50671`.
