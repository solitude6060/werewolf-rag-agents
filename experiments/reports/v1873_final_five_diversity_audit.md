# v1873 Final Five Diversity Audit

Date: 2026-05-15

## Purpose

Check whether the active five-attempt queue is redundant and whether an existing candidate should replace a later slot before real submissions.

## Score-only safe queue metrics

| order | candidate | public_score | risk_adjusted_index | vs_v1824a_role_changes | vs_v1824a_score_mae | vs_first_score_mae | vs_first_score_change_gt_0p05 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | v1856g | 0.5903361896187123 | 5.098339830837956 | 0 | 0.058226 | 0.000000 | 0 |
| 2 | v1853g | 0.5941912034175195 | 5.382555855554955 | 0 | 0.070091 | 0.014013 | 68 |
| 3 | v1850g | 0.5852922620653069 | 4.593710314792134 | 0 | 0.058463 | 0.003535 | 0 |
| 4 | v1848g | 0.5845146748726254 | 4.571983585448416 | 0 | 0.042733 | 0.019265 | 32 |
| 5 | v1846g | 0.5741717768357544 | 3.62919000342378 | 0 | 0.015469 | 0.042757 | 83 |

## Adjacent diversity inside the active safe queue

| from | to | role_changes | score_mae | score_change_gt_0p05 |
| --- | --- | --- | --- | --- |
| scoreonly_safe_queue#1 v1856g | scoreonly_safe_queue#2 v1853g | 0 | 0.014013 | 68 |
| scoreonly_safe_queue#2 v1853g | scoreonly_safe_queue#3 v1850g | 0 | 0.017327 | 72 |
| scoreonly_safe_queue#3 v1850g | scoreonly_safe_queue#4 v1848g | 0 | 0.015730 | 32 |
| scoreonly_safe_queue#4 v1848g | scoreonly_safe_queue#5 v1846g | 0 | 0.027264 | 51 |

## Top risk-adjusted alternatives among audited final-package queues

| group | order | candidate | public_score | risk_adjusted_index | vs_v1824a_role_changes | vs_v1824a_score_mae |
| --- | --- | --- | --- | --- | --- | --- |
| scoreonly_safe_queue | 2 | v1853g | 0.5941912034175195 | 5.382555855554955 | 0 | 0.070091 |
| portfolio_queue | 2 | v1853a | 0.5941912034175195 | 5.356968686789211 | 4 | 0.078046 |
| charprior_queue | 1 | v1853a | 0.5941912034175195 | 5.356968686789211 | 4 | 0.078046 |
| charprior_queue | 2 | v1853b | 0.5941912034175195 | 5.35441828124765 | 6 | 0.075558 |
| charprior_queue | 3 | v1853c | 0.5941912034175195 | 5.349608686789211 | 6 | 0.077849 |
| charprior_queue | 4 | v1853d | 0.5941912034175195 | 5.339608863111629 | 8 | 0.082811 |
| charprior_queue | 5 | v1853e | 0.5941912034175195 | 5.32654053565571 | 10 | 0.084544 |
| scoreonly_safe_queue | 1 | v1856g | 0.5903361896187123 | 5.098339830837956 | 0 | 0.058226 |
| portfolio_queue | 1 | v1856a | 0.5903361896187123 | 5.069127573911004 | 4 | 0.067287 |
| balancedprior_queue | 1 | v1856a | 0.5903361896187123 | 5.069127573911004 | 4 | 0.067287 |
| balancedprior_queue | 2 | v1856b | 0.5903361896187123 | 5.066860571392112 | 6 | 0.064516 |
| balancedprior_queue | 3 | v1856c | 0.5903361896187123 | 5.061596087764909 | 6 | 0.067262 |

## Decision

- Do not replace the first upload: `v1856g` remains the safest first shot because it has high public proxy while preserving verified-best private roles.
- The most attractive pure upside candidate remains `v1853g`; it is already the safe queue order 2.
- Structural `v1853a` has the same public proxy but adds private role changes; keep it as a router escalation after a positive `v1853g`, not as the initial no-feedback upload.
- The active safe queue is not identical-score redundant: later slots have non-trivial score distance from the first upload while keeping role changes at zero versus v1824a.
- Therefore no router/package change is made before the first real score.

## Completion boundary

This audit is local evidence only.  The active score goal still requires a real Kaggle private score greater than `0.50671`.
