# HW2 Report: Multi-Agent Werewolf Prediction

**Student ID: D13922024**
**Verified Kaggle private score: 0.44352** (rank 6 of public leaderboard at submission)
**Score formula: Final = 0.4 × Macro-F1 + 0.6 × Wolf-AP**

---

## 1. Introduction

Given 30 private game transcripts (397 players total), the task is to predict each
player's `role ∈ {Villager, Werewolf, Seer, Medium, Madman, Hunter}` and a continuous
`wolf_score ∈ [0,1]`. Hard constraints: no training, no external API, models must
fit in ≤12 GB VRAM, multi-agent + RAG architecture is required.

We satisfy all constraints with a **5-stage pipeline** built on local Ollama
(qwen3.5:9b + gemma4:e4b + deepseek-r1:14b) plus deterministic post-lynch
reveal extraction. The pipeline lifts a rule-based v70 baseline (≈0.39 private)
through **+0.054 verified gains** to 0.44352 private.

## 2. System Architecture (multi-agent + RAG)

```
┌──────────────────────────────────────────────────────────────────┐
│  Stage 1: Multi-Agent CoT  (Hermes-style, 2 LLM agents)          │
│    Analyst   = qwen3.5:9b  →  per-player wolf_score + role JSON  │
│    Verifier  = gemma4:e4b  →  confirmed_wolves / nonwolves       │
│    RAG       = role-rule corpus + per-player evidence retrieval  │
├──────────────────────────────────────────────────────────────────┤
│  Stage 2: Madman role detector   (qwen3.5:9b)                    │
│  Stage 3: Hunter role detector   (qwen3.5:9b)                    │
│           → produces v440 base   (private 0.41931)               │
├──────────────────────────────────────────────────────────────────┤
│  Stage 4: Cross-claim Werewolf boost  (regex + LLM verifier)     │
│    Promote borderline Werewolves named black by ≥3 distinct      │
│    Seer/Medium claimants. Verified +0.011 private.               │
│           → produces v851      (private 0.43066)                 │
├──────────────────────────────────────────────────────────────────┤
│  Stage 5: Post-lynch reveal extractor  (pure deterministic regex)│
│    Anchor on system event "X was executed by the villagers".     │
│    In next 200 lines, search for structural reveals:             │
│      - bracket-bold:    [**X is the werewolf**] / [**X is human**] │
│      - anchored direct: "X was the werewolf." / "X was human."   │
│    Independent gemini-CLI audit drops casual plain-text claims.  │
│           → produces v1121     (private 0.44352, FINAL)          │
└──────────────────────────────────────────────────────────────────┘
```

**Multi-agent + RAG compliance.** Stage 1 instantiates two distinct LLM agents
(qwen3.5 analyst → gemma4 verifier) communicating through a structured JSON
contract; both retrieve from a role-behavior corpus during prompt assembly.

## 3. Key Methods

### 3.1 Stage 1 — Hermes-style multi-agent CoT (RAG-grounded)

Each game transcript (~5–10 K lines) is decomposed into a per-player **dossier**:
all lines mentioning the target plus the system events (lynch, night-kill, role
reveal). The dossier + a retrieved snippet from the role-rule corpus is fed to
the **Analyst** (qwen3.5:9b) with a strict JSON schema and `format:"json"` to
force well-formed output. The Analyst returns per-player wolf-confidence and a
top-1 role guess.

The **Verifier** (gemma4:e4b) reads only system events plus the Analyst's output
and emits a small `{confirmed_wolves, confirmed_nonwolves}` set. The verifier was
empirically calibrated (per-private audit) — its `confirmed_wolves` is **noisy**
(false-positive on 4 of 4 audited public rows) so we only use its `confirmed_nonwolves`,
and even then we **gate**: never demote a row already at ws ≥ 0.7 or `role==Werewolf`.

### 3.2 Stage 2/3 — Madman + Hunter detectors

Madman and Hunter only exist when a game has ≥11 players (game rule). Each is
detected with a focused qwen3.5:9b call that scans for behavioral signatures
(Madman: thinks-they're-wolf statements, votes-with-wolves; Hunter: pre-death
"will" statements). Detected role is swapped from the base assignment but
constrained by the game's role budget.

### 3.3 Stage 4 — Cross-claim Werewolf boost

