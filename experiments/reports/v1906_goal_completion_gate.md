# v1906 Goal Completion Gate

Generated UTC: `2026-05-15T00:40:56+00:00`

## Summary

- Goal complete: `no`
- Records consistent: `yes`
- Records path: `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv`
- Records count: `1`
- Best score: `0.42894`
- Top-3 threshold: `>0.52380`

## Best record

```json
{
  "candidate": "v1856g",
  "delta_vs_current_best": "-0.04225",
  "group": "scoreonly_safe_queue",
  "order": "1",
  "recommended_next": "experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv",
  "recorded_at_utc": "2026-05-15T00:14:10+00:00",
  "score": "0.42894",
  "top3_hit": "no",
  "uploaded_path": "experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv"
}
```

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| records_exist | yes | `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv` |
| records_within_attempt_budget | yes | `1` |
| score_values_valid | yes | `ok` |
| top3_flags_consistent | yes | `ok` |
| best_score_exceeds_threshold | no | `0.42894` |

## Completion boundary

Only `GOAL_COMPLETE=yes` from this records-based gate is sufficient local evidence to allow marking the active goal complete.
