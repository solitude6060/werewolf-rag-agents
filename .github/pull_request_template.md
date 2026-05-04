## Summary

## Scope

- [ ] Docs only
- [ ] Tests only
- [ ] Prediction behavior
- [ ] Experiment tooling
- [ ] Submission artifact

## Validation

```bash
UV_CACHE_DIR=.uv-cache uv run pytest tests/ -q
```

If a submission candidate changed:

```bash
UV_CACHE_DIR=.uv-cache uv run python assert/validate_submission.py <candidate_private.csv>
```

## Risk Notes

## Data/Secret Check

- [ ] No raw course/Kaggle dataset files are committed.
- [ ] No private labels or local LLM transcript caches are committed.
- [ ] No credentials, tokens, or `.env` files are committed.
