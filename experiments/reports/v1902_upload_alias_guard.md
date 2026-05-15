# v1902 Upload Alias Guard

Generated UTC: `2026-05-15T02:22:04+00:00`

## Summary

- Alias guard ready: `yes`
- Canonical upload: `experiments/final_submission_package/current_upload/submission.csv`
- Canonical rows: `397`
- Canonical SHA-256: `fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145`

## Alias results

| Alias | Exists | Rows | SHA matches | Detail |
| --- | --- | ---: | --- | --- |
| `hw2_D13922024/submission.csv` | yes | `397` | yes | `ok` |
| `hw2_D13922024/checkpoints/final_current_private.csv` | yes | `397` | yes | `ok` |
| `hw2_D13922024/checkpoints/final_v1840c_private.csv` | yes | `397` | yes | `ok` |

## submission.csv lookalike scan

| Path | Rows | SHA matches canonical | Status | Detail |
| --- | ---: | --- | --- | --- |
| `experiments/final_submission_package/current_upload/submission.csv` | `397` | yes | `safe_whitelist` | `safe upload path` |
| `experiments/worktrees/consistency-solver/hw2_D13922024/submission.csv` | `673` | no | `do_not_upload` | `different SHA or row count from canonical current upload` |
| `experiments/worktrees/endgame-parser/hw2_D13922024/submission.csv` | `673` | no | `do_not_upload` | `different SHA or row count from canonical current upload` |
| `experiments/worktrees/v53-feedback/hw2_D13922024/submission.csv` | `673` | no | `do_not_upload` | `different SHA or row count from canonical current upload` |
| `hw2_D13922024/submission.csv` | `397` | yes | `safe_whitelist` | `safe upload path` |
| `werewolf-project/artifacts/legacy-submissions/hw2_D13922024/submission.csv` | `673` | no | `do_not_upload` | `different SHA or row count from canonical current upload` |

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| canonical_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| canonical_rows_397 | yes | `397` |
| alias_1_exists | yes | `hw2_D13922024/submission.csv` |
| alias_1_rows_match | yes | `alias=397 canonical=397` |
| alias_1_sha_matches | yes | `fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145` |
| alias_2_exists | yes | `hw2_D13922024/checkpoints/final_current_private.csv` |
| alias_2_rows_match | yes | `alias=397 canonical=397` |
| alias_2_sha_matches | yes | `fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145` |
| alias_3_exists | yes | `hw2_D13922024/checkpoints/final_v1840c_private.csv` |
| alias_3_rows_match | yes | `alias=397 canonical=397` |
| alias_3_sha_matches | yes | `fa06e6028d18ecf6e75a73aedd634c190461970b0b330c13721b31c38f56a145` |
| lookalike_scan_completed | yes | `.` |

## Completion boundary

This guard only prevents wrong-file manual upload risk. The active goal is complete only after a real private score greater than `0.52380` is recorded.
