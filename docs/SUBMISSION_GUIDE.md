# Submission Guide

This guide lists the files and checks needed before submitting the HW2 Werewolf project or a Kaggle candidate.

## 1. Current Verified Kaggle Candidate

Best verified private score so far:

| File | Kaggle private | Notes |
| --- | ---: | --- |
| `../experiments/submissions/submission_v144_filtered_big_gamble_private.csv` | **0.40743** | Current best; upload this for Kaggle private if no newer candidate supersedes it. |

Matching public file for local validation:

```text
../experiments/submissions/submission_v144_filtered_big_gamble_public.csv
```

## 2. Required Validation Commands

Run from `werewolf-project/`:

```bash
UV_CACHE_DIR=.uv-cache uv run pytest tests/ -q
UV_CACHE_DIR=.uv-cache uv run python assert/validate_submission.py \
  ../experiments/submissions/submission_v144_filtered_big_gamble_private.csv
UV_CACHE_DIR=.uv-cache uv run python ../experiments/scripts/local_score.py \
  ../experiments/submissions/submission_v144_filtered_big_gamble_public.csv \
  --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv \
  --quiet
```

Expected current evidence:

```text
71 passed, 3 warnings
OK: 397 predictions validated
F1=0.4363 AP=0.5007 Score=0.4750
```

## 3. Assignment Package Checklist

The course package usually needs a folder/zip like `hw2_<student-id>.zip`. Keep the exact course instructions as the source of truth, but this project currently maps files as follows:

| Required item | Current source |
| --- | --- |
| `main.py` | `werewolf-project/main.py` |
| `assert/` or validation code | `werewolf-project/assert/` |
| `requirements.txt` | `werewolf-project/requirements.txt` |
| README | `werewolf-project/README.md` |
| Report draft | `werewolf-project/docs/report/hw2_report.md` |
| Final Kaggle CSV | `../experiments/submissions/submission_v144_filtered_big_gamble_private.csv` |
| Legacy generated bundle | `werewolf-project/artifacts/legacy-submissions/hw2_D13922024/` |

## 4. Recommended Report Reading Order

Use these files to assemble the written report:

1. `docs/PROJECT_GUIDE.md` — architecture and assignment fit.
2. `docs/EXPERIMENTS.md` — experiment progression and final result.
3. `docs/evals/2026-05-04-structured-llm-rag-audit-plan.md` — detailed final sprint audit trail.
4. `docs/report/hw2_report.md` — report draft material.

## 5. Script Paths

Preferred organized paths:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/audits/candidate_llm_audit.py --help
UV_CACHE_DIR=.uv-cache uv run python scripts/audits/structured_llm_audit.py --help
UV_CACHE_DIR=.uv-cache uv run python scripts/postprocess/leaderboard_informed_fixes.py --help
```

Compatibility wrappers still work:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/candidate_llm_audit.py --help
UV_CACHE_DIR=.uv-cache uv run python scripts/structured_llm_audit.py --help
UV_CACHE_DIR=.uv-cache uv run python scripts/leaderboard_informed_fixes.py --help
```

## 6. What Not to Move During Final Sprint

Do not move these outer workspace directories without a separate migration plan:

```text
../experiments/submissions/
../experiments/llm_runs/
../experiments/scripts/
```

They are shared by score sweeps, cached local Ollama audits, and historical hand-over commands.
