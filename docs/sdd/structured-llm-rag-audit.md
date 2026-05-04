# SDD: Structured Local-LLM RAG Audit for Werewolf Prediction

Last updated: 2026-05-04
Branch: `dev/structured-llm-rag-audit`

## Goal

Improve Kaggle private score without violating HW2 constraints by using local LLMs more effectively as evidence auditors, not as unconstrained role replacers.

## HW2 Constraints

- Multi-agent system with at least two agents.
- RAG required.
- No model training or fine-tuning.
- No external API.
- Avoid models requiring more than 12GB VRAM.
- Final metric: `0.4 * Macro-F1 + 0.6 * Wolf-AP`.

Allowed models for this lane:

- `qwen3.5:9b` (local Ollama, 6.6GB model file)
- `deepseek-r1:14b` (local Ollama, 9.0GB model file)
- Avoid `qwen3.5:27b`, `qwen3.6:27b`, `gemma4:26b`, `gpt-oss:20b`.

## Architecture

```text
Transcript + roles.csv
  -> Evidence/RAG Agent (deterministic parser + role handbook snippets)
  -> Structured LLM Analyst Agent (qwen/deepseek, think:false, JSON audit)
  -> Conservative Scoring Solver (score-only or guarded changes)
  -> CSV Validator + public local scorer
```

## Structured Reasoning Contract

We do not request hidden/free-form CoT. The LLM must output compact structured rationale fields:

- `wolf_prob`: calibrated wolf-likelihood for AP ordering
- `wolf_rank`: per-game ranking
- `nonwolf_lock`: true for hard non-wolf evidence such as night-killed players
- `key_evidence`: short evidence phrases
- `risk_note`: short uncertainty note

This gives inspectable reasoning while keeping output parseable and avoiding role-count chaos.

## RAG Sources

- Role/rule handbook embedded in `structured_llm_audit.py`
- Deterministic extracted features from `werewolf_variants.features()`
- Retrieved transcript snippets selected by keyword/event regex

## Safety/Generalization Rules

- Prefer score-only changes before role changes.
- Use public local score only as a filter, not as proof of private improvement.
- v121 private failed, so do not blindly zero all Madman scores.
- v120 private failed, so do not aggressively swap special roles.
- Every candidate must preserve CSV schema and score range `[0,1]`.

## Validation

- `UV_CACHE_DIR=.uv-cache uv run python scripts/structured_llm_audit.py ...`
- `UV_CACHE_DIR=.uv-cache uv run python ../experiments/scripts/local_score.py <public.csv> --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv`
- `UV_CACHE_DIR=.uv-cache uv run python assert/validate_submission.py <private.csv>`
- `uv run python -m py_compile <changed scripts>`

## Stop Conditions

- Stop a candidate lane if public local drops materially or changes exceed conservative scope without evidence.
- Promote to private only if public local improves or the change is logically safer than the public delta suggests.


## VRAM Measurement Policy

Do not judge HW2 model compliance from whole-GPU `nvidia-smi` total used memory, because it includes drivers, unrelated services, and background processes. For Ollama runs, use `ollama ps` model `SIZE` as the primary compliance signal, with `nvidia-smi` only as auxiliary operational evidence. `qwen3.5:9b` is acceptable when `ollama ps` reports model size below 12GB; context is kept at 8192 by default for speed and margin, not because 32768 was proven non-compliant.


## Path note after folder restructure

Preferred organized script path: `scripts/audits/structured_llm_audit.py` and `scripts/audits/candidate_llm_audit.py`. Older commands using `scripts/structured_llm_audit.py` or `scripts/candidate_llm_audit.py` still work through compatibility wrappers.
