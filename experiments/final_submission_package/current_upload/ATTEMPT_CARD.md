# Final Attempt Cockpit

Generated UTC: `2026-05-14T17:17:42+00:00`

## Upload now

Use this fixed path:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Selected row source: `no_records_default`
Selected candidate: `v1856g` (`scoreonly_safe_queue` order `1`)
Selected source: `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv`
Rows: `397`
SHA-256: `468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d`
Manifest validation status: `pass`
Staged file exists: `yes`
Staged file matches selected source: `yes`
Staged validator: `OK: 397 predictions validated`

If staged match is not `yes`, run:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py --from-records
```

For the first upload with no records, this is also valid:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py
```

## Attempt budget

Attempts used from records: `0`
Attempts remaining from records: `5`
Best recorded score: `none`
Latest recorded score: `none`
Stop threshold: `>0.50671`

## After real score appears

Dry-run first:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Then record only if the score is real:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --confirm-real-score
```

## Router preview for this selected row

| Scenario | Example score | Recommended next | Path check |
| --- | ---: | --- | --- |
| hit top-3 | `0.50672` | `STOP: score exceeds top-3 threshold.` | `not_a_csv` |
| strong positive | `0.48000` | `experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv` | `ok manifest_status=pass candidate=v1853g` |
| tiny positive | `0.47120` | `experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv` | `ok manifest_status=pass candidate=v1853g` |
| exact current best | `0.47119` | `experiments/final_submission_package/scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv` | `ok manifest_status=pass candidate=v1850g` |
| near baseline | `0.47080` | `experiments/final_submission_package/scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv` | `ok manifest_status=pass candidate=v1850g` |
| small regression | `0.46600` | `experiments/final_submission_package/scoreonly_safe_queue/04_v1848g_scoreonly_denoise_private.csv` | `ok manifest_status=pass candidate=v1848g` |
| severe regression | `0.46400` | `experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv` | `ok manifest_status=pass candidate=v1846g` |

## Completion boundary

Only a real private score greater than `0.50671` completes the active score objective.

