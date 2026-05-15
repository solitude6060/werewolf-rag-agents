# v1929 Cockpit No-Edit Bridge Regression

## Summary

- Failures: `0`

## Checks

| Check | OK | Detail |
| --- | --- | --- |
| cockpit_no_write_exit_zero | yes | `exit=0` |
| no_write_output_has_v1898_dry | yes | `python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>` |
| no_write_output_has_v1898_confirm | yes | `python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score` |
| no_write_output_keeps_v1872_fallback | yes | `python3 experiments/scripts/v1872_post_score_command_center.py --group queue --order 2 --score <REAL_SCORE> --confirm-real-score` |
| tracked_card_has_v1898_dry | yes | `python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>` |
| tracked_card_has_v1898_confirm | yes | `python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score` |
| tracked_card_keeps_v1872_fallback | yes | `python3 experiments/scripts/v1872_post_score_command_center.py --group queue --order 2 --score <REAL_SCORE> --confirm-real-score` |
| card_mentions_completion_boundary | yes | `completion boundary` |

## Completion boundary

This regression verifies cockpit handoff wording only. The active goal is complete only after a real private score greater than `0.52380` is recorded.
