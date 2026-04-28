from src.agents.stage3_solver import (
    assign_roles_greedy,
    compute_final_wolf_scores,
    verify_constraints,
    run_solver,
)
from src.data.schema import Role, GameConstraints


def test_assign_roles_greedy_small_game():
    player_ids = list(range(1, 11))
    wolf_scores = {i: 0.1 * i for i in range(1, 11)}
    constraints = GameConstraints.from_player_count(10)

    assignments = assign_roles_greedy(player_ids, wolf_scores, constraints)

    assert len(assignments) == 10
    werewolf_count = sum(1 for r in assignments.values() if r == Role.WEREWOLF)
    assert werewolf_count == 2


def test_assign_roles_greedy_large_game():
    player_ids = list(range(1, 16))
    wolf_scores = {i: 0.1 * i for i in range(1, 16)}
    constraints = GameConstraints.from_player_count(15)

    assignments = assign_roles_greedy(player_ids, wolf_scores, constraints)

    assert len(assignments) == 15
    werewolf_count = sum(1 for r in assignments.values() if r == Role.WEREWOLF)
    assert werewolf_count == 3


def test_compute_final_wolf_scores():
    assignments = {
        1: Role.WEREWOLF,
        2: Role.VILLAGER,
        3: Role.SEER,
        4: Role.MADMAN,
    }
    original = {1: 0.9, 2: 0.2, 3: 0.3, 4: 0.5}

    final_scores = compute_final_wolf_scores(assignments, original)

    assert final_scores[1] == 1.0
    assert final_scores[2] == 0.1
    assert final_scores[4] == 0.0


def test_verify_constraints_small_game():
    assignments = {
        1: Role.WEREWOLF,
        2: Role.WEREWOLF,
        3: Role.SEER,
        4: Role.MEDIUM,
        5: Role.VILLAGER,
        6: Role.VILLAGER,
        7: Role.VILLAGER,
        8: Role.VILLAGER,
        9: Role.VILLAGER,
        10: Role.VILLAGER,
    }
    constraints = GameConstraints.from_player_count(10)

    assert verify_constraints(assignments, constraints) is True


def test_verify_constraints_wrong_wolf_count():
    assignments = {
        1: Role.WEREWOLF,
        2: Role.VILLAGER,
    }
    constraints = GameConstraints.from_player_count(10)

    assert verify_constraints(assignments, constraints) is False


def test_run_solver_basic():
    player_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    wolf_scores = {i: 0.1 * i for i in range(1, 11)}

    result = run_solver("game_01", player_ids, wolf_scores)

    assert result.game_id == "game_01"
    assert len(result.assignments) == 10
    assert len(result.wolf_scores) == 10


def test_run_solver_known_players():
    player_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    wolf_scores = {i: 0.5 for i in range(1, 17)}

    result = run_solver("game_02", player_ids, wolf_scores)

    assert result.constraints_satisfied is True
    werewolf_count = sum(1 for r in result.assignments.values() if r == Role.WEREWOLF)
    assert werewolf_count == 3


def test_solver_confidence():
    player_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    wolf_scores = {i: 0.1 * i for i in range(1, 11)}

    result = run_solver("game_03", player_ids, wolf_scores)

    assert 0.0 <= result.confidence <= 1.0