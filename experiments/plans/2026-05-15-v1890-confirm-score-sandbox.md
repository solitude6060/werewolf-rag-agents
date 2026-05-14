# v1890 Confirm Score Sandbox Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Exercise the real `--confirm-real-score` write path against temporary score-record files so the final-attempt score ledger behavior is verified without touching official records or spending a Kaggle attempt.

## Risk

Previous regressions covered dry-runs and the append guard function, but the actual confirmed-write path also depends on CLI parsing, manifest lookup, result formatting, CSV/Markdown writes, duplicate rejection, and top-3 stop behavior.

## Scope

- Add `experiments/scripts/v1890_confirm_score_sandbox_regression.py`.
- Monkeypatch the router's record paths to temporary files.
- Run confirmed writes through `v1836_score_feedback_router.py`'s `main()`.
- Verify first write, duplicate rejection, top-3 stop write, post-top-3 rejection, and exhausted-budget rejection.
- Verify official score-record files remain absent.

## Non-goals

- Do not create official score-feedback records.
- Do not upload to Kaggle.
- Do not change the current upload candidate.
- Do not mark the active goal complete without a real private score greater than `0.50671`.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1890_confirm_score_sandbox_regression.py`
- `python3 experiments/scripts/v1890_confirm_score_sandbox_regression.py`
- `python3 experiments/scripts/v1888_final_upload_preflight.py`
- Expected official records remain absent.

## Stop condition

The sandbox confirms the real write path behavior while leaving official records untouched and the active score goal open pending a real private score.
