# Dataset Policy

This repository intentionally does **not** publish the raw course/Kaggle dataset.

## Expected Local Layout

Place the dataset locally at:

```text
data/raw/Werewolf_Prediction_Dataset/
├── public/
├── private/
└── ...
```

The exact files depend on the official HW2 distribution. Obtain them from the course or Kaggle source authorized for the assignment.

## Why Raw Data Is Excluded

- Course datasets may have redistribution restrictions.
- Kaggle/private leaderboard files should not be republished accidentally.
- Local LLM audit caches may contain transcript excerpts and are therefore also excluded from git.

## Tracked Data-like Artifacts

Small legacy CSV artifacts under `artifacts/legacy-submissions/` are retained only as an audit trail for earlier generated predictions. They are not the raw dataset and are not the current final Kaggle upload path.

## Reproducibility Notes

The current best verified Kaggle candidate is documented in `docs/SUBMISSION_GUIDE.md`. Some final-sprint generated CSVs live in the outer experiment workspace (`../experiments/submissions/`) and should be copied into a release package only when intentionally submitting or archiving that exact candidate.


## CI Behavior

Dataset-dependent tests are skipped automatically when the raw dataset is absent. This keeps GitHub Actions useful for code and documentation checks without redistributing course/Kaggle data. With the dataset installed locally at the expected path, the full test suite runs.
