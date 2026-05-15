# v1904 Attempt State Guard

Generated UTC: `2026-05-15T02:19:12+00:00`

## Summary

- Attempt state ready: `yes`
- State: `staged_latest_recommended`
- Records count: `3`
- Recommended next: `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv`
- Current upload source: `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| manifest_exists | yes | `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| upload_rows_397 | yes | `397` |
| attempt_budget_not_exhausted | yes | `3` |
| no_prior_top3_hit | yes | `none` |
| latest_recommended_next_concrete | yes | `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv` |
| latest_recommended_next_in_manifest | yes | `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv` |
| current_source_matches_expected | yes | `current=experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv expected=experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv` |
| current_group_matches_expected | yes | `current=overlay expected=overlay` |
| current_order_matches_expected | yes | `current=9 expected=9` |
| current_candidate_matches_expected | yes | `current=v1840c expected=v1840c` |
| current_upload_sha_matches_expected | yes | `upload=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145 expected=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145` |
| metadata_sha_matches_expected | yes | `metadata=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145 expected=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145` |

## Completion boundary

This guard only verifies upload attempt-state consistency. The active goal is complete only after a real private score greater than `0.52380` is recorded.
