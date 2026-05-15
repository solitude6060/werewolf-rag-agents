# Final Attempt Cockpit

Generated UTC: `2026-05-15T00:24:17+00:00`

## Upload now

Use this fixed path:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Selected row source: `latest_record_recommended_next`
Selected candidate: `v1846g` (`scoreonly_safe_queue` order `5`)
Selected source: `experiments/final_submission_package/scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv`
Rows: `397`
SHA-256: `f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb`
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

Attempts used from records: `1`
Attempts remaining from records: `4`
Best recorded score: `0.42894`
Latest recorded score: `0.42894`
Stop threshold: `>0.50671`

## After real score appears

Dry-run first:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Then record only if the score is real:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group scoreonly_safe_queue --order 5 --score <REAL_SCORE> --confirm-real-score
```

## Router preview for this selected row

| Scenario | Example score | Recommended next | Path check |
| --- | ---: | --- | --- |
| hit top-3 | `0.50672` | `STOP: score exceeds top-3 threshold.` | `not_a_csv` |
| strong positive | `0.48000` | `experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv` | `ok manifest_status=pass candidate=v1826a` |
| tiny positive | `0.47120` | `experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv` | `ok manifest_status=pass candidate=v1826a` |
| exact current best | `0.47119` | `experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv` | `ok manifest_status=pass candidate=v1826a` |
| near baseline | `0.47080` | `experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv` | `ok manifest_status=pass candidate=v1826a` |
| small regression | `0.46600` | `experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv` | `ok manifest_status=pass candidate=v1826a` |
| severe regression | `0.46400` | `experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv` | `ok manifest_status=pass candidate=v1826a` |

## Completion boundary

Only a real private score greater than `0.50671` completes the active score objective.

