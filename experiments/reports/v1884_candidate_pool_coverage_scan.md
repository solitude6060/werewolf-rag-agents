# v1884 Candidate Pool Coverage Scan

Date: 2026-05-15

## Purpose

Scan private candidates under `experiments/submissions/` for high-public-proxy candidates that are not already represented in the final submission package.
This is a local decision-support audit only; it does not use private labels and does not prove Kaggle performance.

## Summary

- Private files scanned: `1331`
- Private/public pairs scored: `1309`
- Skipped without public counterpart: `22`
- Skipped due to scoring errors or no matches: `0`
- Final-package manifest rows: `73` source paths
- Final-package normalized prediction signatures: `70`
- Max packaged public proxy in v1873 audit: `0.594191203418`
- Active first-upload public proxy: `0.590336189619`

## Recommendation counts

| Recommendation | Count |
| --- | ---: |
| already_packaged | 73 |
| already_packaged_duplicate | 12 |
| not_preferred | 1224 |

## Top unmanifested candidates by public proxy

| Rank | Recommendation | Public score | Role changes vs v1824a | Score MAE vs v1824a | Private path |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | not_preferred | 0.577676 | 0 | 0.059577 | `experiments/submissions/submission_v1863_v1853g_alpha0p85_scoreblend_private.csv` |
| 2 | not_preferred | 0.577676 | 0 | 0.059577 | `experiments/submissions/submission_v1863k_v1853g_alpha0p85_scoreblend_private.csv` |
| 3 | not_preferred | 0.577346 | 0 | 0.036323 | `experiments/submissions/submission_v1863_v1848g_alpha0p85_scoreblend_private.csv` |
| 4 | not_preferred | 0.577346 | 0 | 0.036323 | `experiments/submissions/submission_v1863w_v1848g_alpha0p85_scoreblend_private.csv` |
| 5 | not_preferred | 0.577346 | 0 | 0.049693 | `experiments/submissions/submission_v1863_v1850g_alpha0p85_scoreblend_private.csv` |
| 6 | not_preferred | 0.577346 | 0 | 0.049693 | `experiments/submissions/submission_v1863q_v1850g_alpha0p85_scoreblend_private.csv` |
| 7 | not_preferred | 0.574639 | 0 | 0.029913 | `experiments/submissions/submission_v1863_v1848g_alpha0p7_scoreblend_private.csv` |
| 8 | not_preferred | 0.574639 | 0 | 0.029913 | `experiments/submissions/submission_v1863v_v1848g_alpha0p7_scoreblend_private.csv` |
| 9 | not_preferred | 0.574639 | 0 | 0.040924 | `experiments/submissions/submission_v1863_v1850g_alpha0p7_scoreblend_private.csv` |
| 10 | not_preferred | 0.574639 | 0 | 0.040924 | `experiments/submissions/submission_v1863p_v1850g_alpha0p7_scoreblend_private.csv` |
| 11 | not_preferred | 0.574603 | 0 | 0.049064 | `experiments/submissions/submission_v1863_v1853g_alpha0p7_scoreblend_private.csv` |
| 12 | not_preferred | 0.574603 | 0 | 0.049064 | `experiments/submissions/submission_v1863j_v1853g_alpha0p7_scoreblend_private.csv` |
| 13 | not_preferred | 0.573329 | 0 | 0.049492 | `experiments/submissions/submission_v1863_v1856g_alpha0p85_scoreblend_private.csv` |
| 14 | not_preferred | 0.573329 | 0 | 0.049492 | `experiments/submissions/submission_v1863e_v1856g_alpha0p85_scoreblend_private.csv` |
| 15 | not_preferred | 0.573151 | 0 | 0.038550 | `experiments/submissions/submission_v1863_v1853g_alpha0p55_scoreblend_private.csv` |
| 16 | not_preferred | 0.573151 | 0 | 0.038550 | `experiments/submissions/submission_v1863i_v1853g_alpha0p55_scoreblend_private.csv` |
| 17 | not_preferred | 0.571771 | 0 | 0.028036 | `experiments/submissions/submission_v1863_v1853g_alpha0p4_scoreblend_private.csv` |
| 18 | not_preferred | 0.571771 | 0 | 0.028036 | `experiments/submissions/submission_v1863h_v1853g_alpha0p4_scoreblend_private.csv` |
| 19 | not_preferred | 0.570327 | 0 | 0.040758 | `experiments/submissions/submission_v1863_v1856g_alpha0p7_scoreblend_private.csv` |
| 20 | not_preferred | 0.570327 | 0 | 0.040758 | `experiments/submissions/submission_v1863d_v1856g_alpha0p7_scoreblend_private.csv` |

## Review candidates above packaged max public proxy

No unmanifested candidate met the review thresholds of public proxy at or above the packaged maximum with <=4 role changes versus v1824a.

## Decision

No low-role-change, unmanifested unique prediction beats the packaged maximum public proxy threshold.  Keep the staged first upload unchanged.

## Completion boundary

This scan can identify missed local candidates, but it does not complete the active score goal.  Completion still requires a real Kaggle private score greater than `0.50671`.
