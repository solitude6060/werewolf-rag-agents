# Final Submission / Report Pack Plan

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`
Owner: workspace automation

## Goal

Create a reproducible final-pack workflow that, with one command, can regenerate the current upload queue, the current top known submissions, and assignment-structured Markdown report artifacts for HW2.

This is **packaging/reporting work**, not a new Kaggle upload or a new score-search iteration.

## Assignment requirements used as source of truth

From `HW2-Multi-Agent Werewolf Prediction.pdf`:

- Performance ranking is 80% on Kaggle private leaderboard.
- Report is 20% and must briefly explain:
  - RAG system design, issues faced, and solutions.
  - Design structure / prompt design diagram (5%).
  - Discussion of success and failure cases (5%).
  - Optimizations and improvements (10%).
- Report page limit: within 5 pages.
- Upload package: `hw2_<student-id>.zip` containing:
  - `hw2_<student-id>.pdf`
  - `main.py`
  - `assert/`
  - `requirements.txt`
  - `README`
- Deadline: 2026-05-15 23:59.
- Constraints: at least two agents; no training/fine-tuning; no external API; avoid models requiring more than 12GB VRAM.

## Inputs

### Current verified top known private submissions

| Rank | Candidate | Private score | Path |
| ---: | --- | ---: | --- |
| 1 | v1824a | 0.47119 | `experiments/submissions/submission_v1824a_v1823a_plus_g24_thomas_trueseer_private.csv` |
| 2 | v1823a | 0.46492 | `experiments/submissions/submission_v1823a_v1821a_plus_v1819b_positive_stack_private.csv` |
| 3 | v1823b | 0.46492 | `experiments/submissions/submission_v1823b_v1821a_v1819b_plus_g30_dieter_private.csv` |
| 4 | v1821a | 0.46455 | `experiments/submissions/submission_v1821a_claimgraph_g10_pamela_repair_private.csv` |
| 5 | v1819b | 0.45499 | `experiments/submissions/submission_v1819b_v1817b_v1818a_private.csv` |

### Current final upload queue candidates

Use the v1833 queue as the conservative normal five-attempt plan:

1. `01_v1826a_primary_first_private.csv`
2. `02_v1826b_if_01_positive_private.csv`
3. `03_v1826d_if_02_positive_private.csv`
4. `04_v1826c_alt_structural_private.csv`
5. `05_v1829e_clean_hailmary_private.csv`

Use the v1850 low-tail queue as the highest public-proxy final sprint plan:

1. `01_v1850a_queue01_v1848a_lowtail_private.csv`
2. `02_v1850b_queue02_v1848b_lowtail_private.csv`
3. `03_v1850c_queue03_v1848c_lowtail_private.csv`
4. `04_v1850d_queue04_v1848d_lowtail_private.csv`
5. `05_v1850e_queue05_v1848e_lowtail_private.csv`

Use the v1853 character-prior queue as the highest local public-proxy, highest calibration-risk final sprint plan:

1. `01_v1853a_queue01_v1850a_charprior_private.csv`
2. `02_v1853b_queue02_v1850b_charprior_private.csv`
3. `03_v1853c_queue03_v1850c_charprior_private.csv`
4. `04_v1853d_queue04_v1850d_charprior_private.csv`
5. `05_v1853e_queue05_v1850e_charprior_private.csv`

Use the v1856 balanced-prior queue as the risk-balanced calibration sprint plan:

1. `01_v1856a_queue01_v1850a_balancedprior_private.csv`
2. `02_v1856b_queue02_v1850b_balancedprior_private.csv`
3. `03_v1856c_queue03_v1850c_balancedprior_private.csv`
4. `04_v1856d_queue04_v1850d_balancedprior_private.csv`
5. `05_v1856e_queue05_v1850e_balancedprior_private.csv`

## Planned outputs

Add a new one-command generator:

- `experiments/scripts/v1835_final_submission_pack.py`

Default command:

```bash
python3 experiments/scripts/v1835_final_submission_pack.py --preset full
```

Expected generated package root:

- `experiments/final_submission_package/README.md`
- `experiments/final_submission_package/queue/*.csv`
- `experiments/final_submission_package/known_best/*.csv`
- `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv`
- `experiments/final_submission_package/manifests/validation_log.txt`
- `experiments/final_submission_package/reports/hw2_report_draft.md`
- `experiments/final_submission_package/reports/submission_strategy.md`
- `experiments/final_submission_package/reports/reproducibility_checklist.md`
- `experiments/final_submission_package/cool_package/hw2_D13922024/` as a COOL zip staging folder mirroring the required structure, with report Markdown as the PDF source.

The generator must support at least:

- `--preset queue`: only final upload queue.
- `--preset known-best`: only current verified top known submissions.
- `--preset contingency`: adaptive reserve candidates for score-response routing.
- `--preset rolecap-queue`: role-cap AP calibration queue.
- `--preset denoise-queue`: denoise AP calibration queue.
- `--preset lowtail-queue`: absolute highest public-proxy AP calibration queue.
- `--preset charprior-queue`: highest local public-proxy character-prior calibration queue.
- `--preset balancedprior-queue`: risk-balanced character-prior calibration queue.
- `--preset full`: queue + known-best + report artifacts.
- `--skip-validation`: generate without running validators when speed is needed.

Additional active-goal support:

- Add `experiments/scripts/v1836_score_feedback_router.py` so tomorrow's real Kaggle score can be mapped to the next queue/contingency file without manual path mistakes.

## Validation standards

- `python3 -m py_compile experiments/scripts/v1835_final_submission_pack.py`
- `python3 -m py_compile experiments/scripts/v1836_score_feedback_router.py`
- Run default full generation.
- Validate every generated private CSV with `werewolf-project/assert/validate_submission.py`.
- Confirm row count is 397 predictions for every generated CSV.
- Confirm generated manifest records SHA256 and source paths.
- Run router dry-runs for positive, negative, and top-3-hit examples.
- Manual QA: inspect generated README/report headings against assignment requirements.
- Run submission-facing document lint and confirm zero attribution/watermark findings.

## 2026-05-14 final sprint addendum

The final package now contains 73 private CSV candidates across the conservative queue, known-best rollback files, overlays, contingency files, and the role-cap / denoise / low-tail / character-prior / balanced-prior calibration queues.

Current highest local public-proxy first upload path:

```text
experiments/final_submission_package/charprior_queue/01_v1853a_queue01_v1850a_charprior_private.csv
```

Less public-label-calibrated high-proxy fallback:

```text
experiments/final_submission_package/lowtail_queue/01_v1850a_queue01_v1848a_lowtail_private.csv
```

Risk-balanced prior fallback:

```text
experiments/final_submission_package/balancedprior_queue/01_v1856a_queue01_v1850a_balancedprior_private.csv
```

The private-feedback transfer audit (`experiments/reports/v1858_private_feedback_transfer_audit.md`) recommends v1856a as the first upload when balancing upside and transfer risk.  v1853a remains the maximum local-proxy shot if accepting higher calibration risk.

Conservative high-proxy fallback if avoiding the final marginal low-tail calibration:

```text
experiments/final_submission_package/denoise_queue/01_v1848a_queue01_v1846a_denoise_private.csv
```

Robust AP calibration fallback:

```text
experiments/final_submission_package/rolecap_queue/01_v1846a_queue01_v1842a_rolecap099_private.csv
```

Routing command for score feedback:

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group lowtail_queue --order 1 --score <REAL_SCORE> --dry-run
```

High-risk character-prior routing command:

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group charprior_queue --order 1 --score <REAL_SCORE> --dry-run
```

Risk-balanced routing command:

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group balancedprior_queue --order 1 --score <REAL_SCORE> --dry-run
```

## Stop condition

Stop when the generator and Markdown artifacts are created, command output is verified, and the final response lists exact paths and risks. Do **not** mark the score-race goal complete because no new Kaggle score above `0.50671` is available yet.

## Risks / non-goals

- No Kaggle upload is performed locally.
- No PDF rendering is performed in this pass; the generated Markdown is a report draft source for PDF conversion.
- Existing score-search scripts and candidate CSVs are not reorganized/moved to avoid breaking tomorrow's sprint.
- The active score goal remains paused/waiting for user-reported Kaggle feedback rather than completed.

## Addendum: document attribution / authorship-footprint lint

User requirement added after initial plan: every generated / submission-facing document must avoid attribution strings that could look like machine-authorship/tool watermarks.

The final-pack generator should therefore lint generated Markdown and README files for disallowed pattern classes such as:

- commit authorship trailers
- tool/product watermark phrases
- assistant/tool brand names used as authorship markers
- machine-written attribution phrases

Important allowlist: the assignment itself requires a **multi-agent system**, so terms like `agent`, `multi-agent`, `Analysis Agent`, and `Fetching Agent` remain allowed when they describe the technical architecture rather than authorship.

Additional validation standard:

- Generated report/doc lint must pass and write `experiments/final_submission_package/manifests/document_lint_log.txt`.
- Run a broader advisory scan over submission-facing existing docs (`hw2_D13922024/`, `werewolf-project/docs/report/`, `experiments/final_submission_package/`) and record any findings / non-findings.

## Addendum: hand-in package one-command regression

During final hand-in verification, running the documented package-local command failed because `make_final.py --output submission.csv` wrote the relative output in `hw2_D13922024/`, then invoked the validator from the workspace root with the same relative path.  The validator therefore looked for `submission.csv` in the wrong directory.

Fix scope:

- Resolve relative `--output` paths against the caller's current working directory once.
- Pass the absolute resolved path to the validator subprocess.
- Keep the default output path as `hw2_D13922024/submission.csv`.
- Update the package README so the documented one-command path is actually one command; keep the explicit validator as an optional re-check.
- Correct the report validator command to the packaged validator path.

Regression standard:

```bash
cd hw2_D13922024 && python3 make_final.py --output submission.csv
cd hw2_D13922024 && python3 assert/validate_submission.py submission.csv
```

Expected result: both commands report `OK: 397 predictions validated`.
