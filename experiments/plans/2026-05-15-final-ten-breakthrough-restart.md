# 2026-05-15 Final Ten-Submit Breakthrough Restart

## Goal

Restart the final Kaggle submission sprint after the original five-attempt window with ten additional submit opportunities.

- Current verified private best: `v1840c = 0.49349`.
- Current known top-3 threshold to beat: `>0.52380`.
- Existing score-feedback records: `5`.
- New total working budget: `15` records (`5` spent + `10` newly available).
- Stop condition for the active score objective remains unchanged: record a real private score `>0.52380`.

## Constraints

- Do not mark the active score goal complete unless a real private score greater than `0.52380` is recorded.
- Keep the closed hand-in package on `develop` reproducible; new score attempts live on `feature/final-ten-breakthrough`.
- Upload only locally validated CSVs with 397 prediction rows.
- Avoid duplicate uploads; `v1841e` is byte-identical to `v1840c` and should not spend an attempt.
- Avoid treating private leaderboard feedback as an unlimited oracle; each upload must have a concrete candidate rationale and post-score routing artifact.
- Do not use `git add .`; commit only explicit paths.

## Evidence Baseline

Known score records:

| Attempt | Candidate | Private score | Notes |
| --- | --- | ---: | --- |
| 1 | `v1856g` | `0.42894` | score-only balanced first; severe regression |
| 2 | `v1826a` | `0.48854` | structural baseline positive |
| 3 | `v1840b` | `0.49266` | overlay positive |
| 4 | `v1840c` | `0.49349` | best verified |
| 5 | `v1846e` | `0.46698` | rolecap/blackboost stack regressed |

Candidate pool facts used for the restart:

- `v1842e` differs from best `v1840c` by only 3 score rows and no role-row changes.
- `v1841e` has the same SHA-256 as `v1840c`; skip as duplicate.
- `v1846e` regressed, so the next attempt should isolate the black-boost delta without the rolecap stack.

## Plan

1. Update attempt-budget tools from a closed five-attempt sprint to a fifteen-record sprint:
   - `v1836_score_feedback_router.py`
   - `v1869_attempt_budget_guard.py`
   - `v1871_final_attempt_cockpit.py`
   - `v1904_attempt_state_guard.py`
   - `v1883_pre_upload_guard.py`
2. Add/adjust regression coverage so:
   - five existing score records still leave ten attempts remaining;
   - manual override is accepted when the latest router recommendation is non-concrete but current metadata documents the override;
   - exhausted state is only reached at fifteen records.
3. Stage first restart candidate:
   - candidate: `v1842e`
   - group/order: `black_boost_queue#5`
   - upload path: `experiments/final_submission_package/current_upload/submission.csv`
   - rationale: isolate black boost from the failed rolecap stack.
4. Run validation:
   - candidate validator
   - attempt state guard
   - pre-upload guard
   - final upload preflight
   - relevant regression scripts
5. Commit the restart tooling and staged candidate on `feature/final-ten-breakthrough`.

## Candidate Queue Draft

1. `v1842e` — isolate black-boost delta; only 3 score-only row changes vs `v1840c`.
2. If `v1842e` improves: search around the three changed rows and preserve no-rolecap constraint.
3. If neutral/regresses: try the smallest overlay deltas next (`v1839c`, `v1838c`, `v1829e`) before larger structural variants.
4. If multiple small deltas fail: re-evaluate `v1826b`/`v1826d` structural-positive lane.
5. Keep rolecap/prior/denoise/lowtail families as late contingencies because the latest score evidence transferred poorly.

## Rollback

To return to the closed hand-in candidate on this branch:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py \
  --group overlay \
  --order 9 \
  --override-reason "rollback to best verified v1840c=0.49349"
```

## Completion Boundary

This plan is complete when a staged candidate is locally ready to upload, the toolchain supports the new ten-submit budget, and the user receives the exact upload path plus score-recording command. The score objective itself remains open until a real private score `>0.52380` is recorded.

## Implementation Log

- Updated final-attempt budget policy from `5` to `15` records in the score router, budget guard, score-report intake, attempt-state guard, cockpit, and completion gate.
- Added regression coverage for documented manual override after a non-concrete latest router recommendation.
- Staged `v1842e` (`black_boost_queue#5`) as the first restart upload.
- Updated the assignment-facing README to distinguish the closed `develop` hand-in baseline (`v1840c`) from this branch's active breakthrough upload (`v1842e`).

## Verification Log

Commands executed on `feature/final-ten-breakthrough`:

```bash
python3 experiments/scripts/v1904_attempt_state_guard_regression.py
python3 experiments/scripts/v1894_score_report_intake_regression.py
python3 experiments/scripts/v1870_stage_current_upload.py --group black_boost_queue --order 5 --override-reason 'extra ten-submit restart after prior 5/5 records; isolate v1842e black-boost delta from failed rolecap v1846e; v1842e differs from best v1840c by 3 score-only rows and is not a duplicate'
python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv
python3 experiments/scripts/v1869_attempt_budget_guard.py
python3 experiments/scripts/v1904_attempt_state_guard.py
python3 experiments/scripts/v1883_pre_upload_guard.py
python3 experiments/scripts/v1888_final_upload_preflight.py
python3 experiments/scripts/v1871_final_attempt_cockpit.py
python3 experiments/scripts/v1908_final_goal_status.py
python3 experiments/scripts/v1898_current_score_report_bridge.py --score 0.50000
```

Observed results:

- `v1904` regression: `SCENARIOS=7`, `FAILURES=0`.
- `v1894` regression: `SCENARIOS=6`, `FAILURES=0`.
- Validator: `OK: 397 predictions validated`.
- Budget guard: `max_attempts=15`, `attempts_used=5`, `attempts_remaining=10`.
- Attempt state guard: `ATTEMPT_STATE_READY=yes`.
- Pre-upload guard: `UPLOAD_READY=yes`.
- Final upload preflight: `READY_TO_MANUAL_UPLOAD=yes`.
- Goal status: `ACTION=UPLOAD_CURRENT`, `GOAL_COMPLETE=no`, `READY_TO_MANUAL_UPLOAD=yes`.
- Dry-run score bridge: `BRIDGE_EXIT_CODE=0`, `OFFICIAL_RECORDS_MUTATED=no`.

Current upload file:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Current upload SHA-256:

```text
6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f
```
