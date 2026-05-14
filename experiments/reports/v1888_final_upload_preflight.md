# v1888 Final Upload Preflight

Generated UTC: `2026-05-14T18:27:48+00:00`

## Summary

- Ready to manually upload: `yes`
- Relative upload path: `experiments/final_submission_package/current_upload/submission.csv`
- Absolute upload path: `/home/ma/Research/PhD/course/114_2/AI/hw2/experiments/final_submission_package/current_upload/submission.csv`
- Candidate: `scoreonly_safe_queue` order `1` (`v1856g`)
- Rows: `397`
- SHA-256: `468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d`
- Stop threshold: `>0.50671`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| current_upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| current_upload_rows_397 | yes | `397` |
| current_upload_sha_matches_metadata | yes | `468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d` |
| manifest_row_found | yes | `scoreonly_safe_queue#1:v1856g` |
| manifest_candidate_matches | yes | `v1856g` |
| manifest_status_pass | yes | `pass` |
| manifest_sha_matches_upload | yes | `468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d` |
| manifest_output_exists | yes | `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` |
| manifest_output_sha_matches_upload | yes | `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` |
| validator_ok | yes | `OK: 397 predictions validated` |
| pre_upload_guard_ready | yes | `PRE_UPLOAD_GUARD; UPLOAD_READY=yes; UPLOAD_PATH=experiments/final_submission_package/current_upload/submission.csv; CANDIDATE=v1856g; GROUP=scoreonly_safe_queue; ORDER=1; SHA256=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d; ROWS=397; REPORT=experiments/reports/v1883_pre_upload_guard.md; JSON=experiments/reports/v1883_pre_upload_guard.json` |
| candidate_pool_review_zero | yes | `WROTE_CSV=experiments/reports/v1884_candidate_pool_coverage_scan.csv; WROTE_REPORT=experiments/reports/v1884_candidate_pool_coverage_scan.md; PRIVATE_FILES=1331; SCORED_PAIRS=1309; REVIEW_CANDIDATES=0; SAFE_OR_DUPLICATE_ABOVE_FIRST=0` |
| score_records_absent_for_first_upload | yes | `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv` |

## Manual upload instruction

Upload exactly this file in the browser:

```text
experiments/final_submission_package/current_upload/submission.csv
```

After the real private score appears:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE> --confirm-real-score
```

## Completion boundary

This preflight only proves local upload readiness. The active objective still requires a real Kaggle private score greater than `0.50671`.
