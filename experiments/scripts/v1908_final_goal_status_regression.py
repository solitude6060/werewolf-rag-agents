#!/usr/bin/env python3
"""Regression-check final goal status action selection."""
from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from pathlib import Path

STATUS = Path("experiments/scripts/v1908_final_goal_status.py")
OUT_CSV = Path("experiments/reports/v1908_final_goal_status_regression.csv")
OUT_MD = Path("experiments/reports/v1908_final_goal_status_regression.md")


def write_mock(path: Path, *, lines: list[str], exit_code: int = 0) -> None:
    body = "\n".join([f"print({line!r})" for line in lines])
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import argparse, sys\n"
        "p=argparse.ArgumentParser()\n"
        "p.add_argument('--out-json')\n"
        "p.add_argument('--out-md')\n"
        "p.parse_args()\n"
        f"{body}\n"
        f"sys.exit({exit_code})\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def run_status(completion: Path, preflight: Path, out_json: Path, out_md: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(STATUS),
            "--completion-gate",
            str(completion),
            "--preflight",
            str(preflight),
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
    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="v1908_status_") as tmp:
        tmpdir = Path(tmp)
        completion_yes = tmpdir / "completion_yes.py"
        write_mock(
            completion_yes,
            lines=["GOAL_COMPLETION_GATE", "GOAL_COMPLETE=yes", "RECORDS_CONSISTENT=yes", "BEST_SCORE=0.50672"],
        )
        completion_no = tmpdir / "completion_no.py"
        write_mock(
            completion_no,
            lines=["GOAL_COMPLETION_GATE", "GOAL_COMPLETE=no", "RECORDS_CONSISTENT=yes", "BEST_SCORE=none"],
        )
        preflight_yes = tmpdir / "preflight_yes.py"
        write_mock(
            preflight_yes,
            lines=[
                "FINAL_UPLOAD_PREFLIGHT",
                "READY_TO_MANUAL_UPLOAD=yes",
                "RELATIVE_UPLOAD_PATH=experiments/final_submission_package/current_upload/submission.csv",
            ],
        )
        preflight_no = tmpdir / "preflight_no.py"
        write_mock(
            preflight_no,
            lines=["FINAL_UPLOAD_PREFLIGHT", "READY_TO_MANUAL_UPLOAD=no"],
            exit_code=1,
        )
        cases = [
            {
                "label": "complete_records_mark_goal_complete",
                "completion": completion_yes,
                "preflight": preflight_yes,
                "expect_exit": "zero",
                "expect_text": "ACTION=MARK_GOAL_COMPLETE",
            },
            {
                "label": "not_complete_ready_upload_current",
                "completion": completion_no,
                "preflight": preflight_yes,
                "expect_exit": "zero",
                "expect_text": "ACTION=UPLOAD_CURRENT",
            },
            {
                "label": "not_complete_not_ready_blocked",
                "completion": completion_no,
                "preflight": preflight_no,
                "expect_exit": "nonzero",
                "expect_text": "ACTION=BLOCKED",
            },
        ]
        for case in cases:
            out_json = tmpdir / f"{case['label']}.json"
            out_md = tmpdir / f"{case['label']}.md"
            proc = run_status(case["completion"], case["preflight"], out_json, out_md)
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
        "# v1908 Final Goal Status Regression",
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
            "The status command chooses mark-complete only from the completion gate, upload-current only when not complete but preflight ready, and blocked when upload readiness fails.",
            "",
            "## Completion boundary",
            "",
            "This regression validates local action selection only. A real private score record is still required before the active goal can be marked complete.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    if failures:
        raise SystemExit("final goal status regression failed")


if __name__ == "__main__":
    main()
