# v1835 Final Submission Pack Completion Audit

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Prompt-to-artifact checklist

| User need | Artifact / evidence | Status |
| --- | --- | --- |
| Pause score-race goal until tomorrow | Goal remains active/waiting; not marked complete because no score >0.50671 is available. | done |
| Work on a new branch | `dev/final-submission-report-pack` | done |
| One command to generate different submissions | `experiments/scripts/v1835_final_submission_pack.py` with `--preset full` plus focused presets | done |
| Include current candidate queue | `experiments/final_submission_package/queue/*.csv` | done |
| Include current top 5 known verified submissions | `experiments/final_submission_package/known_best/*.csv` | done |
| Include score-only overlays on known best | `experiments/final_submission_package/known_best_overlay/*.csv` | done |
| Include adaptive contingency submissions | `experiments/final_submission_package/contingency/*.csv` | done |
| Include overlay / score-attack queues | `overlay/`, `attack_queue/`, `black_boost_queue/` | done |
| Include role-cap, denoise, low-tail, character-prior, balanced-prior queues/fallbacks | `rolecap_*`, `denoise_*`, `lowtail_*`, `charprior_*`, `balancedprior_*` package folders | done |
| Include cross-risk final portfolio queue | `experiments/final_submission_package/portfolio_queue/*.csv` and `experiments/reports/v1859_final_portfolio_queue.md` | done |
| Include score-only safe queue | `experiments/final_submission_package/scoreonly_safe_queue/*.csv` and `experiments/reports/v1862_scoreonly_safe_queue.md` | done |
| Include private-feedback transfer audit | `experiments/reports/v1858_private_feedback_transfer_audit.md` | done |
| Assignment-structured report Markdown | `experiments/final_submission_package/reports/hw2_report_draft.md` | done |
| Strategy / reproducibility docs | `submission_strategy.md`, `reproducibility_checklist.md`, package `README.md` | done |
| COOL package structure staging | `experiments/final_submission_package/cool_package/hw2_D13922024/` | done |
| Check docs for authorship/tool watermark phrases | `experiments/reports/v1852_submission_document_lint_final_rerun.md` | done; 77 submission-facing files and 409 broad document-ish files checked, 0 findings |
| Validate all generated private CSV files | `experiments/final_submission_package/manifests/validation_log.txt` | done; 83 validator passes |
| Route tomorrow's score feedback to the next candidate | `experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue ...` | done |

## Verification commands run

```bash
python3 -m py_compile experiments/scripts/v1835_final_submission_pack.py experiments/scripts/v1836_score_feedback_router.py
python3 experiments/scripts/v1835_final_submission_pack.py --preset full
python3 experiments/scripts/v1835_final_submission_pack.py --preset scoreonly-safe-queue --out /tmp/hw2_pack_scoreonly_safe_queue_smoke --skip-validation --no-existing-doc-scan
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.48000 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.47080 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.46400 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.50672 --dry-run
```

Document lint reruns:

```text
Submission-facing package/report scan: FILES_CHECKED=62, FINDINGS=0
Broad document-ish repo scan: FILES_CHECKED=394, FINDINGS=0
```

## Verification results

- Full package generation succeeded.
- 83 generated private CSV files are listed in `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv`.
- All 83 generated private CSV files have 397 prediction rows and `validation_status=pass`.
- Score-only-safe queue smoke generation succeeded with 5 files.
- Router dry-runs for `scoreonly_safe_queue`:
  - order 1 score `0.48000` -> `scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv`.
  - order 1 score `0.47080` -> `scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv`.
  - order 1 score `0.46400` -> `scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv`.
  - order 1 score `0.50672` -> `STOP: score exceeds top-3 threshold.`
- Private-feedback transfer audit compares 11 known user-reported private scores and initially recommended v1856a; v1860/v1862 now prefer v1856g as the lower role-risk first upload while keeping v1853g/v1853a for maximum-upside calibration risk.

## Primary paths for tomorrow

1. Recommended first upload: `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv`
2. Strategy table: `experiments/final_submission_package/reports/submission_strategy.md`
3. Report draft: `experiments/final_submission_package/reports/hw2_report_draft.md`
4. COOL staging folder: `experiments/final_submission_package/cool_package/hw2_D13922024/`
5. Current best rollback: `experiments/final_submission_package/known_best/01_v1824a_score_0p47119_private.csv`
6. Score feedback router preview: `python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --dry-run`
7. Maximum-upside direct shot if accepting higher calibration risk: `experiments/final_submission_package/charprior_queue/01_v1853a_queue01_v1850a_charprior_private.csv`
8. Lower-calibration fallback: `experiments/final_submission_package/lowtail_queue/01_v1850a_queue01_v1848a_lowtail_private.csv`
9. Robust AP fallback: `experiments/final_submission_package/denoise_queue/01_v1848a_queue01_v1846a_denoise_private.csv`
10. Role-cap fallback: `experiments/final_submission_package/rolecap_queue/01_v1846a_queue01_v1842a_rolecap099_private.csv`

## Risks / not done

- No Kaggle upload was performed locally.
- No real private score above `0.50671` has been reported, so the active score goal is not complete.
- No final PDF was produced; convert the Markdown report to `hw2_D13922024.pdf` and keep it within the assignment page limit.
