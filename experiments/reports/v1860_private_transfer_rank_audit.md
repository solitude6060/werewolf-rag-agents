# v1860 Private-Transfer Rank Audit

Date: 2026-05-14

## Purpose

Audit whether the current final portfolio order is contradicted by known private-feedback history and structural distance from the verified-best v1824a submission.  This is a decision audit, not a private leaderboard predictor.

## Completion boundary

The active goal is complete only after a real Kaggle private score greater than `0.50671` is reported.  This audit does not provide that proof.

## Method summary

- Known private-feedback rows: 11.
- Future/package candidates scored: 53.
- Features: public proxy deltas, public/private role-change rate, score-difference magnitude, high-wolf-score rate, and nearest known private-feedback neighbors.
- Leave-one-known-out nearest-neighbor MAE: `0.00502`.  This is too large for completion proof, but useful for risk ranking.

## Current portfolio order

| Order | Candidate | Public proxy | Public delta | Private role-change rate vs v1824a | Score MAE vs v1824a | Nearest known private feedback | Upload path |
| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| 1 | v1856a | 0.5903 | 0.0528 | 0.0101 | 0.0673 | v1400@0.43655/d=4.41; v1812b@0.45349/d=4.75; v1810g@0.45462/d=4.76 | `experiments/final_submission_package/portfolio_queue/01_v1856a_risk_balanced_first_private.csv` |
| 2 | v1853a | 0.5942 | 0.0566 | 0.0101 | 0.0780 | v1400@0.43655/d=4.49; v1810g@0.45462/d=5.86; v1821a@0.46455/d=5.92 | `experiments/final_submission_package/portfolio_queue/02_v1853a_max_proxy_second_private.csv` |
| 3 | v1850a | 0.5853 | 0.0477 | 0.0101 | 0.0675 | v1400@0.43655/d=4.24; v1812b@0.45349/d=4.48; v1810g@0.45462/d=4.48 | `experiments/final_submission_package/portfolio_queue/03_v1850a_lowtail_fallback_private.csv` |
| 4 | v1848a | 0.5845 | 0.0470 | 0.0101 | 0.0515 | v1810g@0.45462/d=3.77; v1812b@0.45349/d=3.77; v1821a@0.46455/d=3.94 | `experiments/final_submission_package/portfolio_queue/04_v1848a_denoise_fallback_private.csv` |
| 5 | v1846a | 0.5742 | 0.0366 | 0.0101 | 0.0256 | v1810g@0.45462/d=2.53; v1812b@0.45349/d=2.58; v1821a@0.46455/d=2.73 | `experiments/final_submission_package/portfolio_queue/05_v1846a_rolecap_fallback_private.csv` |

## Score-only safe order

| Order | Candidate | Public proxy | Public delta | Private role-change rate vs v1824a | Score MAE vs v1824a | Nearest known private feedback | Upload path |
| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| 1 | v1856g | 0.5903 | 0.0528 | 0.0000 | 0.0582 | v1821a@0.46455/d=4.69; v1810g@0.45462/d=4.77; v1400@0.43655/d=4.89 | `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` |
| 2 | v1853g | 0.5942 | 0.0566 | 0.0000 | 0.0701 | v1400@0.43655/d=4.96; v1821a@0.46455/d=5.87; v1810g@0.45462/d=6.05 | `experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv` |
| 3 | v1850g | 0.5853 | 0.0477 | 0.0000 | 0.0585 | v1821a@0.46455/d=4.41; v1810g@0.45462/d=4.49; v1812b@0.45349/d=4.68 | `experiments/final_submission_package/scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv` |
| 4 | v1848g | 0.5845 | 0.0470 | 0.0000 | 0.0427 | v1821a@0.46455/d=3.72; v1810g@0.45462/d=3.85; v1812b@0.45349/d=4.07 | `experiments/final_submission_package/scoreonly_safe_queue/04_v1848g_scoreonly_denoise_private.csv` |
| 5 | v1846g | 0.5742 | 0.0366 | 0.0000 | 0.0155 | v1821a@0.46455/d=2.55; v1810g@0.45462/d=2.79; v1823a@0.46492/d=2.95 | `experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv` |

## Top risk-adjusted package candidates

The index below is only a ranking diagnostic: public delta is rewarded while distance from v1824a is penalized.  It is not an expected Kaggle score.

| Rank | Group | Candidate | Public proxy | Risk-adjusted index | Private role-change rate | Upload path |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| 1 | charprior_fallback | v1853g | 0.5942 | 5.3826 | 0.0000 | `experiments/final_submission_package/charprior_fallback/02_v1853g_v1850g_charprior_private.csv` |
| 2 | scoreonly_safe_queue | v1853g | 0.5942 | 5.3826 | 0.0000 | `experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv` |
| 3 | charprior_queue | v1853a | 0.5942 | 5.3570 | 0.0101 | `experiments/final_submission_package/charprior_queue/01_v1853a_queue01_v1850a_charprior_private.csv` |
| 4 | portfolio_queue | v1853a | 0.5942 | 5.3570 | 0.0101 | `experiments/final_submission_package/portfolio_queue/02_v1853a_max_proxy_second_private.csv` |
| 5 | charprior_queue | v1853b | 0.5942 | 5.3544 | 0.0151 | `experiments/final_submission_package/charprior_queue/02_v1853b_queue02_v1850b_charprior_private.csv` |
| 6 | charprior_queue | v1853c | 0.5942 | 5.3496 | 0.0151 | `experiments/final_submission_package/charprior_queue/03_v1853c_queue03_v1850c_charprior_private.csv` |
| 7 | charprior_queue | v1853d | 0.5942 | 5.3396 | 0.0202 | `experiments/final_submission_package/charprior_queue/04_v1853d_queue04_v1850d_charprior_private.csv` |
| 8 | charprior_queue | v1853e | 0.5942 | 5.3265 | 0.0252 | `experiments/final_submission_package/charprior_queue/05_v1853e_queue05_v1850e_charprior_private.csv` |
| 9 | balancedprior_fallback | v1856g | 0.5903 | 5.0983 | 0.0000 | `experiments/final_submission_package/balancedprior_fallback/02_v1856g_v1850g_balancedprior_private.csv` |
| 10 | scoreonly_safe_queue | v1856g | 0.5903 | 5.0983 | 0.0000 | `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` |
| 11 | balancedprior_queue | v1856a | 0.5903 | 5.0691 | 0.0101 | `experiments/final_submission_package/balancedprior_queue/01_v1856a_queue01_v1850a_balancedprior_private.csv` |
| 12 | portfolio_queue | v1856a | 0.5903 | 5.0691 | 0.0101 | `experiments/final_submission_package/portfolio_queue/01_v1856a_risk_balanced_first_private.csv` |

## Decision

Prefer the score-only safe first upload when minimizing role-label transfer risk. It keeps the v1856 balanced-prior public proxy while preserving the verified-best private role labels.

Recommended first upload:

```text
experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
```

If the user reports a real private score, use:

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --dry-run
```

## Artifacts

- `experiments/reports/v1860_private_transfer_rank_audit.csv`
