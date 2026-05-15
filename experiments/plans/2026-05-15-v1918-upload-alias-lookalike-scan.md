# v1918 Upload Alias Lookalike Scan Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Promote the v1917 wrong-file documentation into the automated upload alias guard, so preflight output explicitly lists `submission.csv` lookalikes that are not safe to upload.

## Constraints

- Do not block the valid current upload merely because documented legacy/worktree lookalikes exist.
- Do not modify or delete legacy/worktree CSV files.
- Do not mutate score records or current upload CSV contents.
- Keep `ALIAS_GUARD_READY=yes` tied to safe alias parity while emitting `LOOKALIKE=... status=do_not_upload` warnings for unsafe lookalikes.

## Regression-first change

1. Extend `v1902_upload_alias_guard_regression.py` with a synthetic unsafe `submission.csv` lookalike under a temporary scan root.
2. Confirm the new scenario fails before implementation because `--scan-root` / `LOOKALIKE=` output is absent.
3. Implement lookalike scanning in `v1902_upload_alias_guard.py`.
4. Rerun regression and guard.

## Verification standard

- `python3 experiments/scripts/v1902_upload_alias_guard_regression.py` reports `SCENARIOS=4`, `FAILURES=0`.
- `python3 experiments/scripts/v1902_upload_alias_guard.py` reports safe aliases and `LOOKALIKE=... status=do_not_upload` for legacy/worktree lookalikes.
- `python3 -m py_compile experiments/scripts/v1902_upload_alias_guard.py experiments/scripts/v1902_upload_alias_guard_regression.py experiments/scripts/v1888_final_upload_preflight.py` passes.
- `validate_submission.py` still passes for current upload.

## Outputs

- Updated `experiments/scripts/v1902_upload_alias_guard.py`
- Updated `experiments/scripts/v1902_upload_alias_guard_regression.py`
- Updated `experiments/reports/v1902_upload_alias_guard.md/json`
- Updated `experiments/reports/v1902_upload_alias_guard_regression.md/csv`

## Stop condition

Stop when automated preflight-visible output distinguishes safe upload aliases from do-not-upload lookalikes and the current upload remains validator-clean.
