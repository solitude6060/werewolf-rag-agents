# v1898 Current Score Report Bridge

Generated UTC: `2026-05-15T00:14:10+00:00`

## Summary

- Template: `experiments/final_submission_package/current_upload/SCORE_REPORT.txt`
- Score: `0.42894`
- Write mode: `confirmed`
- Bridge exit code: `0`
- Filled report persisted: `no`

## Bridge command

```bash
/usr/bin/python3 experiments/scripts/v1895_score_report_command_center.py /tmp/v1898_score_report_762jegts/SCORE_REPORT.txt --out-json /tmp/v1898_score_report_762jegts/v1895_bridge.json --out-md /tmp/v1898_score_report_762jegts/v1895_bridge.md --confirm-real-score
```

## Bridge output

```text
SCORE_REPORT_COMMAND_CENTER
INTAKE_READY=yes
SCORE=0.42894
SCORE_STATUS=continue_routing_required
WRITE_MODE=confirmed
COMMAND_CENTER_EXIT_CODE=0
OFFICIAL_RECORDS_MUTATED=yes
REPORT=/tmp/v1898_score_report_762jegts/v1895_bridge.md
JSON=/tmp/v1898_score_report_762jegts/v1895_bridge.json
```

## v1895 report

# v1895 Score Report Command Center

Generated UTC: `2026-05-15T00:14:10+00:00`

## Summary

- Intake ready: `yes`
- Score: `0.42894`
- Score status: `continue_routing_required`
- Write mode: `confirmed`
- Command-center exit code: `0`
- Official records mutated: `yes`

## Command

```bash
/usr/bin/python3 experiments/scripts/v1872_post_score_command_center.py --score 0.42894 --confirm-real-score
```

## Command-center output

```text
UPLOAD_CONTEXT
group=scoreonly_safe_queue
order=1
source=experiments/final_submission_package/current_upload/metadata.json
ROUTER_DRY_RUN
candidate=v1856g
score=0.42894
delta_vs_current_best=-0.04225
top3_hit=no
recommended_next=experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv
NEXT_PATH_STATUS=concrete_ok:scoreonly_safe_queue#5:v1846g
ROUTER_CONFIRMED_WRITE
candidate=v1856g
score=0.42894
delta_vs_current_best=-0.04225
top3_hit=no
recommended_next=experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv
wrote=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
wrote=experiments/final_submission_package/manifests/v1836_score_feedback_records.md
ATTEMPT_BUDGET_AFTER_WRITE
ATTEMPT_BUDGET
records_path=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
max_attempts=5
attempts_used=1
attempts_remaining=4
best_score=0.42894
best_candidate=v1856g
best_group=scoreonly_safe_queue
delta_vs_current_best=-0.04225
latest_score=0.42894
latest_recommended_next=experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv
top3_hit=no
next_action=VALIDATE_AND_UPLOAD_RECOMMENDED_NEXT
next_command=python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records
stage_command=python3 experiments/scripts/v1870_stage_current_upload.py --from-records
NEXT_UPLOAD_RUNBOOK
LATEST_RECORD
group=scoreonly_safe_queue
order=1
candidate=v1856g
score=0.42894
recommended_next=experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv
NEXT_UPLOAD
group=scoreonly_safe_queue
order=5
candidate=v1846g
path=experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv
rows=397
sha256=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb
manifest_validation_status=pass
validator=OK: 397 predictions validated
POST_SCORE_COMMAND
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 5 --score <REAL_SCORE> --dry-run
STOP_IF_SCORE_GREATER_THAN=0.50671
STAGED_NEXT_UPLOAD
STAGED_UPLOAD
source=experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv
staged=experiments/final_submission_package/current_upload/submission.csv
group=scoreonly_safe_queue
order=5
candidate=v1846g
rows=397
sha256=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb
validator=OK: 397 predictions validated
metadata=experiments/final_submission_package/current_upload/metadata.json
readme=experiments/final_submission_package/current_upload/README.md
score_report=experiments/final_submission_package/current_upload/SCORE_REPORT.txt
COCKPIT_REFRESHED
# Final Attempt Cockpit

Generated UTC: `2026-05-15T00:14:10+00:00`

## Upload now

Use this fixed path:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Selected row source: `latest_record_recommended_next`
Selected candidate: `v1846g` (`scoreonly_safe_queue` order `5`)
Selected source: `experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv`
Rows: `397`
SHA-256: `f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb`
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

Attempts used from records: `1`
Attempts remaining from records: `4`
Best recorded score: `0.42894`
Latest recorded score: `0.42894`
Stop threshold: `>0.50671`

## After real score appears

Dry-run first:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Then record only if the score is real:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group scoreonly_safe_queue --order 5 --score <REAL_SCORE> --confirm-real-score
```

## Router preview for this selected row

| Scenario | Example score | Recommended next | Path check |
| --- | ---: | --- | --- |
| hit top-3 | `0.50672` | `STOP: score exceeds top-3 threshold.` | `not_a_csv` |
| strong positive | `0.48000` | `NO_SCOREONLY_SAFE_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| tiny positive | `0.47120` | `NO_SCOREONLY_SAFE_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| exact current best | `0.47119` | `NO_SCOREONLY_SAFE_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| near baseline | `0.47080` | `NO_SCOREONLY_SAFE_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| small regression | `0.46600` | `NO_SCOREONLY_SAFE_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| severe regression | `0.46400` | `NO_SCOREONLY_SAFE_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |

## Completion boundary

Only a real private score greater than `0.50671` completes the active score objective.

CARD_WRITTEN=experiments/final_submission_package/current_upload/ATTEMPT_CARD.md
RECORDS_PATH=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
```

## Completion boundary

This bridge validates and routes a score report. The active goal is complete only after a real private score greater than `0.50671` is recorded.


## Completion boundary

This wrapper only reduces score-entry handling risk. The active goal is complete only after a real private score greater than `0.50671` is recorded.
