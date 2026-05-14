# v1869 Attempt Budget Guard

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Purpose

Track the final five-attempt budget from score-feedback records so the submission process stops when the top-3 threshold is hit and does not silently exceed the planned attempt count.

## Command

```bash
python3 experiments/scripts/v1869_attempt_budget_guard.py
```

Default records file:

```text
experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
```

## Validation

```bash
python3 -m py_compile experiments/scripts/v1869_attempt_budget_guard.py
python3 experiments/scripts/v1869_attempt_budget_guard.py --records /tmp/nonexistent_v1869_records.csv
python3 experiments/scripts/v1869_attempt_budget_guard.py --records /tmp/v1869_records_one.csv
python3 experiments/scripts/v1869_attempt_budget_guard.py --records /tmp/v1869_records_top3.csv
python3 experiments/scripts/v1869_attempt_budget_guard.py --records /tmp/v1869_records_five.csv
```

Observed scenarios:

| Scenario | Attempts used | Attempts remaining | Top-3 hit | Next action |
| --- | ---: | ---: | --- | --- |
| no records | 0 | 5 | no | run first-upload runbook and stage first upload |
| one positive record | 1 | 4 | no | validate latest recommended next and restage `current_upload/submission.csv` from records |
| top-3 record | 1 | 4 | yes | stop; candidate completion proof exists if record is real |
| five records below top-3 | 5 | 0 | no | no attempts remaining |

## Current real-record state

At the time of this audit, the real score-feedback records file is absent:

```text
NO_SCORE_FEEDBACK_RECORDS
```

Therefore the active goal remains incomplete and the next action is still the first-upload runbook:

```bash
python3 experiments/scripts/v1866_final_attempt_runbook.py
python3 experiments/scripts/v1870_stage_current_upload.py
```

After score-feedback records exist, use:

```bash
python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records
python3 experiments/scripts/v1870_stage_current_upload.py --from-records
```

## Completion boundary

The guard can identify a top-3 score in records, but only a real Kaggle private score record greater than `0.50671` can complete the active goal.  The validation scenarios above used temporary records files.
