#!/usr/bin/env python3
"""Scan experiments/submissions for high-value private candidates missing from final package."""
from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path

SUBMISSIONS = Path("experiments/submissions")
MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
BASELINE = Path("experiments/final_submission_package/known_best/01_v1824a_score_0p47119_private.csv")
CURRENT_UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
DIVERSITY = Path("experiments/reports/v1873_final_five_diversity_audit.csv")
GT = Path("werewolf-project/data/raw/Werewolf_Prediction_Dataset/public/roles_with_gt.csv")
OUT_CSV = Path("experiments/reports/v1884_candidate_pool_coverage_scan.csv")
OUT_MD = Path("experiments/reports/v1884_candidate_pool_coverage_scan.md")

ROLES = ["Villager", "Werewolf", "Seer", "Medium", "Madman", "Hunter"]
SAFE_ROLE_CHANGE_LIMIT = 0
NEAR_SAFE_ROLE_CHANGE_LIMIT = 4


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def prediction_signature(path: Path) -> str:
    """Hash normalized prediction content, independent of CSV formatting."""
    rows = sorted(
        (
            row["id"],
            row["index"],
            row["character"],
            row["role"],
            format(float(row["wolf_score"]), ".12g"),
        )
        for row in read_rows(path)
    )
    h = hashlib.sha256()
    for row in rows:
        h.update("\x1f".join(row).encode("utf-8"))
        h.update(b"\x1e")
    return h.hexdigest()


def macro_f1(y_true: list[str], y_pred: list[str]) -> float:
    scores: list[float] = []
    for role in ROLES:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == role and p == role)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != role and p == role)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == role and p != role)
        if tp == 0:
            scores.append(0.0)
            continue
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(scores) / len(scores)


def average_precision(y_true: list[int], scores: list[float]) -> float:
    n_pos = sum(y_true)
    if n_pos == 0:
        return 0.0
    pairs = sorted(zip(scores, y_true), key=lambda item: item[0], reverse=True)
    total = 0.0
    tp = 0
    for rank, (_, y) in enumerate(pairs, start=1):
        if y:
            tp += 1
            total += tp / rank
    return total / n_pos


def public_score(path: Path) -> tuple[float, float, float, int, int]:
    pred = read_rows(path)
    gt = read_rows(GT)
    gt_map = {(row["index"], row["character"]): row for row in gt}
    matched: list[tuple[dict[str, str], dict[str, str]]] = []
    for row in pred:
        key = (row.get("index", ""), row.get("character", ""))
        if key in gt_map:
            matched.append((row, gt_map[key]))
    y_true_role = [gt_row["role"] for _, gt_row in matched]
    y_pred_role = [pred_row["role"] for pred_row, _ in matched]
    y_true_wolf = [1 if gt_row["role"] == "Werewolf" else 0 for _, gt_row in matched]
    y_pred_score = [float(pred_row["wolf_score"]) for pred_row, _ in matched]
    f1 = macro_f1(y_true_role, y_pred_role)
    ap = average_precision(y_true_wolf, y_pred_score)
    return 0.4 * f1 + 0.6 * ap, f1, ap, len(matched), len(pred)


def row_map(path: Path) -> dict[tuple[str, str, str], dict[str, str]]:
    return {(row["id"], row["index"], row["character"]): row for row in read_rows(path)}


def distance(path: Path, reference: dict[tuple[str, str, str], dict[str, str]]) -> tuple[int, float, int, int]:
    rows = row_map(path)
    shared = sorted(set(rows) & set(reference))
    if not shared:
        return 999999, 999.0, 999999, 0
    role_changes = sum(1 for key in shared if rows[key]["role"] != reference[key]["role"])
    abs_diffs = [abs(float(rows[key]["wolf_score"]) - float(reference[key]["wolf_score"])) for key in shared]
    score_mae = sum(abs_diffs) / len(abs_diffs)
    score_change_gt_0p05 = sum(1 for value in abs_diffs if value > 0.05)
    return role_changes, score_mae, score_change_gt_0p05, len(shared)


def paired_public(private_path: Path) -> Path | None:
    public = private_path.with_name(private_path.name.replace("_private.csv", "_public.csv"))
    return public if public.exists() else None


def manifest_label(row: dict[str, str]) -> str:
    return f"{row.get('group', '')}#{row.get('order', '')}:{row.get('candidate', '')}"


def preferred_manifest_match(rows: list[dict[str, str]]) -> dict[str, str]:
    """Prefer the upload-facing safe queue when duplicate signatures exist."""
    for group in ("scoreonly_safe_queue", "portfolio_queue", "known_best", "charprior_fallback"):
        for row in rows:
            if row.get("group") == group:
                return row
    return rows[0] if rows else {}


