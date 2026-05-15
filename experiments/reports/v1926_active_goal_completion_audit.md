# v1926 Active Goal Completion Audit

Generated UTC: `2026-05-15T01:47:00+00:00`
Branch: `dev/final-submission-report-pack`

## Objective restatement

Use the remaining final attempts to record an HW2 private leaderboard score that beats the currently known top-3 cutoff. Based on the latest working threshold preserved in the handoff artifacts, completion requires a real recorded private score strictly greater than `0.52380`.

This audit distinguishes local readiness from actual leaderboard success. Local validation, package reproduction, and routing guards are not sufficient to complete the active goal without the external score record.

## Current decision

**NOT COMPLETE.**

The records-backed gate reports:

```text
GOAL_COMPLETE=no
RECORDS_CONSISTENT=yes
RECORDS_COUNT=1
BEST_SCORE=0.42894
TOP3_THRESHOLD=0.52380
```

Because `0.42894 <= 0.52380`, the active goal must remain active and `update_goal(status="complete")` must not be called.

## Prompt-to-artifact checklist

| Requirement / explicit gate | Concrete evidence inspected | Coverage judgment | Status |
| --- | --- | --- | --- |
| Beat the top-3 cutoff | `v1906_goal_completion_gate.py --out-json /tmp/hw2_v1926_gate.json --out-md /tmp/hw2_v1926_gate.md` reports `BEST_SCORE=0.42894`, `TOP3_THRESHOLD=0.52380`, `GOAL_COMPLETE=no`. | Direct records-backed completion gate; decisive for completion. | missing |
| Use real score records only | `experiments/final_submission_package/manifests/v1836_score_feedback_records.csv` has one real recorded score: `v1856g=0.42894`, `top3_hit=no`. | Confirms no unrecorded local proxy is being treated as real success. | pass |
| Current upload is staged and ready | `v1921_upload_now_console.py` reports `READY_TO_UPLOAD=yes`, `CANDIDATE=v1826a`, `GROUP=queue`, `ORDER=1`, `ROWS=397`, SHA `e4b44b76...`. | Proves the next manual upload candidate is prepared; does not prove score success. | pass |
| Upload file validates | `python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv` reports `OK: 397 predictions validated`. | Covers submission format/row validity for the staged CSV. | pass |
| Safe manual-upload aliases match canonical | `v1921_upload_now_console.py` reports three safe aliases with `rows=397 sha_matches=yes`. | Reduces wrong-file upload risk. | pass |
| Stale lookalikes are identified | `v1921_upload_now_console.py` reports worktree/legacy `DO_NOT_UPLOAD` files with `rows=673 sha_matches=no`. | Prevents selecting stale `submission.csv` files. | pass |
| Active handoffs use live cutoff | `v1925_active_handoff_threshold_guard.py --out-csv /tmp/hw2_v1926_threshold_guard.csv --out-md /tmp/hw2_v1926_threshold_guard.md` reports `ACTIVE_HANDOFF_THRESHOLD_READY=yes`, `FILES_SCANNED=24`, `FAILURES=0`. | Covers active upload/package/post-score surfaces against stale `0.50671` stop condition. | pass |
| Package one-command reproduction matches current upload | `v1924_package_current_submit_regression.py` reports `FAILURES=0`; package `make_final.py` output SHA matches current upload SHA. | Confirms assignment package one-command output is aligned to current `v1826a`. | pass |
| Post-score command is ready | `v1921_upload_now_console.py` prints `POST_SCORE_DRY_RUN_COMMAND`, `POST_SCORE_CONFIRM_COMMAND`, and `FINAL_STATUS_COMMAND`. `v1923` sandbox regression already covers confirmed staging behavior. | Covers what to run after the external score appears. | pass |
| No completion shortcut from local readiness | This audit and `v1906` both state completion requires a real score `>0.52380`. | Prevents false completion from green local gates. | pass |

## Current upload to use next

```text
experiments/final_submission_package/current_upload/submission.csv
```

```text
candidate=v1826a
group=queue
order=1
rows=397
sha256=e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad
stop_if_score_greater_than=0.52380
```

Safe aliases:

```text
hw2_D13922024/submission.csv
hw2_D13922024/checkpoints/final_current_private.csv
hw2_D13922024/checkpoints/final_v1826a_private.csv
```

## Post-score commands

After the real private score appears, run:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score
python3 experiments/scripts/v1908_final_goal_status.py
```

If the resulting records-backed gate reports `GOAL_COMPLETE=yes`, then perform the final completion audit and only then mark the goal complete.

## Missing evidence / blocker

Missing external evidence: no real private score greater than `0.52380` is recorded for the active final attempts.

Current best recorded score:

```text
v1856g = 0.42894
```

## Stop condition

Stop condition is not met. Continue only after the manual upload result is available. The next local action after the user reports the score is score intake via the commands above.
