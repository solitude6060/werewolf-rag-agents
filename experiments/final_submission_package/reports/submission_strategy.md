# Final Submission Strategy and Outcome

Date: 2026-05-15

## Outcome

The final leaderboard sprint is exhausted.  The best verified private score is:

```text
v1840c = 0.49349
```

The failed last attempt was:

```text
v1846e = 0.46698
```

The final coursework package therefore defaults to `v1840c`, not `v1846e`.

## Final packaged file

```text
hw2_D13922024/submission.csv
```

Equivalent archived paths:

```text
hw2_D13922024/checkpoints/final_current_private.csv
hw2_D13922024/checkpoints/final_v1840c_private.csv
experiments/final_submission_package/current_upload/submission.csv
```

SHA-256:

```text
fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145
```

## Final attempt ledger

| Attempt | Candidate | Private score | Decision |
| ---: | --- | ---: | --- |
| 1 | v1856g | 0.42894 | rejected; score-only balanced prior did not transfer |
| 2 | v1826a | 0.48854 | strong positive structural signal |
| 3 | v1840b | 0.49266 | positive overlay signal |
| 4 | v1840c | 0.49349 | best verified score; package default |
| 5 | v1846e | 0.46698 | failed role-cap final shot |

## Lessons

1. Transcript-grounded structural repairs transferred better than public-proxy calibration.
2. Public AP calibration improved local proxy but did not reliably transfer to private scoring.
3. The final hand-in should preserve the best verified private score instead of the latest failed experiment.

## Reproduction command

```bash
cd hw2_D13922024
python3 make_final.py --output submission.csv
```

Expected validator output:

```text
OK: 397 predictions validated
```

## Report files

```text
hw2_D13922024/hw2_report.md
hw2_D13922024/hw2_report.zh-TW.md
```
