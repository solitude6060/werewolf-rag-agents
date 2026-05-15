# v1929 Cockpit No-Edit Score Bridge Plan

## 目標

讓 `experiments/final_submission_package/current_upload/ATTEMPT_CARD.md` 的主要 post-score 指令與已驗證的 safest handoff 一致：優先使用 `v1898_current_score_report_bridge.py` no-edit dry-run/confirm，而不是直接要求手打 `v1872 --group --order`。

## 問題

`current_upload/README.md` 已提示 v1898 no-edit path，且 v1928 sandbox 已證明 v1898 confirm 能 record/stage/stop。但 `ATTEMPT_CARD.md` 的「After real score appears」仍以 direct v1872 為主。這不會阻塞，但增加臨場打錯 group/order 的風險。

## 步驟

1. 新增 `v1929_cockpit_noedit_bridge_regression.py`，要求 cockpit no-write/card output 包含 v1898 dry-run 與 confirm commands，且仍保留 v1872 fallback。
2. 先跑 regression，確認現況失敗。
3. 修改 `v1871_final_attempt_cockpit.py` 的 card template。
4. 重建 tracked `current_upload/ATTEMPT_CARD.md`。
5. 執行 v1929/v1928/v1921/v1906 與敏感字串掃描。

## 驗證標準

- v1929 regression `FAILURES=0`。
- ATTEMPT_CARD contains:
  - `python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>`
  - `python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score`
- Direct v1872 remains present only under fallback wording.
- Active upload still `READY_TO_UPLOAD=yes` and goal gate still `GOAL_COMPLETE=no` until external score exists.
