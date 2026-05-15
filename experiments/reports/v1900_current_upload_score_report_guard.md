# v1900 Current Upload Score Report Guard

Generated UTC: `2026-05-15T02:27:34+00:00`

## Summary

- Score report ready: `yes`
- Upload: `experiments/final_submission_package/current_upload/submission.csv`
- Score report: `experiments/final_submission_package/current_upload/SCORE_REPORT.txt`
- Candidate: `v1846e`
- Rows: `397`
- SHA-256: `c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| score_report_exists | yes | `experiments/final_submission_package/current_upload/SCORE_REPORT.txt` |
| required_keys_present | yes | `all_present` |
| uploaded_path_matches | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| candidate_matches_metadata | yes | `v1846e` |
| group_matches_metadata | yes | `rolecap_queue` |
| order_matches_metadata | yes | `5` |
| rows_match_upload | yes | `report=397 upload=397` |
| rows_match_metadata | yes | `metadata=397 upload=397` |
| sha_matches_upload | yes | `report=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912 upload=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912` |
| sha_matches_metadata | yes | `metadata=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912 upload=c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912` |
| score_placeholder_ready | yes | `<REAL_PRIVATE_SCORE_DECIMAL>` |
| real_private_flag_yes | yes | `yes` |

## Completion boundary

This guard only verifies score-report handoff integrity. The active goal is complete only after a real private score greater than `0.52380` is recorded.
