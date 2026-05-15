# v1908 Final Goal Status

Generated UTC: `2026-05-15T02:40:09+00:00`

## Summary

- Action: `BLOCKED`
- Goal complete: `no`
- Ready to manual upload: `no`
- Records consistent: `yes`
- Best score: `0.49349`
- Upload path: `experiments/final_submission_package/current_upload/submission.csv`

## Next command

```bash
inspect v1908 report outputs and fix the failing gate before uploading
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
REPORT=/tmp/v1908_final_status_427t8qwl/completion.md
JSON=/tmp/v1908_final_status_427t8qwl/completion.json
```

## Preflight output

```text
FINAL_UPLOAD_PREFLIGHT
READY_TO_MANUAL_UPLOAD=no
RELATIVE_UPLOAD_PATH=experiments/final_submission_package/current_upload/submission.csv
ABSOLUTE_UPLOAD_PATH=/home/ma/Research/PhD/course/114_2/AI/hw2/experiments/final_submission_package/current_upload/submission.csv
CANDIDATE=v1840c
GROUP=overlay
ORDER=9
ROWS=397
SHA256=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145
REPORT=experiments/reports/v1888_final_upload_preflight.md
JSON=experiments/reports/v1888_final_upload_preflight.json
preflight failed: pre_upload_guard_ready,attempt_state_guard_ready
```

## Completion boundary

Only `ACTION=MARK_GOAL_COMPLETE` from this status command is sufficient local evidence to proceed to the final completion audit and `update_goal` call.
