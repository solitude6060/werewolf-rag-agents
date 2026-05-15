# v1927 Contingency Score Bridge Regression

## Summary

- Failures: `0`
- Real repo unchanged: `yes`
- Staged sandbox candidate after low v1826a score: `contingency#v1825c`
- Bridge exit code: `0`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| stage_exit_zero | yes | `exit=0` |
| stage_recommends_contingency | yes | `v1825c recommendation` |
| metadata_group_contingency | yes | `contingency` |
| metadata_candidate_v1825c | yes | `v1825c` |
| bridge_exit_zero | yes | `exit=0; CURRENT_SCORE_REPORT_BRIDGE\nTEMPLATE=experiments/final_submission_package/current_upload/SCORE_REPORT.txt\nSCORE=0.47000\nWRITE_MODE=dry_run\nBRIDGE_EXIT_CODE=0\nFILLED_REPORT_PERSISTED=no\nREPORT=experiments/reports/v1898_current_score_report_bridge.md\nJSON=experiments/reports/v1898_current_score_report_bridge.json\nBRIDGE_OUTPUT_BEGIN\nSCORE_REPORT_COMMAND_CENTER\nINTAKE_READY=yes\nSCORE=0.47000\nSCORE_STATUS=continue_routing_required\nWRITE_MODE=dry_run\nCOMMAND_CENTER_EXIT_CODE=0\nOFFICIAL_RECORDS_MUTATE` |
| bridge_routes_manual_review | yes | `manual review fallback` |
| bridge_candidate_v1825c | yes | `candidate=v1825c` |
| official_repo_unchanged | yes | `before={'records_sha': 'fc7c1f781c557e8a4b9fede40344dfaf7dfabe09f115a1fdef8b9c9f92053590', 'upload_sha': 'e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad'}; after={'records_sha': 'fc7c1f781c557e8a4b9fede40344dfaf7dfabe09f115a1fdef8b9c9f92053590', 'upload_sha': 'e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad'}` |
| sandbox_latest_is_v1826a | yes | `candidate=v1826a score=0.47150 next=experiments/final_submission_package/contingency/01_v1825c_diagnostic_neutral_private.csv` |

## Bridge output excerpt

```text
CURRENT_SCORE_REPORT_BRIDGE
TEMPLATE=experiments/final_submission_package/current_upload/SCORE_REPORT.txt
SCORE=0.47000
WRITE_MODE=dry_run
BRIDGE_EXIT_CODE=0
FILLED_REPORT_PERSISTED=no
REPORT=experiments/reports/v1898_current_score_report_bridge.md
JSON=experiments/reports/v1898_current_score_report_bridge.json
BRIDGE_OUTPUT_BEGIN
SCORE_REPORT_COMMAND_CENTER
INTAKE_READY=yes
SCORE=0.47000
SCORE_STATUS=continue_routing_required
WRITE_MODE=dry_run
COMMAND_CENTER_EXIT_CODE=0
OFFICIAL_RECORDS_MUTATED=no
REPORT=<TEMP_SCORE_REPORT_DIR>/v1895_bridge.md
JSON=<TEMP_SCORE_REPORT_DIR>/v1895_bridge.json
BRIDGE_OUTPUT_END
# v1898 Current Score Report Bridge

Generated UTC: `<UTC_TIMESTAMP>`

## Summary

- Template: `experiments/final_submission_package/current_upload/SCORE_REPORT.txt`
- Score: `0.47000`
- Write mode: `dry_run`
- Synthetic dry-run score only: `yes`
- Bridge exit code: `0`
- Filled report persisted: `no`

## Bridge command

```bash
/usr/bin/python3 experiments/scripts/v1895_score_report_command_center.py <TEMP_SCORE_REPORT_DIR>/SCORE_REPORT.txt --out-json <TEMP_SCORE_REPORT_DIR>/v1895_bridge.json --out-md <TEMP_SCORE_REPORT_DIR>/v1895_bridge.md
```

## Bridge output

```text
SCORE_REPORT_COMMAND_CENTER
INTAKE_READY=yes
SCORE=0.47000
SCORE_STATUS=continue_routing_required
WRITE_MODE=dry_run
COMMAND_CENTER_EXIT_CODE=0
OFFICIAL_RECORDS_MUTATED=no
REPORT=<TEMP_SCORE_REPORT_DIR>/v1895_bridge.md
JSON=<TEMP_SCORE_REPORT_DIR>/v1895_bridge.json
```

## v1895 report

# v1895 Score Report Command Center

Generated UTC: `<UTC_TIMESTAMP>`

## Summary

- Intake ready: `yes`
- Score: `0.47000`
- Score status: `continue_routing_required`
- Write mode: `dry_run`
- Command-center exit code: `0`
- Official records mutated: `no`

## Command

```bash
/usr/bin/python3 experiments/scripts/v1872_post_score_command_center.py --score 0.47000
```

## Command-center output

```text
UPLOAD_CONTEXT
group=contingency
order=1
source=experiments/final_submission_package/current_upload/metadata.js
```

## Completion boundary

This regression proves the contingency score bridge path only. The active goal remains incomplete until a real private score greater than `0.52380` is recorded.
