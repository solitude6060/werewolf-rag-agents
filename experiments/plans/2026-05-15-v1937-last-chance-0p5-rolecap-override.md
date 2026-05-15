# v1937 Last-Chance 0.5 Role-Cap Override Plan

## Goal

Use the final remaining upload attempt to maximize the chance of crossing the user-updated operational target:

- Last-attempt target: real private score `>0.50000`.
- Original top-three gate remains: real private score `>0.52380`.

## Current score state

- `v1840c` real private score: `0.49349`.
- Current best: `0.49349`.
- Gap to last-attempt target `0.50000`: `0.00651`.
- Attempt budget: `4` used, `1` remaining.

## Decision

Override the router's concrete fallback from `v1842e` to `v1846e`.

Reason:

- `v1842e` is the route-safe fallback and changes only `3` score rows relative to `v1840c`.
- `v1846e` keeps the same role labels as `v1842e` and adds role-cap AP calibration.
- Public proxy comparison:
  - `v1840c`: `0.5412`
  - `v1842e`: `0.5448`
  - `v1846e`: `0.5742`
- v1847 robustness audit reports leave-one-game-out positive deltas `20/20` for the role-cap rule.
- Higher-calibration prior candidates (`v1853e`, `v1856e`) are rejected for this final shot because `v1856g` already returned a poor real private score (`0.42894`) despite high public proxy, weakening the prior-calibration family.

## Selected upload

```text
experiments/final_submission_package/current_upload/submission.csv
```

Candidate:

```text
v1846e
```

Source:

```text
experiments/final_submission_package/rolecap_queue/05_v1846e_queue05_v1842e_rolecap099_private.csv
```

SHA-256:

```text
c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912
```

## Validation standard

- Current upload validates as exactly `397` rows.
- Current upload SHA matches metadata and safe aliases.
- Pre-upload guard reports `UPLOAD_READY=yes`.
- Final preflight reports `READY_TO_MANUAL_UPLOAD=yes`.
- Package reproduction regression reports `FAILURES=0`.
- Score report guard reports `SCORE_REPORT_READY=yes`.
- Attempt state guard reports `manual_override_from_records` and records the override.

## Stop condition

After the real `v1846e` private score is reported:

1. Record it with the current score bridge.
2. If score is `>0.50000`, the updated operational target is met.
3. If score is `>0.52380`, the original top-three goal is also met and the active goal may be completed after the completion audit.
4. If neither threshold is met, stop local score-routing work because the attempt budget is exhausted.
