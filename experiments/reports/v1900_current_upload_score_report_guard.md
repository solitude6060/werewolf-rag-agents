# v1900 Current Upload Score Report Guard

Generated UTC: `2026-05-15T02:09:15+00:00`

## Summary

- Score report ready: `yes`
- Upload: `experiments/final_submission_package/current_upload/submission.csv`
- Score report: `experiments/final_submission_package/current_upload/SCORE_REPORT.txt`
- Candidate: `v1840b`
- Rows: `397`
- SHA-256: `16d56e36317dfdbe3e2372754def6ddeda8182f4bbfdd6723e8018eaa8a911dc`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| score_report_exists | yes | `experiments/final_submission_package/current_upload/SCORE_REPORT.txt` |
| required_keys_present | yes | `all_present` |
| uploaded_path_matches | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| candidate_matches_metadata | yes | `v1840b` |
| group_matches_metadata | yes | `overlay` |
| order_matches_metadata | yes | `8` |
| rows_match_upload | yes | `report=397 upload=397` |
| rows_match_metadata | yes | `metadata=397 upload=397` |
| sha_matches_upload | yes | `report=16d56e36317dfdbe3e2372754def6ddeda8182f4bbfdd6723e8018eaa8a911dc upload=16d56e36317dfdbe3e2372754def6ddeda8182f4bbfdd6723e8018eaa8a911dc` |
| sha_matches_metadata | yes | `metadata=16d56e36317dfdbe3e2372754def6ddeda8182f4bbfdd6723e8018eaa8a911dc upload=16d56e36317dfdbe3e2372754def6ddeda8182f4bbfdd6723e8018eaa8a911dc` |
| score_placeholder_ready | yes | `<REAL_PRIVATE_SCORE_DECIMAL>` |
| real_private_flag_yes | yes | `yes` |

## Completion boundary

This guard only verifies score-report handoff integrity. The active goal is complete only after a real private score greater than `0.52380` is recorded.
