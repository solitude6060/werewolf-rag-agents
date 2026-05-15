# Final Best Submission Archive

All final leaderboard attempts are exhausted.  The archived best verified CSV is:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Source: `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv`
Candidate: `v1840c` (`overlay` order `9`)
Rows: `397`
SHA-256: `fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145`
Validator: `OK: 397 predictions validated`

Before packaging or hand-in, run the final one-command preflight:

```bash
python3 experiments/scripts/v1888_final_upload_preflight.py
```

Expected result: `READY_TO_MANUAL_UPLOAD=yes` for file consistency; no upload attempts remain.

Single status command for the current goal:

```bash
python3 experiments/scripts/v1908_final_goal_status.py
```

Historical score-report template path:

```text
experiments/final_submission_package/current_upload/SCORE_REPORT.txt
```

Historical no-edit score bridge:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>
```

Historical record command:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score
```

Completion gate for the archived score state:

```bash
python3 experiments/scripts/v1906_goal_completion_gate.py
```

Score report template command, retained for traceability:

```bash
python3 experiments/scripts/v1893_score_report_template.py
```

Score report bridge command, retained for traceability:

```bash
python3 experiments/scripts/v1895_score_report_command_center.py <SCORE_REPORT_FILE>
```

Score report confirm command, retained for traceability:

```bash
python3 experiments/scripts/v1895_score_report_command_center.py <SCORE_REPORT_FILE> --confirm-real-score
```

Fallback direct dry-run command, retained for traceability:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Fallback direct record command, retained for traceability:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group overlay --order 9 --score <REAL_SCORE> --confirm-real-score
```

Final recorded best: `v1840c = 0.49349`.  Last attempt `v1846e = 0.46698`.  Attempts remaining: `0`.
