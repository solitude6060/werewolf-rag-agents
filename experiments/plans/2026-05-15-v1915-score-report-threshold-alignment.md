# v1915 Score Report Threshold Alignment Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Remove stale active score-report guidance that still references the old `>0.50671` completion threshold, so the user score-report path cannot accidentally treat a rank-4-beating score as a top-3 completion.

## Current context

- Live top-3 cutoff from the latest leaderboard: real private score `>0.52380`.
- Current upload: `experiments/final_submission_package/current_upload/submission.csv` (`v1826a`, `queue#1`).
- Current active score-report scripts use `0.52380`, but generated report artifacts `v1893` and `v1898` still contain stale `0.50671` wording.

## Constraints

- Do not record or confirm any synthetic score.
- Do not mutate `v1836_score_feedback_records.csv`.
- Do not stage a new upload; current upload must remain `v1826a`.
- Keep historical decision reports untouched unless they are active score-report handoff artifacts.

## Method

1. Regenerate the v1893 score-report template from the current script/current upload.
2. Regenerate the v1898 current-score bridge report in dry-run mode using a representative non-completion score, so its default report reflects the current bridge behavior and threshold.
3. Verify no `0.50671` remains in current score-report handoff artifacts.
4. Verify official score records count and current upload SHA remain unchanged.

## Verification standard

- `python3 experiments/scripts/v1893_score_report_template.py` reports `CANDIDATE=v1826a` and writes threshold `>0.52380`.
- `python3 experiments/scripts/v1898_current_score_report_bridge.py --score 0.50000` reports `WRITE_MODE=dry_run` and does not mutate official records.
- `grep` finds no `0.50671` in current score-report handoff artifacts.
- `validate_submission.py` still passes for current upload.

## Outputs

- `experiments/reports/v1893_score_report_template.json`
- `experiments/reports/v1893_score_report_template.md`
- `experiments/reports/v1898_current_score_report_bridge.json`
- `experiments/reports/v1898_current_score_report_bridge.md`

## Stop condition

Stop when active score-report artifacts are aligned to `>0.52380`, official records remain unchanged, and the current upload path remains ready.
