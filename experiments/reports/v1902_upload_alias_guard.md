# v1902 Upload Alias Guard

Generated UTC: `2026-05-15T00:33:12+00:00`

## Summary

- Alias guard ready: `yes`
- Canonical upload: `experiments/final_submission_package/current_upload/submission.csv`
- Canonical rows: `397`
- Canonical SHA-256: `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad`

## Alias results

| Alias | Exists | Rows | SHA matches | Detail |
| --- | --- | ---: | --- | --- |
| `hw2_D13922024/submission.csv` | yes | `397` | yes | `ok` |
| `hw2_D13922024/checkpoints/final_current_private.csv` | yes | `397` | yes | `ok` |
| `hw2_D13922024/checkpoints/final_v1826a_private.csv` | yes | `397` | yes | `ok` |

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| canonical_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| canonical_rows_397 | yes | `397` |
| alias_1_exists | yes | `hw2_D13922024/submission.csv` |
| alias_1_rows_match | yes | `alias=397 canonical=397` |
| alias_1_sha_matches | yes | `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad` |
| alias_2_exists | yes | `hw2_D13922024/checkpoints/final_current_private.csv` |
| alias_2_rows_match | yes | `alias=397 canonical=397` |
| alias_2_sha_matches | yes | `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad` |
| alias_3_exists | yes | `hw2_D13922024/checkpoints/final_v1826a_private.csv` |
| alias_3_rows_match | yes | `alias=397 canonical=397` |
| alias_3_sha_matches | yes | `e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad` |

## Completion boundary

This guard only prevents wrong-file manual upload risk. The active goal is complete only after a real private score greater than `0.52380` is recorded.
