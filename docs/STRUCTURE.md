# Folder Structure

This project is organized to separate four concerns: runtime code, experiment tools, documentation, and archived artifacts.

## Current Layout

```text
werewolf-project/
├── README.md
├── main.py
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── assert/
│   └── validate_submission.py
├── data/
│   └── .gitkeep
├── docs/
│   ├── PROJECT_GUIDE.md
│   ├── EXPERIMENTS.md
│   ├── STRUCTURE.md
│   ├── archive/
│   │   ├── notes.md
│   │   └── task_plan.md
│   ├── cleanup/
│   ├── evals/
│   ├── report/
│   └── sdd/
├── artifacts/
│   └── legacy-submissions/
│       └── hw2_D13922024/
├── scripts/
│   ├── audits/
│   │   ├── candidate_llm_audit.py
│   │   └── structured_llm_audit.py
│   ├── postprocess/
│   │   └── leaderboard_informed_fixes.py
│   ├── candidate_llm_audit.py
│   ├── structured_llm_audit.py
│   └── leaderboard_informed_fixes.py
├── src/
│   ├── agents/
│   ├── data/
│   ├── rag/
│   ├── utils/
│   ├── model_adapter.py
│   └── pipeline.py
└── tests/
    ├── integration/
    └── unit/
```

## Directory Responsibilities

| Directory | Responsibility |
| --- | --- |
| `src/` | Importable prediction package and multi-agent pipeline. |
| `tests/` | Unit/integration tests that lock current behavior. |
| `assert/` | Assignment-facing submission validator; kept at top-level for packaging compatibility. |
| `scripts/audits/` | Local LLM audit scripts using Ollama and transcript evidence. |
| `scripts/postprocess/` | Score-only post-processing utilities. |
| `scripts/*.py` | Thin compatibility wrappers for old commands. New code should import/run files in subfolders. |
| `docs/sdd/` | Spec-driven design documents. |
| `docs/evals/` | Experiment/evaluation logs. |
| `docs/cleanup/` | Planning-with-files cleanup and restructure records. |
| `docs/archive/` | Historical notes/plans kept for audit trail, not the current entry point. |
| `artifacts/legacy-submissions/` | Old generated prediction CSV bundles retained for reproducibility. |
| `data/` | Runtime data location; raw/interim/submission files are ignored by git. |

## External Experiment Workspace

The active leaderboard artifacts remain one level above this repo:

```text
../experiments/submissions/   # generated public/private CSV candidates
../experiments/llm_runs/      # local Ollama audit caches
../experiments/scripts/       # variant generation and scoring utilities
../hand-over.md               # long chronological hand-over record
```

These were not moved because they are large, rapidly changing, and shared by multiple worktrees/experiments.

## Command Compatibility

Old commands still work:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/candidate_llm_audit.py --help
```

Preferred new commands use the organized subfolders:

```bash
UV_CACHE_DIR=.uv-cache uv run python scripts/audits/candidate_llm_audit.py --help
UV_CACHE_DIR=.uv-cache uv run python scripts/postprocess/leaderboard_informed_fixes.py --help
```

