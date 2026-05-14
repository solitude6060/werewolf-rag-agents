#!/usr/bin/env python3
"""Validate a SCORE_REPORT block before routing or recording a final private score."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shlex
from pathlib import Path
from typing import Any

UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
RECORDS = Path("experiments/final_submission_package/manifests/v1836_score_feedback_records.csv")
OUT_JSON = Path("experiments/reports/v1894_score_report_intake.json")
OUT_MD = Path("experiments/reports/v1894_score_report_intake.md")
TOP3 = 0.50671
REQUIRED_KEYS = [
    "uploaded_path",
    "candidate",
    "group",
    "order",
    "sha256",
    "rows",
    "real_private_score",
    "score_is_real_kaggle_private",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def parse_score_report(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line == "SCORE_REPORT" or line.startswith("#") or line.startswith("```"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def parse_score(text: str) -> float:
    try:
        score = float(text)
    except ValueError as exc:
        raise SystemExit(f"Invalid real_private_score: not a number: {text!r}") from exc
    if not math.isfinite(score) or score < 0.0 or score > 1.0:
        raise SystemExit(
            f"Invalid real_private_score: expected decimal score in [0, 1], got {text!r}. "
            "Use values like 0.47119, not 47.119."
        )
    return score


def add_check(checks: list[dict[str, str]], name: str, ok: bool, detail: str) -> None:
    checks.append({"name": name, "ok": "yes" if ok else "no", "detail": detail})


def command(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a SCORE_REPORT file before post-score routing.")
    parser.add_argument("report", type=Path, help="Path containing a SCORE_REPORT key-value block.")
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    report = parse_score_report(args.report)
    checks: list[dict[str, str]] = []

    missing = [key for key in REQUIRED_KEYS if not report.get(key)]
    add_check(checks, "required_keys_present", not missing, ",".join(missing) if missing else "all present")
    if missing:
        raise SystemExit(f"missing required score-report keys: {', '.join(missing)}")

    actual_sha = sha256(UPLOAD)
    actual_rows = row_count(UPLOAD)
    score = parse_score(report["real_private_score"])

    add_check(checks, "uploaded_path_matches_current", Path(report["uploaded_path"]) == UPLOAD, report["uploaded_path"])
    add_check(checks, "candidate_matches_metadata", report["candidate"] == str(metadata.get("candidate", "")), report["candidate"])
    add_check(checks, "group_matches_metadata", report["group"] == str(metadata.get("group", "")), report["group"])
    add_check(checks, "order_matches_metadata", report["order"] == str(metadata.get("order", "")), report["order"])
    add_check(checks, "sha_matches_current_upload", report["sha256"] == actual_sha, report["sha256"])
    add_check(checks, "rows_match_current_upload", report["rows"] == str(actual_rows), report["rows"])
    add_check(
        checks,
        "score_marked_real_private",
        report["score_is_real_kaggle_private"].lower() == "yes",
        report["score_is_real_kaggle_private"],
    )
    add_check(checks, "score_decimal_range_ok", True, f"{score:.5f}")
    add_check(checks, "official_records_absent_before_intake", not RECORDS.exists(), str(RECORDS))

    ready = all(check["ok"] == "yes" for check in checks)
    dry_run_cmd = command(["python3", "experiments/scripts/v1872_post_score_command_center.py", "--score", f"{score:.5f}"])
    confirm_cmd = command(
        ["python3", "experiments/scripts/v1872_post_score_command_center.py", "--score", f"{score:.5f}", "--confirm-real-score"]
    )
    status = "top3_completion_candidate" if score > TOP3 else "continue_routing_required"
    payload: dict[str, Any] = {
        "report_path": str(args.report),
        "ready_for_command_center": "yes" if ready else "no",
        "score": f"{score:.5f}",
        "score_status": status,
        "top3_threshold": TOP3,
        "dry_run_command": dry_run_cmd,
        "confirm_command": confirm_cmd,
        "checks": checks,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v1894 Score Report Intake",
        "",
        "## Summary",
        "",
        f"- Ready for command center: `{payload['ready_for_command_center']}`",
        f"- Score: `{payload['score']}`",
        f"- Score status: `{payload['score_status']}`",
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
            "## Next commands",
            "",
            "```bash",
            dry_run_cmd,
            confirm_cmd,
            "```",
            "",
            "## Completion boundary",
            "",
            "This intake validates a report format only. The active goal is complete only after the real score is recorded and is greater than `0.50671`.",
            "",
        ]
    )
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text("\n".join(lines), encoding="utf-8")

    print("SCORE_REPORT_INTAKE")
    print(f"READY_FOR_COMMAND_CENTER={'yes' if ready else 'no'}")
    print(f"SCORE={score:.5f}")
    print(f"SCORE_STATUS={status}")
    print(f"DRY_RUN_COMMAND={dry_run_cmd}")
    print(f"CONFIRM_COMMAND={confirm_cmd}")
    print(f"REPORT={args.out_md}")
    print(f"JSON={args.out_json}")
    if not ready:
        failed = ",".join(check["name"] for check in checks if check["ok"] != "yes")
        raise SystemExit(f"score report intake failed: {failed}")


if __name__ == "__main__":
    main()
