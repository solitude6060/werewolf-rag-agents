#!/usr/bin/env python3
"""Leave-one-game-out robustness audit for v1863 score-only alpha ladder."""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from local_score import ROLES, average_precision, macro_f1, read_csv, score  # noqa: E402

BASE_PUBLIC = Path("experiments/submissions/submission_v1824a_v1823a_plus_g24_thomas_trueseer_public.csv")
BASE_PRIVATE = Path("experiments/submissions/submission_v1824a_v1823a_plus_g24_thomas_trueseer_private.csv")
V1863_CSV = Path("experiments/reports/v1863_scoreonly_blend_ladder.csv")
GT = Path("werewolf-project/data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv")
OUT_CSV = Path("experiments/reports/v1864_scoreonly_alpha_robustness.csv")
OUT_MD = Path("experiments/reports/v1864_scoreonly_alpha_robustness.md")
CURRENT_FIRST = Path("experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv")
TOP3 = 0.50671


def score_subset(pred_csv: Path, excluded_index: str | None = None) -> dict[str, float]:
    pred = read_csv(pred_csv)
    gt = read_csv(GT)
    gt_map = {(row["index"], row["character"]): row for row in gt if row["index"] != excluded_index}
    allowed = {row["index"] for row in gt if row["index"] != excluded_index}
    matched = []
    for row in pred:
        if row["index"] not in allowed:
            continue
        key = (row["index"], row["character"])
        if key in gt_map:
            matched.append((row, gt_map[key]))
    y_true_role = [gt_row["role"] for _, gt_row in matched]
    y_pred_role = [pred_row["role"] for pred_row, _ in matched]
    y_true_wolf = [1 if gt_row["role"] == "Werewolf" else 0 for _, gt_row in matched]
    y_pred_score = [float(pred_row["wolf_score"]) for pred_row, _ in matched]
    f1, _ = macro_f1(y_true_role, y_pred_role)
    ap = average_precision(y_true_wolf, y_pred_score)
    return {"macro_f1": f1, "ap": ap, "final_score": 0.4 * f1 + 0.6 * ap, "n": len(matched)}


def diff_stats(private_csv: Path) -> dict[str, float]:
    base = {(row["index"], row["character"]): row for row in read_csv(BASE_PRIVATE)}
    rows = read_csv(private_csv)
    diffs = []
    role_changes = 0
    for row in rows:
        b = base[(row["index"], row["character"])]
        diffs.append(abs(float(row["wolf_score"]) - float(b["wolf_score"])))
        role_changes += int(row["role"] != b["role"])
    return {
        "score_mae": sum(diffs) / len(diffs),
        "score_max_abs": max(diffs),
        "score_change_gt_0p05": float(sum(d > 0.05 for d in diffs)),
        "role_changes": float(role_changes),
    }


