#!/usr/bin/env python3
"""Guard active upload handoff surfaces against stale leaderboard thresholds."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LIVE_THRESHOLD = "0.52380"
STALE_THRESHOLD = "0.50671"
OUT_CSV = Path("experiments/reports/v1925_active_handoff_threshold_guard.csv")
OUT_MD = Path("experiments/reports/v1925_active_handoff_threshold_guard.md")
ACTIVE_PATHS = [
    Path("experiments/final_submission_package/current_upload"),
    Path("hw2_D13922024/README.md"),
    Path("hw2_D13922024/make_final.py"),
    Path("hw2_D13922024/hw2_report.md"),
    Path("experiments/scripts/v1866_final_attempt_runbook.py"),
    Path("experiments/scripts/v1836_score_feedback_router.py"),
    Path("experiments/scripts/v1870_stage_current_upload.py"),
    Path("experiments/scripts/v1871_final_attempt_cockpit.py"),
    Path("experiments/scripts/v1872_post_score_command_center.py"),
    Path("experiments/scripts/v1883_pre_upload_guard.py"),
    Path("experiments/scripts/v1888_final_upload_preflight.py"),
    Path("experiments/scripts/v1893_score_report_template.py"),
    Path("experiments/scripts/v1894_score_report_intake.py"),
    Path("experiments/scripts/v1895_score_report_command_center.py"),
    Path("experiments/scripts/v1898_current_score_report_bridge.py"),
    Path("experiments/scripts/v1900_current_upload_score_report_guard.py"),
    Path("experiments/scripts/v1902_upload_alias_guard.py"),
    Path("experiments/scripts/v1904_attempt_state_guard.py"),
    Path("experiments/scripts/v1906_goal_completion_gate.py"),
    Path("experiments/scripts/v1908_final_goal_status.py"),
    Path("experiments/scripts/v1921_upload_now_console.py"),
]
TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".csv"}


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(item for item in path.rglob("*") if item.is_file() and item.suffix in TEXT_SUFFIXES))
        elif path.is_file():
            files.append(path)
        else:
            files.append(path)
    return files


def scan_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {
            "path": str(path),
            "exists": "no",
            "stale_hits": "0",
            "live_hits": "0",
            "status": "missing",
            "detail": "active handoff path missing",
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    stale_hits = text.count(STALE_THRESHOLD)
    live_hits = text.count(LIVE_THRESHOLD)
    status = "pass" if stale_hits == 0 else "fail_stale_threshold"
    detail = "ok" if status == "pass" else f"found stale threshold {STALE_THRESHOLD}"
    return {
        "path": str(path),
        "exists": "yes",
        "stale_hits": str(stale_hits),
        "live_hits": str(live_hits),
        "status": status,
        "detail": detail,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan active handoff files for stale threshold literals.")
    parser.add_argument("--path", type=Path, action="append", default=None, help="Override active paths to scan.")
    parser.add_argument("--out-csv", type=Path, default=OUT_CSV)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    return parser.parse_args()


def write_outputs(payload: dict[str, Any], out_csv: Path, out_md: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = ["path", "exists", "stale_hits", "live_hits", "status", "detail"]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(payload["rows"])
    lines = [
        "# v1925 Active Handoff Threshold Guard",
        "",
        f"Generated UTC: `{payload['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        f"- Ready: `{payload['ready']}`",
        f"- Live threshold: `>{payload['live_threshold']}`",
        f"- Stale threshold rejected: `{payload['stale_threshold']}`",
        f"- Files scanned: `{payload['files_scanned']}`",
        f"- Failures: `{payload['failure_count']}`",
        "",
        "## Matrix",
        "",
        "| Path | Stale hits | Live hits | Status | Detail |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        detail = row["detail"].replace("|", "\\|")
        lines.append(f"| `{row['path']}` | `{row['stale_hits']}` | `{row['live_hits']}` | `{row['status']}` | `{detail}` |")
    lines.extend(
        [
            "",
            "## Completion boundary",
            "",
            "This guard verifies active handoff wording only. The active goal is complete only after a real private score greater than `0.52380` is recorded.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    paths = args.path if args.path is not None else ACTIVE_PATHS
    rows = [scan_file(path) for path in iter_files(paths)]
    failures = [row for row in rows if row["status"] != "pass"]
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ready": "yes" if not failures else "no",
        "live_threshold": LIVE_THRESHOLD,
        "stale_threshold": STALE_THRESHOLD,
        "files_scanned": len(rows),
        "failure_count": len(failures),
        "rows": rows,
    }
    write_outputs(payload, args.out_csv, args.out_md)

    print("ACTIVE_HANDOFF_THRESHOLD_GUARD")
    print(f"ACTIVE_HANDOFF_THRESHOLD_READY={'yes' if not failures else 'no'}")
    print(f"LIVE_THRESHOLD={LIVE_THRESHOLD}")
    print(f"STALE_THRESHOLD={STALE_THRESHOLD}")
    print(f"FILES_SCANNED={len(rows)}")
    print(f"FAILURES={len(failures)}")
    print(f"REPORT={args.out_md}")
    print(f"CSV={args.out_csv}")
    for failure in failures:
        print(f"FAIL={failure['path']} detail={failure['detail']}")
    if failures:
        raise SystemExit("active handoff threshold guard failed")


if __name__ == "__main__":
    main()
