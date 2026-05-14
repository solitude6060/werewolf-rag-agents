# v1859 Final Portfolio Queue Plan

Date: 2026-05-14
Branch: `dev/final-submission-report-pack`

## Objective

Use the current validated candidate set to build a five-attempt portfolio queue that balances:

- risk-balanced private-transfer evidence (`v1856a`),
- maximum local public proxy (`v1853a`),
- lower public-label calibration fallback (`v1850a`),
- denoise fallback (`v1848a`),
- role-cap fallback (`v1846a`).

This is an operational queue for the remaining Kaggle attempts. It does not claim the active goal is complete.

## Queue design

| Order | Candidate | Purpose |
| ---: | --- | --- |
| 1 | v1856a | First shot: risk-balanced prior, no negative no-leak heldout games. |
| 2 | v1853a | Maximum local proxy if accepting higher calibration risk after a positive signal. |
| 3 | v1850a | Less public-label-calibrated AP calibration. |
| 4 | v1848a | Denoise fallback with positive LOO evidence. |
| 5 | v1846a | Role-cap fallback with robust LOO evidence. |

## Implementation

- Add `portfolio_queue` to `experiments/scripts/v1835_final_submission_pack.py`.
- Add `portfolio_queue` routing to `experiments/scripts/v1836_score_feedback_router.py`.
- Write report `experiments/reports/v1859_final_portfolio_queue.md`.

## Validation

- `python3 -m py_compile experiments/scripts/v1835_final_submission_pack.py experiments/scripts/v1836_score_feedback_router.py`
- `python3 experiments/scripts/v1835_final_submission_pack.py --preset full`
- Manifest row count and validator pass count.
- Router dry-runs:
  - `--group portfolio_queue --order 1 --score 0.48000 --dry-run`
  - `--group portfolio_queue --order 1 --score 0.50672 --dry-run`
- Submission-facing document lint remains zero findings.

## Stop condition

Stop after the portfolio queue is generated, validated, and documented. Do not mark the active goal complete without a real Kaggle private score greater than `0.50671`.
