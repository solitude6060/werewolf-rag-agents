# v1868 Deadline-Day Pre-Upload Audit

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Purpose

Run a fresh deadline-day check so the next Kaggle upload uses the intended CSV and not a stale candidate.

## Current recommended upload

```text
experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
```

## Fresh command evidence

```bash
python3 experiments/scripts/v1866_final_attempt_runbook.py
```

Observed:

```text
NEXT_UPLOAD
group=scoreonly_safe_queue
order=1
candidate=v1856g
path=experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
rows=397
sha256=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
manifest_validation_status=pass
validator=OK: 397 predictions validated
POST_SCORE_COMMAND
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --dry-run
STOP_IF_SCORE_GREATER_THAN=0.50671
```

Score-feedback records check:

```text
NO_SCORE_FEEDBACK_RECORDS
```

Manifest check:

```text
MANIFEST_ROWS 83
VALIDATION_PASS 83
ROW_COUNT_397 83
FIRST_ROW v1856g experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv 468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d pass
```

## Deadline-day upload instructions

1. Upload exactly:

```text
experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
```

2. After the real private score appears, preview routing:

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --dry-run
```

3. If the score is real and should be recorded:

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --confirm-real-score
python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records
```

4. If `<REAL_SCORE> > 0.50671`, stop because the top-3 target has been met.

## Completion status

The package is ready for the next upload, but the active goal is not complete yet because there is no real Kaggle private score greater than `0.50671`.
