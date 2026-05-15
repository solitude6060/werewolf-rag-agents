# v1900 Current Upload Score Report Guard

Generated UTC: `2026-05-15T03:34:49+00:00`

## Summary

- Score report ready: `yes`
- Upload: `experiments/final_submission_package/current_upload/submission.csv`
- Score report: `experiments/final_submission_package/current_upload/SCORE_REPORT.txt`
- Candidate: `v1842e`
- Rows: `397`
- SHA-256: `6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| score_report_exists | yes | `experiments/final_submission_package/current_upload/SCORE_REPORT.txt` |
| required_keys_present | yes | `all_present` |
| uploaded_path_matches | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| candidate_matches_metadata | yes | `v1842e` |
| group_matches_metadata | yes | `black_boost_queue` |
| order_matches_metadata | yes | `5` |
| rows_match_upload | yes | `report=397 upload=397` |
| rows_match_metadata | yes | `metadata=397 upload=397` |
| sha_matches_upload | yes | `report=6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f upload=6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f` |
| sha_matches_metadata | yes | `metadata=6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f upload=6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f` |
| score_placeholder_ready | yes | `<REAL_PRIVATE_SCORE_DECIMAL>` |
| real_private_flag_yes | yes | `yes` |

## Completion boundary

This guard only verifies score-report handoff integrity. The active goal is complete only after a real private score greater than `0.52380` is recorded.
