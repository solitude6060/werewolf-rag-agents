# v1900 Current Upload Score Report Guard

Generated UTC: `2026-05-15T01:55:55+00:00`

## Summary

- Score report ready: `yes`
- Upload: `experiments/final_submission_package/current_upload/submission.csv`
- Score report: `experiments/final_submission_package/current_upload/SCORE_REPORT.txt`
- Candidate: `v1826b`
- Rows: `397`
- SHA-256: `8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| score_report_exists | yes | `experiments/final_submission_package/current_upload/SCORE_REPORT.txt` |
| required_keys_present | yes | `all_present` |
| uploaded_path_matches | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| candidate_matches_metadata | yes | `v1826b` |
| group_matches_metadata | yes | `queue` |
| order_matches_metadata | yes | `2` |
| rows_match_upload | yes | `report=397 upload=397` |
| rows_match_metadata | yes | `metadata=397 upload=397` |
| sha_matches_upload | yes | `report=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b upload=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b` |
| sha_matches_metadata | yes | `metadata=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b upload=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b` |
| score_placeholder_ready | yes | `<REAL_PRIVATE_SCORE_DECIMAL>` |
| real_private_flag_yes | yes | `yes` |

## Completion boundary

This guard only verifies score-report handoff integrity. The active goal is complete only after a real private score greater than `0.52380` is recorded.
