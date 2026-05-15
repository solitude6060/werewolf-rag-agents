# v1925 Active Handoff Threshold Guard

Generated UTC: `2026-05-15T01:33:29+00:00`

## Summary

- Ready: `yes`
- Live threshold: `>0.52380`
- Stale threshold rejected: `0.50671`
- Files scanned: `25`
- Failures: `0`

## Matrix

| Path | Stale hits | Live hits | Status | Detail |
| --- | ---: | ---: | --- | --- |
| `experiments/final_submission_package/current_upload/ATTEMPT_CARD.md` | `0` | `4` | `pass` | `ok` |
| `experiments/final_submission_package/current_upload/README.md` | `0` | `1` | `pass` | `ok` |
| `experiments/final_submission_package/current_upload/SCORE_REPORT.txt` | `0` | `0` | `pass` | `ok` |
| `experiments/final_submission_package/current_upload/metadata.json` | `0` | `1` | `pass` | `ok` |
| `experiments/final_submission_package/current_upload/submission.csv` | `0` | `0` | `pass` | `ok` |
| `hw2_D13922024/README.md` | `0` | `2` | `pass` | `ok` |
| `hw2_D13922024/make_final.py` | `0` | `0` | `pass` | `ok` |
| `hw2_D13922024/hw2_report.md` | `0` | `0` | `pass` | `ok` |
| `experiments/scripts/v1866_final_attempt_runbook.py` | `0` | `1` | `pass` | `ok` |
| `experiments/scripts/v1836_score_feedback_router.py` | `0` | `1` | `pass` | `ok` |
| `experiments/scripts/v1870_stage_current_upload.py` | `0` | `1` | `pass` | `ok` |
| `experiments/scripts/v1871_final_attempt_cockpit.py` | `0` | `1` | `pass` | `ok` |
| `experiments/scripts/v1872_post_score_command_center.py` | `0` | `1` | `pass` | `ok` |
| `experiments/scripts/v1883_pre_upload_guard.py` | `0` | `2` | `pass` | `ok` |
| `experiments/scripts/v1888_final_upload_preflight.py` | `0` | `2` | `pass` | `ok` |
| `experiments/scripts/v1893_score_report_template.py` | `0` | `2` | `pass` | `ok` |
| `experiments/scripts/v1894_score_report_intake.py` | `0` | `2` | `pass` | `ok` |
| `experiments/scripts/v1895_score_report_command_center.py` | `0` | `1` | `pass` | `ok` |
| `experiments/scripts/v1898_current_score_report_bridge.py` | `0` | `1` | `pass` | `ok` |
| `experiments/scripts/v1900_current_upload_score_report_guard.py` | `0` | `1` | `pass` | `ok` |
| `experiments/scripts/v1902_upload_alias_guard.py` | `0` | `1` | `pass` | `ok` |
| `experiments/scripts/v1904_attempt_state_guard.py` | `0` | `1` | `pass` | `ok` |
| `experiments/scripts/v1906_goal_completion_gate.py` | `0` | `1` | `pass` | `ok` |
| `experiments/scripts/v1908_final_goal_status.py` | `0` | `0` | `pass` | `ok` |
| `experiments/scripts/v1921_upload_now_console.py` | `0` | `0` | `pass` | `ok` |

## Completion boundary

This guard verifies active handoff wording only. The active goal is complete only after a real private score greater than `0.52380` is recorded.
