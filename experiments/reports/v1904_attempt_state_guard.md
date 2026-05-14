# v1904 Attempt State Guard

Generated UTC: `2026-05-14T19:11:31+00:00`

## Summary

- Attempt state ready: `yes`
- State: `no_records_first_upload`
- Records count: `0`
- Recommended next: ``
- Current upload source: `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| manifest_exists | yes | `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| upload_rows_397 | yes | `397` |
| attempt_budget_not_exhausted | yes | `0` |
| no_prior_top3_hit | yes | `none` |
| first_upload_default_context | yes | `scoreonly_safe_queue#1` |
| first_upload_manifest_row_found | yes | `scoreonly_safe_queue#1` |
| current_source_matches_expected | yes | `current=experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv expected=experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` |
| current_group_matches_expected | yes | `current=scoreonly_safe_queue expected=scoreonly_safe_queue` |
| current_order_matches_expected | yes | `current=1 expected=1` |
| current_candidate_matches_expected | yes | `current=v1856g expected=v1856g` |
| current_upload_sha_matches_expected | yes | `upload=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d expected=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d` |
| metadata_sha_matches_expected | yes | `metadata=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d expected=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d` |

## Completion boundary

This guard only verifies upload attempt-state consistency. The active goal is complete only after a real private score greater than `0.50671` is recorded.
