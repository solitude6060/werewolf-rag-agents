# v1935 v1840c Final Fallback Route Regression

## Summary

- Scenarios checked: `3`
- Failures: `0`
- Records unchanged: `yes`
- Current best used for routing: `0.49266`

## Matrix

| Label | Score | Expected top3 | Actual top3 | Expected next | Actual next | Pass |
| --- | ---: | --- | --- | --- | --- | --- |
| v1840c_positive_miss_routes_final_blackboost | `0.51000` | no | no | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` | yes |
| v1840c_regression_still_routes_final_blackboost | `0.48000` | no | no | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` | yes |
| v1840c_top3_hit_stops | `0.52381` | yes | yes | `STOP: score exceeds top-3 threshold.` | `STOP: score exceeds top-3 threshold.` | yes |

## Completion boundary

This regression only protects local final-attempt routing. The active goal is complete only after a real private score greater than `0.52380` is recorded.
