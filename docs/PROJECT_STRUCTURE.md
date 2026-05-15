# Project Structure Guide

This guide explains the public `main` branch layout and the purpose of the tracked artifacts.

## Top-level map

| Path | Purpose | Audience |
| --- | --- | --- |
| `README.md` | Public landing page and quick start | Reviewers, maintainers |
| `README.zh-TW.md` | Traditional Chinese public landing page | Local review |
| `docs/TECHNICAL_REPORT.md` | Detailed English technical report | Technical reviewers |
| `docs/TECHNICAL_REPORT.zh-TW.md` | Detailed Traditional Chinese technical report | Course/report review |
| `docs/REPRODUCIBILITY.md` | Reproduction and validation runbook | Anyone rerunning outputs |
| `hw2_D13922024/` | Self-contained coursework package | Submission reviewer |
| `experiments/final_submission_package/` | Candidate archive, manifests, reports, upload state | Submission operations |
| `experiments/scripts/` | Packaging, routing, and guard scripts | Maintainers |
| `werewolf-project/assert/validate_submission.py` | Submission format validator | QA / preflight |

## Packaged HW2 folder

```text
hw2_D13922024/
├── make_final.py                         Fast reproduction entry point
├── main.py                               Pipeline CLI entry point
├── submission.csv                        Current branch packaged CSV
├── hw2_report.md                         English coursework report
├── hw2_report.zh-TW.md                   Traditional Chinese coursework report
├── requirements.txt                      Python package requirements
├── assert/validate_submission.py         CSV validator
├── checkpoints/                          Reproducible CSV checkpoints
├── pipeline_steps/                       Stepwise scripts used in the report
└── src/                                  Pipeline modules
```

## Pipeline modules

| Module | Role |
| --- | --- |
| `src/data/schema.py` | Pydantic data models for roles, players, events, submissions, and constraints |
| `src/data/loader.py` | Dataset loading and transcript discovery |
| `src/rag/corpus.py` | Static Werewolf rules and terminology corpus |
| `src/rag/retriever.py` | Simple/BM25 retrieval over rule snippets |
| `src/agents/stage1_fetching.py` | Regex-driven extraction of statements, votes, deaths, and claims |
| `src/agents/stage2_analysis.py` | Player-level evidence scoring and wolf-score estimation |
| `src/agents/stage3_solver.py` | Role-budget assignment and final wolf-score normalization |
| `src/model_adapter.py` | Optional local model adapters through Ollama or llama.cpp |
| `src/pipeline.py` | End-to-end prediction orchestration |

## Submission archive

```text
experiments/final_submission_package/
├── current_upload/                       Current upload candidate and metadata
├── upload_batch_2026-05-15_extra3/       Three fixed validated upload candidates
├── manifests/                            Candidate manifest, score records, validation logs
├── reports/                              Audit, preflight, and strategy reports
├── queue/ overlay/ black_boost_queue/    Candidate families
└── README.md                             Archive-level runbook
```

## What should not be treated as public deliverables

The local workspace may contain untracked cache, video, browser, worktree, and local state files.  The public project should rely on tracked files only.  Check with:

```bash
git ls-files
```
