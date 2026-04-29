# HW2 Report: Multi-Agent Werewolf Prediction

**Student ID: D13922024**

---

## 1. Introduction

We present a multi-agent pipeline for predicting player roles in Werewolf (狼人殺) games from transcripts. The system uses a three-stage pipeline: **Fetching → Analysis → Constrained Solving**, with optional LLM enhancement via Ollama.

### 1.1 Task Description

Given:
- 20 public games with ground truth (276 players)
- 30 private games for submission (397 players)
- Goal: Predict role (Villager, Werewolf, Seer, Medium, Hunter, Madman) and wolf_score (0.0-1.0) for each player

### 1.2 Constraints

- No external APIs, no training/fine-tuning
- Use SDD, TDD, git dev flow
- Local GGUF models via Ollama (qwen2.5-7b preferred)
- 5-page limit, D13922024 as identifier

---

## 2. System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Main Pipeline                          │
├──────────────────────────────────────────────────────────┤
│  Stage 1: Fetching Agent                                   │
│  - Parse transcripts (statements, votes, deaths, claims)  │
│  - Detect suspicious patterns                              │
├──────────────────────────────────────────────────────────┤
│  Stage 2: Analysis Agent                                   │
│  - Compute role scores based on behavior                  │
│  - Calculate wolf suspicion scores                        │
├──────────────────────────────────────────────────────────┤
│  Stage 3: Constrained Solver                              │
│  - Greedy role assignment                                 │
│  - Enforce werewolf/special role counts                   │
└──────────────────────────────────────────────────────────┘
```

**Multi-Agent Design:**

| Agent | Responsibility | LLM Usage |
|-------|---------------|----------|
| Stage 1: Fetching | Parse transcripts, extract events | Optional (rule-based fallback) |
| Stage 2: Analysis | Score roles, detect deception | Optional |
| Stage 3: Solver | Constrained optimization | Deterministic |

---

## 3. Technical Implementation

### 3.1 Stage 1: Fetching Agent

Rule-based parser extracts structured events:
- **Statement extraction**: Regex pattern matching for player ID, character name, timestamp, content
- **Vote extraction**: Pattern matching for vote patterns "X voted Y"
- **Death extraction**: Pattern matching for death announcements
- **Claim extraction**: Detection of role claims (Seer, Medium, etc.)

```python
# Statement pattern: "1. Optimist Gerd\n21:45\nContent"
player_pattern = r"^(\d+)\.\s*([A-Za-z][A-Za-z\s']*)\s*$"
time_pattern = r"^(\d{2}:\d{2})$"
```

### 3.2 Stage 2: Analysis Agent

Heuristic scoring based on behavior patterns:
- **Wolf score**: Based on suspicious patterns (contradictions, defense)
- **Role scores**: Based on claim detection and vote patterns

Default scoring (no LLM):
- Identified werewolf: 1.0
- Identified special role (Seer/Medium): 0.5
- Default: 0.5 for all others

### 3.3 Stage 3: Constrained Solver

Greedy assignment respecting game constraints:

| Players | Werewolves | Seer | Medium | Hunter | Madman |
|---------|------------|------|--------|--------|--------|
| ≤7 | 2 | 0 | 0 | 0 | 0 |
| 8-10 | 2 | 1 | 0 | 0 | 0 |
| 11-13 | 3 | 1 | 1 | 1 | 1 |
| ≥14 | 3 | 1 | 1 | 1 | 2 |

**Algorithm**:
1. Assign werewolves by highest wolf_score
2. Assign special roles (Seer → highest seer_score, etc.)
3. Fill remaining with Villager

### 3.4 RAG Pipeline

- **Corpus**: Game rules, role behaviors, evidence patterns
- **Retriever**: Simple keyword matching / BM25
- **Usage**: Context injection for Analysis Agent

---

## 4. Evaluation Results

### 4.1 Public Games Performance

| Metric | Value |
|--------|-------|
| Accuracy | 32.25% |
| Macro-F1 | 0.1938 |
| Average Precision (AP) | 0.1872 |
| Total Predictions | 276 |

### 4.2 Role Distribution

| Role | Predicted | Actual |
|------|-----------|--------|
| Villager | 145 | 145 |
| Werewolf | 53 | 53 |
| Seer | 20 | 20 |
| Medium | 20 | 20 |
| Hunter | 19 | 19 |
| Madman | 19 | 19 |

### 4.3 Game 01 Case Study

**Correct**: 5/16 (31.2%)
- Boy Peter (Werewolf) ✓
- Sister Friedel (Villager) ✓
- Young Man Joachim (Villager) ✓
- Merchant Albin (Villager) ✓
- Wounded Soldier Simon (Villager) ✓

**Errors**:
- Optimist Gerd: Predicted Werewolf (actual Villager)
- Village Girl Pamela: Predicted Werewolf (actual Villager)
- Father Jimzon: Predicted Villager (actual Seer)
- Farmer Jacob: Predicted Villager (actual Werewolf)

---

## 5. Key Implementation Details

### 5.1 Character Name Normalization

```python
name_map = {
    "Gerd": "Optimist Gerd",
    "Katharina": "Shepherd Katharina",
    ...
}
```

### 5.2 Data Schema

```python
class Prediction(BaseModel):
    id: int
    index: int  # game number
    character: str
    role: str  # Villager|Werewolf|Seer|Medium|Hunter|Madman
    wolf_score: float  # 0.0-1.0
```

### 5.3 Submission Format

```csv
id,index,character,role,wolf_score
1,1,Optimist Gerd,Werewolf,1.0
2,1,Boy Peter,Werewolf,1.0
...
673,30,Young Girl Liza,Villager,0.5
```

---

## 6. Limitations and Future Work

### Current Limitations

1. **Rule-based parsing**: May miss complex dialogue
2. **No LLM enhancement**: Analysis relies on heuristics
3. **Fixed scoring**: No adaptation to game-specific patterns

### Potential Improvements

1. **LLM Integration**: Ollama qwen2.5-7b for better analysis
2. **Deception Detection**: ML classifier for statement patterns
3. **Ensemble Methods**: Combine multiple scoring heuristics
4. **MMR Retrieval**: Diversify RAG context

---

## 7. Conclusion

We implemented a multi-agent Werewolf prediction system with three stages:
- **Stage 1 (Fetching)**: Rule-based transcript parsing
- **Stage 2 (Analysis)**: Heuristic role scoring
- **Stage 3 (Solving)**: Constraint-based role assignment

Current performance: 32.25% accuracy, 0.1938 Macro-F1. The system correctly identifies some werewolves but struggles with subtle deception patterns.

**Files**:
- `main.py`: CLI with `predict` and `predict-all` commands
- `submission.csv`: 673 predictions for Kaggle
- `assert/validate_submission.py`: Format validation

---

## References

- LangChain Ollama: https://python.langchain.com/docs/integrations/llms/ollama
- Pydantic: https://docs.pydantic.dev/
- scikit-learn: https://scikit-learn.org/