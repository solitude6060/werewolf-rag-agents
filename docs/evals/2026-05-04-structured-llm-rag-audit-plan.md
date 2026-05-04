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


## Kaggle update

`submission_v131_candidate_qwen_safe_private.csv` scored **0.40434 private**, improving v119 by +0.01240. Continue from v131 for the final sprint; prioritize score-ordering variants and additional local LLM agreement, not broad role swaps.

## Final sprint after v131 private score

Kaggle private confirmed: `submission_v131_candidate_qwen_safe_private.csv` = **0.40434**.

Final candidate generated:

- `experiments/submissions/submission_v136_final_qwen_safe_zero_private.csv`
- Public local: **0.4691** (`AP=0.4909`), slightly above v131 public 0.4690.
- Private validation: OK, 397 rows.
- Difference vs v131: only seven qwen-demoted non-Werewolf candidates move from `0.05` to `0.0`; roles and Werewolf floor logic unchanged.

Deepseek candidate audit was tested but rejected for final use: public local dropped to 0.4544 when used directly; qwen/deepseek agreement variants also underperformed v131/v136 public local. Use v136 only if the final attempt should be a minimal-risk refinement over the already-successful v131.

## Big-gamble LLM disagreement sprint

After v131 scored 0.40434 private, we tested riskier Werewolf demotion variants using cached local qwen3.5:9b and deepseek-r1:14b candidate audits. The goal was to improve Wolf-AP ordering without violating the assignment: all reasoning is from local Ollama models and existing transcripts/features; no external labels or API calls are used.

Key public/local results from v136 base:

| Candidate | Private file | Public local | Private changes vs v136 | Rationale |
| --- | --- | ---: | --- | --- |
| v138 | `../experiments/submissions/submission_v138_bothllm_wwdemote_private.csv` | 0.4707 | Demote only game 14 Boy Peter | qwen and deepseek both say demote; conservative big-gamble. |
| v144 | `../experiments/submissions/submission_v144_filtered_big_gamble_private.csv` | **0.4750** | Demote game 14 Boy Peter, 17 Baker Otto, 23 Young Girl Liza | Public-calibrated filter: qwen demote + deepseek ambiguous-high `wolf_prob>=0.49`, excluding qwen hard-lock + deepseek keep contradictions. |
| v132 | `../experiments/submissions/submission_v132_qwen_floor_045_private.csv` | 0.4696 | Broad qwen demotions plus lower floor | Rejected as less defensible; private qwen evidence contained attacked/night-kill hallucinations. |

Recommendation if only one final upload remains:

1. Submit `submission_v144_filtered_big_gamble_private.csv` only if accepting a genuine high-variance final attempt. It has the best new public local score (0.4750) and avoids the most suspicious qwen-lock/deepseek-keep private case.
2. Use `submission_v138_bothllm_wwdemote_private.csv` if wanting a smaller gamble over v136/v131.
3. Do not submit v132 unless intentionally ignoring the private evidence audit; its public score is weaker than v144 and its evidence quality is worse.

Validation evidence:

```bash
cd werewolf-project
UV_CACHE_DIR=.uv-cache uv run python ../experiments/scripts/local_score.py ../experiments/submissions/submission_v144_filtered_big_gamble_public.csv --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv --quiet
# submission_v144_filtered_big_gamble_public.csv F1=0.4363 AP=0.5007 Score=0.4750
UV_CACHE_DIR=.uv-cache uv run python assert/validate_submission.py ../experiments/submissions/submission_v144_filtered_big_gamble_private.csv
# OK: 397 predictions validated
```