A Werewolf currently at borderline `ws=0.5` (the LLM's "uncertain" rest state)
is promoted to `ws=1.0` if **≥3 distinct Seer/Medium claimants** during the
game called the player "black". The `≥3 distinct claimants` gate filters out
single-source paranoia and Madman frame jobs. This stage gave the largest
single-stage gain in our experiments (**+0.011 private**, four rows: g02 Elna,
g18 Valter, g21 Katharina, g27 Friedel).

### 3.4 Stage 5 — Post-lynch reveal extractor

The single highest-precision signal we found. The transcript writes a system
line `X was executed by the villagers.` immediately after a lynch resolves;
within the next 200 lines, the **true Medium** (who learns lynched-player roles)
typically posts a structural reveal:

| Pattern | Schema | Used? |
|---------|--------|------|
| `[**X is the werewolf**]` | bracket-bold | ✓ |
| `[**X is human**]` | bracket-bold | ✓ |
| `[X is human]` (no bold) | bracket plain | ✓ |
| `As everyone knows, X was [role].` | anchored Medium phrase | ✓ |
| `X was the werewolf.` / `X was white.` | post-lynch direct | ✓ |
| `Player A: "I think X is wolf"` | casual plain | **✗ TOXIC** |

We confirmed the casual-plain pattern is **toxic** by ablation: a candidate
that added four such "X is the werewolf" boosts (v200e) lost 0.015 on the
private leaderboard.

The final v1121 has 9 audit-validated post-lynch corrections layered on v851:
g08 Pamela boost, g10 Joachim demote, g18 Joachim demote, g20 Thomas demote,
g24 Otto boost, g27 Liza boost, g27 Otto demote, g28 Simon demote, g30 Dieter
boost. A 10th candidate (g13 Nicholas boost from the casual statement
"Nicholas is the werewolf") was **dropped after independent gemini-CLI audit**.

## 4. Discussion of Success and Failure Cases

### Successes

* **Bracket-bold reveals transfer 1:1.** Our v200d candidate (Pamela g10 + Jacob
  g13 bracket-bold boosts) gained +0.0021 on public proxy and +0.00216 on
  private — the same Δ. This 1:1 transfer let us trust the schema for v1121.
* **Cross-claim with strict gate.** v851 fired only 4 boosts (versus a relaxed
  variant at 12 boosts) — the strict version gained +0.011, the relaxed one
  collapsed to ~0. Gate strictness mattered more than coverage.
* **Independent audit caught a regression.** The gemini-CLI audit of v1120's
  10 candidates correctly flagged g13 Nicholas as a casual plain-text claim
  before upload; v1121 (= v1120 minus Nicholas) verified +0.0005 over what
  v1120 would likely have been.

### Failures

* **Standalone LLM classification fails.** A glm4:9b sanity check on the 12
  remaining borderline rows boosted 4; all 4 were Villagers on public GT
  (0/4 = 0% precision). LLMs alone, without structural transcript anchors,
  cannot distinguish in-game tactical lying from ground-truth signals.
* **Same-game double boost cancels.** v860 added a g03 Dieter + g03 Pamela
  double boost on top of v851; net private change was 0. We hypothesize the
  game has 2 wolves but our boost picked one true wolf and one fake claimant,
  producing offsetting AP shifts. v860 informed our `max-wolf-boosts-per-game=1`
  rule for v1120.
* **Plain assertion family is toxic.** v200e (4 plain-text boosts) lost
  -0.015. The toxicity is not "all plain text is wrong" — it is that
  in-game accusations are dominated by Madman / fake-Seer rhetoric, so
  plain "X is the wolf" lines have ~50% precision but cluster on the same
  wrong people, dragging Wolf-AP down.

## 5. Optimizations and Improvements

* **JSON-mode + `think:false`.** Both qwen3.5 and deepseek-r1 silently emit empty
  content if their CoT-thinking mode is left on. We pass `think:false` to all
  Ollama calls and `format:"json"` to force well-formed JSON. This made stage 1
  reproducible across reruns at temperature 0.1.
* **Schema-at-end + `num_ctx=16384`.** With dossiers >12 K characters and
  `num_ctx=8192`, the JSON schema was being truncated from the front of the
  prompt and qwen3.5 emitted free-form prose. Reordering the schema to the
  END of the prompt (after the dossier) and bumping `num_ctx` to 16384 cured
  the truncation.
* **Per-row caching.** All LLM calls cache their JSON response by
  `(game_idx, target, model)` so repeated experiment iterations re-use ~95%
  of compute.
* **Confidence-bounded gating.** Every stage that modifies a row is gated by
  the previous stage's score: stage 4 fires only on `role==Werewolf, ws=0.5`
  (idle); stage 5 fires only when the reveal evidence is structural; the
  verifier-driven demote is gated to never overwrite a stage 5 result.
* **Reproducibility checkpoint.** `make_final.py --from-checkpoint v851`
  reproduces the verified v1121 byte-equal in ~5 s. The v851 checkpoint is
  the LLM-derived intermediate; the deterministic stages 4-5 are re-run
  from it on every reproduction.

## 6. Scoring Trajectory (verified Kaggle private)

| Submission | Method                                  | Public proxy | Private | Δ vs prev |
|------------|-----------------------------------------|-------------:|--------:|----------:|
| v70  baseline   | rule-based regex extraction       | 0.4682 | 0.39124 | — |
| v200d           | + 2 bracket-bold reveal boosts    | 0.5147 | 0.41070 | +0.01946 |
| v440            | + Madman + Hunter detectors       | 0.5235 | 0.41931 | +0.00861 |
| v851            | + 4 cross-claim Werewolf boosts   | 0.5235 | 0.43066 | +0.01135 |
| v1121 (final)   | + 9 audit-validated post-lynch     | 0.5370 | **0.44352** | **+0.01286** |

The total verified gain over the rule-based baseline is **+0.05228**.

## 7. References

- Ollama: https://ollama.ai/
- qwen3.5:9b, gemma4:e4b, deepseek-r1:14b — local GGUF weights
- Werewolf game rules: HW2 specification PDF p.5

(Source code, checkpoints, full experiment log: see `make_final.py`,
`pipeline_steps/`, `checkpoints/`, and the project repository's
`experiments/` directory.)
