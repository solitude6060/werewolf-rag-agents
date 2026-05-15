# v1908 Final Goal Status

Generated UTC: `2026-05-15T00:33:12+00:00`

## Summary

- Action: `UPLOAD_CURRENT`
- Goal complete: `no`
- Ready to manual upload: `yes`
- Records consistent: `yes`
- Best score: `0.42894`
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
RECORDS_COUNT=1
BEST_SCORE=0.42894
TOP3_THRESHOLD=0.52380
REPORT=/tmp/v1908_final_status_z1ujyxcr/completion.md
JSON=/tmp/v1908_final_status_z1ujyxcr/completion.json
```

## Preflight output

```text
FINAL_UPLOAD_PREFLIGHT
READY_TO_MANUAL_UPLOAD=yes
RELATIVE_UPLOAD_PATH=experiments/final_submission_package/current_upload/submission.csv
ABSOLUTE_UPLOAD_PATH=/home/ma/Research/PhD/course/114_2/AI/hw2/experiments/final_submission_package/current_upload/submission.csv
CANDIDATE=v1826a
GROUP=queue
ORDER=1
ROWS=397
SHA256=e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad
REPORT=experiments/reports/v1888_final_upload_preflight.md
JSON=experiments/reports/v1888_final_upload_preflight.json
```

## Completion boundary

Only `ACTION=MARK_GOAL_COMPLETE` from this status command is sufficient local evidence to proceed to the final completion audit and `update_goal` call.
