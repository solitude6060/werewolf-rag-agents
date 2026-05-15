# Reproducibility and Validation Guide

This guide describes how to reproduce the packaged submission, validate candidate CSVs, and record returned private scores without mutating records prematurely.

## Environment

Minimum fast-path environment:

- Python 3.10+
- Packages listed in `hw2_D13922024/requirements.txt`
- No external API is required for the bundled checkpoint reproduction path.

Optional full pipeline environment:

- Local Ollama server if rerunning local model stages.
- Local models matching the report assumptions, for example qwen/gemma-class models within course constraints.

## Fast reproduction path

From the repository root:

```bash
cd hw2_D13922024
python3 make_final.py --output /tmp/werewolf_submission_check.csv
```

Validate the generated file:

```bash
python3 assert/validate_submission.py /tmp/werewolf_submission_check.csv
```

Expected result:

```text
OK: 397 predictions validated
```

## Current upload validation

From the repository root:

```bash
python3 werewolf-project/assert/validate_submission.py \
  experiments/final_submission_package/current_upload/submission.csv
```

Expected result:

```text
OK: 397 predictions validated
```

## Pre-upload guard sequence

```bash
python3 experiments/scripts/v1869_attempt_budget_guard.py
python3 experiments/scripts/v1904_attempt_state_guard.py
python3 experiments/scripts/v1883_pre_upload_guard.py
python3 experiments/scripts/v1888_final_upload_preflight.py
python3 experiments/scripts/v1908_final_goal_status.py
```

Expected high-level state before upload:

| Check | Expected |
| --- | --- |
| Attempt budget | `max_attempts=15`, `attempts_remaining=10` before new scores are recorded |
| Attempt state | `ATTEMPT_STATE_READY=yes` |
| Upload guard | `UPLOAD_READY=yes` |
| Final status | `ACTION=UPLOAD_CURRENT` |

## Extra three-submit batch

Validate all three fixed upload files:

```bash
python3 werewolf-project/assert/validate_submission.py \
  experiments/final_submission_package/upload_batch_2026-05-15_extra3/01_v1842e_conservative_blackboost_isolation_private.csv
python3 werewolf-project/assert/validate_submission.py \
  experiments/final_submission_package/upload_batch_2026-05-15_extra3/02_v1845c_high_variance_knownbest_blackboost_private.csv
python3 werewolf-project/assert/validate_submission.py \
  experiments/final_submission_package/upload_batch_2026-05-15_extra3/03_v1826b_structural_positive_followup_private.csv
```

The batch validation report is:

```text
experiments/final_submission_package/upload_batch_2026-05-15_extra3/validation.md
```

## Score recording rule

Do not record a score until it is a real private leaderboard score.  Use the per-candidate commands from:

```text
experiments/final_submission_package/upload_batch_2026-05-15_extra3/README.md
```

Example dry-run/confirm pattern:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py \
  --group black_boost_queue --order 5 --score <REAL_SCORE> --skip-stage

python3 experiments/scripts/v1872_post_score_command_center.py \
  --group black_boost_queue --order 5 --score <REAL_SCORE> --confirm-real-score --skip-stage
```

## Completion gate

The score objective is complete only if the records-based gate says so:

```bash
python3 experiments/scripts/v1906_goal_completion_gate.py
```

Required local evidence:

```text
GOAL_COMPLETE=yes
BEST_SCORE > 0.52380
```

## Integrity checks

Useful SHA-256 checks:

```bash
sha256sum \
  experiments/final_submission_package/current_upload/submission.csv \
  hw2_D13922024/submission.csv \
  hw2_D13922024/checkpoints/final_current_private.csv
```

Current expected SHA for `v1842e`:

```text
6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f
```
