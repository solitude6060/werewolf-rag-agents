# Final Attempt Cockpit

Generated UTC: `2026-05-15T03:34:45+00:00`

## Upload now

Use this fixed path:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Selected row source: `current_upload_manual_override`
Manual override reason: `extra ten-submit restart after prior 5/5 records; isolate v1842e black-boost delta from failed rolecap v1846e; v1842e differs from best v1840c by 3 score-only rows and is not a duplicate`
Selected candidate: `v1842e` (`black_boost_queue` order `5`)
Selected source: `experiments/final_submission_package/black_boost_queue/05_v1842e_queue05_v1829e_blackboost_attack_private.csv`
Rows: `397`
SHA-256: `6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f`
Manifest validation status: `pass`
Staged file exists: `yes`
Staged file matches selected source: `yes`
Staged validator: `OK: 397 predictions validated`

If staged match is not `yes`, run:

```bash
python3 experiments/scripts/v1870_stage_current_upload.py --group black_boost_queue --order 5 --override-reason 'extra ten-submit restart after prior 5/5 records; isolate v1842e black-boost delta from failed rolecap v1846e; v1842e differs from best v1840c by 3 score-only rows and is not a duplicate'
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

Attempts used from records: `5`
Attempts remaining from records: `10`
Best recorded score: `0.49349`
Latest recorded score: `0.46698`
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
python3 experiments/scripts/v1872_post_score_command_center.py --group black_boost_queue --order 5 --score <REAL_SCORE> --confirm-real-score
```

## Router preview for this selected row

| Scenario | Example score | Recommended next | Path check |
| --- | ---: | --- | --- |
| hit top-3 | `0.52381` | `STOP: score exceeds top-3 threshold.` | `not_a_csv` |
| strong positive | `0.48000` | `NO_BLACK_BOOST_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| tiny positive | `0.47120` | `NO_BLACK_BOOST_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| exact current best | `0.47119` | `NO_BLACK_BOOST_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| near baseline | `0.47080` | `NO_BLACK_BOOST_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| small regression | `0.46600` | `NO_BLACK_BOOST_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |
| severe regression | `0.46400` | `NO_BLACK_BOOST_QUEUE_REMAINING: keep best verified score or choose contingency manually.` | `not_a_csv` |

## Completion boundary

Only a real private score greater than `0.52380` completes the active score objective.

