#!/usr/bin/env python3
"""v800 — Wolf-AP boost via cross-claim (Seer/Medium) BLACK results.

Hypothesis: If multiple distinct claimants say a player is BLACK, and our anchor
already thinks they are a Werewolf with borderline score (0.3-0.7), we boost
them to 1.0.

Includes Selected Seer and Selected Medium WHITE vetoes.
Stricter selector scores to avoid meta-talkers.
Default threshold is 3 claimants because the original 2-claimant gate regressed
the public proxy.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

DATA = Path("werewolf-project/data/raw/Werewolf_Prediction_Dataset")
FIELDNAMES = ["id", "index", "character", "role", "wolf_score"]

NAME_WORDS = re.compile(r"[A-Za-z]+")
DAY = re.compile(r"=+\s*Day\s+(\d+)\s*=+", re.I)
NUM = re.compile(r"^(\d+)\.$")
TIME = re.compile(r"^\d{2}:\d{2}$")
EXECUTED = re.compile(
    r"\b\[?([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,2})\]?\s+"
    r"was executed by the villagers\.",
    re.I,
)
ATTACKED = re.compile(r"(.{2,45}?)\s+was found in a gruesome state", re.I)

MEDIUM_CLAIM = re.compile(
    r"(?<!not )(?:\bmedium\b.{0,28}(?:claim|co|here|result)|"
    r"(?:claim|co).{0,28}\bmedium\b|\bi\s*(?:am|'m)\s+(?:the\s+)?medium\b|"
    r"\[medium(?:\s+co)?\]|commune with|thoughts of the dead)",
    re.I | re.S,
)
NOT_MEDIUM = re.compile(r"not\s+(?:a\s+)?medium|neither\s+a\s+medium", re.I)

SEER_CLAIM = re.compile(
    r"(?<!not )(?:\bseer\b.{0,28}(?:claim|co|here|coming out)|"
    r"(?:claim|co).{0,28}\bseer\b|\bi\s*(?:am|'m)\s+(?:the\s+)?seer\b|"
    r"\[seer(?:\s+co)?\]|\[\*\*seer claim\*\*\]|crystal ball|"
    r"divin(?:e|ation)|fortune[- ]?tell|oracle)",
    re.I | re.S,
)
NOT_SEER = re.compile(r"not\s+(?:a\s+)?seer|neither\s+a\s+seer", re.I)

@dataclass(frozen=True)
class Utterance:
    no: int
    character: str
    day: int
    start_line: int
    end_line: int
    text: str

@dataclass(frozen=True)
class Death:
    kind: str
    character: str
    day: int
    line_no: int
    text: str

@dataclass(frozen=True)
class VerdictHit:
    role: str  # 'Seer' or 'Medium'
    speaker: str
    target: str
    verdict: str  # 'black' or 'white'
    day: int
    line_no: int
    text: str

def read_roles(split: str) -> list[dict[str, str]]:
    with (DATA / split / "roles.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def read_submission(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def by_game(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    games: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        games[row["index"]].append(row)
    return dict(games)

def base_name(character: str) -> str:
    parts = NAME_WORDS.findall(character)
    return parts[-1] if parts else character

def lookup(players: list[dict[str, str]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in players:
        character = row["character"]
        out[character.lower()] = character
        out[base_name(character).lower()] = character
    return out

def resolve(raw: str, lk: dict[str, str]) -> str | None:
    cleaned = raw.strip().strip("[]* .,!?:;\"'")
    return lk.get(cleaned.lower()) or lk.get(base_name(cleaned).lower())

def parse_utterances(lines: list[str]) -> list[Utterance]:
    utterances: list[Utterance] = []
    day = 0
    i = 0
    while i < len(lines):
        mday = DAY.search(lines[i].strip())
        if mday:
            day = int(mday.group(1))
            i += 1
            continue
        mno = NUM.match(lines[i].strip())
        if not mno or i + 2 >= len(lines):
            i += 1
            continue
        character = lines[i + 1].strip()
        tm = lines[i + 2].strip()
        if not character or not TIME.match(tm):
            i += 1
            continue
        j = i + 3
        body: list[str] = []
        while j < len(lines) and not NUM.match(lines[j].strip()) and not DAY.search(lines[j].strip()):
            body.append(lines[j].rstrip())
            j += 1
        utterances.append(
            Utterance(
                no=int(mno.group(1)),
                character=character,
                day=day,
                start_line=i + 1,
                end_line=j,
                text="\n".join(body).strip(),
            )
        )
        i = j
    return utterances

def parse_deaths(lines: list[str], lk: dict[str, str]) -> list[Death]:
    deaths: list[Death] = []
    day = 0
    for lineno, line in enumerate(lines, start=1):
        mday = DAY.search(line.strip())
        if mday:
            day = int(mday.group(1))
            continue
        for match in EXECUTED.finditer(line):
            character = resolve(match.group(1), lk)
            if character:
                deaths.append(Death("executed", character, day, lineno, line.strip()))
        for match in ATTACKED.finditer(line):
            character = resolve(match.group(1), lk)
            if character:
                deaths.append(Death("attacked", character, day, lineno, line.strip()))
    return deaths

def medium_verdict_patterns(victim: str) -> tuple[re.Pattern[str], re.Pattern[str]]:
    full = re.escape(victim)
    base = re.escape(base_name(victim))
    name = rf"(?:{full}|{base})"
    human = re.compile(rf"\[?\s*{name}\s+(?:is|was)\s+(?:human|white)\b", re.I)
    wolf = re.compile(rf"\[?\s*{name}\s+(?:is|was)\s+(?:a\s+|the\s+)?(?:werewolf|black)\b", re.I)
    return human, wolf

def seer_divination_patterns(target: str) -> tuple[re.Pattern[str], re.Pattern[str]]:
    full = re.escape(target)
    base = re.escape(base_name(target))
    name = rf"\[?\s*(?:{full}|{base})(?:-?(?:san|han|kun|sama))?\b"
    bridge = r"(?:\s+(?:is|was)(?:\s+(?:definitely|really|surely|certainly))?\s+(?:a\s+|the\s+)?|:\s*)"
    white = re.compile(rf"{name}{bridge}(?:human|white)\b", re.I | re.S)
    black = re.compile(rf"{name}{bridge}(?:werewolf|wolf|black)\b", re.I | re.S)
    return white, black

def death_line_before(deaths: list[Death], speaker: str, line_no: int) -> bool:
    return any(death.character == speaker and death.line_no < line_no for death in deaths)

def collect_verdicts(
    split: str,
    index: str,
    players: list[dict[str, str]],
) -> tuple[list[VerdictHit], dict[str, int], dict[str, int], list[Death]]:
    lines = (DATA / split / f"{index}.txt").read_text(encoding="utf-8").splitlines()
    lk = lookup(players)
    deaths = parse_deaths(lines, lk)
    utterances = parse_utterances(lines)

    seer_claims: dict[str, int] = defaultdict(int)
    medium_claims: dict[str, int] = defaultdict(int)
    
    hits: list[VerdictHit] = []
    
    # Track who claimed what
    for utterance in utterances:
        speaker = resolve(utterance.character, lk)
        if not speaker:
            continue
        if SEER_CLAIM.search(utterance.text) and not NOT_SEER.search(utterance.text):
            seer_claims[speaker] += 1
        if MEDIUM_CLAIM.search(utterance.text) and not NOT_MEDIUM.search(utterance.text):
            medium_claims[speaker] += 1

    executed = [death for death in deaths if death.kind == "executed"]
    
    for utterance in utterances:
        speaker = resolve(utterance.character, lk)
        if not speaker:
            continue
        if death_line_before(deaths, speaker, utterance.start_line):
            continue

        # Check Seer verdicts
        for player in players:
            target = player["character"]
            if target == speaker:
                continue
            white_pat, black_pat = seer_divination_patterns(target)
            white = white_pat.search(utterance.text)
            black = black_pat.search(utterance.text)
            if bool(white) != bool(black):
                verdict = "black" if black else "white"
                hits.append(VerdictHit("Seer", speaker, target, verdict, utterance.day, utterance.start_line, (black or white).group(0)))

        # Check Medium verdicts
        for death in executed:
            if death.line_no >= utterance.start_line: # Must be after execution
                continue
            if utterance.start_line > death.line_no + 100: # Limit window for Medium results
                continue
            white_pat, black_pat = medium_verdict_patterns(death.character)
            white = white_pat.search(utterance.text)
            black = black_pat.search(utterance.text)
            if bool(white) != bool(black):
                verdict = "black" if black else "white"
                hits.append(VerdictHit("Medium", speaker, death.character, verdict, utterance.day, utterance.start_line, (black or white).group(0)))

    return hits, dict(seer_claims), dict(medium_claims), deaths

def select_v260_medium(
    hits: list[VerdictHit],
    medium_claims: dict[str, int],
    anchor_roles: dict[str, str],
) -> str | None:
    medium_hits = [h for h in hits if h.role == "Medium"]
    by_speaker: dict[str, list[VerdictHit]] = defaultdict(list)
    for h in medium_hits:
        by_speaker[h.speaker].append(h)
        
    candidates = []
    for speaker, speaker_hits in by_speaker.items():
        is_anchor_medium = anchor_roles.get(speaker) == "Medium"
        verdict_by_victim: dict[str, set[str]] = defaultdict(set)
        for h in speaker_hits:
            verdict_by_victim[h.target].add(h.verdict)
        conflicts = sum(1 for verdicts in verdict_by_victim.values() if len(verdicts) > 1)
        if conflicts:
            continue
        
        # Priority 1: Anchor role. Priority 2: Evidence.
        score = (1 if is_anchor_medium else 0, medium_claims.get(speaker, 0), len(verdict_by_victim))
        if score[0] == 0 and score[1] == 0:
            continue
            
        candidates.append((score, speaker))
        
    if not candidates:
        return None
    candidates.sort(reverse=True)
    if len(candidates) > 1 and candidates[1][0] == candidates[0][0]:
        return None
    return candidates[0][1]

def select_v310_seer(
    hits: list[VerdictHit],
    seer_claims: dict[str, int],
    anchor_roles: dict[str, str],
) -> str | None:
    seer_hits = [h for h in hits if h.role == "Seer"]
    by_speaker: dict[str, list[VerdictHit]] = defaultdict(list)
    for h in seer_hits:
        by_speaker[h.speaker].append(h)
        
    candidates = []
    for speaker, speaker_hits in by_speaker.items():
        is_anchor_seer = anchor_roles.get(speaker) == "Seer"
        verdict_by_target: dict[str, set[str]] = defaultdict(set)
        for h in speaker_hits:
            verdict_by_target[h.target].add(h.verdict)
        conflicts = sum(1 for verdicts in verdict_by_target.values() if len(verdicts) > 1)
        if conflicts:
            continue
        
        # Priority 1: Anchor role. Priority 2: Evidence.
        score = (1 if is_anchor_seer else 0, seer_claims.get(speaker, 0), len(verdict_by_target))
        if score[0] == 0 and score[1] == 0:
            continue
            
        candidates.append((score, speaker))
        
    if not candidates:
        return None
    candidates.sort(reverse=True)
    if len(candidates) > 1 and candidates[1][0] == candidates[0][0]:
        return None
    return candidates[0][1]

def apply_boost(
    input_csv: Path,
    output_csv: Path,
    split: str,
    min_claimants: int,
) -> None:
    rows = read_submission(input_csv)
    role_by_game_char: dict[tuple[str, str], str] = {
        (row["index"], row["character"]): row["role"] for row in rows
    }
    games_roles = by_game(read_roles(split))
    
    evidence = []
    
    for index, players in sorted(games_roles.items()):
        hits, seer_claims, medium_claims, deaths = collect_verdicts(split, index, players)
        anchor_roles = {p["character"]: role_by_game_char.get((index, p["character"]), "") for p in players}
        
        selected_medium = select_v260_medium(hits, medium_claims, anchor_roles)
        selected_seer = select_v310_seer(hits, seer_claims, anchor_roles)
        
        # Group BLACK claimants per target
        black_claimants = defaultdict(set)
        for h in hits:
            if h.verdict == "black":
                has_claim = False
                if h.role == "Seer" and seer_claims.get(h.speaker, 0) > 0:
                    has_claim = True
                if h.role == "Medium" and medium_claims.get(h.speaker, 0) > 0:
                    has_claim = True
                if has_claim:
                    black_claimants[h.target].add(h.speaker)
        
        # Vetoes
        veto_white = set()
        if selected_medium:
            for h in hits:
                if h.speaker == selected_medium and h.role == "Medium" and h.verdict == "white":
                    veto_white.add(h.target)
        if selected_seer:
            for h in hits:
                if h.speaker == selected_seer and h.role == "Seer" and h.verdict == "white":
                    veto_white.add(h.target)

        # Apply to rows
        game_rows = [r for r in rows if r["index"] == index]
        for row in game_rows:
            target = row["character"]
            if row["role"] != "Werewolf":
                continue
            
            ws = float(row["wolf_score"])
            if not (0.3 <= ws <= 0.7):
                continue
                
            claimants = black_claimants.get(target, set())
            if len(claimants) >= min_claimants and target not in veto_white:
                row["wolf_score"] = "1.0"
                evidence.append({
                    "id": row["id"],
                    "index": index,
                    "character": target,
                    "old_score": ws,
                    "claimants": ",".join(sorted(claimants)),
                    "veto_source": (f"M:{selected_medium}" if selected_medium else "") + (f"S:{selected_seer}" if selected_seer else ""),
                    "reason": f"{len(claimants)} black claimants; min_claimants={min_claimants}"
                })

    # Write output
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
        
    # Write evidence
    evidence_path = output_csv.with_suffix(".evidence.csv")
    with evidence_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "index", "character", "old_score", "claimants", "veto_source", "reason"])
        writer.writeheader()
        writer.writerows(evidence)
        
    print(f"Applied {len(evidence)} boosts to {output_csv}")
    for e in evidence:
        print(f"  {e['index']} {e['character']} ({e['old_score']}) boosted by {e['claimants']}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", type=Path, required=True)
    parser.add_argument("--split", choices=("public", "private"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-claimants", type=int, default=3)
    args = parser.parse_args()
    
    apply_boost(args.input_csv, args.output, args.split, args.min_claimants)

if __name__ == "__main__":
    main()
