# v1894 Score Report Intake Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Validate a copied `SCORE_REPORT` block before any score routing or completion decision, so a real private score report is tied to the staged upload file and cannot be confused with a proxy, wrong file, or percentage-like value.

## Risk

The v1893 template makes reporting explicit, but a pasted block could still be edited incorrectly. A separate intake validator can reject wrong path, wrong candidate context, mismatched SHA/row count, missing `score_is_real_kaggle_private=yes`, or malformed score before the command center is used.

## Scope

- Add `experiments/scripts/v1894_score_report_intake.py`.
- Parse a key-value `SCORE_REPORT` block from a file.
- Validate upload path, candidate, group, order, rows, SHA, real-private flag, and decimal score.
- Print v1872 dry-run and confirm commands, but do not write score records.
- Add a regression covering valid top-3, valid continue, wrong SHA, missing real-private flag, and percentage-like score.

## Non-goals

- Do not upload to Kaggle.
- Do not write official score records.
- Do not replace `v1872_post_score_command_center.py` for actual routing/recording.
- Do not mark the active goal complete without a recorded real score greater than `0.50671`.

## Validation standard

- `python3 -m py_compile experiments/scripts/v1894_score_report_intake.py experiments/scripts/v1894_score_report_intake_regression.py`
- `python3 experiments/scripts/v1894_score_report_intake_regression.py`
- `python3 experiments/scripts/v1893_score_report_template.py`
- Official score-record file remains absent.

## Stop condition

The intake script rejects ambiguous score reports, accepts valid reports, and leaves the active goal open until a real score greater than `0.50671` is confirmed and recorded through v1872.
