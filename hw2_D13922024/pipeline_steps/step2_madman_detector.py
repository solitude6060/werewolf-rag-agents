#!/usr/bin/env python3
"""v400 Madman detector.

This prototype tries one guarded role-count-preserving operation:
swap the anchor Madman role with a non-selected Seer/Medium claimant who is
also explicitly discussed as a Madman in the transcript.

It intentionally does not use private GT or leaderboard feedback.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

import v260_true_medium_selector as medium
import v310_true_seer_selector as seer


FIELDNAMES = ["id", "index", "character", "role", "wolf_score"]
DATA = Path("werewolf-project/data/raw/Werewolf_Prediction_Dataset")


MADMAN_WORD = re.compile(r"\bmadm[ae]n\b|\bmadness\b", re.I)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def base_name(character: str) -> str:
    return seer.base_name(character)


def name_positions(text: str, names: set[str]) -> list[int]:
    lowered = text.lower()
    out: list[int] = []
    for name in names:
        if not name:
            continue
        pattern = re.compile(rf"\b{re.escape(name.lower())}\b")
        out.extend(match.start() for match in pattern.finditer(lowered))
    return out


def madman_mention_count(character: str, utterances: list[seer.Utterance], window: int) -> int:
    names = {character, base_name(character)}
    count = 0
    for utterance in utterances:
        text = utterance.text
        mad_positions = [match.start() for match in MADMAN_WORD.finditer(text)]
        if not mad_positions:
            continue
        char_positions = name_positions(text, names)
        if any(abs(cp - mp) <= window for cp in char_positions for mp in mad_positions):
            count += 1
    return count


def collect_claims(
    players: list[dict[str, str]],
    utterances: list[seer.Utterance],
    lk: dict[str, str],
) -> dict[str, dict[str, int]]:
    claims: dict[str, dict[str, int]] = defaultdict(lambda: {"seer": 0, "medium": 0})
    for utterance in utterances:
        speaker = seer.resolve(utterance.character, lk)
        if not speaker:
            continue
        if seer.SEER_CLAIM.search(utterance.text) and not seer.NOT_SEER.search(utterance.text):
            claims[speaker]["seer"] += 1
        if medium.MEDIUM_CLAIM.search(utterance.text) and not medium.NOT_MEDIUM.search(utterance.text):
            claims[speaker]["medium"] += 1
    for player in players:
        claims.setdefault(player["character"], {"seer": 0, "medium": 0})
    return claims


def select_swap(
    index: str,
    players: list[dict[str, str]],
    roles: dict[str, str],
    scores: dict[str, float],
    min_claims: int,
    min_madman_mentions: int,
    mention_window: int,
    require_mention_beats_anchor: bool,
) -> tuple[str | None, str | None, str, dict[str, dict[str, str]]]:
    lines = (DATA / players[0]["index_split"] / f"{index}.txt").read_text(encoding="utf-8").splitlines()
    lk = seer.lookup(players)
    utterances = seer.parse_utterances(lines)
    claims = collect_claims(players, utterances, lk)

    current_madman = next((p["character"] for p in players if roles.get(p["character"]) == "Madman"), None)
    if not current_madman:
        return None, None, "no anchor Madman to swap", {}

    anchor_mentions = madman_mention_count(current_madman, utterances, mention_window)
    selected_special = {p["character"] for p in players if roles.get(p["character"]) in {"Seer", "Medium"}}

    candidates: list[tuple[tuple[int, int, float], str, str]] = []
    details: dict[str, dict[str, str]] = {}
    for player in players:
        character = player["character"]
        role = roles.get(character, "")
        if character == current_madman or character in selected_special:
            continue
        if role != "Villager":
            continue
        claim_total = claims[character]["seer"] + claims[character]["medium"]
        if claim_total < min_claims:
            continue
        mentions = madman_mention_count(character, utterances, mention_window)
        if mentions < min_madman_mentions:
            continue
        if require_mention_beats_anchor and mentions <= anchor_mentions:
            continue
        score = (mentions, claim_total, -scores.get(character, 0.0))
        reason = (
            f"mentions={mentions}; claims={claim_total}; "
            f"seer_claim={claims[character]['seer']}; medium_claim={claims[character]['medium']}; "
            f"anchor_madman={current_madman}; anchor_mentions={anchor_mentions}; "
            f"old_score={scores.get(character, 0.0):.6g}"
        )
        candidates.append((score, character, reason))
        details[character] = {
            "mentions": str(mentions),
            "claims": str(claim_total),
            "seer_claim": str(claims[character]["seer"]),
            "medium_claim": str(claims[character]["medium"]),
            "old_score": f"{scores.get(character, 0.0):.6g}",
        }

    if not candidates:
        return None, current_madman, "no guarded non-selected Villager claimant beat thresholds", details
    candidates.sort(reverse=True)
    if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
        return None, current_madman, f"ambiguous tie: {candidates[0][1]} vs {candidates[1][1]}", details
    _, selected, reason = candidates[0]
    return selected, current_madman, reason, details


def apply(
    input_csv: Path,
    output_csv: Path,
    split: str,
    min_claims: int,
    min_madman_mentions: int,
    mention_window: int,
    require_mention_beats_anchor: bool,
) -> None:
    rows = read_csv(input_csv)
    rows_by_key = {(row["index"], row["character"]): row for row in rows}
    games = seer.by_game(seer.read_roles(split))
    evidence: list[dict[str, str]] = []
    selector_rows: list[dict[str, str]] = []

    for index, players in sorted(games.items()):
        if len(players) < 11:
            selector_rows.append({"index": index, "selected": "", "swapped_out": "", "reason": "no Madman in small game"})
            continue
        tagged_players = [dict(player, index_split=split) for player in players]
        roles = {
            player["character"]: rows_by_key[(index, player["character"])]["role"]
            for player in players
        }
        scores = {
            player["character"]: float(rows_by_key[(index, player["character"])]["wolf_score"])
            for player in players
        }
        selected, swapped_out, reason, _details = select_swap(
            index=index,
            players=tagged_players,
            roles=roles,
            scores=scores,
            min_claims=min_claims,
            min_madman_mentions=min_madman_mentions,
            mention_window=mention_window,
            require_mention_beats_anchor=require_mention_beats_anchor,
        )
        selector_rows.append({
            "index": index,
            "selected": selected or "",
            "swapped_out": swapped_out or "",
            "reason": reason,
        })
        if not selected or not swapped_out:
            continue
        selected_row = rows_by_key[(index, selected)]
        old_madman_row = rows_by_key[(index, swapped_out)]
        selected_old_role = selected_row["role"]
        old_madman_old_role = old_madman_row["role"]
        selected_row["role"] = "Madman"
        selected_row["wolf_score"] = "0"
        old_madman_row["role"] = selected_old_role
        if selected_old_role != "Werewolf":
            old_madman_row["wolf_score"] = min(old_madman_row["wolf_score"], "0.49")
        evidence.append({
            "index": index,
            "selected": selected,
            "selected_old_role": selected_old_role,
            "swapped_out": swapped_out,
            "swapped_out_old_role": old_madman_old_role,
            "reason": reason,
        })

    write_csv(output_csv, rows)

    evidence_path = output_csv.with_suffix(".evidence.csv")
    with evidence_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["index", "selected", "selected_old_role", "swapped_out", "swapped_out_old_role", "reason"],
        )
        writer.writeheader()
        writer.writerows(evidence)

    selector_path = output_csv.with_suffix(".selector.csv")
    with selector_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["index", "selected", "swapped_out", "reason"])
        writer.writeheader()
        writer.writerows(selector_rows)

    print(f"{output_csv}: rows={len(rows)} changes={len(evidence)}")
    print(f"{evidence_path}: evidence rows={len(evidence)}")
    print(f"{selector_path}: selector rows={len(selector_rows)}")
    for row in evidence:
        print(
            f"  g{row['index']} {row['selected']} {row['selected_old_role']}->Madman; "
            f"{row['swapped_out']} Madman->{row['selected_old_role']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--split", choices=("public", "private"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-claims", type=int, default=1)
    parser.add_argument("--min-madman-mentions", type=int, default=3)
    parser.add_argument("--mention-window", type=int, default=60)
    parser.add_argument("--allow-weaker-than-anchor", action="store_true")
    args = parser.parse_args()

    apply(
        input_csv=args.input_csv,
        output_csv=args.output,
        split=args.split,
        min_claims=args.min_claims,
        min_madman_mentions=args.min_madman_mentions,
        mention_window=args.mention_window,
        require_mention_beats_anchor=not args.allow_weaker_than_anchor,
    )


if __name__ == "__main__":
    main()
