#!/usr/bin/env python3
"""Regression-check that final attempt runbook prints the live top-3 cutoff."""
from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

RUNBOOK = Path("experiments/scripts/v1866_final_attempt_runbook.py")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
CURRENT_UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
OUT_CSV = Path("experiments/reports/v1922_runbook_threshold_regression.csv")
OUT_MD = Path("experiments/reports/v1922_runbook_threshold_regression.md")
EXPECTED_THRESHOLD = "0.52380"
STALE_THRESHOLD = "0.50671"


def sha256(path: Path) -> str:
    if not path.exists():
        return "missing"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def records_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def main() -> None:
    before = {"records_sha": sha256(RECORDS), "records_count": str(records_count(RECORDS)), "upload_sha": sha256(CURRENT_UPLOAD)}
    proc = subprocess.run(
        [sys.executable, str(RUNBOOK), "--group", "queue", "--order", "1", "--skip-validation"],
        text=True,
        capture_output=True,
        check=False,
    )
    output = (proc.stdout + proc.stderr).strip()
    after = {"records_sha": sha256(RECORDS), "records_count": str(records_count(RECORDS)), "upload_sha": sha256(CURRENT_UPLOAD)}

    checks = [
        {
            "name": "runbook_exit_zero",
            "ok": proc.returncode == 0,
            "detail": f"exit={proc.returncode}",
        },
        {
            "name": "prints_live_threshold",
            "ok": f"STOP_IF_SCORE_GREATER_THAN={EXPECTED_THRESHOLD}" in output,
            "detail": f"expected={EXPECTED_THRESHOLD}",
        },
        {
            "name": "does_not_print_stale_threshold",
            "ok": f"STOP_IF_SCORE_GREATER_THAN={STALE_THRESHOLD}" not in output,
            "detail": f"stale={STALE_THRESHOLD}",
        },
        {
            "name": "records_and_upload_unchanged",
            "ok": before == after,
            "detail": f"before={before}; after={after}",
        },
    ]
    failures = [check for check in checks if not check["ok"]]

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "ok", "detail"], lineterminator="\n")
        writer.writeheader()
        writer.writerows({"name": c["name"], "ok": "yes" if c["ok"] else "no", "detail": c["detail"]} for c in checks)

    lines = [
        "# v1922 Runbook Threshold Regression",
        "",
        "## Summary",
        "",
        f"- Failures: `{len(failures)}`",
        f"- Expected threshold: `>{EXPECTED_THRESHOLD}`",
        f"- Stale threshold rejected: `{STALE_THRESHOLD}`",
        "",
        "## Checks",
        "",
        "| Check | OK | Detail |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        detail = str(check["detail"]).replace("|", "\\|")
        lines.append(f"| {check['name']} | {'yes' if check['ok'] else 'no'} | `{detail}` |")
    lines.extend(
        [
            "",
            "## Runbook output",
            "",
            "```text",
            output,
            "```",
            "",
            "## Completion boundary",
            "",
            "This regression only aligns the user-facing stop threshold. The active goal is complete only after a real private score greater than `0.52380` is recorded.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("V1922_RUNBOOK_THRESHOLD_REGRESSION")
    print(f"WROTE_CSV={OUT_CSV}")
    print(f"WROTE_REPORT={OUT_MD}")
    print(f"FAILURES={len(failures)}")
    for failure in failures:
        print(f"FAIL={failure['name']} detail={failure['detail']}")
    if failures:
        raise SystemExit("runbook threshold regression failed")


if __name__ == "__main__":
    main()
