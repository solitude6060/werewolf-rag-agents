# v1904 Attempt State Guard

Generated UTC: `2026-05-15T01:55:55+00:00`

## Summary

- Attempt state ready: `yes`
- State: `staged_latest_recommended`
- Records count: `2`
- Recommended next: `experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv`
- Current upload source: `experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv`

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
| current_source_matches_expected | yes | `current=experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv expected=experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv` |
| current_group_matches_expected | yes | `current=queue expected=queue` |
| current_order_matches_expected | yes | `current=2 expected=2` |
| current_candidate_matches_expected | yes | `current=v1826b expected=v1826b` |
| current_upload_sha_matches_expected | yes | `upload=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b expected=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b` |
| metadata_sha_matches_expected | yes | `metadata=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b expected=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b` |

## Completion boundary

This guard only verifies upload attempt-state consistency. The active goal is complete only after a real private score greater than `0.52380` is recorded.
