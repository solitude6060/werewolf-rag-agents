#!/usr/bin/env python3
"""Record a real final-pack Kaggle score and route to the next candidate.

The script reads experiments/final_submission_package/manifests/final_submission_pack_manifest.csv.
It does not upload anything.  Non-dry-run writes require --confirm-real-score.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

BASELINE = 0.47119
TOP3 = 0.50671
MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
RESULTS_CSV = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
RESULTS_MD = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.md")

RESULT_FIELDS = [
    "recorded_at_utc",
    "group",
    "order",
    "candidate",
    "uploaded_path",
    "score",
    "delta_vs_current_best",
    "top3_hit",
    "recommended_next",
]


def read_manifest(path: Path = MANIFEST) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Manifest not found: {path}. Run v1835_final_submission_pack.py first.")
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_results() -> list[dict[str, str]]:
    if not RESULTS_CSV.exists():
        return []
    with RESULTS_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_results(rows: list[dict[str, str]]) -> None:
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# v1836 Score Feedback Records",
        "",
        f"Current best before this router: `{BASELINE:.5f}`.",
        f"Top-3 target: `>{TOP3:.5f}`.",
        "",
        "| Time UTC | Group | Order | Candidate | Score | Delta | Top-3 hit | Recommended next |",
        "| --- | --- | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['recorded_at_utc']} | {row['group']} | {row['order']} | {row['candidate']} | "
            f"{row['score']} | {row['delta_vs_current_best']} | {row['top3_hit']} | `{row['recommended_next']}` |"
        )
    RESULTS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def find_row(
    manifest: list[dict[str, str]], order: int | None, candidate: str | None, group: str
) -> dict[str, str]:
    if order is not None:
        for row in manifest:
            if row["group"] == group and int(row["order"]) == order:
                return row
        raise SystemExit(f"Unknown {group} order: {order}")
    if candidate is not None:
        matches = [row for row in manifest if row["candidate"] == candidate]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise SystemExit(f"Unknown candidate: {candidate}")
        raise SystemExit(f"Candidate is ambiguous: {candidate}")
    raise SystemExit("Pass --order or --candidate.")


def by_candidate(manifest: list[dict[str, str]], candidate: str) -> str:
    for row in manifest:
        if row["candidate"] == candidate:
            return row["output_path"]
    raise SystemExit(f"Candidate not in manifest: {candidate}")


def by_group_order(manifest: list[dict[str, str]], group: str, order: int) -> str:
    for row in manifest:
        if row["group"] == group and int(row["order"]) == order:
            return row["output_path"]
    raise SystemExit(f"Order not in manifest: {group} {order}")


def latest_score_for(results: list[dict[str, str]], candidate: str) -> float | None:
    for row in reversed(results):
        if row["candidate"] == candidate:
            return float(row["score"])
    return None


def route_next(
    manifest: list[dict[str, str]],
    results: list[dict[str, str]],
    row: dict[str, str],
    score: float,
    previous_score: float | None,
) -> str:
    if score > TOP3:
        return "STOP: score exceeds top-3 threshold."

    candidate = row["candidate"]
    group = row["group"]
    order = int(row["order"])

    if group == "overlay":
        # v1838 overlay files are score-only overlays on queue files.  Route
        # them through the equivalent queue stage while preferring later overlay
        # replacements when they exist.
        overlay_order = {
            "v1838a": 1,
            "v1838b": 3,
            "v1838c": 5,
            "v1839a": 1,
            "v1839b": 3,
            "v1839c": 5,
            "v1840a": 1,
            "v1840b": 3,
            "v1840c": 5,
        }
        if candidate in overlay_order:
            order = overlay_order[candidate]
            group = "queue"

    if group == "attack_queue":
        if order == 1:
            if score >= 0.47200:
                return by_group_order(manifest, "attack_queue", 2)
            if score >= 0.47050:
                return by_candidate(manifest, "v1825c")
            if score >= 0.46500:
                return by_candidate(manifest, "v1825a")
            return by_candidate(manifest, "v1827a")
        if order == 2:
            first_score = previous_score if previous_score is not None else latest_score_for(results, "v1841a")
            if first_score is not None and score > first_score:
                return by_group_order(manifest, "attack_queue", 3)
            if first_score is not None and first_score >= BASELINE:
                return by_candidate(manifest, "v1827d")
            return by_group_order(manifest, "attack_queue", 4)
        if order == 3:
            return by_group_order(manifest, "attack_queue", 4)
        if order == 4:
            return by_group_order(manifest, "attack_queue", 5)
        if order == 5:
            return "NO_ATTACK_QUEUE_REMAINING: keep best verified score or choose contingency manually."

    if group == "portfolio_queue":
        if order == 1:
            if score >= 0.47200:
                return by_group_order(manifest, "portfolio_queue", 2)
            if score >= 0.47050:
                return by_group_order(manifest, "portfolio_queue", 3)
            if score >= 0.46500:
                return by_group_order(manifest, "portfolio_queue", 4)
            return by_group_order(manifest, "portfolio_queue", 5)
        if order == 2:
            first_score = previous_score if previous_score is not None else latest_score_for(results, "v1856a")
            if first_score is not None and score > first_score:
                return "PORTFOLIO_POSITIVE: keep best verified score; use remaining slots only for rank-1 chase or manual high-upside review."
            return by_group_order(manifest, "portfolio_queue", 3)
        if order == 3:
            return by_group_order(manifest, "portfolio_queue", 4)
        if order == 4:
            return by_group_order(manifest, "portfolio_queue", 5)
        if order == 5:
            return "NO_PORTFOLIO_QUEUE_REMAINING: keep best verified score or choose contingency manually."

    if group == "scoreonly_safe_queue":
        if order == 1:
            if score > BASELINE:
                return by_group_order(manifest, "scoreonly_safe_queue", 2)
            if score >= 0.47050:
                return by_group_order(manifest, "scoreonly_safe_queue", 3)
            if score >= 0.46500:
                return by_group_order(manifest, "scoreonly_safe_queue", 4)
            return by_group_order(manifest, "scoreonly_safe_queue", 5)
        if order == 2:
            first_score = previous_score if previous_score is not None else latest_score_for(results, "v1856g")
            if first_score is not None and score > first_score:
                return by_group_order(manifest, "portfolio_queue", 2)
            return by_group_order(manifest, "scoreonly_safe_queue", 3)
        if order == 3:
            if score >= BASELINE:
                return by_group_order(manifest, "portfolio_queue", 3)
            return by_group_order(manifest, "scoreonly_safe_queue", 4)
        if order == 4:
            if score >= BASELINE:
                return by_group_order(manifest, "portfolio_queue", 4)
            return by_group_order(manifest, "scoreonly_safe_queue", 5)
        if order == 5:
            return "NO_SCOREONLY_SAFE_QUEUE_REMAINING: keep best verified score or choose contingency manually."

    if group in {"black_boost_queue", "rolecap_queue", "denoise_queue", "lowtail_queue", "charprior_queue", "balancedprior_queue"}:
        ordered_group = group
        if order == 1:
            if score >= 0.47200:
                return by_group_order(manifest, ordered_group, 2)
            if score >= 0.47050:
                return by_candidate(manifest, "v1825c")
            if score >= 0.46500:
                return by_candidate(manifest, "v1825a")
            return by_candidate(manifest, "v1827a")
        if order == 2:
            first_candidate = {
                "black_boost_queue": "v1842a",
                "rolecap_queue": "v1846a",
                "denoise_queue": "v1848a",
                "lowtail_queue": "v1850a",
                "charprior_queue": "v1853a",
                "balancedprior_queue": "v1856a",
            }[group]
            first_score = previous_score if previous_score is not None else latest_score_for(results, first_candidate)
            if first_score is not None and score > first_score:
                return by_group_order(manifest, ordered_group, 3)
            if first_score is not None and first_score >= BASELINE:
                return by_candidate(manifest, "v1827d")
            return by_group_order(manifest, ordered_group, 4)
        if order == 3:
            return by_group_order(manifest, ordered_group, 4)
        if order == 4:
            return by_group_order(manifest, ordered_group, 5)
        if order == 5:
            return f"NO_{ordered_group.upper()}_REMAINING: keep best verified score or choose contingency manually."

    if group != "queue":
        return "MANUAL_REVIEW: contingency/rollback score recorded; compare with remaining attempts."

    if order == 1:
        if score >= 0.47200:
            return by_candidate(manifest, "v1826b")
        if score >= 0.47050:
            return by_candidate(manifest, "v1825c")
        if score >= 0.46500:
            return by_candidate(manifest, "v1825a")
        return by_candidate(manifest, "v1827a")

    if order == 2:
        first_score = previous_score if previous_score is not None else latest_score_for(results, "v1826a")
        if first_score is not None and score > first_score:
            try:
                return by_candidate(manifest, "v1840b")
            except SystemExit:
                pass
            try:
                return by_candidate(manifest, "v1839b")
            except SystemExit:
                pass
            try:
                return by_candidate(manifest, "v1838b")
            except SystemExit:
                return by_candidate(manifest, "v1826d")
        if first_score is not None and first_score >= BASELINE:
            return by_candidate(manifest, "v1827d")
        return by_candidate(manifest, "v1826c")

    if order == 3:
        return by_candidate(manifest, "v1826c")

    if order == 4:
        try:
            return by_candidate(manifest, "v1840c")
        except SystemExit:
            pass
        try:
            return by_candidate(manifest, "v1839c")
        except SystemExit:
            pass
        try:
            return by_candidate(manifest, "v1838c")
        except SystemExit:
            return by_candidate(manifest, "v1829e")

    if order == 5:
        return "NO_QUEUE_REMAINING: keep best verified score or choose maximum-risk contingency manually."

    return f"MANUAL_REVIEW: no rule for queue order {order} candidate {candidate}."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route final-pack Kaggle score feedback to the next candidate.")
    parser.add_argument("--order", type=int, default=None, help="Queue order, e.g. 1 for 01_v1826a.")
    parser.add_argument(
        "--group",
        choices=[
            "queue",
            "attack_queue",
            "black_boost_queue",
            "known_best_overlay",
            "rolecap_queue",
            "denoise_queue",
            "lowtail_queue",
            "charprior_queue",
            "balancedprior_queue",
            "portfolio_queue",
            "scoreonly_safe_queue",
        ],
        default="queue",
        help="Which ordered upload group --order refers to.",
    )
    parser.add_argument("--candidate", default=None, help="Candidate name, e.g. v1826a.")
    parser.add_argument("--score", type=float, required=True, help="Real or dry-run Kaggle private score.")
    parser.add_argument("--previous-score", type=float, default=None, help="Previous queue score if not already recorded.")
    parser.add_argument("--dry-run", action="store_true", help="Print routing result without writing records.")
    parser.add_argument("--confirm-real-score", action="store_true", help="Required for non-dry-run writes.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.dry_run and not args.confirm_real_score:
        raise SystemExit("Refusing to write without --confirm-real-score. Use --dry-run for examples.")

    manifest = read_manifest(args.manifest)
    results = read_results()
    row = find_row(manifest, args.order, args.candidate, args.group)
    recommended_next = route_next(manifest, results, row, args.score, args.previous_score)
    result = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "group": row["group"],
        "order": row["order"],
        "candidate": row["candidate"],
        "uploaded_path": row["output_path"],
        "score": f"{args.score:.5f}",
        "delta_vs_current_best": f"{args.score - BASELINE:+.5f}",
        "top3_hit": "yes" if args.score > TOP3 else "no",
        "recommended_next": recommended_next,
    }

    if not args.dry_run:
        rows = read_results()
        rows.append(result)
        write_results(rows)

    print(f"candidate={result['candidate']}")
    print(f"score={result['score']}")
    print(f"delta_vs_current_best={result['delta_vs_current_best']}")
    print(f"top3_hit={result['top3_hit']}")
    print(f"recommended_next={recommended_next}")
    if not args.dry_run:
        print(f"wrote={RESULTS_CSV}")
        print(f"wrote={RESULTS_MD}")


if __name__ == "__main__":
    main()
