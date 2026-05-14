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

Before manually uploading, run the final one-command preflight:

```bash
python3 experiments/scripts/v1888_final_upload_preflight.py
```

Expected result: `READY_TO_MANUAL_UPLOAD=yes`.

Fill this ready-to-edit score report after the real private score appears:

```text
experiments/final_submission_package/current_upload/SCORE_REPORT.txt
```

Before the score appears, prepare the copy/paste score report template:

```bash
python3 experiments/scripts/v1893_score_report_template.py
```

After the real private score appears, save the filled `SCORE_REPORT` block to a file and dry-run the safe bridge first:

```bash
python3 experiments/scripts/v1895_score_report_command_center.py <SCORE_REPORT_FILE>
```

Then record only after confirming the score is real:

```bash
python3 experiments/scripts/v1895_score_report_command_center.py <SCORE_REPORT_FILE> --confirm-real-score
```

Fallback direct dry-run if no report file is available:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Fallback direct record command if the validated score must be typed manually:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --confirm-real-score
```

Stop if the real score is greater than `0.50671`.
