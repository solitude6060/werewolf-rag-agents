# v1863 Score-Only Blend Ladder Plan

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Goal

Search for score-only candidates that preserve v1824a role labels while applying only a fraction of the v1856g/v1853g score calibration.  The objective is to keep most public AP lift while reducing score-distance risk versus the current verified-best private submission.

## Rationale

v1862 selected v1856g because it has the same local public proxy as v1856a but zero private role changes versus v1824a.  However v1856g still changes many `wolf_score` values.  A partial blend may provide a safer first upload if it keeps a high public proxy with lower score MAE.

## Inputs

- Baseline roles/scores: v1824a public/private.
- Safer high-proxy score-only targets: v1856g, v1853g, v1850g, v1848g, v1846g public/private.
- Local public scorer: `experiments/scripts/local_score.py`.
- Submission validator: `werewolf-project/assert/validate_submission.py`.

## Method

For each target candidate and alpha value:

```text
new_score = (1 - alpha) * v1824a_score + alpha * target_score
role = v1824a_role
```

Evaluate public score, score MAE versus v1824a, changed-score rate, and validator status.  Promote a compact five-file queue ordered by risk-adjusted evidence.

## Validation

- `python3 -m py_compile experiments/scripts/v1863_scoreonly_blend_ladder.py`
- `python3 experiments/scripts/v1863_scoreonly_blend_ladder.py`
- Validate generated private CSVs.
- If promoted, add package/router support and run full package validation.
- Rerun document scans.

## Completion boundary

This can improve the next upload path but cannot complete the active goal without a real Kaggle private score greater than `0.50671`.
