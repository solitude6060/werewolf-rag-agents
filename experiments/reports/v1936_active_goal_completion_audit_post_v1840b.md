# v1936 Active Goal Completion Audit after `v1840b=0.49266`

> Superseded note, 2026-05-15: `v1840c` later returned a real private score of
> `0.49349`.  The current last-shot package is now governed by
> `experiments/reports/v1937_last_chance_0p5_rolecap_override.md`.
> Do not use this v1936 audit as the current upload instruction.

## Objective restatement

Original goal: exceed the current top-three private leaderboard cutoff during the final HW2 submission sprint.

Concrete completion criterion:

- Real private score must be strictly greater than `0.52380`.

Current audit result:

- `GOAL_COMPLETE=no`
- Best recorded score is `0.49266`
- Gap to completion gate is `0.03114`

## Prompt-to-artifact checklist

| Requirement / deliverable | Concrete evidence | Status |
| --- | --- | --- |
| Track real private score updates | `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv` has `v1840b` recorded as `0.49266` | Pass |
| Determine whether the goal is complete | `python3 experiments/scripts/v1906_goal_completion_gate.py --out-json /tmp/hw2_post049266_final_gate.json --out-md /tmp/hw2_post049266_final_gate.md` returned `GOAL_COMPLETE=no`, `BEST_SCORE=0.49266`, `TOP3_THRESHOLD=0.52380` | Not complete |
| Provide a current manual upload path | `python3 experiments/scripts/v1921_upload_now_console.py` returned `READY_TO_UPLOAD=yes` and `UPLOAD_PATH=experiments/final_submission_package/current_upload/submission.csv` | Pass |
| Preserve the staged candidate identity | Current upload metadata reports `CANDIDATE=v1840c`, `ROWS=397`, SHA-256 `fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145` | Pass |
| Validate current upload format | `python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv` returned `OK: 397 predictions validated` | Pass |
| Confirm attempt budget | `python3 experiments/scripts/v1869_attempt_budget_guard.py` returned `attempts_used=3`, `attempts_remaining=2`, `best_score=0.49266` | Pass |
| Ensure a non-top-three `v1840c` result has a concrete next route | `python3 experiments/scripts/v1872_post_score_command_center.py --score 0.49266` dry-run returned `recommended_next=experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` and `NEXT_PATH_STATUS=concrete_ok:black_boost_queue#5:v1842e` | Pass |
| Validate final fallback candidate | `python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` returned `OK: 397 predictions validated` | Pass |
| Identify paths that must not be uploaded | `v1921_upload_now_console.py` lists legacy `673`-row worktree paths under `DO_NOT_UPLOAD` with `sha_matches=no` | Pass |
| Stop the active goal only when achieved | Completion gate says `GOAL_COMPLETE=no`; no `update_goal` call is allowed | Pass |

## Current upload handoff

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
v1840c
```

SHA-256:

```text
fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145
```

## If `v1840c` misses the gate

The verified concrete fallback is:

```text
experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv
```

Candidate:

```text
v1842e
```

SHA-256:

```text
6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f
```

## Missing / weakly verified items

- No real private score has been reported for `v1840c` yet.
- No real private score above `0.52380` has been recorded.
- External manual upload remains outside local verification.

## Decision

The goal is not complete. Continue with the current upload path and wait for the real `v1840c` private score before recording another result or staging `v1842e`.
