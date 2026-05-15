# v1922 Runbook Threshold Regression

## Summary

- Failures: `0`
- Expected threshold: `>0.52380`
- Stale threshold rejected: `0.50671`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| runbook_exit_zero | yes | `exit=0` |
| prints_live_threshold | yes | `expected=0.52380` |
| does_not_print_stale_threshold | yes | `stale=0.50671` |
| records_and_upload_unchanged | yes | `before={'records_sha': 'fc7c1f781c557e8a4b9fede40344dfaf7dfabe09f115a1fdef8b9c9f92053590', 'records_count': '1', 'upload_sha': 'e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad'}; after={'records_sha': 'fc7c1f781c557e8a4b9fede40344dfaf7dfabe09f115a1fdef8b9c9f92053590', 'records_count': '1', 'upload_sha': 'e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad'}` |

## Runbook output

```text
NEXT_UPLOAD
group=queue
order=1
candidate=v1826a
path=experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv
rows=397
sha256=e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad
manifest_validation_status=pass
validator=skipped
STAGED_UPLOAD
path=experiments/final_submission_package/current_upload/submission.csv
sha256=e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad
POST_SCORE_COMMAND
python3 experiments/scripts/v1836_score_feedback_router.py --group queue --order 1 --score <REAL_SCORE> --dry-run
STOP_IF_SCORE_GREATER_THAN=0.52380
```

## Completion boundary

This regression only aligns the user-facing stop threshold. The active goal is complete only after a real private score greater than `0.52380` is recorded.
