# HW2 — Multi-Agent Werewolf Prediction

Student ID: `D13922024`

## Current packaged submission

The package default submission is the current final-attempt candidate:

```text
submission.csv
```

It is byte-equal to:

```text
checkpoints/final_v1856g_private.csv
```

Candidate lineage: `scoreonly_safe_queue` order `1`, `v1856g`.

Known private leaderboard context before this final-attempt package:

| Rank in our known submissions | Candidate | Private score | Note |
| ---: | --- | ---: | --- |
| 1 | v1824a | 0.47119 | Current verified best rollback |
| 2 | v1823a | 0.46492 | Positive stack backup |
| 3 | v1823b | 0.46492 | Alternative tied backup |
| 4 | v1821a | 0.46455 | Claim-graph repair baseline |
| 5 | v1819b | 0.45499 | Older conservative backup |

Target to beat for the active final-attempt goal: `>0.50671`.

## One-command reproduction

From this directory:

```bash
python3 make_final.py --output submission.csv
python3 assert/validate_submission.py submission.csv
```

Expected validator output:

```text
OK: 397 predictions validated
```

The default command copies the packaged final candidate and validates it.  This is the recommended deadline-day path because the late-stage candidate selection depends on the final attempt queue and score-feedback router preserved in the experiment package.

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
│   ├── final_v1856g_private.csv
│   ├── v440_base_private.csv
│   ├── v440_base_public.csv
│   ├── v851_after_cross_claim_private.csv
│   ├── v851_after_cross_claim_public.csv
│   └── v1120_evidence.csv
├── pipeline_steps/
└── src/
```

## Completion boundary

This package prepares the upload and reproduction artifacts.  It does not by itself prove the active leaderboard objective.  The objective is complete only after a real Kaggle private score greater than `0.50671` is recorded.
