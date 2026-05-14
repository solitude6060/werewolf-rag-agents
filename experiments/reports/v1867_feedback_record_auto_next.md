# v1867 Feedback Record Auto-Next

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Purpose

Extend the final-attempt runbook so that after a real score has been recorded, the next upload can be derived directly from the latest score-feedback record.  This avoids manually copying the `recommended_next` path after each Kaggle result.

## New command

After recording a real score with `v1836_score_feedback_router.py --confirm-real-score`, run:

```bash
python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records
```

The command reads:

```text
experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
```

If the latest `recommended_next` is a concrete package CSV path, it resolves that path back to the manifest row and validates the file.  If the latest recommendation is STOP or manual review, it prints that state instead of pretending there is a next upload.

## Validation

```bash
python3 -m py_compile experiments/scripts/v1866_final_attempt_runbook.py
python3 experiments/scripts/v1866_final_attempt_runbook.py --skip-validation
python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records --records /tmp/v1867_records_next.csv --skip-validation
python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records --records /tmp/v1867_records_next.csv
python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records --records /tmp/v1867_records_stop.csv
```

Observed next-record result:

```text
LATEST_RECORD
group=scoreonly_safe_queue
order=1
candidate=v1856g
score=0.48000
recommended_next=experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv
NEXT_UPLOAD
group=scoreonly_safe_queue
order=2
candidate=v1853g
path=experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv
rows=397
manifest_validation_status=pass
validator=OK: 397 predictions validated
```

Observed stop-record result:

```text
LATEST_RECORD
group=scoreonly_safe_queue
order=1
candidate=v1856g
score=0.50672
recommended_next=STOP: score exceeds top-3 threshold.
STOP_STATE=top3_hit_or_stop_recommended
```

The validation used temporary records files in `/tmp` and did not write the real feedback-record CSV.

## Operational usage

1. Before first upload:

```bash
python3 experiments/scripts/v1866_final_attempt_runbook.py
```

2. After uploading and seeing a real private score:

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --confirm-real-score
python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records
```

The active goal remains incomplete until a real Kaggle private score greater than `0.50671` is reported.
