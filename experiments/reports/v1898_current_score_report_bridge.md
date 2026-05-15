# v1898 Current Score Report Bridge

Generated UTC: `2026-05-15T01:55:51+00:00`

## Summary

- Template: `experiments/final_submission_package/current_upload/SCORE_REPORT.txt`
- Score: `0.48854`
- Write mode: `confirmed`
- Synthetic dry-run score only: `no`
- Bridge exit code: `0`
- Filled report persisted: `no`

## Bridge command

```bash
/usr/bin/python3 experiments/scripts/v1895_score_report_command_center.py /tmp/v1898_score_report_ugsi6kqh/SCORE_REPORT.txt --out-json /tmp/v1898_score_report_ugsi6kqh/v1895_bridge.json --out-md /tmp/v1898_score_report_ugsi6kqh/v1895_bridge.md --confirm-real-score
```

## Bridge output

```text
SCORE_REPORT_COMMAND_CENTER
INTAKE_READY=yes
SCORE=0.48854
SCORE_STATUS=continue_routing_required
WRITE_MODE=confirmed
COMMAND_CENTER_EXIT_CODE=0
OFFICIAL_RECORDS_MUTATED=yes
REPORT=/tmp/v1898_score_report_ugsi6kqh/v1895_bridge.md
JSON=/tmp/v1898_score_report_ugsi6kqh/v1895_bridge.json
```

## v1895 report

# v1895 Score Report Command Center

Generated UTC: `2026-05-15T01:55:51+00:00`

## Summary

- Intake ready: `yes`
- Score: `0.48854`
- Score status: `continue_routing_required`
- Write mode: `confirmed`
- Command-center exit code: `0`
- Official records mutated: `yes`

## Command

```bash
/usr/bin/python3 experiments/scripts/v1872_post_score_command_center.py --score 0.48854 --confirm-real-score
```

## Command-center output

```text
UPLOAD_CONTEXT
group=queue
order=1
source=experiments/final_submission_package/current_upload/metadata.json
ROUTER_DRY_RUN
candidate=v1826a
score=0.48854
delta_vs_current_best=+0.01735
top3_hit=no
recommended_next=experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv
NEXT_PATH_STATUS=concrete_ok:queue#2:v1826b
ROUTER_CONFIRMED_WRITE
candidate=v1826a
score=0.48854
delta_vs_current_best=+0.01735
top3_hit=no
recommended_next=experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv
wrote=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
wrote=experiments/final_submission_package/manifests/v1836_score_feedback_records.md
ATTEMPT_BUDGET_AFTER_WRITE
ATTEMPT_BUDGET
records_path=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
max_attempts=5
attempts_used=2
attempts_remaining=3
best_score=0.48854
best_candidate=v1826a
best_group=queue
delta_vs_current_best=+0.01735
latest_score=0.48854
latest_recommended_next=experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv
top3_hit=no
next_action=VALIDATE_AND_UPLOAD_RECOMMENDED_NEXT
next_command=python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records
stage_command=python3 experiments/scripts/v1870_stage_current_upload.py --from-records
NEXT_UPLOAD_RUNBOOK
LATEST_RECORD
group=queue
order=1
candidate=v1826a
score=0.48854
recommended_next=experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv
NEXT_UPLOAD
group=queue
order=2
candidate=v1826b
path=experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv
rows=397
sha256=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b
manifest_validation_status=pass
validator=OK: 397 predictions validated
POST_SCORE_COMMAND
python3 experiments/scripts/v1836_score_feedback_router.py --group queue --order 2 --score <REAL_SCORE> --dry-run
STOP_IF_SCORE_GREATER_THAN=0.52380
STAGED_NEXT_UPLOAD
STAGED_UPLOAD
source=experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv
staged=experiments/final_submission_package/current_upload/submission.csv
group=queue
order=2
candidate=v1826b
rows=397
sha256=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b
validator=OK: 397 predictions validated
metadata=experiments/final_submission_package/current_upload/metadata.json
readme=experiments/final_submission_package/current_upload/README.md
score_report=experiments/final_submission_package/current_upload/SCORE_REPORT.txt
alias=hw2_D13922024/submission.csv
alias=hw2_D13922024/checkpoints/final_current_private.csv
alias=hw2_D13922024/checkpoints/final_v1826b_private.csv
COCKPIT_REFRESHED
# Final Attempt Cockpit

Generated UTC: `2026-05-15T01:55:50+00:00`

## Upload now

Use this fixed path:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Selected row source: `latest_record_recommended_next`
Selected candidate: `v1826b` (`queue` order `2`)
Selected source: `experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv`
Rows: `397`
SHA-256: `8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b`
Manifest validation status: `pass`
Staged file exists: `yes`
Staged file matches selected source: `yes`
Staged validator: `OK: 397 predictions validated`

If staged match is not `yes`, run:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py --from-records
```

For the first upload with no records, this is also valid:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py
```

Before manually uploading, run the final guard:

```bash
python3 experiments/scripts/v1883_pre_upload_guard.py
```

Expected guard result: `UPLOAD_READY=yes`.

## Attempt budget

Attempts used from records: `2`
Attempts remaining from records: `3`
Best recorded score: `0.48854`
Latest recorded score: `0.48854`
Stop threshold: `>0.52380`

## After real score appears

Dry-run first:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Then record only if the score is real:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group queue --order 2 --score <REAL_SCORE> --confirm-real-score
```

## Router preview for this selected row

| Scenario | Example score | Recommended next | Path check |
| --- | ---: | --- | --- |
| hit top-3 | `0.52381` | `STOP: score exceeds top-3 threshold.` | `not_a_csv` |
| strong positive | `0.48000` | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | `ok manifest_status=pass candidate=v1827d` |
| tiny positive | `0.47120` | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | `ok manifest_status=pass candidate=v1827d` |
| exact current best | `0.47119` | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | `ok manifest_status=pass candidate=v1827d` |
| near baseline | `0.47080` | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | `ok manifest_status=pass candidate=v1827d` |
| small regression | `0.46600` | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | `ok manifest_status=pass candidate=v1827d` |
| severe regression | `0.46400` | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | `ok manifest_status=pass candidate=v1827d` |

## Completion boundary

Only a real private score greater than `0.52380` completes the active score objective.

CARD_WRITTEN=experiments/final_submission_package/current_upload/ATTEMPT_CARD.md
RECORDS_PATH=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
```

## Completion boundary

This bridge validates and routes a score report. The active goal is complete only after a real private score greater than `0.52380` is recorded.


## Completion boundary

This wrapper only reduces score-entry handling risk. The active goal is complete only after a real private score greater than `0.52380` is recorded.
