# v1863 Score-Only Blend Ladder

Date: 2026-05-14

## Purpose

Search partial score-only blends between the verified-best v1824a scores and high-proxy score-only targets. Roles always remain v1824a roles.

## Search summary

- Targets: 5.
- Alpha values per target: 6.
- Generated public/private pairs: 30.
- Baseline public proxy: `0.5376`.
- All generated private CSVs passed the local submission validator.

## Promoted one-per-family candidates

| Candidate | Target | Alpha | Public proxy | Public delta | Score MAE vs v1824a | Changed scores >0.05 | Private CSV |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| v1863_12 | v1853g | 1.00 | 0.5942 | +0.0566 | 0.0701 | 167 | `experiments/submissions/submission_v1863_v1853g_alpha1p0_scoreblend_private.csv` |
| v1863_06 | v1856g | 1.00 | 0.5903 | +0.0528 | 0.0582 | 96 | `experiments/submissions/submission_v1863_v1856g_alpha1p0_scoreblend_private.csv` |
| v1863_18 | v1850g | 1.00 | 0.5853 | +0.0477 | 0.0585 | 96 | `experiments/submissions/submission_v1863_v1850g_alpha1p0_scoreblend_private.csv` |
| v1863_24 | v1848g | 1.00 | 0.5845 | +0.0470 | 0.0427 | 64 | `experiments/submissions/submission_v1863_v1848g_alpha1p0_scoreblend_private.csv` |
| v1863_30 | v1846g | 1.00 | 0.5742 | +0.0366 | 0.0155 | 13 | `experiments/submissions/submission_v1863_v1846g_alpha1p0_scoreblend_private.csv` |

## Top 10 by risk-adjusted index

| Rank | Candidate | Target | Alpha | Public proxy | Risk-adjusted index | Score MAE | Private CSV |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | v1863_12 | v1853g | 1.00 | 0.5942 | 5.4071 | 0.0701 | `experiments/submissions/submission_v1863_v1853g_alpha1p0_scoreblend_private.csv` |
| 2 | v1863_06 | v1856g | 1.00 | 0.5903 | 5.1080 | 0.0582 | `experiments/submissions/submission_v1863_v1856g_alpha1p0_scoreblend_private.csv` |
| 3 | v1863_18 | v1850g | 1.00 | 0.5853 | 4.6033 | 0.0585 | `experiments/submissions/submission_v1863_v1850g_alpha1p0_scoreblend_private.csv` |
| 4 | v1863_24 | v1848g | 1.00 | 0.5845 | 4.5774 | 0.0427 | `experiments/submissions/submission_v1863_v1848g_alpha1p0_scoreblend_private.csv` |
| 5 | v1863_23 | v1848g | 0.85 | 0.5773 | 3.8686 | 0.0363 | `experiments/submissions/submission_v1863_v1848g_alpha0p85_scoreblend_private.csv` |
| 6 | v1863_17 | v1850g | 0.85 | 0.5773 | 3.8197 | 0.0497 | `experiments/submissions/submission_v1863_v1850g_alpha0p85_scoreblend_private.csv` |
| 7 | v1863_11 | v1853g | 0.85 | 0.5777 | 3.7697 | 0.0596 | `experiments/submissions/submission_v1863_v1853g_alpha0p85_scoreblend_private.csv` |
| 8 | v1863_30 | v1846g | 1.00 | 0.5742 | 3.6286 | 0.0155 | `experiments/submissions/submission_v1863_v1846g_alpha1p0_scoreblend_private.csv` |
| 9 | v1863_22 | v1848g | 0.70 | 0.5746 | 3.6069 | 0.0299 | `experiments/submissions/submission_v1863_v1848g_alpha0p7_scoreblend_private.csv` |
| 10 | v1863_16 | v1850g | 0.70 | 0.5746 | 3.5619 | 0.0409 | `experiments/submissions/submission_v1863_v1850g_alpha0p7_scoreblend_private.csv` |

## Decision

No partial alpha below 1.00 dominated the existing full-strength score-only safe queue.  Therefore no new package queue is added from v1863.

Highest public-proxy generated blend:

```text
experiments/submissions/submission_v1863_v1853g_alpha1p0_scoreblend_private.csv
```

Operational first upload remains the v1862 lower role-risk file:

```text
experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
```

The active goal is still incomplete until a real private score greater than `0.50671` is reported.

## Artifacts

- `experiments/reports/v1863_scoreonly_blend_ladder.csv`
