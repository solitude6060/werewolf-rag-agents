# v1880 Post-Score Next-Path Validation

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Purpose

Make the user-facing post-score command center validate the recommended next upload path during dry-run.  This avoids relying on the user to manually cross-check manifest membership, file existence, row count, SHA-256, and package validation status after reporting a real score.

## Change

`experiments/scripts/v1872_post_score_command_center.py` now prints:

```text
NEXT_PATH_STATUS=<status>
```

For concrete CSV recommendations, the status is only `concrete_ok:<group>#<order>:<candidate>` when all checks pass:

1. `recommended_next` appears in `final_submission_pack_manifest.csv`.
2. The CSV file exists.
3. The CSV has exactly `397` prediction rows.
4. The file SHA-256 matches the manifest.
5. Manifest `validation_status` is `pass`.

For terminal/non-CSV recommendations such as top-3 stop states, the status is:

```text
non_concrete_ok
```

Any concrete-path validation failure exits the command instead of silently showing an unsafe next upload.

## Validation evidence

```bash
python3 -m py_compile experiments/scripts/v1872_post_score_command_center.py
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.47120
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.50672
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.46400
python3 experiments/scripts/v1872_post_score_command_center.py --group portfolio_queue --order 2 --score 0.48001 --previous-score 0.48000
python3 experiments/scripts/v1875_route_matrix_regression.py
```

Observed:

```text
0.47120 -> NEXT_PATH_STATUS=concrete_ok:scoreonly_safe_queue#2:v1853g
0.50672 -> NEXT_PATH_STATUS=non_concrete_ok
0.46400 -> NEXT_PATH_STATUS=concrete_ok:scoreonly_safe_queue#5:v1846g
portfolio order2 0.48001 vs 0.48000 -> NEXT_PATH_STATUS=concrete_ok:charprior_queue#2:v1853b
route matrix -> SCENARIOS=45, FAILURES=0
```

Dry-run mutation check:

```text
score feedback records = absent
current_upload/submission.csv SHA-256 = 468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
current_upload/metadata.json SHA-256 = 3ba1d6018708ae9178f86f74027274e3ab9aca107e2199b8c798db9ccccd5904
```

## Completion boundary

This improves the safety of acting on the next real score.  It does not complete the active score goal because no real Kaggle private score greater than `0.50671` has been recorded.
