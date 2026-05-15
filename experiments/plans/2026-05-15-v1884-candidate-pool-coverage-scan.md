# v1884 Candidate Pool Coverage Scan Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Before spending the final deadline-day upload attempts, verify that the final submission package does not miss a locally available private candidate with a stronger public proxy and lower structural risk than the staged first upload or packaged maximum.

## Constraints

- This is a local audit only; it cannot prove private leaderboard performance.
- Do not upload, record, or infer a Kaggle private score from local proxy metrics.
- Preserve the staged first upload unless a unique, unmanifested candidate clears the review threshold.
- Compare candidates by normalized prediction content, not only file paths or byte hashes, because duplicate predictions may differ by CSV formatting.

## Inputs

- Candidate pool: `experiments/submissions/*private.csv`
- Public counterparts: `experiments/submissions/*public.csv`
- Package manifest: `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv`
- Current upload: `experiments/final_submission_package/current_upload/submission.csv`
- Verified rollback baseline: `experiments/final_submission_package/known_best/01_v1824a_score_0p47119_private.csv`
- Public labels for proxy scoring: `werewolf-project/data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv`

## Method

1. Score paired public CSVs with the local assignment proxy formula.
2. Keep private-shaped candidates with 397 rows.
3. Compute distance versus v1824a and the current staged upload.
4. Compute a normalized prediction signature over `(id,index,character,role,wolf_score)` so formatting-only duplicates map to the package.
5. Mark direct manifest matches and signature-level package duplicates as covered.
6. Flag only unmanifested unique predictions that beat the packaged maximum proxy with at most four role changes versus v1824a.

## Verification standard

- `python3 -m py_compile experiments/scripts/v1884_candidate_pool_coverage_scan.py`
- `python3 experiments/scripts/v1884_candidate_pool_coverage_scan.py`
- Expected audit output includes `REVIEW_CANDIDATES=0` before keeping the staged upload unchanged.
- The generated report must state that the active score goal is not complete without a real private score greater than `0.52380`.

## Outputs

- `experiments/scripts/v1884_candidate_pool_coverage_scan.py`
- `experiments/reports/v1884_candidate_pool_coverage_scan.csv`
- `experiments/reports/v1884_candidate_pool_coverage_scan.md`

## Stop condition

Stop this audit when no unmanifested unique high-public-proxy candidate is found, the staged upload remains validator-clean, and the release checklist records the v1884 guard.
