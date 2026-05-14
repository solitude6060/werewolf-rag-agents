# Final Submission Release Checklist

Date: 2026-05-15  
Branch: `dev/final-submission-report-pack`

## Current upload

Upload this file:

```text
experiments/final_submission_package/current_upload/submission.csv
```

Current staged candidate:

```text
scoreonly_safe_queue order 1, v1856g
```

Validation:

```text
Rows: 397
SHA-256: 468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
Validator: OK: 397 predictions validated
```

## One-command entry points

Rebuild the full candidate package:

```bash
python3 experiments/scripts/v1835_final_submission_pack.py --preset full
```

Show the current upload card:

```bash
python3 experiments/scripts/v1871_final_attempt_cockpit.py
```

Run the final pre-upload guard immediately before manual upload:

```bash
python3 experiments/scripts/v1883_pre_upload_guard.py
```

Expected output: `UPLOAD_READY=yes`.

Confirm no higher-public-proxy unique prediction was missed from the local candidate pool:

```bash
python3 experiments/scripts/v1884_candidate_pool_coverage_scan.py
```

Expected output: `REVIEW_CANDIDATES=0`.

After a real Kaggle private score appears, preview the route:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE>
```

Record the score only after confirming it is real:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --score <REAL_SCORE> --confirm-real-score
```

## Package structure

```text
experiments/final_submission_package/
  README.md
  RELEASE_CHECKLIST.md
  current_upload/
    submission.csv
    metadata.json
    README.md
    ATTEMPT_CARD.md
  manifests/
    final_submission_pack_manifest.csv
    validation_log.txt
    document_lint_log.txt
  reports/
    submission_strategy.md
    reproducibility_checklist.md
    hw2_report_draft.md
  scoreonly_safe_queue/
  portfolio_queue/
  known_best/
  known_best_overlay/
  queue/
  contingency/
  overlay/
```

## Key reports

- `experiments/final_submission_package/reports/submission_strategy.md`
- `experiments/reports/v1861_active_goal_completion_audit.md`
- `experiments/reports/v1873_final_five_diversity_audit.md`
- `experiments/reports/v1874_positive_signal_router_threshold.md`
- `experiments/reports/v1875_route_matrix_regression.md`
- `experiments/reports/v1883_pre_upload_guard.md`
- `experiments/reports/v1884_candidate_pool_coverage_scan.md`

## Latest local verification

```text
Route matrix: 45 scenarios, 0 failures
Pre-upload guard: UPLOAD_READY=yes
Candidate pool coverage: REVIEW_CANDIDATES=0
Current upload validator: OK: 397 predictions validated
Submission-facing document findings: 0
Broad problem-phrase findings: 0
```

## Stop condition

The active score objective is not complete until a real Kaggle private score is strictly greater than:

```text
0.50671
```

No local proxy, manifest pass, route regression, or validator result is enough by itself.
