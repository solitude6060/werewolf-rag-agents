# Worker-3 狀態更新：handover/round16 與 hand-in 套件版本差異（v1730 vs v1121）

## 1. 事實證據（文件截圖式）

### A. hand-in 套件仍停留在 v1121 版本
- `/home/ma/Research/PhD/course/114_2/AI/hw2/hw2_D13922024/README.md:4` 記載：`Verified Kaggle private score: 0.44352`。
- `/home/ma/Research/PhD/course/114_2/AI/hw2/hw2_D13922024/README.md:45`、`:67`、`:118` 明確標示最終為 **v1121**。
- `/home/ma/Research/PhD/course/114_2/AI/hw2/hw2_D13922024/hw2_report.md:4`、`:45`、`:176` 也重複 `0.44352`、`v1121`。
- `/home/ma/Research/PhD/course/114_2/AI/hw2/hw2_D13922024/make_final.py:2-3,37-40,96-100,120-124,137-142`：腳本 docstring、常數與流程明確回復 **v1121**，且預設採 `--from-checkpoint v851`。
- `submission.csv`（`/home/ma/Research/PhD/course/114_2/AI/hw2/hw2_D13922024/submission.csv`）內容為 397 筆最終輸出，未附帶版本欄位；其內容對照 `make_final.py` 的 v1121 修正行為（9 筆）一致（例如 08/ Pamela、10/ Joachim 等行）

### B. 研究進度文件顯示已達到 v1730（新現況）
- `/home/ma/Research/PhD/course/114_2/AI/hw2/hand-over.md:4`：直接宣告「當前已驗證最佳：v1730 = 0.44384」並保留 v1121 → v1730 歷程。
- `/home/ma/Research/PhD/course/114_2/AI/hw2/hand-over.md:8,10-14`：在歷史與 Round16 區段標註 v1730 為 current best。
- `/home/ma/Research/PhD/course/114_2/AI/hw2/experiments/plans/round16_FINAL_SUMMARY.md:5-6,22,112-130,124-131`：明示 round16 最終驗證為 `v1730 = 0.44384`，並列出應新增到 hw2 package 的 5 點補丁（g21/22/26/29、g27）。

## 2. stale / gap 分類

### Stale（明確已過時）
1. **版本與成績描述陳舊**：手工提交包 (`README.md`, `hw2_report.md`, `make_final.py`) 仍宣告並復現 v1121/0.44352，未更新到實際最新驗證值。
2. **流程未同步到新最優**：round16 已明示需更新 `hw2_D13922024/main.py` 與 `make_final.py` 以復現 v1730 byte-equal，但現有文件未對齊（`make_final.py` 尚以 v1121 常數為核心）。
3. **no-upload/no-new-CSV 規範衝突風險**：在無新建 CSV 的前提下，現有包仍需修正 pipeline 邏輯才能產出 v1730；否則只能上傳 v1121 但不應被視為當前最佳。

### Gap（可修復差距）
1. **補丁未落地**：尚無可直接生產 v1730 的手工包產物（v1730 CSV 或對應 checkpoint 變更腳本）。
2. **驗證證據缺口**：未見在 hw2_D13922024 目錄中以「驗證命令」顯示可直接得到 v1730 的證據鏈（僅在 round16 summary 有描述）。

## 3. 可直接執行之「修復前置驗證」項目

在不建立新 submission.csv 的前提下，先做以下核對才能允許進一步修復：
1. **核對實作差異**：比對 `make_final.py` 的 v1121 常數邏輯與 round16 summary 所列 v1730 五點 patch（g21/g22/g26/g27/g29），確認偏差。
2. **補齊最少補丁路徑**（在現有文件架構下）：規劃將修正寫進可重現步驟，不改動輸出文件名稱規則。
3. **端對端可重現校驗腳本**：確認 `make_final.py --from-checkpoint v851 --output submission.csv` 是否可改成穩定產生 v1730（需先完成補丁）且 `validate_submission.py` pass。
4. **版本同步檢查**：更新 `README.md`、`hw2_report.md`、（如有）`CLAUDE.md` 的最佳分數與版本標註，避免 hand-over 與 hand-in 包互相矛盾。

## 4. 可執行的結論

- 目前 hand-over 與 round16 記錄是**新一輪真實狀態**（v1730=0.44384）。
- 當前 hand-in 套件仍是**v1121/0.44352 的凍結快照**，屬於可驗證的 stale package。
- 尚未看到「不新增 CSV、只更新流程」的前提下完成 v1730 對齊；因此目前階段應先做流程對齊與重現驗證，再行最終封包更新。
