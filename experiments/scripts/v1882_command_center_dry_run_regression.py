#!/usr/bin/env python3
"""Regression-check the user-facing post-score command center dry-run surface."""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

COMMAND_CENTER = Path("experiments/scripts/v1872_post_score_command_center.py")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
RECORDS_MD = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.md")
CURRENT_UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
CURRENT_METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
OUT_CSV = Path("experiments/reports/v1882_command_center_dry_run_regression.csv")
OUT_MD = Path("experiments/reports/v1882_command_center_dry_run_regression.md")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_case(args: list[str]) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(COMMAND_CENTER), *args]
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def parse_kv(output: str) -> dict[str, str]:
    values: dict[str, str] = {}
    lines = output.splitlines()
    for index, line in enumerate(lines):
        if "=" in line:
            key, value = line.split("=", 1)
            if key.isupper() or key in {"group", "order", "source", "candidate", "score", "top3_hit", "recommended_next"}:
                values[key] = value.strip()
        if line == "NEXT_CONFIRM_COMMAND" and index + 1 < len(lines):
            values["NEXT_CONFIRM_COMMAND"] = lines[index + 1].strip()
    return values


def expect_contains(text: str, expected: str) -> bool:
    return expected in text


def main() -> None:
    before_records = RECORDS.exists() or RECORDS_MD.exists()
    before_upload_sha = sha256(CURRENT_UPLOAD)
    before_metadata_sha = sha256(CURRENT_METADATA)

    cases = [
        {
            "label": "scoreonly_order1_tiny_positive",
            "args": ["--group", "scoreonly_safe_queue", "--order", "1", "--score", "0.47120"],
            "expected_status": "concrete_ok:scoreonly_safe_queue#2:v1853g",
            "expected_next": "scoreonly_safe_queue/02_v1853g_scoreonly_max_proxy_private.csv",
            "expected_confirm_fragment": "--group scoreonly_safe_queue --order 1 --score 0.47120 --confirm-real-score",
        },
        {
            "label": "scoreonly_order1_exact_best",
            "args": ["--group", "scoreonly_safe_queue", "--order", "1", "--score", "0.47119"],
            "expected_status": "concrete_ok:scoreonly_safe_queue#3:v1850g",
            "expected_next": "scoreonly_safe_queue/03_v1850g_scoreonly_lowtail_private.csv",
            "expected_confirm_fragment": "--group scoreonly_safe_queue --order 1 --score 0.47119 --confirm-real-score",
        },
        {
            "label": "scoreonly_order1_top3_stop",
            "args": ["--group", "scoreonly_safe_queue", "--order", "1", "--score", "0.50672"],
            "expected_status": "non_concrete_ok",
            "expected_next": "STOP: score exceeds top-3 threshold.",
            "expected_confirm_fragment": "--group scoreonly_safe_queue --order 1 --score 0.50672 --confirm-real-score",
        },
        {
            "label": "scoreonly_order1_severe_regression",
            "args": ["--group", "scoreonly_safe_queue", "--order", "1", "--score", "0.46400"],
            "expected_status": "concrete_ok:scoreonly_safe_queue#5:v1846g",
            "expected_next": "scoreonly_safe_queue/05_v1846g_scoreonly_rolecap_private.csv",
            "expected_confirm_fragment": "--group scoreonly_safe_queue --order 1 --score 0.46400 --confirm-real-score",
        },
        {
            "label": "scoreonly_order5_fallback_to_structural_queue",
            "args": ["--group", "scoreonly_safe_queue", "--order", "5", "--score", "0.46400"],
            "expected_status": "concrete_ok:queue#1:v1826a",
            "expected_next": "queue/01_v1826a_primary_first_private.csv",
            "expected_confirm_fragment": "--group scoreonly_safe_queue --order 5 --score 0.46400 --confirm-real-score",
        },
        {
            "label": "portfolio_order2_positive_preserves_previous",
            "args": ["--group", "portfolio_queue", "--order", "2", "--score", "0.48001", "--previous-score", "0.48000"],
            "expected_status": "concrete_ok:charprior_queue#2:v1853b",
            "expected_next": "charprior_queue/02_v1853b_queue02_v1850b_charprior_private.csv",
            "expected_confirm_fragment": "--group portfolio_queue --order 2 --score 0.48001 --previous-score 0.48000 --confirm-real-score",
        },
        {
            "label": "portfolio_order2_skip_stage_preserved",
            "args": ["--group", "portfolio_queue", "--order", "2", "--score", "0.48001", "--previous-score", "0.48000", "--skip-stage"],
            "expected_status": "concrete_ok:charprior_queue#2:v1853b",
            "expected_next": "charprior_queue/02_v1853b_queue02_v1850b_charprior_private.csv",
            "expected_confirm_fragment": "--group portfolio_queue --order 2 --score 0.48001 --previous-score 0.48000 --confirm-real-score --skip-stage",
        },
        {
            "label": "charprior_order2_positive",
            "args": ["--group", "charprior_queue", "--order", "2", "--score", "0.48101", "--previous-score", "0.48001"],
            "expected_status": "concrete_ok:charprior_queue#3:v1853c",
            "expected_next": "charprior_queue/03_v1853c_queue03_v1850c_charprior_private.csv",
            "expected_confirm_fragment": "--group charprior_queue --order 2 --score 0.48101 --previous-score 0.48001 --confirm-real-score",
        },
    ]

    rows: list[dict[str, str]] = []
    for case in cases:
        proc = run_case(case["args"])
        output = (proc.stdout + proc.stderr).strip()
        values = parse_kv(output)
        status_ok = values.get("NEXT_PATH_STATUS") == case["expected_status"]
        next_ok = expect_contains(values.get("recommended_next", ""), case["expected_next"])
        write_ok = values.get("WRITE_STATUS") == "dry_run_only"
        confirm_ok = expect_contains(values.get("NEXT_CONFIRM_COMMAND", ""), case["expected_confirm_fragment"])
        exit_ok = proc.returncode == 0
        passed = exit_ok and status_ok and next_ok and write_ok and confirm_ok
        rows.append(
            {
                "label": case["label"],
                "exit_code": str(proc.returncode),
                "next_path_status": values.get("NEXT_PATH_STATUS", ""),
                "recommended_next": values.get("recommended_next", ""),
                "write_status": values.get("WRITE_STATUS", ""),
                "confirm_command": values.get("NEXT_CONFIRM_COMMAND", ""),
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
        failures.append({"label": "dry_run_mutation_check", "pass": "no"})

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["label", "exit_code", "next_path_status", "recommended_next", "write_status", "confirm_command", "pass"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# v1882 Command Center Dry-Run Regression",
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
        "| Label | Next path status | Write status | Pass |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['label']} | `{row['next_path_status']}` | `{row['write_status']}` | {row['pass']} |")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "The user-facing post-score command center dry-runs are safe and produce validated next-path statuses without mutating score records or the staged current upload.",
            "",
            "## Completion boundary",
            "",
            "This regression does not complete the active score objective; completion still requires a real Kaggle private score greater than `0.50671`.",
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
        raise SystemExit("command center dry-run regression failed")


if __name__ == "__main__":
    main()
