# worker-3：current status stale package gap lane

日期：2026-05-11
任務：比較最新 hand-over / Round 16 狀態與 `hw2_D13922024/` hand-in package 內容，判定 stale/gap 與後續修包前需要驗證的事項。
限制：本 lane 僅產出 audit note；**未修改 hand-in package、未上傳、未建立新的 submission CSV**。

## 結論摘要

- **最新已驗證最佳**：`v1730 = 0.44384`（Kaggle private），比 `v1121 = 0.44352` 高 `+0.00032`。
- **目前 hand-in package (`hw2_D13922024/`) 仍是 stale v1121 package**：README、report、`make_final.py` 與 `submission.csv` 均指向 / 產生 v1121，而非 v1730。
- **gap 分類**：
  1. **文檔 stale**：package README / report 的分數與版本仍寫 v1121 / 0.44352。
  2. **reproducer stale**：`make_final.py` docstring、CLI description、stage5 function 仍是 v1121 logic。
  3. **artifact stale**：`hw2_D13922024/submission.csv` 與 v1730 差 5 rows；雖格式合法，但不是 current best。
  4. **reproducibility risk**：若日後直接交 `hw2_D13922024/`，可重現的是 v1121，而不是最新 hand-over 要求的 v1730。

## 證據

### A. 最新狀態來源：hand-over / Round 16

- `hand-over.md:4`：標示「當前已驗證最佳：v1730 = 0.44384 (Kaggle private)」。
- `hand-over.md:8`：最佳變遷列出 `v1121 (0.44352) → v1730 (0.44384)`。
- `hand-over.md:13`：`v1730 stack` 為 `0.44384 (+0.00032)`，註記為當前最佳。
- `experiments/plans/round16_FINAL_SUMMARY.md:5`：`v1730 = 0.44384 (+0.00032 over v1121, rank 6)`，Kaggle private verified。
- `experiments/plans/round16_FINAL_SUMMARY.md:15-22`：timeline 將 baseline `v1121 = 0.44352` 與 final stack `v1730 = 0.44384` 並列。
- `experiments/plans/round16_FINAL_SUMMARY.md:103-104`：submissions 區塊明確說 `v1730_kaggle_validated_stack` 是 current best，並要求 final report 使用。
- `experiments/plans/round16_FINAL_SUMMARY.md:122-133`：final-submission package status 指出 `hw2_D13922024/main.py + make_final.py` 應更新到可 byte-equal reproduce v1730，包含 5 個 row patches，並要求 validator 回報 `OK: 397 predictions validated`。

### B. hand-in package 現況：仍宣稱 v1121 / 0.44352

- `hw2_D13922024/README.md:4`：`Verified Kaggle private score: 0.44352`。
- `hw2_D13922024/README.md:45`：pipeline 圖示寫 `produces v1121 = final submission`。
- `hw2_D13922024/README.md:67`：`submission.csv = v1121, the file to upload to Kaggle`。
- `hw2_D13922024/README.md:118`：table 仍列 `v1121 ... 0.44352`。
- `hw2_D13922024/hw2_report.md:4`：report 標示 verified private score `0.44352`。
- `hw2_D13922024/hw2_report.md:45`：pipeline 圖示寫 `produces v1121 (private 0.44352, FINAL)`。
- `hw2_D13922024/hw2_report.md:176`：final row 仍是 `v1121 (final) ... 0.44352`。
- `hw2_D13922024/make_final.py:2`：docstring 寫 `Reproduce final v1121 submission (Kaggle private 0.44352)`。
- `hw2_D13922024/make_final.py:96`：核心函式仍名為 `stage5_apply_v1121`。
- `hw2_D13922024/make_final.py:120`：CLI description 仍是 `Build final v1121 submission.`。

### C. artifact 差異：package CSV 合法但不是 v1730

本 lane 僅讀取與比對；未寫入或生成 CSV。驗證結果：

```text
python3 hw2_D13922024/assert/validate_submission.py hw2_D13922024/submission.csv
→ OK: 397 predictions validated

python3 hw2_D13922024/assert/validate_submission.py experiments/submissions/submission_v1730_kaggle_validated_stack_private.csv
→ OK: 397 predictions validated
```

