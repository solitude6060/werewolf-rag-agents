# System Design Document: Multi-Agent Werewolf Prediction

## 1. Problem Statement

### 1.1 Task Overview
Build a multi-agent LangChain system to predict player roles and wolf scores in Werewolf game records. The system analyzes game transcripts (dialogue, votes, events) to predict:
- **Role**: Villager, Werewolf, Seer, Medium, Madman, or Hunter
- **Wolf Score**: Probability (0.0 = human, 1.0 = werewolf)

### 1.2 Success Metrics
- **Macro-F1**: Class-wise F1 score across all roles
- **AP**: Average Precision for werewolf detection
- Target: Beat simple and strong baselines on Kaggle leaderboard

### 1.3 Constraints
| Constraint | Value |
|------------|-------|
| Model VRAM | ≤12GB |
| Training | NO training/fine-tuning |
| External APIs | NO external APIs |
| Multi-agent | Minimum 2 agents |
| Models | GGUF format (Qwen2.5-7B, GLM-4, Gemma) |

---

## 2. System Architecture

### 2.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                      Main Pipeline (main.py)                      │
├─────────────────────────────────────────────────────────────────┤
│  1. Data Loading     2. Stage 1 Agent  3. Stage 2 Agent        │
│     (Loader)            (Fetching)          (Analysis)           │
│         │                   │                  │                │
│         ▼                   ▼                  ▼                │
│  ┌─────────┐        ┌─────────────┐    ┌─────────────┐        │
│  │ Schema  │        │  Evidence   │    │  Role       │        │
│  │ Models  │        │  Extraction │    │  Ranking    │        │
│  └─────────┘        └─────────────┘    └─────────────┘        │
│                                          │                      │
│                                          ▼                      │
│                              4. Stage 3 Solver                  │
│                              (Constrained Assignment)            │
│                                          │                      │
│                                          ▼                      │
│                              ┌─────────────────────┐           │
│                              │   Kaggle Submission  │           │
│                              │   (role, wolf_score) │           │
│                              └─────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Multi-Agent Design (LangGraph)

| Agent | Responsibility | Input | Output |
|-------|---------------|-------|--------|
| **Stage 1: Fetching Agent** | Extract evidence, events, claims | Raw transcript | Normalized events, votes, deaths |
| **Stage 2: Analysis Agent** | Role behavior analysis | Events + RAG context | Per-player role rankings, wolf scores |
| **Stage 3: Solver** | Constrained role assignment | Rankings | Final role assignments |

### 2.3 RAG Pipeline

```
                    ┌──────────────┐
                    │  Game Rules  │
                    │   Corpus     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   ChromaDB   │
                    │   (BM25)     │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
   ┌─────▼─────┐    ┌──────▼──────┐   ┌─────▼─────┐
   │  Stage 1  │    │   Stage 2   │   │  Stage 3  │
   │   Agent   │    │    Agent    │   │   Solver  │
   └───────────┘    └─────────────┘   └───────────┘
```

---

## 3. Data Schema

### 3.1 Game Transcript Schema

```python
class GameRecord(BaseModel):
    game_id: str
    index: int  # 01, 02, ..., 20
    players: list[Player]
    days: list[DayPhase]

class Player(BaseModel):
    id: int
    character: str  # "Optimist Gerd", "Boy Peter"
    role: Optional[Role] = None  # for prediction

class DayPhase(BaseModel):
    day_num: int
    statements: list[Statement]
    votes: list[Vote]
    deaths: list[Death]
    night_actions: Optional[NightActions] = None

class Statement(BaseModel):
    player_id: int
    timestamp: str
    content: str
    day_num: int

class Vote(BaseModel):
    voter_id: int
    target_id: int
    day_num: int

class Death(BaseModel):
    player_id: int
    cause: str  # "execution", "werewolf_attack", "sudden_death"
    day_num: int
```

### 3.2 Roles Enum

```python
class Role(str, Enum):
    VILLAGER = "Villager"
    WEREWOLF = "Werewolf"
    SEER = "Seer"
    MEDIUM = "Medium"
    MADMAN = "Madman"
    HUNTER = "Hunter"
```

### 3.3 Prediction Output Schema

