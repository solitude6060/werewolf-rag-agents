# Security and Data Handling

## Supported Versions

This is a coursework/research artifact. The active branch is maintained during the HW2 development window.

## Reporting Issues

If you find a security issue, secret leak, or accidental dataset exposure, open a private channel with the repository owner rather than filing a public issue.

## Data and Secret Policy

Do not commit:

- raw course/Kaggle datasets,
- private leaderboard labels,
- local LLM caches containing transcript excerpts,
- API tokens or GitHub credentials,
- `.env`, `.venv`, `.uv-cache`, `.pytest_cache`, model files, or Ollama model blobs.

The project is designed for local Ollama inference and does not require external model APIs.
