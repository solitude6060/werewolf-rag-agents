# v1937 Last-Chance 0.5 Role-Cap Override Report

## Result

The final remaining upload has been staged as `v1846e`, not the default router fallback `v1842e`.

Upload exactly:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Safe alias:

```text
hw2_D13922024/submission.csv
```

Candidate:

```text
v1846e
```

SHA-256:

```text
c9e4d0d236c08296f6a5501219d05eb1c5861345cd1de7dcbae5c11c83e75912
```

## Why `v1846e`

`v1840c` returned a real private score of `0.49349`.  With one upload remaining and the operational target moved to `0.50000`, the final shot needs at least `+0.00651`.

Candidate evidence:

| Candidate | Relationship to `v1840c` | Public proxy | Role changes | Score changes | Decision |
| --- | --- | ---: | ---: | ---: | --- |
| `v1842e` | router fallback, black-boost AP shot | `0.5448` | `0` | `3` | Rejected as too small a move for the last shot |
| `v1846e` | `v1842e` plus role-cap AP calibration | `0.5742` | `0` | `74` | Selected |
| `v1848e` | denoise calibration on top of `v1846e` | `0.5845` | `0` | `123` | Rejected as more calibration risk |
| `v1850e` | low-tail calibration on top of `v1848e` | `0.5853` | `0` | `180` | Rejected as more calibration risk |
| `v1853e` | character-prior calibration | `0.5942` | `0` | `212` | Rejected due prior-family transfer risk |
| `v1856e` | balanced-prior calibration | `0.5903` | `0` | `210` | Rejected due `v1856g=0.42894` real-score warning |

Supporting artifact:

- `experiments/reports/v1847_rolecap_robustness_audit.md` reports role-cap global public proxy delta `+0.0293`, leave-one-game-out positive deltas `20/20`, and no leave-one-game-out negatives.

## Prompt-to-artifact checklist

| Requirement / deliverable | Evidence | Status |
| --- | --- | --- |
| Record `v1840c=0.49349` as real score | `v1836_score_feedback_records.csv` has `v1840c`, score `0.49349`, `top3_hit=no` | Pass |
| Confirm only one attempt remains | `v1869_attempt_budget_guard.py` returned `attempts_used=4`, `attempts_remaining=1` | Pass |
| Select a final candidate for target `0.5` | `v1846e` staged with explicit override reason in `current_upload/metadata.json` | Pass |
| Keep role labels fixed | Candidate diff check found `role_diff=0` for `v1846e` relative to `v1840c` | Pass |
| Validate selected CSV format | `validate_submission.py experiments/final_submission_package/current_upload/submission.csv` returned `OK: 397 predictions validated` | Pass |
| Confirm upload readiness | `v1921_upload_now_console.py` returned `READY_TO_UPLOAD=yes`, candidate `v1846e` | Pass |
| Confirm package aliases match | `v1902_upload_alias_guard.py` returned `ALIAS_GUARD_READY=yes` and `sha_matches=yes` for safe aliases | Pass |
| Preserve top-three completion discipline | `v1906_goal_completion_gate.py` returned `GOAL_COMPLETE=no`, `BEST_SCORE=0.49349`, `TOP3_THRESHOLD=0.52380` | Pass |

## Completion boundary

The updated operational target is not complete until a real private score greater than `0.50000` is reported for the last upload.

The original top-three goal is not complete until a real private score greater than `0.52380` is reported and the completion gate confirms it.
