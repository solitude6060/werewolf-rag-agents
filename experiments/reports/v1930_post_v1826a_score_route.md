# v1930 Post-v1826a Score Route Audit

Generated UTC: `2026-05-15T02:02:00+00:00`

## Result received

User-reported result for the just-uploaded `submission.csv`:

```text
private_score=0.48854
leaderboard_rank=5
```

Latest known leaderboard snapshot:

| Rank | ID | Private score |
| ---: | --- | ---: |
| 1 | D13922023 | 0.54251 |
| 2 | R14922184 | 0.53461 |
| 3 | R14922115 | 0.52380 |
| 4 | R14942077 | 0.50671 |
| 5 | D13922024 | 0.48854 |

## Completion decision

**NOT COMPLETE.**

The active goal requires a real private score strictly greater than `0.52380`. The new score `0.48854` is a positive lift but remains below the top-3 cutoff by:

```text
0.52380 - 0.48854 = 0.03526
```

Records-backed gate after recording:

```text
GOAL_COMPLETE=no
RECORDS_COUNT=2
BEST_SCORE=0.48854
TOP3_THRESHOLD=0.52380
```

## Score ledger update

The score was processed through the no-edit current score bridge:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score 0.48854
python3 experiments/scripts/v1898_current_score_report_bridge.py --score 0.48854 --confirm-real-score
```

Ledger now includes:

```text
queue,1,v1826a,score=0.48854,top3_hit=no,recommended_next=experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv
```

## Next upload staged

Router staged the positive-followup candidate:

```text
experiments/final_submission_package/current_upload/submission.csv
```

```text
candidate=v1826b
group=queue
order=2
rows=397
sha256=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b
stop_if_score_greater_than=0.52380
```

Safe aliases:

```text
hw2_D13922024/submission.csv
hw2_D13922024/checkpoints/final_current_private.csv
hw2_D13922024/checkpoints/final_v1826b_private.csv
```

## Verification evidence

```text
python3 experiments/scripts/v1921_upload_now_console.py
READY_TO_UPLOAD=yes
CANDIDATE=v1826b
GROUP=queue
ORDER=2
BEST_SCORE=0.48854

python3 experiments/scripts/v1906_goal_completion_gate.py --out-json /tmp/hw2_after048854_gate.json --out-md /tmp/hw2_after048854_gate.md
GOAL_COMPLETE=no
RECORDS_COUNT=2
BEST_SCORE=0.48854
TOP3_THRESHOLD=0.52380

python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv
OK: 397 predictions validated

python3 experiments/scripts/v1902_upload_alias_guard.py
ALIAS_GUARD_READY=yes
CANONICAL_SHA256=8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b

python3 experiments/scripts/v1924_package_current_submit_regression.py
FAILURES=0

python3 experiments/scripts/v1929_cockpit_noedit_bridge_regression.py
FAILURES=0

python3 experiments/scripts/v1928_current_bridge_confirm_sandbox_regression.py
FAILURES=0
REAL_REPO_UNCHANGED=yes
```

## Next score intake commands

After uploading the staged `v1826b` and receiving the real private score:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score
python3 experiments/scripts/v1908_final_goal_status.py
```

## Stop condition

Only stop and perform the final completion audit if the next real score is greater than `0.52380`.
