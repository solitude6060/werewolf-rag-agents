#!/usr/bin/env python3
"""Audit final-five candidate diversity and redundancy."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
TRANSFER = Path("experiments/reports/v1860_private_transfer_rank_audit.csv")
BASELINE = Path("experiments/final_submission_package/known_best/01_v1824a_score_0p47119_private.csv")
FIRST = Path("experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv")
OUT_CSV = Path("experiments/reports/v1873_final_five_diversity_audit.csv")
OUT_MD = Path("experiments/reports/v1873_final_five_diversity_audit.md")


@dataclass(frozen=True)
class Delta:
    role_changes: int
    role_change_rate: float
    score_mae: float
    score_max_abs: float
    score_change_gt_0p05: int


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def keyed_predictions(path: Path) -> dict[tuple[str, str, str], tuple[str, float]]:
    data: dict[tuple[str, str, str], tuple[str, float]] = {}
    for row in read_rows(path):
        key = (row["id"], row["index"], row["character"])
        data[key] = (row["role"], float(row["wolf_score"]))
    return data


def delta(a_path: Path, b_path: Path) -> Delta:
    a = keyed_predictions(a_path)
    b = keyed_predictions(b_path)
    if set(a) != set(b):
        raise SystemExit(f"key mismatch: {a_path} vs {b_path}")
    n = len(a)
    role_changes = 0
    abs_deltas: list[float] = []
    for key in a:
        a_role, a_score = a[key]
        b_role, b_score = b[key]
        role_changes += int(a_role != b_role)
        abs_deltas.append(abs(a_score - b_score))
    return Delta(
        role_changes=role_changes,
        role_change_rate=role_changes / n,
        score_mae=sum(abs_deltas) / n,
        score_max_abs=max(abs_deltas),
        score_change_gt_0p05=sum(1 for value in abs_deltas if value > 0.05),
    )


def transfer_by_path() -> dict[str, dict[str, str]]:
    rows = read_rows(TRANSFER)
    return {str(Path(row["output_path"])): row for row in rows if row.get("kind") == "future"}


def queue_rows(manifest: list[dict[str, str]], group: str) -> list[dict[str, str]]:
    rows = [row for row in manifest if row["group"] == group]
    return sorted(rows, key=lambda row: int(row["order"]))


def annotate(row: dict[str, str], transfer: dict[str, dict[str, str]]) -> dict[str, str]:
    path = Path(row["output_path"])
    d_base = delta(path, BASELINE)
    d_first = delta(path, FIRST)
    t = transfer.get(str(path), {})
    return {
        "group": row["group"],
        "order": row["order"],
        "candidate": row["candidate"],
        "output_path": str(path),
        "public_score": t.get("public_score", ""),
        "risk_adjusted_index": t.get("risk_adjusted_index", ""),
        "vs_v1824a_role_changes": str(d_base.role_changes),
        "vs_v1824a_role_change_rate": f"{d_base.role_change_rate:.6f}",
        "vs_v1824a_score_mae": f"{d_base.score_mae:.6f}",
        "vs_v1824a_score_max_abs": f"{d_base.score_max_abs:.6f}",
        "vs_v1824a_score_change_gt_0p05": str(d_base.score_change_gt_0p05),
        "vs_first_role_changes": str(d_first.role_changes),
        "vs_first_score_mae": f"{d_first.score_mae:.6f}",
        "vs_first_score_change_gt_0p05": str(d_first.score_change_gt_0p05),
    }


def adjacent_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for prev, cur in zip(rows, rows[1:]):
        d = delta(Path(cur["output_path"]), Path(prev["output_path"]))
        output.append(
            {
                "from": f"{prev['group']}#{prev['order']} {prev['candidate']}",
                "to": f"{cur['group']}#{cur['order']} {cur['candidate']}",
                "role_changes": str(d.role_changes),
                "score_mae": f"{d.score_mae:.6f}",
                "score_change_gt_0p05": str(d.score_change_gt_0p05),
            }
        )
    return output


def md_table(rows: list[dict[str, str]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(row.get(field, "") for field in fields) + " |")
    return lines


def main() -> None:
    manifest = read_rows(MANIFEST)
    transfer = transfer_by_path()
    groups = [
        "scoreonly_safe_queue",
        "portfolio_queue",
        "charprior_queue",
        "balancedprior_queue",
        "attack_queue",
        "black_boost_queue",
    ]
    selected: list[dict[str, str]] = []
    for group in groups:
        selected.extend(queue_rows(manifest, group))

    annotated = [annotate(row, transfer) for row in selected]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = list(annotated[0].keys())
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(annotated)

    safe_queue = [row for row in annotated if row["group"] == "scoreonly_safe_queue"]
    top_risk = sorted(
        [row for row in annotated if row["risk_adjusted_index"]],
        key=lambda row: float(row["risk_adjusted_index"]),
        reverse=True,
    )[:12]
    adjacent = adjacent_rows(queue_rows(manifest, "scoreonly_safe_queue"))

    lines = [
        "# v1873 Final Five Diversity Audit",
        "",
        "Date: 2026-05-15",
        "",
        "## Purpose",
        "",
        "Check whether the active five-attempt queue is redundant and whether an existing candidate should replace a later slot before real submissions.",
        "",
        "## Score-only safe queue metrics",
        "",
        *md_table(
            safe_queue,
            [
                "order",
                "candidate",
                "public_score",
                "risk_adjusted_index",
                "vs_v1824a_role_changes",
                "vs_v1824a_score_mae",
                "vs_first_score_mae",
                "vs_first_score_change_gt_0p05",
            ],
        ),
        "",
        "## Adjacent diversity inside the active safe queue",
        "",
        *md_table(adjacent, ["from", "to", "role_changes", "score_mae", "score_change_gt_0p05"]),
        "",
        "## Top risk-adjusted alternatives among audited final-package queues",
        "",
        *md_table(
            top_risk,
            [
                "group",
                "order",
                "candidate",
                "public_score",
                "risk_adjusted_index",
                "vs_v1824a_role_changes",
                "vs_v1824a_score_mae",
            ],
        ),
        "",
        "## Decision",
        "",
        "- Do not replace the first upload: `v1856g` remains the safest first shot because it has high public proxy while preserving verified-best private roles.",
        "- The most attractive pure upside candidate remains `v1853g`; it is already the safe queue order 2.",
        "- Structural `v1853a` has the same public proxy but adds private role changes; keep it as a router escalation after a positive `v1853g`, not as the initial no-feedback upload.",
        "- The active safe queue is not identical-score redundant: later slots have non-trivial score distance from the first upload while keeping role changes at zero versus v1824a.",
        "- Therefore no router/package change is made before the first real score.",
        "",
        "## Completion boundary",
        "",
        "This audit is local evidence only.  The active score goal still requires a real Kaggle private score greater than `0.50671`.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print("DECISION=no_router_change_before_first_real_score")


if __name__ == "__main__":
    main()
