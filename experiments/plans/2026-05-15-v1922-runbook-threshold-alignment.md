# v1922 Runbook Threshold Alignment Plan

## 目標

修正 post-score 交接路徑中 `v1866_final_attempt_runbook.py` 仍輸出舊 top-3 threshold `0.50671` 的風險，使所有使用者可見的上傳/下一輪 runbook 都一致使用最新完成門檻：真實 private score 必須 `>0.52380`。

## 問題

稽核 `v1872_post_score_command_center.py` 的 confirm flow 時確認：若分數未達 top-3，command center 會呼叫 `v1866_final_attempt_runbook.py --from-records` 印出下一輪 `NEXT_UPLOAD_RUNBOOK`。目前 `v1866` 內的 `TOP3` 常數仍是 `0.50671`，可能在下一輪交接中誤導 stop condition。

## 限制

- 不寫入真實 score records，不消耗外部提交機會。
- 不重新產生 current upload。
- 修復範圍限制於 stale threshold 與其 regression/report。

## TDD 步驟

1. 新增 `experiments/scripts/v1922_runbook_threshold_regression.py`，執行 `v1866_final_attempt_runbook.py --group queue --order 1 --skip-validation`，要求 stdout 包含 `STOP_IF_SCORE_GREATER_THAN=0.52380` 且不包含 `0.50671`。
2. 先執行 regression，確認目前失敗。
3. 修正 `v1866_final_attempt_runbook.py` 的 `TOP3` 為 `0.52380`。
4. 重新執行 regression 與相關 post-score boundary/console checks。

## 驗證標準

- v1922 regression `FAILURES=0`。
- `v1866_final_attempt_runbook.py --group queue --order 1 --skip-validation` 輸出 `STOP_IF_SCORE_GREATER_THAN=0.52380`。
- v1919 v1826a boundary regression 仍通過。
- v1898 / v1895 score bridge regressions 仍通過。
- v1921 upload-now console 仍顯示 current upload ready。
- 敏感署名字串掃描無命中。

## 停止條件

- stale threshold 被 regression 鎖住且 commit。
- goal 仍不得 complete，除非後續真實 private score `>0.52380` 被 records-backed gate 驗證。

## Rollback

若此修復造成 runbook regression 之外的路由錯誤，回退 `v1866` 常數修改與 v1922 artifacts，並改由單一 shared threshold source 另行處理。
