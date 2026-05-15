# v1931 Post-0.48854 Upside Override Plan

## Goal

Maximize the chance of beating the live top-3 cutoff after the real `v1826a`
private score came back as `0.48854`.

Success still requires a recorded real private score strictly greater than
`0.52380`; local staging or validation cannot complete the active goal.

## Current Evidence

- Recorded scores:
  - `v1856g = 0.42894`, severe regression for the score-only calibration family.
  - `v1826a = 0.48854`, positive structural transfer over the rollback
    `v1824a = 0.47119`.
- Attempt records used: `2 / 5`; remaining records budget: `3`.
- `v1826a` positive stack includes:
  - g4 Regina white repair.
  - g29 Friedel white repair.
  - AP boosts for already-assigned wolves in g3/g15/g17.

## Decision

Stage `v1840b` as a manual upside override for the next upload instead of the
default diagnostic `v1826b`.

Chosen path:

```text
experiments/final_submission_package/overlay/08_v1840b_v1826d_high_precision_medium_ap_overlay_private.csv
```

Rationale:

- `v1826b` removes the three AP boosts that were part of the positive `v1826a`
  result, then adds the g23 structural repair.
- `v1826d` keeps the positive `v1826a` AP layer and adds the same g23 repair.
- `v1840b` uses `v1826d` plus only AP demotes from previously-audited
  high-precision white/human evidence. It changes no extra role labels beyond
  the g23 repair.
- With only three recorded attempts remaining and a `+0.03526` gap to top-3,
  the next attempt should prioritize upside over a lower-information diagnostic.

## Verification Criteria

- Current upload metadata records the manual override reason.
- `current_upload/submission.csv` is byte-identical to manifest row
  `overlay#8:v1840b`.
- Assignment-facing aliases point to the same SHA.
- Pre-upload guard passes with `UPLOAD_READY=yes`.
- Completion gate remains `GOAL_COMPLETE=no` until a real score `>0.52380` is
  recorded.

## Stop Condition

Stop local staging after the override upload path is validated and committed.
Do not call goal completion unless the next real private score exceeds
`0.52380`.
