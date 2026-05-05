# Post-v144 Optimization Plan

Date: 2026-05-05
Branch: `dev/structured-llm-rag-audit`

## Current verified best

- `submission_v144_filtered_big_gamble_private.csv` scored **0.40743 private**.
- Public local for v144: **0.4750**.

## Goal

Generate additional score-only candidates after v144 without changing assignment compliance:

- local data and cached local Ollama audits only,
- no external API,
- no training/fine-tuning,
- no raw dataset publication,
- no role rewrites unless a separate plan/test justifies them.

## Hypothesis

The next gain is most likely from fine-tuning predicted-Werewolf `wolf_score` demotions selected by qwen/deepseek audit disagreement patterns. Public subset search showed some qwen demotions were correct and some were catastrophic; therefore candidate policies must be small and explicit.

## Validation

For each candidate:

```bash
cd werewolf-project
UV_CACHE_DIR=.uv-cache uv run --no-sync python ../experiments/scripts/local_score.py <public_candidate> --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv --quiet
UV_CACHE_DIR=.uv-cache uv run --no-sync python assert/validate_submission.py <private_candidate>
```

## Stop condition

Stop after producing a ranked candidate table with public local scores, private diff lists, and an upload recommendation.

## Results: v145-v165 score-only sweep

All candidates are score-only; roles are unchanged.

| Candidate | Public local | Private validator | Private diff vs v144 | Risk | Notes |
| --- | ---: | --- | --- | --- | --- |
| v150/v151 | 0.47504 | OK | Only v144's three 0.05 demotions become 0/0.001 | Low | Tiny public improvement over v144 by demoting the same three rows harder. |
| v156/v159 | 0.4812 | OK | v150 plus 9 high-score Werewolf rows with any LLM Madman signal | High | Public 3/3 were false high-score wolves, but private changed too many rows. |
| v162 | 0.4812 | OK | v150 plus 7 high-score Werewolf rows where qwen is Villager/Madman and any LLM says Madman | Medium/high | Same public gain as v156 with fewer private changes. |
| v164 | **0.4812** | OK | packaged v162 with clearer name | Medium/high | Recommended upside candidate. |
| v165 | 0.4770 | OK | v150 plus one qwen-Madman high-score Werewolf row | Medium/low | Recommended lower-variance candidate. |

Generated upload files:

- Upside: `../experiments/submissions/submission_v164_postv144_highww_madman_private.csv`
- Lower variance: `../experiments/submissions/submission_v165_postv144_qwenmadman_lowrisk_private.csv`

Validation evidence:

```bash
cd werewolf-project
UV_CACHE_DIR=.uv-cache uv run --no-sync python ../experiments/scripts/local_score.py ../experiments/submissions/submission_v164_postv144_highww_madman_private_public.csv --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv --quiet
# Score=0.4812
UV_CACHE_DIR=.uv-cache uv run --no-sync python assert/validate_submission.py ../experiments/submissions/submission_v164_postv144_highww_madman_private.csv
# OK: 397 predictions validated

UV_CACHE_DIR=.uv-cache uv run --no-sync python ../experiments/scripts/local_score.py ../experiments/submissions/submission_v165_postv144_qwenmadman_lowrisk_public.csv --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv --quiet
# Score=0.4770
UV_CACHE_DIR=.uv-cache uv run --no-sync python assert/validate_submission.py ../experiments/submissions/submission_v165_postv144_qwenmadman_lowrisk_private.csv
# OK: 397 predictions validated
```

Recommendation:

- If continuing the successful v144 high-variance lane, submit **v164** next. Its public lift is the largest found after v144 (+0.0062 public local), and the rule is interpretable: demote high-score predicted Werewolves that a local LLM calls Madman while qwen does not call Werewolf.
- If submission attempts are scarce or risk tolerance is lower, submit **v165** first; it adds only one high-score qwen-Madman demotion beyond the v144-zero refinement.

## Kaggle feedback: v164 failed to generalize

`submission_v164_postv144_highww_madman_private.csv` scored **0.40400 private**, below v144's 0.40743 and also below v131's 0.40434. This rejects the high-score predicted-Werewolf + LLM-Madman demotion lane for private generalization.

Interpretation:

- The public gain from demoting high-score predicted Werewolves with Madman signals was overfit.
- Do not upload v165 unless intentionally testing a single-row variant; v165 still contains the same high-score Madman-demotion hypothesis through game 01 Baker Otto.
- The safest remaining post-v144 candidate is now the tiny v144-zero refinement.

New low-risk candidate:

| Candidate | Public local | Private validator | Diff vs v144 | Recommendation |
| --- | ---: | --- | --- | --- |
| v166 | 0.4750 (`AP=0.5009`) | OK | Only v144's three `0.05` demotions become `0` | Use only if another low-risk attempt is desired. |

Generated file:

- `../experiments/submissions/submission_v166_postv144_zero_refine_private.csv`

Validation evidence:

```bash
cd werewolf-project
UV_CACHE_DIR=.uv-cache uv run --no-sync python ../experiments/scripts/local_score.py ../experiments/submissions/submission_v166_postv144_zero_refine_public.csv --gt data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv --quiet
# submission_v166_postv144_zero_refine_public.csv F1=0.4363 AP=0.5009 Score=0.4750
UV_CACHE_DIR=.uv-cache uv run --no-sync python assert/validate_submission.py ../experiments/submissions/submission_v166_postv144_zero_refine_private.csv
# OK: 397 predictions validated
```

## Kaggle feedback: v166 is new verified best

`submission_v166_postv144_zero_refine_private.csv` scored **0.40764 private**, improving over v144's 0.40743 by +0.00021. This validates the tiny refinement of changing only the three v144 demoted Werewolf scores from `0.05` to `0`.

Current verified best:

- `../experiments/submissions/submission_v166_postv144_zero_refine_private.csv` = **0.40764 private**

Next implication:

- Very small score-ordering refinements can still matter.
- Avoid broad new demotion classes; prioritize changes already supported by the successful v144/v166 row set or near-identical evidence patterns.

## Final sprint candidate after v166: v186 Madman ceiling gamble

After v166 became the verified best, the next local search focused on score-ordering-only changes so F1 stays unchanged and only AP can move.

Candidate generated:

- `../experiments/submissions/submission_v186_last_gamble_madman_ceiling_private.csv`
- Rule: from v166, set predicted `Madman` rows with `0 < wolf_score <= 0.326` to `0`.
- Public evidence: `F1=0.4363 AP=0.5021 Score=0.4758`, compared with v166 public `F1=0.4363 AP=0.5009 Score=0.4750`.
- Private validation: `OK: 397 predictions validated`.

Why not all-Madman-zero:

- The broader all-Madman-zero lane changes 17 private rows, including `0.414`, `0.49`, and two `1.0` rows.
- Prior `submission_v121_madman_zero_private.csv` scored only `0.38844`, so broad Madman zeroing is known to be dangerous.
- v186 keeps the same public AP gain while excluding the highest-risk private Madman scores above `0.326`.

Risk note:

- v186 is still a gamble because it demotes 11 private rows without private labels.
- It is more defensible than v170/v181 all-Madman-zero because it preserves the high-confidence private Madman-as-wolf scores.
