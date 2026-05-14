# v1874 Positive-Signal Router Threshold

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Purpose

Align the score-only safe router with the documented v1865 rule: if the first upload beats the current verified best `0.47119`, route to the higher-upside `v1853g` second slot.

## Change

In `experiments/scripts/v1836_score_feedback_router.py`, the score-only order-1 positive gate changed from:

```text
score >= 0.47200
```

to:

```text
score > 0.47119
```

Only the `scoreonly_safe_queue` order-1 route was changed.

## Validation evidence

```bash
python3 -m py_compile experiments/scripts/v1836_score_feedback_router.py
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.47120 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.47119 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.48000 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.50672 --dry-run
```

Observed routing:

```text
0.47120 -> scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv
0.47119 -> scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv
0.48000 -> scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv
0.50672 -> STOP: score exceeds top-3 threshold.
```

The final-attempt cockpit now includes both the tiny-positive and exact-current-best scenarios.

## Completion boundary

This improves the adaptive use of remaining attempts after the first real score.  It does not complete the active score goal without a real Kaggle private score greater than `0.50671`.
