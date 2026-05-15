# v1934 Post-v1840b Score Route Audit

Generated after the user reported:

```text
submission1840b.csv
Complete
0.49266
```

## Completion Decision

**Not complete.**

The latest real score `0.49266` is an improvement over the prior best
`0.48854`, but it remains below the live top-3 cutoff:

```text
0.52380 - 0.49266 = 0.03114
```

The active goal can only complete after a real private score strictly greater
than `0.52380`.

## Ledger Update

The score was processed through the no-edit current score bridge:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score 0.49266
python3 experiments/scripts/v1898_current_score_report_bridge.py --score 0.49266 --confirm-real-score
```

The ledger now records:

```text
overlay,8,v1840b,score=0.49266,top3_hit=no,
recommended_next=experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv
```

## Next Upload Staged

Use:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Current staged candidate:

```text
candidate=v1840c
group=overlay
order=9
rows=397
sha256=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145
```

Safe aliases:

```text
hw2_D13922024/submission.csv
hw2_D13922024/checkpoints/final_current_private.csv
hw2_D13922024/checkpoints/final_v1840c_private.csv
```

## Verification Evidence

```text
python3 experiments/scripts/v1921_upload_now_console.py
READY_TO_UPLOAD=yes
CANDIDATE=v1840c
GROUP=overlay
ORDER=9
BEST_SCORE=0.49266

python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv
OK: 397 predictions validated

python3 experiments/scripts/v1883_pre_upload_guard.py
UPLOAD_READY=yes
CANDIDATE=v1840c

python3 experiments/scripts/v1902_upload_alias_guard.py
ALIAS_GUARD_READY=yes
CANONICAL_SHA256=fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145

python3 experiments/scripts/v1906_goal_completion_gate.py --out-json /tmp/hw2_post049266_gate.json --out-md /tmp/hw2_post049266_gate.md
GOAL_COMPLETE=no
RECORDS_COUNT=3
BEST_SCORE=0.49266
TOP3_THRESHOLD=0.52380
```

## Next Score Intake

After uploading `v1840c` and receiving the real score:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score
python3 experiments/scripts/v1908_final_goal_status.py
```
