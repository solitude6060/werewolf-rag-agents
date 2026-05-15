# v1898 Current Score Report Bridge

Generated UTC: `2026-05-15T02:35:18+00:00`

## Summary

- Template: `experiments/final_submission_package/current_upload/SCORE_REPORT.txt`
- Score: `0.46698`
- Write mode: `confirmed`
- Synthetic dry-run score only: `no`
- Bridge exit code: `0`
- Filled report persisted: `no`

## Bridge command

```bash
/usr/bin/python3 experiments/scripts/v1895_score_report_command_center.py /tmp/v1898_score_report_kj9ebid7/SCORE_REPORT.txt --out-json /tmp/v1898_score_report_kj9ebid7/v1895_bridge.json --out-md /tmp/v1898_score_report_kj9ebid7/v1895_bridge.md --confirm-real-score
```

## Bridge output

```text
SCORE_REPORT_COMMAND_CENTER
INTAKE_READY=yes
SCORE=0.46698
SCORE_STATUS=continue_routing_required
WRITE_MODE=confirmed
COMMAND_CENTER_EXIT_CODE=0
OFFICIAL_RECORDS_MUTATED=yes
REPORT=/tmp/v1898_score_report_kj9ebid7/v1895_bridge.md
JSON=/tmp/v1898_score_report_kj9ebid7/v1895_bridge.json
```

## v1895 report

# v1895 Score Report Command Center

Generated UTC: `2026-05-15T02:35:18+00:00`

## Summary

- Intake ready: `yes`
- Score: `0.46698`
- Score status: `continue_routing_required`
- Write mode: `confirmed`
- Command-center exit code: `0`
- Official records mutated: `yes`

## Command

```bash
/usr/bin/python3 experiments/scripts/v1872_post_score_command_center.py --score 0.46698 --confirm-real-score
```

## Command-center output

```text
UPLOAD_CONTEXT
group=rolecap_queue
order=5
source=experiments/final_submission_package/current_upload/metadata.json
ROUTER_DRY_RUN
candidate=v1846e
score=0.46698
delta_vs_current_best=-0.00421
top3_hit=no
recommended_next=NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.
NEXT_PATH_STATUS=non_concrete_ok
ROUTER_CONFIRMED_WRITE
candidate=v1846e
score=0.46698
delta_vs_current_best=-0.00421
top3_hit=no
recommended_next=NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.
wrote=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
wrote=experiments/final_submission_package/manifests/v1836_score_feedback_records.md
ATTEMPT_BUDGET_AFTER_WRITE
ATTEMPT_BUDGET
records_path=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
max_attempts=5
attempts_used=5
attempts_remaining=0
best_score=0.49349
best_candidate=v1840c
best_group=overlay
delta_vs_current_best=+0.02230
latest_score=0.46698
latest_recommended_next=NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.
top3_hit=no
next_action=NO_ATTEMPTS_REMAINING
STAGE_STATUS=skipped_non_concrete_next recommended_next=NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.
COCKPIT_AFTER_MANUAL_STATE
# Final Attempt Cockpit

Generated UTC: `2026-05-15T02:35:17+00:00`

## Upload now

Use this fixed path:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Selected row source: `current_upload_manual_override`
Manual override reason: `last chance target 0.5 after v1840c=0.49349; override router v1842e to v1846e because role-cap keeps labels fixed and has stronger public AP/LOO evidence for crossing 0.5`
Selected candidate: `v1846e` (`rolecap_queue` order `5`)
Selected source: `experiments/final_submission_package/rolecap_queue/05_v1846e_queue05_v1842e_rolecap099_private.csv`
Rows: `397`
SHA-256: `c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912`
Manifest validation status: `pass`
Staged file exists: `yes`
Staged file matches selected source: `yes`
Staged validator: `OK: 397 predictions validated`

If staged match is not `yes`, run:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py --group rolecap_queue --order 5 --override-reason 'last chance target 0.5 after v1840c=0.49349; override router v1842e to v1846e because role-cap keeps labels fixed and has stronger public AP/LOO evidence for crossing 0.5'
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

Attempts used from records: `5`
Attempts remaining from records: `0`
Best recorded score: `0.49349`
Latest recorded score: `0.46698`
Stop threshold: `>0.52380`

## After real score appears

Use the no-edit current-upload bridge first; it reads the staged metadata and avoids typing group/order by hand:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>
```

Then record only if the score is real:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score
```

Fallback direct dry-run if the bridge is unavailable:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Fallback direct record command if the validated score must be typed manually:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group rolecap_queue --order 5 --score <REAL_SCORE> --confirm-real-score
```

## Router preview for this selected row

| Scenario | Example score | Recommended next | Path check |
| --- | ---: | --- | --- |
| hit top-3 | `0.52381` | `STOP: score exceeds top-3 threshold.` | `not_a_csv` |
| strong positive | `0.48000` | `NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| tiny positive | `0.47120` | `NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| exact current best | `0.47119` | `NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| near baseline | `0.47080` | `NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| small regression | `0.46600` | `NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| severe regression | `0.46400` | `NO_ROLECAP_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |

## Completion boundary

Only a real private score greater than `0.52380` completes the active score objective.

CARD_WRITTEN=experiments/final_submission_package/current_upload/ATTEMPT_CARD.md
```

## Completion boundary

This bridge validates and routes a score report. The active goal is complete only after a real private score greater than `0.52380` is recorded.


## Completion boundary

This wrapper only reduces score-entry handling risk. The active goal is complete only after a real private score greater than `0.52380` is recorded.
