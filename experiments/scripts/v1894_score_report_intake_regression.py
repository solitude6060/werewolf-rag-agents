#!/usr/bin/env python3
"""Regression-check SCORE_REPORT intake validation."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

INTAKE = Path("experiments/scripts/v1894_score_report_intake.py")
UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
OUT_CSV = Path("experiments/reports/v1894_score_report_intake_regression.csv")
OUT_MD = Path("experiments/reports/v1894_score_report_intake_regression.md")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def report_text(*, score: str, sha: str | None = None, real_flag: str = "yes", path: str | None = None) -> str:
    metadata = json.loads(Path("experiments/final_submission_package/current_upload/metadata.json").read_text(encoding="utf-8"))
    return "\n".join(
        [
            "SCORE_REPORT",
            f"uploaded_path={path or UPLOAD}",
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


def run_intake(path: Path, out_json: Path, out_md: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INTAKE), str(path), "--out-json", str(out_json), "--out-md", str(out_md)],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> None:
    cases = [
        {
            "label": "valid_top3_report",
            "text": report_text(score="0.52381"),
            "expect_exit": "zero",
            "expect_text": "SCORE_STATUS=top3_completion_candidate",
        },
        {
            "label": "valid_continue_report",
            "text": report_text(score="0.47120"),
            "expect_exit": "zero",
            "expect_text": "SCORE_STATUS=continue_routing_required",
        },
        {
            "label": "reject_wrong_sha",
            "text": report_text(score="0.47120", sha="0" * 64),
            "expect_exit": "nonzero",
            "expect_text": "sha_matches_current_upload",
        },
        {
            "label": "reject_missing_real_private_flag",
            "text": report_text(score="0.47120", real_flag="no"),
            "expect_exit": "nonzero",
            "expect_text": "score_marked_real_private",
        },
        {
            "label": "reject_percentage_like_score",
            "text": report_text(score="47.119"),
            "expect_exit": "nonzero",
            "expect_text": "Invalid real_private_score",
        },
        {
            "label": "reject_wrong_upload_path",
            "text": report_text(score="0.47120", path="experiments/final_submission_package/current_upload/wrong.csv"),
            "expect_exit": "nonzero",
            "expect_text": "uploaded_path_matches_current",
        },
    ]

    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="v1894_score_report_") as tmp:
        tmpdir = Path(tmp)
        for case in cases:
            report = tmpdir / f"{case['label']}.txt"
            report.write_text(case["text"], encoding="utf-8")
            proc = run_intake(report, tmpdir / f"{case['label']}.json", tmpdir / f"{case['label']}.md")
            output = (proc.stdout + proc.stderr).strip()
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

    failures = [row for row in rows if row["pass"] != "yes"]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["label", "exit_code", "expected_exit", "expected_text", "text_found", "pass"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# v1894 Score Report Intake Regression",
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
            "The intake validator accepts valid top-3/continue reports and rejects wrong SHA, missing real-private flag, percentage-like score, and wrong upload path before command-center routing.",
            "",
            "## Completion boundary",
            "",
            "This regression validates score-report intake only. The active goal is complete only after a real private score greater than `0.52380` is recorded.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    if failures:
        raise SystemExit("score report intake regression failed")


if __name__ == "__main__":
    main()