def load_manifest() -> tuple[
    set[str],
    set[str],
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    dict[str, list[dict[str, str]]],
]:
    rows = read_rows(MANIFEST)
    source_paths = {str(Path(row["source_path"])) for row in rows if row.get("source_path")}
    output_paths = {str(Path(row["output_path"])) for row in rows if row.get("output_path")}
    by_source = {str(Path(row["source_path"])): row for row in rows if row.get("source_path")}
    by_output = {str(Path(row["output_path"])): row for row in rows if row.get("output_path")}
    by_signature: dict[str, list[dict[str, str]]] = {}
    seen_signature_rows: set[tuple[str, str]] = set()
    for row in rows:
        for key in ("output_path", "source_path"):
            if not row.get(key):
                continue
            path = Path(row[key])
            if not path.exists():
                continue
            signature = prediction_signature(path)
            row_key = (signature, manifest_label(row))
            if row_key in seen_signature_rows:
                continue
            by_signature.setdefault(signature, []).append(row)
            seen_signature_rows.add(row_key)
    return source_paths, output_paths, by_source, by_output, by_signature


def max_packaged_public_score() -> tuple[float, float]:
    rows = read_rows(DIVERSITY)
    scores = [float(row["public_score"]) for row in rows if row.get("public_score")]
    first = next(
        float(row["public_score"])
        for row in rows
        if row["group"] == "scoreonly_safe_queue" and row["order"] == "1" and row.get("public_score")
    )
    return max(scores), first


def recommendation(row: dict[str, str], max_public: float, active_first_public: float) -> str:
    if row["in_manifest"] == "yes":
        if row["manifest_match_type"] == "prediction_signature":
            return "already_packaged_duplicate"
        return "already_packaged"
    public = float(row["public_score"])
    role_changes = int(row["vs_v1824a_role_changes"])
    if public >= max_public and role_changes <= SAFE_ROLE_CHANGE_LIMIT:
        return "review_scoreonly_miss"
    if public >= max_public and role_changes <= NEAR_SAFE_ROLE_CHANGE_LIMIT:
        return "review_near_safe_miss"
    if public >= active_first_public and role_changes <= SAFE_ROLE_CHANGE_LIMIT:
        return "covered_by_safe_queue_or_duplicate_check"
    if public >= active_first_public and role_changes <= NEAR_SAFE_ROLE_CHANGE_LIMIT:
        return "higher_risk_than_safe_queue"
    return "not_preferred"


