# v1888 Final Upload Preflight

Generated UTC: `2026-05-15T01:55:55+00:00`

## Summary

- Ready to manually upload: `yes`
- Relative upload path: `experiments/final_submission_package/current_upload/submission.csv`
- Absolute upload path: `/home/ma/Research/PhD/course/114_2/AI/hw2/experiments/final_submission_package/current_upload/submission.csv`
- Candidate: `queue` order `2` (`v1826b`)
- Rows: `397`
- SHA-256: `8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b`
- Stop threshold: `>0.52380`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| metadata_exists | yes | `experiments/final_submission_package/current_upload/metadata.json` |
| current_upload_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| current_upload_rows_397 | yes | `397` |
| current_upload_sha_matches_metadata | yes | `8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b` |
| manifest_row_found | yes | `queue#2:v1826b` |
| manifest_candidate_matches | yes | `v1826b` |
| manifest_status_pass | yes | `pass` |
| manifest_sha_matches_upload | yes | `8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b` |
| manifest_output_exists | yes | `experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv` |
| manifest_output_sha_matches_upload | yes | `experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv` |
| validator_ok | yes | `OK: 397 predictions validated` |
| pre_upload_guard_ready | yes | `PRE_UPLOAD_GUARD; UPLOAD_READY=yes; ATTEMPT_CONTEXT=followup_from_records; UPLOAD_PATH=experiments/final_submission_package/current_upload/submission.csv; CANDIDATE=v1826b; GROUP=queue; ORDER=2; SHA256=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b; ROWS=397; REPORT=experiments/reports/v1883_pre_upload_guard.md; JSON=experiments/reports/v1883_pre_upload_guard.json` |
| candidate_pool_review_zero | yes | `WROTE_CSV=experiments/reports/v1884_candidate_pool_coverage_scan.csv; WROTE_REPORT=experiments/reports/v1884_candidate_pool_coverage_scan.md; PRIVATE_FILES=1331; SCORED_PAIRS=1309; REVIEW_CANDIDATES=0; SAFE_OR_DUPLICATE_ABOVE_FIRST=0` |
| score_report_guard_ready | yes | `CURRENT_UPLOAD_SCORE_REPORT_GUARD; SCORE_REPORT_READY=yes; UPLOAD=experiments/final_submission_package/current_upload/submission.csv; SCORE_REPORT=experiments/final_submission_package/current_upload/SCORE_REPORT.txt; CANDIDATE=v1826b; ROWS=397; SHA256=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b; REPORT=experiments/reports/v1900_current_upload_score_report_guard.md; JSON=experiments/reports/v1900_current_upload_score_report_guard.json` |
| upload_alias_guard_ready | yes | `UPLOAD_ALIAS_GUARD; ALIAS_GUARD_READY=yes; CANONICAL=experiments/final_submission_package/current_upload/submission.csv; CANONICAL_ROWS=397; CANONICAL_SHA256=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b; ALIAS=hw2_D13922024/submission.csv rows=397 sha_matches=yes; ALIAS=hw2_D13922024/checkpoints/final_current_private.csv rows=397 sha_matches=yes; ALIAS=hw2_D13922024/checkpoints/final_v1826b_private.csv rows=397 sha_matches=yes; LOOKALIKE=experiments/final_submission_package/current_upload/submission.csv rows=397 sha_matches=yes status=safe_whitelist; LOOKALIKE=experiments/worktrees/consistency-solver/hw2_D13922024/submission.csv rows=673 sha_matches=no status=do_not_upload; LOOKALIKE=experiments/worktrees/endgame-parser/hw2_D13922024/submission.csv rows=673 sha_matches=no status=do_not_upload; LOOKALIKE=experiments/worktrees/v53-feedback/hw2_D13922024/submission.csv rows=673 sha_matches=no status=do_not_upload; LOOKALIKE=hw2_D13922024/submission.csv rows=397 sha_matches=yes status=safe_whitelist; LOOKALIKE=werewolf-project/artifacts/legacy-submissions/hw2_D13922024/submission.csv rows=673 sha_matches=no status=do_not_upload; REPORT=experiments/reports/v1902_upload_alias_guard.md; JSON=experiments/reports/v1902_upload_alias_guard.json` |
| attempt_state_guard_ready | yes | `ATTEMPT_STATE_GUARD; ATTEMPT_STATE_READY=yes; STATE=staged_latest_recommended; RECORDS_COUNT=2; RECOMMENDED_NEXT=experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv; CURRENT_SOURCE_PATH=experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv; UPLOAD_ROWS=397; UPLOAD_SHA256=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b; REPORT=experiments/reports/v1904_attempt_state_guard.md; JSON=experiments/reports/v1904_attempt_state_guard.json` |

## Manual upload instruction

Upload exactly this file in the browser:

```text
experiments/final_submission_package/current_upload/submission.csv
```

After the real private score appears:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score
```

## Completion boundary

This preflight only proves local upload readiness. The active objective still requires a real Kaggle private score greater than `0.52380`.
