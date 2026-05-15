# Final Submission Strategy and Outcome

Date: 2026-05-15

## Outcome

The original five-attempt sprint found a best verified private score of:

```text
v1840c = 0.49349
```

The failed role-cap attempt was:

```text
v1846e = 0.46698
```

The public `main` branch now prepares the reopened extra-submit sprint.  The
current upload candidate is `v1842e`; the best verified rollback remains
`v1840c`.

## Current packaged file

```text
hw2_D13922024/submission.csv
```

Equivalent current-upload paths:

```text
hw2_D13922024/checkpoints/final_current_private.csv
hw2_D13922024/checkpoints/final_v1842e_private.csv
experiments/final_submission_package/current_upload/submission.csv
```

Current candidate SHA-256:

```text
6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f
```

Best verified rollback SHA-256 (`v1840c`):

```text
fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145
```

Extra fixed upload batch:

```text
experiments/final_submission_package/upload_batch_2026-05-15_extra3/
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
