# Plan: Structured LLM + RAG Score Breakthrough

Date: 2026-05-04
Branch: `dev/structured-llm-rag-audit`

## Baseline Facts

- Best verified private: v119 = 0.39194.
- v121 all-Madman-zero private: 0.38844, so that strategy is rejected.
- v127/v128 are score-only candidates from v119:
  - v127: Werewolf score floor 0.5, public local 0.4612.
  - v128: v127 + guarded Madman zero, public local 0.4618.

## Experiment Lane A: Structured LLM Audit

1. Run qwen3.5:9b on a small public subset with structured JSON audit.
2. Apply conservative score-only solver to v119 public.
3. Score public local.
4. If positive, run all public; if still positive, run private.

## Experiment Lane B: Dual-LLM Agreement

After Lane A works, repeat with deepseek-r1:14b and only change cells when qwen/deepseek agree on direction.

## Install/Tooling Policy

- Use `uv run` from `werewolf-project/`.
- No `pip install` into the user environment.
- Dependencies should come from `werewolf-project/pyproject.toml` / `uv.lock`.
- Do not add external API SDKs.

## Git Hygiene

- Work on `dev/structured-llm-rag-audit` only.
- Do not `git add .` because the repo contains large media/data.
- If committing later, add only scripts/docs/submission candidates explicitly.

## Immediate Commands

```bash
cd werewolf-project
UV_CACHE_DIR=.uv-cache uv run python scripts/structured_llm_audit.py run --split public --model qwen3.5:9b --limit 3 --num-ctx 8192
UV_CACHE_DIR=.uv-cache uv run python scripts/structured_llm_audit.py apply ../experiments/submissions/submission_v119_swap_public.csv --split public --model qwen3.5:9b --output ../experiments/submissions/submission_v129_structured_qwen_public.csv
UV_CACHE_DIR=.uv-cache uv run python ../experiments/scripts/local_score.py ../experiments/submissions/submission_v129_structured_qwen_public.csv --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv
```


## VRAM policy

Use `ollama ps` model `SIZE` as the primary compliance check. Do not use whole-GPU `nvidia-smi used` as the model-size estimate. Keep `--num-ctx 8192` for speed/margin unless evidence shows longer context helps.

## Results update: candidate-focused audit

Full-game `v129_structured` prompts were rejected for scoring use: qwen3.5 often returned a valid JSON object but with a summary schema instead of the required `players[]` audit schema. Those caches should not drive submissions.

`v130_candidate` uses a shorter candidate-only prompt over rows that matter for Wolf-AP ordering. This produced parseable audits quickly with local qwen3.5:9b at `num_ctx=4096`.

Public results from v119 base:

| Candidate | Description | Public local |
| --- | --- | ---: |
| v130 | qwen candidate audit, allows demoting predicted Werewolf rows | 0.4671 |
| **v131** | safe qwen candidate audit: floor low predicted-Werewolves; demote only non-Werewolf candidates | **0.4690** |

Recommended next Kaggle upload: `experiments/submissions/submission_v131_candidate_qwen_safe_private.csv`.

Why v131 over v130: public local is better and it avoids allowing the LLM to overturn predicted Werewolf rows, consistent with the earlier lesson that aggressive role-side changes generalized poorly.
