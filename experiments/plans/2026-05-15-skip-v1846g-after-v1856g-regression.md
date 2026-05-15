# 2026-05-15 Skip-v1846g Decision Plan

## Goal

Maximize the remaining chance of recording a real Kaggle private score above `0.52380` after `scoreonly_safe_queue#1 v1856g` returned `0.42894`.

## Current state

- Real score recorded: `v1856g = 0.42894`.
- Current staged follow-up before this plan: `scoreonly_safe_queue#5 v1846g`.
- Attempts remaining from records: `4`.
- Active goal remains incomplete: best recorded score is below `0.52380`.

## Decision

Skip the conservative `v1846g` follow-up and stage structural `queue#1 v1826a` next.

## Rationale

- `v1856g` is a score-only prior-calibration candidate and severely regressed below both the rollback `0.47119` and the known v1400 warning score range.
- `v1846g` is also score-only and lower-upside: it preserves role labels and has the lowest risk-adjusted index among the score-only safe queue in `v1873_final_five_diversity_audit.md`.
- The active objective is not to preserve the current best; it is to exceed `0.52380`. With four attempts left, the next attempt should probe a differentiated structural lane.
- `v1831_candidate_risk_scores.md` ranks `v1826a` as the strongest evidence/risk structural first shot.

## Implementation steps

1. Add an explicit manual-override reason to current upload staging metadata.
2. Update the attempt-state guard so a documented manual override can pass when the override target is manifest-backed, validated, and not already uploaded.
3. Stage `queue#1 v1826a` as `experiments/final_submission_package/current_upload/submission.csv`.
4. Run validator, alias guard, pre-upload guard, final preflight, final status, and route regressions.

## Stop condition

- Current upload is `queue#1 v1826a` and `READY_TO_MANUAL_UPLOAD=yes`.
- Goal remains active unless a real private score above `0.52380` is recorded.
