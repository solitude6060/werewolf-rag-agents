# v1924 Package Current Submit Sync Plan

## 目標

修正 `hw2_D13922024/` hand-in package 的一鍵輸出，使：

```bash
python3 hw2_D13922024/make_final.py --output <path>
```

產生的 CSV 與目前 canonical upload `experiments/final_submission_package/current_upload/submission.csv` byte-equal，而不是舊的 v1856g checkpoint。

## 問題

稽核發現：

- `hw2_D13922024/submission.csv` 已是 current v1826a SHA `e4b44b76...`。
- `make_final.py` 的 `FINAL_CHECKPOINT` 仍指向 `final_v1856g_private.csv`，實際產出 SHA `468ecff3...`。
- `README.md` 仍寫 candidate=`v1856g` 與舊門檻 `>0.50671`。

這會讓使用者依文件一鍵重建時得到錯誤 submit。

## TDD 步驟

1. 新增 `experiments/scripts/v1924_package_current_submit_regression.py`：
   - 讀 canonical current upload SHA。
   - 跑 `make_final.py --output /tmp/...csv`。
   - 要求輸出 SHA 等於 canonical、等於 package `submission.csv`、validator OK。
   - 要求 README 不含舊 cutoff / 舊 default candidate 字串。
2. 先執行 regression，確認目前失敗。
3. 修 `make_final.py` 指向 `final_current_private.csv` 並更新 help text。
4. 修 `README.md` 的 byte-equal checkpoint、candidate lineage、threshold、layout、completion boundary。
5. 重跑 regression 與 final upload guards。

## 驗證標準

- v1924 regression `FAILURES=0`。
- package-local command from `hw2_D13922024/` can rebuild `submission.csv` byte-equal to canonical current upload.
- current upload validator `OK: 397 predictions validated`。
- 敏感署名字串掃描無命中。

## 停止條件

- hand-in package 一鍵重建與文件都同步到 current v1826a。
- Active score goal 仍只可在真實 private score `>0.52380` 後 complete。