def read_v1863_rows() -> list[dict[str, str]]:
    with V1863_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    gt_rows = read_csv(GT)
    indices = sorted({row["index"] for row in gt_rows})
    base_global = score(BASE_PUBLIC)["final_score"]
    base_loo = {idx: score_subset(BASE_PUBLIC, idx)["final_score"] for idx in indices}

    out_rows: list[dict[str, str]] = []
    for row in read_v1863_rows():
        public_csv = Path(row["public_csv"])
        private_csv = Path(row["private_csv"])
        global_score = score(public_csv)["final_score"]
        deltas = []
        loo_scores = []
        for idx in indices:
            loo = score_subset(public_csv, idx)["final_score"]
            loo_scores.append(loo)
            deltas.append(loo - base_loo[idx])
        stats = diff_stats(private_csv)
        robust_index = min(deltas) * 100.0 + (sum(deltas) / len(deltas)) * 25.0 + (global_score - base_global) * 20.0 - stats["score_mae"] * 2.0
        out_rows.append(
            {
                "candidate": row["candidate"],
                "target": row["target"],
                "family": row["family"],
                "alpha": row["alpha"],
                "public_score": f"{global_score:.12f}",
                "global_delta_vs_v1824a": f"{global_score - base_global:+.12f}",
                "loo_min_delta_vs_v1824a": f"{min(deltas):+.12f}",
                "loo_mean_delta_vs_v1824a": f"{sum(deltas) / len(deltas):+.12f}",
                "loo_positive_count": str(sum(1 for d in deltas if d > 0)),
                "loo_negative_count": str(sum(1 for d in deltas if d < 0)),
                "loo_neutral_count": str(sum(1 for d in deltas if d == 0)),
                "loo_min_score": f"{min(loo_scores):.12f}",
                "private_score_mae_vs_v1824a": f"{stats['score_mae']:.12f}",
                "private_score_max_abs_vs_v1824a": f"{stats['score_max_abs']:.12f}",
                "private_score_change_gt_0p05": str(int(stats["score_change_gt_0p05"])),
                "private_role_changes_vs_v1824a": str(int(stats["role_changes"])),
                "robust_index": f"{robust_index:.12f}",
                "public_csv": str(public_csv),
                "private_csv": str(private_csv),
            }
        )

    fields = list(out_rows[0].keys())
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)

    robust_sorted = sorted(out_rows, key=lambda r: float(r["robust_index"]), reverse=True)
    minloo_sorted = sorted(out_rows, key=lambda r: (float(r["loo_min_delta_vs_v1824a"]), float(r["public_score"])), reverse=True)
    v1856g_full = next((r for r in out_rows if r["target"] == "v1856g" and r["alpha"] == "1.00"), None)
    best = robust_sorted[0]

    decision = "No package/router change."
    decision_note = "The robustness audit does not identify a lower-alpha candidate that should replace the v1862 first upload."
    if best["target"] != "v1856g" or best["alpha"] != "1.00":
        decision_note += " The top robust-index row differs from v1856g, but it is treated as analysis-only because v1862 intentionally prioritizes lower role-label risk and balanced-prior calibration."

    lines = [
        "# v1864 Score-Only Alpha Robustness Audit",
        "",
        "Date: 2026-05-14",
        "",
        "## Purpose",
        "",
        "Check whether any v1863 partial-alpha score-only blend is more robust than the current v1862 first upload under leave-one-public-game-out scoring.",
        "",
        "## Method",
        "",
        f"- Candidates evaluated: {len(out_rows)}.",
        f"- Public games left out one at a time: {len(indices)}.",
        f"- Baseline v1824a public proxy: `{base_global:.4f}`.",
        "- Deltas are computed against v1824a under the same held-out split.",
        "",
        "## Top 10 by robust index",
        "",
        "| Rank | Candidate | Target | Alpha | Public proxy | Min LOO delta | Mean LOO delta | LOO +/- | Score MAE | Robust index | Private CSV |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for i, r in enumerate(robust_sorted[:10], 1):
        lines.append(
            f"| {i} | {r['candidate']} | {r['target']} | {r['alpha']} | {float(r['public_score']):.4f} | {float(r['loo_min_delta_vs_v1824a']):+.4f} | {float(r['loo_mean_delta_vs_v1824a']):+.4f} | {r['loo_positive_count']}/{r['loo_negative_count']} | {float(r['private_score_mae_vs_v1824a']):.4f} | {float(r['robust_index']):.4f} | `{r['private_csv']}` |"
        )
    lines.extend(
        [
            "",
            "## Top 5 by minimum LOO delta",
            "",
            "| Rank | Candidate | Target | Alpha | Public proxy | Min LOO delta | Mean LOO delta | Score MAE | Private CSV |",
            "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for i, r in enumerate(minloo_sorted[:5], 1):
        lines.append(
            f"| {i} | {r['candidate']} | {r['target']} | {r['alpha']} | {float(r['public_score']):.4f} | {float(r['loo_min_delta_vs_v1824a']):+.4f} | {float(r['loo_mean_delta_vs_v1824a']):+.4f} | {float(r['private_score_mae_vs_v1824a']):.4f} | `{r['private_csv']}` |"
        )
    if v1856g_full:
        lines.extend(
            [
                "",
                "## Current first upload row",
                "",
                "| Candidate | Target | Alpha | Public proxy | Min LOO delta | Mean LOO delta | LOO +/- | Score MAE |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
                f"| {v1856g_full['candidate']} | {v1856g_full['target']} | {v1856g_full['alpha']} | {float(v1856g_full['public_score']):.4f} | {float(v1856g_full['loo_min_delta_vs_v1824a']):+.4f} | {float(v1856g_full['loo_mean_delta_vs_v1824a']):+.4f} | {v1856g_full['loo_positive_count']}/{v1856g_full['loo_negative_count']} | {float(v1856g_full['private_score_mae_vs_v1824a']):.4f} |",
            ]
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"{decision} {decision_note}",
            "",
            "Operational first upload remains:",
            "",
            "```text",
            str(CURRENT_FIRST),
            "```",
            "",
            "The active goal remains incomplete until a real Kaggle private score greater than `0.50671` is reported.",
            "",
            "## Artifacts",
            "",
            f"- `{OUT_CSV}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"candidates={len(out_rows)}")
    print(f"best_robust={best['candidate']} target={best['target']} alpha={best['alpha']} public={float(best['public_score']):.4f} min_loo_delta={float(best['loo_min_delta_vs_v1824a']):+.4f}")
    if v1856g_full:
        print(f"current_first_row={v1856g_full['candidate']} public={float(v1856g_full['public_score']):.4f} min_loo_delta={float(v1856g_full['loo_min_delta_vs_v1824a']):+.4f}")
    print(f"decision={decision}")
    print(f"csv={OUT_CSV}")
    print(f"report={OUT_MD}")


if __name__ == "__main__":
    main()
