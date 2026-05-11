# Worker 4 Lane Note — No long LLM runs guardrail

## 結論

本 team run 是 **research-only audit**，不得把下一步研究線升級成新的長 LLM 推論工作。本 lane 的用途是把「不跑長 LLM」轉成可整合到主 audit matrix 的執行邊界：允許讀取既有 LLM / experiment artifacts；禁止新開大規模 prompt sweep、multi-model rerank、長 transcript inference、或任何需要額外 LLM compute 才能完成的候選產生。

## Binding evidence

| Evidence | Interpretation | Matrix implication |
|---|---|---|
| `.omx/specs/deep-interview-project-progress-requirements-status.md:45-48` | 本輪 scope 是 read-only repository artifacts / experiment logs，並整理既有 evidence-backed lines。 | audit matrix 只能引用既有證據，不應啟動新 LLM 生產線。 |
| `.omx/specs/deep-interview-project-progress-requirements-status.md:68-72` | 明列 Kaggle upload、hand-in package edit、新 submission CSV、以及 long-running LLM compute 都需要重新詢問或明確 gating。 | `Blocked action` 欄位應包含 `long LLM run blocked this pass`。 |
| `.omx/specs/deep-interview-project-progress-requirements-status.md:88-91` | Round16 已暴露 public proxy / LLM consensus 不能直接導向 next upload。 | LLM 共識最多當 hypothesis generator，不可當 authority 或 validation。 |
| `experiments/plans/round16_FINAL_SUMMARY.md` lessons | v1400 / v1710 / v1713 顯示 LLM rerank 或 4-model consensus 可 private-regress。 | 若候選依賴新的 LLM consensus，需停在 research-only，先要求 structural evidence。 |
| `research-audit-2026-05-11/worker-4-next-research-lines.md` | v1731 / v1432-fixed / v1610b 已被整理成 evidence requirement，而非執行請求。 | 主矩陣可引用該 note，不需再跑 LLM。 |

## Allowed vs blocked actions

| Action type | This pass | Notes |
|---|---:|---|
| 讀取既有 plan / hand-over / logs / submission evidence | 允許 | 僅作 audit citation。 |
| 讀取既有 LLM outputs 或既有 candidate taxonomy | 允許 | 不重新生成、不擴寫 prompt sweep。 |
| 小型 grep / diff / file-existence validation | 允許 | 用來證明 artifact 與 guardrail。 |
| 新開 multi-model transcript rerank | 禁止 | 屬於 long LLM run；Round16 已顯示 private transfer risk。 |
| 新開 LLM consensus 來推翻 reverse-anchor rows | 禁止 | v1710/v1713 是 toxic precedent。 |
| 用 LLM confidence label 取代 transcript line evidence | 禁止 | v930d-style hybrid 也要求 line numbers + veto audit。 |
| 以「需要 LLM 再判斷」作為完成條件 | 禁止 | 本輪 stop condition 應改為列明缺證據並停止。 |

## Integration rule for the primary audit matrix

建議主矩陣每個 research-only row 加上：

- `LLM status`: `No new LLM run this pass` / `Existing LLM artifact only` / `Blocked: would require long LLM run`。
- `Evidence replacement`: 若不能跑 LLM，需改列 transcript line numbers、deterministic regex、row diff、validator、manual veto audit。
- `Stop condition`: 若候選需要新 LLM consensus、長 transcript inference、或 LLM confidence 才能成立，停在 research-only。

## Stop condition

本 guardrail 在主矩陣可明確阻擋 long LLM run 並提供替代 evidence 欄位後完成；不新增 prompt、不呼叫本地或外部 LLM、不建立任何候選 CSV、不修改 `hw2_D13922024/`。
