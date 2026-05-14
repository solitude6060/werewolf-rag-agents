# v1883 Pre-Upload Guard

Date: 2026-05-15

## Summary

- Upload ready: `yes`
- Upload path: `experiments/final_submission_package/current_upload/submission.csv`
- Candidate: `scoreonly_safe_queue` order `1` (`v1856g`)
- SHA-256: `468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d`
- Rows: `397`
- Stop if real score is greater than: `0.50671`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| manifest_exists | yes | `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv` |
| current_upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| metadata_context_is_first_upload | yes | `scoreonly_safe_queue#1:v1856g` |
| manifest_row_found | yes | `scoreonly_safe_queue#1` |
| manifest_candidate_matches | yes | `v1856g` |
| manifest_status_pass | yes | `pass` |
| metadata_source_matches_manifest | yes | `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` |
| source_exists | yes | `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` |
| current_upload_rows_397 | yes | `397` |
| current_upload_sha_matches_expected | yes | `468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d` |
| current_upload_sha_matches_metadata | yes | `upload=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d metadata=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d` |
| current_upload_sha_matches_manifest | yes | `upload=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d manifest=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d` |
| current_upload_sha_matches_source | yes | `upload=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d source=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d` |
| validator_ok | yes | `OK: 397 predictions validated` |
| score_records_absent_for_first_upload | yes | `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv` |
| attempt_budget_command_ok | yes | `ATTEMPT_BUDGET; records_path=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv; max_attempts=5; attempts_used=0; attempts_remaining=5; best_score=none; top3_hit=no; next_action=RUN_FIRST_UPLOAD_RUNBOOK; next_command=python3 experiments/scripts/v1866_final_attempt_runbook.py; stage_command=python3 experiments/scripts/v1870_stage_current_upload.py` |
| attempts_remaining_5 | yes | `5` |
| top3_not_already_hit | yes | `no` |
| command_center_regression_ok | yes | `WROTE_CSV=experiments/reports/v1882_command_center_dry_run_regression.csv; WROTE_REPORT=experiments/reports/v1882_command_center_dry_run_regression.md; SCENARIOS=7; FAILURES=0; MUTATION_OK=yes` |

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

This guard only proves the upload file is ready.  The active score goal still requires a real Kaggle private score greater than `0.50671`.
