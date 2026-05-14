# v1865 Score-Only to Portfolio Router Plan

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Goal

Improve the final-attempt router so the score-only safe queue does not stop too early when it receives a positive score below the top-3 threshold.

## Problem

After v1862, the recommended first upload is `scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv`.  The current router sends a positive first score to v1853g, but if v1853g improves over v1856g without exceeding `0.50671`, it returns a manual-review message.  That is too conservative for an objective that still has remaining attempts and needs to chase the top-3 score.

## Rule update

Keep the score-only safe queue as the lower role-risk first route, but when a score-only stage is positive and still below top-3, route to the structural portfolio counterpart for a higher-upside chase:

| Score-only stage | Positive but below top-3 next action |
| --- | --- |
| order 2 v1853g | `portfolio_queue/02_v1853a_max_proxy_second_private.csv` |
| order 3 v1850g | `portfolio_queue/03_v1850a_lowtail_fallback_private.csv` |
| order 4 v1848g | `portfolio_queue/04_v1848a_denoise_fallback_private.csv` |

Order 1 remains unchanged: positive first score still routes to score-only max-proxy v1853g first.

## Validation

- `python3 -m py_compile experiments/scripts/v1836_score_feedback_router.py`
- Router matrix dry-runs:
  - order 1 positive / near-neutral / negative / top-3.
  - order 2 positive vs previous, non-positive vs previous.
  - order 3 and order 4 positive fallback routes.
- Confirm no package manifest changes are required.
- Rerun document scans.

## Completion boundary

Router readiness is not completion proof. The active goal requires a real private score greater than `0.50671`.
