# v1871 Final Attempt Cockpit

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Purpose

Provide one deadline-day command that prints and writes a compact upload/score-routing card.

## Command

```bash
python3 experiments/scripts/v1871_final_attempt_cockpit.py
```

Default card path:

```text
experiments/final_submission_package/current_upload/ATTEMPT_CARD.md
```

## Fresh evidence

Observed current state:

```text
Selected candidate: v1856g (scoreonly_safe_queue order 1)
Fixed upload path: experiments/final_submission_package/current_upload/submission.csv
Rows: 397
SHA-256: 468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
Staged file matches selected source: yes
Staged validator: OK: 397 predictions validated
Attempts used from records: 0
Attempts remaining from records: 5
```

Router preview in the generated card:

| Scenario | Example score | Recommended next |
| --- | ---: | --- |
| hit top-3 | `0.50672` | stop |
| strong positive | `0.48000` | `scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv` |
| near baseline | `0.47080` | `scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv` |
| small regression | `0.46600` | `scoreonly_safe_queue/04_v1848g_scoreonly_denoise_private.csv` |
| severe regression | `0.46400` | `scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv` |

## Validation commands

```bash
python3 -m py_compile experiments/scripts/v1871_final_attempt_cockpit.py
python3 experiments/scripts/v1871_final_attempt_cockpit.py
python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv
```

## Completion boundary

This cockpit does not prove a leaderboard improvement.  The active goal still requires a real Kaggle private score greater than `0.50671`.
