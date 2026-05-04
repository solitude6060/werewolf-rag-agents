# Folder Restructure Plan

Date: 2026-05-04
Branch: `dev/structured-llm-rag-audit`

## Intent

Reorganize `werewolf-project/` into a teaching-friendly layout while preserving existing command compatibility and final submission behavior.

## Non-goals

- Do not move outer `../experiments/` submissions or `../experiments/llm_runs/` caches in this pass.
- Do not change prediction logic or generated CSV contents.
- Do not remove old artifacts; archive them under a clearer path instead.
- Do not rename the package/import root `src/` during the active leaderboard sprint.

## Behavior Lock

Before restructure, the previous cleanup pass established:

- `UV_CACHE_DIR=.uv-cache uv run pytest tests/ -q` -> 71 passed, 3 warnings.
- `validate_submission.py` on v144 private -> OK, 397 rows.
- `local_score.py` on v144 public -> Score 0.4750.

These checks must pass after restructuring.

## Target Layout

```text
werewolf-project/
├── README.md
├── main.py
├── pyproject.toml
├── requirements.txt
├── assert/                         # assignment-required validator path
├── data/                           # ignored raw/interim/submission data + .gitkeep
├── docs/
│   ├── PROJECT_GUIDE.md
│   ├── EXPERIMENTS.md
│   ├── STRUCTURE.md                # new folder map
│   ├── archive/                    # old notes/plans moved here
│   ├── cleanup/                    # cleanup/restructure plans
│   ├── evals/
│   ├── report/
│   └── sdd/
├── artifacts/
│   └── legacy-submissions/         # old packaged predictions kept for audit
├── scripts/
│   ├── audits/                     # local LLM audit scripts
│   ├── postprocess/                # score post-processing scripts
│   └── *.py                        # thin compatibility wrappers
├── src/
└── tests/
```

## Moves

| Old path | New path | Compatibility |
| --- | --- | --- |
| `scripts/candidate_llm_audit.py` | `scripts/audits/candidate_llm_audit.py` | Keep wrapper at old path. |
| `scripts/structured_llm_audit.py` | `scripts/audits/structured_llm_audit.py` | Keep wrapper at old path. |
| `scripts/leaderboard_informed_fixes.py` | `scripts/postprocess/leaderboard_informed_fixes.py` | Keep wrapper at old path. |
| `notes.md` | `docs/archive/notes.md` | README/docs point to new location. |
| `task_plan.md` | `docs/archive/task_plan.md` | README/docs point to new location. |
| `hw2_D13922024/` | `artifacts/legacy-submissions/hw2_D13922024/` | Archive only; not final upload path. |

## Verification

Run after edits:

```bash
cd werewolf-project
UV_CACHE_DIR=.uv-cache uv run pytest tests/ -q
UV_CACHE_DIR=.uv-cache uv run python assert/validate_submission.py ../experiments/submissions/submission_v144_filtered_big_gamble_private.csv
UV_CACHE_DIR=.uv-cache uv run python ../experiments/scripts/local_score.py ../experiments/submissions/submission_v144_filtered_big_gamble_public.csv --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv --quiet
UV_CACHE_DIR=.uv-cache uv run python scripts/candidate_llm_audit.py --help
UV_CACHE_DIR=.uv-cache uv run python scripts/audits/candidate_llm_audit.py --help
```

## Stop Condition

Stop when the new layout is committed, wrappers work, tests pass, and docs describe where to find everything.
