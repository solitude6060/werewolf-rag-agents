from typing import Optional
import pandas as pd
from sklearn.metrics import f1_score, average_precision_score


def compute_macro_f1(predictions: list[dict], ground_truth: list[dict]) -> float:
    pred_roles = [p["role"] for p in predictions]
    gt_roles = [g["role"] for g in ground_truth]

    return f1_score(gt_roles, pred_roles, average="macro")


def compute_ap(predictions: list[dict], ground_truth: list[dict]) -> float:
    pred_scores = [p.get("wolf_score", 0.0) for p in predictions]
    gt_labels = [g.get("wolf_score", 0.0) for g in ground_truth]

    gt_binary = [1 if s >= 0.5 else 0 for s in gt_labels]

    return average_precision_score(gt_binary, pred_scores)


def evaluate_predictions(submission_path: str, gt_path: str) -> dict:
    submission = pd.read_csv(submission_path)
    gt = pd.read_csv(gt_path)

    merged = submission.merge(gt, on=["id", "index", "character"], suffixes=("_pred", "_gt"))

    predictions = merged[["role_pred", "wolf_score_pred"]].rename(
        columns={"role_pred": "role", "wolf_score_pred": "wolf_score"}
    ).to_dict("records")

    ground_truth = merged[["role_gt", "wolf_score_gt"]].rename(
        columns={"role_gt": "role", "wolf_score_gt": "wolf_score"}
    ).to_dict("records")

    macro_f1 = compute_macro_f1(predictions, ground_truth)
    ap = compute_ap(predictions, ground_truth)

    return {
        "macro_f1": macro_f1,
        "ap": ap,
        "samples": len(merged),
    }


def compute_baseline_metrics(data_dir: str) -> dict:
    from src.data.loader import get_data_root, load_public_games

    root = get_data_root() if data_dir is None else data_dir
    games = load_public_games(root)

    all_predictions = []
    all_ground_truth = []

    for game_id, game in games.items():
        for player in game.players:
            if player.role and player.wolf_score is not None:
                all_ground_truth.append({
                    "id": player.id,
                    "index": player.index,
                    "character": player.character,
                    "role": player.role.value if hasattr(player.role, 'value') else player.role,
                    "wolf_score": player.wolf_score,
                })

    baseline_pred = [{"role": "Villager", "wolf_score": 0.0} for _ in all_ground_truth]

    macro_f1 = compute_macro_f1(baseline_pred, all_ground_truth)
    ap = compute_ap(baseline_pred, all_ground_truth)

    return {
        "macro_f1": macro_f1,
        "ap": ap,
        "samples": len(all_ground_truth),
    }


def run_full_evaluation(predictions_csv: str, data_dir: Optional[str] = None) -> dict:
    root = get_data_root() if data_dir is None else data_dir

    from src.pipeline import predict_all_public
    from pathlib import Path

    results = predict_all_public(Path(root))

    all_preds = []
    for sub in results.values():
        all_preds.extend(sub.predictions)

    from src.data.schema import Submission
    full_sub = Submission(predictions=all_preds)

    pred_path = Path(predictions_csv)
    pred_path.write_text(full_sub.to_csv())

    gt_path = root / "public" / "roles_with_gt.csv"

    metrics = evaluate_predictions(str(pred_path), str(gt_path))
    metrics["predictions_saved"] = str(pred_path)

    return metrics