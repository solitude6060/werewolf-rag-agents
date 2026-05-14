#!/usr/bin/env python3
"""Regression-check current upload SCORE_REPORT integrity guard."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

GUARD = Path("experiments/scripts/v1900_current_upload_score_report_guard.py")
UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
SCORE_REPORT = Path("experiments/final_submission_package/current_upload/SCORE_REPORT.txt")
OUT_CSV = Path("experiments/reports/v1900_current_upload_score_report_guard_regression.csv")
OUT_MD = Path("experiments/reports/v1900_current_upload_score_report_guard_regression.md")


def run_guard(score_report: Path, metadata: Path, out_json: Path, out_md: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(GUARD),
            "--upload",
            str(UPLOAD),
            "--metadata",
            str(metadata),
            "--score-report",
            str(score_report),
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
    base_report = SCORE_REPORT.read_text(encoding="utf-8")
    base_metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    cases = [
        {
            "label": "valid_current_report_passes",
            "report_text": base_report,
            "metadata": base_metadata,
            "expect_exit": "zero",
            "expect_text": "SCORE_REPORT_READY=yes",
        },
        {
            "label": "wrong_sha_rejected",
            "report_text": base_report.replace(base_metadata["sha256"], "0" * 64),
            "metadata": base_metadata,
            "expect_exit": "nonzero",
            "expect_text": "sha_matches_upload",
        },
        {
            "label": "filled_score_rejected_before_upload",
            "report_text": base_report.replace("<REAL_PRIVATE_SCORE_DECIMAL>", "0.47120"),
            "metadata": base_metadata,
            "expect_exit": "nonzero",
            "expect_text": "score_placeholder_ready",
        },
        {
            "label": "wrong_candidate_rejected",
            "report_text": base_report.replace("candidate=v1856g", "candidate=v0000x"),
            "metadata": base_metadata,
            "expect_exit": "nonzero",
            "expect_text": "candidate_matches_metadata",
        },
    ]

    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="v1900_score_report_guard_") as tmp:
        tmpdir = Path(tmp)
        for case in cases:
            report = tmpdir / f"{case['label']}.txt"
            report.write_text(case["report_text"], encoding="utf-8")
            metadata = tmpdir / f"{case['label']}_metadata.json"
            metadata.write_text(json.dumps(case["metadata"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
            out_json = tmpdir / f"{case['label']}.json"
            out_md = tmpdir / f"{case['label']}.md"
            proc = run_guard(report, metadata, out_json, out_md)
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
        "# v1900 Current Upload Score Report Guard Regression",
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
            "The guard accepts the current score report only when it matches the staged upload and rejects stale or pre-filled report contexts.",
            "",
            "## Completion boundary",
            "",
            "This regression validates local handoff integrity only. The active goal is complete only after a real private score greater than `0.50671` is recorded.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    if failures:
        raise SystemExit("score report guard regression failed")


if __name__ == "__main__":
    main()
