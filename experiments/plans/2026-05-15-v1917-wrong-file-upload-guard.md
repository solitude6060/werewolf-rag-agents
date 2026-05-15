# v1917 Wrong-File Upload Guard Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Reduce the chance of spending a final attempt on a stale `submission.csv` by documenting the safe upload whitelist and the unsafe legacy/worktree lookalikes.

## Context

The current valid upload is `v1826a` at `experiments/final_submission_package/current_upload/submission.csv` with SHA-256 `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad` and 397 prediction rows. A deeper repository scan found legacy/worktree `submission.csv` files with 673 rows and a different SHA.

## Constraints

- Do not modify candidate CSV contents.
- Do not delete legacy or worktree files.
- Do not record a score or stage a new upload.
- Keep the warning focused on the current upload handoff and audit artifact.

## Method

1. Enumerate every `submission.csv` outside `.git`.
2. Compute row counts and SHA-256 values.
3. Mark the exact safe whitelist and unsafe lookalike paths.
4. Update current-upload README with a concise wrong-file warning.
5. Verify the safe upload still validates and all safe aliases share the current SHA.

## Verification standard

- `find . -path './.git' -prune -o -type f -name 'submission.csv'` identifies all lookalikes.
- Safe whitelist files all have SHA `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad`.
- Legacy/worktree lookalikes are documented as not safe to upload.
- `validate_submission.py` passes for the current upload.

## Outputs

- `experiments/reports/v1917_wrong_file_upload_guard.md`
- Updated `experiments/final_submission_package/current_upload/README.md`

## Stop condition

Stop when the whitelist and do-not-upload list are documented and the current upload remains validator-clean.
