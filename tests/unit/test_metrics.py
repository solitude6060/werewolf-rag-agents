from src.utils.metrics import (
    compute_macro_f1,
    compute_ap,
    compute_baseline_metrics,
)


def test_compute_macro_f1_same():
    predictions = [
        {"role": "Villager", "wolf_score": 0.0},
        {"role": "Werewolf", "wolf_score": 1.0},
    ]
    ground_truth = [
        {"role": "Villager", "wolf_score": 0.0},
        {"role": "Werewolf", "wolf_score": 1.0},
    ]
    f1 = compute_macro_f1(predictions, ground_truth)
    assert f1 == 1.0


def test_compute_macro_f1_all_wrong():
    predictions = [
        {"role": "Werewolf", "wolf_score": 1.0},
        {"role": "Villager", "wolf_score": 0.0},
    ]
    ground_truth = [
        {"role": "Villager", "wolf_score": 0.0},
        {"role": "Werewolf", "wolf_score": 1.0},
    ]
    f1 = compute_macro_f1(predictions, ground_truth)
    assert f1 == 0.0


def test_compute_ap_perfect():
    predictions = [
        {"role": "Villager", "wolf_score": 0.0},
        {"role": "Werewolf", "wolf_score": 1.0},
    ]
    ground_truth = [
        {"role": "Villager", "wolf_score": 0.0},
        {"role": "Werewolf", "wolf_score": 1.0},
    ]
    ap = compute_ap(predictions, ground_truth)
    assert ap == 1.0


def test_compute_ap_all_wrong():
    predictions = [
        {"role": "Werewolf", "wolf_score": 0.0},
        {"role": "Villager", "wolf_score": 0.0},
    ]
    ground_truth = [
        {"role": "Villager", "wolf_score": 0.0},
        {"role": "Werewolf", "wolf_score": 1.0},
    ]
    ap = compute_ap(predictions, ground_truth)
    assert ap < 1.0


def test_compute_baseline_metrics():
    metrics = compute_baseline_metrics(None)
    assert "macro_f1" in metrics
    assert "ap" in metrics
    assert "samples" in metrics
    assert metrics["samples"] > 0