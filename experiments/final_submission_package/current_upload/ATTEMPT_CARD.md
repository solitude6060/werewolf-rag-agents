# Final Attempt Cockpit

Generated UTC: `2026-05-15T02:07:26+00:00`

## Upload now

Use this fixed path:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Selected row source: `current_upload_manual_override`
Manual override reason: `post-v1826a 0.48854: only 3 recorded attempts remain; preserve the positive v1826a AP layer, add g23 via v1826d, and apply high-precision AP overlay for higher top-3 upside than diagnostic v1826b`
Selected candidate: `v1840b` (`overlay` order `8`)
Selected source: `experiments/final_submission_package/overlay/08_v1840b_v1826d_high_precision_medium_ap_overlay_private.csv`
Rows: `397`
SHA-256: `16d56e36317dfdbe3e2372754def6ddeda8182f4bbfdd6723e8018eaa8a911dc`
Manifest validation status: `pass`
Staged file exists: `yes`
Staged file matches selected source: `yes`
Staged validator: `OK: 397 predictions validated`

If staged match is not `yes`, run:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py --group overlay --order 8 --override-reason 'post-v1826a 0.48854: only 3 recorded attempts remain; preserve the positive v1826a AP layer, add g23 via v1826d, and apply high-precision AP overlay for higher top-3 upside than diagnostic v1826b'
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
python3 experiments/scripts/v1872_post_score_command_center.py --group overlay --order 8 --score <REAL_SCORE> --confirm-real-score
```

## Router preview for this selected row

| Scenario | Example score | Recommended next | Path check |
| --- | ---: | --- | --- |
| hit top-3 | `0.52381` | `STOP: score exceeds top-3 threshold.` | `not_a_csv` |
| strong positive | `0.48000` | `experiments/final_submission_package/queue/04_v1826c_alt_structural_private.csv` | `ok manifest_status=pass candidate=v1826c` |
| tiny positive | `0.47120` | `experiments/final_submission_package/queue/04_v1826c_alt_structural_private.csv` | `ok manifest_status=pass candidate=v1826c` |
| exact current best | `0.47119` | `experiments/final_submission_package/queue/04_v1826c_alt_structural_private.csv` | `ok manifest_status=pass candidate=v1826c` |
| near baseline | `0.47080` | `experiments/final_submission_package/queue/04_v1826c_alt_structural_private.csv` | `ok manifest_status=pass candidate=v1826c` |
| small regression | `0.46600` | `experiments/final_submission_package/queue/04_v1826c_alt_structural_private.csv` | `ok manifest_status=pass candidate=v1826c` |
| severe regression | `0.46400` | `experiments/final_submission_package/queue/04_v1826c_alt_structural_private.csv` | `ok manifest_status=pass candidate=v1826c` |

## Completion boundary

Only a real private score greater than `0.52380` completes the active score objective.

