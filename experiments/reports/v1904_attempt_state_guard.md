# v1904 Attempt State Guard

Generated UTC: `2026-05-15T03:34:49+00:00`

## Summary

- Attempt state ready: `yes`
- State: `manual_override_from_records`
- Records count: `5`
- Recommended next: `NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.`
- Current upload source: `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| manifest_exists | yes | `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| upload_rows_397 | yes | `397` |
| attempt_budget_not_exhausted | yes | `5` |
| no_prior_top3_hit | yes | `none` |
| latest_recommended_next_concrete_or_manual_override | yes | `manual_override; concrete=False; recommended_next=NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.` |
| manual_override_from_non_concrete_latest | yes | `NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.` |
| manual_override_reason_present | yes | `extra ten-submit restart after prior 5/5 records; isolate v1842e black-boost delta from failed rolecap v1846e; v1842e differs from best v1840c by 3 score-only rows and is not a duplicate` |
| manual_override_row_found | yes | `black_boost_queue#5` |
| manual_override_not_already_uploaded | yes | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` |
| current_source_matches_expected | yes | `current=experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv expected=experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` |
| current_group_matches_expected | yes | `current=black_boost_queue expected=black_boost_queue` |
| current_order_matches_expected | yes | `current=5 expected=5` |
| current_candidate_matches_expected | yes | `current=v1842e expected=v1842e` |
| current_upload_sha_matches_expected | yes | `upload=6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f expected=6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f` |
| metadata_sha_matches_expected | yes | `metadata=6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f expected=6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f` |

## Completion boundary

This guard only verifies upload attempt-state consistency. The active goal is complete only after a real private score greater than `0.52380` is recorded.
