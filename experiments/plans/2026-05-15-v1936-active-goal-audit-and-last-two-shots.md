# v1936 Active Goal Audit and Last-Two-Shots Plan

> Superseded note, 2026-05-15: `v1840c` later returned a real private score of
> `0.49349`.  The current last-shot package is now governed by
> `experiments/plans/2026-05-15-v1937-last-chance-0p5-rolecap-override.md`.
> Do not use this v1936 plan as the current upload instruction.

## Goal

Beat the live top-three private leaderboard cutoff for the HW2 Werewolf submission sprint.

Concrete success criterion:

- A real private leaderboard score strictly greater than `0.52380`.

## Current state

- Recorded best score: `0.49266` from `v1840b`.
- Current staged upload: `v1840c`.
- Current upload path: `experiments/final_submission_package/current_upload/submission.csv`.
- Current upload SHA-256: `fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145`.
- Attempt budget records: `3` used out of `5`, `2` remaining.
- Goal gate: `GOAL_COMPLETE=no`.

## Constraints

- Do not mark the goal complete without a real score above `0.52380`.
- Do not change the staged upload away from `v1840c` before its real private score is known.
- Do not upload legacy `673`-row paths.
- Preserve exact CSV bytes for current upload aliases.

## Plan

1. Keep `v1840c` staged as the next manual upload.
2. Verify current upload path and aliases remain byte-identical.
3. Verify the post-score route for a non-top-three `v1840c` result is concrete.
4. Verify the final fallback CSV (`v1842e`) is present, manifest-valid, and submission-format valid.
5. Record a prompt-to-artifact completion audit showing the goal is not yet achieved and listing the exact next action.

## Verification standard

- `v1921_upload_now_console.py` reports `READY_TO_UPLOAD=yes`.
- `v1906_goal_completion_gate.py` reports `GOAL_COMPLETE=no` until the real score exceeds `0.52380`.
- `v1872_post_score_command_center.py --score <miss-score>` dry-run routes `v1840c` to `v1842e`.
- `validate_submission.py` accepts both current upload and fallback candidate.

## Stop condition

Stop local work only when one of these is true:

- A real private score greater than `0.52380` is recorded and the completion gate reports `GOAL_COMPLETE=yes`.
- The user returns with the next private score, and the router stages the next candidate or stops.
- All local pre-upload and post-score fallback evidence is current, and no external score is available yet.

## Rollback

If a route or staged file is wrong, restage from the manifest with:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py --from-records
```

Then rerun preflight and the goal gate.
