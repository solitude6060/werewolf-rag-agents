# v1892 Current Upload Generator Preflight Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Keep regenerated `current_upload/` instructions aligned with the latest one-command final upload preflight so re-staging does not reintroduce the older multi-command guard path.

## Problem

`v1870_stage_current_upload.py` still generated `current_upload/README.md` with the old `v1883_pre_upload_guard.py` instruction. If run after the v1888 preflight work, it could overwrite the current README and confuse the last-mile upload flow.

## Scope

- Add `pre_upload_preflight_command` to generated metadata.
- Keep the legacy `pre_upload_guard_command` for compatibility.
- Generate `current_upload/README.md` with `v1888_final_upload_preflight.py` and expected `READY_TO_MANUAL_UPLOAD=yes`.
- Re-stage the current first upload and re-run v1888.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1870_stage_current_upload.py`
- `python3 experiments/scripts/v1870_stage_current_upload.py`
- `python3 experiments/scripts/v1888_final_upload_preflight.py`
- `python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv`
- grep confirms generated metadata/README include `v1888_final_upload_preflight.py`.

## Stop condition

The staged CSV remains byte-identical to the selected v1856g upload, the generated README points to v1888, and the active goal remains open until a real private score exceeds `0.50671`.
