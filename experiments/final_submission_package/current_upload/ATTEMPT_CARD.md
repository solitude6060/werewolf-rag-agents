# Final Attempt Cockpit

Generated UTC: `2026-05-15T00:32:57+00:00`

## Upload now

Use this fixed path:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Selected row source: `current_upload_manual_override`
Manual override reason: `skip score-only v1846g after v1856g real private score 0.42894; updated top3 threshold is 0.52380; pivot to structural v1826a for upside`
Selected candidate: `v1826a` (`queue` order `1`)
Selected source: `experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv`
Rows: `397`
SHA-256: `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad`
Manifest validation status: `pass`
Staged file exists: `yes`
Staged file matches selected source: `yes`
Staged validator: `OK: 397 predictions validated`

If staged match is not `yes`, run:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py --group queue --order 1 --override-reason 'skip score-only v1846g after v1856g real private score 0.42894; updated top3 threshold is 0.52380; pivot to structural v1826a for upside'
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
Stop threshold: `>0.52380`

## After real score appears

Dry-run first:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Then record only if the score is real:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group queue --order 1 --score <REAL_SCORE> --confirm-real-score
```

## Router preview for this selected row

| Scenario | Example score | Recommended next | Path check |
| --- | ---: | --- | --- |
| hit top-3 | `0.52381` | `STOP: score exceeds top-3 threshold.` | `not_a_csv` |
| strong positive | `0.48000` | `experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv` | `ok manifest_status=pass candidate=v1826b` |
| tiny positive | `0.47120` | `experiments/final_submission_package/contingency/01_v1825c_diagnostic_neutral_private.csv` | `ok manifest_status=pass candidate=v1825c` |
| exact current best | `0.47119` | `experiments/final_submission_package/contingency/01_v1825c_diagnostic_neutral_private.csv` | `ok manifest_status=pass candidate=v1825c` |
| near baseline | `0.47080` | `experiments/final_submission_package/contingency/01_v1825c_diagnostic_neutral_private.csv` | `ok manifest_status=pass candidate=v1825c` |
| small regression | `0.46600` | `experiments/final_submission_package/contingency/02_v1825a_diagnostic_mild_regression_private.csv` | `ok manifest_status=pass candidate=v1825a` |
| severe regression | `0.46400` | `experiments/final_submission_package/contingency/03_v1827a_fallback_severe_regression_private.csv` | `ok manifest_status=pass candidate=v1827a` |

## Completion boundary

Only a real private score greater than `0.52380` completes the active score objective.

