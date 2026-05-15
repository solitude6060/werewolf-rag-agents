# v1883 Pre-Upload Guard

Date: 2026-05-15

## Summary

- Upload ready: `yes`
- Attempt context: `followup_from_records`
- Upload path: `experiments/final_submission_package/current_upload/submission.csv`
- Candidate: `rolecap_queue` order `5` (`v1846e`)
- SHA-256: `c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912`
- Rows: `397`
- Stop if real score is greater than: `0.52380`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| manifest_exists | yes | `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv` |
| current_upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| score_records_present_for_followup | yes | `4` |
| latest_recommended_next_is_csv | yes | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` |
| attempt_state_guard_ready | yes | `ATTEMPT_STATE_GUARD; ATTEMPT_STATE_READY=yes; STATE=manual_override_from_records; RECORDS_COUNT=4; RECOMMENDED_NEXT=experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv; CURRENT_SOURCE_PATH=experiments/final_submission_package/rolecap_queue/05_v1846e_queue05_v1842e_rolecap099_private.csv; UPLOAD_ROWS=397; UPLOAD_SHA256=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912; REPORT=experiments/reports/v1904_attempt_state_guard.md; JSON=experiments/reports/v1904_attempt_state_guard.json` |
| manifest_row_found | yes | `rolecap_queue#5` |
| manifest_candidate_matches | yes | `v1846e` |
| manifest_status_pass | yes | `pass` |
| metadata_source_matches_manifest | yes | `experiments/final_submission_package/rolecap_queue/05_v1846e_queue05_v1842e_rolecap099_private.csv` |
| source_exists | yes | `experiments/final_submission_package/rolecap_queue/05_v1846e_queue05_v1842e_rolecap099_private.csv` |
| current_upload_rows_397 | yes | `397` |
| current_upload_sha_matches_metadata | yes | `upload=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912 metadata=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912` |
| current_upload_sha_matches_manifest | yes | `upload=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912 manifest=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912` |
| current_upload_sha_matches_source | yes | `upload=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912 source=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912` |
| validator_ok | yes | `OK: 397 predictions validated` |
| attempt_budget_command_ok | yes | `ATTEMPT_BUDGET; records_path=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv; max_attempts=5; attempts_used=4; attempts_remaining=1; best_score=0.49349; best_candidate=v1840c; best_group=overlay; delta_vs_current_best=+0.02230; latest_score=0.49349; latest_recommended_next=experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv; top3_hit=no; next_action=VALIDATE_AND_UPLOAD_RECOMMENDED_NEXT; next_command=python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records; stage_command=python3 experiments/scripts/v1870_stage_current_upload.py --from-records` |
| attempts_remaining_positive | yes | `1` |
| top3_not_already_hit | yes | `no` |
| command_center_regression_ok | yes | `WROTE_CSV=experiments/reports/v1882_command_center_dry_run_regression.csv; WROTE_REPORT=experiments/reports/v1882_command_center_dry_run_regression.md; SCENARIOS=8; FAILURES=0; MUTATION_OK=yes` |

## Upload instruction

Upload exactly this file:

```text
experiments/final_submission_package/current_upload/submission.csv
```

After the real private score appears, run:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

## Completion boundary

This guard only proves the upload file is ready.  The active score goal still requires a real Kaggle private score greater than `0.52380`.
