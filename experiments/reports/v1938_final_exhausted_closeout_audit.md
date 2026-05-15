# v1938 Final Exhausted Closeout Audit

## Objective restatement

Original active goal:

- Use the remaining final submissions to exceed the live top-three private leaderboard cutoff.
- Concrete top-three success criterion: real private score `>0.52380`.

User-updated operational target during the last attempt:

- Try to exceed real private score `>0.50000`.

Final state:

- Attempts used: `5/5`.
- Best verified private score: `0.49349` from `v1840c`.
- Last attempted score: `0.46698` from `v1846e`.
- Top-three goal: not achieved.
- Operational `0.50000` target: not achieved.

## Prompt-to-artifact checklist

| Requirement / deliverable | Evidence | Status |
| --- | --- | --- |
| Record all final real private scores | `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv` has 5 rows, including `v1846e=0.46698` | Pass |
| Identify best verified candidate | `v1869_attempt_budget_guard.py` reports `best_score=0.49349`, `best_candidate=v1840c` | Pass |
| Verify top-three completion gate | `v1906_goal_completion_gate.py` reports `GOAL_COMPLETE=no`, `BEST_SCORE=0.49349`, `TOP3_THRESHOLD=0.52380` | Not achieved |
| Verify user-updated `0.50000` target | Best score `0.49349` is below `0.50000` | Not achieved |
| Stop Ralph / OMX execution mode | `omx cancel` returned `Cancelled: ralph` | Pass |
| Do not falsely mark Codex goal complete | No `update_goal complete` call is valid because success criteria are not met | Pass |
| Package final hand-in around best candidate | `hw2_D13922024/submission.csv`, `final_current_private.csv`, and `final_v1840c_private.csv` are byte-identical | Pass |
| Preserve failed last attempt in records | `v1836_score_feedback_records.csv` records `v1846e=0.46698` and `NO_ROLECAP_QUEUE_REMAINING` | Pass |
| Update final report | `hw2_D13922024/hw2_report.md` states final packaged candidate `v1840c`, best score `0.49349`, and failed last attempt `v1846e=0.46698` | Pass |
| Update final package docs | `hw2_D13922024/README.md`, `experiments/final_submission_package/README.md`, `RELEASE_CHECKLIST.md`, and `reports/submission_strategy.md` describe exhausted-attempt final state | Pass |

## Final package default

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

## Decision

The score goal is stopped as unsuccessful/exhausted, not completed.  The final coursework package is organized around the best verified candidate `v1840c` and includes the final report and reproducibility commands.
