# v1935 v1840c Final Fallback Route Plan

## Goal

Ensure the score bridge gives a concrete final upload if `v1840c` misses the
top-3 cutoff.  After the `v1840b = 0.49266` score, `v1840c` is the next staged
upload and there should still be one final recorded attempt left after it.

## Problem

The router currently maps final overlay candidates back to queue order 5.  A
non-top-3 `v1840c` score therefore returns:

```text
NO_QUEUE_REMAINING: keep best verified score or choose maximum-risk contingency manually.
```

That is unsafe for a deadline sprint because it requires manual reasoning at
the last moment.

## Decision

Route any non-top-3 score for the final overlay lane to the concrete maximum
public-proxy final shot:

```text
experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv
```

Rationale:

- `v1840c` is equivalent to the attack-queue final overlay `v1841e`.
- `v1842e` is the same final Hail Mary family with the black-boost attack layer.
- If `v1840c` fails to clear top-3, the remaining useful local action is a
  maximum-upside final attempt, not a non-concrete manual state.

## Verification

- Add a dedicated regression for `v1840c` final fallback routing.
- Re-run the current score bridge sandbox regression.
- Confirm current upload remains `v1840c` and goal remains incomplete.

## Stop Condition

The router returns `v1842e` for non-top-3 `v1840c` scores and still stops for a
strict score greater than `0.52380`.
