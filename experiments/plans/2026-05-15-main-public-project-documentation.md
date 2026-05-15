# 2026-05-15 Main Public Project Documentation Plan

## Goal

Prepare `main` as a public-facing repository branch with clear entry points, detailed technical reporting, reproducibility instructions, and upload-candidate guidance.

## User requirements

- The `main` branch should look like a polished external project, not only an internal experiment dump.
- The technical report should be as detailed and clear as possible.
- Include more charts, diagrams, tables, and structure explanations.
- Preserve the current candidate batch and final-attempt audit trail.
- Avoid problematic attribution or tool-credit wording in public-facing files.

## Current gaps

- No tracked root `README.md`, so GitHub visitors land on a directory listing.
- Existing documentation is useful but spread across `hw2_D13922024/` and `experiments/final_submission_package/`.
- Some older package text still describes the closed five-attempt state and does not clearly explain the reopened extra-submit sprint on `main`.
- The technical report exists, but the public branch needs a richer architecture/report layer with diagrams and tables.

## Files to add or update

Add:

- `README.md`
- `README.zh-TW.md`
- `docs/TECHNICAL_REPORT.md`
- `docs/TECHNICAL_REPORT.zh-TW.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/REPRODUCIBILITY.md`

Update:

- `hw2_D13922024/README.md`
- `experiments/final_submission_package/README.md`
- `experiments/final_submission_package/reports/submission_strategy.md`

## Documentation design

Public entry points:

1. Root README: quick project summary, current candidate, repository map, run commands, reports.
2. Traditional Chinese README: concise mirror for local/user-facing review.
3. Technical report: detailed architecture, pipeline, diagrams, candidate strategy, evaluation evidence.
4. Project structure guide: path-by-path map explaining what is tracked and what should be ignored.
5. Reproducibility guide: one-command reproduction, validation, score recording, and known limits.

## Verification standards

- Validate the current submission CSV:

  ```bash
  python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv
  ```

- Validate the packaged reproduction command:

  ```bash
  cd hw2_D13922024 && python3 make_final.py --output /tmp/hw2_public_doc_check.csv
  ```

- Verify the generated CSV hash matches the current upload hash.
- Scan changed docs and latest commit for disallowed attribution phrases.
- Ensure `.omx` is not tracked:

  ```bash
  git ls-files .omx
  ```

## Stop condition

Stop when the documentation is committed and pushed to `origin/main`, with verification evidence and remaining risks reported.

## 2026-05-15 revision notes

- User requested deeper technical detail and more visual material in the reports.
- Added extra Mermaid charts and decision matrices to the public technical reports:
  - feature-to-decision calibration flow;
  - private-score trajectory chart plus text fallback;
  - candidate selection matrix with evidence type, upside, variance, reversibility, and priority.
- Added additional score-trajectory and decision-map diagrams to the coursework reports under `hw2_D13922024/` so the hand-in report itself is more self-contained.

## Verification log

Executed on `main` from `/home/ma/Research/PhD/course/114_2/AI/hw2`.

| Check | Command | Result |
| --- | --- | --- |
| Current upload schema | `python3 werewolf-project/assert/validate_submission.py experiments/final_submission_package/current_upload/submission.csv` | `OK: 397 predictions validated` |
| Packaged reproduction | `cd hw2_D13922024 && python3 make_final.py --output /tmp/hw2_public_doc_check.csv` | validator passed and wrote `/tmp/hw2_public_doc_check.csv` |
| SHA equality | `sha256sum /tmp/hw2_public_doc_check.csv experiments/final_submission_package/current_upload/submission.csv hw2_D13922024/checkpoints/final_current_private.csv hw2_D13922024/checkpoints/final_v1842e_private.csv hw2_D13922024/submission.csv` | all five paths matched `6223a0ead5230c655d0ea09ccd3c6a5af51f8d35af2f2b9dd118b584cf8d6d7f` |
| Extra batch validators | three `validate_submission.py` commands for `01_v1842e`, `02_v1845c`, `03_v1826b` | all three returned `OK: 397 predictions validated` |
| Local markdown links | Python local-link scanner over 11 public/package docs | 12 local links checked, 0 missing |
| Public-doc attribution scan | Python scan over 12 changed/new docs | 0 hits for disallowed attribution/tool-credit phrases |
| Local-only state | `git ls-files .omx` | empty output |
| Stale state wording | grep for old feature/final/no-upload wording | 0 hits |

Note: an earlier hash check used a non-existent checkpoint directory name; it was immediately rerun with the actual tracked checkpoint files listed above.