```python
class Prediction(BaseModel):
    id: int
    index: str  # "01", "02", etc.
    character: str
    role: Role
    wolf_score: float  # 0.0 or 1.0

class Submission(BaseModel):
    predictions: list[Prediction]

    def to_csv(self) -> str:
        # Kaggle format: id,index,character,role,wolf_score
```

---

## 4. Agent Specifications

### 4.1 Stage 1: Fetching Agent

**System Prompt**:
```
You are the Data Fetching Agent for a Werewolf game analysis system.
Your task is to analyze game transcripts and extract:
1. Player list and their发言 counts
2. Day-by-day events (votes, deaths, speeches)
3. Claims (Seer claims, Medium claims, etc.)
4. Suspicious patterns (contradictions, defensive behavior)

Output a structured JSON with extracted evidence.
```

**Output Schema**:
```python
class FetchingResult(BaseModel):
    game_id: str
    player_count: int
    day_count: int
    events: list[GameEvent]
    claims: list[Claim]
    votes: list[VoteRecord]
    deaths: list[DeathRecord]
    suspicious_patterns: list[str]
```

**Evidence Types**:
- Vote patterns (who voted whom)
- Death patterns (who died when, by what cause)
- Claim statements (Seer claiming white/black results)
- Defense statements
- Attack/accusation patterns

### 4.2 Stage 2: Analysis Agent

**System Prompt**:
```
You are the Event Analysis Agent for Werewolf prediction.
Given extracted game events and role behavior rules, analyze:
1. Each player's behavior matches which role patterns
2. Suspicion scores for each player
3. Werewolf probability based on:
   - Voting alignment with werewolves
   - Claim consistency
   - Defense patterns
   - Death timing

Output per-player role rankings and wolf suspicion scores.
```

**Role Behavior Patterns**:

| Role | Expected Behavior |
|------|------------------|
| **Villager** | Normal discussion, no special claims |
| **Werewolf** | Defensive when accused, may deflect to others |
| **Seer** | May claim seeing results, targets likely wolves |
| **Medium** | May claim examining dead players |
| **Madman** | Acts like villager, wolves don't know them |
| **Hunter** | Protects players, survives attacks |

**Output Schema**:
```python
class AnalysisResult(BaseModel):
    game_id: str
    player_analyses: list[PlayerAnalysis]

class PlayerAnalysis(BaseModel):
    player_id: int
    character: str
    role_candidates: dict[Role, float]  # probability ranking
    wolf_score: float
    key_evidence: list[str]
    deception_indicators: list[str]
```

### 4.3 Stage 3: Constrained Solver

**System Prompt**:
```
You are the Constrained Solver for Werewolf role assignment.
Given per-player role rankings and game constraints, determine valid assignments.

Constraints:
- Villagers: N - W - 1 (excluding werewolves and special roles)
- Werewolves: 2 (if ≤12 players) or 3 (if ≥13 players)
- Seer: 1 (if exists in game)
- Medium: 1 (if exists in game)
- Hunter: 1 (if ≥11 players)
- Madman: 1 (if ≥11 players)

Use greedy assignment based on rankings, respecting constraints.
```

**Solver Algorithm**:
1. Sort players by wolf_score descending
2. Assign werewolves (highest scores, respecting count)
3. Assign special roles (Seer, Medium, Hunter, Madman)
4. Fill remaining with Villagers

**Output Schema**:
```python
class SolverResult(BaseModel):
    game_id: str
    assignments: dict[int, Role]  # player_id -> role
    wolf_scores: dict[int, float]  # player_id -> score
    confidence: float
```

---

## 5. RAG Implementation

### 5.1 Knowledge Corpus

```python
# rules_corpus.py - Game rules and role behaviors
corpus_chunks = [
    "Werewolf rules: 2 wolves (≤12 players), 3 wolves (≥13 players)",
    "Seer behavior: can divine one player per night, learns human/wolf",
    "Medium behavior: can check if executed player was human/wolf",
    "Hunter behavior: can protect one player per night",
    "Madman behavior: human aligned with wolves, wolves don't know them",
    # ... more chunks
]
```

### 5.2 Retrieval Configuration

```python
# retriever.py
retriever_config = {
    "vector_store": "ChromaDB",
    "embedding_model": "all-MiniLM-L6-v2",  # Local embeddings
    "retrieval_method": "bm25",  # or "mmr"
    "top_k": 5,
}
```

---

## 6. Model Configuration

