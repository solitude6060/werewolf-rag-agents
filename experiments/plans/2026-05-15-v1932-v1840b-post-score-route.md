# v1932 v1840b Post-Score Route Plan

## Goal

Protect the post-score route after manually staging `v1840b` as the current
upload.  If `v1840b` beats the latest recorded best but still misses the
`0.52380` top-3 cutoff, the next recommendation should stay on the same
high-upside overlay lane instead of falling back to the plain diagnostic queue.

## Problem

The current router treats `v1840b` as equivalent to queue order `3`
(`v1826d`).  For any non-top-3 score it routes to plain `v1826c`:

```text
python3 experiments/scripts/v1836_score_feedback_router.py --group overlay --order 8 --score 0.50000 --dry-run
recommended_next=experiments/final_submission_package/queue/04_v1826c_alt_structural_private.csv
```

This is too conservative for the current state because:

- `v1826a = 0.48854` already confirmed the g4/g29/AP structural direction.
- `v1840b` is the higher-upside continuation of that direction.
- With only three recorded attempts remaining before uploading `v1840b`, a
  score above the current best but below top-3 should route to `v1840c`, the
  corresponding high-upside final Hail Mary overlay.

## Intended Route

- `score > 0.52380`: stop.
- `score > latest recorded best`: route to
  `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv`.
- otherwise: keep the existing fallback to
  `experiments/final_submission_package/queue/04_v1826c_alt_structural_private.csv`.

## Verification

1. Add a regression script covering the `v1840b` positive, non-improving, and
   top-3 scenarios.
2. Confirm the regression fails before the router fix.
3. Patch the router.
4. Re-run the regression plus current upload/bridge guards.

## Stop Condition

The current upload remains `v1840b`, the route for a positive-but-not-top-3
`v1840b` score points to `v1840c`, and the active goal remains incomplete until
a real private score greater than `0.52380` is recorded.
