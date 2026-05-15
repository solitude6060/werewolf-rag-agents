# v1934 Post-v1840b Score Route Plan

## Goal

Record the user-reported `submission1840b.csv` private score `0.49266`,
verify whether the active top-3 goal is complete, and stage the next upload.

## Current Score Boundary

- Latest real score: `v1840b = 0.49266`.
- Previous best record: `v1826a = 0.48854`.
- Live top-3 cutoff: `0.52380`.
- Completion requires a real private score strictly greater than `0.52380`.

## Expected Route

Because `0.49266` improves over `0.48854` but is not greater than `0.52380`,
the route should continue on the overlay lane:

```text
experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv
```

## Verification Criteria

- Official score ledger contains `overlay#8:v1840b score=0.49266 top3_hit=no`.
- Current upload is `overlay#9:v1840c`.
- Current upload, assignment alias, and checkpoint aliases share the same SHA.
- Validator accepts the staged current upload.
- Completion gate reports `GOAL_COMPLETE=no`, `BEST_SCORE=0.49266`.

## Stop Condition

Stop local score routing after `v1840c` is staged, validated, and committed.
Do not mark the active goal complete unless a later real private score is
greater than `0.52380`.
