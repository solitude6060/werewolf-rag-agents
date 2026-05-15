# v1908 Final Goal Status

Generated UTC: `2026-05-15T03:34:49+00:00`

## Summary

- Action: `UPLOAD_CURRENT`
- Goal complete: `no`
- Ready to manual upload: `yes`
- Records consistent: `yes`
- Best score: `0.49349`
- Upload path: `experiments/final_submission_package/current_upload/submission.csv`

## Next command

```bash
upload experiments/final_submission_package/current_upload/submission.csv
```

## Completion gate output

```text
GOAL_COMPLETION_GATE
GOAL_COMPLETE=no
RECORDS_CONSISTENT=yes
RECORDS_PATH=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
RECORDS_COUNT=5
BEST_SCORE=0.49349
TOP3_THRESHOLD=0.52380
REPORT=/tmp/v1908_final_status_ilhs6bae/completion.md
JSON=/tmp/v1908_final_status_ilhs6bae/completion.json
```

## Preflight output

```text
FINAL_UPLOAD_PREFLIGHT
READY_TO_MANUAL_UPLOAD=yes
RELATIVE_UPLOAD_PATH=experiments/final_submission_package/current_upload/submission.csv
ABSOLUTE_UPLOAD_PATH=/home/ma/Research/PhD/course/114_2/AI/hw2/experiments/final_submission_package/current_upload/submission.csv
CANDIDATE=v1842e
GROUP=black_boost_queue
ORDER=5
ROWS=397
SHA256=6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f
REPORT=experiments/reports/v1888_final_upload_preflight.md
JSON=experiments/reports/v1888_final_upload_preflight.json
```

## Completion boundary

Only `ACTION=MARK_GOAL_COMPLETE` from this status command is sufficient local evidence to proceed to the final completion audit and `update_goal` call.
