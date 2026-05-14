# v1877 Positive Portfolio Route Closure

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Purpose

Remove one remaining manual decision point in the final-attempt router without spending a Kaggle attempt.  The active goal still requires a real private score greater than `0.50671`, but the route after a strong positive sequence should be concrete so the next upload can be staged reproducibly.

## Gap found

The package already contained `83` manifest rows, all with `validation_status=pass`, across the safe, portfolio, calibration, overlay, contingency, and known-best groups.

The active first upload and most feedback bands were concrete.  However, this feedback path still returned a manual message:

```text
portfolio_queue order 2 score > previous_score but score <= 0.50671
```

That path can occur after:

1. `scoreonly_safe_queue` order 1 (`v1856g`) gives a positive signal.
2. `scoreonly_safe_queue` order 2 (`v1853g`) improves further.
3. `portfolio_queue` order 2 (`v1853a`) improves further but still does not exceed `0.50671`.

Before this change, the router stopped at a non-concrete instruction for manual high-upside review.  That was safe, but it created avoidable deadline-day ambiguity.

## Change

`experiments/scripts/v1836_score_feedback_router.py` now routes that strong-positive portfolio branch to the next high-proxy character-prior variant:

```text
experiments/final_submission_package/charprior_queue/02_v1853b_queue02_v1850b_charprior_private.csv
```

Rationale:

- `v1853a` / `v1853b` share the highest local public proxy family.
- This route only activates after the corresponding structural high-proxy branch has already improved over the previous real score.
- It does not affect the first upload, conservative fallback bands, exact-current-best band, or top-3 stop condition.

## Validation evidence

```bash
python3 -m py_compile experiments/scripts/v1836_score_feedback_router.py experiments/scripts/v1875_route_matrix_regression.py
python3 experiments/scripts/v1836_score_feedback_router.py --group portfolio_queue --order 2 --score 0.48001 --previous-score 0.48000 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group portfolio_queue --order 2 --score 0.47900 --previous-score 0.48000 --dry-run
python3 experiments/scripts/v1875_route_matrix_regression.py
```

Observed:

```text
0.48001 vs previous 0.48000 -> charprior_queue/02_v1853b_queue02_v1850b_charprior_private.csv
0.47900 vs previous 0.48000 -> portfolio_queue/03_v1850a_lowtail_fallback_private.csv
route matrix -> SCENARIOS=33, FAILURES=0
```

The concrete recommendation is checked by the route matrix against manifest membership, file existence, 397-row shape, SHA-256, and `validation_status=pass`.

## Completion boundary

This closes a routing ambiguity.  It does not complete the active score goal because no real Kaggle private score greater than `0.50671` has been recorded.
