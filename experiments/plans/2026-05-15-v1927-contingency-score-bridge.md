# v1927 Contingency Score Bridge Plan

## 目標

修復一個 post-score chain blocker：當 `v1826a` 的真實分數低於 `0.47200` 時，router 會 stage `contingency` 候選（例如 `v1825c`）。下一次上傳該 contingency 檔後，current score bridge 仍必須能記錄/乾跑該候選的分數，而不能因 `v1836_score_feedback_router.py --group` choices 不接受 `contingency` 而失敗。

## 風險

目前 `v1836` parser choices 缺少 manifest 中的若干非 queue group。`route_next()` 已有 `group != "queue"` 的 manual review fallback，但 argparse 會先拒絕未知 group，使 fallback 無法生效。

## TDD 步驟

1. 新增 `experiments/scripts/v1927_contingency_score_bridge_regression.py`：
   - 在 `/tmp` 複製 scripts/final_submission_package/validator fixture。
   - sandbox confirm `queue#1/v1826a` score `0.47150`，期待 stage `contingency#1/v1825c`。
   - sandbox run `v1898_current_score_report_bridge.py --score 0.47000` dry-run，期待成功且輸出 `candidate=v1825c`、`recommended_next=MANUAL_REVIEW...`。
   - 驗證真實 repo records/current_upload 未變。
2. 先跑 regression，確認目前失敗。
3. 修 `v1836_score_feedback_router.py`，讓 parser 接受 manifest 內會被 stage/record 的 non-primary groups。
4. 重跑 v1927 與既有 v1919/v1923/v1898/v1921/v1906。

## 驗證標準

- v1927 regression `FAILURES=0` 且 `REAL_REPO_UNCHANGED=yes`。
- v1919 boundary regression 仍 `FAILURES=0`。
- v1923 confirmed staging sandbox 仍 `FAILURES=0`。
- v1898 current score bridge regression 仍 `FAILURES=0`。
- Current upload console 仍 `READY_TO_UPLOAD=yes`。
- Completion gate 仍 `GOAL_COMPLETE=no`，直到真實 score `>0.52380`。

## 停止條件

Post-score chain 在 low-score contingency 分支不再卡死；active goal 仍等待外部上傳分數。
