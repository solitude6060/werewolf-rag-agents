from typing import Optional
from src.data.schema import (
    Role,
    FetchingResult,
    PlayerAnalysis,
    AnalysisResult,
    GameConstraints,
)
from src.rag.retriever import get_retriever
import ollama
from collections import defaultdict


ROLE_INDICATORS = {
    Role.VILLAGER: ["normal", "dramatic", "no special", "everyone"],
    Role.WEREWOLF: ["defensive", "accuse others", "redirect", "protect"],
    Role.SEER: ["divine", "seer", "white", "black", "check"],
    Role.MEDIUM: ["medium", "dead", "executed", "soul"],
    Role.MADMAN: ["village", "team", "not wolf"],
    Role.HUNTER: ["protect", "guard", "save", "shield"],
}


def analyze_with_llm(
    character: str,
    statements: list[str],
    game_context: str,
) -> float:
    """Use LLM to analyze if a player is likely a werewolf."""
    if not statements:
        return 0.5

    combined_text = "\n".join(statements[:5])

    prompt = f"""You are analyzing a Werewolf game transcript.

Player: {character}
Statements (up to 5 most recent):
{combined_text[:500]}...

Based on how this player speaks, rate how likely they are a WEREWOLF (1.0 = definitely wolf, 0.0 = definitely not wolf).

Look for:
- Deceptive or evasive language
- Defensive behavior
- Inconsistent statements
- Protecting other players subtly
- Using vague language to avoid being pinned down

Respond ONLY with a number between 0.0 and 1.0 representing wolf probability."""

    try:
        import requests
        response = requests.post('http://localhost:11434/api/chat', json={
            'model': 'qwen3.5:9b',
            'messages': [{'role': 'user', 'content': prompt}],
            'stream': False,
            'think': False,
            'options': {'temperature': 0.3, 'num_predict': 15}
        }, timeout=30)
        result = response.json()['message']['content'].strip()

        # Extract number from response
        for c in result:
            if c.isdigit() or c == '.':
                try:
                    score = float(c + ''.join(filter(lambda x: x.isdigit() or x == '.', result[result.index(c):result.index(c)+4])))
                    return min(1.0, max(0.0, score))
                except:
                    pass
        return 0.5
    except Exception as e:
        return 0.5


def compute_role_scores(
    player_name: str,
    statements: list[str],
    votes: list[dict],
    claims: list[dict],
) -> dict[str, float]:
    scores = {r.value: 0.0 for r in Role}

    if not statements:
        return scores

    combined_text = " ".join(statements).lower()

    for role, keywords in ROLE_INDICATORS.items():
        for kw in keywords:
            if kw in combined_text:
                scores[role.value] += 0.15

    for claim in claims:
        if claim.get("claimed_role") == role.value:
            scores[role.value] += 0.5

    total = sum(scores.values())
    if total > 0:
        for r in scores:
            scores[r] = scores[r] / total

    return scores


def compute_wolf_score(
    player_name: str,
    role_scores: dict[str, float],
    votes: list[dict],
    is_accused: bool,
    is_defensive: bool,
) -> float:
    base_wolf = 1 - role_scores.get(Role.VILLAGER.value, 0.0)

    if is_defensive:
        base_wolf += 0.2

    if is_accused:
        base_wolf += 0.1

    wolf_keywords = ["defensive", "accuse", "redirect", "protect wolf"]
    if any(kw in player_name.lower() for kw in wolf_keywords):
        base_wolf += 0.1

    return min(1.0, max(0.0, base_wolf))


def analyze_player(
    player_id: int,
    player_name: str,
    statements: list[str],
    votes: list[dict],
    claims: list[dict],
    is_accused: bool = False,
    is_defensive: bool = False,
) -> PlayerAnalysis:
    role_scores = compute_role_scores(player_name, statements, votes, claims)

    wolf_score = compute_wolf_score(
        player_name,
        role_scores,
        votes,
        is_accused,
        is_defensive,
    )

    key_evidence = []
    if len(statements) < 3:
        key_evidence.append("Low statement count")
    if is_defensive:
        key_evidence.append("Defensive behavior detected")
    if is_accused:
        key_evidence.append("Was accused by other players")

    deception_indicators = []
    if is_defensive and is_accused:
        deception_indicators.append("Defensive when accused - possible wolf")

    return PlayerAnalysis(
        player_id=player_id,
        character=player_name,
        role_candidates=role_scores,
        wolf_score=wolf_score,
        key_evidence=key_evidence,
        deception_indicators=deception_indicators,
        reasoning=f"Analyzed based on {len(statements)} statements and {len(votes)} votes",
    )


