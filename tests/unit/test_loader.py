from pathlib import Path
from src.data.loader import normalize_character_name, parse_roles_csv, get_data_root
from tests.dataset_mark import requires_dataset


def test_normalize_character_name_short():
    assert normalize_character_name("Gerd") == "Optimist Gerd"
    assert normalize_character_name("Peter") == "Boy Peter"
    assert normalize_character_name("Nicholas") == "Traveler Nicholas"


def test_normalize_character_name_full():
    assert normalize_character_name("Optimist Gerd") == "Optimist Gerd"
    assert normalize_character_name("Boy Peter") == "Boy Peter"


def test_normalize_character_name_mixed_case():
    assert normalize_character_name("GERD") == "Optimist Gerd"
    assert normalize_character_name("KATHARINA") == "Shepherd Katharina"


@requires_dataset
def test_get_data_root():
    root = get_data_root()
    assert root.exists()
    assert (root / "public").exists()
    assert (root / "private").exists()
    assert (root / "Dataset_README.md").exists()


@requires_dataset
def test_parse_roles_csv_structure():
    root = get_data_root()
    public_roles = root / "public" / "roles.csv"
    assert public_roles.exists()

    players = parse_roles_csv(public_roles, has_ground_truth=False)
    assert len(players) > 0
    assert players[0].id is not None
    assert players[0].index is not None
    assert players[0].character is not None


@requires_dataset
def test_parse_roles_with_gt():
    root = get_data_root()
    gt_path = root / "public" / "roles_with_gt.csv"
    assert gt_path.exists()

    players = parse_roles_csv(gt_path, has_ground_truth=True)
    assert len(players) > 0
    for p in players:
        if p.role is not None:
            assert p.wolf_score is not None