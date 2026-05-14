# v1862 Score-Only Safe Queue Plan

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Goal

Add a safer final upload route using candidates that preserve the current verified-best private role labels and change only `wolf_score` values.

## Why this is worth doing

The v1860 private-transfer rank audit found that several fallback candidates keep the same public proxy as their structural counterparts while reducing private-side role-change risk versus v1824a:

| Candidate | Public proxy | Private role changes vs v1824a | Score MAE vs v1824a | Note |
| --- | ---: | ---: | ---: | --- |
| v1856a | 0.5903 | 4 | 0.0673 | current portfolio first |
| v1856g | 0.5903 | 0 | 0.0582 | same proxy, lower structural risk |
| v1853a | 0.5942 | 4 | 0.0780 | max-proxy structural path |
| v1853g | 0.5942 | 0 | 0.0701 | max-proxy score-only fallback |

This suggests v1856g is a plausible first upload when preserving private F1 is more important than testing additional role changes.

## Scope

- Add `scoreonly_safe_queue` to `experiments/scripts/v1835_final_submission_pack.py`.
- Add `--preset scoreonly-safe-queue`.
- Add `scoreonly_safe_queue` to the full package.
- Add router support in `experiments/scripts/v1836_score_feedback_router.py`.
- Produce report `experiments/reports/v1862_scoreonly_safe_queue.md`.

## Queue

1. v1856g — balanced-prior score-only first attempt.
2. v1853g — maximum public-proxy score-only shot.
3. v1850g — low-tail score-only fallback.
4. v1848g — denoise score-only fallback.
5. v1846g — role-cap score-only fallback.

## Validation

- `python3 -m py_compile experiments/scripts/v1835_final_submission_pack.py experiments/scripts/v1836_score_feedback_router.py experiments/scripts/v1860_private_transfer_rank_audit.py`
- `python3 experiments/scripts/v1835_final_submission_pack.py --preset full`
- `python3 experiments/scripts/v1835_final_submission_pack.py --preset scoreonly-safe-queue --out /tmp/hw2_pack_scoreonly_safe_queue_smoke --skip-validation --no-existing-doc-scan`
- Router smoke for `scoreonly_safe_queue`.
- Validate the first upload CSV.
- Rerun submission-facing and broad document scans.

## Completion boundary

This can improve the upload recommendation but cannot complete the active goal. The goal still requires a real Kaggle private score greater than `0.50671`.
