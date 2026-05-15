# v1875 Route Matrix Regression

Date: 2026-05-15

## Summary

- Scenarios checked: `45`
- Failures: `0`
- Concrete CSV recommendations are checked against manifest membership, file existence, row count, SHA-256, and manifest validation status.

## v1874 boundary cases

| label | group | order | score | previous_score | recommended_next | status | pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| order1_tiny_positive_v1874 | scoreonly_safe_queue | 1 | 0.47120 |  | experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv | concrete_ok:scoreonly_safe_queue#2:v1853g | yes |
| order1_exact_current_best_v1874 | scoreonly_safe_queue | 1 | 0.47119 |  | experiments/final_submission_package/scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv | concrete_ok:scoreonly_safe_queue#3:v1850g | yes |

## Full matrix

| label | group | order | score | previous_score | recommended_next | status | pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| order1_top3 | scoreonly_safe_queue | 1 | 0.52381 |  | STOP: score exceeds top-3 threshold. | non_concrete_ok | yes |
| order1_strong_positive | scoreonly_safe_queue | 1 | 0.48000 |  | experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv | concrete_ok:scoreonly_safe_queue#2:v1853g | yes |
| order1_tiny_positive_v1874 | scoreonly_safe_queue | 1 | 0.47120 |  | experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv | concrete_ok:scoreonly_safe_queue#2:v1853g | yes |
| order1_exact_current_best_v1874 | scoreonly_safe_queue | 1 | 0.47119 |  | experiments/final_submission_package/scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv | concrete_ok:scoreonly_safe_queue#3:v1850g | yes |
| order1_near_baseline | scoreonly_safe_queue | 1 | 0.47080 |  | experiments/final_submission_package/scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv | concrete_ok:scoreonly_safe_queue#3:v1850g | yes |
| order1_small_regression | scoreonly_safe_queue | 1 | 0.46600 |  | experiments/final_submission_package/scoreonly_safe_queue/04_v1848g_scoreonly_denoise_private.csv | concrete_ok:scoreonly_safe_queue#4:v1848g | yes |
| order1_severe_regression | scoreonly_safe_queue | 1 | 0.46400 |  | experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv | concrete_ok:scoreonly_safe_queue#5:v1846g | yes |
| order2_beats_first | scoreonly_safe_queue | 2 | 0.48001 | 0.48000 | experiments/final_submission_package/portfolio_queue/02_v1853a_max_proxy_second_private.csv | concrete_ok:portfolio_queue#2:v1853a | yes |
| order2_ties_first | scoreonly_safe_queue | 2 | 0.48000 | 0.48000 | experiments/final_submission_package/scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv | concrete_ok:scoreonly_safe_queue#3:v1850g | yes |
| order2_below_first | scoreonly_safe_queue | 2 | 0.47900 | 0.48000 | experiments/final_submission_package/scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv | concrete_ok:scoreonly_safe_queue#3:v1850g | yes |
| scoreonly_safe_queue_order3_positive | scoreonly_safe_queue | 3 | 0.47200 |  | experiments/final_submission_package/portfolio_queue/03_v1850a_lowtail_fallback_private.csv | concrete_ok:portfolio_queue#3:v1850a | yes |
| scoreonly_safe_queue_order3_regression | scoreonly_safe_queue | 3 | 0.46600 |  | experiments/final_submission_package/scoreonly_safe_queue/04_v1848g_scoreonly_denoise_private.csv | concrete_ok:scoreonly_safe_queue#4:v1848g | yes |
| scoreonly_safe_queue_order3_top3 | scoreonly_safe_queue | 3 | 0.52381 |  | STOP: score exceeds top-3 threshold. | non_concrete_ok | yes |
| scoreonly_safe_queue_order4_positive | scoreonly_safe_queue | 4 | 0.47200 |  | experiments/final_submission_package/portfolio_queue/04_v1848a_denoise_fallback_private.csv | concrete_ok:portfolio_queue#4:v1848a | yes |
| scoreonly_safe_queue_order4_regression | scoreonly_safe_queue | 4 | 0.46600 |  | experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv | concrete_ok:scoreonly_safe_queue#5:v1846g | yes |
| scoreonly_safe_queue_order4_top3 | scoreonly_safe_queue | 4 | 0.52381 |  | STOP: score exceeds top-3 threshold. | non_concrete_ok | yes |
| scoreonly_safe_queue_order5_positive | scoreonly_safe_queue | 5 | 0.47200 |  | experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv | concrete_ok:queue#1:v1826a | yes |
| scoreonly_safe_queue_order5_regression | scoreonly_safe_queue | 5 | 0.46600 |  | experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv | concrete_ok:queue#1:v1826a | yes |
| scoreonly_safe_queue_order5_top3 | scoreonly_safe_queue | 5 | 0.52381 |  | STOP: score exceeds top-3 threshold. | non_concrete_ok | yes |
| portfolio_queue_order3_positive | portfolio_queue | 3 | 0.47200 |  | experiments/final_submission_package/portfolio_queue/04_v1848a_denoise_fallback_private.csv | concrete_ok:portfolio_queue#4:v1848a | yes |
| portfolio_queue_order3_regression | portfolio_queue | 3 | 0.46600 |  | experiments/final_submission_package/portfolio_queue/04_v1848a_denoise_fallback_private.csv | concrete_ok:portfolio_queue#4:v1848a | yes |
| portfolio_queue_order3_top3 | portfolio_queue | 3 | 0.52381 |  | STOP: score exceeds top-3 threshold. | non_concrete_ok | yes |
| portfolio_queue_order4_positive | portfolio_queue | 4 | 0.47200 |  | experiments/final_submission_package/portfolio_queue/05_v1846a_rolecap_fallback_private.csv | concrete_ok:portfolio_queue#5:v1846a | yes |
| portfolio_queue_order4_regression | portfolio_queue | 4 | 0.46600 |  | experiments/final_submission_package/portfolio_queue/05_v1846a_rolecap_fallback_private.csv | concrete_ok:portfolio_queue#5:v1846a | yes |
| portfolio_queue_order4_top3 | portfolio_queue | 4 | 0.52381 |  | STOP: score exceeds top-3 threshold. | non_concrete_ok | yes |
| portfolio_queue_order5_positive | portfolio_queue | 5 | 0.47200 |  | NO_PORTFOLIO_QUEUE_REMAINING: keep best verified score or choose contingency manually. | non_concrete_ok | yes |
| portfolio_queue_order5_regression | portfolio_queue | 5 | 0.46600 |  | NO_PORTFOLIO_QUEUE_REMAINING: keep best verified score or choose contingency manually. | non_concrete_ok | yes |
| portfolio_queue_order5_top3 | portfolio_queue | 5 | 0.52381 |  | STOP: score exceeds top-3 threshold. | non_concrete_ok | yes |
| portfolio_order1_positive | portfolio_queue | 1 | 0.47200 |  | experiments/final_submission_package/portfolio_queue/02_v1853a_max_proxy_second_private.csv | concrete_ok:portfolio_queue#2:v1853a | yes |
| portfolio_order1_near | portfolio_queue | 1 | 0.47080 |  | experiments/final_submission_package/portfolio_queue/03_v1850a_lowtail_fallback_private.csv | concrete_ok:portfolio_queue#3:v1850a | yes |
| portfolio_order1_regression | portfolio_queue | 1 | 0.46600 |  | experiments/final_submission_package/portfolio_queue/04_v1848a_denoise_fallback_private.csv | concrete_ok:portfolio_queue#4:v1848a | yes |
| portfolio_order2_beats_first_to_charprior | portfolio_queue | 2 | 0.48001 | 0.48000 | experiments/final_submission_package/charprior_queue/02_v1853b_queue02_v1850b_charprior_private.csv | concrete_ok:charprior_queue#2:v1853b | yes |
| portfolio_order2_below_first | portfolio_queue | 2 | 0.47900 | 0.48000 | experiments/final_submission_package/portfolio_queue/03_v1850a_lowtail_fallback_private.csv | concrete_ok:portfolio_queue#3:v1850a | yes |
| charprior_order2_beats_first | charprior_queue | 2 | 0.48101 | 0.48001 | experiments/final_submission_package/charprior_queue/03_v1853c_queue03_v1850c_charprior_private.csv | concrete_ok:charprior_queue#3:v1853c | yes |
| charprior_order2_below_first | charprior_queue | 2 | 0.48000 | 0.48001 | experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv | concrete_ok:contingency#4:v1827d | yes |
| charprior_order2_top3 | charprior_queue | 2 | 0.52381 | 0.48001 | STOP: score exceeds top-3 threshold. | non_concrete_ok | yes |
| charprior_queue_order3_positive | charprior_queue | 3 | 0.47200 |  | experiments/final_submission_package/charprior_queue/04_v1853d_queue04_v1850d_charprior_private.csv | concrete_ok:charprior_queue#4:v1853d | yes |
| charprior_queue_order3_regression | charprior_queue | 3 | 0.46600 |  | experiments/final_submission_package/charprior_queue/04_v1853d_queue04_v1850d_charprior_private.csv | concrete_ok:charprior_queue#4:v1853d | yes |
| charprior_queue_order3_top3 | charprior_queue | 3 | 0.52381 |  | STOP: score exceeds top-3 threshold. | non_concrete_ok | yes |
| charprior_queue_order4_positive | charprior_queue | 4 | 0.47200 |  | experiments/final_submission_package/charprior_queue/05_v1853e_queue05_v1850e_charprior_private.csv | concrete_ok:charprior_queue#5:v1853e | yes |
| charprior_queue_order4_regression | charprior_queue | 4 | 0.46600 |  | experiments/final_submission_package/charprior_queue/05_v1853e_queue05_v1850e_charprior_private.csv | concrete_ok:charprior_queue#5:v1853e | yes |
| charprior_queue_order4_top3 | charprior_queue | 4 | 0.52381 |  | STOP: score exceeds top-3 threshold. | non_concrete_ok | yes |
| charprior_queue_order5_positive | charprior_queue | 5 | 0.47200 |  | NO_CHARPRIOR_QUEUE_REMAINING: keep best verified score or choose contingency manually. | non_concrete_ok | yes |
| charprior_queue_order5_regression | charprior_queue | 5 | 0.46600 |  | NO_CHARPRIOR_QUEUE_REMAINING: keep best verified score or choose contingency manually. | non_concrete_ok | yes |
| charprior_queue_order5_top3 | charprior_queue | 5 | 0.52381 |  | STOP: score exceeds top-3 threshold. | non_concrete_ok | yes |

## Decision

All checked router outcomes are either concrete validated package files or intentional non-concrete stop/manual states.  No route-matrix failure is present.

## Completion boundary

This regression does not complete the active score objective; completion still requires a real Kaggle private score greater than `0.52380`.
