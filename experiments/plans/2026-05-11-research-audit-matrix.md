# 2026-05-11 Research Audit Matrix（主整合骨架）

日期：2026-05-11
狀態：research-only audit matrix skeleton
整合者：worker-3（Task 12）
硬邊界：**不執行 Kaggle upload、不給本輪 upload recommendation、不建立新的 submission CSV、不修改 `hw2_D13922024/` hand-in package**。

## 0. Source lane notes

本矩陣整合下列 lane notes；若後續 lane note 更新，應先更新對應 row 的「Evidence source / Stop condition」，再討論任何修包或提交行動。

| Lane | Source note | Integrated status | Scope used here |
|---|---|---|---|
| worker-1 assignment compliance | `experiments/plans/research-audit-2026-05-11/worker-1-assignment-compliance.md` | 已存在並納入 | 作業需求、合規 checklist、package repair gate |
| worker-2 no-upload guardrail | `experiments/plans/research-audit-2026-05-11/worker-2-no-kaggle-upload-guardrail.md` | 已納入 | no-upload / no-upload-recommendation / no-new-CSV binding boundary |
| worker-2 candidate taxonomy | `experiments/plans/research-audit-2026-05-11/worker-2-candidate-family-taxonomy.md` | 已納入 | candidate family classification、reuse / avoid rules、toxic families |
| worker-3 stale package gap | `experiments/plans/research-audit-2026-05-11/worker-3-status-stale-package-gap.md` | 已納入 | v1730 current best vs `hw2_D13922024` v1121 stale package gap |
| worker-4 next research lines | `experiments/plans/research-audit-2026-05-11/worker-4-next-research-lines.md` | 已存在並納入 | research-only next-line priority、evidence requirements、stop conditions |

> TODO policy：worker-1 與 worker-4 notes 在本次整合時已存在，因此本版不保留空白 TODO row；若 leader 判定任一 note 尚未 final，將該 lane row 狀態改為 `TODO / awaiting final lane note`，不得用推測內容補洞。

## 1. Binding guardrails（本輪不可跨越）

| Boundary | Status this pass | Evidence source | Enforcement in this matrix |
|---|---|---|---|
| No Kaggle upload | Blocked | `worker-2-no-kaggle-upload-guardrail.md`：binding constraints 明列 no Kaggle upload；使用者選擇 research-only no-upload | 所有 candidate row 的 upload status 固定為 `Blocked this pass / research-only` |
| No upload recommendation | Blocked | `worker-2-no-kaggle-upload-guardrail.md`：不得把任何候選標記成「本輪應上傳」 | 「建議排序」只能是 research priority，不是 upload order |
| No new submission CSV | Blocked | `worker-2-no-kaggle-upload-guardrail.md` 與 task-4 guardrail；worker-3 note 也確認未產生新 CSV | 允許讀取既有 CSV / validator；禁止產生 replacement / candidate CSV |
| No hand-in package edit | Blocked in this audit pass | task-12 明令 `Do not edit hw2_D13922024`；worker-1/3 notes 均列為後續 repair gate | `hw2_D13922024/` 只做 stale/gap 記錄，不在本矩陣修正 |
| First deliverable is audit matrix | Required | `worker-2-no-kaggle-upload-guardrail.md`：first pass desired outcome 指向本矩陣 | 本檔是 primary artifact；不替代 package repair / submission decision |

## 2. Current status matrix

