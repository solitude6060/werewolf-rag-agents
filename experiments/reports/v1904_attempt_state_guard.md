# v1904 Attempt State Guard

Generated UTC: `2026-05-15T02:13:21+00:00`

## Summary

- Attempt state ready: `yes`
- State: `manual_override_from_records`
- Records count: `2`
- Recommended next: `experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv`
- Current upload source: `experiments/final_submission_package/overlay/08_v1840b_v1826d_high_precision_medium_ap_overlay_private.csv`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| manifest_exists | yes | `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| upload_rows_397 | yes | `397` |
| attempt_budget_not_exhausted | yes | `2` |
| no_prior_top3_hit | yes | `none` |
| latest_recommended_next_concrete | yes | `experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv` |
| latest_recommended_next_in_manifest | yes | `experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv` |
| manual_override_reason_present | yes | `post-v1826a 0.48854: only 3 recorded attempts remain; preserve the positive v1826a AP layer, add g23 via v1826d, and apply high-precision AP overlay for higher top-3 upside than diagnostic v1826b` |
| manual_override_row_found | yes | `overlay#8` |
| manual_override_not_already_uploaded | yes | `experiments/final_submission_package/overlay/08_v1840b_v1826d_high_precision_medium_ap_overlay_private.csv` |
| current_source_matches_expected | yes | `current=experiments/final_submission_package/overlay/08_v1840b_v1826d_high_precision_medium_ap_overlay_private.csv expected=experiments/final_submission_package/overlay/08_v1840b_v1826d_high_precision_medium_ap_overlay_private.csv` |
| current_group_matches_expected | yes | `current=overlay expected=overlay` |
| current_order_matches_expected | yes | `current=8 expected=8` |
| current_candidate_matches_expected | yes | `current=v1840b expected=v1840b` |
| current_upload_sha_matches_expected | yes | `upload=16d56e36317dfdbe3e2372754def6ddeda8182f4bbfdd6723e8018eaa8a911dc expected=16d56e36317dfdbe3e2372754def6ddeda8182f4bbfdd6723e8018eaa8a911dc` |
| metadata_sha_matches_expected | yes | `metadata=16d56e36317dfdbe3e2372754def6ddeda8182f4bbfdd6723e8018eaa8a911dc expected=16d56e36317dfdbe3e2372754def6ddeda8182f4bbfdd6723e8018eaa8a911dc` |

## Completion boundary

This guard only verifies upload attempt-state consistency. The active goal is complete only after a real private score greater than `0.52380` is recorded.
