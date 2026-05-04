# Project Teaching Cleanup Plan

Date: 2026-05-04
Branch: `dev/structured-llm-rag-audit`

## Intent

Make the project readable as a homework/teaching artifact without changing prediction behavior, generated submissions, or competition scripts.

## Behavior Lock

Before cleanup:

- `UV_CACHE_DIR=.uv-cache uv run pytest tests/ -q` -> 71 passed, 3 known Pydantic v2 warnings.
- `UV_CACHE_DIR=.uv-cache uv run python assert/validate_submission.py ../experiments/submissions/submission_v144_filtered_big_gamble_private.csv` -> OK, 397 predictions.
- `UV_CACHE_DIR=.uv-cache uv run python ../experiments/scripts/local_score.py ../experiments/submissions/submission_v144_filtered_big_gamble_public.csv --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv --quiet` -> Score 0.4750.

## Scope

Documentation and navigation only:

- `README.md`
- `docs/PROJECT_GUIDE.md`
- `docs/EXPERIMENTS.md`
- `docs/cleanup/2026-05-04-project-teaching-cleanup-plan.md`

No source-code refactor, no data movement, no submission rewriting in this pass.

## Smells to Remove

| Finding | Category | Severity | Fix in this pass | Rationale |
| --- | --- | --- | --- | --- |
| README is generic and misses final competition workflow | Missing documentation | High | Yes | It is the first teaching entry point. |
| Experiment history is split between hand-over and eval notes | Documentation scatter | High | Yes | Students/readers need a concise map. |
| Final submission candidates are hard to identify | Missing release notes | High | Yes | Prevents uploading the wrong file. |
| Some old scripts/results remain for audit trail | Dead-looking artifacts | Medium | No | Keep for reproducibility until a separate archival pass. |
| Pydantic v2 warnings | Technical debt | Low | No | Behavior-changing code cleanup belongs in a separate test-first pass. |

## Fallback-like Code Inventory

No code edits in this pass. Existing fallback-like logic is deferred because the requested outcome is project readability, not runtime refactor.

## Execution Order

1. Rewrite root project README as a teaching-oriented entry point.
2. Add `docs/PROJECT_GUIDE.md` for architecture, data flow, and assignment compliance.
3. Add `docs/EXPERIMENTS.md` for leaderboard history, final candidates, and lessons.
4. Re-run behavior lock commands.
5. Commit only documentation changes using Lore commit protocol.

## Stop Condition

Stop after docs make the project navigable and validation evidence remains unchanged.
