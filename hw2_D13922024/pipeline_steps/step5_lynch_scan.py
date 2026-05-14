#!/usr/bin/env python3
"""v1120 - scan all post-lynch reveal windows and apply score corrections.

The extractor trusts direct role-result text only when it appears shortly after
the same character was executed by the villagers. It changes wolf_score only;
roles remain exactly as the anchor submission predicted.
"""
from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path


DATA = Path("werewolf-project/data/raw/Werewolf_Prediction_Dataset")
DEFAULT_ANCHOR = "experiments/submissions/submission_v851_single_per_game_{split}.csv"
DEFAULT_OUTPUT = "experiments/submissions/submission_v1120_full_lynch_scan_{split}.csv"
FIELDNAMES = ["id", "index", "character", "role", "wolf_score"]
NAME_WORDS = re.compile(r"[A-Za-z]+")
EXECUTED = re.compile(
    r"\b\[?([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})\]?\s+"
    r"was executed by the villagers\b",
    re.I,
)
SPECULATIVE = re.compile(
    r"\b(?:if|would|could|maybe|perhaps|possible|assuming|hypothesis|"
    r"prediction|hope|wish|guess|probably|suppose|suspect|think|thought|"
    r"seems|might|may be|not sure|I wonder)\b",
    re.I,
)
NEGATED = re.compile(r"\b(?:not|isn't|wasn't|ain't|no)\b", re.I)
TRAILING_TITLE = re.compile(
    r"\s+(?:the\s+)?(?:Baker|Librarian|Tailor|Mayor|Farmer|Soldier|Girl|Man|"
    r"Woman|Traveler|Optimist|Sister|Father|Boy|Young|Old|Woodcutter|Shepherd)$",
    re.I,
)


@dataclass(frozen=True)
class ExecutionEvent:
    index: str
    character: str
    execution_line: int
    execution_text: str


@dataclass(frozen=True)
class RevealHit:
    index: str
    character: str
    verdict: str
    confidence: str
    execution_line: int
    execution_text: str
    reveal_line: int
    reveal_text: str
    pattern: str


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def base_name(character: str) -> str:
    parts = NAME_WORDS.findall(character)
    return parts[-1] if parts else character


def normalize_name(raw: str) -> str:
    cleaned = raw.strip().strip("[](){}【】* .,!?:;\"'")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return TRAILING_TITLE.sub("", cleaned).strip()


