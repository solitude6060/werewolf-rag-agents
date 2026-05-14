# v1886 Manual Upload Handoff

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Purpose

Reduce the risk of spending a final attempt on the wrong CSV. This handoff is intentionally local-only and does not submit to Kaggle.

## Why manual upload remains the next action

- Local `kaggle` CLI was checked with `command -v kaggle`; no executable was found in `PATH`.
- No reliable competition slug or CLI submit command was found in the local assignment/package docs.
- Spending a Kaggle attempt is an external leaderboard action, so this repository prepares the exact file and post-score commands but does not auto-submit.

## Upload exactly this file

```text
experiments/final_submission_package/current_upload/submission.csv
```

Current staged metadata:

| Field | Value |
| --- | --- |
| Group | `scoreonly_safe_queue` |
| Order | `1` |
| Candidate | `v1856g` |
| Rows | `397` |
| SHA-256 | `468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d` |
| Stop threshold | `>0.50671` |

## Pre-upload command sequence

Run these from the workspace root immediately before selecting the file in the browser:

```bash
python3 experiments/scripts/v1883_pre_upload_guard.py
python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv
python3 experiments/scripts/v1884_candidate_pool_coverage_scan.py
```

Expected minimum outputs:

```text
UPLOAD_READY=yes
OK: 397 predictions validated
REVIEW_CANDIDATES=0
```

## Browser upload checklist

1. Open the course Kaggle submission page.
2. Select `experiments/final_submission_package/current_upload/submission.csv`.
3. Confirm the filename/path before submitting.
4. Submit once.
5. Wait for the private score to appear.
6. If the score is greater than `0.50671`, stop all further attempts.
7. If the score is not greater than `0.50671`, route the next attempt with the command-center commands below.

## After-score commands

Dry-run first:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Record only after confirming the score is the real Kaggle private score:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE> --confirm-real-score
```

## Completion boundary

This handoff reduces upload risk, but it does not complete the active objective. Completion still requires a real private score strictly greater than `0.50671`.
