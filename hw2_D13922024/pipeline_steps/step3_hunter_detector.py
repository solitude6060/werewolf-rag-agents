#!/usr/bin/env python3
"""v410 Hunter dedicated detector for the v300 anchor.

This is a constrained role-only post-processor:
- no training or fine-tuning
- no external API
- no private GT reads
- preserves per-game role counts by swapping the Hunter slot with one
  Villager/Madman candidate in the same game
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from werewolf_variants import DATA, base, by_game, constraints, features, read_roles  # type: ignore


OUT = Path("experiments/submissions")
DEFAULT_PUBLIC_ANCHOR = OUT / "submission_v300_v260_plus_v290_public.csv"
DEFAULT_PRIVATE_ANCHOR = OUT / "submission_v300_v260_plus_v290_private.csv"
DEFAULT_PUBLIC_OUT = OUT / "submission_v410_hunter_detector_public.csv"
DEFAULT_PRIVATE_OUT = OUT / "submission_v410_hunter_detector_private.csv"

FIELDNAMES = ["id", "index", "character", "role", "wolf_score"]
PROTECTED_ROLES = {"Werewolf", "Seer", "Medium", "Hunter"}
TARGET_ROLES = {"Villager", "Madman"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)


def rows_by_game(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        out[row["index"]].append(row)
    return dict(out)


def role_counts(rows: list[dict[str, str]]) -> Counter[str]:
    return Counter(row["role"] for row in rows)


def validate_role_counts(rows: list[dict[str, str]]) -> None:
    for idx, game_rows in rows_by_game(rows).items():
        need = constraints(len(game_rows))
        if sum(need.values()) > len(game_rows):
            # Private split contains a tiny 3-player warm-up row group; the
            # anchor itself cannot satisfy the normal role budget there, and
            # v410 never edits games below 11 players.
            continue
        got = role_counts(game_rows)
        for role, count in need.items():
            if got[role] != count:
                raise ValueError(f"game {idx}: role {role} count {got[role]} != {count}")
        expected_villagers = len(game_rows) - sum(need.values())
        if got["Villager"] != expected_villagers:
            raise ValueError(
                f"game {idx}: Villager count {got['Villager']} != {expected_villagers}"
            )


def mention_metrics(txt: str, character: str) -> tuple[int, int]:
    """Approximate cross-vote / execution attention for evidence logging.

    The translated logs vary in formatting, so this is deliberately broad and
    only used as a small tie-breaker rather than a hard gate.
    """
    names = {character, base(character)}
    vote_terms = re.compile(r"\b(vote|lynch|execute|execution|provisional|final|decision)\b", re.I)
    exec_terms = re.compile(r"\b(executed|lynched|hanged)\b", re.I)
    cross_vote = 0
    executed = 0
    for line in txt.splitlines():
        lower = line.lower()
        if not any(name and name.lower() in lower for name in names):
            continue
        if vote_terms.search(line):
            cross_vote += 1
        if exec_terms.search(line):
            executed += 1
    return cross_vote, executed


def hunter_candidate_score(row: dict[str, str], metrics: Counter[str], cross_vote: int, executed: int) -> float:
    wolf_score = float(row["wolf_score"])
    return (
        3.0 * metrics["attacked"]
        - 0.015 * metrics["stmts"]
        - 0.20 * metrics["seer_claim"]
        - 0.15 * metrics["medium_claim"]
        - 0.10 * metrics["hunter_claim"]
        - 0.40 * metrics["retract"]
        - 0.50 * wolf_score
    )


def apply_hunter_detector(split: str, anchor: Path, output: Path) -> Path:
    rows = read_csv(anchor)
    by_idx = rows_by_game(rows)
    player_meta = by_game(read_roles(split))
    evidence_rows: list[dict[str, str]] = []

    for idx in sorted(by_idx):
        game_rows = by_idx[idx]
        players = player_meta[idx]
        if len(players) < 11:
            continue

        txt = (DATA / split / f"{idx}.txt").read_text(encoding="utf-8")
        fs, _, _ = features(txt, players)
        row_map = {row["character"]: row for row in game_rows}
        hunter_rows = [row for row in game_rows if row["role"] == "Hunter"]
        if len(hunter_rows) != 1:
            evidence_rows.append({
                "index": idx,
                "action": "skip",
                "old_hunter": "",
                "new_hunter": "",
                "score": "",
                "reason": f"expected one Hunter, found {len(hunter_rows)}",
            })
            continue

        old_hunter = hunter_rows[0]
        old_metrics = fs[old_hunter["character"]]
        old_ws = float(old_hunter["wolf_score"])

        if old_metrics["attacked"]:
            evidence_rows.append({
                "index": idx,
                "action": "skip",
                "old_hunter": old_hunter["character"],
                "new_hunter": "",
                "score": "",
                "reason": "anchor Hunter is night-killed; keep high-quality signal",
            })
            continue
        if not (0.01 <= old_ws <= 0.49):
            evidence_rows.append({
                "index": idx,
                "action": "skip",
                "old_hunter": old_hunter["character"],
                "new_hunter": "",
                "score": "",
                "reason": f"old Hunter wolf_score {old_ws:.6g} outside weak interval",
            })
            continue

        candidates: list[tuple[float, dict[str, str], int, int]] = []
        for player in players:
            ch = player["character"]
            row = row_map[ch]
            metrics = fs[ch]
            wolf_score = float(row["wolf_score"])
            if ch == old_hunter["character"] or base(ch) == "Gerd":
                continue
            if row["role"] in PROTECTED_ROLES or row["role"] not in TARGET_ROLES:
                continue
            if not metrics["attacked"]:
                continue
            if metrics["stmts"] > 70:
                continue
            if wolf_score > 0.05:
                continue
            cross_vote, executed = mention_metrics(txt, ch)
            score = hunter_candidate_score(row, metrics, cross_vote, executed)
            candidates.append((score, row, cross_vote, executed))

        if not candidates:
            evidence_rows.append({
                "index": idx,
                "action": "skip",
                "old_hunter": old_hunter["character"],
                "new_hunter": "",
                "score": "",
                "reason": "no gated night-killed Villager/Madman candidate",
            })
            continue

        candidates.sort(key=lambda item: (item[0], -fs[item[1]["character"]]["stmts"]), reverse=True)
        best_score, new_hunter, cross_vote, executed = candidates[0]
        old_role = old_hunter["role"]
        new_old_role = new_hunter["role"]

        old_hunter["role"] = new_old_role
        new_hunter["role"] = old_role
        if float(new_hunter["wolf_score"]) > 0.49:
            new_hunter["wolf_score"] = "0.49"

        nf = fs[new_hunter["character"]]
        evidence_rows.append({
            "index": idx,
            "action": "swap",
            "old_hunter": old_hunter["character"],
            "new_hunter": new_hunter["character"],
            "score": f"{best_score:.6f}",
            "reason": (
                f"new old_role={new_old_role} stmts={nf['stmts']} attacked={nf['attacked']} "
                f"seer_claim={nf['seer_claim']} medium_claim={nf['medium_claim']} "
                f"hunter_claim={nf['hunter_claim']} retract={nf['retract']} "
                f"cross_vote={cross_vote} executed_mentions={executed}"
            ),
        })

    validate_role_counts(rows)
    write_csv(rows, output)
    evidence_path = output.with_suffix(".evidence.csv")
    with evidence_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["index", "action", "old_hunter", "new_hunter", "score", "reason"],
        )
        w.writeheader()
        w.writerows(evidence_rows)
    print(f"wrote {output} ({len(rows)} rows)")
    print(f"wrote {evidence_path} ({len(evidence_rows)} evidence rows)")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-anchor", type=Path, default=DEFAULT_PUBLIC_ANCHOR)
    parser.add_argument("--private-anchor", type=Path, default=DEFAULT_PRIVATE_ANCHOR)
    parser.add_argument("--public-output", type=Path, default=DEFAULT_PUBLIC_OUT)
    parser.add_argument("--private-output", type=Path, default=DEFAULT_PRIVATE_OUT)
    args = parser.parse_args()

    apply_hunter_detector("public", args.public_anchor, args.public_output)
    apply_hunter_detector("private", args.private_anchor, args.private_output)


if __name__ == "__main__":
    main()
