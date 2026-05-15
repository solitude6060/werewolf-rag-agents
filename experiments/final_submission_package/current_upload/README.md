# Current Upload Staging

Upload this CSV to Kaggle:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Source: `experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv`
Candidate: `v1826a` (`queue` order `1`)
Rows: `397`
SHA-256: `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad`
Validator: `OK: 397 predictions validated`

Before manually uploading, run the final one-command preflight:

```bash
python3 experiments/scripts/v1888_final_upload_preflight.py
```

Expected result: `READY_TO_MANUAL_UPLOAD=yes`.

Single status command for the current goal:

```bash
python3 experiments/scripts/v1908_final_goal_status.py
```

Fill this ready-to-edit score report after the real private score appears:

```text
experiments/final_submission_package/current_upload/SCORE_REPORT.txt
```

No-edit path after the score appears:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>
```

No-edit record command after confirming the score is real:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score
```

After recording, run the completion gate before declaring the score goal complete:

```bash
python3 experiments/scripts/v1906_goal_completion_gate.py
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
python3 experiments/scripts/v1872_post_score_command_center.py --group queue --order 1 --score <REAL_SCORE> --confirm-real-score
```

Stop if the real score is greater than `0.52380`.
