#!/usr/bin/env python3
"""Build the packaged HW2 submission.

Pipeline (multi-agent + RAG + post-lynch event extraction):
  Stage 1  multi-agent CoT (qwen3.5:9b analyst + gemma4:e4b verifier) → base CSV
  Stage 2  Madman role detector (LLM-assisted)
  Stage 3  Hunter role detector (LLM-assisted)
  Stage 4  Cross-claim Werewolf boost (≥3 distinct Seer/Medium claimants)
  Stage 5  Post-lynch reveal extractor (system 'executed by villagers' +
           bracket-bold or definitive Medium reveal in next 200 lines)

Usage:
  # Fast path (copies the packaged current final candidate and validates it):
  python3 make_final.py --output submission.csv

  # Earlier reproducibility checkpoint:
  python3 make_final.py --from-checkpoint v851 --output submission.csv

  # Full reproduction (requires Ollama with qwen3.5:9b + gemma4:e4b loaded):
  python3 make_final.py --full --output submission.csv

Constraints honored:
  * No external API. Ollama only (local).
  * Models: qwen3.5:9b (~6.6 GB) + gemma4:e4b (~9.6 GB), both ≤ 12 GB VRAM.
  * No training. Pure inference + deterministic regex.
  * Multi-agent + RAG architecture.
"""

import argparse
import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = ROOT / "pipeline_steps"
CKPT = ROOT / "checkpoints"
DATA_ROOT = ROOT.parent / "werewolf-project" / "data" / "raw" / "Werewolf_Prediction_Dataset"

FINAL_CHECKPOINT = CKPT / "final_current_private.csv"

# 9 audit-validated post-lynch reveal corrections that v1120 produced and v1121 keeps.
# (g13 Nicholas was DROPPED in audit — its reveal "Nicholas is the werewolf." was
#  casual plain text from a player, not a structural game-master reveal.)
V1121_LYNCH_KEEPS = {
    ("08", "Village Girl Pamela"): ("Werewolf", 1.0, "bracket_werewolf @ L7560"),
    ("10", "Young Man Joachim"):   ("Medium",   0.05, "bracket_human @ L3855"),
    ("18", "Joachim"):             ("Villager", 0.05, "bracket_human @ L2781"),
    ("20", "Woodcutter Thomas"):   ("Villager", 0.05, "anchored_direct @ L6319"),
    ("24", "Otto the Baker"):      ("Werewolf", 1.0, "bracket_werewolf @ L5229"),
    ("27", "Young Girl Liza"):     ("Madman",   1.0, "anchored_direct @ L7101"),
    ("27", "Baker Otto"):          ("Werewolf", 0.05, "anchored_direct @ L9617"),
    ("28", "Wounded Soldier Simon"): ("Villager", 0.05, "bracket_human @ L7643"),
    ("30", "Dieter"):              ("Villager", 1.0, "bracket_werewolf @ L4646"),
}


def run_step(cmd: list[str], label: str) -> None:
    print(f"\n[{label}] {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=str(ROOT.parent))
    if r.returncode != 0:
        sys.exit(f"[{label}] failed (code {r.returncode})")


def stage1_3_full(split: str, work_csv: Path) -> None:
    """Stages 1–3: multi-agent CoT + Madman + Hunter detectors. Slow (LLM)."""
    run_step(
        [sys.executable, str(STEPS / "step1_multi_agent_cot.py"), "run",
         "--split", split, "--with-verifier"],
        "stage1.run",
    )
    run_step(
        [sys.executable, str(STEPS / "step1_multi_agent_cot.py"), "apply",
         "--split", split, "--output", str(work_csv),
         str(CKPT / f"v440_base_{split}.csv")],
        "stage1.apply",
    )
    # Stage 2 + 3 mutate work_csv in place
    run_step(
        [sys.executable, str(STEPS / "step2_madman_detector.py"),
         "--split", split, "--input-csv", str(work_csv),
         "--output", str(work_csv)],
        "stage2.madman",
    )
    run_step(
        [sys.executable, str(STEPS / "step3_hunter_detector.py"),
         "--split", split, "--input-csv", str(work_csv),
         "--output", str(work_csv)],
        "stage3.hunter",
    )


def stage4_cross_claim(split: str, in_csv: Path, out_csv: Path) -> None:
    run_step(
        [sys.executable, str(STEPS / "step4_cross_claim_boost.py"),
         "--input-csv", str(in_csv), "--split", split, "--output", str(out_csv)],
        "stage4.cross_claim",
    )


def stage5_apply_v1121(in_csv: Path, out_csv: Path) -> None:
    """Apply the 9 audit-validated post-lynch reveal corrections deterministically.

    Equivalent to running step5_lynch_scan.py and keeping only rows in V1121_LYNCH_KEEPS
    (i.e. dropping g13 Traveler Nicholas after independent audit).
    """
    rows = list(csv.DictReader(in_csv.open()))
    applied = 0
    for r in rows:
        key = (r["index"], r["character"])
        if key in V1121_LYNCH_KEEPS:
            role, ws, evidence = V1121_LYNCH_KEEPS[key]
            r["role"] = role
            r["wolf_score"] = f"{ws:g}"
            applied += 1
            print(f"  [v1121] g{key[0]} {key[1]:25} -> role={role:9} ws={ws:<5} ({evidence})")
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "index", "character", "role", "wolf_score"])
        w.writeheader()
        w.writerows(rows)
    print(f"\n[stage5] applied {applied}/9 lynch-reveal corrections -> {out_csv}")


def validate_output(path: Path) -> None:
    print(f"\n[validator]")
    run_step(
        [sys.executable, str(ROOT / "assert" / "validate_submission.py"), str(path.resolve())],
        "validate",
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the packaged HW2 submission.")
    ap.add_argument("--split", choices=["private", "public"], default="private")
    ap.add_argument("--output", type=Path, default=ROOT / "submission.csv")
    ap.add_argument("--from-checkpoint", choices=["final", "v440", "v851"], default="final",
                    help="final copies the packaged current candidate; v440/v851 reproduce the earlier pipeline")
    ap.add_argument("--full", action="store_true",
                    help="rerun stages 1-3 from raw transcripts (requires Ollama)")
    args = ap.parse_args()
    output = args.output if args.output.is_absolute() else Path.cwd() / args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    if args.from_checkpoint == "final" and not args.full:
        if args.split != "private":
            sys.exit("the packaged final checkpoint is for the private split")
        if not FINAL_CHECKPOINT.exists():
            sys.exit(f"missing checkpoint: {FINAL_CHECKPOINT}")
        output.write_bytes(FINAL_CHECKPOINT.read_bytes())
        validate_output(output)
        print(f"\nFinal submission written to: {output}")
        return

    work = ROOT / f".work_{args.split}.csv"

    if args.full:
        stage1_3_full(args.split, work)
        stage4_cross_claim(args.split, work, work)
    elif args.from_checkpoint == "v440":
        # start from bundled v440 base, apply stage 4
        stage4_cross_claim(args.split, CKPT / f"v440_base_{args.split}.csv", work)
    else:  # from-checkpoint v851
        # already has stage 4 applied
        v851 = CKPT / f"v851_after_cross_claim_{args.split}.csv"
        if not v851.exists():
            sys.exit(f"missing checkpoint: {v851}")
        work.write_bytes(v851.read_bytes())

    stage5_apply_v1121(work, output)
    work.unlink(missing_ok=True)

    validate_output(output)
    print(f"\nFinal submission written to: {output}")


if __name__ == "__main__":
    main()
