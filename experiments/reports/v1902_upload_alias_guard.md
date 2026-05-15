# v1902 Upload Alias Guard

Generated UTC: `2026-05-15T00:18:47+00:00`

## Summary

- Alias guard ready: `yes`
- Canonical upload: `experiments/final_submission_package/current_upload/submission.csv`
- Canonical rows: `397`
- Canonical SHA-256: `f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb`

## Alias results

| Alias | Exists | Rows | SHA matches | Detail |
| --- | --- | ---: | --- | --- |
| `hw2_D13922024/submission.csv` | yes | `397` | yes | `ok` |
| `hw2_D13922024/checkpoints/final_current_private.csv` | yes | `397` | yes | `ok` |
| `hw2_D13922024/checkpoints/final_v1846g_private.csv` | yes | `397` | yes | `ok` |

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| canonical_exists | yes | `experiments/final_submission_package/current_upload/submission.csv` |
| canonical_rows_397 | yes | `397` |
| alias_1_exists | yes | `hw2_D13922024/submission.csv` |
| alias_1_rows_match | yes | `alias=397 canonical=397` |
| alias_1_sha_matches | yes | `f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb` |
| alias_2_exists | yes | `hw2_D13922024/checkpoints/final_current_private.csv` |
| alias_2_rows_match | yes | `alias=397 canonical=397` |
| alias_2_sha_matches | yes | `f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb` |
| alias_3_exists | yes | `hw2_D13922024/checkpoints/final_v1846g_private.csv` |
| alias_3_rows_match | yes | `alias=397 canonical=397` |
| alias_3_sha_matches | yes | `f8411ba777122c92aca6dc72ff9cdadfe087ac4222258041269d7c0fe05bbffb` |

## Completion boundary

This guard only prevents wrong-file manual upload risk. The active goal is complete only after a real private score greater than `0.50671` is recorded.
