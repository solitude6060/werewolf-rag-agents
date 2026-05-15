# v1911 Post-v1856g Score Routing Audit

Generated UTC: `2026-05-15T00:20:00+00:00`
Branch: `dev/final-submission-report-pack`

## Objective restated

Use the remaining final attempts to record a real Kaggle private score strictly greater than the third-place threshold `0.50671`.

## New real score

| Uploaded candidate | Group | Order | Real private score | Delta vs rollback `0.47119` | Top-3 hit |
| --- | --- | ---: | ---: | ---: | --- |
| v1856g | scoreonly_safe_queue | 1 | 0.42894 | -0.04225 | no |

The score was recorded through the current score-report bridge and written to `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv`.

## Prompt-to-artifact checklist

| Requirement / gate | Evidence inspected | Coverage judgment | Status |
| --- | --- | --- | --- |
| Record the real `0.42894` score | `v1836_score_feedback_records.csv` contains `scoreonly_safe_queue,1,v1856g,...,0.42894,...,recommended_next=...05_v1846g...`. | Covers the real feedback for the just-uploaded file. | pass |
| Do not mark goal complete unless score is above `0.50671` | `v1908_final_goal_status.py` reports `GOAL_COMPLETE=no`, `BEST_SCORE=0.42894`. | Prevents proxy/local readiness from ending the active score objective. | pass |
| Stage a concrete next upload | `v1870_stage_current_upload.py --from-records` staged `scoreonly_safe_queue` order `5`, candidate `v1846g`. | Current upload now matches the latest router recommendation. | pass |
| Manual upload path remains fixed | `v1888_final_upload_preflight.py` reports `RELATIVE_UPLOAD_PATH=experiments/final_submission_package/current_upload/submission.csv`. | Keeps the browser upload instruction stable. | pass |
| Current upload is valid | Validator reports `OK: 397 predictions validated`; SHA-256 is `f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb`. | Covers CSV format and row count for the next attempt. | pass |
| Guard follow-up attempt state | `v1883_pre_upload_guard.py` reports `UPLOAD_READY=yes`, `ATTEMPT_CONTEXT=followup_from_records`. | Confirms guards support post-record follow-up attempts. | pass |
| Alias upload files match canonical upload | `v1902_upload_alias_guard.py` is included in final preflight and passes after staging aliases. | Reduces wrong-file manual upload risk. | pass |
| Final status is actionable | `v1908_final_goal_status.py` reports `ACTION=UPLOAD_CURRENT`, `READY_TO_MANUAL_UPLOAD=yes`. | The next concrete action is manual upload of the staged file. | pass |

## Next upload

Upload exactly:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Current staged candidate:

```text
candidate=v1846g
group=scoreonly_safe_queue
order=5
rows=397
sha256=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb
```

## Completion decision

`NOT COMPLETE`.

Reason: the best recorded real private score is `0.42894`, which is below `0.50671`. The local state is ready for the next manual upload, but the active score objective still requires a real score above the threshold.

## Verification evidence

Commands executed after recording the score and staging the next candidate:

```text
python3 experiments/scripts/v1882_command_center_dry_run_regression.py
SCENARIOS=7
FAILURES=0
MUTATION_OK=yes

python3 experiments/scripts/v1902_upload_alias_guard_regression.py
SCENARIOS=3
FAILURES=0

python3 experiments/scripts/v1883_pre_upload_guard.py
UPLOAD_READY=yes
ATTEMPT_CONTEXT=followup_from_records

python3 experiments/scripts/v1888_final_upload_preflight.py
READY_TO_MANUAL_UPLOAD=yes
CANDIDATE=v1846g
GROUP=scoreonly_safe_queue
ORDER=5
SHA256=f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb

python3 experiments/scripts/v1908_final_goal_status.py
ACTION=UPLOAD_CURRENT
GOAL_COMPLETE=no
READY_TO_MANUAL_UPLOAD=yes
BEST_SCORE=0.42894

python3 -m py_compile experiments/scripts/v1870_stage_current_upload.py experiments/scripts/v1882_command_center_dry_run_regression.py experiments/scripts/v1883_pre_upload_guard.py experiments/scripts/v1902_upload_alias_guard.py
py_compile=pass
```
