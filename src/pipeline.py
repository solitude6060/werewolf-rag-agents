"""End-to-end prediction pipeline."""

from pathlib import Path
from typing import Optional

from src.data.schema import (
    GameRecord,
    Submission,
    Prediction,
    GameConstraints,
)
from src.data.loader import load_public_games, load_private_games, get_data_root
from src.agents.stage1_fetching import run_fetching_agent
from src.agents.stage2_analysis import run_analysis_agent
from src.agents.stage3_solver import run_solver


def predict_game(
    game: GameRecord,
    use_llm: bool = False,
    model_name: Optional[str] = None,
) -> Submission:
    players_dict = [
        {"id": p.id, "index": p.index, "character": p.character}
        for p in game.players
    ]

    fetching_result = run_fetching_agent(
        game_id=game.game_id,
        transcript=game.raw_text or "",
        players=players_dict,
    )

    analysis_result = run_analysis_agent(
        game_id=game.game_id,
        players=players_dict,
        fetching_result=fetching_result,
    )

    player_ids = [p["id"] for p in players_dict]
    wolf_scores = {a.player_id: a.wolf_score for a in analysis_result.player_analyses}

    constraints = GameConstraints.from_player_count(len(player_ids))

    solver_result = run_solver(
        game_id=game.game_id,
        player_ids=player_ids,
        wolf_scores=wolf_scores,
        constraints=constraints,
    )

    predictions = []
    for player in game.players:
        pid = player.id
        role = solver_result.assignments.get(pid)
        score = solver_result.wolf_scores.get(pid, 0.0)

        if role is None:
            role = "Villager"

        predictions.append(Prediction(
            id=pid,
            index=player.index,
            character=player.character,
            role=role,
            wolf_score=score,
        ))

    return Submission(predictions=predictions)


def predict_all_public(
    data_dir: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> dict[str, Submission]:
    if data_dir is None:
        data_dir = get_data_root()

    games = load_public_games(data_dir)

    results = {}
    for game_id, game in games.items():
        submission = predict_game(game)
        results[game_id] = submission

    if output_path:
        all_predictions = []
        for game_id, sub in results.items():
            all_predictions.extend(sub.predictions)

        full_submission = Submission(predictions=all_predictions)
        output_path.write_text(full_submission.to_csv())

    return results


def predict_single_game(
    game_index: str,
    is_private: bool = False,
    data_dir: Optional[Path] = None,
) -> Submission:
    if data_dir is None:
        data_dir = get_data_root()

    if is_private:
        games = load_private_games(data_dir)
    else:
        games = load_public_games(data_dir)

    if game_index not in games:
        raise ValueError(f"Game {game_index} not found")

    game = games[game_index]
    return predict_game(game)