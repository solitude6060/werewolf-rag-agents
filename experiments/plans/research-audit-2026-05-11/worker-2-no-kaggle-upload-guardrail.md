# Worker 2 Lane Note — No Kaggle Upload Guardrail

## 結論

本 team run 的研究 audit 必須維持 **research-only / no-upload**：不得登入 Kaggle、不得執行任何上傳動作、不得把任何候選 CSV 標記成「本輪應上傳」。本 lane 只提供可整合到主 audit matrix 的上傳邊界與證據。

## Binding constraints

| 邊界 | 狀態 | 證據 |
|---|---|---|
| 不上傳 Kaggle | 必須遵守 | `.omx/specs/deep-interview-project-progress-requirements-status.md` 的 Non-goals 明列 `No Kaggle upload`。 |
| 不推薦 upload | 必須遵守 | 同一 spec 明列 `No upload recommendation in this pass unless the user later explicitly reopens that decision`。 |
| 不產生新 submission CSV 作為第一交付 | 必須遵守 | 同一 spec 明列 `No new submission CSV as the primary deliverable for the first pass`。 |
| 本輪第一交付為 audit matrix | 必須遵守 | 同一 spec 的 Desired outcome 與 acceptance criteria 指向 `experiments/plans/2026-05-11-research-audit-matrix.md`。 |

## Repo evidence that makes upload unsafe in this pass

| 證據 | 解讀 | 對本輪的限制 |
|---|---|---|
| `experiments/plans/round16_FINAL_SUMMARY.md` 記錄 v1730 為目前 Kaggle private verified best：`0.44384`。 | 目前已有 verified best，但 audit 尚未完成，不能把「已有 best」直接升級成上傳或交付決策。 | 只能引用為現況，不可產生新上傳建議。 |
| `experiments/plans/round16_FINAL_SUMMARY.md` 的 Next steps 前提是 `if more Kaggle slots become available — currently exhausted`。 | 後續 v1731 / v1432 / v1610b 等線仍需額外證據與 slot 判斷。 | 本輪可列為 research-only candidate，不可執行 Kaggle probe。 |
| `experiments/logs/upload_queue.md` 含多段歷史 `Recommended upload order` 與 `Do NOT upload`。 | 舊推薦是在舊 anchor / 舊資訊下形成，且有多個 public proxy 誤導 private 的案例。 | audit matrix 應標示為歷史證據，不可沿用成 2026-05-11 的推薦。 |
| `.omx/interviews/project-progress-requirements-status-20260511T150020Z.md` 第 3 輪使用者選擇 `research_only_no_upload`。 | 使用者已明確把本輪壓力測試結果導向不上傳。 | 任何 upload 決策都需後續使用者重新開啟。 |

## Guardrail for integration into the primary audit matrix

建議主 audit matrix 加入固定欄位：

- `Upload status`: 固定使用 `Blocked this pass / no-upload`、`Historical only`、`Research-only candidate` 等字眼。
- `Evidence required before any future upload discussion`: 列出本地驗證、row diff、風險證據與使用者重新授權。
- `Stop condition`: 若只能靠 Kaggle slot 判斷、或 public proxy/LLM consensus 與 private 泛化證據衝突，則停在 research-only。

## Allowed vs disallowed actions

| 類型 | 本輪是否允許 | 說明 |
|---|---:|---|
| 讀取現有 Kaggle private 分數紀錄 | 允許 | 只作為 historical evidence。 |
| 讀取既有 submission/evidence CSV 以理解差異 | 允許 | 只讀或驗證既有檔案，不新增候選。 |
| 建立 audit/plan markdown | 允許 | 本輪主要交付。 |
| Kaggle web upload / CLI upload | 禁止 | 超出 no-upload 邊界。 |
| 新增「推薦上傳 X」結論 | 禁止 | Task 3 另有 no upload recommendation guardrail。 |
| 新增 candidate submission CSV | 禁止 | 另由 task 4 guardrail 覆蓋；本 note 不產生 CSV。 |

## Stop condition

本 lane 在完成上傳邊界、證據引用與主矩陣整合建議後停止；不執行 Kaggle、不中介外部 upload、不產生 submission CSV。