| Topic | Classification | Evidence source | Current finding | Risk / gap | Required verification before future repair | Stop condition this pass |
|---|---|---|---|---|---|---|
| Current verified best | verified-positive / current status | `hand-over.md:4,8,13`; `experiments/plans/round16_FINAL_SUMMARY.md:5,15-22,103-104`; `worker-3-status-stale-package-gap.md` | `v1730 = 0.44384`，相對 `v1121 = 0.44352` 增加 `+0.00032`，Kaggle private verified | 最新研究狀態已超過 hand-in package，但本輪不直接轉成 upload | 若未來修包，需 byte-equal reproduce existing `submission_v1730_kaggle_validated_stack_private.csv` 並通過 validator | 本輪只記錄 current status；不上傳、不新建 CSV |
| Hand-in package status | stale package gap | `worker-3-status-stale-package-gap.md`; `hw2_D13922024/README.md`; `hw2_D13922024/hw2_report.md`; `hw2_D13922024/make_final.py` | `hw2_D13922024/` README/report/reproducer/submission 仍指向 v1121 / 0.44352 | 若直接交 package，reproducibility claim 會落在 v1121，不是 v1730 | 修包前需同步 docs、reproducer、artifact target；驗證 `OK: 397 predictions validated` 與 5-row diff 對齊 | 不修改 `hw2_D13922024/`；只列為 future package repair gate |
| Assignment compliance | mostly compliant but stale-score risk | `worker-1-assignment-compliance.md` | v1121 package 已有 multi-agent + RAG、local Ollama、no training/API、≤12GB VRAM、397-row validator、report structure 等敘述 | score / version stale；PDF artifact、zip contents、report page count 仍需 future package gate；Gemini audit 需清楚界定非 submission pipeline | 修包前檢查 zip/PDF 命名、頁數、validator、模型大小 evidence、external API boundary | 不把 assignment submission requirement 解讀為本輪 upload authorization |
| Upload boundary | blocked this pass | `worker-2-no-kaggle-upload-guardrail.md` | 可讀既有 private score 紀錄與既有 CSV；不可 Kaggle upload、不可 upload recommendation | 舊 `upload_queue.md` 或 hand-over 歷史推薦語句可能誤導 | future upload discussion 需使用者重新授權 + row diff + local validation + risk record | 一律停在 research-only |
| Candidate family taxonomy | integrated evidence map | `worker-2-candidate-family-taxonomy.md` | 已分類 verified-positive、toxic、research-only、historical-positive families | toxic families 容易由 public proxy / LLM consensus 誤導 | future candidate 需逐 row evidence、validator、manual veto audit、與 toxic-family exclusion | 本輪不將 taxonomy 轉成 candidate CSV 或 upload order |
| Next research lines | research-only priority | `worker-4-next-research-lines.md` | v1432-fixed、v1731、v1610b、strict claimant/veto、bracket residue 均可作未來研究線 | 多數需要 Kaggle slot / user reauthorization；public proxy 不足以判斷 private rows | future plan 需 row diff、transcript line numbers、validator、manual evidence table | 本輪只保留 markdown research queue；不跑長 LLM、不產生 CSV |

## 3. Candidate / family decision matrix

