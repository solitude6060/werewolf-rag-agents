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

After the real private score appears, run:

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --dry-run
```

Stop if the real score is greater than `0.50671`.
