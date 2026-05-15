# 2026-05-15 Post-v1846g Fallback Routing Plan

## Goal

Keep the active five-attempt score objective moving after the real `v1856g` private score (`0.42894`) showed a severe regression. The immediate upload is already staged to `v1846g`; this plan prevents the next score report from ending in a non-concrete router state if `v1846g` also misses the `0.52380` threshold.

## Constraints

- Do not mark the active goal complete unless a real private score is strictly greater than `0.52380`.
- Do not spend or simulate external leaderboard attempts locally.
- Keep `experiments/final_submission_package/current_upload/submission.csv` as the fixed manual upload path.
- Preserve validation gates: router recommendations must be manifest-backed CSVs unless the score is a top-3 stop.
- Keep edits surgical; no unrelated candidate generation.

## Current evidence

- Recorded real score: `scoreonly_safe_queue#1 v1856g = 0.42894`.
- Current staged upload: `scoreonly_safe_queue#5 v1846g`, SHA-256 `f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb`.
- Existing router currently returns `NO_SCOREONLY_SAFE_QUEUE_REMAINING` after score-only order 5, which is safe but not operationally helpful under a submission deadline.
- `v1831_candidate_risk_scores.md` ranks `v1826a` as the strongest evidence/risk structural first shot.
- `v1858_private_feedback_transfer_audit.md` warns that high public-proxy prior-calibration candidates may transfer poorly; the new `0.42894` score reinforces that warning.

## Decision

If `scoreonly_safe_queue#5 v1846g` does not exceed the top-3 threshold, route next to the evidence-driven structural queue first slot:

```text
experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv
```

Rationale:

- It exits the score-only prior-calibration family after two score-only feedback signals.
- It uses the pre-existing structural queue with documented follow-up rules.
- It keeps remaining attempts concrete and validated without inventing new candidates.

## Implementation steps

1. Change `v1836_score_feedback_router.py` score-only order-5 branch from non-concrete manual state to `queue#1` unless the score is already a top-3 stop.
2. Add regression coverage in `v1882_command_center_dry_run_regression.py` for score-only order 5 routing to `queue#1`.
3. Run route-matrix regression, command-center regression, pre-upload guard, final preflight, and final status.
4. Record a concise audit artifact with prompt-to-artifact evidence.

## Stop condition

- `v1908_final_goal_status.py` remains `ACTION=UPLOAD_CURRENT` until a real score above `0.52380` is recorded.
- The router must provide a concrete manifest-backed next CSV for post-v1846g non-top-3 scores.
