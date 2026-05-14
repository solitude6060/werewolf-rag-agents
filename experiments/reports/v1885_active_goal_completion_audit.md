# v1885 Active Goal Completion Audit

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`
Latest commit inspected: `4899f47`

## Objective restated as concrete criteria

The active objective is to use the remaining final attempts to move `D13922024` above the current third-place private leaderboard threshold.

Success requires all of the following:

1. A real Kaggle private score is obtained for a submitted CSV.
2. The real private score is strictly greater than `0.50671`.
3. The score is tied to an identifiable submitted file and attempt context.
4. The attempt budget remains within the five remaining submissions.
5. The score is not a local proxy, validator result, dry-run, manifest pass, or hypothetical route preview.

Current known context:

| Rank | Entrant | Private score |
| ---: | --- | ---: |
| 1 | D13922023 | 0.54251 |
| 2 | R14922115 | 0.52380 |
| 3 | R14942077 | 0.50671 |
| 4 | D13922036 | 0.47792 |
| 5 | D13922024 | 0.47119 |

## Prompt-to-artifact checklist

| Requirement / named gate | Evidence inspected | Result | Coverage verdict |
| --- | --- | --- | --- |
| Active goal is still open | Goal state inspected in this continuation | Status is `active`; target remains `>0.50671` | Covered; not complete |
| Branch/commit context is known | `git rev-parse --short HEAD`; `git status --short --branch -uno` | `4899f47`; clean tracked status on `dev/final-submission-report-pack` before fresh report creation | Covered |
| Attempt budget is intact | `python3 experiments/scripts/v1869_attempt_budget_guard.py` | `attempts_used=0`, `attempts_remaining=5`, `best_score=none`, `top3_hit=no` | Covered; no score yet |
| Score record existence is checked | `test -f experiments/final_submission_package/manifests/v1836_score_feedback_records.csv ...` | `NO_SCORE_RECORD_FILE` | Covered; completion evidence missing |
| Current upload path is concrete | `experiments/final_submission_package/current_upload/submission.csv` | File exists and is the staged upload | Covered |
| Current upload has valid assignment shape | `python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv` | `OK: 397 predictions validated` | Covered; proxy only |
| Current upload metadata is consistent | Metadata read from `experiments/final_submission_package/current_upload/metadata.json` | `scoreonly_safe_queue`, order `1`, candidate `v1856g` | Covered |
| Current upload SHA is fixed | SHA check in this continuation | `468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d` | Covered |
| Pre-upload guard passes | `python3 experiments/scripts/v1883_pre_upload_guard.py` | `UPLOAD_READY=yes`; rows `397`; same SHA; report/json written | Covered; proxy only |
| Local candidate pool has no missed unique high-proxy candidate | `python3 experiments/scripts/v1884_candidate_pool_coverage_scan.py` | `PRIVATE_FILES=1331`, `SCORED_PAIRS=1309`, `REVIEW_CANDIDATES=0` | Covered; proxy only |
| Post-score route matrix is green | `python3 experiments/scripts/v1875_route_matrix_regression.py` | `SCENARIOS=45`, `FAILURES=0` | Covered; route logic only |
| Command-center dry-run is non-mutating | `python3 experiments/scripts/v1882_command_center_dry_run_regression.py` | `SCENARIOS=7`, `FAILURES=0`, `MUTATION_OK=yes` | Covered; route logic only |
| Real private score is greater than `0.50671` | Score record or user-reported Kaggle result | No real score is present | Missing; goal not achieved |
| Goal may be marked complete | Completion audit | Required real private score proof is absent | Not achieved |

## Fresh command evidence

```text
ATTEMPT_BUDGET
records_path=experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
max_attempts=5
attempts_used=0
attempts_remaining=5
best_score=none
top3_hit=no
next_action=RUN_FIRST_UPLOAD_RUNBOOK
next_command=python3 experiments/scripts/v1866_final_attempt_runbook.py
stage_command=python3 experiments/scripts/v1870_stage_current_upload.py
```

```text
PRE_UPLOAD_GUARD
UPLOAD_READY=yes
UPLOAD_PATH=experiments/final_submission_package/current_upload/submission.csv
CANDIDATE=v1856g
GROUP=scoreonly_safe_queue
ORDER=1
SHA256=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
ROWS=397
```

```text
OK: 397 predictions validated
```

```text
WROTE_CSV=experiments/reports/v1884_candidate_pool_coverage_scan.csv
WROTE_REPORT=experiments/reports/v1884_candidate_pool_coverage_scan.md
PRIVATE_FILES=1331
SCORED_PAIRS=1309
REVIEW_CANDIDATES=0
SAFE_OR_DUPLICATE_ABOVE_FIRST=0
```

```text
WROTE_CSV=experiments/reports/v1875_route_matrix_regression.csv
WROTE_REPORT=experiments/reports/v1875_route_matrix_regression.md
SCENARIOS=45
FAILURES=0
```

```text
WROTE_CSV=experiments/reports/v1882_command_center_dry_run_regression.csv
WROTE_REPORT=experiments/reports/v1882_command_center_dry_run_regression.md
SCENARIOS=7
FAILURES=0
MUTATION_OK=yes
```

```text
NO_SCORE_RECORD_FILE
```

## Completion verdict

Not complete.

The package and route controls are ready for the next real submission attempt, but the active goal requires a real private score strictly greater than `0.50671`. No such score record or user-reported Kaggle result is available in the current project state.

## Next concrete action

Upload exactly:

```text
experiments/final_submission_package/current_upload/submission.csv
```

After the private score appears, preview and then record the real result:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE> --confirm-real-score
```

Stop only if the real score is greater than `0.50671`; otherwise follow the command-center recommendation within the remaining attempt budget.
