# HW2 Final Submission Package

Student ID: `D13922024`  
Package date: `2026-05-14`  
Assignment deadline: `2026-05-15 23:59`  
Preset: `full`

## One-command rebuild

From the workspace root:

```bash
python3 experiments/scripts/v1835_final_submission_pack.py --preset full
```

Useful variants:

```bash
python3 experiments/scripts/v1835_final_submission_pack.py --preset queue
python3 experiments/scripts/v1835_final_submission_pack.py --preset known-best
python3 experiments/scripts/v1835_final_submission_pack.py --preset known-best-overlay
python3 experiments/scripts/v1835_final_submission_pack.py --preset contingency
python3 experiments/scripts/v1835_final_submission_pack.py --preset overlay
python3 experiments/scripts/v1835_final_submission_pack.py --preset attack-queue
python3 experiments/scripts/v1835_final_submission_pack.py --preset black-boost-queue
python3 experiments/scripts/v1835_final_submission_pack.py --preset rolecap-queue
python3 experiments/scripts/v1835_final_submission_pack.py --preset rolecap-fallback
python3 experiments/scripts/v1835_final_submission_pack.py --preset denoise-queue
python3 experiments/scripts/v1835_final_submission_pack.py --preset denoise-fallback
python3 experiments/scripts/v1835_final_submission_pack.py --preset lowtail-queue
python3 experiments/scripts/v1835_final_submission_pack.py --preset lowtail-fallback
python3 experiments/scripts/v1835_final_submission_pack.py --preset charprior-queue
python3 experiments/scripts/v1835_final_submission_pack.py --preset charprior-fallback
python3 experiments/scripts/v1835_final_submission_pack.py --preset balancedprior-queue
python3 experiments/scripts/v1835_final_submission_pack.py --preset balancedprior-fallback
python3 experiments/scripts/v1835_final_submission_pack.py --preset portfolio-queue
python3 experiments/scripts/v1835_final_submission_pack.py --preset scoreonly-safe-queue
python3 experiments/scripts/v1835_final_submission_pack.py --preset full --skip-validation
```

## What to upload to Kaggle

Upload one CSV from the selected queue/fallback group; use the strategy table and router before spending the next attempt.
Stop immediately if any score is above `0.50671`.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1826a | pending | `experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv` | Upload first in the normal final-attempt sequence. |
| 2 | v1826b | pending | `experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv` | Use if v1826a improves or gives a positive signal. |
| 3 | v1826d | pending | `experiments/final_submission_package/queue/03_v1826d_if_02_positive_private.csv` | Use if v1826b improves over v1826a. |
| 4 | v1826c | pending | `experiments/final_submission_package/queue/04_v1826c_alt_structural_private.csv` | Use if still below the top-3 threshold and testing the g6 structural lane is acceptable. |
| 5 | v1829e | pending | `experiments/final_submission_package/queue/05_v1829e_clean_hailmary_private.csv` | Preferred final-slot attempt if earlier queue entries are positive but still below top-3. |

## Score-attack queue

This is the highest public-proxy AP-only five-shot queue. Use it only if accepting the v1840 overlay risk.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1841a | pending | `experiments/final_submission_package/attack_queue/01_v1841a_queue01_v1826a_attack_overlay_private.csv` | Highest public-proxy first shot; v1826a plus v1840 AP-only overlay. |
| 2 | v1841b | pending | `experiments/final_submission_package/attack_queue/02_v1841b_queue02_v1826b_attack_overlay_private.csv` | Use after a positive first score; v1826b plus v1840 AP-only overlay. |
| 3 | v1841c | pending | `experiments/final_submission_package/attack_queue/03_v1841c_queue03_v1826d_attack_overlay_private.csv` | Use if order 2 improves over order 1; v1826d plus v1840 AP-only overlay. |
| 4 | v1841d | pending | `experiments/final_submission_package/attack_queue/04_v1841d_queue04_v1826c_attack_overlay_private.csv` | Use if still below threshold and testing the g6 structural lane is acceptable. |
| 5 | v1841e | pending | `experiments/final_submission_package/attack_queue/05_v1841e_queue05_v1829e_attack_overlay_private.csv` | Final high-upside attack-queue shot; v1829e plus v1840 AP-only overlay. |

## Maximum public-proxy black-boost queue

