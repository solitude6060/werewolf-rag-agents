# Final Submission Release Checklist

Date: 2026-05-15  
Branch: `dev/final-submission-report-pack`

## Final status

All five final leaderboard attempts have been used.

- Best verified candidate: `v1840c`
- Best verified private score: `0.49349`
- Failed last attempt: `v1846e = 0.46698`
- Operational target `>0.50000`: not reached
- Original top-three gate `>0.52380`: not reached

## Final packaged submission

Use this file for the final coursework package:

```text
hw2_D13922024/submission.csv
```

It is byte-equal to:

```text
hw2_D13922024/checkpoints/final_current_private.csv
hw2_D13922024/checkpoints/final_v1840c_private.csv
experiments/final_submission_package/current_upload/submission.csv
```

Candidate:

```text
overlay order 9, v1840c
```

Validation:

```text
Rows: 397
SHA-256: fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145
Validator: OK: 397 predictions validated
```

## One-command entry point

From the package directory:

```bash
cd hw2_D13922024
python3 make_final.py --output submission.csv
```

Expected output includes:

```text
OK: 397 predictions validated
```

## Verification before hand-in

From the workspace root:

```bash
python3 hw2_D13922024/assert/validate_submission.py hw2_D13922024/submission.csv
python3 hw2_D13922024/make_final.py --output /tmp/hw2_final_verify.csv
python3 experiments/scripts/v1906_goal_completion_gate.py --out-json /tmp/hw2_final_gate.json --out-md /tmp/hw2_final_gate.md
```

Expected score gate result:

```text
GOAL_COMPLETE=no
BEST_SCORE=0.49349
TOP3_THRESHOLD=0.52380
```

## Required files

```text
hw2_D13922024/submission.csv
hw2_D13922024/hw2_report.md
hw2_D13922024/hw2_report.zh-TW.md
hw2_D13922024/README.md
hw2_D13922024/make_final.py
hw2_D13922024/assert/validate_submission.py
hw2_D13922024/checkpoints/final_current_private.csv
hw2_D13922024/checkpoints/final_v1840c_private.csv
```

## Hygiene checks

- No further leaderboard upload is available.
- Do not package local `.omx`, cache, or credential files.
- Do not use the failed last-attempt `v1846e` as the package default.
- Preserve the score-feedback ledger for auditability:

```text
experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
```
