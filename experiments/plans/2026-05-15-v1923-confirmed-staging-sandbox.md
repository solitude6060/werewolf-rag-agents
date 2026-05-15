# v1923 Confirmed Staging Sandbox Plan

## 目標

補上目前缺少的整合回歸：在不污染真實 repo score ledger/current upload 的前提下，模擬 `queue#1` / `v1826a` 回報真實分數後，`v1872_post_score_command_center.py --confirm-real-score` 是否真的會：

1. 寫入 score-feedback record。
2. 將 router 推薦的下一張 CSV staging 到 `current_upload/submission.csv`。
3. 更新 metadata 與人工上傳 aliases。
4. 若 score `>0.52380`，停止而不 staging 下一張。

## 限制

- 所有 confirm mutation 必須發生在 `/tmp` sandbox copy 內。
- 真實 repo 的 `v1836_score_feedback_records.csv` 與 `current_upload/submission.csv` SHA/count 不得改變。
- 不呼叫外部 API、不上傳。

## 方法

新增 `experiments/scripts/v1923_confirmed_staging_sandbox_regression.py`：

- 複製 `experiments/scripts`、`experiments/final_submission_package`、`werewolf-project/assert` 到 temp cwd。
- Scenario A：以 `0.50000` confirm `queue#1/v1826a`，期待 record count +1，latest candidate=`v1826a`，recommended next=`queue/02_v1826b...`，sandbox current upload metadata candidate=`v1826b`，canonical + aliases SHA 均等於 v1826b manifest SHA。
- Scenario B：以 `0.52381` confirm `queue#1/v1826a`，期待 top3 hit、output `STOP_STATUS=top3_hit_no_next_stage`，sandbox current upload 保持 v1826a SHA。
- 檢查真實 repo records/current upload 未變。

## 驗證標準

- v1923 regression `FAILURES=0`。
- v1922 runbook threshold regression 仍為 `FAILURES=0`。
- v1919 boundary regression 仍為 `FAILURES=0`。
- v1921 upload-now console 仍 `READY_TO_UPLOAD=yes`。
- 敏感署名字串掃描無命中。

## 停止條件

- 交接流程「dry-run boundary + confirmed staging」都有 regression artifact。
- active goal 仍等待真實 private score；不得因 sandbox simulation 而 complete。
