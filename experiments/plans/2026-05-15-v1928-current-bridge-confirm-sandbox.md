# v1928 Current Bridge Confirm Sandbox Plan

## 目標

補齊實際交接命令的 confirmed path 驗證：使用者回報 score 後，文件建議執行的是：

```bash
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE>
python3 experiments/scripts/v1898_current_score_report_bridge.py --score <REAL_SCORE> --confirm-real-score
```

既有 v1923 已驗證 direct `v1872_post_score_command_center.py --confirm-real-score` 會 record/stage，但還未直接驗證 `v1898 --confirm-real-score` wrapper 本身。v1928 要在 `/tmp` sandbox 中驗證此 no-edit bridge command。

## 範圍

- Scenario A：current `v1826a` score `0.50000` confirm through v1898，應記錄 `v1826a` 並 stage `v1826b`。
- Scenario B：current `v1826a` score `0.52381` confirm through v1898，應記錄 top3 hit，且不 stage 下一張。
- 真實 repo 的 score ledger/current upload 不得改變。

## 驗證標準

- v1928 regression `FAILURES=0`。
- `REAL_REPO_UNCHANGED=yes`。
- continue path：records +1、latest candidate `v1826a`、metadata candidate `v1826b`、upload SHA = v1826b manifest SHA。
- top3 path：records +1、latest top3_hit yes、metadata/current upload 仍 v1826a。
- active goal 仍由 real official ledger 判斷；sandbox 不可導致 completion。

## 停止條件

使用者實際 score confirm command 已由 sandbox 覆蓋；若沒有真實 private score `>0.52380`，goal 繼續 active。
