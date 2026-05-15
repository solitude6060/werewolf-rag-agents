# v1913 Leaderboard Threshold and Skip-v1846g Audit

Generated UTC: `2026-05-15T00:33:00+00:00`
Branch: `dev/final-submission-report-pack`

## Updated leaderboard threshold

The latest user-provided leaderboard snapshot moved the top-3 cutoff upward:

| Rank | ID | Private score |
| ---: | --- | ---: |
| 1 | D13922023 | 0.54251 |
| 2 | R14922184 | 0.53461 |
| 3 | R14922115 | 0.52380 |
| 4 | R14942077 | 0.50671 |

Therefore the current completion condition for a top-3 hit is now:

```text
real private score > 0.52380
```

The old `>0.50671` threshold is no longer sufficient for top 3.

## Current upload decision

Current upload is switched from conservative score-only `v1846g` to structural `v1826a`:

```text
experiments/final_submission_package/current_upload/submission.csv
candidate=v1826a
group=queue
order=1
sha256=e4b44b76dbcd0d2068b24a0ba4b65585a142d8f3944da210f79bb35fd60421ad
```

## Rationale

- `v1856g` real private score was `0.42894`, a severe negative signal for the score-only prior-calibration family.
- `v1846g` is the conservative score-only fallback and is less aligned with the updated objective of beating `0.52380`.
- `v1826a` is the documented structural primary shot in `v1831_candidate_risk_scores.md` and remains manifest-backed with validation status `pass`.

## Prompt-to-artifact checklist

| Requirement / gate | Evidence inspected | Coverage judgment | Status |
| --- | --- | --- | --- |
| Completion threshold reflects latest leaderboard | Active scripts and current metadata now use `0.52380`; `v1906_goal_completion_gate.py` reports `TOP3_THRESHOLD=0.52380`. | Prevents false completion at old rank-4 threshold. | pass |
| Goal is not complete | `v1908_final_goal_status.py` reports `GOAL_COMPLETE=no`, `BEST_SCORE=0.42894`. | Correct under both old and new thresholds. | pass |
| Current upload is structural v1826a | `metadata.json` reports `candidate=v1826a`, `group=queue`, `order=1`. | Confirms skip-v1846g decision is staged. | pass |
| Current upload is valid | `v1888_final_upload_preflight.py` reports `READY_TO_MANUAL_UPLOAD=yes`; validator reports `OK: 397 predictions validated`. | Covers upload readiness. | pass |
| Manual override is documented | `metadata.json` contains `attempt_state_override_reason`; `v1904_attempt_state_guard.py` reports `STATE=manual_override_from_records`, `ATTEMPT_STATE_READY=yes`. | Prevents hidden divergence from latest score-feedback recommendation. | pass |
| Score-report flow works with records already present | `v1894`, `v1895`, and `v1898` regressions all report `FAILURES=0`. | Covers post-first-score score intake/bridge behavior. | pass |
| Router/completion regressions use new top-3 threshold | `v1906` regression, `v1882` regression, and `v1875` route matrix all report `FAILURES=0`. | Covers top-3 gate and next-route safety. | pass |

## Verification evidence

```text
python3 -m py_compile active score workflow scripts
py_compile=pass

python3 experiments/scripts/v1906_goal_completion_gate_regression.py
SCENARIOS=6
FAILURES=0

python3 experiments/scripts/v1882_command_center_dry_run_regression.py
SCENARIOS=8
FAILURES=0
MUTATION_OK=yes

python3 experiments/scripts/v1875_route_matrix_regression.py
SCENARIOS=45
FAILURES=0

python3 experiments/scripts/v1894_score_report_intake_regression.py
SCENARIOS=6
FAILURES=0

python3 experiments/scripts/v1895_score_report_command_center_regression.py
SCENARIOS=4
FAILURES=0
OFFICIAL_RECORDS_UNCHANGED=yes

python3 experiments/scripts/v1898_current_score_report_bridge_regression.py
SCENARIOS=4
FAILURES=0
OFFICIAL_RECORDS_UNCHANGED=yes

python3 experiments/scripts/v1888_final_upload_preflight.py
READY_TO_MANUAL_UPLOAD=yes
CANDIDATE=v1826a
GROUP=queue
ORDER=1

python3 experiments/scripts/v1906_goal_completion_gate.py
GOAL_COMPLETE=no
BEST_SCORE=0.42894
TOP3_THRESHOLD=0.52380

python3 experiments/scripts/v1908_final_goal_status.py
ACTION=UPLOAD_CURRENT
GOAL_COMPLETE=no
READY_TO_MANUAL_UPLOAD=yes
```

## Completion decision

`NOT COMPLETE`.

Reason: the best recorded real private score is `0.42894`, below the updated top-3 threshold `0.52380`.
