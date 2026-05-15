# v1932 v1840b Override Route Regression

## Summary

- Scenarios checked: `3`
- Failures: `0`
- Records unchanged: `yes`
- Current best used for routing: `0.48854`

## Matrix

| Label | Score | Expected top3 | Actual top3 | Expected next | Actual next | Pass |
| --- | ---: | --- | --- | --- | --- | --- |
| positive_v1840b_stays_on_overlay_hailmary | `0.50000` | no | no | `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv` | `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv` | yes |
| non_improving_v1840b_uses_alt_structural | `0.48000` | no | no | `experiments/final_submission_package/queue/04_v1826c_alt_structural_private.csv` | `experiments/final_submission_package/queue/04_v1826c_alt_structural_private.csv` | yes |
| top3_hit_stops_without_next_stage | `0.52381` | yes | yes | `STOP: score exceeds top-3 threshold.` | `STOP: score exceeds top-3 threshold.` | yes |

## Completion boundary

This regression only protects the local post-score route. The active goal is complete only after a real private score greater than `0.52380` is recorded.