def main() -> None:
    manifest_sources, manifest_outputs, manifest_by_source, manifest_by_output, manifest_by_signature = load_manifest()
    max_public, active_first_public = max_packaged_public_score()
    baseline_rows = row_map(BASELINE)
    current_rows = row_map(CURRENT_UPLOAD)
    private_paths = sorted(SUBMISSIONS.glob("*private.csv"))

    rows: list[dict[str, str]] = []
    skipped_no_public = 0
    skipped_bad_score = 0
    for private_path in private_paths:
        public_path = paired_public(private_path)
        if public_path is None:
            skipped_no_public += 1
            continue
        try:
            final, f1, ap, matched, pred_rows = public_score(public_path)
        except Exception:
            skipped_bad_score += 1
            continue
        if matched == 0:
            skipped_bad_score += 1
            continue
        private_row_count = len(read_rows(private_path))
        if private_row_count != 397:
            # Keep only actual private submission-shaped files for upload relevance.
            continue
        baseline_role_changes, baseline_mae, baseline_gt005, shared = distance(private_path, baseline_rows)
        current_role_changes, current_mae, current_gt005, _ = distance(private_path, current_rows)
        path_key = str(private_path)
        signature = prediction_signature(private_path)
        signature_rows = manifest_by_signature.get(signature, [])
        direct_source_row = manifest_by_source.get(path_key)
        direct_output_row = manifest_by_output.get(path_key)
        if direct_source_row:
            manifest_match_type = "source_path"
            manifest_row = direct_source_row
        elif direct_output_row:
            manifest_match_type = "output_path"
            manifest_row = direct_output_row
        elif signature_rows:
            manifest_match_type = "prediction_signature"
            manifest_row = preferred_manifest_match(signature_rows)
        else:
            manifest_match_type = "none"
            manifest_row = {}
        signature_matches = ";".join(manifest_label(row) for row in signature_rows)
        in_manifest = path_key in manifest_sources or path_key in manifest_outputs or bool(signature_rows)
        rows.append(
            {
                "private_path": path_key,
                "public_path": str(public_path),
                "sha256": sha256(private_path),
                "prediction_signature": signature,
                "public_score": f"{final:.12f}",
                "public_f1": f"{f1:.12f}",
                "public_ap": f"{ap:.12f}",
                "public_matched": str(matched),
                "public_rows": str(pred_rows),
                "private_rows": str(private_row_count),
                "in_manifest": "yes" if in_manifest else "no",
                "manifest_match_type": manifest_match_type,
                "manifest_group": manifest_row.get("group", ""),
                "manifest_order": manifest_row.get("order", ""),
                "manifest_candidate": manifest_row.get("candidate", ""),
                "manifest_signature_matches": signature_matches,
                "vs_v1824a_role_changes": str(baseline_role_changes),
                "vs_v1824a_score_mae": f"{baseline_mae:.6f}",
                "vs_v1824a_score_change_gt_0p05": str(baseline_gt005),
                "vs_current_role_changes": str(current_role_changes),
                "vs_current_score_mae": f"{current_mae:.6f}",
                "vs_current_score_change_gt_0p05": str(current_gt005),
                "shared_private_rows": str(shared),
            }
        )

    for row in rows:
        row["recommendation"] = recommendation(row, max_public, active_first_public)

    rows.sort(
        key=lambda row: (
            row["in_manifest"] != "no",
            -float(row["public_score"]),
            int(row["vs_v1824a_role_changes"]),
            float(row["vs_v1824a_score_mae"]),
            row["private_path"],
        )
    )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "recommendation",
        "in_manifest",
        "public_score",
        "public_f1",
        "public_ap",
        "vs_v1824a_role_changes",
        "vs_v1824a_score_mae",
        "vs_v1824a_score_change_gt_0p05",
        "vs_current_role_changes",
        "vs_current_score_mae",
        "vs_current_score_change_gt_0p05",
        "shared_private_rows",
        "private_rows",
        "public_matched",
        "public_rows",
        "manifest_match_type",
        "manifest_group",
        "manifest_order",
        "manifest_candidate",
        "manifest_signature_matches",
        "private_path",
        "public_path",
        "sha256",
        "prediction_signature",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(row["recommendation"] for row in rows)
    unmanifested = [row for row in rows if row["in_manifest"] == "no"]
    review = [row for row in unmanifested if row["recommendation"].startswith("review_")]
    safe_or_duplicate = [row for row in unmanifested if row["recommendation"] == "covered_by_safe_queue_or_duplicate_check"]
    top_unmanifested = unmanifested[:20]
    top_review = review[:20]

    lines = [
        "# v1884 Candidate Pool Coverage Scan",
        "",
        "Date: 2026-05-15",
        "",
        "## Purpose",
        "",
        "Scan private candidates under `experiments/submissions/` for high-public-proxy candidates that are not already represented in the final submission package.",
        "This is a local decision-support audit only; it does not use private labels and does not prove Kaggle performance.",
        "",
        "## Summary",
        "",
        f"- Private files scanned: `{len(private_paths)}`",
        f"- Private/public pairs scored: `{len(rows)}`",
        f"- Skipped without public counterpart: `{skipped_no_public}`",
        f"- Skipped due to scoring errors or no matches: `{skipped_bad_score}`",
        f"- Final-package manifest rows: `{len(manifest_sources)}` source paths",
        f"- Final-package normalized prediction signatures: `{len(manifest_by_signature)}`",
        f"- Max packaged public proxy in v1873 audit: `{max_public:.12f}`",
        f"- Active first-upload public proxy: `{active_first_public:.12f}`",
        "",
        "## Recommendation counts",
        "",
        "| Recommendation | Count |",
        "| --- | ---: |",
    ]
    for key, value in sorted(counts.items()):
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Top unmanifested candidates by public proxy",
            "",
            "| Rank | Recommendation | Public score | Role changes vs v1824a | Score MAE vs v1824a | Private path |",
            "| ---: | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for rank, row in enumerate(top_unmanifested, start=1):
        lines.append(
            f"| {rank} | {row['recommendation']} | {float(row['public_score']):.6f} | "
            f"{row['vs_v1824a_role_changes']} | {row['vs_v1824a_score_mae']} | `{row['private_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Review candidates above packaged max public proxy",
            "",
        ]
    )
    if not top_review:
        lines.append("No unmanifested candidate met the review thresholds of public proxy at or above the packaged maximum with <=4 role changes versus v1824a.")
    else:
        lines.extend(
            [
                "| Rank | Recommendation | Public score | Role changes vs v1824a | Score MAE vs v1824a | Private path |",
                "| ---: | --- | ---: | ---: | ---: | --- |",
            ]
        )
        for rank, row in enumerate(top_review, start=1):
            lines.append(
                f"| {rank} | {row['recommendation']} | {float(row['public_score']):.6f} | "
                f"{row['vs_v1824a_role_changes']} | {row['vs_v1824a_score_mae']} | `{row['private_path']}` |"
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
        ]
    )
    if review:
        lines.append(
            "At least one unmanifested candidate meets the high-public-proxy review threshold.  Do not upload it blindly; inspect its evidence and private-transfer risk before changing the final queue."
        )
    else:
        lines.append(
            "No low-role-change, unmanifested unique prediction beats the packaged maximum public proxy threshold.  Keep the staged first upload unchanged."
        )
    if safe_or_duplicate:
        lines.append(
            f"There are `{len(safe_or_duplicate)}` unmanifested score-only/duplicate-like candidates above the active first-upload public proxy, but below the packaged maximum; they are not better first uploads than the existing safe queue without new evidence."
        )
    lines.extend(
        [
            "",
            "## Completion boundary",
            "",
            "This scan can identify missed local candidates, but it does not complete the active score goal.  Completion still requires a real Kaggle private score greater than `0.50671`.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"PRIVATE_FILES={len(private_paths)}")
    print(f"SCORED_PAIRS={len(rows)}")
    print(f"REVIEW_CANDIDATES={len(review)}")
    print(f"SAFE_OR_DUPLICATE_ABOVE_FIRST={len(safe_or_duplicate)}")


if __name__ == "__main__":
    main()
