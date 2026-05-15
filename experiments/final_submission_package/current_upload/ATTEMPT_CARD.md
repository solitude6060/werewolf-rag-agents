# Final Attempt Cockpit

Generated UTC: `2026-05-15T02:17:25+00:00`

## Upload now

Use this fixed path:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Selected row source: `latest_record_recommended_next`
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

Attempts used from records: `3`
Attempts remaining from records: `2`
Best recorded score: `0.49266`
Latest recorded score: `0.49266`
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
python3 experiments/scripts/v1872_post_score_command_center.py --group overlay --order 9 --score <REAL_SCORE> --confirm-real-score
```

## Router preview for this selected row

| Scenario | Example score | Recommended next | Path check |
| --- | ---: | --- | --- |
| hit top-3 | `0.52381` | `STOP: score exceeds top-3 threshold.` | `not_a_csv` |
| strong positive | `0.48000` | `NO_QUEUE_REMAINING: keep best verified score or choose maximum-risk contingency manually.` | `not_a_csv` |
| tiny positive | `0.47120` | `NO_QUEUE_REMAINING: keep best verified score or choose maximum-risk contingency manually.` | `not_a_csv` |
| exact current best | `0.47119` | `NO_QUEUE_REMAINING: keep best verified score or choose maximum-risk contingency manually.` | `not_a_csv` |
| near baseline | `0.47080` | `NO_QUEUE_REMAINING: keep best verified score or choose maximum-risk contingency manually.` | `not_a_csv` |
| small regression | `0.46600` | `NO_QUEUE_REMAINING: keep best verified score or choose maximum-risk contingency manually.` | `not_a_csv` |
| severe regression | `0.46400` | `NO_QUEUE_REMAINING: keep best verified score or choose maximum-risk contingency manually.` | `not_a_csv` |

## Completion boundary

Only a real private score greater than `0.52380` completes the active score objective.

