# v1897 Current Upload Score Report Handoff

Generated UTC: `2026-05-14T18:54:24+00:00`
Branch: `dev/final-submission-report-pack`

## Goal

Reduce deadline-day transcription risk by keeping a ready-to-edit score report next to the exact CSV that should be uploaded.

## Artifacts

- Upload CSV: `experiments/final_submission_package/current_upload/submission.csv`
- Editable score report: `experiments/final_submission_package/current_upload/SCORE_REPORT.txt`
- Current-upload metadata: `experiments/final_submission_package/current_upload/metadata.json`
- Current-upload instructions: `experiments/final_submission_package/current_upload/README.md`

## Current score report template

```text
SCORE_REPORT
uploaded_path=experiments/final_submission_package/current_upload/submission.csv
candidate=v1856g
group=scoreonly_safe_queue
order=1
sha256=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
rows=397
real_private_score=<REAL_PRIVATE_SCORE_DECIMAL>
score_is_real_kaggle_private=yes
```

## Verification evidence

```text
python3 experiments/scripts/v1870_stage_current_upload.py
STAGED_UPLOAD
candidate=v1856g
rows=397
sha256=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
validator=OK: 397 predictions validated
score_report=experiments/final_submission_package/current_upload/SCORE_REPORT.txt
```

```text
python3 experiments/scripts/v1895_score_report_command_center.py /tmp/v1897_score_report_example.txt --out-json /tmp/v1897_score_report_example.json --out-md /tmp/v1897_score_report_example.md
INTAKE_READY=yes
SCORE=0.47120
SCORE_STATUS=continue_routing_required
WRITE_MODE=dry_run
OFFICIAL_RECORDS_MUTATED=no
```

```text
python3 experiments/scripts/v1888_final_upload_preflight.py
READY_TO_MANUAL_UPLOAD=yes
```

## Completion boundary

This handoff reduces score-report handling risk only. It does not complete the active score goal. The active goal remains incomplete until a real Kaggle private score strictly greater than `0.50671` is recorded.
