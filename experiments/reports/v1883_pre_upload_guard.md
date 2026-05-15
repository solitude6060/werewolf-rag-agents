# v1883 Pre-Upload Guard

Date: 2026-05-15

## Summary

- Upload ready: `yes`
- Attempt context: `followup_from_records`
- Upload path: `experiments/final_submission_package/current_upload/submission.csv`
- Candidate: `overlay` order `9` (`v1840c`)
- SHA-256: `fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145`
- Rows: `397`
- Stop if real score is greater than: `0.52380`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| manifest_exists | yes | `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv` |
| current_upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| score_records_present_for_followup | yes | `3` |
| latest_recommended_next_is_csv | yes | `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv` |
| attempt_state_guard_ready | yes | `ATTEMPT_STATE_GUARD; ATTEMPT_STATE_READY=yes; STATE=staged_latest_recommended; RECORDS_COUNT=3; RECOMMENDED_NEXT=experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv; CURRENT_SOURCE_PATH=experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv; UPLOAD_ROWS=397; UPLOAD_SHA256=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145; REPORT=experiments/reports/v1904_attempt_state_guard.md; JSON=experiments/reports/v1904_attempt_state_guard.json` |
| manifest_row_found | yes | `overlay#9` |
| manifest_candidate_matches | yes | `v1840c` |
| manifest_status_pass | yes | `pass` |
| metadata_source_matches_manifest | yes | `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv` |
| source_exists | yes | `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv` |
| current_upload_rows_397 | yes | `397` |
| current_upload_sha_matches_metadata | yes | `upload=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145 metadata=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145` |
| current_upload_sha_matches_manifest | yes | `upload=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145 manifest=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145` |
| current_upload_sha_matches_source | yes | `upload=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145 source=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145` |
| validator_ok | yes | `OK: 397 predictions validated` |
| attempt_budget_command_ok | yes | `ATTEMPT_BUDGET; records_path=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv; max_attempts=5; attempts_used=3; attempts_remaining=2; best_score=0.49266; best_candidate=v1840b; best_group=overlay; delta_vs_current_best=+0.02147; latest_score=0.49266; latest_recommended_next=experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv; top3_hit=no; next_action=VALIDATE_AND_UPLOAD_RECOMMENDED_NEXT; next_command=python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records; stage_command=python3 experiments/scripts/v1870_stage_current_upload.py --from-records` |
| attempts_remaining_positive | yes | `2` |
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
