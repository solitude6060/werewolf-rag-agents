# Extra Three-Submit Batch

Date: 2026-05-15

Purpose: prepare three fixed, validated CSVs for manual upload during the ten-additional-submit sprint. This batch does not record any score by itself.

## Upload order

| Order | Candidate | Path | Rationale | SHA-256 |
| ---: | --- | --- | --- | --- |
| 01 | `v1842e` | `experiments/final_submission_package/upload_batch_2026-05-15_extra3/01_v1842e_conservative_blackboost_isolation_private.csv` | First: isolates black-boost without the failed rolecap stack; 3 score-only row changes vs v1840c. | `6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f` |
| 02 | `v1845c` | `experiments/final_submission_package/upload_batch_2026-05-15_extra3/02_v1845c_high_variance_knownbest_blackboost_private.csv` | Second: independent black-boost/known-best overlay; larger swing than v1842e, kept for breakthrough chance. | `dc42d87aceb2cd79d4e2f1ae026f03f234f6b4e4060aed784098df2f5f5ea401` |
| 03 | `v1826b` | `experiments/final_submission_package/upload_batch_2026-05-15_extra3/03_v1826b_structural_positive_followup_private.csv` | Third: untried structural follow-up that router originally recommends after the positive v1826a score. | `8c16775f7eba65456c6050260ed8a0446ef11d2f75a4bdc2a39423400a2aad4b` |

## After each private score appears

Use the matching command below. Keep `<REAL_SCORE>` as a decimal like `0.49349`, not a percent.

### 01 `v1842e`

Dry-run first:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group black_boost_queue --order 5 --score <REAL_SCORE> --skip-stage
```

Record only after confirming the score is a real Kaggle private score:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group black_boost_queue --order 5 --score <REAL_SCORE> --confirm-real-score --skip-stage
```

### 02 `v1845c`

Dry-run first:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group known_best_overlay --order 3 --score <REAL_SCORE> --skip-stage
```

Record only after confirming the score is a real Kaggle private score:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group known_best_overlay --order 3 --score <REAL_SCORE> --confirm-real-score --skip-stage
```

### 03 `v1826b`

Dry-run first:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group queue --order 2 --score <REAL_SCORE> --skip-stage
```

Record only after confirming the score is a real Kaggle private score:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group queue --order 2 --score <REAL_SCORE> --confirm-real-score --skip-stage
```

## Validation boundary

All files in this batch are byte-for-byte copies of manifest candidates and have 397 rows. The active score goal remains incomplete until a real private score greater than `0.52380` is recorded.
