# v1866 Final Attempt Runbook

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Purpose

Provide a single local command that prints the exact next upload file, validates it, checks its hash against the final package manifest, and prints the router command to use after the real Kaggle private score is known.

## Command

```bash
python3 experiments/scripts/v1866_final_attempt_runbook.py
```

Default output points to:

```text
experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
```

After v1870 staging, the same command also prints the fixed manual-upload path when it is a byte-for-byte match:

```text
experiments/final_submission_package/current_upload/submission.csv
```

## Verified output fields

The command prints:

- group/order/candidate,
- upload path,
- row count,
- SHA-256 hash,
- manifest validation status,
- live validator output,
- fixed staged upload path when available,
- exact post-score router command,
- stop threshold `0.50671`.

## Validation performed

```bash
python3 -m py_compile experiments/scripts/v1866_final_attempt_runbook.py
python3 experiments/scripts/v1866_final_attempt_runbook.py --skip-validation
python3 experiments/scripts/v1866_final_attempt_runbook.py
python3 experiments/scripts/v1866_final_attempt_runbook.py --score 0.48000
python3 experiments/scripts/v1866_final_attempt_runbook.py --score 0.50672
```

Observed key output:

```text
NEXT_UPLOAD
group=scoreonly_safe_queue
order=1
candidate=v1856g
path=experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
rows=397
sha256=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
manifest_validation_status=pass
validator=OK: 397 predictions validated
STAGED_UPLOAD
path=experiments/final_submission_package/current_upload/submission.csv
sha256=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
POST_SCORE_COMMAND
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --dry-run
STOP_IF_SCORE_GREATER_THAN=0.50671
```

Router previews:

- score `0.48000` -> `scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv`.
- score `0.50672` -> stop.

## Decision

Use this command immediately before each manual upload to avoid uploading a stale or wrong file.  This does not complete the active score goal; the goal still requires a real Kaggle private score greater than `0.50671`.
