#!/usr/bin/env python3
"""Small, leaderboard-informed post-processing fixes for v119-style CSVs.

The competition metric weights Wolf-AP by 60%, so score ordering matters even
when role assignments stay unchanged.  These fixes are deliberately conservative:

1. `--ww-floor`: predicted Werewolf rows should not rank below ordinary
   non-wolves.  Raise only Werewolf wolf_score values below the floor.
2. `--guarded-madman-zero`: v121 showed that zeroing every predicted Madman
   overfits public and hurts private.  This option only zeroes moderate-score
   Madman rows when both cached LLM agents also rate the player as low/non-wolf.

No training, fine-tuning, external API, or >12GB model is used.  The optional LLM
guard reads existing local cache files produced by werewolf_v105_llm.py.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


MODELS = ("qwen3.5_9b", "deepseek-r1_14b")
FIELDNAMES = ["id", "index", "character", "role", "wolf_score"]


def norm(name: str) -> str:
    return "".join(ch.lower() for ch in name if ch.isalnum())


def cached_llm_votes(split: str, idx: str, character: str, cache_dir: Path) -> list[tuple[str, str, float]]:
    """Return [(model, role, wolf_score)] from local JSON cache for one player."""
    target = norm(character)
    votes: list[tuple[str, str, float]] = []
    for model in MODELS:
        path = cache_dir / f"{split}_{idx}_v105_{model}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for pred in data.get("parsed", {}).get("predictions", []):
            candidate = norm(str(pred.get("character", "")))
            if target in candidate or candidate in target:
                votes.append(
                    (
                        model,
                        str(pred.get("role", "")),
                        float(pred.get("wolf_score", 0.0)),
                    )
                )
                break
    return votes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--split", choices=("public", "private"), required=True)
    parser.add_argument("--ww-floor", type=float, default=None)
    parser.add_argument("--guarded-madman-zero", action="store_true")
    parser.add_argument("--cache-dir", type=Path, default=Path("experiments/llm_runs"))
    args = parser.parse_args()

    rows = list(csv.DictReader(args.input_csv.open(newline="", encoding="utf-8")))
    changes: list[str] = []

    for row in rows:
        old = float(row["wolf_score"])
        new = old

        if args.ww_floor is not None and row["role"] == "Werewolf" and old < args.ww_floor:
            new = args.ww_floor

        if args.guarded_madman_zero and row["role"] == "Madman":
            votes = cached_llm_votes(args.split, row["index"], row["character"], args.cache_dir)
            max_llm_ws = max((vote[2] for vote in votes), default=0.0)
            any_llm_wolf = any(vote[1] == "Werewolf" for vote in votes)
            # Guard against the v121 failure mode: keep high-base-score Madmen and
            # any player an LLM agent thinks could be Werewolf.
            if 0.05 < old < 0.45 and len(votes) >= 2 and max_llm_ws <= 0.25 and not any_llm_wolf:
                new = 0.0

        if new != old:
            row["wolf_score"] = f"{new:.6g}"
            changes.append(
                f'{row["index"]} {row["character"]}: {row["role"]} {old:.6g}->{new:.6g}'
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{args.output}: {len(rows)} rows, {len(changes)} score changes")
    for change in changes:
        print("  " + change)


if __name__ == "__main__":
    main()