def build_lookup(roster: list[str]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for character in roster:
        keys = {
            character,
            base_name(character),
            normalize_name(character),
            normalize_name(base_name(character)),
        }
        for key in keys:
            if key:
                lookup.setdefault(key.lower(), character)
    return lookup


def roster_by_game(split: str) -> dict[str, list[str]]:
    rows = read_csv(DATA / split / "roles.csv")
    games: dict[str, list[str]] = {}
    for row in rows:
        games.setdefault(f"{int(row['index']):02d}", []).append(row["character"])
    return games


def resolve_name(raw: str, lookup: dict[str, str]) -> str | None:
    cleaned = normalize_name(raw)
    if not cleaned:
        return None
    return lookup.get(cleaned.lower()) or lookup.get(base_name(cleaned).lower())


def compile_reveal_patterns(character: str) -> list[tuple[str, str, re.Pattern[str]]]:
    full = re.escape(character)
    base = re.escape(base_name(character))
    name = rf"(?:{full}|{base})"
    sep = r"(?:\s+|[^A-Za-z0-9\n]{1,6})"
    return [
        ("bracket_werewolf", "werewolf", re.compile(rf"[\[【][^\]】\n]*{name}[^\]】\n]*\b(?:Werewolf|wolf|black)\b[^\]】\n]*[\]】]", re.I)),
        ("bracket_human", "human", re.compile(rf"[\[【][^\]】\n]*{name}[^\]】\n]*\b(?:human|villager|white)\b[^\]】\n]*[\]】]", re.I)),
        ("direct_werewolf", "werewolf", re.compile(rf"\b{name}{sep}(?:is|was|was found to be|revealed as)\s+(?:a\s+|the\s+)?(?:werewolf|wolf|black)\b", re.I)),
        ("direct_human", "human", re.compile(rf"\b{name}{sep}(?:is|was|was found to be|revealed as)\s+(?:a\s+|the\s+)?(?:human|villager|white)\b", re.I)),
        ("known_human", "human", re.compile(rf"\bAs everyone knows,\s+{name}\s+was\s+(?:a\s+|the\s+)?(?:human|villager|white)\b", re.I)),
        ("known_werewolf", "werewolf", re.compile(rf"\bAs everyone knows,\s+{name}\s+was\s+(?:a\s+|the\s+)?(?:werewolf|wolf|black)\b", re.I)),
    ]


def find_executions(split: str, index: str, lines: list[str], lookup: dict[str, str]) -> list[ExecutionEvent]:
    events: list[ExecutionEvent] = []
    for lineno, line in enumerate(lines, start=1):
        match = EXECUTED.search(line)
        if not match:
            continue
        character = resolve_name(match.group(1), lookup)
        if character:
            events.append(ExecutionEvent(index=index, character=character, execution_line=lineno, execution_text=line.strip()))
    return events


def find_reveal_for_event(event: ExecutionEvent, lines: list[str], window_lines: int) -> RevealHit | None:
    patterns = compile_reveal_patterns(event.character)
    start = event.execution_line
    end = min(len(lines), event.execution_line + window_lines)
    hits: list[RevealHit] = []
    for offset in range(start, end):
        line = lines[offset].strip()
        if not line or SPECULATIVE.search(line):
            continue
        for pattern_name, verdict, pattern in patterns:
            if not pattern.search(line):
                continue
            if verdict == "werewolf" and NEGATED.search(line):
                continue
            if verdict == "human" and "not human" in line.lower():
                continue
            confidence = "bracket" if pattern_name.startswith("bracket") else "anchored_direct"
            hits.append(
                RevealHit(
                    index=event.index,
                    character=event.character,
                    verdict=verdict,
                    confidence=confidence,
                    execution_line=event.execution_line,
                    execution_text=event.execution_text,
                    reveal_line=offset + 1,
                    reveal_text=line,
                    pattern=pattern_name,
                )
            )
    if not hits:
        return None
    verdicts = {hit.verdict for hit in hits}
    if len(verdicts) > 1:
        return None
    return sorted(hits, key=lambda hit: (hit.reveal_line, 0 if hit.confidence == "bracket" else 1))[0]


def collect_hits(split: str, window_lines: int) -> tuple[list[ExecutionEvent], list[RevealHit]]:
    rosters = roster_by_game(split)
    executions: list[ExecutionEvent] = []
    hits: list[RevealHit] = []
    for transcript in sorted((DATA / split).glob("[0-9][0-9].txt")):
        index = transcript.stem
        lookup = build_lookup(rosters[index])
        lines = transcript.read_text(encoding="utf-8").splitlines()
        events = find_executions(split, index, lines, lookup)
        executions.extend(events)
        for event in events:
            hit = find_reveal_for_event(event, lines, window_lines)
            if hit:
                hits.append(hit)
    return executions, hits


def choose_corrections(
    anchor_rows: list[dict[str, str]],
    hits: list[RevealHit],
    human_score: float,
    wolf_score: float,
    protect_human_demote_score: float,
    max_wolf_boosts_per_game: int,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rows = [dict(row) for row in anchor_rows]
    hit_by_key = {(hit.index, hit.character): hit for hit in hits}
    wolf_boosts: dict[str, int] = {}
    evidence: list[dict[str, str]] = []
    for row in rows:
        index = f"{int(row['index']):02d}"
        hit = hit_by_key.get((index, row["character"]))
        if not hit:
            continue
        old = float(row["wolf_score"])
        new = old
        action = "none"
        if hit.verdict == "werewolf" and old < wolf_score:
            if wolf_boosts.get(index, 0) >= max_wolf_boosts_per_game:
                continue
            new = wolf_score
            action = "boost_wolf"
            wolf_boosts[index] = wolf_boosts.get(index, 0) + 1
        elif (
            hit.verdict == "human"
            and old > human_score
            and old < protect_human_demote_score
        ):
            new = human_score
            action = "demote_human"
        if new == old:
            continue
        row["wolf_score"] = f"{new:.6g}"
        evidence.append(
            {
                "id": row["id"],
                "index": row["index"],
                "character": row["character"],
                "role": row["role"],
                "old_score": f"{old:.6g}",
                "new_score": f"{new:.6g}",
                "action": action,
                "verdict": hit.verdict,
                "confidence": hit.confidence,
                "execution_line": str(hit.execution_line),
                "execution_text": hit.execution_text,
                "reveal_line": str(hit.reveal_line),
                "reveal_text": hit.reveal_text,
                "pattern": hit.pattern,
            }
        )
    return rows, evidence


def write_scan_summary(path: Path, executions: list[ExecutionEvent], hits: list[RevealHit], evidence: list[dict[str, str]]) -> None:
    by_game_exec: dict[str, list[ExecutionEvent]] = {}
    by_game_hits: dict[str, list[RevealHit]] = {}
    for event in executions:
        by_game_exec.setdefault(event.index, []).append(event)
    for hit in hits:
        by_game_hits.setdefault(hit.index, []).append(hit)

    lines = [
        "# v1120 Full Lynch Scan Summary",
        "",
        f"- Executions scanned: {len(executions)}",
        f"- Execution-anchored reveal hits: {len(hits)}",
        f"- Candidate row changes: {len(evidence)}",
        "",
        "## Per-Game Executions And Reveals",
        "",
    ]
    for index in sorted(by_game_exec):
        lines.append(f"### Game {index}")
        hit_lookup = {(hit.character, hit.execution_line): hit for hit in by_game_hits.get(index, [])}
        for event in by_game_exec[index]:
            hit = hit_lookup.get((event.character, event.execution_line))
            if hit:
                lines.append(
                    f"- L{event.execution_line} {event.character}: reveal={hit.verdict} "
                    f"at L{hit.reveal_line} via `{hit.pattern}`"
                )
            else:
                lines.append(f"- L{event.execution_line} {event.character}: no high-confidence reveal in window")
        lines.append("")

    lines.extend(["## Changed Rows", ""])
    if not evidence:
        lines.append("- None")
    else:
        for row in evidence:
            lines.append(
                f"- g{int(row['index']):02d} {row['character']}: {row['old_score']} -> {row['new_score']} "
                f"({row['verdict']}, execution L{row['execution_line']}, reveal L{row['reveal_line']})"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    input_csv = Path(args.input_csv.format(split=args.split))
    output_csv = Path(args.output.format(split=args.split))
    anchor_rows = read_csv(input_csv)
    executions, hits = collect_hits(args.split, args.window_lines)
    rows, evidence = choose_corrections(
        anchor_rows=anchor_rows,
        hits=hits,
        human_score=args.human_score,
        wolf_score=args.wolf_score,
        protect_human_demote_score=args.protect_human_demote_score,
        max_wolf_boosts_per_game=args.max_wolf_boosts_per_game,
    )
    write_csv(output_csv, rows, FIELDNAMES)
    write_csv(
        output_csv.with_suffix(".evidence.csv"),
        evidence,
        [
            "id", "index", "character", "role", "old_score", "new_score",
            "action", "verdict", "confidence", "execution_line", "execution_text",
            "reveal_line", "reveal_text", "pattern",
        ],
    )
    summary_path = output_csv.with_suffix(".summary.md")
    write_scan_summary(summary_path, executions, hits, evidence)
    print(f"{output_csv}: {len(rows)} rows, {len(evidence)} changes")
    print(f"{output_csv.with_suffix('.evidence.csv')}: evidence rows={len(evidence)}")
    print(f"{summary_path}: executions={len(executions)}, reveal_hits={len(hits)}")
    for row in evidence:
        print(
            f"  {int(row['index']):02d} {row['character']}: "
            f"{row['old_score']}->{row['new_score']} "
            f"{row['verdict']} L{row['execution_line']}->{row['reveal_line']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("public", "private"), required=True)
    parser.add_argument("--input-csv", default=DEFAULT_ANCHOR)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--window-lines", type=int, default=200)
    parser.add_argument("--human-score", type=float, default=0.05)
    parser.add_argument("--wolf-score", type=float, default=1.0)
    parser.add_argument("--protect-human-demote-score", type=float, default=0.7)
    parser.add_argument("--max-wolf-boosts-per-game", type=int, default=1)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
