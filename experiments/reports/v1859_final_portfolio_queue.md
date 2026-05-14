# v1859 Final Portfolio Queue

Date: 2026-05-14

## Purpose

The remaining Kaggle attempts should not all be spent inside one score-calibration family.  This queue combines the current best validated candidates across risk layers, using the v1858 private-feedback transfer audit as the ordering guide.

## Queue

| Order | Candidate | Upload path | Public proxy | Risk layer | Why |
| ---: | --- | --- | ---: | --- | --- |
| 1 | v1856a | `experiments/final_submission_package/portfolio_queue/01_v1856a_risk_balanced_first_private.csv` | 0.5903 | balanced | v1858 recommends it as first upload; v1857 no-leak heldout has 0/20 negatives. |
| 2 | v1853a | `experiments/final_submission_package/portfolio_queue/02_v1853a_max_proxy_second_private.csv` | 0.5942 | high | Highest local public proxy; use only after a positive signal or when maximum upside is needed. |
| 3 | v1850a | `experiments/final_submission_package/portfolio_queue/03_v1850a_lowtail_fallback_private.csv` | 0.5853 | medium | Lower public-label calibration than v1853/v1856. |
| 4 | v1848a | `experiments/final_submission_package/portfolio_queue/04_v1848a_denoise_fallback_private.csv` | 0.5845 | medium-low | Denoise calibration; v1849 LOO positive 20/20. |
| 5 | v1846a | `experiments/final_submission_package/portfolio_queue/05_v1846a_rolecap_fallback_private.csv` | 0.5742 | medium-low | Role-cap calibration; v1847 LOO positive 20/20. |

## Router

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group portfolio_queue --order 1 --score <REAL_SCORE> --dry-run
```

Dry-run examples verified:

- order 1 score `0.48000` routes to order 2 (`v1853a`).
- order 1 score `0.47080` routes to order 3 (`v1850a`).
- order 1 score `0.46400` routes to order 5 (`v1846a`).
- order 1 score `0.50672` routes to stop.

## Validation

```bash
python3 -m py_compile experiments/scripts/v1835_final_submission_pack.py experiments/scripts/v1836_score_feedback_router.py
python3 experiments/scripts/v1835_final_submission_pack.py --preset full
python3 experiments/scripts/v1835_final_submission_pack.py --preset portfolio-queue --out /tmp/hw2_pack_portfolio_queue_smoke --skip-validation --no-existing-doc-scan
python3 experiments/scripts/v1836_score_feedback_router.py --group portfolio_queue --order 1 --score 0.48000 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group portfolio_queue --order 1 --score 0.47080 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group portfolio_queue --order 1 --score 0.46400 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group portfolio_queue --order 1 --score 0.50672 --dry-run
```

Observed package state: 78 private CSVs in the full manifest, all with 397 rows and validator pass status.  The portfolio smoke package generated 5 files.

## Decision

Use this portfolio queue when the user wants a five-attempt plan that balances upside and transfer risk.  If the user explicitly wants the single maximum-public-proxy shot, use v1853a directly.  If the user wants the more conservative calibration path, use v1850a directly.

The active goal remains incomplete until a real Kaggle private score greater than `0.50671` is reported.

## v1862 supersession note

The portfolio queue remains valid, but `experiments/reports/v1862_scoreonly_safe_queue.md` adds a lower role-risk first route.  Use `scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` first when preserving the verified-best private role labels is preferred.