This queue has the highest public proxy but also the highest AP false-positive risk.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1842a | pending | `experiments/final_submission_package/black_boost_queue/01_v1842a_queue01_v1826a_blackboost_attack_private.csv` | Maximum public-proxy first shot; highest AP risk. |
| 2 | v1842b | pending | `experiments/final_submission_package/black_boost_queue/02_v1842b_queue02_v1826b_blackboost_attack_private.csv` | Use after a positive first score if staying in maximum-risk queue. |
| 3 | v1842c | pending | `experiments/final_submission_package/black_boost_queue/03_v1842c_queue03_v1826d_blackboost_attack_private.csv` | Use if order 2 improves over order 1. |
| 4 | v1842d | pending | `experiments/final_submission_package/black_boost_queue/04_v1842d_queue04_v1826c_blackboost_attack_private.csv` | Use if still below threshold and accepting g6 plus black-boost risk. |
| 5 | v1842e | pending | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` | Final maximum public-proxy AP-risk shot. |

## Role-cap queue

This queue has the strongest public proxy by capping generic Werewolf-role 1.0 scores to 0.99.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1846a | pending | `experiments/final_submission_package/rolecap_queue/01_v1846a_queue01_v1842a_rolecap099_private.csv` | New maximum-public-proxy first shot if accepting AP-rank calibration risk. |
| 2 | v1846b | pending | `experiments/final_submission_package/rolecap_queue/02_v1846b_queue02_v1842b_rolecap099_private.csv` | Use after a positive v1846a score if staying in role-cap queue. |
| 3 | v1846c | pending | `experiments/final_submission_package/rolecap_queue/03_v1846c_queue03_v1842c_rolecap099_private.csv` | Use if order 2 improves over order 1. |
| 4 | v1846d | pending | `experiments/final_submission_package/rolecap_queue/04_v1846d_queue04_v1842d_rolecap099_private.csv` | Use if still below threshold and accepting the g6 lane plus role-cap risk. |
| 5 | v1846e | pending | `experiments/final_submission_package/rolecap_queue/05_v1846e_queue05_v1842e_rolecap099_private.csv` | Final role-cap high-upside shot. |

## Role-cap fallback

These score-only fallback candidates preserve the verified-best role labels where possible.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1846f | pending | `experiments/final_submission_package/rolecap_fallback/01_v1846f_v1824a_rolecap099_private.csv` | Low-structural-risk role-cap fallback on verified-best v1824a. |
| 2 | v1846g | pending | `experiments/final_submission_package/rolecap_fallback/02_v1846g_v1845c_rolecap099_private.csv` | Score-only fallback with black-evidence overlay plus role-cap calibration. |

## Denoise queue

This queue has the highest public proxy but adds a denoise layer on top of role-cap calibration.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1848a | pending | `experiments/final_submission_package/denoise_queue/01_v1848a_queue01_v1846a_denoise_private.csv` | Most aggressive public-proxy first shot if accepting non-Werewolf denoise risk. |
| 2 | v1848b | pending | `experiments/final_submission_package/denoise_queue/02_v1848b_queue02_v1846b_denoise_private.csv` | Use after a positive v1848a score if staying in denoise queue. |
| 3 | v1848c | pending | `experiments/final_submission_package/denoise_queue/03_v1848c_queue03_v1846c_denoise_private.csv` | Use if order 2 improves over order 1. |
| 4 | v1848d | pending | `experiments/final_submission_package/denoise_queue/04_v1848d_queue04_v1846d_denoise_private.csv` | Use if still below threshold and accepting g6 lane plus denoise risk. |
| 5 | v1848e | pending | `experiments/final_submission_package/denoise_queue/05_v1848e_queue05_v1846e_denoise_private.csv` | Final denoise high-upside shot. |

## Denoise fallback

These score-only fallback candidates use the same denoise calibration with lower structural risk.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1848f | pending | `experiments/final_submission_package/denoise_fallback/01_v1848f_v1824a_rolecap_denoise_private.csv` | Lower-structural-risk denoise fallback on verified-best v1824a. |
| 2 | v1848g | pending | `experiments/final_submission_package/denoise_fallback/02_v1848g_v1845c_rolecap_denoise_private.csv` | Score-only denoise fallback with v1845c black-evidence overlay. |

## Low-tail queue

This queue has the absolute highest public proxy but only a tiny lift over denoise queue.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1850a | pending | `experiments/final_submission_package/lowtail_queue/01_v1850a_queue01_v1848a_lowtail_private.csv` | Absolute highest public-proxy first shot; marginal extra calibration over v1848. |
| 2 | v1850b | pending | `experiments/final_submission_package/lowtail_queue/02_v1850b_queue02_v1848b_lowtail_private.csv` | Use after a positive v1850a score if staying in low-tail queue. |
| 3 | v1850c | pending | `experiments/final_submission_package/lowtail_queue/03_v1850c_queue03_v1848c_lowtail_private.csv` | Use if order 2 improves over order 1. |
| 4 | v1850d | pending | `experiments/final_submission_package/lowtail_queue/04_v1850d_queue04_v1848d_lowtail_private.csv` | Use if still below threshold and accepting maximum calibration risk. |
| 5 | v1850e | pending | `experiments/final_submission_package/lowtail_queue/05_v1850e_queue05_v1848e_lowtail_private.csv` | Final low-tail high-upside shot. |

## Low-tail fallback

These score-only fallback candidates add the same low-tail denoise calibration.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1850f | pending | `experiments/final_submission_package/lowtail_fallback/01_v1850f_v1848f_lowtail_private.csv` | Lower-structural-risk low-tail fallback. |
| 2 | v1850g | pending | `experiments/final_submission_package/lowtail_fallback/02_v1850g_v1848g_lowtail_private.csv` | Score-only low-tail fallback with v1845c role-preserving branch. |

## Character-prior queue

This queue has the highest local public proxy but uses public-label character priors, so it is the highest calibration-risk option.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1853a | pending | `experiments/final_submission_package/charprior_queue/01_v1853a_queue01_v1850a_charprior_private.csv` | Highest local public-proxy first shot; high public-label calibration risk. |
| 2 | v1853b | pending | `experiments/final_submission_package/charprior_queue/02_v1853b_queue02_v1850b_charprior_private.csv` | Use after a positive v1853a score if staying in character-prior queue. |
| 3 | v1853c | pending | `experiments/final_submission_package/charprior_queue/03_v1853c_queue03_v1850c_charprior_private.csv` | Use if order 2 improves over order 1. |
| 4 | v1853d | pending | `experiments/final_submission_package/charprior_queue/04_v1853d_queue04_v1850d_charprior_private.csv` | Use if still below threshold and accepting maximum calibration risk. |
| 5 | v1853e | pending | `experiments/final_submission_package/charprior_queue/05_v1853e_queue05_v1850e_charprior_private.csv` | Final character-prior high-upside shot. |

## Character-prior fallback

These score-only fallback candidates add the same character-prior tie-break calibration.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1853f | pending | `experiments/final_submission_package/charprior_fallback/01_v1853f_v1850f_charprior_private.csv` | Lower-structural-risk character-prior fallback. |
| 2 | v1853g | pending | `experiments/final_submission_package/charprior_fallback/02_v1853g_v1850g_charprior_private.csv` | Score-only character-prior fallback with v1845c role-preserving branch. |

## Balanced-prior queue

This queue is the risk-balanced alternative: lower proxy than character-prior queue, but stronger no-leak heldout evidence.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1856a | pending | `experiments/final_submission_package/balancedprior_queue/01_v1856a_queue01_v1850a_balancedprior_private.csv` | Balanced public-prior first shot; lower proxy than v1853 but stronger no-leak audit. |
| 2 | v1856b | pending | `experiments/final_submission_package/balancedprior_queue/02_v1856b_queue02_v1850b_balancedprior_private.csv` | Use after a positive v1856a score if staying in balanced-prior queue. |
| 3 | v1856c | pending | `experiments/final_submission_package/balancedprior_queue/03_v1856c_queue03_v1850c_balancedprior_private.csv` | Use if order 2 improves over order 1. |
| 4 | v1856d | pending | `experiments/final_submission_package/balancedprior_queue/04_v1856d_queue04_v1850d_balancedprior_private.csv` | Use if still below threshold and accepting balanced calibration risk. |
| 5 | v1856e | pending | `experiments/final_submission_package/balancedprior_queue/05_v1856e_queue05_v1850e_balancedprior_private.csv` | Final balanced-prior high-upside shot. |

## Balanced-prior fallback

These score-only fallback candidates add the same balanced non-Werewolf mid-tier calibration.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1856f | pending | `experiments/final_submission_package/balancedprior_fallback/01_v1856f_v1850f_balancedprior_private.csv` | Lower-structural-risk balanced-prior fallback. |
| 2 | v1856g | pending | `experiments/final_submission_package/balancedprior_fallback/02_v1856g_v1850g_balancedprior_private.csv` | Score-only balanced-prior fallback with v1845c role-preserving branch. |

## Portfolio queue

This queue spreads the remaining five attempts across distinct risk layers rather than spending all slots inside one calibration family.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1856a | pending | `experiments/final_submission_package/portfolio_queue/01_v1856a_risk_balanced_first_private.csv` | First upload in the cross-risk portfolio queue. |
| 2 | v1853a | pending | `experiments/final_submission_package/portfolio_queue/02_v1853a_max_proxy_second_private.csv` | Use after a positive v1856a signal or when maximum local-proxy upside is needed. |
| 3 | v1850a | pending | `experiments/final_submission_package/portfolio_queue/03_v1850a_lowtail_fallback_private.csv` | Use if avoiding the character-prior calibration risk. |
| 4 | v1848a | pending | `experiments/final_submission_package/portfolio_queue/04_v1848a_denoise_fallback_private.csv` | Use as a lower-calibration denoise fallback. |
| 5 | v1846a | pending | `experiments/final_submission_package/portfolio_queue/05_v1846a_rolecap_fallback_private.csv` | Use as the final robust role-cap fallback. |

## Score-only safe queue

This queue preserves the verified-best role labels and only changes wolf scores. It is the lower-F1-risk companion to the portfolio queue.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1856g | pending | `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` | Use first when preserving the verified-best role labels is prioritized. |
| 2 | v1853g | pending | `experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv` | Use after a positive v1856g signal or when maximum score-only public proxy is needed. |
| 3 | v1850g | pending | `experiments/final_submission_package/scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv` | Use if avoiding character-prior calibration risk. |
| 4 | v1848g | pending | `experiments/final_submission_package/scoreonly_safe_queue/04_v1848g_scoreonly_denoise_private.csv` | Use as a lower-calibration score-only denoise fallback. |
| 5 | v1846g | pending | `experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv` | Use as the final low-distance score-only fallback. |

## Current verified rollback set

If no new final-attempt CSV improves, keep the best verified candidate below as the final rollback.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1824a | 0.47119 | `experiments/final_submission_package/known_best/01_v1824a_score_0p47119_private.csv` | Current best verified private score; keep as rollback/final if no new attempt improves. |
| 2 | v1823a | 0.46492 | `experiments/final_submission_package/known_best/02_v1823a_score_0p46492_private.csv` | Known positive stack backup. |
| 3 | v1823b | 0.46492 | `experiments/final_submission_package/known_best/03_v1823b_score_0p46492_private.csv` | Alternative tied backup with g30 Dieter branch. |
| 4 | v1821a | 0.46455 | `experiments/final_submission_package/known_best/04_v1821a_score_0p46455_private.csv` | Stable claim-graph repair baseline. |
| 5 | v1819b | 0.45499 | `experiments/final_submission_package/known_best/05_v1819b_score_0p45499_private.csv` | Conservative older high-score backup. |

## Verified-best score-only overlays

These candidates keep the verified-best role labels and change only scores. Use them as fallback diagnostics when structural queues look too risky.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1845a | pending | `experiments/final_submission_package/known_best_overlay/01_v1845a_v1824a_strict_ap_overlay_private.csv` | Score-only fallback on verified-best v1824a if structural role changes are considered too risky. |
| 2 | v1845b | pending | `experiments/final_submission_package/known_best_overlay/02_v1845b_v1824a_medium_ap_overlay_private.csv` | Score-only fallback on v1824a with the v1840 Medium-result agree-direction gate. |
| 3 | v1845c | pending | `experiments/final_submission_package/known_best_overlay/03_v1845c_v1824a_blackboost_score_overlay_private.csv` | Maximum public-proxy score-only fallback on verified-best v1824a. |

## Contingency candidates

These are not the primary five-shot queue. They exist to support adaptive decisions after tomorrow's real scores.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1825c | pending | `experiments/final_submission_package/contingency/01_v1825c_diagnostic_neutral_private.csv` | Use if v1826a is near-neutral and the AP boost layer needs isolation. |
| 2 | v1825a | pending | `experiments/final_submission_package/contingency/02_v1825a_diagnostic_mild_regression_private.csv` | Use if v1826a mildly regresses but the g4 isolate remains worth testing. |
| 3 | v1827a | pending | `experiments/final_submission_package/contingency/03_v1827a_fallback_severe_regression_private.csv` | Use if v1826a severely regresses and the g4/g29 family should be abandoned. |
| 4 | v1827d | pending | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | Use if v1826a improves but v1826b regresses or is neutral. |
| 5 | v1826e | pending | `experiments/final_submission_package/contingency/05_v1826e_standard_allin_private.csv` | Use only if avoiding g17/g27 residues is preferred over the cleaner Hail Mary queue file. |
| 6 | v1829d | pending | `experiments/final_submission_package/contingency/06_v1829d_maximum_allin_private.csv` | Use only as a true final-slot maximum-risk attempt. |

## Optional confirmed-white overlays

These overlay candidates are not required for the primary queue, but they add the v1838 confirmed-white AP demote.

| Order | Candidate | Private score | File | Condition |
| ---: | --- | ---: | --- | --- |
| 1 | v1838a | pending | `experiments/final_submission_package/overlay/01_v1838a_v1826a_confirmed_white_overlay_private.csv` | Optional replacement for queue order 1 if accepting the confirmed-white AP demote overlay. |
| 2 | v1838b | pending | `experiments/final_submission_package/overlay/02_v1838b_v1826d_confirmed_white_overlay_private.csv` | Optional replacement for v1826d if the v1826b direction is confirmed. |
| 3 | v1838c | pending | `experiments/final_submission_package/overlay/03_v1838c_v1829e_confirmed_white_overlay_private.csv` | Optional replacement for the final Hail Mary queue file. |
| 4 | v1839a | pending | `experiments/final_submission_package/overlay/04_v1839a_v1826a_high_precision_ap_overlay_private.csv` | Optional stronger AP-only replacement for queue order 1. |
| 5 | v1839b | pending | `experiments/final_submission_package/overlay/05_v1839b_v1826d_high_precision_ap_overlay_private.csv` | Optional stronger AP-only replacement for v1826d after v1826b is positive. |
| 6 | v1839c | pending | `experiments/final_submission_package/overlay/06_v1839c_v1829e_high_precision_ap_overlay_private.csv` | Optional stronger AP-only replacement for the final Hail Mary queue file. |
| 7 | v1840a | pending | `experiments/final_submission_package/overlay/07_v1840a_v1826a_high_precision_medium_ap_overlay_private.csv` | Optional most aggressive AP-only replacement for queue order 1. |
| 8 | v1840b | pending | `experiments/final_submission_package/overlay/08_v1840b_v1826d_high_precision_medium_ap_overlay_private.csv` | Optional most aggressive AP-only replacement for v1826d after v1826b is positive. |
| 9 | v1840c | pending | `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv` | Optional most aggressive AP-only replacement for the final Hail Mary queue file. |

## Score feedback router

After a manual Kaggle upload, preview the next action with:

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --order 1 --score <PRIVATE_SCORE> --dry-run
```

To record a real score, add `--confirm-real-score` and remove `--dry-run`.

## Report / COOL package mapping

The course zip should be named `hw2_D13922024.zip` and contain:

| Required item | Source to use |
| --- | --- |
| `hw2_D13922024.pdf` | Convert `reports/hw2_report_draft.md` to PDF and keep within 5 pages. |
| `main.py` | `werewolf-project/main.py` |
| `assert/` | `werewolf-project/assert/` |
| `requirements.txt` | `werewolf-project/requirements.txt` |
| `README` | Use this package README or `werewolf-project/README.md` after final cleanup. |

Staging folder: `cool_package/hw2_D13922024/`.

## Checks already recorded here

- Candidate hashes and row counts: `manifests/final_submission_pack_manifest.csv`
- CSV validation evidence: `manifests/validation_log.txt`
- Submission-facing document lint: `manifests/document_lint_log.txt`
- Rebuild checklist: `reports/reproducibility_checklist.md`
