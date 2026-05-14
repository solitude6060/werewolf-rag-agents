# v1871 Final Attempt Cockpit Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Add one deadline-day command that prints and writes a compact attempt card with:

- the exact current fixed upload path,
- selected source candidate and checksum,
- staged-file match status,
- remaining attempt budget,
- stop threshold,
- score-band router previews,
- the commands to record the real score and refresh the fixed upload path.

## Why

The package already has a runbook, router, budget guard, and staging script.  The remaining operational risk is switching between multiple commands while the final attempts are time-constrained.  A one-page cockpit reduces manual errors without changing any candidate predictions.

## Scope

- Add `experiments/scripts/v1871_final_attempt_cockpit.py`.
- Default output card: `experiments/final_submission_package/current_upload/ATTEMPT_CARD.md`.
- Read the final package manifest and optional score-feedback records.
- Resolve the current upload row from records when possible, otherwise default to `scoreonly_safe_queue` order 1.
- Verify the selected file hash, row count, manifest validation status, and staged-file parity.
- Generate router previews using `v1836_score_feedback_router.py --dry-run`.

## Validation

- `python3 -m py_compile experiments/scripts/v1871_final_attempt_cockpit.py`
- `python3 experiments/scripts/v1871_final_attempt_cockpit.py`
- `python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv`
- rerun submission-facing and broad phrase scans.

## Completion boundary

This cockpit improves execution reliability only.  It does not complete the active score goal.  Completion still requires a real Kaggle private score greater than `0.50671`.
