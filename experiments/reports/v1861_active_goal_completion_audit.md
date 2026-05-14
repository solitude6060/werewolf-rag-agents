# v1861 Active Goal Completion Audit

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Objective as concrete success criteria

Objective: use the remaining Kaggle attempts to exceed the current rank-3 private leaderboard score.

Completion criteria:

1. A real Kaggle private score is reported for one of our submissions.
2. That real private score is strictly greater than `0.50671`.
3. The reported score is not a local proxy, not a dry-run, and not a hypothetical route preview.
4. The corresponding uploaded CSV path is identifiable in the final package or score-feedback records.

Current verified best before new uploads remains `0.47119`; the required improvement is `+0.03552`.

## Prompt-to-artifact checklist

| Requirement / gate | Evidence inspected | Status |
| --- | --- | --- |
| Remaining-attempt strategy exists | `experiments/reports/v1859_final_portfolio_queue.md` | covered |
| First upload path is concrete | `experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` | covered |
| First upload CSV format is valid | `python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` -> `OK: 397 predictions validated` | covered |
| Full package manifest covers generated private CSVs | `experiments/final_submission_package/manifests/final_submission_pack_manifest.csv` has 83 rows, all validator pass | covered |
| Router can react to first private score | `v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 ...` dry-runs route positive, fallback, and top-3 outcomes | covered |
| Additional private-transfer rank audit exists | `experiments/reports/v1860_private_transfer_rank_audit.md`; 11 known private rows and 53 future/package candidates audited | covered |
| Recommendation remains stable after v1860 | v1860/v1862 recommend the score-only safe first upload `scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv` | covered |
| Score-only blend ladder audit exists | v1863 generated 30 public/private score-only blends; no partial alpha below 1.00 supersedes v1862 first upload | covered |
| Score-only alpha robustness audit exists | v1864 evaluated 30 candidates with 20 leave-one-game-out splits; no lower-alpha candidate replaces v1862 first upload | covered |
| Adaptive router matrix exists | v1865 routes positive score-only follow-ups into structural portfolio counterparts instead of stopping early | covered |
| Final attempt runbook CLI exists | v1866 prints next upload path, hash, validator status, and router command | covered |
| Feedback-record auto-next runbook exists | v1867 extends v1866 with --from-records and validates the latest recommended_next CSV | covered |
| Deadline-day pre-upload audit exists | v1868 re-ran runbook/manifest/records checks on 2026-05-15 | covered |
| Attempt budget guard exists | v1869 summarizes used/remaining attempts, best score, top-3 hit, and next action from records | covered |
| Current upload staging exists | v1870 stages the current upload as `current_upload/submission.csv` with matching SHA-256 and validator pass | covered |
| Final-attempt cockpit exists | v1871 writes `current_upload/ATTEMPT_CARD.md` with current upload, budget, router previews, and next commands | covered |
| Post-score command center exists | v1872 wraps router dry-run/confirmed write, budget guard, restaging, and cockpit refresh; defaults to `current_upload/metadata.json`; dry-run does not create records | covered |
| Final-five diversity audit exists | v1873 compares safe queue diversity against portfolio/charprior/balanced alternatives and records no pre-feedback router change | covered |
| Positive score-only signal routes to upside slot | v1874 fixes `0.47119 < score < 0.47200` so any real improvement over current best routes to `v1853g` | covered |
| Route matrix regression exists | v1875 checks 33 score-band scenarios; concrete recommendations are manifest/file/hash/row/status checked | covered |
| Release checklist exists | `experiments/final_submission_package/RELEASE_CHECKLIST.md` summarizes branch, structure, commands, upload path, reports, and stop condition | covered |
| Submission/report text scan is clean | v1852 final rerun plus v1871 post-cockpit scans: submission-facing and broad phrase checks have 0 findings | covered |
| Real Kaggle private score >0.50671 exists | No such user-reported score or score-feedback record is present | missing |
| Goal can be marked complete | Requires the missing real score proof | not achieved |

## Fresh verification evidence

Commands run in this continuation:

```bash
python3 -m py_compile experiments/scripts/v1860_private_transfer_rank_audit.py
python3 experiments/scripts/v1860_private_transfer_rank_audit.py
python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.48000 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.50672 --dry-run
python3 -m py_compile experiments/scripts/v1863_scoreonly_blend_ladder.py
python3 experiments/scripts/v1863_scoreonly_blend_ladder.py
python3 -m py_compile experiments/scripts/v1864_scoreonly_alpha_robustness.py
python3 experiments/scripts/v1864_scoreonly_alpha_robustness.py
python3 -m py_compile experiments/scripts/v1836_score_feedback_router.py
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 2 --score 0.48100 --previous-score 0.48000 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 3 --score 0.47200 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 4 --score 0.47200 --dry-run
python3 -m py_compile experiments/scripts/v1866_final_attempt_runbook.py
python3 experiments/scripts/v1866_final_attempt_runbook.py
python3 experiments/scripts/v1866_final_attempt_runbook.py --score 0.48000
python3 experiments/scripts/v1866_final_attempt_runbook.py --score 0.50672
python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records --records /tmp/v1867_records_next.csv
python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records --records /tmp/v1867_records_stop.csv
python3 experiments/scripts/v1866_final_attempt_runbook.py  # 2026-05-15 preflight
python3 -m py_compile experiments/scripts/v1869_attempt_budget_guard.py
python3 experiments/scripts/v1869_attempt_budget_guard.py --records /tmp/nonexistent_v1869_records.csv
python3 experiments/scripts/v1869_attempt_budget_guard.py --records /tmp/v1869_records_one.csv
python3 experiments/scripts/v1869_attempt_budget_guard.py --records /tmp/v1869_records_top3.csv
python3 experiments/scripts/v1869_attempt_budget_guard.py --records /tmp/v1869_records_five.csv
python3 experiments/scripts/v1870_stage_current_upload.py --from-records --records /tmp/v1869_records_one.csv --out-dir /tmp/v1870_test_current_upload
python3 -m py_compile experiments/scripts/v1870_stage_current_upload.py
python3 experiments/scripts/v1870_stage_current_upload.py
python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv
python3 -m py_compile experiments/scripts/v1866_final_attempt_runbook.py
python3 experiments/scripts/v1866_final_attempt_runbook.py
python3 experiments/scripts/v1866_final_attempt_runbook.py --from-records
python3 experiments/scripts/v1869_attempt_budget_guard.py
python3 -m py_compile experiments/scripts/v1871_final_attempt_cockpit.py
python3 experiments/scripts/v1871_final_attempt_cockpit.py
python3 -m py_compile experiments/scripts/v1872_post_score_command_center.py
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.48000
python3 experiments/scripts/v1872_post_score_command_center.py --group scoreonly_safe_queue --order 1 --score 0.48000
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.50672
python3 -m py_compile experiments/scripts/v1873_final_five_diversity_audit.py
python3 experiments/scripts/v1873_final_five_diversity_audit.py
python3 -m py_compile experiments/scripts/v1836_score_feedback_router.py
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.47120 --dry-run
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score 0.47119 --dry-run
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.47120
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.47119
python3 -m py_compile experiments/scripts/v1875_route_matrix_regression.py
python3 experiments/scripts/v1875_route_matrix_regression.py
```

