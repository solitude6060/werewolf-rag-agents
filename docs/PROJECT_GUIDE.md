# Project Guide — Teaching Version

This guide explains the Werewolf HW2 project as if presenting it in class: problem framing, architecture, data flow, and how the final leaderboard improvements were produced without violating the assignment rules.

## 1. Problem

Input: Werewolf game transcripts plus player metadata.

Output: one CSV row per player:

```csv
id,index,character,role,wolf_score
```

The score combines role prediction quality and Werewolf ranking quality. The most important optimization lesson was that `wolf_score` ordering matters heavily, so later experiments focused on Wolf-AP-safe score repairs instead of broad role rewrites.

## 2. Assignment Constraints

| Constraint | How this project satisfies it |
| --- | --- |
| Multi-agent system | Stage 1 fetching, Stage 2 analysis, Stage 3 solver; final sprint also uses qwen/deepseek as independent local audit agents. |
| RAG/retrieval | Transcript events, player features, role rules, and candidate snippets are retrieved before analysis. |
| Local models | Ollama local models only (`qwen3.5:9b`, `deepseek-r1:14b`). |
| No training/fine-tuning | All improvements are inference-time prompting, deterministic features, constraints, and post-processing. |
| VRAM limit | Final LLMs are under the project’s model-size budget; `gpt-oss:20b`/27B-class models were rejected. |
| Submission format | `assert/validate_submission.py` verifies header, roles, scores, and row count. |

## 3. Architecture

```text
Raw transcript + roles.csv
        |
        v
Stage 1: Fetching Agent
- Extract talks, claims, votes, attacks, divination-like statements
- Produce structured evidence
        |
        v
Stage 2: Analysis Agent
- Convert evidence into role/wolf likelihood signals
- Use RAG-style rule context and transcript features
        |
        v
Stage 3: Constrained Solver
- Enforce role-count constraints
- Produce role and wolf_score predictions
        |
        v
Submission validator + local scoring
```

The final high-scoring lane adds a **candidate audit layer**:

```text
Existing strong submission
        |
        v
Candidate selector
- low-score predicted Werewolves
- high-score non-Werewolves
- moderate/high Madmen
        |
        v
Local LLM audit agents
- qwen3.5:9b
- deepseek-r1:14b
        |
        v
Score-only policy
- avoid broad role swaps
- mostly preserve roles
- adjust wolf_score ordering for Wolf-AP
```

## 4. Important Files

| Path | Purpose |
| --- | --- |
| `main.py` | CLI for baseline predictions. |
| `src/agents/stage1_fetching.py` | Evidence extraction agent. |
| `src/agents/stage2_analysis.py` | Analysis/probability agent. |
| `src/agents/stage3_solver.py` | Constraint-based role assignment. |
| `src/rag/` | RAG corpus/retrieval utilities. |
| `scripts/candidate_llm_audit.py` | Final local LLM audit workflow. |
| `scripts/structured_llm_audit.py` | Earlier full-game structured audit attempt; retained for audit trail. |
| `scripts/leaderboard_informed_fixes.py` | Conservative post-processing utilities. |
| `assert/validate_submission.py` | Required output validation. |
| `docs/EXPERIMENTS.md` | Score progression and final candidate guide. |

## 5. Why the Final Strategy Worked

Earlier attempts showed that LLMs are weak as full role predictors, but useful as **auditors for suspicious rows**. The final strategy therefore does not ask an LLM to solve the game from scratch. Instead, it asks local LLMs to inspect only rows that can affect Werewolf AP ordering.

Key lessons:

1. **Do not broadly rewrite roles.** Aggressive role swaps improved public but hurt private.
2. **Optimize Wolf-AP carefully.** Many improvements came from reordering `wolf_score` while preserving roles.
3. **Use LLMs as bounded reviewers.** Candidate-level prompts were more reliable than full-game JSON prompts.
4. **Keep an audit trail.** Every final candidate has a public counterpart, validation command, and rationale.

## 6. Reproducible Validation

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

Expected current evidence:

```text
71 passed, 3 warnings
OK: 397 predictions validated
Score=0.4750
```

## 7. Presentation Outline

For a homework presentation/report, use this story:

1. Define the task and metric.
2. Explain the three-agent baseline architecture.
3. Explain RAG/evidence extraction from transcripts.
4. Show failed experiments: full LLM prediction, broad role swaps, broad Madman/Werewolf demotion.
5. Show successful experiments: conservative consensus, per-game safe swaps, candidate-level local LLM audit.
6. Conclude with why v144 improved: high-variance but filtered score-only changes.

