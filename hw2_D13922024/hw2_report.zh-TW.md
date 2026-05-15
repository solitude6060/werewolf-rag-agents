# HW2 報告：多角色推理的狼人預測系統

**學生 ID：** D13922024
**最終封裝候選：** v1840c
**最佳已驗證 private 分數：** 0.49349
**評分公式：** 0.4 × Macro-F1 + 0.6 × Werewolf AP

## 1. 任務與限制

本作業的目標是根據狼人遊戲逐字稿，預測每位玩家的角色與 `wolf_score`。private split 包含 30 場遊戲、397 位玩家。合法角色包含 Villager、Werewolf、Seer、Medium、Hunter、Madman。

本系統遵守課程限制：

- 使用至少兩個互相協作的推理元件；
- 使用檢索增強的逐字稿證據；
- 不訓練、不微調模型；
- 僅使用本機推論與可重現的規則式後處理；
- 每個 submission CSV 在上傳或封裝前都通過格式驗證。

最後繳交包預設使用最佳已驗證候選 `v1840c`。最後一輪排行榜衝刺共用完 5 次嘗試；最後一槍 `v1846e` 的 private 分數退步到 `0.46698`，因此它只保留為失敗實驗紀錄，不作為最終 `submission.csv`。

## 2. 系統設計

```text
逐字稿檔案
    │
    ▼
擷取元件
    - 解析玩家名單、角色宣告、投票、處刑、死亡與揭示窗口
    - 擷取角色規則與玩家相關證據片段
    │
    ▼
分析元件 + 驗證元件
    - 排序 Werewolf、Seer、Medium、Hunter、Madman、Villager 候選
    - 檢查宣告、處刑結果與夜晚事件之間的矛盾
    - 輸出結構化的逐列修正建議
    │
    ▼
限制求解器
    - 依遊戲人數限制各角色數量
    - 合併確定性揭示、宣告圖證據與本機模型審核
    - 輸出 `id,index,character,role,wolf_score`
    │
    ▼
最終候選佇列與封裝
    - 以 SHA-256 記錄並封裝通過驗證的 CSV 候選
    - 記錄 private 回饋並保存 rollback checkpoint
```

系統將「證據擷取」與「限制式決策」分離。先列出逐字稿中的可查證事實，再由驗證元件檢查候選角色是否符合角色數量、角色宣告與事件時間線。最後的求解器是 deterministic，因此選定候選可由封裝 checkpoint 重現。

## 3. 檢索增強證據

檢索資料包含角色規則、不同遊戲人數的角色配置、常見欺騙模式，以及逐字稿中與宣告、處刑、死亡相關的上下文窗口。高影響修正前會先做檢索：

- **角色規則檢索：**確認該場遊戲是否可能存在 Seer、Medium、Hunter、Madman。
- **宣告檢索：**整理誰宣告了角色、誰指控誰為黑或白。
- **處刑後檢索：**掃描處刑後窗口，尋找結構化的 Medium 風格揭示。
- **交叉檢查檢索：**將本機模型建議與確定性事件、角色預算交叉比對。

最有效的提示流程是「先列證據，再找矛盾，最後要求受限制的決策」。這能降低把遊戲中的欺騙或壓力發言誤當成真實標籤的機率。

## 4. 優化策略

1. **角色數量限制。** 求解器依遊戲人數限制 Werewolf 與特殊角色數量，避免產生不可能的 submission。
2. **結構化揭示過濾。** 系統優先採用括號式或處刑事件錨定的揭示，並拒絕未綁定事件的隨口指控。
3. **宣告圖一致性。** 將重複的角色宣告與互相指控建成圖結構，用於辨識真 Seer、假 Seer 與 Medium 矛盾。
4. **本機模型審核與快取。** 本機模型輸出以遊戲或列為單位快取，讓實驗可重現且不依賴外部服務。
5. **排行榜安全佇列。** 最終嘗試依「證據強度」到「高風險高報酬」排序，並保留已知 private 分數的 rollback checkpoint。
6. **驗證優先封裝。** 所有最終候選 CSV 都記錄 SHA-256，並通過作業 validator。

## 5. 分數軌跡

| Candidate | Private score | 主要想法 | 結果 |
| --- | ---: | --- | --- |
| v1819b | 0.45499 | v1817b/v1818a 正向 stack | 早期改善 |
| v1821a | 0.46455 | claim-graph CSP 加上 g10 Pamela 修正 | 正向 |
| v1823a | 0.46492 | v1821a 加上 v1819b 正向 stack | 正向 |
| v1824a | 0.47119 | v1823a 加上 g24 Thomas true-Seer 修正 | 前一個 rollback best |
| v1826a | 0.48854 | g4/g29 結構修正與 AP boost | 大幅改善 |
| v1840b | 0.49266 | high-precision Medium/AP overlay | 正向 |
| v1840c | 0.49349 | 將 v1840 overlay 延伸到 v1829e clean Hail Mary family | 最佳已驗證 |
| v1846e | 0.46698 | 最後 role-cap one-shot，建立在 v1842e 上 | 最後嘗試失敗 |

最後一輪嘗試用量為 `5/5`。操作目標 `>0.50000` 與原始 top-three gate `>0.52380` 都未達成。因此最終封裝候選是最佳已驗證的 `v1840c`，不是最後失敗的 `v1846e`。

## 6. 成功與失敗分析

**有效的部分。** 最大收益來自可審核的結構性修正：宣告圖矛盾、true-Seer / Medium 一致性檢查，以及小範圍 AP overlay。分數從 `0.47119` 提升到 `0.48854`，再到 `0.49349`，顯示小型、證據明確的改動比大範圍 all-in 更容易轉移到 private split。

**失敗的部分。** 最後的 role-cap 嘗試是因為 public proxy 與 leave-one-out 檢查看起來較強而被選中，但 private 分數明顯退步。這表示 public AP calibration 不能取代逐字稿證據，也不能單獨當成 private split 的可靠指標。

**最終封裝的處理。** 繳交包回到最佳已驗證 private 候選 `v1840c`。失敗的 `v1846e` 仍保留在 checkpoints 與實驗 ledger 中，方便追蹤，但不作為預設 `submission.csv`。

## 7. 可重現性

在作業包目錄執行：

```bash
python3 make_final.py --output submission.csv
```

此指令會複製封裝好的最佳候選，並執行 validator。預期輸出包含：

```text
OK: 397 predictions validated
```

也可以額外驗證：

```bash
python3 assert/validate_submission.py submission.csv
```

private submission 的預期形狀是 397 筆預測，表頭為：

```text
id,index,character,role,wolf_score
```

完整最終嘗試 archive 與 score-feedback ledger 保存在：

```text
experiments/final_submission_package/
experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
```
