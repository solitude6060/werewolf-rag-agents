# HW2 Report: Multi-Agent Werewolf Prediction

**Student ID:** D13922024
**Best verified private score so far:** 0.47119
**Score formula:** 0.4 × Macro-F1 + 0.6 × Werewolf AP

## 1. Task and Constraints

The task is to predict each player's role and `wolf_score` from Werewolf game transcripts.  The private split contains 30 games and 397 players.  The valid roles are Villager, Werewolf, Seer, Medium, Hunter, and Madman.  The system follows the course constraints: at least two coordinated reasoning components, retrieval-augmented evidence use, no model training or fine-tuning, local inference only, and submission CSV validation before upload.

## 2. System Design and Prompt Structure

```text
Transcript files
    │
    ▼
Fetching Agent
    - parse player list, claims, votes, executions, deaths, and reveal windows
    - retrieve role rules and player-specific evidence snippets
    │
    ▼
Analysis Agent + Verifier
    - rank Werewolf, Seer, Medium, Hunter, Madman, and Villager candidates
    - check contradictions between claims, lynch results, and night events
    - emit structured row-level repair suggestions
    │
    ▼
Constrained Solver
    - enforce role budgets per game size
    - merge deterministic reveals, claim graph evidence, and local model audits
    - output `id,index,character,role,wolf_score`
```

The retrieval layer is intentionally narrow: for each target player it gathers direct utterances, role claims, vote interactions, execution context, and nearby reveal statements.  The prompt then separates factual evidence from inference.  This reduces the chance that in-game deception is mistaken for ground truth.

## 3. RAG Details

The RAG corpus contains role rules, game-size role budgets, common deception patterns, and transcript-derived evidence windows.  Retrieval is used before every high-impact repair:

- **Role-rule retrieval:** identifies whether Seer, Medium, Hunter, or Madman can exist in the current game size.
- **Claim retrieval:** collects who claimed a role and who accused whom as black or white.
- **Post-lynch retrieval:** scans the window after an execution for structured Medium-style role reveals.
- **Cross-check retrieval:** compares local model suggestions against deterministic events and existing role budgets.

The strongest prompt pattern is evidence-first: list retrieved facts, ask for contradictions, then request a constrained JSON-like decision.  The final solver is deterministic so that a validated candidate can be reproduced from the same evidence decisions.

## 4. Success and Failure Cases

**Success cases.**  Structured reveal windows transferred well from public checks to private submissions.  Post-lynch statements anchored to an execution event often indicated whether the executed player was human or Werewolf.  Claim-graph repairs also helped when multiple independent claimants converged on the same contradiction.

**Failure cases.**  Free-form accusations were noisy.  A player saying that another player is a wolf is often deception, pressure, or a fake-claim tactic rather than a reliable label.  Broad all-in stacks also had high variance: adding too many uncertain repairs could improve one role while hurting Werewolf AP ordering elsewhere.

**Mitigation.**  Later candidates prefer small, auditable repairs.  Each high-risk row is tied back to a game, character, evidence type, and expected role-budget effect before it is added to the final queue.

## 5. Optimizations and Improvements

1. **Constrained role budgets.**  The solver enforces the number of Werewolves and special roles for each game size, preventing impossible submissions.
2. **Structural reveal filtering.**  The pipeline prioritizes bracketed or execution-anchored reveal patterns and downweights casual statements.
3. **Claim-graph consistency.**  Repeated claim interactions are represented as a graph, which helps identify true-Seer, fake-Seer, and Medium contradictions.
4. **Local model audits with caching.**  Local model outputs are cached per game/row so that experiments are reproducible and do not require external services.
5. **Leaderboard-safe queueing.**  Final attempts are ordered from strongest evidence to highest upside, with a rollback set of the five best verified submissions.
6. **Validation-first packaging.**  Every final-pack CSV is copied with SHA256 tracking and checked by the assignment validator before upload.

## 6. Result Trajectory

| Candidate | Private score | Main idea |
| --- | ---: | --- |
| v1819b | 0.45499 | v1817b/v1818a positive stack |
| v1821a | 0.46455 | claim-graph CSP plus g10 Pamela repair |
| v1823a | 0.46492 | v1821a plus v1819b positive stack |
| v1823b | 0.46492 | v1823 stack plus g30 Dieter branch |
| v1824a | 0.47119 | v1823a plus g24 Thomas true-Seer repair |

The current best verified score is `0.47119`.  The final queue is prepared separately because the remaining attempts should be chosen from real Kaggle feedback gathered during final attempts.

## 7. Reproducibility

The package can be rebuilt from the workspace root with:

```bash
python3 experiments/scripts/v1835_final_submission_pack.py --preset full
```

The selected Kaggle CSV must pass:

```bash
python3 werewolf-project/assert/validate_submission.py <candidate.csv>
```

The expected private submission shape is 397 predictions with header `id,index,character,role,wolf_score`.
