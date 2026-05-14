# v1895 Score Report Command-Center Bridge Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Connect a saved `SCORE_REPORT` file to the post-score command center through a safe dry-run wrapper, so the score is validated once and then routed without manually retyping it into the command line.

## Risk

The v1894 intake validates the report, but the user still has to copy the decimal score into `v1872_post_score_command_center.py`. That manual transfer can introduce a typo even after the report was validated.

## Scope

- Add `experiments/scripts/v1895_score_report_command_center.py`.
- Run v1894 intake against the report using temporary intake outputs.
- Run v1872 command-center dry-run by default using the validated score.
- Optionally allow explicit `--confirm-real-score` for the real score path, while preserving v1872's safeguards.
- Update the v1893 score-report template to prefer the new saved-report bridge before any manual score typing.
- Update current-upload staging metadata/readme so regenerated upload instructions point at the safe saved-report bridge.
- Add a regression that proves dry-run bridge scenarios do not touch official records and invalid reports are rejected.

## Non-goals

- Do not upload to Kaggle.
- Do not write records in the default dry-run path.
- Do not bypass v1894 validation or v1872 command-center routing.
- Do not mark the active goal complete without a real recorded score greater than `0.50671`.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1895_score_report_command_center.py experiments/scripts/v1895_score_report_command_center_regression.py`
- `python3 experiments/scripts/v1895_score_report_command_center_regression.py`
- `python3 experiments/scripts/v1893_score_report_template.py`
- Official score-record file remains absent after dry-run regressions.

## Stop condition

A valid report can be routed through v1872 dry-run without record mutation, invalid reports fail before routing, and the active goal remains open pending a real private score.
