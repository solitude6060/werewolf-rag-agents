from typing import Optional
from src.data.schema import (
    Role,
    AnalysisResult,
    SolverResult,
    GameConstraints,
)


def assign_roles_greedy(
    player_ids: list[int],
    wolf_scores: dict[int, float],
    constraints: GameConstraints,
) -> dict[int, Role]:
    assignments = {}

    sorted_by_wolf = sorted(player_ids, key=lambda pid: wolf_scores.get(pid, 0.0), reverse=True)

    werewolf_count = min(constraints.werewolf_count, len(sorted_by_wolf))
    for i in range(werewolf_count):
        assignments[sorted_by_wolf[i]] = Role.WEREWOLF

    remaining_players = [pid for pid in player_ids if pid not in assignments]

    special_roles = []
    if constraints.has_seer:
        special_roles.append(Role.SEER)
    if constraints.has_medium:
        special_roles.append(Role.MEDIUM)
    if constraints.has_hunter:
        special_roles.append(Role.HUNTER)
    if constraints.has_madman:
        special_roles.append(Role.MADMAN)

    for i, role in enumerate(special_roles):
        if i < len(remaining_players):
            assignments[remaining_players[i]] = role

    remaining = [pid for pid in remaining_players if pid not in assignments]
    for pid in remaining:
        assignments[pid] = Role.VILLAGER

    return assignments


def compute_final_wolf_scores(
    assignments: dict[int, Role],
    original_scores: dict[int, float],
) -> dict[int, float]:
    final_scores = {}

    for pid, role in assignments.items():
        if role == Role.WEREWOLF:
            final_scores[pid] = 1.0
        elif role == Role.MADMAN:
            final_scores[pid] = 0.0
        else:
            base_score = original_scores.get(pid, 0.0)
            final_scores[pid] = min(0.5, base_score * 0.5)

    return final_scores


def verify_constraints(
    assignments: dict[int, Role],
    constraints: GameConstraints,
) -> bool:
    role_counts = {role: 0 for role in Role}
    for role in assignments.values():
        role_counts[role] += 1

    expected_wolves = constraints.werewolf_count
    actual_wolves = role_counts[Role.WEREWOLF]

    if actual_wolves != expected_wolves:
        return False

    if constraints.has_seer and role_counts[Role.SEER] != 1:
        return False
    if constraints.has_medium and role_counts[Role.MEDIUM] != 1:
        return False
    if constraints.has_hunter and role_counts[Role.HUNTER] != 1:
        return False
    if constraints.has_madman and role_counts[Role.MADMAN] != 1:
        return False

    total_special = sum(1 for r in assignments.values() if r != Role.VILLAGER)
    expected_special = constraints.werewolf_count + (
        1 if constraints.has_seer else 0
    ) + (
        1 if constraints.has_medium else 0
    ) + (
        1 if constraints.has_hunter else 0
    ) + (
        1 if constraints.has_madman else 0
    )

    if total_special != expected_special:
        return False

    return True


def run_solver(
    game_id: str,
    player_ids: list[int],
    wolf_scores: dict[int, float],
    constraints: Optional[GameConstraints] = None,
) -> SolverResult:
    if constraints is None:
        constraints = GameConstraints.from_player_count(len(player_ids))

    assignments = assign_roles_greedy(player_ids, wolf_scores, constraints)

    final_scores = compute_final_wolf_scores(assignments, wolf_scores)

    constraints_satisfied = verify_constraints(assignments, constraints)

    confidence = 0.8 if constraints_satisfied else 0.3

    reasoning_parts = []
    if constraints_satisfied:
        reasoning_parts.append("All constraints satisfied")
    else:
        reasoning_parts.append("Some constraints may not be satisfied")

    werewolf_ids = [pid for pid, role in assignments.items() if role == Role.WEREWOLF]
    if werewolf_ids:
        reasoning_parts.append(f"Werewolves assigned: {werewolf_ids}")

    reasoning = ". ".join(reasoning_parts)

    return SolverResult(
        game_id=game_id,
        assignments=assignments,
        wolf_scores=final_scores,
        confidence=confidence,
        constraints_satisfied=constraints_satisfied,
        reasoning=reasoning,
    )