`hw2_D13922024/submission.csv` 與 `experiments/submissions/submission_v1730_kaggle_validated_stack_private.csv` 皆為 397 predictions，但有 5 rows 差異：

| id | character | package v1121 wolf_score | v1730 wolf_score | 分類 |
|---:|---|---:|---:|---|
| 275 | Father Jimzon | 0.5 | 0.7 | missing v1610 patch |
| 290 | Shepherd Katharina | 0.5 | 0.7 | missing v1610 patch |
| 328 | Shepherd Katharina | 0.5 | 0.7 | missing v1610 patch |
| 351 | Baker Otto | 0.05 | 0.001 | missing v1605 patch |
| 373 | Young Man Joachim | 0.5 | 0.7 | missing v1610 patch |

這 5 rows 正好對應 `round16_FINAL_SUMMARY.md:125-130` 的 v1730 patch list。

## stale / gap 分類

| 類別 | 嚴重度 | 判定 | 影響 |
|---|---|---|---|
| 文檔 stale | 高 | README / report 仍宣稱 v1121 / 0.44352 / FINAL | final report 若照 package 提交會與 hand-over 最新狀態矛盾 |
| reproducer stale | 高 | `make_final.py` 仍產生 v1121 stage5 corrections | 無法由 package 重現 v1730；reproducibility claim 不成立 |
| artifact stale | 高 | `submission.csv` 缺 v1730 5-row patch | 若直接上傳 package CSV，會回到 v1121 best 而非 current best |
| audit trail gap | 中 | hand-over 最新頂部已更新，但 package 尚未同步 | 後續修包需明確記錄 v1121→v1730 的 patch provenance |
| no-upload / no-new-CSV constraint | 高 | 本 task 明確禁止新 submission CSV / upload | 修包前只能記錄差異與驗證需求，不能在此 lane 產生 replacement CSV |

## 後續修包前必要驗證

若 leader 後續開修包 lane，建議在不違反 no-upload/no-new-CSV 前提下先完成以下檢查：

1. **patch provenance**：確認 v1730 CSV 是由 `v1605 + v1610` disjoint positive stack 組成，且 5 rows 與 Round 16 summary 一致。
2. **byte-equal target**：修包後的 `make_final.py --split private --output <temp>` 必須與既有 `experiments/submissions/submission_v1730_kaggle_validated_stack_private.csv` byte-equal；若仍禁止新 CSV，改以 dry-run / in-memory compare 或 leader 指定的 temp path 執行。
3. **format validator**：修包後目標檔需通過 `python3 hw2_D13922024/assert/validate_submission.py <candidate>` → `OK: 397 predictions validated`。
4. **documentation sync**：README、report、pipeline diagram、score table、reproducer comments 必須一致更新為 v1730 / 0.44384，並保留 v1121 作 baseline history 而非 FINAL。
5. **no-upload gate**：任何 Kaggle upload 都必須由 leader / user 另行授權；本 audit lane 不構成 upload approval。

## no-upload / no-new-CSV implication

- 本次只新增 audit note：`experiments/plans/research-audit-2026-05-11/worker-3-status-stale-package-gap.md`。
- 未執行 `make_final.py --output submission.csv`，未覆寫 `hw2_D13922024/submission.csv`，未在 `hw2_D13922024/` 內新增檔案。
- 未建立新的 submission CSV；比對使用既有 `hw2_D13922024/submission.csv` 與既有 `experiments/submissions/submission_v1730_kaggle_validated_stack_private.csv`。
- 未進行 Kaggle upload。

## 本 lane 驗證紀錄

- `grep -RInE 'v1730|0\.44352|v1121|submission|reproduc' ...`：確認 hand-over / Round 16 指向 v1730，package 指向 v1121。
- `python3 hw2_D13922024/assert/validate_submission.py hw2_D13922024/submission.csv`：PASS，`OK: 397 predictions validated`。
- `python3 hw2_D13922024/assert/validate_submission.py experiments/submissions/submission_v1730_kaggle_validated_stack_private.csv`：PASS，`OK: 397 predictions validated`。
- Python in-memory CSV compare：PASS，確認 row count `397/397`，diff count `5`，差異 rows 為 275 / 290 / 328 / 351 / 373。
- Scope check：PASS，hand-in package 未修改；未建立 submission CSV。
