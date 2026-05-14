#!/usr/bin/env python3
"""Regression-check the current SCORE_REPORT score injection bridge."""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

BRIDGE = Path("experiments/scripts/v1898_current_score_report_bridge.py")
TEMPLATE = Path("experiments/final_submission_package/current_upload/SCORE_REPORT.txt")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
RECORDS_MD = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.md")
OUT_CSV = Path("experiments/reports/v1898_current_score_report_bridge_regression.csv")
OUT_MD = Path("experiments/reports/v1898_current_score_report_bridge_regression.md")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_state(path: Path) -> str:
    if not path.exists():
        return "missing"
    return f"present:{sha256(path)}"


def run_case(*, score: str, template: Path, out_json: Path, out_md: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BRIDGE),
            "--score",
            score,
            "--template",
            str(template),
            "--out-json",
            str(out_json),
            "--out-md",
            str(out_md),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> None:
    before = {"csv": file_state(RECORDS), "md": file_state(RECORDS_MD)}
    cases = [
        {
            "label": "valid_continue_score_routes_next_csv",
            "score": "0.47120",
            "template_text": TEMPLATE.read_text(encoding="utf-8"),
            "expect_exit": "zero",
            "expect_text": "scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv",
        },
        {
            "label": "valid_top3_score_routes_stop",
            "score": "0.50672",
            "template_text": TEMPLATE.read_text(encoding="utf-8"),
            "expect_exit": "zero",
            "expect_text": "STOP: score exceeds top-3 threshold.",
        },
        {
            "label": "invalid_percentage_like_score_rejected",
            "score": "47.119",
            "template_text": TEMPLATE.read_text(encoding="utf-8"),
            "expect_exit": "nonzero",
            "expect_text": "Invalid --score",
        },
        {
            "label": "missing_placeholder_rejected",
            "score": "0.47120",
            "template_text": TEMPLATE.read_text(encoding="utf-8").replace("<REAL_PRIVATE_SCORE_DECIMAL>", "0.47120"),
            "expect_exit": "nonzero",
            "expect_text": "missing placeholder",
        },
    ]

    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="v1898_bridge_regression_") as tmp:
        tmpdir = Path(tmp)
        for case in cases:
            template = tmpdir / f"{case['label']}_template.txt"
            template.write_text(case["template_text"], encoding="utf-8")
            out_json = tmpdir / f"{case['label']}.json"
            out_md = tmpdir / f"{case['label']}.md"
            proc = run_case(score=case["score"], template=template, out_json=out_json, out_md=out_md)
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
    after = {"csv": file_state(RECORDS), "md": file_state(RECORDS_MD)}
    records_unchanged = before == after
    failures = [row for row in rows if row["pass"] != "yes"]
    if not records_unchanged:
        failures.append({"label": "official_records_unchanged", "pass": "no"})

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["label", "exit_code", "expected_exit", "expected_text", "text_found", "pass"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# v1898 Current Score Report Bridge Regression",
        "",
        "Date: 2026-05-15",
        "",
        "## Summary",
        "",
        f"- Scenarios checked: `{len(rows)}`",
        f"- Failures: `{len(failures)}`",
        f"- Official records unchanged: `{records_unchanged}`",
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
            "The wrapper injects valid decimal scores into the current report template, delegates to the v1895 dry-run bridge, rejects unsafe inputs, and leaves official score records unchanged.",
            "",
            "## Completion boundary",
            "",
            "This regression validates local score-entry safety only. The active goal is complete only after a real private score greater than `0.50671` is recorded.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    print(f"OFFICIAL_RECORDS_UNCHANGED={'yes' if records_unchanged else 'no'}")
    if failures:
        raise SystemExit("current score report bridge regression failed")


if __name__ == "__main__":
    main()
