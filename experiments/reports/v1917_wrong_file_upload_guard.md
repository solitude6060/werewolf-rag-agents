# v1917 Wrong-File Upload Guard

Generated UTC: `2026-05-15T00:55:38+00:00`

## Decision

Upload only the current-upload file or its documented safe aliases. Do not upload legacy/worktree `submission.csv` files.

## Safe upload whitelist

| Path | Rows | SHA-256 | Status |
| --- | ---: | --- | --- |
| `experiments/final_submission_package/current_upload/submission.csv` | 397 | `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad` | `safe_upload_whitelist` |
| `hw2_D13922024/checkpoints/final_current_private.csv` | 397 | `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad` | `safe_upload_whitelist` |
| `hw2_D13922024/checkpoints/final_v1826a_private.csv` | 397 | `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad` | `safe_upload_whitelist` |
| `hw2_D13922024/submission.csv` | 397 | `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad` | `safe_upload_whitelist` |

## Do not upload lookalikes

| Path | Rows | SHA-256 | Reason |
| --- | ---: | --- | --- |
| `experiments/worktrees/consistency-solver/hw2_D13922024/submission.csv` | 673 | `6abc72ae3aae93fdba09868e82903c6b8550d424eda9d290e890134847dd9f0a` | different SHA and row count from current v1826a upload |
| `experiments/worktrees/endgame-parser/hw2_D13922024/submission.csv` | 673 | `6abc72ae3aae93fdba09868e82903c6b8550d424eda9d290e890134847dd9f0a` | different SHA and row count from current v1826a upload |
| `experiments/worktrees/v53-feedback/hw2_D13922024/submission.csv` | 673 | `6abc72ae3aae93fdba09868e82903c6b8550d424eda9d290e890134847dd9f0a` | different SHA and row count from current v1826a upload |
| `werewolf-project/artifacts/legacy-submissions/hw2_D13922024/submission.csv` | 673 | `6abc72ae3aae93fdba09868e82903c6b8550d424eda9d290e890134847dd9f0a` | different SHA and row count from current v1826a upload |

## Required current upload

```text
experiments/final_submission_package/current_upload/submission.csv
```

Expected SHA-256: `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad`

## Completion boundary

This wrong-file guard only reduces manual upload risk. It does not complete the active score objective; completion still requires a real private score greater than `0.52380`.
