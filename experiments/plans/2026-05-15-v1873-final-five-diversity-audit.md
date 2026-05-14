# v1873 Final Five Diversity Audit Plan

Date: 2026-05-15
Branch: `dev/final-submission-report-pack`

## Goal

Audit whether the current five-attempt queue is overly redundant, and whether any already-generated candidate should replace a later slot before spending real Kaggle attempts.

## Scope

- Read the final package manifest and v1860 private-transfer rank audit.
- Compare current `scoreonly_safe_queue` against high-risk/high-upside alternatives.
- Compute private CSV deltas versus:
  - verified-best v1824a,
  - current first upload v1856g,
  - adjacent queue slots.
- Produce a CSV and Markdown report with concrete metrics and a recommendation.

## Validation

- `python3 -m py_compile experiments/scripts/v1873_final_five_diversity_audit.py`
- `python3 experiments/scripts/v1873_final_five_diversity_audit.py`
- Verify output report and CSV exist.
- Rerun staged submission validator and document phrase scans.

## Completion boundary

This is a local strategy audit only.  It may improve attempt selection, but the active goal still requires a real Kaggle private score greater than `0.50671`.
