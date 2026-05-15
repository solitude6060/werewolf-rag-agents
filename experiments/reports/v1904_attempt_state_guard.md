# v1904 Attempt State Guard

Generated UTC: `2026-05-15T00:18:47+00:00`

## Summary

- Attempt state ready: `yes`
- State: `staged_latest_recommended`
- Records count: `1`
- Recommended next: `experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv`
- Current upload source: `experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| manifest_exists | yes | `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| upload_rows_397 | yes | `397` |
| attempt_budget_not_exhausted | yes | `1` |
| no_prior_top3_hit | yes | `none` |
| latest_recommended_next_concrete | yes | `experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv` |
| latest_recommended_next_in_manifest | yes | `experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv` |
| current_source_matches_expected | yes | `current=experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv expected=experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv` |
| current_group_matches_expected | yes | `current=scoreonly_safe_queue expected=scoreonly_safe_queue` |
| current_order_matches_expected | yes | `current=5 expected=5` |
| current_candidate_matches_expected | yes | `current=v1846g expected=v1846g` |
| current_upload_sha_matches_expected | yes | `upload=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb expected=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb` |
| metadata_sha_matches_expected | yes | `metadata=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb expected=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb` |

## Completion boundary

This guard only verifies upload attempt-state consistency. The active goal is complete only after a real private score greater than `0.50671` is recorded.
