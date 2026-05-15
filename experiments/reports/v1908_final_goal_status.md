# v1908 Final Goal Status

Generated UTC: `2026-05-15T00:18:47+00:00`

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
TOP3_THRESHOLD=0.50671
REPORT=/tmp/v1908_final_status_gp_5kkt4/completion.md
JSON=/tmp/v1908_final_status_gp_5kkt4/completion.json
```

## Preflight output

```text
FINAL_UPLOAD_PREFLIGHT
READY_TO_MANUAL_UPLOAD=yes
RELATIVE_UPLOAD_PATH=experiments/final_submission_package/current_upload/submission.csv
ABSOLUTE_UPLOAD_PATH=/home/ma/Research/PhD/course/114_2/AI/hw2/experiments/final_submission_package/current_upload/submission.csv
CANDIDATE=v1846g
GROUP=scoreonly_safe_queue
ORDER=5
ROWS=397
SHA256=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb
REPORT=experiments/reports/v1888_final_upload_preflight.md
JSON=experiments/reports/v1888_final_upload_preflight.json
```

## Completion boundary

Only `ACTION=MARK_GOAL_COMPLETE` from this status command is sufficient local evidence to proceed to the final completion audit and `update_goal` call.
