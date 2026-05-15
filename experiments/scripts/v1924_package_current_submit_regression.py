#!/usr/bin/env python3
"""Regression-check that the hand-in package rebuilds the current upload bytes."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CANONICAL = Path("experiments/final_submission_package/current_upload/submission.csv")
PACKAGE_SUBMISSION = Path("hw2_D13922024/submission.csv")
PACKAGE_MAKE = Path("hw2_D13922024/make_final.py")
PACKAGE_README = Path("hw2_D13922024/README.md")
OUT_CSV = Path("experiments/reports/v1924_package_current_submit_regression.csv")
OUT_MD = Path("experiments/reports/v1924_package_current_submit_regression.md")
METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def add(checks: list[dict[str, str]], name: str, ok: bool, detail: str) -> None:
    checks.append({"name": name, "ok": "yes" if ok else "no", "detail": detail})


def main() -> None:
    checks: list[dict[str, str]] = []
    canonical_sha = sha256(CANONICAL)
    package_sha = sha256(PACKAGE_SUBMISSION)
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    candidate = str(metadata.get("candidate", ""))
    with tempfile.TemporaryDirectory(prefix="v1924_package_make_final_") as tmp:
        output = Path(tmp) / "submission.csv"
        proc = subprocess.run(
            [sys.executable, str(PACKAGE_MAKE), "--output", str(output)],
            text=True,
            capture_output=True,
            check=False,
        )
        command_output = (proc.stdout + proc.stderr).strip()
        normalized_command_output = command_output.replace(str(output), "<TEMP_SUBMISSION>")
        output_exists = output.exists()
        output_sha = sha256(output) if output_exists else "missing"
        output_rows = row_count(output) if output_exists else 0

    readme = PACKAGE_README.read_text(encoding="utf-8")
    add(checks, "make_final_exit_zero", proc.returncode == 0, f"exit={proc.returncode}; {normalized_command_output}")
    add(checks, "canonical_sha_matches_metadata", canonical_sha == str(metadata.get("sha256", "")), canonical_sha)
    add(checks, "package_submission_matches_canonical", package_sha == canonical_sha, package_sha)
    add(checks, "make_final_output_matches_canonical", output_sha == canonical_sha, output_sha)
    add(checks, "make_final_rows_397", output_rows == 397, str(output_rows))
    add(checks, "validator_ok", "OK: 397 predictions validated" in command_output, normalized_command_output)
    add(checks, "readme_mentions_current_checkpoint", "checkpoints/final_current_private.csv" in readme, "final_current_private.csv")
    add(checks, "readme_mentions_current_candidate", candidate in readme, candidate)
    add(checks, "readme_mentions_live_threshold", ">0.52380" in readme or "> 0.52380" in readme, "0.52380")
    add(checks, "readme_no_old_default_v1856g", "Candidate lineage: `scoreonly_safe_queue` order `1`, `v1856g`." not in readme, "old v1856g default string")
    add(checks, "readme_no_old_threshold", ">0.50671" not in readme and "greater than `0.50671`" not in readme, "0.50671")

    failures = [check for check in checks if check["ok"] != "yes"]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "ok", "detail"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(checks)

    lines = [
        "# v1924 Package Current Submit Regression",
        "",
        "## Summary",
        "",
        f"- Failures: `{len(failures)}`",
        f"- Canonical SHA: `{canonical_sha}`",
        f"- Package submission SHA: `{package_sha}`",
        f"- make_final output SHA: `{output_sha}`",
        "",
        "## Checks",
        "",
        "| Check | OK | Detail |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        detail = check["detail"].replace("|", "\\|")
        lines.append(f"| {check['name']} | {check['ok']} | `{detail}` |")
    lines.extend(
        [
            "",
            "## Completion boundary",
            "",
            "This regression proves package reproduction alignment only. The active leaderboard goal remains incomplete until a real private score greater than `0.52380` is recorded.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("V1924_PACKAGE_CURRENT_SUBMIT_REGRESSION")
    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"FAILURES={len(failures)}")
    for failure in failures:
        print(f"FAIL={failure['name']} detail={failure['detail']}")
    if failures:
        raise SystemExit("package current submit regression failed")


if __name__ == "__main__":
    main()
