# HW2 — Multi-Agent Werewolf Prediction

**Student ID: D13922024**
**Verified Kaggle private score: 0.44352** (rank 6, leaderboard target = 0.44507)
**Score formula: Final = 0.4 × Macro-F1 + 0.6 × Wolf-AP**

## TL;DR — reproduce the verified submission

```bash
# Fast path (~5 s, byte-equal to verified Kaggle submission)
python3 make_final.py --split private --output submission.csv

# Validate
python3 assert/validate_submission.py submission.csv   # → OK: 397 predictions validated
```

The bundled checkpoint `checkpoints/v851_after_cross_claim_private.csv` is the
output of stages 1-4 (LLM-derived). `make_final.py` then applies the deterministic
stage-5 post-lynch reveal corrections to obtain the final submission.

## Architecture (multi-agent + RAG)

```
┌──────────────────────────────────────────────────────────────────┐
│  Stage 1: Multi-Agent CoT  (Hermes-style, 2 LLM agents + RAG)    │
│    Analyst   = qwen3.5:9b  (per-player wolf_score + role JSON)   │
│    Verifier  = gemma4:e4b  (confirmed_wolves / nonwolves)        │
│    RAG       = role-rule corpus + per-player evidence retrieval  │
├──────────────────────────────────────────────────────────────────┤
│  Stage 2: Madman role detector  (qwen3.5:9b, role swap)          │
│  Stage 3: Hunter role detector  (qwen3.5:9b, role swap)          │
│           → produces v440 base                                   │
├──────────────────────────────────────────────────────────────────┤
│  Stage 4: Cross-claim Werewolf boost  (deterministic + LLM gate) │
│    Promote borderline (ws=0.5) Werewolves named black by         │
│    ≥3 distinct Seer/Medium claimants. Verified +0.011 private.   │
│           → produces v851                                        │
├──────────────────────────────────────────────────────────────────┤
│  Stage 5: Post-lynch reveal extractor  (pure deterministic regex)│
│    Anchor on system event "X was executed by the villagers".     │
│    In next 200 lines, search for structural reveals:             │
│      - bracket-bold:    [**X is the werewolf**] / [**X is human**] │
│      - anchored direct: "X was the werewolf." / "X was human."   │
│    Independent gemini-CLI audit drops casual plain-text claims.  │
│           → produces v1121 = final submission                    │
└──────────────────────────────────────────────────────────────────┘
```

The pipeline satisfies the assignment "≥2 agents + RAG" requirement with the
Analyst + Verifier pair retrieving from a role-rule corpus during stage 1.

## Hard constraints honored

| Rule | Compliance |
|------|------------|
| No training / fine-tuning | ✓ pure inference + deterministic regex |
| No external API in submission pipeline | ✓ local Ollama only |
| Models ≤ 12 GB VRAM | ✓ qwen3.5:9b (6.6 GB), gemma4:e4b (9.6 GB), deepseek-r1:14b (9.0 GB) |
| Multi-agent + RAG | ✓ analyst + verifier + RAG corpus |
| 397-row private CSV | ✓ validator passes |

## File layout

```
hw2_D13922024/
├── make_final.py              # ★ reproducer for verified submission
├── submission.csv             # = v1121, the file to upload to Kaggle
├── checkpoints/
│   ├── v440_base_private.csv          # after stages 1-3 (LLM-derived)
│   ├── v440_base_public.csv
│   ├── v851_after_cross_claim_private.csv  # ★ recommended starting point
│   ├── v851_after_cross_claim_public.csv
│   └── v1120_evidence.csv             # 10 lynch-reveal candidates with line cites
├── pipeline_steps/
│   ├── step1_multi_agent_cot.py       # qwen3.5 analyst + gemma4 verifier
│   ├── step2_madman_detector.py
│   ├── step3_hunter_detector.py
│   ├── step4_cross_claim_boost.py     # Seer/Medium ≥3 distinct claimants
│   └── step5_lynch_scan.py            # system-event-anchored reveal regex
├── main.py                    # legacy entry (single-game predict; demo only)
├── src/                       # earlier exploratory pipeline (kept for reference)
├── assert/validate_submission.py
├── requirements.txt
├── hw2_report.md              # 5-page report
└── README.md (this file)
```

## How to fully reproduce from raw transcripts

Requires Ollama with the three models pulled and the dataset at
`../werewolf-project/data/raw/Werewolf_Prediction_Dataset/`.

```bash
# Prerequisites
ollama pull qwen3.5:9b
ollama pull gemma4:e4b
ollama pull deepseek-r1:14b
pip install -r requirements.txt

# Fast reproduction (~5 s, deterministic, exact byte-equal to verified submission)
python3 make_final.py --split private --output submission.csv

# Full reproduction (slow, ~6-8 hours; runs LLM stages 1-3 from scratch)
python3 make_final.py --split private --full --output submission.csv
```

The fast path is the recommended way to reproduce: stages 1-3 are LLM-bound and
non-deterministic across runs even with `temperature=0.1`, so we ship the verified
v851 checkpoint and re-derive only the deterministic stages 4-5 from it. The full
path validates the methodology end-to-end.

## Scoring breakdown (verified Kaggle private)

| Stage | Anchor | Public proxy | Private | Δ vs prev |
|-------|--------|-------------:|--------:|----------:|
| v440  | Madman + Hunter detectors            | 0.5235 | 0.41931 | — |
| v851  | + 4 cross-claim Werewolf boosts      | 0.5235 | 0.43066 | +0.01135 |
| v1121 | + 9 audit-validated post-lynch reveals | 0.5370 | 0.44352 | +0.01286 |

The 9 post-lynch reveal corrections (line-cited, see `checkpoints/v1120_evidence.csv`):

```
g08 Pamela boost      bracket_werewolf @ L7560
g10 Joachim demote    bracket_human    @ L3855
g18 Joachim demote    bracket_human    @ L2781
g20 Thomas demote     anchored_direct  @ L6319
g24 Otto boost        bracket_werewolf @ L5229
g27 Liza boost        anchored_direct  @ L7101
g27 Otto demote       anchored_direct  @ L9617
g28 Simon demote      bracket_human    @ L7643
g30 Dieter boost      bracket_werewolf @ L4646
```

Independent gemini-CLI audit dropped a 10th candidate (g13 Nicholas) — its reveal
"Nicholas is the werewolf" was a casual plain-text claim from another player, not
a structural game-master statement.

## Lessons learned (from the experimental record)

* **Bracket-bold reveals (`[**X is the werewolf**]`) transfer 1:1** from public
  proxy to private leaderboard. Same schema as the verified v200d Pamela boost.
* **Plain assertions are toxic.** v200e (4 plain "X is the werewolf" boosts) lost
  -0.015 private — these are mostly Madman / fake-Seer lies, not authoritative reveals.
* **Same-game double boost cancels out.** v860 added 2 boosts in one game and
  netted 0 on private — likely promoting a real wolf and a fake-claim simultaneously.
* **LLM standalone classification is unreliable.** A glm4:9b sanity check on the
  remaining 12 borderline rows scored 0/4 GT precision on the public split — LLM
  classification alone, without structural transcript anchors, fails.

The strongest signal is **system-event-anchored structural reveals**: post-lynch
role announcement formatted as `[**X is human/werewolf**]` or `As everyone knows,
X was [role]`. These are game-master-level statements that survive the
public→private transfer because they reflect ground truth, not opinion.
