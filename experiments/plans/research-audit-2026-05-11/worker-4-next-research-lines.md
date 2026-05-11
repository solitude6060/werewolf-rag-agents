# Worker 4 Lane Note — Research-only next-line matrix（v1731 / v1432-fixed / v1610b）

## 本 lane 結論

本文件只評估下一輪「研究線」的排序與證據需求，供 `experiments/plans/2026-05-11-research-audit-matrix.md` 整合；**不推薦上傳、不建立 submission CSV、不登入或呼叫 Kaggle、不執行長 LLM runs**。所有候選都維持 research-only，除非未來使用者重新開啟 upload 決策、Kaggle slot 可用，且已補齊本地 row diff / evidence / validator。

目前可信 anchor 是 `v1730 = 0.44384`（`v1605 + v1610`，5 rows，Kaggle private verified）。下一步應以「最小 row 差異、可逐列驗證、避免 toxic family」為準則；不能把 public proxy、LLM 共識或歷史推薦直接升級成本輪行動。

## 下一研究線矩陣

| Candidate / line | Hypothesis | Required evidence before any future probe | Main risk | Expected artifact | Validation | Stop condition |
|---|---|---|---|---|---|---|
| **v1731**：`v1730 + g14 Boy Peter ws=0 → 0.001` demote | mirror `v1605`：若 g14 Peter 也是 reverse-anchored hedge（`role=Werewolf, ws=0` 但 AP 上刻意壓低），微幅 demote 應 neutral 或 +epsilon；比 boost 安全。 | 1) 從 v1730 anchor 產生單列 diff，只動 g14 Boy Peter；2) transcript / historical notes 說明為何 Peter 是 reverse-anchor，而不是可 boost 的真狼；3) validator `OK: 397 predictions validated`；4) 與 v1605 的 row-disjoint / AP rank impact 說明。 | reverse-anchor rows 已被 v1710/v1713 證明不能靠 LLM 共識 boost；但 demote 到 0.001 仍可能微幅改變 AP 排序，且 Kaggle slot 才能分辨 neutral vs epsilon。 | `experiments/plans/v1731_g14_peter_demote.md`（研究計畫 + row diff table）；本輪不產生任何 CSV，未來若重新授權需另開規格。 | 本輪只允許 markdown audit；未來若授權：validate_submission + local diff + no role change check + manual evidence table。 | 缺使用者重新授權、缺 Kaggle slot、缺單列 row diff/evidence，或需要 LLM 共識作主要理由時停止。 |
| **v1432-fixed**：Madman-aware fake-Seer scan on v1730 | 修補 v1450/v1500 的錯誤：Seer white-call 到 `role=Madman` 應視為標準規則下合理 WHITE，不是 fake-Seer。修補後只在 target 是 `role=Werewolf, ws=1.0` 且非 Madman 時尋找 fake-Seer candidate。 | 1) 明確規則：skip target role==Madman；2) 多行 window evidence（speaker 自稱 Seer / divination result / target role）不能退化成 plain accusation；3) 每個候選需 transcript line number、speaker、target、target v1730 role/ws、candidate old/new ws；4) no same-game double boost / no role change audit。 | fake-Seer family 曾因 g27 Otto 誤判造成 v1500 additional −0.001；若 parser 太寬，會重新落入 plain assertion / role-play toxicity。 | `experiments/plans/v1432_fixed_madman_aware_fake_seer.md`（規則規格、候選 evidence table、拒絕案例）；本輪不產生任何 CSV。 | 本輪驗證是規格與 evidence 完整性；未來若授權才跑 deterministic script、validator、candidate-vs-v1730 diff。 | 若 white-call target 是 Madman、target 非 verified Werewolf、證據只是普通對話指控、或候選需要人工/LLM 主觀補洞，停止。 |
| **v1610b**：四個 borderline 0.5 rows 從 0.7 微調到 0.75 | v1610 已證明 g21/g22/g26/g29 集體 0.5→0.7 為正；0.75 是比 0.7 更細的單軸 tuning，可能保留大多數收益並微增 AP。 | 1) 從 v1730 anchor 只改四個 rows（g21 Father Jimzon、g22/g26 Shepherd Katharina、g29 Young Man Joachim）0.7→0.75；2) 說明為何不碰 ws=1.0 cluster、不碰 g23 Liza、不碰 0.85+；3) validator + diff summary。 | v1710 中 g29 0.85 伴隨 regression，雖混有 g23 Liza toxic component，但仍提示 0.85+ overpush；0.75 只能由 Kaggle slot 分辨，public proxy 對 private rows 無效。 | `experiments/plans/v1610b_borderline_0p75.md`（single-axis tuning plan + four-row diff）；本輪不產生任何 CSV，未來若重新授權需另開規格。 | 本輪只檢查設計符合 cap discipline；未來若授權：validate_submission、diff exactly 4 rows、public proxy 標為不具鑑別力。 | 若需要用 public proxy 證明、想跳到 0.85/0.95、混入其他 rows、或沒有 Kaggle slot，停止於 research-only。 |
| **v930d-style strict claimant / veto hybrid**（evidence-backed alternative） | taxonomy 顯示 strict distinct≥5 cross-claim + Seer/Medium veto audit 比 LLM confidence label 更可靠；可作下一個 structural/LLM hybrid research template。 | 1) transcript line numbers；2) distinct claimants 計數；3) Seer/Medium WHITE/HUMAN veto audit；4) 只處理未被 toxic family 排除的 role==Werewolf candidate；5) 明確不採用 LLM confidence 字面值。 | coverage 低，且若 evidence 退化成普通 accusation 會接近 v200e toxic family；若缺 veto audit，容易產生假陽性。 | `experiments/plans/v93xx_strict_claimant_veto_research.md`（候選規格、claimant table、veto table）；本輪不跑長 LLM。 | read-only transcript audit + deterministic counting spec；未來授權才可轉 script / validator。 | distinct claimant 不足、缺 line numbers、存在 WHITE/HUMAN veto、或需要長 LLM run 才能補 evidence 時停止。 |
| **bracket / execution-anchored reveal residue scan**（low-priority alternative） | v1120/v1121、v200d 顯示 bracket-bold / execution/post-lynch 結構 reveal 可信；若還有未耗盡 residue，可作高 precision scan。 | 1) 證明不是 plain assertion；2) GM/system/execution/post-lynch proximity；3) row 尚未在 v1730 ws=1.0 或已處理；4) no same-game double boost。 | round16 結論指出 post-lynch bracket-bold reveal pool 幾乎耗盡；高機率 no-op。 | `experiments/plans/bracket_reveal_residue_audit.md`（no-op 也要記錄 search terms / rejected rows）。 | read-only grep/spec audit；若無 eligible rows，artifact 明列 no-op。 | 找不到新 eligible row、或 evidence 只是玩家普通發言時停止。 |

