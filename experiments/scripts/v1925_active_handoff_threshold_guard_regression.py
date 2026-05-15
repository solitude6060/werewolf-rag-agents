#!/usr/bin/env python3
"""Regression-check the active handoff stale-threshold guard."""
from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from pathlib import Path

GUARD = Path("experiments/scripts/v1925_active_handoff_threshold_guard.py")
OUT_CSV = Path("experiments/reports/v1925_active_handoff_threshold_guard_regression.csv")
OUT_MD = Path("experiments/reports/v1925_active_handoff_threshold_guard_regression.md")


def run_guard(path: Path, tmpdir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(GUARD),
            "--path",
            str(path),
            "--out-csv",
            str(tmpdir / f"{path.name}.csv"),
            "--out-md",
            str(tmpdir / f"{path.name}.md"),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> None:
    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="v1925_guard_regression_") as tmp:
        tmpdir = Path(tmp)
        stale = tmpdir / "stale.md"
        live = tmpdir / "live.md"
        stale.write_text("Stop if score greater than 0.50671\n", encoding="utf-8")
        live.write_text("Stop if score greater than 0.52380\n", encoding="utf-8")
        cases = [
            ("stale_file_rejected", stale, "nonzero", "FAILURES=1"),
            ("live_file_accepted", live, "zero", "ACTIVE_HANDOFF_THRESHOLD_READY=yes"),
        ]
        for label, path, expected_exit, expected_text in cases:
            proc = run_guard(path, tmpdir)
            output = (proc.stdout + proc.stderr).strip()
            exit_ok = (proc.returncode == 0) if expected_exit == "zero" else (proc.returncode != 0)
            text_ok = expected_text in output
            rows.append(
                {
                    "label": label,
                    "exit_code": str(proc.returncode),
                    "expected_exit": expected_exit,
                    "expected_text": expected_text,
                    "text_found": "yes" if text_ok else "no",
                    "pass": "yes" if exit_ok and text_ok else "no",
                }
            )

    real = subprocess.run(
        [sys.executable, str(GUARD), "--out-csv", "/tmp/v1925_real_guard.csv", "--out-md", "/tmp/v1925_real_guard.md"],
        text=True,
        capture_output=True,
        check=False,
    )
    real_output = (real.stdout + real.stderr).strip()
    rows.append(
        {
            "label": "real_active_paths_accepted",
            "exit_code": str(real.returncode),
            "expected_exit": "zero",
            "expected_text": "ACTIVE_HANDOFF_THRESHOLD_READY=yes",
            "text_found": "yes" if "ACTIVE_HANDOFF_THRESHOLD_READY=yes" in real_output else "no",
            "pass": "yes" if real.returncode == 0 and "ACTIVE_HANDOFF_THRESHOLD_READY=yes" in real_output else "no",
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
        "# v1925 Active Handoff Threshold Guard Regression",
        "",
        "## Summary",
        "",
        f"- Scenarios: `{len(rows)}`",
        f"- Failures: `{len(failures)}`",
        "",
        "## Matrix",
        "",
        "| Label | Exit code | Expected exit | Text found | Pass |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['label']} | `{row['exit_code']}` | `{row['expected_exit']}` | {row['text_found']} | {row['pass']} |")
    lines.extend(
        [
            "",
            "## Completion boundary",
            "",
            "This regression only validates the stale-threshold guard. The active goal is complete only after a real private score greater than `0.52380` is recorded.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("V1925_ACTIVE_HANDOFF_THRESHOLD_GUARD_REGRESSION")
    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    for failure in failures:
        print(f"FAIL={failure['label']}")
    if failures:
        raise SystemExit("active handoff threshold guard regression failed")


if __name__ == "__main__":
    main()
