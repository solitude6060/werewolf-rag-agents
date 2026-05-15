# v1906 Goal Completion Gate

Generated UTC: `2026-05-15T03:37:24+00:00`

## Summary

- Goal complete: `no`
- Records consistent: `yes`
- Records path: `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv`
- Records count: `5`
- Best score: `0.49349`
- Top-3 threshold: `>0.52380`

## Best record

```json
{
  "candidate": "v1840c",
  "delta_vs_current_best": "+0.02230",
  "group": "overlay",
  "order": "9",
  "recommended_next": "experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv",
  "recorded_at_utc": "2026-05-15T02:25:22+00:00",
  "score": "0.49349",
  "top3_hit": "no",
  "uploaded_path": "experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv"
}
```

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| records_exist | yes | `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv` |
| records_within_attempt_budget | yes | `5` |
| score_values_valid | yes | `ok` |
| top3_flags_consistent | yes | `ok` |
| best_score_exceeds_threshold | no | `0.49349` |

## Completion boundary

Only `GOAL_COMPLETE=yes` from this records-based gate is sufficient local evidence to allow marking the active goal complete.
