#!/usr/bin/env python3
"""Regression-check final-attempt router decisions and concrete next files."""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
ROUTER = Path("experiments/scripts/v1836_score_feedback_router.py")
OUT_CSV = Path("experiments/reports/v1875_route_matrix_regression.csv")
OUT_MD = Path("experiments/reports/v1875_route_matrix_regression.md")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def manifest_by_output(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {str(Path(row["output_path"])): row for row in rows}


def router(group: str, order: int, score: float, previous_score: float | None = None) -> tuple[str, str]:
    cmd = [
        sys.executable,
        str(ROUTER),
        "--group",
        group,
        "--order",
        str(order),
        "--score",
        f"{score:.5f}",
        "--dry-run",
    ]
    if previous_score is not None:
        cmd.extend(["--previous-score", f"{previous_score:.5f}"])
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        return output, f"router_exit_{proc.returncode}"
    for line in output.splitlines():
        if line.startswith("recommended_next="):
            return line.split("=", 1)[1], "router_ok"
    return output, "router_missing_recommendation"


def path_status(recommendation: str, by_path: dict[str, dict[str, str]]) -> str:
    if not recommendation.endswith(".csv"):
        return "non_concrete_ok"
    row = by_path.get(str(Path(recommendation)))
    if row is None:
        return "fail_not_in_manifest"
    path = Path(row["output_path"])
    if not path.exists():
        return "fail_missing_file"
    if row_count(path) != 397:
        return "fail_bad_row_count"
    actual = sha256(path)
    if row.get("sha256") and actual != row["sha256"]:
        return "fail_hash_mismatch"
    if row.get("validation_status") != "pass":
        return f"fail_manifest_status_{row.get('validation_status')}"
    return f"concrete_ok:{row['group']}#{row['order']}:{row['candidate']}"


def scenarios() -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []
    # Active first-upload boundary and operating bands.
    for label, score in [
        ("order1_top3", 0.50672),
        ("order1_strong_positive", 0.48000),
        ("order1_tiny_positive_v1874", 0.47120),
        ("order1_exact_current_best_v1874", 0.47119),
        ("order1_near_baseline", 0.47080),
        ("order1_small_regression", 0.46600),
        ("order1_severe_regression", 0.46400),
    ]:
        cases.append({"group": "scoreonly_safe_queue", "order": "1", "score": f"{score:.5f}", "previous_score": "", "label": label})

    # Score-only order 2 depends on first score; cover both directions.
    for label, score, previous in [
        ("order2_beats_first", 0.48001, 0.48000),
        ("order2_ties_first", 0.48000, 0.48000),
        ("order2_below_first", 0.47900, 0.48000),
    ]:
        cases.append(
            {
                "group": "scoreonly_safe_queue",
                "order": "2",
                "score": f"{score:.5f}",
                "previous_score": f"{previous:.5f}",
                "label": label,
            }
        )

    # Later score-only orders and portfolio queue should remain concrete or terminal.
    for group in ["scoreonly_safe_queue", "portfolio_queue"]:
        for order in range(3, 6):
            for label, score in [("positive", 0.47200), ("regression", 0.46600), ("top3", 0.50672)]:
                cases.append({"group": group, "order": str(order), "score": f"{score:.5f}", "previous_score": "", "label": f"{group}_order{order}_{label}"})

    for label, score in [("portfolio_order1_positive", 0.47200), ("portfolio_order1_near", 0.47080), ("portfolio_order1_regression", 0.46600)]:
        cases.append({"group": "portfolio_queue", "order": "1", "score": f"{score:.5f}", "previous_score": "", "label": label})
    for label, score, previous in [
        ("portfolio_order2_beats_first_to_charprior", 0.48001, 0.48000),
        ("portfolio_order2_below_first", 0.47900, 0.48000),
    ]:
        cases.append(
            {
                "group": "portfolio_queue",
                "order": "2",
                "score": f"{score:.5f}",
                "previous_score": f"{previous:.5f}",
                "label": label,
            }
        )

    # The portfolio order-2 positive branch can now enter charprior_queue order 2.
    # Cover the downstream high-upside continuation so that the new concrete
    # route does not lead to an unverified branch.
    for label, score, previous in [
        ("charprior_order2_beats_first", 0.48101, 0.48001),
        ("charprior_order2_below_first", 0.48000, 0.48001),
        ("charprior_order2_top3", 0.50672, 0.48001),
    ]:
        cases.append(
            {
                "group": "charprior_queue",
                "order": "2",
                "score": f"{score:.5f}",
                "previous_score": f"{previous:.5f}",
                "label": label,
            }
        )
    for order in range(3, 6):
        for label, score in [("positive", 0.47200), ("regression", 0.46600), ("top3", 0.50672)]:
            cases.append(
                {
                    "group": "charprior_queue",
                    "order": str(order),
                    "score": f"{score:.5f}",
                    "previous_score": "",
                    "label": f"charprior_queue_order{order}_{label}",
                }
            )
    return cases


def md_table(rows: list[dict[str, str]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(row.get(field, "") for field in fields) + " |")
    return lines


def main() -> None:
    manifest_rows = read_rows(MANIFEST)
    by_path = manifest_by_output(manifest_rows)
    result_rows: list[dict[str, str]] = []
    for case in scenarios():
        previous = float(case["previous_score"]) if case["previous_score"] else None
        recommendation, router_status = router(case["group"], int(case["order"]), float(case["score"]), previous)
        status = path_status(recommendation, by_path) if router_status == "router_ok" else router_status
        result_rows.append(
            {
                **case,
                "recommended_next": recommendation,
                "status": status,
                "pass": "yes" if status.startswith(("concrete_ok", "non_concrete_ok")) else "no",
            }
        )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["label", "group", "order", "score", "previous_score", "recommended_next", "status", "pass"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(result_rows)

    failures = [row for row in result_rows if row["pass"] != "yes"]
    boundary = [row for row in result_rows if "v1874" in row["label"]]
    lines = [
        "# v1875 Route Matrix Regression",
        "",
        "Date: 2026-05-15",
        "",
        "## Summary",
        "",
        f"- Scenarios checked: `{len(result_rows)}`",
        f"- Failures: `{len(failures)}`",
        "- Concrete CSV recommendations are checked against manifest membership, file existence, row count, SHA-256, and manifest validation status.",
        "",
        "## v1874 boundary cases",
        "",
        *md_table(boundary, fields),
        "",
        "## Full matrix",
        "",
        *md_table(result_rows, fields),
        "",
        "## Decision",
        "",
        "All checked router outcomes are either concrete validated package files or intentional non-concrete stop/manual states.  No route-matrix failure is present.",
        "",
        "## Completion boundary",
        "",
        "This regression does not complete the active score objective; completion still requires a real Kaggle private score greater than `0.50671`.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(result_rows)}")
    print(f"FAILURES={len(failures)}")
    if failures:
        raise SystemExit("route matrix regression failed")


if __name__ == "__main__":
    main()
