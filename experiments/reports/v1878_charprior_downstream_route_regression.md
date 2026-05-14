# v1878 Charprior Downstream Route Regression

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Purpose

After v1877 made the strong-positive portfolio branch route into `charprior_queue` order 2, the regression matrix needed to cover that new downstream branch.  This check ensures the newly reachable high-upside path points to concrete validated CSV files or intentional terminal states.

## Added route-matrix coverage

`experiments/scripts/v1875_route_matrix_regression.py` now includes:

| Scenario family | Expected behavior |
| --- | --- |
| `charprior_order2_beats_first` | Continue to `charprior_queue` order 3. |
| `charprior_order2_below_first` | Fall back to validated contingency `v1827d`. |
| `charprior_order2_top3` | Stop. |
| `charprior_queue_order3_*` | Continue to order 4 or stop. |
| `charprior_queue_order4_*` | Continue to order 5 or stop. |
| `charprior_queue_order5_*` | Terminal no-remaining or stop. |

## Validation evidence

```bash
python3 experiments/scripts/v1875_route_matrix_regression.py
```

Observed:

```text
SCENARIOS=45
FAILURES=0
```

Key downstream rows:

```text
charprior_order2_beats_first -> charprior_queue/03_v1853c_queue03_v1850c_charprior_private.csv
charprior_order2_below_first -> contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv
charprior_order2_top3 -> STOP
```

The route-matrix checker verifies concrete CSV recommendations against manifest membership, file existence, 397-row shape, SHA-256, and `validation_status=pass`.

## Completion boundary

This strengthens the post-feedback route coverage.  It does not complete the active score goal because completion still requires a real Kaggle private score greater than `0.50671`.