### 6.1 Primary Model: Qwen2.5-7B-Instruct-GGUF

```python
# model_adapter.py
model_config = {
    "name": "qwen2.5-7b-instruct-q8_0.gguf",
    "path": "models/qwen2.5-7b-instruct-q8_0.gguf",
    "n_ctx": 8192,
    "n_gpu_layers": 35,  # RTX 4090: ~35 layers fit in 24GB
    "n_threads": 8,
    "temperature": 0.1,  # Low temp for consistent output
    "max_tokens": 2048,
}
```

### 6.2 Fallback Models

| Model | Quantization | VRAM | Notes |
|-------|-------------|------|-------|
| Qwen2.5-7B | Q8_0 | ~8GB | Primary |
| Qwen2.5-3B | Q8_0 | ~4GB | Fallback |
| Gemma-4-2B | Q8_0 | ~3GB | Conservative |

---

## 7. Evaluation Strategy

### 7.1 Metrics

```python
# metrics.py
def compute_metrics(predictions, ground_truth):
    # Macro-F1 for role classification
    macro_f1 = f1_score(ground_truth["role"], predictions["role"], average="macro")

    # AP for werewolf detection
    ap = average_precision_score(ground_truth["wolf_score"], predictions["wolf_score"])

    return {"macro_f1": macro_f1, "ap": ap}
```

### 7.2 Baselines

| Baseline | Description |
|----------|-------------|
| Simple | Random role assignment, wolf_score = 0.5 |
| Frequency | Most common role distribution |
| Heuristic | Rule-based voting pattern analysis |

---

## 8. Project Structure

```
werewolf-project/
├── docs/
│   ├── sdd/
│   │   └── system-design.md    # This document
│   ├── evals/
│   │   └── experiment-log.md
│   └── report/
│       └── hw2-report-outline.md
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── state.py          # LangGraph state
│   │   ├── stage1_fetching.py # Fetching Agent
│   │   ├── stage2_analysis.py # Analysis Agent
│   │   └── stage3_solver.py   # Constrained Solver
│   ├── data/
│   │   ├── __init__.py
│   │   ├── schema.py         # Pydantic models
│   │   ├── loader.py          # Data loading
│   │   └── parser.py          # Transcript parsing
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── corpus.py          # Knowledge corpus
│   │   └── retriever.py       # Retrieval system
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration
│   │   ├── metrics.py         # Evaluation metrics
│   │   └── submission.py      # Kaggle output
│   └── model_adapter.py       # GGUF model wrapper
├── tests/
│   ├── unit/
│   │   ├── test_schema.py
│   │   ├── test_loader.py
│   │   ├── test_parser.py
│   │   ├── test_fetching_agent.py
│   │   ├── test_analysis_agent.py
│   │   └── test_solver.py
│   └── integration/
│       └── test_pipeline.py
├── assert/
│   ├── validate_submission.py
│   └── run_public_eval.py
├── data/
│   ├── raw/Werewolf_Prediction_Dataset/
│   ├── interim/
│   └── submissions/
├── main.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 9. TDD Implementation Plan

### 9.1 Test Pyramid

```
        ┌─────────────┐
        │ Integration │
        │   Tests     │
        ├─────────────┤
        │   Unit      │
        │   Tests     │
        ├─────────────┤
        │   Schema    │
        │   Tests     │
        └─────────────┘
```

### 9.2 Test Fixtures

```python
# tests/fixtures/sample_game.json
{
    "game_id": "01",
    "players": [...],
    "days": [...],
    "ground_truth": {...}
}
```

### 9.3 CI Pipeline

```bash
# .github/workflows/test.yml
uv pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Model doesn't fit in 12GB | Blocked | Use Q8 quantization, reduce context |
| Long transcripts exceed context | Quality loss | Truncate with priority (recent days) |
| Deception detection poor | Low accuracy | Focus on voting patterns |
| RAG retrieval irrelevant | Bad context | Tune top_k, use MMR |
| Kaggle format mismatch | Rejected | Validate with assert/ script |

---

## 11. Report Requirements

| Section | Weight | Content |
|---------|--------|---------|
| Design Structure | 5% | Architecture diagram, prompt design |
| Success/Failure Cases | 5% | Analysis of predictions |
| Optimizations | 10% | RAG tuning, prompt engineering |

**Format**: Within 5 pages, PDF submission
