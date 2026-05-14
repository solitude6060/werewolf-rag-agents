"""Werewolf prediction data loading."""

import re
from pathlib import Path
from typing import Optional

from .schema import GameRecord, Player, Role

name_map = {
    "Gerd": "Optimist Gerd",
    "Katharina": "Shepherd Katharina",
    "Dieter": "Outlaw Dieter",
    "Simon": "Wounded Soldier Simon",
    "Moritz": "Old Man Moritz",
    "Clara": "Librarian Clara",
    "Elna": "Tailor Elna",
    "Joachim": "Young Man Joachim",
    "Liza": "Young Girl Liza",
    "Nicholas": "Traveler Nicholas",
    "Pamela": "Village Girl Pamela",
    "Regina": "Innkeeper Regina",
    "Albin": "Merchant Albin",
    "Jimzon": "Father Jimzon",
    "Peter": "Boy Peter",
    "Jacob": "Farmer Jacob",
    "Otto": "Baker Otto",
    "Friedel": "Sister Friedel",
    "Valter": "Mayor Valter",
    "Thomas": "Woodcutter Thomas",
}


def normalize_character_name(name: str) -> str:
    base_name = name.strip().split()[0] if name else ""
    base_lower = base_name.lower()
    for key, val in name_map.items():
        if key.lower() == base_lower or key.lower() in base_lower:
            return val
    return name.strip()


def parse_roles_csv(csv_path: Path, has_ground_truth: bool = False) -> list[Player]:
    players = []
    content = csv_path.read_text(encoding="utf-8")
    lines = content.strip().split("\n")

    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) < 4:
            continue

        player_id = int(parts[0].strip())
        game_index = parts[1].strip()
        character = normalize_character_name(parts[2].strip())

        role = None
        wolf_score = None

        if has_ground_truth and len(parts) >= 5:
            role_str = parts[3].strip()
            wolf_str = parts[4].strip()
            if role_str:
                try:
                    role = Role(role_str)
                except ValueError:
                    role = None
            if wolf_str:
                try:
                    wolf_score = float(wolf_str)
                except ValueError:
                    wolf_score = None

        players.append(Player(
            id=player_id,
            index=game_index,
            character=character,
            role=role,
            wolf_score=wolf_score,
        ))

    return players


def load_game_record(
    transcript_path: Path,
    roles: list[Player],
    game_index: str,
) -> GameRecord:
    raw_text = transcript_path.read_text(encoding="utf-8")

    game = GameRecord(
        game_id=f"game_{game_index}",
        index=game_index,
        players=roles,
        raw_text=raw_text,
    )

    day_matches = list(re.finditer(r"Day (\d+)", raw_text))
    game.day_count = len(day_matches) if day_matches else 1

    return game


def load_public_games(data_dir: Path) -> dict[str, GameRecord]:
    public_dir = data_dir / "public"
    roles_path = public_dir / "roles.csv"
    roles_with_gt_path = public_dir / "roles_with_gt.csv"

    all_roles = parse_roles_csv(roles_path, has_ground_truth=False)
    ground_truth = parse_roles_csv(roles_with_gt_path, has_ground_truth=True)

    gt_map = {f"{p.index}_{p.character}": p for p in ground_truth}

    games = {}
    for roles_file in sorted(public_dir.glob("*.txt")):
        index = roles_file.stem
        game_roles = [r for r in all_roles if r.index == index]

        for r in game_roles:
            key = f"{r.index}_{r.character}"
            if key in gt_map:
                r.role = gt_map[key].role
                r.wolf_score = gt_map[key].wolf_score

        transcript_path = public_dir / f"{index}.txt"
        if transcript_path.exists():
            games[index] = load_game_record(transcript_path, game_roles, index)

    return games


def load_private_games(data_dir: Path) -> dict[str, GameRecord]:
    private_dir = data_dir / "private"
    roles_path = private_dir / "roles.csv"

    all_roles = parse_roles_csv(roles_path, has_ground_truth=False)

    games = {}
    for roles_file in sorted(private_dir.glob("*.txt")):
        index = roles_file.stem
        game_roles = [r for r in all_roles if r.index == index]

        transcript_path = private_dir / f"{index}.txt"
        if transcript_path.exists():
            games[index] = load_game_record(transcript_path, game_roles, index)

    return games


def get_data_root() -> Path:
    return Path(__file__).parent.parent.parent / "data" / "raw" / "Werewolf_Prediction_Dataset"
