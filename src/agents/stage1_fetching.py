import re
from typing import Optional

from src.data.schema import (
    Statement,
    Vote,
    Death,
    Claim,
    DeathCause,
    Role,
    FetchingResult,
)
from src.rag.retriever import get_retriever


SYSTEM_PROMPT = """You are the Data Fetching Agent for a Werewolf game analysis system.
Your task is to analyze game transcripts and extract structured information.

Extract the following:
1. Player list and their statements
2. Day-by-day events (votes, deaths, speeches)
3. Claims (Seer claims, Medium claims, etc.)
4. Suspicious patterns (contradictions, defensive behavior)

Return your analysis as a structured summary that will be used by the Analysis Agent."""


def extract_statements(transcript: str) -> list[Statement]:
    statements = []
    lines = transcript.split("\n")

    player_pattern = re.compile(r"^(\d+)\.\s*([A-Za-z\s']+)\s*$")
    time_pattern = re.compile(r"^(\d{2}:\d{2})$")
    day_pattern = re.compile(r"Day (\d+)")

    current_player_id = None
    current_character = None
    current_timestamp = None
    current_day = 1
    line_num = 0

    for i, line in enumerate(lines):
        line_num = i + 1
        line = line.strip()

        if not line:
            continue

        day_match = day_pattern.search(line)
        if day_match:
            current_day = int(day_match.group(1))
            continue

        player_match = player_pattern.match(line)
        if player_match:
            player_num = int(player_match.group(1))
            character = player_match.group(2).strip()
            current_player_id = player_num
            current_character = character
            continue

        time_match = time_pattern.match(line)
        if time_match and current_player_id:
            current_timestamp = time_match.group(1)
            continue

        if current_player_id and current_timestamp and line:
            statements.append(Statement(
                player_id=current_player_id,
                character=current_character,
                timestamp=current_timestamp,
                content=line,
                day_num=current_day,
                line_start=line_num,
            ))

    return statements


def extract_votes(transcript: str) -> list[Vote]:
    votes = []
    vote_patterns = [
        re.compile(r"\[(\w+)\].*?vote.*?\[(\w+)\]", re.IGNORECASE),
        re.compile(r"vote\s+(?:for\s+)?(\w+)", re.IGNORECASE),
        re.compile(r">>\d+.*?\[(\w+)\]", re.IGNORECASE),
    ]

    lines = transcript.split("\n")
    current_day = 1
    day_pattern = re.compile(r"Day (\d+)")

    for line in lines:
        day_match = day_pattern.search(line)
        if day_match:
            current_day = int(day_match.group(1))

        for pattern in vote_patterns:
            matches = pattern.findall(line)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    votes.append(Vote(
                        voter_id=0,
                        voter_character=match[0],
                        target_id=0,
                        target_character=match[1],
                        day_num=current_day,
                        vote_text=line.strip(),
                    ))

    return votes


def extract_deaths(transcript: str) -> list[Death]:
    deaths = []
    death_patterns = [
        re.compile(r"(\w+)\s+(?:was\s+)?(?:killed|attacked|executed|died)", re.IGNORECASE),
        re.compile(r"dead.*?\[(\w+)\]", re.IGNORECASE),
    ]

    lines = transcript.split("\n")
    current_day = 1
    day_pattern = re.compile(r"Day (\d+)")

    for line in lines:
        day_match = day_pattern.search(line)
        if day_match:
            current_day = int(day_match.group(1))

        for pattern in death_patterns:
            matches = pattern.findall(line)
            for match in matches:
                deaths.append(Death(
                    player_id=0,
                    character=match,
                    cause=DeathCause.WEREWOLF_ATTACK if "attack" in line.lower() else DeathCause.EXECUTION,
                    day_num=current_day,
                ))

    return deaths


def extract_claims(transcript: str) -> list[Claim]:
    claims = []
    claim_patterns = [
        re.compile(r"(seer|medium|hunter|madman).*?(?:divine|check|protect).*?(\w+)", re.IGNORECASE),
        re.compile(r"I\s+(?:am\s+)?(?:a\s+)?(seer|medium|hunter|madman)", re.IGNORECASE),
    ]

    lines = transcript.split("\n")
    current_day = 1
    day_pattern = re.compile(r"Day (\d+)")

    for line in lines:
        day_match = day_pattern.search(line)
        if day_match:
            current_day = int(day_match.group(1))

        for pattern in claim_patterns:
            matches = pattern.findall(line)
            for match in matches:
                if isinstance(match, tuple):
                    role_str = match[0] if len(match) > 1 else match
                    target = match[1] if len(match) > 1 else None

                    role_map = {
                        "seer": Role.SEER,
                        "medium": Role.MEDIUM,
                        "hunter": Role.HUNTER,
                        "madman": Role.MADMAN,
                    }
                    role = role_map.get(role_str.lower())

                    if role:
                        claims.append(Claim(
                            player_id=0,
                            character="Unknown",
                            claimed_role=role,
                            day_num=current_day,
                            target_id=0,
                            target_character=target,
                            claim_text=line.strip(),
                        ))

    return claims


def detect_suspicious_patterns(statements: list[Statement], votes: list[Vote]) -> list[str]:
    patterns = []

    if len(statements) < 5:
        patterns.append("Low statement activity - possible silent player")

    vote_targets = [v.target_character for v in votes]
    if len(set(vote_targets)) == 1 and len(vote_targets) > 3:
        patterns.append("Same player voted multiple times - suspicious voting pattern")

    return patterns


def run_fetching_agent(
    game_id: str,
    transcript: str,
    players: list[dict],
) -> FetchingResult:
    statements = extract_statements(transcript)
    votes = extract_votes(transcript)
    deaths = extract_deaths(transcript)
    claims = extract_claims(transcript)
    suspicious = detect_suspicious_patterns(statements, votes)

    day_count = max((s.day_num for s in statements), default=1)

    player_chars = [p.get("character", "") for p in players]

    for vote in votes:
        if vote.voter_character in player_chars:
            for i, p in enumerate(players):
                if p.get("character") == vote.voter_character:
                    vote.voter_id = i + 1
        if vote.target_character in player_chars:
            for i, p in enumerate(players):
                if p.get("character") == vote.target_character:
                    vote.target_id = i + 1

    for death in deaths:
        if death.character in player_chars:
            for i, p in enumerate(players):
                if p.get("character") == death.character:
                    death.player_id = i + 1

    key_events = []
    if len(votes) > 10:
        key_events.append(f"Multiple votes recorded: {len(votes)} votes")
    if len(deaths) > 0:
        key_events.append(f"Deaths recorded: {len(deaths)}")
    if len(claims) > 0:
        key_events.append(f"Role claims found: {len(claims)}")

    return FetchingResult(
        game_id=game_id,
        player_count=len(players),
        day_count=day_count,
        total_statements=len(statements),
        total_votes=len(votes),
        total_deaths=len(deaths),
        total_claims=claims,
        votes=votes,
        deaths=deaths,
        suspicious_patterns=suspicious,
        key_events=key_events,
    )