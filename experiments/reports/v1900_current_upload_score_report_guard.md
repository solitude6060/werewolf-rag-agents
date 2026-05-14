# v1900 Current Upload Score Report Guard

Generated UTC: `2026-05-14T19:02:47+00:00`

## Summary

- Score report ready: `yes`
- Upload: `experiments/final_submission_package/current_upload/submission.csv`
- Score report: `experiments/final_submission_package/current_upload/SCORE_REPORT.txt`
- Candidate: `v1856g`
- Rows: `397`
- SHA-256: `468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| score_report_exists | yes | `experiments/final_submission_package/current_upload/SCORE_REPORT.txt` |
| required_keys_present | yes | `all_present` |
| uploaded_path_matches | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| candidate_matches_metadata | yes | `v1856g` |
| group_matches_metadata | yes | `scoreonly_safe_queue` |
| order_matches_metadata | yes | `1` |
| rows_match_upload | yes | `report=397 upload=397` |
| rows_match_metadata | yes | `metadata=397 upload=397` |
| sha_matches_upload | yes | `report=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d upload=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d` |
| sha_matches_metadata | yes | `metadata=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d upload=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d` |
| score_placeholder_ready | yes | `<REAL_PRIVATE_SCORE_DECIMAL>` |
| real_private_flag_yes | yes | `yes` |

## Completion boundary

This guard only verifies score-report handoff integrity. The active goal is complete only after a real private score greater than `0.50671` is recorded.
