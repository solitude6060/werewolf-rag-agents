from src.agents.stage2_analysis import (
    compute_role_scores,
    compute_wolf_score,
    analyze_player,
    run_analysis_agent,
)
from src.data.schema import Role, FetchingResult, Vote


def test_compute_role_scores_basic():
    scores = compute_role_scores("Test Player", ["I am normal", "nothing special"], [], [])
    assert isinstance(scores, dict)
    assert Role.VILLAGER.value in scores


def test_compute_role_scores_seer_keywords():
    scores = compute_role_scores(
        "Test Seer",
        ["I divine this player", "he is white", "I am seer"],
        [],
        [],
    )
    assert scores[Role.SEER.value] > 0


def test_compute_wolf_score_basic():
    role_scores = {r.value: 0.1 for r in Role}
    role_scores[Role.VILLAGER.value] = 0.3

    score = compute_wolf_score("Player", role_scores, [], False, False)
    assert 0.0 <= score <= 1.0


def test_compute_wolf_score_defensive():
    role_scores = {r.value: 0.1 for r in Role}
    role_scores[Role.VILLAGER.value] = 0.5

    score = compute_wolf_score("Player", role_scores, [], False, True)
    assert score > 0.5


def test_analyze_player_basic():
    analysis = analyze_player(
        player_id=1,
        player_name="Test Player",
        statements=["Normal statement"],
        votes=[],
        claims=[],
    )
    assert analysis.player_id == 1
    assert analysis.character == "Test Player"
    assert 0.0 <= analysis.wolf_score <= 1.0


def test_analyze_player_accused():
    analysis = analyze_player(
        player_id=1,
        player_name="Test Player",
        statements=["Why are you accusing me?"],
        votes=[],
        claims=[],
        is_accused=True,
        is_defensive=True,
    )
    assert len(analysis.deception_indicators) > 0


def test_run_analysis_agent_empty():
    players = [
        {"id": 1, "index": "01", "character": "Player1"},
        {"id": 2, "index": "01", "character": "Player2"},
    ]

    fetching = FetchingResult(
        game_id="game_01",
        player_count=2,
        day_count=1,
        total_statements=0,
        total_votes=0,
        total_deaths=0,
        total_claims=[],
        votes=[],
        deaths=[],
    )

    result = run_analysis_agent("game_01", players, fetching)
    assert result.game_id == "game_01"
    assert result.player_count == 2
    assert len(result.player_analyses) == 2


def test_run_analysis_agent_with_votes():
    players = [
        {"id": 1, "index": "01", "character": "Player1"},
        {"id": 2, "index": "01", "character": "Player2"},
    ]

    votes = [
        Vote(voter_id=1, voter_character="Player1", target_id=2, target_character="Player2", day_num=1, vote_text="vote"),
    ]

    fetching = FetchingResult(
        game_id="game_01",
        player_count=2,
        day_count=1,
        total_statements=0,
        total_votes=1,
        total_deaths=0,
        total_claims=[],
        votes=votes,
        deaths=[],
    )

    result = run_analysis_agent("game_01", players, fetching)
    assert result.player_count == 2
    assert len(result.suspicious_players) > 0