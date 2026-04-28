# Werewolf Prediction - Multi-Agent System

A multi-agent LangChain system for predicting player roles and wolf scores in Werewolf game records.

## Architecture

### Multi-Agent Pipeline

1. **Stage 1: Fetching Agent** - Extracts events from game transcripts
2. **Stage 2: Analysis Agent** - Computes role probabilities and wolf scores
3. **Stage 3: Constrained Solver** - Assigns roles respecting game constraints

### RAG System

- Game rules and role behavior corpus
- Simple keyword and BM25 retrieval

## Installation

```bash
uv sync
```

## Usage

### Predict Single Game
```bash
uv run python main.py predict 01
```

### Predict All Public Games
```bash
uv run python main.py predict-all --output predictions.csv
```

### Validate Submission
```bash
uv run python assert/validate_submission.py predictions.csv
```

## Testing

```bash
uv run pytest tests/ -v
```

## Model Configuration

Default backend: **Ollama** (localhost:11434)

Set model via environment variable:
```bash
export OLLAMA_MODEL=qwen2.5:7b
```

## Project Structure

```
werewolf-project/
├── src/
│   ├── agents/          # Multi-agent implementations
│   ├── data/            # Data loading and schema
│   ├── rag/             # RAG corpus and retriever
│   ├── utils/           # Metrics and utilities
│   └── pipeline.py      # End-to-end prediction
├── tests/               # Unit and integration tests
├── assert/              # Validation scripts
└── docs/               # SDD and report
```

## Git Flow

- `main`: Protected release branch
- `develop`: Integration branch
- `feat/*`: Feature branches

## License

MIT