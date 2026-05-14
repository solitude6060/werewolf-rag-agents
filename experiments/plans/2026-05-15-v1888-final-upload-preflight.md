# v1888 Final Upload Preflight Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Provide one local command that summarizes whether the fixed current upload is ready for the manual Kaggle upload step, without uploading or spending an attempt.

## Problem

The current upload is ready, but the last-mile checklist is spread across the guard, validator, candidate-pool scan, handoff document, and metadata files. A one-command preflight reduces file-selection and stale-state risk immediately before the browser upload.

## Scope

- Add `experiments/scripts/v1888_final_upload_preflight.py`.
- Run the existing pre-upload guard and candidate-pool coverage scan.
- Validate the current upload CSV directly.
- Verify current metadata, SHA, row count, score-record absence, and manifest/source consistency.
- Write machine-readable JSON and Markdown evidence under `experiments/reports/`.
- Update handoff/checklist docs to point to the one-command preflight.

## Non-goals

- Do not upload to Kaggle.
- Do not record a score.
- Do not change the staged upload candidate.
- Do not mark the active goal complete from local readiness evidence.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1888_final_upload_preflight.py`
- `python3 experiments/scripts/v1888_final_upload_preflight.py`
- Expected `READY_TO_MANUAL_UPLOAD=yes`.
- `python3 experiments/scripts/v1887_score_input_safety_regression.py`
- `python3 experiments/scripts/v1882_command_center_dry_run_regression.py`
- Sensitive phrase grep on changed handoff/report-facing docs.

## Stop condition

Stop when one command prints the exact relative and absolute upload path, all local readiness checks pass, the evidence is committed, and the active score goal remains open pending a real private score above `0.50671`.
