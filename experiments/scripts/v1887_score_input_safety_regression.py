#!/usr/bin/env python3
"""Regression-check score input validation for final-attempt post-score tools."""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

COMMAND_CENTER = Path("experiments/scripts/v1872_post_score_command_center.py")
ROUTER = Path("experiments/scripts/v1836_score_feedback_router.py")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
RECORDS_MD = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.md")
CURRENT_UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
CURRENT_METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
OUT_CSV = Path("experiments/reports/v1887_score_input_safety_regression.csv")
OUT_MD = Path("experiments/reports/v1887_score_input_safety_regression.md")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def combined(proc: subprocess.CompletedProcess[str]) -> str:
    return (proc.stdout + proc.stderr).strip()


def main() -> None:
    before_records = RECORDS.exists() or RECORDS_MD.exists()
    before_upload_sha = sha256(CURRENT_UPLOAD)
    before_metadata_sha = sha256(CURRENT_METADATA)

    cases = [
        {
            "label": "command_center_rejects_percentage_like_score",
            "cmd": [sys.executable, str(COMMAND_CENTER), "--score", "47.119"],
            "expect_exit": "nonzero",
            "expect_text": "Invalid --score",
        },
        {
            "label": "command_center_rejects_nan_score",
            "cmd": [sys.executable, str(COMMAND_CENTER), "--score", "nan"],
            "expect_exit": "nonzero",
            "expect_text": "Invalid --score",
        },
        {
            "label": "command_center_rejects_negative_score",
            "cmd": [sys.executable, str(COMMAND_CENTER), "--score", "-0.10000"],
            "expect_exit": "nonzero",
            "expect_text": "Invalid --score",
        },
        {
            "label": "command_center_rejects_bad_previous_score",
            "cmd": [sys.executable, str(COMMAND_CENTER), "--score", "0.47120", "--previous-score", "47.119"],
            "expect_exit": "nonzero",
            "expect_text": "Invalid --previous-score",
        },
        {
            "label": "router_rejects_percentage_like_score",
            "cmd": [sys.executable, str(ROUTER), "--group", "scoreonly_safe_queue", "--order", "1", "--score", "47.119", "--dry-run"],
            "expect_exit": "nonzero",
            "expect_text": "Invalid --score",
        },
        {
            "label": "valid_top3_dry_run_still_routes_stop",
            "cmd": [sys.executable, str(COMMAND_CENTER), "--score", "0.50672"],
            "expect_exit": "zero",
            "expect_text": "NEXT_PATH_STATUS=non_concrete_ok",
        },
        {
            "label": "valid_tiny_positive_dry_run_still_routes_next_csv",
            "cmd": [sys.executable, str(COMMAND_CENTER), "--score", "0.47120"],
            "expect_exit": "zero",
            "expect_text": "scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv",
        },
    ]

    rows: list[dict[str, str]] = []
    for case in cases:
        proc = run(case["cmd"])
        text = combined(proc)
        exit_ok = (proc.returncode == 0) if case["expect_exit"] == "zero" else (proc.returncode != 0)
        text_ok = case["expect_text"] in text
        passed = exit_ok and text_ok
        rows.append(
            {
                "label": case["label"],
                "exit_code": str(proc.returncode),
                "expected_exit": case["expect_exit"],
                "expected_text": case["expect_text"],
                "text_found": "yes" if text_ok else "no",
                "pass": "yes" if passed else "no",
            }
        )

    after_records = RECORDS.exists() or RECORDS_MD.exists()
    after_upload_sha = sha256(CURRENT_UPLOAD)
    after_metadata_sha = sha256(CURRENT_METADATA)
    mutation_ok = (
        before_records == after_records
        and before_upload_sha == after_upload_sha
        and before_metadata_sha == after_metadata_sha
    )
    failures = [row for row in rows if row["pass"] != "yes"]
    if not mutation_ok:
        failures.append({"label": "mutation_check", "pass": "no"})

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["label", "exit_code", "expected_exit", "expected_text", "text_found", "pass"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# v1887 Score Input Safety Regression",
        "",
        "Date: 2026-05-15",
        "",
        "## Summary",
        "",
        f"- Scenarios checked: `{len(rows)}`",
        f"- Failures: `{len(failures)}`",
        f"- Score feedback records existed before: `{before_records}`",
        f"- Score feedback records existed after: `{after_records}`",
        f"- Current upload SHA unchanged: `{before_upload_sha == after_upload_sha}`",
        f"- Current metadata SHA unchanged: `{before_metadata_sha == after_metadata_sha}`",
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
            "Malformed score inputs are rejected before routing or recording, while valid dry-runs still route to the expected stop/next-candidate outcomes without mutating score records or staged upload files.",
            "",
            "## Completion boundary",
            "",
            "This safety regression does not complete the active score objective. Completion still requires a real Kaggle private score greater than `0.50671`.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    print(f"MUTATION_OK={'yes' if mutation_ok else 'no'}")
    if failures:
        raise SystemExit("score input safety regression failed")


if __name__ == "__main__":
    main()