## 建議排序（research-only，不是 upload order）

1. **v1432-fixed 規格先行**：它修補已知錯因（Madman discrimination），可產出明確 evidence table；但必須嚴格避免 plain accusation。
2. **v1731 單列 demote**：row diff 最小，與 v1605 mirror，適合作為未來 slot 可用時的低風險 epsilon probe；本輪只寫證據需求。
3. **v1610b 0.75 tuning**：假設清楚但需要 Kaggle slot 才能判斷；不得用 public proxy 或 0.85+ 推論。
4. **v930d-style hybrid / bracket residue**：作為替代研究模板；優先要求 deterministic evidence 與 veto audit，不跑長 LLM。

## 整合到主 audit matrix 的欄位建議

- `Research line`: v1731 / v1432-fixed / v1610b / strict-claimant hybrid / bracket residue。
- `Anchor`: 固定從 v1730 或現行 verified best 出發；不可從 toxic v1400/v1500/v1710/v1713 出發。
- `Allowed action this pass`: `Markdown audit only` / `read-only evidence review`。
- `Evidence required before future upload discussion`: row diff、transcript line numbers、validator、manual veto audit、user reauthorization。
- `Blocked action`: Kaggle upload、upload recommendation、新 submission CSV、長 LLM run。
- `Stop condition`: 缺 slot、缺授權、缺 row-level evidence、需要 public proxy 私端推論、或 evidence 落入 toxic family。

## 硬邊界

- 不修改 `hw2_D13922024/`。
- 不建立 `experiments/submissions/submission_*.csv` 、candidate CSV、evidence CSV 或任何新 CSV。
- 不執行 Kaggle upload / Kaggle CLI / browser upload。
- 不執行新的長 LLM inference；本文件只引用既有 round16 summary、taxonomy、fix-log 與 plan evidence。
- 不給「本輪應上傳」建議；上方排序是 research-only triage priority。

## 本 lane stop condition

本文件完成候選假設、必要證據、風險、預期 artifact、驗證方式與停止條件後即停止。下一步只能由 leader 整合到主 audit matrix；任何 candidate CSV 或 upload 決策都需要使用者後續明確重新授權。
