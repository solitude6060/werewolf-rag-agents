# v1866 Final Attempt Runbook Plan

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Goal

Create a small local CLI that prints the exact next upload path, file hash, validation status, and the router command to use after the real Kaggle score is known.  This reduces the risk of wasting one of the remaining attempts by uploading the wrong file or using the wrong router group/order.

## Scope

- Add `experiments/scripts/v1866_final_attempt_runbook.py`.
- Default next upload: `scoreonly_safe_queue` order 1.
- Read `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv`.
- Confirm the recommended file exists, has 397 rows, matches manifest hash, and passes `werewolf-project/assert/validate_submission.py` unless `--skip-validation` is used.
- Print the exact upload path and post-score router command.
- Support `--group`, `--order`, and `--score` to preview router output after a reported score.
- Follow-up after v1870: if `experiments/final_submission_package/current_upload/submission.csv` exists and has the same SHA-256 as the selected manifest row, print a `STAGED_UPLOAD` block so the manual upload path is unmistakable.

## Validation

- `python3 -m py_compile experiments/scripts/v1866_final_attempt_runbook.py`
- `python3 experiments/scripts/v1866_final_attempt_runbook.py --skip-validation`
- `python3 experiments/scripts/v1866_final_attempt_runbook.py`
- `python3 experiments/scripts/v1866_final_attempt_runbook.py --score 0.48000`
- `python3 experiments/scripts/v1866_final_attempt_runbook.py --score 0.50672`
- `python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records`
- Rerun document scans.

## Completion boundary

This runbook improves execution reliability but cannot complete the active goal.  Completion still requires a real Kaggle private score greater than `0.50671`.
