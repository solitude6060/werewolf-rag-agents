#!/usr/bin/env python3
"""Regression-check adaptive final-attempt state guard."""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GUARD = Path("experiments/scripts/v1904_attempt_state_guard.py")
MANIFEST = Path("experiments/final_submission_package/manifests/final_submission_pack_manifest.csv")
METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
OUT_CSV = Path("experiments/reports/v1904_attempt_state_guard_regression.csv")
OUT_MD = Path("experiments/reports/v1904_attempt_state_guard_regression.md")
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


def manifest_rows() -> list[dict[str, str]]:
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def row_for(group: str, order: str) -> dict[str, str]:
    for row in manifest_rows():
        if row.get("group") == group and row.get("order") == str(order):
            return row
    raise SystemExit(f"missing manifest row {group}#{order}")


def write_records(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def record(*, group: str, order: str, candidate: str, uploaded_path: str, score: str, top3_hit: str, recommended_next: str) -> dict[str, str]:
    return {
        "recorded_at_utc": "2026-05-15T00:00:00+00:00",
        "group": group,
        "order": order,
        "candidate": candidate,
        "uploaded_path": uploaded_path,
        "score": score,
        "delta_vs_current_best": "+0.00001",
        "top3_hit": top3_hit,
        "recommended_next": recommended_next,
    }


def run_guard(records: Path, metadata: Path, upload: Path, out_json: Path, out_md: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(GUARD),
            "--manifest",
            str(MANIFEST),
            "--records",
            str(records),
            "--metadata",
            str(metadata),
            "--upload",
            str(upload),
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
    first_row = row_for("scoreonly_safe_queue", "1")
    second_row = row_for("scoreonly_safe_queue", "2")
    base_metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="v1904_attempt_state_") as tmp:
        tmpdir = Path(tmp)
        upload = tmpdir / "submission.csv"
        shutil.copyfile(UPLOAD, upload)
        metadata = tmpdir / "metadata.json"
        metadata.write_text(json.dumps(base_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        no_records = tmpdir / "no_records.csv"  # intentionally absent
        match_records = tmpdir / "match_records.csv"
        write_records(
            match_records,
            [
                record(
                    group="scoreonly_safe_queue",
                    order="0",
                    candidate="previous",
                    uploaded_path="previous.csv",
                    score="0.47120",
                    top3_hit="no",
                    recommended_next=first_row["output_path"],
                )
            ],
        )
        mismatch_records = tmpdir / "mismatch_records.csv"
        write_records(
            mismatch_records,
            [
                record(
                    group="scoreonly_safe_queue",
                    order="1",
                    candidate="v1856g",
                    uploaded_path=first_row["output_path"],
                    score="0.47120",
                    top3_hit="no",
                    recommended_next=second_row["output_path"],
                )
            ],
        )
        stop_records = tmpdir / "stop_records.csv"
        write_records(
            stop_records,
            [
                record(
                    group="scoreonly_safe_queue",
                    order="1",
                    candidate="v1856g",
                    uploaded_path=first_row["output_path"],
                    score="0.50672",
                    top3_hit="yes",
                    recommended_next="STOP: score exceeds top-3 threshold.",
                )
            ],
        )
        exhausted_records = tmpdir / "exhausted_records.csv"
        write_records(
            exhausted_records,
            [
                record(
                    group="scoreonly_safe_queue",
                    order=str(i + 1),
                    candidate=f"v{i}",
                    uploaded_path=f"v{i}.csv",
                    score="0.46000",
                    top3_hit="no",
                    recommended_next=first_row["output_path"],
                )
                for i in range(5)
            ],
        )

        cases = [
            {
                "label": "no_records_first_upload_passes",
                "records": no_records,
                "expect_exit": "zero",
                "expect_text": "STATE=no_records_first_upload",
            },
            {
                "label": "latest_recommended_match_passes",
                "records": match_records,
                "expect_exit": "zero",
                "expect_text": "STATE=staged_latest_recommended",
            },
            {
                "label": "latest_recommended_mismatch_rejected",
                "records": mismatch_records,
                "expect_exit": "nonzero",
                "expect_text": "current_source_matches_expected",
            },
            {
                "label": "stop_record_rejected",
                "records": stop_records,
                "expect_exit": "nonzero",
                "expect_text": "no_prior_top3_hit",
            },
            {
                "label": "budget_exhausted_rejected",
                "records": exhausted_records,
                "expect_exit": "nonzero",
                "expect_text": "attempt_budget_not_exhausted",
            },
        ]
        for case in cases:
            out_json = tmpdir / f"{case['label']}.json"
            out_md = tmpdir / f"{case['label']}.md"
            proc = run_guard(case["records"], metadata, upload, out_json, out_md)
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
        "# v1904 Attempt State Guard Regression",
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
            "The guard accepts the first upload or a staged latest recommendation, and rejects mismatched, stopped, or exhausted attempt states.",
            "",
            "## Completion boundary",
            "",
            "This regression validates local attempt-state readiness only. The active goal is complete only after a real private score greater than `0.50671` is recorded.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    if failures:
        raise SystemExit("attempt state guard regression failed")


if __name__ == "__main__":
    main()
