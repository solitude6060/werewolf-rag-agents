# HW2 — Multi-Agent Werewolf Prediction

Student ID: `D13922024`

## Current packaged submission

The package default submission is the current final-attempt candidate:

```text
submission.csv
```

It is byte-equal to:

```text
checkpoints/final_current_private.csv
checkpoints/final_v1846e_private.csv
```

Candidate lineage: `rolecap_queue` order `5`, `v1846e`.

Staging note: this is the final one-shot override after `v1840c` scored `0.49349`.
The score-feedback router recommended `v1842e`; this package intentionally stages
`v1846e` instead because it keeps role labels fixed, applies the role-cap AP
calibration on top of `v1842e`, and has stronger public AP / leave-one-out
evidence for a last attempt aimed at crossing `0.50000`.

Known private leaderboard context before this final-attempt package:

| Rank in our known submissions | Candidate | Private score | Note |
| ---: | --- | ---: | --- |
| 1 | v1840c | 0.49349 | Latest positive final-attempt score |
| 2 | v1840b | 0.49266 | Previous positive overlay score |
| 3 | v1826a | 0.48854 | Previous positive structural score |
| 4 | v1824a | 0.47119 | Verified rollback |
| 5 | v1823a | 0.46492 | Positive stack backup |

Last-attempt operational target: `>0.50000`.
Original active top-three gate: `>0.52380`.

## One-command reproduction

From this directory:

```bash
python3 make_final.py --output submission.csv
```

The command copies the packaged final candidate and runs the validator. Expected validator output:

```text
OK: 397 predictions validated
```

This is the recommended deadline-day path because the late-stage candidate selection depends on the final attempt queue and score-feedback router preserved in the experiment package. Optional explicit re-check:

```bash
python3 assert/validate_submission.py submission.csv
```

## Full final-attempt package

The complete candidate package is stored one level up under:

```text
../experiments/final_submission_package/
```

Important files:

```text
../experiments/final_submission_package/current_upload/submission.csv
../experiments/final_submission_package/current_upload/ATTEMPT_CARD.md
../experiments/final_submission_package/RELEASE_CHECKLIST.md
../experiments/final_submission_package/manifests/final_submission_pack_manifest.csv
../experiments/final_submission_package/reports/submission_strategy.md
```

Useful commands from the workspace root:

```bash
python3 experiments/scripts/v1835_final_submission_pack.py --preset full
python3 experiments/scripts/v1871_final_attempt_cockpit.py
python3 experiments/scripts/v1883_pre_upload_guard.py
python3 experiments/scripts/v1884_candidate_pool_coverage_scan.py
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE> --confirm-real-score
```

## Architecture summary

The project follows the required multi-agent + retrieval-augmented design:

1. Fetching stage parses players, claims, votes, executions, deaths, and reveal windows.
2. Analysis and verifier stages compare transcript evidence against role rules and claim contradictions.
3. A constrained solver enforces game-size role budgets and emits `id,index,character,role,wolf_score`.
4. Late-stage deterministic audits prioritize execution-anchored reveals and reject noisy in-game accusations.
5. The final candidate queue wraps validated CSVs with manifest hashes, route rules, and rollback baselines.

## Directory layout

```text
hw2_D13922024/
├── make_final.py
├── submission.csv
├── hw2_report.md
├── README.md
├── requirements.txt
├── assert/validate_submission.py
├── checkpoints/
│   ├── final_current_private.csv
│   ├── final_v1846e_private.csv  (current final one-shot candidate)
│   ├── final_v1840c_private.csv  (previous scored attempt: 0.49349)
│   ├── final_v1840b_private.csv  (previous scored attempt: 0.49266)
│   ├── final_v1826b_private.csv  (previous staged diagnostic follow-up)
│   ├── final_v1826a_private.csv  (previous scored attempt: 0.48854)
│   ├── final_v1856g_private.csv  (score-feedback history checkpoint)
│   ├── v440_base_private.csv
│   ├── v440_base_public.csv
│   ├── v851_after_cross_claim_private.csv
│   ├── v851_after_cross_claim_public.csv
│   └── v1120_evidence.csv
├── pipeline_steps/
└── src/
```

## Completion boundary

This package prepares the upload and reproduction artifacts.  It does not by itself prove the leaderboard objective.  The last-attempt operational target is complete only after a real private score greater than `0.50000` is recorded; the original top-three objective remains complete only after a real private score greater than `0.52380` is recorded.
