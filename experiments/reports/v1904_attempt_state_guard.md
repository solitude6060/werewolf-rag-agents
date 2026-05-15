# v1904 Attempt State Guard

Generated UTC: `2026-05-15T00:33:12+00:00`

## Summary

- Attempt state ready: `yes`
- State: `manual_override_from_records`
- Records count: `1`
- Recommended next: `experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv`
- Current upload source: `experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv`

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
| manual_override_reason_present | yes | `skip score-only v1846g after v1856g real private score 0.42894; updated top3 threshold is 0.52380; pivot to structural v1826a for upside` |
| manual_override_row_found | yes | `queue#1` |
| manual_override_not_already_uploaded | yes | `experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv` |
| current_source_matches_expected | yes | `current=experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv expected=experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv` |
| current_group_matches_expected | yes | `current=queue expected=queue` |
| current_order_matches_expected | yes | `current=1 expected=1` |
| current_candidate_matches_expected | yes | `current=v1826a expected=v1826a` |
| current_upload_sha_matches_expected | yes | `upload=e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad expected=e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad` |
| metadata_sha_matches_expected | yes | `metadata=e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad expected=e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad` |

## Completion boundary

This guard only verifies upload attempt-state consistency. The active goal is complete only after a real private score greater than `0.52380` is recorded.