Observed outputs:

```text
v1860 known_rows=11
v1860 future_rows=53
v1860 loo_mae=0.00502
v1860 recommended_first=experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
validator=OK: 397 predictions validated
router 0.48000 -> experiments/final_submission_package/scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv
router 0.50672 -> STOP: score exceeds top-3 threshold.
v1863 generated_pairs=30
v1863 promoted=v1863_12,v1863_06,v1863_18,v1863_24,v1863_30
v1863 decision=no partial alpha below 1.00 supersedes scoreonly_safe_queue/01_v1856g
v1864 candidates=30
v1864 best_robust=v1863_12 target=v1853g alpha=1.00 min_loo_delta=+0.0451
v1864 current_first=v1863_06 target=v1856g alpha=1.00 min_loo_delta=+0.0450
v1864 decision=no package/router change
v1865 order2 positive -> portfolio_queue/02_v1853a_max_proxy_second_private.csv
v1865 order3 positive -> portfolio_queue/03_v1850a_lowtail_fallback_private.csv
v1865 order4 positive -> portfolio_queue/04_v1848a_denoise_fallback_private.csv
v1866 next_upload=experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
v1866 sha256=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
v1866 validator=OK: 397 predictions validated
v1866 staged_upload=experiments/final_submission_package/current_upload/submission.csv
v1867 auto_next=scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv
v1867 stop_record=STOP_STATE=top3_hit_or_stop_recommended
v1868 deadline_day_preflight=validator OK, manifest 83/83 pass, no score records
v1869 no_records=attempts_used 0, attempts_remaining 5
v1869 one_record=attempts_used 1, attempts_remaining 4, next_action validate recommended next, stage_command v1870 --from-records
v1869 top3_record=top3_hit yes, next_action stop
v1869 five_records=attempts_remaining 0, next_action no attempts remaining
v1870 from_records_test=staged /tmp/v1870_test_current_upload/submission.csv from scoreonly_safe_queue order 2 v1853g, validator OK
v1870 staged_upload=experiments/final_submission_package/current_upload/submission.csv
v1870 sha256=468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
v1870 validator=OK: 397 predictions validated
v1871 cockpit_card=experiments/final_submission_package/current_upload/ATTEMPT_CARD.md
v1871 staged_match=yes
v1871 attempts_remaining=5
v1871 router_preview validates next score-only paths in manifest
v1872 dry_run_score_0.48000=metadata-default context scoreonly_safe_queue order 1, recommends scoreonly_safe_queue/02_v1853g, no record write
v1872 explicit_context_parity=scoreonly_safe_queue order 1 matches metadata-default routing
v1872 dry_run_score_0.50672=recommends STOP, no record write
v1873 diversity_audit=score-only safe queue is not identical-score redundant; v1853g remains best pure upside; no router change before first real score
v1874 tiny_positive=0.47120 routes to scoreonly_safe_queue/02_v1853g
v1874 exact_current_best=0.47119 routes to scoreonly_safe_queue/03_v1850g
v1875 route_matrix=33 scenarios, 0 failures
```

Document scan outputs after v1870/v1861 artifacts:

```text
SUBMISSION_FILES_CHECKED=84
SUBMISSION_FINDINGS=0
BROAD_FILES_CHECKED=416
BROAD_FINDINGS=0
SUBMISSION_DOC_FILES_CHECKED=59
SUBMISSION_DOC_FINDINGS=0
BROAD_DOC_FILES_CHECKED=4474
BROAD_PROBLEM_PHRASE_FINDINGS=0
```

## Verdict

The local preparation is stronger after v1874, but the active score goal is **not complete**.  There is still no real Kaggle private score greater than `0.50671`.

Recommended next real action is uploading the staged fixed path:

```text
experiments/final_submission_package/current_upload/submission.csv
```

That staged CSV is a byte-for-byte copy of the selected candidate:

```text
experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv
```

Then route the reported score with:

```bash
python3 experiments/scripts/v1836_score_feedback_router.py --group scoreonly_safe_queue --order 1 --score <REAL_SCORE> --dry-run
```
