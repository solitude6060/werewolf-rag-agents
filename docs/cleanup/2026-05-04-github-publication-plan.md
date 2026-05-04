# GitHub Publication Plan

Date: 2026-05-04
Branch: `dev/structured-llm-rag-audit`

## Repository Name

Recommended GitHub repository name: `werewolf-rag-agents`

Why:

- `werewolf` identifies the task/domain.
- `rag` identifies the retrieval/evidence layer.
- `agents` identifies the multi-agent architecture.
- It is short enough for URLs and clear enough for coursework presentation.

## Publication Scope

Publish code, tests, docs, and small legacy artifacts already tracked in the repo.

Do not publish ignored/raw artifacts unless explicitly reviewed:

- `data/raw/`
- `.venv/`, `.uv-cache/`, `.pytest_cache/`
- outer `../experiments/llm_runs/`
- outer `../experiments/submissions/` unless a specific CSV is intentionally copied into a release package

## Files to Add

| File | Purpose |
| --- | --- |
| `LICENSE` | MIT license for project code. |
| `DATASETS.md` | Explain dataset is excluded and must be obtained from the course/Kaggle source. |
| `CONTRIBUTING.md` | Development and validation workflow. |
| `SECURITY.md` | Responsible disclosure and secret/data handling notes. |
| `CITATION.cff` | Citation metadata for GitHub. |
| `.github/workflows/ci.yml` | GitHub Actions test workflow. |
| `.github/ISSUE_TEMPLATE/*.md` | Bug/experiment report templates. |
| `.github/pull_request_template.md` | PR checklist. |

## Verification

After adding docs/metadata:

```bash
cd werewolf-project
UV_CACHE_DIR=.uv-cache uv run pytest tests/ -q
UV_CACHE_DIR=.uv-cache uv run python assert/validate_submission.py ../experiments/submissions/submission_v144_filtered_big_gamble_private.csv
UV_CACHE_DIR=.uv-cache uv run python scripts/candidate_llm_audit.py --help
```

## Push Plan

If creating manually on GitHub:

```bash
git remote add origin git@github.com:<owner>/werewolf-rag-agents.git
git push -u origin dev/structured-llm-rag-audit
```

If using GitHub CLI:

```bash
gh repo create <owner>/werewolf-rag-agents --private --source=. --remote=origin --push
```

Use `--private` by default until course/data publication policy is confirmed.
