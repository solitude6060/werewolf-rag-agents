"""Pytest helpers for tests that require the non-public course dataset."""
from __future__ import annotations

import pytest

from src.data.loader import get_data_root

DATASET_ROOT = get_data_root()
DATASET_AVAILABLE = (
    DATASET_ROOT.exists()
    and (DATASET_ROOT / "public" / "roles.csv").exists()
    and (DATASET_ROOT / "public" / "roles_with_gt.csv").exists()
    and (DATASET_ROOT / "private" / "roles.csv").exists()
)

requires_dataset = pytest.mark.skipif(
    not DATASET_AVAILABLE,
    reason=(
        "course/Kaggle dataset is not checked into this repository; "
        "see DATASETS.md for the expected local layout"
    ),
)
