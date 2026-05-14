# v1872 Post-Score Command Center

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Purpose

Provide one safe command for the moment after a real Kaggle private score appears:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Default behavior is dry-run only and reads the uploaded group/order from:

```text
experiments/final_submission_package/current_upload/metadata.json
```

It writes score-feedback records only with:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE> --confirm-real-score
```

## Current dry-run evidence

Positive-but-not-top-3 preview:

```text
UPLOAD_CONTEXT
group=scoreonly_safe_queue
order=1
source=experiments/final_submission_package/current_upload/metadata.json
score=0.48000
top3_hit=no
recommended_next=experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv
WRITE_STATUS=dry_run_only
```

Top-3 preview:

```text
score=0.50672
top3_hit=yes
recommended_next=STOP: score exceeds top-3 threshold.
WRITE_STATUS=dry_run_only
```

v1874 positive-signal threshold preview through the command center:

```text
score=0.47120
recommended_next=experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv

score=0.47119
recommended_next=experiments/final_submission_package/scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv
```

After both dry-runs, no real score record was created:

```text
NO_SCORE_FEEDBACK_RECORDS
```

## Validation commands

```bash
python3 -m py_compile experiments/scripts/v1872_post_score_command_center.py
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.48000
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.50672
python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv
```

## Completion boundary

This command center remains an operational helper.  The active score objective still requires a real Kaggle private score greater than `0.50671`; dry-runs do not count.
