from pathlib import Path

from tests.dataset_mark import requires_dataset
from src.pipeline import predict_single_game, predict_all_public, predict_game
from src.data.loader import get_data_root


@requires_dataset
def test_predict_single_game():
    submission = predict_single_game("01", is_private=False)
    assert len(submission.predictions) > 0
    for pred in submission.predictions:
        assert pred.index == "01"


@requires_dataset
def test_predict_all_public():
    data_dir = get_data_root()
    results = predict_all_public(data_dir)
    assert len(results) >= 20
    for game_id, sub in results.items():
        assert len(sub.predictions) > 0


@requires_dataset
def test_predict_game_csv_output():
    from src.data.loader import load_public_games

    data_dir = get_data_root()
    games = load_public_games(data_dir)

    game = games["01"]
    submission = predict_game(game)

    csv = submission.to_csv()
    lines = csv.split("\n")
    assert len(lines) > 1
    assert lines[0] == "id,index,character,role,wolf_score"