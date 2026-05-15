# Final Attempt Cockpit

Generated UTC: `2026-05-15T01:56:20+00:00`

## Upload now

Use this fixed path:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Selected row source: `latest_record_recommended_next`
Selected candidate: `v1826b` (`queue` order `2`)
Selected source: `experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv`
Rows: `397`
SHA-256: `8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b`
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

Before manually uploading, run the final guard:

```bash
python3 experiments/scripts/v1883_pre_upload_guard.py
```

Expected guard result: `UPLOAD_READY=yes`.

## Attempt budget

Attempts used from records: `2`
Attempts remaining from records: `3`
Best recorded score: `0.48854`
Latest recorded score: `0.48854`
Stop threshold: `>0.52380`

## After real score appears

Use the no-edit current-upload bridge first; it reads the staged metadata and avoids typing group/order by hand:

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
python3 experiments/scripts/v1872_post_score_command_center.py --group queue --order 2 --score <REAL_SCORE> --confirm-real-score
```

## Router preview for this selected row

| Scenario | Example score | Recommended next | Path check |
| --- | ---: | --- | --- |
| hit top-3 | `0.52381` | `STOP: score exceeds top-3 threshold.` | `not_a_csv` |
| strong positive | `0.48000` | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | `ok manifest_status=pass candidate=v1827d` |
| tiny positive | `0.47120` | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | `ok manifest_status=pass candidate=v1827d` |
| exact current best | `0.47119` | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | `ok manifest_status=pass candidate=v1827d` |
| near baseline | `0.47080` | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | `ok manifest_status=pass candidate=v1827d` |
| small regression | `0.46600` | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | `ok manifest_status=pass candidate=v1827d` |
| severe regression | `0.46400` | `experiments/final_submission_package/contingency/04_v1827d_after_v1826a_positive_b_negative_private.csv` | `ok manifest_status=pass candidate=v1827d` |

## Completion boundary

Only a real private score greater than `0.52380` completes the active score objective.

