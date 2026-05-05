# Werewolf RAG Agents

這是一份用於 **AI HW2 Multi-Agent Werewolf Prediction** 的可重現專案。目標是根據狼人殺遊戲文字紀錄，預測每位玩家的角色與 `wolf_score`，並輸出符合 Kaggle/作業格式的 submission CSV。

目前最佳已上傳結果：

| Candidate | Kaggle private | 說明 |
| --- | ---: | --- |
| `submission_v131_candidate_qwen_safe_private.csv` | 0.40434 | 第一個大幅突破；保守 qwen candidate audit。 |
| `submission_v144_filtered_big_gamble_private.csv` | **0.40743** | 最新最佳；filtered LLM disagreement big-gamble。 |

> 最後衝刺用檔案位於 repo 外層：`../experiments/submissions/`。本 repo 保留程式碼、驗證器、報告與實驗紀錄。


## Repository Name

Recommended GitHub repository name: **`werewolf-rag-agents`**.

Suggested description:

> Multi-agent RAG and local-LLM audit workflow for Werewolf role and wolf-score prediction.

Suggested topics: `multi-agent`, `rag`, `ollama`, `local-llm`, `werewolf`, `social-deduction`, `coursework`.

---

## 1. Assignment Fit

本專案遵守作業限制：

- **Multi-agent**：Stage 1 evidence fetching、Stage 2 analysis、Stage 3 constrained solver，另有 candidate-level local LLM audit agents。
- **RAG / evidence retrieval**：從 transcript、事件、角色規則與 feature extractor 取回證據，再交給 solver 或 local LLM audit。
- **Local models only**：使用 Ollama local models，例如 `qwen3.5:9b`、`deepseek-r1:14b`。
- **No training / fine-tuning**：所有改進都是推論、規則、後處理與本地 LLM audit。
- **Submission validation**：使用 `assert/validate_submission.py` 檢查欄位、角色、分數範圍與 row count。

詳細教學版說明見：[`docs/PROJECT_GUIDE.md`](docs/PROJECT_GUIDE.md)

---

## 2. Quick Start

```bash
cd werewolf-project
uv sync
```

Run tests:

```bash
UV_CACHE_DIR=.uv-cache uv run pytest tests/ -q
```

Validate the current final private candidate:

```bash
UV_CACHE_DIR=.uv-cache uv run python assert/validate_submission.py \
  ../experiments/submissions/submission_v166_postv144_zero_refine_private.csv
```

Score the matching public candidate locally:

```bash
UV_CACHE_DIR=.uv-cache uv run python ../experiments/scripts/local_score.py \
  ../experiments/submissions/submission_v166_postv144_zero_refine_public.csv \
  --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv \
  --quiet
```

Expected evidence at cleanup time:

```text
71 passed, 3 warnings
OK: 397 predictions validated
submission_v166_postv144_zero_refine_public.csv F1=0.4363 AP=0.5009 Score=0.4750
```

---

## 3. Project Map

```text
werewolf-project/
├── main.py                         # CLI entry point for baseline pipeline
├── src/                            # Multi-agent package: agents/data/rag/utils
├── tests/                          # Unit and integration tests
├── assert/                         # Assignment-facing submission validator
├── scripts/
│   ├── audits/                     # qwen/deepseek local LLM audit tools
│   ├── postprocess/                # score-only post-processing tools
│   └── *.py                        # compatibility wrappers for old commands
├── docs/
│   ├── PROJECT_GUIDE.md            # Teaching-oriented architecture guide
│   ├── EXPERIMENTS.md              # Score history and final sprint guide
│   ├── STRUCTURE.md                # Folder layout reference
│   ├── archive/                    # Historical notes/plans
│   ├── cleanup/                    # Planning-with-files records
│   ├── evals/                      # Detailed experiment logs
│   ├── report/                     # Report draft/outline
│   └── sdd/                        # Spec/design documents
└── artifacts/
    └── legacy-submissions/         # Old generated predictions kept for audit
```

Out-of-repo experiment artifacts used by the final sprint:

```text
../experiments/submissions/          # Public/private submission candidates
../experiments/llm_runs/             # Local Ollama audit caches
../experiments/scripts/              # Scoring and variant-generation utilities
../hand-over.md                      # Long chronological hand-over log
```

---

## 4. Main Workflows

### Baseline prediction pipeline

```bash
UV_CACHE_DIR=.uv-cache uv run python main.py predict 01
UV_CACHE_DIR=.uv-cache uv run python main.py predict-all --output predictions.csv
UV_CACHE_DIR=.uv-cache uv run python main.py predict-private --output private_predictions.csv
```

### Local LLM candidate audit

Run qwen/deepseek only on rows likely to affect Wolf-AP ordering:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/audits/candidate_llm_audit.py run \
  ../experiments/submissions/submission_v119_swap_private.csv \
  --split private \
  --model qwen3.5:9b \
  --num-ctx 4096
```

Apply a conservative or experimental scoring policy:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/audits/candidate_llm_audit.py apply \
  ../experiments/submissions/submission_v119_swap_private.csv \
  --split private \
  --model qwen3.5:9b \
  --ww-floor 0.5 \
  --output ../experiments/submissions/my_candidate_private.csv
```

---

## 5. What to Read First

1. [`docs/PROJECT_GUIDE.md`](docs/PROJECT_GUIDE.md) — architecture and assignment-compliance walkthrough.
2. [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md) — which submissions worked, failed, and why.
3. [`docs/STRUCTURE.md`](docs/STRUCTURE.md) — folder layout and command compatibility.
4. [`docs/SUBMISSION_GUIDE.md`](docs/SUBMISSION_GUIDE.md) — Kaggle candidate and package checklist.
5. [`docs/evals/2026-05-04-structured-llm-rag-audit-plan.md`](docs/evals/2026-05-04-structured-llm-rag-audit-plan.md) — detailed final sprint audit trail.
6. [`docs/report/hw2_report.md`](docs/report/hw2_report.md) — report draft material.
7. [`DATASETS.md`](DATASETS.md) — dataset and privacy policy.
8. [`CONTRIBUTING.md`](CONTRIBUTING.md) — development workflow.

---

## 6. Git / Development Discipline

- Use feature/dev branches; current active branch: `dev/structured-llm-rag-audit`.
- Use `uv`; do not install packages globally.
- Keep data/model/cache artifacts out of git.
- Before changing behavior, add or run tests first.
- For final candidates, always run both:
  - `pytest tests/ -q`
  - `assert/validate_submission.py <candidate_private.csv>`

