# v1879 Post-Score Command Center Smoke

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Purpose

Validate the exact command surface intended for use after the next real Kaggle score appears.  This is higher-level than the low-level router regression: it checks that `v1872_post_score_command_center.py` reads `current_upload/metadata.json`, dry-runs safely, and does not write score records unless `--confirm-real-score` is passed.

## Pre-check state

```text
current_upload/submission.csv SHA-256 = 468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
current_upload/metadata.json SHA-256 = 3ba1d6018708ae9178f86f74027274e3ab9aca107e2199b8c798db9ccccd5904
score feedback records = absent
```

Current upload context from metadata:

```text
group=scoreonly_safe_queue
order=1
candidate=v1856g
```

## Dry-run scenarios

Commands:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.47120
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.47119
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.50672
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.46400
```

Observed routing:

| Score | Upload context source | Expected behavior | Observed recommendation | Write status |
| ---: | --- | --- | --- | --- |
| 0.47120 | `current_upload/metadata.json` | Tiny positive -> max proxy score-only second slot | `scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv` | `dry_run_only` |
| 0.47119 | `current_upload/metadata.json` | Exact current best -> low-tail score-only fallback | `scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv` | `dry_run_only` |
| 0.50672 | `current_upload/metadata.json` | Top-3 hit -> stop | `STOP: score exceeds top-3 threshold.` | `dry_run_only` |
| 0.46400 | `current_upload/metadata.json` | Severe regression -> final low-distance score-only fallback | `scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv` | `dry_run_only` |

## Post-check state

```bash
ls -l experiments/final_submission_package/manifests/v1836_score_feedback_records.csv \
      experiments/final_submission_package/manifests/v1836_score_feedback_records.md 2>/dev/null || true
sha256sum experiments/final_submission_package/current_upload/submission.csv \
          experiments/final_submission_package/current_upload/metadata.json
python3 experiments/scripts/v1869_attempt_budget_guard.py
```

Observed:

```text
score feedback records = absent
current_upload/submission.csv SHA-256 = 468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
current_upload/metadata.json SHA-256 = 3ba1d6018708ae9178f86f74027274e3ab9aca107e2199b8c798db9ccccd5904
attempts_used=0
attempts_remaining=5
best_score=none
top3_hit=no
```

## Decision

The post-score command center is safe to use for previewing a real score before recording it.  Dry-runs do not mutate score records or the staged current upload.

## Completion boundary

This verifies the post-score operating surface.  It does not complete the active score goal because no real Kaggle private score greater than `0.50671` has been recorded.
