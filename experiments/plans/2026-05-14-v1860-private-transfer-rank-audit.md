# v1860 Private-Transfer Rank Audit Plan

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Goal

Before waiting for the next real Kaggle private score, check whether the current final upload recommendation can be improved using the available private-feedback history and structural distance from the verified-best submission.

## Constraints

- Do not treat local public proxy or statistical estimates as completion proof.
- Do not upload to Kaggle from the local environment.
- Do not add dependencies; use Python standard library and existing `local_score.py`.
- Preserve the already validated final package unless this audit produces a clearly better and validated upload path.
- Keep submission/report documents free of authorship/watermark phrases.

## Inputs

- Known private scores in `experiments/scripts/v1858_private_feedback_transfer_audit.py`.
- Current package manifest: `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv`.
- Baseline verified-best candidate: v1824a (`0.47119`).
- Candidate public CSVs from `experiments/submissions/*_public.csv`.
- Candidate private CSVs from the final package and `experiments/submissions/*_private.csv`.

## Method

1. Compute public score features for known and future candidates.
2. Compute structural features relative to v1824a:
   - private/public role changes,
   - score mean absolute difference,
   - score maximum absolute difference,
   - count of score changes above 0.05,
   - count of high-wolf-score rows.
3. Use small-sample private-feedback diagnostics:
   - nearest known candidates by feature distance,
   - leave-one-known-out error,
   - simple risk-adjusted ordering.
4. Compare the resulting order against the current `portfolio_queue` order.

## Validation

- `python3 -m py_compile experiments/scripts/v1860_private_transfer_rank_audit.py`
- `python3 experiments/scripts/v1860_private_transfer_rank_audit.py`
- Re-check final first upload path still exists and validates via package manifest.
- Rerun document lint for submission-facing reports after adding v1860 report.

## Stop condition

- If v1860 supports the existing portfolio first upload, record that evidence and do not alter the package.
- If v1860 identifies a safer/better order with concrete evidence, update the package/router artifacts and rerun validation.
- In all cases, do not mark the active goal complete without a real private score greater than `0.50671`.
