# Experiments and Leaderboard Notes

This document is the concise experiment guide. The long chronological log remains in `../hand-over.md`, and detailed final-sprint notes are in `docs/evals/2026-05-04-structured-llm-rag-audit-plan.md`.

## 1. Current Best

| Submission | Kaggle private | Notes |
| --- | ---: | --- |
| `submission_v119_swap_private.csv` | 0.39194 | Earlier best before LLM candidate audit. |
| `submission_v131_candidate_qwen_safe_private.csv` | 0.40434 | Major breakthrough; safe qwen candidate audit. |
| `submission_v144_filtered_big_gamble_private.csv` | **0.40743** | Latest best; filtered qwen/deepseek disagreement gamble. |

## 2. Final Candidate Ranking

| Candidate | File | Public local | Private result | Risk |
| --- | --- | ---: | ---: | --- |
| v144 | `../experiments/submissions/submission_v144_filtered_big_gamble_private.csv` | **0.4750** | **0.40743** | Medium/high but now verified best. |
| v138 | `../experiments/submissions/submission_v138_bothllm_wwdemote_private.csv` | 0.4707 | Not uploaded | Lower variance than v144. |
| v136 | `../experiments/submissions/submission_v136_final_qwen_safe_zero_private.csv` | 0.4691 | Not uploaded | Minimal-risk refinement over v131. |
| v132 | `../experiments/submissions/submission_v132_qwen_floor_045_private.csv` | 0.4696 | Not uploaded | Rejected: broad qwen demotion with hallucinated evidence risk. |

## 3. Score Progression

| Version | Kaggle private | Main idea | Lesson |
| --- | ---: | --- | --- |
| v70 | 0.39031 | Strong rule baseline | Stable local optimum. |
| v110 | 0.39124 | qwen/deepseek consensus score adjustment | LLMs help when constrained. |
| v119 | 0.39194 | conservative per-game swap | Small safe role changes can help. |
| v120 | 0.38716 | any-role swap | Aggressive special-role swaps hurt private. |
| v121 | 0.38844 | all Madman score zero | Public logic did not generalize. |
| v131 | 0.40434 | safe qwen candidate audit | Candidate-level LLM audit was the breakthrough. |
| v144 | 0.40743 | filtered qwen/deepseek disagreement | Carefully filtered higher variance can still improve. |

## 4. Final v144 Policy

Base: v136/v131-style safe qwen candidate audit.

Additional private changes vs v136: demote three predicted Werewolf rows to `wolf_score=0.05`:

- Game 14 — Boy Peter
- Game 17 — Baker Otto
- Game 23 — Young Girl Liza

Selection rule:

- qwen audit asks to demote the predicted Werewolf row, and
- deepseek still reports ambiguous-high `wolf_prob >= 0.49`, and
- exclude the worst contradiction type: qwen `nonwolf_lock=true` with deepseek `decision=keep`.

Why this is defensible:

- It is score-only; roles are preserved.
- It changes only three private rows.
- It outperformed v136/v138/v132 on public local validation.
- It was validated by Kaggle private after upload: 0.40743.

## 5. Important Failures

| Experiment | Outcome | Why it matters |
| --- | --- | --- |
| Full LLM role prediction | Poor local scores | Local LLMs are not reliable as full solvers. |
| Full-game structured qwen JSON | Schema drift | Candidate-only prompts are more stable. |
| Any-role swaps | Private drop | Do not casually replace Hunter/Seer/Medium assignments. |
| Broad qwen demotion | Risky | Qwen sometimes hallucinated attacked/night-kill evidence. |
| Direct deepseek candidate application | Public local 0.4544 | Deepseek alone was not a good final solver. |

## 6. Validation Commands

```bash
cd werewolf-project
UV_CACHE_DIR=.uv-cache uv run pytest tests/ -q
UV_CACHE_DIR=.uv-cache uv run python assert/validate_submission.py \
  ../experiments/submissions/submission_v144_filtered_big_gamble_private.csv
UV_CACHE_DIR=.uv-cache uv run python ../experiments/scripts/local_score.py \
  ../experiments/submissions/submission_v144_filtered_big_gamble_public.csv \
  --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv \
  --quiet
```

Current expected output summary:

```text
71 passed, 3 warnings
OK: 397 predictions validated
F1=0.4363 AP=0.5007 Score=0.4750
```

