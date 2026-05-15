# v1921 Upload Now Console Plan

## 目標

建立一個預設不改檔的最後上傳指令，讓使用者在剩餘提交機會前可以直接取得：

- 應上傳的 canonical path。
- 安全 aliases 與不能上傳的 `submission.csv` lookalikes。
- current candidate / group / order / rows / SHA-256。
- 目前 top-3 完成門檻與 records-backed goal 狀態。
- 上傳後回報真實 private score 的下一步命令。

## 限制

- 不把 goal 標記完成；目前缺少真實 private score `>0.52380`。
- 預設 stdout-only，不更新既有 preflight/report timestamp，避免造成追蹤檔案 churn。
- 不重新產生 submission；只讀 current upload、metadata、score ledger 與檔案系統 lookalikes。
- 延續 v1902 alias guard 的判定邏輯，避免與既有 guard 分歧。

## 步驟

1. 新增 `experiments/scripts/v1921_upload_now_console.py`。
2. 新增 regression `experiments/scripts/v1921_upload_now_console_regression.py`，覆蓋 stdout-only、canonical/alias/lookalike、門檻與 post-score command。
3. 產出靜態報告 `experiments/reports/v1921_upload_now_console.md`，記錄最新使用方式與驗證證據。
4. 執行 validator、v1902 alias guard、v1921 regression、v1921 command、敏感字串 grep。

## 驗證標準

- `v1921_upload_now_console.py` 預設不寫入任何 report 檔案。
- stdout 顯示 `READY_TO_UPLOAD=yes`、canonical upload path、3 個 safe aliases、至少 2 個 do-not-upload lookalikes。
- stdout 顯示 `STOP_IF_SCORE_GREATER_THAN=0.52380`、`GOAL_COMPLETE_BY_RECORDS=no`、`BEST_SCORE=0.42894`。
- regression return code 0。
- current upload validator 仍通過 397 rows。
- 敏感署名字串掃描不含共同作者或工具署名類字眼。

## 停止條件

- 完成 v1921 指令、驗證、報告與 commit；回報使用者目前唯一建議上傳 path。
- 若 regression 或 validator 失敗，停止並修復，不建議上傳。

## 風險與 rollback

- 風險：複製 v1902 判定邏輯可能分歧；改以 import v1902 helpers 降低分歧。
- Rollback：刪除 v1921 script/regression/report/plan，不影響 current upload bytes。
