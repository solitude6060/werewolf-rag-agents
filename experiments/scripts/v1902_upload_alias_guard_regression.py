#!/usr/bin/env python3
"""Regression-check upload alias guard behavior."""
from __future__ import annotations

import csv
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GUARD = Path("experiments/scripts/v1902_upload_alias_guard.py")
CANONICAL = Path("experiments/final_submission_package/current_upload/submission.csv")
OUT_CSV = Path("experiments/reports/v1902_upload_alias_guard_regression.csv")
OUT_MD = Path("experiments/reports/v1902_upload_alias_guard_regression.md")


def run_guard(canonical: Path, aliases: list[Path], out_json: Path, out_md: Path) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(GUARD), "--canonical", str(canonical), "--out-json", str(out_json), "--out-md", str(out_md)]
    for alias in aliases:
        cmd.extend(["--alias", str(alias)])
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def mutate_csv(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    # Keep header and row count valid, but change one score byte.
    parts = lines[1].split(",")
    parts[-1] = "0" if parts[-1] != "0" else "1"
    lines[1] = ",".join(parts)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="v1902_alias_guard_") as tmp:
        tmpdir = Path(tmp)
        canonical = tmpdir / "canonical.csv"
        alias_ok = tmpdir / "alias_ok.csv"
        alias_bad = tmpdir / "alias_bad.csv"
        missing_alias = tmpdir / "missing.csv"
        shutil.copyfile(CANONICAL, canonical)
        shutil.copyfile(CANONICAL, alias_ok)
        shutil.copyfile(CANONICAL, alias_bad)
        mutate_csv(alias_bad)

        cases = [
            {
                "label": "valid_alias_passes",
                "canonical": canonical,
                "aliases": [alias_ok],
                "expect_exit": "zero",
                "expect_text": "ALIAS_GUARD_READY=yes",
            },
            {
                "label": "sha_mismatch_rejected",
                "canonical": canonical,
                "aliases": [alias_bad],
                "expect_exit": "nonzero",
                "expect_text": "alias_1_sha_matches",
            },
            {
                "label": "missing_alias_rejected",
                "canonical": canonical,
                "aliases": [missing_alias],
                "expect_exit": "nonzero",
                "expect_text": "alias_1_exists",
            },
        ]
        for case in cases:
            out_json = tmpdir / f"{case['label']}.json"
            out_md = tmpdir / f"{case['label']}.md"
            proc = run_guard(case["canonical"], case["aliases"], out_json, out_md)
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
        "# v1902 Upload Alias Guard Regression",
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
            "The guard accepts identical upload aliases and rejects missing or byte-different aliases.",
            "",
            "## Completion boundary",
            "",
            "This regression validates local wrong-file prevention only. The active goal is complete only after a real private score greater than `0.50671` is recorded.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"SCENARIOS={len(rows)}")
    print(f"FAILURES={len(failures)}")
    if failures:
        raise SystemExit("upload alias guard regression failed")


if __name__ == "__main__":
    main()
