# v1893 Score Report Template Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Make the user's post-upload score report unambiguous enough to decide whether the active goal can be completed or whether the next attempt should be routed.

## Risk

The active goal can only be closed from a real private leaderboard score greater than `0.50671`. A vague message, percentage-like score, wrong file, or missing candidate context could lead to an unsafe completion claim or an incorrect next upload route.

## Scope

- Add `experiments/scripts/v1893_score_report_template.py`.
- Read current upload metadata and produce a copy/paste score-report template.
- Optionally validate a provided score as decimal `[0, 1]` and classify whether it is a top-3 completion candidate.
- Write Markdown and JSON evidence under `experiments/reports/`.

## Non-goals

- Do not upload to Kaggle.
- Do not write score records.
- Do not replace `v1872_post_score_command_center.py` for actual routing/recording.
- Do not mark the active goal complete without a real score report and score record.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1893_score_report_template.py`
- `python3 experiments/scripts/v1893_score_report_template.py`
- `python3 experiments/scripts/v1893_score_report_template.py --score 0.50672`
- `python3 experiments/scripts/v1893_score_report_template.py --score 47.119` must reject the percentage-like score.
- Current upload SHA/candidate in the template must match metadata.

## Stop condition

The template prints the exact upload context, score-report fields, and post-score commands while leaving official score records absent and the active goal open.
