# Worker-1 作業需求／合規檢核 lane note（research-only）

- 日期：2026-05-11
- 範圍：assignment requirements / compliance checklist
- 邊界：本文件只做既有證據盤點；**不建議上傳 Kaggle**、**不產生新 submission CSV**、**不修改 `hw2_D13922024/` hand-in package**。
- 主要來源：
  - `/home/ma/Research/PhD/course/114_2/AI/hw2/HW2-Multi-Agent Werewolf Prediction.pdf`
  - `/home/ma/Research/PhD/course/114_2/AI/hw2/hw2_D13922024/README.md`
  - `/home/ma/Research/PhD/course/114_2/AI/hw2/hw2_D13922024/hw2_report.md`
  - `/home/ma/Research/PhD/course/114_2/AI/hw2/werewolf-project/docs/SUBMISSION_GUIDE.md`
  - `/home/ma/Research/PhD/course/114_2/AI/hw2/werewolf-project/README.md`

## 高層結論

目前文件證據顯示 hand-in package 的 `v1121 / 0.44352` 已具備基本作業合規敘述：多代理 + RAG、local Ollama、無訓練/微調、無外部 API、模型 ≤12GB VRAM、397-row validator、報告 5 頁內等。但它與本輪 audit 的 binding spec / 最新實驗紀錄存在「研究狀態落差」：最新最佳已由 `v1121` 推進到 `v1730 = 0.44384`，本 lane 不修 package，也不把該落差轉成上傳建議；只標記為後續若要修交付包時必須驗證的風險。

## 作業需求與目前合規矩陣

| 需求 / 規則 | 證據來源 | 目前狀態 | gap / risk | no-upload implication |
|---|---|---|---|---|
| 任務目標：根據 50 場狼人殺資料，預測角色與 `wolf_score`，提交 Kaggle | PDF 說 Dataset 含 50 game runs、20 public、30 private，目標是 build multi-agent system to predict role and wolf score and submit to Kaggle（`HW2-Multi-Agent Werewolf Prediction.pdf`，pdftotext lines 57-65） | hand-in README 說 fast path 可產生 verified submission，validator 為 397 predictions（`hw2_D13922024/README.md:9-15`） | assignment 目標是提交，但本次任務明確是 research-only/no-upload；且 hand-in 目前描述 v1121，不是最新 v1730 | 本輪不可把「作業需要 Kaggle」解讀成要上傳；只記錄驗證需求 |
| Kaggle performance 佔 80%，private leaderboard 計分；metric 為 Macro-F1 + AP | PDF performance ranking / private leaderboard（pdftotext lines 117-141）；hand-in README 給公式（`hw2_D13922024/README.md:3-5`）與 scoring breakdown（`hw2_D13922024/README.md:112-118`） | hand-in package 宣稱 verified private 0.44352（`hw2_D13922024/README.md:3-5`；`hw2_D13922024/hw2_report.md:3-5`） | 最新研究狀態（非本 lane 必讀來源外的 cross-lane 事實）指出 v1730 0.44384；hand-in score 可能 stale | 不因分數落差建議補傳；後續若修包須先 reproduce / compare CSV |
| Multi-agent system 至少兩個 agents | PDF 明列 multi-agent system contains at least two agents（pdftotext lines 117-121） | README: Analyst + Verifier pair retrieving role-rule corpus（`hw2_D13922024/README.md:21-50`）；report: qwen3.5 analyst + gemma4 verifier with structured JSON contract（`hw2_D13922024/hw2_report.md:21-51`）；project README 也列 Stage 1/2/3 與 candidate-level agents（`werewolf-project/README.md:27-35`） | hand-in 的 `main.py` 是否能完整展示 multi-agent behavior 需 package-level smoke；README 已把 `main.py` 標為 legacy demo only（`hw2_D13922024/README.md:74-81`） | 不跑長 LLM 全流程；後續若需交付包修正，優先用文件與 fast reproduction 檢查 |
| RAG / evidence retrieval 需求 | PDF 建議可包含 RAG（pdftotext lines 75-80）；report rubric 要說明 RAG design、issues、retrieval accuracy（pdftotext lines 145-152） | README: RAG = role-rule corpus + per-player evidence retrieval（`hw2_D13922024/README.md:21-50`）；report: dossiers + retrieved role-rule snippet（`hw2_D13922024/hw2_report.md:55-69`）；project README: transcript、events、role rules、feature extractor retrieval（`werewolf-project/README.md:27-35`） | README/report 合規敘述充分；但若老師重跑 full path，LLM nondeterminism 可能造成 reproduction 差異（`hw2_D13922024/README.md:100-110`） | 本輪只標示風險；不啟動 6-8 小時 full reproduction |
| 不可 train / fine-tune | PDF 禁止 train/fine-tune，違規 0 分（pdftotext lines 124-127） | README hard constraints: pure inference + deterministic regex（`hw2_D13922024/README.md:52-60`）；report hard constraints（`hw2_D13922024/hw2_report.md:11-19`）；project README: no training/fine-tuning（`werewolf-project/README.md:27-35`） | 無明顯違規證據；需避免後續研究誤導成訓練線 | 任何後續研究只能是推論、規則、後處理、local audit |
| 不可使用 external API in submission pipeline | PDF 禁止 external API（pdftotext lines 124-127） | README: local Ollama only（`hw2_D13922024/README.md:52-60`）；report: local Ollama qwen/gemma/deepseek（`hw2_D13922024/hw2_report.md:16-19`）；project README: local models only（`werewolf-project/README.md:27-35`） | report 提到 independent gemini-CLI audit（`hw2_D13922024/hw2_report.md:39-45`、`hw2_D13922024/hw2_report.md:123-126`），需要清楚界定為離線 audit/非 submission pipeline，以免被誤讀 | 不新增任何外部 API run；若修 report，需補強「audit-only, not pipeline」界線 |
| 模型需 ≤12GB VRAM | PDF 禁止使用 require more than 12GB VRAM 的模型（pdftotext lines 124-127） | README hard constraints 列 qwen3.5:9b 6.6GB、gemma4:e4b 9.6GB、deepseek-r1:14b 9.0GB（`hw2_D13922024/README.md:52-60`）；report 同列 local Ollama models（`hw2_D13922024/hw2_report.md:16-19`） | 模型大小證據目前在 README 敘述，未附 `ollama ps` 當時截圖；若被要求重現，需環境證據 | 本輪不拉模型、不跑長模型；只標記驗證需要 |
| private submission CSV 需格式正確 / 397 rows | README validate command says OK: 397 predictions validated（`hw2_D13922024/README.md:9-15`）；hard constraints table（`hw2_D13922024/README.md:52-60`）；project README quick start validator expected OK 397（`werewolf-project/README.md:54-76`）；submission guide expected OK 397（`werewolf-project/docs/SUBMISSION_GUIDE.md:19-39`） | hand-in fast path supposedly byte-equal to verified submission（`hw2_D13922024/README.md:7-19`） | 本 lane 未重跑 validator on hand-in `submission.csv`，只做文件 evidence audit；另 `werewolf-project/docs/SUBMISSION_GUIDE.md` 是舊 v166 狀態，與 hand-in v1121 不一致（`werewolf-project/docs/SUBMISSION_GUIDE.md:5-12`） | 不新建 CSV；後續 package repair 前應重跑 validator 並比對 397 rows |
| report 佔 20%，需含 RAG 設計、成功/失敗案例、優化，且 5 頁內 | PDF rubric（pdftotext lines 145-152）；zip structure 要 `hw2_<student-id>.pdf` report within 5 pages（pdftotext lines 167-190） | hand-in report 章節包含架構、methods、success/failure、optimizations（`hw2_D13922024/hw2_report.md:21-52`、`:113-166`） | Markdown report 是否實際轉成 `hw2_D13922024.pdf` 且 5 頁內，不在本 lane 驗證範圍；若 `hw2_report.md` 超轉頁數，可能扣分 | 不修改 report；只把頁數/輸出 PDF 標為後續 package check |
| zip 檔名與結構：`hw2_<student-id>.zip`，含 report pdf、`main.py`、`assert`、`requirements.txt`、README | PDF submission rules（pdftotext lines 156-190） | hand-in README file layout 列 `make_final.py`、`submission.csv`、`main.py`、`assert/validate_submission.py`、`requirements.txt`、`hw2_report.md`、README（`hw2_D13922024/README.md:62-86`）；submission guide package checklist 映射 source files（`werewolf-project/docs/SUBMISSION_GUIDE.md:41-53`） | PDF 要 `hw2_<student-id>.pdf`，目前 hand-in source cited here is `hw2_report.md`；需確認 final zip/pdf artifact 是否存在且命名正確。本 lane不得改 hand-in | 後續若做交付包修復，要以 file-existence + zip contents check 為 gate |
| deadline：2026/05/15 23:59；Kaggle hard deadline no extensions | PDF deadline（pdftotext lines 156-164、196-200） | binding spec 也記錄 deadline 2026-05-15 23:59 | 距 2026-05-11 尚有時間，但不能用 private leaderboard 當無限 oracle | 本輪以 audit matrix 為 stop condition，不上傳、不推薦上傳 |

