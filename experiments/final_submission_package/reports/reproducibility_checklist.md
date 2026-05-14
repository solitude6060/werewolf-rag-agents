# Reproducibility Checklist

Date: `2026-05-14`  
Student ID: `D13922024`

## Rebuild package

```bash
python3 experiments/scripts/v1835_final_submission_pack.py --preset full
```

## Validate one candidate manually

```bash
python3 werewolf-project/assert/validate_submission.py \
  experiments/final_submission_package/queue/01_v1826a_primary_first_private.csv
```

Expected shape:

```text
OK: 397 predictions validated
```

## Course package checklist

- [ ] Convert `reports/hw2_report_draft.md` to `hw2_D13922024.pdf` and keep it within 5 pages.
- [ ] Include `werewolf-project/main.py`.
- [ ] Include `werewolf-project/assert/`.
- [ ] Include `werewolf-project/requirements.txt`.
- [ ] Include a README with run instructions.
- [ ] Use `cool_package/hw2_D13922024/` as the staging folder for the required zip structure.
- [ ] Upload the final selected private CSV to Kaggle under the student ID account.
- [ ] Preview the next upload with `experiments/scripts/v1836_score_feedback_router.py --dry-run` after each reported score.
- [ ] Submit `hw2_D13922024.zip` to NTU COOL before `2026-05-15 23:59`.

## Compliance notes

- Multi-agent design: fetching, analysis/verifier, and constrained solver stages.
- Retrieval component: role-rule and transcript-evidence retrieval before scoring.
- Model policy: local inference only; no training or fine-tuning; no external prediction API.
- Candidate validation: all package CSV files must pass the local submission validator.
- Document hygiene: report-facing Markdown files are linted for authorship/watermark phrases.
