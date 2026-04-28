from src.data.schema import (
    Role,
    DeathCause,
    Statement,
    Vote,
    Death,
    Claim,
    Player,
    GameRecord,
    Prediction,
    Submission,
    GameConstraints,
)


def test_role_enum_values():
    assert Role.VILLAGER == "Villager"
    assert Role.WEREWOLF == "Werewolf"
    assert Role.SEER == "Seer"


def test_player_schema():
    player = Player(id=1, index="01", character="Optimist Gerd")
    assert player.id == 1
    assert player.index == "01"
    assert player.character == "Optimist Gerd"
    assert player.role is None
    assert player.wolf_score is None


def test_player_with_role():
    player = Player(id=1, index="01", character="Optimist Gerd", role=Role.VILLAGER, wolf_score=0.0)
    assert player.role == Role.VILLAGER
    assert player.wolf_score == 0.0


def test_death_cause_enum():
    assert DeathCause.EXECUTION == "execution"
    assert DeathCause.WEREWOLF_ATTACK == "werewolf_attack"
    assert DeathCause.SUDDEN_DEATH == "sudden_death"


def test_statement_schema():
    stmt = Statement(
        player_id=1,
        character="Optimist Gerd",
        timestamp="21:45",
        content="There's no way there is a werewolf here.",
        day_num=1,
        line_start=8,
        line_end=10,
    )
    assert stmt.player_id == 1
    assert stmt.day_num == 1


def test_vote_schema():
    vote = Vote(
        voter_id=1,
        voter_character="Optimist Gerd",
        target_id=2,
        target_character="Boy Peter",
        day_num=1,
        vote_text="Vote for Peter",
    )
    assert vote.voter_id == 1
    assert vote.target_id == 2


def test_death_schema():
    death = Death(
        player_id=5,
        character="Outlaw Dieter",
        cause=DeathCause.WEREWOLF_ATTACK,
        day_num=3,
    )
    assert death.player_id == 5
    assert death.cause == DeathCause.WEREWOLF_ATTACK


def test_claim_schema():
    claim = Claim(
        player_id=14,
        character="Father Jimzon",
        claimed_role=Role.SEER,
        day_num=2,
        target_id=2,
        target_character="Boy Peter",
        claim_text="I divine Boy Peter as werewolf",
    )
    assert claim.player_id == 14
    assert claim.claimed_role == Role.SEER
    assert claim.target_id == 2


def test_prediction_schema():
    pred = Prediction(
        id=1,
        index="01",
        character="Optimist Gerd",
        role=Role.VILLAGER,
        wolf_score=0.0,
    )
    assert pred.id == 1
    assert pred.role == Role.VILLAGER
    assert pred.wolf_score == 0.0


def test_submission_to_csv():
    predictions = [
        Prediction(id=1, index="01", character="Optimist Gerd", role=Role.VILLAGER, wolf_score=0.0),
        Prediction(id=2, index="01", character="Boy Peter", role=Role.WEREWOLF, wolf_score=1.0),
    ]
    submission = Submission(predictions=predictions)
    csv = submission.to_csv()

    lines = csv.split("\n")
    assert lines[0] == "id,index,character,role,wolf_score"
    assert lines[1] == "1,01,Optimist Gerd,Villager,0.0"
    assert lines[2] == "2,01,Boy Peter,Werewolf,1.0"


def test_game_constraints_from_player_count_small():
    constraints = GameConstraints.from_player_count(10)
    assert constraints.total_players == 10
    assert constraints.werewolf_count == 2
    assert constraints.has_seer is True
    assert constraints.has_medium is True
    assert constraints.has_hunter is False
    assert constraints.has_madman is False


def test_game_constraints_from_player_count_large():
    constraints = GameConstraints.from_player_count(15)
    assert constraints.total_players == 15
    assert constraints.werewolf_count == 3
    assert constraints.has_seer is True
    assert constraints.has_medium is True
    assert constraints.has_hunter is True
    assert constraints.has_madman is True


def test_game_record_schema():
    players = [
        Player(id=1, index="01", character="Optimist Gerd"),
        Player(id=2, index="01", character="Boy Peter"),
    ]
    game = GameRecord(
        game_id="game_01",
        index="01",
        players=players,
        day_count=3,
        raw_text="Game text here",
    )
    assert game.game_id == "game_01"
    assert len(game.players) == 2
    assert game.day_count == 3