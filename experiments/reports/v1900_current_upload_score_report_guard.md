# v1900 Current Upload Score Report Guard

Generated UTC: `2026-05-15T00:18:47+00:00`

## Summary

- Score report ready: `yes`
- Upload: `experiments/final_submission_package/current_upload/submission.csv`
- Score report: `experiments/final_submission_package/current_upload/SCORE_REPORT.txt`
- Candidate: `v1846g`
- Rows: `397`
- SHA-256: `f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| score_report_exists | yes | `experiments/final_submission_package/current_upload/SCORE_REPORT.txt` |
| required_keys_present | yes | `all_present` |
| uploaded_path_matches | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| candidate_matches_metadata | yes | `v1846g` |
| group_matches_metadata | yes | `scoreonly_safe_queue` |
| order_matches_metadata | yes | `5` |
| rows_match_upload | yes | `report=397 upload=397` |
| rows_match_metadata | yes | `metadata=397 upload=397` |
| sha_matches_upload | yes | `report=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb upload=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb` |
| sha_matches_metadata | yes | `metadata=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb upload=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb` |
| score_placeholder_ready | yes | `<REAL_PRIVATE_SCORE_DECIMAL>` |
| real_private_flag_yes | yes | `yes` |

## Completion boundary

This guard only verifies score-report handoff integrity. The active goal is complete only after a real private score greater than `0.50671` is recorded.
