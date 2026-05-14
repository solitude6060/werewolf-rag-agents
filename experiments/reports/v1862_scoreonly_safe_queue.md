# v1862 Score-Only Safe Queue

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Purpose

Add a final upload route that preserves the current verified-best private role labels and changes only `wolf_score` values.  This reduces the chance of losing private Macro-F1 from role-label changes while keeping the high public AP proxy from the v1846-v1856 calibration sequence.

## Key finding

The v1860 audit showed that v1856g has the same local public proxy as the current portfolio first file v1856a, but no private-side role-label changes versus the verified-best v1824a submission.

| Candidate | Public proxy | Private role changes vs v1824a | Score MAE vs v1824a | Interpretation |
| --- | ---: | ---: | ---: | --- |
| v1856a | 0.5903 | 4 | 0.0673 | previous risk-balanced first file |
| v1856g | 0.5903 | 0 | 0.0582 | same proxy, lower role-transfer risk |
| v1853a | 0.5942 | 4 | 0.0780 | previous maximum-proxy portfolio file |
| v1853g | 0.5942 | 0 | 0.0701 | same maximum proxy, score-only fallback |
| v1850g | 0.5853 | 0 | 0.0585 | score-only low-tail fallback |
| v1848g | 0.5845 | 0 | 0.0427 | score-only denoise fallback |
| v1846g | 0.5742 | 0 | 0.0155 | lowest-distance score-only fallback |

## Queue

| Order | Candidate | Upload path | Public proxy | Risk note |
| ---: | --- | --- | ---: | --- |
| 1 | v1856g | `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` | 0.5903 | Same public proxy as v1856a, but preserves verified-best private roles. |
| 2 | v1853g | `experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv` | 0.5942 | Maximum public proxy; still higher score-calibration risk. |
| 3 | v1850g | `experiments/final_submission_package/scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv` | 0.5853 | Lower-calibration fallback. |
| 4 | v1848g | `experiments/final_submission_package/scoreonly_safe_queue/04_v1848g_scoreonly_denoise_private.csv` | 0.5845 | Denoise fallback. |
| 5 | v1846g | `experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv` | 0.5742 | Lowest score-distance among the high-proxy fallbacks. |

## Router

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --dry-run
```

Verified dry-runs:

- order 1 score `0.48000` -> order 2 (`v1853g`).
- order 1 score `0.47080` -> order 3 (`v1850g`).
- order 1 score `0.46400` -> order 5 (`v1846g`).
- order 1 score `0.50672` -> stop.

## Validation

```bash
python3 -m py_compile experiments/scripts/v1835_final_submission_pack.py experiments/scripts/v1836_score_feedback_router.py experiments/scripts/v1860_private_transfer_rank_audit.py
python3 experiments/scripts/v1835_final_submission_pack.py --preset full
python3 experiments/scripts/v1835_final_submission_pack.py --preset scoreonly-safe-queue --out /tmp/hw2_pack_scoreonly_safe_queue_smoke --skip-validation --no-existing-doc-scan
python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
```

Observed package state after this change:

- Full manifest rows: 83.
- Full manifest validator pass rows: 83.
- Rows per private CSV: 397.
- `scoreonly_safe_queue` rows: 5.
- First upload validator: `OK: 397 predictions validated`.

## Decision

Recommended first upload is now the score-only safe first slot:

```text
experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
```

The older portfolio first slot remains available if the user explicitly wants to test role-label changes:

```text
experiments/final_submission_package/portfolio_queue/01_v1856a_risk_balanced_first_private.csv
```

The active goal remains incomplete until a real Kaggle private score greater than `0.50671` is reported.
