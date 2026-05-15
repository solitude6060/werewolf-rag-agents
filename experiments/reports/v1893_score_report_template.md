# v1893 Score Report Template

Generated UTC: `2026-05-15T00:48:10+00:00`

## Upload context to report back

```text
SCORE_REPORT
uploaded_path=experiments/final_submission_package/current_upload/submission.csv
candidate=v1826a
group=queue
order=1
sha256=e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad
rows=397
real_private_score=<REAL_PRIVATE_SCORE_DECIMAL>
score_is_real_kaggle_private=yes
```

## Current validation

- SHA matches metadata: `True`
- Official score records already exist: `True`
- Stop threshold: `>0.52380`
- Provided score status: `not_provided`

## Commands after score appears

Safest path from a saved report file:

```bash
python3 experiments/scripts/v1895_score_report_command_center.py <SCORE_REPORT_FILE>
```

Then record only after confirming the score is real:

```bash
python3 experiments/scripts/v1895_score_report_command_center.py <SCORE_REPORT_FILE> --confirm-real-score
```

Fallback direct command if no report file is available:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Validate the pasted block first if you saved it to a file:

```bash
python3 experiments/scripts/v1894_score_report_intake.py <SCORE_REPORT_FILE>
```

Direct record command if the validated score must be typed manually:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE> --confirm-real-score
```

## Completion boundary

This template only structures the score report. The active goal is complete only after a real private score greater than `0.52380` is recorded.
