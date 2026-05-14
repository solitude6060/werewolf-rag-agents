# v1865 Score-Only to Portfolio Router

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Purpose

Make the score-only safe queue usable for all remaining attempts, not just the first upload.  If a score-only candidate improves but still does not pass the top-3 threshold, the router now moves into the matching structural portfolio candidate for a higher-upside chase.

## Updated routing rule

| Current upload | If score is positive but below `0.50671` | If score is not positive enough |
| --- | --- | --- |
| score-only order 1 v1856g | score-only order 2 v1853g | score-only order 3/4/5 by severity |
| score-only order 2 v1853g | portfolio order 2 v1853a | score-only order 3 v1850g |
| score-only order 3 v1850g | portfolio order 3 v1850a | score-only order 4 v1848g |
| score-only order 4 v1848g | portfolio order 4 v1848a | score-only order 5 v1846g |

## Validation command matrix

```bash
python3 -m py_compile experiments/scripts/v1836_score_feedback_router.py
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.48000 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.47120 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.47119 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.47080 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.46400 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.50672 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 2 --score 0.48100 --previous-score 0.48000 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 2 --score 0.47900 --previous-score 0.48000 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 3 --score 0.47200 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 4 --score 0.47200 --dry-run
```

## Decision

The operational first upload remains:

```text
experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
```

After any real score, preview the next action with:

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order <ORDER> --score <REAL_SCORE> --dry-run
```

The active goal remains incomplete until a real Kaggle private score greater than `0.50671` is reported.

## v1874 threshold correction

The order-1 score-only route now treats any real score strictly greater than the current verified best `0.47119` as positive:

- `0.47120` -> `scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv`
- `0.47119` -> `scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv`

This keeps the documented positive-signal rule aligned with the router.
