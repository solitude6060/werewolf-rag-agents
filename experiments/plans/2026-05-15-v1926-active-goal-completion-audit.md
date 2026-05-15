# v1926 Active Goal Completion Audit Plan

## 目標

依最新實際狀態重新稽核 active leaderboard goal 是否可完成。成功條件不是本地 readiness，而是：真實 private leaderboard score 已記錄，且分數嚴格大於目前 top-3 cutoff `0.52380`。

## 稽核範圍

- Score ledger：`experiments/final_submission_package/manifests/v1836_score_feedback_records.csv`
- Completion gate：`experiments/scripts/v1906_goal_completion_gate.py`
- Current upload：`experiments/final_submission_package/current_upload/submission.csv`
- Upload console：`experiments/scripts/v1921_upload_now_console.py`
- Active threshold guard：`experiments/scripts/v1925_active_handoff_threshold_guard.py`
- Package reproduction：`experiments/scripts/v1924_package_current_submit_regression.py`
- Validator：`werewolf-project/assert/validate_submission.py`

## 驗證標準

- 如果 `GOAL_COMPLETE=yes` 且 best score `>0.52380`，才允許後續 final audit / `update_goal`。
- 如果 best score 缺失或 `<=0.52380`，明確記錄 `NOT COMPLETE`。
- Readiness gates 可作為上傳準備證據，但不可當成 goal 完成證據。

## 停止條件

- 產出 `experiments/reports/v1926_active_goal_completion_audit.md`。
- 若仍缺外部真實 score，維持 goal active，等待使用者回報上傳結果。
