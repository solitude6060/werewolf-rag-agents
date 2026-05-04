# Contributing

This project follows a spec-first, test-first workflow because leaderboard changes are easy to overfit.

## Development Setup

```bash
uv sync
UV_CACHE_DIR=.uv-cache uv run pytest tests/ -q
```

## Branching

- Use feature/dev branches.
- Keep `main` or release branches stable.
- Prefer small commits with validation evidence.

## Before Changing Prediction Behavior

1. Read the relevant spec/design document in `docs/sdd/`.
2. Add or run tests that lock current behavior.
3. Document non-trivial plans in `docs/cleanup/` or `docs/evals/`.
4. Keep generated submissions and raw data out of git unless explicitly approved.

## Required Checks

Run from `werewolf-project/`:

```bash
UV_CACHE_DIR=.uv-cache uv run pytest tests/ -q
UV_CACHE_DIR=.uv-cache uv run python assert/validate_submission.py <candidate_private.csv>
```

For public candidates with ground truth available:

```bash
UV_CACHE_DIR=.uv-cache uv run python ../experiments/scripts/local_score.py <candidate_public.csv> \
  --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv \
  --quiet
```

## Commit Style

Use concise decision-oriented commits. Include:

- why the change exists,
- what was tested,
- what was not tested,
- risk/scope notes when relevant.