## Stale / 衝突證據摘要

1. `hw2_D13922024/README.md` 與 `hw2_report.md` 均以 `v1121 = 0.44352` 作為 final / verified submission（`hw2_D13922024/README.md:3-5`、`:112-118`；`hw2_D13922024/hw2_report.md:168-178`）。
2. `werewolf-project/docs/SUBMISSION_GUIDE.md` 更舊，仍說 best verified candidate 是 v166 / 0.40764（`werewolf-project/docs/SUBMISSION_GUIDE.md:5-12`），只能作「package checklist / validation command」來源，不應作最新分數來源。
3. `werewolf-project/README.md` 仍以 v144 / 0.40743 作「目前最佳已上傳結果」（`werewolf-project/README.md:5-12`），也屬 stale project-doc risk。
4. 本輪 binding spec 要求 first outcome 是 research audit matrix、不是新 CSV 或 upload；No Kaggle upload、no upload recommendation、no new submission CSV、no direct implementation（`.omx/specs/deep-interview-project-progress-requirements-status.md` 的 Out of scope / Non-goals）。

## 後續 package repair 前的 gate（非本 lane 執行）

- `hw2_D13922024/` 不可在本 team run 被修改；若未來另開修包任務，需先確認 `make_final.py --split private --output submission.csv` 是否 byte-equal / validator OK。
- 確認 zip artifact 是否包含 PDF 而非只有 Markdown report，且頁數 ≤5。
- 若要把 v1730 納入 hand-in/package，必須先有 reproducible CSV、validator `OK: 397 predictions validated`、與明確風險記錄；本 lane 不提供 upload recommendation。
- `werewolf-project/docs/SUBMISSION_GUIDE.md` 和 `werewolf-project/README.md` 的 stale candidate 敘述需在未來文件修復中統一，但本 lane 只記錄風險。

## Stop condition

本 lane 完成於：已產出 assignment compliance checklist、引用指定來源、明確標示 no-upload/no-new-CSV/no-hand-in-edit 邊界，並以輕量檔案存在與 citation grep 驗證。未執行 Kaggle upload、未產生 submission CSV、未改 `hw2_D13922024/`。
