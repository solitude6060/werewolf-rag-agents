#!/usr/bin/env python3
"""Regression-check SCORE_REPORT-to-command-center dry-run bridge."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BRIDGE = Path("experiments/scripts/v1895_score_report_command_center.py")
UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
RECORDS_MD = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.md")
OUT_CSV = Path("experiments/reports/v1895_score_report_command_center_regression.csv")
OUT_MD = Path("experiments/reports/v1895_score_report_command_center_regression.md")


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


def report_text(*, score: str, sha: str | None = None, real_flag: str = "yes") -> str:
    metadata = json.loads(Path("experiments/final_submission_package/current_upload/metadata.json").read_text(encoding="utf-8"))
    return "\n".join(
        [
            "SCORE_REPORT",
            f"uploaded_path={UPLOAD}",
            f"candidate={metadata['candidate']}",
            f"group={metadata['group']}",
            f"order={metadata['order']}",
            f"sha256={sha or sha256(UPLOAD)}",
            "rows=397",
            f"real_private_score={score}",
            f"score_is_real_kaggle_private={real_flag}",
            "",
        ]
    )


def run_bridge(report: Path, out_json: Path, out_md: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BRIDGE), str(report), "--out-json", str(out_json), "--out-md", str(out_md)],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> None:
    before = {"csv": file_state(RECORDS), "md": file_state(RECORDS_MD)}
    cases = [
        {
            "label": "valid_continue_report_dry_runs_next_csv",
            "text": report_text(score="0.47120"),
            "expect_exit": "zero",
            "expect_text": "contingency/01_v1825c_diagnostic_neutral_private.csv",
        },
        {
            "label": "valid_top3_report_dry_runs_stop",
            "text": report_text(score="0.52381"),
            "expect_exit": "zero",
            "expect_text": "STOP: score exceeds top-3 threshold.",
        },
        {
            "label": "valid_equal_threshold_report_dry_runs_next_csv",
            "text": report_text(score="0.52380"),
            "expect_exit": "zero",
            "expect_text": "experiments/final_submission_package/queue/02_v1826b_if_01_positive_private.csv",
        },
        {
            "label": "invalid_wrong_sha_stops_before_command_center",
            "text": report_text(score="0.47120", sha="0" * 64),
            "expect_exit": "nonzero",
            "expect_text": "INTAKE_READY=no",
        },
        {
            "label": "invalid_real_flag_stops_before_command_center",
            "text": report_text(score="0.47120", real_flag="no"),
            "expect_exit": "nonzero",
            "expect_text": "INTAKE_READY=no",
        },
    ]

    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="v1895_score_report_") as tmp:
        tmpdir = Path(tmp)
        for case in cases:
            report = tmpdir / f"{case['label']}.txt"
            report.write_text(case["text"], encoding="utf-8")
            out_json = tmpdir / f"{case['label']}.json"
            out_md = tmpdir / f"{case['label']}.md"
            proc = run_bridge(report, out_json, out_md)
            output = (proc.stdout + proc.stderr).strip()
            if out_md.exists():
                output += "\n" + out_md.read_text(encoding="utf-8")
            exit_ok = (proc.returncode == 0) if case["expect_exit"] == "zero" else (proc.returncode != 0)
            text_ok = case["expect_text"] in output
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
        "# v1895 Score Report Command Center Regression",
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
            "The bridge routes valid SCORE_REPORT files through the command-center dry-run and rejects invalid reports before routing, without mutating official score records.",
            "",
            "## Completion boundary",
            "",
            "This regression validates the dry-run bridge only. The active goal is complete only after a real private score greater than `0.52380` is recorded.",
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
        raise SystemExit("score report command-center regression failed")


if __name__ == "__main__":
    main()
