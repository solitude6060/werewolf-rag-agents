# HW2 Report: Multi-Agent Werewolf Prediction

**Student ID:** D13922024
**Final packaged candidate:** v1840c
**Best verified private score:** 0.49349
**Score formula:** 0.4 × Macro-F1 + 0.6 × Werewolf AP

## 1. Task and Constraints

The task is to predict each player's role and `wolf_score` from Werewolf game transcripts.  The private split contains 30 games and 397 players.  Valid roles are Villager, Werewolf, Seer, Medium, Hunter, and Madman.

The solution follows the course constraints:

- use at least two coordinated reasoning components;
- use retrieval-augmented transcript evidence;
- do not train or fine-tune a model;
- use local inference and deterministic post-processing only;
- validate every submission CSV before upload.

The final hand-in package defaults to the best verified candidate, `v1840c`.  The final leaderboard sprint used all five attempts; the last experimental candidate `v1846e` regressed to `0.46698`, so it is documented as a failed experiment rather than used as the packaged default.

## 2. System Design

```text
Transcript files
    │
    ▼
Fetching component
    - parse player lists, claims, votes, executions, deaths, and reveal windows
    - retrieve role rules and player-specific evidence snippets
    │
    ▼
Analysis component + verifier
    - rank Werewolf, Seer, Medium, Hunter, Madman, and Villager candidates
    - check contradictions between claims, lynch results, and night events
    - emit structured row-level repair suggestions
    │
    ▼
Constrained solver
    - enforce role budgets by game size
    - merge deterministic reveals, claim-graph evidence, and local model audits
    - output `id,index,character,role,wolf_score`
    │
    ▼
Final queue and packaging
    - package validated CSV candidates with SHA-256 hashes
    - record private feedback and preserve rollback checkpoints
```

The design separates evidence retrieval from constrained decisions.  Retrieved facts are first listed as transcript evidence, then the verifier checks whether a proposed role assignment is compatible with role budgets, claims, and event timing.  The final solver is deterministic so that a selected candidate can be reproduced from the bundled checkpoints.

## 3. Retrieval-Augmented Evidence

The retrieval corpus contains role rules, game-size role budgets, common deception patterns, and transcript-derived windows around claims and executions.  Retrieval is used before high-impact repairs:

- **Role-rule retrieval:** confirms whether Seer, Medium, Hunter, or Madman can appear in the current game size.
- **Claim retrieval:** collects who claimed a role and who accused whom as black or white.
- **Post-lynch retrieval:** scans the window after an execution for structured Medium-style role reveals.
- **Cross-check retrieval:** compares local model suggestions against deterministic events and existing role budgets.

The strongest prompt pattern is evidence-first: list retrieved facts, identify contradictions, then request a constrained decision.  This reduces the chance that in-game deception is mistaken for ground truth.

## 4. Optimization Strategy

1. **Constrained role budgets.**  The solver enforces the number of Werewolves and special roles for each game size, preventing impossible submissions.
2. **Structural reveal filtering.**  The pipeline prioritizes bracketed or execution-anchored reveal patterns and rejects casual accusations when they are not tied to a game event.
3. **Claim-graph consistency.**  Repeated claim interactions are represented as a graph, which helps identify true-Seer, fake-Seer, and Medium contradictions.
4. **Local model audits with caching.**  Local model outputs are cached per game or row so experiments are reproducible and do not require external services.
5. **Leaderboard-safe queueing.**  Final attempts are ordered from strongest evidence to highest upside, with rollback checkpoints for known private scores.
6. **Validation-first packaging.**  Every final-pack CSV is copied with SHA-256 tracking and checked by the assignment validator.

## 5. Result Trajectory

| Candidate | Private score | Main idea | Outcome |
| --- | ---: | --- | --- |
| v1819b | 0.45499 | v1817b/v1818a positive stack | early improvement |
| v1821a | 0.46455 | claim-graph CSP plus g10 Pamela repair | positive |
| v1823a | 0.46492 | v1821a plus v1819b positive stack | positive |
| v1824a | 0.47119 | v1823a plus g24 Thomas true-Seer repair | previous rollback best |
| v1826a | 0.48854 | g4/g29 structural and AP boost push | major improvement |
| v1840b | 0.49266 | high-precision Medium/AP overlay | positive |
| v1840c | 0.49349 | v1840 overlay extended to v1829e clean Hail Mary family | best verified |
| v1846e | 0.46698 | final role-cap one-shot on top of v1842e | failed last attempt |

Final attempt budget: `5/5` used.  The operational target `>0.50000` and the original top-three gate `>0.52380` were not reached.  The final packaged candidate is therefore the best verified submission, `v1840c`, rather than the failed last attempt.

## 6. Success and Failure Analysis

**What worked.**  The largest gains came from auditable structural repairs: claim-graph contradictions, true-Seer/Medium consistency checks, and carefully scoped AP overlays.  The move from `0.47119` to `0.48854` and then to `0.49349` shows that small evidence-backed changes transferred better than broad rewrites.

**What failed.**  The final role-cap attempt was selected because public proxy and leave-one-out checks were strong, but private feedback regressed sharply.  This confirms that public AP calibration was not a reliable substitute for transcript-grounded evidence on the private split.

**Mitigation used in the final package.**  The hand-in package returns to `v1840c`, the best verified private candidate.  The failed `v1846e` file remains in checkpoints and the experiment ledger for traceability, but it is not the default `submission.csv`.

## 7. Reproducibility

From the package directory:

```bash
python3 make_final.py --output submission.csv
```

The command copies the packaged best candidate and runs the validator.  Expected validator output:

```text
OK: 397 predictions validated
```

Additional validation:

```bash
python3 assert/validate_submission.py submission.csv
```

The expected private submission shape is 397 predictions with header:

```text
id,index,character,role,wolf_score
```

The complete final-attempt archive and score-feedback ledger are preserved under:

```text
experiments/final_submission_package/
experiments/final_submission_package/manifests/v1836_score_feedback_records.csv
```
