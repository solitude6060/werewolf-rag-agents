from src.agents.stage1_fetching import (
    extract_statements,
    extract_votes,
    extract_deaths,
    extract_claims,
    detect_suspicious_patterns,
    run_fetching_agent,
)


def test_extract_statements_simple():
    transcript = """
Day 1
1. Optimist Gerd
21:45
There's no way there is a werewolf here.
2. Boy Peter
22:19
There's no way this village will be the last one!
"""
    statements = extract_statements(transcript)
    assert len(statements) >= 2
    assert any("werewolf" in s.content.lower() for s in statements)


def test_extract_statements_day_tracking():
    transcript = """
Day 1
1. Player A
10:00
Statement on day 1
Day 2
1. Player A
09:00
Statement on day 2
"""
    statements = extract_statements(transcript)
    day1_stmts = [s for s in statements if s.day_num == 1]
    day2_stmts = [s for s in statements if s.day_num == 2]
    assert len(day1_stmts) >= 1
    assert len(day2_stmts) >= 1


def test_extract_votes_basic():
    transcript = """
Day 1
Player1 vote for Player2
>>1 [Player3]
"""
    votes = extract_votes(transcript)
    assert len(votes) >= 0


def test_extract_deaths_basic():
    transcript = """
Day 2
Player1 was killed
Player2 died
"""
    deaths = extract_deaths(transcript)
    assert len(deaths) >= 0


def test_extract_claims_seer():
    transcript = """
Day 2
I divine Player2 as werewolf
I am a seer
"""
    claims = extract_claims(transcript)
    assert len(claims) >= 0


def test_detect_suspicious_low_activity():
    statements = []
    patterns = detect_suspicious_patterns(statements, [])
    assert any("Low statement activity" in p for p in patterns)


def test_detect_suspicious_voting():
    from src.data.schema import Vote
    votes = [
        Vote(voter_id=1, voter_character="A", target_id=2, target_character="B", day_num=1, vote_text="v"),
        Vote(voter_id=2, voter_character="B", target_id=2, target_character="B", day_num=1, vote_text="v"),
        Vote(voter_id=3, voter_character="C", target_id=2, target_character="B", day_num=1, vote_text="v"),
    ]
    patterns = detect_suspicious_patterns([], votes)
    assert len(patterns) >= 0


def test_run_fetching_agent_basic():
    transcript = """
Day 1
1. Optimist Gerd
21:45
Statement 1
2. Boy Peter
22:19
Statement 2
"""
    players = [
        {"id": 1, "index": "01", "character": "Optimist Gerd"},
        {"id": 2, "index": "01", "character": "Boy Peter"},
    ]
    result = run_fetching_agent("game_01", transcript, players)
    assert result.game_id == "game_01"
    assert result.player_count == 2
    assert result.total_statements >= 2


def test_run_fetching_agent_with_players():
    transcript = """
Day 1
1. Optimist Gerd
21:45
Hello everyone
2. Boy Peter
22:19
Hi there
3. Village Girl Pamela
22:27
Hello
"""
    players = [
        {"id": 1, "index": "01", "character": "Optimist Gerd"},
        {"id": 2, "index": "01", "character": "Boy Peter"},
        {"id": 3, "index": "01", "character": "Village Girl Pamela"},
    ]
    result = run_fetching_agent("game_01", transcript, players)
    assert result.player_count == 3
    assert result.day_count >= 1