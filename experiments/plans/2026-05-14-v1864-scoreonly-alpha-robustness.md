# v1864 Score-Only Alpha Robustness Plan

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Goal

Audit the v1863 score-only alpha ladder with leave-one-game-out public robustness.  The goal is to check whether a lower-alpha score-only candidate should replace the current v1862 first upload before the next real Kaggle attempt.

## Why this is different from v1863

v1863 ranked candidates by full public proxy and score-distance.  v1864 tests whether those candidates remain robust when each public game is left out.  This is a guard against selecting a high public AP candidate that depends too much on a small set of public games.

## Inputs

- `experiments/reports/v1863_scoreonly_blend_ladder.csv`
- Generated v1863 public/private blend CSVs.
- Baseline v1824a public/private CSVs.
- `werewolf-project/data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv`

## Method

For each v1863 candidate:

1. Compute global public final score.
2. Compute leave-one-game-out final score for each public game.
3. Compare deltas against v1824a under the same left-out split.
4. Rank by minimum LOO delta first, then mean LOO delta, then global score, while tracking score distance.

## Validation

- `python3 -m py_compile experiments/scripts/v1864_scoreonly_alpha_robustness.py`
- `python3 experiments/scripts/v1864_scoreonly_alpha_robustness.py`
- If it recommends changing the first upload, update package/router and rerun full validation.
- Otherwise record no package change.

## Completion boundary

Even a robust public LOO result is not completion proof. The active goal remains incomplete until a real private score greater than `0.50671` is reported.
