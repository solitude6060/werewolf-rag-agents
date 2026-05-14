# v1881 Post-Score Confirm Command Parity

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Purpose

Ensure the `NEXT_CONFIRM_COMMAND` printed by the post-score command center preserves the routing inputs used during dry-run.  This matters for order-2 feedback paths where `--previous-score` determines whether a candidate is treated as an improvement over the previous real score.

## Gap found

Before this fix, this dry-run:

```bash
python3 experiments/scripts/v1872_post_score_command_center.py --group portfolio_queue --order 2 --score 0.48001 --previous-score 0.48000
```

correctly routed with `--previous-score`, but printed a confirmation command without it:

```text
python3 experiments/scripts/v1872_post_score_command_center.py --group portfolio_queue --order 2 --score 0.48001 --confirm-real-score
```

That could make a human copy a command that does not exactly preserve the dry-run context.

## Change

`experiments/scripts/v1872_post_score_command_center.py` now builds `NEXT_CONFIRM_COMMAND` from the resolved context and preserves:

- `--group`
- `--order`
- `--score`
- `--previous-score` when supplied
- `--skip-stage` when supplied
- `--confirm-real-score`

## Validation evidence

```bash
python3 -m py_compile experiments/scripts/v1872_post_score_command_center.py
python3 experiments/scripts/v1872_post_score_command_center.py --group portfolio_queue --order 2 --score 0.48001 --previous-score 0.48000
python3 experiments/scripts/v1872_post_score_command_center.py --group portfolio_queue --order 2 --score 0.48001 --previous-score 0.48000 --skip-stage
python3 experiments/scripts/v1872_post_score_command_center.py --score 0.47120
python3 experiments/scripts/v1875_route_matrix_regression.py
```

Observed confirmation commands:

```text
python3 experiments/scripts/v1872_post_score_command_center.py --group portfolio_queue --order 2 --score 0.48001 --previous-score 0.48000 --confirm-real-score
python3 experiments/scripts/v1872_post_score_command_center.py --group portfolio_queue --order 2 --score 0.48001 --previous-score 0.48000 --confirm-real-score --skip-stage
python3 experiments/scripts/v1872_post_score_command_center.py --group scoreonly_safe_queue --order 1 --score 0.47120 --confirm-real-score
```

Post-check:

```text
score feedback records = absent
current_upload/submission.csv SHA-256 = 468ecff35fcb7f8db53c9a06a68100df687d859b8380682e662c7d1e09ea086d
current_upload/metadata.json SHA-256 = 3ba1d6018708ae9178f86f74027274e3ab9aca107e2199b8c798db9ccccd5904
route matrix -> SCENARIOS=45, FAILURES=0
```

## Completion boundary

This removes a copy/paste mismatch risk in the post-score workflow.  It does not complete the active score goal because no real Kaggle private score greater than `0.50671` has been recorded.
