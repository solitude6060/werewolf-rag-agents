# v1925 Active Handoff Threshold Guard Plan

## 目標

新增一個 active handoff guard，防止目前真正會被使用的上傳、交接、package 文件與 post-score scripts 再出現舊 top-3 cutoff `0.50671`。目前 live cutoff 是 `0.52380`，完成條件是 real private score 嚴格大於該值。

## 範圍

掃描 active surfaces：

- `experiments/final_submission_package/current_upload/`
- `hw2_D13922024/README.md`
- `hw2_D13922024/make_final.py`
- `hw2_D13922024/hw2_report.md`
- post-score / preflight / completion scripts：`v1866`, `v1870`, `v1871`, `v1872`, `v1883`, `v1888`, `v1893`, `v1894`, `v1895`, `v1898`, `v1900`, `v1902`, `v1904`, `v1906`, `v1908`, `v1921`

不掃歷史研究報告與舊候選產生器，避免把舊上下文當作 active blocker。

## TDD 步驟

1. 新增 `v1925_active_handoff_threshold_guard.py`，支援 default active paths 與 `--path` override。
2. 新增 `v1925_active_handoff_threshold_guard_regression.py`：
   - temp stale file 含 `0.50671` 時 guard 必須 nonzero。
   - temp live file 含 `0.52380` 且無 stale 時 guard 必須 zero。
   - real active paths guard 必須 zero。
3. 執行 guard 與既有 v1921/v1922/v1924 checks。

## 驗證標準

- v1925 regression `FAILURES=0`。
- default guard `ACTIVE_HANDOFF_THRESHOLD_READY=yes`。
- current upload console 仍 `READY_TO_UPLOAD=yes`。
- package current submit regression 仍 `FAILURES=0`。
- completion gate 仍 `GOAL_COMPLETE=no`, `BEST_SCORE=0.42894`, `TOP3_THRESHOLD=0.52380`。

## 停止條件

Active handoff surfaces 已有 guard 防 stale cutoff；外部 blocker 仍是缺少真實 private score `>0.52380`。
