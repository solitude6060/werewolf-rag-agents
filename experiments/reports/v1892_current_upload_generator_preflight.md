# v1892 Current Upload Generator Preflight Alignment

Date: 2026-05-15

## Summary

`v1870_stage_current_upload.py` now regenerates `current_upload/README.md` with the latest one-command preflight instead of the older guard-only command.

## Evidence

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
```

```text
FINAL_UPLOAD_PREFLIGHT
READY_TO_MANUAL_UPLOAD=yes
RELATIVE_UPLOAD_PATH=experiments/final_submission_package/current_upload/submission.csv
CANDIDATE=v1856g
GROUP=scoreonly_safe_queue
ORDER=1
ROWS=397
SHA256=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
```

```text
OK: 397 predictions validated
```

Generated metadata includes both:

```text
pre_upload_preflight_command=python3 experiments/scripts/v1888_final_upload_preflight.py
pre_upload_guard_command=python3 experiments/scripts/v1883_pre_upload_guard.py
```

The README upload instruction uses the preflight command and expects `READY_TO_MANUAL_UPLOAD=yes`.

## Completion boundary

This fixes local last-mile instructions only. The active score objective still requires a real Kaggle private score greater than `0.50671`.
