# v1906 Goal Completion Gate

Generated UTC: `2026-05-14T19:15:34+00:00`

## Summary

- Goal complete: `no`
- Records consistent: `yes`
- Records path: `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv`
- Records count: `0`
- Best score: `none`
- Top-3 threshold: `>0.50671`

## Best record

```json
{}
```

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| records_exist | no | `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv` |
| records_within_attempt_budget | yes | `0` |
| score_values_valid | yes | `ok` |
| top3_flags_consistent | yes | `ok` |
| best_score_exceeds_threshold | no | `none` |

## Completion boundary

Only `GOAL_COMPLETE=yes` from this records-based gate is sufficient local evidence to allow marking the active goal complete.
