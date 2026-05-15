#!/usr/bin/env python3
"""Regression-check exact v1826a queue#1 post-score boundaries."""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

COMMAND_CENTER = Path("experiments/scripts/v1872_post_score_command_center.py")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
OUT_CSV = Path("experiments/reports/v1919_v1826a_boundary_regression.csv")
OUT_MD = Path("experiments/reports/v1919_v1826a_boundary_regression.md")


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


def run_case(score: float) -> tuple[int, str, dict[str, str]]:
    cmd = [
        sys.executable,
        str(COMMAND_CENTER),
        "--group",
        "queue",
        "--order",
        "1",
        "--score",
        f"{score:.5f}",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    output = (proc.stdout + proc.stderr).strip()
    parsed: dict[str, str] = {}
    for line in output.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            parsed[key.strip()] = value.strip()
    return proc.returncode, output, parsed


def cases() -> list[dict[str, str]]:
    return [
        {
            "label": "top3_strictly_above_threshold",
            "score": "0.52381",
            "expected_top3_hit": "yes",
            "expected_next": "STOP: score exceeds top-3 threshold.",
            "expected_status": "non_concrete_ok",
        },
        {
            "label": "equal_threshold_is_not_complete",
            "score": "0.52380",
            "expected_top3_hit": "no",
            "expected_next": "experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv",
            "expected_status": "concrete_ok:queue#2:v1826b",
        },
        {
            "label": "positive_lower_bound_inclusive",
            "score": "0.47200",
            "expected_top3_hit": "no",
            "expected_next": "experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv",
            "expected_status": "concrete_ok:queue#2:v1826b",
        },
        {
            "label": "just_below_positive_to_neutral_diag",
            "score": "0.47199",
            "expected_top3_hit": "no",
            "expected_next": "experiments/final_submission_package/contingency/01_v1825c_diagnostic_neutral_private.csv",
            "expected_status": "concrete_ok:contingency#1:v1825c",
        },
        {
            "label": "neutral_diag_lower_bound_inclusive",
            "score": "0.47050",
            "expected_top3_hit": "no",
            "expected_next": "experiments/final_submission_package/contingency/01_v1825c_diagnostic_neutral_private.csv",
            "expected_status": "concrete_ok:contingency#1:v1825c",
        },
        {
            "label": "just_below_neutral_to_mild_regression",
            "score": "0.47049",
            "expected_top3_hit": "no",
            "expected_next": "experiments/final_submission_package/contingency/02_v1825a_diagnostic_mild_regression_private.csv",
            "expected_status": "concrete_ok:contingency#2:v1825a",
        },
        {
            "label": "mild_regression_lower_bound_inclusive",
            "score": "0.46500",
            "expected_top3_hit": "no",
            "expected_next": "experiments/final_submission_package/contingency/02_v1825a_diagnostic_mild_regression_private.csv",
            "expected_status": "concrete_ok:contingency#2:v1825a",
        },
        {
            "label": "just_below_mild_to_severe_fallback",
            "score": "0.46499",
            "expected_top3_hit": "no",
            "expected_next": "experiments/final_submission_package/contingency/03_v1827a_fallback_severe_regression_private.csv",
            "expected_status": "concrete_ok:contingency#3:v1827a",
        },
    ]


def main() -> None:
    before_sha = sha256(RECORDS)
    before_count = records_count(RECORDS)
    rows: list[dict[str, str]] = []
    for case in cases():
        rc, output, parsed = run_case(float(case["score"]))
        actual_next = parsed.get("recommended_next", "")
        actual_status = parsed.get("NEXT_PATH_STATUS", "")
        actual_write = parsed.get("WRITE_STATUS", "")
        actual_top3 = parsed.get("top3_hit", "")
        passed = (
            rc == 0
            and actual_next == case["expected_next"]
            and actual_status == case["expected_status"]
            and actual_write == "dry_run_only"
            and actual_top3 == case["expected_top3_hit"]
        )
        rows.append(
            {
                "label": case["label"],
                "score": case["score"],
                "expected_top3_hit": case["expected_top3_hit"],
                "actual_top3_hit": actual_top3,
                "expected_next": case["expected_next"],
                "actual_next": actual_next,
                "expected_status": case["expected_status"],
                "actual_status": actual_status,
                "write_status": actual_write,
                "exit_code": str(rc),
                "pass": "yes" if passed else "no",
                "output": output.replace("\n", "\\n"),
            }
        )

    after_sha = sha256(RECORDS)
    after_count = records_count(RECORDS)
    records_unchanged = before_sha == after_sha and before_count == after_count
    failures = [row for row in rows if row["pass"] != "yes"]
    if not records_unchanged:
        failures.append({"label": "records_mutated", "pass": "no"})

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "label",
        "score",
        "expected_top3_hit",
        "actual_top3_hit",
        "expected_next",
        "actual_next",
        "expected_status",
        "actual_status",
        "write_status",
        "exit_code",
        "pass",
        "output",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# v1919 v1826a Boundary Regression",
        "",
        "Date: 2026-05-15",
        "",
        "## Summary",
        "",
        f"- Scenarios checked: `{len(rows)}`",
        f"- Failures: `{len(failures)}`",
        f"- Records unchanged: `{'yes' if records_unchanged else 'no'}`",
        f"- Records count before/after: `{before_count}` / `{after_count}`",
        "",
        "## Boundary matrix",
        "",
        "| Label | Score | Expected top3 | Actual top3 | Expected status | Actual status | Write status | Pass |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {label} | `{score}` | {expected_top3_hit} | {actual_top3_hit} | `{expected_status}` | `{actual_status}` | `{write_status}` | {pass_} |".format(
                label=row["label"],
                score=row["score"],
                expected_top3_hit=row["expected_top3_hit"],
                actual_top3_hit=row["actual_top3_hit"],
                expected_status=row["expected_status"],
                actual_status=row["actual_status"],
                write_status=row["write_status"],
                pass_=row["pass"],
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "Exact current-upload boundaries are covered. A score equal to `0.52380` is not a completion; only a strictly greater score stops the goal route.",
            "",
            "## Completion boundary",
            "",
            "This regression is local routing evidence only. The active goal is complete only after a real private score greater than `0.52380` is recorded and the records-backed gate reports completion.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    print(f"RECORDS_UNCHANGED={'yes' if records_unchanged else 'no'}")
    if failures:
        raise SystemExit("v1826a boundary regression failed")


if __name__ == "__main__":
    main()
