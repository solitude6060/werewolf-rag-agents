# Final Attempt Cockpit

Generated UTC: `2026-05-15T02:37:55+00:00`

## Final archived best

Use this fixed path for the final package default:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Selected row source: `current_upload_manual_override`
Manual override reason: `final project closeout after all attempts exhausted; package default returns to best verified candidate v1840c=0.49349 rather than failed last attempt v1846e=0.46698`
Selected candidate: `v1840c` (`overlay` order `9`)
Selected source: `experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv`
Rows: `397`
SHA-256: `fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145`
Manifest validation status: `pass`
Staged file exists: `yes`
Staged file matches selected source: `yes`
Staged validator: `OK: 397 predictions validated`

If staged match is not `yes`, run:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py --group overlay --order 9 --override-reason 'final project closeout after all attempts exhausted; package default returns to best verified candidate v1840c=0.49349 rather than failed last attempt v1846e=0.46698'
```

For the first upload with no records, this is also valid:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py
```

Before packaging or hand-in, run the final guard:

```bash
python3 experiments/scripts/v1883_pre_upload_guard.py
```

Expected guard result: `UPLOAD_READY=yes` for file consistency; no upload attempts remain.

## Attempt budget

Attempts used from records: `5`
Attempts remaining from records: `0`
Best recorded score: `0.49349`
Latest recorded score: `0.46698`
Stop threshold: `>0.52380`

## Score recording status

All five final attempts have already been recorded.  The best recorded score is `v1840c = 0.49349`; the failed last attempt is `v1846e = 0.46698`.  The commands below are retained only for traceability:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>
```

Then record only if the score is real:

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score
```

Fallback direct dry-run if the bridge is unavailable:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Fallback direct record command if the validated score must be typed manually:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group overlay --order 9 --score <REAL_SCORE> --confirm-real-score
```

## Router preview for this selected row

| Scenario | Example score | Recommended next | Path check |
| --- | ---: | --- | --- |
| hit top-3 | `0.52381` | `STOP: score exceeds top-3 threshold.` | `not_a_csv` |
| strong positive | `0.48000` | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` | `ok manifest_status=pass candidate=v1842e` |
| tiny positive | `0.47120` | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` | `ok manifest_status=pass candidate=v1842e` |
| exact current best | `0.47119` | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` | `ok manifest_status=pass candidate=v1842e` |
| near baseline | `0.47080` | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` | `ok manifest_status=pass candidate=v1842e` |
| small regression | `0.46600` | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` | `ok manifest_status=pass candidate=v1842e` |
| severe regression | `0.46400` | `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv` | `ok manifest_status=pass candidate=v1842e` |

## Completion boundary

Only a real private score greater than `0.52380` completes the active score objective.

