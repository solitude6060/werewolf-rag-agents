#!/usr/bin/env python3
"""Regression-check records-based goal completion gate."""
from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from pathlib import Path

GATE = Path("experiments/scripts/v1906_goal_completion_gate.py")
OUT_CSV = Path("experiments/reports/v1906_goal_completion_gate_regression.csv")
OUT_MD = Path("experiments/reports/v1906_goal_completion_gate_regression.md")
FIELDS = [
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


def record(score: str, top3_hit: str = "no") -> dict[str, str]:
    return {
        "recorded_at_utc": "2026-05-15T00:00:00+00:00",
        "group": "scoreonly_safe_queue",
        "order": "1",
        "candidate": "v1856g",
        "uploaded_path": "experiments/final_submission_package/scoreonly_safe_queue/01_v1856g_scoreonly_balanced_first_private.csv",
        "score": score,
        "delta_vs_current_best": "+0.00001",
        "top3_hit": top3_hit,
        "recommended_next": "STOP: score exceeds top-3 threshold." if top3_hit == "yes" else "next.csv",
    }


def write_records(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_gate(records: Path, out_json: Path, out_md: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), "--records", str(records), "--out-json", str(out_json), "--out-md", str(out_md)],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> None:
    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="v1906_goal_gate_") as tmp:
        tmpdir = Path(tmp)
        below = tmpdir / "below.csv"
        write_records(below, [record("0.47120", "no")])
        hit = tmpdir / "hit.csv"
        write_records(hit, [record("0.50672", "yes")])
        mismatch = tmpdir / "mismatch.csv"
        write_records(mismatch, [record("0.50672", "no")])
        invalid = tmpdir / "invalid.csv"
        write_records(invalid, [record("47.119", "yes")])
        overflow = tmpdir / "overflow.csv"
        write_records(overflow, [record("0.46000", "no") for _ in range(6)])
        missing = tmpdir / "missing.csv"

        cases = [
            {
                "label": "no_records_is_not_complete",
                "records": missing,
                "expect_exit": "zero",
                "expect_text": "GOAL_COMPLETE=no",
            },
            {
                "label": "below_threshold_is_not_complete",
                "records": below,
                "expect_exit": "zero",
                "expect_text": "GOAL_COMPLETE=no",
            },
            {
                "label": "top3_record_is_complete",
                "records": hit,
                "expect_exit": "zero",
                "expect_text": "GOAL_COMPLETE=yes",
            },
            {
                "label": "top3_flag_mismatch_rejected",
                "records": mismatch,
                "expect_exit": "nonzero",
                "expect_text": "top3_flag_mismatch",
            },
            {
                "label": "invalid_score_rejected",
                "records": invalid,
                "expect_exit": "nonzero",
                "expect_text": "score_out_of_range",
            },
            {
                "label": "budget_overflow_not_complete",
                "records": overflow,
                "expect_exit": "zero",
                "expect_text": "RECORDS_CONSISTENT=no",
            },
        ]
        for case in cases:
            out_json = tmpdir / f"{case['label']}.json"
            out_md = tmpdir / f"{case['label']}.md"
            proc = run_gate(case["records"], out_json, out_md)
            output = (proc.stdout + proc.stderr).strip()
            if out_md.exists():
                output += "\n" + out_md.read_text(encoding="utf-8")
            exit_ok = (proc.returncode == 0) if case["expect_exit"] == "zero" else (proc.returncode != 0)
            text_ok = case["expect_text"] in output
            rows.append(
                {
                    "label": case["label"],
                    "exit_code": str(proc.returncode),
                    "expected_exit": case["expect_exit"],
                    "expected_text": case["expect_text"],
                    "text_found": "yes" if text_ok else "no",
                    "pass": "yes" if exit_ok and text_ok else "no",
                }
            )

    failures = [row for row in rows if row["pass"] != "yes"]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["label", "exit_code", "expected_exit", "expected_text", "text_found", "pass"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# v1906 Goal Completion Gate Regression",
        "",
        "Date: 2026-05-15",
        "",
        "## Summary",
        "",
        f"- Scenarios checked: `{len(rows)}`",
        f"- Failures: `{len(failures)}`",
        "",
        "## Matrix",
        "",
        "| Label | Exit code | Expected exit | Text found | Pass |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['label']} | `{row['exit_code']}` | `{row['expected_exit']}` | {row['text_found']} | {row['pass']} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "The gate returns complete only for a consistent score record strictly above the top-3 threshold and rejects inconsistent records.",
            "",
            "## Completion boundary",
            "",
            "This regression validates the local completion gate only. A real private score record is still required in the official records file before the active goal can be marked complete.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    if failures:
        raise SystemExit("goal completion gate regression failed")


if __name__ == "__main__":
    main()