| Candidate / family | Classification | Private result if known | Reuse / avoid rule | Evidence required before future discussion | Upload status this pass |
|---|---|---:|---|---|---|
| v1121 anchor | verified baseline / rollback | 0.44352 | 可作 rollback baseline；只接受 execution/post-lynch 結構 evidence | validator、baseline provenance、與 v1730 diff 說明 | Historical only / no upload |
| v1605 g27 Otto demote | verified-positive component | 0.44357 | fake-Seer 規則必須跳過 target role==Madman；錯向 boost 可反向檢驗 | row-disjoint evidence、Madman rule explanation、validator | Historical positive / no upload |
| v1610 four borderline 0.5→0.7 | verified-positive component | 0.44378 | borderline boost cap = 0.7；避免 0.85+ overshoot | exactly four-row diff、cap discipline、validator | Historical positive / no upload |
| v1730 stack | current verified best | 0.44384 | 只 stack Kaggle-verified positive 且 row-disjoint 小改動 | byte-equal reproduce target、5-row patch provenance、validator | Current status only / no upload |
| v1400 LLM ensemble rerank | toxic / failed | 0.43655 | 避免 public-proxy-only 大範圍 rank reblend | 若 >20 rows 且 >0.10 ws 變動，需 structural cross-check；否則停止 | Avoid / no upload |
| v1500 v1400 + fake-Seer boost | toxic / failed | 0.43557 | v1450 as-written dead；fake-Seer gate 需 Madman discrimination | target role audit、line evidence、no plain accusation | Avoid / no upload |
| v1710 / v1713 LLM consensus boosts | toxic / failed | 0.44256 / 0.44273 | 不 LLM-boost v1121 `role=Werewolf, ws=0` reverse anchors | LLM 只能 hypothesis generator；需 independent structural evidence | Avoid / no upload |
| v200d bracket-bold assertion | historical positive evidence family | 0.41070 | bracket-bold / structured reveal 可作高品質 evidence family | row-level validation、確認非 plain assertion | Historical only / no upload |
| v200e plain assertion | toxic language family | 0.39559 | generic plain accusation 不可直接 boost | 需 execution/bracket/selected-role anchor，否則停止 | Avoid / no upload |
| v930d strict claimant/veto hybrid | research template | public proxy positive；private not in cited plan | distinct claimants + Seer/Medium veto 比 LLM confidence 可信 | transcript line numbers、claimant count、WHITE/HUMAN veto audit | Research-only / no upload |
| v810 WHITE consensus demote | negative/no-op probe | 0 delta vs anchor | WHITE/HUMAN 必須是 result context，不能是普通村讀 | parser precision audit；若 identical/no-op 則停止 | Historical negative / no upload |
| v1731 | future research line | unknown | mirror v1605 單列 demote；不可 boost reverse anchor | single-row diff、manual evidence、validator、user reauthorization | Research-only / blocked |
| v1432-fixed | future research line | unknown | Madman-aware fake-Seer scan；嚴禁退化成 plain accusation | line evidence、target role/ws、skip Madman rule、candidate table | Research-only / blocked |
| v1610b | future research line | unknown | four-row 0.7→0.75 micro tuning；不可跳 0.85+ | exactly four-row diff、validator、Kaggle slot only if reauthorized | Research-only / blocked |

## 4. Future package repair gate（非本輪執行）

若未來 leader / user 明確開啟 package repair，最小 gate 如下；未通過前不得討論 upload：

1. **Scope authorization**：明確授權可修改 `hw2_D13922024/`；本 audit pass 沒有此授權。
2. **Target provenance**：以既有 v1730 CSV 作 byte-equal target，確認 5-row patch 與 `round16_FINAL_SUMMARY.md:125-130` 一致。
3. **Reproducer sync**：`make_final.py` / README / report 同步為 v1730 / 0.44384；v1121 只能保留作 baseline history。
4. **Validation**：`assert/validate_submission.py <candidate>` 必須回報 `OK: 397 predictions validated`；若禁止新 CSV，需使用 leader 指定 temp path 或 in-memory compare。
5. **Assignment packaging**：確認 final zip / PDF 命名、report ≤5 pages、requirements、assert script、README、main/make_final 的可執行性。
6. **Compliance boundary**：外部 API audit 必須與 submission pipeline 切開；模型大小 / local Ollama evidence 補齊。
7. **No-upload reauthorization**：即使修包完成，也仍需使用者另行重新開啟 upload decision；修包 ≠ 上傳許可。

## 5. Verification log for this matrix

- 已確認 source lane notes 存在：`worker-1-assignment-compliance.md`、`worker-2-no-kaggle-upload-guardrail.md`、`worker-2-candidate-family-taxonomy.md`、`worker-3-status-stale-package-gap.md`、`worker-4-next-research-lines.md`。
- 本檔只新增 / 更新 markdown audit artifact：`experiments/plans/2026-05-11-research-audit-matrix.md`。
- 未修改 `hw2_D13922024/`，未建立新的 submission CSV，未執行 Kaggle upload。
- 後續驗證命令應至少檢查：檔案存在、source lane note references 存在、`hw2_D13922024/` 無 diff、無新增 CSV。
