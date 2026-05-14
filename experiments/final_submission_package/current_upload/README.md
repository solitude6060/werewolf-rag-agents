# Current Upload Staging

Upload this CSV to Kaggle:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Source: `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv`
Candidate: `v1856g` (`scoreonly_safe_queue` order `1`)
Rows: `397`
SHA-256: `468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d`
Validator: `OK: 397 predictions validated`

After the real private score appears, dry-run the route first:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Record the score only after confirming it is real:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --confirm-real-score
```

Stop if the real score is greater than `0.50671`.
