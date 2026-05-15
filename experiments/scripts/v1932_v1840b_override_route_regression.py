#!/usr/bin/env python3
"""Regression-check the post-score route after the v1840b override upload."""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

ROUTER = Path("experiments/scripts/v1836_score_feedback_router.py")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
OUT_CSV = Path("experiments/reports/v1932_v1840b_override_route_regression.csv")
OUT_MD = Path("experiments/reports/v1932_v1840b_override_route_regression.md")

V1840C = "experiments/final_submission_package/overlay/09_v1840c_v1829e_high_precision_medium_ap_overlay_private.csv"
V1826C = "experiments/final_submission_package/queue/04_v1826c_alt_structural_private.csv"
STOP = "STOP: score exceeds top-3 threshold."
CURRENT_BEST = 0.48854


def sha256(path: Path) -> str:
    if not path.exists():
        return "missing"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def records_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def run_case(label: str, score: float, expected_next: str, expected_top3: str) -> dict[str, str]:
    cmd = [
        sys.executable,
        str(ROUTER),
        "--group",
        "overlay",
        "--order",
        "8",
        "--score",
        f"{score:.5f}",
        "--previous-score",
        f"{CURRENT_BEST:.5f}",
        "--dry-run",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    output = (proc.stdout + proc.stderr).strip()
    parsed: dict[str, str] = {}
    for line in output.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            parsed[key.strip()] = value.strip()
    actual_next = parsed.get("recommended_next", "")
    actual_top3 = parsed.get("top3_hit", "")
    passed = proc.returncode == 0 and actual_next == expected_next and actual_top3 == expected_top3
    return {
        "label": label,
        "score": f"{score:.5f}",
        "expected_top3": expected_top3,
        "actual_top3": actual_top3,
        "expected_next": expected_next,
        "actual_next": actual_next,
        "exit_code": str(proc.returncode),
        "pass": "yes" if passed else "no",
        "output": output.replace("\n", "\\n"),
    }


def main() -> None:
    before_sha = sha256(RECORDS)
    before_count = records_count(RECORDS)
    rows = [
        run_case("positive_v1840b_stays_on_overlay_hailmary", 0.50000, V1840C, "no"),
        run_case("non_improving_v1840b_uses_alt_structural", 0.48000, V1826C, "no"),
        run_case("top3_hit_stops_without_next_stage", 0.52381, STOP, "yes"),
    ]
    after_sha = sha256(RECORDS)
    after_count = records_count(RECORDS)
    records_unchanged = before_sha == after_sha and before_count == after_count
    failures = [row for row in rows if row["pass"] != "yes"]
    if not records_unchanged:
        failures.append(
            {
                "label": "records_unchanged",
                "score": "",
                "expected_top3": "",
                "actual_top3": "",
                "expected_next": "",
                "actual_next": "",
                "exit_code": "",
                "pass": "no",
                "output": "records mutated during dry-run regression",
            }
        )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "label",
        "score",
        "expected_top3",
        "actual_top3",
        "expected_next",
        "actual_next",
        "exit_code",
        "pass",
        "output",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# v1932 v1840b Override Route Regression",
        "",
        "## Summary",
        "",
        f"- Scenarios checked: `{len(rows)}`",
        f"- Failures: `{len(failures)}`",
        f"- Records unchanged: `{'yes' if records_unchanged else 'no'}`",
        f"- Current best used for routing: `{CURRENT_BEST:.5f}`",
        "",
        "## Matrix",
        "",
        "| Label | Score | Expected top3 | Actual top3 | Expected next | Actual next | Pass |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        expected = row["expected_next"].replace("|", "\\|")
        actual = row["actual_next"].replace("|", "\\|")
        lines.append(
            f"| {row['label']} | `{row['score']}` | {row['expected_top3']} | {row['actual_top3']} | `{expected}` | `{actual}` | {row['pass']} |"
        )
    lines.extend(
        [
            "",
            "## Completion boundary",
            "",
            "This regression only protects the local post-score route. The active goal is complete only after a real private score greater than `0.52380` is recorded.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("V1932_V1840B_OVERRIDE_ROUTE_REGRESSION")
    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    print(f"RECORDS_UNCHANGED={'yes' if records_unchanged else 'no'}")
    for failure in failures:
        print(f"FAIL={failure['label']}")
    if failures:
        raise SystemExit("v1840b override route regression failed")


if __name__ == "__main__":
    main()
