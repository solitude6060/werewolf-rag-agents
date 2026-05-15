#!/usr/bin/env python3
"""Guard that current_upload/SCORE_REPORT.txt matches the staged upload context."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UPLOAD = Path("experiments/final_submission_package/current_upload/submission.csv")
METADATA = Path("experiments/final_submission_package/current_upload/metadata.json")
SCORE_REPORT = Path("experiments/final_submission_package/current_upload/SCORE_REPORT.txt")
OUT_JSON = Path("experiments/reports/v1900_current_upload_score_report_guard.json")
OUT_MD = Path("experiments/reports/v1900_current_upload_score_report_guard.md")
PLACEHOLDER = "<REAL_PRIVATE_SCORE_DECIMAL>"
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


def parse_report(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line == "SCORE_REPORT" or line.startswith("#") or line.startswith("```"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def add_check(checks: list[dict[str, str]], name: str, ok: bool, detail: str) -> None:
    checks.append({"name": name, "ok": "yes" if ok else "no", "detail": detail})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate current_upload/SCORE_REPORT.txt against the staged upload.")
    parser.add_argument("--upload", type=Path, default=UPLOAD)
    parser.add_argument("--metadata", type=Path, default=METADATA)
    parser.add_argument("--score-report", type=Path, default=SCORE_REPORT)
    parser.add_argument("--allow-filled-score", action="store_true", help="Allow real_private_score to be filled instead of placeholder.")
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    return parser.parse_args()


def write_outputs(payload: dict[str, Any], out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v1900 Current Upload Score Report Guard",
        "",
        f"Generated UTC: `{payload['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        f"- Score report ready: `{payload['score_report_ready']}`",
        f"- Upload: `{payload['upload']}`",
        f"- Score report: `{payload['score_report']}`",
        f"- Candidate: `{payload['candidate']}`",
        f"- Rows: `{payload['rows']}`",
        f"- SHA-256: `{payload['sha256']}`",
        "",
        "## Checks",
        "",
        "| Check | OK | Detail |",
        "| --- | --- | --- |",
    ]
    for check in payload["checks"]:
        detail = str(check["detail"]).replace("|", "\\|")
        lines.append(f"| {check['name']} | {check['ok']} | `{detail}` |")
    lines.extend(
        [
            "",
            "## Completion boundary",
            "",
            "This guard only verifies score-report handoff integrity. The active goal is complete only after a real private score greater than `0.52380` is recorded.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    checks: list[dict[str, str]] = []
    add_check(checks, "upload_exists", args.upload.exists(), str(args.upload))
    add_check(checks, "metadata_exists", args.metadata.exists(), str(args.metadata))
    add_check(checks, "score_report_exists", args.score_report.exists(), str(args.score_report))

    metadata: dict[str, Any] = {}
    report: dict[str, str] = {}
    actual_sha = ""
    rows = 0
    if args.metadata.exists():
        metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    if args.score_report.exists():
        report = parse_report(args.score_report)
    if args.upload.exists():
        actual_sha = sha256(args.upload)
        rows = row_count(args.upload)

    missing = [key for key in REQUIRED_KEYS if key not in report]
    add_check(checks, "required_keys_present", not missing, ",".join(missing) if missing else "all_present")
    add_check(checks, "uploaded_path_matches", report.get("uploaded_path") == str(args.upload), report.get("uploaded_path", ""))
    add_check(checks, "candidate_matches_metadata", report.get("candidate") == str(metadata.get("candidate", "")), report.get("candidate", ""))
    add_check(checks, "group_matches_metadata", report.get("group") == str(metadata.get("group", "")), report.get("group", ""))
    add_check(checks, "order_matches_metadata", report.get("order") == str(metadata.get("order", "")), report.get("order", ""))
    add_check(checks, "rows_match_upload", report.get("rows") == str(rows), f"report={report.get('rows', '')} upload={rows}")
    add_check(checks, "rows_match_metadata", str(metadata.get("rows", "")) == str(rows), f"metadata={metadata.get('rows', '')} upload={rows}")
    add_check(checks, "sha_matches_upload", report.get("sha256") == actual_sha, f"report={report.get('sha256', '')} upload={actual_sha}")
    add_check(checks, "sha_matches_metadata", str(metadata.get("sha256", "")) == actual_sha, f"metadata={metadata.get('sha256', '')} upload={actual_sha}")
    score_value = report.get("real_private_score", "")
    score_ok = bool(score_value) if args.allow_filled_score else score_value == PLACEHOLDER
    add_check(checks, "score_placeholder_ready", score_ok, score_value)
    add_check(checks, "real_private_flag_yes", report.get("score_is_real_kaggle_private", "").lower() == "yes", report.get("score_is_real_kaggle_private", ""))

    ready = all(check["ok"] == "yes" for check in checks)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "score_report_ready": "yes" if ready else "no",
        "upload": str(args.upload),
        "score_report": str(args.score_report),
        "candidate": str(metadata.get("candidate", "")),
        "rows": rows,
        "sha256": actual_sha,
        "checks": checks,
    }
    write_outputs(payload, args.out_json, args.out_md)

    print("CURRENT_UPLOAD_SCORE_REPORT_GUARD")
    print(f"SCORE_REPORT_READY={'yes' if ready else 'no'}")
    print(f"UPLOAD={args.upload}")
    print(f"SCORE_REPORT={args.score_report}")
    print(f"CANDIDATE={payload['candidate']}")
    print(f"ROWS={rows}")
    print(f"SHA256={actual_sha}")
    print(f"REPORT={args.out_md}")
    print(f"JSON={args.out_json}")
    if not ready:
        failed = ",".join(check["name"] for check in checks if check["ok"] != "yes")
        raise SystemExit(f"score report guard failed: {failed}")


if __name__ == "__main__":
    main()
