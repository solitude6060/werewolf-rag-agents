# v1893 Score Report Template

Generated UTC: `2026-05-14T18:30:38+00:00`

## Upload context to report back

```text
SCORE_REPORT
uploaded_path=experiments/final_submission_package/current_upload/submission.csv
candidate=v1856g
group=scoreonly_safe_queue
order=1
sha256=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
rows=397
real_private_score=<REAL_PRIVATE_SCORE_DECIMAL>
score_is_real_kaggle_private=yes
```

## Current validation

- SHA matches metadata: `True`
- Official score records already exist: `False`
- Stop threshold: `>0.50671`
- Provided score status: `not_provided`

## Commands after score appears

Dry-run first:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Then record only after confirming the score is real:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE> --confirm-real-score
```

## Completion boundary

This template only structures the score report. The active goal is complete only after a real private score greater than `0.50671` is recorded.
