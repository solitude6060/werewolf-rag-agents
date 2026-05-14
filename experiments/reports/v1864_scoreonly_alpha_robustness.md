# v1864 Score-Only Alpha Robustness Audit

Date: 2026-05-14

## Purpose

Check whether any v1863 partial-alpha score-only blend is more robust than the current v1862 first upload under leave-one-public-game-out scoring.

## Method

- Candidates evaluated: 30.
- Public games left out one at a time: 20.
- Baseline v1824a public proxy: `0.5376`.
- Deltas are computed against v1824a under the same held-out split.

## Top 10 by robust index

| Rank | Candidate | Target | Alpha | Public proxy | Min LOO delta | Mean LOO delta | LOO +/- | Score MAE | Robust index | Private CSV |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | v1863_12 | v1853g | 1.00 | 0.5942 | +0.0451 | +0.0565 | 20/0 | 0.0701 | 6.9196 | `experiments/submissions/submission_v1863_v1853g_alpha1p0_scoreblend_private.csv` |
| 2 | v1863_06 | v1856g | 1.00 | 0.5903 | +0.0450 | +0.0526 | 20/0 | 0.0582 | 6.7523 | `experiments/submissions/submission_v1863_v1856g_alpha1p0_scoreblend_private.csv` |
| 3 | v1863_18 | v1850g | 1.00 | 0.5853 | +0.0396 | +0.0475 | 20/0 | 0.0585 | 5.9881 | `experiments/submissions/submission_v1863_v1850g_alpha1p0_scoreblend_private.csv` |
| 4 | v1863_24 | v1848g | 1.00 | 0.5845 | +0.0389 | +0.0468 | 20/0 | 0.0427 | 5.9082 | `experiments/submissions/submission_v1863_v1848g_alpha1p0_scoreblend_private.csv` |
| 5 | v1863_11 | v1853g | 0.85 | 0.5777 | +0.0318 | +0.0400 | 20/0 | 0.0596 | 4.8621 | `experiments/submissions/submission_v1863_v1853g_alpha0p85_scoreblend_private.csv` |
| 6 | v1863_23 | v1848g | 0.85 | 0.5773 | +0.0304 | +0.0396 | 20/0 | 0.0363 | 4.7499 | `experiments/submissions/submission_v1863_v1848g_alpha0p85_scoreblend_private.csv` |
| 7 | v1863_17 | v1850g | 0.85 | 0.5773 | +0.0304 | +0.0396 | 20/0 | 0.0497 | 4.7232 | `experiments/submissions/submission_v1863_v1850g_alpha0p85_scoreblend_private.csv` |
| 8 | v1863_10 | v1853g | 0.70 | 0.5746 | +0.0289 | +0.0369 | 20/0 | 0.0491 | 4.4544 | `experiments/submissions/submission_v1863_v1853g_alpha0p7_scoreblend_private.csv` |
| 9 | v1863_22 | v1848g | 0.70 | 0.5746 | +0.0269 | +0.0369 | 20/0 | 0.0299 | 4.2915 | `experiments/submissions/submission_v1863_v1848g_alpha0p7_scoreblend_private.csv` |
| 10 | v1863_16 | v1850g | 0.70 | 0.5746 | +0.0269 | +0.0369 | 20/0 | 0.0409 | 4.2694 | `experiments/submissions/submission_v1863_v1850g_alpha0p7_scoreblend_private.csv` |

## Top 5 by minimum LOO delta

| Rank | Candidate | Target | Alpha | Public proxy | Min LOO delta | Mean LOO delta | Score MAE | Private CSV |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | v1863_12 | v1853g | 1.00 | 0.5942 | +0.0451 | +0.0565 | 0.0701 | `experiments/submissions/submission_v1863_v1853g_alpha1p0_scoreblend_private.csv` |
| 2 | v1863_06 | v1856g | 1.00 | 0.5903 | +0.0450 | +0.0526 | 0.0582 | `experiments/submissions/submission_v1863_v1856g_alpha1p0_scoreblend_private.csv` |
| 3 | v1863_18 | v1850g | 1.00 | 0.5853 | +0.0396 | +0.0475 | 0.0585 | `experiments/submissions/submission_v1863_v1850g_alpha1p0_scoreblend_private.csv` |
| 4 | v1863_24 | v1848g | 1.00 | 0.5845 | +0.0389 | +0.0468 | 0.0427 | `experiments/submissions/submission_v1863_v1848g_alpha1p0_scoreblend_private.csv` |
| 5 | v1863_11 | v1853g | 0.85 | 0.5777 | +0.0318 | +0.0400 | 0.0596 | `experiments/submissions/submission_v1863_v1853g_alpha0p85_scoreblend_private.csv` |

## Current first upload row

| Candidate | Target | Alpha | Public proxy | Min LOO delta | Mean LOO delta | LOO +/- | Score MAE |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v1863_06 | v1856g | 1.00 | 0.5903 | +0.0450 | +0.0526 | 20/0 | 0.0582 |

## Decision

No package/router change. The robustness audit does not identify a lower-alpha candidate that should replace the v1862 first upload. The top robust-index row differs from v1856g, but it is treated as analysis-only because v1862 intentionally prioritizes lower role-label risk and balanced-prior calibration.

Operational first upload remains:

```text
experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
```

The active goal remains incomplete until a real Kaggle private score greater than `0.50671` is reported.

## Artifacts

- `experiments/reports/v1864_scoreonly_alpha_robustness.csv`