def run_analysis_agent(
    game_id: str,
    players: list[dict],
    fetching_result: FetchingResult,
) -> AnalysisResult:
    player_analyses = []

    statements_by_player = {}
    for stmt in fetching_result.statements:
        char = stmt.character
        if char not in statements_by_player:
            statements_by_player[char] = []
        statements_by_player[char].append(stmt.content)

    deaths_by_player = {}
    for death in fetching_result.deaths:
        char = death.character
        if char not in deaths_by_player:
            deaths_by_player[char] = 0
        deaths_by_player[char] += 1

    votes_received = {}
    for vote in fetching_result.votes:
        target = vote.target_character
        if target:
            votes_received[target] = votes_received.get(target, 0) + 1

    votes_cast = {}
    for vote in fetching_result.votes:
        voter = vote.voter_character
        votes_cast[voter] = votes_cast.get(voter, 0) + 1

    all_chars = set(statements_by_player.keys()) | set(deaths_by_player.keys())
    total_statements = sum(len(s) for s in statements_by_player.values())
    avg_statements = total_statements / max(1, len(all_chars))

    llm_analyzed_games: dict[str, int] = defaultdict(int)

    player_count = len(players)
    for player in players:
        player_id = player.get("id", 0)
        character = player.get("character", "")

        player_statements = statements_by_player.get(character, [])
        statement_count = len(player_statements)

        died = deaths_by_player.get(character, 0)
        votes_against = votes_received.get(character, 0)
        votes_made = votes_cast.get(character, 0)

        heuristic_score = 0.35

        if died > 0:
            heuristic_score += 0.15

        if statement_count > avg_statements * 1.5:
            heuristic_score += 0.1
        elif statement_count < 5:
            heuristic_score += 0.15
        elif statement_count > 80:
            heuristic_score -= 0.1

        if votes_against >= 2:
            heuristic_score += 0.1 * min(votes_against, 5)

        heuristic_score = min(1.0, max(0.0, heuristic_score))

        # Use LLM for top 3 suspicious players per game
        if game_id not in llm_analyzed_games:
            llm_analyzed_games[game_id] = 0

        llm_score = None
        if statement_count > 0 and (votes_against >= 2 or died > 0 or heuristic_score > 0.4):
            llm_score = analyze_with_llm(character, player_statements, "")
            llm_analyzed_games[game_id] += 1

        if llm_score is not None:
            wolf_score = heuristic_score * 0.6 + llm_score * 0.4
        else:
            wolf_score = heuristic_score

        analysis = PlayerAnalysis(
            player_id=player_id,
            character=character,
            role_candidates={},
            wolf_score=wolf_score,
            key_evidence=[f"Stmts: {statement_count}, Died: {died}, Votes: {votes_against}"],
            deception_indicators=[],
            reasoning=f"Based on {statement_count} statements, died={died}",
        )

        player_analyses.append(analysis)

    all_wolf_scores = [a.wolf_score for a in player_analyses]
    overall_wolf_odds = sum(all_wolf_scores) / len(all_wolf_scores) if all_wolf_scores else 0.5

    suspicious = sorted(
        [a.player_id for a in player_analyses],
        key=lambda pid: next((a.wolf_score for a in player_analyses if a.player_id == pid), 0.5),
        reverse=True,
    )

    return AnalysisResult(
        game_id=game_id,
        player_count=player_count,
        day_count=fetching_result.day_count,
        player_analyses=player_analyses,
        overall_wolf_odds=overall_wolf_odds,
        suspicious_players=suspicious,
    )