# v1870 Current Upload Staging

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Purpose

Stage the current recommended Kaggle upload into one fixed path so the final manual upload does not require selecting from many candidate folders.

## Staged upload path

Upload this file:

```text
experiments/final_submission_package/current_upload/submission.csv
```

It is a byte-for-byte copy of:

```text
experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
```

## Command

```bash
python3 experiments/scripts/v1870_stage_current_upload.py
```

The final-attempt runbook now also echoes this staged path when the hash matches the selected manifest row:

```bash
python3 experiments/scripts/v1866_final_attempt_runbook.py
```

After score-feedback records exist, refresh the same fixed path from the router's latest recommendation:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py --from-records
```

## Fresh validation evidence

Observed output:

```text
STAGED_UPLOAD
source=experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
staged=experiments/final_submission_package/current_upload/submission.csv
group=scoreonly_safe_queue
order=1
candidate=v1856g
rows=397
sha256=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
validator=OK: 397 predictions validated
metadata=experiments/final_submission_package/current_upload/metadata.json
readme=experiments/final_submission_package/current_upload/README.md
```

Independent staged-file validator:

```text
OK: 397 predictions validated
```

## Generated staging files

- `experiments/final_submission_package/current_upload/submission.csv`
- `experiments/final_submission_package/current_upload/metadata.json`
- `experiments/final_submission_package/current_upload/README.md`

## Post-upload command

After the real private score appears:

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --dry-run
```

The active goal remains incomplete until a real Kaggle private score greater than `0.50671` is reported.
