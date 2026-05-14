# v1874 Positive-Signal Router Threshold Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Fix the score-feedback router so the score-only first-upload route matches the documented v1865 rule: if the first score-only safe upload improves over the current verified best, the next upload should be `v1853g`.

## Problem

The current verified best is `0.47119`.  The v1865 report says a positive score-only order-1 result should route to score-only order 2, but the implementation currently uses `score >= 0.47200`.  That leaves a real positive range:

```text
0.47119 < score < 0.47200
```

where the router would skip the highest-upside score-only `v1853g` slot and move to a more conservative fallback.

## Scope

- Update `experiments/scripts/v1836_score_feedback_router.py` only for `scoreonly_safe_queue` order 1.
- Add validation evidence for:
  - `0.47120` routes to order 2 `v1853g`,
  - `0.47119` does not count as positive,
  - existing `0.48000` and top-3 routes remain unchanged.
- Update reports/audit artifacts.

## Validation

- `python3 -m py_compile experiments/scripts/v1836_score_feedback_router.py`
- `python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.47120 --dry-run`
- `python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.47119 --dry-run`
- `python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.48000 --dry-run`
- `python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.50672 --dry-run`
- staged submission validator and document scans.

## Completion boundary

This improves the adaptive use of remaining attempts.  It does not complete the active goal without a real Kaggle private score greater than `0.50671`.
