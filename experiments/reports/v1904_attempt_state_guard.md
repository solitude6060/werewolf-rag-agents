# v1904 Attempt State Guard

Generated UTC: `2026-05-15T02:27:34+00:00`

## Summary

- Attempt state ready: `yes`
- State: `manual_override_from_records`
- Records count: `4`
- Recommended next: `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv`
- Current upload source: `experiments/final_submission_package/rolecap_queue/05_v1846e_queue05_v1842e_rolecap099_private.csv`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| manifest_exists | yes | `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| upload_rows_397 | yes | `397` |
| attempt_budget_not_exhausted | yes | `4` |
| no_prior_top3_hit | yes | `none` |
| latest_recommended_next_concrete | yes | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` |
| latest_recommended_next_in_manifest | yes | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` |
| manual_override_reason_present | yes | `last chance target 0.5 after v1840c=0.49349; override router v1842e to v1846e because role-cap keeps labels fixed and has stronger public AP/LOO evidence for crossing 0.5` |
| manual_override_row_found | yes | `rolecap_queue#5` |
| manual_override_not_already_uploaded | yes | `experiments/final_submission_package/rolecap_queue/05_v1846e_queue05_v1842e_rolecap099_private.csv` |
| current_source_matches_expected | yes | `current=experiments/final_submission_package/rolecap_queue/05_v1846e_queue05_v1842e_rolecap099_private.csv expected=experiments/final_submission_package/rolecap_queue/05_v1846e_queue05_v1842e_rolecap099_private.csv` |
| current_group_matches_expected | yes | `current=rolecap_queue expected=rolecap_queue` |
| current_order_matches_expected | yes | `current=5 expected=5` |
| current_candidate_matches_expected | yes | `current=v1846e expected=v1846e` |
| current_upload_sha_matches_expected | yes | `upload=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912 expected=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912` |
| metadata_sha_matches_expected | yes | `metadata=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912 expected=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912` |

## Completion boundary

This guard only verifies upload attempt-state consistency. The active goal is complete only after a real private score greater than `0.52380` is recorded.
